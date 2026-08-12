# Conversation Trajectory Lab

*AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis*

 

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

Subject to adviser approval of the corrected conversation-level endpoint, this study seeks to answer the following questions:

1. Under connected-author separation, how effectively can a sequence model identify PAN12 conversations containing a listed predator?
2. How does a seven-feature LSTM compare with matched weighted, raw Layer 1, and keyword baselines when every method uses the same endpoint, partitions, and validation-only selection protocol?
3. For correctly flagged positive conversations, at which turn does each method first cross its validation-selected threshold during offline sequential replay?

## 1.3 Objectives of the Study

__General Objective:__ Develop and evaluate an offline conversation-trajectory research prototype for the proposed PAN12 endpoint `conversation_contains_listed_predator`. Genuine message-level grooming detection remains a separate extension that requires independently reviewed labels.

- __Specific Objective:__
	1. Audit label provenance and construct connected-author train, validation, and locked holdout partitions without shared authors or conversations.
	2. Rebuild context-matched Layer 1 inputs and train the LSTM using the valid conversation target only.
	3. Compare the matched LSTM, weighted scorer, raw Layer 1, and keyword baselines under one predeclared validation and final-test protocol.

## 1.4 Scope and Limitations

### 1.4.1 Scope of the Study

The corrected study includes a matched comparison among the LSTM, a seven-feature weighted scorer, the raw Layer 1 proxy, and a static keyword baseline. Every method will use the same eligible conversations, conversation endpoint, connected-author partitions, and predeclared validation procedure. No performance improvement is claimed before the locked final test is completed.

The proposed prototype is platform-independent and intended for possible future adaptation into chat-based moderation workflows. Rather than replacing existing moderation mechanisms, it is designed as a research prototype for studying contextual analysis and behavioral pattern tracking.

The prototype uses natural language processing and machine learning techniques to analyze ordered conversation records through an offline, turn-by-turn replay. This controlled replay demonstrates how a sequence score changes as additional turns are supplied; it is not a live moderation deployment or a validated safety determination.

PAN12 is the only currently eligible large corpus for the corrected primary experiment. The locally generated synthetic conversations remain annotation candidates and are excluded from training, validation, and testing until independent review and adjudication are completed. No separate real, message-annotated study dataset is presently evidenced. Consequently, the current experiment does not establish performance on contemporary Philippine slang, Filipino or Taglish communication, or newly developed obfuscation methods.

__1.4.2 Limitations of the Study__

This study is limited to the development of a prototype moderation module and does not involve full deployment in a live chat environment. The scope is further limited to grooming-related interactions. As such, the module will not be tested with real users, and its performance is evaluated only through controlled datasets and simulations.

The study is limited to English-language chat data. It includes no Filipino- or Taglish-language corpus, Philippine annotator study, locally calibrated threshold, or Philippine subgroup evaluation. Philippine relevance is therefore a motivation and intended area of application, not an empirical localization claim.

The study builds upon pre-trained machine learning models and libraries. The preserved fine-tuned Layer 1 checkpoint is retained only as a historical proxy because its recovered target is not valid grooming-message truth. Corrected training, target provenance, and context-matched inference are therefore required before an end-to-end performance claim.

Additionally, the evaluation is conducted through controlled offline replay rather than a live deployment. The study does not test live users, platform integration, latency, throughput, scalability, moderator workload, intervention efficacy, or real-world data drift. It also does not account for all variations in language, cultural context, or evolving evasion techniques.

## 1.5 Significance of the Study

This section explains the importance and potential impact of the research, identifying key beneficiaries and contributions across multiple domains.

### 1.5.1 Academic Contribution

This research contributes to the academic field of computer science, artificial intelligence, and cybersecurity by advancing the understanding of AI-driven content moderation. The proposed approach bridges a gap in existing literature by demonstrating how machine learning and natural language processing can be combined with behavioral pattern analysis to detect nuanced forms of harmful communication. 

This work provides a framework for contextual analysis in chat moderation that goes beyond traditional keyword-based approaches. The findings will be valuable for researchers exploring AI applications in safety and security, offering insights into feature extraction techniques, model architecture, and evaluation methodologies for detecting complex communication patterns. 

Additionally, this study contributes to theoretical knowledge in understanding grooming-related interactions in digital environments.

