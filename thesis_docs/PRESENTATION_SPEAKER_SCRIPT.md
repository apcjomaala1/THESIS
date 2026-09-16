# Thesis Defense Speaker Script

Updated September 16, 2026. Slide numbers match **WASD - Thesis 2 - panel revised.pptx**. Slides 1-34 form the main presentation. Slides 35-39 retain hidden template resources.

## Slide 1: CONVERSATION TRAJECTORY LAB

Good day. Our study developed a chat moderation module that combines language context with patterns across a conversation. We tested whether this combination could reduce the positive conversations missed by keyword rules and static scoring. I will connect our objectives to the methods, explain the model, and show the results.



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

The second half connects development and evaluation. For Objective 2, we implemented the complete two-layer pipeline and the review interface. For Objective 3, we assessed it on the locked held-out test. The primary LSTM identified 40 of 44 positives, so its recall was 90.91 percent. Its four misses were half the weighted scorer's eight and 76.5 percent fewer than the keyword rule's seventeen. These are measured comparisons against implemented methods. The module can complement reporting workflows, while an actual comparison with moderator reporting remains a separate study.



Sources: Alignment Table.docx, rows 3-4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 10: What the Study Built

The system has two learned layers. DistilBERT processes the current turn with up to two preceding turns. We then track seven features across the conversation. The LSTM combines that sequence into a conversation score. The practical output is a priority for human review. The moderator interprets the content and decides what action is appropriate.



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

Read the diagram from left to right. The current turn and up to two preceding turns enter the fine-tuned DistilBERT classifier. Its output is an author-derived contextual proxy score. A separate fixed base encoder represents the current turn for topic-distance calculation against the benign training reference. The pipeline combines those signals with speaker-turn information into seven features. The LSTM processes the ordered feature sequence and outputs a conversation score. A threshold selected on validation determines which conversations receive a flag for human review. The primary LSTM has seven inputs per turn. The enhanced experiment additionally feeds 768 embedding values into its recurrent model.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.2-3.4.2; thesis_docs/assets/AI_Model_Architecture_Diagram.svg

## Slide 19: Data Preparation and Controls

The controls make the comparison reproducible. We preserve original conversation and turn identifiers, maintain chronological context, and restrict this experiment to two-speaker conversations. Derived resources come from training data. Validation is used for selection. The held-out final test is then evaluated with those choices already fixed.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3 and 3.5

## Slide 20: Why Authors Stay in One Partition

Suppose one conversation contains authors A and B, and another contains B and C. The shared author B connects the conversations, so both stay in the same partition. The same rule applies to every connected group, including indirect connections. Otherwise the model could benefit from recognizing recurring participants or their language during testing. We verified zero overlap of conversations, authors, and connected components. The bootstrap analysis resamples these whole groups for the same reason: conversations linked by an author should not be treated as independent observations.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.3 and 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 21: Models Compared Fairly

The central comparison uses the same seven trajectory features. The weighted scorer combines them statically, while the LSTM learns a recurrent sequence model. This evaluates the selected aggregation methods with matched inputs. Keyword matching and maximum Layer 1 aggregation provide additional baselines. We report the enhanced LSTM separately because it also receives 768 embedding values. Feature-removal and ordering ablations would be needed to isolate individual design contributions.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.4.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.2-4.5

## Slide 22: Evaluation Measures

Because the test contains only 44 positive conversations among 1,862, we report precision-recall measures together with actual error counts. PR-AUC summarizes performance across thresholds. Precision measures the proportion of alerts that are positive. Recall measures the proportion of all positives that we find. We also report uncertainty using 2,000 bootstrap resamples of connected-author groups.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1-4.3

## Slide 23: Why We Use F0.5

F0.5 and recall serve different purposes in this experiment. We used validation F0.5 to choose an operating threshold that gives greater weight to precision, because a review queue has limited capacity and false alerts consume that capacity. In the F-beta formulation, beta of one-half weights precision four times as much as recall. We then separately report recall and false-negative counts to answer the research objective about missed cases. The selected model reached 85.11 percent precision and 90.91 percent recall on the final test, with seven false alerts and four missed positives. The operating threshold was 0.9688298. We did not optimize that threshold on the final test, and this rationale does not substitute for a future study of actual moderator workload.



Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2 and Section 4.7

## Slide 24: Results and Conclusions

These results come from the frozen held-out evaluation. The following table and graphs show the same accepted Chapter IV figures.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 25: Frozen Experimental Setup

