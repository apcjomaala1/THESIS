# GroomShield Defense Speaker Script

Updated October 1, 2026 for the 17-slide main sequence in `WASD - Thesis 2 - Adviser Flow Revised.pptx`. The seven hidden backup/template slides remain outside the spoken sequence. This script explains each slide rather than reading its text. Source lines are presenter references.

## Slide 1: GroomShield

Good day. GroomShield asks whether a moderation system can identify concerning chat conversations by following how the exchange develops. We combine contextual language analysis with an LSTM that learns from the ordered conversation. I will first show how the study aligns with our objectives, then explain the method and the results.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, title and Sections 1.2-1.3.

## Slide 2: Meet Our Team

This work was completed by Andrei Torres, Don Idos, Justin Arroco, and Michael Maala under the guidance of Manuel Calimlim Jr. Our focus was to build a working moderation module and test whether it finds more positive conversations than simpler comparison methods.

Sources: original presentation team slide.

## Slide 3: SDG and Research Agenda

The project supports SDG 9 by developing AI-assisted digital-safety infrastructure. It supports SDG 16 by improving how concerning online interactions can be identified for human review. Within the research agenda, it connects AI, analytics, and intelligent systems with cybersecurity and digital trust: the technology is a contextual language model followed by behavioral sequence modeling, and the application is safer chat moderation.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.5.5; Pseudoers THESIS2 Midterms Presentation.pdf, page 6, for the SoCIT agenda category names; https://apc.edu.ph/about-apc/ai_manifesto/ for APC's applied AI and cybersecurity context.

## Slide 4: Research Alignment - Existing Methods

Our first objective asks how far simpler moderation approaches go. We tested a keyword rule and a maximum contextual-score method on the same held-out conversations as the LSTMs. The keyword rule found 27 of 44 positive conversations and missed 17. The alignment table connects that measured limitation to the research question and its evidence. We did not run a field trial of an operational user-report system.

Sources: Alignment Table.docx, rows 1-2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2.

## Slide 5: Research Alignment - Module and Improvement

The next objective is the module itself: contextual DistilBERT, trajectory features, and an LSTM that follows those features through the chat. The third objective asks whether that design reduces missed positive conversations. Under the F2 reporting policy, the seven-feature LSTM missed three, compared with six for the weighted scorer; the embedding-and-feature LSTM missed none, with a higher alert count. The next slides explain how these comparisons were produced.

Sources: Alignment Table.docx, rows 3-4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2.

## Slide 6: AI Model Architecture

Each new turn enters with nearby conversational context. Layer 1 produces an author-derived proxy score, and the fixed encoder supplies a text embedding. Seven trajectory features summarize the developing conversation. One LSTM uses the seven features; the other receives those features plus the embedding. Each produces a conversation score for a validation-selected cutoff and human review. The turn-level score is an input to the system, not a verified label that grooming began at that message.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.2-3.4.2; thesis_docs/assets/AI_Model_Architecture_Diagram.svg.

## Slide 7: Dataset and Evaluation Scope

We selected PAN-2012 because its ordered chats and speaker identifiers support the sequence design. The evaluated positive endpoint is a conversation containing an author on the official predator list. That makes the final results conversation-level decisions. The study does not treat individual turns as independently annotated grooming events.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 1.4 and 3.3.1; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1.

## Slide 8: Frozen Experimental Setup

We divided conversations into training, validation, and final test by connected author groups. People who appear together through any chain of conversations stay in one partition, so the model does not encounter the same author in both development and test. The final test has 1,862 conversations, including 44 positives. All operating cutoffs came from validation; none were tuned on the test set.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.3 and 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1-4.2.

## Slide 9: Models Compared Fairly

The key controlled comparison gives the weighted scorer and Trajectory-Feature LSTM the same seven inputs. The weighted method combines their values without learning the turn order; the LSTM learns how they change across the sequence. The Embedding-and-Feature LSTM also receives text embeddings, so it is an additional model variant rather than the matched-input test of sequence aggregation. Both variants use the same upstream contextual classifier.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.4.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.2-4.5.

