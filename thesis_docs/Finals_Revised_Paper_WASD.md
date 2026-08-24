__*AI-Based Identification of PAN12 Conversations Associated with Listed Predator Authors Using Contextual and Behavioral Trajectory Analysis*__

 

A Thesis Proposal Submitted to the Faculty 

of the School of Computing and Information Technologies

Asia Pacific College, Makati City

 

 

In Partial Fulfillment of the Requirements of the subject

THESIS1

 

 

By

Justin Bryden G. Arroco 

Don Victor L. Idos

John Michael O. Maala

Andrei Luis M. Torres

 

 

 

 

 

 

 

 

 

 

# I. Introduction

## 1.1 Background of the Study

The rapid growth of online multiplayer games and interactive digital platforms has made real-time chat central to online social activity. These systems support collaboration and community building, but they also create channels through which grooming-related interactions and other forms of harmful conduct can develop [1], [2], [3]. Keyword filters and user reports remain useful first-line controls, yet they are poorly suited to evidence distributed across ordinary-looking turns, altered spellings, coded language, and gradual shifts in conversational behavior [4], [5], [6], [7], [8].

Context-aware modeling addresses this limitation by evaluating a turn in relation to surrounding messages and by tracking how evidence changes across an interaction [6], [9]. This is particularly relevant to grooming-related risk because a single greeting, question, or request may be ambiguous, while its placement within a sustained exchange can be informative. The resulting technical problem is not merely text classification; it is the aggregation of sparse and noisy conversational evidence into a reliable interaction-level decision.

The PAN-2012 Sexual Predator Identification corpus provides a strong benchmark for this problem because it combines large-scale chronological chat records, persistent speaker identifiers, and an official predator-author list [13]. These properties support two safeguards essential to the present study: conversation-level evaluation against a verifiable endpoint and connected-author partitioning that prevents any author from appearing across development and final-test partitions. PAN12 was therefore selected not only for its scale, but because its structure permits a rigorous test of temporal modeling under author-disjoint evaluation.

This study operationalizes a positive case as a dyadic PAN12 conversation containing at least one author on the official predator list. It implements a two-layer architecture. Layer 1 uses DistilBERT with the current turn and up to two preceding turns to estimate a contextualized predator-author proxy for the current speaker. Layer 2 receives the chronological sequence of seven trajectory features constructed from proxy scores, current-turn base-encoder embeddings, and cumulative speaker-turn counts, then produces the final conversation-level score. The proxy is not interpreted as a message-level grooming label; it is an intermediate signal whose value is tested through conversation-level aggregation.

The primary scientific comparison is deliberately controlled: the seven-feature LSTM and a validation-fitted weighted scorer receive the same seven trajectory inputs. This controls input availability and directly compares learned recurrent aggregation with validation-fitted weighted aggregation. On the locked author-disjoint final test, the primary LSTM achieved a PR-AUC of 0.9153, precision of 0.8511, recall of 0.9091, and F0.5 of 0.8621. It exceeded the matched weighted scorer by 0.1103 PR-AUC and 0.1121 F0.5, with both paired 95% bootstrap intervals above zero. These results establish that learned temporal aggregation contributes substantial predictive value for the PAN12 conversation endpoint.

This study also supports the United Nations Sustainable Development Goals (SDGs), particularly SDG 9 (Industry, Innovation and Infrastructure) and SDG 16 (Peace, Justice and Strong Institutions). It supports SDG 9 by advancing a reproducible machine-learning approach for human-reviewed online-safety screening. It supports SDG 16 by contributing methods that can inform the development of safer and more accountable digital communication systems.

## 1.2 Statement of the Problem

Keyword and rule-based moderation can detect explicit lexical violations, but they do not directly model the order, persistence, or interaction pattern of contextual evidence. A contextual classifier can improve local interpretation, yet reducing a conversation to its single maximum score discards the trajectory through which evidence accumulates or changes. The central research problem is therefore whether a recurrent model can use the same engineered trajectory information more effectively than static aggregation methods when identifying PAN12 conversations associated with officially listed predator authors.

The study addresses this problem under severe class imbalance and a strict author-disjoint protocol. It evaluates all methods on identical conversation IDs, selects every learned configuration and threshold using validation data, and reserves the final partition for one locked comparison. This design permits a direct assessment of predictive performance while preventing author overlap and final-test threshold tuning.

This study seeks to answer the following questions:

1. How effectively do the keyword rule, aggregated Layer 1 proxy, weighted trajectory scorer, and LSTM-based models identify PAN12 conversations containing an officially listed predator author under author-disjoint evaluation?
2. Does the seven-feature trajectory LSTM outperform the matched seven-feature weighted scorer on PR-AUC, F0.5, precision, and recall?
3. How much does the trajectory LSTM improve conversation-level performance over the keyword rule and maximum Layer 1 proxy aggregation?
4. What additional predictive value is observed when the seven trajectory features are supplemented with 768-dimensional base DistilBERT embeddings?

## 1.3 Objectives of the Study

__General Objective:__ Develop and evaluate a two-layer contextual trajectory model for identifying PAN12 conversations containing an officially listed predator author under strict author-disjoint testing.

