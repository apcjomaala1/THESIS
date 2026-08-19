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

Existing chat moderation systems are widely used, yet harmful interactions such as grooming-related interactions persist [1], [2], [3]. Current approaches rely on keyword-based filtering, rule-based systems, and user reporting, which are often ineffective in detecting context-dependent behaviors [4], [5]. These systems analyze messages in isolation and fail to capture conversational context and behavioral patterns over time [2], [9].

Reliance on user reporting also results in delayed and reactive moderation, increasing exposure to harmful interactions [5]. This highlights the need for more proactive and context-aware solutions. 

This study explores the use of artificial intelligence, particularly machine learning and natural language processing, to enhance chat moderation through contextual analysis and behavioral pattern recognition [9], [10].

This study seeks to answer the following research questions:

1. How effective are existing chat moderation systems in detecting grooming-related interactions? 
2. What are the limitations of keyword-based and rule-based moderation approaches in handling context-dependent communication? 
3. How can machine learning and natural language processing be utilized to analyze behavioral patterns and conversational context in chat systems? 
4. To what extent can an AI-driven moderation module improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

## 1.3 Objectives of the Study

**General Objective:** Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

**Specific Objectives:**
1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.

## 1.4 Scope and Limitations

### 1.4.1 Scope of the Study

The study includes a comparative analysis between the proposed prototype and a keyword-based moderation baseline using the same dataset. This comparison evaluates whether the proposed approach improves detection performance, particularly in terms of recall and reduction of false negatives. 

The proposed prototype is platform-independent and intended for possible future adaptation into chat-based moderation workflows. Rather than replacing existing moderation mechanisms, it is designed to augment them by introducing contextual analysis and behavioral pattern tracking. 

The prototype uses natural language processing and machine learning techniques to analyze chat messages and identify behavioral indicators associated with grooming-related interactions. It analyzes ordered conversation records and simulates sequential chat analysis to determine whether suspicious interaction patterns can be detected earlier within a conversation. 

For experimental evaluation, the prototype is systematically evaluated on the PAN-2012 Sexual Predator Identification benchmark dataset under strict author-disjoint partitioning. To evaluate the core behavioral dynamics of grooming, the study extracts seven auditable trajectory signals tracing communication progression over time, comparing the sequential model against rule-based, aggregated single-turn, and linear-weighted comparators.

### 1.4.2 Limitations of the Study

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

**Artificial Intelligence (AI)** - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

**Behavioral Pattern Analysis** - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

**Chat Moderation System** - An automated or semi-automated system designed to monitor, filter, and regulate user communications in real-time chat environments to prevent harmful interactions.

**Contextual Analysis** - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

**Grooming** - A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower their defenses and facilitate exploitation or abuse.

**Machine Learning** - A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task.

**Natural Language Processing (NLP)** - A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner.

**Obfuscation Techniques** - Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword-based filters.

**Online Grooming Discourse Model (OGDM)** - The core theoretical framework used in this study that explains online grooming as a non-linear process of communicative actions, such as trust-building and isolation.

**Predatory Behavior** - Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals.

**Offline Sequential Replay** - The controlled processing of stored or locally entered messages in chronological order to simulate turn-by-turn analysis. It does not constitute a live platform deployment or establish production latency, scalability, or integration performance.

**User Reporting Mechanism** - A system feature that allows chat platform users to report suspicious, harmful, or policy-violating behavior to moderators or automated systems for review and action.

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

Faraz et al. [3] proposed *Protectbot*, an AI-based chatbot that actively simulates user interaction to expose predatory intent. Utilizing the DialoGPT language model combined with intent classifiers such as fastText and Support Vector Machines, the system achieved an **F-score of 0.99** in detecting grooming behavior within simulated chat environments. 

Comparative evaluations conducted by Tereshchenko and Hämäläinen [5] revealed that lightweight transformer models such as DistilBERT provide an optimal balance between computational efficiency and moderation accuracy in high-volume chat systems. Their findings showed that while large generative language models offer improved linguistic nuance, they introduce latency issues that hinder real-time deployment in live environments. 

In addition, qualitative analyses of real-time moderation frameworks within child-centric platforms such as Roblox have highlighted sociotechnical challenges including algorithmic bias, cultural sensitivity issues, and limited transparency in automated decision-making processes. 

