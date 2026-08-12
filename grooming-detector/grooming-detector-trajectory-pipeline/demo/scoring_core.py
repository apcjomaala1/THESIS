"""
Shared scoring core used by both demo modes.

A `LiveConversation` masks common direct identifiers, accumulates messages turn by turn, scores each one with
Layer 1, computes the trajectory features against the loaded benign centroid,
applies both the saved author-disjoint LSTM and the weighted comparator, and
tracks the LSTM's first-flagged turn (time to detection). The PAN12 replay
panel and the live-typed chat UI both drive this same object.
"""

import json
import sys
from pathlib import Path

import numpy as np
import torch

# Allow running `python -m demo.replay` from the package root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from features import (
    MessageEncoder,
    compute_trajectory_features,
    FEATURE_NAMES,
)
from message_classifier import MessageClassifier
from privacy import redact_text
from trajectory_model_lstm import load_trajectory_model
from weighted_scorer import WeightedScorer


HERE = Path(__file__).resolve().parent.parent


class LiveConversation:
    """Stateful per-turn scoring driver. One instance per conversation."""

    def __init__(self, classifier, encoder, centroid, scorer, lstm_model, lstm_threshold):
        self.classifier = classifier
        self.encoder = encoder
        self.centroid = centroid
        self.scorer = scorer
        self.lstm_model = lstm_model
        self.lstm_threshold = float(lstm_threshold)

        self.texts = []
        self.authors = []
        self.risk_scores = []
        self.embeddings = []
        self.trajectory_history = []
        self.turn_scores = []
        self.weighted_scores = []
        self.first_flagged_turn = None

    def add_message(self, text, author):
        text = redact_text(text.strip())
        if not text:
            return None
        self.texts.append(text)
        self.authors.append(author)

        risk = float(self.classifier.score(text))
        self.risk_scores.append(risk)

        emb = self.encoder.encode_single(text)
        self.embeddings.append(emb)

        traj = compute_trajectory_features(
            risk_scores_so_far=self.risk_scores,
            embeddings_so_far=self.embeddings,
            texts_so_far=self.texts,
            authors_so_far=self.authors,
            benign_centroid=self.centroid,
            spike_drop=self.scorer.spike_drop,
        )
        self.trajectory_history.append(traj.tolist())

        weighted_score = float(self.scorer.score_turn(traj))
        self.weighted_scores.append(weighted_score)

        sequence = np.concatenate(
            [np.asarray(self.embeddings), np.asarray(self.trajectory_history)], axis=-1
        )
        device = next(self.lstm_model.parameters()).device
        x_tensor = torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(device)
        with torch.no_grad():
            turn_score = float(self.lstm_model(x_tensor)[0, -1].cpu())
        self.turn_scores.append(turn_score)

        flagged = turn_score > self.lstm_threshold
        if flagged and self.first_flagged_turn is None:
            self.first_flagged_turn = len(self.texts) - 1

        return {
            "turn": len(self.texts) - 1,
            "text": text,
            "author": author,
            "risk_score": risk,
            "trajectory_features": dict(zip(FEATURE_NAMES, traj.tolist())),
            "turn_score": turn_score,
            "lstm_score": turn_score,
            "lstm_threshold": self.lstm_threshold,
            "weighted_score": weighted_score,
            "weighted_threshold": self.scorer.flagging_threshold,
            "flagged_now": flagged,
            "first_flagged_turn": self.first_flagged_turn,
        }


def build_scoring_stack(
    classifier_path=HERE.parent / "trained_model_distillbert/final_moderation_model",
    centroid_path=HERE / "benign_centroid.npy",
    scorer_path=HERE / "weighted_scorer.json",
    lstm_path=HERE / "trajectory_model_author_disjoint.pt",
    evaluation_path=HERE / "lstm_author_disjoint_evaluation.json",
):
    """Load the provisional fixed-Layer-1 demonstration stack."""
    classifier = MessageClassifier(model_path=classifier_path)
    encoder = MessageEncoder()
    centroid = np.load(centroid_path)
    if centroid.shape != (768,):
        raise ValueError(f"centroid must be (768,), got {centroid.shape}")
    scorer = WeightedScorer.load(scorer_path)
    lstm_model = load_trajectory_model(lstm_path)

    # Match the validation-selected threshold used in the frozen evaluation.
    evaluation_path = Path(evaluation_path)
    if evaluation_path.exists():
        report = json.loads(evaluation_path.read_text(encoding="utf-8"))
        lstm_threshold = report["validation_lstm"]["threshold"]
    else:
        lstm_threshold = getattr(lstm_model, "selection_metadata", {}).get("threshold", 0.5)

    return classifier, encoder, centroid, scorer, lstm_model, lstm_threshold


def new_conversation(stack):
    return LiveConversation(*stack)
