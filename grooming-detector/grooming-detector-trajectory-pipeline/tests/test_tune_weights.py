"""Tests for the validation-set tuner."""

import numpy as np
import pytest

from tune_weights import conversation_metrics, evaluate_configuration, search
from weighted_scorer import WeightedScorer


def test_conversation_metrics_perfect():
    preds = np.array([1, 1, 0, 0])
    labels = np.array([1, 1, 0, 0])
    recall, precision, f1 = conversation_metrics(preds, labels)
    assert recall == precision == f1 == 1.0


def test_conversation_metrics_all_wrong():
    preds = np.array([0, 0, 1, 1])
    labels = np.array([1, 1, 0, 0])
    recall, precision, f1 = conversation_metrics(preds, labels)
    assert recall == 0.0
    assert precision == 0.0
    assert f1 == 0.0


def test_evaluate_configuration_flags_strong_scores():
    # 2 strong-feature predatory convs, 2 quiet benign convs.
    val = [
        {
            "trajectory_features": np.array([[0.9, 0.9, 5, 1, 0.5, 0.9, 0.3]] * 3, dtype=np.float32),
            "conversation_label": 1,
        },
        {
            "trajectory_features": np.array([[0.85, 0.85, 4, 1, 0.4, 0.8, 0.2]] * 3, dtype=np.float32),
            "conversation_label": 1,
        },
        {
            "trajectory_features": np.zeros((3, 7), dtype=np.float32),
            "conversation_label": 0,
        },
        {
            "trajectory_features": np.zeros((3, 7), dtype=np.float32),
            "conversation_label": 0,
        },
    ]
    scorer = WeightedScorer(
        weights=np.ones(7, dtype=np.float32),
        spike_drop=0.2,
        flagging_threshold=0.6,
    )
    recall, precision, f1 = evaluate_configuration(scorer, val)
    assert recall == 1.0
    assert precision == 1.0


def test_search_returns_required_keys(monkeypatch):
    # Shrink grids to keep the test fast.
    import tune_weights as tw
    monkeypatch.setattr(tw, "WEIGHT_GRID", [0.0, 1.0])
    monkeypatch.setattr(tw, "SPIKE_DROP_GRID", [0.2])
    monkeypatch.setattr(tw, "FLAG_THRESHOLD_GRID", [0.5, 0.7])

    val = [
        {
            "trajectory_features": np.array([[0.9, 0.9, 3, 1, 0.3, 0.8, 0.2]] * 2, dtype=np.float32),
            "conversation_label": 1,
        },
        {
            "trajectory_features": np.zeros((2, 7), dtype=np.float32),
            "conversation_label": 0,
        },
    ]
    best_under, best_f1 = tw.search(val, min_precision=0.5)
    chosen = best_under or best_f1
    for k in ("weights", "spike_drop", "flagging_threshold", "recall", "precision", "f1"):
        assert k in chosen
    assert len(chosen["weights"]) == 7
