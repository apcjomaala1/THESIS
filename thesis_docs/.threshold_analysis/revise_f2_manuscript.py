"""Apply the approved Markdown revision using verified F2 evaluation receipts."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, difflib
ROOT=Path(__file__).resolve().parents[2]
D=ROOT/"thesis_docs"
TITLE="GroomShield: Detecting Grooming-Related Interactions in Chat Conversations Using DistilBERT and LSTM-Based Behavioral Sequence Modeling"
r=json.loads((D/".threshold_analysis/f2_test_reanalysis.json").read_text(encoding="utf-8"))
for p,h in r["input_hashes"].items():
    assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
files={}
def read(name):
    text=(D/name).read_text(encoding="utf-8")
    files[name]=[text,text]
    return text
def para(text,prefix,new):
    parts=text.split("\n\n")
    hit=[i for i,p in enumerate(parts) if p.startswith(prefix)]
    assert len(hit)==1,(prefix,len(hit))
    parts[hit[0]]=new
    return "\n\n".join(parts)
def between(text,a,b):
    return text.split(a,1)[1].split(b,1)[0]
main=read("Finals_Revised_Paper_WASD.md")
protected={
"objectives":between(main,"## 1.3 Objectives of the Study","## 1.4 Scope and Limitations"),
"questions":between(main,"This study seeks to answer the following questions:","For quantitative evaluation,"),
"chapter2":between(main,"# II. RELATED WORK","# III. METHODOLOGY"),
"references":main.split("# References",1)[1]}
main=para(main,"__*AI-Based Detection",f"__*{TITLE}*__")
changes=[
("This study develops an AI-powered moderation module",
"This study develops GroomShield, an AI-powered moderation module that combines contextual language analysis with behavioral sequence modeling. Layer 1 uses DistilBERT to evaluate the current turn together with up to two preceding turns. Layer 2 uses an LSTM to aggregate a chronological sequence of seven trajectory features reflecting score level and change, semantic movement, and speaker-turn structure. GroomShield complements keyword filters and reporting mechanisms by identifying conversations that warrant human review, with recall and false-negative reduction as its central performance priorities."),
("The study compares the proposed seven-feature LSTM",
"The study compares the proposed seven-feature LSTM with a training-derived keyword rule, maximum Layer 1 proxy aggregation, and a validation-fitted weighted trajectory scorer. A secondary LSTM supplemented with 768-dimensional base DistilBERT embeddings is evaluated separately. All methods use identical author-disjoint conversation partitions. F2 is the principal final-cutoff selection criterion, supported by recall, false-negative counts, precision, PR-AUC, and paired performance differences."),
("The approach is particularly relevant to human-review workflows",
"The approach is particularly relevant to moderation workflows seeking broader detection coverage, including conversations not identified by keyword filters or reports. Keyword rules, contextual classifiers, sequence models, and human escalation policies operate as complementary safeguards. F2 aligns the conversation-level decision rule with the study's priority of reducing missed positive conversations; precision and false-positive counts document the accompanying tradeoff."),
("The research additionally contributes a reproducible evaluation framework",
"The research additionally contributes a reproducible evaluation framework for conversational data: connected-author partitioning, training-only construction of derived resources, validation-based checkpoint and threshold selection, preserved test-score artifacts, and component-grouped uncertainty estimation. These controls distinguish model learning from operating-threshold analysis and support repeatable comparison of the same methods."),
("This study uses a developmental and experimental research design",
"This study uses a developmental and experimental research design [15] to build and evaluate GroomShield, an offline conversation-analysis prototype. The research centers on the two-layer contextual and behavioral sequence architecture. PAN12 was selected as an appropriate evaluation corpus, with the measurable outcome operationalized as **conversation-level identification of conversations containing at least one author on the dataset's official predator list**. This outcome is applied consistently across model development and evaluation."),
("The training partition is used for parameter estimation.",
"The training partition is used for parameter estimation. After partitioning, negative Layer 1 training rows were downsampled to three negatives per positive row; validation and test distributions remained untouched. Validation supplies checkpoint selection, hyperparameter selection, comparator fitting, and threshold selection. The original test evaluation produced preserved conversation scores; the revised F2 policy is evaluated from those same scores using validation-selected cutoffs, as described in Section 3.5.1."),
("The principal architecture comparison is the seven-feature LSTM",
"The principal architecture comparison is the seven-feature LSTM versus the seven-feature weighted scorer. The F2 analysis holds learned parameters, weighted-scorer coefficients, keyword resources, and feature definitions fixed and selects each scored method's final cutoff independently on validation data. It compares fixed models under an F2 operating policy, not a new F2-directed hyperparameter search or weighted-scorer refit. The raw Layer 1 baseline uses its actual positive-class score directly and is not passed through the weighted scorer or another sigmoid.")]
for p,n in changes:main=para(main,p,n)
main=main.replace(
"The checkpoint is selected using validation PR-AUC, and its operating threshold is selected separately on validation data using F0.5.",
"The checkpoint was selected using validation PR-AUC, and its original diagnostic binary threshold was selected using F0.5. Layer 2 consumes the continuous positive-class score, not this diagnostic binary decision; the Layer 1 checkpoint and diagnostic threshold remain unchanged.")
main=main.replace(
"Both searches use seed 42 and select by validation PR-AUC with validation F0.5 as the first tie-break criterion.",
"Both completed searches used seed 42 and validation PR-AUC with validation F0.5 as the first tie-break criterion. These checkpoints are retained; F2 changes their final conversation cutoffs, not the training loss, learned weights, or checkpoint selection.")
term="Conversation-Level Endpoint - The primary measurable outcome used in the experiment: whether a dyadic PAN12 conversation contains at least one author included in the official predator-author list."
assert term in main
main=main.replace(term,term+"\n\nF2 Score - A precision-recall summary that places greater weight on recall. Validation F2 selects the final conversation cutoffs, aligning the operating policy with false-negative reduction.\n\nGroomShield - The proposed conversation-analysis module combining context-conditioned DistilBERT scoring with LSTM-based behavioral sequence modeling.")
evaluation=r"""## 3.5 Evaluation/Validation

