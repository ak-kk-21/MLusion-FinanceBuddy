import pandas as pd
import numpy as np
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

# -----------------------------
# 1. Load and clean the dataset
# -----------------------------
df = pd.read_csv(
    r'models/datasets/MLusion JustDial Dataset - Combined.csv',
    names=['vendor_name', 'category']
)

# Drop rows with missing values
df.dropna(inplace=True)

# Clean text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()    # Normalize whitespace
    return text

df['vendor_name'] = df['vendor_name'].astype(str).apply(clean_text)

# -----------------------------
# 2. Filter out rare categories (fix for stratify error)
# -----------------------------
category_counts = df['category'].value_counts()
valid_categories = category_counts[category_counts >= 2].index
df = df[df['category'].isin(valid_categories)]

# -----------------------------
# 3. Vectorize using TF-IDF
# -----------------------------
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['vendor_name'])

# -----------------------------
# 4. Encode labels
# -----------------------------
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['category'])

# -----------------------------
# 5. Train/test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=41, stratify=y
)

# -----------------------------
# 6. Train KNN classifier
# -----------------------------
knn = KNeighborsClassifier(n_neighbors=7)
knn.fit(X_train, y_train)

# -----------------------------
# 7. Evaluate
# -----------------------------
y_pred = knn.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# -----------------------------
# 8. Save trained model & assets
# -----------------------------
joblib.dump(knn, 'models/knn_model.pkl')
joblib.dump(vectorizer, 'models/vectorizer.pkl')
joblib.dump(label_encoder, 'models/label_encoder.pkl')

print("Model, vectorizer, and label encoder saved successfully.")
