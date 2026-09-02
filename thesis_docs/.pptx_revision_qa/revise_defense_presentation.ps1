param(
    [Parameter(Mandatory = $true)][string]$Source,
    [Parameter(Mandatory = $true)][string]$Output,
    [Parameter(Mandatory = $true)][string]$Receipt
)

$ErrorActionPreference = 'Stop'
$msoFalse = 0
$msoTrue = -1
$ppSaveAsOpenXMLPresentation = 24
$ppPlaceholderBody = 2
$ppAlignLeft = 1
$ppAlignCenter = 2
$msoAnchorMiddle = 3

function Get-SlideText([object]$slide) {
    $parts = @()
    foreach ($shape in @($slide.Shapes)) {
        if ($shape.HasTextFrame -eq $msoTrue -and $shape.TextFrame.HasText -eq $msoTrue) {
            $parts += $shape.TextFrame.TextRange.Text
        }
    }
    return ($parts -join "`n")
}

function Set-Title([object]$slide, [string]$text, [double]$fontSize = 0) {
    $shape = $null
    foreach ($candidate in @($slide.Shapes)) {
        if ($candidate.Name -like 'Title*' -and $candidate.HasTextFrame -eq $msoTrue) {
            $shape = $candidate
            break
        }
    }
    if ($null -eq $shape) { throw "Title shape not found on slide $($slide.SlideIndex)" }
    $shape.TextFrame.TextRange.Text = $text
    if ($fontSize -gt 0) { $shape.TextFrame.TextRange.Font.Size = $fontSize }
}

function Set-Subtitle([object]$slide, [string]$text) {
    $shape = $slide.Shapes.Item('Text Placeholder 2')
    $shape.TextFrame.TextRange.Text = $text
}

function Set-Bullets([object]$slide, [string[]]$items, [double]$fontSize) {
    $shape = $slide.Shapes.Item('Content Placeholder 6')
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.WordWrap = $msoTrue
    $shape.TextFrame.TextRange.Text = ($items -join "`r")
    $range = $shape.TextFrame.TextRange
    $range.Font.Name = 'Calibri Light'
    $range.Font.Size = $fontSize
    $range.ParagraphFormat.Bullet.Visible = $msoTrue
    $range.ParagraphFormat.SpaceAfter = 7
    $range.ParagraphFormat.SpaceWithin = 1
}

function Set-Notes([object]$slide, [string]$text) {
    foreach ($shape in @($slide.NotesPage.Shapes)) {
        $placeholderType = $null
        try { $placeholderType = $shape.PlaceholderFormat.Type } catch { continue }
        if ($placeholderType -eq $ppPlaceholderBody) {
            $shape.TextFrame.TextRange.Text = $text
            $shape.TextFrame.TextRange.Font.Name = 'Calibri'
            $shape.TextFrame.TextRange.Font.Size = 12
            return
        }
    }
    throw "Notes body placeholder not found on slide $($slide.SlideIndex)"
}

function Rgb([int]$r, [int]$g, [int]$b) {
    return $r + (256 * $g) + (65536 * $b)
}

