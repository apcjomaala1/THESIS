# V. SUMMARY, CONCLUSIONS, AND RECOMMENDATIONS

## 5.1 Summary of Findings

This study delivered and evaluated a complete AI-powered moderation module that augments conventional chat moderation with contextual analysis and behavioral pattern tracking across ordered interactions. The two-layer system combines a context-conditioned DistilBERT classifier with an LSTM that models seven chronological trajectory features, supported by a working interface for sequential conversation review. To evaluate this architecture, PAN-2012 was selected because its chronological conversations and persistent speaker identifiers support trajectory modeling and author-disjoint testing. The experiment used connected-author partitions, validation-only selection, training-only derived resources, and a one-time held-out final evaluation.

The principal findings are:

1. The keyword rule and the maximum Layer 1 proxy exposed the limits of static lexical matching and isolated high-score aggregation in context-dependent conversations. The keyword rule attained 0.6136 recall with 17 false negatives, while the maximum Layer 1 proxy attained 0.5227 recall with 21 false negatives.
2. The completed module successfully integrated contextual message analysis with chronological behavioral modeling. Its primary seven-feature trajectory LSTM achieved a held-out PR-AUC of 0.9153, ROC-AUC of 0.9930, F0.5 of 0.8621, precision of 0.8511, recall of 0.9091, and specificity of 0.9961. It correctly identified 40 of 44 endpoint-positive conversations and produced seven false positives among 1,818 endpoint-negative conversations.
3. The proposed LSTM reduced false negatives to four: a 76.5% reduction from the keyword rule's 17, an 81.0% reduction from the maximum Layer 1 proxy's 21, and a 50.0% reduction from the weighted scorer's eight. Its recall of 0.9091 exceeded the keyword rule's 0.6136, the maximum Layer 1 proxy's 0.5227, and the weighted scorer's 0.8182.
4. In the matched architecture comparison, the primary LSTM improved PR-AUC over the validation-fitted weighted scorer by 0.1103 and F0.5 by 0.1121. The paired 95% connected-author bootstrap intervals for both differences were entirely above zero, supporting the predictive value of recurrent aggregation when both methods receive the same seven inputs.
5. The enhanced LSTM produced higher point estimates than the primary model, but the paired difference intervals contained zero. The experiment therefore supports neither a superiority nor an equivalence conclusion between the two LSTMs.

## 5.2 Conclusions

The conclusions directly answer the General Objective and three Specific Objectives of the study:

1. **Specific Objective 1 - Evaluate existing keyword-based and rule-based moderation approaches.** The controlled comparison confirmed the limitations of static moderation approaches in handling context-dependent communication. The keyword rule detected 27 of 44 positive conversations and produced 17 false negatives, while maximum Layer 1 aggregation detected 23 and produced 21 false negatives. These results demonstrate that isolated lexical matches and maximum contextual scores capture substantially less of the conversational evidence than the proposed sequential model.
2. **Specific Objective 2 - Design and develop the AI-based moderation module.** The study successfully implemented a complete two-layer module that applies machine learning and natural language processing across multiple chat interactions. It integrates context-conditioned DistilBERT scoring, seven interpretable behavioral trajectory features, recurrent LSTM aggregation, and a working interface for sequential conversation assessment and human review.
3. **Specific Objective 3 - Assess detection improvement and false-negative reduction.** The proposed module materially improved detection performance. The primary trajectory LSTM achieved 0.9091 recall and reduced false negatives to four: 76.5% fewer than the keyword rule, 81.0% fewer than maximum Layer 1 aggregation, and 50.0% fewer than the weighted scorer. The matched comparison further establishes that learned sequential aggregation contributed predictive value beyond static use of the same seven trajectory features. The module is designed to complement report-driven moderation, while its quantitative improvement is established against the tested keyword and score-based approaches.
4. **General Objective - Develop an AI-powered moderation module that enhances existing chat moderation.** The study achieved this objective by delivering and evaluating a complete contextual and behavioral moderation module. The results demonstrate that combining contextual NLP, interpretable behavioral trajectories, and recurrent sequence modeling strengthens detection coverage and substantially reduces false negatives compared with the tested traditional and static approaches.

## 5.3 Recommendations

Based on the results and remaining limitations, the study recommends:

1. Validate the frozen approach on an independent external corpus to measure cross-platform generalization. A message-level extension should use genuinely reviewed message annotations rather than repeating author labels across turns.
2. Conduct targeted feature-removal and architecture ablations to separate the contributions of ordering, recurrence, and each trajectory feature. This would extend the current architecture-level evidence by quantifying the contribution of individual design elements.
3. Measure probability calibration, end-to-end latency, throughput, memory use, and moderator-review outcomes as the next stage toward operational deployment. Human escalation rules and the consequences of false positives and false negatives should be evaluated explicitly.
4. Acquire representative contemporary and Philippine-context data, including Filipino and Taglish conversations where ethically and legally permissible, and perform privacy, fairness, and subgroup analyses to establish evidence for local deployment.
5. Extend preprocessing and evaluation to multi-party conversations through a separately frozen protocol that preserves participant identity boundaries and prevents author leakage.
