import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)  # Fix: quiet=True suppresses repeated download messages

stop_words = set(stopwords.words('english'))


def clean_text(text):
    if not isinstance(text, str):  # Fix: handle non-string inputs gracefully
        text = str(text)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z ]', '', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)
