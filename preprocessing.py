import inspect
if not hasattr(inspect, 'formatargspec'):
    inspect.formatargspec = inspect.formatargvalues

import re
from io import BytesIO
from pdfminer.high_level import extract_text
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

def extract_resume_text(uploaded_file):
    try:
        text = extract_text(BytesIO(uploaded_file.read()))
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.lower()
    except:
        return ""

def clean_text(text):
    if not text:
        return ""
    try:
        stop_words = set(stopwords.words('english'))
    except:
        stop_words = set()

    words = text.split()
    filtered = [w for w in words if w not in stop_words]
    return " ".join(filtered)
