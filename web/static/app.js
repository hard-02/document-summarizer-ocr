"use strict";

const LANG_CONFIG = {
  en: { min: 40, max: 180 },
  hi: { min: 5, max: 64 },
};

const state = {
  tab: "document",
  documentFile: null,
};

const $ = (id) => document.getElementById(id);

// ---------------------------------------------------------------------------
// Tabs
// ---------------------------------------------------------------------------
document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $(`panel-${btn.dataset.tab}`).classList.add("active");
    state.tab = btn.dataset.tab;
    updateRun();
  });
});

// ---------------------------------------------------------------------------
// Language + length sliders
// ---------------------------------------------------------------------------
const langEl = $("language");
const minEl = $("min-length");
const maxEl = $("max-length");
const minVal = $("min-val");
const maxVal = $("max-val");

function applyLangConfig() {
  const cfg = LANG_CONFIG[langEl.value];
  maxEl.max = cfg.max;
  maxEl.value = cfg.max;
  minEl.value = cfg.min;
  minVal.textContent = cfg.min;
  maxVal.textContent = cfg.max;
}
langEl.addEventListener("change", applyLangConfig);
minEl.addEventListener("input", () => (minVal.textContent = minEl.value));
maxEl.addEventListener("input", () => (maxVal.textContent = maxEl.value));
applyLangConfig();

// ---------------------------------------------------------------------------
// Dropzone (document only)
// ---------------------------------------------------------------------------
function setupDropzone(dropzoneId, inputId, onFile) {
  const dz = $(dropzoneId);
  const input = $(inputId);
  dz.addEventListener("click", () => input.click());
  dz.addEventListener("dragover", (e) => {
    e.preventDefault();
    dz.classList.add("dragover");
  });
  dz.addEventListener("dragleave", () => dz.classList.remove("dragover"));
  dz.addEventListener("drop", (e) => {
    e.preventDefault();
    dz.classList.remove("dragover");
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) onFile(file);
  });
  input.addEventListener("change", () => {
    if (input.files && input.files[0]) onFile(input.files[0]);
  });
}

setupDropzone("dropzone-document", "file-document", (file) => {
  state.documentFile = file;
  const p = $("dropzone-document").querySelector("p b");
  if (p) p.textContent = file.name;
  updateRun();
});

const textInput = $("text-input");
textInput.addEventListener("input", updateRun);

// ---------------------------------------------------------------------------
// Run button state
// ---------------------------------------------------------------------------
function updateRun() {
  let ready = false;
  if (state.tab === "document") ready = !!state.documentFile;
  else ready = textInput.value.trim().length > 0;
  $("run-btn").disabled = !ready;
}

// ---------------------------------------------------------------------------
// Status + result rendering
// ---------------------------------------------------------------------------
function setStatus(type, msg) {
  const el = $("status");
  if (!type) {
    el.classList.add("hidden");
    el.textContent = "";
    return;
  }
  el.classList.remove("hidden");
  el.className = `status ${type}`;
  el.textContent = msg;
}

function hideResult() {
  $("result").classList.add("hidden");
}

let lastSummary = "";

function showResult(data) {
  lastSummary = data.summary || "";
  $("summary-text").textContent = lastSummary;
  if (data.source_text) {
    $("source-text").textContent = data.source_text;
    $("source-details").classList.remove("hidden");
  } else {
    $("source-details").classList.add("hidden");
  }
  $("result").classList.remove("hidden");
}

// ---------------------------------------------------------------------------
// Submit
// ---------------------------------------------------------------------------
$("run-btn").addEventListener("click", run);

async function run() {
  const language = langEl.value;
  const maxLength = parseInt(maxEl.value, 10);
  const minLength = Math.min(parseInt(minEl.value, 10), maxLength);
  hideResult();
  setStatus("loading", "Working… this may take a few seconds.");
  $("run-btn").disabled = true;

  try {
    let resp;
    if (state.tab === "text") {
      resp = await fetch("/api/summarize-text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textInput.value,
          language,
          max_length: maxLength,
          min_length: minLength,
        }),
      });
    } else {
      const fd = new FormData();
      fd.append("file", state.documentFile);
      fd.append("language", language);
      fd.append("max_length", String(maxLength));
      fd.append("min_length", String(minLength));
      resp = await fetch("/api/summarize-document", { method: "POST", body: fd });
    }

    const data = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(data.detail || `Request failed (${resp.status})`);
    showResult(data);
    setStatus(null);
  } catch (err) {
    setStatus("error", err.message || "Something went wrong");
  } finally {
    $("run-btn").disabled = false;
    updateRun();
  }
}

// ---------------------------------------------------------------------------
// Copy + download
// ---------------------------------------------------------------------------
$("copy-btn").addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(lastSummary);
    $("copy-btn").textContent = "Copied ✓";
    setTimeout(() => ($("copy-btn").textContent = "Copy"), 1500);
  } catch {
    /* clipboard unavailable */
  }
});

$("download-btn").addEventListener("click", () => {
  const blob = new Blob([lastSummary], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "summary.txt";
  a.click();
  URL.revokeObjectURL(url);
});

updateRun();
