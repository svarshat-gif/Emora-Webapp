"""
Converts the raw GoEmotions .tsv files into the single CSV that train.py expects.

Usage:
    python ml/prepare_goemotions.py

Downloads the GoEmotions dataset automatically via the HuggingFace datasets library
(pip install datasets) OR reads local .tsv files if already downloaded.

GoEmotions source:
  https://github.com/google-research/google-research/tree/master/goemotions
"""
import os
import sys
import pandas as pd

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "data", "raw", "emotion_dataset.csv")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 28 GoEmotions label names in order (matches the column indices in the .tsv)
LABEL_NAMES = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral",
]


def from_huggingface():
    """Download directly from HuggingFace hub (easiest)."""
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install HuggingFace datasets: pip install datasets")
        sys.exit(1)

    print("Downloading GoEmotions from HuggingFace…")
    ds = load_dataset("go_emotions", "simplified")

    rows = []
    for split in ["train", "validation", "test"]:
        for item in ds[split]:
            labels = item["labels"]
            if not labels:
                continue
            # Use the first (most confident) label
            emotion = ds["train"].features["labels"].feature.int2str(labels[0])
            rows.append({"text": item["text"], "emotion": emotion})

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df):,} samples → {OUTPUT_PATH}")
    return df


def from_local_tsv(tsv_dir: str):
    """
    Parse raw GoEmotions .tsv files.
    Each line: text <TAB> label_indices (comma-separated) <TAB> comment_id
    """
    rows = []
    for fname in ["train.tsv", "dev.tsv", "test.tsv"]:
        path = os.path.join(tsv_dir, fname)
        if not os.path.exists(path):
            print(f"  Skipping {fname} (not found)")
            continue
        print(f"  Reading {fname}…")
        with open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) < 2:
                    continue
                text = parts[0]
                label_indices = [int(x) for x in parts[1].split(",") if x.strip().isdigit()]
                if not label_indices:
                    continue
                # Take the first label (multi-label → single label)
                emotion = LABEL_NAMES[label_indices[0]]
                rows.append({"text": text, "emotion": emotion})

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(df):,} samples → {OUTPUT_PATH}")
    return df


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Local .tsv directory provided
        tsv_dir = sys.argv[1]
        print(f"Reading local TSV files from: {tsv_dir}")
        df = from_local_tsv(tsv_dir)
    else:
        # Try HuggingFace auto-download
        print("No path provided — attempting HuggingFace download…")
        df = from_huggingface()

    print(f"\nEmotion distribution:")
    print(df["emotion"].value_counts().to_string())
    print(f"\nNext step: python ml/train.py {OUTPUT_PATH}")