The training set contains 13,031 conversations, validation contains 1,827, and the final test contains 1,862. There are 44 positive and 1,818 negative conversations in the final test. The manifest also retains 1,847 excluded historical-test conversations for complete accounting. We kept every connected-author group in one partition and froze all selection decisions before testing.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 26: Held-Out Results

This table shows all five methods. The primary LSTM reached PR-AUC of 0.9153, F0.5 of 0.8621, precision of 0.8511, and recall of 0.9091. It found 40 of the 44 positive conversations and made seven false alerts. The main architectural comparison is against the weighted scorer because both receive seven features. The enhanced LSTM has higher point estimates with additional embedding inputs. The paired comparison does not establish a performance difference between the two LSTMs.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 27: Detection Performance Across Methods

The blue bars show PR-AUC and the green bars show F0.5. Higher is better for both. The primary LSTM improves both measures over the keyword rule, maximum Layer 1 aggregation, and weighted scoring. The clearest architecture comparison is weighted scoring versus the primary LSTM because the inputs match. The enhanced LSTM also receives embeddings. These bars show point estimates, while the paper reports confidence intervals and paired differences.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 28: The Primary LSTM Found 40 of 44 Positives

Recall answers the question most directly connected to our third objective: how many positive conversations did we find? The primary LSTM found 40 out of 44, compared with 27 for the keyword rule, 23 for maximum Layer 1, and 36 for the weighted scorer. The enhanced LSTM found 41. The paired evidence supports the primary model's improvement over the three static baselines. One extra detected case does not establish superiority for the enhanced LSTM.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 29: Fewer Missed Cases and False Alerts

Lower bars are better here. The primary LSTM cut the weighted scorer's missed positives from eight to four, a 50 percent reduction, while also cutting false alerts from thirteen to seven. Compared with keyword matching, it reduced missed cases from seventeen to four, a 76.5 percent reduction. These counts show that the improved recall was accompanied by fewer false alerts at the selected operating points. The units are conversations, not individual messages.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1 and Section 4.7

## Slide 30: Sequence Modeling Added Value

We compared the models within the same 2,000 bootstrap resamples of author groups. For primary LSTM minus weighted scorer, the PR-AUC improvement was 0.1103 and the F0.5 improvement was 0.1121. Both paired 95 percent intervals remain above zero. This supports an advantage for the learned recurrent aggregator over the selected static combination of the same features. It establishes the architecture comparison as tested. It does not by itself quantify how much each feature or temporal ordering contributes individually.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.2 and Section 4.5

## Slide 31: The Four Missed Conversations Were Short

All four missed positives were short conversations: two, eleven, thirteen, and twenty-six turns. Each was shorter than the lower quartile of correctly detected positives, which was thirty-six turns. Their median was sixty-two. This is the main observed error pattern and is consistent with limited accumulated sequence evidence. It does not prove that length caused each miss or establish a minimum safe number of turns. We have not annotated the first onset of grooming, so these lengths cannot measure detection delay after onset. A future study should measure performance at fixed conversation prefixes, with onset annotations when evaluating time from onset.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.6

## Slide 32: Conclusions by Research Objective

These conclusions answer the approved objectives. First, the controlled comparison established the limitations of the tested static methods. Second, we implemented the complete contextual and behavioral module with a working review interface. Third, we measured higher recall and fewer false negatives, including half as many misses as weighted scoring. Together, the architecture and comparative results support the general objective of enhancing chat moderation. Our measured improvement is against the implemented keyword and score-based baselines.



Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 33: Next Evaluation Steps

The next stage is to test the completed system in conditions closer to a platform workflow. Contemporary external data can assess how performance transfers to current language and interaction patterns. Latency testing should measure the complete per-turn pipeline, including both transformer processing and sequence scoring, with median, p95, p99, and throughput. Expert-reviewed onset annotations are needed if we want to measure how quickly the model reacts after grooming begins. Ablations can identify which model components contribute most, and a separate protocol can extend the current two-speaker design to group conversations. The current demo provides sequential replay; production real-time performance remains to be measured.



Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.3; thesis_docs/PANEL_COMMENTS_MATRIX.md

## Slide 34: The LSTM Reduced Missed Cases

Our main result is that the learned trajectory model improved conversation detection over the tested static approaches, using the same seven inputs as the weighted comparator. It identified forty of forty-four positives with seven false alerts. Thank you. We welcome your questions about the architecture, data partitions, metric choice, and results.



Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 35: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 36: PACIFIC COLLEGE [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 37: Sustainable Development Goals  [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 38: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template

## Slide 39: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.



Sources: Original presentation template