function Add-ResultsTable([object]$slide) {
    try { $slide.Shapes.Item('Content Placeholder 6').Delete() } catch {}
    try { $slide.Shapes.Item('Results Table').Delete() } catch {}
    try { $slide.Shapes.Item('Results Footnote').Delete() } catch {}

    $headers = @('Method', 'PR-AUC', 'F0.5', 'Precision', 'Recall', 'FP', 'FN')
    $rows = @(
        @('Keyword rule', '0.4451', '0.6888', '0.7105', '0.6136', '11', '17'),
        @('Maximum Layer 1', '0.5523', '0.5529', '0.5610', '0.5227', '18', '21'),
        @('Weighted scorer', '0.8050', '0.7500', '0.7347', '0.8182', '13', '8'),
        @('Primary trajectory LSTM', '0.9153', '0.8621', '0.8511', '0.9091', '7', '4'),
        @('Enhanced LSTM', '0.9483', '0.8836', '0.8723', '0.9318', '6', '3')
    )

    $shape = $slide.Shapes.AddTable(6, 7, 52, 130, 856, 292)
    $shape.Name = 'Results Table'
    $widths = @(236, 120, 110, 120, 110, 80, 80)
    for ($column = 1; $column -le 7; $column++) {
        $shape.Table.Columns.Item($column).Width = $widths[$column - 1]
    }

    for ($column = 1; $column -le 7; $column++) {
        $cell = $shape.Table.Cell(1, $column).Shape
        $cell.TextFrame.TextRange.Text = $headers[$column - 1]
    }
    for ($row = 2; $row -le 6; $row++) {
        for ($column = 1; $column -le 7; $column++) {
            $cell = $shape.Table.Cell($row, $column).Shape
            $cell.TextFrame.TextRange.Text = $rows[$row - 2][$column - 1]
        }
    }

    for ($row = 1; $row -le 6; $row++) {
        for ($column = 1; $column -le 7; $column++) {
            $cell = $shape.Table.Cell($row, $column).Shape
            $cell.TextFrame.MarginLeft = 4
            $cell.TextFrame.MarginRight = 4
            $cell.TextFrame.MarginTop = 3
            $cell.TextFrame.MarginBottom = 3
            $cell.TextFrame.VerticalAnchor = $msoAnchorMiddle
            $cell.TextFrame.TextRange.Font.Name = 'Calibri'
            $cell.TextFrame.TextRange.Font.Size = 16
            $cell.TextFrame.TextRange.Font.Color.RGB = Rgb 0 0 0
            $cell.TextFrame.TextRange.ParagraphFormat.Alignment = if ($column -eq 1) { $ppAlignLeft } else { $ppAlignCenter }
            if ($row -eq 1) {
                $cell.Fill.Solid()
                $cell.Fill.ForeColor.RGB = Rgb 225 231 239
                $cell.TextFrame.TextRange.Font.Bold = $msoTrue
            } elseif ($row -eq 5) {
                $cell.Fill.Solid()
                $cell.Fill.ForeColor.RGB = Rgb 226 239 230
                $cell.TextFrame.TextRange.Font.Bold = $msoTrue
            } else {
                $cell.Fill.Solid()
                $cell.Fill.ForeColor.RGB = Rgb 255 255 255
            }
        }
    }

    $footnote = $slide.Shapes.AddTextbox(1, 52, 440, 856, 36)
    $footnote.Name = 'Results Footnote'
    $footnote.TextFrame.TextRange.Text = 'Held-out test: N = 1,862 conversations; 44 positive. Thresholds were frozen on validation.'
    $footnote.TextFrame.TextRange.Font.Name = 'Calibri Light'
    $footnote.TextFrame.TextRange.Font.Size = 17
    $footnote.TextFrame.TextRange.Font.Color.RGB = Rgb 64 64 64
    $footnote.TextFrame.TextRange.ParagraphFormat.Alignment = $ppAlignCenter
}

