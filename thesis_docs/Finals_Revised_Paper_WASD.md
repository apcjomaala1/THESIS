# Conversation Trajectory Lab

__*AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis*__

 

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

The rapid growth of online multiplayer games and interactive digital platforms has led to the widespread use of real-time chat systems as a primary mode of communication among users. These systems enable collaboration, social interaction, and community building; however, they also introduce significant risks related to harmful user behavior. Among these, grooming-related interactions have become increasingly prevalent [1], [2], [3]. Existing moderation approaches in many platforms rely heavily on keyword-based filtering and user reporting mechanisms, which are often insufficient in addressing these complex and context-dependent threats [4], [5].

Traditional chat moderation systems primarily focus on detecting explicit keywords or predefined patterns. While effective in identifying straightforward violations such as profanity, these systems are easily bypassed through obfuscation techniques, including altered spellings, special characters, or coded language [6], [7], [8]. More critically, they lack the ability to understand conversational context, intent, and behavioral progression over time—key elements in identifying grooming-related interactions [2], [9]. Additionally, reliance on manual reporting introduces delays in response, allowing harmful interactions to persist before appropriate action is taken [5].

A critical limitation of existing moderation approaches is their inability to detect a sufficient number of harmful interactions, particularly grooming, resulting in a high number of missed cases (false negatives). This highlights the need for approaches that improve detection coverage, particularly by reducing false negatives in identifying harmful interactions.

Recent advancements in artificial intelligence, particularly in machine learning and natural language processing, provide opportunities to enhance moderation systems beyond static keyword detection [10]. By incorporating behavioral pattern recognition and contextual analysis, AI-driven systems can identify subtle and evolving forms of harmful communication [9]. These approaches enable the detection of suspicious interaction patterns across conversations, rather than relying solely on isolated messages, thereby improving both accuracy and timeliness of moderation.

This study proposes the development of an AI-powered moderation approach designed to augment existing chat filtering and reporting mechanisms. The approach leverages machine learning, natural language processing, and behavioral pattern analysis to detect grooming-related interactions within chat environments. By combining content-level analysis with user behavior modeling, the proposed approach aims to address the limitations of current moderation systems and contribute to safer and more responsive digital communication platforms. 

Unlike traditional moderation systems that analyze messages in isolation, the proposed approach integrates conversational context and behavioral pattern tracking across multiple message turns within a conversation to enable earlier and more accurate detection of grooming-related interactions. Grooming is prioritized due to its reliance on contextual and behavioral progression, making it a suitable case for evaluating the effectiveness of the proposed approach.

This study also supports the United Nations Sustainable Development Goals (SDGs), particularly SDG 9 (Industry, Innovation and Infrastructure) and SDG 16 (Peace, Justice and Strong Institutions). It supports SDG 9 through the development of an AI-powered moderation approach that applies machine learning, natural language processing, and behavioral analysis to improve digital safety technologies. It also supports SDG 16 by promoting safer online communication environments through improved detection of grooming-related interactions and stronger protection for vulnerable users in digital platforms.

## 1.2 Statement of the Problem

Existing chat moderation systems are widely used, yet harmful interactions such as grooming-related interactions persist [1][2][3]. Current approaches rely on keyword-based filtering, rule-based systems, and user reporting, which are often ineffective in detecting context-dependent behaviors [4][5]. These systems analyze messages in isolation and fail to capture conversational context and behavioral patterns over time [2][9].

Reliance on user reporting also results in delayed and reactive moderation, increasing exposure to harmful interactions [5]. This highlights the need for more proactive and context-aware solutions. 

This study explores the use of artificial intelligence, particularly machine learning and natural language processing, to enhance chat moderation through contextual analysis and behavioral pattern recognition [9][10].

This study seeks to answer the following questions:

1. How effective are existing chat moderation systems in detecting grooming-related interactions? 
2. What are the limitations of keyword-based and rule-based moderation approaches in handling context-dependent communication? 
3. How can machine learning and natural language processing be utilized to analyze behavioral patterns and conversational context in chat systems? 
4. To what extent can an AI-driven moderation module improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

## 1.3 Objectives of the Study

__General Objective:__ Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

- __Specific Objective:__
	1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
	2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
	3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.

## 1.4 Scope and Limitations

### 1.4.1 Scope of the Study

