import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)


SEED = 42
REQUIRED_COLUMNS = {"text", "is_predator", "is_suspicious"}


def parse_args():
    script_dir = Path(__file__).resolve().parent
    default_data_dir = script_dir.parent / "grooming-detector-trajectory-pipeline" / "data"
    parser = argparse.ArgumentParser(description="Train DistilBERT for grooming detection.")
    parser.add_argument("--data-dir", type=Path, default=default_data_dir)
    parser.add_argument("--data-file", type=Path)
    parser.add_argument("--label-mode", choices=("predator", "suspicious", "either"), default="suspicious")
    parser.add_argument("--output-dir", type=Path, default=script_dir / "final_moderation_model")
    parser.add_argument("--model-name", default="distilbert-base-uncased")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--eval-batch-size", type=int, default=32)
    parser.add_argument("--negative-ratio", type=float, default=1.0)
    parser.add_argument(
        "--context-window", type=int, default=2,
        help="Number of messages before and after each message to include.",
    )
    return parser.parse_args()


def read_labeled_csv(data_file):
    columns = REQUIRED_COLUMNS | {"conv_id", "convo_id", "line"}
    df = None
    for encoding in ("utf-8-sig", "cp1252", "latin1"):
        try:
            df = pd.read_csv(data_file, encoding=encoding, usecols=lambda column: column in columns)
            if encoding != "utf-8-sig":
                print(f"Reading {data_file.name} as {encoding}")
            break
        except UnicodeDecodeError:
            continue
        except ValueError as error:
            raise ValueError(f"{data_file.name} does not contain the required label columns") from error
    if df is None:
        raise ValueError(f"Could not decode {data_file.name} as UTF-8, cp1252, or latin1")
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"{data_file.name} is missing required columns: {sorted(missing)}")

    conversation_column = "conv_id" if "conv_id" in df.columns else "convo_id"
    conversation_values = df[conversation_column].fillna("").astype(str)
    df["conversation_id"] = data_file.stem + ":" + conversation_values
    df["line_number"] = pd.to_numeric(df.get("line", 0), errors="coerce").fillna(0)
    return df


def load_dataset(data_dir, data_file, label_mode, negative_ratio, context_window=2):
    if data_file is not None:
        data_files = [data_file]
    else:
        if not data_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {data_dir}")
        data_files = sorted(data_dir.glob("*.csv"))
        fixed_pan12 = data_dir / "fixed_pan12_dataset.csv"
        original_pan12 = data_dir / "pan12_final_dataset.csv"
        if fixed_pan12 in data_files and original_pan12 in data_files:
            data_files.remove(original_pan12)
            print("Using fixed_pan12_dataset.csv instead of pan12_final_dataset.csv")
    if not data_files:
        raise FileNotFoundError("No CSV datasets found")

    frames = []
    for current_file in data_files:
        if not current_file.exists():
            raise FileNotFoundError(f"Dataset not found: {current_file}")
        frames.append(read_labeled_csv(current_file))
        print(f"Found {current_file.name}")
    df = pd.concat(frames, ignore_index=True)
    df = df.dropna(subset=list(REQUIRED_COLUMNS)).copy()

    predator = pd.to_numeric(df["is_predator"], errors="coerce")
    suspicious = pd.to_numeric(df["is_suspicious"], errors="coerce")
    valid_labels = predator.isin([0, 1]) & suspicious.isin([0, 1])
    df = df.loc[valid_labels].copy()
    predator = predator.loc[valid_labels].astype(int)
    suspicious = suspicious.loc[valid_labels].astype(int)

    if label_mode == "predator":
        df["label"] = predator
    elif label_mode == "suspicious":
        df["label"] = suspicious
    else:
        df["label"] = np.maximum(predator.to_numpy(), suspicious.to_numpy())

    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0].sort_values(["conversation_id", "line_number"])
    if context_window > 0:
        grouped_text = df.groupby("conversation_id", sort=False)["text"]
        context_parts = [grouped_text.shift(offset).fillna("") for offset in range(0, context_window + 1)]
        df["text"] = pd.concat(context_parts, axis=1).apply(
            lambda row: " [SEP] ".join(part for part in row if part), axis=1
        )

    df = df[["text", "label", "conversation_id"]]
    before_deduplication = len(df)
    df = df.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)
    print(f"Loaded {before_deduplication:,} valid rows from {len(data_files)} CSV file(s)")
    print(f"Removed {before_deduplication - len(df):,} duplicate context/label rows")

    positives = df[df["label"] == 1]
    negatives = df[df["label"] == 0]
    if positives.empty or negatives.empty:
        raise ValueError("Both positive and negative examples are required.")
    if negative_ratio > 0:
        negative_count = min(len(negatives), max(1, int(len(positives) * negative_ratio)))
        negatives = negatives.sample(n=negative_count, random_state=SEED)

    balanced = pd.concat([positives, negatives]).sample(frac=1, random_state=SEED)
    print(f"Training pool: {len(balanced):,} rows ({len(positives):,} positive, {len(negatives):,} negative)")
    return balanced.reset_index(drop=True)


def split_by_conversation(data):
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=SEED)
    train_indices, eval_indices = next(
        splitter.split(data, data["label"], groups=data["conversation_id"])
    )
    train_data = data.iloc[train_indices].reset_index(drop=True)
    eval_data = data.iloc[eval_indices].reset_index(drop=True)
    if train_data["label"].nunique() < 2 or eval_data["label"].nunique() < 2:
        raise ValueError("Conversation split did not contain both labels; use more conversation data.")
    return train_data, eval_data


def compute_metrics(prediction):
    predictions = np.argmax(prediction.predictions, axis=-1)
    labels = prediction.label_ids
    return {
        "accuracy": accuracy_score(labels, predictions),
        "precision": precision_score(labels, predictions, zero_division=0),
        "recall": recall_score(labels, predictions, zero_division=0),
        "f1": f1_score(labels, predictions, zero_division=0),
    }


def main():
    args = parse_args()
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)
    print(f"Training on: {'CUDA' if torch.cuda.is_available() else 'CPU'}")

    data = load_dataset(
        args.data_dir, args.data_file, args.label_mode, args.negative_ratio, args.context_window
    )
    train_df, eval_df = split_by_conversation(data)
    train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
    eval_dataset = Dataset.from_pandas(eval_df, preserve_index=False)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    columns_to_remove = ["text", "conversation_id"]
    train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=columns_to_remove)
    eval_dataset = eval_dataset.map(tokenize, batched=True, remove_columns=columns_to_remove)
    model = AutoModelForSequenceClassification.from_pretrained(args.model_name, num_labels=2)
    training_args = TrainingArguments(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=500,
        fp16=torch.cuda.is_available(),
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        logging_steps=100,
        report_to="none",
        seed=SEED,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    print("Starting training...")
    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    print(f"SUCCESS: Model saved to {args.output_dir}")


if __name__ == "__main__":
    main()