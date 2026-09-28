# Thesis Defense Speaker Script

Updated September 27, 2026. Slide numbers match **WASD - Thesis 2 - F2 and latency revised.pptx**. Slides 1-35 form the main presentation. Slides 36-40 retain hidden template resources.

## Slide 1: GroomShield

Good day. GroomShield combines language context with patterns across a conversation. We tested whether this design could reduce positive conversations missed by keyword rules and static scoring. I will connect our objectives to the model and results, then show how quickly the local prototype processes a turn.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, title and Sections 1.2-1.3

## Slide 2: Meet Our Team

Our team is Andrei Torres, Don Idos, Justin Arroco, and Michael Maala, with Manuel Calimlim Jr. as our project adviser.

Source: Original presentation team slide.

## Slide 3: Introduction

The problem begins with how conversations develop. A single turn may provide very little information. Our study examines whether recent context and the longer sequence together improve the evidence available to a moderator.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.1

## Slide 4: Template asset

Keyword filters remain useful for explicit language. The difficulty is that a conversation can develop through ordinary wording, indirect requests, or changing interaction patterns. Reports also depend on someone recognizing a problem. This motivated us to develop an additional module that examines context and the conversation sequence.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.1

## Slide 5: Statement of the Problem

Our research asks whether a system that follows the development of a conversation can identify more positive cases than static methods. We built the architecture to address that problem, then selected a dataset with ordered conversations and persistent speaker identifiers to evaluate it.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.2

## Slide 6: Research Questions

These slide questions summarize the unchanged research questions in the paper. The first two examine existing moderation and its limits. The third concerns the architecture we developed. The fourth asks whether the completed system improves recall and reduces missed cases. Recall means the fraction of positive conversations that the model identifies.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.2

## Slide 7: Objectives of the Study

The objectives remain the ones approved for the study. We evaluate conventional approaches, develop a module using context and behavioral patterns, and assess the improvement in detection. The next two slides show the alignment between these objectives, our methods, and the resulting evidence. The slide wording is abbreviated for presentation.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.3



Exact approved wording:

## 1.3 Objectives of the Study

__General Objective:__ Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

- __Specific Objective:__
	1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
	2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
	3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.


## Slide 8: Research Alignment: Existing Methods

This is the first half of the alignment table, shortened to keep one clear entry in each cell. Research Questions 1 and 2 both support Objective 1. We assessed the keyword rule on the same test conversations as the other methods. It identified 27 of 44 positives and missed 17. We also tested maximum Layer 1 aggregation, which uses the highest contextual score in a conversation. Comparing these methods with the LSTM establishes where the sequence model improves over static aggregation. We did not run a separate experiment against an operational user-report system.



Sources: Alignment Table.docx, rows 1-2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 9: Research Alignment: Module and Improvement

The second half connects development and evaluation. For Objective 2, we built the complete two-layer pipeline and review interface. For Objective 3, the Trajectory-Feature LSTM identified 41 of 44 positive conversations under the F2 policy, giving 93.18 percent recall. Its three misses were half the weighted scorer's six and 82.4 percent fewer than the keyword rule's seventeen. The F2 cutoffs came from validation and were applied to preserved test scores after the original evaluation. These are measured comparisons against implemented methods, not an operational comparison with user reports.



Sources: Alignment Table.docx, rows 3-4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 10: What the Study Built

The system has two learned layers. DistilBERT processes the current turn with up to two preceding turns. We then track seven features across the conversation. The Trajectory-Feature LSTM combines that sequence into a conversation score; an Embedding-and-Feature LSTM also receives text embeddings. The practical output is a priority for human review. The moderator interprets the content and decides what action is appropriate.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.1 and 3.4

## Slide 11: Dataset and Evaluation Scope

PAN-2012 met the study's need for a large collection of ordered conversations and stable speaker identifiers. For the evaluated outcome, a positive conversation contains at least one author on the official predator list. Layer 1 learns from author-derived supervision, and Layer 2 learns the conversation label. A turn-level score is an intermediate signal, so we do not interpret it as an independently verified grooming label for that message. This gives every comparison the same measurable conversation outcome.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 1.4 and 3.3.1; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 12: Why the Study Matters

The contribution is a complete contextual and behavioral architecture with a controlled comparison. It delivers a working review interface and evidence that learned aggregation improves detection over static use of the same inputs. For a moderation workflow, both kinds of errors matter: missed positive conversations and false alerts that consume review time.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.5; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.7

## Slide 13: Review of Related Literature

The literature supports two parts of our design: understanding language in context and following how interaction develops over time. The theory section explains why a sequence representation is appropriate.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Chapter II

## Slide 14: Why Context and Sequence Matter

