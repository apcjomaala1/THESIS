# Targeted Audit: Chapters 1-2 vs Chapter 3 TEMPORARY

Source rule used here:

- **Chapter 3 TEMPORARY.docx is the latest Chapter 3 source.**
- **Main paper Chapters 1-3.docx is used for Chapters 1 and 2 only.**
- The private tech demo is not treated as thesis evidence.

Target labels below use Word paragraph numbers extracted directly from the `.docx` files:

- `Main Paper P###` = paragraph number from `Main paper Chapters 1-3.docx`
- `Ch3 Temp P###` = paragraph number from `Chapter 3 TEMPORARY.docx`

These paragraph numbers may shift after edits, so each item also includes exact text to search for.

## Terminology Rule

Your adviser's advice to avoid **system** is reasonable. In this thesis, use:

- **moderation module** for the proposed artifact/component
- **proposed approach** for the research method or model strategy
- **prototype** when emphasizing experimental status
- **existing moderation systems** only when referring to external/current platform moderation systems

In short: **module is appropriate**. It sounds like a bounded component that augments a larger moderation workflow, which fits the thesis better than "system."

## Priority 1 - Edits Needed for Scope and Consistency

### A01 - Replace "system" wording in Chapter 1 Background

Target:

- `Main Paper P038`, Chapter 1.1 Background of the Study

Find this exact paragraph:

> This study proposes the development of an AI-powered moderation approach designed to augment existing chat filtering and reporting mechanisms. The approach leverages machine learning, natural language processing, and behavioral pattern analysis to detect grooming-related interactions within chat environments. By combining content-level analysis with user behavior modeling, the proposed approach aims to address the limitations of current moderation systems and contribute to safer and more responsive digital communication platforms.

Issue:

This paragraph is mostly good already. It uses **approach**, not **system**, for the proposed work. The only potential issue is the ending phrase "moderation systems," but that refers to existing systems, so it is acceptable.

Recommendation:

No required edit. If you want stricter adviser-safe wording, revise only the last phrase.

Suggested revision:

> This study proposes the development of an AI-powered moderation approach designed to augment existing chat filtering and reporting mechanisms. The approach leverages machine learning, natural language processing, and behavioral pattern analysis to detect grooming-related interactions within chat environments. By combining content-level analysis with user behavior modeling, the proposed approach aims to address the limitations of existing moderation methods and contribute to safer and more responsive digital communication platforms.

### A02 - Narrow "across multiple interactions" to match Chapter 3's conversation-level method

Target:

- `Main Paper P039`, Chapter 1.1 Background of the Study
- Related Chapter 3 target: `Ch3 Temp P048`, `Ch3 Temp P049`

Find this exact paragraph:

> Unlike traditional moderation systems that analyze messages in isolation, the proposed approach integrates conversational context and behavioral pattern tracking across multiple interactions to enable earlier and more accurate detection of grooming-related interactions. Grooming is prioritized due to its reliance on contextual and behavioral progression, making it a suitable case for evaluating the effectiveness of the proposed approach.

Issue:

"Across multiple interactions" is a little broad. Chapter 3 Temporary describes ordered conversation records, message turns, and conversation-level trajectory scoring. It does not clearly claim cross-platform or cross-session user tracking.

Recommendation:

Change "across multiple interactions" to "across multiple message turns within a conversation."

Suggested revision:

> Unlike traditional moderation systems that analyze messages in isolation, the proposed approach integrates conversational context and behavioral pattern tracking across multiple message turns within a conversation to enable earlier and more accurate detection of grooming-related interactions. Grooming is prioritized due to its reliance on contextual and behavioral progression, making it a suitable case for evaluating the effectiveness of the proposed approach.

### A03 - Replace "system" in Research Question 4

Target:

- `Main Paper P048`, Chapter 1.2 Statement of the Problem

Find this exact paragraph:

> To what extent can an AI-driven moderation system improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

Issue:

Adviser prefers avoiding "system." Since this is your proposed work, "module" or "approach" is better.

Suggested revision:

> To what extent can an AI-driven moderation module improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

