"""Freeze and consume an auditable one-time final-test gate.

The gate prevents accidental test iteration.  It is an operational safeguard
inside a mutable local repository, not a claim of tamper-proof security.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    canonical_sha256,
    load_locked_manifest,
    sha256_file,
    tree_sha256,
    validate_layer1_run,
    write_json,
)


FREEZE_ACKNOWLEDGEMENT = "FREEZE_COMPLETE_PROTOCOL_BEFORE_FINAL_TEST"
ARM_ACKNOWLEDGEMENT = "SCORE_LOCKED_FINAL_TEST_EXACTLY_ONCE"


def _load_canonical_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    payload = dict(value)
    expected = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected:
        raise ValueError(f"Canonical JSON integrity failed: {path}")
    return value


def _require_false_flags(record: dict[str, Any], name: str) -> None:
    if record.get("final_test_scored") is not False:
        raise ValueError(f"{name} does not prove final_test_scored=false")
    if record.get("historical_test_scored") is not False:
        raise ValueError(f"{name} does not prove historical_test_scored=false")


def _hash_role(path: Path) -> dict[str, Any]:
    path = path.resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    return {
        "path": str(path),
        "kind": "directory" if path.is_dir() else "file",
        "sha256": tree_sha256(path) if path.is_dir() else sha256_file(path),
    }


def code_tree_sha256(root: Path) -> str:
    """Hash only authored Python sources, never transient pycache files."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _hash_code_role(path: Path) -> dict[str, Any]:
    path = path.resolve()
    return {
        "path": str(path),
        "kind": "python-source-tree",
        "sha256": code_tree_sha256(path),
    }


def preflight_frozen_protocol(path: Path) -> dict[str, Any]:
    frozen = _load_canonical_json(path.resolve())
    if frozen.get("status") != "FROZEN_READY_FOR_ONE_FINAL_EVALUATION":
        raise ValueError("Protocol is not frozen for final evaluation")
    for role_name, role in frozen.get("artifact_roles", {}).items():
        role_path = Path(role["path"])
        if not role_path.exists():
            raise FileNotFoundError(f"Frozen artifact is missing ({role_name}): {role_path}")
        if role.get("kind") == "python-source-tree":
            actual = code_tree_sha256(role_path)
        elif role_path.is_dir():
            actual = tree_sha256(role_path)
        else:
            actual = sha256_file(role_path)
        if actual != role.get("sha256"):
            raise ValueError(f"Frozen artifact changed after freeze: {role_name}")
    return frozen