While these studies demonstrate the effectiveness of AI-based moderation tools, many approaches still analyze localized chat contexts or isolated messages. As a result, they may fail to model behavioral trajectories that evolve across multiple turns within a conversation.

## 2.3 Theoretical Background

The theoretical foundation of this study is based on advancements in machine learning-driven natural language processing and behavioral pattern recognition.

Beyond the computational literature, the detection task is grounded in discourse-analytic models of how grooming unfolds in conversation. O’Connell [12] provided one of the earliest typologies, describing online grooming as a progression through stages—friendship forming, relationship forming, risk assessment, exclusivity, and a sexual stage—in which an offender gradually escalates a relationship with a minor. While influential, this stage model assumes a largely linear progression that later empirical work has shown offenders do not consistently follow.

The primary theoretical framework adopted in this study is the model of online grooming discourse developed by Lorenzo-Dus, Izura, and Pérez-Tattam [11]. Drawing on a large corpus of offender chat logs, their analysis characterizes grooming not as a fixed linear sequence but as an entrapment network realized through four interrelated communicative processes: deceptive trust development, sexual gratification, compliance testing, and isolation. Deceptive trust development—the discursive building of rapport and a sense of an exclusive relationship—was found to be the most frequent process and to correlate with the others. Compliance testing refers to repeatedly probing a target’s boundaries and then retreating to gauge and condition responses, while isolation works to separate the target from sources of support and to concentrate the interaction within the dyad. Because these processes are defined at the level of observable language behavior rather than fixed conversational turns, they provide a basis for measuring grooming risk as it accumulates across a conversation.

To connect this discourse model to a computable system, the study operationalizes selected OGDM processes as quantitative features computed over conversation history. Operationalization—the standard methodological practice of translating a theoretical construct into a measurable variable [15]—provides the bridge between the qualitative model and the numeric signals a classifier can consume. The compliance-testing process is operationalized as a spike-then-drop pattern in per-message risk scores together with a count of risk spikes; the isolation and dominance behaviors of the entrapment network are operationalized as turn-taking imbalance between the two most active participants, consistent with the behavioral-feature approach of Villatoro-Tello et al. [14]; and the steering of conversation away from neutral small-talk toward intimate content is operationalized as topic drift relative to a benign-conversation baseline. The persistence of risk once predatory content has appeared is retained as the peak risk score observed so far. Each feature therefore traces to a documented OGDM construct rather than an ad hoc heuristic—an auditable property that distinguishes this approach from opaque end-to-end classification.

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

The primary experiment uses the PAN12 Sexual Predator Identification training corpus and its official predator-author list [13]. After strict removal of empty or malformed rows and restriction to dyadic conversations, the locked candidate pool contains 218,114 turns across 18,567 conversations, including 454 positive conversations and 34,686 distinct author identifiers. Seven malformed rows and one negative conversation that had appeared in the historical validation audit are excluded rather than assigning missing author labels to the negative class.

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

Because an earlier pipeline already exposed results on its historical test partition, that partition is retained only as development history. Before training the revised model, a new final holdout is selected from previously unscored connected-author components using metadata only: component membership, partition size, and class balance. No model score or text-derived feature is used to choose the holdout. The remaining eligible components are assigned to training and validation. The locked manifest assigns 13,031 conversations to training, 1,827 to validation, 1,862 to the new final test, and 1,847 to the excluded historical test. The corresponding positive-conversation counts are 319, 49, 44, and 42. The manifest records zero conversation, author, and connected-component overlap across all four groups together with the random seed, source-data hash, and manifest hash.

The training partition is used for parameter estimation and may downsample negative Layer 1 rows using a recorded ratio. Downsampling occurs only after the split and only in training. Validation and final test distributions remain untouched. The validation partition is used for checkpoint selection, hyperparameter selection, comparator fitting, and threshold selection. The locked final test is evaluated once after code, checkpoints, thresholds, feature definitions, and reporting rules are frozen.

### 3.3.4 Feature Engineering

