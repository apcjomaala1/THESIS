$ErrorActionPreference='Stop'
$root='C:\Projects\THESIS'
$source=Join-Path $root 'WASD - Thesis 2 - F2 and latency revised.pptx'
$staged=Join-Path $PSScriptRoot 'narrative_notes_staged.pptx'
$script=Get-Content -LiteralPath (Join-Path $root 'thesis_docs\PRESENTATION_SPEAKER_SCRIPT.md') -Raw -Encoding UTF8
$pattern='(?ms)^## Slide (\d+): [^\r\n]+\r?\n(.*?)(?=^## Slide \d+: |^## Presenter reference:|\z)'
$sections=[regex]::Matches($script,$pattern)
if($sections.Count -ne 43){throw "Expected 43 slide scripts, found $($sections.Count)."}
if(Test-Path -LiteralPath $staged){throw 'Staged narrative deck already exists; do not overwrite blindly.'}
for($i=0;$i -lt 43;$i++) {
    if([int]$sections[$i].Groups[1].Value -ne ($i+1)){throw "Slide script order invalid at $i"}
    if($sections[$i].Groups[2].Value -notmatch '(?m)^Sources?: '){throw "Citation missing for slide $($i+1)"}
}
Copy-Item -LiteralPath $source -Destination $staged
$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($staged,$false,$false,$false)
    if($deck.Slides.Count -ne 43){throw 'Slide count changed.'}
    for($n=1;$n -le 43;$n++) {
        $notes=$sections[$n-1].Groups[2].Value.Trim() -replace '\r?\n',[Environment]::NewLine
        $shape=$deck.Slides.Item($n).NotesPage.Shapes.Item('Notes Placeholder 2')
        $shape.TextFrame.TextRange.Text=$notes
    }
    $deck.Save()
    Write-Output "Embedded 43 scripts in $staged"
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