### 1.5.2 Industry and Practical Applications

For the technology industry and online platform providers, this research defines an auditable prototype and evaluation protocol that may inform future safety tooling after independent validation.

If later validated in the intended domain, this line of research could support moderator triage by prioritizing conversations for human review. The present prototype does not establish reduced moderator workload, earlier intervention, or production-time performance.

Compatibility with existing moderation workflows is a future engineering question. The present work does not establish integration effort, scalability, operational reliability, user trust effects, or legal-risk reduction.

### 1.5.3 Societal Benefits

Beyond academia and industry, the study addresses a socially important safety problem. Online harassment and grooming pose serious threats to user well-being, particularly for children, adolescents, and people with limited digital literacy. The present prototype does not demonstrate reduced harm; it contributes a more explicit research protocol for evaluating a possible future moderator-support approach.

In the Philippine context, the study is motivated by the need for stronger online child-safety research and moderator decision support. However, the current English PAN12-based evaluation is not a localized Philippine validation. A Philippine deployment claim would require appropriately governed Filipino and Taglish data, local expert review, subgroup analysis, threshold calibration, and field evaluation.

Whether a later validated system would be affordable or usable for smaller platforms remains to be evaluated through deployment, cost, workload, and stakeholder studies.

### 1.5.4 Implications for Future Research

This research establishes a foundation for future investigations into AI-powered moderation systems and behavioral analysis in digital communication. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media. 

Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy. Future research can also explore the integration of multimodal analysis (text, images, video) for comprehensive content moderation. 

The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field.

### 1.5.5 Sustainable Development Goal (SDG) Contribution

This study supports Sustainable Development Goal 9 (Industry, Innovation and Infrastructure) through the development of an AI-driven moderation prototype that applies machine learning and natural language processing techniques to enhance digital communication safety systems. The study also supports Sustainable Development Goal 16 (Peace, Justice and Strong Institutions) by contributing to safer online environments through improved detection of grooming-related interactions and harmful communication patterns. By augmenting existing moderation systems with contextual and behavioral analysis, the proposed approach aims to support more secure and responsible digital communication platforms.

## 1.6 Definition of Terms

Artificial Intelligence (AI) - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

Behavioral Pattern Analysis - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

Chat Moderation System - An automated or semi-automated system designed to support the monitoring, filtering, or review of user communications. In this study, the term refers to an offline research prototype rather than a deployed platform service.

Contextual Analysis - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

Grooming - A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower their defenses and facilitate exploitation or abuse.

Machine Learning - A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task.

Natural Language Processing (NLP) - A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner.

Obfuscation Techniques - Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword-based filters.

Online Grooming Discourse Model (OGDM) - The core theoretical framework used in this study that explains online grooming as a non-linear process of communicative actions, such as trust-building and isolation.

Predatory Behavior - Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals.

Offline Sequential Replay - The chronological processing of a stored or manually entered conversation one turn at a time in a controlled local environment. It demonstrates sequence-processing mechanics but does not establish production latency or real-time deployment capability.

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

This study uses OGDM as an interpretive framework for contextual review. The seven implemented trajectory features are computational sequence signals, not direct annotations or validated measurements of individual OGDM communicative processes.

# III. METHODOLOGY

## 3.1 Research Design

This study employs a developmental and experimental research design. It develops an offline conversation-trajectory prototype and defines a corrected evaluation protocol for a sequence model and its baselines. Because the available PAN12 training corpus does not provide genuine message-level grooming labels, the proposed defensible primary endpoint is conversation-level identification of conversations containing a PAN12-listed predator. This scope remains subject to adviser approval; message-level grooming detection is retained as a later extension requiring independently reviewed labels.

The prototype consists of four stages: (1) corpus and label-provenance audit, (2) turn-level representation with DistilBERT-derived inputs, (3) chronological trajectory modeling with a Long Short-Term Memory (LSTM) network, and (4) matched conversation-level comparison against prespecified baselines. The LSTM processes ordered feature vectors across turns. Until corrected training and evaluation are completed, its output is described as a development sequence score rather than a validated grooming-risk probability.

Rather than replacing existing moderation systems, the proposed approach is intended as human-in-the-loop research and potential future decision support. Any claim that contextual and behavioral analysis improves detection will be made only after the corrected protocol uses valid targets, matched comparators, validation-only selection, and a locked final test.