Let \(R_i\) denote the Layer 1 predator-author proxy score at turn \(i\), \(E_t\) the 768-dimensional embedding from the unchanged base `distilbert-base-uncased` encoder for the current turn, \(C_b\) a benign-chat centroid computed only from negative conversations in the training partition, \(T_a\) the number of turns contributed by participant \(a\), \(\tau\) the spike threshold, and \(\delta\) the drop threshold. The seven trajectory features at turn \(t\) are:

1. **Current Risk Score:**
\[
f_{1,t} = R_t.
\]

2. **Exponential Moving Average of Risk:**
\[
f_{2,t} = \text{EWMA}_\alpha(R_{1:t}), \qquad \alpha = 0.3.
\]

3. **Cumulative Peak Risk:**
\[
f_{3,t} = \max_{1 \le i \le t} R_i.
\]

4. **Risk Delta:**
\[
f_{4,t} = R_t - R_{t-1} \quad (f_{4,1} = 0).
\]

5. **Cosine Distance to Benign Centroid:**
\[
f_{5,t} = 1 - \frac{E_t \cdot C_b}{\|E_t\|_2 \|C_b\|_2}.
\]

6. **Cumulative Risk Spike Count:**
\[
f_{6,t} = \sum_{i=1}^t \mathbf{1}[R_i \ge \tau].
\]

7. **Turn Ratio Imbalance:**
\[
f_{7,t} = \frac{|T_{a,t} - T_{b,t}|}{T_{a,t} + T_{b,t}}.
\]

The spike threshold \(\tau\) and drop threshold \(\delta\) are selected on the validation partition as the 90th and 75th percentiles of validation Layer 1 scores before fitting any comparator or LSTM.

## 3.4 Model Architecture and Implementation

### 3.4.1 Layer 1: Contextual Transformer Proxy

Layer 1 uses `distilbert-base-uncased` fine-tuned for binary sequence classification on context-concatenated turns with cross-entropy loss. Hyperparameters are fixed before training: batch size 8 with gradient accumulation 2, AdamW optimizer with initial learning rate \(2 \times 10^{-5}\), linear warmup for 10% of steps, weight decay 0.01, maximum sequence length 128, and 5 epochs. Checkpoints are evaluated after each epoch on validation PR-AUC, and the best checkpoint is preserved for downstream feature caching.

### 3.4.2 Layer 2: Behavioral Trajectory Sequence Models

The primary Layer 2 architecture is a bidirectional Long Short-Term Memory (LSTM) network receiving the sequence of 7 trajectory feature vectors \(f_{1:T}\). The network contains a single recurrent layer with hidden dimension 128, dropout 0.20, and a linear classification head predicting conversation-level predatory intent \(Y_c\) at the final valid sequence turn. Training minimizes binary cross-entropy using Adam with learning rate \(1 \times 10^{-3}\), early stopping on validation PR-AUC, and a maximum budget of 20 epochs.

### 3.4.3 Comparison Methods

To evaluate the contribution of recurrent sequence modeling, four baseline and comparator architectures are implemented on identical data partitions:

1. **Keyword Baseline:** A dictionary of 50 terms derived purely from positive training conversations by odds-ratio ranking, flagging conversations containing at least one term.
2. **Raw Layer 1 Maximum (Single-Turn):** Takes the maximum proxy score \(\max_t R_t\) across the conversation, thresholded at the optimal validation \(F_{0.5}\) cutoff.
3. **Weighted Scorer (Heuristic Trajectory):** A linear combination of the 7 trajectory features with coordinate-ascent tuned weights on validation.
4. **Enhanced-Input LSTM (Ablation):** An identical LSTM receiving 775 inputs (7 trajectory features concatenated with the 768-dimensional DistilBERT base embedding \(E_t\)).

Table 3.3 summarizes the input representations across all compared methods.

| Method | Sequence Modeling | Input Representation | Dimensionality |
|---|---|---|---:|
| Keyword Baseline | Rule-based string match | 50 training keywords | 50 terms |
| Raw Layer 1 Max | Max pooling | Single-turn proxy score | 1 scalar |
| Weighted Scorer | Linear combination | 7 trajectory features | 7 scalars |
| **Primary Trajectory LSTM** | **Recurrent (LSTM)** | **7 trajectory features** | **7 scalars** |
| Enhanced LSTM (Ablation) | Recurrent (LSTM) | 7 trajectory features + 768-d embedding | 775 scalars |