### 3.5.1 Validation-Based F2 Threshold Selection and Test-Score Analysis

Training, checkpoint selection, feature construction, and comparator fitting use the original training and validation partitions. The selected DistilBERT and LSTM checkpoints, weighted-scorer coefficients, keyword lexicon, and seven-feature definitions are retained. The revised operating policy selects final conversation cutoffs by maximizing validation F2. Each scored method is evaluated at every distinct saved validation score; a score at or above the cutoff produces a positive decision. Ties are resolved by higher recall, then higher precision, then the higher cutoff. The keyword rule remains binary, so a cutoff of 1.0 gives the same decisions as its original 0.5 cutoff.

The F2 policy was adopted after the original F0.5 test evaluation. Its cutoffs are selected exclusively from the 1,827 validation conversations and applied unchanged to the saved scores for the 1,862-conversation test partition. These F2 results are a revised-policy analysis of the previously evaluated, author-disjoint test partition, not a new untouched holdout. No test-score threshold search, retraining, checkpoint reselection, or new model inference is performed.

The analysis verifies identical validation populations across methods, reproduces the original test predictions and metrics, and preserves the original evaluation artifacts. Every method is evaluated on the same test conversation IDs, and all outcomes are retained regardless of which method performs best. F2 applies to the final conversation decision; existing Layer 1 diagnostic and feature-construction thresholds remain unchanged.

### 3.5.2 Metrics and Comparative Analysis

The unit of evaluation is the conversation, with \(Y_c\) as ground truth. The primary reporting measures are recall, false-negative count, and F2. Precision, false-positive count, specificity, F1, PR-AUC, and ROC-AUC characterize the complete detection tradeoff. Let \(P\) and \(R\) denote precision and recall:

\[
P=\frac{TP}{TP+FP}, \qquad
R=\frac{TP}{TP+FN},
\]

\[
F_1=\frac{2PR}{P+R}, \qquad
F_2=\frac{5PR}{4P+R}
=\frac{5TP}{5TP+4FN+FP}.
\]