- __Specific Objective:__
	1. Fine-tune a context-conditioned DistilBERT classifier using official predator-author membership as an explicitly defined proxy target.
	2. Construct seven chronological trajectory features and compare recurrent LSTM aggregation with a validation-fitted weighted scorer receiving the same inputs.
	3. Evaluate the primary model, keyword rule, raw Layer 1 aggregation, weighted scorer, and enhanced-input LSTM on identical locked conversation partitions using PR-AUC, ROC-AUC, precision, recall, specificity, F1, F0.5, and confusion counts.
	4. Quantify uncertainty and paired method differences by bootstrap resampling connected-author components.

## 1.4 Scope and Limitations

### 1.4.1 Scope of the Study

The primary experiment uses eligible dyadic conversations from the PAN12 training corpus with non-empty messages, chronological turn order, and valid conversation and author identifiers. The candidate pool contains 18,567 conversations and 218,114 turns. The official predator-author list is the sole source of supervision: Layer 1 uses current-author membership as a weak proxy target, and Layer 2 uses the derived conversation endpoint.

The study compares five methods on identical connected-author partitions: a training-derived keyword rule, maximum Layer 1 proxy aggregation, a validation-fitted weighted trajectory scorer, a primary seven-feature LSTM, and a secondary LSTM that adds 768-dimensional base DistilBERT embeddings. The primary architecture comparison is the seven-feature LSTM against the seven-feature weighted scorer because both receive the same information.

The prototype processes stored or locally entered messages in chronological order through offline sequential replay. It demonstrates how contextual scores and conversation trajectories can be inspected, but it is not evaluated as a live platform integration.

### 1.4.2 Limitations of the Study

The evaluated endpoint is PAN12 conversation-level predator-author presence. The experiment does not provide exhaustive message-level grooming labels and therefore does not measure grooming-message classification, grooming stage, onset, or intent at an individual turn. Author-derived Layer 1 supervision is necessarily coarse: a turn written by a listed author is a positive proxy observation even when that turn is linguistically ordinary.

The final results establish generalization to unseen authors within the locked PAN12 partitions. They do not establish performance on contemporary gaming platforms, external corpora, Filipino or Taglish conversations, or live users. The offline prototype is intended for human-review decision support; latency, throughput, platform integration, and autonomous moderation are outside the evaluated scope.

## 1.5 Significance of the Study

This section explains the importance and potential impact of the research, identifying key beneficiaries and contributions across multiple domains.

### 1.5.1 Academic Contribution

This research contributes a controlled evaluation of temporal aggregation for an imbalanced, author-derived conversation endpoint. Its principal result is not merely that an LSTM produces a strong score, but that the seven-feature LSTM outperforms a validation-fitted weighted scorer supplied with the same seven inputs. This matched comparison provides direct evidence that recurrent sequence modeling adds predictive value beyond static combination of the engineered trajectory features.

The study also contributes a reproducible evaluation design for conversational safety research: connected-author partitions; training-only construction of the benign centroid and keyword lexicon; validation-only selection of checkpoints, model configurations, feature thresholds, scorer weights, and operating thresholds; a single held-out final comparison; and component-grouped uncertainty estimates. These controls address a common but consequential source of overstatement in conversation datasets, where the same participant can otherwise appear across multiple splits.

### 1.5.2 Industry and Practical Applications

For platform and moderation researchers, the prototype demonstrates a practical architecture for combining contextual language modeling with an auditable sequence representation. The seven-feature recurrent head is compact, its input signals can be inspected over time, and its output is intended to prioritize conversations for human review. These properties make the design a credible candidate for later platform-specific validation and integration research.

The present evidence supports offline decision assistance rather than autonomous action. Any operational deployment would require representative platform data, calibration, privacy and fairness review, throughput measurement, and a clearly defined human escalation process.

### 1.5.3 Societal Benefits

Beyond academia and industry, this research has potential societal value. Online harassment and grooming pose serious threats to user well-being, particularly for children, adolescents, and individuals with limited digital literacy. The present study contributes an experimentally evaluated screening architecture that future platform-specific research can adapt for human-reviewed digital-safety workflows. Its PAN12 results do not by themselves demonstrate prevention of real-world harm, but they provide evidence for a more effective way to prioritize conversations under the study's endpoint.

In the Philippine context, the study is relevant to continuing efforts to protect young people who participate in online gaming, social media, and digital communication platforms. The research offers a prototype and an evaluation approach that local platform administrators and digital-safety researchers may build upon. It does not, however, claim Philippine-specific or Filipino/Taglish model validation; that requires representative local data and separate evaluation.

The work provides a foundation that organizations with limited moderation resources may evaluate and adapt, subject to representative data, governance, and human-review safeguards.

### 1.5.4 Implications for Future Research

This research establishes a foundation for future investigations into AI-powered moderation systems and behavioral analysis in digital communication. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media. 

Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy. Future research can also explore the integration of multimodal analysis (text, images, video) for comprehensive content moderation. 

The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field.

### 1.5.5 Sustainable Development Goal (SDG) Contribution

This study supports Sustainable Development Goal 9 (Industry, Innovation and Infrastructure) through the development of an AI-driven moderation prototype that applies machine learning and natural language processing to contextual conversation analysis. It also supports Sustainable Development Goal 16 (Peace, Justice and Strong Institutions) by contributing a reproducible, human-review-oriented method for prioritizing PAN12 conversations associated with listed predator authors. The study establishes this contribution on its defined benchmark endpoint while reserving real-platform safety effects for later external validation.

