param(
    [string]$DocumentPath = (Join-Path $PSScriptRoot '..\..\Alignment Table.docx')
)

$ErrorActionPreference = 'Stop'
$resolvedPath = [System.IO.Path]::GetFullPath($DocumentPath)

if (-not (Test-Path -LiteralPath $resolvedPath)) {
    throw "Alignment-table document not found: $resolvedPath"
}

$content = @{
    '2,1' = @(
        'SOP 1: Existing chat moderation systems must be evaluated for how effectively they detect grooming-related interactions.'
    )
    '2,2' = @(
        'RQ1 / RO1: How effective are existing chat moderation systems in detecting grooming-related interactions? This aligns with evaluating the effectiveness of existing keyword-based and rule-based systems.'
    )
    '2,3' = @(
        'Method: Section 3.4.3 evaluates the training-derived keyword rule on the connected-author held-out test using precision, recall, PR-AUC, F0.5, and confusion counts.'
    )
    '2,4' = @(
        'Evidence: Table 4.1 reports that the keyword rule achieved PR-AUC 0.4451, recall 0.6136, and 17 false negatives on the held-out test.'
    )
    '3,1' = @(
        'SOP 2: Keyword-based and rule-based approaches are limited when the meaning of a message depends on conversational context.'
    )
    '3,2' = @(
        'RQ2 / RO1: What are the limitations of keyword-based and rule-based moderation approaches in handling context-dependent communication? This aligns with evaluating their limitations and effectiveness.'
    )
    '3,3' = @(
        'Method: Sections 3.4.3 and 3.5 compare the keyword rule and static score-based methods with the context-conditioned trajectory LSTM on the same locked partition.'
    )
    '3,4' = @(
        'Evidence: Table 4.2 shows that the primary LSTM exceeded maximum Layer 1 aggregation by +0.3630 PR-AUC and +0.3864 recall.'
    )
    '4,1' = @(
        'SOP 3: The study requires an AI architecture that analyzes conversational context and behavioral development across multiple interactions.'
    )
    '4,2' = @(
        'RQ3 / RO2: How can machine learning and natural language processing analyze behavioral patterns and conversational context? This aligns with designing and developing the two-layer AI moderation module.'
    )
    '4,3' = @(
        'Method: Sections 3.3.4 and 3.4 implement context-conditioned DistilBERT, seven chronological trajectory features, and a primary LSTM sequence model.'
    )
    '4,4' = @(
        'Evidence: Section 4.7 confirms that the completed module combines chronological trajectory scoring with a working sequential human-review interface.'
    )
    '5,1' = @(
        'SOP 4: The completed AI-driven module must be assessed for recall improvement and false-negative reduction against conventional and static approaches.'
    )
    '5,2' = @(
        'RQ4 / RO3: To what extent does the module improve recall and reduce false negatives? This aligns with assessing improvement over traditional keyword-based and report-driven approaches.'
    )
    '5,3' = @(
        'Method: Section 3.5 applies validation-frozen choices and a one-time 1,862-conversation held-out test, with 2,000 connected-author bootstrap resamples for comparative inference.'
    )
    '5,4' = @(
        'Evidence: Table 4.1 shows 0.9091 recall and 4 false negatives for the primary LSTM, reducing false negatives by 76.5% versus the keyword rule and 50.0% versus the weighted scorer.'
    )
}

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$wordNamespace = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
$tempPath = Join-Path ([System.IO.Path]::GetTempPath()) ("alignment-table-" + [guid]::NewGuid().ToString('N') + '.docx')
[System.IO.File]::Copy($resolvedPath, $tempPath, $true)

function New-TextRun {
    param(
        [Parameter(Mandatory)] [xml]$Xml,
        [Parameter(Mandatory)] [System.Xml.XmlElement]$Paragraph,
        [System.Xml.XmlNode]$BaseRunProperties,
        [Parameter(Mandatory)] [string]$Text,
        [bool]$Bold
    )

    $run = $Xml.CreateElement('w', 'r', $wordNamespace)
    if ($BaseRunProperties) {
        $runProperties = $BaseRunProperties.CloneNode($true)
    }
    else {
        $runProperties = $Xml.CreateElement('w', 'rPr', $wordNamespace)
    }

    $boldNode = $runProperties.SelectSingleNode('./w:b', $script:namespaceManager)
    if ($Bold -and -not $boldNode) {
        $boldNode = $Xml.CreateElement('w', 'b', $wordNamespace)
        $null = $runProperties.AppendChild($boldNode)
    }
    elseif (-not $Bold -and $boldNode) {
        $null = $runProperties.RemoveChild($boldNode)
    }

    $null = $run.AppendChild($runProperties)
    $textNode = $Xml.CreateElement('w', 't', $wordNamespace)
    $spaceAttribute = $Xml.CreateAttribute('xml', 'space', 'http://www.w3.org/XML/1998/namespace')
    $spaceAttribute.Value = 'preserve'
    $null = $textNode.Attributes.Append($spaceAttribute)
    $textNode.InnerText = $Text
    $null = $run.AppendChild($textNode)
    $null = $Paragraph.AppendChild($run)
}

