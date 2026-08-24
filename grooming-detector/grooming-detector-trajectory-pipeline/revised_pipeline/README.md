# Revised Author-Proxy Pipeline Runbook

## Status and scope

The adviser approved only the primary endpoint: conversation-level
identification of PAN12 conversations containing at least one author on the
official predator list. This package implements and records the completed
experiment for that endpoint; it does not imply that every downstream feature,
hyperparameter, or statistical choice separately received adviser approval.

As of 2026-08-24, the revised pipeline has completed. The accepted Layer 1 run,
development caches, centroid, comparators, deterministic LSTM searches, freeze
receipt, and final evaluation are retained locally under `revised_runs/`. The
one-time final-test ledger is consumed. **Do not arm or score the final test
again, and do not use final-test predictions to change a model, feature,
threshold, or comparator.** The commands below document the executed workflow;
development-only stages remain reusable on training and validation data.

The revised endpoint is author-derived and conversation-level. A Layer 1 score
is a predator-author proxy under prefix context, not a validated probability
that the current message is grooming. PAN `is_suspicious` is prohibited from
revised labels, losses, features, selection, and metrics.

## Data-access boundary

The canonical PAN CSV contains every locked partition in one source file. The
strict loader may parse that combined file to verify its hash, eligible pool,
split assignments, and aggregate counts. During development-cache generation,
it selects `train` and `validation` before building model contexts, scoring
rows, creating embeddings, or writing cache indexes. Consequently, final-test
rows are not scored, embedded, or retained in development artifacts, although
the combined source CSV is parsed for integrity and split routing. This is an
auditable holdout procedure, not cryptographic text blinding.

The `excluded_historical_test` partition is permanently unavailable to this
pipeline. Do not inspect either test partition to guide model changes.

## Generated-artifact root

Keep generated outputs under:

```text
grooming-detector/grooming-detector-trajectory-pipeline/revised_runs/
```

That directory is ignored by the root Git repository. It may contain model
weights, cache indexes, PAN-derived keywords, predictions, and conversation
identifiers, so keep it local and access-controlled. Commit the implementation,
runbook, compact status records, and non-sensitive hashes—not the generated run
tree.

The one-time final-test claim and consumption receipt are stored separately in
`training_packages/layer1_author_proxy/.final_test_ledger/`. That ledger is also
ignored, but it is an audit record: never delete, rename, copy, or recreate it
to obtain another final-test attempt.

## Preconditions

Run from
`C:\Projects\THESIS\grooming-detector\grooming-detector-trajectory-pipeline`
in the verified project environment. The returned Layer 1 directory must
contain `best_model/`, `run_configuration.json`, `run_summary.json`,
`selected_threshold.json`, and `validation_predictions.csv` from the exact
sendable training package.

Set the paths once. Replace the Layer 1 placeholder before running anything:

```powershell
$PipelineRoot = (Get-Location).Path
$RunRoot = Join-Path $PipelineRoot 'revised_runs'
$DataFile = (Resolve-Path '..\trained_model_distillbert\pan12_final_dataset.csv').Path
$SplitManifest = (Resolve-Path '..\training_packages\layer1_author_proxy\locked_split_manifest.json').Path
$PackageManifest = (Resolve-Path '..\training_packages\layer1_author_proxy\package_manifest.json').Path
$ComponentAudit = (Resolve-Path '.\author_disjoint_split_audit.json').Path
$Layer1Run = 'C:\ABSOLUTE\PATH\TO\RETURNED_LAYER1_RUN'

if (-not (Test-Path -LiteralPath $Layer1Run)) {
    throw 'Replace $Layer1Run with the returned teammate run directory.'
}
New-Item -ItemType Directory -Path $RunRoot -Force | Out-Null
```

Use new, empty output directories. Do not overwrite or silently reuse a failed
run.

## Development-only workflow

### 1. Validate the returned Layer 1 artifacts

```powershell
python -m revised_pipeline.contracts `
  --layer1-run $Layer1Run `
  --split-manifest $SplitManifest `
  --package-manifest $PackageManifest `
  --data-file $DataFile `
  --output (Join-Path $RunRoot 'layer1_acceptance_receipt.json')
```

Stop if validation fails. Do not work around a hash, argument, row-ID,
threshold, label, or no-test-scoring error.

Return the complete run, including its retained `checkpoint-*` Trainer state.
The validator accepts the documented hardware-dependent requested batch pairs
`8/16`, `16/32`, `32/64`, `64/128`, or `128/256`
(training/evaluation) and records the effective training batch after any
automatic memory reduction. The completed Layer 1 run used `8/16` with
gradient accumulation 1.

### 2. Generate train/validation caches only

```powershell
$DevelopmentCache = Join-Path $RunRoot 'development_cache'

python -m revised_pipeline.cache `
  --data-file $DataFile `
  --split-manifest $SplitManifest `
  --component-audit $ComponentAudit `
  --package-manifest $PackageManifest `
  --layer1-run $Layer1Run `
  --output-dir $DevelopmentCache `
  --splits train validation `
  --device cuda
```

Never add `final_test` to this command during development. Never request
`excluded_historical_test`.

### 3. Build the benign centroid from negative training conversations

```powershell
$CentroidDir = Join-Path $RunRoot 'centroid'