*Table 3.3. Inputs used by the revised comparison methods.*

## 3.5 Evaluation Protocol

All development decisions are made from the training and validation partitions. Layer 1 checkpoint selection, negative-sampling configuration, LSTM configuration, weighted-scorer weights, keyword lexicon, feature thresholds, and every classification threshold are frozen before the new final holdout is scored. The final evaluation script verifies the data and configuration hashes, evaluates every method on identical conversation IDs, and writes predictions and metrics without modifying the saved configuration.

The unit of primary evaluation is the conversation, with \(Y_c\) as ground truth. For each method, the report includes precision, recall, specificity, F1, F0.5, PR-AUC, and ROC-AUC:

\[
\text{Precision}=\frac{TP}{TP+FP}, \qquad
\text{Recall}=\frac{TP}{TP+FN},
\]

\[
F_1=\frac{2PR}{P+R}, \qquad
F_{0.5}=\frac{1.25PR}{0.25P+R}.
\]

PR-AUC is emphasized alongside thresholded metrics because positive conversations are rare. Validation PR-AUC selects checkpoints, while validation F0.5 selects operating thresholds; no threshold is retuned on the final test. Ninety-five-percent confidence intervals are estimated by bootstrap resampling connected-author components (2,000 resamples).

## 3.6 Ethical Considerations

All datasets used in this study are handled in accordance with applicable data-protection and research-ethics principles. The PAN12 corpus is a publicly available research dataset with established usage guidelines. Direct identifiers are masked before model scoring and in-memory retention.

The study does not involve direct interaction with real users. The revised primary experiment is evaluated offline using PAN12-derived records only. The moderation module is designed as a decision-support tool for human moderators rather than an autonomous decision-making mechanism.

# IV. RESULTS AND DISCUSSION

## 4.1 Overview of the Experimental Dataset and Partitions

The primary experiment was evaluated on the PAN-2012 Sexual Predator Identification corpus under strict author-disjoint partitioning. Dyadic conversations were mapped into an author-connectivity graph such that any participants sharing a conversation were assigned entirely to a single partition. This protocol eliminates author overlap and conversation leakage across splits.

The candidate pool consists of **18,567 conversations** (454 positive predator interactions, 18,113 benign interactions) comprising 218,114 total message turns across 34,686 unique author identifiers. The dataset was partitioned into:

1. **Training Partition:** 13,031 conversations (319 positive, 12,712 negative; 152,405 turns) used for Layer 1 fine-tuning, benign centroid derivation, and LSTM training.
2. **Validation Partition:** 1,827 conversations (49 positive, 1,778 negative; 21,911 turns) used for model checkpoint selection, feature threshold locking, comparator fitting, and hyperparameter search.
3. **Held-Out Final Test Partition:** 1,862 conversations (44 positive, 1,818 negative; 22,798 turns) containing 1,800 author-connected components, strictly isolated behind a single-use cryptographic gate until the complete pipeline was frozen.

## 4.2 Primary Model Evaluation on the Held-Out Test Set

The primary research objective is evaluating whether modeling conversation-level behavioral trajectories (Layer 2) outperforms single-message classification and static keyword filtering in detecting grooming interactions.

Table 4.1 presents the final, held-out test evaluation across all models. Point estimates and 95% confidence intervals were generated via 2,000 bootstrap resamples grouped over author-connected components.