## 1.6 Definition of Terms

Artificial Intelligence (AI) - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

Behavioral Pattern Analysis - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

Chat Moderation System - An automated or semi-automated system designed to monitor, filter, and regulate user communications in real-time chat environments to prevent harmful interactions.

Contextual Analysis - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

Grooming - A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower their defenses and facilitate exploitation or abuse.

Machine Learning - A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task.

Natural Language Processing (NLP) - A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner.

Obfuscation Techniques - Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword-based filters.

Online Grooming Discourse Model (OGDM) - The theoretical lens used to motivate analysis of grooming as a non-linear, cross-turn discourse process. In this study it informs the sequence-modeling rationale; it is not treated as a source of verified message-stage labels.

Predatory Behavior - Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals.

Offline Sequential Replay - The controlled processing of stored or locally entered messages in chronological order to simulate turn-by-turn analysis. It does not constitute a live platform deployment or establish production latency, scalability, or integration performance.

User Reporting Mechanism - A system feature that allows chat platform users to report suspicious, harmful, or policy-violating behavior to moderators or automated systems for review and action.

# II. RELATED WORK

This chapter presents a review and synthesis of existing literature and empirical studies related to AI-based chat moderation and the detection of harmful interactions in online communication environments. The discussion focuses on recent developments in natural language processing (NLP), machine learning-based moderation frameworks, and behavioral analysis techniques used to identify grooming-related interactions and other context-dependent harmful communication patterns.

The purpose of this chapter is to establish the scholarly foundation of the study, examine current moderation approaches and methodologies, and identify research gaps that justify the development of a behavioral and context-aware prototype for conversation-level safety screening.

## 2.1 Review of Related Literature

Recent research in chat moderation has shifted from traditional rule-based filtering toward AI-driven contextual analysis models. Earlier moderation approaches relied primarily on keyword blacklists to detect violations such as profanity or explicit harmful language. However, these systems are limited in their ability to interpret conversational intent, allowing malicious users to bypass filters through techniques such as altered spellings, coded language, or multi-message grooming strategies.

Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. Schurger-Foy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history. Similarly, Yang et al. [6] introduced the ToxBuster architecture, which incorporates message history and speaker metadata into text classification models. Their results showed significant improvements in detection accuracy, achieving up to 95% precision in identifying harmful interactions through sequence-based moderation rather than single message evaluation.

These findings suggest that integrating conversational context and historical behavioral patterns improves moderation effectiveness compared to static filtering methods. Transformer-based NLP architectures such as BERT, RoBERTa, and DistilBERT have consequently emerged as standard tools for understanding linguistic patterns in chat environments. 

Furthermore, longitudinal behavioral analysis has been shown to be a strong predictive indicator of future harmful activity. Studies indicate that tracking interaction patterns over time can achieve up to 74% balanced accuracy in forecasting future toxic behavior, reinforcing the importance of behavioral modeling in proactive moderation systems. 

Despite these advancements, current moderation systems remain constrained by their reliance on legacy datasets such as PAN12, which may not adequately represent modern online communication styles, slang, or evolving evasion techniques used by malicious actors. 

## 2.2 Related Studies

Several empirical studies have explored the application of artificial intelligence in detecting grooming-related interactions within online environments.

The empirical study of automated grooming detection is anchored in the PAN-2012 Sexual Predator Identification task introduced by Inches and Crestani [13]. PAN12 defined separate author-identification and distinctive-line tasks. The present study adopts the official predator-author list as its verified supervision and derives a conversation endpoint from author presence; it does not reinterpret author membership as an exhaustive message-level grooming annotation.

PAN12 is especially suitable for the present research question because its scale, chronological message order, and persistent speaker identifiers support trajectory construction and connected-author evaluation. These properties make it possible to test generalization to conversations involving unseen authors while preserving the sequential structure required by the LSTM. Author-derived labels are therefore used as weak supervision for an intermediate contextual proxy, while the final empirical claim remains at the conversation level.

Building on this benchmark, Villatoro-Tello et al. [14] proposed a two-step approach that first separates predatory from non-predatory participants and then identifies the most suspicious users, combining content-based features with behavioral features such as the proportion and pattern of a user’s interventions within a conversation. Their system achieved the highest performance among the sixteen teams in the PAN-2012 competition, demonstrating that participation and interaction-pattern features—not message content alone—carry discriminative signal for predator detection. This finding directly motivates the use of behavioral trajectory features alongside context-conditioned turn-level proxy signals in the present study.

Street et al. [2] developed a transformer-based classification approach using BERT and RoBERTa models to identify online grooming interactions by analyzing conversational roles between adults and minors. Their contextual determination framework improved cross-dataset robustness in identifying suspicious communication patterns across multiplayer gaming chats. 

Faraz et al. [3] proposed *Protectbot*, an AI-based chatbot that actively simulates user interaction to expose predatory intent. Utilizing the DialoGPT language model combined with intent classifiers such as fastText and Support Vector Machines, the system achieved an __F__-__score of 0.99__ in detecting grooming behavior within simulated chat environments. 

