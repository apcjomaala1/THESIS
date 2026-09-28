$ErrorActionPreference = 'Stop'
$path = 'C:\Projects\THESIS\WASD - Thesis 2 - F2 and latency revised.pptx'
$pairs = @(
    @('Primary trajectory LSTM','Trajectory-Feature LSTM'),
    @('primary seven-feature LSTM','Trajectory-Feature LSTM'),
    @('Primary comparison','Matched-input comparison'),
    @('primary LSTM','Trajectory-Feature LSTM'),
    @('Primary LSTM','Trajectory-Feature LSTM'),
    @('Enhanced LSTM','Embedding-and-Feature LSTM'),
    @('enhanced LSTM','Embedding-and-Feature LSTM'),
    @('primary model','trajectory-feature model'),
    @('enhanced model','embedding-and-feature model'),
    @('enhanced experiment','embedding-and-feature variant'),
    @('primary LSTM','Trajectory-Feature LSTM'),
    @('Primary:','Trajectory-Feature LSTM:'),
    @('Enhanced:','Embedding-and-Feature LSTM:'),
    @('the primary median','the trajectory-feature median'),
    @('Enhanced was','The Embedding-and-Feature LSTM was'),
    @('primary precision','trajectory-feature precision'),
    @('primary-versus-weighted','trajectory-feature-versus-weighted'),
    @('versus 21 for primary','versus 21 for the trajectory-feature model'),
    @('The primary has','The Trajectory-Feature LSTM has')
)
function Rename-Text([string]$text) {
    foreach ($pair in $pairs) { $text = $text.Replace($pair[0], $pair[1]) }
    return $text
}
function Rename-Shape($shape) {
    if ($shape.HasTextFrame -and $shape.TextFrame.HasText) {
        $old = $shape.TextFrame.TextRange.Text
        $new = Rename-Text $old
        if ($old -ne $new) { $shape.TextFrame.TextRange.Text = $new }
    }
    if ($shape.HasTable) {
        for ($row=1; $row -le $shape.Table.Rows.Count; $row++) {
            for ($col=1; $col -le $shape.Table.Columns.Count; $col++) {
                Rename-Shape $shape.Table.Cell($row,$col).Shape
            }
        }
    }
    if ($shape.Type -eq 6) {
        foreach ($child in $shape.GroupItems) { Rename-Shape $child }
    }
}
$ppt=$null
$deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($path,$false,$false,$false)
    foreach ($slide in $deck.Slides) {
        foreach ($shape in $slide.Shapes) { Rename-Shape $shape }
        foreach ($shape in $slide.NotesPage.Shapes) { Rename-Shape $shape }
    }
    # Treat the two result rows identically; remove the old preferred-row styling.
    foreach ($shape in $deck.Slides.Item(26).Shapes) {
        if (-not $shape.HasTable) { continue }
        for ($row=2; $row -le $shape.Table.Rows.Count; $row++) {
            $label=$shape.Table.Cell($row,1).Shape.TextFrame.TextRange.Text
            if ($label -notmatch 'LSTM') { continue }
            for ($col=1; $col -le $shape.Table.Columns.Count; $col++) {
                $cell=$shape.Table.Cell($row,$col).Shape
                $cell.TextFrame.TextRange.Font.Bold=0
                $cell.Fill.ForeColor.RGB=16777215
            }
        }
    }
    # Chart categories are synchronized separately at package level: activating
    # embedded ChartData blocked Office automation on this machine.
    $deck.Slides.Item(21).Shapes.Item('Content Placeholder 6').TextFrame.TextRange.Text = "Trajectory-Feature LSTM: seven behavioral features.`rEmbedding-and-Feature LSTM: those features plus 768 text-embedding values.`rBoth use contextual DistilBERT upstream.`rWeighted scoring uses the same seven features as the trajectory variant."
    $deck.Slides.Item(28).Shapes.Item('Title 1').TextFrame.TextRange.Text = 'Detection Coverage: 41 and 44 of 44'
    $deck.Slides.Item(28).Shapes.Item('Recall interpretation').TextFrame.TextRange.Text = 'Detected positives: keyword 27, maximum L1 39, weighted 38, 7-feature LSTM 41, 775-input LSTM 44.'
    $deck.Slides.Item(29).Shapes.Item('Error interpretation').TextFrame.TextRange.Text = '7-feature LSTM: 3 misses and 21 false alerts. 775-input LSTM: 0 misses and 41 false alerts.'
    $deck.Slides.Item(32).Shapes.Item('Panel body').TextFrame.TextRange.Text = "Local CPU HTTP benchmark: 160 requests per model.`r7-feature LSTM: median 267 ms, p95 709 ms, p99 830 ms.`r775-input LSTM: median 246 ms, p95 718 ms, p99 1,058 ms.`rThroughput: 3.39 and 3.32 requests/s, respectively."
    $deck.Slides.Item(35).NotesPage.Shapes.Item('Notes Placeholder 2').TextFrame.TextRange.Text = 'GroomShield provides two tested sequence variants. The Trajectory-Feature LSTM found 41 of 44 positives with 21 false alerts. The Embedding-and-Feature LSTM found all 44 with 41 false alerts. Its extra coverage makes it a useful recall-first option, while the trajectory variant has higher precision and a slightly higher F2 point estimate. The benchmark does not show one variant is faster overall. Thank you.'
    $deck.Save()
    Write-Output "Updated model names in $($deck.Slides.Count) slides without rendering."
} finally {
    if ($deck -ne $null) { $deck.Close() }
    if ($ppt -ne $null) { $ppt.Quit() }
}
