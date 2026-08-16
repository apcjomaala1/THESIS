"""Lock neutral trajectory-feature thresholds before comparator/LSTM fitting.

The spike threshold is the already validation-selected Layer 1 author-row
operating threshold. The drop magnitude is the 75th percentile of positive
adjacent score decreases that follow a spike in the untouched validation
distribution. Neither value is selected from conversation labels, weighted
scores, or LSTM outcomes, so the shared inputs do not privilege one method.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .cache import load_partition_cache
from .contracts import canonical_sha256, write_json
from .features import FEATURE_NAMES
from .metrics import select_f05_threshold


LOCKED_DROP_QUANTILE = 0.75


def derive_feature_thresholds(
    index: Any,
    scores: np.ndarray,
) -> dict[str, Any]:
    """Deterministically derive the shared thresholds from validation rows."""
    author_labels = index["author_label"].to_numpy(dtype=np.int8)
    fp32_scores = np.asarray(scores, dtype=np.float64)
    spike_threshold, spike_metrics = select_f05_threshold(author_labels, fp32_scores)
    if not 0.0 <= spike_threshold <= 1.0:
        raise ValueError("Layer 1 row threshold is outside [0, 1]")
    eligible_drops: list[float] = []
    for _conversation_id, positions in index.groupby(
        "conversation_id", sort=True
    ).indices.items():
        conversation_scores = np.asarray(scores[positions], dtype=np.float64)
        if len(conversation_scores) < 2:
            continue
        drops = conversation_scores[:-1] - conversation_scores[1:]
        # Strict comparison is intentional and matches the approved feature
        # definition 1[R_i > tau]. It is distinct from classifier decisions,
        # which use score >= their selected operating threshold.
        eligible = drops[
            (conversation_scores[:-1] > spike_threshold) & (drops > 0.0)
        ]
        eligible_drops.extend(eligible.tolist())
    if not eligible_drops:
        raise ValueError(
            "Validation cache contains no positive adjacent drop after a proxy-score spike"
        )
    return {
        "spike_threshold": float(spike_threshold),
        "spike_metrics": spike_metrics,
        "drop_threshold": float(
            np.quantile(eligible_drops, LOCKED_DROP_QUANTILE)
        ),
        "eligible_validation_drops": len(eligible_drops),
    }


def lock_feature_config(validation_cache: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(f"Feature configuration already exists: {output}")
    index, scores, _embeddings, cache_manifest = load_partition_cache(
        validation_cache, expected_split="validation"
    )
    derived = derive_feature_thresholds(index, scores)
    spike_threshold = derived["spike_threshold"]
    spike_metrics = derived["spike_metrics"]
    drop_threshold = derived["drop_threshold"]
    record = {
        "schema_version": 1,
        "status": "locked_before_comparator_or_lstm_fitting",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "feature_names": list(FEATURE_NAMES),
        "spike_threshold": spike_threshold,
        "spike_threshold_source": (
            "recomputed author-row F0.5 threshold from the locked FP32 validation cache"
        ),
        "spike_comparison": "score > spike_threshold",
        "spike_threshold_metrics": spike_metrics,
        "trainer_mixed_precision_row_threshold_provenance_only": cache_manifest[
            "provenance"
        ]["layer1_row_threshold"],
        "drop_threshold": drop_threshold,
        "drop_threshold_source": (
            "75th percentile of positive adjacent validation-score decreases "
            "whose preceding score exceeds the frozen spike threshold"
        ),
        "drop_threshold_quantile": LOCKED_DROP_QUANTILE,
        "eligible_validation_drops": derived["eligible_validation_drops"],
        "selection_partition": "validation",
        "conversation_labels_used_for_feature_thresholds": False,
        "architecture_outcomes_used": False,
        "validation_cache_manifest_payload_sha256": cache_manifest[
            "canonical_payload_sha256"
        ],
        "layer1_model_tree_sha256": cache_manifest["provenance"][
            "layer1_model_tree_sha256"
        ],
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    record["canonical_payload_sha256"] = canonical_sha256(record)
    write_json(output, record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = lock_feature_config(args.validation_cache, args.output)
    print(
        f"Feature thresholds locked: spike={result['spike_threshold']:.8f}, "
        f"drop={result['drop_threshold']:.8f}"
    )


if __name__ == "__main__":
    main()