Transformers help represent the current wording together with recent context. The LSTM addresses a different scale: how the evidence changes across the conversation. We evaluate their combination through the completed two-layer module.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 2.1-2.3

## Slide 15: Theory and Dataset Selection

Our theoretical basis is the Online Grooming Discourse Model, or OGDM. It describes interrelated conversational processes that can recur or overlap rather than always following one fixed order. That motivates tracking how evidence persists and changes across turns. We then selected PAN-2012 as the evaluation dataset because it provides the chronology and participant identifiers needed for this design.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 2.3 and references [11], [13]

## Slide 16: How OGDM Informs the Features

This table connects theory to computation. Peak and current scores, together with spike count, represent persistence and accumulation of contextual evidence. Rate of change and spike-then-drop represent increases and retreats. Topic distance measures movement away from a reference built from negative training conversations. Turn-taking imbalance summarizes participation within the pair. These are indicators motivated by the theory. We have not independently annotated them as OGDM stages, and the experiment does not establish the individual causal contribution of each feature.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 2.3 and 3.3.4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.5

## Slide 17: Methodology

I will now explain the model architecture, how we separated the data, and how we selected the operating threshold before the final test.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Chapter III

## Slide 18: AI Model Architecture

Read the diagram from left to right. Both variants start with contextual DistilBERT scoring and a fixed encoder for the current turn. The Trajectory-Feature LSTM directly receives seven behavioral features. The Embedding-and-Feature LSTM receives those features plus the 768 text-embedding values. Each learns a chronological sequence and uses its own validation-selected F2 cutoff to flag conversations for review.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.2-3.4.2; thesis_docs/assets/AI_Model_Architecture_Diagram.svg

## Slide 19: Data Preparation and Controls

The controls make the comparison reproducible. We preserve conversation and turn identifiers, maintain chronological context, and restrict this experiment to two-speaker conversations. Derived resources come from training data. Validation selects checkpoints and final F2 cutoffs. The F2 policy came after the original test evaluation, so its cutoffs were applied to saved test scores without retraining or rerunning inference.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3 and 3.5

## Slide 20: Why Authors Stay in One Partition

Suppose one conversation contains authors A and B, and another contains B and C. The shared author B connects the conversations, so both stay in the same partition. The same rule applies to every connected group, including indirect connections. Otherwise the model could benefit from recognizing recurring participants or their language during testing. We verified zero overlap of conversations, authors, and connected components. The bootstrap analysis resamples these whole groups for the same reason: conversations linked by an author should not be treated as independent observations.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.3 and 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 21: Models Compared Fairly

The central comparison uses the same seven trajectory features. The weighted scorer combines them statically, while the LSTM learns a recurrent sequence model. This evaluates the selected aggregation methods with matched inputs. Keyword matching and maximum Layer 1 aggregation provide additional baselines. We report the Embedding-and-Feature LSTM separately because it also receives 768 embedding values. Feature-removal and ordering ablations would be needed to isolate individual design contributions.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.4.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.2-4.5

## Slide 22: Evaluation Measures

Because the test contains 44 positive conversations among 1,862, we report both rates and actual error counts. PR-AUC summarizes ranking across cutoffs. Recall is the share of positives found; precision is the share of alerts that are positive. F2 combines both with extra weight on recall. We also report uncertainty using 2,000 bootstrap resamples of connected-author groups.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1-4.3

## Slide 23: Why We Use F2

GroomShield is a screening module, so the final decision policy emphasizes finding positive conversations that might otherwise be missed. We choose each method's cutoff by maximizing F2 on validation, giving more weight to recall while still accounting for precision. On the preserved test scores, the Trajectory-Feature LSTM found 41 of 44 positives with 21 false alerts; the embedding-and-feature model found all 44 with 41 false alerts. F2 changes the final decisions, not the trained weights. Because this policy came after the original F0.5 test evaluation, it is a revised-policy analysis, not a new untouched test.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2 and Section 4.7

## Slide 24: Results and Conclusions

The following table and graphs show the Chapter IV F2-policy analysis of saved test scores. A separate local benchmark later in the deck addresses the panel's latency question.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 25: Frozen Experimental Setup

Training contains 13,031 conversations, validation 1,827, and test 1,862. There are 44 positives in the test. We kept every connected-author group in one partition. The original test evaluation used F0.5 cutoffs. The revised F2 cutoffs were chosen only on validation and applied to saved test scores; no new model inference was run.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 26: Held-Out Results

This table shows all five methods under their validation-selected F2 cutoffs. The Trajectory-Feature LSTM reached PR-AUC 0.9153, F2 0.8613, precision 0.6613, and recall 0.9318. It found 41 of 44 positives with 21 false alerts. The Embedding-and-Feature LSTM found all 44 with 41 false alerts and F2 0.8429. The matched architecture comparison is with the weighted scorer, which uses the same seven inputs. Paired intervals do not establish an F2 or PR-AUC difference between the two LSTMs.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 27: Detection Performance Across Methods

