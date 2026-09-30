$ErrorActionPreference = 'Stop'
$source = 'C:\Projects\THESIS\Finalized Complete Paper WASD - reconciled.docx'
$target = 'C:\Projects\THESIS\output\pdf\Finalized Complete Paper WASD - reconciled.pdf'
$sourceHash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
if (Test-Path -LiteralPath $target) { throw "Refusing to overwrite an existing PDF: $target" }
$word = $null
$document = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $confirmConversions = $false
    $readOnly = $true
    $addToRecentFiles = $false
    $document = $word.Documents.Open([ref]$source, [ref]$confirmConversions, [ref]$readOnly, [ref]$addToRecentFiles)
    $document.PrintRevisions = $false
    $document.ShowRevisions = $false
    # wdExportDocumentContent = 0, not wdExportDocumentWithMarkup = 7.
    $document.ExportAsFixedFormat($target, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    if (-not (Test-Path -LiteralPath $target)) { throw 'Word did not create the PDF' }
} finally {
    $doNotSave = 0
    if ($document -ne $null) { $document.Close([ref]$doNotSave) }
    if ($word -ne $null) { $word.Quit([ref]$doNotSave) }
}
if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne $sourceHash) {
    throw 'Source DOCX changed during export'
}
Get-Item -LiteralPath $target | Select-Object FullName,Length,LastWriteTime
