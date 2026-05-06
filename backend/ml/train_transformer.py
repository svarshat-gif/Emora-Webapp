"""
Fine-tunes DistilBERT on 7-class emotion detection.
Expected accuracy: 78-85% on GoEmotions test set.
Usage:
    python ml/train_transformer.py [path/to/emotion_dataset.csv]

Requirements:
    pip install torch transformers accelerate
"""
import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

import torch
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME   = "distilbert-base-uncased"
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "models", "transformer")
MAX_LEN      = 128
BATCH_SIZE   = 32
EPOCHS       = 5
LR           = 2e-5
SEED         = 42

EMOTION_MAPPING = {
    "admiration": "joy",   "amusement": "joy",   "approval": "joy",
    "caring":     "joy",   "desire":    "joy",   "excitement": "joy",
    "gratitude":  "joy",   "joy":       "joy",   "love":       "joy",
    "optimism":   "joy",   "pride":     "joy",   "relief":     "joy",
    "anger":         "anger",  "annoyance": "anger", "disapproval": "anger",
    "disgust":       "disgust",
    "embarrassment": "sadness", "grief":   "sadness", "sadness": "sadness",
    "remorse":       "sadness", "disappointment": "sadness",
    "fear":          "fear",   "nervousness": "fear",
    "confusion":     "surprise", "curiosity": "surprise",
    "realization":   "surprise", "surprise": "surprise",
    "neutral":       "neutral",
}
CORE_EMOTIONS = ["anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"]

torch.manual_seed(SEED)
np.random.seed(SEED)


# ── Dataset ───────────────────────────────────────────────────────────────────
class EmotionDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.texts     = texts
        self.labels    = labels
        self.tokenizer = tokenizer
        self.max_len   = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            max_length=self.max_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids":      enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long),
        }


# ── Metrics ───────────────────────────────────────────────────────────────────
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, preds)}


# ── Data loading ──────────────────────────────────────────────────────────────
def load_data(data_path: str):
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["text", "emotion"])
    df["label"] = df["emotion"].map(EMOTION_MAPPING)
    df = df.dropna(subset=["label"])
    df = df[df["text"].str.strip().str.len() > 5]

    print(f"\nLoaded {len(df):,} samples")
    print("Class distribution:")
    print(df["label"].value_counts().to_string())
    print()
    return df["text"].tolist(), df["label"].tolist()


# ── Training ──────────────────────────────────────────────────────────────────
def train(data_path: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    if device == "cpu":
        print("  No GPU detected — training on CPU (~30-60 min).")
        print("  Tip: use Google Colab (free GPU) for faster training.\n")

    # Load and encode data
    texts, labels_str = load_data(data_path)
    le = LabelEncoder()
    le.fit(CORE_EMOTIONS)
    labels = le.transform(labels_str).tolist()
    num_labels = len(le.classes_)
    id2label = {i: l for i, l in enumerate(le.classes_)}
    label2id = {l: i for i, l in id2label.items()}

    X_train, X_val, y_train, y_val = train_test_split(
        texts, labels, test_size=0.15, random_state=SEED, stratify=labels
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_val, y_val, test_size=0.5, random_state=SEED, stratify=y_val
    )
    print(f"Train: {len(X_train):,}  Val: {len(X_val):,}  Test: {len(X_test):,}")

    # Tokenizer + model
    print(f"\nLoading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels,
        id2label=id2label,
        label2id=label2id,
    )

    train_ds = EmotionDataset(X_train, y_train, tokenizer)
    val_ds   = EmotionDataset(X_val,   y_val,   tokenizer)
    test_ds  = EmotionDataset(X_test,  y_test,  tokenizer)

    # Reduce batch size on CPU to avoid OOM
    batch = BATCH_SIZE if device == "cuda" else 16

    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=batch,
        per_device_eval_batch_size=batch * 2,
        learning_rate=LR,
        warmup_ratio=0.1,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        greater_is_better=True,
        logging_steps=100,
        fp16=(device == "cuda"),
        seed=SEED,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    print("\nTraining...")
    trainer.train()

    # Final evaluation
    print("\n── Final Test Evaluation ──")
    preds_out = trainer.predict(test_ds)
    preds = np.argmax(preds_out.predictions, axis=-1)
    acc = accuracy_score(y_test, preds)
    print(f"Test Accuracy: {acc:.4f} ({acc*100:.1f}%)\n")
    print(classification_report(y_test, preds, target_names=le.classes_))

    # Save model + tokenizer + metadata
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    meta = {"id2label": id2label, "label2id": label2id, "max_len": MAX_LEN, "accuracy": round(acc, 4)}
    with open(os.path.join(OUTPUT_DIR, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\nModel saved to: {OUTPUT_DIR}")
    print("  config.json, model.safetensors, tokenizer files, meta.json")
    return acc


if __name__ == "__main__":
    data_path = (
        sys.argv[1] if len(sys.argv) > 1
        else os.path.join(os.path.dirname(__file__), "data", "raw", "emotion_dataset.csv")
    )
    if not os.path.exists(data_path):
        print(f"Dataset not found: {data_path}")
        print("Run: python ml/prepare_goemotions.py")
        sys.exit(1)
    train(data_path)
