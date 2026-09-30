$ErrorActionPreference='Stop'
$path=Join-Path $PSScriptRoot 'condensed_flow_staged.pptx'
$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($path,$false,$false,$false)
    if($deck.Slides.Count -ne 31){throw 'Unexpected condensed slide count.'}
    $shape=$deck.Slides.Item(19).Shapes.Item('Policy meaning')
    $shape.TextFrame.TextRange.Text="Embedding model: F1 catches 43/44 with 14 false alerts.`rF2 catches 44/44 with 41 false alerts: 27 more for one additional positive."
    if($shape.TextFrame.TextRange.BoundHeight -gt ($shape.Height+2)){throw 'Policy takeaway does not fit.'}
    $deck.Save()
    Write-Output 'Corrected false-alert wording without another render.'
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
