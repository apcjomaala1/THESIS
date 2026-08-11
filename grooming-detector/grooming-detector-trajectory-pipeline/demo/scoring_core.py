"""
Shared scoring core used by both demo modes.

A `LiveConversation` accumulates messages turn by turn, scores each one with
Layer 1, computes the trajectory features against the loaded benign centroid,
applies the weighted scorer, and tracks the first-flagged turn (time to
detection). The PAN12 replay panel and the live-typed chat UI both drive
this same object.
"""

import sys
from pathlib import Path

import numpy as np

# Allow running `python -m demo.replay` from the package root.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from features import (
    MessageEncoder,
    compute_trajectory_features,
    FEATURE_NAMES,
)
from message_classifier import MessageClassifier
from weighted_scorer import WeightedScorer


class LiveConversation:
    """Stateful per-turn scoring driver. One instance per conversation."""

    def __init__(self, classifier, encoder, centroid, scorer):
        self.classifier = classifier
        self.encoder = encoder
        self.centroid = centroid
        self.scorer = scorer

        self.texts = []
        self.authors = []
        self.risk_scores = []
        self.embeddings = []
        self.trajectory_history = []
        self.turn_scores = []
        self.first_flagged_turn = None

    def add_message(self, text, author):
        text = text.strip()
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

        turn_score = float(self.scorer.score_turn(traj))
        self.turn_scores.append(turn_score)

        flagged = turn_score > self.scorer.flagging_threshold
        if flagged and self.first_flagged_turn is None:
            self.first_flagged_turn = len(self.texts) - 1

        return {
            "turn": len(self.texts) - 1,
            "text": text,
            "author": author,
            "risk_score": risk,
            "trajectory_features": dict(zip(FEATURE_NAMES, traj.tolist())),
            "turn_score": turn_score,
            "flagged_now": flagged,
            "first_flagged_turn": self.first_flagged_turn,
        }


def build_scoring_stack(
    classifier_path="../trained_model_distillbert/final_moderation_model",
    centroid_path="benign_centroid.npy",
    scorer_path="weighted_scorer.json",
):
    """Load and return (classifier, encoder, centroid, scorer)."""
    classifier = MessageClassifier(model_path=classifier_path)
    encoder = MessageEncoder()
    centroid = np.load(centroid_path)
    if centroid.shape != (768,):
        raise ValueError(f"centroid must be (768,), got {centroid.shape}")
    scorer = WeightedScorer.load(scorer_path)
    return classifier, encoder, centroid, scorer


def new_conversation(stack):
    classifier, encoder, centroid, scorer = stack
    return LiveConversation(classifier, encoder, centroid, scorer)
