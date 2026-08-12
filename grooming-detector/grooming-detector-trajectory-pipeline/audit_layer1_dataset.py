"""Audit Layer 1 label provenance and build a deterministic source manifest.

This script deliberately refuses to approve training rows when their labels are
derived from PAN correction metadata or synthetic speaker roles. Its outputs
are an evidence manifest and a blank human-review worksheet, not a training
dataset.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "text",
    "author",
    "line",
    "is_predator",
    "is_suspicious",
}
SPLITS = ("train", "validation", "test")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def relative_path(path: Path, workspace: Path) -> str:
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def conversation_column(frame: pd.DataFrame) -> str:
    if "conv_id" in frame.columns:
        return "conv_id"
    if "convo_id" in frame.columns:
        return "convo_id"
    raise ValueError("Dataset needs either conv_id or convo_id")


def read_source(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
    conversation_column(frame)
    return frame


def label_counts(series: pd.Series) -> dict[str, int]:
    numeric = pd.to_numeric(series, errors="coerce")
    return {
        "0": int((numeric == 0).sum()),
        "1": int((numeric == 1).sum()),
        "invalid_or_missing": int((~numeric.isin([0, 1])).sum()),
    }


def summarize_frame(frame: pd.DataFrame) -> dict:
    conv = conversation_column(frame)
    texts = frame["text"].fillna("").astype(str).str.strip()
    conversation_sizes = frame.groupby(conv).size()
    return {
        "rows": int(len(frame)),
        "conversations": int(frame[conv].nunique(dropna=True)),
        "authors": int(frame["author"].nunique(dropna=True)),
        "blank_text_rows": int((texts == "").sum()),
        "duplicate_exact_text_rows_after_first": int(texts.duplicated().sum()),
        "duplicate_conversation_line_rows_after_first": int(
            frame.duplicated([conv, "line"]).sum()
        ),
        "messages_per_conversation": {
            "minimum": int(conversation_sizes.min()),
            "median": float(conversation_sizes.median()),
            "maximum": int(conversation_sizes.max()),
        },
        "is_predator": label_counts(frame["is_predator"]),
        "is_suspicious": label_counts(frame["is_suspicious"]),
        "predator_suspicious_disagreements": int(
            (
                pd.to_numeric(frame["is_predator"], errors="coerce")
                != pd.to_numeric(frame["is_suspicious"], errors="coerce")
            ).sum()
        ),
    }


def parse_generator(path: Path, list_name: str) -> dict:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    assignments = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        try:
            assignments[target.id] = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue

    prompts = assignments.get(list_name, [])
    temperature_values = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            try:
                literal_key = ast.literal_eval(key)
                literal_value = ast.literal_eval(value)
            except (ValueError, TypeError):
                continue
            if literal_key == "temperature":
                temperature_values.append(literal_value)
    return {
        "sha256": sha256_file(path),
        "declared_model_name": assignments.get("MODEL_NAME"),
        "declared_temperature_values": temperature_values,
        "requested_conversations_per_category": assignments.get(
            "NUM_EXAMPLES_PER_TACTIC",
            assignments.get("NUM_EXAMPLES_PER_SCENARIO"),
        ),
        "categories": [item.get("name") for item in prompts],
        "prompt_sha256": [
            hashlib.sha256(item.get("prompt", "").encode("utf-8")).hexdigest().upper()
            for item in prompts
        ],
        "model_version_or_digest_recorded": False,
        "random_seed_recorded": False,
        "raw_model_responses_retained": False,
        "human_annotation_recorded": False,
    }


def author_label_map(frame: pd.DataFrame) -> dict[str, list[int]]:
    labels = pd.to_numeric(frame["is_suspicious"], errors="coerce")
    result = {}
    for author, indices in frame.groupby("author", dropna=False).groups.items():
        result[str(author)] = sorted(
            int(value) for value in labels.loc[indices].dropna().unique()
        )
    return result


def synthetic_source(
    name: str,
    path: Path,
    generator_path: Path,
    generator_list_name: str,
    workspace: Path,
) -> tuple[dict, pd.DataFrame]:
    frame = read_source(path)
    conv = conversation_column(frame)
    generator = parse_generator(generator_path, generator_list_name)
    predator = pd.to_numeric(frame["is_predator"], errors="coerce")
    suspicious = pd.to_numeric(frame["is_suspicious"], errors="coerce")
    author_map = author_label_map(frame)
    global_placeholder_authors = sorted(str(value) for value in frame["author"].unique())
    requested_total = (
        len(generator["categories"])
        * int(generator["requested_conversations_per_category"] or 0)
    )
    adjacent_same_author = 0
    for _, conversation in frame.groupby(conv, sort=False):
        adjacent_same_author += int(
            (conversation["author"].shift() == conversation["author"]).fillna(False).sum()
        )

    if name == "synthetic_grooming":
        decision = "EXCLUDE_PENDING_INDEPENDENT_MESSAGE_ANNOTATION"
        label_method = (
            "Generator code copies the parsed speaker-role flag directly into "
            "both is_predator and is_suspicious."
        )
        issues = [
            "Every generated predator-role utterance is positive, including ordinary setup talk.",
            "The target is perfectly confounded with speaker role.",
            "No independent message-level annotation or adjudication is recorded.",
        ]
    else:
        decision = "EXCLUDE_PENDING_INDEPENDENT_MESSAGE_VALIDATION"
        label_method = "Generator code assigns zero to every generated message."
        issues = [
            "Safety is inherited from the prompt scenario rather than independently annotated.",
            "No human validation or hard-negative adjudication is recorded.",
        ]

    issues.extend(
        [
            "The local model name is recorded without a model digest/version.",
            "No generation seed or raw response archive is recorded.",
            "Placeholder author IDs are reused across unrelated generated conversations.",
        ]
    )
    return (
        {
            "path": relative_path(path, workspace),
            "sha256": sha256_file(path),
            "summary": summarize_frame(frame),
            "generator": {
                "path": relative_path(generator_path, workspace),
                **generator,
            },
            "label_provenance": label_method,
            "diagnostics": {
                "suspicious_equals_predator_for_every_row": bool(
                    (predator == suspicious).all()
                ),
                "suspicious_labels_by_placeholder_author": author_map,
                "global_placeholder_authors": global_placeholder_authors,
                "placeholder_authors_reused_across_conversations": bool(
                    frame.groupby("author")[conv].nunique().gt(1).any()
                ),
                "requested_conversations": requested_total,
                "observed_nonempty_conversations": int(frame[conv].nunique()),
                "generation_shortfall": int(requested_total - frame[conv].nunique()),
                "adjacent_same_author_pairs": adjacent_same_author,
            },
            "decision": decision,
            "issues": issues,
            "required_remediation": [
                "Have reviewers label each message for observable grooming behavior using a written rubric.",
                "Keep generated/proposed labels separate from reviewed labels.",
                "Record annotator IDs, disagreements, adjudication, and inclusion decisions.",
                "Treat placeholder identities as conversation-local after confirming conversations are independent generations.",
            ],
        },
        frame,
    )


def normalized_pan_equality(first: pd.DataFrame, second: pd.DataFrame) -> dict:
    if list(first.columns) != list(second.columns) or first.shape != second.shape:
        return {"same_shape_and_columns": False, "equal_after_line_ending_normalization": False}
    different_by_column = {}
    for column in first.columns:
        left = first[column].fillna("__NA__").astype(str)
        right = second[column].fillna("__NA__").astype(str)
        different_by_column[column] = int((left != right).sum())
        if column == "text":
            left = left.str.replace("\r\n", "\n", regex=False).str.replace("\r", "\n", regex=False)
            right = right.str.replace("\r\n", "\n", regex=False).str.replace("\r", "\n", regex=False)
        if not left.equals(right):
            return {
                "same_shape_and_columns": True,
                "raw_different_rows_by_column": different_by_column,
                "equal_after_line_ending_normalization": False,
            }
    return {
        "same_shape_and_columns": True,
        "raw_different_rows_by_column": different_by_column,
        "equal_after_line_ending_normalization": True,
    }


def pan_sources(
    active_path: Path,
    archive_path: Path,
    split_audit_path: Path,
    preprocessor_path: Path,
    readme_path: Path,
    workspace: Path,
) -> dict:
    active = read_source(active_path)
    archived = read_source(archive_path)
    conv = conversation_column(active)
    split_audit = json.loads(split_audit_path.read_text(encoding="utf-8"))
    assignments = split_audit["assignments"]
    assigned_split = active[conv].astype(str).map(
        lambda value: assignments.get(f"pan12:{value}", {}).get("split")
    )
    row_counts = {
        split: int((assigned_split == split).sum()) for split in SPLITS
    }
    row_counts["unassigned_non_dyadic_or_filtered"] = int(assigned_split.isna().sum())
    assigned_conversations = sum(
        f"pan12:{value}" in assignments for value in active[conv].astype(str).unique()
    )

    return {
        "active": {
            "path": relative_path(active_path, workspace),
            "sha256": sha256_file(active_path),
            "summary": summarize_frame(active),
        },
        "archived_latest_layer1_bundle_copy": {
            "path": relative_path(archive_path, workspace),
            "sha256": sha256_file(archive_path),
            "summary": summarize_frame(archived),
        },
        "copy_comparison": normalized_pan_equality(active, archived),
        "label_provenance": {
            "is_predator": "PAN-provided predator-author membership repeated on that author's message rows.",
            "is_suspicious": "Project-derived membership in PAN's modified-text diff file; not a grooming annotation.",
            "preprocessor_path": relative_path(preprocessor_path, workspace),
            "preprocessor_sha256": sha256_file(preprocessor_path),
            "corpus_readme_path": relative_path(readme_path, workspace),
            "corpus_readme_sha256": sha256_file(readme_path),
        },
        "frozen_split": {
            "path": relative_path(split_audit_path, workspace),
            "sha256": sha256_file(split_audit_path),
            "protocol": split_audit["protocol"],
            "invariants": split_audit["invariants"],
            "assigned_conversations": int(assigned_conversations),
            "unassigned_conversations": int(active[conv].nunique() - assigned_conversations),
            "source_rows_by_assignment": row_counts,
        },
        "decision_for_message_level_layer1": "EXCLUDE",
        "decision_for_weak_author_supervision": "OPTIONAL_TRAIN_SPLIT_ONLY_WITH_EXPLICIT_WEAK_SUPERVISION_CLAIM",
        "hard_rule": "No PAN validation/test conversation may enter Layer 1 fitting or checkpoint selection.",
    }


def annotation_rows(name: str, path: Path, frame: pd.DataFrame) -> pd.DataFrame:
    conv = conversation_column(frame)
    source_sha = sha256_file(path)
    ordered = frame.reset_index(names="source_row_index").sort_values(
        [conv, "line", "source_row_index"]
    )
    grouped_text = ordered.groupby(conv, sort=False)["text"]
    previous_two = pd.concat(
        [grouped_text.shift(2).fillna(""), grouped_text.shift(1).fillna("")],
        axis=1,
    )
    ordered["preceding_context_2"] = previous_two.apply(
        lambda values: " [SEP] ".join(str(value) for value in values if str(value)),
        axis=1,
    )
    records = []
    for _, row in ordered.iterrows():
        row_index = int(row["source_row_index"])
        identity = "\x1f".join(
            [
                source_sha,
                str(row_index),
                str(row[conv]),
                str(row["line"]),
                str(row["author"]),
                str(row["text"]),
            ]
        )
        records.append(
            {
                "source": name,
                "source_row_index": row_index,
                "row_id": hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24],
                "conversation_id": f"{name}:{row[conv]}",
                "conversation_local_author": f"{name}:{row[conv]}:{row['author']}",
                "line": row["line"],
                "preceding_context_2": row["preceding_context_2"],
                "text": row["text"],
                "generated_is_suspicious": row["is_suspicious"],
                "reviewer_1_label": "",
                "reviewer_1_id": "",
                "reviewer_1_notes": "",
                "reviewer_2_label": "",
                "reviewer_2_id": "",
                "reviewer_2_notes": "",
                "adjudicated_message_label": "",
                "adjudicator_id": "",
                "include_for_training": "",
                "exclusion_reason": "",
            }
        )
    return pd.DataFrame.from_records(records)


def build_manifest(args: argparse.Namespace) -> tuple[dict, pd.DataFrame]:
    workspace = args.workspace.resolve()
    grooming_report, grooming_frame = synthetic_source(
        "synthetic_grooming",
        args.synthetic_grooming,
        args.grooming_generator,
        "tactics",
        workspace,
    )
    safe_report, safe_frame = synthetic_source(
        "synthetic_safe",
        args.synthetic_safe,
        args.safe_generator,
        "scenarios",
        workspace,
    )
    grooming_text = set(grooming_frame["text"].astype(str).str.strip().str.casefold())
    safe_text = set(safe_frame["text"].astype(str).str.strip().str.casefold())

    worksheet = pd.concat(
        [
            annotation_rows("synthetic_grooming", args.synthetic_grooming, grooming_frame),
            annotation_rows("synthetic_safe", args.synthetic_safe, safe_frame),
        ],
        ignore_index=True,
    )
    worksheet_csv = worksheet.to_csv(index=False, lineterminator="\n")
    manifest = {
        "schema_version": 1,
        "purpose": "Audit candidate sources for a genuine binary message-level grooming Layer 1 target.",
        "target_definition": {
            "unit": "message with preceding context",
            "positive": "The current message contains observable grooming-related behavior under a written annotation rubric.",
            "negative": "The current message does not contain observable grooming-related behavior under that rubric.",
            "forbidden_proxies": [
                "PAN modified-text diff membership",
                "speaker is a PAN-listed predator",
                "speaker role emitted by a synthetic prompt",
                "synthetic scenario membership without message review",
            ],
        },
        "training_gate": {
            "status": "BLOCKED_NO_INDEPENDENTLY_ANNOTATED_MESSAGE_ROWS",
            "approved_training_rows": 0,
            "approved_validation_rows": 0,
            "approved_test_rows": 0,
            "rule": "Do not retrain Layer 1 from these labels until the review worksheet is completed and adjudicated.",
        },
        "sources": {
            "synthetic_grooming": grooming_report,
            "synthetic_safe": safe_report,
            "pan12": pan_sources(
                args.pan_active,
                args.pan_archive,
                args.split_audit,
                args.pan_preprocessor,
                args.pan_readme,
                workspace,
            ),
        },
        "cross_source_diagnostics": {
            "normalized_exact_text_overlap_between_synthetic_files": len(
                grooming_text & safe_text
            ),
            "annotation_candidate_rows": int(len(worksheet)),
        },
        "annotation_worksheet": {
            "path": relative_path(args.worksheet, workspace),
            "sha256": hashlib.sha256(worksheet_csv.encode("utf-8")).hexdigest().upper(),
            "rows": int(len(worksheet)),
            "review_fields_are_blank": True,
            "review_protocol": relative_path(
                args.synthetic_grooming.parent.parent / "README.md", workspace
            ),
        },
        "required_next_gate": [
            "Approve a written message-level annotation rubric.",
            "Complete at least two independent reviews of the candidate worksheet.",
            "Adjudicate disagreements and freeze reviewed row labels.",
            "Assign reviewed synthetic conversations to deterministic conversation-level partitions.",
            "Use PAN only under its frozen author-disjoint assignments and never use its validation/test rows for fitting.",
        ],
    }
    return manifest, worksheet


def default_paths() -> dict[str, Path]:
    pipeline = Path(__file__).resolve().parent
    project = pipeline.parent
    workspace = project.parent
    corpus = (
        workspace
        / "Groomer Thesis"
        / "pan12-sexual-predator-identification-training-corpus-2012-05-01"
    )
    return {
        "workspace": workspace,
        "synthetic_grooming": project / "data_sources" / "synthetic" / "synthetic_grooming_data.csv",
        "synthetic_safe": project / "data_sources" / "synthetic" / "synthetic_safe_data.csv",
        "grooming_generator": corpus / "generate_synthetic_data.py",
        "safe_generator": corpus / "generate_safe_data.py",
        "pan_active": project / "trained_model_distillbert" / "pan12_final_dataset.csv",
        "pan_archive": project / "data_sources" / "layer1_training_archive" / "pan12_final_dataset.csv",
        "pan_preprocessor": project / "trained_model_distillbert" / "Python.py",
        "pan_readme": project / "trained_model_distillbert" / "readme.txt",
        "split_audit": pipeline / "author_disjoint_split_audit.json",
        "output": project / "data_sources" / "layer1_dataset_manifest.json",
        "worksheet": project / "data_sources" / "layer1_annotation_candidates.csv",
    }


def parse_args() -> argparse.Namespace:
    defaults = default_paths()
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default in defaults.items():
        parser.add_argument(f"--{name.replace('_', '-')}", type=Path, default=default)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest, worksheet = build_manifest(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    worksheet_csv = worksheet.to_csv(index=False, lineterminator="\n")
    args.worksheet.write_text(worksheet_csv, encoding="utf-8", newline="")
    print(f"Saved manifest: {args.output.resolve()}")
    print(f"Saved review worksheet: {args.worksheet.resolve()}")
    print(json.dumps(manifest["training_gate"], indent=2))


if __name__ == "__main__":
    main()
