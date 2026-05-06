import joblib
import numpy as np
import os
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from typing import Dict, Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# 28 GoEmotions -> 7 core emotions
EMOTION_MAPPING: Dict[str, str] = {
    "admiration": "joy",   "amusement": "joy",   "approval": "joy",
    "caring":     "joy",   "desire":    "joy",   "excitement": "joy",
    "gratitude":  "joy",   "joy":       "joy",   "love":       "joy",
    "optimism":   "joy",   "pride":     "joy",   "relief":     "joy",
    "anger":         "anger",  "annoyance":  "anger", "disapproval": "anger",
    "disgust":       "disgust",
    "embarrassment": "sadness", "grief":    "sadness", "sadness": "sadness",
    "remorse":       "sadness", "disappointment": "sadness",
    "fear":          "fear",   "nervousness": "fear",
    "confusion":     "surprise", "curiosity": "surprise",
    "realization":   "surprise", "surprise":  "surprise",
    "neutral":       "neutral",
}

CORE_EMOTIONS = ["joy", "sadness", "anger", "fear", "disgust", "surprise", "neutral"]

EMOTION_COLORS = {
    "joy":     "#FFD700",
    "sadness": "#4A90D9",
    "anger":   "#E74C3C",
    "fear":    "#9B59B6",
    "disgust": "#27AE60",
    "surprise":"#F39C12",
    "neutral": "#95A5A6",
}