Alternative:

> To what extent can an AI-driven moderation approach improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

### A04 - Remove filler sentence before objectives

Target:

- `Main Paper P052`, Chapter 1.3 Objectives of the Study

Find this exact paragraph:

> This section outlines the goals of the research. It includes:

Issue:

This is meta-writing. It does not add content and sounds like a template.

Recommendation:

Delete the paragraph. Start directly with the General Objective.

### A05 - Replace "system" in General Objective only if adviser is strict

Target:

- `Main Paper P053`, Chapter 1.3 Objectives of the Study

Find this exact paragraph:

> General Objective: Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

Issue:

This is mostly good because the proposed artifact is called a **module**. "Existing chat moderation systems" refers to external systems, so it is acceptable.

Recommendation:

No required edit. If adviser wants near-total avoidance of "system," use "methods" or "workflows."

Suggested revision:

> General Objective: Develop an AI-powered moderation module that enhances existing chat moderation workflows by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

### A06 - Replace "system" in Specific Objective 4

Target:

- `Main Paper P058`, Chapter 1.3 Objectives of the Study

Find this exact paragraph:

> Assess the improvement in detecting harmful interactions achieved by the proposed AIdriven moderation system compared to traditional moderation approaches.

Issue:

This uses "system" for the proposed work. Also, the hyphen in "AI-driven" appears corrupted in the document as a control/encoding character.

Suggested revision:

> Assess the improvement in detecting harmful interactions achieved by the proposed AI-driven moderation module compared to traditional moderation approaches.

### A07 - Keep Chapter 1 scope aligned with Chapter 3 Temporary's dataset scope

Target:

- `Main Paper P066`, Chapter 1.4.1 Scope of the Study
- Related Chapter 3 targets: `Ch3 Temp P017`, `Ch3 Temp P019`, `Ch3 Temp P020`, `Ch3 Temp P126`

Find this exact paragraph:

> For evaluation, the prototype is tested using PAN12-derived data, real conversation datasets, and synthetically generated annotated chat data. This allows the study to assess its performance in handling context-dependent and behavior-based grooming detection scenarios.

Issue:

This paragraph already matches Chapter 3 Temporary well. It is stronger and more specific than the older "public datasets + simulated data" wording.

Recommendation:

Keep it. No edit needed unless Table 3.1 in Chapter 3 is changed.

### A08 - Replace "prototype system" and "system" in limitations

Target:

- `Main Paper P068`, Chapter 1.4.2 Limitations of the Study

Find this exact paragraph:

> This study is limited to the development of a prototype system and does not involve full deployment in a live chat environment. The scope is further limited to grooming-related interactions. As such, the system will not be tested with real users, and its performance is evaluated only through controlled datasets and simulations.

Issue:

This paragraph uses "system" twice for the proposed artifact. It also correctly distinguishes offline evaluation from live deployment, so keep that idea.

Suggested revision:

> This study is limited to the development of a prototype moderation module and does not involve full deployment in a live chat environment. The scope is further limited to grooming-related interactions. As such, the module will not be tested with real users, and its performance is evaluated only through controlled datasets and simulations.

### A09 - Fix grammar in limitations paragraph

Target:

- `Main Paper P071`, Chapter 1.4.2 Limitations of the Study

Find this exact paragraph:

> Additionally, while the prototype simulates sequential analysis of chat message the implementation is conducted within a simulated environment. Actual performance in real-world deployment may vary depending on system integration, scalability, and data variability. The study also does not account for all possible variations in language, cultural context, or evolving evasion techniques used by malicious users.

Issue:

"chat message the implementation" is grammatically broken. This is also the best place to state the offline/real-time distinction once. Do not repeat the explanation elsewhere.

Suggested revision:

> Additionally, while the prototype simulates sequential analysis of chat messages, the evaluation is conducted within a controlled offline environment rather than a live deployment. Actual performance in real-world deployment may vary depending on platform integration, scalability, latency, and data variability. The study also does not account for all possible variations in language, cultural context, or evolving evasion techniques used by malicious users.

### A10 - Reorder Significance subsections

Target:

- `Main Paper P074`, Chapter 1.5.2 Industry and Practical Applications
- `Main Paper P076`, Chapter 1.5.1 Academic Contribution

Find these exact headings:

> 1.5.2 Industry and Practical Applications

then later:

> 1.5.1 Academic Contribution

Issue:

The subsections are out of order. Academic Contribution should come before Industry and Practical Applications if numbered 1.5.1 and 1.5.2.

Recommendation:

Move the whole `1.5.1 Academic Contribution` section before `1.5.2 Industry and Practical Applications`, or renumber them if the current order is intentional.

### A11 - Replace "system" in Industry and Practical Applications

Target:

- `Main Paper P075`, Chapter 1.5.2 Industry and Practical Applications

Find this exact paragraph:

> For the technology industry and online platform providers, this research has significant practical implications. Chat-based platforms, gaming communities, social networks, and collaborative tools can leverage the proposed moderation module to enhance user safety and platform integrity. By automating the detection of harmful interactions, platforms can reduce the burden on manual moderation teams, enabling them to focus on complex cases requiring human judgment. The real-time analysis capability of the system allows for immediate detection and flagging of suspicious behavior, reducing response time and limiting prolonged exposure to harmful interactions. This is particularly critical for platforms serving vulnerable user populations, including minors. Furthermore, the proposed system can be integrated into existing infrastructure without replacing current filtering mechanisms, offering a scalable and non-disruptive enhancement to platform safety. The adoption of such advanced moderation techniques positions platforms as responsible actors in digital safety, potentially building user trust and reducing legal liabilities.

Issue:

This paragraph calls the proposed artifact "system" twice. It is also a bit too implementation-heavy for a thesis proposal if read literally.

Suggested revision:

> For the technology industry and online platform providers, this research has significant practical implications. Chat-based platforms, gaming communities, social networks, and collaborative tools can leverage the proposed moderation module to enhance user safety and platform integrity. By supporting the detection of harmful interactions, platforms can reduce the burden on manual moderation teams, enabling them to focus on complex cases requiring human judgment. The real-time analysis capability of the module may allow earlier detection and flagging of suspicious behavior, reducing response time and limiting prolonged exposure to harmful interactions. This is particularly critical for platforms serving vulnerable user populations, including minors. Furthermore, the proposed module can be adapted into existing moderation workflows without replacing current filtering mechanisms, offering a scalable and non-disruptive enhancement to platform safety. The adoption of such advanced moderation techniques positions platforms as responsible actors in digital safety, potentially building user trust and reducing legal liabilities.

### A12 - Replace "system" in Academic Contribution

Target:

- `Main Paper P077`, Chapter 1.5.1 Academic Contribution

Find this exact paragraph:

> This research contributes to the academic field of computer science, artificial intelligence, and cybersecurity by advancing the understanding of AI-driven content moderation. The proposed system bridges a gap in existing literature by demonstrating how machine learning and natural language processing can be effectively combined with behavioral pattern analysis to detect nuanced forms of harmful communication. This work provides a novel framework for contextual analysis in chat systems that goes beyond traditional keyword-based approaches. The findings will be valuable for researchers exploring AI applications in safety and security, offering insights into feature extraction techniques, model architecture, and evaluation methodologies for detecting complex communication patterns. Additionally, this study contributes to theoretical knowledge in understanding grooming-related interactions in digital environments, providing empirical evidence on the effectiveness of AI-driven solutions in this domain.

Issue:

"The proposed system" should become "The proposed module" or "The proposed approach." Since this paragraph discusses contribution and methodology, "approach" is slightly better.

Suggested revision:

> This research contributes to the academic field of computer science, artificial intelligence, and cybersecurity by advancing the understanding of AI-driven content moderation. The proposed approach bridges a gap in existing literature by demonstrating how machine learning and natural language processing can be combined with behavioral pattern analysis to detect nuanced forms of harmful communication. This work provides a framework for contextual analysis in chat moderation that goes beyond traditional keyword-based approaches. The findings will be valuable for researchers exploring AI applications in safety and security, offering insights into feature extraction techniques, model architecture, and evaluation methodologies for detecting complex communication patterns. Additionally, this study contributes to theoretical knowledge in understanding grooming-related interactions in digital environments.

