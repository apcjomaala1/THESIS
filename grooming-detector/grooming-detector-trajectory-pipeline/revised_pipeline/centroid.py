"""Build the benign centroid from negative training conversations only."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .cache import load_partition_cache
from .contracts import canonical_sha256, sha256_file, write_json


def build_training_centroid(train_cache_dir: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Centroid output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    index, _scores, embeddings, cache_manifest = load_partition_cache(
        train_cache_dir, expected_split="train"
    )
    negative_conversations = sorted(
        index.loc[index["conversation_label"] == 0, "conversation_id"].unique()
    )
    if not negative_conversations:
        raise ValueError("Training cache has no negative conversations")
    negative_mask = index["conversation_id"].isin(negative_conversations).to_numpy()
    if int(negative_mask.sum()) == 0:
        raise ValueError("Training cache has no negative rows")
    # Give each conversation equal influence so long chats do not dominate the
    # reference direction. Cosine distance is then evaluated against the
    # normalized mean direction.
    conversation_means = []
    for conversation_id in negative_conversations:
        positions = np.flatnonzero(
            index["conversation_id"].to_numpy() == conversation_id
        )
        conversation_means.append(
            np.asarray(embeddings[positions], dtype=np.float64).mean(axis=0)
        )
    centroid = np.mean(np.stack(conversation_means), axis=0)
    norm = float(np.linalg.norm(centroid))
    if norm <= 0.0:
        raise ValueError("Computed centroid has zero norm")
    centroid = (centroid / norm).astype(np.float32)
    if centroid.shape != (768,) or not np.isfinite(centroid).all():
        raise ValueError("Computed centroid is invalid")

    ids_path = output_dir / "source_negative_conversation_ids.txt"
    ids_path.write_text("\n".join(negative_conversations) + "\n", encoding="utf-8")
    centroid_path = output_dir / "benign_centroid.npy"
    np.save(centroid_path, centroid, allow_pickle=False)
    record = {
        "schema_version": 1,
        "status": "complete",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_split": "train",
        "selection_rule": (
            "mean current-turn embedding per negative training conversation; "
            "equal-weight mean across conversations; L2 normalize"
        ),
        "label_source": "official predator-author membership aggregated by conversation",
        "is_suspicious_used": False,
        "negative_conversations": len(negative_conversations),
        "negative_rows": int(negative_mask.sum()),
        "centroid_shape": [768],
        "centroid_dtype": "float32",
        "centroid_l2_norm": float(np.linalg.norm(centroid)),
        "source_conversation_ids_sha256": canonical_sha256(negative_conversations),
        "source_cache_manifest_payload_sha256": cache_manifest[
            "canonical_payload_sha256"
        ],
        "base_encoder_state_sha256": cache_manifest["provenance"][
            "base_encoder_state_sha256"
        ],
        "base_encoder_config_sha256": cache_manifest["provenance"][
            "base_encoder_config_sha256"
        ],
        "base_tokenizer": cache_manifest["provenance"]["base_tokenizer"],
        "torch_version": cache_manifest["provenance"]["torch_version"],
        "transformers_version": cache_manifest["provenance"]["transformers_version"],
        "files": {
            "benign_centroid.npy": sha256_file(centroid_path),
            "source_negative_conversation_ids.txt": sha256_file(ids_path),
        },
    }
    record["canonical_payload_sha256"] = canonical_sha256(record)
    write_json(output_dir / "centroid_manifest.json", record)
    return record


def load_centroid(centroid_dir: Path) -> tuple[np.ndarray, dict[str, Any]]:
    import json

    manifest = json.loads(
        (centroid_dir / "centroid_manifest.json").read_text(encoding="utf-8")
    )
    payload = dict(manifest)
    expected = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected:
        raise ValueError("Centroid manifest integrity check failed")
    centroid_path = centroid_dir / "benign_centroid.npy"
    ids_path = centroid_dir / "source_negative_conversation_ids.txt"
    for name, path in {
        "benign_centroid.npy": centroid_path,
        "source_negative_conversation_ids.txt": ids_path,
    }.items():
        if sha256_file(path) != manifest["files"][name]:
            raise ValueError(f"Centroid artifact hash mismatch: {name}")
    centroid = np.load(centroid_path, allow_pickle=False)
    if centroid.shape != (768,) or centroid.dtype != np.float32:
        raise ValueError("Centroid has an unexpected shape or dtype")
    return centroid, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-cache", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    record = build_training_centroid(args.train_cache, args.output_dir)
    print(f"Training-only centroid prepared: {record['negative_conversations']:,} conversations")


if __name__ == "__main__":
    main()
