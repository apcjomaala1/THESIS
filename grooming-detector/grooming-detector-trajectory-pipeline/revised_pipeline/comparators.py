"""Fit fair raw-Layer-1 and weighted comparators on validation only.

The output feature configuration is shared byte-for-byte with both revised
LSTMs.  The Layer 1 author-row threshold is retained only as provenance; the
raw Layer 1 conversation baseline gets its own validation-selected threshold.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .cache import load_partition_cache
from .centroid import load_centroid
from .contracts import canonical_sha256, write_json
from .features import compute_sequence_features
from .metrics import select_f05_threshold


WEIGHT_CANDIDATES = (0.0, 0.05, 0.10, 0.20, 0.40, 0.80, 1.20)
LOCKED_COORDINATE_PASSES = 4


@dataclass
class _RawConversation:
    conversation_id: str
    proxy_scores: np.ndarray
    embeddings: np.ndarray
    speaker_indices: np.ndarray
    label: int


def _load_raw_conversations(
    validation_cache: Path,
    centroid_dir: Path,
) -> tuple[list[_RawConversation], np.ndarray, dict[str, Any], np.ndarray]:
    index, scores, embeddings, cache_manifest = load_partition_cache(
        validation_cache, expected_split="validation"
    )
    centroid, centroid_manifest = load_centroid(centroid_dir)
    for field in [
        "base_encoder_state_sha256",
        "base_encoder_config_sha256",
        "base_tokenizer",
        "torch_version",
        "transformers_version",
    ]:
        if cache_manifest["provenance"][field] != centroid_manifest[field]:
            raise ValueError(
                f"Validation cache and centroid disagree on base-model field: {field}"
            )
    raw: list[_RawConversation] = []
    for conversation_id, positions in index.groupby(
        "conversation_id", sort=True
    ).indices.items():
        positions = np.asarray(positions, dtype=np.int64)
        block = index.iloc[positions]
        labels = block["conversation_label"].astype(int).unique()
        if len(labels) != 1:
            raise ValueError(f"Mixed conversation label: {conversation_id}")
        raw.append(
            _RawConversation(
                conversation_id=str(conversation_id),
                proxy_scores=np.asarray(scores[positions], dtype=np.float32),
                embeddings=np.asarray(embeddings[positions], dtype=np.float32),
                speaker_indices=block["speaker_index"].to_numpy(dtype=np.int64),
                label=int(labels[0]),
            )
        )
    labels = np.asarray([conversation.label for conversation in raw], dtype=np.int8)
    metadata = {
        "cache_manifest": cache_manifest,
        "centroid_manifest": centroid_manifest,
    }
    return raw, labels, metadata, centroid


def _feature_blocks(
    conversations: list[_RawConversation],
    centroid: np.ndarray,
    spike_threshold: float,
    drop_threshold: float,
) -> list[np.ndarray]:
    return [
        compute_sequence_features(
            conversation.proxy_scores,
            conversation.embeddings,
            conversation.speaker_indices,
            centroid,
            spike_threshold,
            drop_threshold,
        )
        for conversation in conversations
    ]


def weighted_conversation_scores(
    feature_blocks: list[np.ndarray],
    weights: np.ndarray,
) -> np.ndarray:
    weights = np.asarray(weights, dtype=np.float64)
    if weights.shape != (7,) or not np.isfinite(weights).all() or (weights < 0).any():
        raise ValueError("Weighted scorer requires seven finite non-negative weights")
    if float(weights.sum()) <= 0.0:
        raise ValueError("At least one weighted-scorer weight must be positive")
    weights = weights / weights.sum()
    scores = []
    for features in feature_blocks:
        raw = np.asarray(features, dtype=np.float64) @ weights
        turn_scores = 1.0 / (1.0 + np.exp(-np.clip(raw, -80.0, 80.0)))
        scores.append(float(turn_scores.max()))
    return np.asarray(scores, dtype=np.float64)


def _configuration_key(metrics: dict[str, Any], weights: np.ndarray) -> tuple:
    return (
        float(metrics["f0_5"]),
        float(metrics["pr_auc"] or 0.0),
        float(metrics["recall"]),
        float(metrics["precision"]),
        tuple((-weights).tolist()),
    )


def tune_weighted_scorer(
    feature_blocks: list[np.ndarray],
    labels: np.ndarray,
    coordinate_passes: int = 4,
) -> dict[str, Any]:
    weights = np.full(7, 1.0 / 7.0, dtype=np.float64)
    scores = weighted_conversation_scores(feature_blocks, weights)
    threshold, metrics = select_f05_threshold(labels, scores)
    for _pass in range(coordinate_passes):
        changed = False
        for coordinate in range(7):
            best = (weights.copy(), scores, threshold, metrics)
            best_key = _configuration_key(metrics, weights)
            for candidate in WEIGHT_CANDIDATES:
                proposed = weights.copy()
                proposed[coordinate] = candidate
                if proposed.sum() <= 0:
                    continue
                proposed /= proposed.sum()
                proposed_scores = weighted_conversation_scores(feature_blocks, proposed)
                proposed_threshold, proposed_metrics = select_f05_threshold(
                    labels, proposed_scores
                )
                proposed_key = _configuration_key(proposed_metrics, proposed)
                if proposed_key > best_key:
                    best_key = proposed_key
                    best = (
                        proposed,
                        proposed_scores,
                        proposed_threshold,
                        proposed_metrics,
                    )
            if not np.allclose(best[0], weights, rtol=0.0, atol=1e-15):
                changed = True
            weights, scores, threshold, metrics = best
        if not changed:
            break
    return {
        "weights": weights.tolist(),
        "threshold": float(threshold),
        "metrics": metrics,
        "scores": scores,
    }


def fit_comparators(
    validation_cache: Path,
    centroid_dir: Path,
    feature_config_path: Path,
    output_dir: Path,
    coordinate_passes: int = LOCKED_COORDINATE_PASSES,
) -> dict[str, Any]:
    if coordinate_passes != LOCKED_COORDINATE_PASSES:
        raise ValueError(
            f"The revised protocol locks coordinate_passes={LOCKED_COORDINATE_PASSES}"
        )
    allowed_existing = {feature_config_path.resolve()}
    existing = set(path.resolve() for path in output_dir.iterdir()) if output_dir.exists() else set()
    if existing - allowed_existing:
        raise FileExistsError(
            f"Comparator output directory contains unexpected files: {output_dir}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)
    conversations, labels, provenance, centroid = _load_raw_conversations(
        validation_cache, centroid_dir
    )
    feature_config = json.loads(feature_config_path.read_text(encoding="utf-8"))
    feature_payload = dict(feature_config)
    expected_feature_hash = feature_payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(feature_payload) != expected_feature_hash:
        raise ValueError("Feature configuration failed its canonical hash check")
    if feature_config.get("architecture_outcomes_used") is not False:
        raise ValueError("Shared feature thresholds were selected from architecture outcomes")
    if (
        feature_config.get("validation_cache_manifest_payload_sha256")
        != provenance["cache_manifest"]["canonical_payload_sha256"]
    ):
        raise ValueError("Feature configuration names a different validation cache")
    spike_threshold = float(feature_config["spike_threshold"])
    drop_threshold = float(feature_config["drop_threshold"])
    conversation_ids = [conversation.conversation_id for conversation in conversations]
    raw_scores = np.asarray(
        [float(conversation.proxy_scores.max()) for conversation in conversations],
        dtype=np.float64,
    )
    raw_threshold, raw_metrics = select_f05_threshold(labels, raw_scores)

    blocks = _feature_blocks(
        conversations,
        centroid,
        spike_threshold,
        drop_threshold,
    )
    best_weighted = tune_weighted_scorer(
        blocks,
        labels,
        coordinate_passes=coordinate_passes,
    )

    cache_manifest = provenance["cache_manifest"]
    centroid_manifest = provenance["centroid_manifest"]
    shared = {
        "selection_partition": "validation",
        "objective": "maximum conversation F0.5",
        "validation_conversations": len(conversations),
        "validation_conversation_id_sequence_sha256": canonical_sha256(
            conversation_ids
        ),
        "validation_cache_manifest_payload_sha256": cache_manifest[
            "canonical_payload_sha256"
        ],
        "centroid_manifest_payload_sha256": centroid_manifest[
            "canonical_payload_sha256"
        ],
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    raw_config = {
        "schema_version": 1,
        **shared,
        "method": "aggregated_raw_layer1",
        "score": "maximum FP32 author-proxy score across turns",
        "aggregation": "max",
        "extra_sigmoid": False,
        "threshold": raw_threshold,
        "metrics": raw_metrics,
        "layer1_row_threshold_provenance_only": cache_manifest["provenance"][
            "layer1_row_threshold"
        ],
    }
    raw_config["canonical_payload_sha256"] = canonical_sha256(raw_config)
    weighted_config = {
        "schema_version": 1,
        **shared,
        "method": "weighted_trajectory",
        "score": "max_t sigmoid(normalized_nonnegative_weights dot seven_features_t)",
        "aggregation": "max",
        "feature_config_payload_sha256": expected_feature_hash,
        "weights": best_weighted["weights"],
        "weight_sum": float(sum(best_weighted["weights"])),
        "coordinate_candidates": list(WEIGHT_CANDIDATES),
        "coordinate_passes": int(coordinate_passes),
        "threshold": best_weighted["threshold"],
        "metrics": best_weighted["metrics"],
    }
    weighted_config["canonical_payload_sha256"] = canonical_sha256(weighted_config)
    if feature_config_path.resolve() != (output_dir / "feature_config.json").resolve():
        write_json(output_dir / "feature_config.json", feature_config)
    write_json(output_dir / "raw_layer1_config.json", raw_config)
    write_json(output_dir / "weighted_scorer_config.json", weighted_config)
    pd.DataFrame(
        {
            "conversation_id": conversation_ids,
            "label": labels,
            "raw_layer1_score": raw_scores,
            "raw_layer1_prediction": (raw_scores >= raw_threshold).astype(np.int8),
            "weighted_score": best_weighted["scores"],
            "weighted_prediction": (
                best_weighted["scores"] >= best_weighted["threshold"]
            ).astype(np.int8),
        }
    ).to_csv(output_dir / "validation_predictions.csv", index=False)
    summary = {
        "schema_version": 1,
        "status": "completed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "raw_layer1": raw_metrics,
        "weighted": best_weighted["metrics"],
        "feature_config_payload_sha256": expected_feature_hash,
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    write_json(output_dir / "run_summary.json", summary)
    return summary


def validate_comparator_artifacts(
    validation_cache: Path,
    centroid_dir: Path,
    comparator_dir: Path,
) -> dict[str, Any]:
    conversations, labels, provenance, centroid = _load_raw_conversations(
        validation_cache, centroid_dir
    )
    configs = {}
    for filename in [
        "feature_config.json",
        "raw_layer1_config.json",
        "weighted_scorer_config.json",
    ]:
        record = json.loads((comparator_dir / filename).read_text(encoding="utf-8"))
        payload = dict(record)
        expected = payload.pop("canonical_payload_sha256", None)
        if canonical_sha256(payload) != expected:
            raise ValueError(f"Comparator canonical hash failed: {filename}")
        configs[filename] = record
    feature_config = configs["feature_config.json"]
    raw_config = configs["raw_layer1_config.json"]
    weighted_config = configs["weighted_scorer_config.json"]
    if (
        feature_config["validation_cache_manifest_payload_sha256"]
        != provenance["cache_manifest"]["canonical_payload_sha256"]
    ):
        raise ValueError("Comparator feature configuration names another cache")
    from .feature_config import LOCKED_DROP_QUANTILE, derive_feature_thresholds

    index, cached_scores, _embeddings, _cache_manifest = load_partition_cache(
        validation_cache, expected_split="validation"
    )
    derived_features = derive_feature_thresholds(index, cached_scores)
    if feature_config.get("drop_threshold_quantile") != LOCKED_DROP_QUANTILE:
        raise ValueError("Feature drop quantile is not the locked value")
    for field in ["spike_threshold", "drop_threshold"]:
        if not np.isclose(
            float(feature_config[field]),
            float(derived_features[field]),
            rtol=0,
            atol=1e-12,
        ):
            raise ValueError(f"Feature configuration was not deterministically derived: {field}")
    if int(feature_config.get("eligible_validation_drops", -1)) != int(
        derived_features["eligible_validation_drops"]
    ):
        raise ValueError("Feature configuration has the wrong eligible-drop count")
    blocks = _feature_blocks(
        conversations,
        centroid,
        float(feature_config["spike_threshold"]),
        float(feature_config["drop_threshold"]),
    )
    raw_scores = np.asarray(
        [float(conversation.proxy_scores.max()) for conversation in conversations]
    )
    raw_threshold, raw_metrics = select_f05_threshold(labels, raw_scores)
    if weighted_config.get("coordinate_candidates") != list(WEIGHT_CANDIDATES):
        raise ValueError("Weighted scorer uses a different coordinate candidate grid")
    if int(weighted_config.get("coordinate_passes", -1)) != LOCKED_COORDINATE_PASSES:
        raise ValueError("Weighted scorer uses a different coordinate-pass budget")
    regenerated_weighted = tune_weighted_scorer(
        blocks,
        labels,
        coordinate_passes=LOCKED_COORDINATE_PASSES,
    )
    recorded_weights = np.asarray(weighted_config["weights"], dtype=np.float64)
    regenerated_weights = np.asarray(regenerated_weighted["weights"], dtype=np.float64)
    if not np.allclose(recorded_weights, regenerated_weights, rtol=0, atol=1e-15):
        raise ValueError("Weighted weights are not the deterministic validation optimum")
    weighted_scores = np.asarray(regenerated_weighted["scores"], dtype=np.float64)
    weighted_threshold, weighted_metrics = select_f05_threshold(
        labels, weighted_scores
    )
    if not np.isclose(raw_threshold, float(raw_config["threshold"]), rtol=0, atol=1e-12):
        raise ValueError("Raw Layer 1 threshold is not the validation F0.5 optimum")
    if not np.isclose(
        weighted_threshold, float(weighted_config["threshold"]), rtol=0, atol=1e-12
    ):
        raise ValueError("Weighted threshold is not the validation F0.5 optimum")
    predictions = pd.read_csv(comparator_dir / "validation_predictions.csv")
    expected_ids = [conversation.conversation_id for conversation in conversations]
    if predictions["conversation_id"].astype(str).tolist() != expected_ids:
        raise ValueError("Comparator validation conversation order is wrong")
    expected_columns = {
        "label": labels,
        "raw_layer1_score": raw_scores,
        "raw_layer1_prediction": (raw_scores >= raw_threshold).astype(np.int8),
        "weighted_score": weighted_scores,
        "weighted_prediction": (weighted_scores >= weighted_threshold).astype(np.int8),
    }
    for column, expected_values in expected_columns.items():
        observed = predictions[column].to_numpy()
        if np.issubdtype(np.asarray(expected_values).dtype, np.floating):
            if not np.allclose(observed, expected_values, rtol=1e-7, atol=1e-7):
                raise ValueError(f"Comparator validation values differ: {column}")
        elif not np.array_equal(observed.astype(np.int64), np.asarray(expected_values).astype(np.int64)):
            raise ValueError(f"Comparator validation values differ: {column}")
    return {
        "status": "validated",
        "validation_conversations": len(conversations),
        "raw_metrics": raw_metrics,
        "weighted_metrics": weighted_metrics,
        "feature_config_payload_sha256": feature_config[
            "canonical_payload_sha256"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-cache", type=Path, required=True)
    parser.add_argument("--centroid-dir", type=Path, required=True)
    parser.add_argument("--feature-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--coordinate-passes", type=int, default=4)
    args = parser.parse_args()
    summary = fit_comparators(
        args.validation_cache,
        args.centroid_dir,
        args.feature_config,
        args.output_dir,
        args.coordinate_passes,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
