import argparse
import re
from pathlib import Path

import fasttext
from train_distillbert import SEED, load_dataset, split_by_conversation


def clean_text(text):
    return re.sub(r"[\r\n]+", " ", str(text)).strip()


def write_fasttext_file(data, path):
    with path.open("w", encoding="utf-8") as file:
        for row in data.itertuples(index=False):
            text = clean_text(row.text)
            if text:
                file.write(f"__label__{int(row.label)} {text}\n")


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Train FastText for grooming detection.")
    parser.add_argument("--data-dir", type=Path, default=script_dir / "data")
    parser.add_argument("--data-file", type=Path)
    parser.add_argument("--label-mode", choices=("predator", "suspicious", "either"), default="either")
    parser.add_argument("--output-dir", type=Path, default=script_dir)
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--negative-ratio", type=float, default=1.0)
    parser.add_argument("--context-window", type=int, default=2)
    args = parser.parse_args()

    print("Training FastText on: CPU (the standard fastText Python package is CPU-only)")
    data = load_dataset(args.data_dir, args.data_file, args.label_mode, args.negative_ratio, args.context_window)
    train_df, eval_df = split_by_conversation(data)
    train_path = args.output_dir / "fasttext_train.txt"
    eval_path = args.output_dir / "fasttext_test.txt"
    model_path = args.output_dir / "final_fasttext_model.bin"
    write_fasttext_file(train_df, train_path)
    write_fasttext_file(eval_df, eval_path)
    model = fasttext.train_supervised(
        input=str(train_path), epoch=args.epochs, lr=0.1, wordNgrams=2,
        loss="ova", dim=100, minn=2, maxn=5,
    )
    samples, precision, recall = model.test(str(eval_path))
    print(f"Evaluated {samples:,} rows | precision={precision:.4f} | recall={recall:.4f}")
    model.save_model(str(model_path))
    print(f"SUCCESS: FastText model saved to {model_path}")


if __name__ == "__main__":
    main()
