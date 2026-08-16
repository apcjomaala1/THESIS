param(
    [string]$DataFile = ""
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $packageRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Run setup_cuda.ps1 first. Missing $venvPython"
}
$packageManifestPath = Join-Path $packageRoot "package_manifest.json"
if (-not (Test-Path $packageManifestPath)) {
    throw "Missing package integrity manifest: $packageManifestPath"
}
$packageManifest = Get-Content $packageManifestPath -Raw | ConvertFrom-Json
foreach ($entry in $packageManifest.files) {
    $candidate = Join-Path $packageRoot $entry.path
    if (-not (Test-Path $candidate)) {
        throw "Package file is missing: $($entry.path)"
    }
    $actualHash = (Get-FileHash $candidate -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $entry.sha256) {
        throw "Package file hash mismatch: $($entry.path)"
    }
}
if ([string]::IsNullOrWhiteSpace($DataFile)) {
    $DataFile = Join-Path $packageRoot "data\pan12_final_dataset.csv"
}
if (-not (Test-Path $DataFile)) {
    throw "PAN12 CSV not found: $DataFile"
}

& $venvPython -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); assert torch.cuda.is_available(), 'CUDA is not available to PyTorch'"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$verifyDir = Join-Path $packageRoot ".verification\$stamp"
& $venvPython (Join-Path $packageRoot "train_layer1_author_proxy.py") `
    --data-file (Resolve-Path $DataFile) `
    --split-manifest (Join-Path $packageRoot "locked_split_manifest.json") `
    --output-dir $verifyDir `
    --dry-run

Write-Host "Package verification passed. No model or final-test scores were produced."
