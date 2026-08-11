"""Tests for evaluation metrics, keyword baseline, and ablation utility."""

import math

import pytest

from evaluation import (
    GROOMING_KEYWORDS,
    evaluate_conversations,
    evaluate_keyword_baseline,
    keyword_baseline_score,
    run_ablation,
)


def test_keyword_score_hits_known_phrase():
    assert keyword_baseline_score("hey how old are you?") == 1
    assert keyword_baseline_score("can you send photo plz") == 1
    assert keyword_baseline_score("let's keep this between us") == 1


def test_keyword_score_misses_benign():
    assert keyword_baseline_score("did you watch the game last night") == 0
    assert keyword_baseline_score("ok cool see you tomorrow") == 0


def test_keyword_keyword_list_non_empty():
    assert len(GROOMING_KEYWORDS) > 0


def test_evaluate_conversations_perfect_classifier():
    convs = [
        {"conversation_id": "a", "scores": [0.9, 0.95], "label": 1},
        {"conversation_id": "b", "scores": [0.1, 0.2], "label": 0},
    ]
    m = evaluate_conversations(convs, threshold=0.5)
    assert m["recall"] == 1.0
    assert m["precision"] == 1.0
    assert m["f1"] == 1.0
    assert m["n_true_positives"] == 1
    assert m["n_false_positives"] == 0
    assert m["n_false_negatives"] == 0
    assert m["n_true_negatives"] == 1


def test_time_to_detection_picks_first_crossing():
    convs = [
        {"conversation_id": "a", "scores": [0.1, 0.2, 0.8, 0.9], "label": 1},
        {"conversation_id": "b", "scores": [0.3, 0.6, 0.6], "label": 1},
    ]
    m = evaluate_conversations(convs, threshold=0.5)
    # conv a: first crossing at turn 2; conv b: at turn 1 → median = 1.5
    assert m["median_time_to_detection"] == pytest.approx(1.5)
    assert m["avg_time_to_detection"] == pytest.approx(1.5)


def test_false_negative_when_below_threshold():
    convs = [
        {"conversation_id": "a", "scores": [0.1, 0.4, 0.45], "label": 1},  # never crosses
        {"conversation_id": "b", "scores": [0.1, 0.2], "label": 0},
    ]
    m = evaluate_conversations(convs, threshold=0.5)
    assert m["recall"] == 0.0
    assert m["n_false_negatives"] == 1
    # no TTD for missed positives
    assert math.isnan(m["avg_time_to_detection"])


def test_keyword_baseline_aggregates_per_conversation():
    snapshots = [
        # benign conv
        {"conversation_id": "c1", "messages_so_far": ["hi"], "label": 0, "conversation_label": 0},
        {"conversation_id": "c1", "messages_so_far": ["hi", "hello"], "label": 0, "conversation_label": 0},
        # predatory conv with one matching keyword phrase
        {"conversation_id": "c2", "messages_so_far": ["hey"], "label": 0, "conversation_label": 1},
        {"conversation_id": "c2", "messages_so_far": ["hey", "how old are you"], "label": 1, "conversation_label": 1},
    ]
    results = evaluate_keyword_baseline(snapshots)
    by_id = {r["conversation_id"]: r for r in results}
    assert by_id["c1"]["label"] == 0
    assert by_id["c2"]["label"] == 1
    assert max(by_id["c2"]["scores"]) == 1.0   # the keyword phrase fires
    assert max(by_id["c1"]["scores"]) == 0.0


def test_run_ablation_does_not_crash():
    a = {"recall": 0.8, "f1": 0.7, "avg_time_to_detection": 4.0}
    b = {"recall": 0.6, "f1": 0.5, "avg_time_to_detection": 7.0}
    # Just exercising the formatter; if it raises, the test fails.
    run_ablation(a, b)