The corrected primary experiment will be validated offline using PAN12-derived data. The synthetic files are excluded pending independent review, and no separate real message-annotated dataset is currently eligible. Performance will be reported with precision, recall, false-negative rate, F1, F0.5, ROC-AUC, confusion counts, and first-threshold-crossing turn, together with the exact split, threshold, and artifact provenance.

## 3.2 Relevant Technology

### 3.2.1 Python Programming Language

Python is used as the primary programming language for the development and evaluation of the proposed moderation module. It was selected due to its extensive support for machine learning, natural language processing, and data analysis through established libraries and frameworks.

### 3.2.2 Hugging Face Transformers and PyTorch

The study utilizes the Hugging Face Transformers library together with the PyTorch deep learning framework for model training and inference. These technologies provide pre-trained transformer architectures and efficient tools for fine-tuning NLP models for text classification tasks.	

### 3.2.3 DistilBERT

DistilBERT supplies two distinct components in the prototype: a base encoder used to obtain turn embeddings and a separate preserved sequence-classification checkpoint used to obtain a scalar historical proxy. DistilBERT can represent contextual text beyond exact keyword matching, but suitability for the corrected endpoint must be established empirically; the preserved checkpoint is not treated as a validated grooming classifier.

### 3.2.4 Development Environment

The prototype is developed and tested in a Python environment using Visual Studio Code and command-line scripts. Table 3.1 records the environment observed for the current rerun and demonstration workspace on 12 August 2026. These versions support reproducibility of the present code state but are not claimed as the unrecoverable exact environment of the historical Layer 1 training run.

| Component | Observed version |
|---|---|
| Python | 3.12.5 |
| PyTorch | 2.11.0+cu128 |
| Transformers | 4.57.3 |
| Accelerate | 1.13.0 |
| Datasets | 4.8.5 |
| scikit-learn | 1.6.1 |
| NumPy | 2.2.3 |
| pandas | 2.2.3 |
| SciPy | 1.15.2 |
| Flask | 3.1.2 |

*Table 3.1. Current Rerun and Demonstration Environment Snapshot*

## 3.3 Data Collection and Processing

### 3.3.1 Data Collection

The PAN12 Sexual Predator Identification training corpus is the only currently eligible large corpus for the corrected primary experiment. It supplies an official list of predator authors. A conversation-level target can therefore be derived as positive when at least one participant is on that list. PAN12 does not provide message-level grooming labels for training.

The project also contains synthetic grooming and safe conversations. Their labels were generated from speaker roles or scenario prompts rather than independent message review, so both sources are excluded from training, validation, and testing pending two independent reviews and adjudication. The previously described “Study Dataset (provided)” could not be substantiated and has been removed. Table 3.2 distinguishes inventory, label provenance, and eligibility rather than combining unlike labels under one generic field.

| Resource | Source | Inventory or analysis unit | Label provenance | Current status and permitted use |
|---|---|---:|---|---|
| PAN12 training corpus | PAN-CLEF 2012 [13] | 378,023 rows; 27,353 conversations; 41,892 author IDs before eligibility filtering | Official predator-author list; project-derived correction/diff-membership column | Predator-author labels may derive the proposed conversation target. PAN `is_suspicious` is excluded from message-level supervision. |
| PAN12 two-author Layer 2 subset | Derived from the PAN12 training corpus | 18,568 assigned conversations; 219,019 assigned message rows | Conversation target derived from presence of a PAN-listed predator author | Eligible for the proposed connected-author conversation experiment after all training-only artifacts are rebuilt. |
| PAN12 Problem 2 judgments | PAN-CLEF 2012 [13] | 6,478 judged conversation-line pairs across 834 test conversations | Pooled test-line judgments, primarily from a single trained expert | Potential frozen external evaluation only; currently blocked because the matching test XML/text is absent. |
| Synthetic grooming conversations | Local generator | 739 messages; 60 conversations | Generated speaker role copied into both label columns | Excluded pending independent message review and adjudication. |
| Synthetic safe conversations | Local generator | 596 messages; 56 nonempty conversations | Scenario-derived all-zero labels | Excluded pending independent message validation. |
| Independent annotation worksheet | Project audit artifact | 1,335 candidate rows; 0 approved rows | Two-reviewer, OGDM-guided annotation fields | Annotation has not begun; not eligible for training, validation, or testing. |

