"""Integrity contracts for the revised author-proxy experiment."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_LAYER1_ARGUMENTS: dict[str, Any] = {
    "model_name": "distilbert-base-uncased",
    "max_length": 128,
    "negative_ratio": 3.0,
    "epochs": 5.0,
    "learning_rate": 2e-5,
    "weight_decay": 0.01,
    "warmup_ratio": 0.10,
    "gradient_accumulation_steps": 1,
    "gradient_clip": 1.0,
    "early_stopping_patience": 2,
    "seed": 42,
    "require_cuda": True,
    "auto_find_batch_size": True,
    "dry_run": False,
}

ALLOWED_LAYER1_REQUESTED_BATCH_PAIRS = {
    (64, 128),
    (128, 256),
}

EXPECTED_LAYER1_GUARDS: dict[str, Any] = {
    "label": "official is_predator author membership only",
    "is_suspicious_loaded": False,
    "context": "current turn plus up to two preceding turns",
    "author_ids_in_model_text": False,
    "negative_sampling": "training only",
    "validation_distribution_untouched": True,
    "final_test_scored": False,
    "historical_test_scored": False,
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def load_locked_manifest(path: Path, data_file: Path | None = None) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    integrity = manifest.get("integrity", {})
    payload = copy.deepcopy(manifest)
    payload.pop("integrity", None)
    actual = canonical_sha256(payload)
    expected = integrity.get("canonical_payload_sha256")
    if not expected or actual != expected:
        raise ValueError(
            "Locked split manifest failed its canonical SHA-256 check: "
            f"expected {expected}, got {actual}"
        )
    required_invariants = {
        "all_eligible_conversations_assigned_once",
        "conversation_overlap_is_zero",
        "author_overlap_is_zero",
        "component_overlap_is_zero",
        "historical_test_is_excluded",
        "final_test_originates_only_from_historical_train",
    }
    invariants = manifest.get("invariants", {})
    failed = sorted(
        name for name in required_invariants if invariants.get(name) is not True
    )
    if failed:
        raise ValueError(f"Locked split invariants are not satisfied: {failed}")
    if data_file is not None:
        if sha256_file(data_file) != manifest["dataset"]["sha256"]:
            raise ValueError("PAN12 data file does not match the locked SHA-256")
        if data_file.stat().st_size != int(manifest["dataset"]["bytes"]):
            raise ValueError("PAN12 data file does not match the locked byte count")
    return manifest


def _values_match(actual: Any, expected: Any) -> bool:
    if isinstance(expected, float):
        try:
            return math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-12)
        except (TypeError, ValueError):
            return False
    return actual == expected


def _package_trainer_hash(package_manifest: dict[str, Any]) -> str:
    matches = [
        row["sha256"]
        for row in package_manifest.get("files", [])
        if row.get("path") == "train_layer1_author_proxy.py"
    ]
    if len(matches) != 1:
        raise ValueError("Package manifest does not identify exactly one Layer 1 trainer")
    return matches[0]


def validate_layer1_run(
    run_dir: Path,
    split_manifest_path: Path,
    package_manifest_path: Path,
    data_file: Path,
) -> dict[str, Any]:
    """Validate a returned teammate run before any downstream model consumes it."""
    run_dir = run_dir.resolve()
    required = {
        "best_model": run_dir / "best_model",
        "run_configuration": run_dir / "run_configuration.json",
        "run_summary": run_dir / "run_summary.json",
        "selected_threshold": run_dir / "selected_threshold.json",
        "validation_predictions": run_dir / "validation_predictions.csv",
    }
    missing = [name for name, path in required.items() if not path.exists()]
    if missing:
        raise ValueError(f"Returned Layer 1 run is missing: {missing}")
    if not required["best_model"].is_dir():
        raise ValueError("best_model must be a directory")

    suspicious_artifacts = sorted(
        path.relative_to(run_dir).as_posix()
        for path in run_dir.rglob("*")
        if path.is_file()
        and (
            "final_test" in path.name.lower()
            or "final-test" in path.name.lower()
            or "test_predictions" in path.name.lower()
        )
    )
    if suspicious_artifacts:
        raise ValueError(
            "Returned run contains a prohibited test-scoring artifact: "
            f"{suspicious_artifacts}"
        )

    data_file = data_file.resolve()
    manifest = load_locked_manifest(split_manifest_path.resolve(), data_file)
    package_manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))
    configuration = json.loads(required["run_configuration"].read_text(encoding="utf-8"))
    summary = json.loads(required["run_summary"].read_text(encoding="utf-8"))
    threshold_record = json.loads(
        required["selected_threshold"].read_text(encoding="utf-8")
    )

    if configuration.get("package_version") != package_manifest.get("version"):
        raise ValueError("Layer 1 package version does not match the transfer manifest")
    if configuration.get("data_sha256") != manifest["dataset"]["sha256"]:
        raise ValueError("Layer 1 run used a different dataset")
    split_hash = manifest["integrity"]["canonical_payload_sha256"]
    if configuration.get("split_manifest_payload_sha256") != split_hash:
        raise ValueError("Layer 1 run used a different split manifest")
    if configuration.get("script_sha256") != _package_trainer_hash(package_manifest):
        raise ValueError("Layer 1 run used a modified training script")

    arguments = configuration.get("arguments", {})
    argument_errors = {
        key: {"expected": expected, "actual": arguments.get(key)}
        for key, expected in EXPECTED_LAYER1_ARGUMENTS.items()
        if not _values_match(arguments.get(key), expected)
    }
    if argument_errors:
        raise ValueError(f"Layer 1 locked arguments changed: {argument_errors}")
    requested_batch_pair = (
        int(arguments.get("train_batch_size", -1)),
        int(arguments.get("eval_batch_size", -1)),
    )
    if requested_batch_pair not in ALLOWED_LAYER1_REQUESTED_BATCH_PAIRS:
        raise ValueError(
            "Layer 1 requested batch sizes are outside the documented "
            f"hardware-dependent choices: {requested_batch_pair}"
        )
    guard_errors = {
        key: {"expected": expected, "actual": configuration.get("methodology_guards", {}).get(key)}
        for key, expected in EXPECTED_LAYER1_GUARDS.items()
        if configuration.get("methodology_guards", {}).get(key) != expected
    }
    if guard_errors:
        raise ValueError(f"Layer 1 methodology guard failed: {guard_errors}")

    expected_rows = manifest["splits"]["validation"]
    row_counts = configuration.get("row_counts", {})
    train_positive_rows = int(manifest["splits"]["train"]["positive_author_rows"])
    train_negative_rows = int(manifest["splits"]["train"]["negative_author_rows"])
    sampled_training_negatives = min(
        train_negative_rows,
        int(round(train_positive_rows * float(EXPECTED_LAYER1_ARGUMENTS["negative_ratio"]))),
    )
    expected_config_counts = {
        "train_before_negative_sampling": manifest["splits"]["train"]["rows"],
        "train_after_negative_sampling": train_positive_rows + sampled_training_negatives,
        "train_positive": train_positive_rows,
        "train_negative": sampled_training_negatives,
        "validation": expected_rows["rows"],
        "validation_positive": expected_rows["positive_author_rows"],
        "validation_negative": expected_rows["negative_author_rows"],
    }
    for key, expected in expected_config_counts.items():
        if int(row_counts.get(key, -1)) != int(expected):
            raise ValueError(
                f"Layer 1 row count mismatch for {key}: "
                f"expected {expected}, got {row_counts.get(key)}"
            )

    if summary.get("status") != "completed":
        raise ValueError("Layer 1 run summary is not completed")
    if summary.get("final_test_scored") is not False:
        raise ValueError("Layer 1 run reports that the locked final test was scored")
    if summary.get("historical_test_scored") is not False:
        raise ValueError("Layer 1 run reports that the historical test was scored")
    trainer_state_paths = sorted(
        (run_dir / "checkpoints").glob("checkpoint-*/trainer_state.json")
    )
    if not trainer_state_paths:
        raise ValueError(
            "Returned Layer 1 run omits checkpoint trainer_state.json; "
            "the effective auto-selected batch size cannot be audited"
        )
    effective_batch_sizes = {
        int(json.loads(path.read_text(encoding="utf-8")).get("train_batch_size", -1))
        for path in trainer_state_paths
    }
    if len(effective_batch_sizes) != 1:
        raise ValueError("Returned Layer 1 checkpoints disagree on effective batch size")
    effective_train_batch_size = next(iter(effective_batch_sizes))
    if (
        effective_train_batch_size <= 0
        or effective_train_batch_size > requested_batch_pair[0]
        or effective_train_batch_size & (effective_train_batch_size - 1)
    ):
        raise ValueError(
            "Returned Layer 1 effective batch size is invalid or exceeds the request"
        )
    actual_model_hash = tree_sha256(required["best_model"])
    if summary.get("best_model_tree_sha256") != actual_model_hash:
        raise ValueError("Returned best_model tree does not match run_summary.json")
    model_config = json.loads(
        (required["best_model"] / "config.json").read_text(encoding="utf-8")
    )
    configured_label_count = model_config.get("num_labels")
    if configured_label_count is None:
        configured_label_count = len(model_config.get("id2label", {}))
    if int(configured_label_count) != 2:
        raise ValueError("Returned Layer 1 classifier does not have exactly two labels")
    expected_label2id = {
        "NOT_LISTED_PREDATOR_AUTHOR": 0,
        "LISTED_PREDATOR_AUTHOR": 1,
    }
    if model_config.get("label2id") != expected_label2id:
        raise ValueError("Returned Layer 1 positive class is not label index 1")

    threshold = float(threshold_record.get("threshold", float("nan")))
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("Layer 1 validation threshold is not a finite value in [0, 1]")
    if threshold_record.get("selection_partition") != "validation":
        raise ValueError("Layer 1 threshold was not selected on validation")
    if threshold_record.get("objective") != "maximum F0.5":
        raise ValueError("Layer 1 threshold objective is not the locked F0.5 objective")
    if not math.isclose(
        float(summary.get("selected_threshold", float("nan"))),
        threshold,
        rel_tol=1e-12,
        abs_tol=1e-12,
    ):
        raise ValueError("Layer 1 threshold artifacts disagree")

    predictions = pd.read_csv(required["validation_predictions"])
    expected_columns = {
        "row_id",
        "conversation_id",
        "line",
        "label",
        "probability",
        "prediction",
    }
    if set(predictions.columns) != expected_columns:
        raise ValueError(
            "validation_predictions.csv has an unexpected schema: "
            f"{list(predictions.columns)}"
        )
    if len(predictions) != int(expected_rows["rows"]):
        raise ValueError("Layer 1 validation prediction count is incomplete")
    if predictions["row_id"].duplicated().any():
        raise ValueError("Layer 1 validation predictions contain duplicate row IDs")
    validation_ids = set(expected_rows["conversation_ids"])
    if set(predictions["conversation_id"]) != validation_ids:
        raise ValueError("Layer 1 predictions do not exactly cover validation conversations")
    prohibited_ids = set(manifest["splits"]["final_test"]["conversation_ids"])
    prohibited_ids.update(
        manifest["splits"]["excluded_historical_test"]["conversation_ids"]
    )
    if set(predictions["conversation_id"]) & prohibited_ids:
        raise ValueError("Layer 1 validation artifact contains a test conversation")
    if not predictions["label"].isin([0, 1]).all():
        raise ValueError("Layer 1 validation labels are not binary")
    if int(predictions["label"].sum()) != int(expected_rows["positive_author_rows"]):
        raise ValueError("Layer 1 validation positive-label count is wrong")

    # Regenerate the exact validation stable IDs and author labels from the
    # locked CSV. This catches missing/extra lines even when aggregate counts
    # and conversation membership happen to match.
    from .data import attach_locked_splits, build_context_records, load_eligible_rows

    regenerated = build_context_records(
        attach_locked_splits(load_eligible_rows(data_file), manifest).loc[
            lambda value: value["split"] == "validation"
        ]
    )[["row_id", "conversation_id", "line", "author_label"]].rename(
        columns={"author_label": "label"}
    )
    observed = predictions[["row_id", "conversation_id", "line", "label"]].copy()
    regenerated = regenerated.sort_values("row_id", kind="stable").reset_index(drop=True)
    observed = observed.sort_values("row_id", kind="stable").reset_index(drop=True)
    try:
        pd.testing.assert_frame_equal(regenerated, observed, check_dtype=False)
    except AssertionError as exc:
        raise ValueError("Layer 1 validation row IDs or labels differ from locked data")
    probabilities = pd.to_numeric(predictions["probability"], errors="coerce")
    if probabilities.isna().any() or not probabilities.between(0.0, 1.0).all():
        raise ValueError("Layer 1 validation probabilities are invalid")
    expected_predictions = (probabilities.to_numpy() >= threshold).astype(np.int8)
    if not np.array_equal(
        expected_predictions,
        pd.to_numeric(predictions["prediction"], errors="coerce").to_numpy(),
    ):
        raise ValueError("Layer 1 validation predictions do not use the recorded threshold")

    from .metrics import conversation_metrics, select_f05_threshold

    labels = predictions["label"].to_numpy(dtype=np.int8)
    probabilities_array = probabilities.to_numpy(dtype=np.float64)
    recomputed_threshold, recomputed_metrics = select_f05_threshold(
        labels, probabilities_array
    )
    if not math.isclose(recomputed_threshold, threshold, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("Recorded Layer 1 threshold is not the validation F0.5 optimum")
    recorded_metrics = threshold_record.get("metrics", {})
    trainer_metric_keys = {
        "threshold", "accuracy", "precision", "recall", "f1", "f0_5",
        "pr_auc", "roc_auc", "tn", "fp", "fn", "tp",
    }
    for key in trainer_metric_keys:
        actual = recomputed_metrics[key]
        if key not in recorded_metrics:
            raise ValueError(f"Layer 1 threshold artifact omits metric {key}")
        expected_metric = recorded_metrics[key]
        if actual is None:
            if expected_metric is not None:
                raise ValueError(f"Layer 1 metric mismatch for {key}")
        elif isinstance(actual, float):
            if not math.isclose(
                float(expected_metric), actual, rel_tol=1e-9, abs_tol=1e-9
            ):
                raise ValueError(f"Layer 1 metric mismatch for {key}")
        elif int(expected_metric) != int(actual):
            raise ValueError(f"Layer 1 metric mismatch for {key}")

    return {
        "schema_version": 1,
        "status": "accepted_for_revised_downstream_preparation",
        "layer1_run": str(run_dir),
        "data_sha256": manifest["dataset"]["sha256"],
        "split_manifest_payload_sha256": split_hash,
        "split_manifest_file_sha256": sha256_file(split_manifest_path),
        "package_version": configuration["package_version"],
        "best_model_tree_sha256": actual_model_hash,
        "selected_row_threshold": threshold,
        "requested_train_batch_size": requested_batch_pair[0],
        "requested_eval_batch_size": requested_batch_pair[1],
        "effective_train_batch_size": effective_train_batch_size,
        "validation_rows": len(predictions),
        "validation_conversations": len(validation_ids),
        "final_test_scored": False,
        "historical_test_scored": False,
        "artifact_sha256": {
            name: tree_sha256(path) if path.is_dir() else sha256_file(path)
            for name, path in required.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layer1-run", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--data-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate_layer1_run(
        args.layer1_run,
        args.split_manifest,
        args.package_manifest,
        args.data_file,
    )
    write_json(args.output, report)
    print(f"Layer 1 run accepted: {args.output.resolve()}")


if __name__ == "__main__":
    main()
