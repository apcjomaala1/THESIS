param(
    [string]$DataFile = "",
    [string]$OutputDir = "",
    [int]$TrainBatchSize = 64,
    [int]$EvalBatchSize = 128,
    [double]$NegativeRatio = 3.0,
    [double]$Epochs = 5.0
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $packageRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Run setup_cuda.ps1 first. Missing $venvPython"
}
if ([string]::IsNullOrWhiteSpace($DataFile)) {
    $DataFile = Join-Path $packageRoot "data\pan12_final_dataset.csv"
}
if (-not (Test-Path $DataFile)) {
    throw "PAN12 CSV not found: $DataFile"
}
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $OutputDir = Join-Path $packageRoot "runs\layer1-author-proxy-$stamp"
}

$env:HF_HUB_DISABLE_TELEMETRY = "1"
$env:TOKENIZERS_PARALLELISM = "false"

& $venvPython (Join-Path $packageRoot "train_layer1_author_proxy.py") `
    --data-file (Resolve-Path $DataFile) `
    --split-manifest (Join-Path $packageRoot "locked_split_manifest.json") `
    --output-dir $OutputDir `
    --model-name "distilbert-base-uncased" `
    --max-length 128 `
    --negative-ratio $NegativeRatio `
    --epochs $Epochs `
    --learning-rate 0.00002 `
    --weight-decay 0.01 `
    --warmup-ratio 0.10 `
    --train-batch-size $TrainBatchSize `
    --eval-batch-size $EvalBatchSize `
    --gradient-accumulation-steps 1 `
    --gradient-clip 1.0 `
    --early-stopping-patience 2 `
    --seed 42 `
    --require-cuda `
    --auto-find-batch-size

if ($LASTEXITCODE -ne 0) {
    throw "Layer 1 training failed with exit code $LASTEXITCODE"
}
Write-Host "Training finished. Return this entire directory: $OutputDir"
