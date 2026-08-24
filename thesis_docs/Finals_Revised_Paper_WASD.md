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

The rapid growth of online multiplayer games and interactive digital platforms has made real-time chat a primary channel for collaboration, social interaction, and community building. These environments also create opportunities for grooming-related interactions and other harmful conduct to develop across sustained conversations [1], [2], [3]. Many moderation systems continue to rely on keyword filtering and user reports, which remain useful first-line controls but are often insufficient for complex, context-dependent threats [4], [5].

Traditional moderation methods primarily detect explicit terms or predefined patterns. They can identify straightforward violations such as profanity, yet altered spellings, special characters, coded language, and other obfuscation techniques can bypass static rules [6], [7], [8]. More importantly, an ordinary-looking message may acquire a different meaning when interpreted with surrounding turns, speaker behavior, and the progression of the interaction [2], [9]. Reliance on user reporting is also reactive and may delay review of interactions that do not contain immediately obvious violations [5].

A central challenge is therefore the number of harmful or concerning interactions that conventional systems may miss. In a safety-oriented moderation setting, false negatives are especially important because every missed conversation represents an interaction that receives no timely review. Improving detection coverage requires methods capable of combining local language context with evidence that develops across multiple turns.

Advances in machine learning and natural language processing provide a practical basis for moving beyond isolated-message filtering [9], [10]. Transformer models can represent a message in relation to its preceding context, while sequence models can learn how scores and behavioral indicators change over time. Together, these techniques support a moderation architecture that analyzes both what is being communicated and how the interaction develops.

This study develops an AI-powered moderation module that combines contextual language analysis with behavioral trajectory modeling. Layer 1 uses DistilBERT to evaluate the current turn together with up to two preceding turns. Layer 2 uses an LSTM to aggregate a chronological sequence of seven trajectory features reflecting score level and change, semantic movement, and speaker-turn structure. The module is designed to complement keyword filters and reporting mechanisms by prioritizing conversations that warrant human review.

The primary empirical evaluation uses the PAN-2012 Sexual Predator Identification corpus because it provides large-scale chronological conversations, persistent speaker identifiers, and an official predator-author list [13]. For measurement, a positive case is operationalized as a dyadic conversation containing at least one officially listed predator author. This author-derived endpoint supplies reproducible supervision for evaluating the complete architecture, while the system's broader research purpose remains the contextual and behavioral detection of grooming-related interactions. The endpoint does not imply that every turn written by a listed author contains grooming behavior.

By developing and evaluating a complete two-layer prototype, the study investigates whether contextual and behavioral sequence analysis can reduce the interactions missed by conventional moderation approaches. It also contributes to Sustainable Development Goal 9 through innovation in AI-assisted digital-safety infrastructure and to Sustainable Development Goal 16 by supporting more accountable and responsive mechanisms for identifying potentially harmful online interactions.

## 1.2 Statement of the Problem

Existing chat moderation systems are widely used, yet grooming-related and other harmful interactions persist [1], [2], [3]. Keyword-based filters, rule-based systems, and user-reporting mechanisms are effective for explicit and readily recognizable violations, but they are less capable of handling communication whose meaning depends on conversational context and behavioral progression [4], [5], [9].

The research problem addressed by this study is how an AI-powered moderation module can combine natural language processing, contextual analysis, and behavioral trajectory modeling to identify concerning interactions that static or isolated-message approaches may miss. The study develops a complete two-layer architecture and evaluates whether recurrent aggregation of chronological evidence improves detection coverage, particularly recall and false-negative reduction.

This study seeks to answer the following questions:

1. How effective are existing chat moderation systems in detecting grooming-related interactions?
2. What are the limitations of keyword-based and rule-based moderation approaches in handling context-dependent communication?
3. How can machine learning and natural language processing be utilized to analyze behavioral patterns and conversational context in chat systems?
4. To what extent can an AI-driven moderation module improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