Comparative evaluations conducted by Tereshchenko and Hämäläinen [5] revealed that lightweight transformer models such as DistilBERT provide an optimal balance between computational efficiency and moderation accuracy in high-volume chat systems. Their findings showed that while large generative language models offer improved linguistic nuance, they introduce latency issues that hinder real-time deployment in live environments. 

In addition, qualitative analyses of real-time moderation frameworks within child-centric platforms such as Roblox have highlighted sociotechnical challenges including algorithmic bias, cultural sensitivity issues, and limited transparency in automated decision-making processes. 

While these studies demonstrate the effectiveness of AI-based moderation tools, many approaches still analyze localized chat contexts or isolated messages. As a result, they may fail to model behavioral trajectories that evolve across multiple turns within a conversation.

## 2.3 Theoretical Background

The theoretical foundation of this study is based on advancements in machine learning-driven natural language processing and behavioral pattern recognition.

Beyond the computational literature, the detection task is grounded in discourse-analytic models of how grooming unfolds in conversation. O’Connell [12] provided one of the earliest typologies, describing online grooming as a progression through stages—friendship forming, relationship forming, risk assessment, exclusivity, and a sexual stage—in which an offender gradually escalates a relationship with a minor. While influential, this stage model assumes a largely linear progression that later empirical work has shown offenders do not consistently follow.

The primary theoretical framework adopted in this study is the model of online grooming discourse developed by Lorenzo-Dus, Izura, and Pérez-Tattam [11]. Drawing on a large corpus of offender chat logs, their analysis characterizes grooming not as a fixed linear sequence but as an entrapment network realized through four interrelated communicative processes: deceptive trust development, sexual gratification, compliance testing, and isolation. Deceptive trust development—the discursive building of rapport and a sense of an exclusive relationship—was found to be the most frequent process and to correlate with the others. Compliance testing refers to repeatedly probing a target’s boundaries and then retreating to gauge and condition responses, while isolation works to separate the target from sources of support and to concentrate the interaction within the dyad. Because these processes can unfold across multiple turns rather than at fixed conversational positions, the framework provides a strong rationale for studying cross-turn evidence and interaction trajectories.

OGDM supplies the theoretical reason to examine evidence across a conversation rather than treating turns as independent observations. The implemented trajectory features translate that general sequence-oriented rationale into inspectable computational signals: proxy-score level and change, threshold-crossing patterns, semantic distance from a training-derived benign centroid, and speaker-turn imbalance. These features are not direct measurements of OGDM stages or communicative processes, because PAN12 does not provide the message-level discourse annotations needed to validate such a mapping. Their empirical role is therefore tested through the matched comparison between recurrent and static aggregation, while OGDM remains the interpretive framework for why cross-turn dynamics may matter.

Recent moderation frameworks adopt sequence modeling techniques, which evaluate conversations as evolving interaction chains rather than isolated textual inputs [6]. This approach allows systems to detect behavioral trajectories characteristic of grooming related activities, such as gradual trust-building, self-disclosure, or attempts to isolate users within private communication channels. 

However, current methodologies often evaluate text-based data in isolation and may fail to capture longer conversational progression across message turns. Multimodal behavioral indicators, such as spatial interaction patterns or economic incentives within digital environments, remain outside the scope of the present study and are recommended for future work.

These limitations reveal a methodological gap in existing moderation systems, particularly in detecting slow-developing threats such as grooming behavior, which typically manifest through subtle interaction patterns across multiple messages rather than explicit rule violations. 

To address these challenges, contemporary research recommends hybrid moderation frameworks combining automated AI-based triage with human-in-the-loop (HITL) review mechanisms. Such layered architectures enable high-speed real-time flagging of suspicious interactions while preserving human oversight for nuanced adjudication and minimizing algorithmic bias. 

This study adopts the sequence-oriented implication of these theoretical principles by modeling how contextual proxy evidence and interaction structure change across turns. The resulting trajectory variables are computational features for the PAN12 endpoint, not validated OGDM stage labels. This distinction preserves a clear boundary between the discourse theory that motivates temporal analysis and the supervised evidence available for evaluating the system.

# III. METHODOLOGY

## 3.1 Research Design

This study uses a developmental and experimental research design [15] to build and evaluate an offline conversation-analysis prototype. The approved primary endpoint is **conversation-level identification of PAN12 conversations that contain at least one author listed by PAN12 as a sexual predator**. The endpoint is author-derived and conversation-level; it is not a claim that PAN12 provides complete message-level grooming or grooming-onset annotations.

The proposed system has two learned layers. Layer 1 fine-tunes DistilBERT using the official predator-author list as weak supervision. For each current turn, it processes that turn together with the two preceding turns and produces a **predator-author proxy score**. Layer 2 uses the chronological sequence of features constructed from proxy-score dynamics, base-encoder topic distance, and cumulative turn structure to estimate whether the conversation contains a listed predator. The LSTM is the sequence model, while a weighted scorer, an aggregated raw Layer 1 score, and a keyword rule serve as comparison methods.

All model development and evaluation are conducted through chronological offline replay of dataset conversations. The study does not evaluate deployment latency, platform integration, live users, or autonomous moderation. The output is intended as decision support for human review. A below-threshold result is not a determination that a conversation or participant is safe.