The study includes a comparative analysis between the proposed prototype and a keyword-based moderation baseline using the same dataset. This comparison evaluates whether the proposed approach improves detection performance, particularly in terms of recall and reduction of false negatives. 

The proposed prototype is platform-independent and intended for possible future adaptation into chat-based moderation workflows. Rather than replacing existing moderation mechanisms, it is designed to augment them by introducing contextual analysis and behavioral pattern tracking. 

The prototype uses natural language processing and machine learning techniques to analyze chat messages and identify behavioral indicators associated with grooming-related interactions. It analyzes ordered conversation records and simulates sequential chat analysis to determine whether suspicious interaction patterns can be detected earlier within a conversation. 

For evaluation, the prototype is tested using PAN12-derived data, real conversation datasets, and synthetically generated annotated chat data. To ensure the system's analysis is highly relevant to contemporary users, the training and evaluation datasets will actively incorporate current internet language, modern gaming lingo, and up-to-date obfuscation methods used to bypass standard filters. This allows the study to assess its performance in handling current, context-dependent, and behavior-based grooming detection scenarios. 

__1.4.2 Limitations of the Study__

This study is limited to the development of a prototype moderation module and does not involve full deployment in a live chat environment. The scope is further limited to grooming-related interactions. As such, the module will not be tested with real users, and its performance is evaluated only through controlled datasets and simulations.

The study focuses specifically on detecting grooming-related interactions in English-language chat data. Although the study is motivated in part by online-safety concerns in the Philippines, the present evaluation does not establish performance for Filipino, Taglish, or other Philippine-language conversations.

The study builds upon pre-trained machine learning models and libraries, which are further adapted and fine-tuned for the specific task of detecting grooming-related interactions. As a result, system performance is influenced by the capabilities and limitations of these underlying models.

Additionally, while the prototype simulates sequential analysis of chat messages, the evaluation is conducted within a controlled offline environment rather than a live deployment. Actual performance in real-world deployment may vary depending on platform integration, scalability, latency, and data variability. The study also does not account for all possible variations in language, cultural context, or evolving evasion techniques used by malicious users.

## 1.5 Significance of the Study

This section explains the importance and potential impact of the research, identifying key beneficiaries and contributions across multiple domains.

### 1.5.1 Academic Contribution

This research contributes to the academic field of computer science, artificial intelligence, and cybersecurity by advancing the understanding of AI-driven content moderation. The proposed approach bridges a gap in existing literature by demonstrating how machine learning and natural language processing can be combined with behavioral pattern analysis to detect nuanced forms of harmful communication. 

This work provides a framework for contextual analysis in chat moderation that goes beyond traditional keyword-based approaches. The findings will be valuable for researchers exploring AI applications in safety and security, offering insights into feature extraction techniques, model architecture, and evaluation methodologies for detecting complex communication patterns. 

Additionally, this study contributes to theoretical knowledge in understanding grooming-related interactions in digital environments.

### 1.5.2 Industry and Practical Applications

For the technology industry and online platform providers, this research has significant practical implications. Chat-based platforms, gaming communities, social networks, and collaborative tools can leverage the proposed moderation module to enhance user safety and platform integrity. 

By supporting the detection of harmful interactions, platforms may reduce the burden on manual moderation teams, enabling them to focus on complex cases requiring human judgment. The prototype currently demonstrates sequential analysis through controlled offline replay; possible integration into live moderation workflows remains future work. This application is particularly relevant to platforms serving vulnerable user populations, including minors.

Furthermore, the proposed module can be adapted into existing moderation workflows without replacing current filtering mechanisms, offering a scalable and non-disruptive enhancement to platform safety. The adoption of such advanced moderation techniques positions platforms as responsible actors in digital safety, potentially building user trust and reducing legal liabilities.

### 1.5.3 Societal Benefits

Beyond academia and industry, this research has direct societal benefits. Online harassment and grooming pose serious threats to user well-being, particularly affecting vulnerable populations such as children, adolescents, and individuals with limited digital literacy. By improving detection mechanisms, this study contributes to creating safer online environments where users can interact with reduced fear of exploitation or harm. The development of effective AI-driven moderation tools can help prevent real-world harm that originates from online interactions, including trauma and abuse. 

In the Philippine context, the study is relevant to continuing efforts to protect young people who participate in online gaming, social media, and digital communication platforms. The research offers a prototype and an evaluation approach that local platform administrators and digital-safety researchers may build upon. It does not, however, claim Philippine-specific or Filipino/Taglish model validation; that requires representative local data and separate evaluation.

