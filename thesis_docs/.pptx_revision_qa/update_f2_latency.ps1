$ErrorActionPreference = 'Stop'

$source = 'C:\Projects\THESIS\WASD - Thesis 2 - panel revised.pptx'
$target = 'C:\Projects\THESIS\WASD - Thesis 2 - F2 and latency revised.pptx'
if (-not (Test-Path -LiteralPath $source)) { throw "Source deck not found: $source" }
if (Test-Path -LiteralPath $target) { throw "Target deck already exists: $target" }

function Set-ShapeText($slide, [string]$name, [string]$value) {
    $shape = $slide.Shapes.Item($name)
    if (-not $shape.HasTextFrame) { throw "No text frame on $name" }
    $shape.TextFrame.TextRange.Text = $value.Replace('`n', [Environment]::NewLine)
}

function Set-Notes($slide, [string]$value) {
    foreach ($shape in $slide.NotesPage.Shapes) {
        if ($shape.Name -eq 'Notes Placeholder 2') {
            $shape.TextFrame.TextRange.Text = $value
            return
        }
    }
    throw "Notes placeholder missing on slide $($slide.SlideIndex)"
}

function Set-TableRow($table, [int]$row, [string[]]$values) {
    if ($values.Count -ne $table.Columns.Count) { throw "Wrong column count on row $row" }
    for ($column = 1; $column -le $values.Count; $column++) {
        $table.Cell($row, $column).Shape.TextFrame.TextRange.Text = $values[$column - 1]
    }
}

function Set-ChartSeries($slide, [int]$seriesNumber, [string]$name, [double[]]$values, [string[]]$categories) {
    $chart = $slide.Shapes.Item('Editable results chart').Chart
    $series = $chart.SeriesCollection($seriesNumber)
    $series.Name = $name
    $series.Values = [object[]]$values
    $series.XValues = [object[]]$categories
}