$sourcePath = [IO.Path]::GetFullPath((Resolve-Path -LiteralPath $Source).Path)
$outputPath = [IO.Path]::GetFullPath($Output)
$receiptPath = [IO.Path]::GetFullPath($Receipt)
$workspace = [IO.Path]::GetFullPath((Get-Location).Path)
foreach ($path in @($sourcePath, $outputPath, $receiptPath)) {
    if (-not $path.StartsWith($workspace + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the workspace: $path"
    }
}
if (Test-Path -LiteralPath $outputPath) { Remove-Item -LiteralPath $outputPath -Force }

$ppt = $null
$sourceDeck = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $sourceDeck = $ppt.Presentations.Open($sourcePath, $msoTrue, $msoFalse, $msoFalse)
    if ($sourceDeck.Slides.Count -ne 34) { throw "Expected 34 source slides; found $($sourceDeck.Slides.Count)" }
    $resourceBefore = @{}
    foreach ($index in @(2, 30, 31, 32, 33, 34)) {
        $resourceBefore[$index] = Get-SlideText $sourceDeck.Slides.Item($index)
    }
    $sourceDeck.SaveCopyAs($outputPath, $ppSaveAsOpenXMLPresentation)
    $sourceDeck.Close()
    $sourceDeck = $null

    $deck = $ppt.Presentations.Open($outputPath, $msoFalse, $msoFalse, $msoFalse)

    Set-Title $deck.Slides.Item(3) 'Introduction' 60
    Set-Subtitle $deck.Slides.Item(3) 'Why contextual and behavioral analysis matters'

    Set-Bullets $deck.Slides.Item(4) @(
        'Online chats can carry harmful interactions across many turns.',
        'Keyword filters detect explicit words but miss context and progression.',
        'User reports help, but they usually act after someone notices a problem.',
        'Moderation needs both local context and conversation-wide patterns.'
    ) 27

    Set-Title $deck.Slides.Item(5) 'Statement of the Problem' 44
    Set-Bullets $deck.Slides.Item(5) @(
        'An ordinary message can change meaning when viewed with surrounding turns.',
        'Static methods miss gradual or obfuscated behavior.',
        'The study tests whether contextual and trajectory modeling reduces missed cases.'
    ) 29

    Set-Title $deck.Slides.Item(6) 'Research Questions' 44
    Set-Bullets $deck.Slides.Item(6) @(
        'How effective are existing chat moderation systems?',
        'Where do keyword and rule-based methods fail on context?',
        'How can ML and NLP analyze behavior across a conversation?',
        'How much can the proposed module improve recall and reduce false negatives?'
    ) 25

    Set-Title $deck.Slides.Item(7) 'Objectives of the Study' 44
    Set-Bullets $deck.Slides.Item(7) @(
        'General: Build an AI moderation module using context and behavioral patterns.',
        '1. Evaluate the limits of keyword-based and rule-based moderation.',
        '2. Develop a two-layer module for multi-turn chat analysis.',
        '3. Measure recall improvement and false-negative reduction.'
    ) 24

    Set-Title $deck.Slides.Item(8) 'What the Study Built' 44
    Set-Bullets $deck.Slides.Item(8) @(
        'Context-conditioned DistilBERT reads each turn with recent context.',
        'Seven trajectory features describe how evidence changes over time.',
        'An LSTM learns from the ordered feature sequence.',
        'A working interface supports sequential human review.'
    ) 27

    Set-Title $deck.Slides.Item(9) 'Scope and Evaluation Boundary' 40
    Set-Bullets $deck.Slides.Item(9) @(
        'PAN-2012 was selected to evaluate the completed architecture.',
        '18,567 eligible dyadic conversations; 218,114 turns.',
        'Conversation-level prediction with author-disjoint partitions.',
        'Offline English-language evaluation; external and local validation are next.'
    ) 25

    Set-Title $deck.Slides.Item(10) 'Why the Study Matters' 36
    Set-Bullets $deck.Slides.Item(10) @(
        'Academic: tests sequence modeling against matched static methods.',
        'Practical: delivers a working conversation-review workflow.',
        'Social: supports earlier prioritization of concerning interactions.',
        'Research: provides a reproducible author-disjoint evaluation design.'
    ) 25

    Set-Title $deck.Slides.Item(11) 'Review of Related Literature' 60
    Set-Subtitle $deck.Slides.Item(11) 'Context, behavior, and sequence learning'

    Set-Title $deck.Slides.Item(12) 'Why Context and Sequence Matter' 40
    Set-Bullets $deck.Slides.Item(12) @(
        'The meaning of a turn depends on the surrounding conversation.',
        'Transformers represent local conversational context.',
        'Behavioral evidence develops across multiple turns.',
        'Sequence models can learn how that evidence changes over time.'
    ) 28

    Set-Title $deck.Slides.Item(13) 'Theory and Dataset Selection' 40
    Set-Bullets $deck.Slides.Item(13) @(
        'OGDM explains grooming as a non-linear conversational process.',
        'Trajectory features translate progression into measurable signals.',
        'PAN-2012 was selected for its scale, chronology, and persistent speaker IDs.',
        'Related studies support combining language and behavioral evidence.'
    ) 26

    Set-Title $deck.Slides.Item(14) 'Methodology' 60
    Set-Subtitle $deck.Slides.Item(14) 'How the two-layer system was evaluated'

    Set-Title $deck.Slides.Item(15) 'Two-Layer Architecture' 44
    Set-Bullets $deck.Slides.Item(15) @(
        'Input: current turn plus up to two preceding turns.',
        'Layer 1: DistilBERT produces a contextual proxy score.',
        'Features: seven signals summarize the evolving conversation.',
        'Layer 2: the LSTM produces a conversation-priority score.',
        'Output: flagged conversations are presented for human review.'
    ) 25

    Set-Title $deck.Slides.Item(16) 'Data Preparation and Controls' 40
    Set-Bullets $deck.Slides.Item(16) @(
        '18,567 eligible conversations and 218,114 turns.',
        'Connected-author partitioning prevents author overlap.',
        'Training resources come only from the training partition.',
        'Models and thresholds are selected only on validation.',
        'The locked final test was evaluated once.'
    ) 25

    Set-Title $deck.Slides.Item(17) 'Models Compared Fairly' 40
    Set-Bullets $deck.Slides.Item(17) @(
        'Primary LSTM: chronological sequence of seven trajectory features.',
        'Weighted scorer: the same seven inputs combined statically.',
        'Additional baselines: keyword rule and maximum Layer 1 score.',
        'Enhanced LSTM: seven features plus DistilBERT embeddings.',
        'The matched comparison isolates the value of recurrent aggregation.'
    ) 24

    Set-Title $deck.Slides.Item(18) 'Evaluation and Responsible Use' 40
    Set-Bullets $deck.Slides.Item(18) @(
        'Primary metrics: PR-AUC, F0.5, precision, recall, and false negatives.',
        'Confidence intervals use 2,000 author-grouped bootstrap samples.',
        'Thresholds were frozen before the final test.',
        'All evaluation was offline; the output supports human review.'
    ) 25

    Set-Title $deck.Slides.Item(19) 'Results and Conclusions' 56
    Set-Subtitle $deck.Slides.Item(19) 'What the frozen held-out evaluation demonstrated'

    Set-Title $deck.Slides.Item(20) 'Frozen Experimental Setup' 38
    Set-Bullets $deck.Slides.Item(20) @(
        'Training: 13,031 conversations - 319 positive.',
        'Validation: 1,827 conversations - 49 positive.',
        'Held-out test: 1,862 conversations - 44 positive.',
        'Zero author overlap; validation-only selection; one-time final evaluation.'
    ) 26

    Set-Title $deck.Slides.Item(21) 'Held-Out Results: The Trajectory LSTM Led the Matched Methods' 31
    Add-ResultsTable $deck.Slides.Item(21)

    Set-Title $deck.Slides.Item(22) 'Sequence Modeling Added Value' 38
    Set-Bullets $deck.Slides.Item(22) @(
        'Same seven inputs: primary LSTM versus weighted scorer.',
        '+0.1103 PR-AUC [95% CI: +0.0251, +0.2254].',
        '+0.1121 F0.5 [95% CI: +0.0194, +0.2336].',
        'False negatives: 17 keyword -> 8 weighted -> 4 LSTM.',
        'Learned recurrent aggregation outperformed static aggregation.'
    ) 25

    Set-Title $deck.Slides.Item(23) 'The Objectives Were Achieved' 38
    Set-Bullets $deck.Slides.Item(23) @(
        'Static methods missed more context-dependent conversations.',
        'A complete two-layer module and review interface were delivered.',
        'The primary LSTM reached 0.9091 recall with four false negatives.',
        'Next: external validation, ablations, and moderator-centered evaluation.'
    ) 25

    Set-Title $deck.Slides.Item(24) 'AI Tool Usage' 60
    Set-Subtitle $deck.Slides.Item(24) 'AI assisted the work; researchers remained responsible.'

    Set-Title $deck.Slides.Item(25) 'AI Tools Used' 44
    Set-Bullets $deck.Slides.Item(25) @(
        'OpenAI ChatGPT and Codex',
        'Google Gemini'
    ) 30

    Set-Title $deck.Slides.Item(26) 'How AI Assisted the Study' 40
    Set-Bullets $deck.Slides.Item(26) @(
        'Writing and proofreading',
        'Literature discovery and source checking',
        'Methodology and label-provenance auditing',
        'Programming and test assistance',
        'Documentation and presentation revision'
    ) 27

    Set-Title $deck.Slides.Item(27) 'Responsible AI Use' 44
    Set-Bullets $deck.Slides.Item(27) @(
        'Researchers verified all AI-assisted work.',
        'Claims were checked against original sources and experiment artifacts.',
        'Synthetic candidates were excluded from the primary experiment.',
        'Confidential data should not be entered into hosted tools.',
        'AI use is disclosed; final responsibility remains with the researchers.'
    ) 24

    Set-Title $deck.Slides.Item(28) 'Risk Mitigation' 44
    Set-Bullets $deck.Slides.Item(28) @(
        'Check citations and numerical claims.',
        'Review code and outputs manually.',
        'Keep training, validation, and test boundaries frozen.',
        'Remove sensitive information before tool use.',
        'Maintain independent researcher judgment.'
    ) 27

    Set-Title $deck.Slides.Item(29) 'The LSTM Reduced Missed Cases' 48
    Set-Subtitle $deck.Slides.Item(29) 'Questions and discussion'

    $notes = @{}
    $notes[1] = @(
        'Good day. Our study is titled AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis. We developed a two-layer moderation module that reads recent conversational context and then models how evidence changes across the full interaction.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md'
    ) -join "`r"
    $notes[3] = @(
        'We will begin with the problem that motivated the study, then explain the architecture, the evaluation design, the results, and what those results mean for the research objectives.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md'
    ) -join "`r"
    $notes[4] = @(
        'Online chat moderation often starts with keyword filters and user reports. Those tools are useful, but they do not always capture meaning that develops over several turns. Our study addresses that gap by combining recent message context with a model of the conversation trajectory.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 1.1)'
    ) -join "`r"
    $notes[5] = @(
        'The key problem is context. A message that looks ordinary by itself may become concerning when we see what came before it and how the interaction is progressing. We therefore test whether combining contextual language analysis with conversation-wide sequence modeling reduces the cases missed by static approaches.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 1.2)'
    ) -join "`r"
    $notes[6] = @(
        'The study asks four questions. First, how effective are existing moderation systems? Second, where do keyword and rule-based approaches struggle with context? Third, how can machine learning and NLP analyze behavioral patterns across a conversation? Fourth, how much can our module improve recall and reduce false negatives compared with the tested approaches?',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 1.2)'
    ) -join "`r"
    $notes[7] = @(
        'Our general objective is to develop an AI-powered moderation module that adds behavioral and contextual understanding to existing moderation. The three specific objectives are to evaluate static approaches, build the two-layer module, and measure whether it improves detection, especially by reducing false negatives.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 1.3)'
    ) -join "`r"
    $notes[8] = @(
        'This is the complete system we built. Layer 1 reads the current turn together with recent context. From its outputs and the conversation structure, we compute seven trajectory features. Layer 2 uses an LSTM to learn how those features develop over time. The interface then presents the result for human review.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 1.4 and 3.1)'
    ) -join "`r"
    $notes[9] = @(
        'The research and architecture came first. We then selected PAN-2012 because it provides the scale, chronological conversations, and persistent speaker identifiers needed for trajectory modeling and author-disjoint evaluation. For this experiment, the measured outcome is conversation-level. The detailed label definition is documented in the paper, while external and Philippine-language validation remain future work.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 1.4 and 3.3.1)'
    ) -join "`r"
    $notes[10] = @(
        'The academic contribution is the combination of contextual language modeling and learned behavioral trajectories. The practical contribution is a working review interface, and the evaluation framework makes the comparison reproducible. The study also provides a foundation for future work using contemporary and Philippine-context data.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 1.5)'
    ) -join "`r"
    $notes[11] = @(
        'Chapter 2 explains why both context and sequence matter and how the literature supports the design choices used in our module.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Chapter II)'
    ) -join "`r"
    $notes[12] = @(
        'Prior studies show that isolated words are not enough for many context-dependent interactions. Transformers help represent a turn together with nearby messages. Sequence models add another level by learning how evidence changes across the interaction instead of treating every turn as independent.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 2.1 and 2.2)'
    ) -join "`r"
    $notes[13] = @(
        'OGDM provides the theoretical reason to look at progression across a conversation. We do not claim that each feature directly identifies a grooming stage. Instead, the theory guides which changes may be useful to model. PAN-2012 was selected later as the empirical dataset because it supports the sequence and split requirements of the architecture.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 2.2 and 2.3)'
    ) -join "`r"
    $notes[14] = @(
        'We now move to the methodology: how the data was prepared, how the two layers work, how the comparisons were made fair, and how the final evaluation was kept separate from model development.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Chapter III)'
    ) -join "`r"
    $notes[15] = @(
        'The easiest way to understand the architecture is as two levels of context. Layer 1 looks at the current turn and up to two previous turns. Layer 2 looks at the ordered trajectory of the entire conversation. Its final score is used to prioritize a conversation for human review, not to make an automatic enforcement decision.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 3.1 and 3.4)'
    ) -join "`r"
    $notes[16] = @(
        'The eligible pool contains 18,567 dyadic conversations and 218,114 turns. We split connected groups of authors together, so the same author cannot appear in training and testing. Training-derived resources use training data only, validation is used for model and threshold selection, and the final test is used once after everything is frozen.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 3.3)', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md (Section 4.1)'
    ) -join "`r"
    $notes[17] = @(
        'The most important comparison is between the primary LSTM and the weighted scorer because both receive the same seven trajectory features. The difference is how they combine those features: the weighted scorer is static, while the LSTM learns from their order and progression. Keyword and maximum Layer 1 baselines provide additional reference points.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 3.4.3)'
    ) -join "`r"
    $notes[18] = @(
        'We emphasize precision-recall performance, recall, and false negatives because the positive class is rare and missed cases matter. Confidence intervals were computed by resampling connected author groups. All thresholds were selected on validation and frozen before the final test. The prototype is evaluated offline and is intended to support human reviewers.',
        '', '[Sources]', '- thesis_docs/Finals_Revised_Paper_WASD.md (Sections 3.5 and 3.6)', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md'
    ) -join "`r"
    $notes[19] = @(
        'The next slides present the frozen experimental setup, the actual held-out results, the matched comparison, and the conclusions tied directly to the research objectives.',
        '', '[Sources]', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md', '- thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md'
    ) -join "`r"
    $notes[20] = @(
        'The training partition contains 13,031 conversations, validation contains 1,827, and the held-out test contains 1,862. Only 44 test conversations are positive, so the task is highly imbalanced. The author-disjoint design prevents the model from being tested on authors it already saw during training.',
        '', '[Sources]', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md (Section 4.1)'
    ) -join "`r"
    $notes[21] = @(
        'This table shows the actual held-out results. The primary trajectory LSTM achieved 0.9153 PR-AUC, 0.8621 F0.5, 0.8511 precision, and 0.9091 recall. It identified 40 of the 44 positive conversations, leaving four false negatives and seven false positives. The enhanced LSTM has slightly higher point estimates, but the paired analysis does not establish that it is superior to the primary model.',
        '', '[Sources]', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md (Table 4.1)', '- grooming-detector/grooming-detector-trajectory-pipeline/revised_runs/final_results/final_evaluation.json'
    ) -join "`r"
    $notes[22] = @(
        'The matched comparison is the clearest evidence for the architecture. With the same seven inputs, the LSTM improved PR-AUC by 0.1103 and F0.5 by 0.1121 over the weighted scorer. Both confidence intervals remain above zero. False negatives also fell from 17 for the keyword rule, to eight for the weighted scorer, and then to four for the LSTM. This supports learned recurrent aggregation rather than static combination.',
        '', '[Sources]', '- thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md (Table 4.2 and Section 4.7)'
    ) -join "`r"
    $notes[23] = @(
        'The conclusions answer the objectives directly. First, the static approaches missed more positive conversations. Second, we completed the two-layer module and its review interface. Third, the primary LSTM improved recall and reduced false negatives. Together, these results show that the general objective was achieved. The next work is external validation, targeted ablations, and evaluation with actual moderation workflows.',
        '', '[Sources]', '- thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md (Sections 5.2 and 5.3)'
    ) -join "`r"
    $notes[24] = @(
        'We also disclose how AI tools assisted the project. They supported parts of the research workflow, but the researchers remained responsible for every submitted claim, result, and decision.',
        '', '[Sources]', '- thesis_docs/THESIS_RECOVERY_NEXT_STEPS.md'
    ) -join "`r"
    $notes[25] = @(
        'The main AI tools used were OpenAI ChatGPT and Codex, together with Google Gemini. Different tools were used for different support tasks, and their outputs were not accepted automatically.',
        '', '[Sources]', '- thesis_docs/THESIS_RECOVERY_NEXT_STEPS.md'
    ) -join "`r"
    $notes[26] = @(
        'AI assisted with language refinement, literature discovery, methodology auditing, programming, tests, documentation, and presentation revision. It also helped generate candidate synthetic material during development, but that material was excluded from the primary experiment because it did not meet the required annotation standard.',
        '', '[Sources]', '- thesis_docs/THESIS_RECOVERY_NEXT_STEPS.md', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 3.6)'
    ) -join "`r"
    $notes[27] = @(
        'Human validation remained central. We checked claims against the cited papers and checked numerical statements against the frozen experiment artifacts. AI-generated material was not treated as ground truth, and the researchers retain responsibility for the final work.',
        '', '[Sources]', '- thesis_docs/THESIS_RECOVERY_NEXT_STEPS.md', '- thesis_docs/Finals_Revised_Paper_WASD.md (Section 3.6)'
    ) -join "`r"
    $notes[28] = @(
        'Our safeguards are straightforward: verify citations, inspect code and outputs, preserve the training-validation-test boundary, remove sensitive information, and keep independent researcher judgment. These controls reduce the risk of hallucinated claims, leakage, and overreliance on AI.',
        '', '[Sources]', '- thesis_docs/THESIS_RECOVERY_NEXT_STEPS.md'
    ) -join "`r"
    $notes[29] = @(
        'In summary, the study delivered the proposed two-layer module, and the held-out results show that contextual and trajectory modeling reduced missed positive conversations compared with the tested static approaches. Thank you. We are ready for your questions.',
        '', '[Sources]', '- thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md'
    ) -join "`r"

    foreach ($index in $notes.Keys) { Set-Notes $deck.Slides.Item([int]$index) $notes[$index] }

    foreach ($index in @(2, 30, 31, 32, 33, 34)) {
        if ((Get-SlideText $deck.Slides.Item($index)) -ne $resourceBefore[$index]) {
            throw "Preserve-only slide $index changed"
        }
    }

    $deck.Save()
    $deck.Close()
    $deck = $null
    $ppt.Quit()
    $ppt = $null
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $sourceDeck) { $sourceDeck.Close() }
    if ($null -ne $ppt) { $ppt.Quit() }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$ppt = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open($outputPath, $msoTrue, $msoFalse, $msoFalse)
    if ($deck.Slides.Count -ne 34) { throw "Expected 34 output slides; found $($deck.Slides.Count)" }
    $tableShape = $deck.Slides.Item(21).Shapes.Item('Results Table')
    if ($tableShape.Table.Rows.Count -ne 6 -or $tableShape.Table.Columns.Count -ne 7) {
        throw 'Results table dimensions are incorrect'
    }
    $requiredText = @(
        @{ Slide = 9; Text = 'PAN-2012 was selected to evaluate the completed architecture.' },
        @{ Slide = 22; Text = '+0.1103 PR-AUC' },
        @{ Slide = 23; Text = 'The primary LSTM reached 0.9091 recall with four false negatives.' }
    )
    foreach ($check in $requiredText) {
        if (-not (Get-SlideText $deck.Slides.Item($check.Slide)).Contains($check.Text)) {
            throw "Required text is missing from slide $($check.Slide): $($check.Text)"
        }
    }
    if ($tableShape.Table.Cell(5, 1).Shape.TextFrame.TextRange.Text -ne 'Primary trajectory LSTM') {
        throw 'Primary trajectory LSTM row is missing from the results table'
    }
    $noteSlides = @()
    foreach ($index in 1..29) {
        $hasNote = $false
        foreach ($shape in @($deck.Slides.Item($index).NotesPage.Shapes)) {
            $placeholderType = $null
            try { $placeholderType = $shape.PlaceholderFormat.Type } catch { continue }
            if ($placeholderType -eq $ppPlaceholderBody -and $shape.TextFrame.HasText -eq $msoTrue) {
                if ($shape.TextFrame.TextRange.Text.Trim().Length -gt 0) { $hasNote = $true }
            }
        }
        if ($hasNote) { $noteSlides += $index }
    }
    $overflow = @()
    foreach ($index in 1..29) {
        foreach ($shape in @($deck.Slides.Item($index).Shapes)) {
            if ($shape.HasTextFrame -eq $msoTrue -and $shape.TextFrame.HasText -eq $msoTrue) {
                $bound = $shape.TextFrame.TextRange.BoundHeight
                if ($bound -gt ($shape.Height - $shape.TextFrame.MarginTop - $shape.TextFrame.MarginBottom + 2)) {
                    $overflow += "slide $index / $($shape.Name): bound=$bound height=$($shape.Height)"
                }
            }
        }
    }
    $verification = [ordered]@{
        slide_count = $deck.Slides.Count
        results_table_rows = $tableShape.Table.Rows.Count
        results_table_columns = $tableShape.Table.Columns.Count
        slides_with_speaker_notes = $noteSlides
        preserve_only_slides_unchanged = @(2, 30, 31, 32, 33, 34)
        required_text_checks_passed = $true
        text_overflow_warnings = $overflow
        visual_rendering_performed = $false
    }
    $deck.Close()
    $deck = $null
    $ppt.Quit()
    $ppt = $null
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $ppt) { $ppt.Quit() }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

