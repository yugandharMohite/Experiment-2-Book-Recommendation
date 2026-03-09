import torch
import torch.nn as nn
from torch.utils.data import Dataset
import numpy as np

class RatingsDataset(Dataset):
    def __init__(self, user_indices, movie_indices, ratings):
        self.users = torch.LongTensor(user_indices)
        self.movies = torch.LongTensor(movie_indices)
        self.ratings = torch.FloatTensor(ratings)

    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, i):
        return self.users[i], self.movies[i], self.ratings[i]

class MatrixFactorization(nn.Module):
    """Pure PyTorch implementation of Matrix Factorization (like SVD)"""
    def __init__(self, n_users, n_movies, n_factors=100):
        super().__init__()
        self.user_factors = nn.Embedding(n_users, n_factors)
        self.movie_factors = nn.Embedding(n_movies, n_factors)
        self.user_biases = nn.Embedding(n_users, 1)
        self.movie_biases = nn.Embedding(n_movies, 1)
        
        # initialize
        self.user_factors.weight.data.normal_(0, 0.1)
        self.movie_factors.weight.data.normal_(0, 0.1)
        self.user_biases.weight.data.zero_()
        self.movie_biases.weight.data.zero_()

    def forward(self, user, movie):
        pred = self.user_biases(user) + self.movie_biases(movie)
        pred += (self.user_factors(user) * self.movie_factors(movie)).sum(1, keepdim=True)
        return pred.squeeze()

class NCF(nn.Module):
    """Neural Collaborative Filtering: GMF + MLP fusion"""
    def __init__(self, n_users, n_movies, emb_dim=64, mlp_layers=[128, 64, 32]):
        super().__init__()
        # GMF embeddings
        self.gmf_user = nn.Embedding(n_users, emb_dim)
        self.gmf_movie = nn.Embedding(n_movies, emb_dim)
        
        # MLP embeddings
        self.mlp_user = nn.Embedding(n_users, emb_dim)
        self.mlp_movie = nn.Embedding(n_movies, emb_dim)

        # MLP tower
        layers = []
        in_dim = emb_dim * 2
        for out_dim in mlp_layers:
            layers += [nn.Linear(in_dim, out_dim), nn.ReLU(), nn.Dropout(0.2)]
            in_dim = out_dim
        self.mlp = nn.Sequential(*layers)

        # Output
        self.output = nn.Linear(emb_dim + mlp_layers[-1], 1)

        self._init_weights()

    def _init_weights(self):
        for emb in [self.gmf_user, self.gmf_movie, self.mlp_user, self.mlp_movie]:
            nn.init.normal_(emb.weight, std=0.01)

    def forward(self, user, movie):
        # GMF path
        gmf = self.gmf_user(user) * self.gmf_movie(movie)
        # MLP path
        mlp_in = torch.cat([self.mlp_user(user), self.mlp_movie(movie)], dim=1)
        mlp_out = self.mlp(mlp_in)
        # Concat and predict
        out = self.output(torch.cat([gmf, mlp_out], dim=1))
        # Scale to [1, 5] range
        return out.squeeze() * 4 + 1
        