## Priority 2 - Chapter 2 Alignment and Proofreading

### B01 - Fix "SchurgerFoy" spelling/formatting

Target:

- `Main Paper P113`, Chapter 2.1 Review of Related Literature

Find this exact paragraph:

> Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. SchurgerFoy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history.

Issue:

"SchurgerFoy" appears to be missing a hyphen or spacing. Also check the paragraph in Word because it contains odd line/control characters around the next sentence.

Suggested revision:

> Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. Schurger-Foy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history.

### B02 - Make the cross-platform gap match Chapter 3 Temporary

Target:

- `Main Paper P125`, Chapter 2.2 Related Studies
- Related Chapter 3 target: `Ch3 Temp P003`, `Ch3 Temp P048`, `Ch3 Temp P049`

Find this exact paragraph:

> While these studies demonstrate the effectiveness of AIbased moderation tools, most implementations analyze localized chat contexts within single sessions. As a result, they often fail to model behavioral trajectories that evolve across multiple conversations or platforms over time.

Issue:

Chapter 3 Temporary models trajectory over ordered message turns and conversation history. It does not clearly implement cross-platform tracking or user identity linking across platforms. The phrase "across multiple conversations or platforms" may overstate the scope.

Suggested revision:

> While these studies demonstrate the effectiveness of AI-based moderation tools, many approaches still analyze localized chat contexts or isolated messages. As a result, they may fail to model behavioral trajectories that evolve across multiple turns within a conversation.

### B03 - Keep multimodal indicators as future scope, not current method

Target:

- `Main Paper P132`, Chapter 2.3 Theoretical Background

Find this exact paragraph:

> However, current methodologies often evaluate textbased data in isolation and neglect multimodal behavioral indicators such as spatial interaction patterns or economic incentives within digital environments.

Issue:

Chapter 3 Temporary is text/chat focused. It uses DistilBERT, message risk scores, topic drift, turn-taking imbalance, spike count, and score progression. It does not operationalize spatial behavior, item gifting, images, video, avatar movement, or Robux/economic behavior.

Suggested revision:

> However, current methodologies often evaluate text-based data in isolation and may fail to capture longer conversational progression across message turns. Multimodal behavioral indicators, such as spatial interaction patterns or economic incentives within digital environments, remain outside the scope of the present study and are recommended for future work.

### B04 - Keep "high-speed real-time" but avoid implying live evaluation

Target:

- `Main Paper P134`, Chapter 2.3 Theoretical Background

Find this exact paragraph:

> To address these challenges, contemporary research recommends hybrid moderation frameworks combining automated AIbased triage with humanintheloop (HITL) review mechanisms. Such layered architectures enable highspeed realtime flagging of suspicious interactions while preserving human oversight for nuanced adjudication and minimizing algorithmic bias.

Issue:

This is acceptable as literature/theory, but make sure Chapter 1 limitations carries the one-time clarification that your evaluation is offline. No need to repeat that here.

Suggested minor cleanup:

> To address these challenges, contemporary research recommends hybrid moderation frameworks combining automated AI-based triage with human-in-the-loop (HITL) review mechanisms. Such layered architectures enable high-speed real-time flagging of suspicious interactions while preserving human oversight for nuanced adjudication and minimizing algorithmic bias.

### B05 - Encoding/control-character cleanup across Chapters 1 and 2

Targets:

- `Main Paper P041`
- `Main Paper P056`
- `Main Paper P057`
- `Main Paper P058`
- `Main Paper P112`
- `Main Paper P121`
- `Main Paper P122`
- `Main Paper P123`
- `Main Paper P124`
- `Main Paper P125`
- `Main Paper P127`
- `Main Paper P131`
- `Main Paper P132`
- `Main Paper P134`
- `Main Paper P135`

Find examples like:

> keywordbased

> rulebased

> AIbased

> realtime

Problem:

These are not normal hyphens. They appear as control characters or encoding artifacts in the extracted Word text. They may render badly in PDF or when copied.

Recommendation:

Replace all corrupted hyphen/control-character forms with normal hyphens:

- keyword-based
- rule-based
- AI-based
- real-time
- child-centric
- machine learning-driven
- self-disclosure
- trust-building
- human-in-the-loop

## Priority 3 - Chapter 3 TEMPORARY Internal Edits

### C01 - Replace "system" in Chapter 3 opening objective

Target:

- `Ch3 Temp P002`, 3.1 Research Design

Find this exact paragraph:

> This study will employ a developmental and experimental research design. The primary objective is to design and evaluate an AI-powered chat moderation prototype for detecting grooming-related interactions. The study focuses on combining message-level contextual analysis using DistilBERT with conversation-level behavioral trajectory scoring to improve moderation performance beyond traditional keyword-based approaches.

Issue:

This paragraph is mostly good. It avoids "system" for the proposed artifact and uses "prototype." No required edit.

Optional suggested revision:

> This study will employ a developmental and experimental research design. The primary objective is to design and evaluate an AI-powered moderation module for detecting grooming-related interactions in chat conversations. The study focuses on combining message-level contextual analysis using DistilBERT with conversation-level behavioral trajectory scoring to improve moderation performance beyond traditional keyword-based approaches.

### C02 - Change "across conversations" to "across conversation turns"

Target:

- `Ch3 Temp P003`, 3.1 Research Design

Find this exact paragraph:

> The prototype consists of three primary stages: (1) data collection and preprocessing, (2) message-level model development using DistilBERT, and (3) comparative evaluation against a rule-based keyword moderation baseline. In addition, the study proposes a conversation-level trajectory scoring component that utilizes behavioral indicators derived from message risk progression across conversations. An LSTM-based sequence modeling approach is also explored as a proposed extension for future development.

Issue:

"Across conversations" sounds like the model links multiple separate conversations. The described methodology is turn-by-turn analysis within ordered conversation histories.

Suggested revision:

> The prototype consists of three primary stages: (1) data collection and preprocessing, (2) message-level model development using DistilBERT, and (3) comparative evaluation against a rule-based keyword moderation baseline. In addition, the study proposes a conversation-level trajectory scoring component that utilizes behavioral indicators derived from message risk progression across conversation turns. An LSTM-based sequence modeling approach is also explored as a proposed extension for future development.

### C03 - Check dataset scope in Research Design against Data Collection

Target:

- `Ch3 Temp P005`, 3.1 Research Design
- `Ch3 Temp P017`, 3.3.1 Data Collection

Find this exact paragraph:

> The proposed models will be validated offline using the PAN12-derived dataset to establish baseline and enhanced performance metrics. Performance will be evaluated quantitatively using classification metrics such as recall, precision, F1-score, and comparative analysis against traditional moderation approaches.

Compare with:

> The study utilizes a combination of publicly available datasets, real conversation datasets, and synthetically generated annotated chat data for model training and evaluation.

Issue:

P005 says validation uses the PAN12-derived dataset. P017 says the study uses public, real conversation, and synthetic datasets for training/evaluation. Both can be true if PAN12 is primary and the others are supplementary, but the relationship should be explicit.

Suggested revision for P005:

> The proposed models will be validated offline using PAN12-derived data as the primary benchmark, with real conversation datasets and synthetically generated annotated chat data used where applicable to supplement underrepresented interaction patterns. Performance will be evaluated quantitatively using classification metrics such as recall, precision, F1-score, and comparative analysis against traditional moderation approaches.

Alternative if PAN12 only is truly evaluated:

> The proposed models will be validated offline using the PAN12-derived dataset to establish baseline and enhanced performance metrics. Real conversation datasets and synthetically generated annotated chat data are treated as supplementary sources for future evaluation and controlled examples.

### C04 - Table 3.1 still marks study dataset as future while prose says it is used

Target:

- `Ch3 Temp P019`, prose
- `Ch3 Temp P034` to `Ch3 Temp P037`, Table 3.1 Study Dataset row

Find this exact prose paragraph:

