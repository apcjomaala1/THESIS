$ErrorActionPreference='Stop'
$root='C:\Projects\THESIS'
$source=Join-Path $root 'WASD - Thesis 2 - F2 and latency revised.pptx'
$target=Join-Path $PSScriptRoot 'condensed_flow_staged.pptx'
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'condensed_flow_manifest.json') -Raw -Encoding UTF8 | ConvertFrom-Json
if((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash -ne '2314620376D65967D736ED7E4E3E293CA70E01D062E3E138D8A2B6122377045B'){throw 'Source deck changed since flow audit.'}
if(Test-Path -LiteralPath $target){throw 'Staged condensed deck already exists.'}

function Add-Text($slide,[string]$name,[string]$value,[single]$left,[single]$top,[single]$width,[single]$height,[single]$size){
    $sh=$slide.Shapes.AddTextbox(1,$left,$top,$width,$height)
    $sh.Name=$name
    $sh.TextFrame.TextRange.Text=$value
    $sh.TextFrame.TextRange.Font.Name='Calibri Light'
    $sh.TextFrame.TextRange.Font.Size=$size
    $sh.TextFrame.TextRange.Font.Color.RGB=3355443
    $sh.TextFrame.MarginLeft=0; $sh.TextFrame.MarginRight=0
    $sh.TextFrame.MarginTop=0; $sh.TextFrame.MarginBottom=0
    return $sh
}

$ppt=$null; $deck=$null
try {
    $ppt=New-Object -ComObject PowerPoint.Application
    $deck=$ppt.Presentations.Open($source,$false,$false,$false)
    if($deck.Slides.Count -ne 43){throw 'Expected the 43-slide source.'}
    $ids=@()
    for($n=1;$n -le 43;$n++){$ids += [int]$deck.Slides.Item($n).SlideID}
    $deck.SaveAs($target,24)

    # Consolidate the two separate LSTM policy slides into one editable table.
    $policy=$deck.Slides.Item(30).Duplicate().Item(1)
    $policyId=[int]$policy.SlideID
    foreach($name in @('Model label','Policy takeaway','Policy denominator','Policy comparison table')){
        $policy.Shapes.Item($name).Delete()
    }
    $policy.Shapes.Item('Title 1').TextFrame.TextRange.Text='Cutoff Choice: Coverage and Alerts'
    $null=Add-Text $policy 'Policy context' 'Same two trained models. Only the validation-selected cutoff changes.' 54 137 850 30 22

    $tableShape=$policy.Shapes.AddTable(7,7,54,169,850,282)
    $tableShape.Name='Combined policy table'
    $table=$tableShape.Table
    $headers=@('Model','Policy','Found','Missed','False alerts','Precision','Recall')
    $widths=@(245,75,75,75,110,135,135)
    for($c=1;$c -le 7;$c++){$table.Columns.Item($c).Width=$widths[$c-1]}
    for($r=1;$r -le 7;$r++){
        $values=$headers
        if($r -gt 1){
            $sourceRow=$manifest.policy_rows[$r-2]
            $model='Embedding-and-Feature LSTM'
            if($r -gt 4){$model='Trajectory-Feature LSTM'}
            $values=@($model,$sourceRow[1],$sourceRow[2],$sourceRow[3],$sourceRow[4],$sourceRow[5],$sourceRow[6])
        }
        for($c=1;$c -le 7;$c++){
            $cell=$table.Cell($r,$c).Shape
            $cell.TextFrame.TextRange.Text=[string]$values[$c-1]
            $cell.TextFrame.TextRange.Font.Name='Calibri'
            $cell.TextFrame.TextRange.Font.Size=18
            $cell.TextFrame.TextRange.Font.Bold=0
            $cell.TextFrame.TextRange.Font.Color.RGB=3355443
            $cell.TextFrame.TextRange.ParagraphFormat.Alignment=2
            $cell.TextFrame.VerticalAnchor=3
            $cell.TextFrame.MarginLeft=4; $cell.TextFrame.MarginRight=4
            $cell.TextFrame.MarginTop=2; $cell.TextFrame.MarginBottom=2
            $cell.Fill.ForeColor.RGB=16777215
            if($c -eq 1){$cell.TextFrame.TextRange.ParagraphFormat.Alignment=1}
            if($r -eq 1){$cell.Fill.ForeColor.RGB=10053171; $cell.TextFrame.TextRange.Font.Bold=-1; $cell.TextFrame.TextRange.Font.Color.RGB=16777215}
        }
    }
    $null=Add-Text $policy 'Policy meaning' "Embedding model: F1 catches 43/44 with 14 false alerts.`rF2 catches 44/44 with 41 false alerts: 27 more for one additional positive." 54 466 850 60 20

    $wanted=New-Object 'System.Collections.Generic.HashSet[int]'
    $ordered=New-Object 'System.Collections.Generic.List[int]'
    foreach($entry in $manifest.slides){
        $id=$policyId
        if($null -ne $entry.source_index){$id=$ids[[int]$entry.source_index-1]}
        if(-not $wanted.Add([int]$id)){throw "Repeated source slide ID $id"}
        $ordered.Add([int]$id)
    }
    if($ordered.Count -ne 31){throw 'Wrong target slide count.'}
    for($n=$deck.Slides.Count;$n -ge 1;$n--){
        if(-not $wanted.Contains([int]$deck.Slides.Item($n).SlideID)){$deck.Slides.Item($n).Delete()}
    }
    if($deck.Slides.Count -ne 31){throw 'Failed to remove redundant slides.'}
    for($n=1;$n -le 31;$n++){
        $deck.Slides.FindBySlideID($ordered[$n-1]).MoveTo($n)
        $slide=$deck.Slides.Item($n)
        if([int]$slide.SlideID -ne $ordered[$n-1]){throw "Slide order mismatch at $n"}
        $slide.SlideShowTransition.Hidden=0
        if($n -ge 25){$slide.SlideShowTransition.Hidden=-1}
        $notes=[string]$manifest.slides[$n-1].notes
        $slide.NotesPage.Shapes.Item('Notes Placeholder 2').TextFrame.TextRange.Text=($notes -replace '\n',[Environment]::NewLine)
    }
    $deck.Slides.Item(24).Shapes.Item('Correct divider number').TextFrame.TextRange.Text='24'
    $deck.Save()
    for($r=1;$r -le 7;$r++){
        for($c=1;$c -le 7;$c++){
            $cell=$deck.Slides.Item(19).Shapes.Item('Combined policy table').Table.Cell($r,$c).Shape
            if($cell.TextFrame.TextRange.BoundHeight -gt ($cell.Height+2)){throw "Policy table text overflow: row $r column $c"}
        }
    }
    Write-Output "Saved 24 main slides, two hidden backups, five hidden resources to $target"
} finally {
    if($deck -ne $null){$deck.Close()}
    if($ppt -ne $null){$ppt.Quit()}
}
