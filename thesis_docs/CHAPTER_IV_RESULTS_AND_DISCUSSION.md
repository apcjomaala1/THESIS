# IV. RESULTS AND DISCUSSION

## 4.1 Experimental Dataset and Author-Disjoint Partitions

The primary experiment evaluates the PAN-2012 author-derived conversation endpoint under connected-author partitioning. Conversations are vertices in an author-connectivity graph, and every connected component is assigned wholly to one partition. Consequently, no conversation, author, or author-connected component appears across training, validation, and final-test partitions.

The candidate pool contains **18,567 conversations**, of which 454 are endpoint-positive and 18,113 are endpoint-negative, comprising 218,114 total turns and 34,686 distinct author identifiers. The primary partitions are:

1. **Training:** 13,031 conversations (319 positive, 12,712 negative; 152,405 turns), used for Layer 1 fine-tuning, training-derived resources, and LSTM fitting.
2. **Validation:** 1,827 conversations (49 positive, 1,778 negative; 21,911 turns), used for checkpoint selection, feature-threshold locking, comparator fitting, hyperparameter selection, and operating-threshold selection.
3. **Held-out final test:** 1,862 conversations (44 positive, 1,818 negative; 22,929 turns) in 1,800 author-connected components, evaluated after the pipeline and reporting rules were frozen.
4. **Excluded historical-test group:** 1,847 conversations (42 positive, 1,805 negative; 20,869 turns), retained in the locked manifest for complete accounting but not used for primary model development, selection, or final evaluation.

The positive label means that a conversation contains at least one author on the official PAN12 predator list. It is a conversation-level benchmark endpoint, not an exhaustive annotation that every turn contains grooming behavior.

## 4.2 Held-Out Final-Test Performance

The primary research question is whether the seven-feature trajectory LSTM outperforms the validation-fitted weighted scorer supplied with the same seven inputs. The keyword rule and maximum Layer 1 proxy provide additional reference baselines, while the 775-input LSTM measures the effect of adding base DistilBERT embeddings.

Table 4.1 reports point estimates and 95% confidence intervals from 2,000 bootstrap resamples over author-connected components.

### Table 4.1. Held-Out Final-Test Performance (N = 1,862 Conversations)

| Method | Input representation | PR-AUC [95% CI] | ROC-AUC [95% CI] | F0.5 [95% CI] | Precision | Recall | Specificity | TP | FP | FN | TN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Keyword rule | 50 training-derived unigram/bigram terms | 0.4451 [0.2930, 0.5664] | 0.8038 [0.7536, 0.8665] | 0.6888 [0.5072, 0.8010] | 0.7105 | 0.6136 | 0.9939 | 27 | 11 | 17 | 1,807 |
| Maximum Layer 1 proxy | Maximum context-conditioned proxy in the conversation | 0.5523 [0.3210, 0.7422] | 0.9678 [0.9087, 0.9916] | 0.5529 [0.3053, 0.7042] | 0.5610 | 0.5227 | 0.9901 | 23 | 18 | 21 | 1,800 |
| Weighted scorer | Validation-fitted combination of seven trajectory features | 0.8050 [0.6163, 0.9263] | 0.9719 [0.9063, 0.9971] | 0.7500 [0.5384, 0.8649] | 0.7347 | 0.8182 | 0.9928 | 36 | 13 | 8 | 1,805 |
| **Primary trajectory LSTM** | **Chronological sequence of seven trajectory features** | **0.9153 [0.7781, 0.9876]** | **0.9930 [0.9790, 0.9997]** | **0.8621 [0.6944, 0.9513]** | **0.8511** | **0.9091** | **0.9961** | **40** | **7** | **4** | **1,811** |
| Enhanced LSTM | Seven features plus 768-dimensional base embeddings | 0.9483 [0.7940, 0.9965] | 0.9987 [0.9964, 0.9999] | 0.8836 [0.7181, 0.9667] | 0.8723 | 0.9318 | 0.9967 | 41 | 6 | 3 | 1,812 |

The operating thresholds were selected on validation and frozen before final testing: maximum Layer 1 proxy = 0.9819877, weighted scorer = 0.7149941, keyword rule = 0.5000, primary LSTM = 0.9688298, and enhanced LSTM = 0.9558892.

