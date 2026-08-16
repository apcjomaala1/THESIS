"""Training-only keyword lexicon baseline for the revised endpoint."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd

from .contracts import canonical_sha256, load_locked_manifest, write_json
from .data import attach_locked_splits, load_eligible_rows
from .metrics import conversation_metrics


TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)
STOPWORDS = frozenset(
    {
        "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
        "do", "for", "from", "had", "has", "have", "he", "her", "him",
        "his", "i", "if", "in", "is", "it", "its", "me", "my", "no",
        "not", "of", "on", "or", "our", "she", "so", "that", "the",
        "their", "them", "they", "this", "to", "was", "we", "were", "what",
        "when", "where", "who", "will", "with", "you", "your",
    }
)


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(str(text))]


def candidate_terms(text: str) -> set[str]:
    tokens = tokenize(text)
    unigrams = {
        token for token in tokens if len(token) >= 3 and token not in STOPWORDS
    }
    bigrams = {
        f"{left} {right}"
        for left, right in zip(tokens, tokens[1:])
        if left not in STOPWORDS or right not in STOPWORDS
    }
    return unigrams | bigrams


def contains_lexicon_term(text: str, lexicon: set[str]) -> bool:
    return bool(candidate_terms(text) & lexicon)


def derive_lexicon(
    training_frame: pd.DataFrame,
    max_terms: int = 50,
    min_positive_conversations: int = 3,
) -> list[dict[str, Any]]:
    labels = (
        training_frame.groupby("conversation_id")["author_is_predator"].max().astype(int)
    )
    positive_ids = set(labels[labels == 1].index)
    negative_ids = set(labels[labels == 0].index)
    if not positive_ids or not negative_ids:
        raise ValueError("Keyword derivation requires positive and negative training conversations")
    positive_df: Counter[str] = Counter()
    negative_df: Counter[str] = Counter()
    for conversation_id, conversation in training_frame.groupby(
        "conversation_id", sort=True
    ):
        terms: set[str] = set()
        for text in conversation["text"].astype(str):
            terms.update(candidate_terms(text))
        target = positive_df if conversation_id in positive_ids else negative_df
        target.update(terms)

    candidates: list[dict[str, Any]] = []
    for term, positive_count in positive_df.items():
        if positive_count < min_positive_conversations:
            continue
        negative_count = negative_df.get(term, 0)
        positive_rate = (positive_count + 0.5) / (len(positive_ids) + 1.0)
        negative_rate = (negative_count + 0.5) / (len(negative_ids) + 1.0)
        if positive_rate <= negative_rate:
            continue
        log_odds = math.log(positive_rate / (1.0 - positive_rate)) - math.log(
            negative_rate / (1.0 - negative_rate)
        )
        candidates.append(
            {
                "term": term,
                "n": len(term.split()),
                "positive_conversation_df": int(positive_count),
                "negative_conversation_df": int(negative_count),
                "positive_rate": positive_rate,
                "negative_rate": negative_rate,
                "log_odds_ratio": log_odds,
            }
        )
    candidates.sort(
        key=lambda row: (
            -row["log_odds_ratio"],
            -row["positive_conversation_df"],
            row["term"],
        )
    )
    selected = candidates[:max_terms]
    if not selected:
        raise ValueError("Training data did not produce an eligible keyword lexicon")
    return selected


def score_conversations(frame: pd.DataFrame, terms: Iterable[str]) -> pd.DataFrame:
    lexicon = set(terms)
    rows = []
    for conversation_id, conversation in frame.groupby("conversation_id", sort=True):
        label = int(conversation["author_is_predator"].max())
        matched = sorted(
            {
                term
                for text in conversation["text"].astype(str)
                for term in candidate_terms(text)
                if term in lexicon
            }
        )
        rows.append(
            {
                "conversation_id": conversation_id,
                "label": label,
                "score": float(bool(matched)),
                "prediction": int(bool(matched)),
                "matched_term_count": len(matched),
            }
        )
    return pd.DataFrame(rows)


def build_keyword_baseline(
    data_file: Path,
    split_manifest_path: Path,
    output_dir: Path,
    max_terms: int = 50,
    min_positive_conversations: int = 3,
) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Keyword output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = load_locked_manifest(split_manifest_path, data_file)
    frame = attach_locked_splits(load_eligible_rows(data_file), manifest)
    train = frame[frame["split"] == "train"].copy()
    validation = frame[frame["split"] == "validation"].copy()
    lexicon = derive_lexicon(train, max_terms, min_positive_conversations)
    terms = [row["term"] for row in lexicon]
    validation_predictions = score_conversations(validation, terms)
    metrics = conversation_metrics(
        validation_predictions["label"].to_numpy(dtype=np.int8),
        validation_predictions["score"].to_numpy(dtype=np.float64),
        threshold=0.5,
    )
    config = {
        "schema_version": 1,
        "status": "completed",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "training-derived fixed keyword lexicon",
        "derivation_partition": "train",
        "validation_partition": "validation",
        "decision_rule": "positive when any turn contains at least one frozen term",
        "tokenization": "lowercase ASCII-alphanumeric/apostrophe tokens; unigrams and adjacent bigrams",
        "max_terms": int(max_terms),
        "min_positive_conversations": int(min_positive_conversations),
        "lexicon": lexicon,
        "training_conversations": int(train["conversation_id"].nunique()),
        "training_conversation_id_sha256": canonical_sha256(
            sorted(train["conversation_id"].unique())
        ),
        "validation_conversations": int(validation["conversation_id"].nunique()),
        "validation_metrics": metrics,
        "data_sha256": manifest["dataset"]["sha256"],
        "split_manifest_payload_sha256": manifest["integrity"][
            "canonical_payload_sha256"
        ],
        "is_suspicious_used": False,
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    config["canonical_payload_sha256"] = canonical_sha256(config)
    write_json(output_dir / "keyword_config.json", config)
    validation_predictions.to_csv(
        output_dir / "validation_predictions.csv", index=False
    )
    return config


def validate_keyword_artifacts(
    data_file: Path,
    split_manifest_path: Path,
    keyword_dir: Path,
) -> dict[str, Any]:
    config = json.loads((keyword_dir / "keyword_config.json").read_text(encoding="utf-8"))
    payload = dict(config)
    expected_hash = payload.pop("canonical_payload_sha256", None)
    if canonical_sha256(payload) != expected_hash:
        raise ValueError("Keyword configuration failed its canonical hash check")
    manifest = load_locked_manifest(split_manifest_path, data_file)
    frame = attach_locked_splits(load_eligible_rows(data_file), manifest)
    train = frame[frame["split"] == "train"]
    validation = frame[frame["split"] == "validation"]
    regenerated = derive_lexicon(
        train,
        int(config["max_terms"]),
        int(config["min_positive_conversations"]),
    )
    if regenerated != config["lexicon"]:
        raise ValueError("Keyword lexicon is not the deterministic training-only result")
    predictions = score_conversations(
        validation, [row["term"] for row in regenerated]
    )
    recorded = pd.read_csv(keyword_dir / "validation_predictions.csv")
    if predictions["conversation_id"].tolist() != recorded["conversation_id"].tolist():
        raise ValueError("Keyword validation conversation order is wrong")
    for column in ["label", "score", "prediction", "matched_term_count"]:
        if not np.allclose(
            predictions[column].to_numpy(), recorded[column].to_numpy(), rtol=0, atol=0
        ):
            raise ValueError(f"Keyword validation predictions differ: {column}")
    metrics = conversation_metrics(
        predictions["label"].to_numpy(dtype=np.int8),
        predictions["score"].to_numpy(dtype=np.float64),
        0.5,
    )
    return {
        "status": "validated",
        "training_conversations": int(train["conversation_id"].nunique()),
        "validation_conversations": len(predictions),
        "metrics": metrics,
        "keyword_config_payload_sha256": expected_hash,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-file", type=Path, required=True)
    parser.add_argument("--split-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-terms", type=int, default=50)
    parser.add_argument("--min-positive-conversations", type=int, default=3)
    args = parser.parse_args()
    result = build_keyword_baseline(
        args.data_file,
        args.split_manifest,
        args.output_dir,
        args.max_terms,
        args.min_positive_conversations,
    )
    print(json.dumps(result["validation_metrics"], indent=2))


if __name__ == "__main__":
    main()
