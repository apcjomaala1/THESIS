# IV. RESULTS AND DISCUSSION

## 4.1 Experimental Dataset and Author-Disjoint Partitions

The study evaluates the proposed module on the selected PAN-2012 dataset using connected-author partitioning. Conversations are vertices in an author-connectivity graph, and every connected component is assigned wholly to one partition. Consequently, no conversation, author, or author-connected component appears across training, validation, and final-test partitions.

The candidate pool contains **18,567 conversations**, of which 454 are endpoint-positive and 18,113 are endpoint-negative, comprising 218,114 total turns and 34,686 distinct author identifiers. The primary partitions are:

1. **Training:** 13,031 conversations (319 positive, 12,712 negative; 152,405 turns), used for Layer 1 fine-tuning, training-derived resources, and LSTM fitting.
2. **Validation:** 1,827 conversations (49 positive, 1,778 negative; 21,911 turns), used for checkpoint selection, feature-threshold locking, comparator fitting, hyperparameter selection, and operating-threshold selection.
3. **Held-out final test:** 1,862 conversations (44 positive, 1,818 negative; 22,929 turns) in 1,800 author-connected components, excluded from parameter fitting; its saved scores are used for the revised F2 analysis.
4. **Excluded historical-test group:** 1,847 conversations (42 positive, 1,805 negative; 20,869 turns), retained in the locked manifest for complete accounting but not used for primary model development, selection, or final evaluation.

For this evaluation, a positive label identifies a conversation containing at least one author on the dataset's official predator list. This benchmark outcome is applied consistently across every comparison method and does not assign grooming status to every individual turn.

## 4.2 F2-Selected Performance on the Author-Disjoint Test Partition

The primary architectural comparison evaluates the seven-feature LSTM against the weighted scorer supplied with the same seven inputs. The keyword rule and maximum Layer 1 proxy provide additional baselines; the enhanced LSTM separately evaluates the addition of text embeddings. The results below apply validation-selected F2 cutoffs to the previously evaluated test scores, following Section 3.5.2.

### Table 4.1. F2-Selected Test Performance (N = 1,862 Conversations)

| Method | Input representation | PR-AUC [95% CI] | ROC-AUC [95% CI] | F2 [95% CI] | Precision | Recall | Specificity | TP | FP | FN | TN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Keyword rule | 50 training-derived unigram/bigram terms | 0.4451 [0.2930, 0.5664] | 0.8038 [0.7536, 0.8665] | 0.6308 [0.5251, 0.7237] | 0.7105 | 0.6136 | 0.9939 | 27 | 11 | 17 | 1,807 |
| Maximum Layer 1 proxy | Maximum contextual proxy score | 0.5523 [0.3210, 0.7422] | 0.9678 [0.9087, 0.9916] | 0.6655 [0.4587, 0.7859] | 0.3333 | 0.8864 | 0.9571 | 39 | 78 | 5 | 1,740 |
| Weighted scorer | Weighted combination of seven trajectory features | 0.8050 [0.6163, 0.9263] | 0.9719 [0.9063, 0.9971] | 0.7983 [0.6481, 0.8769] | 0.6129 | 0.8636 | 0.9868 | 38 | 24 | 6 | 1,794 |
| Primary trajectory LSTM | Sequence of seven trajectory features | 0.9153 [0.7781, 0.9876] | 0.9930 [0.9790, 0.9997] | 0.8613 [0.7143, 0.9365] | 0.6613 | 0.9318 | 0.9884 | 41 | 21 | 3 | 1,797 |
| Enhanced LSTM | Seven features plus 768-dimensional embeddings | 0.9483 [0.7940, 0.9965] | 0.9987 [0.9964, 0.9999] | 0.8429 [0.6870, 0.9105] | 0.5176 | 1.0000 | 0.9774 | 44 | 41 | 0 | 1,777 |

The validation-selected cutoffs are 0.961438656 for maximum Layer 1 aggregation, 0.696637128 for the weighted scorer, 0.275535285 for the primary LSTM, and 0.000971102 for the enhanced LSTM. The keyword rule uses 1.0, which gives the same binary decisions as 0.5. Cutoff magnitudes are model-specific and are not interpreted as calibrated grooming probabilities.

