"""
Layer 2 — weighted-scoring trajectory aggregator.

For each turn in a conversation, takes the 7-dim trajectory feature vector
produced by `features.compute_trajectory_features` and returns a scalar risk
score reflecting the conversation arc up to that turn.

The weighted-scoring formulation was chosen over a learned sequence model
(e.g., LSTM) for Thesis 1 because each weight maps directly to an OGDM
construct (Lorenzo-Dus et al., 2016), making every contribution to the final
score traceable to a documented behavioral indicator. An LSTM extension is
left as future work (see `experimental/trajectory_model_lstm.py`).

The weights are tuned on the validation set (see `tune_weights.py`) to
maximize recall subject to a precision floor — matching the thesis primary
objective of reducing false negatives.
"""

import json
from pathlib import Path

import numpy as np


# Default weights — placeholders only. These MUST be replaced with values
# produced by tune_weights.py before any evaluation result is reported.
DEFAULT_WEIGHTS = np.array(
    [0.30, 0.30, 0.10, 0.10, 0.05, 0.10, 0.05],
    dtype=np.float32,
)


class WeightedScorer:
    """
    Computes a per-turn risk score = sigmoid(weights · trajectory_features).

    `weights` is a 7-vector aligned with features.FEATURE_NAMES order:
        [peak_score, current_score, spike_count, spike_then_drop,
         rate_of_change, topic_drift, turn_taking_imbalance]
    """

    def __init__(self, weights=None, spike_drop=0.2, flagging_threshold=0.5):
        self.weights = np.asarray(
            weights if weights is not None else DEFAULT_WEIGHTS,
            dtype=np.float32,
        )
        if self.weights.shape != (7,):
            raise ValueError(f"weights must have shape (7,), got {self.weights.shape}")
        self.spike_drop = float(spike_drop)
        self.flagging_threshold = float(flagging_threshold)

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    def score_turn(self, traj_features):
        """One turn → one risk score in [0, 1]."""
        raw = float(np.dot(self.weights, np.asarray(traj_features, dtype=np.float32)))
        return float(self._sigmoid(raw))

    def score_sequence(self, traj_features_per_turn):
        """
        Vectorized: an array of shape (T, 7) → array of shape (T,) of risk scores.
        """
        feats = np.asarray(traj_features_per_turn, dtype=np.float32)
        if feats.ndim != 2 or feats.shape[1] != 7:
            raise ValueError(f"expected (T, 7); got {feats.shape}")
        raw = feats @ self.weights
        return self._sigmoid(raw)

    # -- persistence --

    def to_dict(self):
        return {
            "weights": self.weights.tolist(),
            "spike_drop": self.spike_drop,
            "flagging_threshold": self.flagging_threshold,
        }

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Saved weighted scorer config to {path}")

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            weights=np.array(data["weights"], dtype=np.float32),
            spike_drop=data["spike_drop"],
            flagging_threshold=data["flagging_threshold"],
        )
