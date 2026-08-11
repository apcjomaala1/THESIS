# Author-Disjoint LSTM Experiment Record

**Date:** 2026-08-12  
**Status:** Training and single held-out evaluation complete

## Purpose

Test whether the conversation-supervised LSTM still outperforms the weighted
trajectory scorer and DistilBERT current-score-only baseline when no author,
including no predator author, appears in more than one partition.

## Frozen Protocol

- Dataset: PAN12 canonical CSV, restricted to two-author conversations.
- Split: connected components of conversations linked by any shared author.
- Partition method: deterministic 10-fold stratified grouping, random state 42;
  validation/test folds selected only by size and class-count balance.
- Train/validation/test conversations: 14,893 / 1,828 / 1,847.
- Positive conversations: 363 / 49 / 42.
- Overlap: zero conversations, authors, and predator authors between all pairs.
- Training: five epochs, conversation loss weight 1.0, automatic turn and
  conversation positive weighting, seeded PyTorch/CUDA/DataLoader execution.
- Selection: best validation conversation F0.5, conversation AUC tie-breaker.
- Final threshold: selected on validation conversations only.
- Test: one held-out evaluation after checkpoint selection.

## Exact Training Command

Run from this directory:

```powershell
python train_lstm.py --csv ../trained_model_distillbert/pan12_final_dataset.csv --centroid benign_centroid.npy --epochs 5 --output trajectory_model_author_disjoint.pt --save-test-snaps test_snapshots_author_disjoint.pkl --split-protocol author-disjoint --split-audit author_disjoint_split_audit.json --random-state 42 2>&1 | Tee-Object -FilePath lstm_author_disjoint_train.log
```

## Exact Evaluation Command

Run only after training completes successfully:

```powershell
python evaluate_lstm_checkpoint.py --model trajectory_model_author_disjoint.pt --output lstm_author_disjoint_evaluation.json --split-protocol author-disjoint --split-audit author_disjoint_split_audit.json --random-state 42 2>&1 | Tee-Object -FilePath lstm_author_disjoint_evaluation.log
```

## Expected Artifacts

- `author_disjoint_split_audit.json`
- `author_disjoint_split_audit.log`
- `trajectory_model_author_disjoint.pt`
- `test_snapshots_author_disjoint.pkl`
- `lstm_author_disjoint_train.log`
- `lstm_author_disjoint_evaluation.json`
- `lstm_author_disjoint_evaluation.log`

## Interpretation Guardrails

This split addresses Layer 2 author overlap. Before claiming end-to-end unseen-
author generalization, the provenance and partitioning used to train the Layer 1
DistilBERT checkpoint must also be audited. No result should be selected or
discarded after inspecting the held-out test outcome.

## Training Outcome

- Checkpoint saved: `trajectory_model_author_disjoint.pt` (6,340,994 bytes).
- Five epochs completed on CUDA with random state 42.
- Best validation conversation F0.5: 0.786802.
- Validation conversation AUC: 0.986842.
- Checkpoint validation threshold: 0.889397.
- The shell wrapper reported exit code 1 only because PowerShell converted
  `tqdm`'s stderr progress stream into a `NativeCommandError`; the Python run
  reached its normal save messages, and the checkpoint reload/metadata check
  succeeded.

## Held-Out Author-Disjoint Test Outcome

The evaluator independently regenerated the same split, selected threshold
0.889347 from validation only, and then evaluated the test partition once.

| Metric | LSTM | Weighted scorer | DistilBERT current score only |
|---|---:|---:|---:|
| Recall | 0.833333 | 0.333333 | 0.000000 |
| Precision | 0.875000 | 0.184211 | 0.000000 |
| F1 | 0.853659 | 0.237288 | 0.000000 |
| F0.5 | 0.866337 | 0.202312 | 0.000000 |
| AUC-ROC | 0.990357 | 0.884131 | 0.855903 |
| False positives | 5 | 62 | 0 |
| True positives | 35 | 14 | 0 |
| False negatives | 7 | 28 | 42 |
| Mean detection turn | 10.77 | 62.86 | N/A |

Conclusion at the Layer 2 evaluation boundary: the conversation-supervised LSTM
outperforms both required comparators on every substantive discrimination and
detection metric under the author-disjoint split. This does not yet prove fully
end-to-end unseen-author generalization until Layer 1 training provenance is
confirmed disjoint from these validation/test messages and authors.