python -m revised_pipeline.centroid `
  --train-cache (Join-Path $DevelopmentCache 'train') `
  --output-dir $CentroidDir
```

### 4. Lock neutral shared feature thresholds

This step runs before fitting either comparator or LSTM. It does not select
thresholds from weighted-scorer or LSTM outcomes.

```powershell
$ComparatorDir = Join-Path $RunRoot 'comparators'
$FeatureConfig = Join-Path $ComparatorDir 'feature_config.json'

python -m revised_pipeline.feature_config `
  --validation-cache (Join-Path $DevelopmentCache 'validation') `
  --output $FeatureConfig
```

### 5. Fit the raw Layer 1 and weighted comparators on validation

```powershell
python -m revised_pipeline.comparators `
  --validation-cache (Join-Path $DevelopmentCache 'validation') `
  --centroid-dir $CentroidDir `
  --feature-config $FeatureConfig `
  --output-dir $ComparatorDir `
  --coordinate-passes 4
```

### 6. Derive the fixed training-only keyword baseline

```powershell
$KeywordDir = Join-Path $RunRoot 'keyword'

python -m revised_pipeline.keyword `
  --data-file $DataFile `
  --split-manifest $SplitManifest `
  --output-dir $KeywordDir `
  --max-terms 50 `
  --min-positive-conversations 3
```

### 7. Run the locked conversation-only LSTM searches

`experiment_plan.json` was committed before the returned Layer 1 model was
available. It fixes seed 42, the training budget, four candidates for the
primary matched seven-feature LSTM, two candidates for the separately reported
775-input model, and the deterministic selection rule: validation average
precision first, validation F0.5 second, then the earlier candidate in the
file. Every candidate is retained. The final gate rejects hand-picked direct
`revised_pipeline.lstm` runs.

```powershell
$Lstm7Search = Join-Path $RunRoot 'lstm_search_trajectory7'
$Lstm775Search = Join-Path $RunRoot 'lstm_search_enhanced775'

python -m revised_pipeline.lstm_search `
  --train-cache (Join-Path $DevelopmentCache 'train') `
  --validation-cache (Join-Path $DevelopmentCache 'validation') `
  --centroid-dir $CentroidDir `
  --feature-config $FeatureConfig `
  --output-dir $Lstm7Search `
  --input-mode trajectory7 `
  --device cuda

python -m revised_pipeline.lstm_search `
  --train-cache (Join-Path $DevelopmentCache 'train') `
  --validation-cache (Join-Path $DevelopmentCache 'validation') `
  --centroid-dir $CentroidDir `
  --feature-config $FeatureConfig `
  --output-dir $Lstm775Search `
  --input-mode enhanced775 `
  --device cuda
```

Do not add, remove, rerun, or reorder candidates after viewing outcomes. The
final result must be reported even if an LSTM does not outperform a comparator.

### 8. Freeze and preflight the complete protocol

Freeze only after the returned model, caches, feature configuration,
comparators, keyword artifact, both LSTM runs, code, and reporting plan have
been reviewed. Freezing itself does not score the final test.

```powershell
$FrozenProtocol = Join-Path $RunRoot 'frozen_protocol.json'

python -m revised_pipeline.final_gate freeze `
  --data-file $DataFile `
  --split-manifest $SplitManifest `
  --package-manifest $PackageManifest `
  --component-audit $ComponentAudit `
  --layer1-run $Layer1Run `
  --development-cache $DevelopmentCache `
  --centroid-dir $CentroidDir `
  --comparator-dir $ComparatorDir `
  --keyword-dir $KeywordDir `
  --lstm7-search $Lstm7Search `
  --lstm775-search $Lstm775Search `
  --output $FrozenProtocol `
  --acknowledgement FREEZE_COMPLETE_PROTOCOL_BEFORE_FINAL_TEST

python -m revised_pipeline.evaluate_final preflight `
  --frozen-protocol $FrozenProtocol
```

## Hard stop before the final test

Preparation ends after a successful preflight. Do not run `final_gate arm`, do
not generate a `final_test` cache directly, and do not run final evaluation
without explicit authorization for the one held-out evaluation.

The commands below are recorded for that later authorized event only. Arming
creates the single canonical claim for this dataset/split. Evaluation consumes
it before final rows are scored or cached. A later failure deliberately does
not restore the claim; report the failure and preserve the ledger rather than
deleting it or manufacturing another attempt.

```powershell
$FrozenRecord = Get-Content -Raw -LiteralPath $FrozenProtocol | ConvertFrom-Json
$FrozenHash = $FrozenRecord.canonical_payload_sha256

python -m revised_pipeline.final_gate arm `
  --frozen-protocol $FrozenProtocol `
  --expected-protocol-hash $FrozenHash `
  --acknowledgement SCORE_LOCKED_FINAL_TEST_EXACTLY_ONCE

$ClaimPath = Join-Path $FrozenRecord.gate_registry_path 'claim.json'
$FinalCache = Join-Path $RunRoot 'final_cache'
$FinalResults = Join-Path $RunRoot 'final_results'

python -m revised_pipeline.evaluate_final run `
  --frozen-protocol $FrozenProtocol `
  --final-test-claim $ClaimPath `
  --final-cache-dir $FinalCache `
  --output-dir $FinalResults `
  --device cuda
```

Do not tune, rerun, replace artifacts, or suppress an unfavorable result after
this point.