> In addition to PAN12-derived data, the study incorporates real conversation datasets collected and annotated for research purposes. These datasets contain per-message labels and conversation identifiers, enabling both message-level analysis and reconstruction of ordered conversation sequences for behavioral and trajectory-based analysis.

Find this exact table row:

> Study Dataset (provided)
> Institutional/platform logs (proposed future data source)
> Variable
> Per-message + Conversation ID

Issue:

The prose says real conversation datasets are incorporated. The table says the study dataset is a proposed future data source. Pick one.

Suggested table source cell if used now:

> Anonymized real conversation datasets collected and annotated for research purposes

Suggested table source cell if future only:

> Institutional/platform logs (proposed future data source; not included in current evaluation)

If using the future-only version, also revise P019 so it does not say "the study incorporates."

### C05 - PAN12 label type is under-described

Target:

- `Ch3 Temp P029` to `Ch3 Temp P032`, Table 3.1 PAN12 row

Find this exact table row:

> PAN12 Sexual Predator Dataset
> PAN12 Competition Corpus
> Conversation count determined from the PAN12-derived split used in this study
> Per-conversation

Issue:

Chapter 3 also discusses message-level labels, suspicious annotations, and DistilBERT message-level training. If PAN12-derived data includes suspicious-line annotations, the table should say so.

Suggested label type:

> Per-conversation + suspicious-line annotations

If no suspicious-line annotations are used, revise the message-level training language instead.

### C06 - Tighten "may additionally" if trajectory snapshots are core

Target:

- `Ch3 Temp P049`, 3.3.2 Data Preprocessing

Find this exact paragraph:

> For trajectory-based analysis, conversation data may additionally be represented as sequential conversation instances corresponding to message turns. These instances are intended to support the analysis of how behavioral risk indicators evolve throughout a conversation. The processed data is then used for message-level classification and conversation-level behavioral scoring.

Issue:

Trajectory scoring is central to the methodology, so "may additionally" sounds optional or uncertain.

Suggested revision:

> For trajectory-based analysis, conversation data is represented as sequential conversation instances corresponding to message turns. These instances support the analysis of how behavioral risk indicators evolve throughout a conversation. The processed data is then used for message-level classification and conversation-level behavioral scoring.

### C07 - Clarify "existing predatory classifier" in Table 3.2

Target:

- `Ch3 Temp P071` to `Ch3 Temp P073`, Table 3.2

Find this exact table row:

> Per-message risk score
> Output of existing predatory classifier (0–1)
> Message

Issue:

"Existing predatory classifier" sounds like an external tool. It should refer to the proposed message-level classifier.

Suggested table row:

> Per-message risk score
> Output of the message-level DistilBERT classifier (0-1)
> Message

### C08 - Fix awkward "precomputational step" wording

Target:

- `Ch3 Temp P109`, 3.4.2 Trajectory Scoring Model and LSTM Extension

Find this exact paragraph:

> The current trajectory model is a feature-based scoring approach that takes as input per-message DistilBERT risk scores and per-turn trajectory features (for example: peak score so far, spike count, score-change rate, score drop after spike, average score so far, turn number, and conversation length so far). A precomputational step is run over a corpus of benign chats to calculate the benchmark centroid before feature extraction. A weighted combination of these signals produces a trajectory risk score between 0 and 1 at each turn. LSTM-based sequence learning remains a proposed extension after baseline trajectory scoring is fully validated.

Issue:

"Precomputational" is awkward. "Benchmark centroid" is also less clear than "benign-chat centroid," which matches the Topic Drift section.

Suggested revision:

> The current trajectory model is a feature-based scoring approach that takes as input per-message DistilBERT risk scores and per-turn trajectory features (for example: peak score so far, spike count, score-change rate, score drop after spike, average score so far, turn number, and conversation length so far). Before trajectory feature extraction, a precomputation step is run over a corpus of benign chats to calculate the benign-chat centroid used for topic-drift measurement. A weighted combination of these signals produces a trajectory risk score between 0 and 1 at each turn. LSTM-based sequence learning remains a proposed extension after baseline trajectory scoring is fully validated.