Furthermore, the accessibility and scalability of the proposed solution mean that smaller platforms and communities with limited moderation resources can also implement advanced safety measures, democratizing access to robust content moderation technology.

### 1.5.4 Implications for Future Research

This research establishes a foundation for future investigations into AI-powered moderation systems and behavioral analysis in digital communication. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media. 

Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy. Future research can also explore the integration of multimodal analysis (text, images, video) for comprehensive content moderation. 

The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field.

### 1.5.5 Sustainable Development Goal (SDG) Contribution

This study supports Sustainable Development Goal 9 (Industry, Innovation and Infrastructure) through the development of an AI-driven moderation prototype that applies machine learning and natural language processing techniques to enhance digital communication safety systems. The study also supports Sustainable Development Goal 16 (Peace, Justice and Strong Institutions) by contributing to safer online environments through improved detection of grooming-related interactions and harmful communication patterns. By augmenting existing moderation systems with contextual and behavioral analysis, the proposed approach aims to support more secure and responsible digital communication platforms.

## 1.6 Definition of Terms

Artificial Intelligence (AI) - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

Behavioral Pattern Analysis - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

Chat Moderation System - An automated or semi-automated system designed to monitor, filter, and regulate user communications in real-time chat environments to prevent harmful interactions.

Contextual Analysis - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

Grooming - A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower their defenses and facilitate exploitation or abuse.

Machine Learning - A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task.

Natural Language Processing (NLP) - A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner.

Obfuscation Techniques - Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword-based filters.

Online Grooming Discourse Model (OGDM) - The core theoretical framework used in this study that explains online grooming as a non-linear process of communicative actions, such as trust-building and isolation.

Predatory Behavior - Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals.

Offline Sequential Replay - The controlled processing of stored or locally entered messages in chronological order to simulate turn-by-turn analysis. It does not constitute a live platform deployment or establish production latency, scalability, or integration performance.

User Reporting Mechanism - A system feature that allows chat platform users to report suspicious, harmful, or policy-violating behavior to moderators or automated systems for review and action.

# II. RELATED WORK

This chapter presents a review and synthesis of existing literature and empirical studies related to AI-based chat moderation and the detection of harmful interactions in online communication environments. The discussion focuses on recent developments in natural language processing (NLP), machine learning-based moderation frameworks, and behavioral analysis techniques used to identify grooming-related interactions and other context-dependent harmful communication patterns.

The purpose of this chapter is to establish the scholarly foundation of the study, examine current moderation approaches and methodologies, and identify research gaps that justify the development of a behavioral and context-aware moderation prototype for grooming detection in chat systems.

## 2.1 Review of Related Literature

Recent research in chat moderation has shifted from traditional rule-based filtering toward AI-driven contextual analysis models. Earlier moderation approaches relied primarily on keyword blacklists to detect violations such as profanity or explicit harmful language. However, these systems are limited in their ability to interpret conversational intent, allowing malicious users to bypass filters through techniques such as altered spellings, coded language, or multi-message grooming strategies.

Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. Schurger-Foy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history. Similarly, Yang et al. [6] introduced the ToxBuster architecture, which incorporates message history and speaker metadata into text classification models. Their results showed significant improvements in detection accuracy, achieving up to 95% precision in identifying harmful interactions through sequence-based moderation rather than single message evaluation.

These findings suggest that integrating conversational context and historical behavioral patterns improves moderation effectiveness compared to static filtering methods. Transformer-based NLP architectures such as BERT, RoBERTa, and DistilBERT have consequently emerged as standard tools for understanding linguistic patterns in chat environments. 

Furthermore, longitudinal behavioral analysis has been shown to be a strong predictive indicator of future harmful activity. Studies indicate that tracking interaction patterns over time can achieve up to 74% balanced accuracy in forecasting future toxic behavior, reinforcing the importance of behavioral modeling in proactive moderation systems. 

Despite these advancements, current moderation systems remain constrained by their reliance on legacy datasets such as PAN12, which may not adequately represent modern online communication styles, slang, or evolving evasion techniques used by malicious actors. 

## 2.2 Related Studies

Several empirical studies have explored the application of artificial intelligence in detecting grooming-related interactions within online environments.

