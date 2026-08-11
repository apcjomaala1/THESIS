"""
Demo mode A — replay a PAN12 conversation message-by-message.

Reads one conversation from the PAN12 CSV by `conv_id` and streams it through
the same scoring core as the live-chat mode. Prints, per turn:

  * The message + its author
  * Layer 1 risk score
  * Each trajectory feature
  * Weighted aggregate score
  * Whether the conversation has been flagged yet, and on which turn

This is the empirical-defense demo: it ties the running pipeline directly to
the time-to-detection metric reported in evaluation.

Usage:
    python -m demo.replay --csv ../trained_model_distillbert/pan12_final_dataset.csv \
        --conv-id <some_conv_id>
"""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from demo.scoring_core import build_scoring_stack, new_conversation


def format_features(features_dict):
    return "  ".join(f"{k}={v:+.3f}" for k, v in features_dict.items())


def main():
    parser = argparse.ArgumentParser(description="PAN12 conversation replay demo.")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--conv-id", required=True)
    parser.add_argument("--centroid", default="benign_centroid.npy")
    parser.add_argument("--classifier", default="../trained_model_distillbert/final_moderation_model")
    parser.add_argument("--scorer-config", default="weighted_scorer.json")
    parser.add_argument("--delay", type=float, default=0.0, help="Seconds between turns.")
    args = parser.parse_args()

    df = pd.read_csv(args.csv).dropna(subset=["text"])
    df["text"] = df["text"].astype(str)
    df = df[df["conv_id"] == args.conv_id].copy()
    if df.empty:
        raise SystemExit(f"No messages found for conversation {args.conv_id}")
    df["line_int"] = df["line"].astype(int)
    df = df.sort_values("line_int").reset_index(drop=True)
    print(f"Replaying {len(df)} messages from conversation {args.conv_id}")

    stack = build_scoring_stack(
        classifier_path=args.classifier,
        centroid_path=args.centroid,
        scorer_path=args.scorer_config,
    )
    conv = new_conversation(stack)

    for _, row in df.iterrows():
        result = conv.add_message(row["text"], row["author"])
        if result is None:
            continue
        print(
            f"[turn {result['turn']:>3}] author={result['author']:<12} "
            f"risk={result['risk_score']:.3f}  agg={result['turn_score']:.3f}"
            f"{'  *FLAGGED*' if result['flagged_now'] else ''}"
        )
        print(f"   text: {result['text']}")
        print(f"   features: {format_features(result['trajectory_features'])}")
        if args.delay:
            time.sleep(args.delay)

    print("\n--- summary ---")
    print(f"First flagged turn: {conv.first_flagged_turn}")
    print(f"Final aggregate score: {conv.turn_scores[-1]:.3f}")
    print(f"Peak Layer-1 risk: {max(conv.risk_scores):.3f}")


if __name__ == "__main__":
    main()
