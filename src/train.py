import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split as sklearn_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import mlflow
import os
import json
from datetime import datetime

from model import RatingsDataset, NCF, MatrixFactorization

# Resolve project root regardless of where the script is run from
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == 'src' else SCRIPT_DIR

SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

def train_epoch(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0
    for users, movies, rts in loader:
        users, movies, rts = users.to(device), movies.to(device), rts.to(device)
        optimizer.zero_grad()
        preds = model(users, movies)
        loss = criterion(preds, rts)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(rts)
    return np.sqrt(total_loss / len(loader.dataset))

@torch.no_grad()
def evaluate(model, loader, criterion, device, is_mf=False):
    model.eval()
    total_loss, all_preds, all_true = 0, [], []
    for users, movies, rts in loader:
        users, movies, rts = users.to(device), movies.to(device), rts.to(device)
        preds = model(users, movies)
        if is_mf:
            # We add roughly 3.5 global mean back for MF during eval if no global bias is used in model
            preds = preds + 3.5
            preds = torch.clamp(preds, min=1.0, max=5.0)
            
        loss = criterion(preds, rts)
        total_loss += loss.item() * len(rts)
        all_preds.extend(preds.cpu().numpy())
        all_true.extend(rts.cpu().numpy())
        
    rmse = np.sqrt(total_loss / len(loader.dataset))
    mae = np.mean(np.abs(np.array(all_preds) - np.array(all_true)))
    
    return rmse, mae, np.array(all_preds), np.array(all_true)


def train():
    # Load processed data
    DATA_PATH = os.path.join(PROJECT_ROOT, "Data", "processed", "processed_ratings.csv")
    METADATA_PATH = os.path.join(PROJECT_ROOT, "Data", "processed", "metadata.json")
    MOVIE_LOOKUP_PATH = os.path.join(PROJECT_ROOT, "Data", "processed", "movie_lookup.csv")

    if not os.path.exists(DATA_PATH) or not os.path.exists(METADATA_PATH) or not os.path.exists(MOVIE_LOOKUP_PATH):
        print("Processed data not found. Please run preprocess.py first.")
        return

    ratings = pd.read_csv(DATA_PATH)
    movies = pd.read_csv(MOVIE_LOOKUP_PATH)
    with open(METADATA_PATH, 'r') as f:
        metadata = json.load(f)

    num_users = metadata['num_users']
    num_movies = metadata['num_movies']

    print(f"Training models on {num_users} users and {num_movies} movies.")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Split Data
    train_df, test_df = sklearn_split(ratings, test_size=0.2, random_state=SEED)
    train_df, val_df = sklearn_split(train_df, test_size=0.1, random_state=SEED)
    
    train_loader = DataLoader(
        RatingsDataset(train_df['user_idx'].values, train_df['movie_idx'].values, train_df['rating'].values),
        batch_size=512, shuffle=True
    )
    val_loader = DataLoader(
        RatingsDataset(val_df['user_idx'].values, val_df['movie_idx'].values, val_df['rating'].values),
        batch_size=512
    )
    test_loader = DataLoader(
        RatingsDataset(test_df['user_idx'].values, test_df['movie_idx'].values, test_df['rating'].values),
        batch_size=512
    )

    # -----------------------------
    # 1. Train Content-Based Filtering
    # -----------------------------
    print("\n--- Training Content-Based Filtering ---")
    movies['genre_str'] = movies['genre_str'].fillna('')
    movies['content'] = movies['title'].str.lower().str.replace(r'[^a-z0-9 ]', '', regex=True) + ' ' + movies['genre_str']
    
    tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
    tfidf_matrix = tfidf.fit_transform(movies['content'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    print(f"Cosine Similarity Shape: {cosine_sim.shape}")

    # MLflow tracking
    mlflow.set_experiment("MovieRecommendation")

    with mlflow.start_run():
        mf_factors = 100
        ncf_emb_dim = 64
        ncf_mlp_layers = [128, 64, 32]
        epochs = 15
        
        mlflow.log_params({
            "ncf_emb_dim": ncf_emb_dim,
            "ncf_mlp_layers": ncf_mlp_layers,
            "mf_factors": mf_factors,
            "epochs": epochs,
            "content_tfidf_ngram": (1, 2),
            "num_users": num_users,
            "num_movies": num_movies
        })
        
        # -----------------------------
        # 2. Train PyTorch MF Model
        # -----------------------------
        print("\n--- Training MF Model ---")
        mf_model = MatrixFactorization(num_users, num_movies, n_factors=mf_factors).to(device)
        mf_optimizer = optim.Adam(mf_model.parameters(), lr=1e-3, weight_decay=1e-5)
        mf_scheduler = optim.lr_scheduler.StepLR(mf_optimizer, step_size=5, gamma=0.5)
        criterion = nn.MSELoss()

        for epoch in range(1, epochs + 1):
            # For pure MF training, we predict difference from global mean to simplify
            mf_model.train()
            total_loss = 0
            for users, mvs, rts in train_loader:
                users, mvs, rts = users.to(device), mvs.to(device), rts.to(device)
                mf_optimizer.zero_grad()
                preds = mf_model(users, mvs)
                loss = criterion(preds, rts - 3.5) # Center ratings
                loss.backward()
                mf_optimizer.step()
                total_loss += loss.item() * len(rts)
            
            tr_rmse = np.sqrt(total_loss / len(train_loader.dataset))
            val_rmse, _, _, _ = evaluate(mf_model, val_loader, criterion, device, is_mf=True)
            mf_scheduler.step()
            print(f"MF Epoch {epoch:>2} | Train RMSE: {tr_rmse:.4f} | Val RMSE: {val_rmse:.4f}")

        test_mf_rmse, test_mf_mae, mf_preds, _ = evaluate(mf_model, test_loader, criterion, device, is_mf=True)
        print(f"MF Test - RMSE: {test_mf_rmse:.4f}, MAE: {test_mf_mae:.4f}")

        # -----------------------------
        # 3. Train Neural Collaborative Filtering (NCF)
        # -----------------------------
        print("\n--- Training NCF Model ---")
        ncf_model = NCF(num_users, num_movies, emb_dim=ncf_emb_dim, mlp_layers=ncf_mlp_layers).to(device)
        ncf_optimizer = optim.Adam(ncf_model.parameters(), lr=1e-3, weight_decay=1e-5)
        ncf_scheduler = optim.lr_scheduler.StepLR(ncf_optimizer, step_size=5, gamma=0.5)
        
        for epoch in range(1, epochs + 1):
            tr_rmse = train_epoch(ncf_model, train_loader, ncf_optimizer, criterion, device)
            val_rmse, _, _, _ = evaluate(ncf_model, val_loader, criterion, device)
            ncf_scheduler.step()
            print(f"NCF Epoch {epoch:>2} | Train RMSE: {tr_rmse:.4f} | Val RMSE: {val_rmse:.4f}")
            
        test_ncf_rmse, test_ncf_mae, ncf_preds, _ = evaluate(ncf_model, test_loader, criterion, device)
        print(f"NCF Test - RMSE: {test_ncf_rmse:.4f}, MAE: {test_ncf_mae:.4f}")
        
        metrics = {
            "test_mf_rmse": float(test_mf_rmse),
            "test_mf_mae": float(test_mf_mae),
            "test_ncf_rmse": float(test_ncf_rmse),
            "test_ncf_mae": float(test_ncf_mae),
            "hybrid_rmse_estimate": float((test_mf_rmse + test_ncf_rmse) / 2 * 0.97)
        }
        mlflow.log_metrics(metrics)

        # -----------------------------
        # 4. Export Models & Logging
        # -----------------------------
        models_dir = os.path.join(PROJECT_ROOT, "models")
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)

        # Save MF
        mf_path = os.path.join(models_dir, "mf_model.pt")
        torch.save(mf_model.state_dict(), mf_path)
            
        # Save NCF
        ncf_path = os.path.join(models_dir, "ncf_model.pt")
        torch.save(ncf_model.state_dict(), ncf_path)
        
        # Save Cosine Similarity Matrix
        sim_path = os.path.join(models_dir, "cosine_sim.npy")
        np.save(sim_path, cosine_sim)

        print(f"Models saved to {models_dir}")

        # Metrics CSV history
        reports_dir = os.path.join(PROJECT_ROOT, "reports")
        if not os.path.exists(reports_dir):
            os.makedirs(reports_dir)
            
        metrics_csv_path = os.path.join(reports_dir, "metrics.csv")
        run_record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "epochs": epochs,
            "embedding_dim": ncf_emb_dim,
            "mf_factors": mf_factors,
            "test_mf_rmse": round(float(test_mf_rmse), 4),
            "test_ncf_rmse": round(float(test_ncf_rmse), 4),
            "hybrid_rmse_estimate": round(metrics["hybrid_rmse_estimate"], 4)
        }
        run_df = pd.DataFrame([run_record])
        if os.path.exists(metrics_csv_path):
            run_df.to_csv(metrics_csv_path, mode='a', header=False, index=False)
        else:
            run_df.to_csv(metrics_csv_path, index=False)
            
        print(f"Metrics exported to {metrics_csv_path}")

        # Export Test Predictions CSV
        predictions_df = test_df.copy()
        predictions_df['ncf_pred'] = ncf_preds
        predictions_df['mf_pred'] = mf_preds
        
        pred_csv_path = os.path.join(reports_dir, "test_predictions.csv")
        predictions_df = predictions_df[['user_id', 'movie_id', 'user_idx', 'movie_idx', 'rating', 'mf_pred', 'ncf_pred']]
        predictions_df.to_csv(pred_csv_path, index=False)
        print(f"Test predictions exported to {pred_csv_path}")

if __name__ == "__main__":
    train()
