import json
from pathlib import Path

import pytest

from revised_pipeline.cache import _resolve_requested_splits
from revised_pipeline.contracts import canonical_sha256, sha256_file
from revised_pipeline.final_gate import (
    ARM_ACKNOWLEDGEMENT,
    arm_gate,
    consume_claim,
    validate_claim,
)
from revised_pipeline.evaluate_final import run_final_evaluation


def _split_manifest():
    return {
        "dataset": {"sha256": "data-hash"},
        "integrity": {"canonical_payload_sha256": "split-hash"},
    }


def _write_frozen(path: Path):
    record = {
        "schema_version": 1,
        "status": "FROZEN_READY_FOR_ONE_FINAL_EVALUATION",
        "dataset_sha256": "data-hash",
        "split_manifest_payload_sha256": "split-hash",
        "gate_registry_path": str(path.parent / "fixed-gate-registry"),
    }
    record["canonical_payload_sha256"] = canonical_sha256(record)
    path.write_text(json.dumps(record), encoding="utf-8")
    return record


def test_development_splits_reject_both_test_partitions():
    requested, claim = _resolve_requested_splits(
        ["train", "validation"], None, _split_manifest()
    )
    assert requested == ["train", "validation"]
    assert claim is None
    with pytest.raises(ValueError, match="permanently excluded"):
        _resolve_requested_splits(["excluded_historical_test"], None, _split_manifest())
    with pytest.raises(PermissionError, match="Locked final test denied"):
        _resolve_requested_splits(["final_test"], None, _split_manifest())


def test_final_claim_is_consumed_atomically_and_never_reusable(tmp_path):
    frozen_path = tmp_path / "frozen_protocol.json"
    frozen = _write_frozen(frozen_path)
    claim = arm_gate(
        frozen_path,
        frozen["canonical_payload_sha256"],
        ARM_ACKNOWLEDGEMENT,
    )
    claim_path = Path(claim["canonical_claim_path"])
    validate_claim(claim_path, _split_manifest())
    receipt = consume_claim(claim_path, _split_manifest())
    assert receipt["status"] == "CONSUMED_BEFORE_FINAL_ROWS_SCORED_OR_CACHED"
    assert (Path(claim["gate_registry_path"]) / "consumed.json").exists()
    with pytest.raises(PermissionError, match="already been consumed"):
        validate_claim(claim_path, _split_manifest())
    with pytest.raises(PermissionError, match="already been consumed"):
        consume_claim(claim_path, _split_manifest())


def test_arm_requires_explicit_phrase_and_exact_hash(tmp_path):
    frozen_path = tmp_path / "frozen_protocol.json"
    frozen = _write_frozen(frozen_path)
    with pytest.raises(PermissionError):
        arm_gate(frozen_path, "wrong", "wrong phrase")
    with pytest.raises(ValueError, match="hash"):
        arm_gate(
            frozen_path,
            "wrong",
            ARM_ACKNOWLEDGEMENT,
        )


def test_same_frozen_protocol_cannot_be_armed_twice_or_via_copied_claim(tmp_path):
    frozen_path = tmp_path / "frozen_protocol.json"
    frozen = _write_frozen(frozen_path)
    claim = arm_gate(
        frozen_path,
        frozen["canonical_payload_sha256"],
        ARM_ACKNOWLEDGEMENT,
    )
    with pytest.raises(FileExistsError, match="already been armed"):
        arm_gate(
            frozen_path,
            frozen["canonical_payload_sha256"],
            ARM_ACKNOWLEDGEMENT,
        )
    copied = tmp_path / "copied_claim.json"
    copied.write_text(Path(claim["canonical_claim_path"]).read_text())
    with pytest.raises(PermissionError, match="Copied or renamed"):
        validate_claim(copied, _split_manifest())


def test_final_wrapper_rejects_claim_for_another_protocol_before_consumption(tmp_path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    first_path = first_dir / "frozen.json"
    second_path = second_dir / "frozen.json"
    first = _write_frozen(first_path)
    _write_frozen(second_path)
    claim = arm_gate(
        first_path,
        first["canonical_payload_sha256"],
        ARM_ACKNOWLEDGEMENT,
    )
    claim_path = Path(claim["canonical_claim_path"])
    with pytest.raises(ValueError, match="different frozen protocol"):
        run_final_evaluation(
            second_path,
            claim_path,
            tmp_path / "final_cache",
            tmp_path / "final_output",
        )
    assert not (Path(claim["gate_registry_path"]) / "consumed.json").exists()


def test_nonempty_final_output_is_rejected_without_consuming_claim(tmp_path):
    frozen_path = tmp_path / "frozen.json"
    frozen = _write_frozen(frozen_path)
    claim = arm_gate(
        frozen_path,
        frozen["canonical_payload_sha256"],
        ARM_ACKNOWLEDGEMENT,
    )
    output_dir = tmp_path / "already_used"
    output_dir.mkdir()
    (output_dir / "keep.txt").write_text("existing", encoding="utf-8")
    with pytest.raises(FileExistsError, match="not empty"):
        run_final_evaluation(
            frozen_path,
            Path(claim["canonical_claim_path"]),
            tmp_path / "final_cache",
            output_dir,
        )
    assert not (Path(claim["gate_registry_path"]) / "consumed.json").exists()


def test_invalid_final_cache_batch_is_rejected_without_consuming_claim(tmp_path):
    frozen_path = tmp_path / "frozen.json"
    frozen = _write_frozen(frozen_path)
    claim = arm_gate(
        frozen_path,
        frozen["canonical_payload_sha256"],
        ARM_ACKNOWLEDGEMENT,
    )
    with pytest.raises(ValueError, match="positive integer"):
        run_final_evaluation(
            frozen_path,
            Path(claim["canonical_claim_path"]),
            tmp_path / "final_cache",
            tmp_path / "final_output",
            cache_batch_size=0,
        )
    assert not (Path(claim["gate_registry_path"]) / "consumed.json").exists()
