"""One gated command for the corrected final conversation-level evaluation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .cache import build_cache, load_partition_cache
from .comparators import weighted_conversation_scores
from .contracts import canonical_sha256, sha256_file, write_json
from .data import attach_locked_splits, load_eligible_rows
from .dataset import load_conversation_sequences
from .final_gate import preflight_frozen_protocol, validate_claim
from .keyword import score_conversations
from .lstm import load_lstm_checkpoint, predict_lstm_sequences
from .metrics import (
    component_bootstrap_differences,
    component_bootstrap_intervals,
    conversation_metrics,
)


def _role_path(frozen: dict[str, Any], name: str) -> Path:
    return Path(frozen["artifact_roles"][name]["path"])


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_empty(path: Path, label: str) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"{label} is not empty: {path}")


def _verify_final_cache(
    final_cache_dir: Path,
    frozen: dict[str, Any],
) -> dict[str, Any]:
    root = _load_json(final_cache_dir / "cache_manifest.json")
    payload = dict(root)
    expected = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected:
        raise ValueError("Final cache root manifest failed its integrity check")
    if root.get("splits") != ["final_test"]:
        raise ValueError("Final cache does not contain exactly the locked final test")
    if root.get("final_test_scored") is not True:
        raise ValueError("Final cache is not marked as final-test scoring")
    if root.get("historical_test_scored") is not False:
        raise ValueError("Final cache touched the excluded historical test")
    partition_hashes = root.get("partition_manifest_payload_sha256", {})
    if set(partition_hashes) != {"final_test"}:
        raise ValueError("Final cache root does not bind exactly one final partition")
    _index, _scores, _embeddings, child = load_partition_cache(
        final_cache_dir / "final_test", expected_split="final_test"
    )
    if (
        partition_hashes["final_test"]
        != child.get("canonical_payload_sha256")
    ):
        raise ValueError("Final cache root and child partition manifests disagree")
    if child.get("provenance") != root.get("provenance"):
        raise ValueError("Final cache root and child partition provenance disagree")
    provenance = root["provenance"]
    if provenance.get("data_sha256") != frozen["dataset_sha256"]:
        raise ValueError("Final cache used a different dataset")
    if (
        provenance.get("split_manifest_payload_sha256")
        != frozen["split_manifest_payload_sha256"]
    ):
        raise ValueError("Final cache used a different split manifest")
    if (
        provenance.get("layer1_model_tree_sha256")
        != frozen["layer1_receipt"]["best_model_tree_sha256"]
    ):
        raise ValueError("Final cache used a different Layer 1 model")
    claim = provenance.get("final_test_claim", {})
    if claim.get("status") != "CONSUMED_BEFORE_FINAL_ROWS_SCORED_OR_CACHED":
        raise ValueError("Final cache lacks a consumed one-time gate receipt")
    if (
        claim.get("frozen_protocol_payload_sha256")
        != frozen["canonical_payload_sha256"]
    ):
        raise ValueError("Final cache was not authorized by this frozen protocol")
    development_cache = _load_json(
        _role_path(frozen, "development_cache") / "cache_manifest.json"
    )
    for field in [
        "base_encoder_state_sha256",
        "base_encoder_config_sha256",
        "base_tokenizer",
        "torch_version",
        "transformers_version",
    ]:
        if provenance.get(field) != development_cache["provenance"].get(field):
            raise ValueError(f"Final cache changed frozen base-model field: {field}")
    return root


def _score_final_methods(
    frozen: dict[str, Any],
    final_cache_dir: Path,
    device_name: str | None,
) -> tuple[pd.DataFrame, dict[str, dict[str, Any]], dict[str, Any]]:
    comparator_dir = _role_path(frozen, "comparators")
    centroid_dir = _role_path(frozen, "centroid")
    feature_config = _load_json(comparator_dir / "feature_config.json")
    raw_config = _load_json(comparator_dir / "raw_layer1_config.json")
    weighted_config = _load_json(comparator_dir / "weighted_scorer_config.json")
    keyword_config = _load_json(
        _role_path(frozen, "keyword") / "keyword_config.json"
    )
    spike_threshold = float(feature_config["spike_threshold"])
    drop_threshold = float(feature_config["drop_threshold"])
    sequences, sequence_metadata = load_conversation_sequences(
        final_cache_dir / "final_test",
        centroid_dir,
        "final_test",
        spike_threshold,
        drop_threshold,
    )
    conversation_ids = [sequence.conversation_id for sequence in sequences]
    labels = np.asarray([sequence.label for sequence in sequences], dtype=np.int8)

    index, proxy_scores, _embeddings, cache_manifest = load_partition_cache(
        final_cache_dir / "final_test", expected_split="final_test"
    )
    raw_by_conversation = {
        conversation_id: float(np.asarray(proxy_scores[positions]).max())
        for conversation_id, positions in index.groupby(
            "conversation_id", sort=True
        ).indices.items()
    }
    raw_scores = np.asarray(
        [raw_by_conversation[conversation_id] for conversation_id in conversation_ids],
        dtype=np.float64,
    )
    weighted_scores = weighted_conversation_scores(
        [sequence.trajectory_features for sequence in sequences],
        np.asarray(weighted_config["weights"], dtype=np.float64),
    )

    # The keyword configuration is frozen from training. Raw final text is
    # loaded only after the one-time claim was consumed by cache generation.
    split_manifest = _load_json(_role_path(frozen, "split_manifest"))
    data_frame = attach_locked_splits(
        load_eligible_rows(_role_path(frozen, "data_file")), split_manifest
    )
    final_frame = data_frame[data_frame["split"] == "final_test"]
    keyword_predictions = score_conversations(
        final_frame, [row["term"] for row in keyword_config["lexicon"]]
    ).set_index("conversation_id")
    if set(keyword_predictions.index) != set(conversation_ids):
        raise ValueError("Keyword baseline did not cover the exact final conversations")
    keyword_predictions = keyword_predictions.loc[conversation_ids]
    if not np.array_equal(
        keyword_predictions["label"].to_numpy(dtype=np.int8), labels
    ):
        raise ValueError("Keyword baseline labels disagree with the final cache")
    keyword_scores = keyword_predictions["score"].to_numpy(dtype=np.float64)

    lstm_scores: dict[str, np.ndarray] = {}
    lstm_thresholds: dict[str, float] = {}
    for mode, role in {
        "lstm_trajectory7": ("trajectory7", "lstm_trajectory7"),
        "lstm_enhanced775": ("enhanced775", "lstm_enhanced775"),
    }.items():
        expected_mode, role_name = role
        run_dir = _role_path(frozen, role_name)
        model, config, device = load_lstm_checkpoint(
            run_dir, expected_mode, device_name
        )
        ids, model_labels, scores = predict_lstm_sequences(
            sequences, model, config, device
        )
        if ids != conversation_ids or not np.array_equal(model_labels, labels):
            raise ValueError(f"{mode} did not score identical ordered conversations")
        lstm_scores[mode] = scores
        lstm_thresholds[mode] = float(
            _load_json(run_dir / "selected_threshold.json")["threshold"]
        )

    method_scores = {
        "raw_layer1": raw_scores,
        "weighted": weighted_scores,
        "keyword": keyword_scores,
        **lstm_scores,
    }
    method_thresholds = {
        "raw_layer1": float(raw_config["threshold"]),
        "weighted": float(weighted_config["threshold"]),
        "keyword": 0.5,
        **lstm_thresholds,
    }
    component_by_conversation = (
        index.groupby("conversation_id", sort=True)["component_id"].first().to_dict()
    )
    components = np.asarray(
        [component_by_conversation[conversation_id] for conversation_id in conversation_ids]
    )
    output = pd.DataFrame(
        {
            "conversation_id": conversation_ids,
            "component_id": components,
            "label": labels,
        }
    )
    metrics: dict[str, dict[str, Any]] = {}
    predictions: dict[str, np.ndarray] = {}
    for method, scores in method_scores.items():
        threshold = method_thresholds[method]
        method_predictions = (scores >= threshold).astype(np.int8)
        predictions[method] = method_predictions
        output[f"{method}_score"] = scores
        output[f"{method}_prediction"] = method_predictions
        metrics[method] = {
            "point_estimate": conversation_metrics(labels, scores, threshold),
            "confidence_intervals": component_bootstrap_intervals(
                labels,
                scores,
                threshold,
                components,
                replicates=int(frozen["confidence_interval_bootstrap_replicates"]),
                seed=int(frozen["confidence_interval_bootstrap_seed"]),
                level=float(frozen["confidence_interval_level"]),
            ),
        }
    paired_differences = {
        f"lstm_trajectory7_minus_{other}": component_bootstrap_differences(
            labels,
            method_scores["lstm_trajectory7"],
            method_thresholds["lstm_trajectory7"],
            method_scores[other],
            method_thresholds[other],
            components,
            replicates=int(frozen["confidence_interval_bootstrap_replicates"]),
            seed=int(frozen["confidence_interval_bootstrap_seed"]),
            level=float(frozen["confidence_interval_level"]),
        )
        for other in ["weighted", "raw_layer1", "keyword", "lstm_enhanced775"]
    }
    audit = {
        "conversation_id_sequence_sha256": canonical_sha256(conversation_ids),
        "conversations": len(conversation_ids),
        "positive_conversations": int(labels.sum()),
        "components": len(np.unique(components)),
        "all_methods_identical_order": True,
        "cache_manifest_payload_sha256": cache_manifest[
            "canonical_payload_sha256"
        ],
        "feature_config_payload_sha256": feature_config[
            "canonical_payload_sha256"
        ],
        "prefix_scores_in_primary_metrics": False,
        "lstm_conversation_score": "sigmoid of logit at final valid turn",
    }
    return output, metrics, {
        "paired_component_bootstrap_differences": paired_differences,
        "audit": audit,
    }


def run_final_evaluation(
    frozen_protocol_path: Path,
    final_test_claim: Path,
    final_cache_dir: Path,
    output_dir: Path,
    cache_batch_size: int = 128,
    device_name: str | None = None,
    local_files_only: bool = True,
) -> dict[str, Any]:
    if int(cache_batch_size) <= 0:
        raise ValueError("cache_batch_size must be a positive integer")
    _ensure_empty(final_cache_dir, "Final cache directory")
    _ensure_empty(output_dir, "Final evaluation output directory")
    frozen = preflight_frozen_protocol(frozen_protocol_path)
    claim = validate_claim(
        final_test_claim,
        {
            "dataset": {"sha256": frozen["dataset_sha256"]},
            "integrity": {
                "canonical_payload_sha256": frozen[
                    "split_manifest_payload_sha256"
                ]
            },
        },
    )
    if Path(claim["frozen_protocol_path"]).resolve() != frozen_protocol_path.resolve():
        raise ValueError(
            "The final-test claim belongs to a different frozen protocol"
        )
    if (
        claim["frozen_protocol_payload_sha256"]
        != frozen["canonical_payload_sha256"]
    ):
        raise ValueError(
            "The final-test claim hash differs from the supplied frozen protocol"
        )
    build_cache(
        data_file=_role_path(frozen, "data_file"),
        split_manifest_path=_role_path(frozen, "split_manifest"),
        component_audit_path=_role_path(frozen, "component_audit"),
        package_manifest_path=_role_path(frozen, "package_manifest"),
        layer1_run=_role_path(frozen, "layer1_run"),
        output_dir=final_cache_dir,
        splits=["final_test"],
        batch_size=cache_batch_size,
        device_name=device_name,
        local_files_only=local_files_only,
        final_test_claim=final_test_claim,
    )
    # Close the time-of-check/time-of-use gap: cache generation can be long,
    # so re-hash every frozen choice before loading it for scoring.
    frozen_after_cache = preflight_frozen_protocol(frozen_protocol_path)
    if (
        frozen_after_cache["canonical_payload_sha256"]
        != frozen["canonical_payload_sha256"]
    ):
        raise ValueError("Frozen protocol changed during final cache generation")
    frozen = frozen_after_cache
    final_cache_record = _verify_final_cache(final_cache_dir, frozen)
    predictions, metrics, auxiliary = _score_final_methods(
        frozen, final_cache_dir, device_name
    )
    expected_conversations = int(frozen["final_test_conversations"])
    if len(predictions) != expected_conversations:
        raise ValueError(
            f"Expected {expected_conversations} final conversations, got {len(predictions)}"
        )
    frozen_before_write = preflight_frozen_protocol(frozen_protocol_path)
    if (
        frozen_before_write["canonical_payload_sha256"]
        != frozen["canonical_payload_sha256"]
    ):
        raise ValueError("Frozen protocol changed during final scoring")
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "per_conversation_predictions.csv"
    predictions.to_csv(predictions_path, index=False)
    result = {
        "schema_version": 1,
        "status": "FINAL_TEST_EVALUATION_COMPLETED",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": frozen["endpoint"],
        "frozen_protocol_payload_sha256": frozen[
            "canonical_payload_sha256"
        ],
        "final_cache_manifest_payload_sha256": final_cache_record[
            "canonical_payload_sha256"
        ],
        "metrics": metrics,
        **auxiliary,
        "predictions_sha256": sha256_file(predictions_path),
        "final_test_scored": True,
        "historical_test_scored": False,
        "result_must_be_reported_even_if_lstm_does_not_win": True,
    }
    result["canonical_payload_sha256"] = canonical_sha256(result)
    write_json(output_dir / "final_evaluation.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--frozen-protocol", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--frozen-protocol", type=Path, required=True)
    run.add_argument("--final-test-claim", type=Path, required=True)
    run.add_argument("--final-cache-dir", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    run.add_argument("--cache-batch-size", type=int, default=128)
    run.add_argument("--device")
    run.add_argument(
        "--local-files-only", action=argparse.BooleanOptionalAction, default=True
    )
    args = parser.parse_args()
    if args.command == "preflight":
        result = preflight_frozen_protocol(args.frozen_protocol)
        print(
            "Preflight passed. Frozen protocol hash: "
            f"{result['canonical_payload_sha256']}"
        )
    else:
        result = run_final_evaluation(
            args.frozen_protocol,
            args.final_test_claim,
            args.final_cache_dir,
            args.output_dir,
            args.cache_batch_size,
            args.device,
            args.local_files_only,
        )
        print(json.dumps(result["metrics"], indent=2))


if __name__ == "__main__":
    main()
