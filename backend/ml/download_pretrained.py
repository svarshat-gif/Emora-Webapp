"""
Downloads j-hartmann/emotion-english-distilroberta-base — a model already
fine-tuned on GoEmotions + other emotion corpora. No training required.

Classes: anger, disgust, fear, joy, neutral, sadness, surprise  (our 7)
Reported accuracy: ~66% on GoEmotions test set, noticeably higher on
clean first-person text (journals, chat messages).

Usage:
    python ml/download_pretrained.py
"""
import os
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

MODEL_ID   = "j-hartmann/emotion-english-distilroberta-base"
SAVE_DIR   = os.path.join(os.path.dirname(__file__), "models", "transformer")
META_PATH  = os.path.join(SAVE_DIR, "meta.json")

os.makedirs(SAVE_DIR, exist_ok=True)

print(f"Downloading {MODEL_ID} (~320 MB)...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model     = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)

print(f"Saving to {SAVE_DIR}...")
tokenizer.save_pretrained(SAVE_DIR)
model.save_pretrained(SAVE_DIR)

# Write meta so the detector knows the label mapping
id2label = {str(i): l for i, l in model.config.id2label.items()}
label2id = {l: i for i, l in model.config.id2label.items()}
meta = {
    "id2label":  id2label,
    "label2id":  label2id,
    "max_len":   128,
    "accuracy":  0.66,
    "source":    MODEL_ID,
}
with open(META_PATH, "w") as f:
    json.dump(meta, f, indent=2)

# Quick smoke test
print("\nSmoke test...")
clf = pipeline("text-classification", model=SAVE_DIR, tokenizer=SAVE_DIR, top_k=None, device=-1)
tests = [
    ("I feel so happy and grateful today", "joy"),
    ("I am furious about what happened",   "anger"),
    ("This makes me so anxious and scared", "fear"),
    ("I feel deeply sad and alone",         "sadness"),
]
correct = 0
for text, expected in tests:
    results = sorted(clf(text)[0], key=lambda x: x["score"], reverse=True)
    top = results[0]["label"]
    mark = "OK" if top == expected else f"WRONG (got {top})"
    print(f"  [{mark}] '{text[:45]}...' -> {top} ({results[0]['score']:.2f})")
    if top == expected:
        correct += 1

print(f"\n{correct}/{len(tests)} smoke tests passed")
print(f"\nDone. Model ready at: {SAVE_DIR}")
print("The backend will automatically use this model on next start.")