The primary LSTM identified 41 of 44 positive conversations, achieving 0.9318 recall and 0.8613 F2 with 21 false positives. The weighted scorer identified 38 positives, maximum Layer 1 aggregation identified 39, and the keyword rule identified 27. The primary LSTM retained the highest F2 point estimate among all five methods while missing fewer positive conversations than each non-recurrent baseline.

The enhanced LSTM detected all 44 positives, giving 1.0000 recall, with 41 false positives and 0.5176 precision. Its F2 of 0.8429 was below the primary model's 0.8613 because F2 still accounts for precision. This distinguishes maximum observed coverage from the strongest recall-oriented precision-recall balance. The observed zero false negatives applies to this test partition, not to every future conversation.

## 4.3 Paired Bootstrap Difference Analysis

Table 4.2 reports primary-LSTM minus comparator differences using 2,000 paired connected-author bootstrap resamples. F2, precision, and recall intervals were recalculated for the revised cutoffs. Ranking-metric intervals remain unchanged because the scores and labels are unchanged. An interval entirely above zero supports a positive difference; one containing zero does not establish a difference or equivalence.

### Table 4.2. Primary LSTM Minus Comparator Under the F2 Policy

| Comparison | Delta PR-AUC [95% CI] | Delta F2 [95% CI] | Delta Precision [95% CI] | Delta Recall [95% CI] | Interpretation |
|---|---:|---:|---:|---:|---|
| vs. Maximum Layer 1 proxy | +0.3630 [+0.2056, +0.5351] | +0.1958 [+0.1218, +0.3105] | +0.3280 [+0.2236, +0.4240] | +0.0455 [+0.0000, +0.1364] | Positive differences supported for PR-AUC, F2, and precision; recall interval includes zero |
| vs. Keyword rule | +0.4702 [+0.3563, +0.5773] | +0.2305 [+0.0949, +0.3009] | -0.0492 [-0.2088, +0.0927] | +0.3182 [+0.2083, +0.3824] | Positive differences supported for PR-AUC, F2, and recall; precision inconclusive |
| vs. Weighted scorer | +0.1103 [+0.0251, +0.2254] | +0.0630 [+0.0034, +0.1294] | +0.0484 [-0.0457, +0.1394] | +0.0682 [+0.0000, +0.1373] | Positive differences supported for PR-AUC and F2; precision and recall intervals include zero |
| vs. Enhanced LSTM | -0.0330 [-0.1095, +0.0326] | +0.0184 [-0.0758, +0.1153] | +0.1436 [+0.0524, +0.2310] | -0.0682 [-0.1945, +0.0000] | Primary precision advantage supported; F2 and PR-AUC differences inconclusive; recall interval includes zero |

The matched-input comparison supports the contribution of recurrent aggregation: the primary LSTM exceeds the weighted scorer by 0.1103 PR-AUC and 0.0630 F2, with both intervals above zero. The recall point difference is +0.0682, but its interval includes zero. The evidence supports higher F2 and ranking performance without claiming a separately established recall advantage over every comparator.

The primary LSTM has higher precision than the enhanced model, while the enhanced model has higher observed recall. Their F2 and PR-AUC difference intervals include zero, so neither is established as superior on those measures. The primary recurrent classifier contains 70,273 trainable parameters compared with 463,489 for the enhanced classifier, an 84.8% reduction. This concerns the recurrent classifiers, not the complete pipeline, since both require transformer inference.

## 4.4 Validation and Test Behavior

Each method uses the same validation-selected F2 cutoff on both partitions. Validation values describe the threshold-selection population; test values describe the revised policy on preserved author-disjoint test scores.

### Table 4.3. Validation and Test Performance Under the F2 Policy

| Method | Validation PR-AUC | Test PR-AUC | Validation F2 | Test F2 | Validation precision | Test precision | Validation recall | Test recall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Keyword rule | 0.3318 | 0.4451 | 0.5000 | 0.6308 | 0.6765 | 0.7105 | 0.4694 | 0.6136 |
| Maximum Layer 1 proxy | 0.6840 | 0.5523 | 0.6655 | 0.6655 | 0.4021 | 0.3333 | 0.7959 | 0.8864 |
| Weighted scorer | 0.7613 | 0.8050 | 0.7347 | 0.7983 | 0.7347 | 0.6129 | 0.7347 | 0.8636 |
| Primary trajectory LSTM | 0.8192 | 0.9153 | 0.8431 | 0.8613 | 0.7288 | 0.6613 | 0.8776 | 0.9318 |
| Enhanced LSTM | 0.8605 | 0.9483 | 0.8577 | 0.8429 | 0.6026 | 0.5176 | 0.9592 | 1.0000 |

