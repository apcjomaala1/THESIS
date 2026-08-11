"""
Tune the weighted scorer on the validation set.

Searches over:
  * Per-feature weights w_1..w_7 (coarse coordinate-ascent grid).
  * SPIKE_DROP — the minimum risk-score drop that counts as a retreat for the
    OGDM compliance-testing feature (Lorenzo-Dus et al., 2016).
  * `flagging_threshold` — conversation-level alert cutoff.

The objective is **recall at precision >= MIN_PRECISION**, matching Thesis
Chapter 1's primary success metric (reducing false negatives in grooming
detection). If no configuration meets the precision floor, the search falls
back to maximizing F1.

Outputs `weighted_scorer.json` consumable by `WeightedScorer.load()`.
"""

import argparse
import itertools
import json
from pathlib import Path

import numpy as np

from weighted_scorer import WeightedScorer


# Precision floor for the tuner. Lowered from 0.5 to 0.15 for the dyadic
# Thesis 1 corpus: PAN12 has only ~41 dyadic predator convs out of 18.5k 2-author
# convs (~0.2% positive prior), so precision >= 0.5 is essentially mathematically
# blocked even with a strong classifier. 0.15 is roughly 3x the dyadic base rate
# and represents a defensible triage operating point (a moderator queue catching
# 1-in-7 flagged convs as real grooming, with high recall).
MIN_PRECISION = 0.15

# Each weight is searched over the same coarse grid. Wider per-axis grids cost
# real time at 7 dims (5^7 = 78,125 combos already), so we use 3 values per
# axis. Tighten the grid around the chosen point if you need finer tuning.
WEIGHT_GRID = [0.1, 0.3, 0.6]
SPIKE_DROP_GRID = [0.10, 0.15, 0.20, 0.25, 0.30]
FLAG_THRESHOLD_GRID = np.linspace(0.30, 0.80, 11)


def conversation_metrics(predictions, labels):
    """Conversation-level recall, precision, F1 from binary arrays."""
    tp = int(((predictions == 1) & (labels == 1)).sum())
    fp = int(((predictions == 1) & (labels == 0)).sum())
    fn = int(((predictions == 0) & (labels == 1)).sum())
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    return recall, precision, f1


def evaluate_configuration(scorer, val_conversations):
    """
    For one (weights, spike_drop, flag_threshold) configuration, compute
    conversation-level recall / precision / F1 on the validation set.

    `val_conversations` is a list of dicts, each with:
        trajectory_features: np.ndarray of shape (T, 7)
        conversation_label:  int (0/1)
    """
    preds = np.zeros(len(val_conversations), dtype=np.int32)
    labels = np.zeros(len(val_conversations), dtype=np.int32)
    for i, conv in enumerate(val_conversations):
        turn_scores = scorer.score_sequence(conv["trajectory_features"])
        flagged = int(turn_scores.max() > scorer.flagging_threshold)
        preds[i] = flagged
        labels[i] = int(conv["conversation_label"])
    return conversation_metrics(preds, labels)


def search(val_conversations, min_precision=MIN_PRECISION):
    """Grid search over weights × spike_drop × flag_threshold."""
    best_under_precision = None  # (recall, f1, config)
    best_f1_fallback = None      # (f1, recall, config)
    total_combos = (len(WEIGHT_GRID) ** 7) * len(SPIKE_DROP_GRID) * len(FLAG_THRESHOLD_GRID)
    print(f"Searching {total_combos:,} configurations...")

    weight_combos = itertools.product(*[WEIGHT_GRID] * 7)
    for i, weights in enumerate(weight_combos):
        weights_arr = np.array(weights, dtype=np.float32)
        for spike_drop in SPIKE_DROP_GRID:
            # Recompute features for each spike_drop happens upstream;
            # here we assume the caller passed feature matrices computed at
            # the spike_drop being searched. If you want one search to span
            # spike_drops, pass per-config feature matrices.
            for flag_threshold in FLAG_THRESHOLD_GRID:
                scorer = WeightedScorer(
                    weights=weights_arr,
                    spike_drop=spike_drop,
                    flagging_threshold=float(flag_threshold),
                )
                recall, precision, f1 = evaluate_configuration(scorer, val_conversations)
                cfg = {
                    "weights": weights_arr.tolist(),
                    "spike_drop": float(spike_drop),
                    "flagging_threshold": float(flag_threshold),
                    "recall": recall, "precision": precision, "f1": f1,
                }
                if precision >= min_precision:
                    if best_under_precision is None or recall > best_under_precision["recall"]:
                        best_under_precision = cfg
                if best_f1_fallback is None or f1 > best_f1_fallback["f1"]:
                    best_f1_fallback = cfg

        if (i + 1) % 1000 == 0:
            print(f"  ... {i + 1:,} weight combos searched")

    return best_under_precision, best_f1_fallback


def main():
    parser = argparse.ArgumentParser(description="Tune weighted scorer on val set.")
    parser.add_argument(
        "--val-features", required=True,
        help="Path to .npz with `features` (object array of (T,7) arrays) and `labels` (ints).",
    )
    parser.add_argument("--out", default="weighted_scorer.json")
    parser.add_argument("--min-precision", type=float, default=MIN_PRECISION)
    args = parser.parse_args()

    data = np.load(args.val_features, allow_pickle=True)
    val_conversations = [
        {"trajectory_features": feats, "conversation_label": int(lab)}
        for feats, lab in zip(data["features"], data["labels"])
    ]
    print(f"Loaded {len(val_conversations)} validation conversations.")

    best_p, best_f1 = search(val_conversations, min_precision=args.min_precision)

    if best_p is not None:
        chosen = best_p
        print(f"\nBest config meeting precision >= {args.min_precision}:")
    else:
        chosen = best_f1
        print(f"\nNo config met precision floor; falling back to best F1:")
    for k, v in chosen.items():
        print(f"  {k}: {v}")

    WeightedScorer(
        weights=np.array(chosen["weights"], dtype=np.float32),
        spike_drop=chosen["spike_drop"],
        flagging_threshold=chosen["flagging_threshold"],
    ).save(args.out)


if __name__ == "__main__":
    main()