For quantitative evaluation, these questions are operationalized using the PAN12 author-derived conversation endpoint and a set of controlled comparison methods: a training-derived keyword rule, maximum Layer 1 proxy aggregation, a validation-fitted weighted trajectory scorer, and LSTM-based sequence models. Accordingly, the reported metrics establish performance for that conversation-level endpoint rather than exhaustive message-level grooming classification or grooming-onset detection.

## 1.3 Objectives of the Study

__General Objective:__ Develop an AI-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming-related interactions in chat environments.

- __Specific Objective:__
	1. Evaluate the limitations and effectiveness of existing keyword-based and rule-based chat moderation systems in handling context-dependent communication.
	2. Design and develop an AI-based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions.
	3. Assess the improvement in detection performance of the proposed AI-driven module, specifically focusing on the reduction of false negatives compared to traditional keyword-based and report-driven approaches.

## 1.4 Scope and Limitations

### 1.4.1 Scope of the Study

The study covers the design, implementation, and comparative evaluation of an AI-powered moderation module that combines contextual message analysis with behavioral trajectory modeling. The prototype is intended to augment, rather than replace, keyword filters, user reports, and human moderation by assigning conversation-level scores that can help prioritize review.

The completed architecture contains two learned layers. Layer 1 uses a context-conditioned DistilBERT classifier to produce an author-derived proxy score for each turn. Layer 2 analyzes the chronological sequence of seven trajectory features using an LSTM. The system also includes an offline sequential-replay interface through which stored or locally entered messages can be assessed turn by turn.

The primary experiment uses eligible dyadic conversations from the PAN12 training corpus. After the required validity and conversation-structure checks, the candidate pool contains 18,567 conversations and 218,114 turns. The official predator-author list is the sole source of primary supervision: Layer 1 uses current-author membership as weak supervision, while Layer 2 uses the derived conversation-level endpoint.

The study compares the proposed seven-feature LSTM with a training-derived keyword rule, maximum Layer 1 proxy aggregation, and a validation-fitted weighted trajectory scorer. A secondary LSTM supplemented with 768-dimensional base DistilBERT embeddings is evaluated separately. All methods are tested on identical author-disjoint conversation partitions, with particular attention to recall, false negatives, PR-AUC, F0.5, and paired performance differences.

### 1.4.2 Limitations of the Study

PAN12 does not provide exhaustive grooming labels for every training message. The author-derived Layer 1 target is therefore a weak proxy: a turn written by a listed author is positive for the training target even when its isolated wording is ordinary. The primary experiment consequently evaluates conversation-level predator-author presence and does not claim validated grooming-message classification, grooming-stage recognition, or true grooming-onset detection.

The primary evaluation does not include the project's locally generated synthetic conversations or other unreviewed candidate datasets. It also does not establish coverage of contemporary gaming slang, newly developed obfuscation strategies, Filipino or Taglish communication, or external platforms. PAN12 was processed as supplied; no independent English-language filter was used.

The prototype operates through controlled offline sequential replay and was not tested with real users or integrated into a live platform. Production latency, throughput, scalability, moderator outcomes, fairness, privacy performance, and autonomous enforcement remain outside the completed evaluation. Its present role is an experimentally evaluated moderation module and a basis for future human-review integration.

The system builds upon pretrained language models and a dyadic conversation design. Its performance is therefore influenced by the limitations of those models, the age and composition of PAN12, class imbalance, and the extent to which the selected trajectory features represent behavior in other environments.

## 1.5 Significance of the Study

This section explains the academic, practical, societal, and future-research value of the proposed AI-powered moderation module.

### 1.5.1 Academic Contribution

This research contributes to computer science, artificial intelligence, cybersecurity, and online-safety research by demonstrating how contextual natural language processing can be integrated with behavioral trajectory analysis in a complete moderation architecture. Rather than reducing an interaction to isolated keywords or a single message score, the proposed system represents how evidence evolves across an ordered conversation.

The study contributes a two-layer design consisting of a context-conditioned DistilBERT classifier, seven interpretable trajectory features, and recurrent LSTM aggregation. The matched comparison between the seven-feature LSTM and a weighted scorer receiving the same information provides direct empirical evidence that learned sequence modeling adds predictive value beyond static feature combination. The primary LSTM's improvements in recall and false-negative reduction also address the study's central safety-oriented performance objective.