*Table 3.2. Dataset Inventory, Label Provenance, and Eligibility Status*

The label fields are not interchangeable. Table 3.3 gives their operational meaning and permitted interpretation.

| Field or target | Level | Actual meaning | Permitted interpretation |
|---|---|---|---|
| PAN `is_predator` | Author-derived value carried on message rows | The author appears in PAN12's official predator list | Valid for listed-predator author identification and deriving a conversation target; not a message-behavior label. |
| `conversation_contains_listed_predator` | Conversation | At least one participant is PAN-listed | Proposed defensible primary endpoint, subject to adviser approval. |
| PAN `is_suspicious` | Message row | The row is associated with PAN correction/diff metadata | Never grooming-message or onset ground truth; excluded from labels, losses, tuning, and performance claims. |
| Synthetic `is_suspicious` | Message row | Generated speaker role or scenario-wide zero | Weak proxy only; excluded pending independent review. |
| Human-reviewed OGDM label | Current message with preceding context | Observable grooming-related behavior under an approved rubric | Pending; no approved rows currently exist. |

*Table 3.3. Label Provenance and Allowed Interpretation*

### 3.3.2 Data Preprocessing

Preprocessing first preserves source identity, stable conversation and line identifiers, author identifiers, and chronological order. CSV repair is limited to schema recovery and standards-compliant quoting where embedded commas would otherwise shift columns. The current implementation does not justify a claim that all obfuscated language is normalized.

The base DistilBERT encoder and the recovered Layer 1 trainer tokenize inputs with a maximum sequence length of 128 tokens. The recovered trainer constructs each Layer 1 input from the current message and up to two preceding messages separated by `[SEP]`; the same context construction must be used during corrected inference and cache generation.

For the local demonstration interface, common direct identifiers are masked with typed placeholders before model input or in-memory retention. This automated rule-based control covers categories such as email addresses, telephone numbers, URLs, IP addresses, social handles, coordinates, and long numeric identifiers. It cannot reliably recognize every personal name, free-form street address, or indirect identifier; manual review remains necessary for research datasets. Historical corpora and checkpoints predate this interface safeguard and are not claimed to have been retroactively sanitized by it.

At the conversation level, rows are grouped by stable conversation ID and sorted by their original line order. Sequential snapshots contain the complete prefix up to the current turn. The corrected experiment will freeze connected-author partitions before fitting, downsampling, centroid construction, cache generation, threshold selection, or any other learned preprocessing step.

### 3.3.3 Data Processing

Processed records use an auditable structure containing dataset source, stable conversation ID, original message order, participant ID, message text, and separate provenance-bearing label fields. The corrected pipeline must not silently map generic fields such as `label`, `warning`, or `suspicious` into one training target. PAN correction/diff membership may be retained only as audit metadata, while synthetic proxy labels remain quarantined from eligible splits.

Machine-readable manifests record source paths, hashes, row and conversation counts, schemas, label origins, review status, and inclusion decisions. Any future reviewed or externally acquired data must preserve its original label taxonomy and pass licensing, ethics, overlap, and split audits before use.

### 3.3.4 Feature Engineering

Two DistilBERT components serve distinct functions. The base `distilbert-base-uncased` encoder supplies a 768-dimensional CLS embedding $e_t$ for the current turn. A separate fine-tuned sequence-classification checkpoint supplies a scalar Layer 1 proxy $p_t \in [0,1]$. Because the historical checkpoint's target is not valid message-level grooming truth, $p_t$ is not interpreted as a calibrated probability of grooming or predatory content.

Seven deterministic trajectory features are computed from the prefix ending at turn $t$. Let $p_i$ be the Layer 1 proxy for turn $i$, $e_t$ the base-encoder embedding for the current turn, $\mu_B$ a benign centroid computed from training-partition records only, and $n_a(t)$ the number of turns contributed by author $a$ through turn $t$. The two most active authors form the dominant dyad for the imbalance calculation.

