$ErrorActionPreference = 'Stop'
$root = 'C:\Projects\THESIS'
$source = Join-Path $root 'WASD - Thesis 2 - F2 and latency revised.pptx'
$target = Join-Path $root 'thesis_docs\.pptx_revision_qa\policy_comparison_staged.pptx'
$content = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'policy_deck_content.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if (Test-Path -LiteralPath $target) { throw 'Staged deck already exists; do not run authoring twice blindly.' }

function Set-Text($slide, [string]$name, [string]$value) {
    $slide.Shapes.Item($name).TextFrame.TextRange.Text = $value
}
function Add-Text($slide, [string]$name, [string]$value, [single]$left, [single]$top, [single]$width, [single]$height, [single]$size) {
    $sh = $slide.Shapes.AddTextbox(1,$left,$top,$width,$height)
    $sh.Name = $name
    $sh.TextFrame.TextRange.Text = $value
    $sh.TextFrame.TextRange.Font.Name = 'Calibri Light'
    $sh.TextFrame.TextRange.Font.Size = $size
    $sh.TextFrame.TextRange.Font.Color.RGB = 3355443
    $sh.TextFrame.MarginLeft=0; $sh.TextFrame.MarginRight=0
    $sh.TextFrame.MarginTop=0; $sh.TextFrame.MarginBottom=0
    return $sh
}
function Add-PolicyTable($slide, $rows, [single]$top, [single]$height, [single]$fontSize, [bool]$baseline) {
    $cols=7; if($baseline){$cols=8}
    $sh=$slide.Shapes.AddTable($rows.Count+1,$cols,54,$top,850,$height)
    $sh.Name='Policy comparison table'
    $table=$sh.Table
    $headers=@('Policy','TP','FN','FP','TN','Precision','Recall')
    $widths=@(120,78,78,78,98,160,238)
    if($baseline){$headers=@('Method','Policy','TP','FN','FP','TN','Precision','Recall'); $widths=@(205,78,53,53,53,78,165,165)}
    for($col=1;$col -le $cols;$col++) { $table.Columns.Item($col).Width=$widths[$col-1] }
    for($row=1;$row -le $rows.Count+1;$row++) {
        $values=$headers; if($row -gt 1){$values=$rows[$row-2]}
        for($col=1;$col -le $cols;$col++) {
            $cell=$table.Cell($row,$col).Shape
            $cell.TextFrame.TextRange.Text=[string]$values[$col-1]
            $cell.TextFrame.TextRange.Font.Name='Calibri'
            $cell.TextFrame.TextRange.Font.Size=$fontSize
            $cell.TextFrame.TextRange.Font.Bold=0
            $cell.TextFrame.TextRange.Font.Color.RGB=3355443
            $cell.TextFrame.TextRange.ParagraphFormat.Alignment=2
            $cell.TextFrame.VerticalAnchor=3
            $cell.TextFrame.MarginLeft=5; $cell.TextFrame.MarginRight=5
            $cell.TextFrame.MarginTop=3; $cell.TextFrame.MarginBottom=3
            $cell.Fill.ForeColor.RGB=16777215
            if($col -eq 1){$cell.TextFrame.TextRange.ParagraphFormat.Alignment=1}
            if($row -eq 1){$cell.Fill.ForeColor.RGB=10053171; $cell.TextFrame.TextRange.Font.Bold=-1}
        }
    }
    return $sh
}