The research additionally contributes a reproducible evaluation framework for conversational data: connected-author partitioning, training-only construction of derived resources, validation-only model and threshold selection, a locked final test, and component-grouped uncertainty estimation. These controls strengthen the reliability of the reported findings and provide a foundation for future studies of contextual and behavioral moderation.

### 1.5.2 Industry and Practical Applications

For chat platforms, gaming communities, social networks, and collaborative systems, the research demonstrates a practical architecture for augmenting existing moderation workflows. The module combines contextual language processing with an auditable sequence representation, allowing its trajectory features and conversation scores to be inspected rather than functioning only as an opaque end-to-end decision.

The approach is particularly relevant to human-review workflows in which limited moderation resources must be directed toward conversations most likely to require attention. Its modular design allows keyword rules, contextual classifiers, trajectory models, and human escalation policies to operate as complementary safeguards rather than mutually exclusive alternatives.

The completed prototype establishes technical feasibility in controlled offline evaluation. Adaptation to a specific platform would still require representative local data, calibration, privacy and fairness assessment, performance engineering, and evaluation with actual moderators; these are deployment requirements rather than limitations on the architectural contribution demonstrated here.

### 1.5.3 Societal Benefits

Online grooming and related forms of exploitation pose serious threats to user well-being, particularly for children, adolescents, and users with limited digital literacy. By improving the ability of a moderation system to identify conversations missed by static keyword rules, this study contributes to the development of more responsive digital-safety tools.

The proposed module is not presented as an autonomous judge or as proof of real-world harm prevention. Its societal value lies in strengthening the technical basis for human-reviewed detection, increasing attention to false negatives, and supporting future platform-specific systems that can intervene more consistently in concerning interactions.

The architecture and evaluation process can also provide a starting point for organizations with limited moderation resources, provided that any adaptation is accompanied by appropriate governance, representative data, and qualified human oversight.

### 1.5.4 Implications for Future Research

This research establishes a foundation for future investigations into AI-powered moderation systems and behavioral analysis in digital communication. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media.

Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy. Future research can also explore the integration of multimodal analysis (text, images, video) for comprehensive content moderation.

The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field.

### 1.5.5 Sustainable Development Goal (SDG) Contribution

This study supports Sustainable Development Goal 9 (Industry, Innovation and Infrastructure) through the development of an AI-driven moderation prototype that combines machine learning, natural language processing, and behavioral trajectory analysis to advance digital-safety infrastructure. It also supports Sustainable Development Goal 16 (Peace, Justice and Strong Institutions) by contributing a reproducible method for improving the identification and human review of potentially harmful online interactions. The study's empirical claims are bounded to its PAN12 evaluation, while its architectural and methodological contributions provide a basis for broader future adaptation.

## 1.6 Definition of Terms

Artificial Intelligence (AI) - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

Behavioral Pattern Analysis - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

Chat Moderation System - An automated or semi-automated system designed to monitor, prioritize, filter, or regulate user communications in chat environments to reduce harmful interactions and support moderator action.

Contextual Analysis - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

Conversation-Level Endpoint - The primary measurable outcome used in the experiment: whether a dyadic PAN12 conversation contains at least one author included in the official predator-author list.

Grooming - A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower the target's defenses and facilitate exploitation or abuse.

Machine Learning - A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task.

Natural Language Processing (NLP) - A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner.

Obfuscation Techniques - Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword-based filters.

Online Grooming Discourse Model (OGDM) - The principal theoretical framework used to understand grooming as a non-linear network of communicative processes, including deceptive trust development, sexual gratification, compliance testing, and isolation. In this study, OGDM informs the rationale and hypotheses behind cross-turn trajectory analysis; the implemented features are theoretically informed indicators rather than independently validated OGDM-stage labels.

Predator-Author Proxy Score - The Layer 1 output learned from official predator-author membership under the available message context. It is an intermediate signal for conversation modeling and is not treated as a validated probability that an individual message contains grooming behavior.

Predatory Behavior - Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals.