function Set-CellOoxmlText {
    param(
        [Parameter(Mandatory)] [xml]$Xml,
        [Parameter(Mandatory)] [System.Xml.XmlElement]$Cell,
        [Parameter(Mandatory)] [string]$Text
    )

    $sourceParagraph = $Cell.SelectSingleNode('./w:p[1]', $script:namespaceManager)
    $sourceParagraphProperties = if ($sourceParagraph) { $sourceParagraph.SelectSingleNode('./w:pPr', $script:namespaceManager) } else { $null }
    $sourceRunProperties = if ($sourceParagraph) { $sourceParagraph.SelectSingleNode('.//w:rPr[1]', $script:namespaceManager) } else { $null }

    foreach ($child in @($Cell.ChildNodes)) {
        if ($child.LocalName -ne 'tcPr') {
            $null = $Cell.RemoveChild($child)
        }
    }

    $paragraph = $Xml.CreateElement('w', 'p', $wordNamespace)
    if ($sourceParagraphProperties) {
        $null = $paragraph.AppendChild($sourceParagraphProperties.CloneNode($true))
    }

    $labelEnd = $Text.IndexOf(':')
    if ($labelEnd -ge 0) {
        New-TextRun -Xml $Xml -Paragraph $paragraph -BaseRunProperties $sourceRunProperties -Text $Text.Substring(0, $labelEnd + 1) -Bold $true
        New-TextRun -Xml $Xml -Paragraph $paragraph -BaseRunProperties $sourceRunProperties -Text $Text.Substring($labelEnd + 1) -Bold $false
    }
    else {
        New-TextRun -Xml $Xml -Paragraph $paragraph -BaseRunProperties $sourceRunProperties -Text $Text -Bold $false
    }

    $null = $Cell.AppendChild($paragraph)
}

$zip = $null
try {
    $zip = [System.IO.Compression.ZipFile]::Open($tempPath, [System.IO.Compression.ZipArchiveMode]::Update)
    $documentEntry = $zip.GetEntry('word/document.xml')
    if (-not $documentEntry) {
        throw 'The DOCX package does not contain word/document.xml.'
    }

    $reader = [System.IO.StreamReader]::new($documentEntry.Open(), $true)
    try {
        [xml]$documentXml = $reader.ReadToEnd()
    }
    finally {
        $reader.Dispose()
    }

    $script:namespaceManager = [System.Xml.XmlNamespaceManager]::new($documentXml.NameTable)
    $script:namespaceManager.AddNamespace('w', $wordNamespace)
    $tables = @($documentXml.SelectNodes('//w:body/w:tbl', $script:namespaceManager))
    if ($tables.Count -ne 1) {
        throw "Expected exactly one table; found $($tables.Count)."
    }

    $table = $tables[0]
    $rows = @($table.SelectNodes('./w:tr', $script:namespaceManager))
    if ($rows.Count -notin @(4, 5)) {
        throw "Expected four or five table rows; found $($rows.Count)."
    }
    foreach ($row in $rows) {
        $cellCount = @($row.SelectNodes('./w:tc', $script:namespaceManager)).Count
        if ($cellCount -ne 4) {
            throw "Expected four cells in every row; found $cellCount."
        }
    }

    if ($rows.Count -eq 4) {
        $newRow = $rows[-1].CloneNode($true)
        $null = $table.AppendChild($newRow)
        $rows = @($table.SelectNodes('./w:tr', $script:namespaceManager))
    }

    foreach ($entry in $content.GetEnumerator()) {
        $indices = $entry.Key.Split(',')
        $rowIndex = [int]$indices[0] - 1
        $columnIndex = [int]$indices[1] - 1
        $cells = @($rows[$rowIndex].SelectNodes('./w:tc', $script:namespaceManager))
        Set-CellOoxmlText -Xml $documentXml -Cell $cells[$columnIndex] -Text (($entry.Value) -join ' ')
    }

    $documentEntry.Delete()
    $replacementEntry = $zip.CreateEntry('word/document.xml', [System.IO.Compression.CompressionLevel]::Optimal)
    $writer = [System.IO.StreamWriter]::new($replacementEntry.Open(), [System.Text.UTF8Encoding]::new($false))
    try {
        $writer.Write($documentXml.OuterXml)
    }
    finally {
        $writer.Dispose()
    }
}
finally {
    if ($zip) {
        $zip.Dispose()
    }
}

[System.IO.File]::Copy($tempPath, $resolvedPath, $true)
[System.IO.File]::Delete($tempPath)

[pscustomobject]@{
    output = $resolvedPath
    sha256 = (Get-FileHash -LiteralPath $resolvedPath -Algorithm SHA256).Hash
    filled_rows = 4
    research_questions = 4
    specific_objectives = 3
    visual_qa_performed = $false
} | ConvertTo-Json