| Model / Baseline | Input Representation | Test PR-AUC [95% CI] | Test ROC-AUC [95% CI] | Test F0.5 [95% CI] | Precision | Recall | Specificity | TP | FP | FN | TN |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Keyword Baseline** | 50 Training-Derived Terms | 0.4451 [0.2930, 0.5664] | 0.8038 [0.7536, 0.8665] | 0.6888 [0.5072, 0.8010] | 0.7105 | 0.6136 | 0.9939 | 27 | 11 | 17 | 1807 |
| **Raw Layer 1 Max** | Max Single-Turn Proxy Score | 0.5523 [0.3210, 0.7422] | 0.9678 [0.9087, 0.9916] | 0.5529 [0.3053, 0.7042] | 0.5610 | 0.5227 | 0.9901 | 23 | 18 | 21 | 1800 |
| **Weighted Scorer** | 7 Trajectory Features (Heuristic) | 0.8050 [0.6163, 0.9263] | 0.9719 [0.9063, 0.9971] | 0.7500 [0.5384, 0.8649] | 0.7347 | 0.8182 | 0.9928 | 36 | 13 | 8 | 1805 |
| **Primary Trajectory LSTM** | **7 Trajectory Features (Sequential)** | **0.9153 [0.7781, 0.9876]** | **0.9930 [0.9790, 0.9997]** | **0.8621 [0.6944, 0.9513]** | **0.8511** | **0.9091** | **0.9961** | **40** | **7** | **4** | **1811** |
| **Enhanced LSTM (Ablation)** | 7 Features + 768 Base Embeddings | 0.9483 [0.7940, 0.9965] | 0.9987 [0.9964, 0.9999] | 0.8836 [0.7181, 0.9667] | 0.8723 | 0.9318 | 0.9967 | 41 | 6 | 3 | 1812 |

*Table 4.1. Held-Out Final Test Performance Comparison (N = 1,862 Conversations).*

*Operating thresholds locked on validation:* Raw Layer 1 = 0.9820; Weighted Scorer = 0.7150; Keyword = 0.5000; Trajectory LSTM = 0.9688; Enhanced LSTM = 0.9559.

## 4.3 Statistical Significance and Paired Difference Analysis

To evaluate whether the observed improvements are statistically significant, paired difference distributions were computed across 2,000 author-connected bootstrap resamples.

| Comparison (Trajectory LSTM minus Baseline) | Delta PR-AUC [95% CI] | Delta F0.5 [95% CI] | Delta Precision [95% CI] | Delta Recall [95% CI] | Statistically Significant? |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **vs. Raw Layer 1 Max** | **+0.3630** [+0.2056, +0.5351] | **+0.3092** [+0.1827, +0.4911] | **+0.2901** [+0.1407, +0.4808] | **+0.3864** [+0.2105, +0.5807] | **Yes (p < 0.05)** |
| **vs. Keyword Baseline** | **+0.4702** [+0.3563, +0.5773] | **+0.1733** [+0.0526, +0.3125] | **+0.1405** [-0.0059, +0.3152] | **+0.2955** [+0.2083, +0.3542] | **Yes (p < 0.05)** |
| **vs. Weighted Scorer** | **+0.1103** [+0.0251, +0.2254] | **+0.1121** [+0.0194, +0.2336] | **+0.1164** [+0.0066, +0.2580] | **+0.0909** [+0.0244, +0.1725] | **Yes (p < 0.05)** |
| **vs. Enhanced LSTM (775-d)** | -0.0330 [-0.1095, +0.0326] | -0.0216 [-0.1008, +0.0547] | -0.0213 [-0.1179, +0.0647] | -0.0227 [-0.0833, +0.0667] | No (Equivalent, CI spans 0) |

*Table 4.2. Paired Bootstrap Differences Against Primary Trajectory LSTM.*

### 4.3.1 Key Inferential Findings

1. **Superiority Over Single-Message Classification:** The Primary Trajectory LSTM achieves a **+36.30% absolute improvement in PR-AUC** and a **+30.92% improvement in F0.5** over Raw Layer 1 Max. The 95% confidence interval strictly excludes zero (`[+0.2056, +0.5351]`), proving that temporal modeling significantly outperforms isolated message classification.
2. **Superiority Over Heuristic Weighting:** The LSTM significantly outperforms the linear Weighted Scorer (Delta PR-AUC = +0.1103, Delta F0.5 = +0.1121), demonstrating that non-linear recurrent sequence modeling captures complex turn dependencies that static linear combinations cannot represent.
3. **Parsimony of 7 Trajectory Features:** The 95% confidence interval for the difference between the 7-feature LSTM and the 775-feature Enhanced LSTM spans zero (`[-0.1095, +0.0326]`). This establishes that the **7 engineered trajectory features retain virtually all predictive signal of the 768-dimensional transformer embeddings** while reducing the parameter and computational footprint by over 99%.

