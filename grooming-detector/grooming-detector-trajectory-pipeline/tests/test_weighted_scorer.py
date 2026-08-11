"""Tests for the Layer 2 weighted scorer (the OGDM-tied aggregator)."""

import json

import numpy as np
import pytest

from weighted_scorer import WeightedScorer, DEFAULT_WEIGHTS


def test_default_weights_shape():
    w = WeightedScorer()
    assert w.weights.shape == (7,)


def test_rejects_wrong_shape():
    with pytest.raises(ValueError):
        WeightedScorer(weights=np.zeros(6))
    with pytest.raises(ValueError):
        WeightedScorer(weights=np.zeros(8))


def test_score_turn_in_unit_interval():
    w = WeightedScorer()
    s = w.score_turn(np.zeros(7))
    assert 0.0 <= s <= 1.0
    assert s == pytest.approx(0.5)  # sigmoid(0) == 0.5


def test_score_turn_monotonic_in_strong_feature():
    w = WeightedScorer(weights=np.array([1, 0, 0, 0, 0, 0, 0], dtype=np.float32))
    low = w.score_turn(np.array([0.1, 0, 0, 0, 0, 0, 0]))
    high = w.score_turn(np.array([0.9, 0, 0, 0, 0, 0, 0]))
    assert high > low


def test_score_sequence_matches_per_turn():
    w = WeightedScorer()
    feats = np.array([
        [0.3, 0.4, 1.0, 0.0, 0.0, 0.2, 0.1],
        [0.5, 0.6, 2.0, 1.0, 0.2, 0.3, 0.2],
        [0.8, 0.7, 3.0, 1.0, 0.1, 0.4, 0.3],
    ], dtype=np.float32)
    seq = w.score_sequence(feats)
    assert seq.shape == (3,)
    for i, row in enumerate(feats):
        assert seq[i] == pytest.approx(w.score_turn(row), rel=1e-6)


def test_score_sequence_rejects_wrong_dim():
    w = WeightedScorer()
    with pytest.raises(ValueError):
        w.score_sequence(np.zeros((3, 5)))
    with pytest.raises(ValueError):
        w.score_sequence(np.zeros(7))  # not 2-D


def test_save_load_roundtrip(tmp_path):
    weights = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], dtype=np.float32)
    w = WeightedScorer(weights=weights, spike_drop=0.15, flagging_threshold=0.42)
    p = tmp_path / "scorer.json"
    w.save(str(p))

    w2 = WeightedScorer.load(str(p))
    assert np.allclose(w2.weights, weights)
    assert w2.spike_drop == pytest.approx(0.15)
    assert w2.flagging_threshold == pytest.approx(0.42)


def test_save_writes_valid_json(tmp_path):
    p = tmp_path / "scorer.json"
    WeightedScorer().save(str(p))
    data = json.loads(p.read_text(encoding="utf-8"))
    assert set(data.keys()) == {"weights", "spike_drop", "flagging_threshold"}
    assert len(data["weights"]) == 7
