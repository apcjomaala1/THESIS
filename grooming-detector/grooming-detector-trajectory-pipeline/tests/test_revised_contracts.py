import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from revised_pipeline.contracts import (
    EXPECTED_LAYER1_ARGUMENTS,
    EXPECTED_LAYER1_GUARDS,
    canonical_sha256,
    sha256_file,
    tree_sha256,
    validate_layer1_run,
)
from revised_pipeline.data import attach_locked_splits, build_context_records, load_eligible_rows
from revised_pipeline.metrics import select_f05_threshold


def _statistics(frame, ids):
    selected = frame[frame["conversation_id"].isin(ids)]
    labels = selected.groupby("conversation_id")["author_is_predator"].max()
    return {
        "conversations": len(ids),
        "rows": len(selected),
        "positive_conversations": int(labels.sum()),
        "negative_conversations": int(len(labels) - labels.sum()),
        "positive_author_rows": int(selected["author_is_predator"].sum()),
        "negative_author_rows": int(len(selected) - selected["author_is_predator"].sum()),
        "authors": int(selected["author_id"].nunique()),
        "components": len(ids),
        "conversation_ids": sorted(ids),
    }


def _build_fake_run(tmp_path):
    source = tmp_path / "pan12_final_dataset.csv"
    raw_rows = []
    specifications = [
        ("tneg", "train", 0),
        ("tpos", "train", 1),
        ("vneg", "validation", 0),
        ("vpos", "validation", 1),
        ("fpos", "final_test", 1),
        ("xneg", "excluded_historical_test", 0),
    ]
    split_ids = {name: set() for name in ["train", "validation", "final_test", "excluded_historical_test"]}
    for conversation, split, positive in specifications:
        split_ids[split].add(f"pan12:{conversation}")
        raw_rows.extend(
            [
                {
                    "conv_id": conversation,
                    "line": 1,
                    "author": f"{conversation}-a",
                    "text": f"first {conversation}",
                    "is_predator": positive,
                    "is_suspicious": "ignored",
                },
                {
                    "conv_id": conversation,
                    "line": 2,
                    "author": f"{conversation}-b",
                    "text": f"second {conversation}",
                    "is_predator": 0,
                    "is_suspicious": 99,
                },
            ]
        )
    pd.DataFrame(raw_rows).to_csv(source, index=False)
    eligible = load_eligible_rows(source)
    manifest = {
        "schema_version": 1,
        "dataset": {
            "sha256": sha256_file(source),
            "bytes": source.stat().st_size,
        },
        "historical_audit": {"sha256": "audit-hash"},
        "splits": {
            name: _statistics(eligible, ids) for name, ids in split_ids.items()
        },
        "invariants": {
            "all_eligible_conversations_assigned_once": True,
            "conversation_overlap_is_zero": True,
            "author_overlap_is_zero": True,
            "component_overlap_is_zero": True,
            "historical_test_is_excluded": True,
            "final_test_originates_only_from_historical_train": True,
        },
    }
    manifest["integrity"] = {"canonical_payload_sha256": canonical_sha256(manifest)}
    split_path = tmp_path / "locked_split_manifest.json"
    split_path.write_text(json.dumps(manifest), encoding="utf-8")

    trainer_hash = "trainer-script-hash"
    package = {
        "version": "1.0.0",
        "files": [
            {"path": "train_layer1_author_proxy.py", "sha256": trainer_hash}
        ],
    }
    package_path = tmp_path / "package_manifest.json"
    package_path.write_text(json.dumps(package), encoding="utf-8")

    assigned = attach_locked_splits(eligible, manifest)
    validation = build_context_records(
        assigned[assigned["split"] == "validation"]
    )
    probabilities = np.where(validation["author_label"].to_numpy() == 1, 0.9, 0.1)
    labels = validation["author_label"].to_numpy(dtype=np.int8)
    threshold, metrics = select_f05_threshold(labels, probabilities)
    run = tmp_path / "run"
    model = run / "best_model"
    model.mkdir(parents=True)
    (model / "config.json").write_text(
        json.dumps(
            {
                "num_labels": 2,
                "id2label": {
                    "0": "NOT_LISTED_PREDATOR_AUTHOR",
                    "1": "LISTED_PREDATOR_AUTHOR",
                },
                "label2id": {
                    "NOT_LISTED_PREDATOR_AUTHOR": 0,
                    "LISTED_PREDATOR_AUTHOR": 1,
                },
            }
        ),
        encoding="utf-8",
    )
    (model / "model.safetensors").write_bytes(b"fake-model-weights")
    arguments = copy.deepcopy(EXPECTED_LAYER1_ARGUMENTS)
    arguments["train_batch_size"] = 64
    arguments["eval_batch_size"] = 128
    configuration = {
        "package_version": "1.0.0",
        "arguments": arguments,
        "data_sha256": manifest["dataset"]["sha256"],
        "split_manifest_payload_sha256": manifest["integrity"]["canonical_payload_sha256"],
        "script_sha256": trainer_hash,
        "methodology_guards": copy.deepcopy(EXPECTED_LAYER1_GUARDS),
        "row_counts": {
            "train_before_negative_sampling": 4,
            "train_after_negative_sampling": 4,
            "train_positive": 1,
            "train_negative": 3,
            "validation": 4,
            "validation_positive": 1,
            "validation_negative": 3,
        },
    }
    (run / "run_configuration.json").write_text(json.dumps(configuration), encoding="utf-8")
    trainer_state = run / "checkpoints" / "checkpoint-1" / "trainer_state.json"
    trainer_state.parent.mkdir(parents=True)
    trainer_state.write_text(json.dumps({"train_batch_size": 64}), encoding="utf-8")
    predictions = validation[["row_id", "conversation_id", "line", "author_label"]].rename(
        columns={"author_label": "label"}
    )
    predictions["probability"] = probabilities
    predictions["prediction"] = (probabilities >= threshold).astype(np.int8)
    predictions.to_csv(run / "validation_predictions.csv", index=False)
    (run / "selected_threshold.json").write_text(
        json.dumps(
            {
                "selection_partition": "validation",
                "objective": "maximum F0.5",
                "threshold": threshold,
                "metrics": metrics,
            }
        ),
        encoding="utf-8",
    )
    summary = {
        "status": "completed",
        "selected_threshold": threshold,
        "best_model_tree_sha256": tree_sha256(model),
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    (run / "run_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return run, split_path, package_path, source


def test_returned_layer1_contract_accepts_exact_locked_run(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    receipt = validate_layer1_run(run, split_path, package_path, source)
    assert receipt["status"] == "accepted_for_revised_downstream_preparation"
    assert receipt["validation_rows"] == 4
    assert receipt["effective_train_batch_size"] == 64
    assert receipt["final_test_scored"] is False


def test_returned_layer1_contract_accepts_documented_larger_requested_batch(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    config_path = run / "run_configuration.json"
    configuration = json.loads(config_path.read_text())
    configuration["arguments"]["train_batch_size"] = 128
    configuration["arguments"]["eval_batch_size"] = 256
    config_path.write_text(json.dumps(configuration))
    state_path = run / "checkpoints" / "checkpoint-1" / "trainer_state.json"
    state_path.write_text(json.dumps({"train_batch_size": 64}))
    receipt = validate_layer1_run(run, split_path, package_path, source)
    assert receipt["requested_train_batch_size"] == 128
    assert receipt["effective_train_batch_size"] == 64


def test_returned_layer1_contract_accepts_consumer_gpu_requested_batch(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    config_path = run / "run_configuration.json"
    configuration = json.loads(config_path.read_text())
    configuration["arguments"]["train_batch_size"] = 8
    configuration["arguments"]["eval_batch_size"] = 16
    config_path.write_text(json.dumps(configuration))
    state_path = run / "checkpoints" / "checkpoint-1" / "trainer_state.json"
    state_path.write_text(json.dumps({"train_batch_size": 8}))
    receipt = validate_layer1_run(run, split_path, package_path, source)
    assert receipt["requested_train_batch_size"] == 8
    assert receipt["effective_train_batch_size"] == 8


def test_returned_layer1_contract_rejects_model_tree_tamper(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    (run / "best_model" / "model.safetensors").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="best_model tree"):
        validate_layer1_run(run, split_path, package_path, source)


def test_returned_layer1_contract_rejects_wrong_stable_row(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    predictions = pd.read_csv(run / "validation_predictions.csv")
    predictions.loc[0, "row_id"] = "pan12:vneg:999"
    predictions.to_csv(run / "validation_predictions.csv", index=False)
    with pytest.raises(ValueError, match="row IDs or labels"):
        validate_layer1_run(run, split_path, package_path, source)


def test_returned_layer1_contract_rejects_test_scoring_flag(tmp_path):
    run, split_path, package_path, source = _build_fake_run(tmp_path)
    summary_path = run / "run_summary.json"
    summary = json.loads(summary_path.read_text())
    summary["final_test_scored"] = True
    summary_path.write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="final test was scored"):
        validate_layer1_run(run, split_path, package_path, source)