F2 is selected because the research aims to identify positive conversations missed by keyword and static-score approaches. Its formulation assigns a coefficient of four to false negatives and one to false positives, emphasizing recall without ignoring precision. This is a recall-oriented precision-recall objective, not unconstrained recall maximization or an empirically established four-to-one operational harm ratio. False alerts remain reported, while reducing moderator workload is not the principal optimization claim.

Validation PR-AUC selected the retained checkpoints. PR-AUC remains important because positive conversations are rare; a cutoff change does not change PR-AUC or ROC-AUC. Ninety-five-percent percentile intervals and paired method-difference intervals use 2,000 bootstrap resamples of connected-author components with seed 42. All conversations in each sampled component remain grouped, with identical draws across methods. Threshold-dependent intervals are recalculated for F2 decisions; unchanged ranking-metric intervals are retained after scores and point estimates are verified. These intervals are conditional on fixed models and selected cutoffs and do not incorporate selection uncertainty.

Prefix-level scores show how the conversation score develops as evidence accumulates. The primary result uses the final valid turn; intermediate values and first threshold crossings are not validated grooming-onset labels. A separate onset study requires expert-reviewed first-onset annotations and time-to-detection evaluation.

"""
a=main.index("## 3.5 Evaluation/Validation");b=main.index("## 3.6 Ethical Considerations")
main=main[:a]+evaluation+main[b:]
assert between(main,"## 1.3 Objectives of the Study","## 1.4 Scope and Limitations")==protected["objectives"]
assert between(main,"This study seeks to answer the following questions:","For quantitative evaluation,")==protected["questions"]
assert between(main,"# II. RELATED WORK","# III. METHODOLOGY")==protected["chapter2"]
assert main.split("# References",1)[1]==protected["references"]
files["Finals_Revised_Paper_WASD.md"][1]=main

old4=read("CHAPTER_IV_RESULTS_AND_DISCUSSION.md")
intro=old4.split("## 4.2",1)[0].replace("evaluated after the pipeline and reporting rules were frozen.",
"excluded from parameter fitting; its saved scores are used for the revised F2 analysis.")
features=between(old4,"## 4.5 Interpretation of the Seven-Feature Trajectory","## 4.6")
methods=list(r["results"])
names={"keyword":"Keyword rule","raw_layer1":"Maximum Layer 1 proxy","weighted":"Weighted scorer","lstm_trajectory7":"Primary trajectory LSTM","lstm_enhanced775":"Enhanced LSTM"}
inputs={"keyword":"50 training-derived unigram/bigram terms","raw_layer1":"Maximum contextual proxy score","weighted":"Weighted combination of seven trajectory features","lstm_trajectory7":"Sequence of seven trajectory features","lstm_enhanced775":"Seven features plus 768-dimensional embeddings"}
def ci(key,metric):
    m=r["results"][key];b=m["confidence_intervals"][metric]
    return f"{m['test'][metric]:.4f} [{b['lower']:.4f}, {b['upper']:.4f}]"
t1=["| Method | Input representation | PR-AUC [95% CI] | ROC-AUC [95% CI] | F2 [95% CI] | Precision | Recall | Specificity | TP | FP | FN | TN |",
"|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for k in methods:
    m=r["results"][k]["test"]
    t1.append(f"| {names[k]} | {inputs[k]} | {ci(k,'pr_auc')} | {ci(k,'roc_auc')} | {ci(k,'f2')} | {m['precision']:.4f} | {m['recall']:.4f} | {m['specificity']:.4f} | {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']:,} |")
interpret={
"keyword":"Positive differences supported for PR-AUC, F2, and recall; precision inconclusive",
"raw_layer1":"Positive differences supported for PR-AUC, F2, and precision; recall interval includes zero",
"weighted":"Positive differences supported for PR-AUC and F2; precision and recall intervals include zero",
"lstm_enhanced775":"Primary precision advantage supported; F2 and PR-AUC differences inconclusive; recall interval includes zero"}
t2=["| Comparison | Delta PR-AUC [95% CI] | Delta F2 [95% CI] | Delta Precision [95% CI] | Delta Recall [95% CI] | Interpretation |",
"|---|---:|---:|---:|---:|---|"]
for k in ["raw_layer1","keyword","weighted","lstm_enhanced775"]:
    d=r["paired_differences"][k]
    vals=[f"{d[m]['point_difference']:+.4f} [{d[m]['lower']:+.4f}, {d[m]['upper']:+.4f}]" for m in ["pr_auc","f2","precision","recall"]]
    t2.append("| vs. "+names[k]+" | "+" | ".join(vals)+" | "+interpret[k]+" |")
t3=["| Method | Validation PR-AUC | Test PR-AUC | Validation F2 | Test F2 | Validation precision | Test precision | Validation recall | Test recall |",
"|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
for k in methods:
    m=r["results"][k];v,t=m["validation"],m["test"]
    nums=[v["pr_auc"],t["pr_auc"],v["f2"],t["f2"],v["precision"],t["precision"],v["recall"],t["recall"]]
    t3.append("| "+names[k]+" | "+" | ".join(f"{n:.4f}" for n in nums)+" |")
ch4=intro+"""## 4.2 F2-Selected Performance on the Author-Disjoint Test Partition

