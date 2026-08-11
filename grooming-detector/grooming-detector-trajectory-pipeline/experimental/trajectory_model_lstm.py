"""
trajectory_model.py
Layer 2 -- LSTM that reads sequences of (DistilBERT embedding + trajectory features)
and outputs a continuous risk score per turn reflecting the full conversation arc.
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, classification_report
from tqdm import tqdm

EMBEDDING_DIM = 768
TRAJECTORY_FEATURE_DIM = 7
INPUT_DIM = EMBEDDING_DIM + TRAJECTORY_FEATURE_DIM
HIDDEN_DIM = 256


# -- model --

class TrajectoryLSTM(nn.Module):
    def __init__(self, input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout,
        )
        self.dropout = nn.Dropout(dropout)
        self.output_layer = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, lengths=None):
        """
        x: (batch, seq_len, input_dim)
        lengths: actual lengths of each sequence in batch (for padding)
        Returns risk scores: (batch, seq_len)
        """
        lstm_out, _ = self.lstm(x)
        lstm_out = self.dropout(lstm_out)
        scores = self.sigmoid(self.output_layer(lstm_out)).squeeze(-1)
        return scores


# -- dataset --

class ConversationDataset(Dataset):
    """
    Each item is a full conversation represented as a sequence of
    (embedding + trajectory_features) vectors with a label per turn.
    """
    def __init__(self, conversations):
        """
        conversations: list of dicts with keys:
            embeddings: np.array (seq_len, 768)
            trajectory_features: np.array (seq_len, 7)
            labels: np.array (seq_len,) -- cumulative label per turn
        """
        self.conversations = conversations

    def __len__(self):
        return len(self.conversations)

    def __getitem__(self, idx):
        conv = self.conversations[idx]
        embeddings = torch.tensor(conv["embeddings"], dtype=torch.float32)
        traj_feats = torch.tensor(conv["trajectory_features"], dtype=torch.float32)
        x = torch.cat([embeddings, traj_feats], dim=-1)  # (seq_len, 775)
        labels = torch.tensor(conv["labels"], dtype=torch.float32)
        return x, labels


def collate_fn(batch):
    """Pad sequences to same length within batch."""
    xs, ys = zip(*batch)
    lengths = [x.shape[0] for x in xs]
    max_len = max(lengths)

    padded_xs = torch.zeros(len(xs), max_len, xs[0].shape[1])
    padded_ys = torch.zeros(len(ys), max_len)
    mask = torch.zeros(len(xs), max_len, dtype=torch.bool)

    for i, (x, y) in enumerate(zip(xs, ys)):
        l = x.shape[0]
        padded_xs[i, :l] = x
        padded_ys[i, :l] = y
        mask[i, :l] = True

    return padded_xs, padded_ys, mask, torch.tensor(lengths)


# -- training --

def train_trajectory_model(train_convs, val_convs, epochs=10, batch_size=16, lr=1e-3, device=None):
    """
    Train LSTM trajectory model.

    train_convs / val_convs: list of conversation dicts (see ConversationDataset)
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training trajectory model on {device}")

    train_dataset = ConversationDataset(train_convs)
    val_dataset = ConversationDataset(val_convs)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, collate_fn=collate_fn)

    model = TrajectoryLSTM().to(device)
    criterion = nn.BCELoss(reduction="none")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_val_auc = 0
    best_state = None

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x, y, mask, lengths in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            x, y, mask = x.to(device), y.to(device), mask.to(device)
            optimizer.zero_grad()
            scores = model(x)
            loss = criterion(scores, y)
            # mask out padding
            loss = (loss * mask.float()).sum() / mask.float().sum()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        print(f"  Train loss: {total_loss / len(train_loader):.4f}")

        # validation
        val_scores, val_labels = evaluate_trajectory_model(model, val_loader, device)
        auc = roc_auc_score(val_labels, val_scores)
        preds = (np.array(val_scores) > 0.5).astype(int)
        print(f"  Val AUC: {auc:.4f}")
        print(classification_report(val_labels, preds, target_names=["benign", "predatory"], zero_division=0))

        if auc > best_val_auc:
            best_val_auc = auc
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

    if best_state:
        model.load_state_dict(best_state)
        print(f"Restored best model (val AUC {best_val_auc:.4f})")

    return model


def evaluate_trajectory_model(model, loader, device):
    """Returns flat lists of scores and labels across all turns in all conversations."""
    model.eval()
    all_scores, all_labels = [], []
    with torch.no_grad():
        for x, y, mask, lengths in loader:
            x = x.to(device)
            scores = model(x).cpu().numpy()
            y = y.numpy()
            mask = mask.numpy()
            for i in range(len(lengths)):
                l = int(lengths[i])
                all_scores.extend(scores[i, :l].tolist())
                all_labels.extend(y[i, :l].tolist())
    return all_scores, all_labels


def save_trajectory_model(model, path="trajectory_model.pt"):
    torch.save({"model_state": model.state_dict()}, path)
    print(f"Saved trajectory model to {path}")


def load_trajectory_model(path="trajectory_model.pt", device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = TrajectoryLSTM().to(device)
    checkpoint = torch.load(path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model