### C09 - Replace "moderation system" with "moderation module" in trajectory output paragraph

Target:

- `Ch3 Temp P111`, 3.4.2 Trajectory Scoring Model and LSTM Extension

Find this exact paragraph:

> The trajectory risk score is the primary output consumed by the moderation system. A configurable threshold determines when a conversation is flagged for human review. The threshold is tuned during validation to optimize recall — the study's primary metric — while maintaining a false positive rate that is operationally sustainable for the moderation team.

Issue:

This refers to the proposed artifact, so "module" is better than "system."

Suggested revision:

> The trajectory risk score is the primary output consumed by the moderation module. A configurable threshold determines when a conversation is flagged for human review. The threshold is tuned during validation to optimize recall — the study's primary metric — while maintaining a false positive rate that is operationally sustainable for the moderation team.

### C10 - Fix rule-based weights and remove stray "Onboarding"

Target:

- `Ch3 Temp P117`, 3.5.1 Evaluation Metrics

Find this exact paragraph:

> The dataset is divided into training, validation, and test sets at the conversation level to prevent data leakage across splits. The validation set is used to tune model parameters, rule-based scoring weights, and flagging thresholds, while the test set is reserved for final evaluation. Onboarding is also included.

Issues:

- "Rule-based scoring weights" is inaccurate; the weights belong to the trajectory scoring model.
- "Onboarding is also included" appears unrelated and should be removed.

Suggested revision:

> The dataset is divided into training, validation, and test sets at the conversation level to prevent data leakage across splits. The validation set is used to tune model parameters, trajectory scoring weights, and flagging thresholds, while the test set is reserved for final evaluation.

### C11 - Avoid "system" in ethics paragraph

Target:

- `Ch3 Temp P127`, 3.6 Ethical Considerations

Find this exact paragraph:

> The system is designed as a support tool for human moderators rather than an autonomous decision-making system. Flagged conversations are intended for human review before any moderation action is taken, preserving human oversight and reducing the risk of algorithmic harm to falsely flagged users.

Issue:

This uses "system" twice. Since the adviser prefers avoiding it, use "module" for the proposed artifact and "mechanism" for autonomous decision-making.

Suggested revision:

> The moderation module is designed as a support tool for human moderators rather than an autonomous decision-making mechanism. Flagged conversations are intended for human review before any moderation action is taken, preserving human oversight and reducing the risk of algorithmic harm to falsely flagged users.

## Quick Revision Checklist

- [ ] Main Paper P048: change "AI-driven moderation system" to "module" or "approach."
- [ ] Main Paper P052: delete filler sentence.
- [ ] Main Paper P058: change "proposed AI-driven moderation system" to "module."
- [ ] Main Paper P068: change "prototype system" and "system" to "prototype moderation module" and "module."
- [ ] Main Paper P071: fix broken grammar and state offline/live-deployment distinction once.
- [ ] Main Paper P074/P076: reorder 1.5.1 and 1.5.2 sections.
- [ ] Main Paper P075/P077: replace proposed-work "system" wording.
- [ ] Main Paper P113: fix SchurgerFoy.
- [ ] Main Paper P125: narrow "across multiple conversations or platforms" to "across multiple turns within a conversation."
- [ ] Main Paper P132: frame multimodal indicators as future work.
- [ ] Main Paper P041/P056/P057/P058/P112/P121-P135: clean corrupted hyphen/control characters.
- [ ] Ch3 Temp P003: change "across conversations" to "across conversation turns."
- [ ] Ch3 Temp P005/P017/P019/Table 3.1: make dataset scope consistent.
- [ ] Ch3 Temp P049: replace "may additionally be represented" if trajectory snapshots are core.
- [ ] Ch3 Temp P071-P073: replace "existing predatory classifier."
- [ ] Ch3 Temp P109: fix "precomputational" and "benchmark centroid."
- [ ] Ch3 Temp P111/P127: replace proposed-work "system" with "module."
- [ ] Ch3 Temp P117: fix "rule-based scoring weights" and remove "Onboarding is also included."
