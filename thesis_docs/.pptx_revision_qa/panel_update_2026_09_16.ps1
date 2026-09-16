param([switch]$SkipRender)
$ErrorActionPreference = 'Stop'
$root = 'C:\Projects\THESIS'
$build = Join-Path $root 'tmp\presentation_panel_2026-09-16'
$source = Join-Path $root 'WASD - Thesis 2 - final revised.pptx'
$output = Join-Path $root 'WASD - Thesis 2 - panel revised.pptx'
$scriptPath = Join-Path $root 'thesis_docs\PRESENTATION_SPEAKER_SCRIPT.md'
New-Item -ItemType Directory -Path $build -Force | Out-Null
function RGB($r,$g,$b){ return [int]($r+256*$g+65536*$b) }
$blue=RGB 54 88 140; $ink=RGB 25 31 40; $green=RGB 37 118 86; $gold=RGB 213 154 22
function Text($s,$name,$text,$x,$y,$w,$h,$size=24,$bold=$false,$color=$ink){
    $sh=$s.Shapes.AddTextbox(1,$x,$y,$w,$h); $sh.Name=$name
    $sh.TextFrame.AutoSize=0; $sh.TextFrame.WordWrap=-1
    $sh.TextFrame.MarginLeft=2; $sh.TextFrame.MarginRight=2; $sh.TextFrame.MarginTop=2; $sh.TextFrame.MarginBottom=2
    $sh.TextFrame.TextRange.Text=$text; $sh.TextFrame.TextRange.Font.Name='Calibri Light'
    $sh.TextFrame.TextRange.Font.Size=$size; $sh.TextFrame.TextRange.Font.Bold=[int]$bold*-1; $sh.TextFrame.TextRange.Font.Color.RGB=$color
    $sh.TextFrame.TextRange.ParagraphFormat.Bullet.Visible=0
    return $sh
}
function Title($s,$text){
    $sh=@($s.Shapes | Where-Object { $_.Name -like 'Title*' })[0]
    $sh.TextFrame.TextRange.Text=$text; $sh.TextFrame.TextRange.Font.Size=34
    $sh.Left=65; $sh.Top=54; $sh.Width=785; $sh.Height=77
}
function ClearBody($s){
    for($i=$s.Shapes.Count;$i -ge 1;$i--){$sh=$s.Shapes.Item($i); if($sh.Name -notlike 'Title*'){$sh.Delete()}}
}
function Body($s,$title,$lines,$size=26){
    Title $s $title; ClearBody $s
    $sh=Text $s 'Panel body' ($lines -join "`r") 66 148 815 344 $size
    $sh.TextFrame.TextRange.ParagraphFormat.SpaceAfter=15
}
function Notes($s,$text,$sources){
    foreach($sh in @($s.NotesPage.Shapes)){
        try{$kind=$sh.PlaceholderFormat.Type}catch{continue}
        if($kind -eq 2){$sh.TextFrame.TextRange.Text="$text`r`rSources: $sources";return}
    }
    throw 'Notes placeholder unavailable'
}
function NewSlide($after,$title){
    $new=$base.Duplicate().Item(1); $new.MoveTo($after.SlideIndex+1); ClearBody $new; Title $new $title; return $new
}
function Table($s,$headers,$rows,$widths,$font=19,$top=150,$height=292){
    $shape=$s.Shapes.AddTable(($rows.Count+1),$headers.Count,54,$top,850,$height); $shape.Name='Evidence table'
    for($c=1;$c -le $headers.Count;$c++){$shape.Table.Columns.Item($c).Width=$widths[$c-1]}
    for($r=1;$r -le ($rows.Count+1);$r++){
      for($c=1;$c -le $headers.Count;$c++){
        $cell=$shape.Table.Cell($r,$c).Shape
        $cell.TextFrame.TextRange.Text=if($r -eq 1){$headers[$c-1]}else{$rows[$r-2][$c-1]}
        $cell.TextFrame.TextRange.Font.Name='Calibri';$cell.TextFrame.TextRange.Font.Size=$font;$cell.TextFrame.TextRange.Font.Color.RGB=$ink
        $cell.TextFrame.TextRange.Font.Bold=if($r -eq 1){-1}else{0}
        $cell.TextFrame.MarginLeft=8;$cell.TextFrame.MarginRight=8;$cell.TextFrame.MarginTop=6;$cell.TextFrame.MarginBottom=6
        $cell.TextFrame.VerticalAnchor=3;$cell.Fill.Solid();$cell.Fill.ForeColor.RGB=if($r -eq 1){RGB 224 232 241}else{RGB 255 255 255}
      }
    }; return $shape
}
function Chart($s,$categories,$series,$max,$format='0.0',$legend=$true){
    $shape=Text $s 'Results chart' 'Chart data attached for native chart generation' 62 145 824 297 24
    $spec=@{categories=$categories;series=$series;maximum=$max;number_format=$format;legend=$legend}
    $shape.AlternativeText=($spec | ConvertTo-Json -Depth 5 -Compress)
    return $shape
}
function DiagramBox($s,$name,$text,$x,$y,$w,$h,$fill,$size=20){
    $sh=$s.Shapes.AddShape(1,$x,$y,$w,$h);$sh.Name=$name;$sh.Fill.ForeColor.RGB=$fill;$sh.Line.ForeColor.RGB=$blue
    $sh.TextFrame.MarginLeft=8;$sh.TextFrame.MarginRight=8;$sh.TextFrame.MarginTop=5;$sh.TextFrame.MarginBottom=5
    $sh.TextFrame.TextRange.Text=$text;$sh.TextFrame.TextRange.Font.Name='Calibri';$sh.TextFrame.TextRange.Font.Size=$size
    $sh.TextFrame.TextRange.Font.Color.RGB=$ink;$sh.TextFrame.VerticalAnchor=3;$sh.TextFrame.TextRange.ParagraphFormat.Alignment=2
    return $sh
}
function Arrow($s,$x1,$y1,$x2,$y2){$line=$s.Shapes.AddLine($x1,$y1,$x2,$y2);$line.Line.ForeColor.RGB=$blue;$line.Line.Weight=2;$line.Line.EndArrowheadStyle=3}
$app=New-Object -ComObject PowerPoint.Application
$deck=$null
try{
  $deck=$app.Presentations.Open($source,0,0,0)
  $original=@{};for($i=1;$i -le $deck.Slides.Count;$i++){$original[$i]=$deck.Slides.Item($i)}
  $base=$original[8]
  $ch1='thesis_docs/Finals_Revised_Paper_WASD.md'
  $ch4='thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md'
  $ch5='thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md'
  Notes $original[1] 'Good day. Our study developed a chat moderation module that combines language context with patterns across a conversation. We tested whether this combination could reduce the positive conversations missed by keyword rules and static scoring. I will connect our objectives to the methods, explain the model, and show the results.' "$ch1, title and Sections 1.2-1.3"
  Notes $original[3] 'The problem begins with how conversations develop. A single turn may provide very little information. Our study examines whether recent context and the longer sequence together improve the evidence available to a moderator.' "$ch1, Section 1.1"
  Notes $original[4] 'Keyword filters remain useful for explicit language. The difficulty is that a conversation can develop through ordinary wording, indirect requests, or changing interaction patterns. Reports also depend on someone recognizing a problem. This motivated us to develop an additional module that examines context and the conversation sequence.' "$ch1, Section 1.1"
  Notes $original[5] 'Our research asks whether a system that follows the development of a conversation can identify more positive cases than static methods. We built the architecture to address that problem, then selected a dataset with ordered conversations and persistent speaker identifiers to evaluate it.' "$ch1, Section 1.2"
  Notes $original[6] 'These slide questions summarize the unchanged research questions in the paper. The first two examine existing moderation and its limits. The third concerns the architecture we developed. The fourth asks whether the completed system improves recall and reduces missed cases. Recall means the fraction of positive conversations that the model identifies.' "$ch1, Section 1.2"
  Notes $original[7] 'The objectives remain the ones approved for the study. We evaluate conventional approaches, develop a module using context and behavioral patterns, and assess the improvement in detection. The next two slides show the alignment between these objectives, our methods, and the resulting evidence. The slide wording is abbreviated for presentation.' "$ch1, Section 1.3"
  $a1=NewSlide $original[7] 'Research Alignment: Existing Methods'
  $null=Table $a1 @('Problem','Question / Objective','Method','Results evidence') @(
    @('How well do existing systems detect relevant conversations?','RQ1 / Objective 1: Evaluate existing moderation.','Test the keyword rule on the same held-out conversations.','Keyword rule: 61.36% recall and 17 missed cases.'),
    @('Static methods can miss meaning that develops across turns.','RQ2 / Objective 1: Examine the limits of static methods.','Compare keyword and score aggregation with the trajectory LSTM.','LSTM gains over maximum Layer 1: +0.3630 PR-AUC and +0.3864 recall.')
  ) @(198,211,221,220) 20 152 295
  Notes $a1 'This is the first half of the alignment table, shortened to keep one clear entry in each cell. Research Questions 1 and 2 both support Objective 1. We assessed the keyword rule on the same test conversations as the other methods. It identified 27 of 44 positives and missed 17. We also tested maximum Layer 1 aggregation, which uses the highest contextual score in a conversation. Comparing these methods with the LSTM establishes where the sequence model improves over static aggregation. We did not run a separate experiment against an operational user-report system.' "Alignment Table.docx, rows 1-2; $ch4, Tables 4.1-4.2"
  $a2=NewSlide $a1 'Research Alignment: Module and Improvement'
  $null=Table $a2 @('Problem','Question / Objective','Method','Results evidence') @(
    @('Chat analysis needs both context and behavioral development.','RQ3 / Objective 2: Develop the AI moderation module.','Combine DistilBERT, seven trajectory features, and an LSTM.','Completed two-layer module and sequential review interface.'),
    @('The module must improve detection and reduce missed cases.','RQ4 / Objective 3: Measure recall and false-negative reduction.','Use a locked test and paired comparisons across author groups.','LSTM: 90.91% recall and four misses; 50% fewer misses than weighted scoring.')
  ) @(198,211,221,220) 20 152 295
  Notes $a2 'The second half connects development and evaluation. For Objective 2, we implemented the complete two-layer pipeline and the review interface. For Objective 3, we assessed it on the locked held-out test. The primary LSTM identified 40 of 44 positives, so its recall was 90.91 percent. Its four misses were half the weighted scorer''s eight and 76.5 percent fewer than the keyword rule''s seventeen. These are measured comparisons against implemented methods. The module can complement reporting workflows, while an actual comparison with moderator reporting remains a separate study.' "Alignment Table.docx, rows 3-4; $ch4, Tables 4.1-4.2; $ch5, Section 5.2"
  Body $original[8] 'What the Study Built' @('DistilBERT reads each turn with recent context.','Seven features track changes across the conversation.','An LSTM uses the feature sequence to score the conversation.','The interface helps a moderator decide what to review.')
  Notes $original[8] 'The system has two learned layers. DistilBERT processes the current turn with up to two preceding turns. We then track seven features across the conversation. The LSTM combines that sequence into a conversation score. The practical output is a priority for human review. The moderator interprets the content and decides what action is appropriate.' "$ch1, Sections 3.1 and 3.4"
  Body $original[9] 'Dataset and Evaluation Scope' @('We selected PAN-2012 to evaluate the proposed architecture.','18,567 eligible two-speaker conversations and 218,114 turns.','The test evaluates conversation decisions on unseen author groups.','The completed experiment uses offline sequential replay.')
  Notes $original[9] 'PAN-2012 met the study''s need for a large collection of ordered conversations and stable speaker identifiers. For the evaluated outcome, a positive conversation contains at least one author on the official predator list. Layer 1 learns from author-derived supervision, and Layer 2 learns the conversation label. A turn-level score is an intermediate signal, so we do not interpret it as an independently verified grooming label for that message. This gives every comparison the same measurable conversation outcome.' "$ch1, Sections 1.4 and 3.3.1; $ch4, Section 4.1"
  Body $original[10] 'Why the Study Matters' @('The study tests whether sequence modeling improves detection.','The complete module supports conversation review.','The comparison measures both missed cases and false alerts.','The evaluation keeps author groups separate across partitions.')
  Notes $original[10] 'The contribution is a complete contextual and behavioral architecture with a controlled comparison. It delivers a working review interface and evidence that learned aggregation improves detection over static use of the same inputs. For a moderation workflow, both kinds of errors matter: missed positive conversations and false alerts that consume review time.' "$ch1, Section 1.5; $ch4, Section 4.7"
  Notes $original[11] 'The literature supports two parts of our design: understanding language in context and following how interaction develops over time. The theory section explains why a sequence representation is appropriate.' "$ch1, Chapter II"
  Notes $original[12] 'Transformers help represent the current wording together with recent context. The LSTM addresses a different scale: how the evidence changes across the conversation. We evaluate their combination through the completed two-layer module.' "$ch1, Sections 2.1-2.3"
  Body $original[13] 'Theory and Dataset Selection' @('OGDM describes grooming as a developing conversational process.','The model tracks persistence, changes, and interaction patterns.','PAN-2012 provides ordered conversations and persistent speaker IDs.','These properties support trajectory analysis and author-group testing.') 25
  Notes $original[13] 'Our theoretical basis is the Online Grooming Discourse Model, or OGDM. It describes interrelated conversational processes that can recur or overlap rather than always following one fixed order. That motivates tracking how evidence persists and changes across turns. We then selected PAN-2012 as the evaluation dataset because it provides the chronology and participant identifiers needed for this design.' "$ch1, Section 2.3 and references [11], [13]"
  $ogdm=NewSlide $original[13] 'How OGDM Informs the Features'
  $null=Table $ogdm @('Conversational property','Features used') @(
    @('Accumulation and persistence','Peak score, current score, spike count'),
    @('Escalation and retreat','Rate of change, spike-then-drop'),
    @('Movement in conversational content','Topic distance from the benign training reference'),
    @('Interaction structure','Cumulative turn-taking imbalance')
  ) @(355,495) 22 145 284
  $null=Text $ogdm 'Interpretation' 'The LSTM learns how these signals develop together across turns.' 64 447 822 43 22
  Notes $ogdm 'This table connects theory to computation. Peak and current scores, together with spike count, represent persistence and accumulation of contextual evidence. Rate of change and spike-then-drop represent increases and retreats. Topic distance measures movement away from a reference built from negative training conversations. Turn-taking imbalance summarizes participation within the pair. These are indicators motivated by the theory. We have not independently annotated them as OGDM stages, and the experiment does not establish the individual causal contribution of each feature.' "$ch1, Sections 2.3 and 3.3.4; $ch4, Section 4.5"
  Notes $original[14] 'I will now explain the model architecture, how we separated the data, and how we selected the operating threshold before the final test.' "$ch1, Chapter III"
  $arch=$original[15];Title $arch 'AI Model Architecture';ClearBody $arch
  $pale=RGB 236 242 249;$light=RGB 236 246 239
  $null=DiagramBox $arch 'Current turn input' "Current turn`r+ up to two`rprevious turns" 48 201 160 104 $pale 22
  $null=DiagramBox $arch 'Context classifier' "Layer 1: DistilBERT`rAuthor-derived`rproxy score" 245 153 217 97 $pale 21
  $null=DiagramBox $arch 'Base encoder' "Fixed base encoder`rCurrent-turn embedding`r+ training reference" 245 337 217 97 $pale 19
  $null=DiagramBox $arch 'Trajectory features' "Seven features`r`rPeak / current score`rSpike count / drop`rRate of change`rTopic distance`rTurn imbalance" 500 153 219 281 $pale 20
  $null=DiagramBox $arch 'Sequence model' "Layer 2: LSTM`rOrdered feature sequence" 755 153 163 105 $light 21
  $null=DiagramBox $arch 'Review decision' "Conversation score`rFrozen threshold`rHuman review" 755 337 163 97 $light 20
  Arrow $arch 208 224 227 224;Arrow $arch 227 224 227 201;Arrow $arch 227 201 245 201
  Arrow $arch 208 278 227 278;Arrow $arch 227 278 227 385;Arrow $arch 227 385 245 385
  Arrow $arch 462 201 500 201;Arrow $arch 462 385 500 385;Arrow $arch 719 201 755 201;Arrow $arch 836 258 836 337
  $null=Text $arch 'Architecture summary' 'Each new turn updates the feature sequence and the conversation score.' 64 461 830 42 22
  Notes $arch 'Read the diagram from left to right. The current turn and up to two preceding turns enter the fine-tuned DistilBERT classifier. Its output is an author-derived contextual proxy score. A separate fixed base encoder represents the current turn for topic-distance calculation against the benign training reference. The pipeline combines those signals with speaker-turn information into seven features. The LSTM processes the ordered feature sequence and outputs a conversation score. A threshold selected on validation determines which conversations receive a flag for human review. The primary LSTM has seven inputs per turn. The enhanced experiment additionally feeds 768 embedding values into its recurrent model.' "$ch1, Sections 3.3.2-3.4.2; thesis_docs/assets/AI_Model_Architecture_Diagram.svg"
  Body $original[16] 'Data Preparation and Controls' @('Keep valid, ordered conversations with two distinct speakers.','Build the benign reference and keyword list from training data.','Use validation to choose checkpoints, settings, and thresholds.','Freeze these choices before the final test.') 26
  Notes $original[16] 'The controls make the comparison reproducible. We preserve original conversation and turn identifiers, maintain chronological context, and restrict this experiment to two-speaker conversations. Derived resources come from training data. Validation is used for selection. The held-out final test is then evaluated with those choices already fixed.' "$ch1, Sections 3.3 and 3.5"
  $part=NewSlide $original[16] 'Why Authors Stay in One Partition'
  Body $part 'Why Authors Stay in One Partition' @('Conversations that share an author belong to one connected group.','Each entire group goes into training, validation, or test.','This prevents the model from meeting the same author across splits.','The final test contains unseen author groups.') 27
  Notes $part 'Suppose one conversation contains authors A and B, and another contains B and C. The shared author B connects the conversations, so both stay in the same partition. The same rule applies to every connected group, including indirect connections. Otherwise the model could benefit from recognizing recurring participants or their language during testing. We verified zero overlap of conversations, authors, and connected components. The bootstrap analysis resamples these whole groups for the same reason: conversations linked by an author should not be treated as independent observations.' "$ch1, Sections 3.3.3 and 3.5.2; $ch4, Section 4.1"
  Notes $original[17] 'The central comparison uses the same seven trajectory features. The weighted scorer combines them statically, while the LSTM learns a recurrent sequence model. This evaluates the selected aggregation methods with matched inputs. Keyword matching and maximum Layer 1 aggregation provide additional baselines. We report the enhanced LSTM separately because it also receives 768 embedding values. Feature-removal and ordering ablations would be needed to isolate individual design contributions.' "$ch1, Section 3.4.3; $ch4, Sections 4.2-4.5"
  Body $original[18] 'Evaluation Measures' @('PR-AUC measures the precision-recall tradeoff across thresholds.','Precision measures how many flagged conversations are positive.','Recall measures how many positive conversations are found.','False positives and false negatives show the actual error counts.') 25
  Notes $original[18] 'Because the test contains only 44 positive conversations among 1,862, we report precision-recall measures together with actual error counts. PR-AUC summarizes performance across thresholds. Precision measures the proportion of alerts that are positive. Recall measures the proportion of all positives that we find. We also report uncertainty using 2,000 bootstrap resamples of connected-author groups.' "$ch1, Section 3.5.2; $ch4, Sections 4.1-4.3"
  $f=NewSlide $original[18] 'Why We Use F0.5'
  Body $f 'Why We Use F0.5' @('F0.5 gives more weight to precision when choosing the threshold.','False alerts consume moderator review capacity.','Recall and missed cases still measure the detection objective.','Result: 85.11% precision, 90.91% recall, and four missed cases.') 26
  Notes $f 'F0.5 and recall serve different purposes in this experiment. We used validation F0.5 to choose an operating threshold that gives greater weight to precision, because a review queue has limited capacity and false alerts consume that capacity. In the F-beta formulation, beta of one-half weights precision four times as much as recall. We then separately report recall and false-negative counts to answer the research objective about missed cases. The selected model reached 85.11 percent precision and 90.91 percent recall on the final test, with seven false alerts and four missed positives. The operating threshold was 0.9688298. We did not optimize that threshold on the final test, and this rationale does not substitute for a future study of actual moderator workload.' "$ch1, Section 3.5.2; $ch4, Tables 4.1-4.2 and Section 4.7"
  Notes $original[19] 'These results come from the frozen held-out evaluation. The following table and graphs show the same accepted Chapter IV figures.' "$ch4, Tables 4.1-4.2"
  Notes $original[20] 'The training set contains 13,031 conversations, validation contains 1,827, and the final test contains 1,862. There are 44 positive and 1,818 negative conversations in the final test. The manifest also retains 1,847 excluded historical-test conversations for complete accounting. We kept every connected-author group in one partition and froze all selection decisions before testing.' "$ch4, Section 4.1"
  Title $original[21] 'Held-Out Results'
  Notes $original[21] 'This table shows all five methods. The primary LSTM reached PR-AUC of 0.9153, F0.5 of 0.8621, precision of 0.8511, and recall of 0.9091. It found 40 of the 44 positive conversations and made seven false alerts. The main architectural comparison is against the weighted scorer because both receive seven features. The enhanced LSTM has higher point estimates with additional embedding inputs. The paired comparison does not establish a performance difference between the two LSTMs.' "$ch4, Tables 4.1-4.2"
  $names=@('Keyword','Maximum L1','Weighted','Primary LSTM','Enhanced LSTM')
  $perf=NewSlide $original[21] 'Detection Performance Across Methods'
  $null=Chart $perf $names @(@{name='PR-AUC';values=@(.4451,.5523,.8050,.9153,.9483);color=$blue},@{name='F0.5';values=@(.6888,.5529,.7500,.8621,.8836);color=$green}) 1.1 '0.0000'
  $null=Text $perf 'Graph interpretation' 'Primary comparison: weighted scorer and primary LSTM use the same seven features.' 65 456 820 58 21
  Notes $perf 'The blue bars show PR-AUC and the green bars show F0.5. Higher is better for both. The primary LSTM improves both measures over the keyword rule, maximum Layer 1 aggregation, and weighted scoring. The clearest architecture comparison is weighted scoring versus the primary LSTM because the inputs match. The enhanced LSTM also receives embeddings. These bars show point estimates, while the paper reports confidence intervals and paired differences.' "$ch4, Tables 4.1-4.2"
  $rec=NewSlide $perf 'The Primary LSTM Found 40 of 44 Positives'
  $null=Chart $rec $names @(@{name='Recall';values=@(.6136,.5227,.8182,.9091,.9318);color=$green}) 1.1 '0.0%' $false
  $null=Text $rec 'Recall interpretation' 'Detected positives: keyword 27, maximum L1 23, weighted 36, primary 40, enhanced 41.' 65 456 820 62 21
  Notes $rec 'Recall answers the question most directly connected to our third objective: how many positive conversations did we find? The primary LSTM found 40 out of 44, compared with 27 for the keyword rule, 23 for maximum Layer 1, and 36 for the weighted scorer. The enhanced LSTM found 41. The paired evidence supports the primary model''s improvement over the three static baselines. One extra detected case does not establish superiority for the enhanced LSTM.' "$ch4, Tables 4.1-4.2"
  $err=NewSlide $rec 'Fewer Missed Cases and False Alerts'
  $null=Chart $err $names @(@{name='Missed positives (FN)';values=@(17,21,8,4,3);color=$gold},@{name='False alerts (FP)';values=@(11,18,13,7,6);color=$blue}) 25 '0'
  $null=Text $err 'Error interpretation' 'Against weighted scoring: missed cases fell from 8 to 4 and false alerts from 13 to 7.' 65 456 820 62 22
  Notes $err 'Lower bars are better here. The primary LSTM cut the weighted scorer''s missed positives from eight to four, a 50 percent reduction, while also cutting false alerts from thirteen to seven. Compared with keyword matching, it reduced missed cases from seventeen to four, a 76.5 percent reduction. These counts show that the improved recall was accompanied by fewer false alerts at the selected operating points. The units are conversations, not individual messages.' "$ch4, Tables 4.1 and Section 4.7"
  Body $original[22] 'Sequence Modeling Added Value' @('The primary LSTM and weighted scorer use the same seven inputs.','PR-AUC improvement: +0.1103, with 95% interval [0.0251, 0.2254].','F0.5 improvement: +0.1121, with 95% interval [0.0194, 0.2336].','Both intervals stay above zero, supporting the improvement.') 25
  Notes $original[22] 'We compared the models within the same 2,000 bootstrap resamples of author groups. For primary LSTM minus weighted scorer, the PR-AUC improvement was 0.1103 and the F0.5 improvement was 0.1121. Both paired 95 percent intervals remain above zero. This supports an advantage for the learned recurrent aggregator over the selected static combination of the same features. It establishes the architecture comparison as tested. It does not by itself quantify how much each feature or temporal ordering contributes individually.' "$ch4, Table 4.2 and Section 4.5"
  $short=NewSlide $original[22] 'The Four Missed Conversations Were Short'
  $null=Chart $short @('Missed case 1','Missed case 2','Missed case 3','Missed case 4') @(@{name='Conversation length in turns';values=@(2,11,13,26);color=$gold}) 40 '0' $false
  $null=Text $short 'Length comparison' 'Missed cases: 2-26 turns. Correctly detected positives: lower quartile 36, median 62 turns.' 65 453 820 67 22
  Notes $short 'All four missed positives were short conversations: two, eleven, thirteen, and twenty-six turns. Each was shorter than the lower quartile of correctly detected positives, which was thirty-six turns. Their median was sixty-two. This is the main observed error pattern and is consistent with limited accumulated sequence evidence. It does not prove that length caused each miss or establish a minimum safe number of turns. We have not annotated the first onset of grooming, so these lengths cannot measure detection delay after onset. A future study should measure performance at fixed conversation prefixes, with onset annotations when evaluating time from onset.' "$ch4, Section 4.6"
  Body $original[23] 'Conclusions by Research Objective' @('Objective 1: Static methods missed more positive conversations.','Objective 2: We delivered the two-layer module and review interface.','Objective 3: The primary LSTM reached 90.91% recall with four misses.','General objective: The contextual and behavioral module improved detection over the tested baselines.') 25
  Notes $original[23] 'These conclusions answer the approved objectives. First, the controlled comparison established the limitations of the tested static methods. Second, we implemented the complete contextual and behavioral module with a working review interface. Third, we measured higher recall and fewer false negatives, including half as many misses as weighted scoring. Together, the architecture and comparative results support the general objective of enhancing chat moderation. Our measured improvement is against the implemented keyword and score-based baselines.' "$ch5, Section 5.2"
  $next=NewSlide $original[23] 'Next Evaluation Steps'
  Body $next 'Next Evaluation Steps' @('Test transfer to contemporary chats and Filipino / Taglish data.','Measure latency, throughput, and moderator review outcomes.','Evaluate early prefixes and obtain expert onset annotations.','Test individual features and extend to multi-party conversations.') 26
  Notes $next 'The next stage is to test the completed system in conditions closer to a platform workflow. Contemporary external data can assess how performance transfers to current language and interaction patterns. Latency testing should measure the complete per-turn pipeline, including both transformer processing and sequence scoring, with median, p95, p99, and throughput. Expert-reviewed onset annotations are needed if we want to measure how quickly the model reacts after grooming begins. Ablations can identify which model components contribute most, and a separate protocol can extend the current two-speaker design to group conversations. The current demo provides sequential replay; production real-time performance remains to be measured.' "$ch5, Section 5.3; thesis_docs/PANEL_COMMENTS_MATRIX.md"
  Notes $original[24] 'Our main result is that the learned trajectory model improved conversation detection over the tested static approaches, using the same seven inputs as the weighted comparator. It identified forty of forty-four positives with seven false alerts. Thank you. We welcome your questions about the architecture, data partitions, metric choice, and results.' "$ch4, Tables 4.1-4.2; $ch5, Section 5.2"
  # Template assets remain available but do not interrupt the defense slideshow.
  $original[2].SlideShowTransition.Hidden=-1
  foreach($i in 25..29){$original[$i].SlideShowTransition.Hidden=-1;Notes $original[$i] 'Reference asset retained from the original presentation. This slide is hidden during the main defense.' 'Original presentation template'}
  # Put the exact adviser-locked objective wording in notes without overloading slides.
  $md=Get-Content (Join-Path $root $ch1) -Raw -Encoding UTF8
  $objectives=([regex]::Match($md,'(?s)## 1\.3 .*?(?=\r?\n## 1\.4 )')).Value
  if(-not $objectives){throw 'Could not extract the exact objective section'}
  foreach($sh in @($original[7].NotesPage.Shapes)){try{$kind=$sh.PlaceholderFormat.Type}catch{continue};if($kind -eq 2){$sh.TextFrame.TextRange.Text+="`r`rExact approved wording:`r$objectives"}}
  $deck.SaveAs($output,24)
  $outline=[Collections.Generic.List[string]]::new()
  $outline.Add('# Thesis Defense Speaker Script');$outline.Add('');$outline.Add('Updated September 16, 2026. Slide numbers match WASD - Thesis 2 - panel revised.pptx. Hidden template slides are identified below.');$outline.Add('')
  $inventory=@();$fit=@()
  foreach($s in @($deck.Slides)){
    $titleShape=@($s.Shapes | Where-Object Name -like 'Title*')[0]
    $title=if($titleShape){$titleShape.TextFrame.TextRange.Text -replace "`r",' '}else{'Template asset'}
    $hidden=$s.SlideShowTransition.Hidden -eq -1
    $notes='';foreach($sh in @($s.NotesPage.Shapes)){try{$kind=$sh.PlaceholderFormat.Type}catch{continue};if($kind -eq 2){$notes=$sh.TextFrame.TextRange.Text}}
    $outline.Add("## Slide $($s.SlideIndex): $title$(if($hidden){' [hidden]'})");$outline.Add('');$outline.Add(($notes -replace "`r", "`n"));$outline.Add('')
    $tables=0;$charts=0
    foreach($sh in @($s.Shapes)){
      if($sh.HasTable -eq -1){$tables++}
      if($sh.HasChart -eq -1){$charts++}
      if($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1){
        $bound=$sh.TextFrame.TextRange.BoundHeight;$available=$sh.Height-$sh.TextFrame.MarginTop-$sh.TextFrame.MarginBottom
        if($bound -gt $available+3 -and -not $hidden){$fit+=@{slide=$s.SlideIndex;shape=$sh.Name;bound=$bound;available=$available}}
      }
    }
    $inventory+=@{slide=$s.SlideIndex;title=$title;hidden=$hidden;tables=$tables;charts=$charts;has_notes=([bool]$notes)}
  }
  [IO.File]::WriteAllText($scriptPath,($outline -join "`n"),[Text.UTF8Encoding]::new($false))
  $receipt=@{date='2026-09-16';source=$source;source_sha256=(Get-FileHash $source).Hash;output=$output;output_sha256=(Get-FileHash $output).Hash;slides=$deck.Slides.Count;inventory=$inventory;text_fit_warnings=$fit;render_passes=0;method='PowerPoint COM fallback: skill dependency loader and artifact-tool unavailable';frozen_models_changed=$false;source_references=@($ch1,$ch4,$ch5,'Alignment Table.docx');speaker_script=$scriptPath}
  if(-not $SkipRender){$renderDir=Join-Path $build 'final_render';New-Item -ItemType Directory -Path $renderDir -Force|Out-Null;foreach($s in @($deck.Slides)){$s.Export((Join-Path $renderDir ('slide-{0:00}.png' -f $s.SlideIndex)),'PNG',1280,720)};$receipt.render_passes=1}
  $receipt|ConvertTo-Json -Depth 9|Set-Content (Join-Path $root 'thesis_docs\.pptx_revision_qa\panel_revision_2026_09_16_receipt.json') -Encoding UTF8
  "Saved $output";"Slides: $($deck.Slides.Count). Fit warnings: $($fit.Count)";$fit|ConvertTo-Json -Depth 4
} finally {
  if($deck){$deck.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}
  [Runtime.InteropServices.Marshal]::ReleaseComObject($app)|Out-Null
}
