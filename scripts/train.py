#!/usr/bin/env python3
"""Fine-tune a summarization model locally (no Kaggle required).

Mirrors the Kaggle notebooks in ``notebooks/`` but runs on your own machine.

Examples
--------
    python scripts/train.py --language en --epochs 2 --batch-size 4
    python scripts/train.py --language hi --epochs 2
    python scripts/train.py --language mr --epochs 2

Dependencies
------------
    pip install -r requirements.txt -r requirements-train.txt

The fine-tuned weights are written to ``./finetuned-<lang>/``. Move them into
``models/<lang>/`` to have the app/web UI use them automatically.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make the repo root importable so we can reuse the src/ helpers.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import src.config  # noqa: E402,F401  (redirects a broken HF cache before transformers imports)

import evaluate  # noqa: E402
import nltk  # noqa: E402
import numpy as np  # noqa: E402
import torch  # noqa: E402
from datasets import load_dataset  # noqa: E402
from transformers import (  # noqa: E402
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)

from src.summarizer import _decoder_start_id  # noqa: E402

# Training presets. Note: inference uses bart-LARGE-cnn for English, but we
# fine-tune bart-BASE (smaller and much faster to train on a single GPU).
PRESETS = {
    "en": {
        "model_id": "facebook/bart-base",
        "dataset": "abisee/cnn_dailymail",
        "dataset_config": "3.0.0",
        "text_col": "article",
        "summary_col": "highlights",
        "tokenizer_kwargs": {},
        "lang_code": None,
    },
    "hi": {
        "model_id": "ai4bharat/IndicBARTSS",
        "dataset": "csebuetnlp/xlsum",
        "dataset_config": "hindi",
        "text_col": "text",
        "summary_col": "summary",
        "tokenizer_kwargs": {"do_lower_case": False, "use_fast": False},
        "lang_code": "hi_IN",
    },
}


# XL-Sum is script-based and unsupported by datasets >= 4, so we load its
# auto-converted Parquet shards directly by URL.
_XLSUM_BASE = "https://huggingface.co/datasets/csebuetnlp/xlsum/resolve/refs%2Fconvert%2Fparquet"

_XLSUM_PARQUET = {
    "hi": {
        "train": [f"{_XLSUM_BASE}/hindi/train/0000.parquet", f"{_XLSUM_BASE}/hindi/train/0001.parquet"],
        "validation": [f"{_XLSUM_BASE}/hindi/validation/0000.parquet"],
        "test": [f"{_XLSUM_BASE}/hindi/test/0000.parquet"],
    },
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fine-tune a summarization model.")
    p.add_argument("--language", choices=["en", "hi"], default="en")
    p.add_argument("--model-id", default=None, help="Override the preset Hugging Face model id")
    p.add_argument("--dataset", default=None, help="Override the dataset name")
    p.add_argument("--dataset-config", default=None, help="Override the dataset config/version")
    p.add_argument("--text-col", default=None, help="Override the article/text column name")
    p.add_argument("--summary-col", default=None, help="Override the summary column name")
    p.add_argument("--train-size", type=int, default=2000, help="Sample size (remove to use full data)")
    p.add_argument("--eval-size", type=int, default=200)
    p.add_argument("--max-input-length", type=int, default=512)
    p.add_argument("--max-target-length", type=int, default=128)
    p.add_argument("--epochs", type=float, default=2.0)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--lr", type=float, default=3e-5)
    p.add_argument("--output-dir", default=None)
    p.add_argument("--fp16", dest="fp16", action="store_true", default=None)
    p.add_argument("--no-fp16", dest="fp16", action="store_false")
    p.add_argument("--push-to-hub", default=None, help="Optional HF Hub repo id to push to")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    preset = PRESETS[args.language]

    model_id = args.model_id or preset["model_id"]
    dataset_name = args.dataset or preset["dataset"]
    dataset_config = args.dataset_config or preset["dataset_config"]
    text_col = args.text_col or preset["text_col"]
    summary_col = args.summary_col or preset["summary_col"]
    output_dir = args.output_dir or f"./finetuned-{args.language}"

    nltk.download("punkt")
    use_cuda = torch.cuda.is_available()
    print(f"CUDA available: {use_cuda}")

    print(f"Loading dataset {dataset_name} ({dataset_config or '-'}) ...")
    if args.language in _XLSUM_PARQUET:
        # XL-Sum: load Parquet shards directly (script datasets unsupported in datasets >= 4).
        ds = load_dataset("parquet", data_files=_XLSUM_PARQUET[args.language])
        train = ds["train"].shuffle(seed=42).select(range(args.train_size))
        valid = ds["validation"].shuffle(seed=42).select(range(args.eval_size))
    elif dataset_config:
        train = load_dataset(dataset_name, dataset_config, split=f"train[:{args.train_size}]").shuffle(seed=42)
        valid = load_dataset(dataset_name, dataset_config, split=f"validation[:{args.eval_size}]").shuffle(seed=42)
    else:
        train = load_dataset(dataset_name, split=f"train[:{args.train_size}]").shuffle(seed=42)
        valid = load_dataset(dataset_name, split=f"validation[:{args.eval_size}]").shuffle(seed=42)

    print(f"Loading model {model_id} ...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, **preset["tokenizer_kwargs"])
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    if preset["lang_code"]:
        _start_id = _decoder_start_id(tokenizer, preset["lang_code"])
        model.config.decoder_start_token_id = _start_id
        model.generation_config.forced_bos_token_id = _start_id
        print("decoder_start_token_id =", _start_id)

    def preprocess(examples):
        if preset["lang_code"]:
            # IndicBART expects "<text> </s> <2xx>" inputs and "<2xx> <summary> </s>" targets.
            lang_tok = f"<2{preset['lang_code'][:2]}>"
            inputs = [f"{t} </s> {lang_tok}" for t in examples[text_col]]
            targets = [f"{lang_tok} {s} </s>" for s in examples[summary_col]]
            model_inputs = tokenizer(inputs, max_length=args.max_input_length, truncation=True, add_special_tokens=False)
            labels = tokenizer(targets, max_length=args.max_target_length, truncation=True, add_special_tokens=False)
        else:
            model_inputs = tokenizer(examples[text_col], max_length=args.max_input_length, truncation=True)
            labels = tokenizer(examples[summary_col], max_length=args.max_target_length, truncation=True)
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    tokenized_train = train.map(preprocess, batched=True, remove_columns=train.column_names)
    tokenized_valid = valid.map(preprocess, batched=True, remove_columns=valid.column_names)

    collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)
    rouge = evaluate.load("rouge")

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        pad = int(tokenizer.pad_token_id)

        # Normalize to lists of plain ints and drop any negative/invalid
        # sentinel id (e.g. -100) so decode never sees an out-of-range value.
        def clean_ids(seqs):
            if hasattr(seqs, "tolist"):
                seqs = seqs.tolist()
            out = []
            for seq in seqs:
                cleaned = []
                for t in seq:
                    try:
                        v = int(t)
                    except Exception:
                        continue
                    if v < 0:
                        continue
                    cleaned.append(v)
                out.append(cleaned)
            return out

        preds = clean_ids(predictions)
        labs = clean_ids(labels)

        decoded_preds = tokenizer.batch_decode(preds, skip_special_tokens=True)
        decoded_labels = tokenizer.batch_decode(labs, skip_special_tokens=True)
        decoded_preds = ["\n".join(nltk.sent_tokenize(p.strip())) for p in decoded_preds]
        decoded_labels = ["\n".join(nltk.sent_tokenize(l.strip())) for l in decoded_labels]
        result = rouge.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
        result = {k: round(v * 100, 2) for k, v in result.items()}
        result["gen_len"] = round(float(np.mean([sum(1 for t in p if t != pad) for p in preds])), 2)
        return result

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="steps",
        save_steps=200,
        logging_steps=50,
        learning_rate=args.lr,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        weight_decay=0.01,
        save_total_limit=2,
        num_train_epochs=args.epochs,
        predict_with_generate=True,
        fp16=(use_cuda if args.fp16 is None else args.fp16),
        report_to="none",
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_valid,
        processing_class=tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    metrics = trainer.evaluate(eval_dataset=tokenized_valid, max_length=args.max_target_length, num_beams=4)
    print("Eval metrics:", metrics)

    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    print(f"Saved fine-tuned model to {output_dir}")
    print(f"Move it to models/{args.language}/ to use it in the app/web UI.")

    if args.push_to_hub:
        model.push_to_hub(args.push_to_hub)
        tokenizer.push_to_hub(args.push_to_hub)
        print(f"Pushed to https://huggingface.co/{args.push_to_hub}")


if __name__ == "__main__":
    main()
