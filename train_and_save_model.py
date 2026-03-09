"""
train_and_save_model.py
────────────────────────────────────────────────────────
Run this ONCE to train the ML models from the UCI Obesity
dataset and save them as pickle files for the FastAPI app.

Usage:
    python train_and_save_model.py
"""

import pickle, warnings, os, csv
from datetime import datetime
import mlflow
import mlflow.sklearn
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from ucimlrepo import fetch_ucirepo
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score

SEED = 42
np.random.seed(SEED)
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# ── 1. Load dataset ──────────────────────────────────────────
print("Fetching UCI Obesity dataset...")
repo   = fetch_ucirepo(id=544)
X_raw  = repo.data.features
y_raw  = repo.data.targets

df = pd.concat([X_raw, y_raw], axis=1)
df.columns = [
    "Gender","Age","Height","Weight",
    "FamilyHistory","FAVC","FCVC","NCP","CAEC",
    "SMOKE","CH2O","SCC","FAF","TUE","CALC","MTRANS",
    "ObesityLevel"
]

GENRE_COLS = ["Gender","FamilyHistory","FAVC","CAEC","SMOKE","SCC","CALC","MTRANS"]

# ── 2. Encode ─────────────────────────────────────────────────
label_encoders = {}
df_enc = df.copy()
for col in GENRE_COLS:
    le = LabelEncoder()
    df_enc[col] = le.fit_transform(df_enc[col].astype(str))
    label_encoders[col] = le

target_le = LabelEncoder()
df_enc["ObesityLevel_enc"] = target_le.fit_transform(df_enc["ObesityLevel"])

# ── 3. Feature engineering ────────────────────────────────────
df_enc["BMI"]           = df_enc["Weight"] / (df_enc["Height"] ** 2)
df_enc["ActivityScore"] = df_enc["FAF"] * df_enc["CH2O"]
df_enc["DietScore"]     = df_enc["FCVC"] * df_enc["NCP"] - df_enc["FAVC"]
df_enc["HealthIndex"]   = df_enc["FAF"] + df_enc["FCVC"] + df_enc["CH2O"] - df_enc["TUE"]

FEATURE_COLS = [
    "Gender","Age","Height","Weight","BMI",
    "FamilyHistory","FAVC","FCVC","NCP","CAEC",
    "SMOKE","CH2O","SCC","FAF","TUE","CALC","MTRANS",
    "ActivityScore","DietScore","HealthIndex"
]

X = df_enc[FEATURE_COLS].values
y = df_enc["ObesityLevel_enc"].values

scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=SEED, stratify=y
)

# ── 4. Train classifier with MLflow ───────────────────────────
mlflow.set_experiment("Nutrition Recommendation")

with mlflow.start_run():
    print("Training Gradient Boosting classifier...")
    n_estimators = 150
    lr = 0.1
    clf = GradientBoostingClassifier(n_estimators=n_estimators, learning_rate=lr, random_state=SEED)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='macro')
    
    print(f"   - Accuracy : {acc:.4f}")
    print(f"   - F1 Macro : {f1:.4f}")

    # Log to MLflow
    mlflow.log_param("n_estimators", n_estimators)
    mlflow.log_param("learning_rate", lr)
    mlflow.log_metric("accuracy", acc)
    mlflow.log_metric("f1_macro", f1)
    
    # ── 5. Train KNN for collaborative filtering ──────────────────
    print("Training KNN similarity model...")
    knn = NearestNeighbors(n_neighbors=6, metric="cosine")
    knn.fit(X_scaled)
    
    # Log models
    mlflow.sklearn.log_model(clf, "classifier")
    mlflow.sklearn.log_model(knn, "knn_model")

    # ── 6. Save to CSV for legacy reporting ────────────────────────
    try:
        os.makedirs("reports", exist_ok=True)
        csv_path = "reports/metrics.csv"
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "model", "accuracy", "f1_macro"])
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "GradientBoosting", acc, f1])
    except Exception as e:
        print(f"Error saving to CSV: {e}")

# ── 6. Save everything ────────────────────────────────────────
artifacts = {
    "classifier"     : clf,
    "knn"            : knn,
    "scaler"         : scaler,
    "label_encoders" : label_encoders,
    "target_le"      : target_le,
    "feature_cols"   : FEATURE_COLS,
    "X_scaled"       : X_scaled,
    "df_enc"         : df_enc,
    "n_users"        : len(df_enc),
}

out_path = os.path.join(MODELS_DIR, "nutrition_model.pkl")
with open(out_path, "wb") as f:
    pickle.dump(artifacts, f)

print(f"\nAll artifacts saved to -> {out_path}")
print("   You can now run: uvicorn main:app --reload")
