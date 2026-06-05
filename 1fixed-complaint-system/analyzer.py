import pickle
import os
from backend.utils.preprocess import clean_text  # Fix: correct import path

# Fix: Load pre-trained models once at startup instead of retraining every call
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")

with open(os.path.join(MODELS_DIR, "category_model.pkl"), "rb") as f:
    category_model = pickle.load(f)

with open(os.path.join(MODELS_DIR, "priority_model.pkl"), "rb") as f:
    priority_model = pickle.load(f)

with open(os.path.join(MODELS_DIR, "vectorizer.pkl"), "rb") as f:
    vectorizer = pickle.load(f)


def analyze_complaint(text):
    """Analyze a complaint text and return (category, priority)."""
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])  # Fix: use transform, not fit_transform

    category = category_model.predict(X)[0]
    priority = priority_model.predict(X)[0]

    return category, priority
