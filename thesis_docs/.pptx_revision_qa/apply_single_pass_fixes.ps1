$ErrorActionPreference='Stop'
$path=Join-Path $PSScriptRoot 'policy_comparison_staged.pptx'
$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($path,$false,$false,$false)
    $title=$deck.Slides.Item(1).Shapes.Item('Title 4')
    $title.TextFrame.TextRange.Text='GroomShield'
    $title.Top=130; $title.Height=100
    $title.TextFrame.TextRange.Font.Size=50
    $title.TextFrame.TextRange.Font.Color.RGB=16777215
    $subtitle=$deck.Slides.Item(1).Shapes.Item('Subtitle 2')
    $subtitle.TextFrame.TextRange.Text='Detecting Grooming-Related Interactions in Chat Conversations Using DistilBERT and LSTM-Based Behavioral Sequence Modeling'
    $subtitle.Top=270; $subtitle.Height=210
    $subtitle.TextFrame.TextRange.Font.Size=25
    if($subtitle.TextFrame.TextRange.BoundHeight -gt $subtitle.Height){throw 'Cover subtitle does not fit.'}
    # Correct the old fixed scale: values of 78 and 41 were clipped above 25.
    $axis=$deck.Slides.Item(29).Shapes.Item('Editable results chart').Chart.Axes(2)
    $axis.MinimumScale=0; $axis.MaximumScale=90; $axis.MajorUnit=15
    foreach($n in @(30,31,38)) {
        $table=$deck.Slides.Item($n).Shapes.Item('Policy comparison table').Table
        for($c=1;$c -le $table.Columns.Count;$c++) {
            $table.Cell(1,$c).Shape.TextFrame.TextRange.Font.Color.RGB=16777215
        }
    }
    $deck.Slides.Item(18).Shapes.Item('Base encoder').TextFrame.TextRange.Text="Fixed base encoder`rCurrent-turn embedding`r+ training reference"
    $deck.Slides.Item(19).Shapes.Item('Panel body').TextFrame.TextRange.Text="Keep ordered, valid two-speaker conversations.`rBuild references and keyword lists from training data.`rUse validation to select models and conversation cutoffs.`rCompare cutoff policies on the saved test scores."
    $deck.Slides.Item(22).Shapes.Item('Panel body').TextFrame.TextRange.Text="PR-AUC: ranking across cutoffs.`rRecall: share of positive conversations found.`rPrecision: share of alerts that are positive.`rF2: combines both, with more weight on recall.`rError counts: false alerts and missed positives."
    # The imported divider badge contains a fixed raster '4'; overlay only its
    # number area with the actual slide number, retaining the star and template.
    foreach($n in @(3,13,17,24,37)) {
        $slide=$deck.Slides.Item($n)
        # Read from the single-pass render: RGB(247,166,1). The layout's
        # Rectangle 10 reports white because the gold badge is raster artwork.
        $gold=108279
        $badge=$null
        try{$badge=$slide.Shapes.Item('Correct divider number')}catch{}
        if($null -eq $badge){$badge=$slide.Shapes.AddShape(1,898.2242,481,51,51.1854)}
        $badge.Name='Correct divider number'
        $badge.Fill.ForeColor.RGB=$gold; $badge.Line.Visible=0
        $badge.TextFrame.TextRange.Text=[string]$n
        $badge.TextFrame.TextRange.Font.Name='Calibri'
        $badge.TextFrame.TextRange.Font.Size=28
        $badge.TextFrame.TextRange.Font.Bold=-1
        $badge.TextFrame.TextRange.Font.Color.RGB=16777215
        $badge.TextFrame.TextRange.ParagraphFormat.Alignment=2
        $badge.TextFrame.VerticalAnchor=3
        $badge.TextFrame.MarginLeft=0; $badge.TextFrame.MarginRight=0
        $badge.TextFrame.MarginTop=0; $badge.TextFrame.MarginBottom=0
    }
    $deck.Save()
    if($axis.MaximumScale -ne 90){throw 'Error chart scale not corrected.'}
    foreach($n in @(1,18,19,22,30,31,38)) {
        foreach($sh in $deck.Slides.Item($n).Shapes) {
            if($sh.HasTextFrame -and $sh.TextFrame.HasText -and $sh.TextFrame.TextRange.BoundHeight -gt ($sh.Height+2)){throw "Post-QA correction overflows slide $n shape $($sh.Name)"}
        }
    }
    Write-Output 'One-pass fixes saved; no second render performed.'
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