The experiment tests whether an LSTM using the same seven trajectory inputs as the weighted scorer improves the approved conversation-level endpoint. A larger LSTM that additionally receives a 768-dimensional base DistilBERT embedding is evaluated separately as an enhanced-input model so that an input-capacity difference is not misreported as an architectural advantage. No superiority result is assumed in advance.

## 3.2 Relevant Technology

### 3.2.1 Python Programming Language

Python is used as the primary programming language for the development and evaluation of the proposed moderation module. It was selected due to its extensive support for machine learning, natural language processing, and data analysis through established libraries and frameworks.

### 3.2.2 Hugging Face Transformers and PyTorch

The study utilizes the Hugging Face Transformers library together with the PyTorch deep learning framework for model training and inference. These technologies provide pre-trained transformer architectures and efficient tools for fine-tuning NLP models for text classification tasks.	

### 3.2.3 DistilBERT

DistilBERT serves as the text encoder and Layer 1 sequence classifier. It is a lightweight transformer-based model derived from BERT that retains contextual language representations while reducing computational requirements. In the revised experiment, the fine-tuned classifier estimates the weakly supervised predator-author target for the current turn under preceding conversational context. Its output is not interpreted as a probability that the current message itself is grooming. A separate, unchanged `distilbert-base-uncased` encoder supplies the 768-dimensional embedding used by topic-distance computation and the enhanced-input LSTM.

### 3.2.4 Development Environment

The prototype system was developed and tested using Jupyter Notebook and Visual Studio Code within a Python-based experimental environment. Layer 1 training used an NVIDIA RTX 3060 Ti with CUDA, BF16 mixed precision, and TF32. The returned run recorded its software environment, command-line configuration, random seed, and locked split assignment. Table 3.1 records the local environment used to rerun and demonstrate the completed pipeline.

| Component | Version |
|---|---:|
| Python | 3.12.5 |
| PyTorch | 2.11.0+cu128 |
| Transformers | 4.57.3 |
| scikit-learn | 1.6.1 |
| NumPy | 2.2.3 |
| pandas | 2.2.3 |
| Flask | 3.1.2 |

*Table 3.1. Current prototype rerun and demonstration environment.*

## 3.3 Data Collection and Processing

### 3.3.1 Corpus and Label Provenance

The primary experiment uses the PAN12 Sexual Predator Identification training corpus and its official predator-author list [13]. After strict removal of rows that fail the required conversation, chronology, author, or label checks and restriction to dyadic conversations, the locked candidate pool contains 218,114 turns across 18,567 conversations, including 454 positive conversations and 34,686 distinct author identifiers. Invalid records are excluded rather than assigning a missing author label to the negative class.

For conversation \(c\), let \(A_c\) be its set of authors and \(P\) the official PAN12 predator-author set. The primary ground-truth label is

\[
Y_c = \mathbf{1}[A_c \cap P \neq \varnothing].
\]

Thus, a positive case is a conversation containing at least one officially listed predator author. For Layer 1 only, the weak target for turn \(t\), authored by \(a_t\), is

\[
Z_t = \mathbf{1}[a_t \in P].
\]

Because \(Z_t\) repeats an author-level identity label on that author's turns, it does not establish that a particular turn contains grooming behavior. The Layer 1 output is therefore called a predator-author proxy score rather than a grooming-message probability.

PAN12 was selected because it is a large established benchmark available to the project with the combination required by this experiment: chronological conversation records, persistent speaker identifiers, and an official author-level endpoint. This supports sequence construction at scale and permits every connected group of authors to be assigned wholly to one partition.

The author-derived target is intentionally interpreted as weak supervision over contextualized turns. It allows Layer 1 to estimate the author-derived target from contextualized text without claiming that every positive-author turn expresses grooming. No per-message field is used as exhaustive grooming ground truth, and all primary training, selection, and evaluation claims are made against the official author-derived conversation endpoint.

### 3.3.2 Inclusion and Preprocessing

The primary corpus is restricted to conversations with exactly two distinct authors to match the dyadic interaction scope and the implemented turn-taking feature. Empty messages and rows without a valid conversation identifier, chronological line identifier, author identifier, or binary official predator-author status are excluded. Original conversation and line identifiers are retained. Each usable row receives a stable key based on dataset source, conversation identifier, and line identifier so that duplicate text cannot overwrite another turn's cached score.

Conversations are ordered by their original line identifier. Layer 1 receives a prefix-only context consisting of the current turn and up to two immediately preceding turns from the same conversation. Neutral turn separators are inserted, but raw author identifiers, predator-list membership, the project `is_suspicious` field, source-revealing role names, future turns, and conversation labels are never included in model text. Training and inference use the identical context-construction function. The DistilBERT tokenizer truncates each context to 128 tokens and applies dynamic padding within each batch.

Text normalization is deliberately conservative: character encoding and whitespace are standardized, while altered spellings and obfuscations are retained so that evaluation does not benefit from a hand-written correction rule unavailable to the learned model. The primary experiment does not add synthetic conversations or separately collected chat logs.

### 3.3.3 Connected-Author Data Partitioning

The dataset is partitioned before negative sampling, context caching, centroid construction, model fitting, or threshold selection. Conversations are represented as vertices in a graph; any conversations sharing an author are connected. Every resulting connected component is assigned wholly to one partition, creating zero conversation overlap and zero author overlap across training, validation, and final test data.

