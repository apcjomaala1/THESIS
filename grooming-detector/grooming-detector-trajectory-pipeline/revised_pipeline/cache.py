"""Generate stable-ID Layer 1 score and base-embedding caches.

Development runs may cache only ``train`` and ``validation``.  Requesting the
locked final test requires a valid, one-time claim produced by
``revised_pipeline.final_gate`` after every downstream choice is frozen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .contracts import (
    canonical_sha256,
    load_locked_manifest,
    sha256_file,
    validate_layer1_run,
    write_json,
)
from .data import (
    ALLOWED_DEVELOPMENT_SPLITS,
    CONTEXT_TURNS,
    attach_locked_splits,
    build_context_records,
    load_eligible_rows,
    select_splits,
)


CACHE_SCHEMA_VERSION = 1
INDEX_COLUMNS = [
    "row_id",
    "conversation_id",
    "line",
    "component_id",
    "speaker_index",
    "author_label",
    "conversation_label",
    "context_sha256",
    "current_text_sha256",
]


def torch_state_sha256(model: Any) -> str:
    """Hash a loaded torch model independent of its local cache path."""
    digest = hashlib.sha256()
    for name, tensor in sorted(model.state_dict().items()):
        cpu = tensor.detach().cpu().contiguous()
        metadata = json.dumps(
            {"name": name, "dtype": str(cpu.dtype), "shape": list(cpu.shape)},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        digest.update(len(metadata).to_bytes(8, "big"))
        digest.update(metadata)
        digest.update(cpu.numpy().tobytes(order="C"))
    return digest.hexdigest()


def tokenizer_fingerprints(tokenizer: Any) -> dict[str, str]:
    backend = tokenizer.backend_tokenizer.to_str().encode("utf-8")
    return {
        "backend_sha256": hashlib.sha256(backend).hexdigest(),
        "vocabulary_sha256": canonical_sha256(tokenizer.get_vocab()),
        "special_tokens_sha256": canonical_sha256(tokenizer.special_tokens_map),
    }


def _resolve_requested_splits(
    splits: Iterable[str],
    final_test_claim: Path | None,
    split_manifest: dict[str, Any],
) -> tuple[list[str], dict[str, Any] | None]:
    requested = list(dict.fromkeys(str(split) for split in splits))
    if not requested:
        raise ValueError("At least one split is required")
    if "excluded_historical_test" in requested:
        raise ValueError("The inspected historical test is permanently excluded")
    unknown = set(requested) - {"train", "validation", "final_test"}
    if unknown:
        raise ValueError(f"Unknown cache split(s): {sorted(unknown)}")
    claim = None
    if "final_test" in requested:
        if set(requested) != {"final_test"}:
            raise ValueError("Final-test caching must be an isolated operation")
        if final_test_claim is None:
            raise PermissionError(
                "Locked final test denied. Freeze the complete protocol and create "
                "a one-time claim with revised_pipeline.final_gate first."
            )
        from .final_gate import validate_claim

        # Validate here; consumption is delayed until output/model/runtime
        # preflight has succeeded and immediately before any final score is
        # written. A later scoring failure deliberately remains consumed.
        claim = validate_claim(final_test_claim, split_manifest)
    elif final_test_claim is not None:
        raise ValueError("A final-test claim is valid only for the final_test split")
    elif not set(requested).issubset(ALLOWED_DEVELOPMENT_SPLITS):
        raise PermissionError("Only train and validation are available during development")
    return requested, claim


def _ensure_empty_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Cache output directory is not empty: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _score_and_embed(
    records: pd.DataFrame,
    classifier: Any,
    classifier_tokenizer: Any,
    base_encoder: Any,
    base_tokenizer: Any,
    device: Any,
    batch_size: int,
    score_path: Path,
    embedding_path: Path,
) -> None:
    import torch

    n_rows = len(records)
    scores = np.lib.format.open_memmap(
        score_path, mode="w+", dtype=np.float32, shape=(n_rows,)
    )
    embeddings = np.lib.format.open_memmap(
        embedding_path, mode="w+", dtype=np.float32, shape=(n_rows, 768)
    )
    classifier.eval()
    base_encoder.eval()
    with torch.inference_mode():
        for start in range(0, n_rows, batch_size):
            stop = min(start + batch_size, n_rows)
            contexts = records.iloc[start:stop]["context_text"].tolist()
            current = records.iloc[start:stop]["current_text"].tolist()
            encoded_context = classifier_tokenizer(
                contexts,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt",
            )
            encoded_context = {key: value.to(device) for key, value in encoded_context.items()}
            encoded_context.pop("token_type_ids", None)
            logits = classifier(**encoded_context).logits
            batch_scores = torch.softmax(logits.float(), dim=-1)[:, 1]

            encoded_current = base_tokenizer(
                current,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt",
            )
            encoded_current = {key: value.to(device) for key, value in encoded_current.items()}
            encoded_current.pop("token_type_ids", None)
            batch_embeddings = base_encoder(**encoded_current).last_hidden_state[:, 0, :]
            scores[start:stop] = batch_scores.cpu().numpy().astype(np.float32)
            embeddings[start:stop] = batch_embeddings.float().cpu().numpy().astype(np.float32)
            if stop == n_rows or stop % max(batch_size * 100, batch_size) == 0:
                print(f"  encoded {stop:,}/{n_rows:,} rows")
    scores.flush()
    embeddings.flush()
    del scores
    del embeddings


def _write_partition_cache(
    records: pd.DataFrame,
    split_name: str,
    output_dir: Path,
    classifier: Any,
    classifier_tokenizer: Any,
    base_encoder: Any,
    base_tokenizer: Any,
    device: Any,
    batch_size: int,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    partition_dir = output_dir / split_name
    partition_dir.mkdir(parents=True, exist_ok=False)
    selected = records[records["split"] == split_name].reset_index(drop=True)
    if selected.empty:
        raise ValueError(f"No records for locked split {split_name}")
    index_path = partition_dir / "index.csv"
    score_path = partition_dir / "layer1_scores.npy"
    embedding_path = partition_dir / "base_embeddings.npy"
    selected[INDEX_COLUMNS].to_csv(index_path, index=False)
    _score_and_embed(
        selected,
        classifier,
        classifier_tokenizer,
        base_encoder,
        base_tokenizer,
        device,
        batch_size,
        score_path,
        embedding_path,
    )
    record = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "status": "complete",
        "split": split_name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "rows": len(selected),
        "conversations": int(selected["conversation_id"].nunique()),
        "positive_conversations": int(
            selected.groupby("conversation_id")["conversation_label"].first().sum()
        ),
        "positive_author_rows": int(selected["author_label"].sum()),
        "stable_key": "pan12:<conversation_id>:<line>",
        "raw_message_text_persisted": False,
        "raw_author_id_persisted": False,
        "speaker_identity": "within-conversation first-seen index 0 or 1",
        "layer1_input": "current turn plus up to two preceding turns joined by [SEP]",
        "base_embedding_input": "current turn only",
        "normalization": "strip current text; literal separator ' [SEP] '",
        "context_turns": CONTEXT_TURNS,
        "max_length": 128,
        "score_dtype": "float32",
        "embedding_dtype": "float32",
        "embedding_shape": [len(selected), 768],
        "row_id_sequence_sha256": canonical_sha256(selected["row_id"].tolist()),
        "provenance": provenance,
        "files": {
            "index.csv": sha256_file(index_path),
            "layer1_scores.npy": sha256_file(score_path),
            "base_embeddings.npy": sha256_file(embedding_path),
        },
    }
    record["canonical_payload_sha256"] = canonical_sha256(record)
    write_json(partition_dir / "manifest.json", record)
    return record


def build_cache(
    data_file: Path,
    split_manifest_path: Path,
    component_audit_path: Path,
    package_manifest_path: Path,
    layer1_run: Path,
    output_dir: Path,
    splits: Iterable[str] = ("train", "validation"),
    batch_size: int = 128,
    device_name: str | None = None,
    base_model_name: str = "distilbert-base-uncased",
    local_files_only: bool = True,
    final_test_claim: Path | None = None,
) -> dict[str, Any]:
    if int(batch_size) <= 0:
        raise ValueError("Cache batch_size must be a positive integer")
    data_file = data_file.resolve()
    split_manifest_path = split_manifest_path.resolve()
    manifest = load_locked_manifest(split_manifest_path, data_file)
    _ensure_empty_output(output_dir)
    requested, claim = _resolve_requested_splits(splits, final_test_claim, manifest)
    import torch
    import transformers
    from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

    expected_development_provenance = None
    if "final_test" in requested:
        from .final_gate import validate_final_cache_request

        _frozen_final, expected_development_provenance = validate_final_cache_request(
            final_test_claim,
            manifest,
            {
                "data_file": data_file,
                "split_manifest": split_manifest_path,
                "component_audit": component_audit_path,
                "package_manifest": package_manifest_path,
                "layer1_run": layer1_run,
            },
            torch_version=str(torch.__version__),
            transformers_version=str(transformers.__version__),
            base_model_name=base_model_name,
        )
    try:
        layer1_receipt = validate_layer1_run(
            layer1_run,
            split_manifest_path,
            package_manifest_path,
            data_file,
        )
        frame = attach_locked_splits(load_eligible_rows(data_file), manifest)
        records = build_context_records(select_splits(frame, requested))
        component_audit_path = component_audit_path.resolve()
        if sha256_file(component_audit_path) != manifest["historical_audit"]["sha256"]:
            raise ValueError("Connected-component audit does not match the locked manifest")
        component_audit = json.loads(component_audit_path.read_text(encoding="utf-8"))
        component_by_conversation = {
            conversation_id: row["component_id"]
            for conversation_id, row in component_audit["assignments"].items()
        }
        records["component_id"] = records["conversation_id"].map(
            component_by_conversation
        )
        if records["component_id"].isna().any():
            raise ValueError("At least one cache row lacks a connected-component ID")
        observed_component_counts = records.groupby("split")["component_id"].nunique()
        for split_name in requested:
            expected_components = int(manifest["splits"][split_name]["components"])
            if int(observed_component_counts[split_name]) != expected_components:
                raise ValueError(f"Connected-component count mismatch for {split_name}")
        device = torch.device(
            device_name or ("cuda" if torch.cuda.is_available() else "cpu")
        )
        if device.type == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        model_dir = layer1_run.resolve() / "best_model"
        classifier_tokenizer = AutoTokenizer.from_pretrained(
            model_dir, local_files_only=True, use_fast=True
        )
        classifier = AutoModelForSequenceClassification.from_pretrained(
            model_dir, local_files_only=True
        ).to(device)
        base_tokenizer = AutoTokenizer.from_pretrained(
            base_model_name,
            local_files_only=local_files_only,
            use_fast=True,
        )
        base_encoder = AutoModel.from_pretrained(
            base_model_name,
            local_files_only=local_files_only,
        ).to(device)
        if int(getattr(base_encoder.config, "hidden_size", -1)) != 768:
            raise ValueError("Revised enhanced input requires a 768-dimensional base encoder")
        base_digest = torch_state_sha256(base_encoder)
        base_tokenizer_digests = tokenizer_fingerprints(base_tokenizer)
        if expected_development_provenance is not None:
            actual_base_fields = {
                "base_encoder_name": base_model_name,
                "base_encoder_state_sha256": base_digest,
                "base_encoder_config_sha256": canonical_sha256(
                    base_encoder.config.to_dict()
                ),
                "base_tokenizer": base_tokenizer_digests,
                "torch_version": str(torch.__version__),
                "transformers_version": str(transformers.__version__),
                "device": str(device),
            }
            for field, actual_value in actual_base_fields.items():
                if expected_development_provenance.get(field) != actual_value:
                    raise ValueError(
                        f"Final cache runtime/base-model mismatch before gate consumption: {field}"
                    )
            from .final_gate import consume_claim

            # All recoverable preflight checks are complete. Consume directly
            # before final model outputs can be persisted.
            claim = consume_claim(final_test_claim, manifest)
        provenance = {
            "data_sha256": manifest["dataset"]["sha256"],
            "split_manifest_payload_sha256": manifest["integrity"][
                "canonical_payload_sha256"
            ],
            "component_audit_sha256": sha256_file(component_audit_path),
            "layer1_model_tree_sha256": layer1_receipt["best_model_tree_sha256"],
            "layer1_row_threshold": layer1_receipt["selected_row_threshold"],
            "layer1_run_artifact_sha256": layer1_receipt["artifact_sha256"],
            "base_encoder_name": base_model_name,
            "base_encoder_state_sha256": base_digest,
            "base_encoder_config_sha256": canonical_sha256(
                base_encoder.config.to_dict()
            ),
            "base_tokenizer": base_tokenizer_digests,
            "torch_version": str(torch.__version__),
            "transformers_version": str(transformers.__version__),
            "device": str(device),
            "final_test_claim": claim,
        }
        partition_records = {
            split_name: _write_partition_cache(
                records,
                split_name,
                output_dir,
                classifier,
                classifier_tokenizer,
                base_encoder,
                base_tokenizer,
                device,
                batch_size,
                provenance,
            )
            for split_name in requested
        }
        validation_regeneration_check = None
        if "validation" in requested:
            validation_dir = output_dir / "validation"
            regenerated_index = pd.read_csv(validation_dir / "index.csv")
            regenerated_scores = np.load(
                validation_dir / "layer1_scores.npy", mmap_mode="r"
            )
            returned = pd.read_csv(layer1_run / "validation_predictions.csv")
            returned = returned.set_index("row_id").loc[
                regenerated_index["row_id"].tolist()
            ]
            mixed_precision_scores = returned["probability"].to_numpy(dtype=np.float64)
            fp32_scores = np.asarray(regenerated_scores, dtype=np.float64)
            if np.std(mixed_precision_scores) == 0 or np.std(fp32_scores) == 0:
                correlation = 1.0 if np.allclose(mixed_precision_scores, fp32_scores) else 0.0
            else:
                correlation = float(np.corrcoef(mixed_precision_scores, fp32_scores)[0, 1])
            max_absolute_difference = float(
                np.max(np.abs(mixed_precision_scores - fp32_scores))
            )
            if not np.isfinite(correlation) or correlation < 0.995:
                raise ValueError(
                    "Regenerated FP32 validation scores do not correspond to the "
                    "returned Layer 1 validation predictions"
                )
            validation_regeneration_check = {
                "comparison": "returned mixed-precision Trainer predictions vs regenerated FP32 cache",
                "rows": len(fp32_scores),
                "pearson_correlation": correlation,
                "max_absolute_difference": max_absolute_difference,
                "acceptance": "correlation >= 0.995; values are not required to be bitwise equal",
            }
        root_record = {
            "schema_version": CACHE_SCHEMA_VERSION,
            "status": "complete",
            "splits": requested,
            "development_only": "final_test" not in requested,
            "final_test_scored": "final_test" in requested,
            "historical_test_scored": False,
            "partition_manifest_payload_sha256": {
                name: record["canonical_payload_sha256"]
                for name, record in partition_records.items()
            },
            "validation_regeneration_check": validation_regeneration_check,
            "provenance": provenance,
        }
        root_record["canonical_payload_sha256"] = canonical_sha256(root_record)
        write_json(output_dir / "cache_manifest.json", root_record)
        return root_record
    except Exception:
        # A partial cache must never be mistaken for a complete cache.
        if output_dir.exists():
            (output_dir / "INCOMPLETE.txt").write_text(
                "Cache generation failed. Do not use this directory.\n",
                encoding="utf-8",
            )
        raise


def load_partition_cache(
    partition_dir: Path,
    expected_split: str | None = None,
    verify_hashes: bool = True,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray, dict[str, Any]]:
    partition_dir = partition_dir.resolve()
    manifest_path = partition_dir / "manifest.json"
    record = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload = dict(record)
    expected_payload_hash = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected_payload_hash:
        raise ValueError(f"Cache manifest integrity failed: {manifest_path}")
    if record.get("status") != "complete":
        raise ValueError("Cache partition is not complete")
    if expected_split is not None and record.get("split") != expected_split:
        raise ValueError(
            f"Expected {expected_split} cache, got {record.get('split')}"
        )
    paths = {
        "index.csv": partition_dir / "index.csv",
        "layer1_scores.npy": partition_dir / "layer1_scores.npy",
        "base_embeddings.npy": partition_dir / "base_embeddings.npy",
    }
    if verify_hashes:
        for name, path in paths.items():
            if sha256_file(path) != record["files"][name]:
                raise ValueError(f"Cache file hash mismatch: {path}")
    index = pd.read_csv(paths["index.csv"])
    scores = np.load(paths["layer1_scores.npy"], mmap_mode="r")
    embeddings = np.load(paths["base_embeddings.npy"], mmap_mode="r")
    rows = int(record["rows"])
    if len(index) != rows or scores.shape != (rows,) or embeddings.shape != (rows, 768):
        raise ValueError("Cache arrays and index have inconsistent shapes")
    if list(index.columns) != INDEX_COLUMNS:
        raise ValueError("Cache index schema is not the revised stable-ID schema")
    if index["row_id"].duplicated().any():
        raise ValueError("Cache index has duplicate stable row IDs")
    if canonical_sha256(index["row_id"].tolist()) != record["row_id_sequence_sha256"]:
        raise ValueError("Cache row order does not match its manifest")
    return index, scores, embeddings, record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-file", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--component-audit", type=Path, required=True)
    parser.add_argument("--package-manifest", type=Path, required=True)
    parser.add_argument("--layer1-run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--splits", nargs="+", default=["train", "validation"],
        choices=["train", "validation", "final_test", "excluded_historical_test"],
    )
    parser.add_argument("--batch-size", type=int, default=128)
    parser.add_argument("--device")
    parser.add_argument("--base-model-name", default="distilbert-base-uncased")
    parser.add_argument(
        "--local-files-only", action=argparse.BooleanOptionalAction, default=True
    )
    parser.add_argument("--final-test-claim", type=Path)
    args = parser.parse_args()
    result = build_cache(
        data_file=args.data_file,
        split_manifest_path=args.split_manifest,
        component_audit_path=args.component_audit,
        package_manifest_path=args.package_manifest,
        layer1_run=args.layer1_run,
        output_dir=args.output_dir,
        splits=args.splits,
        batch_size=args.batch_size,
        device_name=args.device,
        base_model_name=args.base_model_name,
        local_files_only=args.local_files_only,
        final_test_claim=args.final_test_claim,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