| Feature | Operational definition | Range and implementation detail |
|---|---|---|
| Current score | $p_t$ | $[0,1]$; Layer 1 proxy, not a validated grooming probability. |
| Peak score | $\max_{i\leq t}p_i$ | $[0,1]$; retains the highest proxy observed in the prefix. |
| Spike count | $\sum_{i\leq t}\mathbf{1}[p_i>\tau_s]$ | 0 to the number of turns; the current development default is $\tau_s=0.5$. |
| Spike-then-drop | 1 if any adjacent pair satisfies $p_{i-1}>\tau_s$ and $p_i<p_{i-1}-\delta$; otherwise 0 | Binary; the current development default is $\delta=0.2$. |
| Rate of change | $p_t-p_{t-1}$ | $[-1,1]$; defined as 0 for the first turn. |
| Topic drift | $1-\cos(e_t,\mu_B)$ | Theoretical range $[0,2]$; the final centroid must be fitted and documented from training data only. |
| Turn-taking imbalance | $\lvert n_{a_1}(t)-n_{a_2}(t)\rvert/[n_{a_1}(t)+n_{a_2}(t)]$ | $[0,1]$; counts turns, not words, and is 0 until two authors are present. |

*Table 3.4. Implemented Trajectory Features Per Conversation Prefix*

The current historical LSTM receives the 768-dimensional base embedding concatenated with these seven values, or 775 inputs per turn. The current weighted scorer receives only the seven trajectory values. Therefore, the historical comparison cannot isolate sequence modeling from unequal input information. In the corrected experiment, the primary architecture comparison will give the LSTM and weighted scorer the same seven inputs; the 775-input LSTM will be reported separately or with matched embedding ablations. The current implementation does not standardize the seven trajectory values, so no scaling claim is made.

### 3.3.5 Data Splitting

Ordinary conversation-level splitting is insufficient because the same author can participate in several conversations. The corrected protocol constructs a graph in which conversations are connected when they share a dataset-namespaced author identifier. Entire connected-author components are then assigned to training, validation, or test partitions, producing zero shared conversations and zero shared authors across partition pairs.

The training partition alone is used for parameter fitting, negative downsampling, score-cache generation, and benign-centroid construction. The validation partition is used for architecture and hyperparameter selection and for independently selecting a threshold for each learned method under one predeclared rule. The final test partition is evaluated once after code, features, checkpoints, thresholds, comparators, and reporting rules are frozen.

The previously displayed development test has already been inspected and is preserved as historical evidence only. Before the corrected experiment, a new connected-author holdout should be locked from component groups whose outcomes have not been used for selection. If the earlier test must be reused because of the deadline, the result will be disclosed as a corrected retrospective evaluation rather than a pristine confirmatory test.

## 3.4 Model Development

### 3.4.1 Layer 1 DistilBERT Components and Required Correction

The preserved Layer 1 component is a `DistilBertForSequenceClassification` checkpoint. Its recovered trainer uses the current message plus up to two preceding messages, a maximum token length of 128, the default two-class sequence-classification cross-entropy objective, retention of all positive rows, and negative downsampling rather than the previously stated class-weighted loss. It used an ordinary conversation-grouped split, not the corrected connected-author split.

The active historical checkpoint was most likely trained against the project's PAN `is_suspicious` field. The corpus documentation and preprocessing code confirm that this field represents correction/diff membership rather than message-level grooming. Its scalar output is therefore retained only as a historical trajectory proxy and is not called a grooming probability. The current live demo also supplies isolated messages rather than the checkpoint's current-plus-two-prior-message training input, so its displayed value is a mechanism demonstration only.

For a conversation-level final endpoint, Layer 1 must be rebuilt on the training partition only using an explicitly disclosed author-derived proxy, with identical context construction during training and inference. If the thesis retains a genuine message-level grooming endpoint, Layer 1 instead requires independently reviewed and adjudicated message labels; no approved rows currently exist.

### 3.4.2 LSTM-Based Trajectory Scoring Model

The LSTM processes an ordered sequence of turn-level feature vectors and returns a development sequence score for each prefix. The historical model used both a turn-level loss derived from invalid PAN diff membership and a conversation-level max-over-turn loss derived from whether the conversation contained a listed predator. That run is retained only as a diagnostic and not as final grooming-detection evidence.