class EmotionDetector:
    """
    Detects emotion from text using a two-tier approach:
      1. Transformer model (DistilBERT) if fine-tuned model exists — ~80%+ accuracy
      2. TF-IDF + LinearSVC fallback — ~61% accuracy
      3. Keyword heuristic if neither model is loaded
    """

    def __init__(self):
        self._vectorizer    = None
        self._tfidf_model   = None
        self._transformer   = None   # HuggingFace pipeline
        self._stemmer       = PorterStemmer()
        self._stop_words    = None
        self._loaded        = False
        self._use_transformer = False

    def _ensure_nltk(self):
        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            nltk.download("stopwords", quiet=True)
        self._stop_words = set(stopwords.words("english"))

    # ── Public ────────────────────────────────────────────────────────────────
    def load_models(self):
        if self._loaded:
            return
        self._ensure_nltk()

        transformer_dir = os.path.join(settings.MODEL_PATH, "transformer")
        tfidf_vec_path  = os.path.join(settings.MODEL_PATH, "tfidf_vectorizer.pkl")
        tfidf_clf_path  = os.path.join(settings.MODEL_PATH, "logreg_model.pkl")

        # Try transformer first (better accuracy)
        if os.path.isdir(transformer_dir) and os.path.exists(os.path.join(transformer_dir, "config.json")):
            self._load_transformer(transformer_dir)

        # Fall back to / also load TF-IDF for speed comparison
        if not self._use_transformer and os.path.exists(tfidf_vec_path) and os.path.exists(tfidf_clf_path):
            self._load_tfidf(tfidf_vec_path, tfidf_clf_path)

        self._loaded = True

    def detect(self, text: str) -> Dict:
        if not text or not text.strip():
            return self._neutral_result()

        self.load_models()

        if self._use_transformer:
            return self._predict_transformer(text)
        if self._vectorizer and self._tfidf_model:
            return self._predict_tfidf(text)
        return self._keyword_fallback(text)

    # ── Loaders ───────────────────────────────────────────────────────────────
    def _load_transformer(self, model_dir: str):
        try:
            from transformers import pipeline as hf_pipeline
            meta_path = os.path.join(model_dir, "meta.json")
            meta = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

            self._transformer = hf_pipeline(
                "text-classification",
                model=model_dir,
                tokenizer=model_dir,
                top_k=None,          # return scores for all labels
                truncation=True,
                max_length=meta.get("max_len", 128),
                device=-1,           # CPU; change to 0 for GPU
            )
            self._use_transformer = True
            acc = meta.get("accuracy", "?")
            logger.info("transformer_model_loaded", accuracy=acc, path=model_dir)
        except Exception as e:
            logger.warning("transformer_load_failed", error=str(e))

    def _load_tfidf(self, vec_path: str, clf_path: str):
        try:
            self._vectorizer  = joblib.load(vec_path)
            self._tfidf_model = joblib.load(clf_path)
            logger.info("tfidf_model_loaded")
        except Exception as e:
            logger.warning("tfidf_load_failed", error=str(e))

    # ── Predictors ────────────────────────────────────────────────────────────
    def _predict_transformer(self, text: str) -> Dict:
        results = self._transformer(text[:512])[0]  # list of {label, score}
        # Normalise label names (model might use capital or underscore forms)
        scores = {r["label"].lower().strip(): float(r["score"]) for r in results}

        # Map to core emotions (in case model outputs 28-class labels)
        core_scores: Dict[str, float] = {e: 0.0 for e in CORE_EMOTIONS}
        for label, score in scores.items():
            core = EMOTION_MAPPING.get(label, label if label in CORE_EMOTIONS else "neutral")
            core_scores[core] = core_scores.get(core, 0.0) + score

        dominant = max(core_scores, key=core_scores.get)
        return {
            "dominant_emotion": dominant,
            "confidence":       round(core_scores[dominant], 4),
            "all_emotions":     {k: round(v, 4) for k, v in core_scores.items()},
            "color":            EMOTION_COLORS.get(dominant, "#95A5A6"),
            "raw_scores":       {k: round(v, 4) for k, v in scores.items()},
            "model":            "transformer",
        }

    def _predict_tfidf(self, text: str) -> Dict:
        processed = self._preprocess(text)
        features  = self._vectorizer.transform([processed])
        probs     = self._tfidf_model.predict_proba(features)[0]
        classes   = self._tfidf_model.classes_

        scores_raw = dict(zip(classes, probs))

        # Aggregate to core emotions
        core_scores: Dict[str, float] = {e: 0.0 for e in CORE_EMOTIONS}
        for emotion, prob in scores_raw.items():
            core = EMOTION_MAPPING.get(emotion, emotion if emotion in CORE_EMOTIONS else "neutral")
            core_scores[core] = core_scores.get(core, 0.0) + float(prob)

        dominant = max(core_scores, key=core_scores.get)
        return {
            "dominant_emotion": dominant,
            "confidence":       round(core_scores[dominant], 4),
            "all_emotions":     {k: round(v, 4) for k, v in core_scores.items()},
            "color":            EMOTION_COLORS.get(dominant, "#95A5A6"),
            "raw_scores":       {k: round(float(v), 4) for k, v in scores_raw.items()},
            "model":            "tfidf",
        }

    def _keyword_fallback(self, text: str) -> Dict:
        text_lower = text.lower()
        keyword_map = {
            "joy":     ["happy", "excited", "great", "love", "wonderful", "amazing", "joy", "glad", "grateful", "blessed"],
            "sadness": ["sad", "cry", "depressed", "hopeless", "alone", "miss", "grief", "hurt", "lonely", "devastated"],
            "anger":   ["angry", "furious", "hate", "annoyed", "rage", "mad", "frustrated", "infuriated"],
            "fear":    ["scared", "afraid", "terrified", "anxious", "worried", "panic", "nervous", "dread"],
            "disgust": ["disgusting", "gross", "awful", "horrible", "nasty", "sick", "revolting"],
            "surprise":["surprised", "shocked", "unexpected", "wow", "incredible", "unbelievable"],
        }
        scores = {e: 0.0 for e in CORE_EMOTIONS}
        for emotion, keywords in keyword_map.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[emotion] += 0.15
        scores["neutral"] = max(0.1, 1.0 - sum(v for k, v in scores.items() if k != "neutral"))
        dominant = max(scores, key=scores.get)
        return {
            "dominant_emotion": dominant,
            "confidence":       round(scores[dominant], 4),
            "all_emotions":     {k: round(v, 4) for k, v in scores.items()},
            "color":            EMOTION_COLORS.get(dominant, "#95A5A6"),
            "raw_scores":       {},
            "model":            "keyword",
        }

    def _preprocess(self, text: str) -> str:
        text = str(text).lower()
        text = re.sub(r"http\S+|www\S+", "", text)
        text = re.sub(r"[^a-zA-Z\s]", " ", text)
        tokens = [self._stemmer.stem(t) for t in text.split() if t not in self._stop_words and len(t) > 2]
        return " ".join(tokens)

    def _neutral_result(self) -> Dict:
        return {
            "dominant_emotion": "neutral",
            "confidence":       1.0,
            "all_emotions":     {**{e: 0.0 for e in CORE_EMOTIONS}, "neutral": 1.0},
            "color":            EMOTION_COLORS["neutral"],
            "raw_scores":       {},
            "model":            "rule",
        }


emotion_detector = EmotionDetector()