The primary architectural comparison evaluates the seven-feature LSTM against the weighted scorer supplied with the same seven inputs. The keyword rule and maximum Layer 1 proxy provide additional baselines; the enhanced LSTM separately evaluates the addition of text embeddings. The results below apply validation-selected F2 cutoffs to the previously evaluated test scores, following Section 3.5.1.

### Table 4.1. F2-Selected Test Performance (N = 1,862 Conversations)

"""+'\n'.join(t1)+"""

The validation-selected cutoffs are 0.961438656 for maximum Layer 1 aggregation, 0.696637128 for the weighted scorer, 0.275535285 for the primary LSTM, and 0.000971102 for the enhanced LSTM. The keyword rule uses 1.0, which gives the same binary decisions as 0.5. Cutoff magnitudes are model-specific and are not interpreted as calibrated grooming probabilities.

The primary LSTM identified 41 of 44 positive conversations, achieving 0.9318 recall and 0.8613 F2 with 21 false positives. The weighted scorer identified 38 positives, maximum Layer 1 aggregation identified 39, and the keyword rule identified 27. The primary LSTM retained the highest F2 point estimate among all five methods while missing fewer positive conversations than each non-recurrent baseline.

The enhanced LSTM detected all 44 positives, giving 1.0000 recall, with 41 false positives and 0.5176 precision. Its F2 of 0.8429 was below the primary model's 0.8613 because F2 still accounts for precision. This distinguishes maximum observed coverage from the strongest recall-oriented precision-recall balance. The observed zero false negatives applies to this test partition, not to every future conversation.

## 4.3 Paired Bootstrap Difference Analysis

Table 4.2 reports primary-LSTM minus comparator differences using 2,000 paired connected-author bootstrap resamples. F2, precision, and recall intervals were recalculated for the revised cutoffs. Ranking-metric intervals remain unchanged because the scores and labels are unchanged. An interval entirely above zero supports a positive difference; one containing zero does not establish a difference or equivalence.

### Table 4.2. Primary LSTM Minus Comparator Under the F2 Policy

"""+'\n'.join(t2)+"""

The matched-input comparison supports the contribution of recurrent aggregation: the primary LSTM exceeds the weighted scorer by 0.1103 PR-AUC and 0.0630 F2, with both intervals above zero. The recall point difference is +0.0682, but its interval includes zero. The evidence supports higher F2 and ranking performance without claiming a separately established recall advantage over every comparator.

The primary LSTM has higher precision than the enhanced model, while the enhanced model has higher observed recall. Their F2 and PR-AUC difference intervals include zero, so neither is established as superior on those measures. The primary recurrent classifier contains 70,273 trainable parameters compared with 463,489 for the enhanced classifier, an 84.8% reduction. This concerns the recurrent classifiers, not the complete pipeline, since both require transformer inference.

## 4.4 Validation and Test Behavior

Each method uses the same validation-selected F2 cutoff on both partitions. Validation values describe the threshold-selection population; test values describe the revised policy on preserved author-disjoint test scores.

### Table 4.3. Validation and Test Performance Under the F2 Policy

"""+'\n'.join(t3)+"""

