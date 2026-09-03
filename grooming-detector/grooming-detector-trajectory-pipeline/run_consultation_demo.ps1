$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

Write-Host 'Starting the WASD Conversation Model Demo...'
Write-Host 'When Ready appears, open http://127.0.0.1:5000'
Write-Host 'Press Ctrl+C to stop the demo.'

python -m demo_live.app