The primary LSTM correctly identified 40 of 44 endpoint-positive conversations while producing seven false positives among 1,818 endpoint-negative conversations. Its PR-AUC of 0.9153 is 0.1103 above the matched weighted scorer and 0.3630 above maximum Layer 1 aggregation. This is the central empirical result: chronological recurrent aggregation extracted substantially more useful conversation-level signal than either a static fitted combination of the same features or a maximum contextual proxy score.

## 4.3 Paired Bootstrap Difference Analysis

Paired differences were calculated within each of the same 2,000 connected-author bootstrap resamples. Intervals entirely above zero support a positive performance difference for the primary LSTM on the reported metric. An interval containing zero is treated as inconclusive; it is not evidence of equivalence.

### Table 4.2. Primary LSTM Minus Comparator

| Comparison | Delta PR-AUC [95% CI] | Delta F0.5 [95% CI] | Delta Precision [95% CI] | Delta Recall [95% CI] | Interpretation |
|---|---:|---:|---:|---:|---|
| **vs. maximum Layer 1 proxy** | **+0.3630** [+0.2056, +0.5351] | **+0.3092** [+0.1827, +0.4911] | **+0.2901** [+0.1407, +0.4808] | **+0.3864** [+0.2105, +0.5807] | Positive difference supported for all four metrics |
| **vs. keyword rule** | **+0.4702** [+0.3563, +0.5773] | **+0.1733** [+0.0526, +0.3125] | +0.1405 [-0.0059, +0.3152] | **+0.2955** [+0.2083, +0.3542] | Positive difference supported for PR-AUC, F0.5, and recall; precision is inconclusive |
| **vs. weighted scorer** | **+0.1103** [+0.0251, +0.2254] | **+0.1121** [+0.0194, +0.2336] | **+0.1164** [+0.0066, +0.2580] | **+0.0909** [+0.0244, +0.1725] | Positive difference supported for all four metrics |
| vs. enhanced LSTM | -0.0330 [-0.1095, +0.0326] | -0.0216 [-0.1008, +0.0547] | -0.0213 [-0.1179, +0.0647] | -0.0227 [-0.0833, +0.0667] | Inconclusive; no superiority or equivalence conclusion |

The matched-input comparison provides the clearest architectural evidence. Because the primary LSTM and weighted scorer receive the same seven trajectory features, the positive PR-AUC and F0.5 difference intervals isolate the value of learned recurrent aggregation rather than additional input information.

The enhanced LSTM has a higher point estimate than the primary model, but the paired intervals contain zero. The experiment therefore does not establish that either LSTM is superior to the other. The primary recurrent classifier remains materially smaller: it contains 70,273 trainable parameters compared with 463,489 for the enhanced recurrent classifier, an 84.8% reduction. This parameter comparison applies to the recurrent classifiers themselves, not to the complete pipeline, since both systems still require transformer inference.

## 4.4 Validation and Final-Test Behavior

Table 4.3 compares validation performance with the locked final test. The test partition contains authors absent from training and validation, so the final figures measure within-PAN12 generalization to unseen author-connected components.

### Table 4.3. Validation and Final-Test Performance

| Method | Validation PR-AUC | Test PR-AUC | Validation F0.5 | Test F0.5 | Validation precision | Test precision | Validation recall | Test recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keyword rule | 0.3318 | 0.4451 | 0.6216 | 0.6888 | 0.6765 | 0.7105 | 0.4694 | 0.6136 |
| Maximum Layer 1 proxy | 0.6840 | 0.5523 | 0.7027 | 0.5529 | 0.7647 | 0.5610 | 0.5306 | 0.5227 |
| Weighted scorer | 0.7613 | 0.8050 | 0.8466 | 0.7500 | 0.9143 | 0.7347 | 0.6531 | 0.8182 |
| **Primary trajectory LSTM** | **0.8192** | **0.9153** | **0.8451** | **0.8621** | **0.8780** | **0.8511** | **0.7347** | **0.9091** |
| Enhanced LSTM | 0.8605 | 0.9483 | 0.8756 | 0.8836 | 0.9048 | 0.8723 | 0.7755 | 0.9318 |

The primary LSTM remained strong on the unseen-author final partition and improved from 0.8192 validation PR-AUC to 0.9153 test PR-AUC. This establishes strong held-out performance on unseen author-connected components within the locked PAN12 design. It does not, by itself, establish transfer to a different platform, language, or dataset.

## 4.5 Interpretation of the Seven-Feature Trajectory

The primary model consumes the exact chronological sequence of the following features:

