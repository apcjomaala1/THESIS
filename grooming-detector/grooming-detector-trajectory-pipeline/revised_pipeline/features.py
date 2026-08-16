"""Exact seven-feature implementation for the revised experiment."""

from __future__ import annotations

import numpy as np


FEATURE_NAMES = (
    "peak_proxy_score",
    "current_proxy_score",
    "spike_count",
    "spike_then_drop",
    "rate_of_change",
    "topic_distance",
    "turn_taking_imbalance",
)


def _cosine_distance_rows(matrix: np.ndarray, centroid: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    centroid = np.asarray(centroid, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] != 768:
        raise ValueError(f"Expected embeddings with shape (T, 768), got {matrix.shape}")
    if centroid.shape != (768,):
        raise ValueError(f"Expected centroid with shape (768,), got {centroid.shape}")
    matrix_norm = np.linalg.norm(matrix, axis=1)
    centroid_norm = float(np.linalg.norm(centroid))
    denominator = matrix_norm * centroid_norm
    similarity = np.zeros(len(matrix), dtype=np.float32)
    valid = denominator > 0
    if np.any(valid):
        similarity[valid] = (matrix[valid] @ centroid) / denominator[valid]
    similarity = np.clip(similarity, -1.0, 1.0)
    return (1.0 - similarity).astype(np.float32)


def compute_sequence_features(
    proxy_scores: np.ndarray,
    embeddings: np.ndarray,
    speaker_indices: np.ndarray,
    benign_centroid: np.ndarray,
    spike_threshold: float,
    drop_threshold: float,
) -> np.ndarray:
    """Return a ``(T, 7)`` chronological feature matrix for one conversation."""
    scores = np.asarray(proxy_scores, dtype=np.float32)
    speakers = np.asarray(speaker_indices, dtype=np.int64)
    embeddings = np.asarray(embeddings, dtype=np.float32)
    if scores.ndim != 1 or len(scores) == 0:
        raise ValueError("proxy_scores must be a non-empty one-dimensional array")
    if embeddings.shape != (len(scores), 768):
        raise ValueError("Embedding rows must align one-to-one with proxy scores")
    if speakers.shape != (len(scores),) or not set(np.unique(speakers)).issubset({0, 1}):
        raise ValueError("speaker_indices must align to rows and contain only 0/1")
    if not np.isfinite(scores).all() or not np.all((0.0 <= scores) & (scores <= 1.0)):
        raise ValueError("Proxy scores must be finite values in [0, 1]")
    if not 0.0 <= float(spike_threshold) <= 1.0:
        raise ValueError("spike_threshold must be in [0, 1]")
    if not 0.0 <= float(drop_threshold) <= 1.0:
        raise ValueError("drop_threshold must be in [0, 1]")

    peak = np.maximum.accumulate(scores)
    spike_count = np.cumsum(scores > float(spike_threshold), dtype=np.int64).astype(
        np.float32
    )
    spike_then_drop = np.zeros(len(scores), dtype=np.float32)
    prior_peak = float(scores[0])
    seen_drop = False
    for index in range(1, len(scores)):
        if prior_peak > float(spike_threshold) and scores[index] < prior_peak - float(
            drop_threshold
        ):
            seen_drop = True
        spike_then_drop[index] = float(seen_drop)
        prior_peak = max(prior_peak, float(scores[index]))

    rate = np.zeros(len(scores), dtype=np.float32)
    rate[1:] = scores[1:] - scores[:-1]
    topic_distance = _cosine_distance_rows(embeddings, benign_centroid)
    imbalance = np.zeros(len(scores), dtype=np.float32)
    counts = [0, 0]
    for index, speaker in enumerate(speakers):
        counts[int(speaker)] += 1
        imbalance[index] = abs(counts[0] - counts[1]) / float(sum(counts))

    result = np.column_stack(
        [
            peak,
            scores,
            spike_count,
            spike_then_drop,
            rate,
            topic_distance,
            imbalance,
        ]
    ).astype(np.float32)
    if result.shape != (len(scores), len(FEATURE_NAMES)) or not np.isfinite(result).all():
        raise ValueError("Trajectory feature computation produced an invalid matrix")
    return result
