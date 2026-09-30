# Thesis Defense Speaker Script

Updated September 30, 2026 for the 24-slide main presentation in **WASD - Thesis 2 - F2 and latency revised.pptx**. Slides 25-26 are hidden evidence backup; slides 27-31 are retained hidden template resources. Citations and the approved objective wording below are presenter references, not lines to read aloud.

## Slide 1: GroomShield

Good day. Our study asks a practical question: can a chat moderation system recognize a concerning conversation by following how it develops, rather than judging each message in isolation? GroomShield combines language context with a model of the conversation sequence. We built the module, compared it with simpler methods on the same conversations, and measured what happens when we prioritize finding positives. I will show the design first, then the evidence behind that choice.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, title and Sections 1.2-1.3

## Slide 2: Meet Our Team

I am presenting the work of Andrei Torres, Don Idos, Justin Arroco, and Michael Maala, advised by Manuel Calimlim Jr. We approached this as both a modeling problem and a moderation problem: a useful result must identify more conversations that deserve attention while making the review cost visible. That is the question that organizes the presentation.

Sources: Original presentation team slide.

## Slide 3: Background of the Study

A single message can be hard to judge without the exchange around it. Keyword filters catch explicit wording, but gradual or indirect interactions may only make sense across several turns. User reports also depend on someone recognizing the problem first. That gap motivates a module that follows how contextual evidence develops across a conversation and helps prioritize what a moderator should review.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.1; thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.2

## Slide 4: Research Questions

The research questions lead from the existing practice to our proposed module. We ask what keyword and rule-based approaches can detect, where they lose conversational meaning, and how machine learning can follow behavior across a chat. The final question is whether that complete module finds more positive conversations and reduces misses. Those questions determine the comparisons we report; they are not separate promises to label every message or predict the exact start of grooming.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.2

## Slide 5: Objectives of the Study

The approved objectives follow the same logic. First, assess the limits of conventional approaches. Second, build a module that combines conversational context with behavioral sequence analysis. Third, test whether that module reduces missed positive conversations. The general objective is an AI moderation module that strengthens human review. We kept these objectives intact and use the next alignment tables to show the method and evidence for each one.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 1.3

## Slide 6: Research Alignment: Existing Methods

For the first objective, we needed concrete comparators. We implemented a keyword rule and a method that takes the highest contextual score seen in a conversation. Both were tested on the same held-out conversations as the sequence models. The keyword rule found 27 of the 44 positives and missed 17. That result gives us a measured baseline for the question about static moderation. We did not run a separate field trial of an operational user-report system.

Sources: Alignment Table.docx, rows 1-2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 7: Research Alignment: Module and Improvement

The second objective is demonstrated by the working two-layer module and review interface. The third is answered by the controlled result: under our recall-oriented F2 policy, the Trajectory-Feature LSTM found 41 of 44 positive conversations and missed three, compared with six misses for the weighted scorer. The other LSTM variant found all 44, with a higher false-alert cost. We will return to that trade-off in the results section, because improving coverage alone is not the entire moderation decision.

Sources: Alignment Table.docx, rows 3-4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.2

## Slide 8: Why Context and Sequence Matter

DistilBERT helps interpret a turn in its nearby conversational context. The LSTM then follows how evidence changes over the full exchange. The Online Grooming Discourse Model motivated this attention to developing, recurring interaction rather than a fixed list of words or a rigid sequence of stages. We turn that motivation into measurable signals on the next slide.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 2.1-2.3; thesis_docs/Finals_Revised_Paper_WASD.md, Section 2.3 and references [11], [13]

## Slide 9: How OGDM Informs the Features

The table shows that translation. Current and peak scores let the model see whether contextual evidence appears and persists. A rising score or a spike followed by a drop captures change rather than a fixed keyword. Topic distance and turn-taking add information about where the exchange moves and how the two speakers participate. We call these theory-informed indicators, not direct OGDM stage labels. Their purpose is to give the LSTM a structured history to learn from.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 2.3 and 3.3.4; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.5

## Slide 10: AI Model Architecture

A new turn enters with recent context. Layer 1 produces an author-derived proxy score, while a fixed encoder supplies a current-turn embedding. Seven features track the conversation as it unfolds. The Trajectory-Feature LSTM receives those seven features; the Embedding-and-Feature LSTM receives them plus 768 embedding values. Each produces a conversation score, which a validation-selected cutoff turns into a flag for human review.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.2-3.4.2; thesis_docs/assets/AI_Model_Architecture_Diagram.svg; thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.1 and 3.4

