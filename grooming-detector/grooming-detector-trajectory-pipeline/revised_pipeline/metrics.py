"""Shared conversation-level metrics and validation-only threshold selection."""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def conversation_metrics(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    labels = np.asarray(labels, dtype=np.int8)
    scores = np.asarray(scores, dtype=np.float64)
    if labels.shape != scores.shape or labels.ndim != 1 or len(labels) == 0:
        raise ValueError("labels and scores must be aligned, non-empty vectors")
    if not set(np.unique(labels)).issubset({0, 1}):
        raise ValueError("Conversation labels must be binary")
    if not np.isfinite(scores).all():
        raise ValueError("Conversation scores must be finite")
    predictions = (scores >= float(threshold)).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    pr_auc = (
        float(average_precision_score(labels, scores))
        if len(np.unique(labels)) == 2
        else None
    )
    roc_auc = (
        float(roc_auc_score(labels, scores)) if len(np.unique(labels)) == 2 else None
    )
    return {
        "threshold": float(threshold),
        "accuracy": float((predictions == labels).mean()),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "f0_5": float(fbeta_score(labels, predictions, beta=0.5, zero_division=0)),
        "pr_auc": pr_auc,
        "roc_auc": roc_auc,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "specificity": float(tn / (tn + fp)) if (tn + fp) else 0.0,
    }


def select_f05_threshold(
    labels: np.ndarray,
    scores: np.ndarray,
) -> tuple[float, dict[str, Any]]:
    """Select a threshold by F0.5, with deterministic documented tie-breaks."""
    labels = np.asarray(labels, dtype=np.int8)
    scores = np.asarray(scores, dtype=np.float64)
    if labels.shape != scores.shape or labels.ndim != 1 or len(labels) == 0:
        raise ValueError("labels and scores must be aligned, non-empty vectors")
    if not np.isfinite(scores).all() or not set(np.unique(labels)).issubset({0, 1}):
        raise ValueError("Threshold selection requires finite scores and binary labels")

    # Sorting once makes the search O(n log n), rather than recomputing a full
    # confusion matrix for every unique candidate (O(n^2)). At the last row of
    # each tied score, cumulative counts equal predictions under score >= value.
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_labels = labels[order]
    cumulative_tp = np.cumsum(sorted_labels == 1)
    cumulative_fp = np.cumsum(sorted_labels == 0)
    group_ends = np.flatnonzero(
        np.r_[sorted_scores[:-1] != sorted_scores[1:], True]
    )
    thresholds = sorted_scores[group_ends]
    tp = cumulative_tp[group_ends].astype(np.float64)
    fp = cumulative_fp[group_ends].astype(np.float64)
    total_positive = float((labels == 1).sum())
    fn = total_positive - tp
    precision = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    recall = np.divide(
        tp,
        tp + fn,
        out=np.zeros_like(tp),
        where=(tp + fn) > 0,
    )
    denominator = 0.25 * precision + recall
    f05 = np.divide(
        1.25 * precision * recall,
        denominator,
        out=np.zeros_like(precision),
        where=denominator > 0,
    )
    best_index = max(
        range(len(thresholds)),
        key=lambda index: (
            float(f05[index]),
            float(recall[index]),
            float(precision[index]),
            float(thresholds[index]),
        ),
    )
    best_threshold = float(thresholds[best_index])
    # Include the valid "predict none" candidate. It normally loses because
    # validation contains positives, but it makes behavior complete for a
    # degenerate score vector.
    above_max = np.nextafter(float(scores.max()), float("inf"))
    selected_key = (
        float(f05[best_index]),
        float(recall[best_index]),
        float(precision[best_index]),
        best_threshold,
    )
    if (0.0, 0.0, 0.0, above_max) > selected_key:
        best_threshold = above_max
    return best_threshold, conversation_metrics(labels, scores, best_threshold)


def component_bootstrap_intervals(
    labels: np.ndarray,
    scores: np.ndarray,
    threshold: float,
    component_ids: np.ndarray,
    replicates: int = 2000,
    seed: int = 42,
    level: float = 0.95,
) -> dict[str, Any]:
    """Percentile intervals resampling connected-author components as units."""
    labels = np.asarray(labels, dtype=np.int8)
    scores = np.asarray(scores, dtype=np.float64)
    component_ids = np.asarray(component_ids).astype(str)
    if not (labels.shape == scores.shape == component_ids.shape):
        raise ValueError("Bootstrap labels, scores, and component IDs must align")
    if replicates <= 0 or not 0.0 < level < 1.0:
        raise ValueError("Invalid bootstrap configuration")
    components = np.unique(component_ids)
    positions = {
        component: np.flatnonzero(component_ids == component) for component in components
    }
    rng = np.random.default_rng(seed)
    tracked = ["accuracy", "precision", "recall", "specificity", "f1", "f0_5", "pr_auc", "roc_auc"]
    samples: dict[str, list[float]] = {name: [] for name in tracked}
    for _ in range(replicates):
        chosen = rng.choice(components, size=len(components), replace=True)
        sampled_positions = np.concatenate([positions[component] for component in chosen])
        metrics = conversation_metrics(
            labels[sampled_positions], scores[sampled_positions], threshold
        )
        for name in tracked:
            value = metrics[name]
            if value is not None and np.isfinite(value):
                samples[name].append(float(value))
    alpha = (1.0 - level) / 2.0
    intervals = {}
    for name, values in samples.items():
        if not values:
            intervals[name] = {
                "lower": None,
                "upper": None,
                "valid_replicates": 0,
            }
        else:
            intervals[name] = {
                "lower": float(np.quantile(values, alpha)),
                "upper": float(np.quantile(values, 1.0 - alpha)),
                "valid_replicates": len(values),
            }
    return {
        "method": "percentile bootstrap over connected-author components",
        "level": level,
        "seed": int(seed),
        "requested_replicates": int(replicates),
        "components": len(components),
        "intervals": intervals,
    }


def component_bootstrap_differences(
    labels: np.ndarray,
    scores_a: np.ndarray,
    threshold_a: float,
    scores_b: np.ndarray,
    threshold_b: float,
    component_ids: np.ndarray,
    replicates: int = 2000,
    seed: int = 42,
    level: float = 0.95,
) -> dict[str, Any]:
    """Paired component-bootstrap intervals for metric differences A minus B."""
    labels = np.asarray(labels, dtype=np.int8)
    scores_a = np.asarray(scores_a, dtype=np.float64)
    scores_b = np.asarray(scores_b, dtype=np.float64)
    component_ids = np.asarray(component_ids).astype(str)
    if not (labels.shape == scores_a.shape == scores_b.shape == component_ids.shape):
        raise ValueError("Paired bootstrap inputs must align")
    tracked = ["precision", "recall", "f1", "f0_5", "pr_auc", "roc_auc"]
    point_a = conversation_metrics(labels, scores_a, threshold_a)
    point_b = conversation_metrics(labels, scores_b, threshold_b)
    components = np.unique(component_ids)
    positions = {
        component: np.flatnonzero(component_ids == component) for component in components
    }
    rng = np.random.default_rng(seed)
    differences: dict[str, list[float]] = {name: [] for name in tracked}
    for _ in range(replicates):
        chosen = rng.choice(components, size=len(components), replace=True)
        sampled_positions = np.concatenate([positions[component] for component in chosen])
        metrics_a = conversation_metrics(
            labels[sampled_positions], scores_a[sampled_positions], threshold_a
        )
        metrics_b = conversation_metrics(
            labels[sampled_positions], scores_b[sampled_positions], threshold_b
        )
        for name in tracked:
            if metrics_a[name] is not None and metrics_b[name] is not None:
                differences[name].append(float(metrics_a[name] - metrics_b[name]))
    alpha = (1.0 - level) / 2.0
    result = {}
    for name, values in differences.items():
        result[name] = {
            "point_difference": (
                float(point_a[name] - point_b[name])
                if point_a[name] is not None and point_b[name] is not None
                else None
            ),
            "lower": float(np.quantile(values, alpha)) if values else None,
            "upper": float(np.quantile(values, 1.0 - alpha)) if values else None,
            "valid_replicates": len(values),
        }
    return {
        "method": "paired percentile bootstrap over connected-author components",
        "direction": "method_a minus method_b",
        "level": level,
        "seed": int(seed),
        "requested_replicates": int(replicates),
        "components": len(components),
        "differences": result,
    }