The corrected LSTM will use the valid conversation target only; the invalid turn loss will be disabled rather than merely assigned a smaller weight. The benign centroid and every cached upstream score will be rebuilt from the appropriate training partition with stable row keys and recorded hashes. During offline replay, the first turn whose score exceeds the method's validation-selected threshold is recorded as the first-threshold-crossing turn. It is not interpreted as delay from grooming onset because PAN12 supplies no training onset annotations.

### 3.4.3 Baseline Comparison Model

The corrected comparison includes: (1) the existing static keyword-lexicon baseline, (2) the raw Layer 1 proxy aggregated to the conversation level and assigned its own validation-selected threshold, (3) the seven-feature weighted scorer with weights and threshold selected on the same validation endpoint, and (4) a seven-feature LSTM as the matched primary architecture comparison. A 775-input LSTM may be reported as a separate enhanced model. All methods use the same conversation endpoint and final partition. The current keyword implementation is a hand-written static lexicon; it is not described as term-frequency-derived from PAN12.

## 3.5 Evaluation/Validation

### 3.5.1 Endpoint, Metrics, and Threshold Selection

Subject to adviser approval, the evaluation unit is a conversation and the positive class is `conversation_contains_listed_predator`. For a turn-scoring method, the conversation score is the maximum score over its prefixes. At a selected threshold, true positives (TP), false positives (FP), true negatives (TN), and false negatives (FN) are counted on the same partition for every method.

The study reports the following definitions: precision $=TP/(TP+FP)$; recall $=TP/(TP+FN)$; false-negative rate $=FN/(TP+FN)$; $F_1=2PR/(P+R)$; and $F_{0.5}=(1+0.5^2)PR/(0.5^2P+R)$. ROC-AUC is computed from continuous conversation scores and reported only when both classes are present. Confusion counts accompany every rate so that class imbalance remains visible.

Each learned method receives an independently selected validation threshold. One selection rule—such as maximizing $F_{0.5}$ or maximizing recall subject to an approved precision floor—must be approved and recorded before the locked test is opened; this decision is not yet finalized. The same rule is then applied to all learned comparators. No threshold or model choice is changed after viewing final-test performance.

For positive conversations, first-threshold-crossing turn is the earliest prefix that exceeds the selected threshold. The study reports the distribution and mean only among correctly flagged positive conversations, together with the number never flagged. This quantity is not “time from grooming onset.”

### 3.5.2 Testing, Robustness, and Statistical Comparison

The corrected test is run once on the locked connected-author holdout after the full pipeline is frozen. All methods receive the same eligible conversations, ground-truth endpoint, and reporting code. The matched seven-feature comparison is the basis for an architecture claim; unequal-input models are labeled separately.

Robustness to obfuscation, coded slang, and contemporary Philippine language remains planned rather than completed because no frozen, independently labeled challenge set is currently available. Such a test will be reported only after its cases, labels, and inclusion rules are fixed without reference to model scores.

If sample size and paired discordant predictions permit, McNemar's exact test will compare the final binary errors of two methods on the same conversations. Confidence intervals and the full paired contingency table will accompany any significance statement. Until the corrected experiment is completed, no claim that the LSTM outperforms the weighted scorer, raw Layer 1, or keyword baseline is made.

## 3.6 Ethical Considerations

The study handles sensitive sexual-safety data under data-minimization and human-oversight principles. The local demonstration applies deterministic masking of common direct identifiers before model input and in-memory retention, uses server-generated opaque conversation IDs, binds to the local machine, and sends no-store response headers. The interface does not intentionally persist messages. Automated masking is a safeguard, not a guarantee of complete anonymization: personal names, free-form addresses, and indirect identifiers can evade pattern rules and still require manual review.

The PAN12 corpus is a public research resource with source-side anonymization practices, but this does not prove that every free-text identifier is absent. Historical datasets and trained artifacts predate the newly added demonstration safeguard. Any future training export must undergo a separate documented redaction and manual verification stage before processing. Raw sensitive records must not be uploaded to external AI services without explicit ethical, licensing, and institutional authorization.

The study does not involve direct interaction with real users. The current prototype is evaluated only through local offline replay. Synthetic conversations are retained as audit and annotation candidates, not as validated evidence, until independent review and adjudication are complete.

The moderation module is designed as a support tool for human moderators rather than an autonomous decision-making mechanism. Flagged conversations are intended for human review before any moderation action is taken, preserving human oversight and reducing the risk of algorithmic harm to falsely flagged users.

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
