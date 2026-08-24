# THESIS EXPLAINER: ARCHITECTURE, RESULTS, AND DEFENSE GUIDE

This guide states the current study in plain language. It is designed for adviser consultation and panel defense and follows the same endpoint, model definitions, and results as the authoritative paper.

## 1. The Study in One Paragraph

The study tests whether an LSTM can identify PAN12 conversations containing an officially listed predator author more effectively than static scoring methods. Layer 1 uses DistilBERT with the current turn and up to two preceding turns to produce an author-derived proxy score. Seven features summarize how that proxy and the conversation structure evolve over time. Layer 2 processes the complete chronological sequence of those features. The primary comparison is fair by construction: the LSTM and weighted scorer receive the same seven features, use validation-selected configurations and thresholds, and are evaluated on the same author-disjoint final conversations.

## 2. What the Final Numbers Establish

The locked final test contains **1,862 conversations**, including 44 endpoint-positive and 1,818 endpoint-negative conversations. No final-test author appears in training or validation.

| Metric | Maximum Layer 1 proxy | Weighted scorer | Primary trajectory LSTM |
|---|---:|---:|---:|
| PR-AUC | 0.5523 | 0.8050 | **0.9153** |
| F0.5 | 0.5529 | 0.7500 | **0.8621** |
| Precision | 0.5610 | 0.7347 | **0.8511** |
| Recall | 0.5227 | 0.8182 | **0.9091** |
| TP / FP / FN / TN | 23 / 18 / 21 / 1,800 | 36 / 13 / 8 / 1,805 | **40 / 7 / 4 / 1,811** |

The primary result is the comparison with the weighted scorer. The LSTM improved PR-AUC by **0.1103** with a paired 95% bootstrap interval of **[0.0251, 0.2254]**, and improved F0.5 by **0.1121** with an interval of **[0.0194, 0.2336]**. Because both models receive the same seven inputs, these results support the contribution of learned recurrent aggregation.

The enhanced 775-input LSTM achieved a higher point estimate of 0.9483 PR-AUC, but its paired difference from the primary LSTM was inconclusive. The study does not claim the two models are equivalent.

## 3. Why PAN12 and Why Author-Derived Supervision?

### Panel question

> “Would message-level grooming labels be better? Are author-level labels being used only because PAN12 does not provide exhaustive message labels?”

### Defensible answer

> “Reliable message-level annotations would be appropriate for a different objective: determining whether a particular message expresses a defined grooming behavior. Our primary objective is conversation-level identification under the official PAN12 author endpoint.
>
> PAN12 was selected because its scale, chronological conversations, persistent speaker identifiers, and official predator-author list support both trajectory modeling and author-disjoint evaluation. We use author membership as weak supervision for Layer 1, not as a claim that every message by a listed author contains grooming. Layer 1 is therefore an author-proxy feature extractor, while the final model is trained and evaluated against the valid conversation endpoint.
>
> This choice preserves label validity and allows a rigorous unseen-author experiment. It also fixes the claim boundary: the system identifies conversations resembling the PAN12 positive-author class; it does not assign validated grooming labels, stages, or onset times to individual messages.”

Do not claim that author labels are universally better than ideal human message labels. The study did not compare those supervision regimes. Its empirical comparison is between aggregation methods under the author-derived endpoint.

## 4. The Exact Seven Features

1. **Peak proxy score:** largest Layer 1 proxy observed so far.
2. **Current proxy score:** current context-conditioned Layer 1 output.
3. **Spike count:** cumulative number of proxy scores above the frozen spike threshold.
4. **Spike-then-drop:** whether an earlier spike was followed by a sufficiently large decrease.
5. **Rate of change:** difference between consecutive proxy scores.
6. **Topic distance:** cosine distance from the benign training centroid using the base DistilBERT embedding.
7. **Turn-taking imbalance:** difference in the speakers' cumulative turn counts divided by total turns.

There is no EWMA or stage-depth feature in the evaluated model.

## 5. Defense Panel Q&A

### “How do you know the model did not memorize specific authors?”

The split is connected-author-disjoint. Any conversations sharing an author are placed in the same component and therefore the same partition. Raw author identifiers and labels are excluded from model text. Final-test authors are absent from training and validation.

### “What exactly did the LSTM beat?”

It beat the validation-fitted weighted scorer receiving the same seven trajectory features. The paired 95% intervals for PR-AUC, F0.5, precision, and recall were all above zero. It also outperformed the keyword rule and maximum Layer 1 proxy aggregation on the principal ranking and thresholded metrics.

### “Does Raw Layer 1 Max represent ideal message-level classification?”

No. Layer 1 receives a three-turn prefix and is trained on an author-derived proxy target. Raw Layer 1 Max tests whether taking the largest contextual proxy in a conversation is sufficient. It does not compare author supervision with a genuinely annotated message-level model.

### “Why use the seven-feature LSTM when the enhanced LSTM scored slightly higher?”

The enhanced model's point estimate was higher, but the paired interval was inconclusive. The primary model directly answers the matched-input research question and its recurrent classifier has 70,273 trainable parameters, compared with 463,489 for the enhanced recurrent classifier. The parameter advantage applies only to the recurrent component; both pipelines still require transformer inference.

### “Why emphasize PR-AUC and F0.5?”

Only 44 of 1,862 final-test conversations are positive. PR-AUC evaluates ranking quality under this imbalance. F0.5 prioritizes precision when selecting an operating threshold, while recall and the complete confusion matrix are reported so missed positive cases remain visible.

### “What happened in the four false negatives?”

They contained 2, 11, 13, and 26 turns. All four were shorter than the first quartile of correctly detected positive conversations (36 turns), so the remaining misses were concentrated among comparatively short conversations with less sequential evidence. The enhanced LSTM recovered two of the four, while two were missed by every evaluated method. This is a descriptive post-final analysis, not proof that length caused the errors, and it was not used for model or threshold selection.

### “Can the system be deployed now?”

The present evidence establishes the offline PAN12 endpoint result and supports selecting the LSTM for the prototype. The interface is designed around human review, but reviewer outcomes were not evaluated. External-dataset validation, platform-specific calibration, privacy and fairness assessment, and end-to-end latency and throughput testing are still required before deployment. A below-threshold output is not a declaration that a conversation is safe.

## 6. One-Sentence Conclusion

Under strict author-disjoint PAN12 evaluation, the seven-feature trajectory LSTM delivered a substantial and uncertainty-supported improvement over a matched static scorer, demonstrating the value of recurrent temporal aggregation for the study's conversation-level endpoint.
