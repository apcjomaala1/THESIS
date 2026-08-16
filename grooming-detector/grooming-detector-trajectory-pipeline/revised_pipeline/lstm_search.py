"""Run and validate the finite, predeclared revised-LSTM search."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import canonical_sha256, sha256_file, tree_sha256, write_json
from .dataset import ConversationSequence, load_conversation_sequences
from .lstm import (
    LSTM_SOURCE_FILES,
    LSTMConfig,
    InputMode,
    train_lstm,
    validate_lstm_run,
)


PLAN_PATH = Path(__file__).with_name("experiment_plan.json")


def load_experiment_plan(path: Path = PLAN_PATH) -> dict[str, Any]:
    plan = json.loads(path.read_text(encoding="utf-8"))
    if plan.get("schema_version") != 1:
        raise ValueError("Unsupported LSTM experiment-plan schema")
    if plan.get("status") != "LOCKED_BEFORE_REVISED_LAYER1_RETURN":
        raise ValueError("LSTM experiment plan is not locked")
    if plan.get("selection_partition") != "validation":
        raise ValueError("LSTM experiment plan does not select on validation")
    if plan.get("checkpoint_objective") != "maximum validation average precision":
        raise ValueError("LSTM experiment plan uses the wrong checkpoint objective")
    if plan.get("final_test_used_for_selection") is not False:
        raise ValueError("LSTM experiment plan permits final-test selection")
    if plan.get("excluded_historical_test_used_for_selection") is not False:
        raise ValueError("LSTM experiment plan permits historical-test selection")
    common = plan.get("common_config", {})
    required_common = {
        "epochs",
        "batch_size",
        "weight_decay",
        "gradient_clip",
        "early_stopping_patience",
        "seed",
    }
    if set(common) != required_common or int(common.get("seed", -1)) != 42:
        raise ValueError("LSTM common configuration is incomplete or unlocked")
    modes = plan.get("modes", {})
    if set(modes) != {"trajectory7", "enhanced775"}:
        raise ValueError("LSTM plan must define trajectory7 and enhanced775")
    identifiers: list[str] = []
    required_candidate = {
        "candidate_id",
        "hidden_dim",
        "num_layers",
        "dropout",
        "learning_rate",
    }
    for mode, candidates in modes.items():
        if not candidates:
            raise ValueError(f"LSTM plan contains no candidates for {mode}")
        for candidate in candidates:
            if set(candidate) != required_candidate:
                raise ValueError(f"Malformed LSTM candidate in {mode}")
            identifiers.append(str(candidate["candidate_id"]))
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("LSTM candidate identifiers are not unique")
    return plan


def _config_for_candidate(
    plan: dict[str, Any], mode: InputMode, candidate: dict[str, Any]
) -> LSTMConfig:
    return LSTMConfig(
        input_mode=mode,
        hidden_dim=int(candidate["hidden_dim"]),
        num_layers=int(candidate["num_layers"]),
        dropout=float(candidate["dropout"]),
        epochs=int(plan["common_config"]["epochs"]),
        batch_size=int(plan["common_config"]["batch_size"]),
        learning_rate=float(candidate["learning_rate"]),
        weight_decay=float(plan["common_config"]["weight_decay"]),
        gradient_clip=float(plan["common_config"]["gradient_clip"]),
        early_stopping_patience=int(
            plan["common_config"]["early_stopping_patience"]
        ),
        seed=int(plan["common_config"]["seed"]),
    )


def _validate_candidate_config(
    run_dir: Path,
    expected_config: LSTMConfig,
    plan_sha256: str,
    candidate_id: str,
) -> dict[str, Any]:
    configuration = json.loads(
        (run_dir / "run_configuration.json").read_text(encoding="utf-8")
    )
    if configuration.get("config") != expected_config.__dict__:
        raise ValueError(f"Candidate configuration drifted: {candidate_id}")
    provenance = configuration.get("provenance", {})
    if provenance.get("experiment_plan_sha256") != plan_sha256:
        raise ValueError(f"Candidate used a different experiment plan: {candidate_id}")
    if provenance.get("candidate_id") != candidate_id:
        raise ValueError(f"Candidate ID provenance mismatch: {candidate_id}")
    source_hashes = configuration.get("runtime", {}).get("source_sha256", {})
    if set(source_hashes) != set(LSTM_SOURCE_FILES):
        raise ValueError(f"Candidate source-hash inventory is incomplete: {candidate_id}")
    code_dir = Path(__file__).resolve().parent
    for source_name in LSTM_SOURCE_FILES:
        if source_hashes[source_name] != sha256_file(code_dir / source_name):
            raise ValueError(
                f"Candidate training source changed ({source_name}): {candidate_id}"
            )
    return configuration


def validate_search(
    search_dir: Path,
    sequences: list[ConversationSequence],
    expected_mode: InputMode,
    plan_path: Path = PLAN_PATH,
    device_name: str | None = None,
) -> dict[str, Any]:
    plan = load_experiment_plan(plan_path)
    plan_sha256 = sha256_file(plan_path)
    search_configuration = json.loads(
        (search_dir / "search_configuration.json").read_text(encoding="utf-8")
    )
    search_payload = dict(search_configuration)
    expected_search_hash = search_payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(search_payload) != expected_search_hash:
        raise ValueError("LSTM search configuration failed its canonical hash check")
    expected_candidate_ids = [
        row["candidate_id"] for row in plan["modes"][expected_mode]
    ]
    if (
        search_configuration.get("status") != "LOCKED_SEARCH_CONFIGURATION"
        or search_configuration.get("input_mode") != expected_mode
        or search_configuration.get("experiment_plan_sha256") != plan_sha256
        or search_configuration.get("candidate_ids") != expected_candidate_ids
        or search_configuration.get("final_test_scored") is not False
        or search_configuration.get("historical_test_scored") is not False
    ):
        raise ValueError("LSTM search configuration differs from the locked plan")
    selection_path = search_dir / "selection.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    payload = dict(selection)
    expected_payload_hash = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected_payload_hash:
        raise ValueError("LSTM search selection failed its canonical hash check")
    if selection.get("status") != "ALL_LOCKED_CANDIDATES_COMPLETED":
        raise ValueError("LSTM search did not complete every locked candidate")
    if selection.get("input_mode") != expected_mode:
        raise ValueError("LSTM search input mode is wrong")
    if selection.get("experiment_plan_sha256") != plan_sha256:
        raise ValueError("LSTM search used a different experiment plan")
    candidates = plan["modes"][expected_mode]
    recorded = selection.get("candidate_results", [])
    if [row.get("candidate_id") for row in recorded] != [
        row["candidate_id"] for row in candidates
    ]:
        raise ValueError("LSTM search candidate list/order differs from the locked plan")
    validated_results: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        candidate_id = str(candidate["candidate_id"])
        run_dir = search_dir / "candidates" / candidate_id
        expected_config = _config_for_candidate(plan, expected_mode, candidate)
        _validate_candidate_config(
            run_dir, expected_config, plan_sha256, candidate_id
        )
        validation = validate_lstm_run(
            run_dir, sequences, expected_mode, device_name
        )
        summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
        if recorded[index].get("run_tree_sha256") != tree_sha256(run_dir):
            raise ValueError(f"LSTM candidate tree hash mismatch: {candidate_id}")
        reproduced_metrics = validation["metrics"]
        if not (
            float(recorded[index]["best_validation_pr_auc"])
            == float(reproduced_metrics["pr_auc"])
            and float(recorded[index]["validation_f0_5"])
            == float(reproduced_metrics["f0_5"])
        ):
            raise ValueError(f"LSTM candidate metrics disagree: {candidate_id}")
        validated_results.append(
            {
                "candidate_id": candidate_id,
                "summary": summary,
                "validation": validation,
                "selection_metrics": reproduced_metrics,
                "run_dir": run_dir,
            }
        )
    selected_index = max(
        range(len(validated_results)),
        key=lambda index: (
            float(validated_results[index]["selection_metrics"]["pr_auc"] or 0.0),
            float(validated_results[index]["selection_metrics"]["f0_5"]),
            -index,
        ),
    )
    selected = validated_results[selected_index]
    if selection.get("selected_candidate_id") != selected["candidate_id"]:
        raise ValueError("LSTM search selection is not deterministic")
    expected_relative = (Path("candidates") / selected["candidate_id"]).as_posix()
    if selection.get("selected_run") != expected_relative:
        raise ValueError("LSTM selected-run path is wrong")
    return {
        "status": "validated",
        "input_mode": expected_mode,
        "candidates": len(validated_results),
        "selected_candidate_id": selected["candidate_id"],
        "selected_run": str(selected["run_dir"].resolve()),
        "selection_payload_sha256": selection["canonical_payload_sha256"],
    }


def run_search(
    train_sequences: list[ConversationSequence],
    validation_sequences: list[ConversationSequence],
    output_dir: Path,
    mode: InputMode,
    base_provenance: dict[str, Any],
    plan_path: Path = PLAN_PATH,
    device_name: str | None = None,
) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"LSTM search output is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir = output_dir / "candidates"
    candidates_dir.mkdir()
    plan = load_experiment_plan(plan_path)
    plan_sha256 = sha256_file(plan_path)
    search_configuration = {
        "schema_version": 1,
        "status": "LOCKED_SEARCH_CONFIGURATION",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input_mode": mode,
        "experiment_plan_path": str(plan_path.resolve()),
        "experiment_plan_sha256": plan_sha256,
        "candidate_ids": [row["candidate_id"] for row in plan["modes"][mode]],
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    search_configuration["canonical_payload_sha256"] = canonical_sha256(
        search_configuration
    )
    write_json(output_dir / "search_configuration.json", search_configuration)
    results: list[dict[str, Any]] = []
    for index, candidate in enumerate(plan["modes"][mode]):
        candidate_id = str(candidate["candidate_id"])
        run_dir = candidates_dir / candidate_id
        config = _config_for_candidate(plan, mode, candidate)
        summary = train_lstm(
            train_sequences,
            validation_sequences,
            run_dir,
            config,
            provenance={
                **base_provenance,
                "experiment_plan_sha256": plan_sha256,
                "candidate_id": candidate_id,
                "candidate_order": index,
            },
            device_name=device_name,
        )
        results.append(
            {
                "candidate_id": candidate_id,
                "best_validation_pr_auc": summary["best_validation_pr_auc"],
                "validation_f0_5": summary[
                    "validation_metrics_at_selected_threshold"
                ]["f0_5"],
                "run_tree_sha256": tree_sha256(run_dir),
            }
        )
    selected_index = max(
        range(len(results)),
        key=lambda index: (
            float(results[index]["best_validation_pr_auc"] or 0.0),
            float(results[index]["validation_f0_5"]),
            -index,
        ),
    )
    selected_id = results[selected_index]["candidate_id"]
    selection = {
        "schema_version": 1,
        "status": "ALL_LOCKED_CANDIDATES_COMPLETED",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "input_mode": mode,
        "experiment_plan_sha256": plan_sha256,
        "selection_rule": (
            "maximum validation average precision; then validation F0.5; "
            "then earliest candidate order"
        ),
        "candidate_results": results,
        "selected_candidate_id": selected_id,
        "selected_run": (Path("candidates") / selected_id).as_posix(),
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    selection["canonical_payload_sha256"] = canonical_sha256(selection)
    write_json(output_dir / "selection.json", selection)
    return selection


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-cache", type=Path, required=True)
    parser.add_argument("--validation-cache", type=Path, required=True)
    parser.add_argument("--centroid-dir", type=Path, required=True)
    parser.add_argument("--feature-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--input-mode", choices=["trajectory7", "enhanced775"], required=True
    )
    parser.add_argument("--plan", type=Path, default=PLAN_PATH)
    parser.add_argument("--device")
    args = parser.parse_args()
    feature_config = json.loads(args.feature_config.read_text(encoding="utf-8"))
    train_sequences, train_metadata = load_conversation_sequences(
        args.train_cache,
        args.centroid_dir,
        "train",
        float(feature_config["spike_threshold"]),
        float(feature_config["drop_threshold"]),
    )
    validation_sequences, validation_metadata = load_conversation_sequences(
        args.validation_cache,
        args.centroid_dir,
        "validation",
        float(feature_config["spike_threshold"]),
        float(feature_config["drop_threshold"]),
    )
    result = run_search(
        train_sequences,
        validation_sequences,
        args.output_dir,
        args.input_mode,
        {
            "feature_config_sha256": sha256_file(args.feature_config),
            "train_cache_manifest_payload_sha256": train_metadata[
                "cache_manifest"
            ]["canonical_payload_sha256"],
            "validation_cache_manifest_payload_sha256": validation_metadata[
                "cache_manifest"
            ]["canonical_payload_sha256"],
            "centroid_manifest_payload_sha256": train_metadata[
                "centroid_manifest"
            ]["canonical_payload_sha256"],
        },
        args.plan,
        args.device,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
