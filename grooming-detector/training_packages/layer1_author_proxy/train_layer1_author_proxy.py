"""Train the revised Layer 1 author-proxy classifier on a locked PAN12 split.

The script intentionally never loads `is_suspicious`, never scores the locked
final test, and never writes message text to its artifacts.  It trains on the
official author-level `is_predator` target and evaluates only the validation
partition so the downstream pipeline can remain the sole final-test consumer.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import random
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
    set_seed,
)

from build_locked_split import canonical_sha256, load_eligible_rows, sha256_file


PACKAGE_VERSION = "1.0.0"
CONTEXT_TURNS = 2
DEFAULT_MAX_LENGTH = 128


@dataclass(frozen=True)
class HardwareInfo:
    platform: str
    python: str
    torch: str
    cuda_available: bool
    torch_cuda: str | None
    cudnn: int | None
    gpu_count: int
    gpu_names: list[str]
    capabilities: list[list[int]]
    bf16_supported: bool
    tf32_enabled: bool


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(json_ready(value), indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def package_versions() -> dict[str, str | None]:
    packages = [
        "torch",
        "transformers",
        "accelerate",
        "datasets",
        "scikit-learn",
        "numpy",
        "pandas",
        "safetensors",
    ]
    versions: dict[str, str | None] = {}
    for package in packages:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def configure_hardware(require_cuda: bool) -> HardwareInfo:
    cuda_available = torch.cuda.is_available()
    if require_cuda and not cuda_available:
        raise RuntimeError(
            "CUDA is required for this handoff run, but PyTorch cannot see an NVIDIA GPU. "
            "Run setup_cuda.ps1, update the NVIDIA driver if needed, and rerun verify_package.ps1."
        )
    if cuda_available:
        torch.cuda.empty_cache()
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.set_float32_matmul_precision("high")
    gpu_names = [
        torch.cuda.get_device_name(index) for index in range(torch.cuda.device_count())
    ]
    capabilities = [
        list(torch.cuda.get_device_capability(index))
        for index in range(torch.cuda.device_count())
    ]
    bf16_supported = bool(
        cuda_available
        and hasattr(torch.cuda, "is_bf16_supported")
        and torch.cuda.is_bf16_supported()
    )
    tf32_enabled = bool(
        cuda_available and any(major >= 8 for major, _minor in capabilities)
    )
    return HardwareInfo(
        platform=platform.platform(),
        python=platform.python_version(),
        torch=torch.__version__,
        cuda_available=cuda_available,
        torch_cuda=torch.version.cuda,
        cudnn=torch.backends.cudnn.version() if cuda_available else None,
        gpu_count=torch.cuda.device_count(),
        gpu_names=gpu_names,
        capabilities=capabilities,
        bf16_supported=bf16_supported,
        tf32_enabled=tf32_enabled,
    )


def load_and_verify_manifest(path: Path, data_file: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    integrity = manifest.get("integrity", {})
    payload = copy.deepcopy(manifest)
    payload.pop("integrity", None)
    actual_payload_hash = canonical_sha256(payload)
    expected_payload_hash = integrity.get("canonical_payload_sha256")
    if actual_payload_hash != expected_payload_hash:
        raise ValueError(
            "Locked split manifest integrity check failed: "
            f"expected {expected_payload_hash}, got {actual_payload_hash}"
        )
    actual_data_hash = sha256_file(data_file)
    expected_data_hash = manifest["dataset"]["sha256"]
    if actual_data_hash != expected_data_hash:
        raise ValueError(
            "Wrong PAN12 CSV. The package is locked to SHA-256 "
            f"{expected_data_hash}, but {data_file} is {actual_data_hash}."
        )
    if data_file.stat().st_size != int(manifest["dataset"]["bytes"]):
        raise ValueError("Dataset byte count does not match the locked manifest")
    return manifest


def attach_locked_splits(
    frame: pd.DataFrame,
    manifest: dict[str, Any],
) -> pd.DataFrame:
    assignment: dict[str, str] = {}
    for split_name, row in manifest["splits"].items():
        for conversation_id in row["conversation_ids"]:
            if conversation_id in assignment:
                raise ValueError(f"Conversation assigned twice: {conversation_id}")
            assignment[conversation_id] = split_name
    frame_ids = set(frame["conversation_id"].unique())
    if frame_ids != set(assignment):
        raise ValueError("Dataset conversations do not exactly match the locked manifest")
    result = frame.copy()
    result["split"] = result["conversation_id"].map(assignment)

    for split_name, expected in manifest["splits"].items():
        selected = result[result["split"] == split_name]
        conversation_labels = (
            selected.groupby("conversation_id")["author_is_predator"].max()
        )
        actual = {
            "conversations": int(selected["conversation_id"].nunique()),
            "rows": int(len(selected)),
            "positive_conversations": int(conversation_labels.sum()),
            "positive_author_rows": int(selected["author_is_predator"].sum()),
            "authors": int(selected["author_id"].nunique()),
        }
        for key, value in actual.items():
            if value != int(expected[key]):
                raise ValueError(
                    f"Locked split statistic mismatch for {split_name}.{key}: "
                    f"expected {expected[key]}, got {value}"
                )
    return result


def build_prefix_contexts(
    frame: pd.DataFrame,
    split_name: str,
    context_turns: int = CONTEXT_TURNS,
) -> pd.DataFrame:
    """Construct prefix-only model text without copying author IDs into text."""
    selected = frame[frame["split"] == split_name].copy()
    rows: list[dict[str, Any]] = []
    for conversation_id, conversation in selected.groupby(
        "conversation_id", sort=True
    ):
        conversation = conversation.sort_values("line", kind="stable")
        messages = conversation["text"].astype(str).str.strip().tolist()
        lines = conversation["line"].astype(int).tolist()
        labels = conversation["author_is_predator"].astype(int).tolist()
        for index, (line, label) in enumerate(zip(lines, labels)):
            first = max(0, index - context_turns)
            context = " [SEP] ".join(messages[first : index + 1])
            rows.append(
                {
                    "row_id": f"{conversation_id}:{line}",
                    "conversation_id": conversation_id,
                    "line": line,
                    "text": context,
                    "label": label,
                }
            )
    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError(f"No rows were constructed for split {split_name}")
    if result["row_id"].duplicated().any():
        raise ValueError(f"Duplicate stable row IDs detected in {split_name}")
    return result


def downsample_training_negatives(
    train_rows: pd.DataFrame,
    negative_ratio: float,
    seed: int,
) -> pd.DataFrame:
    positives = train_rows[train_rows["label"] == 1]
    negatives = train_rows[train_rows["label"] == 0]
    if positives.empty or negatives.empty:
        raise ValueError("Training requires both author-label classes")
    if negative_ratio <= 0:
        sampled_negatives = negatives
    else:
        requested = max(1, int(round(len(positives) * negative_ratio)))
        sampled_negatives = negatives.sample(
            n=min(len(negatives), requested),
            random_state=seed,
            replace=False,
        )
    combined = pd.concat([positives, sampled_negatives], ignore_index=True)
    return combined.sample(frac=1.0, random_state=seed).reset_index(drop=True)


def positive_probabilities(logits: Any) -> np.ndarray:
    if isinstance(logits, tuple):
        logits = logits[0]
    values = np.asarray(logits, dtype=np.float64)
    values -= values.max(axis=1, keepdims=True)
    exponentials = np.exp(values)
    return exponentials[:, 1] / exponentials.sum(axis=1)


def metrics_at_threshold(
    labels: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, Any]:
    predictions = (probabilities >= threshold).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(labels, predictions, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
        "f0_5": fbeta_score(labels, predictions, beta=0.5, zero_division=0),
        "pr_auc": average_precision_score(labels, probabilities),
        "roc_auc": roc_auc_score(labels, probabilities),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def select_f05_threshold(
    labels: np.ndarray,
    probabilities: np.ndarray,
) -> tuple[float, dict[str, Any]]:
    precision, recall, thresholds = precision_recall_curve(labels, probabilities)
    if len(thresholds) == 0:
        raise ValueError("Validation predictions do not support threshold selection")
    candidates: list[tuple[float, float, float, float]] = []
    for index, threshold in enumerate(thresholds):
        p = float(precision[index])
        r = float(recall[index])
        denominator = 0.25 * p + r
        f05 = 0.0 if denominator == 0 else 1.25 * p * r / denominator
        candidates.append((f05, r, p, float(threshold)))
    _f05, _recall, _precision, selected = max(
        candidates,
        key=lambda row: (row[0], row[1], row[2], row[3]),
    )
    return selected, metrics_at_threshold(labels, probabilities, selected)


def trainer_metrics(prediction: Any) -> dict[str, float]:
    probabilities = positive_probabilities(prediction.predictions)
    labels = np.asarray(prediction.label_ids, dtype=np.int8)
    result = metrics_at_threshold(labels, probabilities, 0.5)
    return {
        "accuracy": float(result["accuracy"]),
        "precision_at_0_5": float(result["precision"]),
        "recall_at_0_5": float(result["recall"]),
        "f1_at_0_5": float(result["f1"]),
        "f0_5_at_0_5": float(result["f0_5"]),
        "pr_auc": float(result["pr_auc"]),
        "roc_auc": float(result["roc_auc"]),
    }


def tree_sha256(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    return digest.hexdigest()


def parse_args() -> argparse.Namespace:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-file", type=Path, required=True)
    parser.add_argument(
        "--split-manifest",
        type=Path,
        default=here / "locked_split_manifest.json",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-name", default="distilbert-base-uncased")
    parser.add_argument("--max-length", type=int, default=DEFAULT_MAX_LENGTH)
    parser.add_argument("--negative-ratio", type=float, default=3.0)
    parser.add_argument("--epochs", type=float, default=5.0)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=0.01)
    parser.add_argument("--warmup-ratio", type=float, default=0.10)
    parser.add_argument("--train-batch-size", type=int, default=64)
    parser.add_argument("--eval-batch-size", type=int, default=128)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--gradient-clip", type=float, default=1.0)
    parser.add_argument("--early-stopping-patience", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dataloader-workers",
        type=int,
        default=0 if sys.platform.startswith("win") else min(8, max(0, (os.cpu_count() or 2) - 1)),
    )
    parser.add_argument("--preprocessing-workers", type=int, default=1)
    parser.add_argument(
        "--require-cuda",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--auto-find-batch-size",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument(
        "--local-files-only",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate data/split and build train/validation rows without loading a model.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data_file = args.data_file.resolve()
    split_manifest = args.split_manifest.resolve()
    output_dir = args.output_dir.resolve()
    if not data_file.is_file():
        raise FileNotFoundError(data_file)
    if not split_manifest.is_file():
        raise FileNotFoundError(split_manifest)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"Output directory is not empty: {output_dir}. Use a new run directory."
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    set_seed(args.seed)

    manifest = load_and_verify_manifest(split_manifest, data_file)
    frame = attach_locked_splits(load_eligible_rows(data_file), manifest)
    train_full = build_prefix_contexts(frame, "train")
    validation_rows = build_prefix_contexts(frame, "validation")
    train_rows = downsample_training_negatives(
        train_full,
        negative_ratio=args.negative_ratio,
        seed=args.seed,
    )

    hardware = configure_hardware(require_cuda=args.require_cuda and not args.dry_run)
    configuration = {
        "package_version": PACKAGE_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv,
        "arguments": vars(args),
        "data_sha256": manifest["dataset"]["sha256"],
        "split_manifest_payload_sha256": manifest["integrity"][
            "canonical_payload_sha256"
        ],
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "hardware": asdict(hardware),
        "packages": package_versions(),
        "methodology_guards": {
            "label": "official is_predator author membership only",
            "is_suspicious_loaded": False,
            "context": "current turn plus up to two preceding turns",
            "author_ids_in_model_text": False,
            "negative_sampling": "training only",
            "validation_distribution_untouched": True,
            "final_test_scored": False,
            "historical_test_scored": False,
        },
        "row_counts": {
            "train_before_negative_sampling": len(train_full),
            "train_after_negative_sampling": len(train_rows),
            "train_positive": int(train_rows["label"].sum()),
            "train_negative": int(len(train_rows) - train_rows["label"].sum()),
            "validation": len(validation_rows),
            "validation_positive": int(validation_rows["label"].sum()),
            "validation_negative": int(
                len(validation_rows) - validation_rows["label"].sum()
            ),
        },
    }
    write_json(output_dir / "run_configuration.json", configuration)
    if args.dry_run:
        write_json(
            output_dir / "dry_run_result.json",
            {
                "status": "passed",
                "note": "No model was loaded and no final-test conversation was scored.",
                "configuration": configuration,
            },
        )
        print(json.dumps(json_ready(configuration["row_counts"]), indent=2))
        print(f"Dry run passed: {output_dir}")
        return

    tokenizer = AutoTokenizer.from_pretrained(
        args.model_name,
        use_fast=True,
        local_files_only=args.local_files_only,
    )

    def tokenize(batch: dict[str, list[Any]]) -> dict[str, Any]:
        return tokenizer(
            batch["text"],
            truncation=True,
            max_length=args.max_length,
        )

    train_dataset = Dataset.from_pandas(
        train_rows[["text", "label"]],
        preserve_index=False,
    ).map(
        tokenize,
        batched=True,
        num_proc=args.preprocessing_workers,
        remove_columns=["text"],
        desc="Tokenizing training contexts",
    )
    validation_dataset = Dataset.from_pandas(
        validation_rows[["text", "label"]],
        preserve_index=False,
    ).map(
        tokenize,
        batched=True,
        num_proc=args.preprocessing_workers,
        remove_columns=["text"],
        desc="Tokenizing validation contexts",
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        args.model_name,
        num_labels=2,
        id2label={0: "NOT_LISTED_PREDATOR_AUTHOR", 1: "LISTED_PREDATOR_AUTHOR"},
        label2id={"NOT_LISTED_PREDATOR_AUTHOR": 0, "LISTED_PREDATOR_AUTHOR": 1},
        local_files_only=args.local_files_only,
    )

    use_cuda = hardware.cuda_available
    training_args = TrainingArguments(
        output_dir=str(output_dir / "checkpoints"),
        overwrite_output_dir=False,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        max_grad_norm=args.gradient_clip,
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="steps",
        logging_steps=50,
        load_best_model_at_end=True,
        metric_for_best_model="pr_auc",
        greater_is_better=True,
        save_total_limit=2,
        seed=args.seed,
        data_seed=args.seed,
        bf16=bool(use_cuda and hardware.bf16_supported),
        fp16=bool(use_cuda and not hardware.bf16_supported),
        tf32=bool(use_cuda and hardware.tf32_enabled),
        optim="adamw_torch_fused" if use_cuda else "adamw_torch",
        auto_find_batch_size=args.auto_find_batch_size,
        dataloader_num_workers=args.dataloader_workers,
        dataloader_pin_memory=use_cuda,
        dataloader_persistent_workers=args.dataloader_workers > 0,
        group_by_length=True,
        eval_accumulation_steps=16,
        report_to="none",
        use_cpu=not use_cuda,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(
            tokenizer=tokenizer,
            pad_to_multiple_of=8 if use_cuda else None,
        ),
        compute_metrics=trainer_metrics,
        callbacks=[
            EarlyStoppingCallback(
                early_stopping_patience=args.early_stopping_patience
            )
        ],
    )
    train_result = trainer.train()

    best_model_dir = output_dir / "best_model"
    trainer.save_model(str(best_model_dir))
    tokenizer.save_pretrained(str(best_model_dir))

    # Evaluate validation rows sequentially to guarantee exact row-ID alignment
    model.eval()
    val_contexts = validation_rows["text"].tolist()
    val_probs: list[float] = []
    eval_batch = max(1, args.eval_batch_size)
    use_device = torch.device("cuda" if use_cuda else "cpu")
    with torch.inference_mode():
        for start in range(0, len(val_contexts), eval_batch):
            batch_texts = val_contexts[start : start + eval_batch]
            encoded = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=args.max_length,
                return_tensors="pt",
            )
            encoded = {k: v.to(use_device) for k, v in encoded.items()}
            encoded.pop("token_type_ids", None)
            logits = model(**encoded).logits
            probs = torch.softmax(logits.float(), dim=-1)[:, 1]
            val_probs.extend(probs.cpu().numpy().tolist())

    probabilities = np.array(val_probs, dtype=np.float64)
    labels = validation_rows["label"].to_numpy(dtype=np.int8)
    threshold, validation_metrics = select_f05_threshold(labels, probabilities)
    eval_at_05 = metrics_at_threshold(labels, probabilities, 0.5)

    prediction_output = validation_rows[
        ["row_id", "conversation_id", "line", "label"]
    ].copy()
    prediction_output["probability"] = probabilities
    prediction_output["prediction"] = (probabilities >= threshold).astype(np.int8)
    prediction_output.to_csv(output_dir / "validation_predictions.csv", index=False)
    write_json(
        output_dir / "selected_threshold.json",
        {
            "selection_partition": "validation",
            "objective": "maximum F0.5",
            "threshold": threshold,
            "metrics": validation_metrics,
        },
    )
    write_json(
        output_dir / "run_summary.json",
        {
            "status": "completed",
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "best_checkpoint": trainer.state.best_model_checkpoint,
            "best_validation_pr_auc": trainer.state.best_metric,
            "train_metrics": train_result.metrics,
            "prediction_metrics": {
                "validation_accuracy": eval_at_05["accuracy"],
                "validation_precision_at_0_5": eval_at_05["precision"],
                "validation_recall_at_0_5": eval_at_05["recall"],
                "validation_f1_at_0_5": eval_at_05["f1"],
                "validation_f0_5_at_0_5": eval_at_05["f0_5"],
                "validation_pr_auc": eval_at_05["pr_auc"],
                "validation_roc_auc": eval_at_05["roc_auc"],
            },
            "selected_threshold": threshold,
            "validation_metrics_at_selected_threshold": validation_metrics,
            "best_model_tree_sha256": tree_sha256(best_model_dir),
            "final_test_scored": False,
            "historical_test_scored": False,
            "next_step": (
                "Use best_model and selected_threshold only after generating a stable-ID "
                "Layer 1 cache; keep final_test unscored until the downstream protocol is frozen."
            ),
        },
    )
    print(json.dumps(json_ready(validation_metrics), indent=2))
    print(f"Training complete: {output_dir}")


if __name__ == "__main__":
    main()