## Slide 11: Dataset and Evaluation Scope

We selected PAN-2012 for the evaluation because it has ordered chats and speaker identifiers, which this sequence design requires. Our measured positive endpoint is a conversation containing an author on the official predator list. Layer 1 learns an author-derived proxy, and Layer 2 uses the unfolding signals to classify the conversation. This matters when interpreting the results: the final counts describe conversations, while turn scores are model inputs rather than independently verified grooming labels for individual messages.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 1.4 and 3.3.1; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1

## Slide 12: Why Authors Stay in One Partition

We preserve conversation order and construct derived resources using training data only. We also partition by connected authors, not by individual rows. If one chat has A and B and another has B and C, both chats stay in the same partition through their shared author. This prevents recurring participants from appearing in both development and test. We verified zero author overlap across the partitions.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3.3 and 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.1; thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3 and 3.5

## Slide 13: Models Compared Fairly

Our key comparison holds the input features constant. The weighted scorer combines the seven trajectory features without learning their order. The Trajectory-Feature LSTM receives the same seven features but learns from their sequence. If it improves, that is evidence for the value of the selected sequence aggregator over this static combination. The Embedding-and-Feature LSTM receives additional text information, so we report it alongside the others without pretending it is the same matched-input experiment.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.4.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.2-4.5

## Slide 14: Frozen Experimental Setup

Training contains 13,031 conversations, validation 1,827, and test 1,862. Only 44 test conversations are positive, so missed-case and false-alert counts matter alongside percentages. Connected authors stay in one partition. We selected operating cutoffs on validation and applied them to preserved test scores. The original evaluation used F0.5; the later F1 and F2 comparisons did not retrain the models or rerun inference.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1 and 4.2.1; thesis_docs/Finals_Revised_Paper_WASD.md, Section 3.5.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1-4.3

## Slide 15: Why We Use F2

The cutoff policy deserves its own explanation. F0.5 favors precision, F1 balances precision and recall, and F2 favors recall. Our research emphasis is reducing missed positive conversations, so F2 is the main reporting policy. We choose each cutoff on validation, not on the test set. The original evaluation used F0.5; afterward, we compared validation-selected F1 and F2 cutoffs on the preserved test scores. The model weights did not change. The three-policy tables will show exactly what that choice costs and gains.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.5.1-3.5.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1

## Slide 16: Conversation Results: F2 Policy

This table gives the main F2 result. The Trajectory-Feature LSTM found 41 of 44 positives and missed three, while producing 21 false alerts. The Embedding-and-Feature LSTM found all 44, with 41 false alerts. Both exceed the weighted scorer's 38 detections, although the two LSTMs make a different coverage-versus-workload trade-off. For the matched seven-feature comparison, the trajectory model also has stronger PR-AUC and F2 than the weighted scorer; the paired analysis behind that comparison appears shortly.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 17: Detection Performance Across Methods

PR-AUC describes how well a method ranks positive conversations across possible cutoffs; F2 describes our recall-oriented operating point. The embedding model has the highest observed PR-AUC, while the trajectory model has the highest observed F2. Neither figure alone declares a universal winner. For the specific sequence-model claim, compare the trajectory LSTM with weighted scoring: both use the same seven inputs, but only one learns their order.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2

## Slide 18: Missed Positives and False Alerts

Here the cost of greater coverage becomes concrete. The trajectory model cuts weighted scoring's six misses to three and also lowers false alerts from 24 to 21. The embedding model has no misses on these 44 positives but creates 41 false alerts. Maximum Layer 1 catches 39 positives yet produces 78 false alerts. Those are conversation counts, not individual messages. The question for an actual review team is how many extra alerts are acceptable for each additional positive found, which is why we tested other cutoff policies.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1 and Section 4.7

## Slide 19: Cutoff Choice: Coverage and Alerts

These six rows use the same two trained LSTMs and the same saved test scores; only the validation-selected cutoff changes. For the embedding model, F1 finds 43 of 44 positives with 14 false alerts, while F2 finds all 44 with 41 false alerts. That last positive adds 27 alerts in this test. The trajectory model behaves differently: F1 adds two alerts over F0.5 without finding another positive. F2 remains our main recall-first reporting policy. The table shows why a later moderator-workflow study must choose its operating point deliberately.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1 and Table 4.1a; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Recommendation 7; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1 and Table 4.1a

