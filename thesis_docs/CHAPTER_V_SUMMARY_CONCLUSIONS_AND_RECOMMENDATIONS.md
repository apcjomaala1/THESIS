# V. SUMMARY, CONCLUSIONS, AND RECOMMENDATIONS

## 5.1 Summary of Findings

This study developed and evaluated an AI-powered moderation module that augments conventional chat moderation with contextual analysis and behavioral pattern tracking across ordered interactions. The completed two-layer system combines a context-conditioned DistilBERT classifier with an LSTM that models seven chronological trajectory features. For empirical evaluation, grooming-related interaction detection was operationalized using the PAN-2012 conversation-level endpoint: whether a dyadic conversation contains at least one author on the official predator list. The experiment used connected-author partitions, validation-only selection, training-only derived resources, and a one-time held-out final evaluation.

The principal findings are:

1. The keyword rule and the maximum Layer 1 proxy exposed the limits of static lexical matching and isolated high-score aggregation in context-dependent conversations. The keyword rule attained 0.6136 recall with 17 false negatives, while the maximum Layer 1 proxy attained 0.5227 recall with 21 false negatives.
2. The completed module successfully integrated contextual message analysis with chronological behavioral modeling. Its primary seven-feature trajectory LSTM achieved a held-out PR-AUC of 0.9153, ROC-AUC of 0.9930, F0.5 of 0.8621, precision of 0.8511, recall of 0.9091, and specificity of 0.9961. It correctly identified 40 of 44 endpoint-positive conversations and produced seven false positives among 1,818 endpoint-negative conversations.
3. The proposed LSTM reduced false negatives to four: a 76.5% reduction from the keyword rule's 17, an 81.0% reduction from the maximum Layer 1 proxy's 21, and a 50.0% reduction from the weighted scorer's eight. Its recall of 0.9091 exceeded the keyword rule's 0.6136, the maximum Layer 1 proxy's 0.5227, and the weighted scorer's 0.8182.
4. In the matched architecture comparison, the primary LSTM improved PR-AUC over the validation-fitted weighted scorer by 0.1103 and F0.5 by 0.1121. The paired 95% connected-author bootstrap intervals for both differences were entirely above zero, supporting the predictive value of recurrent aggregation when both methods receive the same seven inputs.
5. The enhanced LSTM produced higher point estimates than the primary model, but the paired difference intervals contained zero. The experiment therefore supports neither a superiority nor an equivalence conclusion between the two LSTMs.

## 5.2 Conclusions

The study draws the following conclusions:

1. Existing keyword-based and score-aggregation approaches are inadequate for the study's context-dependent detection task because they produced substantially more false negatives than the proposed sequential model. The results support incorporating conversational context and behavioral progression rather than relying only on isolated words or a single maximum score.
2. The study achieved its design-and-development objective by implementing a complete two-layer moderation module: contextual DistilBERT scoring at Layer 1, seven interpretable trajectory features, recurrent LSTM aggregation at Layer 2, and an interface for sequential conversation assessment.
3. The proposed module materially improved detection performance on the locked PAN12 evaluation. Its primary LSTM reached 0.9091 recall and reduced false negatives by 76.5% relative to the keyword rule, directly satisfying the study's emphasis on detecting interactions that traditional approaches miss. The matched weighted-scorer comparison further shows that the gain is attributable to the selected sequential aggregation architecture rather than additional input information.
4. These conclusions apply to the study's PAN12 author-derived conversation endpoint. They do not establish message-level grooming intent, grooming stage or onset, transfer to other platforms or languages, moderator outcomes, or production readiness.

## 5.3 Recommendations

Based on the results and remaining limitations, the study recommends:

1. Evaluate the frozen approach on an independent external corpus before making cross-platform or real-world grooming-detection claims. Any message-level extension should use genuinely reviewed message annotations rather than repeating author labels across turns.
2. Conduct targeted feature-removal and architecture ablations to separate the contributions of ordering, recurrence, and each trajectory feature. The present matched comparison establishes the value of the selected recurrent aggregator as a whole, not the causal importance of every feature.
3. Measure probability calibration, end-to-end latency, throughput, memory use, and moderator-review outcomes before considering operational deployment. Human escalation rules and the consequences of false positives and false negatives should be evaluated explicitly.
4. Acquire representative contemporary and Philippine-context data, including Filipino and Taglish conversations where ethically and legally permissible, and perform privacy, fairness, and subgroup analyses before local deployment claims are made.
5. Extend preprocessing and evaluation to multi-party conversations only through a separately frozen protocol that preserves participant identity boundaries and prevents author leakage.