The primary LSTM achieved 0.8776 validation recall and 0.9318 test recall, with F2 increasing from 0.8431 to 0.8613. The enhanced model reached higher recall on both partitions, but lower test precision placed its test F2 below the primary model. Recall, precision, and F2 therefore need to be interpreted together rather than using recall alone to rank methods.

## 4.5 Interpretation of the Seven-Feature Trajectory"""+features+"""## 4.6 Descriptive Error Analysis

At the F2-selected cutoff, the primary LSTM produced three false negatives across two author-connected components and 21 false positives across 20 components. This descriptive analysis examines errors at the selected operating point; it was not used to search for a new cutoff.

The missed positive conversations contained 2, 11, and 26 turns (median 11; mean 13), with scores of 0.1819, 0.0016, and 0.0024, respectively, below the 0.275535285 cutoff. All three were shorter than the first quartile of correctly detected positive conversations, which was 36 turns; correctly detected positives had a median of 61 turns and a mean of 82.59. Short positive conversations remain the main observed false-negative pattern, consistent with the model's use of accumulated sequence evidence. Conversation length alone does not establish when grooming began or prove the cause of an error.

The enhanced LSTM detected all three cases missed by the primary LSTM. The keyword rule, maximum Layer 1 aggregation, and weighted scorer missed all three. The enhanced representation and its independently selected F2 cutoff provide additional observed coverage, accompanied by more false alerts overall.

The primary model's 21 false positives ranged from 3 to 132 turns (median 31; mean 51.29), with scores from 0.4017 to 0.9998. False positives were not confined to one conversation-length range. Because the reference endpoint is author-derived, these errors indicate disagreement with official author-list membership rather than independent content-level judgments about individual messages.

## 4.7 Practical Implications

GroomShield addresses the study's central concern: positive conversations missed by conventional or static approaches. The primary LSTM reduced false negatives from 17 to 3 relative to the keyword rule (82.4%), from 5 to 3 relative to maximum Layer 1 aggregation (40.0%), and from 6 to 3 relative to the matched weighted scorer (50.0%). Its F2 advantage over each non-recurrent baseline is supported by the paired intervals.

F2 places detection coverage ahead of minimizing false alerts while retaining precision in the objective. The primary LSTM produced 21 false alerts compared with 11 for the keyword rule, 78 for maximum Layer 1 aggregation, and 24 for the weighted scorer. The enhanced model recovered the primary model's three remaining missed positives with 20 additional false alerts. These counts describe the measured detection tradeoff; the study does not claim that F2 minimizes moderator workload or that false positives are inconsequential.

The interface demonstrates chronological contextual scoring and feature-based sequence analysis for human review. Deployment evaluation should measure end-to-end latency, throughput, calibration, and review outcomes on representative platform traffic. This separates the demonstrated detection contribution from operational performance requiring platform-level measurement.

## 4.8 Chapter Summary

The revised F2 analysis aligns GroomShield's operating policy with recall and false-negative reduction. The primary seven-feature LSTM achieved 0.9153 PR-AUC, 0.8613 F2, 0.6613 precision, and 0.9318 recall, missing three of 44 positives. Against the matched weighted scorer, the paired improvements were +0.1103 PR-AUC and +0.0630 F2, with both 95% intervals above zero. The enhanced LSTM detected all 44 positives with 0.8429 F2 and 0.5176 precision. These results demonstrate the contribution of contextual and behavioral sequence modeling to broader conversation-level detection, with the coverage-precision tradeoff explicitly measured.
"""
files["CHAPTER_IV_RESULTS_AND_DISCUSSION.md"][1]=ch4
read("CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md")
ch5="""# V. SUMMARY, CONCLUSIONS, AND RECOMMENDATIONS

## 5.1 Summary of Findings

This study developed GroomShield, an AI-powered moderation module combining contextual language analysis with behavioral sequence modeling to identify conversations missed by keyword and static-score approaches. DistilBERT evaluates each turn in its preceding context, and an LSTM processes seven chronological trajectory features. PAN-2012 was selected to evaluate the architecture using connected-author partitions, training-only derived resources, and a common conversation-level endpoint. The revised F2 analysis retains the trained models and applies validation-selected cutoffs to preserved test scores, as specified in Section 3.5.1.