The locked manifest assigns 13,031 conversations to training, 1,827 to validation, and 1,862 to the final test; an additional 1,847 conversations are excluded from the primary experiment. The corresponding positive-conversation counts are 319, 49, 44, and 42. Partition assignment uses connected-component membership, partition size, and class balance rather than model scores or text-derived features. The manifest records zero conversation, author, and connected-component overlap across all groups together with the random seed, source-data hash, and manifest hash.

The training partition is used for parameter estimation. After partitioning, negative Layer 1 training rows were downsampled to three negatives per positive row; validation and final-test distributions remained untouched. The validation partition was used for checkpoint selection, hyperparameter selection, comparator fitting, and threshold selection. The locked final test was evaluated once after code, checkpoints, thresholds, feature definitions, and reporting rules were frozen.

### 3.3.4 Feature Engineering

Let \(R_i\) denote the Layer 1 predator-author proxy score at turn \(i\), \(E_t\) the 768-dimensional embedding from the unchanged base `distilbert-base-uncased` encoder for the current turn, \(C_b\) a benign-chat centroid computed only from negative conversations in the training partition, \(T_a(t)\) the cumulative number of turns contributed by participant \(a\) through turn \(t\), \(\tau\) the spike threshold, and \(\delta\) the drop threshold. The seven trajectory features at turn \(t\) are:

1. **Peak proxy score:** \(\max_{1 \leq i \leq t} R_i\), with range \([0,1]\).
2. **Current proxy score:** \(R_t\), with range \([0,1]\).
3. **Spike count:** \(\sum_{i=1}^{t}\mathbf{1}[R_i>\tau]\), with range \([0,t]\).
4. **Spike-then-drop:** 1 from the first turn whose score falls by more than \(\delta\) below a previous peak that exceeded \(\tau\), and 1 thereafter; otherwise 0.
5. **Rate of change:** \(R_t-R_{t-1}\), or 0 for the first turn, with range \([-1,1]\).
6. **Topic distance:** \(1-\cos(E_t,C_b)\), with theoretical range \([0,2]\).
7. **Turn-taking imbalance:** \(\lvert T_A(t)-T_B(t)\rvert/(T_A(t)+T_B(t))\), with range \([0,1]\). The implementation uses cumulative turn counts through the current turn, not word counts or full-conversation totals.

The centroid source conversation IDs and embedding-model digest are recorded, and validation or test text is never used to construct it. The spike and drop thresholds are selected on validation data and then frozen. Each turn-level cache is keyed by the stable dataset/conversation/line identifier and records the context-construction version, Layer 1 checkpoint digest, base-encoder digest, and split assignment.

| Input | Definition | Models receiving it |
|---|---|---|
| Layer 1 proxy score | Context-conditioned estimate of the author-derived target \(Z_t\) | Raw Layer 1 baseline and trajectory-feature construction |
| Seven trajectory features | Peak, current, spike count, spike-then-drop, rate of change, topic distance, and turn imbalance | Weighted scorer and primary matched-input LSTM |
| Base DistilBERT embedding | 768-dimensional contextual text representation, separate from the Layer 1 proxy | Secondary enhanced-input LSTM only |

*Table 3.2. Inputs used by the comparison methods.*

## 3.4 Model Development

### 3.4.1 Author-Derived Layer 1 Classifier

Layer 1 uses `distilbert-base-uncased` with a two-class sequence-classification head. Its input is the current turn plus up to two preceding turns defined in Section 3.3.2, and its target is the current author's official predator-list membership \(Z_t\). The training loss is two-class cross-entropy. Negative-row downsampling is confined to the training partition; validation and final test rows retain their natural class distribution.

Optimization uses fused AdamW on an NVIDIA RTX 3060 Ti, BF16 mixed precision, TF32, gradient clipping at 1.0, and random seed 42. The completed run uses five epochs, learning rate \(2\times10^{-5}\), weight decay 0.01, warm-up ratio 0.10, three sampled training negatives per positive row, physical training batch size 8, validation batch size 16, gradient accumulation 1, and early-stopping patience of two epoch evaluations. The checkpoint is selected using validation PR-AUC, and its operating threshold is selected separately on validation data using F0.5. The selected checkpoint, tokenizer, configuration, metrics history, and row manifest are saved together.

The positive-class softmax output is denoted \(R_t\). It estimates the weak author-derived classification target under the available text context. It must not be described as a validated probability of grooming content, grooming phase, or grooming onset.

### 3.4.2 LSTM-Based Trajectory Scoring Model

The primary Layer 2 model is an LSTM that receives the chronological sequence of the same seven features supplied to the weighted scorer. Padding masks ensure that padded turns do not affect hidden-state computation. A secondary enhanced-input LSTM concatenates the 768-dimensional base DistilBERT embedding with the seven trajectory features, producing a 775-dimensional turn vector; its result is reported separately and is not used to claim a matched-input architectural advantage.

The selected primary model is a unidirectional, single-layer LSTM with hidden dimension 128 and dropout 0.20, trained with batch size 32, Adam learning rate 0.001, weight decay 0.0001, gradient clipping at 1.0, a maximum of 20 epochs, and early-stopping patience of four validation evaluations. The selected enhanced model uses the same hidden dimension, layer count, dropout, batch size, and stopping rule with learning rate 0.0005. Both searches use seed 42 and select by validation PR-AUC with validation F0.5 as the first tie-break criterion.

