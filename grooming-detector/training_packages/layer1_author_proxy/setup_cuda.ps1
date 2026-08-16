param(
    [string]$PythonCommand = "py -3.12",
    [string]$TorchVersion = "2.11.0",
    [string]$CudaIndexUrl = "https://download.pytorch.org/whl/cu128"
)

$ErrorActionPreference = "Stop"
$packageRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $packageRoot ".venv"

if (-not (Test-Path $venvPath)) {
    $pythonParts = $PythonCommand -split " "
    $pythonExe = $pythonParts[0]
    $pythonArgs = @()
    if ($pythonParts.Length -gt 1) {
        $pythonArgs = $pythonParts[1..($pythonParts.Length - 1)]
    }
    & $pythonExe @pythonArgs -m venv $venvPath
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual-environment Python was not created at $venvPython"
}

& $venvPython -m pip install --upgrade pip wheel
& $venvPython -m pip install "torch==$TorchVersion" --index-url $CudaIndexUrl
& $venvPython -m pip install -r (Join-Path $packageRoot "requirements.txt")

& $venvPython -c "import torch; print('PyTorch:', torch.__version__); print('CUDA runtime:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE'); assert torch.cuda.is_available(), 'CUDA is not available to PyTorch'"

Write-Host "CUDA environment is ready: $venvPath"