The principal findings are:

1. The keyword rule detected 27 of 44 positive test conversations, achieving 0.6136 recall with 17 false negatives. Maximum Layer 1 aggregation detected 39 positives, achieving 0.8864 recall with five false negatives but 78 false positives. These results illustrate the coverage limits of lexical rules and the false-alert cost of expanding coverage through maximum-score aggregation alone.
2. The primary seven-feature LSTM achieved 0.9153 PR-AUC, 0.9930 ROC-AUC, 0.8613 F2, 0.6613 precision, 0.9318 recall, and 0.9884 specificity. It detected 41 of 44 positives and produced 21 false positives among 1,818 negatives.
3. The primary LSTM reduced false negatives to three: 82.4% fewer than the keyword rule, 40.0% fewer than maximum Layer 1 aggregation, and 50.0% fewer than the weighted scorer. These are observed count reductions at independently validation-selected operating points.
4. The primary LSTM exceeded the matched weighted scorer by 0.1103 PR-AUC and 0.0630 F2. Both paired 95% intervals were above zero, supporting the predictive contribution of recurrent aggregation. The separate recall-difference interval included zero.
5. The enhanced LSTM detected all 44 positives, with 0.8429 F2, 0.5176 precision, and 41 false positives. The primary model's precision advantage was supported by the paired interval, while F2 and PR-AUC differences between the LSTMs were inconclusive. The primary recurrent classifier also used 84.8% fewer trainable parameters.
6. The primary model's three missed positives contained 2, 11, and 26 turns, all below the first quartile of correctly detected positive conversation lengths. This identifies short-history assessment as a focused direction for further evaluation; it does not independently measure grooming onset.

## 5.2 Conclusions

The conclusions directly answer the General Objective and three Specific Objectives of the study:

1. **Specific Objective 1 - Evaluate existing keyword-based and rule-based moderation approaches.** Lexical matching and maximum contextual-score aggregation do not capture the same detection tradeoff as sequence modeling. The keyword rule missed 17 positives. Maximum Layer 1 aggregation reduced that count to five but generated 78 false positives, compared with three misses and 21 false positives for the primary LSTM. Contextual scores alone therefore did not obtain the strongest measured F2 performance.
2. **Specific Objective 2 - Design and develop the AI-based moderation module.** The study successfully implemented GroomShield as a complete two-layer module combining context-conditioned DistilBERT scoring, seven interpretable trajectory features, LSTM-based sequence modeling, and a working interface for sequential conversation assessment. The final output is a conversation-level flag for human review.
3. **Specific Objective 3 - Assess detection improvement and false-negative reduction.** GroomShield achieved 93.18% recall with the primary LSTM and reduced observed false negatives by 82.4% relative to the keyword rule, 40.0% relative to maximum Layer 1 aggregation, and 50.0% relative to the weighted scorer. Its supported F2 and PR-AUC advantages over the matched weighted scorer establish the contribution of recurrent aggregation using the same seven inputs. F2 aligns the operating policy with reducing missed positives while retaining precision. Quantitative improvement is demonstrated against the tested keyword and score-based approaches; complementing user reporting is an intended application rather than a measured comparison with a deployed reporting system.
4. **General Objective - Develop an AI-powered moderation module that enhances existing chat moderation.** The study achieved this objective by developing and evaluating a contextual and behavioral sequence module that expands conversation-level detection coverage. The primary LSTM offers the highest observed F2 among the evaluated methods, while the enhanced variant provides additional coverage at a greater false-alert cost. These findings support GroomShield as a technical foundation for complementing existing safeguards and human judgment.

## 5.3 Recommendations

Based on the results and remaining evaluation needs, the study recommends:

