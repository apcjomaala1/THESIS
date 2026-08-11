"""
PAN12 loader for the trajectory pipeline.

Reads three PAN12 files:
  1. The XML chat corpus (conversations and messages, with `line` numbers on each <message>).
  2. The predators-list file: one predator author ID per line.
  3. The diff file: lines of `<conv_id>\\t<line_num>` identifying suspicious messages.

Returns conversation snapshots with PER-MESSAGE `is_suspicious` labels (the
training target for Layer 1) and a conversation-level `is_predatory` flag used
for evaluation.

== Canonical dataset schema ==

All loaders in this module emit a pandas DataFrame with these columns:

    conversation_id    str    — unique conversation identifier
    line               int    — turn order within the conversation (1-indexed)
    author_id          str    — speaker identifier (anonymized per dataset)
    text               str    — message text (non-empty after strip)
    is_suspicious      int    — 1 if this message is grooming-relevant, else 0
    author_is_predator int    — 1 if this author was ever a confirmed predator

Adding a new dataset (ChatCoder2, synthetic, etc.) only requires writing a
loader that produces a DataFrame in this schema; everything downstream
(features, scorer, evaluation) is dataset-agnostic.

== Multi-party conversations ==

PAN12 contains many group chats (3–23 participants). OGDM is dyadic, so the
trajectory features that depend on a "pair" — turn-taking imbalance in
particular — operationalize the relevant dyad as the two most active speakers
in the conversation so far. See features.compute_trajectory_features.
"""

import csv
import html
import random
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import pandas as pd


