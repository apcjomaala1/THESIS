# Layer 1 Author-Proxy Training Package

This package trains the revised DistilBERT Layer 1 model approved on
2026-08-17. It is designed for a Windows workstation with a capable NVIDIA GPU.

## What the model is trained to predict

The target is the PAN12 **official predator-author membership of the current
speaker**. The model sees the current turn plus at most two preceding turns.
Its output is a predator-author proxy score. It is not a message-level grooming
label, grooming-phase label, offender determination, or safety judgment.

The trainer deliberately does not load the project `is_suspicious` column. It
does not use the PAN12 diff file or any synthetic chat data.

## Locked data and split

The accepted input is the active `pan12_final_dataset.csv` with SHA-256:

```text
4131dc7b78865bbe2a48d155f770dd3743236d161b8430893328fbed5a42d408
```

The trainer refuses a different file, including the older archived PAN CSV.
After strict row validation, the frozen design contains:

| Partition | Conversations | Rows | Positive conversations | Use |
|---|---:|---:|---:|---|
| Training | 13,031 | 152,405 | 319 | Model fitting; negative rows may be downsampled |
| Validation | 1,827 | 21,911 | 49 | Checkpoint and F0.5 threshold selection |
| New locked final test | 1,862 | 22,929 | 44 | Not scored by this trainer |
| Historical inspected test | 1,847 | 20,869 | 42 | Excluded completely |

All four groups have zero conversation, author, and connected-component
overlap. The new final test was selected from the former training components
using only component IDs, conversation counts, and class counts before revised
training. Its IDs are already frozen in `locked_split_manifest.json`.

## Fast handoff instructions

1. Extract the transfer ZIP into a normal local folder, preferably on an SSD.
2. Confirm that `data\pan12_final_dataset.csv` is present. The bundle produced
   in this repository already includes the exact locked CSV.
3. Open PowerShell in this folder.
4. Build the isolated CUDA environment:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\setup_cuda.ps1
   ```

5. Validate the GPU, dataset hash, manifest, split counts, context creation,
   and sampling without training:

   ```powershell
   .\verify_package.ps1
   ```

6. Start the full run:

   ```powershell
   .\run_training.ps1
   ```

The default physical batch size is 64 and validation batch size is 128. The
Transformers trainer automatically reduces the training batch if GPU memory is
insufficient. A larger card can be used explicitly, for example:

```powershell
.\run_training.ps1 -TrainBatchSize 128 -EvalBatchSize 256
```

Do not change the seed, dataset, split manifest, label, context window, or test
policy for the official run. If a hardware failure interrupts training, keep
the failed run directory for diagnosis and start a fresh timestamped run after
the cause is corrected.

## What to return after training

Send back the entire newly created `runs\layer1-author-proxy-*` directory. It
contains:

- `best_model\` -- selected model and tokenizer;
- `run_configuration.json` -- data, split, code, environment, hardware, and
  methodology records;
- `run_summary.json` -- selected checkpoint, validation metrics, and model hash;
- `selected_threshold.json` -- validation-only F0.5 threshold;
- `validation_predictions.csv` -- stable IDs, labels, probabilities, and
  predictions, without raw message text; and
- at most two recoverable training checkpoints.

The script intentionally creates no final-test predictions. Final-test scoring
must wait until the Layer 1 cache, Layer 2 models, comparators, thresholds, and
reporting code are frozen.

## Default training configuration

- Base model: `distilbert-base-uncased`
- Context: current turn plus two preceding turns
- Maximum length: 128 tokens
- Training negatives: 3 per positive row; training partition only
- Optimizer: fused AdamW on CUDA
- Learning rate: 2e-5
- Weight decay: 0.01
- Warm-up ratio: 0.10
- Maximum epochs: 5
- Early-stopping patience: 2 evaluations
- Checkpoint objective: validation PR-AUC
- Threshold objective: validation F0.5
- Precision: BF16 when supported, otherwise FP16
- TF32: enabled on Ampere-or-newer NVIDIA hardware
- Random seed: 42

CUDA operations can retain small nondeterministic differences across GPU and
driver versions. The package records the complete executed environment and
hashes so the run can be identified exactly.