1. Evaluate the selected F2 operating policy on an independent external corpus with thresholds fixed before evaluation, testing cross-platform transfer and providing a fresh assessment of the revised policy.
2. Investigate short-history performance through controlled conversation-prefix evaluation. Separately develop expert-reviewed message, stage, and first-onset annotations before evaluating grooming onset or time to detection.
3. Conduct feature-removal, ordering, and architecture ablations to quantify the contribution of individual trajectory features and sequence-learning components.
4. Measure calibration, end-to-end latency, throughput, memory use, and human-review outcomes on representative traffic. Retain recall, false negatives, precision, and false positives as joint measures; select operational escalation policies using development data rather than retuning on evaluation outcomes.
5. Acquire representative contemporary and Philippine-context data, including Filipino and Taglish conversations where ethically and legally permissible, with privacy, fairness, and subgroup analysis.
6. Extend preprocessing and evaluation to multi-party conversations through a separately specified protocol preserving participant boundaries and preventing author leakage.
"""
files["CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md"][1]=ch5

read("ABSTRACT_F2.md")
abstract="""Keyword-based chat moderation can miss grooming-related interactions whose meaning emerges through conversational context and behavioral progression. This study develops GroomShield, a two-layer artificial intelligence module designed to improve detection coverage and reduce false negatives. A context-conditioned DistilBERT classifier produces turn-level author-derived proxy scores, while a Long Short-Term Memory (LSTM) network processes seven chronological features describing score patterns, semantic movement, and speaker participation. The PAN-2012 Sexual Predator Identification corpus was selected for evaluation, with positive conversations defined by the presence of an officially identified predator author. Connected-author partitioning separates participants across training, validation, and test sets. The primary LSTM is compared with a keyword rule, maximum classifier-score aggregation, and a weighted scorer using the same features; an enhanced LSTM additionally incorporates text embeddings. The revised operating policy selects thresholds using validation F2 and applies them to previously evaluated test scores. Across 1,862 test conversations containing 44 positives, the primary LSTM achieved 93.18% recall, 66.13% precision, and 0.8613 F2, missing three positives compared with six for the weighted scorer, five for maximum classifier-score aggregation, and 17 for the keyword rule. Paired component-bootstrap intervals supported its F2 and PR-AUC advantages over the weighted scorer. The enhanced LSTM detected all 44 positives at 51.76% precision and 0.8429 F2. These findings demonstrate the contribution of contextual and behavioral sequence modeling to recall-oriented conversation detection, providing a foundation for AI-assisted moderation that complements existing safeguards and human review."""
assert len(abstract.split())<=250,len(abstract.split())
keywords="online grooming detection; chat moderation; conversational context; behavioral pattern analysis; natural language processing; long short-term memory networks."
files["ABSTRACT_F2.md"][1]=f"# {TITLE}\n\n## Abstract\n\n{abstract}\n\n**Keywords:** {keywords}\n"
files["Finals_Revised_Paper_WASD.md"][1]=main.replace("# I. Introduction",f"# Abstract\n\n{abstract}\n\n**Keywords:** {keywords}\n\n# I. Introduction",1)
index=read("README.md")
index=index.replace(
"single source of truth for the current\n   endpoint, model, completed evaluation, limitations, and next work.",
"historical August 12 recovery report;\n   its model and label descriptions are superseded by the current manuscript.")
index=index.replace("discussion derived from the frozen evaluation artifacts.",
"discussion from the revised F2 analysis of preserved test-score artifacts.")
index=index.replace("aligned with the authoritative paper and final results.",
"awaiting synchronization with the September 20 F2 manuscript revision.")
index=index.replace("The authoritative editable Chapters I-III paper remains at the workspace root:",
"The established Word counterpart for Chapters I-III remains at the workspace root (F2 synchronization pending):")
a=index.index("**Current 2026-09-15 manuscript status:**");b=index.index("\n\nThe Chapters I-III Word",a)
index=index[:a]+"""**Current 2026-09-20 manuscript status:** the authoritative Chapters I-V Markdown and abstract now use the GroomShield title naming DistilBERT and LSTM-based behavioral sequence modeling, and an F2/recall-focused final conversation policy. Chapter IV reports validation-selected F2 cutoffs applied to previously evaluated test scores; Section 3.5.1 records the evaluation chronology. The primary LSTM detects 41/44 positives (recall 0.9318, precision 0.6613, F2 0.8613; 21 false positives), and the enhanced LSTM detects 44/44 (precision 0.5176, F2 0.8429; 41 false positives). Paired intervals and error analysis were recalculated. Research questions, adviser-locked objectives, Chapter II, and references remain unchanged.