def load_predator_ids(predators_path):
    """One predator author ID per line."""
    with open(predators_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def load_suspicious_lines(diff_path):
    """Returns set of `(conv_id, line_num)` tuples flagged as suspicious."""
    suspicious = set()
    with open(diff_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                suspicious.add((parts[0], parts[1]))
    return suspicious


def parse_pan12_xml(xml_path, predator_ids, suspicious_lines):
    """
    Stream-parse PAN12 XML into a flat dataframe of messages.

    Columns: conversation_id, line, author_id, text, is_suspicious, author_is_predator
    """
    rows = []
    current_conv_id = None
    context = ET.iterparse(xml_path, events=("start", "end"))

    for event, elem in context:
        if event == "start" and elem.tag == "conversation":
            current_conv_id = elem.get("id")
        elif event == "end" and elem.tag == "message":
            line_num = elem.get("line")

            author_elem = elem.find("author")
            author_id = author_elem.text if author_elem is not None else "unknown"

            text_elem = elem.find("text")
            raw_text = text_elem.text if text_elem is not None and text_elem.text is not None else ""
            text = html.unescape(raw_text).strip()

            if text:
                rows.append({
                    "conversation_id": current_conv_id,
                    "line": line_num,
                    "author_id": author_id,
                    "text": text,
                    "is_suspicious": 1 if (current_conv_id, line_num) in suspicious_lines else 0,
                    "author_is_predator": 1 if author_id in predator_ids else 0,
                })
            elem.clear()

    return pd.DataFrame(rows)


def filter_two_author_conversations(df):
    """
    Keep only conversations with exactly two distinct authors.

    NOT applied in the default pipeline anymore — features now handle any
    author count via dominant-dyad reduction (see features.py). Retained for
    ablation studies and to support the historical 2-author-only experiments.
    """
    author_counts = df.groupby("conversation_id")["author_id"].nunique()
    keep = author_counts[author_counts == 2].index
    before = df["conversation_id"].nunique()
    df = df[df["conversation_id"].isin(keep)].reset_index(drop=True)
    after = df["conversation_id"].nunique()
    print(f"  2-author filter: kept {after} / {before} conversations")
    return df


def build_conversation_snapshots(df):
    """
    From the per-message dataframe, build one snapshot per (conversation, turn).

    Each snapshot carries the full history up to and including that turn,
    its per-message `is_suspicious` label, and the per-message `is_predatory`
    label inherited from the author (used only for evaluation, never for
    Layer 1 training).
    """
    has_source = "dataset_source" in df.columns
    snapshots = []
    for conv_id, group in df.groupby("conversation_id"):
        # `line` is a string-or-int turn order across sources.
        group = group.assign(line_int=group["line"].astype(int))
        group = group.sort_values("line_int").reset_index(drop=True)
        conv_is_predatory = int(group["author_is_predator"].max())
        predator_authors = sorted(
            group.loc[group["author_is_predator"] == 1, "author_id"]
            .astype(str)
            .unique()
            .tolist()
        )
        dataset_source = group["dataset_source"].iloc[0] if has_source else "unknown"

        messages_so_far = []
        authors_so_far = []
        per_msg_labels = []

        for i, row in group.iterrows():
            messages_so_far.append(row["text"])
            authors_so_far.append(row["author_id"])
            per_msg_labels.append(int(row["is_suspicious"]))

            snapshots.append({
                "conversation_id": conv_id,
                "turn": i,
                "messages_so_far": list(messages_so_far),
                "authors_so_far": list(authors_so_far),
                "per_message_labels": list(per_msg_labels),
                "label": int(row["is_suspicious"]),
                "conversation_label": conv_is_predatory,
                # Split/audit metadata only. Keeping the actual predator-author
                # IDs lets an author-disjoint evaluation prove that this
                # positive-author subset is also disjoint across partitions.
                "predator_authors": list(predator_authors),
                "dataset_source": dataset_source,
            })

    return snapshots


def load_pan12(xml_path, predators_path, diff_path):
    """Full PAN12 loading pipeline. Returns conversation snapshots."""
    print(f"Loading predator IDs from {predators_path}")
    predator_ids = load_predator_ids(predators_path)
    print(f"  {len(predator_ids)} predator authors")

    print(f"Loading suspicious lines from {diff_path}")
    suspicious_lines = load_suspicious_lines(diff_path)
    print(f"  {len(suspicious_lines)} flagged lines")

    print(f"Parsing XML from {xml_path}")
    df = parse_pan12_xml(xml_path, predator_ids, suspicious_lines)
    print(f"  {len(df)} messages across {df['conversation_id'].nunique()} conversations")

    print(f"  {int(df['is_suspicious'].sum())} suspicious messages")

    print("Building conversation snapshots...")
    snapshots = build_conversation_snapshots(df)
    print(f"  {len(snapshots)} snapshots total")
    return snapshots


CANONICAL_COLUMNS = [
    "conversation_id", "line", "author_id", "text",
    "is_suspicious", "author_is_predator",
]

# Source CSVs use slightly different column names. We normalize on read.
COLUMN_ALIASES = {
    # PAN12 final dataset (trained_model_distillbert/Python.py output)
    "conv_id":  "conversation_id",
    # Custom-annotated CSVs (Roblox / YouTube / Discord)
    "convo_id": "conversation_id",
    # Common conversation-id aliases in external exports.
    "chat_id": "conversation_id",
    "chatId": "conversation_id",
    "chatName": "conversation_id",
    "chat_name": "conversation_id",
    "dialogue_id": "conversation_id",
    "session_id": "conversation_id",
    "sessionId": "conversation_id",
    "thread_id": "conversation_id",
    "author":   "author_id",
    "authorName": "author_id",
    "author_name": "author_id",
    "speaker": "author_id",
    "sender": "author_id",
    "user": "author_id",
    "user_id": "author_id",
    "username": "author_id",
    "message": "text",
    "messageText": "text",
    "message_text": "text",
    "content": "text",
    "body": "text",
    "turn": "line",
    "turn_id": "line",
    "turnIndex": "line",
    "message_index": "line",
    "message_idx": "line",
    "message_no": "line",
    "messageNo": "line",
    "index": "line",
    # `is_predator` in source CSVs is an author-level flag carried per message
    "is_predator": "author_is_predator",
    "predator": "author_is_predator",
    "predator_flag": "author_is_predator",
    "user_is_predator": "author_is_predator",
    "author_predator": "author_is_predator",
    "label": "is_suspicious",
    "is_predatory": "is_suspicious",
    "predatory": "is_suspicious",
    "suspicious": "is_suspicious",
    "warning": "is_suspicious",
    "message_label": "is_suspicious",
}


def _read_delimited_table(path):
    """
    Read a CSV/TSV table while tolerating the eSPD repo's TSV exports.

    We prefer sniffing over suffix-only logic because the eSPD tooling can
    emit either `.csv` or `.tsv` depending on which export path was used.
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8", newline="") as f:
        sample = f.read(4096)

    delimiter = ","
    if sample:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
            delimiter = dialect.delimiter
        except csv.Error:
            if path.suffix.lower() == ".tsv":
                delimiter = "\t"

    return pd.read_csv(path, sep=delimiter)


def load_canonical_csv(path, dataset_name, require_dyadic=False):
    """
    Load any CSV that conforms (loosely) to the canonical schema and emit a
    DataFrame with strictly canonical columns. Handles column aliases and
    drops out-of-scope columns (e.g. `image_type`).

    The `dataset_name` is prefixed onto every `conversation_id` so multi-source
    runs cannot accidentally collide on shared IDs (e.g. "yt_01" appears in
    both Roblox CSVs).

    Args:
        path:           CSV path.
        dataset_name:   short identifier (e.g. "pan12", "roblox_run").
        require_dyadic: if True, drop conversations with != 2 distinct authors.

    Returns: pd.DataFrame with columns CANONICAL_COLUMNS + ["dataset_source"].
    """
    print(f"Loading {dataset_name} from {path}")
    df = _read_delimited_table(path)
    df = df.rename(columns=COLUMN_ALIASES)

    # Some external exports preserve message order but omit an explicit line
    # column. Recover a stable 1-indexed turn order before validating.
    if "line" not in df.columns and "conversation_id" in df.columns:
        df["line"] = df.groupby("conversation_id").cumcount() + 1

    missing = [c for c in CANONICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"{path}: missing required canonical column(s) {missing}. "
            f"Got columns: {list(df.columns)}"
        )

    df = df[CANONICAL_COLUMNS].copy()
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str)
    df = df[df["text"].str.strip() != ""].reset_index(drop=True)
    # The tolerant parser hands back strings; coerce labels safely.
    df["is_suspicious"] = pd.to_numeric(df["is_suspicious"], errors="coerce").fillna(0).astype(int)
    df["author_is_predator"] = pd.to_numeric(df["author_is_predator"], errors="coerce").fillna(0).astype(int)
    df["author_id"] = df["author_id"].astype(str)
    # Namespace conversation IDs so multi-source merges never collide.
    df["conversation_id"] = dataset_name + ":" + df["conversation_id"].astype(str)
    df["dataset_source"] = dataset_name

    print(f"  {len(df)} messages across {df['conversation_id'].nunique()} conversations")
    print(f"  {int(df['is_suspicious'].sum())} suspicious messages, "
          f"{int(df['author_is_predator'].sum())} predator-author messages")

    if require_dyadic:
        df = filter_two_author_conversations(df)
        print(f"  {int(df['is_suspicious'].sum())} suspicious messages after dyadic filter")

    return df


def load_datasets(sources, require_dyadic=False):
    """
    Load one or more canonical-schema CSVs and return concatenated snapshots.

    Args:
        sources:        list of (dataset_name, path) tuples.
        require_dyadic: applied per source (so an already-dyadic external corpus
                        is unaffected, while PAN12 gets filtered to its dyadic
                        subset).

    Returns: list of snapshot dicts with an extra `dataset_source` field.
    """
    frames = []
    for name, path in sources:
        frames.append(load_canonical_csv(path, name, require_dyadic=require_dyadic))
    df = pd.concat(frames, ignore_index=True)
    print(f"Combined corpus: {len(df)} messages across "
          f"{df['conversation_id'].nunique()} conversations from "
          f"{df['dataset_source'].nunique()} sources")
    return build_conversation_snapshots(df)


def load_pan12_from_csv(csv_path, require_dyadic=False):
    """Back-compat single-source loader for PAN12. New code should prefer
    `load_datasets([("pan12", csv_path)], ...)`."""
    return load_datasets([("pan12", csv_path)], require_dyadic=require_dyadic)


# -- simulator (development / smoke tests only) --

def simulate_dataset(n_conversations=200, seed=42):
    """Synthetic snapshots that mimic PAN12 structure. Not used in evaluation."""
    random.seed(seed)
    snapshots = []
    for i in range(n_conversations):
        is_predatory = i < n_conversations // 2
        conv_id = f"sim_{i:04d}"
        n_turns = random.randint(8, 25)

        messages_so_far, authors_so_far, per_msg = [], [], []
        for t in range(n_turns):
            author = "user_A" if t % 2 == 0 else "user_B"
            authors_so_far.append(author)

            if is_predatory and t >= n_turns * 0.6:
                text = random.choice([
                    "lets talk somewhere private", "dont tell anyone about this",
                    "can you send me a photo", "lets meet up",
                    "you are so mature for your age",
                ])
                is_msg_suspicious = 1
            elif is_predatory and t >= n_turns * 0.3:
                text = random.choice([
                    "how old are you", "where do you live", "are your parents home",
                ])
                is_msg_suspicious = 1
            else:
                text = random.choice([
                    "hey how are you", "whats up", "haha yeah same",
                    "cool see you tomorrow", "sounds good",
                ])
                is_msg_suspicious = 0

            messages_so_far.append(text)
            per_msg.append(is_msg_suspicious)

            snapshots.append({
                "conversation_id": conv_id,
                "turn": t,
                "messages_so_far": list(messages_so_far),
                "authors_so_far": list(authors_so_far),
                "per_message_labels": list(per_msg),
                "label": is_msg_suspicious,
                "conversation_label": int(is_predatory),
            })

    print(f"Simulated {n_conversations} conversations, {len(snapshots)} snapshots")
    return snapshots