The empirical study of automated grooming detection is anchored in the PAN-2012 Sexual Predator Identification task introduced by Inches and Crestani [13], which released the benchmark corpus of chat logs used throughout this line of research and defined the task in two parts: identifying the predators among all participants in a set of conversations, and identifying the specific lines most characteristic of predatory behavior. This task definition established the author-level labeling protocol—in which a participant is treated as predatory across the conversations they take part in—that subsequent grooming-detection systems, including the present study, adopt.

Building on this benchmark, Villatoro-Tello et al. [14] proposed a two-step approach that first separates predatory from non-predatory participants and then identifies the most suspicious users, combining content-based features with behavioral features such as the proportion and pattern of a user’s interventions within a conversation. Their system achieved the highest performance among the sixteen teams in the PAN-2012 competition, demonstrating that participation and interaction-pattern features—not message content alone—carry discriminative signal for predator detection. This finding directly motivates the use of behavioral trajectory features alongside message-level analysis in the present study.

Street et al. [2] developed a transformer-based classification approach using BERT and RoBERTa models to identify online grooming interactions by analyzing conversational roles between adults and minors. Their contextual determination framework improved cross-dataset robustness in identifying suspicious communication patterns across multiplayer gaming chats. 

Faraz et al. [3] proposed *Protectbot*, an AI-based chatbot that actively simulates user interaction to expose predatory intent. Utilizing the DialoGPT language model combined with intent classifiers such as fastText and Support Vector Machines, the system achieved an __F__-__score of 0.99__ in detecting grooming behavior within simulated chat environments. 

Comparative evaluations conducted by Tereshchenko and Hämäläinen [5] revealed that lightweight transformer models such as DistilBERT provide an optimal balance between computational efficiency and moderation accuracy in high-volume chat systems. Their findings showed that while large generative language models offer improved linguistic nuance, they introduce latency issues that hinder real-time deployment in live environments. 

In addition, qualitative analyses of real-time moderation frameworks within child-centric platforms such as Roblox have highlighted sociotechnical challenges including algorithmic bias, cultural sensitivity issues, and limited transparency in automated decision-making processes. 

While these studies demonstrate the effectiveness of AI-based moderation tools, many approaches still analyze localized chat contexts or isolated messages. As a result, they may fail to model behavioral trajectories that evolve across multiple turns within a conversation.

## 2.3 Theoretical Background

The theoretical foundation of this study is based on advancements in machine learning-driven natural language processing and behavioral pattern recognition.

Beyond the computational literature, the detection task is grounded in discourse-analytic models of how grooming unfolds in conversation. O’Connell [12] provided one of the earliest typologies, describing online grooming as a progression through stages—friendship forming, relationship forming, risk assessment, exclusivity, and a sexual stage—in which an offender gradually escalates a relationship with a minor. While influential, this stage model assumes a largely linear progression that later empirical work has shown offenders do not consistently follow.

The primary theoretical framework adopted in this study is the model of online grooming discourse developed by Lorenzo-Dus, Izura, and Pérez-Tattam [11]. Drawing on a large corpus of offender chat logs, their analysis characterizes grooming not as a fixed linear sequence but as an entrapment network realized through four interrelated communicative processes: deceptive trust development, sexual gratification, compliance testing, and isolation. Deceptive trust development—the discursive building of rapport and a sense of an exclusive relationship—was found to be the most frequent process and to correlate with the others. Compliance testing refers to repeatedly probing a target’s boundaries and then retreating to gauge and condition responses, while isolation works to separate the target from sources of support and to concentrate the interaction within the dyad. Because these processes are defined at the level of observable language behavior rather than fixed conversational turns, they provide a basis for measuring grooming risk as it accumulates across a conversation.

To connect this discourse model to a computable system, the study operationalizes selected OGDM processes as quantitative features computed over conversation history. Operationalization—the standard methodological practice of translating a theoretical construct into a measurable variable [15] —provides the bridge between the qualitative model and the numeric signals a classifier can consume. The compliance-testing process is operationalized as a spike-then-drop pattern in per-message risk scores together with a count of risk spikes; the isolation and dominance behaviors of the entrapment network are operationalized as turn-taking imbalance between the two most active participants, consistent with the behavioral-feature approach of Villatoro-Tello et al. [14]; and the steering of conversation away from neutral small-talk toward intimate content is operationalized as topic drift relative to a benign-conversation baseline. The persistence of risk once predatory content has appeared is retained as the peak risk score observed so far. Each feature therefore traces to a documented OGDM construct rather than an ad hoc heuristic—an auditable property that distinguishes this approach from opaque end-to-end classification.

