"""
Tests for the 7 trajectory features (pure math; no DistilBERT needed).

Each test pins down ONE behavior so a regression in any feature lights up the
specific assertion. Where the feature operationalizes an OGDM construct, the
test docstring names that construct (Lorenzo-Dus et al., 2016).
"""

import numpy as np
import pytest

from features import (
    compute_trajectory_features,
    FEATURE_NAMES,
    SPIKE_THRESHOLD,
    DEFAULT_SPIKE_DROP,
    TRAJECTORY_FEATURE_DIM,
)


# Indices for readability.
PEAK, CURR, SPIKE_CNT, SPIKE_DROP_F, RATE, DRIFT, IMBAL = range(7)


@pytest.fixture
def centroid():
    rng = np.random.default_rng(0)
    v = rng.standard_normal(768).astype(np.float32)
    return v / np.linalg.norm(v)


def make_emb(seed):
    rng = np.random.default_rng(seed)
    e = rng.standard_normal(768).astype(np.float32)
    return e / np.linalg.norm(e)


def compute(scores, texts, authors, centroid, spike_drop=DEFAULT_SPIKE_DROP):
    embs = [make_emb(i) for i in range(len(scores))]
    return compute_trajectory_features(
        risk_scores_so_far=scores,
        embeddings_so_far=embs,
        texts_so_far=texts,
        authors_so_far=authors,
        benign_centroid=centroid,
        spike_drop=spike_drop,
    )


def test_returns_correct_shape_and_names(centroid):
    feats = compute([0.1], ["hi"], ["A"], centroid)
    assert feats.shape == (TRAJECTORY_FEATURE_DIM,)
    assert len(FEATURE_NAMES) == TRAJECTORY_FEATURE_DIM


def test_peak_never_decreases(centroid):
    feats_a = compute([0.1, 0.8, 0.2], ["a", "b", "c"], ["A", "B", "A"], centroid)
    assert feats_a[PEAK] == pytest.approx(0.8)
    feats_b = compute([0.1, 0.8, 0.2, 0.0], ["a", "b", "c", "d"], ["A", "B", "A", "B"], centroid)
    assert feats_b[PEAK] == pytest.approx(0.8)


def test_current_score_is_last(centroid):
    feats = compute([0.1, 0.9, 0.3], ["a", "b", "c"], ["A", "B", "A"], centroid)
    assert feats[CURR] == pytest.approx(0.3)


def test_spike_count_uses_threshold(centroid):
    # SPIKE_THRESHOLD = 0.5; 0.6 and 0.7 count, 0.5 itself does not (strict >)
    feats = compute([0.1, 0.5, 0.6, 0.7], ["a", "b", "c", "d"], ["A", "B", "A", "B"], centroid)
    assert feats[SPIKE_CNT] == pytest.approx(2.0)


def test_spike_then_drop_fires_for_compliance_testing_pattern(centroid):
    """OGDM compliance testing: a spike above SPIKE_THRESHOLD followed by a
    deliberate retreat of at least `spike_drop`."""
    feats = compute(
        [0.1, 0.8, 0.4, 0.2],
        ["a", "b", "c", "d"],
        ["A", "B", "A", "B"],
        centroid,
        spike_drop=0.2,
    )
    assert feats[SPIKE_DROP_F] == 1.0


def test_spike_then_drop_does_not_fire_for_small_drop(centroid):
    feats = compute(
        [0.1, 0.8, 0.7],  # only a 0.1 drop after spike
        ["a", "b", "c"],
        ["A", "B", "A"],
        centroid,
        spike_drop=0.2,
    )
    assert feats[SPIKE_DROP_F] == 0.0


def test_spike_drop_parameter_is_honored(centroid):
    """With spike_drop=0.5, the 0.3 drop should NOT fire; with 0.2 it should."""
    scores = [0.1, 0.8, 0.5]  # drop of 0.3
    strict = compute(scores, ["a", "b", "c"], ["A", "B", "A"], centroid, spike_drop=0.5)
    lenient = compute(scores, ["a", "b", "c"], ["A", "B", "A"], centroid, spike_drop=0.2)
    assert strict[SPIKE_DROP_F] == 0.0
    assert lenient[SPIKE_DROP_F] == 1.0


