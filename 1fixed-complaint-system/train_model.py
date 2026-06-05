import os
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Fix: correct import path for preprocess module
from backend.utils.preprocess import clean_text

# Fix: use absolute paths so script works from any directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "backend", "dataset", "smart_complaints_dataset_4000.csv")
MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")

data = pd.read_csv(DATASET_PATH)
data["clean_text"] = data["complaint_text"].apply(clean_text)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data["clean_text"])

# Category Model
X_train, X_test, y_train, y_test = train_test_split(X, data["category"], test_size=0.2, random_state=42)
category_model = LogisticRegression(max_iter=200)
category_model.fit(X_train, y_train)
print(f"Category model accuracy: {category_model.score(X_test, y_test):.2f}")

# Priority Model
X_train2, X_test2, y_train2, y_test2 = train_test_split(X, data["priority"], test_size=0.2, random_state=42)
priority_model = LogisticRegression(max_iter=200)
priority_model.fit(X_train2, y_train2)
print(f"Priority model accuracy: {priority_model.score(X_test2, y_test2):.2f}")

# Save models
os.makedirs(MODELS_DIR, exist_ok=True)
pickle.dump(category_model, open(os.path.join(MODELS_DIR, "category_model.pkl"), "wb"))
pickle.dump(priority_model, open(os.path.join(MODELS_DIR, "priority_model.pkl"), "wb"))
pickle.dump(vectorizer, open(os.path.join(MODELS_DIR, "vectorizer.pkl"), "wb"))

print("Models trained and saved successfully!")