$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($source,$false,$false,$false)
    if($deck.Slides.Count -ne 40){throw 'Expected the 40-slide source.'}
    $deck.SaveAs($target,24)
    # Retain the verified Calibri/Calibri Light template font pairing.
    Set-Text $deck.Slides.Item(18) 'Base encoder' "Fixed base encoder`r768-value embedding`r+ training reference"
    Set-Text $deck.Slides.Item(18) 'Trajectory features' "Layer 2 inputs`r`rSeven behavioral`rfeatures`r`rEmbedding variant:`r+ 768 text values"
    Set-Text $deck.Slides.Item(18) 'Sequence model' "Layer 2: LSTM`r7 or 775 inputs`rOrdered sequence"
    Set-Text $deck.Slides.Item(18) 'Architecture summary' 'Two input variants; each new turn updates the conversation score.'
    Set-Text $deck.Slides.Item(23) 'Panel body' "F0.5: emphasizes precision.`rF1: balances precision and recall.`rF2: emphasizes recall; our main reporting policy.`rValidation selects the cutoff. We still report false alerts."
    Set-Text $deck.Slides.Item(25) 'Content Placeholder 6' "Training: 13,031 conversations; 319 positive.`rValidation: 1,827 conversations; 49 positive.`rTest: 1,862 conversations; 44 positive.`rZero author overlap. All cutoffs selected on validation."
    Set-Text $deck.Slides.Item(26) 'Title 1' 'Conversation Results: F2 Policy'
    $content.slides[25].title='Conversation Results: F2 Policy'
    Set-Text $deck.Slides.Item(26) 'Results Footnote' 'N = 1,862; 44 positive. Validation-selected F2 cutoffs on saved test scores.'
    Set-Text $deck.Slides.Item(33) 'Panel body' "Objective 1: Quantified the limits of static methods.`rObjective 2: Built the contextual and sequence module.`rObjective 3: F2 misses: weighted 6; trajectory 3; embedding 0.`rGeneral objective: Broader conversation coverage for human review."
    Set-Text $deck.Slides.Item(34) 'Panel body' "Compare embedding-model F1 and F2 in a moderator workflow.`rTest fixed cutoffs on contemporary external chats.`rBenchmark longer histories, concurrent traffic, and caching.`rEvaluate early prefixes with independently reviewed onset labels."
    Set-Text $deck.Slides.Item(24) 'Text Placeholder 2' 'Detection results, cutoff trade-offs, and local latency'

    # Duplicate a simple native template slide, remove its body, then add editable tables.
    $template=$deck.Slides.Item(23)
    for($i=0;$i -lt 2;$i++) {
        $slide=$template.Duplicate().Item(1)
        $slide.MoveTo(30+$i)
        $slide.Shapes.Item('Panel body').Delete()
        Set-Text $slide 'Title 1' $content.slides[29+$i].title
        $key='lstm_enhanced775'; $label='Embedding-and-Feature LSTM'; $takeaway="F1: 43 of 44 found; 14 false alerts.`rF2 adds one detected positive and 27 false alerts."
        if($i -eq 1){$key='lstm_trajectory7';$label='Trajectory-Feature LSTM';$takeaway="F1 adds false alerts without detecting more positives.`rF2 reduces missed positives from four to three."}
        $null=Add-Text $slide 'Model label' "$label | same trained weights" 54 136 850 34 23
        $rows=$content.tables.$key
        $null=Add-PolicyTable $slide $rows 185 195 22 $false
        $null=Add-Text $slide 'Policy takeaway' $takeaway 54 403 850 67 24
        $null=Add-Text $slide 'Policy denominator' 'Same 1,862 test conversations: 44 positive; 1,818 negative. Cutoffs chosen on validation.' 54 482 850 32 16
    }
    $backup=$template.Duplicate().Item(1)
    $backup.MoveTo(38)
    $backup.SlideShowTransition.Hidden=-1
    $backup.Shapes.Item('Panel body').Delete()
    Set-Text $backup 'Title 1' 'Baseline Policy Comparison'
    $null=Add-Text $backup 'Backup context' 'Same test partition and fixed models; three validation-selected cutoff policies.' 54 133 850 32 20
    $rows=New-Object System.Collections.Generic.List[object]
    foreach($entry in @(@('raw_layer1','Maximum Layer 1'),@('weighted','Weighted scorer'),@('keyword','Keyword rule'))) {
        foreach($row in $content.tables.($entry[0])){$rows.Add(@($entry[1]) + @($row))}
    }
    $null=Add-PolicyTable $backup ($rows.ToArray()) 177 302 18 $true
    $null=Add-Text $backup 'Backup footnote' 'TP: found positives | FN: misses | FP: false alerts | TN: correct negatives. N = 1,862.' 54 492 850 30 17
    if($deck.Slides.Count -ne 43){throw 'Expected 43 slides.'}
    for($n=1;$n -le 43;$n++) {
        $slide=$deck.Slides.Item($n)
        $slide.NotesPage.Shapes.Item('Notes Placeholder 2').TextFrame.TextRange.Text=$content.slides[$n-1].notes
    }
    $deck.Save()
    $issues=@()
    foreach($slide in $deck.Slides) {
        foreach($sh in $slide.Shapes) {
            if($sh.HasTextFrame -and $sh.TextFrame.HasText) {
                if($sh.TextFrame.TextRange.BoundHeight -gt ($sh.Height+2)){$issues += "Slide $($slide.SlideIndex): $($sh.Name) bound-height exceeds box"}
            }
        }
    }
    $issues | Write-Output
    Write-Output "Saved $target, 43 slides, 37 visible, six hidden. Structural overflow flags: $($issues.Count)."
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