Offline Sequential Replay - The controlled processing of stored or locally entered messages in chronological order to simulate turn-by-turn analysis. It does not constitute a live platform deployment or establish production latency, scalability, or integration performance.

User Reporting Mechanism - A system feature that allows chat-platform users to report suspicious, harmful, or policy-violating behavior to moderators or automated systems for review and action.

# II. RELATED WORK

This chapter reviews and synthesizes literature and empirical studies concerning AI-based chat moderation, online grooming detection, contextual natural language processing, and behavioral analysis. It examines why isolated keywords and individual messages are insufficient for interactions whose meaning and risk emerge over multiple turns.

The chapter establishes the scholarly and theoretical foundation for the proposed two-layer moderation module. It connects contextual transformer modeling, behavioral-feature research, sequence learning, and the Online Grooming Discourse Model to the study's design, while distinguishing that broader research foundation from the author-derived PAN12 endpoint used for empirical evaluation.

## 2.1 Review of Related Literature

Recent research in chat moderation has shifted from traditional rule-based filtering toward AI-driven contextual analysis models. Earlier moderation approaches relied primarily on keyword blacklists to detect violations such as profanity or explicit harmful language. However, these systems are limited in their ability to interpret conversational intent, allowing malicious users to bypass filters through techniques such as altered spellings, coded language, or multi-message grooming strategies.

Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. Schurger-Foy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history. Similarly, Yang et al. [6] introduced the ToxBuster architecture, which incorporates message history and speaker metadata into text classification models. Their results showed significant improvements in detection accuracy, achieving up to 95% precision in identifying harmful interactions through sequence-based moderation rather than single message evaluation.

These findings suggest that integrating conversational context and historical behavioral patterns improves moderation effectiveness compared to static filtering methods. Transformer-based NLP architectures such as BERT, RoBERTa, and DistilBERT have consequently emerged as standard tools for understanding linguistic patterns in chat environments. 

Furthermore, longitudinal behavioral analysis has been shown to be a strong predictive indicator of future harmful activity. Studies indicate that tracking interaction patterns over time can achieve up to 74% balanced accuracy in forecasting future toxic behavior, reinforcing the importance of behavioral modeling in proactive moderation systems. 

Despite these advancements, current moderation systems remain constrained by their reliance on legacy datasets such as PAN12, which may not adequately represent modern online communication styles, slang, or evolving evasion techniques used by malicious actors. 

## 2.2 Related Studies

Several empirical studies have explored the application of artificial intelligence to grooming-related interactions and other context-dependent harms in online environments.

The empirical study of automated grooming detection is anchored in the PAN-2012 Sexual Predator Identification task introduced by Inches and Crestani [13]. PAN12 defined two related tasks: identifying predators among conversation participants and identifying lines considered most characteristic of predatory behavior. The present study uses the official predator-author list as its verified source of supervision and derives a conversation-level endpoint from author presence. The separate distinctive-line task is not treated as an exhaustive set of grooming-message labels for the training conversations used here.

PAN12 is particularly valuable to the present research because its scale, chronological message order, and persistent speaker identifiers support both trajectory construction and connected-author evaluation. These properties allow the study to examine behavioral progression across turns while testing generalization to conversations involving unseen authors.

Building on the benchmark, Villatoro-Tello et al. [14] proposed a two-step approach that first separates predatory from non-predatory participants and then identifies the most suspicious users. Their method combines content-based evidence with behavioral features such as the proportion and pattern of a user's interventions. Its strong PAN12 performance demonstrates that participation and interaction structure, not message content alone, carry discriminative signal for predator identification. This finding directly motivates the proposed combination of contextual language analysis and behavioral trajectory features.

Street et al. [2] developed a transformer-based classification approach using BERT and RoBERTa to identify online grooming interactions by analyzing conversational roles between adults and minors. Their contextual determination framework improved cross-dataset robustness in identifying suspicious communication patterns across multiplayer gaming chats.

Faraz et al. [3] proposed *Protectbot*, an AI-based chatbot that actively simulates user interaction to expose predatory intent. Using DialoGPT together with intent classifiers such as fastText and Support Vector Machines, the system reported an __F__-__score of 0.99__ for detecting grooming behavior in its simulated chat environment.

