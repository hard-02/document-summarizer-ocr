# Notebooks

Kaggle fine-tuning notebooks (run on a free GPU).

| Notebook | Model | Dataset | Languages | Output folder |
|----------|-------|---------|-----------|---------------|
| [`01_finetune_english_bart.ipynb`](01_finetune_english_bart.ipynb) | `facebook/bart-base` | CNN/DailyMail | English | `bart-finetuned-cnn` → `models/english/` |
| [`02_finetune_indicbart_hindi_marathi.ipynb`](02_finetune_indicbart_hindi_marathi.ipynb) | `ai4bharat/IndicBARTSS` | XL-Sum | Hindi, Marathi | `indicbart-finetuned-{hindi,marathi}` → `models/{hindi,marathi}/` |

## How to use on Kaggle

1. [kaggle.com](https://www.kaggle.com) → **Create → New Notebook**.
2. **Settings → Accelerator → GPU T4 x2** and **Settings → Internet → On**.
3. **File → Import Notebook** and upload the `.ipynb` (or copy the cells manually).
4. **Run All**. When finished, download the folder from the **Output** tab.
5. Place it under `models/` as shown in the table above — the app/web UI pick it up automatically.

## The same thing locally

These notebooks are mirrored by [`scripts/train.py`](../scripts/train.py), which
you can run on your own machine:

```bash
pip install -r ../requirements.txt -r ../requirements-train.txt
python ../scripts/train.py --language en --epochs 2
```

Both the notebooks and the script evaluate with **ROUGE** (via `evaluate` +
`rouge_score`) and save the fine-tuned weights + tokenizer for reuse.