Layer 2 is trained only against the valid conversation label \(Y_c\). `BCEWithLogitsLoss` is applied to the output at the final valid turn using a positive-class weight of 39.8495, computed solely from the 12,712 negative and 319 positive training conversations. No turn-level loss, cumulative `is_suspicious` target, or repeated predator-author label is used as grooming-onset supervision. Validation selects the LSTM checkpoint and its conversation flagging threshold. Intermediate prefix scores may be displayed to demonstrate sequence processing, but the first threshold crossing is reported only as an exploratory prefix statistic, not as validated grooming onset or time-to-harm.

### 3.4.3 Comparison Models

Four comparisons are evaluated on the same conversation endpoint and locked partitions:

1. **Aggregated raw Layer 1:** the maximum \(R_t\) in a conversation, using its independently selected validation threshold.
2. **Weighted trajectory scorer:** a validation-fitted combination of the seven trajectory features, with its own validation-selected weights and threshold.
3. **Keyword rule:** a fixed lexicon derived only from the revised training partition; a conversation is positive when any turn matches the rule. Lexicon construction and matching rules are frozen before final testing.
4. **Enhanced-input LSTM:** the 775-input LSTM reported separately from the primary matched seven-feature LSTM.

The principal architecture comparison is the seven-feature LSTM versus the seven-feature weighted scorer. Every learned comparator is tuned independently on validation data. The raw Layer 1 baseline uses its actual positive-class score directly and is not passed through the weighted scorer or another sigmoid.

## 3.5 Evaluation/Validation

### 3.5.1 Validation and Final-Test Protocol

All development decisions are made from the training and validation partitions. Layer 1 checkpoint selection, negative-sampling configuration, LSTM configuration, weighted-scorer weights, keyword lexicon, feature thresholds, and every classification threshold are frozen before the new final holdout is scored. The final evaluation script verifies the data and configuration hashes, evaluates every method on identical conversation IDs, and writes predictions and metrics without modifying the saved configuration.

The reported result is generated only by this frozen evaluation path. Every method is evaluated on the same ordered conversation IDs, and the final report retains the outcome regardless of which model performs best.

### 3.5.2 Metrics and Comparative Analysis

The unit of primary evaluation is the conversation, with \(Y_c\) as ground truth. For each method, the report includes the numbers of true positives, false positives, true negatives, and false negatives, together with precision, recall, specificity, F1, F0.5, PR-AUC, and ROC-AUC. Precision, recall, F1, and F0.5 are computed as

\[
\text{Precision}=\frac{TP}{TP+FP}, \qquad
\text{Recall}=\frac{TP}{TP+FN},
\]

\[
F_1=\frac{2PR}{P+R}, \qquad
F_{0.5}=\frac{1.25PR}{0.25P+R}.
\]

PR-AUC is emphasized alongside thresholded metrics because positive conversations are rare. Validation PR-AUC selects checkpoints, while validation F0.5 selects operating thresholds; no threshold is retuned on the final test. Ninety-five-percent confidence intervals and paired method-difference intervals are estimated by bootstrap resampling connected-author components so that conversations linked by an author remain grouped.

Prefix-level scores and first-threshold-crossing turns are summarized only as exploratory sequence behavior. PAN12 does not supply exhaustive training annotations for the first grooming turn, so these summaries are not evaluated or described as message-level detection accuracy, grooming-stage accuracy, or true time to detection.

## 3.6 Ethical Considerations

All datasets used in this study are handled in accordance with applicable data-protection and research-ethics principles. PAN12 is a research benchmark used under its applicable access and usage conditions. In the local demonstration interface, common direct identifiers—including email addresses, phone numbers, URLs, IPv4 addresses, and common account handles—are masked on the server before model scoring; the masked history then replaces the browser's active conversation history and displayed text. Responses are marked as non-cacheable, and resetting the demonstration clears the browser's active conversation state. Raw text remains briefly in the local browser while a request is processed. These safeguards reduce exposure but do not guarantee complete anonymization: automatic pattern matching may miss names, indirect identifiers, unusual formats, or identifying combinations of details. Real sensitive information must therefore not be entered into the prototype, and any research data still requires access control and manual privacy review.

The study does not involve direct interaction with real users. The revised primary experiment is evaluated offline using PAN12-derived records only. The locally retained synthetic candidate data and any separately collected conversation files are excluded from primary training, validation, and testing unless a later study completes appropriate provenance, licensing, privacy, and independent annotation review.

The moderation module is designed as a support tool for human moderators rather than an autonomous decision-making mechanism. A model flag indicates similarity to the approved PAN12 author/conversation endpoint and requires human review before any moderation action. It must not be used to identify a person as an offender, infer intent from an isolated message, or declare an unflagged conversation safe.

# References