$receiptObject = [ordered]@{
    date = '2026-09-02'
    source = [ordered]@{ path = $sourcePath; sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourcePath).Hash }
    output = [ordered]@{ path = $outputPath; sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $outputPath).Hash }
    narrative = 'Research problem and architecture first; PAN-2012 presented as the selected evaluation dataset; results and objective-aligned conclusions follow.'
    changes = @(
        'Revised visible copy into concise presentation language rather than manuscript prose.',
        'Replaced the obsolete comment-matrix section with frozen results and conclusions.',
        'Added an editable held-out results table with exact approved metrics.',
        'Added plain-language speaker scripts and source blocks to the presentation slides.',
        'Preserved the existing visual template and resource slides.'
    )
    verification = $verification
    experiment_boundary = [ordered]@{ retrained = $false; retuned = $false; final_test_rescored = $false }
    committed = $false
}
[IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($receiptPath)) | Out-Null
[IO.File]::WriteAllText($receiptPath, ($receiptObject | ConvertTo-Json -Depth 20) + "`n", [Text.UTF8Encoding]::new($false))
Write-Output ('Created revised presentation: ' + $outputPath)
Write-Output ('SHA-256: ' + $receiptObject.output.sha256)
Write-Output ('Overflow warnings: ' + $verification.text_overflow_warnings.Count)
