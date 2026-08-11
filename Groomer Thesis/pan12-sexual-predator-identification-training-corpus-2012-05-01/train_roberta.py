import argparse
from pathlib import Path

import torch
from datasets import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments

from train_distillbert import SEED, compute_metrics, load_dataset, split_by_conversation


def main():
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Train RoBERTa for grooming detection.")
    parser.add_argument("--data-dir", type=Path, default=script_dir / "data")
    parser.add_argument("--data-file", type=Path)
    parser.add_argument("--label-mode", choices=("predator", "suspicious", "either"), default="either")
    parser.add_argument("--output-dir", type=Path, default=script_dir / "final_roberta_model")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--negative-ratio", type=float, default=1.0)
    parser.add_argument("--context-window", type=int, default=2)
    args = parser.parse_args()
    print(f"Training RoBERTa on: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    data = load_dataset(args.data_dir, args.data_file, args.label_mode, args.negative_ratio, args.context_window)
    train_df, eval_df = split_by_conversation(data)
    train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
    eval_dataset = Dataset.from_pandas(eval_df, preserve_index=False)
    tokenizer = AutoTokenizer.from_pretrained("roberta-base")

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=["text", "conversation_id"])
    eval_dataset = eval_dataset.map(tokenize, batched=True, remove_columns=["text", "conversation_id"])
    model = AutoModelForSequenceClassification.from_pretrained("roberta-base", num_labels=2)
    training_args = TrainingArguments(
        output_dir=str(args.output_dir), num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size, per_device_eval_batch_size=args.batch_size * 2,
        learning_rate=2e-5, warmup_steps=500, weight_decay=0.01,
        fp16=torch.cuda.is_available(), eval_strategy="epoch", save_strategy="epoch",
        load_best_model_at_end=True, metric_for_best_model="f1", report_to="none", seed=SEED,
    )
    trainer = Trainer(
        model=model, args=training_args, train_dataset=train_dataset, eval_dataset=eval_dataset,
        processing_class=tokenizer, data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))
    print(f"SUCCESS: RoBERTa model saved to {args.output_dir}")


if __name__ == "__main__":
    main()
