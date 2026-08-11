import argparse
from pathlib import Path

import torch
from transformers import pipeline


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Test the trained BERT model.")
    parser.add_argument("--model-dir", type=Path, default=script_dir / "final_bert_model")
    parser.add_argument("--text")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--context-messages", type=int, default=2)
    args = parser.parse_args()
    device = 0 if torch.cuda.is_available() else -1
    classifier = pipeline(
        "text-classification", model=str(args.model_dir), tokenizer=str(args.model_dir), device=device
    )

    def classify(text):
        results = classifier(text, top_k=2)
        score = next((item["score"] for item in results if item["label"] in {"LABEL_1", "1"}), 0.0)
        print(f"{'FLAGGED' if score >= args.threshold else 'SAFE'}: {score:.2%} positive probability")

    print(f"Testing BERT on: {'CUDA' if device == 0 else 'CPU'}")
    if args.text:
        classify(args.text)
        return
    history = []
    while True:
        text = input("Message (quit to exit): ").strip()
        if text.lower() == "quit":
            break
        if text:
            classify(" [SEP] ".join([text] + history[-args.context_messages:]))
            history.append(text)


if __name__ == "__main__":
    main()
