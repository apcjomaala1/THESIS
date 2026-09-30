$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'policy_comparison_staged.pptx'
$out=Join-Path $PSScriptRoot 'policy_visual_pass_2026-09-29'
if(Test-Path -LiteralPath $out){throw 'One-pass QA directory already exists. No second rendering allowed.'}
$null=New-Item -ItemType Directory -Path $out
$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($source,$true,$false,$false)
    foreach($slide in $deck.Slides){
        $slide.Export((Join-Path $out ('slide-{0:D2}.png' -f $slide.SlideIndex)),'PNG',1280,720)
    }
    Write-Output "One render batch complete: $($deck.Slides.Count) slides."
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
