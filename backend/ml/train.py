"""
Train TF-IDF + LinearSVC emotion classifier on GoEmotions dataset.
Trains on 7 core emotions (mapped from 28 GoEmotions labels) for best accuracy.
Usage: python ml/train.py [path/to/emotion_dataset.csv]
"""
import os
import re
import sys
import joblib
import numpy as np
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import LabelEncoder

nltk.download("stopwords", quiet=True)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

stemmer = PorterStemmer()
stop_words = set(stopwords.words("english"))

# 28 GoEmotions -> 7 core emotions
EMOTION_MAPPING = {
    "admiration": "joy", "amusement": "joy", "approval": "joy", "caring": "joy",
    "desire": "joy", "excitement": "joy", "gratitude": "joy", "joy": "joy",
    "love": "joy", "optimism": "joy", "pride": "joy", "relief": "joy",
    "anger": "anger", "annoyance": "anger", "disapproval": "anger",
    "disgust": "disgust",
    "embarrassment": "sadness", "grief": "sadness", "sadness": "sadness",
    "remorse": "sadness", "disappointment": "sadness",
    "fear": "fear", "nervousness": "fear",
    "confusion": "surprise", "curiosity": "surprise", "realization": "surprise",
    "surprise": "surprise",
    "neutral": "neutral",
}


def preprocess(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    tokens = [stemmer.stem(t) for t in text.split() if t not in stop_words and len(t) > 2]
    return " ".join(tokens)


def load_data(data_path: str) -> tuple:
    """
    Loads CSV with columns: text, emotion
    Maps 28-class GoEmotions labels to 7 core emotions.
    """
    df = pd.read_csv(data_path)
    df = df.dropna(subset=["text", "emotion"])
    # Map to 7 core emotions
    df["core_emotion"] = df["emotion"].map(EMOTION_MAPPING)
    df = df.dropna(subset=["core_emotion"])
    print("Preprocessing text...")
    df["processed"] = df["text"].apply(preprocess)
    df = df[df["processed"].str.len() > 0]

    print("\nClass distribution (7 core emotions):")
    print(df["core_emotion"].value_counts().to_string())
    print()
    return df["processed"].tolist(), df["core_emotion"].tolist()


def train(data_path: str = None):
    if data_path and os.path.exists(data_path):
        print(f"Loading data from {data_path}")
        X, y = load_data(data_path)
    else:
        print("No data file found — using synthetic data for smoke-test...")
        X, y = _synthetic_data()

    print(f"\nDataset: {len(X):,} samples, {len(set(y))} classes")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    vectorizer = TfidfVectorizer(
        max_features=30000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
        strip_accents="unicode",
    )

    # LinearSVC is faster and more accurate than LogReg for text
    # CalibratedClassifierCV wraps it to produce probability estimates
    base_clf = LinearSVC(C=0.5, max_iter=2000, class_weight="balanced")
    model = CalibratedClassifierCV(base_clf, cv=3)

    print("Fitting vectorizer...")
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    print("Training model (this takes ~1-2 minutes)...")
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f} ({acc*100:.1f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.pkl")
    model_path = os.path.join(MODELS_DIR, "logreg_model.pkl")
    joblib.dump(vectorizer, vec_path)
    joblib.dump(model, model_path)
    print(f"Models saved to {MODELS_DIR}")
    print("  tfidf_vectorizer.pkl")
    print("  logreg_model.pkl")


def _synthetic_data():
    samples = [
        ("I am so happy and excited today", "joy"),
        ("feeling grateful and loved", "joy"),
        ("this is amazing wonderful", "joy"),
        ("I feel really sad and hopeless", "sadness"),
        ("crying alone nobody cares", "sadness"),
        ("missing someone I lost", "sadness"),
        ("I am furious and so angry", "anger"),
        ("this is absolutely infuriating", "anger"),
        ("I hate this so much", "anger"),
        ("terrified and scared of everything", "fear"),
        ("anxious worried about tomorrow", "fear"),
        ("nervous panic attack coming", "fear"),
        ("that is disgusting and horrible", "disgust"),
        ("gross awful nasty smell", "disgust"),
        ("wow I cannot believe this surprise", "surprise"),
        ("shocked unexpected news today", "surprise"),
        ("just another ordinary day", "neutral"),
        ("went to the store bought milk", "neutral"),
    ]
    X = [preprocess(s[0]) for s in samples]
    y = [s[1] for s in samples]
    return X * 20, y * 20


if __name__ == "__main__":
    data_path = (
        sys.argv[1] if len(sys.argv) > 1
        else os.path.join(os.path.dirname(__file__), "data", "raw", "emotion_dataset.csv")
    )
    train(data_path if os.path.exists(data_path) else None)
