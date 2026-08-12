"""Thin inference wrapper around the preserved DistilBERT classifier.

The recovered training code used a two-class sequence-classification objective
and negative downsampling. Its historical target is now known to be an invalid
message-level grooming label, so this module exposes a Layer 1 proxy score, not
a calibrated probability of grooming or predatory content.
"""

from pathlib import Path

import numpy as np
import torch
from transformers import (
    AutoTokenizer,
    DistilBertForSequenceClassification,
)


DEFAULT_MODEL_PATH = "../trained_model_distillbert/final_moderation_model"


class MessageClassifier:
    """Loads the saved DistilBertForSequenceClassification model and scores messages."""

    def __init__(self, model_path=DEFAULT_MODEL_PATH, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        model_path = str(Path(model_path).resolve())
        print(f"Loading Layer 1 classifier from {model_path} on {self.device}")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        except Exception:
            self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)
        self.model.eval().to(self.device)

    @torch.no_grad()
    def score(self, text):
        """Return the historical class-1 proxy score as a float in [0, 1]."""
        return float(self.score_batch([text])[0])

    @torch.no_grad()
    def score_batch(self, texts, batch_size=32):
        """Vectorized scoring; return an array of historical proxy scores."""
        out = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            encoded = self.tokenizer(
                batch, padding=True, truncation=True, max_length=128, return_tensors="pt",
            )
            encoded = {k: v.to(self.device) for k, v in encoded.items()}
            encoded.pop("token_type_ids", None)
            logits = self.model(**encoded).logits
            probs = torch.softmax(logits, dim=-1)[:, 1].cpu().numpy()
            out.append(probs)
        return np.concatenate(out)