## Slide 10: Why We Use F2

The cutoff determines how readily the system flags a conversation. F0.5 favors precision, F1 balances precision and recall, and F2 gives more weight to recall. Because our objective emphasizes reducing missed positives, F2 is the main reporting policy, while we retain the false-alert counts. The original evaluation used F0.5; later we compared validation-selected F1 and F2 cutoffs on the saved test scores. The model weights and test set did not change.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.5.1-3.5.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1.

## Slide 11: Conversation Results - F2 Policy

These are the main held-out results under F2. The Trajectory-Feature LSTM found 41 of 44 positives and missed three, with 21 false alerts. The Embedding-and-Feature LSTM found all 44, with 41 false alerts. The weighted scorer found 38 and missed six. Both LSTMs improve positive-conversation coverage, while the two variants show different alert workloads. PR-AUC describes ranking across cutoffs; F2 describes the selected operating point.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2.

## Slide 12: Missed Positives and False Alerts

This graph turns the result into conversation counts. The trajectory model reduces the weighted scorer's six misses to three while also lowering false alerts from 24 to 21. The embedding model reaches zero misses on these 44 positives, with 41 false alerts. That is the coverage-versus-review-workload decision behind our threshold comparison. These are whole conversations, not individual messages.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.1 and Section 4.7.

## Slide 13: Sequence Modeling Added Value

This is the clearest test of the LSTM contribution. We compared the seven-feature LSTM with the weighted scorer using the same inputs and resampled whole author-connected groups. The LSTM gained 0.1103 PR-AUC and 0.0630 F2; both paired 95 percent intervals stayed above zero. That supports learned sequence aggregation over this static scoring baseline. We do not claim the separate recall-difference interval excludes zero.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.2 and Section 4.5.

## Slide 14: Cutoff Choice - Coverage and Alerts

The same trained LSTMs are shown at three validation-selected cutoffs. For the embedding model, F1 finds 43 of 44 positives with 14 false alerts. F2 finds all 44 but raises alerts to 41. In this test, catching the last positive adds 27 alerts. F2 remains our recall-oriented reporting policy, while this comparison gives a moderator team a concrete alternative to evaluate in an independent workflow study.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1 and Table 4.1a; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Recommendation 7.

## Slide 15: Local Turn-by-Turn Latency

We also measured the full local scoring path after each new turn. In 160 sequential requests per model on a Windows 11 laptop with an Intel i5-11400H CPU, the trajectory model's median was 267 milliseconds and the embedding model's was 246. Their 95th-percentile times were about 709 and 718 milliseconds. These figures show usable local response times for the tested chat prefixes; concurrent users and longer histories still need a separate load test.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.4; thesis_docs/.benchmark_evidence/latency_2026-09-27.json.

## Slide 16: Conclusions by Research Objective

The study answers the approved objectives in order. The keyword and static comparisons quantify what the conventional methods miss. We built the two-layer contextual and sequence module. Under F2, the seven-feature LSTM cut weighted scoring's six missed positives to three, while the embedding model found all 44 at a greater alert cost. The matched-input paired analysis supports the value of learning the sequence. Together, these results strengthen conversation-level human review.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Sections 5.1-5.2.

## Slide 17: Recommendations

The next step is to test the frozen models and cutoffs on contemporary external chats and observe moderator workload. The embedding model's F1 and F2 settings make that review trade-off especially clear. We should also benchmark longer histories and concurrent traffic. If future work aims to identify grooming onset, it first needs independent expert annotations. GroomShield has already demonstrated stronger held-out conversation coverage; these studies will determine how best to use that capability in practice. Thank you. We welcome your questions.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.3; thesis_docs/PANEL_COMMENTS_MATRIX.md; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.6.

## Presenter reference: exact approved objectives

General Objective: Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.

## Hidden evidence backups

The hidden short-conversation slide and full baseline-policy table remain available for questions. Five additional hidden slides are retained template resources. They are not part of the 17-slide presentation.