The primary LSTM achieved 0.8776 validation recall and 0.9318 test recall, with F2 increasing from 0.8431 to 0.8613. The enhanced model reached higher recall on both partitions, but lower test precision placed its test F2 below the primary model. Recall, precision, and F2 therefore need to be interpreted together rather than using recall alone to rank methods.

## 4.5 Interpretation of the Seven-Feature Trajectory

The primary model consumes the exact chronological sequence of the following features:

1. **Peak proxy score:** the largest Layer 1 proxy observed up to the current turn.
2. **Current proxy score:** the current context-conditioned Layer 1 output.
3. **Spike count:** the cumulative number of scores above the frozen validation-derived spike threshold.
4. **Spike-then-drop:** whether an earlier spike was followed by a decrease larger than the frozen drop threshold.
5. **Rate of change:** the difference between consecutive proxy scores.
6. **Topic distance:** cosine distance between the current base DistilBERT embedding and the benign training centroid.
7. **Turn-taking imbalance:** the cumulative difference in the two speakers' turn counts divided by total turns.

The weighted scorer and primary LSTM receive these same seven variables. Their performance difference therefore establishes the value of the selected learned recurrent aggregator over the selected static weighted aggregator on the conversation endpoint. The result demonstrates the benefit of the recurrent architecture as a complete aggregation method; targeted architectural, ordering, and feature-removal ablations can extend this evidence by quantifying individual contributions.

The feature set also operationalizes the study's OGDM-informed trajectory rationale. Peak, current, and spike count represent accumulation and persistence of contextual evidence; rate of change and spike-then-drop represent escalation and retreat; topic distance represents semantic movement from the benign training reference; and turn-taking imbalance represents interaction structure. The experiment tests these properties as a chronological sequence rather than treating them as direct labels of grooming stages.

Maximum Layer 1 aggregation provides a direct test of whether trajectory modeling adds value beyond the strongest isolated contextual proxy observed in a conversation. Layer 1 is trained against the study's defined target and receives the current turn plus two preceding turns. The observed gain over maximum Layer 1 aggregation demonstrates the value of conversation-level trajectory modeling over a maximum contextual proxy rule.

## 4.6 Descriptive Error Analysis

At the F2-selected cutoff, the primary LSTM produced three false negatives across two author-connected components and 21 false positives across 20 components. This descriptive analysis examines errors at the selected operating point; it was not used to search for a new cutoff.

The missed positive conversations contained 2, 11, and 26 turns (median 11; mean 13), with scores of 0.1819, 0.0016, and 0.0024, respectively, below the 0.275535285 cutoff. All three were shorter than the first quartile of correctly detected positive conversations, which was 36 turns; correctly detected positives had a median of 61 turns and a mean of 82.59. Short positive conversations remain the main observed false-negative pattern, consistent with the model's use of accumulated sequence evidence. Conversation length alone does not establish when grooming began or prove the cause of an error.

The enhanced LSTM detected all three cases missed by the primary LSTM. The keyword rule, maximum Layer 1 aggregation, and weighted scorer missed all three. The enhanced representation and its independently selected F2 cutoff provide additional observed coverage, accompanied by more false alerts overall.

The primary model's 21 false positives ranged from 3 to 132 turns (median 31; mean 51.29), with scores from 0.4017 to 0.9998. False positives were not confined to one conversation-length range. Because the reference endpoint is author-derived, these errors indicate disagreement with official author-list membership rather than independent content-level judgments about individual messages.

## 4.7 Practical Implications

GroomShield addresses the study's central concern: positive conversations missed by conventional or static approaches. The primary LSTM reduced false negatives from 17 to 3 relative to the keyword rule (82.4%), from 5 to 3 relative to maximum Layer 1 aggregation (40.0%), and from 6 to 3 relative to the matched weighted scorer (50.0%). Its F2 advantage over each non-recurrent baseline is supported by the paired intervals.