**Synchronization boundary:** Word files, presentations and scripts, the alignment table, defense guide, panel matrix/PDF, architecture assets, and live-demo thresholds have not been updated to F2 in this pass. Original models, checkpoint records, final-test gate, and original evaluation outputs remain unchanged. ABSTRACT_F2.md contains the abstract also inserted into the main Markdown. Reproduce results with python thesis_docs/.threshold_analysis/analyze_f2_test.py; the aggregate receipt is .threshold_analysis/f2_test_reanalysis.json.

**Earlier artifact history (not current F2 synchronization):**"""+index[b:]
index=index.replace("The current defense deck is","The September 16 defense-deck snapshot was")
index=index.replace(
"This analysis leaves the models, active thresholds, and Chapter IV results unchanged. Its script and aggregate receipt are in .threshold_analysis/.",
"That validation-only analysis leaves models and active thresholds unchanged. The September 20 manuscript uses the separate F2 test-score reanalysis described above. Scripts and aggregate receipts are in .threshold_analysis/.")
files["README.md"][1]=index
log=read("THESIS_RECOVERY_NEXT_STEPS.md")
entry="| 2026-09-20 | Applied the approved GroomShield title using DistilBERT and LSTM-Based Behavioral Sequence Modeling. Revised authoritative Chapters I-V Markdown and the synchronized abstract for an F2/recall-focused final conversation policy. Verified existing validation-F2 cutoffs before reading preserved test outcomes, then recomputed decisions, paired 2,000-component-bootstrap intervals, and errors without training or inference. Primary test TP/FP/FN = 41/21/3, recall 0.9318, precision 0.6613, F2 0.8613; enhanced = 44/41/0, precision 0.5176, F2 0.8429. Primary-minus-weighted F2 interval remains positive, but recall interval includes zero; claims corrected accordingly. Methodology identifies revised-policy analysis of the previously evaluated test partition. Preserved exact objectives, research questions, Chapter II, references, frozen artifacts, and active thresholds. Updated documentation authority and synchronization status. No DOCX, PPTX, alignment-table, demo, or rendering changes. Next: review Markdown, then synchronize approved content to Word, presentation/script, alignment table, defense guide, panel matrix and demo policy in scoped follow-up work. | Finals_Revised_Paper_WASD.md; CHAPTER_IV_RESULTS_AND_DISCUSSION.md; CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md; ABSTRACT_F2.md; .threshold_analysis/analyze_f2_test.py; .threshold_analysis/f2_test_reanalysis.json; README.md |"
files["THESIS_RECOVERY_NEXT_STEPS.md"][1]=log.rstrip()+"\n"+entry+"\n"
patch_tool=r"C:\Users\JM\.vscode\extensions\openai.chatgpt-26.908.40401-win32-x64\bin\windows-x86_64\codex.exe"
for name,(old,new) in files.items():
    assert old!=new,name
    diff=list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=3))
    patch="*** Begin Patch\n*** Update File: "+(D/name).as_posix()+"\n"
    for line in diff[2:]:
        patch+=("@@\n" if line.startswith("@@") else line+"\n")
    patch+="*** End Patch"
    subprocess.run([patch_tool,"--codex-run-as-apply-patch",patch],check=True)
    assert (D/name).read_text(encoding="utf-8")==new,name
receipt=dict(updated_utc=datetime.now(timezone.utc).isoformat(),title=TITLE,
    abstract_words=len(abstract.split()),objectives_preserved=True,research_questions_preserved=True,
    chapter_2_preserved=True,references_preserved=True,rendering_performed=False,
    source_receipt=".threshold_analysis/f2_test_reanalysis.json",
    files={name:dict(before_sha256=hashlib.sha256(old.encode()).hexdigest(),
                    after_sha256=hashlib.sha256(new.encode()).hexdigest()) for name,(old,new) in files.items()})
(D/".threshold_analysis/f2_manuscript_revision_receipt.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
print("Applied",len(files),"Markdown revisions; abstract words:",len(abstract.split()))
