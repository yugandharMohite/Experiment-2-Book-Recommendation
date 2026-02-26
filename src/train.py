import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from model import create_ncf_model
import mlflow
import mlflow.tensorflow
import os
import json
from datetime import datetime

# Resolve project root regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'src' else SCRIPT_DIR

def train():
    # Load processed data
    DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "processed", "processed_ratings.csv")
    METADATA_PATH = os.path.join(PROJECT_ROOT, "Data", "processed", "metadata.json")

    if not os.path.exists(DATA_PATH) or not os.path.exists(METADATA_PATH):
        print("Processed data not found. Please run preprocess.py first.")
        return

    ratings = pd.read_csv(DATA_PATH)
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)

    num_users = metadata['num_users']
    num_books = metadata['num_books']

    print(f"Training NCF model on {num_users} users and {num_books} books.")

    # Split data
    train_df, test_df = train_test_split(ratings, test_size=0.2, random_state=42)
    train_df, val_df = train_test_split(train_df, test_size=0.1, random_state=42)

    # Prepare inputs
    X_train = [train_df['user_idx'].values, train_df['book_idx'].values]
    y_train = train_df['rating'].values.astype(np.float32)

    X_val = [val_df['user_idx'].values, val_df['book_idx'].values]
    y_val = val_df['rating'].values.astype(np.float32)

    X_test = [test_df['user_idx'].values, test_df['book_idx'].values]
    y_test = test_df['rating'].values.astype(np.float32)

    # MLflow tracking
    mlflow.set_experiment("BookCrossing_Recommendation")

    with mlflow.start_run():
        # Parameters
        embedding_dim = 32
        layers = [64, 32, 16]
        epochs = 10
        batch_size = 512

        mlflow.log_params({
            "embedding_dim": embedding_dim,
            "layers": layers,
            "epochs": epochs,
            "batch_size": batch_size,
            "num_users": num_users,
            "num_books": num_books
        })

        # Create and compile model
        model = create_ncf_model(num_users, num_books, embedding_dim=embedding_dim, layers=layers)
        model.compile(optimizer='adam', loss='mse', metrics=['mae', tf.keras.metrics.RootMeanSquaredError()])

        print("Starting training...")
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )

        # Evaluate
        eval_results = model.evaluate(X_test, y_test, verbose=0)
        metrics = {
            "test_mse": eval_results[0],
            "test_mae": eval_results[1],
            "test_rmse": np.sqrt(eval_results[0])
        }
        mlflow.log_metrics(metrics)

        print(f"Test Metrics: {metrics}")

        # Save model
        models_dir = os.path.join(PROJECT_ROOT, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        model_save_path = os.path.join(models_dir, "ncf_model.keras")
        model.save(model_save_path)
        mlflow.tensorflow.log_model(model, "model")

        print(f"Model saved to {model_save_path} and logged to MLflow")

        # --- Export metrics to CSV ---
        reports_dir = os.path.join(PROJECT_ROOT, "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
        metrics_csv_path = os.path.join(reports_dir, "metrics.csv")

        run_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "embedding_dim": embedding_dim,
            "layers": str(layers),
            "epochs": epochs,
            "batch_size": batch_size,
            "num_users": num_users,
            "num_books": num_books,
            "test_mse": round(metrics["test_mse"], 4),
            "test_mae": round(metrics["test_mae"], 4),
            "test_rmse": round(float(metrics["test_rmse"]), 4),
        }
        run_df = pd.DataFrame([run_record])
        if os.path.exists(metrics_csv_path):
            run_df.to_csv(metrics_csv_path, mode='a', header=False, index=False)
        else:
            run_df.to_csv(metrics_csv_path, index=False)
        print(f"Metrics exported to {metrics_csv_path}")

if __name__ == "__main__":
    train()