F2 places detection coverage ahead of minimizing false alerts while retaining precision in the objective. The primary LSTM produced 21 false alerts compared with 11 for the keyword rule, 78 for maximum Layer 1 aggregation, and 24 for the weighted scorer. The enhanced model recovered the primary model's three remaining missed positives with 20 additional false alerts. These counts describe the measured detection tradeoff; the study does not claim that F2 minimizes moderator workload or that false positives are inconsequential.

The interface demonstrates chronological contextual scoring and feature-based sequence analysis for human review. The local benchmark below measures its current per-turn processing cost. Representative platform traffic, concurrency, network conditions, calibration, and moderator outcomes still require separate deployment evaluation.

### 4.7.1 Local Latency and Throughput

Table 4.4 reports warmed localhost HTTP round-trip latency for the full per-turn scoring path. Each request recomputed the complete prefix, including context-conditioned Layer 1 scoring and current-turn base embeddings, before running the selected LSTM. Both models were tested on the same unlabeled synthetic prefixes; the pooled rows equally weight 1-, 4-, 8-, and 16-turn cases. There were 40 timed requests per model at each length (160 per model), after three warm-ups per condition, with one request in flight. The benchmark ran on an Intel Core i5-11400H CPU with six PyTorch intra-operation threads; it did not use GPU inference or held-out test text.

### Table 4.4. Local Per-Turn HTTP Latency and Sequential Throughput

| Selected LSTM | Prefix turns | Timed requests | Median (ms) | p95 (ms) | p99 (ms) | Throughput (requests/s) |
|---|---:|---:|---:|---:|---:|---:|
| Primary, seven features | 1 | 40 | 41.0 | 77.3 | 123.1 | 21.22 |
| Primary, seven features | 4 | 40 | 159.1 | 283.1 | 304.0 | 5.88 |
| Primary, seven features | 8 | 40 | 308.6 | 418.3 | 457.6 | 3.09 |
| Primary, seven features | 16 | 40 | 597.3 | 795.7 | 977.9 | 1.57 |
| **Primary, equal-length mix** | **1/4/8/16** | **160** | **266.6** | **708.8** | **829.8** | **3.39** |
| Enhanced, features + embeddings | 1 | 40 | 43.7 | 63.7 | 80.3 | 21.54 |
| Enhanced, features + embeddings | 4 | 40 | 159.8 | 218.8 | 228.9 | 5.98 |
| Enhanced, features + embeddings | 8 | 40 | 317.0 | 432.5 | 577.9 | 2.98 |
| Enhanced, features + embeddings | 16 | 40 | 594.1 | 1041.5 | 1100.9 | 1.52 |
| **Enhanced, equal-length mix** | **1/4/8/16** | **160** | **245.6** | **717.7** | **1058.5** | **3.32** |

The complete pipeline's latency rises with prefix length because the prototype recomputes prior turns on every update. In the equal-length mix, the primary variant processed 3.39 sequential requests/s and the enhanced variant 3.32; their local median latencies were 266.6 ms and 245.6 ms, respectively. The small pooled median reversal should not be interpreted as a demonstrated speed advantage for the enhanced recurrent model: upstream transformer computation dominates the request and the benchmark was not designed as a paired inferential speed test. At 16 turns, both median latencies were about 0.6 s, while the enhanced p99 exceeded 1.1 s. The p99 values are empirical estimates from finite samples, not service guarantees. These measurements establish feasibility of local sequential scoring on the tested machine; they do not establish production real-time performance under representative conversation lengths, concurrency, or deployment traffic.

## 4.8 Chapter Summary

The revised F2 analysis aligns GroomShield's operating policy with recall and false-negative reduction. The primary seven-feature LSTM achieved 0.9153 PR-AUC, 0.8613 F2, 0.6613 precision, and 0.9318 recall, missing three of 44 positives. Against the matched weighted scorer, the paired improvements were +0.1103 PR-AUC and +0.0630 F2, with both 95% intervals above zero. The enhanced LSTM detected all 44 positives with 0.8429 F2 and 0.5176 precision. These results demonstrate the contribution of contextual and behavioral sequence modeling to broader conversation-level detection, with the coverage-precision tradeoff explicitly measured.
