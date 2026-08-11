"""
Dataset inventory script — produces exact counts for Table 3.1.

Usage:
    python dataset_counts.py --csv ../trained_model_distillbert/pan12_final_dataset.csv
"""

import argparse
import pandas as pd


def count_dataset(csv_path, label):
    df = pd.read_csv(csv_path)
    print(f"\n{'=' * 60}")
    print(f"  Dataset: {label}")
    print(f"  Path:    {csv_path}")
    print(f"{'=' * 60}")
    print(f"  Total rows (messages):    {len(df):,}")

    # Identify the conversation ID column (raw PAN12 uses 'conv_id',
    # canonical loader output uses 'conversation_id')
    conv_col = None
    for candidate in ["conversation_id", "conv_id"]:
        if candidate in df.columns:
            conv_col = candidate
            break

    if conv_col:
        n_convs = df[conv_col].nunique()
        print(f"  Unique conversations:     {n_convs:,}  (column: {conv_col})")
    else:
        print("  [conversation_id / conv_id column not found]")

    if "author" in df.columns:
        n_authors = df["author"].nunique()
        print(f"  Unique authors:           {n_authors:,}")

    # Label distribution
    for col in ["is_suspicious", "label", "conversation_label"]:
        if col in df.columns:
            vc = df[col].value_counts().sort_index()
            print(f"\n  Label column: '{col}'")
            for val, cnt in vc.items():
                pct = cnt / len(df) * 100
                print(f"    {val}: {cnt:>8,}  ({pct:.1f}%)")

    # If is_predator / author_is_predator exists, count predatory convos
    pred_col = None
    for candidate in ["is_predator", "author_is_predator"]:
        if candidate in df.columns:
            pred_col = candidate
            break

    if pred_col and conv_col:
        pred_convs = df.groupby(conv_col)[pred_col].max()
        n_pred = (pred_convs == 1).sum()
        n_safe = (pred_convs == 0).sum()
        print(f"\n  Predatory conversations:  {n_pred:,}")
        print(f"  Safe conversations:       {n_safe:,}")

    # Dyadic vs multi-party
    if conv_col and "author" in df.columns:
        authors_per_conv = df.groupby(conv_col)["author"].nunique()
        dyadic = (authors_per_conv == 2).sum()
        multi = (authors_per_conv > 2).sum()
        mono = (authors_per_conv == 1).sum()
        print(f"\n  Dyadic (2-author) convos: {dyadic:,}")
        print(f"  Multi-party (3+) convos:  {multi:,}")
        if mono > 0:
            print(f"  Mono-author convos:       {mono:,}")

    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset inventory for Table 3.1")
    parser.add_argument(
        "--datasets", nargs="+", metavar="NAME=PATH",
        help="Datasets in NAME=PATH format",
    )
    parser.add_argument("--csv", help="Single CSV shortcut")
    args = parser.parse_args()

    if args.csv:
        count_dataset(args.csv, "PAN12")
    elif args.datasets:
        for spec in args.datasets:
            name, path = spec.split("=", 1)
            count_dataset(path, name)
    else:
        parser.error("Provide --csv or --datasets")
