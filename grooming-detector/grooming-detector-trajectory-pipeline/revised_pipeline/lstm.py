"""Conversation-only LSTM training for the revised trajectory experiment."""

from __future__ import annotations

import argparse
import copy
import json
import math
import platform
import random
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from .contracts import canonical_sha256, sha256_file, write_json
from .dataset import ConversationSequence, load_conversation_sequences
from .metrics import conversation_metrics, select_f05_threshold


InputMode = Literal["trajectory7", "enhanced775"]
LSTM_SOURCE_FILES = (
    "cache.py",
    "centroid.py",
    "contracts.py",
    "data.py",
    "dataset.py",
    "features.py",
    "lstm.py",
    "lstm_search.py",
    "metrics.py",
)


@dataclass(frozen=True)
class LSTMConfig:
    input_mode: InputMode = "trajectory7"
    hidden_dim: int = 256
    num_layers: int = 2
    dropout: float = 0.30
    epochs: int = 20
    batch_size: int = 32
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    gradient_clip: float = 1.0
    early_stopping_patience: int = 4
    seed: int = 42


def _require_torch() -> Any:
    import torch

    return torch


class ConversationOnlyLSTM:
    """Factory wrapper so importing pure helpers does not require torch."""

    @staticmethod
    def build(config: LSTMConfig) -> Any:
        torch = _require_torch()
        nn = torch.nn
        input_dim = 7 if config.input_mode == "trajectory7" else 775

        class _Model(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.input_dim = input_dim
                self.lstm = nn.LSTM(
                    input_size=input_dim,
                    hidden_size=config.hidden_dim,
                    num_layers=config.num_layers,
                    batch_first=True,
                    dropout=config.dropout if config.num_layers > 1 else 0.0,
                )
                self.dropout = nn.Dropout(config.dropout)
                self.output = nn.Linear(config.hidden_dim, 1)

            def forward(self, values: Any, lengths: Any) -> tuple[Any, Any]:
                packed = nn.utils.rnn.pack_padded_sequence(
                    values,
                    lengths.detach().cpu(),
                    batch_first=True,
                    enforce_sorted=False,
                )
                packed_output, _state = self.lstm(packed)
                padded, _ = nn.utils.rnn.pad_packed_sequence(
                    packed_output,
                    batch_first=True,
                    total_length=values.shape[1],
                )
                turn_logits = self.output(self.dropout(padded)).squeeze(-1)
                gather_index = (lengths - 1).view(-1, 1)
                final_logits = turn_logits.gather(1, gather_index).squeeze(1)
                return turn_logits, final_logits

        return _Model()


class _SequenceDataset:
    def __init__(self, sequences: list[ConversationSequence], mode: InputMode):
        self.sequences = sequences
        self.mode = mode

    def __len__(self) -> int:
        return len(self.sequences)

    def __getitem__(self, index: int) -> tuple[np.ndarray, int, str]:
        sequence = self.sequences[index]
        if self.mode == "trajectory7":
            values = sequence.trajectory_features
        elif self.mode == "enhanced775":
            values = np.concatenate(
                [sequence.embeddings, sequence.trajectory_features], axis=1
            )
        else:
            raise ValueError(f"Unknown input mode: {self.mode}")
        return values.astype(np.float32, copy=False), sequence.label, sequence.conversation_id


class _LengthBucketBatchSampler:
    """Shuffle batches while grouping similar lengths to avoid padding blow-ups."""

    def __init__(
        self,
        dataset: _SequenceDataset,
        batch_size: int,
        seed: int,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.lengths = np.asarray(
            [len(sequence.trajectory_features) for sequence in dataset.sequences],
            dtype=np.int64,
        )
        self.batch_size = int(batch_size)
        self.seed = int(seed)
        self.epoch = 0

    def __len__(self) -> int:
        return int(math.ceil(len(self.lengths) / self.batch_size))

    def __iter__(self):
        rng = np.random.default_rng(self.seed + self.epoch)
        self.epoch += 1
        # Random tie-breaks keep equal-length conversations from retaining a
        # fixed order; the stable length sort still creates compact batches.
        random_order = rng.permutation(len(self.lengths))
        sorted_indices = random_order[
            np.argsort(self.lengths[random_order], kind="stable")
        ]
        batches = [
            sorted_indices[start : start + self.batch_size].tolist()
            for start in range(0, len(sorted_indices), self.batch_size)
        ]
        rng.shuffle(batches)
        yield from batches


def _collate(batch: list[tuple[np.ndarray, int, str]]) -> tuple[Any, Any, Any, list[str]]:
    torch = _require_torch()
    values, labels, conversation_ids = zip(*batch)
    lengths = torch.tensor([len(item) for item in values], dtype=torch.long)
    max_length = int(lengths.max())
    input_dim = int(values[0].shape[1])
    padded = torch.zeros((len(values), max_length, input_dim), dtype=torch.float32)
    for index, item in enumerate(values):
        padded[index, : len(item)] = torch.from_numpy(np.asarray(item))
    return (
        padded,
        lengths,
        torch.tensor(labels, dtype=torch.float32),
        list(conversation_ids),
    )


def _predict(model: Any, loader: Any, device: Any) -> tuple[list[str], np.ndarray, np.ndarray]:
    torch = _require_torch()
    model.eval()
    ids: list[str] = []
    labels: list[int] = []
    scores: list[float] = []
    with torch.inference_mode():
        for values, lengths, batch_labels, conversation_ids in loader:
            values = values.to(device)
            lengths = lengths.to(device)
            _turn_logits, final_logits = model(values, lengths)
            batch_scores = torch.sigmoid(final_logits.float()).cpu().numpy()
            ids.extend(conversation_ids)
            labels.extend(batch_labels.numpy().astype(int).tolist())
            scores.extend(batch_scores.tolist())
    return ids, np.asarray(labels, dtype=np.int8), np.asarray(scores, dtype=np.float64)


def _save_checkpoint(path: Path, model: Any, configuration: dict[str, Any]) -> None:
    torch = _require_torch()
    torch.save(
        {
            "schema_version": 1,
            "model_state": {key: value.detach().cpu() for key, value in model.state_dict().items()},
            # Keep the checkpoint weights-only-loadable.  Full provenance is
            # stored in the separately hashed run_configuration.json; only the
            # primitive model-shape fields needed to audit this state dict are
            # duplicated here.
            "model_config": {
                key: value
                for key, value in configuration["config"].items()
                if key
                in {
                    "input_mode",
                    "hidden_dim",
                    "num_layers",
                    "dropout",
                }
            },
        },
        path,
    )


def _runtime_record(torch: Any, device: Any, amp_dtype: Any) -> dict[str, Any]:
    code_dir = Path(__file__).resolve().parent
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=code_dir,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        git_commit = None
    gpu_name = None
    capability = None
    if device.type == "cuda":
        gpu_name = torch.cuda.get_device_name(device)
        capability = list(torch.cuda.get_device_capability(device))
    return {
        "command": sys.argv,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "torch": str(torch.__version__),
        "torch_cuda": (
            str(torch.version.cuda) if torch.version.cuda is not None else None
        ),
        "cudnn": torch.backends.cudnn.version() if torch.cuda.is_available() else None,
        "numpy": np.__version__,
        "device": str(device),
        "gpu_name": gpu_name,
        "gpu_capability": capability,
        "autocast_dtype": str(amp_dtype) if amp_dtype is not None else "disabled",
        "tf32": bool(device.type == "cuda"),
        "deterministic_algorithms_warn_only": True,
        "git_commit": git_commit,
        "source_sha256": {
            name: sha256_file(code_dir / name) for name in LSTM_SOURCE_FILES
        },
    }


def load_lstm_checkpoint(
    run_dir: Path,
    expected_mode: InputMode,
    device_name: str | None = None,
) -> tuple[Any, LSTMConfig, Any]:
    torch = _require_torch()
    configuration = json.loads(
        (run_dir / "run_configuration.json").read_text(encoding="utf-8")
    )
    config = LSTMConfig(**configuration["config"])
    if config.input_mode != expected_mode:
        raise ValueError(
            f"Expected {expected_mode} checkpoint, got {config.input_mode}"
        )
    device = torch.device(device_name or ("cuda" if torch.cuda.is_available() else "cpu"))
    model = ConversationOnlyLSTM.build(config).to(device)
    checkpoint_path = run_dir / "best_model.pt"
    summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    if sha256_file(checkpoint_path) != summary.get("model_sha256"):
        raise ValueError(f"LSTM checkpoint hash mismatch: {run_dir}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    if checkpoint.get("schema_version") != 1:
        raise ValueError(f"Unsupported LSTM checkpoint schema: {checkpoint_path}")
    expected_model_config = {
        "input_mode": config.input_mode,
        "hidden_dim": config.hidden_dim,
        "num_layers": config.num_layers,
        "dropout": config.dropout,
    }
    if checkpoint.get("model_config") != expected_model_config:
        raise ValueError(
            f"LSTM checkpoint architecture does not match run configuration: {run_dir}"
        )
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, config, device


def predict_lstm_sequences(
    sequences: list[ConversationSequence],
    model: Any,
    config: LSTMConfig,
    device: Any,
) -> tuple[list[str], np.ndarray, np.ndarray]:
    from torch.utils.data import DataLoader

    loader = DataLoader(
        _SequenceDataset(sequences, config.input_mode),
        batch_size=config.batch_size,
        shuffle=False,
        collate_fn=_collate,
    )
    return _predict(model, loader, device)


def validate_lstm_run(
    run_dir: Path,
    sequences: list[ConversationSequence],
    expected_mode: InputMode,
    device_name: str | None = None,
) -> dict[str, Any]:
    model, config, device = load_lstm_checkpoint(run_dir, expected_mode, device_name)
    ids, labels, scores = predict_lstm_sequences(sequences, model, config, device)
    threshold_record = json.loads(
        (run_dir / "selected_threshold.json").read_text(encoding="utf-8")
    )
    if threshold_record.get("selection_partition") != "validation":
        raise ValueError("LSTM threshold was not selected on validation")
    if threshold_record.get("objective") != "maximum F0.5":
        raise ValueError("LSTM threshold objective is not maximum validation F0.5")
    configuration = json.loads(
        (run_dir / "run_configuration.json").read_text(encoding="utf-8")
    )
    summary = json.loads((run_dir / "run_summary.json").read_text(encoding="utf-8"))
    if summary.get("configuration_payload_sha256") != canonical_sha256(configuration):
        raise ValueError("LSTM summary does not bind the run configuration")
    threshold, metrics = select_f05_threshold(labels, scores)
    if not np.isclose(
        threshold, float(threshold_record["threshold"]), rtol=0, atol=1e-12
    ):
        raise ValueError("LSTM threshold is not the validation F0.5 optimum")
    if not np.isclose(
        threshold, float(summary.get("selected_threshold", float("nan"))), rtol=0, atol=1e-12
    ):
        raise ValueError("LSTM summary and threshold record disagree")
    recorded = pd.read_csv(run_dir / "validation_predictions.csv")
    if recorded["conversation_id"].astype(str).tolist() != ids:
        raise ValueError("LSTM validation conversation order is wrong")
    if not np.array_equal(recorded["label"].to_numpy(dtype=np.int8), labels):
        raise ValueError("LSTM validation labels are wrong")
    if not np.allclose(
        recorded["score"].to_numpy(dtype=np.float64), scores, rtol=1e-6, atol=1e-7
    ):
        raise ValueError("LSTM validation scores cannot be reproduced")
    expected_predictions = (scores >= threshold).astype(np.int8)
    if not np.array_equal(
        recorded["prediction"].to_numpy(dtype=np.int8), expected_predictions
    ):
        raise ValueError("LSTM validation predictions use a different threshold")
    recorded_summary_metrics = summary.get(
        "validation_metrics_at_selected_threshold", {}
    )
    for key, actual in metrics.items():
        if key not in recorded_summary_metrics:
            raise ValueError(f"LSTM summary omits validation metric: {key}")
        expected = recorded_summary_metrics[key]
        if actual is None:
            if expected is not None:
                raise ValueError(f"LSTM summary validation metric differs: {key}")
        elif isinstance(actual, (float, np.floating)):
            if not np.isclose(float(expected), float(actual), rtol=1e-9, atol=1e-9):
                raise ValueError(f"LSTM summary validation metric differs: {key}")
        elif int(expected) != int(actual):
            raise ValueError(f"LSTM summary validation metric differs: {key}")
    if not np.isclose(
        float(summary.get("best_validation_pr_auc", float("nan"))),
        float(metrics["pr_auc"] or 0.0),
        rtol=1e-9,
        atol=1e-9,
    ):
        raise ValueError("LSTM summary PR-AUC differs from reproduced validation")
    return {
        "status": "validated",
        "input_mode": expected_mode,
        "validation_conversations": len(ids),
        "threshold": threshold,
        "metrics": metrics,
    }


def train_lstm(
    train_sequences: list[ConversationSequence],
    validation_sequences: list[ConversationSequence],
    output_dir: Path,
    config: LSTMConfig,
    provenance: dict[str, Any],
    device_name: str | None = None,
) -> dict[str, Any]:
    torch = _require_torch()
    from torch.utils.data import DataLoader

    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"LSTM output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    if not train_sequences or not validation_sequences:
        raise ValueError("Both training and validation conversations are required")
    random.seed(config.seed)
    np.random.seed(config.seed)
    torch.manual_seed(config.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(config.seed)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)
    device = torch.device(device_name or ("cuda" if torch.cuda.is_available() else "cpu"))
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")

    train_dataset = _SequenceDataset(train_sequences, config.input_mode)
    validation_dataset = _SequenceDataset(validation_sequences, config.input_mode)
    train_loader = DataLoader(
        train_dataset,
        batch_sampler=_LengthBucketBatchSampler(
            train_dataset, config.batch_size, config.seed
        ),
        collate_fn=_collate,
    )
    validation_loader = DataLoader(
        validation_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        collate_fn=_collate,
    )
    model = ConversationOnlyLSTM.build(config).to(device)
    train_labels = np.asarray([sequence.label for sequence in train_sequences], dtype=np.float32)
    positives = float(train_labels.sum())
    negatives = float(len(train_labels) - positives)
    if positives == 0 or negatives == 0:
        raise ValueError("Training conversations must contain both classes")
    positive_weight = negatives / positives
    criterion = torch.nn.BCEWithLogitsLoss(
        pos_weight=torch.tensor(positive_weight, device=device)
    )
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay,
    )
    amp_dtype = None
    if device.type == "cuda":
        amp_dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    scaler_enabled = bool(device.type == "cuda" and amp_dtype == torch.float16)
    try:
        scaler = torch.amp.GradScaler("cuda", enabled=scaler_enabled)
    except (AttributeError, TypeError):  # PyTorch 2.0 compatibility
        scaler = torch.cuda.amp.GradScaler(enabled=scaler_enabled)

    configuration = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "config": asdict(config),
        "device": str(device),
        "positive_weight": positive_weight,
        "train_conversations": len(train_sequences),
        "validation_conversations": len(validation_sequences),
        "supervision": "conversation label only",
        "loss": "BCEWithLogitsLoss at final valid turn",
        "turn_loss_weight": 0.0,
        "sequence_truncation": False,
        "length_bucketed_training_batches": True,
        "is_suspicious_used": False,
        "checkpoint_objective": "validation PR-AUC",
        "threshold_objective": "validation F0.5",
        "final_test_scored": False,
        "historical_test_scored": False,
        "provenance": provenance,
        "runtime": _runtime_record(torch, device, amp_dtype),
    }
    write_json(output_dir / "run_configuration.json", configuration)

    best_state: dict[str, Any] | None = None
    best_pr_auc = -math.inf
    best_f05 = -math.inf
    stale_epochs = 0
    history: list[dict[str, Any]] = []
    for epoch in range(1, config.epochs + 1):
        model.train()
        losses: list[float] = []
        for values, lengths, labels, _ids in train_loader:
            values = values.to(device)
            lengths = lengths.to(device)
            labels = labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(
                device_type=device.type,
                dtype=amp_dtype,
                enabled=amp_dtype is not None,
            ):
                _turn_logits, final_logits = model(values, lengths)
                loss = criterion(final_logits, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clip)
            scaler.step(optimizer)
            scaler.update()
            losses.append(float(loss.detach().cpu()))

        _ids, val_labels, val_scores = _predict(model, validation_loader, device)
        threshold, validation_metrics = select_f05_threshold(val_labels, val_scores)
        pr_auc = float(validation_metrics["pr_auc"] or 0.0)
        f05 = float(validation_metrics["f0_5"])
        history.append(
            {
                "epoch": epoch,
                "train_loss": float(np.mean(losses)),
                "validation_metrics": validation_metrics,
            }
        )
        print(
            f"epoch {epoch:02d} loss={np.mean(losses):.6f} "
            f"val_pr_auc={pr_auc:.6f} val_f0.5={f05:.6f}"
        )
        if (pr_auc, f05) > (best_pr_auc, best_f05):
            best_pr_auc, best_f05 = pr_auc, f05
            best_state = copy.deepcopy(model.state_dict())
            stale_epochs = 0
        else:
            stale_epochs += 1
            if stale_epochs >= config.early_stopping_patience:
                break

    if best_state is None:
        raise RuntimeError("No LSTM checkpoint was selected")
    model.load_state_dict(best_state)
    validation_ids, validation_labels, validation_scores = _predict(
        model, validation_loader, device
    )
    threshold, validation_metrics = select_f05_threshold(
        validation_labels, validation_scores
    )
    checkpoint_path = output_dir / "best_model.pt"
    _save_checkpoint(checkpoint_path, model, configuration)
    write_json(output_dir / "training_history.json", history)
    write_json(
        output_dir / "selected_threshold.json",
        {
            "selection_partition": "validation",
            "objective": "maximum F0.5",
            "threshold": threshold,
            "metrics": validation_metrics,
        },
    )
    pd.DataFrame(
        {
            "conversation_id": validation_ids,
            "label": validation_labels,
            "score": validation_scores,
            "prediction": (validation_scores >= threshold).astype(np.int8),
        }
    ).to_csv(output_dir / "validation_predictions.csv", index=False)
    summary = {
        "schema_version": 1,
        "status": "completed",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "input_mode": config.input_mode,
        "best_validation_pr_auc": validation_metrics["pr_auc"],
        "selected_threshold": threshold,
        "validation_metrics_at_selected_threshold": validation_metrics,
        "epochs_completed": len(history),
        "model_sha256": sha256_file(checkpoint_path),
        "configuration_payload_sha256": canonical_sha256(configuration),
        "final_test_scored": False,
        "historical_test_scored": False,
    }
    write_json(output_dir / "run_summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-cache", type=Path, required=True)
    parser.add_argument("--validation-cache", type=Path, required=True)
    parser.add_argument("--centroid-dir", type=Path, required=True)
    parser.add_argument("--feature-config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--input-mode", choices=["trajectory7", "enhanced775"], default="trajectory7"
    )
    parser.add_argument("--hidden-dim", type=int, default=256)
    parser.add_argument("--num-layers", type=int, default=2)
    parser.add_argument("--dropout", type=float, default=0.30)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--weight-decay", type=float, default=1e-4)
    parser.add_argument("--gradient-clip", type=float, default=1.0)
    parser.add_argument("--early-stopping-patience", type=int, default=4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device")
    args = parser.parse_args()
    feature_config = json.loads(args.feature_config.read_text(encoding="utf-8"))
    spike_threshold = float(feature_config["spike_threshold"])
    drop_threshold = float(feature_config["drop_threshold"])
    train_sequences, train_metadata = load_conversation_sequences(
        args.train_cache,
        args.centroid_dir,
        "train",
        spike_threshold,
        drop_threshold,
    )
    validation_sequences, validation_metadata = load_conversation_sequences(
        args.validation_cache,
        args.centroid_dir,
        "validation",
        spike_threshold,
        drop_threshold,
    )
    config = LSTMConfig(
        input_mode=args.input_mode,
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        gradient_clip=args.gradient_clip,
        early_stopping_patience=args.early_stopping_patience,
        seed=args.seed,
    )
    summary = train_lstm(
        train_sequences,
        validation_sequences,
        args.output_dir,
        config,
        provenance={
            "feature_config_sha256": sha256_file(args.feature_config),
            "train_cache_manifest_payload_sha256": train_metadata["cache_manifest"][
                "canonical_payload_sha256"
            ],
            "validation_cache_manifest_payload_sha256": validation_metadata[
                "cache_manifest"
            ]["canonical_payload_sha256"],
            "centroid_manifest_payload_sha256": train_metadata["centroid_manifest"][
                "canonical_payload_sha256"
            ],
        },
        device_name=args.device,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