Recent moderation frameworks adopt sequence modeling techniques, which evaluate conversations as evolving interaction chains rather than isolated textual inputs [6]. This approach allows systems to detect behavioral trajectories characteristic of grooming related activities, such as gradual trust-building, self-disclosure, or attempts to isolate users within private communication channels. 

However, current methodologies often evaluate text-based data in isolation and may fail to capture longer conversational progression across message turns. Multimodal behavioral indicators, such as spatial interaction patterns or economic incentives within digital environments, remain outside the scope of the present study and are recommended for future work.

These limitations reveal a methodological gap in existing moderation systems, particularly in detecting slow-developing threats such as grooming behavior, which typically manifest through subtle interaction patterns across multiple messages rather than explicit rule violations. 

To address these challenges, contemporary research recommends hybrid moderation frameworks combining automated AI-based triage with human-in-the-loop (HITL) review mechanisms. Such layered architectures enable high-speed real-time flagging of suspicious interactions while preserving human oversight for nuanced adjudication and minimizing algorithmic bias. 

This study adopts these theoretical principles, operationalizing the OGDM communicative processes as measurable trajectory features, in the development of a behavioral-contextual moderation module designed to enhance existing chat moderation systems by integrating conversational history analysis and user interaction tracking.

# III. METHODOLOGY

## 3.1 Research Design

This study uses a developmental and experimental research design [15] to build and evaluate an offline conversation-analysis prototype. The approved primary endpoint is **conversation-level identification of PAN12 conversations that contain at least one author listed by PAN12 as a sexual predator**. The endpoint is author-derived and conversation-level; it is not a claim that PAN12 provides complete message-level grooming or grooming-onset annotations.

The proposed system has two learned layers. Layer 1 fine-tunes DistilBERT using the official predator-author list as weak supervision. For each current turn, it processes that turn together with the two preceding turns and produces a **predator-author proxy score**. Layer 2 uses the chronological sequence of proxy-derived trajectory features to estimate whether the conversation contains a listed predator. The LSTM remains the proposed sequence model, while a weighted scorer, an aggregated raw Layer 1 score, and a keyword rule serve as comparison methods.

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

The prototype system is developed and tested using Jupyter Notebook and Visual Studio Code within a Python-based experimental environment. Layer 1 training is designed to use an NVIDIA CUDA-capable GPU with mixed-precision computation when supported, while retaining a CPU-compatible path. Table 3.1 records the local development environment available when the protocol was revised. The final training run will additionally serialize the teammate workstation's GPU model, CUDA version, package versions, command-line arguments, random seed, source-data hashes, split-manifest hash, and output-checkpoint hash.

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

The primary experiment uses the PAN12 Sexual Predator Identification training corpus and its official predator-author list [13]. The current audited dyadic candidate pool contains 18,568 conversations, 454 positive conversations, and 34,688 distinct author identifiers before the new final split is locked. Final post-filter message, conversation, author, class, and split counts will be taken from the machine-generated manifest rather than entered manually.

For conversation \(c\), let \(A_c\) be its set of authors and \(P\) the official PAN12 predator-author set. The primary ground-truth label is

\[
Y_c = \mathbf{1}[A_c \cap P \neq \varnothing].
\]

Thus, a positive case is a conversation containing at least one officially listed predator author. For Layer 1 only, the weak target for turn \(t\), authored by \(a_t\), is

\[
Z_t = \mathbf{1}[a_t \in P].
\]

Because \(Z_t\) repeats an author-level identity label on that author's turns, it does not establish that a particular turn contains grooming behavior. The Layer 1 output is therefore called a predator-author proxy score rather than a grooming-message probability.

Table 3.2 separates the valid supervision from project artifacts that are not eligible for the revised experiment.

| Data artifact | Available supervision | Role in the revised experiment |
|---|---|---|
| PAN12 training conversations and official predator list | Author identity and derived conversation label | Sole source for primary training, validation, and final evaluation |
| PAN12 training `diff.txt` / project `is_suspicious` | Locations where released text was modified | Excluded from every filter, target, loss, feature decision, and metric |
| Project synthetic chat files | Generator-, scenario-, or speaker-role-derived proxy labels without completed independent review | Excluded from the primary experiment |
| PAN12 Problem 2 judged test lines | Pooled post-competition line judgments; matching test text is not available locally | Not used; eligible only for a separately qualified future external evaluation if the exact test corpus is recovered |