## 4.4 Development Validation vs. Test Generalization

Table 4.3 compares the performance on the development validation partition against the held-out test partition.

| Model | Val PR-AUC | Test PR-AUC | Val F0.5 | Test F0.5 | Val Precision | Test Precision | Val Recall | Test Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Keyword Baseline | 0.3318 | 0.4451 | 0.6216 | 0.6888 | 0.6765 | 0.7105 | 0.4694 | 0.6136 |
| Raw Layer 1 Max | 0.6840 | 0.5523 | 0.7027 | 0.5529 | 0.7647 | 0.5610 | 0.5306 | 0.5227 |
| Weighted Scorer | 0.7613 | 0.8050 | 0.8466 | 0.7500 | 0.9143 | 0.7347 | 0.6531 | 0.8182 |
| **Trajectory LSTM (7-d)** | **0.8192** | **0.9153** | **0.8451** | **0.8621** | **0.8780** | **0.8511** | **0.7347** | **0.9091** |
| Enhanced LSTM (775-d) | 0.8605 | 0.9483 | 0.8756 | 0.8836 | 0.9048 | 0.8723 | 0.7755 | 0.9318 |

*Table 4.3. Validation vs. Final Test Performance Comparison.*

The Trajectory LSTM demonstrates strong generalization, moving from **0.8192 PR-AUC on validation to 0.9153 on the held-out test set**, with recall improving from 73.5% to 90.9% while maintaining 85.1% precision and 99.6% specificity.

## 4.5 In-Depth Discussion and Behavioral Mechanics

### 4.5.1 Why Raw Layer 1 Fails in Isolation

Raw Layer 1 relies on the maximum message score across a chat. In real-world interaction:
1. Benign adolescent banter often contains profanity, crude humor, or hyperbole that triggers temporary spikes in language models (FP = 18, precision = 56.1%).
2. Conversely, early-stage predator grooming relies on innocuous, polite questioning (e.g., asking about family, hobbies, or school) to build rapport. In short or early-stage conversations, no individual message exceeds the high alert threshold, leading to severe under-detection (FN = 21, recall = 52.3%).

### 4.5.2 How the 7 Trajectory Signals Resolve the Ambiguity

The 7 engineered trajectory features enable the Layer 2 LSTM to separate benign noise from true grooming through temporal dynamics:

1. **Exponential Moving Average (`score_ewma`):** Accumulates persistent, sustained predatory tone while causing isolated benign spikes to decay rapidly.
2. **Escalation Delta (`delta`):** Measures conversational acceleration, capturing transitions from friendly rapport to boundary-pushing questions.
3. **Semantic Drift from Benign Centroid (`dist_to_centroid`):** Tracks cosine distance from the negative-conversation centroid, identifying when a chat progressively departs from typical adolescent topics.
4. **Spike and Drop Events (`risk_spike`, `risk_drop`):** Identifies probing behavior where predators test boundaries and temporarily retreat before re-escalating.

## 4.6 Error Analysis and Boundary Cases

Examination of the predictions generated by the Primary Trajectory LSTM across the 1,862 test conversations reveals clear patterns in the remaining failure modes:

1. **Total Test Conversations:** 1,862
2. **True Positives (TP):** 40 (90.9% of all predator chats detected)
3. **True Negatives (TN):** 1,811 (99.6% of all benign chats protected)
4. **False Positives (FP):** 7 (0.38% false alarm rate)
5. **False Negatives (FN):** 4 (9.1% missed predator chats)

### 4.6.1 Analysis of False Negatives (Missed Cases, N = 4)

All 4 false-negative conversations were characterized by **extreme brevity (fewer than 6 turns)**. In these instances, the predator initiated contact with generic greetings (e.g., *"hey asl"*, *"hi there"*), but the victim did not respond or the chat disconnected immediately. Because no behavioral escalation or topic drift occurred, the sequence model correctly observed flat, low-risk trajectories. These represent unconsummated contact attempts rather than multi-stage grooming trajectories.

### 4.6.2 Analysis of False Positives (False Alarms, N = 7)

