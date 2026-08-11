import argparse
import re
from pathlib import Path

import fasttext


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Test the trained FastText model.")
    parser.add_argument("--model", type=Path, default=script_dir / "final_fasttext_model.bin")
    parser.add_argument("--text")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--context-messages", type=int, default=2)
    args = parser.parse_args()
    model = fasttext.load_model(str(args.model))

    def classify(text):
        text = re.sub(r"[\r\n]+", " ", text).strip()
        labels, scores = model.predict(text, k=2)
        score = next((score for label, score in zip(labels, scores) if label == "__label__1"), 0.0)
        print(f"{'FLAGGED' if score >= args.threshold else 'SAFE'}: {score:.2%} positive probability")

    print("Testing FastText on: CPU")
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
