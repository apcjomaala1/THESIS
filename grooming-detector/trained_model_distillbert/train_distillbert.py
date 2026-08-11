import pandas as pd
import torch
from datasets import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

def main():
    # 1. Check for GPU Acceleration
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"--- Training on: {device.upper()} ---")

    # 2. Load and Balance the Data
    print("Loading pan12_final_dataset.csv...")
    df = pd.read_csv('pan12_final_dataset.csv')
    df = df.dropna(subset=['text', 'is_predator'])
    df['text'] = df['text'].astype(str)
    df['label'] = df['is_predator'].astype(int)

    # Balance the dataset: match the number of non-predators to the number of predators
    predators = df[df['label'] == 1]
    non_predators = df[df['label'] == 0].sample(n=len(predators), random_state=42)
    balanced_df = pd.concat([predators, non_predators]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"Total rows for training (balanced): {len(balanced_df)}")

    # 3. Split Data into Training (80%) and Validation (20%)
    train_df, val_df = train_test_split(balanced_df[['text', 'label']], test_size=0.2, random_state=42)
    train_dataset = Dataset.from_pandas(train_df)
    val_dataset = Dataset.from_pandas(val_df)

    # 4. Tokenization (Converting text to numbers)
    print("Tokenizing text...")
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')

    def tokenize_function(examples):
        return tokenizer(examples['text'], padding="max_length", truncation=True, max_length=128)

    tokenized_train = train_dataset.map(tokenize_function, batched=True)
    tokenized_val = val_dataset.map(tokenize_function, batched=True)

    # 5. Initialize Model
    print("Loading DistilBERT model...")
    model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=2)
    model.to(device)

# 6. Training Arguments (Optimized for 8GB VRAM)
    training_args = TrainingArguments(
        output_dir='./chat_moderation_results',
        num_train_epochs=3,
        per_device_train_batch_size=16, 
        per_device_eval_batch_size=32,
        warmup_steps=500,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=100,
        eval_strategy="epoch",      # <--- THIS IS THE FIX
        save_strategy="epoch",
        load_best_model_at_end=True,
    )

    # 7. Start the Training
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_val,
    )

    print("Starting training phase...")
    trainer.train()

    # 8. Save the Final Custom Model
    trainer.save_model("./final_moderation_model")
    tokenizer.save_pretrained("./final_moderation_model")
    print("SUCCESS: Model saved successfully to ./final_moderation_model")

if __name__ == "__main__":
    main()