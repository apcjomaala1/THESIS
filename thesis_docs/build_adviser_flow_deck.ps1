param(
    [string]$Source = 'C:\Projects\THESIS\WASD - Thesis 2 - F2 and latency revised.pptx',
    [string]$Output = 'C:\Projects\THESIS\WASD - Thesis 2 - Adviser Flow Revised.pptx',
    [string]$Script = 'C:\Projects\THESIS\thesis_docs\PRESENTATION_SPEAKER_SCRIPT.md'
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Source)) { throw "Source deck missing: $Source" }
if (-not (Test-Path -LiteralPath $Script)) { throw "Speaker script missing: $Script" }
if (Test-Path -LiteralPath $Output) { throw "Output already exists: $Output" }

$markdown = Get-Content -LiteralPath $Script -Raw -Encoding UTF8
$matches = [regex]::Matches(
    $markdown,
    '(?ms)^## Slide (\d+):[^\r\n]*\r?\n(.*?)(?=^## Slide \d+:|^## Presenter reference:)'
)
if ($matches.Count -ne 17) { throw "Expected 17 spoken slide sections; got $($matches.Count)" }
$notes = @{}
foreach ($match in $matches) {
    $number = [int]$match.Groups[1].Value
    $notes[$number] = $match.Groups[2].Value.Trim()
}
if (($notes.Keys | Sort-Object) -join ',' -ne ((1..17) -join ',')) {
    throw 'Speaker sections must be numbered 1 through 17.'
}

$powerPoint = $null
$presentation = $null
try {
    $powerPoint = New-Object -ComObject PowerPoint.Application
    $presentation = $powerPoint.Presentations.Open($Source, 1, 0, 0)
    if ($presentation.Slides.Count -ne 31) {
        throw "Expected 31 source slides; got $($presentation.Slides.Count)"
    }

    $originalIds = @{}
    foreach ($slide in $presentation.Slides) {
        $originalIds[$slide.SlideIndex] = $slide.SlideID
    }

    # Work only in memory. The source is opened read-only and stays unchanged.
    foreach ($index in @(24, 17, 12, 9, 8, 5, 4, 3)) {
        $presentation.Slides.Item($index).Delete()
    }

    $sdgSlide = $presentation.Slides.FindBySlideID($originalIds[11]).Duplicate().Item(1)
    $sdgId = $sdgSlide.SlideID
    $sdgSlide.Shapes.Item('Title 1').TextFrame.TextRange.Text = 'SDG and Research Agenda'
    $sdgSlide.Shapes.Item('Panel body').TextFrame.TextRange.Text = (
        "SDG 9: Advances AI-assisted digital-safety infrastructure.`r" +
        "SDG 16: Supports safer interactions through human review.`r" +
        "AI, Analytics, and Intelligent Systems: Contextual NLP and sequence modeling.`r" +
        "Cybersecurity and Digital Trust: Better identification of concerning chats."
    )
    $sdgSlide.Shapes.Item('Panel body').TextFrame.TextRange.Font.Size = 25

    $visibleIds = @(
        $originalIds[1], $originalIds[2], $sdgId,
        $originalIds[6], $originalIds[7],
        $originalIds[10], $originalIds[11], $originalIds[14],
        $originalIds[13], $originalIds[15], $originalIds[16],
        $originalIds[18], $originalIds[20], $originalIds[19], $originalIds[21],
        $originalIds[22], $originalIds[23]
    )
    $hiddenIds = @(25..31 | ForEach-Object { $originalIds[$_] })
    $orderedIds = @($visibleIds) + @($hiddenIds)
    if ($orderedIds.Count -ne 24 -or ($orderedIds | Select-Object -Unique).Count -ne 24) {
        throw 'Reorder list is incomplete or duplicates a slide.'
    }

    for ($position = 1; $position -le $orderedIds.Count; $position++) {
        $presentation.Slides.FindBySlideID($orderedIds[$position - 1]).MoveTo($position)
    }
    $presentation.Slides.Item(17).Shapes.Item('Title 1').TextFrame.TextRange.Text = 'Recommendations'

    for ($position = 1; $position -le $presentation.Slides.Count; $position++) {
        $slide = $presentation.Slides.Item($position)
        $slide.SlideShowTransition.Hidden = if ($position -le 17) { 0 } else { -1 }
        if ($position -le 17) {
            $noteShape = $null
            foreach ($shape in $slide.NotesPage.Shapes) {
                if ($shape.Type -eq 14 -and $shape.PlaceholderFormat.Type -eq 2) {
                    $noteShape = $shape
                    break
                }
            }
            if ($null -eq $noteShape) { throw "Missing notes placeholder on slide $position" }
            $noteShape.TextFrame.TextRange.Text = $notes[$position]
        }
    }

    # Open XML .pptx. Leave the authoritative source file untouched.
    $presentation.SaveAs($Output, 24)
    Write-Output "Created $Output with 17 visible and 7 hidden slides."
}
finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($null -ne $powerPoint) { $powerPoint.Quit() }
}
