import argparse
import csv
from pathlib import Path

import torch
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import pipeline


def parse_args():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Test a trained grooming classifier.")
    parser.add_argument("--model-dir", type=Path, default=script_dir / "final_moderation_model")
    parser.add_argument("--text", help="Classify one message and exit.")
    parser.add_argument("--csv", type=Path, help="Evaluate a CSV containing text and labels.")
    parser.add_argument("--text-column", default="text")
    parser.add_argument(
        "--label-mode",
        choices=("predator", "suspicious", "either"),
        default="either",
        help="Ground-truth definition for CSV evaluation.",
    )
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument(
        "--context-messages", type=int, default=2,
        help="Number of previous messages to include during interactive testing.",
    )
    return parser.parse_args()


def positive_score(classifier, text):
    results = classifier(text, top_k=2)
    return next(
        (item["score"] for item in results if item["label"] in {"LABEL_1", "1"}),
        0.0,
    )


def print_prediction(text, score, threshold):
    verdict = "FLAGGED" if score >= threshold else "SAFE"
    print(f"{verdict}: {score:.2%} positive probability")
    print(f"Message: {text}")


def evaluate_csv(classifier, csv_path, text_column, label_mode, threshold):
    predictions = []
    labels = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames or text_column not in reader.fieldnames:
            raise ValueError(f"CSV must contain a '{text_column}' column.")
        required_labels = {"is_predator", "is_suspicious"}
        missing = required_labels - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV must contain columns: {sorted(required_labels)}")
        for row in reader:
            text = (row[text_column] or "").strip()
            if not text:
                continue
            try:
                predator = int(row["is_predator"])
                suspicious = int(row["is_suspicious"])
            except (TypeError, ValueError):
                continue
            if label_mode == "predator":
                label = predator
            elif label_mode == "suspicious":
                label = suspicious
            else:
                label = int(predator == 1 or suspicious == 1)
            score = positive_score(classifier, text)
            predictions.append(int(score >= threshold))
            labels.append(label)

    if not labels:
        raise ValueError("No valid labeled rows were found in the CSV.")
    print(f"Evaluated {len(labels):,} rows")
    print(f"Accuracy:  {accuracy_score(labels, predictions):.4f}")
    print(f"Precision: {precision_score(labels, predictions, zero_division=0):.4f}")
    print(f"Recall:    {recall_score(labels, predictions, zero_division=0):.4f}")
    print(f"F1:        {f1_score(labels, predictions, zero_division=0):.4f}")


def main():
    args = parse_args()
    if not args.model_dir.exists():
        raise FileNotFoundError(f"Model directory not found: {args.model_dir}")

    device = 0 if torch.cuda.is_available() else -1
    print(f"Testing on: {'CUDA GPU 0' if device == 0 else 'CPU'}")
    classifier = pipeline(
        "text-classification",
        model=str(args.model_dir),
        tokenizer=str(args.model_dir),
        device=device,
    )

    if args.csv:
        evaluate_csv(classifier, args.csv, args.text_column, args.label_mode, args.threshold)
        return
    if args.text:
        print_prediction(args.text, positive_score(classifier, args.text), args.threshold)
        return

    print("Interactive mode. Type 'quit' to exit.")
    history = []
    while True:
        text = input("Message: ").strip()
        if text.lower() == "quit":
            break
        if text:
            context = " [SEP] ".join([text] + history[-args.context_messages:])
            score = positive_score(classifier, context)
            print_prediction(text, score, args.threshold)
            history.append(text)


if __name__ == "__main__":
    main()