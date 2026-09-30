$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'condensed_flow_staged.pptx'
$out=Join-Path $PSScriptRoot 'condensed_visual_pass_2026-09-30'
if(Test-Path -LiteralPath $out){throw 'The one-pass QA directory already exists. No rerender.'}
$null=New-Item -ItemType Directory -Path $out
$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($source,$true,$false,$false)
    if($deck.Slides.Count -ne 31){throw 'Unexpected slide count.'}
    foreach($slide in $deck.Slides){
        $slide.Export((Join-Path $out ('slide-{0:D2}.png' -f $slide.SlideIndex)),'PNG',1280,720)
    }
    Write-Output 'Rendered all 31 slides in one pass.'
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