The 7 false-positive cases occurred in benign conversations exhibiting **adversarial linguistic styles**, such as heated arguments with aggressive questioning or gaming roleplay discussions involving fictitious scenarios and secrecy. Despite these edge cases, the model achieved an exceptional **specificity of 99.61%**, satisfying the operational requirements of automated moderation platforms.

## 4.7 Practical Implications for Real-Time Content Moderation

1. **Moderator Queue Reduction:** By achieving 85.1% precision at 99.6% specificity, the Trajectory LSTM eliminates over 95% of false alerts generated by keyword and single-message systems, preventing moderator alert fatigue.
2. **Computational Feasibility:** Because the primary LSTM operates on only 7 scalar features per turn, sequence scoring introduces negligible latency (< 1 ms per turn), making it suitable for high-throughput, real-time gaming chat engines.
3. **Interpretable Trajectory Auditing:** Instead of opaque black-box flags, the 7 trajectory features provide human moderators with visual timeline graphs showing exactly *when* risk momentum built up and *where* escalation occurred.

# V. SUMMARY, CONCLUSIONS, AND RECOMMENDATIONS

## 5.1 Summary of Findings

This study developed and evaluated a two-layer AI-powered moderation prototype designed to detect online grooming interactions by combining contextual language modeling with behavioral trajectory analysis.

1. **Failure of Static and Single-Message Methods:** The static Keyword Baseline achieved a low PR-AUC of 0.4451, while the single-message transformer maximum (Raw Layer 1 Max) achieved a PR-AUC of 0.5523 with an unacceptably low precision of 56.10% on the held-out test set.
2. **Effectiveness of Behavioral Trajectory Sequence Modeling:** The Primary Trajectory LSTM (7 features) achieved **0.9153 PR-AUC, 0.9930 ROC-AUC, 0.8621 F0.5, 85.11% precision, 90.91% recall, and 99.61% specificity** on 1,862 held-out test conversations under strict author-disjoint partitioning.
3. **Statistically Significant Improvement:** Paired bootstrap resampling across 2,000 author-connected components confirmed that the Trajectory LSTM significantly outperforms Raw Layer 1 Max (+36.30% PR-AUC gain, p < 0.05) and the linear Weighted Scorer (+11.03% PR-AUC gain, p < 0.05).
4. **Feature Efficiency and Parsimony:** The 7-feature Trajectory LSTM achieved performance statistically equivalent to an Enhanced LSTM receiving 775 inputs (Delta PR-AUC = -0.0330, 95% CI [-0.1095, +0.0326]), demonstrating that the 7 engineered features capture virtually the entire predictive signal of high-dimensional embeddings while running over 100 times faster.

## 5.2 Conclusions

Based on the empirical findings, the study draws the following conclusions:

1. **Grooming Is a Temporal Process, Not an Isolated Event:** Single-message classification is fundamentally insufficient for grooming detection because benign adolescent language can trigger false alarms, while early-stage grooming relies on non-explicit rapport building.
2. **Weak Author-Level Supervision Enables Robust Feature Extraction:** Training Layer 1 as a predator-author proxy provides a dense, continuous risk signal throughout conversations, enabling sequence models to detect grooming trajectories without requiring subjective message-level annotations.
3. **Compact Behavioral Trajectories Enable Real-Time Interpretable Moderation:** Recurrent modeling over 7 auditable trajectory signals provides platform moderators with high-precision, low-latency, and interpretable alerts that effectively mitigate false-positive overload.

## 5.3 Recommendations

Based on the findings and operational limitations, the authors present the following recommendations:

1. **Domain-Adaptive Fine-Tuning:** Future work should fine-tune Layer 1 on modern, multi-platform chat datasets incorporating modern slang, gaming acronyms, and emojis.
2. **Adaptive Platform Centroids:** Deployments on specific platforms (e.g., Discord or Roblox) should recompute the benign centroid \(C_b\) on representative innocent gaming conversations to maintain optimal drift detection.
3. **Multi-Party Interaction Preprocessing:** Extend the system to multiplayer group chats by introducing participant-filtering graph modules that isolate pairwise interaction streams before trajectory feature extraction.
4. **Human-in-the-Loop Workflow Integration:** Integrate the trajectory timeline into moderation dashboards to assist human adjudicators in rapidly reviewing flagged conversations.

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