Tereshchenko and Hamalainen [5] compared language-model approaches for real-time moderation and highlighted the tradeoff between linguistic capability and computational cost. Their findings support the use of lightweight transformer architectures such as DistilBERT when contextual analysis must remain computationally manageable.

Research on child-centered platforms also emphasizes that automated moderation is a sociotechnical problem involving algorithmic bias, cultural sensitivity, transparency, and the continuing need for human judgment. These concerns reinforce the study's use of AI as a review-support mechanism rather than an autonomous enforcement authority.

Collectively, the related studies demonstrate the value of contextual language models and behavioral evidence. However, many approaches still emphasize localized context, isolated classification decisions, or static feature aggregation. This leaves an important research opportunity: modeling how contextual and behavioral evidence evolves across the full trajectory of a conversation.

## 2.3 Theoretical Background

The theoretical foundation of this study combines machine-learning sequence modeling with discourse-based accounts of how grooming-related behavior develops across conversation.

O'Connell [12] provided an influential early typology of online grooming, describing a progression through friendship forming, relationship forming, risk assessment, exclusivity, and sexual stages. This framework established that grooming should be understood as a developing interaction rather than a collection of independent messages. Later research, however, showed that offenders do not necessarily follow one fixed linear order.

The principal theoretical framework adopted in this study is the Online Grooming Discourse Model developed by Lorenzo-Dus, Izura, and Perez-Tattam [11]. Based on a large corpus of offender chat logs, OGDM describes grooming as an entrapment network realized through four interrelated communicative processes: deceptive trust development, sexual gratification, compliance testing, and isolation. Deceptive trust development concerns the discursive construction of rapport and an exclusive relationship. Compliance testing involves probing boundaries and adjusting behavior in response, while isolation concentrates the interaction within the dyad and weakens external sources of support.

OGDM provides a strong theoretical reason to examine interaction trajectories. Its processes may emerge gradually, recur, overlap, or change direction across multiple turns. Consequently, a moderation model that retains conversational history and models changes over time is better aligned with the discourse structure of grooming than a system limited to isolated keywords.

The study translates this theoretical orientation into computationally inspectable trajectory signals. Proxy-score level and change represent the accumulation and fluctuation of contextual evidence; spike and spike-then-drop features represent abrupt increases and subsequent retreat; semantic distance from a training-derived benign centroid represents movement away from ordinary conversational content; and cumulative turn-taking imbalance represents asymmetry in participation. These features are theoretically informed behavioral indicators, not direct annotations of OGDM processes. PAN12 does not contain the independently reviewed discourse-stage labels required to establish that a specific feature occurrence is an instance of compliance testing, isolation, or another OGDM process.

This distinction does not remove the theoretical contribution. OGDM guides why cross-turn dynamics are modeled, which forms of progression are considered relevant, and why a recurrent architecture is appropriate. The empirical experiment then tests whether the resulting sequence representation improves conversation-level detection compared with static aggregation. The theory informs feature design and architectural hypotheses; the PAN12 endpoint evaluates predictive performance.

Sequence-learning theory provides the computational complement to OGDM. LSTMs are designed to preserve and update information across ordered observations, allowing the model to learn whether the order, persistence, and interaction of trajectory signals contribute to a final decision. The matched comparison with a weighted scorer tests this proposition directly because both methods receive the same seven inputs, while only the LSTM learns recurrent aggregation.

Current moderation research also supports hybrid systems that combine automated triage with human review. Such systems can process large volumes of communication while reserving contextual judgment and consequential decisions for qualified moderators. This layered principle is reflected in the proposed module: contextual and behavioral modeling supports prioritization, while the prototype does not claim autonomous determination of intent or guilt.

Together, OGDM, contextual NLP, behavioral analysis, and recurrent sequence learning establish a coherent foundation for the study. The proposed module operationalizes that foundation through a two-layer architecture that integrates conversational history, interpretable trajectory features, and learned temporal aggregation to enhance existing chat-moderation approaches.

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
