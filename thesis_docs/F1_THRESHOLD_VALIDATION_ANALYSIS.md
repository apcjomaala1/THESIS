# F0.5, F1, and F2 Threshold Analysis on Saved Validation Scores

**Updated:** September 19, 2026
**Population:** 1,827 validation conversations, including 49 positive conversations.

This analysis selects final conversation cutoffs by F1 and F2 using the already selected models and saved validation scores. It changes no learned weights, feature thresholds, weighted-scorer coefficients, checkpoint choices, active thresholds, or final-test artifacts. Existing cutoffs maximize F0.5 except the fixed binary keyword rule.

| Method | Policy | Threshold | Precision | Recall | F1 | F0.5 | F2 | TP | FP | FN |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Primary LSTM | Existing | 0.968829811 | 0.8780 | 0.7347 | 0.8000 | 0.8451 | 0.7595 | 36 | 5 | 13 |
| Primary LSTM | F1-selected | 0.957859278 | 0.8636 | 0.7755 | 0.8172 | 0.8444 | 0.7917 | 38 | 6 | 11 |
| Primary LSTM | F2-selected | 0.275535285 | 0.7288 | 0.8776 | 0.7963 | 0.7544 | 0.8431 | 43 | 16 | 6 |
| Enhanced LSTM | Existing | 0.955889165 | 0.9048 | 0.7755 | 0.8352 | 0.8756 | 0.7983 | 38 | 4 | 11 |
| Enhanced LSTM | F1-selected | 0.249406472 | 0.8723 | 0.8367 | 0.8542 | 0.8650 | 0.8436 | 41 | 6 | 8 |
| Enhanced LSTM | F2-selected | 0.000971102 | 0.6026 | 0.9592 | 0.7402 | 0.6510 | 0.8577 | 47 | 31 | 2 |
| Maximum Layer 1 | Existing | 0.981987655 | 0.7647 | 0.5306 | 0.6265 | 0.7027 | 0.5652 | 26 | 8 | 23 |
| Maximum Layer 1 | F1-selected | 0.979530394 | 0.6739 | 0.6327 | 0.6526 | 0.6652 | 0.6405 | 31 | 15 | 18 |
| Maximum Layer 1 | F2-selected | 0.961438656 | 0.4021 | 0.7959 | 0.5342 | 0.4462 | 0.6655 | 39 | 58 | 10 |
| Weighted scorer | Existing | 0.714994149 | 0.9143 | 0.6531 | 0.7619 | 0.8466 | 0.6926 | 32 | 3 | 17 |
| Weighted scorer | F1-selected | 0.714994149 | 0.9143 | 0.6531 | 0.7619 | 0.8466 | 0.6926 | 32 | 3 | 17 |
| Weighted scorer | F2-selected | 0.696637128 | 0.7347 | 0.7347 | 0.7347 | 0.7347 | 0.7347 | 36 | 13 | 13 |
| Keyword rule | Existing | 0.500000000 | 0.6765 | 0.4694 | 0.5542 | 0.6216 | 0.5000 | 23 | 11 | 26 |
| Keyword rule | F1-selected | 1.000000000 | 0.6765 | 0.4694 | 0.5542 | 0.6216 | 0.5000 | 23 | 11 | 26 |
| Keyword rule | F2-selected | 1.000000000 | 0.6765 | 0.4694 | 0.5542 | 0.6216 | 0.5000 | 23 | 11 | 26 |

## Primary LSTM result

F1 selects a cutoff of 0.957859278, compared with the existing 0.968829811. This changes 3 validation decisions: 3 new flags and 0 removed flags.
Validation true positives change from 36 to 38, false positives from 5 to 6, and false negatives from 13 to 11. No training or model inference was necessary.

F2 selects 0.275535285: TP 43, FP 16, FN 6; precision 0.7288, recall 0.8776, F2 0.8431.

## Interpretation and scope

- F2 gives recall greater weight than precision; compare additional detections against additional false alerts.
- These are validation results used to select the cutoff. They do not establish an improvement on unseen data.
- PR-AUC and ROC-AUC remain identical because the scores and labels are unchanged.
- The existing keyword rule is binary with a fixed 0.5 cutoff. Equivalent binary decisions can have different numerical cutoffs.
- The weighted scorer remains fitted using its original procedure. Its row compares cutoff choices on fixed scores; it is not a globally F1- or F2-refitted comparator.
- Existing Layer 1 and feature-construction uses of F0.5 remain unchanged. This is not a replacement of every F0.5 selection rule in the pipeline.
- No final-test data were accessed and no primary manuscript results were replaced. A later analysis on an already-examined test set must be identified accordingly.

## Reproduction

`python thesis_docs/.threshold_analysis/analyze_validation_f1.py`

The JSON receipt records input hashes, aggregate results and verification. The selector checks both F1 and F2 optima against independent exhaustive threshold calculations and sklearn. Saved F0.5 decisions are reproduced before comparison, and all methods use the same validation conversation labels. Existing filenames are retained to keep this comparison in one report.
