"""Read verified stable-ID caches as chronological conversation sequences."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import numpy as np

from .cache import load_partition_cache
from .centroid import load_centroid
from .features import compute_sequence_features


@dataclass
class ConversationSequence:
    conversation_id: str
    row_ids: list[str]
    trajectory_features: np.ndarray
    embeddings: np.ndarray
    label: int


def load_conversation_sequences(
    partition_cache: Path,
    centroid_dir: Path,
    expected_split: str,
    spike_threshold: float,
    drop_threshold: float,
) -> tuple[list[ConversationSequence], dict]:
    index, scores, embeddings, cache_manifest = load_partition_cache(
        partition_cache, expected_split=expected_split
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
            raise ValueError(f"Cache and centroid disagree on base-model field: {field}")
    if (
        expected_split == "train"
        and cache_manifest["canonical_payload_sha256"]
        != centroid_manifest["source_cache_manifest_payload_sha256"]
    ):
        raise ValueError("Centroid was not constructed from this exact training cache")

    sequences: list[ConversationSequence] = []
    for conversation_id, positions in index.groupby(
        "conversation_id", sort=True
    ).indices.items():
        positions = np.asarray(positions, dtype=np.int64)
        if not np.array_equal(positions, np.arange(positions[0], positions[-1] + 1)):
            raise ValueError(f"Cache rows are not contiguous for {conversation_id}")
        block = index.iloc[positions]
        labels = block["conversation_label"].astype(int).unique()
        if len(labels) != 1:
            raise ValueError(f"Conversation label changes within {conversation_id}")
        conversation_scores = np.asarray(scores[positions], dtype=np.float32)
        conversation_embeddings = np.asarray(embeddings[positions], dtype=np.float32)
        trajectory = compute_sequence_features(
            proxy_scores=conversation_scores,
            embeddings=conversation_embeddings,
            speaker_indices=block["speaker_index"].to_numpy(dtype=np.int64),
            benign_centroid=centroid,
            spike_threshold=spike_threshold,
            drop_threshold=drop_threshold,
        )
        sequences.append(
            ConversationSequence(
                conversation_id=str(conversation_id),
                row_ids=block["row_id"].astype(str).tolist(),
                trajectory_features=trajectory,
                embeddings=conversation_embeddings,
                label=int(labels[0]),
            )
        )
    expected_conversations = int(cache_manifest["conversations"])
    if len(sequences) != expected_conversations:
        raise ValueError("Conversation cache reconstruction is incomplete")
    metadata = {
        "cache_manifest": cache_manifest,
        "centroid_manifest": centroid_manifest,
        "spike_threshold": float(spike_threshold),
        "drop_threshold": float(drop_threshold),
    }
    return sequences, metadata
