import argparse
import json
from pathlib import Path

import pandas as pd

from audit_layer1_dataset import build_manifest, sha256_file


GENERATOR = '''
MODEL_NAME = "local-test-model"
NUM_EXAMPLES_PER_TACTIC = 1
tactics = [{"name": "Test", "prompt": "Generate a test"}]
'''


def write_csv(path: Path, rows: list[dict]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def test_manifest_blocks_role_and_diff_derived_labels(tmp_path):
    grooming = tmp_path / "grooming.csv"
    safe = tmp_path / "safe.csv"
    active_pan = tmp_path / "active_pan.csv"
    archived_pan = tmp_path / "archived_pan.csv"
    grooming_generator = tmp_path / "grooming_generator.py"
    safe_generator = tmp_path / "safe_generator.py"
    preprocessor = tmp_path / "Python.py"
    readme = tmp_path / "readme.txt"
    split_audit = tmp_path / "split.json"

    common = {
        "line": 1,
        "image_type": "none",
    }
    write_csv(
        grooming,
        [
            {**common, "convo_id": "g1", "author": "Predator_Sim", "text": "hello", "is_predator": 1, "is_suspicious": 1},
            {**common, "convo_id": "g2", "author": "Minor_Sim", "text": "hi", "is_predator": 0, "is_suspicious": 0},
        ],
    )
    write_csv(
        safe,
        [{**common, "convo_id": "s1", "author": "User_A_Sim", "text": "game?", "is_predator": 0, "is_suspicious": 0}],
    )
    pan_rows = [
        {"conv_id": "c1", "line": 1, "author": "a", "text": "x", "is_predator": 1, "is_suspicious": 0},
        {"conv_id": "c2", "line": 1, "author": "b", "text": "y", "is_predator": 0, "is_suspicious": 1},
    ]
    write_csv(active_pan, pan_rows)
    write_csv(archived_pan, pan_rows)
    grooming_generator.write_text(GENERATOR, encoding="utf-8")
    safe_generator.write_text(
        GENERATOR.replace("NUM_EXAMPLES_PER_TACTIC", "NUM_EXAMPLES_PER_SCENARIO").replace("tactics", "scenarios"),
        encoding="utf-8",
    )
    preprocessor.write_text("is_suspicious = key in diff_entries\n", encoding="utf-8")
    readme.write_text("diff contains modified text locations\n", encoding="utf-8")
    split_audit.write_text(
        json.dumps(
            {
                "protocol": {"name": "test"},
                "invariants": {"author_overlap_is_zero": True},
                "assignments": {
                    "pan12:c1": {"split": "train"},
                    "pan12:c2": {"split": "test"},
                },
            }
        ),
        encoding="utf-8",
    )

    args = argparse.Namespace(
        workspace=tmp_path,
        synthetic_grooming=grooming,
        synthetic_safe=safe,
        grooming_generator=grooming_generator,
        safe_generator=safe_generator,
        pan_active=active_pan,
        pan_archive=archived_pan,
        pan_preprocessor=preprocessor,
        pan_readme=readme,
        split_audit=split_audit,
        worksheet=tmp_path / "worksheet.csv",
    )
    manifest, worksheet = build_manifest(args)

    assert manifest["training_gate"]["status"] == "BLOCKED_NO_INDEPENDENTLY_ANNOTATED_MESSAGE_ROWS"
    assert manifest["training_gate"]["approved_training_rows"] == 0
    assert manifest["sources"]["synthetic_grooming"]["decision"].startswith("EXCLUDE")
    assert manifest["sources"]["synthetic_grooming"]["diagnostics"]["suspicious_equals_predator_for_every_row"]
    assert manifest["sources"]["pan12"]["decision_for_message_level_layer1"] == "EXCLUDE"
    assert manifest["sources"]["pan12"]["frozen_split"]["source_rows_by_assignment"] == {
        "train": 1,
        "validation": 0,
        "test": 1,
        "unassigned_non_dyadic_or_filtered": 0,
    }
    assert len(worksheet) == 3
    assert manifest["annotation_worksheet"]["rows"] == 3
    assert len(manifest["annotation_worksheet"]["sha256"]) == 64
    assert worksheet["reviewer_1_label"].eq("").all()
    assert worksheet["reviewer_2_label"].eq("").all()
    assert worksheet["adjudicated_message_label"].eq("").all()
    assert worksheet["row_id"].is_unique


def test_file_hash_is_stable(tmp_path):
    path = tmp_path / "evidence.txt"
    path.write_bytes(b"evidence\n")
    assert sha256_file(path) == "BDCF4C994585AF6DD6CB1CFBFF78BCC73AB27DC30A299DB5BB83766CA05B5DE4"
