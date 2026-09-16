$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$Host.UI.RawUI.WindowTitle = 'WASD - Live model processing'

Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "  Starting PAN12 Conversation Trajectory Research Demonstration" -ForegroundColor Green
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "Loading the frozen author-proxy DistilBERT and 7-feature trajectory LSTM..." -ForegroundColor Yellow
Write-Host "When Ready, open: http://127.0.0.1:5000 in your browser." -ForegroundColor White
Write-Host "Each browser message prints model stages, per-turn scores, and final decisions here." -ForegroundColor White
Write-Host "Press Ctrl+C in this terminal to stop the server.`n" -ForegroundColor Gray

python -u run_live_demo.py