## Slide 20: Sequence Modeling Added Value

For the matched seven-feature comparison, we resampled whole author-connected groups 2,000 times and compared the trajectory LSTM with weighted scoring each time. The estimated gain is 0.1103 in PR-AUC and 0.0630 in F2, with both paired 95 percent intervals above zero. That supports the claim that the selected sequence model improves on static scoring of the same features. The observed miss reduction is real in this test, although its separate recall-difference interval includes zero. This is the evidence behind our sequence-model conclusion.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.2 and Section 4.5

## Slide 21: Local Turn-by-Turn Latency

We also tested the complete local scoring path, because a turn-by-turn prototype has to respond within a usable time. Across 160 sequential requests per model on this CPU, the trajectory model's median was 267 milliseconds and the embedding model's was 246. Their p95 times were about 709 and 718 milliseconds, while the embedding model had a longer p99 tail. The demo recomputes the full history after every turn, so longer conversations take longer. These timings establish local feasibility for the tested prefixes; concurrent users and production hardware remain a separate evaluation.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.4; thesis_docs/.benchmark_evidence/latency_2026-09-27.json

## Slide 22: Conclusions by Research Objective

We can now answer the objectives directly. The static methods exposed measurable coverage and false-alert limits. We delivered the contextual and sequence-based module with a working review interface. Under F2, the trajectory model reduced weighted scoring's six misses to three, and the embedding model found all 44 positives with a larger alert workload. The matched-input paired result supports the benefit of sequence modeling. Together, these results advance the general objective of strengthening conversation-level review while making the cutoff trade-off explicit.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Sections 5.1-5.2

## Slide 23: Next Evaluation Steps

We would first test the fixed models and cutoffs on contemporary chats and measure how moderators handle the resulting queue. The embedding model's F1 and F2 settings are the clearest workflow comparison: one additional positive at F2 came with 27 additional alerts in this test. The three trajectory-model misses were short conversations, so fixed-prefix testing also deserves attention. Production work still needs longer chats and concurrent-load measurement; onset detection requires independent expert annotations.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.3, especially Recommendation 7; thesis_docs/PANEL_COMMENTS_MATRIX.md; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.6

## Slide 24: GroomShield Reduced Missed Positives

GroomShield shows that following a conversation's development can strengthen chat review. The trajectory model has a supported advantage over static scoring of the same inputs, and the embedding model offers the highest observed coverage under F2. The alternative cutoffs show the practical price of that coverage rather than hiding it. Our contribution is a working two-layer system and a clear evidence base for deciding how to use it in a human review workflow. Thank you. We welcome your questions.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Sections 5.2-5.3

## Slide 25: The Three Missed Conversations Were Short [hidden]

The remaining trajectory-model misses help identify what to study next. Those positive conversations had only 2, 11, and 26 turns. Each is shorter than the 36-turn lower quartile of the positives that model detected. This suggests short-history performance deserves targeted testing. It does not identify the exact reason for each miss, and we did not have independently annotated grooming-onset times. The next study should assess fixed conversation prefixes before making an early-detection claim.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.6

## Slide 26: Baseline Policy Comparison [hidden]

If asked about the baselines under other cutoffs, this backup table contains the complete counts. Maximum Layer 1 rises from 23 to 39 detected positives as we move from F0.5 to F2, while false alerts rise from 18 to 78. Weighted scoring makes identical F0.5 and F1 decisions, then finds two more positives under F2 with 11 more false alerts. The keyword rule is binary, so its decisions do not change across the three policies. Every row uses the same 1,862 test conversations.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.1a; thesis_docs/.threshold_analysis/test_threshold_policy_comparison.json

## Slide 27: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.

Sources: Original presentation template

## Slide 28: PACIFIC COLLEGE [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.

Sources: Original presentation template

## Slide 29: Sustainable Development Goals  [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.

Sources: Original presentation template

## Slide 30: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.

Sources: Original presentation template

## Slide 31: Template asset [hidden]

Reference asset retained from the original presentation. This slide is hidden during the main defense.

Sources: Original presentation template

## Presenter reference: exact approved objectives

## 1.3 Objectives of the Study

__General Objective:__ Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

- __Specific Objective:__
	1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
	2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
	3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.