def freeze_protocol(
    *,
    data_file: Path,
    split_manifest_path: Path,
    package_manifest_path: Path,
    component_audit_path: Path,
    layer1_run: Path,
    development_cache: Path,
    centroid_dir: Path,
    comparator_dir: Path,
    keyword_dir: Path,
    lstm7_search: Path,
    lstm775_search: Path,
    output: Path,
    acknowledgement: str,
) -> dict[str, Any]:
    if acknowledgement != FREEZE_ACKNOWLEDGEMENT:
        raise PermissionError(f"Required acknowledgement: {FREEZE_ACKNOWLEDGEMENT}")
    if output.exists():
        raise FileExistsError(f"Frozen protocol already exists: {output}")
    manifest = load_locked_manifest(split_manifest_path, data_file)
    if sha256_file(component_audit_path) != manifest["historical_audit"]["sha256"]:
        raise ValueError("Connected-component audit does not match locked split")
    layer1_receipt = validate_layer1_run(
        layer1_run,
        split_manifest_path,
        package_manifest_path,
        data_file,
    )

    cache_record = _load_canonical_json(development_cache / "cache_manifest.json")
    if set(cache_record.get("splits", [])) != {"train", "validation"}:
        raise ValueError("Development cache must contain exactly train and validation")
    if cache_record.get("development_only") is not True:
        raise ValueError("Development cache is not marked development-only")
    _require_false_flags(cache_record, "development cache")
    cache_provenance = cache_record.get("provenance", {})
    if cache_provenance.get("data_sha256") != manifest["dataset"]["sha256"]:
        raise ValueError("Development cache uses a different dataset")
    if (
        cache_provenance.get("split_manifest_payload_sha256")
        != manifest["integrity"]["canonical_payload_sha256"]
    ):
        raise ValueError("Development cache uses a different split manifest")
    if (
        cache_provenance.get("layer1_model_tree_sha256")
        != layer1_receipt["best_model_tree_sha256"]
    ):
        raise ValueError("Development cache uses a different Layer 1 model")
    if (
        cache_provenance.get("component_audit_sha256")
        != sha256_file(component_audit_path)
    ):
        raise ValueError("Development cache uses a different component audit")
    train_cache_record = _load_canonical_json(
        development_cache / "train" / "manifest.json"
    )
    validation_cache_record = _load_canonical_json(
        development_cache / "validation" / "manifest.json"
    )
    expected_partition_hashes = cache_record.get(
        "partition_manifest_payload_sha256", {}
    )
    if (
        expected_partition_hashes.get("train")
        != train_cache_record["canonical_payload_sha256"]
        or expected_partition_hashes.get("validation")
        != validation_cache_record["canonical_payload_sha256"]
    ):
        raise ValueError("Development cache root and partition manifests disagree")
    from .cache import load_partition_cache

    # Verify the referenced index/score/embedding files, not only the JSON
    # wrappers. This intentionally happens before an irreversible gate exists.
    _train_index, _train_scores, _train_embeddings, loaded_train_record = (
        load_partition_cache(development_cache / "train", expected_split="train")
    )
    _validation_index, _validation_scores, _validation_embeddings, loaded_validation_record = (
        load_partition_cache(
            development_cache / "validation", expected_split="validation"
        )
    )
    if (
        loaded_train_record["canonical_payload_sha256"]
        != train_cache_record["canonical_payload_sha256"]
        or loaded_validation_record["canonical_payload_sha256"]
        != validation_cache_record["canonical_payload_sha256"]
    ):
        raise ValueError("Loaded cache manifests disagree with frozen records")
    centroid_record = _load_canonical_json(centroid_dir / "centroid_manifest.json")
    if centroid_record.get("source_split") != "train":
        raise ValueError("Centroid was not produced from training only")
    if centroid_record.get("is_suspicious_used") is not False:
        raise ValueError("Centroid does not exclude is_suspicious")
    if (
        centroid_record.get("source_cache_manifest_payload_sha256")
        != train_cache_record["canonical_payload_sha256"]
    ):
        raise ValueError("Centroid was built from a different training cache")
    for field in [
        "base_encoder_state_sha256",
        "base_encoder_config_sha256",
        "base_tokenizer",
        "torch_version",
        "transformers_version",
    ]:
        if centroid_record.get(field) != cache_provenance.get(field):
            raise ValueError(f"Centroid base-model provenance mismatch: {field}")
    from .centroid import load_centroid

    _centroid_vector, loaded_centroid_record = load_centroid(centroid_dir)
    if (
        loaded_centroid_record["canonical_payload_sha256"]
        != centroid_record["canonical_payload_sha256"]
    ):
        raise ValueError("Loaded centroid manifest disagrees with frozen record")

    feature_record = _load_canonical_json(comparator_dir / "feature_config.json")
    raw_record = _load_canonical_json(comparator_dir / "raw_layer1_config.json")
    weighted_record = _load_canonical_json(
        comparator_dir / "weighted_scorer_config.json"
    )
    if feature_record.get("architecture_outcomes_used") is not False:
        raise ValueError("Feature thresholds were selected from architecture outcomes")
    if (
        feature_record.get("validation_cache_manifest_payload_sha256")
        != validation_cache_record["canonical_payload_sha256"]
    ):
        raise ValueError("Feature configuration uses a different validation cache")
    for name, record in {
        "raw Layer 1": raw_record,
        "weighted scorer": weighted_record,
    }.items():
        if record.get("selection_partition") != "validation":
            raise ValueError(f"{name} was not selected on validation")
        _require_false_flags(record, name)
        if (
            record.get("validation_cache_manifest_payload_sha256")
            != validation_cache_record["canonical_payload_sha256"]
        ):
            raise ValueError(f"{name} uses a different validation cache")
        if (
            record.get("centroid_manifest_payload_sha256")
            != centroid_record["canonical_payload_sha256"]
        ):
            raise ValueError(f"{name} uses a different centroid")
    if raw_record.get("extra_sigmoid") is not False or raw_record.get("aggregation") != "max":
        raise ValueError("Raw Layer 1 comparator is not the approved direct max score")
    if (
        weighted_record.get("feature_config_payload_sha256")
        != feature_record.get("canonical_payload_sha256")
    ):
        raise ValueError("Weighted scorer and feature configuration disagree")
    from .comparators import validate_comparator_artifacts

    comparator_validation = validate_comparator_artifacts(
        development_cache / "validation", centroid_dir, comparator_dir
    )

    keyword_record = _load_canonical_json(keyword_dir / "keyword_config.json")
    if keyword_record.get("derivation_partition") != "train":
        raise ValueError("Keyword lexicon was not derived from training only")
    _require_false_flags(keyword_record, "keyword baseline")
    if keyword_record.get("data_sha256") != manifest["dataset"]["sha256"]:
        raise ValueError("Keyword baseline uses a different dataset")
    if (
        keyword_record.get("split_manifest_payload_sha256")
        != manifest["integrity"]["canonical_payload_sha256"]
    ):
        raise ValueError("Keyword baseline uses a different split manifest")
    from .keyword import validate_keyword_artifacts

    keyword_validation = validate_keyword_artifacts(
        data_file, split_manifest_path, keyword_dir
    )

    lstm_records: dict[str, dict[str, Any]] = {}
    feature_config_file_sha256 = sha256_file(comparator_dir / "feature_config.json")
    from .dataset import load_conversation_sequences
    from .lstm import LSTM_SOURCE_FILES, validate_lstm_run
    from .lstm_search import PLAN_PATH, validate_search

    validation_sequences, _sequence_metadata = load_conversation_sequences(
        development_cache / "validation",
        centroid_dir,
        "validation",
        float(feature_record["spike_threshold"]),
        float(feature_record["drop_threshold"]),
    )
    lstm_deep_validation: dict[str, Any] = {}
    selected_lstm_dirs: dict[str, Path] = {}
    search_validation: dict[str, Any] = {}
    for expected_mode, search_directory in {
        "trajectory7": lstm7_search,
        "enhanced775": lstm775_search,
    }.items():
        search_validation[expected_mode] = validate_search(
            search_directory,
            validation_sequences,
            expected_mode,
            PLAN_PATH,
        )
        directory = Path(search_validation[expected_mode]["selected_run"])
        selected_lstm_dirs[expected_mode] = directory
        configuration = json.loads(
            (directory / "run_configuration.json").read_text(encoding="utf-8")
        )
        summary = json.loads((directory / "run_summary.json").read_text(encoding="utf-8"))
        threshold = json.loads(
            (directory / "selected_threshold.json").read_text(encoding="utf-8")
        )
        if configuration.get("config", {}).get("input_mode") != expected_mode:
            raise ValueError(f"Wrong LSTM input mode in {directory}")
        if configuration.get("supervision") != "conversation label only":
            raise ValueError(f"LSTM supervision is not conversation-only: {directory}")
        if float(configuration.get("turn_loss_weight", -1)) != 0.0:
            raise ValueError(f"LSTM turn loss is enabled: {directory}")
        if configuration.get("checkpoint_objective") != "validation PR-AUC":
            raise ValueError(f"LSTM checkpoint objective is wrong: {directory}")
        if (
            configuration.get("provenance", {}).get("feature_config_sha256")
            != feature_config_file_sha256
        ):
            raise ValueError(f"LSTM did not use the frozen feature configuration: {directory}")
        lstm_provenance = configuration.get("provenance", {})
        expected_lstm_provenance = {
            "train_cache_manifest_payload_sha256": train_cache_record[
                "canonical_payload_sha256"
            ],
            "validation_cache_manifest_payload_sha256": validation_cache_record[
                "canonical_payload_sha256"
            ],
            "centroid_manifest_payload_sha256": centroid_record[
                "canonical_payload_sha256"
            ],
        }
        for field, expected_value in expected_lstm_provenance.items():
            if lstm_provenance.get(field) != expected_value:
                raise ValueError(f"LSTM provenance mismatch for {field}: {directory}")
        if threshold.get("selection_partition") != "validation":
            raise ValueError(f"LSTM threshold is not validation-selected: {directory}")
        _require_false_flags(configuration, f"{expected_mode} LSTM configuration")
        _require_false_flags(summary, f"{expected_mode} LSTM summary")
        if summary.get("status") != "completed":
            raise ValueError(f"LSTM run is incomplete: {directory}")
        if not (directory / "best_model.pt").is_file():
            raise ValueError(f"LSTM checkpoint is absent: {directory}")
        if sha256_file(directory / "best_model.pt") != summary.get("model_sha256"):
            raise ValueError(f"LSTM checkpoint hash mismatch: {directory}")
        source_hashes = configuration.get("runtime", {}).get("source_sha256", {})
        if set(source_hashes) != set(LSTM_SOURCE_FILES):
            raise ValueError(f"LSTM source-hash inventory is incomplete: {directory}")
        for source_name in LSTM_SOURCE_FILES:
            recorded_hash = source_hashes[source_name]
            source_path = Path(__file__).resolve().parent / source_name
            if not source_path.is_file() or sha256_file(source_path) != recorded_hash:
                raise ValueError(
                    f"LSTM training source changed since model fitting: {source_name}"
                )
        lstm_deep_validation[expected_mode] = validate_lstm_run(
            directory, validation_sequences, expected_mode
        )
        lstm_records[expected_mode] = summary

    code_root = Path(__file__).resolve().parent
    roles = {
        "data_file": _hash_role(data_file),
        "split_manifest": _hash_role(split_manifest_path),
        "component_audit": _hash_role(component_audit_path),
        "package_manifest": _hash_role(package_manifest_path),
        "layer1_run": _hash_role(layer1_run),
        "development_cache": _hash_role(development_cache),
        "centroid": _hash_role(centroid_dir),
        "comparators": _hash_role(comparator_dir),
        "keyword": _hash_role(keyword_dir),
        "lstm_experiment_plan": _hash_role(PLAN_PATH),
        "lstm_trajectory7_search": _hash_role(lstm7_search),
        "lstm_enhanced775_search": _hash_role(lstm775_search),
        "lstm_trajectory7": _hash_role(selected_lstm_dirs["trajectory7"]),
        "lstm_enhanced775": _hash_role(selected_lstm_dirs["enhanced775"]),
        "revised_pipeline_code": _hash_code_role(code_root),
    }
    frozen = {
        "schema_version": 1,
        "status": "FROZEN_READY_FOR_ONE_FINAL_EVALUATION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "endpoint": "PAN12 conversation contains at least one listed predator author",
        "dataset_sha256": manifest["dataset"]["sha256"],
        "split_manifest_payload_sha256": manifest["integrity"][
            "canonical_payload_sha256"
        ],
        "final_test_conversations": manifest["splits"]["final_test"][
            "conversations"
        ],
        "excluded_historical_test_conversations": manifest["splits"][
            "excluded_historical_test"
        ]["conversations"],
        "score_comparison": ">= threshold",
        "threshold_objective": "validation F0.5",
        "checkpoint_objective": "validation PR-AUC",
        "confidence_interval_unit": "connected-author component",
        "confidence_interval_level": 0.95,
        "confidence_interval_bootstrap_seed": 42,
        "confidence_interval_bootstrap_replicates": 2000,
        "prefix_scores": "exploratory only",
        "layer1_receipt": layer1_receipt,
        "deep_validation": {
            "cache_files": True,
            "centroid_files": True,
            "comparators": comparator_validation,
            "keyword": keyword_validation,
            "lstm_search": search_validation,
            "lstm": lstm_deep_validation,
        },
        "artifact_roles": roles,
        # The ledger is derived from the locked dataset/split, not from this
        # protocol filename. Creating a second frozen JSON therefore cannot
        # create a second ordinary-use claim for the same holdout.
        "gate_registry_path": str(
            split_manifest_path.resolve().parent
            / ".final_test_ledger"
            / (
                manifest["dataset"]["sha256"][:16]
                + "-"
                + manifest["integrity"]["canonical_payload_sha256"][:16]
            )
        ),
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    frozen["canonical_payload_sha256"] = canonical_sha256(frozen)
    write_json(output, frozen)
    return frozen


def arm_gate(
    frozen_protocol: Path,
    expected_protocol_hash: str,
    acknowledgement: str,
) -> dict[str, Any]:
    if acknowledgement != ARM_ACKNOWLEDGEMENT:
        raise PermissionError(f"Required acknowledgement: {ARM_ACKNOWLEDGEMENT}")
    frozen = _load_canonical_json(frozen_protocol)
    actual_hash = frozen["canonical_payload_sha256"]
    if expected_protocol_hash != actual_hash:
        raise ValueError("Typed frozen-protocol hash does not match the file")
    if frozen.get("status") != "FROZEN_READY_FOR_ONE_FINAL_EVALUATION":
        raise ValueError("Protocol is not in the frozen-ready state")
    registry = Path(frozen["gate_registry_path"])
    try:
        registry.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise FileExistsError(
            "This frozen protocol has already been armed or consumed"
        ) from exc
    output_claim = registry / "claim.json"
    claim = {
        "schema_version": 1,
        "status": "ARMED_NOT_YET_CONSUMED",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_protocol_path": str(frozen_protocol.resolve()),
        "frozen_protocol_file_sha256": sha256_file(frozen_protocol),
        "frozen_protocol_payload_sha256": actual_hash,
        "dataset_sha256": frozen["dataset_sha256"],
        "split_manifest_payload_sha256": frozen[
            "split_manifest_payload_sha256"
        ],
        "acknowledgement": acknowledgement,
        "gate_registry_path": str(registry.resolve()),
        "canonical_claim_path": str(output_claim.resolve()),
    }
    claim["canonical_payload_sha256"] = canonical_sha256(claim)
    write_json(output_claim, claim)
    return claim


def validate_claim(
    claim_path: Path,
    split_manifest: dict[str, Any],
) -> dict[str, Any]:
    claim_path = claim_path.resolve()
    claim = _load_canonical_json(claim_path)
    if claim.get("status") != "ARMED_NOT_YET_CONSUMED":
        raise PermissionError("Final-test claim is not armed")
    if claim.get("dataset_sha256") != split_manifest["dataset"]["sha256"]:
        raise ValueError("Final-test claim names a different dataset")
    if (
        claim.get("split_manifest_payload_sha256")
        != split_manifest["integrity"]["canonical_payload_sha256"]
    ):
        raise ValueError("Final-test claim names a different split")
    frozen_path = Path(claim["frozen_protocol_path"])
    if sha256_file(frozen_path) != claim["frozen_protocol_file_sha256"]:
        raise ValueError("Frozen protocol changed after the final gate was armed")
    frozen = _load_canonical_json(frozen_path)
    if (
        frozen["canonical_payload_sha256"]
        != claim["frozen_protocol_payload_sha256"]
    ):
        raise ValueError("Final-test claim and frozen protocol disagree")
    expected_registry = Path(frozen["gate_registry_path"]).resolve()
    if Path(claim.get("gate_registry_path", "")).resolve() != expected_registry:
        raise ValueError("Final-test claim uses the wrong gate registry")
    expected_claim_path = expected_registry / "claim.json"
    if claim_path != expected_claim_path or claim.get("canonical_claim_path") != str(
        expected_claim_path
    ):
        raise PermissionError("Copied or renamed final-test claims are invalid")
    consumed_path = expected_registry / "consumed.json"
    if consumed_path.exists():
        raise PermissionError("The one-time final-test claim has already been consumed")
    return claim


def validate_final_cache_request(
    claim_path: Path,
    split_manifest: dict[str, Any],
    provided_roles: dict[str, Path],
    *,
    torch_version: str,
    transformers_version: str,
    base_model_name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind a final-cache request to every frozen input before consumption."""
    claim = validate_claim(claim_path, split_manifest)
    frozen_path = Path(claim["frozen_protocol_path"]).resolve()
    frozen = preflight_frozen_protocol(frozen_path)
    if (
        claim.get("frozen_protocol_payload_sha256")
        != frozen.get("canonical_payload_sha256")
    ):
        raise ValueError("Final-test claim is not bound to the frozen protocol")
    for role_name, provided_path in provided_roles.items():
        frozen_role = frozen.get("artifact_roles", {}).get(role_name)
        if frozen_role is None:
            raise ValueError(f"Frozen protocol omits final-cache role: {role_name}")
        if Path(frozen_role["path"]).resolve() != Path(provided_path).resolve():
            raise ValueError(
                f"Final-cache request does not use frozen artifact: {role_name}"
            )
    development_cache = _load_canonical_json(
        Path(frozen["artifact_roles"]["development_cache"]["path"])
        / "cache_manifest.json"
    )
    provenance = development_cache.get("provenance", {})
    expected_runtime = {
        "torch_version": str(torch_version),
        "transformers_version": str(transformers_version),
        "base_encoder_name": base_model_name,
    }
    for field, actual in expected_runtime.items():
        if provenance.get(field) != actual:
            raise ValueError(
                f"Final-cache runtime differs from development before gate consumption: {field}"
            )
    return frozen, provenance


def consume_claim(
    claim_path: Path,
    split_manifest: dict[str, Any],
) -> dict[str, Any]:
    claim = validate_claim(claim_path, split_manifest)
    consumed_path = Path(claim["gate_registry_path"]) / "consumed.json"
    receipt = {
        "schema_version": 1,
        "status": "CONSUMED_BEFORE_FINAL_ROWS_SCORED_OR_CACHED",
        "consumed_utc": datetime.now(timezone.utc).isoformat(),
        "claim_file_sha256": sha256_file(claim_path),
        "claim_payload_sha256": claim["canonical_payload_sha256"],
        "frozen_protocol_payload_sha256": claim[
            "frozen_protocol_payload_sha256"
        ],
    }
    receipt["canonical_payload_sha256"] = canonical_sha256(receipt)
    serialized = json.dumps(receipt, indent=2, ensure_ascii=False) + "\n"
    try:
        with consumed_path.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise PermissionError("The one-time final-test claim was already consumed") from exc
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze = subparsers.add_parser("freeze")
    for name in [
        "data-file", "split-manifest", "package-manifest", "component-audit",
        "layer1-run", "development-cache", "centroid-dir", "comparator-dir",
        "keyword-dir", "lstm7-search", "lstm775-search", "output",
    ]:
        freeze.add_argument(f"--{name}", type=Path, required=True)
    freeze.add_argument("--acknowledgement", required=True)
    arm = subparsers.add_parser("arm")
    arm.add_argument("--frozen-protocol", type=Path, required=True)
    arm.add_argument("--expected-protocol-hash", required=True)
    arm.add_argument("--acknowledgement", required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze_protocol(
            data_file=args.data_file,
            split_manifest_path=args.split_manifest,
            package_manifest_path=args.package_manifest,
            component_audit_path=args.component_audit,
            layer1_run=args.layer1_run,
            development_cache=args.development_cache,
            centroid_dir=args.centroid_dir,
            comparator_dir=args.comparator_dir,
            keyword_dir=args.keyword_dir,
            lstm7_search=args.lstm7_search,
            lstm775_search=args.lstm775_search,
            output=args.output,
            acknowledgement=args.acknowledgement,
        )
    else:
        result = arm_gate(
            args.frozen_protocol,
            args.expected_protocol_hash,
            args.acknowledgement,
        )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