*Table 3.2. Label provenance and eligibility for the revised experiment.*

### 3.3.2 Inclusion and Preprocessing

The primary corpus is restricted to conversations with exactly two distinct authors to match the dyadic interaction scope and the implemented turn-taking feature. Empty messages and rows without a valid conversation identifier, chronological line identifier, author identifier, or binary official predator-author status are excluded. Original conversation and line identifiers are retained. Each usable row receives a stable key based on dataset source, conversation identifier, and line identifier so that duplicate text cannot overwrite another turn's cached score.

Conversations are ordered by their original line identifier. Layer 1 receives a prefix-only context consisting of the current turn and up to two immediately preceding turns from the same conversation. Neutral turn separators are inserted, but raw author identifiers, predator-list membership, the project `is_suspicious` field, source-revealing role names, future turns, and conversation labels are never included in model text. Training and inference use the identical context-construction function. The DistilBERT tokenizer truncates each context to 128 tokens and applies dynamic padding within each batch.

Text normalization is deliberately conservative: character encoding and whitespace are standardized, while altered spellings and obfuscations are retained so that evaluation does not benefit from a hand-written correction rule unavailable to the learned model. The primary experiment does not add synthetic conversations or separately collected chat logs.

### 3.3.3 Connected-Author Data Partitioning

The dataset is partitioned before negative sampling, context caching, centroid construction, model fitting, or threshold selection. Conversations are represented as vertices in a graph; any conversations sharing an author are connected. Every resulting connected component is assigned wholly to one partition, creating zero conversation overlap and zero author overlap across training, validation, and final test data.

Because an earlier pipeline already exposed results on its historical test partition, that partition is retained only as development history. Before training the revised model, a new final holdout is selected from previously unscored connected-author components using metadata only: component membership, partition size, and class balance. No model score or text-derived feature is used to choose the holdout. The remaining eligible components are assigned to training and validation. The exact assignments, counts, random seed, source-data hash, and manifest hash are serialized and locked before the first revised training run.

The training partition is used for parameter estimation and may downsample negative Layer 1 rows using a recorded ratio. Downsampling occurs only after the split and only in training. Validation and final test distributions remain untouched. The validation partition is used for checkpoint selection, hyperparameter selection, comparator fitting, and threshold selection. The locked final test is evaluated once after code, checkpoints, thresholds, feature definitions, and reporting rules are frozen.

### 3.3.4 Feature Engineering

Let \(R_i\) denote the Layer 1 predator-author proxy score at turn \(i\), \(E_t\) the 768-dimensional embedding from the unchanged base `distilbert-base-uncased` encoder for the current turn, \(C_b\) a benign-chat centroid computed only from negative conversations in the training partition, \(T_a\) the number of turns contributed by participant \(a\), \(\tau\) the spike threshold, and \(\delta\) the drop threshold. The seven trajectory features at turn \(t\) are:

1. **Peak proxy score:** \(\max_{1 \leq i \leq t} R_i\), with range \([0,1]\).
2. **Current proxy score:** \(R_t\), with range \([0,1]\).
3. **Spike count:** \(\sum_{i=1}^{t}\mathbf{1}[R_i>\tau]\), with range \([0,t]\).
4. **Spike-then-drop:** 1 when an earlier score exceeded \(\tau\) and a later score dropped by more than \(\delta\); otherwise 0.
5. **Rate of change:** \(R_t-R_{t-1}\), or 0 for the first turn, with range \([-1,1]\).
6. **Topic distance:** \(1-\cos(E_t,C_b)\), with theoretical range \([0,2]\).
7. **Turn-taking imbalance:** \(\lvert T_A-T_B\rvert/(T_A+T_B)\), with range \([0,1]\). The implementation counts turns, not words.

The centroid source conversation IDs and embedding-model digest are recorded, and validation or test text is never used to construct it. The spike and drop thresholds are selected on validation data and then frozen. Each turn-level cache is keyed by the stable dataset/conversation/line identifier and records the context-construction version, Layer 1 checkpoint digest, base-encoder digest, and split assignment.