$ppt = $null
$deck = $null
try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $deck = $ppt.Presentations.Open($source, $false, $false, $false)
    $deck.SaveAs($target, 24)

    Set-ShapeText $deck.Slides.Item(1) 'Subtitle 2' 'GroomShield: Detecting Grooming-Related Interactions in Chat Conversations Using DistilBERT and LSTM-Based Behavioral Sequence Modeling'
    Set-Notes $deck.Slides.Item(1) 'Good day. GroomShield combines contextual DistilBERT scores with a sequence model that follows how evidence develops across a conversation. We evaluate whether that design identifies more positive conversations than keyword and static-score methods, then show the local processing cost of both LSTM variants.'

    $table = $deck.Slides.Item(8).Shapes.Item('Evidence table').Table
    $table.Cell(3, 4).Shape.TextFrame.TextRange.Text = 'LSTM gains over maximum Layer 1: +0.3630 PR-AUC and +0.1958 F2.'
    $table = $deck.Slides.Item(9).Shapes.Item('Evidence table').Table
    $table.Cell(3, 4).Shape.TextFrame.TextRange.Text = 'Primary LSTM: 93.18% recall and three misses; 50% fewer misses than weighted scoring.'
    Set-Notes $deck.Slides.Item(9) 'For Objective 2, we built the contextual and sequence module with a working review interface. For Objective 3, the primary LSTM found 41 of 44 positive test conversations. That is 93.18 percent recall and three misses, compared with six misses for the weighted scorer. These F2-policy results use validation-selected cutoffs on preserved test scores.'
    Set-ShapeText $deck.Slides.Item(18) 'Review decision' 'Conversation score`nF2-selected cutoff`nHuman review'
    Set-ShapeText $deck.Slides.Item(19) 'Panel body' 'Keep valid, ordered two-speaker conversations. Build the benign reference and keyword list from training data. Use validation to choose models and final F2 cutoffs. Apply those cutoffs to saved test scores.'
    Set-Notes $deck.Slides.Item(19) 'The connected-author split prevents participant overlap across partitions. Training builds learned and derived resources; validation selects checkpoints and operating cutoffs. The original test used F0.5 cutoffs. After adopting F2, we applied cutoffs selected only from validation to the preserved test scores. No retraining or new final-test inference occurred.'

    Set-ShapeText $deck.Slides.Item(22) 'Panel body' 'PR-AUC summarizes ranking across cutoffs. Recall is the share of positive conversations found. Precision is the share of alerts that are positive. F2 combines both while emphasizing recall. We also show false alerts and missed positives.'
    Set-Notes $deck.Slides.Item(22) 'The test set contains 44 positives among 1,862 conversations. We therefore report both rates and actual error counts. PR-AUC summarizes the ranking. Recall says how many positives we caught; precision says how many alerts were positive. F2 gives more weight to recall without ignoring precision. The manuscript reports component-grouped uncertainty intervals.'
    Set-ShapeText $deck.Slides.Item(23) 'Title 1' 'Why We Use F2'
    Set-ShapeText $deck.Slides.Item(23) 'Panel body' 'Our screening goal is to miss fewer positive conversations. Validation F2 selects each final cutoff with extra weight on recall. Precision and false alerts remain visible. Primary LSTM: 41 of 44 found, 21 false alerts.'
    Set-Notes $deck.Slides.Item(23) 'F2 fits this screening task because missing a positive conversation matters more to the chosen operating objective, while false alerts still count. We selected each model cutoff on the separate validation partition, then applied it to preserved test scores. The primary LSTM found 41 of 44 positives, with 21 false alerts. F2 changed decisions, not model weights or checkpoint choice. This is a revised-policy analysis of an already evaluated test set.'

    Set-ShapeText $deck.Slides.Item(24) 'Text Placeholder 2' 'What the F2-selected policy and local latency test showed'
    Set-Notes $deck.Slides.Item(24) 'The next table and graphs show the F2-policy analysis of preserved test scores. They are not a second untouched test. A separate synthetic local benchmark measures latency for each LSTM through the HTTP demo path.'
    Set-ShapeText $deck.Slides.Item(25) 'Content Placeholder 6' 'Training: 13,031 conversations - 319 positive.`nValidation: 1,827 conversations - 49 positive.`nTest: 1,862 conversations - 44 positive.`nZero author overlap. F2 cutoffs selected on validation, then applied to saved test scores.'
    Set-Notes $deck.Slides.Item(25) 'The connected-author partitions contain 13,031 training, 1,827 validation, and 1,862 test conversations. The 44 positive test conversations are the denominator for recall. After the original evaluation, the F2 policy was selected on validation and applied to saved test scores. The original artifacts remain preserved.'

    $table = $deck.Slides.Item(26).Shapes.Item('Results Table').Table
    Set-TableRow $table 1 @('Method','PR-AUC','F2','Precision','Recall','FP','FN')
    Set-TableRow $table 2 @('Keyword rule','0.4451','0.6308','0.7105','0.6136','11','17')
    Set-TableRow $table 3 @('Maximum Layer 1','0.5523','0.6655','0.3333','0.8864','78','5')
    Set-TableRow $table 4 @('Weighted scorer','0.8050','0.7983','0.6129','0.8636','24','6')
    Set-TableRow $table 5 @('Primary trajectory LSTM','0.9153','0.8613','0.6613','0.9318','21','3')
    Set-TableRow $table 6 @('Enhanced LSTM','0.9483','0.8429','0.5176','1.0000','41','0')
    Set-ShapeText $deck.Slides.Item(26) 'Results Footnote' 'Saved test scores: N = 1,862; 44 positive. Final cutoffs selected on validation F2.'
    Set-Notes $deck.Slides.Item(26) 'The primary LSTM found 41 of 44 positives, with F2 of 0.8613, precision 0.6613, and recall 0.9318. The enhanced LSTM found all 44, with 41 false alerts and lower precision. The primary has the highest F2 point estimate. The main architecture comparison is with the weighted scorer because both use the same seven features. These are F2 cutoffs applied to saved test scores.'

    $categories = @('Keyword','Maximum L1','Weighted','Primary LSTM','Enhanced LSTM')
    Set-ChartSeries $deck.Slides.Item(27) 1 'PR-AUC' ([double[]]@(0.4451,0.5523,0.8050,0.9153,0.9483)) $categories
    Set-ChartSeries $deck.Slides.Item(27) 2 'F2' ([double[]]@(0.6308,0.6655,0.7983,0.8613,0.8429)) $categories
    Set-Notes $deck.Slides.Item(27) 'The bars compare PR-AUC and F2. The primary LSTM has the highest F2 point estimate; the enhanced model has the highest PR-AUC point estimate. The weighted scorer is the matched-input comparison for the primary LSTM. The paper contains the paired intervals behind these point estimates.'

    Set-ShapeText $deck.Slides.Item(28) 'Title 1' 'The Primary LSTM Found 41 of 44 Positives'
    Set-ChartSeries $deck.Slides.Item(28) 1 'Recall' ([double[]]@(0.6136,0.8864,0.8636,0.9318,1.0000)) $categories
    Set-ShapeText $deck.Slides.Item(28) 'Recall interpretation' 'Detected positives: keyword 27, maximum L1 39, weighted 38, primary 41, enhanced 44.'
    Set-Notes $deck.Slides.Item(28) 'Recall asks what share of positive conversations we found. The primary LSTM found 41 of 44, versus 27 for keyword matching, 39 for maximum Layer 1, and 38 for weighted scoring. The enhanced model found all 44, at a greater false-alert cost. These are final-conversation decisions, not grooming-onset measurements.'

    Set-ShapeText $deck.Slides.Item(29) 'Title 1' 'Missed Positives and False Alerts'
    Set-ChartSeries $deck.Slides.Item(29) 1 'Missed positives (FN)' ([double[]]@(17,5,6,3,0)) $categories
    Set-ChartSeries $deck.Slides.Item(29) 2 'False alerts (FP)' ([double[]]@(11,78,24,21,41)) $categories
    Set-ShapeText $deck.Slides.Item(29) 'Error interpretation' 'Primary vs weighted: six misses fell to three; false alerts fell from 24 to 21. Enhanced: zero misses, 41 false alerts.'
    Set-Notes $deck.Slides.Item(29) 'The primary LSTM cut the weighted scorer''s six missed positives to three and its 24 false alerts to 21. Relative to the keyword rule, missed positives fell from 17 to three. Maximum Layer 1 caught many positives but generated 78 false alerts. The enhanced LSTM missed none of the 44 test positives, while generating 41 false alerts. These counts show the recall-precision tradeoff directly.'

    Set-ShapeText $deck.Slides.Item(30) 'Panel body' 'The primary LSTM and weighted scorer share seven inputs.`nPR-AUC difference: +0.1103 [0.0251, 0.2254].`nF2 difference: +0.0630 [0.0034, 0.1294].`nBoth paired 95% intervals are above zero.'
    Set-Notes $deck.Slides.Item(30) 'Within 2,000 paired bootstrap resamples of connected-author groups, primary LSTM minus weighted scorer was +0.1103 PR-AUC and +0.0630 F2. Both 95 percent intervals were above zero. This supports the advantage of the selected recurrent aggregator over the static combination of the same seven inputs. The separate recall-difference interval included zero, so we do not claim that recall difference as independently established.'

    Set-ShapeText $deck.Slides.Item(31) 'Title 1' 'The Three Missed Conversations Were Short'
    Set-ChartSeries $deck.Slides.Item(31) 1 'Conversation length in turns' ([double[]]@(2,11,26)) @('Missed case 1','Missed case 2','Missed case 3')
    Set-ShapeText $deck.Slides.Item(31) 'Length comparison' 'Missed cases: 2, 11, and 26 turns. Correctly detected positives: lower quartile 36, median 61 turns.'
    Set-Notes $deck.Slides.Item(31) 'The three positives missed by the primary LSTM were 2, 11, and 26 turns long. Each was shorter than the 36-turn first quartile of correctly detected positives, whose median was 61 turns. This makes short-history testing a focused next step, but length does not prove the cause of a miss or establish when grooming began.'

    Set-ShapeText $deck.Slides.Item(32) 'Panel body' 'Objective 1: Static methods show detection and false-alert limits.`nObjective 2: GroomShield delivers a two-layer module and review interface.`nObjective 3: Primary LSTM found 41 of 44 positives, with three misses.`nGeneral objective: Broader conversation-level coverage for human review.'
    Set-Notes $deck.Slides.Item(32) 'These conclusions answer the approved objectives. We measured limitations of the tested static approaches, built the complete contextual and behavioral module, and improved the observed conversation-level detection tradeoff. The primary LSTM found 41 positives and missed three, compared with six misses for weighted scoring. Human review remains part of the intended workflow.'
    Set-ShapeText $deck.Slides.Item(33) 'Panel body' 'Test F2 cutoffs on contemporary external chats.`nBenchmark longer prefixes, concurrent traffic, and memory use.`nEvaluate moderator review outcomes and calibration.`nStudy early prefixes and independently annotate grooming onset.'
    Set-Notes $deck.Slides.Item(33) 'The local CPU benchmark answers part of the panel latency question, but production use needs representative traffic, longer chats, concurrent requests, deployment hardware, memory testing, and moderator outcomes. We also need external data reflecting current communication and separately reviewed onset annotations to study early detection. Caching or incremental computation could reduce repeated prefix processing.'
    Set-ShapeText $deck.Slides.Item(34) 'Title 1' 'GroomShield Reduced Missed Positives'
    Set-Notes $deck.Slides.Item(34) 'The primary seven-feature LSTM achieved the highest F2 point estimate and found 41 of 44 positives, with three missed conversations. The enhanced model found all 44 but produced more false alerts. The local benchmark shows both variants can run through the prototype on this CPU; deployment performance still needs a platform-level study. Thank you.'

    $latency = $deck.Slides.Item(33).Duplicate().Item(1)
    $latency.MoveTo(32)
    Set-ShapeText $latency 'Title 1' 'Local Turn-by-Turn Latency'
    Set-ShapeText $latency 'Panel body' 'CPU, localhost HTTP, one request at a time; 160 timed requests per LSTM.`nPrimary: median 267 ms; p95 709 ms; p99 830 ms; 3.39 requests/s.`nEnhanced: median 246 ms; p95 718 ms; p99 1,058 ms; 3.32 requests/s.`nLonger chats take longer because the demo recomputes the full history.'
    Set-Notes $latency 'We benchmarked each LSTM through the local HTTP demo path, including DistilBERT processing, feature computation, redaction, and JSON response. Forty timed requests at each of 1, 4, 8, and 16 turns give 160 per model. In the equal-length mix, the primary median was 267 milliseconds, p95 709, p99 830, and throughput 3.39 sequential requests per second. Enhanced was 246, 718, 1,058, and 3.32. Both variants reused the same upstream path. These are synthetic local CPU timings, not a real-time production guarantee. At 16 turns, median latency was about 0.6 second for each.'

    $deck.Save()
    Write-Output "Saved $target with $($deck.Slides.Count) slides."
} finally {
    if ($deck -ne $null) { $deck.Close() }
    if ($ppt -ne $null) { $ppt.Quit() }
}
