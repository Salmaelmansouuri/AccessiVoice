"""French TF-IDF intent classifier, trained from the accompanying CSV."""
from __future__ import annotations
import csv
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'data' / 'intents.csv'
MODEL = ROOT / 'models' / 'intent_model.joblib'
METRICS = ROOT / 'models' / 'metrics.json'


def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', text).strip()


def load_dataset():
    with DATASET.open(encoding='utf-8', newline='') as f:
        data = list(csv.DictReader(f))
    if not data or not {'texte', 'intention'} <= set(data[0]):
        raise ValueError('Dataset invalide: colonnes texte,intention nécessaires')
    return [r['texte'] for r in data], [r['intention'] for r in data]


def new_pipeline():
    return Pipeline([
        ('tfidf', TfidfVectorizer(preprocessor=normalize, analyzer='char_wb', ngram_range=(2, 5), min_df=1)),
        ('classifier', LogisticRegression(max_iter=1200, class_weight='balanced', random_state=42))
    ])


def train_and_evaluate():
    X, y = load_dataset()
    if any(y.count(lbl) < 4 for lbl in set(y)):
        raise ValueError('Au moins 4 exemples par intention sont requis')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    evaluation = new_pipeline().fit(X_train, y_train)
    predicted = evaluation.predict(X_test)
    labels = sorted(set(y))
    p, r, f, _ = precision_recall_fscore_support(y_test, predicted, average='macro', zero_division=0)
    metrics = {
        'total_phrases': len(X), 'train_phrases': len(X_train), 'test_phrases': len(X_test),
        'accuracy': round(float(accuracy_score(y_test, predicted)), 4),
        'precision_macro': round(float(p), 4), 'recall_macro': round(float(r), 4),
        'f1_macro': round(float(f), 4), 'labels': labels,
        'confusion_matrix': confusion_matrix(y_test, predicted, labels=labels).tolist(),
        'evaluation_method': 'hold-out stratifié 25 %, random_state=42; modèle final réentraîné sur tout le dataset',
        'limitations': 'petit jeu de phrases rédigées pour une démonstration; pas de test sur utilisateurs réels'
    }
    production = new_pipeline().fit(X, y)
    MODEL.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(production, MODEL)
    METRICS.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding='utf-8')
    get_model.cache_clear()
    return metrics


@lru_cache(maxsize=1)
def get_model():
    if not MODEL.exists():
        train_and_evaluate()
    return joblib.load(MODEL)


def predict(text: str):
    text = text.strip()
    if not text:
        raise ValueError('Le texte ne peut pas être vide')
    model = get_model()
    probabilities = model.predict_proba([text])[0]
    best = int(probabilities.argmax())
    return {'intention': str(model.classes_[best]), 'confiance': round(float(probabilities[best]), 4)}
