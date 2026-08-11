"""
trajectory_model.py
Layer 2 -- LSTM that reads sequences of (DistilBERT embedding + trajectory features)
and outputs a continuous risk score per turn reflecting the full conversation arc.
"""

import torch
import torch.nn as nn
import numpy as np
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import roc_auc_score, fbeta_score
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
        conversation_label = torch.tensor(float(conv["conversation_label"]), dtype=torch.float32)
        return x, labels, conversation_label


def collate_fn(batch):
    """Pad sequences to same length within batch."""
    xs, ys, conversation_labels = zip(*batch)
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

    return padded_xs, padded_ys, mask, torch.tensor(lengths), torch.stack(conversation_labels)


# -- training --

def _best_turn_threshold(scores, labels):
    """Select validation threshold by F0.5 without inspecting test labels."""
    scores = np.asarray(scores, dtype=np.float32)
    labels = np.asarray(labels, dtype=np.int64)
    if len(scores) == 0 or labels.sum() == 0:
        return 0.5, 0.0
    best_threshold, best_f05 = 0.5, -1.0
    for threshold in np.unique(np.quantile(scores, np.linspace(0.01, 0.99, 199))):
        f05 = fbeta_score(labels, scores >= threshold, beta=0.5, zero_division=0)
        if f05 > best_f05:
            best_threshold, best_f05 = float(threshold), float(f05)
    return best_threshold, best_f05


def _conversation_validation_metrics(model, loader, device):
    """Evaluate the same conversation-level target used by the final benchmark."""
    model.eval()
    scores, labels = [], []
    with torch.no_grad():
        for x, _, mask, _, conv_y in loader:
            x, mask = x.to(device), mask.to(device)
            batch_scores = model(x).masked_fill(~mask, 0.0).max(dim=1).values
            scores.extend(batch_scores.cpu().numpy().tolist())
            labels.extend(conv_y.numpy().astype(int).tolist())
    scores = np.asarray(scores, dtype=np.float32)
    labels = np.asarray(labels, dtype=np.int64)
    candidates = np.unique(np.quantile(scores, np.linspace(0.01, 0.99, 199)))
    best_threshold, best_f05 = 0.5, -1.0
    for threshold in candidates:
        f05 = fbeta_score(labels, scores >= threshold, beta=0.5, zero_division=0)
        if f05 > best_f05:
            best_threshold, best_f05 = float(threshold), float(f05)
    auc = float(roc_auc_score(labels, scores)) if len(np.unique(labels)) == 2 else 0.0
    return best_threshold, best_f05, auc


def train_trajectory_model(
    train_convs, val_convs, epochs=10, batch_size=16, lr=1e-3,
    device=None, positive_weight=None, conversation_loss_weight=1.0,
    random_state=42,
):
    """
    Train LSTM trajectory model.

    train_convs / val_convs: list of conversation dicts (see ConversationDataset)
    """
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training trajectory model on {device}")

    np.random.seed(random_state)
    torch.manual_seed(random_state)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    data_generator = torch.Generator()
    data_generator.manual_seed(random_state)

    train_dataset = ConversationDataset(train_convs)
    val_dataset = ConversationDataset(val_convs)
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=collate_fn,
        generator=data_generator,
    )
    val_loader = DataLoader(val_dataset, batch_size=batch_size, collate_fn=collate_fn)

    model = TrajectoryLSTM().to(device)
    train_labels = np.concatenate([np.asarray(c["labels"], dtype=np.float32) for c in train_convs])
    positives = float(train_labels.sum())
    negatives = float(len(train_labels) - positives)
    positive_weight = float(positive_weight or negatives / max(positives, 1.0))
    conversation_labels = np.asarray([c["conversation_label"] for c in train_convs], dtype=np.float32)
    conversation_positive_weight = float(
        (len(conversation_labels) - conversation_labels.sum()) / max(conversation_labels.sum(), 1.0)
    )
    print(f"Using positive loss weight: {positive_weight:.3f} "
          f"({int(positives)} positive / {int(negatives)} negative training turns)")
    print(f"Using conversation loss weight: {conversation_loss_weight:.3f}; "
          f"conversation positive multiplier: {conversation_positive_weight:.3f}")
    criterion = nn.BCELoss(reduction="none")
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    best_val_auc = 0.0
    best_val_f05 = -1.0
    best_threshold = 0.5
    best_state = None

    for epoch in range(epochs):
        model.train()
        total_loss = 0
        for x, y, mask, lengths, conv_y in tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}"):
            x, y, mask, conv_y = x.to(device), y.to(device), mask.to(device), conv_y.to(device)
            optimizer.zero_grad()
            scores = model(x)
            loss = criterion(scores, y)
            loss = loss * torch.where(y > 0.5, positive_weight, 1.0)
            # mask out padding
            turn_loss = (loss * mask.float()).sum() / mask.float().sum()
            conversation_scores = scores.masked_fill(~mask, 0.0).max(dim=1).values
            conversation_loss = criterion(conversation_scores, conv_y)
            conversation_loss = (conversation_loss * torch.where(
                conv_y > 0.5, conversation_positive_weight, 1.0,
            )).mean()
            loss = turn_loss + float(conversation_loss_weight) * conversation_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        print(f"  Train loss: {total_loss / len(train_loader):.4f}")

        # validation
        val_scores, val_labels = evaluate_trajectory_model(model, val_loader, device)
        try:
            auc = roc_auc_score(val_labels, val_scores)
        except ValueError:
            auc = 0.0
        threshold, f05, conversation_auc = _conversation_validation_metrics(model, val_loader, device)
        print(f"  Turn AUC: {auc:.4f}; Conversation AUC: {conversation_auc:.4f}; "
              f"conversation F0.5: {f05:.4f} at threshold {threshold:.6f}")

        if f05 > best_val_f05 or (f05 == best_val_f05 and conversation_auc >= best_val_auc):
            best_val_f05 = f05
            best_val_auc = float(conversation_auc)
            best_threshold = float(threshold)
            best_state = {k: v.clone() for k, v in model.state_dict().items()}

    if best_state:
        model.load_state_dict(best_state)
        model.selection_metadata = {
            "positive_weight": positive_weight,
            "validation_conversation_auc": best_val_auc,
            "validation_conversation_f0_5": float(best_val_f05),
            "threshold": best_threshold,
            "random_state": int(random_state),
        }
        print(f"Restored best model (conversation val F0.5 {best_val_f05:.4f}, AUC {best_val_auc:.4f}, "
              f"threshold {best_threshold:.6f})")

    return model


def evaluate_trajectory_model(model, loader, device):
    """Returns flat lists of scores and labels across all turns in all conversations."""
    model.eval()
    all_scores, all_labels = [], []
    with torch.no_grad():
        for x, y, mask, lengths, conversation_labels in loader:
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
    torch.save({
        "model_state": model.state_dict(),
        "selection_metadata": getattr(model, "selection_metadata", {}),
    }, path)
    print(f"Saved trajectory model to {path}")


def load_trajectory_model(path="trajectory_model.pt", device=None):
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = TrajectoryLSTM().to(device)
    # Checkpoints are produced locally by save_trajectory_model and contain
    # model weights plus scalar selection metadata.
    checkpoint = torch.load(path, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    model.selection_metadata = checkpoint.get("selection_metadata", {})
    model.eval()
    return model
