$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

Write-Host 'Starting the provisional author-disjoint LSTM consultation demo...'
Write-Host 'When Ready appears, open http://127.0.0.1:5000'
Write-Host 'Press Ctrl+C to stop the demo.'

python -m demo.app
