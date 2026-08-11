"""
Precompute a 768-dim "benign chat" centroid embedding from PAN12.

This is used by features.py to compute topic_drift as cosine distance from a
fixed neutral-chat baseline, rather than from each conversation's own first
message. The latter silently breaks the OGDM "approach phase" feature
(Lorenzo-Dus et al., 2016) whenever a predator opens with risky content — the
drift score is then ~0 throughout, masking the very signal it is meant to
capture.

A conversation qualifies as benign if:
  * it has no `is_suspicious` lines, AND
  * none of its participants is in the predator-author list.

Usage:
    python compute_benign_centroid.py --csv pan12_final_dataset.csv \
        --out benign_centroid.npy [--n-conversations 500] [--max-messages 50]
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from data_loader import load_canonical_csv
from features import MessageEncoder


def select_benign_conversations(df, n_conversations, seed=42):
    """Pick `n` conversations with no suspicious lines and no predator authors.
    Operates on a canonical-schema DataFrame (see data_loader.CANONICAL_COLUMNS)."""
    bad_convs = set(df.loc[df["is_suspicious"] == 1, "conversation_id"].unique())
    bad_convs.update(df.loc[df["author_is_predator"] == 1, "conversation_id"].unique())

    benign_pool = df.loc[~df["conversation_id"].isin(bad_convs), "conversation_id"].unique()
    print(f"Benign conversation pool: {len(benign_pool)}")

    if len(benign_pool) < n_conversations:
        print(f"Pool smaller than requested {n_conversations}; using all of it.")
        return list(benign_pool)

    rng = np.random.default_rng(seed)
    return list(rng.choice(benign_pool, size=n_conversations, replace=False))


def compute_centroid(df, conv_ids, max_messages_per_conv, encoder):
    """Encode messages from selected conversations, mean-pool to one vector."""
    sub = df[df["conversation_id"].isin(conv_ids)].copy()
    sub["text"] = sub["text"].astype(str)
    sub = sub[sub["text"].str.strip() != ""]

    if max_messages_per_conv is not None:
        sub = sub.groupby("conversation_id", group_keys=False).head(max_messages_per_conv)

    texts = sub["text"].tolist()
    print(f"Encoding {len(texts)} benign messages...")
    embeddings = encoder.encode(texts, batch_size=64)
    centroid = embeddings.mean(axis=0)
    centroid = centroid / (np.linalg.norm(centroid) + 1e-12)
    return centroid.astype(np.float32)


def _parse_dataset_specs(specs):
    out = []
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"--datasets entry '{spec}' is not in name=path form")
        name, path = spec.split("=", 1)
        out.append((name.strip(), path.strip()))
    return out


def main():
    parser = argparse.ArgumentParser(description="Precompute benign-chat centroid for topic_drift baseline.")
    parser.add_argument("--csv", help="Single PAN12 CSV (equivalent to --datasets pan12=<path>).")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=None,
        metavar="NAME=PATH",
        help="One or more canonical-schema CSVs to draw benign convs from. "
             "Mixing PAN12 with the Discord/group-chat CSVs gives a more "
             "representative benign baseline than PAN12 alone.",
    )
    parser.add_argument("--out", default="benign_centroid.npy", help="Output .npy file")
    parser.add_argument("--n-conversations", type=int, default=500)
    parser.add_argument("--max-messages", type=int, default=50,
                        help="Cap messages per conversation to keep total tractable")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--require-dyadic",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Restrict centroid pool to dyadic (2-author) conversations. "
             "Default ON to match the dyadic Thesis 1 corpus; pass --no-require-dyadic "
             "to use multi-party benign chats too.",
    )
    args = parser.parse_args()

    if not (args.csv or args.datasets):
        parser.error("Provide --csv or --datasets.")

    sources = []
    if args.datasets:
        sources.extend(_parse_dataset_specs(args.datasets))
    if args.csv:
        sources.append(("pan12", args.csv))

    frames = [
        load_canonical_csv(path, name, require_dyadic=args.require_dyadic)
        for name, path in sources
    ]
    df = pd.concat(frames, ignore_index=True)
    print(f"Combined pool: {len(df)} messages across "
          f"{df['conversation_id'].nunique()} conversations from "
          f"{df['dataset_source'].nunique()} sources")

    conv_ids = select_benign_conversations(df, args.n_conversations, seed=args.seed)
    print(f"Selected {len(conv_ids)} benign conversations.")

    encoder = MessageEncoder()
    centroid = compute_centroid(df, conv_ids, args.max_messages, encoder)

    out_path = Path(args.out)
    np.save(out_path, centroid)
    print(f"Saved centroid (dim={centroid.shape[0]}) to {out_path}")


if __name__ == "__main__":
    main()