The blue bars show PR-AUC and the green bars show F2. The Trajectory-Feature LSTM has the highest F2 point estimate, while the Embedding-and-Feature LSTM has the highest PR-AUC point estimate. Comparing the trajectory-feature model with weighted scoring isolates aggregation with the same seven inputs. The embedding-and-feature model also receives embeddings. These bars show point estimates; the manuscript reports paired intervals for the comparisons.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 28: Detection Coverage: 41 and 44 of 44

Recall asks how many positive conversations we found. The Trajectory-Feature LSTM found 41 of 44, compared with 27 for the keyword rule, 39 for maximum Layer 1, and 38 for the weighted scorer. The Embedding-and-Feature LSTM found all 44. That additional coverage came with 41 false alerts versus 21 for the trajectory-feature model. These are final-conversation decisions, not onset-detection measurements.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 29: Missed Positives and False Alerts

Lower bars are better in both groups, but the recall-oriented cutoff changes the tradeoff. The Trajectory-Feature LSTM reduced weighted scoring's six misses to three and its 24 false alerts to 21. Keyword matching missed 17. Maximum Layer 1 missed five but created 78 false alerts. The embedding-and-feature model missed none of the 44 positives and created 41 false alerts. Every count represents conversations, not messages.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1 and Section 4.7

## Slide 30: Sequence Modeling Added Value

We compared the Trajectory-Feature LSTM with the weighted scorer in the same 2,000 bootstrap resamples of author-connected groups. The PR-AUC difference was +0.1103 and the F2 difference +0.0630. Both paired 95 percent intervals were above zero. This supports the selected recurrent aggregator over the static combination of the same seven inputs. The separate recall-difference interval includes zero, so we do not claim an independently established recall advantage over weighted scoring.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.2 and Section 4.5

## Slide 31: The Three Missed Conversations Were Short

The three positives missed by the Trajectory-Feature LSTM were 2, 11, and 26 turns long. Each was shorter than the 36-turn first quartile of correctly detected positives, whose median length was 61 turns. This directs attention to short-history testing. Conversation length alone does not prove why a case was missed, and no grooming-onset annotations were used. A later study can test fixed prefixes and, with independent annotations, time from onset.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.6

## Slide 32: Local Turn-by-Turn Latency

We tested both selected LSTMs through the local HTTP demo, not just the recurrent layers. Each request included redaction, DistilBERT scoring, feature computation, the chosen LSTM, and the JSON response. We used the same synthetic chat at 1, 4, 8, and 16 turns, with 40 timed requests at each length for each model after warm-up. Across the equal-length mix, the Trajectory-Feature LSTM had a 267 ms median, 709 ms p95, 830 ms p99, and 3.39 sequential requests per second. The Embedding-and-Feature LSTM had 246 ms, 718 ms, 1,058 ms, and 3.32 requests per second. Longer chats took longer because the current demo recomputes all previous turns. This establishes local CPU behavior, not a production real-time guarantee.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.4; thesis_docs/.benchmark_evidence/latency_2026-09-27.json

## Slide 33: Conclusions by Research Objective

These conclusions answer the approved objectives. First, the controlled comparison showed the limitations and false-alert costs of the tested static methods. Second, we built the complete contextual and behavioral module with a working review interface. Third, the Trajectory-Feature LSTM found 41 positives and missed three, half as many misses as weighted scoring. Together, the architecture and results support the general objective of enhancing conversation-level chat moderation with human review.



Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 34: Next Evaluation Steps

The next stage is to test the selected F2 cutoffs on contemporary external data and evaluate the system under conditions closer to a real platform. We have now measured local sequential CPU latency, but production testing still needs longer chats, concurrent users, deployment hardware, memory use, and moderator outcomes. Caching or incremental computation may reduce the repeated prefix work. Expert-reviewed onset annotations are needed before claiming time-to-onset detection.



Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.3; thesis_docs/PANEL_COMMENTS_MATRIX.md

## Slide 35: GroomShield Reduced Missed Positives

GroomShield provides two tested sequence variants. The Trajectory-Feature LSTM found 41 of 44 positives with 21 false alerts and improved F2 over static use of the same inputs. The Embedding-and-Feature LSTM found all 44 with 41 false alerts. Both can support conversation review, with different measured coverage and precision. Thank you. We welcome your questions about the architecture, data partitions, F2 policy, latency, and results.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 36: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 37: PACIFIC COLLEGE [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 38: Sustainable Development Goals  [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 39: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 40: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template