def test_rate_of_change_is_last_delta(centroid):
    feats = compute([0.1, 0.4, 0.9], ["a", "b", "c"], ["A", "B", "A"], centroid)
    assert feats[RATE] == pytest.approx(0.5)


def test_rate_of_change_zero_at_first_turn(centroid):
    feats = compute([0.7], ["a"], ["A"], centroid)
    assert feats[RATE] == 0.0


def test_topic_drift_against_fixed_centroid_is_high_when_far(centroid):
    """Topic drift uses a FIXED benign centroid, not the conversation's first
    message — this is the bug fix for OGDM 'approach phase' on PAN12 convs
    where the predator opens with risky content."""
    # Embedding identical to centroid → drift ≈ 0
    embs = [centroid.copy()]
    near = compute_trajectory_features(
        risk_scores_so_far=[0.5],
        embeddings_so_far=embs,
        texts_so_far=["hi"],
        authors_so_far=["A"],
        benign_centroid=centroid,
    )
    assert near[DRIFT] == pytest.approx(0.0, abs=1e-5)

    # Anti-parallel embedding → drift ≈ 2.0 (1 - (-1))
    far = compute_trajectory_features(
        risk_scores_so_far=[0.5],
        embeddings_so_far=[-centroid.copy()],
        texts_so_far=["hi"],
        authors_so_far=["A"],
        benign_centroid=centroid,
    )
    assert far[DRIFT] == pytest.approx(2.0, abs=1e-5)


def test_turn_taking_imbalance_balanced_is_zero(centroid):
    feats = compute(
        [0.1, 0.1, 0.1, 0.1],
        ["hi there", "hello you", "how are you", "I am fine"],
        ["A", "B", "A", "B"],
        centroid,
    )
    # 2 turns each side, perfectly balanced
    assert feats[IMBAL] == pytest.approx(0.0)


def test_turn_taking_imbalance_one_sided(centroid):
    feats = compute(
        [0.1, 0.1, 0.1, 0.1],
        ["msg1", "ok", "msg2", "msg3"],
        ["A", "B", "A", "A"],
        centroid,
    )
    # A: 3 turns; B: 1 turn. |3-1| / 4 = 0.5
    assert feats[IMBAL] == pytest.approx(0.5, abs=1e-6)


def test_turn_taking_imbalance_single_author_returns_zero(centroid):
    feats = compute([0.5], ["only one message"], ["A"], centroid)
    assert feats[IMBAL] == 0.0


def test_turn_taking_imbalance_multi_author_uses_dominant_dyad(centroid):
    """For chat rooms with >2 authors (most PAN12 predator convs), turn-taking
    imbalance is computed over the top-2 turn contributors. OGDM is dyadic;
    multi-party convs are reduced to their dominant pair."""
    # A: 3 turns (dominant), B: 2 turns (second), C: 1 turn (lurker)
    feats = compute(
        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ["a1", "b1", "a2", "b2", "a3", "c1"],
        ["A", "B", "A", "B", "A", "C"],
        centroid,
    )
    # dominant dyad = A (3) and B (2); imbalance = |3-2| / (3+2) = 0.2
    assert feats[IMBAL] == pytest.approx(0.2, abs=1e-6)


def test_turn_taking_imbalance_lurkers_dont_swing_the_score(centroid):
    """Adding low-volume lurkers should not change the imbalance when the
    dominant pair stays the same."""
    base = compute(
        [0.1, 0.1, 0.1, 0.1, 0.1],
        ["a1", "b1", "a2", "a3", "b2"],
        ["A", "B", "A", "A", "B"],
        centroid,
    )
    with_lurkers = compute(
        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        ["a1", "b1", "a2", "a3", "b2", "c1", "d1"],
        ["A", "B", "A", "A", "B", "C", "D"],
        centroid,
    )
    assert with_lurkers[IMBAL] == pytest.approx(base[IMBAL], abs=1e-6)