class HybridRecommender:
    """
    Weighted hybrid of:
      - PyTorch Matrix Factorization (MF)
      - NCF deep learning model
      - Content-based similarity boosting
    """
    def __init__(self, mf_model, ncf_model, cosine_sim, movie_lookup,
                 user_map, movie_map,
                 w_svd=0.45, w_ncf=0.45, w_content=0.10):
        self.mf = mf_model
        self.ncf = ncf_model
        self.cosine_sim = cosine_sim
        self.movie_lookup = movie_lookup
        
        self.user_map = {str(k): int(v) for k, v in user_map.items()}
        self.movie_map = {int(k): int(v) for k, v in movie_map.items()}
        self.reverse_movie_map = {v: k for k, v in self.movie_map.items()}
        
        self.w_svd = w_svd
        self.w_ncf = w_ncf
        self.w_content = w_content
        
        self.device = next(ncf_model.parameters()).device

    def _mf_predict(self, user_idx, movie_ids):
        """Batch MF predictions for a user."""
        valid_mids = []
        m_idxs = []
        for mid in movie_ids:
            if mid in self.movie_map:
                valid_mids.append(mid)
                m_idxs.append(self.movie_map[mid])

        if not valid_mids:
            return {mid: 3.0 for mid in movie_ids}

        u_tensor = torch.LongTensor([user_idx] * len(valid_mids)).to(self.device)
        m_tensor = torch.LongTensor(m_idxs).to(self.device)

        self.mf.eval()
        with torch.no_grad():
            # Add a global mean of roughly 3.5 to MF predictions for stability 
            # if we didn't add it globally during training bias formulation
            preds = self.mf(u_tensor, m_tensor).cpu().numpy() + 3.5
            
        if preds.ndim == 0:
            preds = np.array([preds])
            
        preds = np.clip(preds, 1, 5)
        result = {mid: float(p) for mid, p in zip(valid_mids, preds)}
        
        # Default for unseen
        for mid in movie_ids:
            if mid not in result:
                result[mid] = 3.0
        return result

    def _ncf_predict(self, user_idx, movie_ids):
        """Batch NCF predictions for a user."""
        valid_mids = []
        m_idxs = []
        for mid in movie_ids:
            if mid in self.movie_map:
                valid_mids.append(mid)
                m_idxs.append(self.movie_map[mid])

        if not valid_mids:
            return {mid: 3.0 for mid in movie_ids}

        u_tensor = torch.LongTensor([user_idx] * len(valid_mids)).to(self.device)
        m_tensor = torch.LongTensor(m_idxs).to(self.device)

        self.ncf.eval()
        with torch.no_grad():
            preds = self.ncf(u_tensor, m_tensor).cpu().numpy()
            
        if preds.ndim == 0:
            preds = np.array([preds])
            
        preds = np.clip(preds, 1, 5)
        result = {mid: float(p) for mid, p in zip(valid_mids, preds)}
        
        # Default for unseen
        for mid in movie_ids:
            if mid not in result:
                result[mid] = 3.0
        return result

    def _content_boost(self, user_id, candidate_ids, ratings_df, top_k_liked=5):
        """Compute average content similarity to user's top-rated movies."""
        if ratings_df is None:
             return {mid: 0.0 for mid in candidate_ids}
             
        user_ratings = ratings_df[ratings_df['user_id'] == user_id]
        liked = user_ratings.nlargest(top_k_liked, 'rating')['movie_id'].tolist()
        
        if not liked:
            return {mid: 0.0 for mid in candidate_ids}

        boosts = {}
        for mid in candidate_ids:
            if mid not in self.movie_map:
                boosts[mid] = 0.0
                continue
            c_idx = self.movie_map[mid]
            sims = []
            for liked_mid in liked:
                if liked_mid in self.movie_map:
                    l_idx = self.movie_map[liked_mid]
                    sims.append(self.cosine_sim[c_idx, l_idx])
            boosts[mid] = float(np.mean(sims)) if sims else 0.0
        return boosts

    def recommend(self, user_id, n=10, ratings_df=None, exclude_seen=True):
        """Generate top-N recommendations for a user."""
        if str(user_id) not in self.user_map:
             return []
             
        user_idx = self.user_map[str(user_id)]
             
        seen = set()
        if exclude_seen and ratings_df is not None:
            seen = set(ratings_df[ratings_df['user_id'] == user_id]['movie_id'])
            
        all_movie_ids = list(self.movie_map.keys())
        candidates = [mid for mid in all_movie_ids if mid not in seen]

        # MF (SVD) predictions
        mf_preds = self._mf_predict(user_idx, candidates)

        # NCF predictions
        ncf_preds = self._ncf_predict(user_idx, candidates)

        # Content boost
        content_raw = self._content_boost(user_id, candidates, ratings_df)
        max_c = max(content_raw.values()) if content_raw and max(content_raw.values()) > 0 else 1
        content_preds = {mid: 1 + 4 * (v / max_c) for mid, v in content_raw.items()}

        # Weighted blend
        scores = {
            mid: self.w_svd * mf_preds[mid]
                 + self.w_ncf * ncf_preds[mid]
                 + self.w_content * content_preds.get(mid, 3.0)
            for mid in candidates
        }

        top_ids = sorted(scores, key=scores.get, reverse=True)[:n]
        
        results = []
        for mid in top_ids:
            info = self.movie_lookup.get(mid, {})
            results.append({
                "movie_id": mid,
                "title": info.get("title", "Unknown"),
                "genre_str": info.get("genre_str", "Unknown"),
                "score": scores[mid],
                "svd_score": mf_preds[mid],
                "ncf_score": ncf_preds[mid]
            })
            
        return results