1. **Peak proxy score:** the largest Layer 1 proxy observed up to the current turn.
2. **Current proxy score:** the current context-conditioned Layer 1 output.
3. **Spike count:** the cumulative number of scores above the frozen validation-derived spike threshold.
4. **Spike-then-drop:** whether an earlier spike was followed by a decrease larger than the frozen drop threshold.
5. **Rate of change:** the difference between consecutive proxy scores.
6. **Topic distance:** cosine distance between the current base DistilBERT embedding and the benign training centroid.
7. **Turn-taking imbalance:** the cumulative difference in the two speakers' turn counts divided by total turns.

The weighted scorer and primary LSTM receive these same seven variables. Their performance difference therefore establishes the value of the selected learned recurrent aggregator over the selected static weighted aggregator on the conversation endpoint. The result is consistent with a benefit from sequence-sensitive nonlinear aggregation, but the current design does not separately isolate ordering, recurrence, or the causal contribution of each feature; targeted architectural and feature-removal ablations would be required for those conclusions.

Maximum Layer 1 aggregation is also a meaningful comparator, but it is not an ideal message-label experiment. Layer 1 itself is trained against an author-derived proxy and receives the current turn plus two preceding turns. The observed gain over maximum Layer 1 aggregation demonstrates the value of conversation-level trajectory modeling over a maximum contextual proxy rule.

## 4.6 Descriptive Error Analysis

The primary LSTM produced eleven final-test errors across nine author-connected components: four false negatives across three components and seven false positives across six components. This analysis is descriptive and post hoc; it was not used to select a model or threshold.

The four false negatives contained 2, 11, 13, and 26 turns (median 12; mean 13), with LSTM scores of 0.1819, 0.0016, 0.8541, and 0.0024 against the locked threshold of 0.9688. All four were shorter than the first quartile of correctly detected positive conversations, which was 36 turns; correctly detected positives had a median of 62 turns and a mean of 84.33. The remaining misses were therefore concentrated among comparatively short positive conversations, where less sequential evidence was available, although this descriptive association does not establish causation. The enhanced LSTM recovered the 13-turn and 26-turn cases, maximum Layer 1 aggregation and the keyword rule recovered the 13-turn case, and the weighted scorer missed all four. Two cases were missed by every evaluated method.

The seven false positives contained 3, 3, 27, 31, 93, 130, and 132 turns (median 31; mean 59.86), with scores between 0.9804 and 0.9998. Four were also flagged by maximum Layer 1 aggregation, the weighted scorer, and the enhanced LSTM; one was also flagged by the keyword rule. Three cases—the two three-turn conversations and the 27-turn conversation—were unique to the primary LSTM across all four comparators. The broad length range shows that false positives were not confined to a single conversation-length regime.

Because PAN12's endpoint is author-derived, the error labels indicate disagreement with official author-list membership. They do not independently prove that the visible content of a false positive is harmless or that a false negative lacks grooming behavior.

## 4.7 Practical Implications

Relative to maximum Layer 1 aggregation, the primary LSTM reduced false positives from 18 to 7, a 61.1% reduction, while increasing true positives from 23 to 40. Relative to the weighted scorer, false positives decreased from 13 to 7, a 46.2% reduction, and false negatives decreased from 8 to 4. Relative to the keyword rule, false positives decreased from 11 to 7, a 36.4% reduction, while true positives increased from 27 to 40.

These results justify selecting the trajectory LSTM as the prototype's conversation-prioritization component. Its seven inputs provide an auditable summary of how proxy evidence evolves, and the matched comparison establishes an improved precision-recall tradeoff over the weighted scorer. The interface positions this component for human review, but reviewer effectiveness was not evaluated. The study also did not benchmark end-to-end latency, production throughput, calibration on live platform traffic, or autonomous moderation outcomes. A below-threshold score is not a declaration that a conversation or participant is safe.

## 4.8 Chapter Summary

The held-out experiment achieved its primary objective. The seven-feature trajectory LSTM reached 0.9153 PR-AUC, 0.8621 F0.5, 0.8511 precision, and 0.9091 recall on unseen author-connected PAN12 conversations. Against the matched weighted scorer, the paired improvements were +0.1103 PR-AUC and +0.1121 F0.5, with both 95% intervals above zero. The evidence therefore supports the study's central conclusion: learned recurrent modeling of the seven-feature conversational trajectory provides a substantial advantage over static aggregation for the defined PAN12 conversation endpoint.