| Input | Definition | Models receiving it |
|---|---|---|
| Layer 1 proxy score | Context-conditioned estimate of the author-derived target \(Z_t\) | Raw Layer 1 baseline and trajectory-feature construction |
| Seven trajectory features | Peak, current, spike count, spike-then-drop, rate of change, topic distance, and turn imbalance | Weighted scorer and primary matched-input LSTM |
| Base DistilBERT embedding | 768-dimensional contextual text representation, separate from the Layer 1 proxy | Secondary enhanced-input LSTM only |

*Table 3.3. Inputs used by the revised comparison methods.*

## 3.4 Model Development

### 3.4.1 Author-Derived Layer 1 Classifier

Layer 1 uses `distilbert-base-uncased` with a two-class sequence-classification head. Its input is the current turn plus the two preceding turns defined in Section 3.3.2, and its target is the current author's official predator-list membership \(Z_t\). The training loss is two-class cross-entropy. Negative-row downsampling is confined to the training partition; validation and final test rows retain their natural class distribution.

Optimization uses AdamW, a recorded random seed, gradient clipping, validation-based early stopping, and mixed precision on a compatible NVIDIA GPU. All numeric choices, including learning rate, batch size, gradient accumulation, epoch limit, warm-up ratio, weight decay, and negative-sampling ratio, are specified in the training configuration rather than altered after test inspection. The checkpoint is selected using validation area under the precision-recall curve (PR-AUC), and its operating threshold is selected separately on validation data using F0.5. The selected checkpoint, tokenizer, configuration, metrics history, row manifest, and cryptographic hashes are saved together.

The positive-class softmax output is denoted \(R_t\). It estimates the weak author-derived classification target under the available text context. It must not be described as a validated probability of grooming content, grooming phase, or grooming onset.

### 3.4.2 LSTM-Based Trajectory Scoring Model

The primary Layer 2 model is an LSTM that receives the chronological sequence of the same seven features supplied to the weighted scorer. Padding masks ensure that padded turns do not affect hidden-state computation. A secondary enhanced-input LSTM concatenates the 768-dimensional base DistilBERT embedding with the seven trajectory features, producing a 775-dimensional turn vector; its result is reported separately and is not used to claim a matched-input architectural advantage.

Layer 2 is trained only against the valid conversation label \(Y_c\). Binary cross-entropy with logits is applied to the output at the final valid turn, with any positive-class weighting computed from training conversations only. No turn-level loss, cumulative `is_suspicious` target, or repeated predator-author label is used as grooming-onset supervision. Validation selects the LSTM checkpoint and its conversation flagging threshold. Intermediate prefix scores may be displayed to demonstrate sequence processing, but the first threshold crossing is reported only as an exploratory prefix statistic, not as validated grooming onset or time-to-harm.

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

The historical LSTM result obtained before this correction is retained only as a development diagnostic because its Layer 1 supervision, comparator tuning, and test-use history do not satisfy the revised protocol. It is not combined with or substituted for the new final evaluation. The revised result is reported even if the LSTM does not outperform a baseline.

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

PR-AUC is emphasized alongside thresholded metrics because positive conversations are rare. Validation PR-AUC selects checkpoints, while validation F0.5 selects operating thresholds; no threshold is retuned on the final test. Ninety-five-percent confidence intervals are estimated by bootstrap resampling connected-author components so that conversations linked by an author remain grouped. Pairwise thresholded predictions may additionally be compared with McNemar's test when the number of discordant final-test cases is sufficient.

Prefix-level scores and first-threshold-crossing turns are summarized only as exploratory sequence behavior. PAN12 does not supply exhaustive training annotations for the first grooming turn, so these summaries are not evaluated or described as message-level detection accuracy, grooming-stage accuracy, or true time to detection.

## 3.6 Ethical Considerations

All datasets used in this study are handled in accordance with applicable data-protection and research-ethics principles. The PAN12 corpus is a publicly available research dataset with established usage guidelines. In the local demonstration interface, common direct identifiers—including email addresses, phone numbers, URLs, IPv4 addresses, and common account handles—are masked before model scoring and in-memory retention. Responses are marked as non-cacheable, and resetting the demonstration deletes the active in-process conversation object. These safeguards reduce exposure but do not guarantee complete anonymization: automatic pattern matching may miss names, indirect identifiers, unusual formats, or identifying combinations of details. Real sensitive information must therefore not be entered into the prototype, and any research data still requires access control and manual privacy review.

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