[1] “Parents’ Perspectives of Pre-Pubescent Aged Children’s Access to Online Gaming: Risks of Exposure to Grooming,” Purdue University Global Research Repository. [Online]. Available: [https://purdueglobal.dspacedirect.org/items/c7f44da9-a59f-46a5-a2e1-cbb560bfe2d9](https://purdueglobal.dspacedirect.org/items/c7f44da9-a59f-46a5-a2e1-cbb560bfe2d9). [Accessed: Apr. 13, 2026].

[2] “Enhanced Online Grooming Detection Employing Context Determination and Message-Level Analysis,” arXiv preprint arXiv:2409.07958. [Online]. Available: [https://arxiv.org/abs/2409.07958](https://arxiv.org/abs/2409.07958). [Accessed: Apr. 13, 2026].

[3] “Enhancing Child Safety in Online Gaming: The Development and Application of Protectbot, an AI-Powered Chatbot Framework,” Information, vol. 15, no. 4, 2024. [Online]. Available: [https://www.mdpi.com/2078-2489/15/4/233](https://www.mdpi.com/2078-2489/15/4/233). [Accessed: Apr. 13, 2026].

[4] Roblox Corporation, “Roblox Launches Real-Time Chat Rephrasing to Maintain Civility and Gameplay Flow,” 2026. [Online]. Available: [https://ir.roblox.com/news/news-details/2026/Roblox-Launches-Real-Time-Chat-Rephrasing-to-Maintain-Civility-and-Gameplay-Flow/default.aspx](https://ir.roblox.com/news/news-details/2026/Roblox-Launches-Real-Time-Chat-Rephrasing-to-Maintain-Civility-and-Gameplay-Flow/default.aspx). [Accessed: Apr. 13, 2026].

[5] “Efficient Toxicity Detection in Gaming Chats: A Comparative Study of Embeddings, Fine-Tuned Transformers and LLMs,” arXiv preprint arXiv:2510.17924. [Online]. Available: [https://arxiv.org/abs/2510.17924](https://arxiv.org/abs/2510.17924). [Accessed: Apr. 13, 2026].

[6] “Towards Detecting Contextual Real-Time Toxicity for In-Game Chat,” arXiv preprint arXiv:2310.18330. [Online]. Available: [https://arxiv.org/abs/2310.18330](https://arxiv.org/abs/2310.18330). [Accessed: Apr. 13, 2026].

[7] “AI Moderation and Legal Frameworks in Child-Centric Social Media: A Case Study of Roblox,” Laws, vol. 14, no. 3, 2025. [Online]. Available: [https://www.mdpi.com/2075-471X/14/3/29](https://www.mdpi.com/2075-471X/14/3/29). [Accessed: Apr. 13, 2026].

[8] “Online Hate Speech and Platform Moderation,” SAGE Journals. [Online]. Available: [https://journals.sagepub.com/doi/full/10.1177/2053951717736335](https://journals.sagepub.com/doi/full/10.1177/2053951717736335). [Accessed: Apr. 13, 2026].

[9] “Context-Aware Toxicity Detection in Multiplayer Games: Integrating Domain-Adaptive Pretraining and Match Metadata,” alphaXiv. [Online]. Available: [https://www.alphaxiv.org/overview/2504.01534](https://www.alphaxiv.org/overview/2504.01534). [Accessed: Apr. 13, 2026].

[10] “Artificial Intelligence and Pattern Recognition Applications,” Sensors, vol. 16, no. 8, 2016. [Online]. Available: [https://www.mdpi.com/1424-8220/16/8/1264](https://www.mdpi.com/1424-8220/16/8/1264). [Accessed: Apr. 13, 2026].

[11] N. Lorenzo-Dus, C. Izura, and R. Pérez-Tattam, “Understanding grooming discourse in computer-mediated environments,” Discourse, Context & Media, vol. 12, pp. 40–50, 2016. [Online]. Available: [https://www.sciencedirect.com/science/article/abs/pii/S2211695816300095](https://www.sciencedirect.com/science/article/abs/pii/S2211695816300095). [Accessed: May 23, 2026].

[12] R. O’Connell, “A typology of cyber sexploitation and online grooming practices,” Cyberspace Research Unit, University of Central Lancashire, 2003.

[13] G. Inches and F. Crestani, “Overview of the International Sexual Predator Identification Competition at PAN-2012,” in CLEF 2012 Evaluation Labs and Workshop – Working Notes, Rome, Italy, 2012. [Online]. Available: [https://ceur-ws.org/Vol-1178/CLEF2012wn-PAN-InchesEt2012.pdf](https://ceur-ws.org/Vol-1178/CLEF2012wn-PAN-InchesEt2012.pdf). [Accessed: May 23, 2026].

[14] E. Villatoro-Tello, A. Juárez-González, H. J. Escalante, M. Montes-y-Gómez, and L. Villaseñor-Pineda, “A two-step approach for effective detection of misbehaving users in chats,” in CLEF 2012 Evaluation Labs and Workshop – Working Notes, Rome, Italy, 2012. [Online]. Available: [https://ceur-ws.org/Vol-1178/CLEF2012wn-PAN-VillatoroTelloEt2012b.pdf](https://ceur-ws.org/Vol-1178/CLEF2012wn-PAN-VillatoroTelloEt2012b.pdf). [Accessed: May 23, 2026].

[15] J. W. Creswell, Research Design: Qualitative, Quantitative, and Mixed Methods Approaches, 4th ed. Thousand Oaks, CA: SAGE Publications, 2014.
