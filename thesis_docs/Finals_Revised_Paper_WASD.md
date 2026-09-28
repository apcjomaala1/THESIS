__*GroomShield: Detecting Grooming-Related Interactions in Chat Conversations Using DistilBERT and LSTM-Based Behavioral Sequence Modeling*__

 

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

 

 

 

 

 

 

 

 

 

 

# Abstract

Keyword-based chat moderation can miss grooming-related interactions whose meaning emerges through conversational context and behavioral progression. This study develops GroomShield, a two-layer artificial intelligence module designed to improve detection coverage and reduce false negatives. A context-conditioned DistilBERT classifier produces turn-level author-derived proxy scores, while a Long Short-Term Memory (LSTM) network processes seven chronological features describing score patterns, semantic movement, and speaker participation. The PAN-2012 Sexual Predator Identification corpus was selected for evaluation, with positive conversations defined by the presence of an officially identified predator author. Connected-author partitioning separates participants across training, validation, and test sets. The primary LSTM is compared with a keyword rule, maximum classifier-score aggregation, and a weighted scorer using the same features; an enhanced LSTM additionally incorporates text embeddings. The revised operating policy selects thresholds using validation F2 and applies them to previously evaluated test scores. Across 1,862 test conversations containing 44 positives, the primary LSTM achieved 93.18% recall, 66.13% precision, and 0.8613 F2, missing three positives compared with six for the weighted scorer, five for maximum classifier-score aggregation, and 17 for the keyword rule. Paired component-bootstrap intervals supported its F2 and PR-AUC advantages over the weighted scorer. The enhanced LSTM detected all 44 positives at 51.76% precision and 0.8429 F2. These findings demonstrate the contribution of contextual and behavioral sequence modeling to recall-oriented conversation detection, providing a foundation for AI-assisted moderation that complements existing safeguards and human review.

**Keywords:** online grooming detection; chat moderation; conversational context; behavioral pattern analysis; natural language processing; long short-term memory networks.

# I. Introduction

## 1.1 Background of the Study

The rapid growth of online multiplayer games and interactive digital platforms has made real-time chat a primary channel for collaboration, social interaction, and community building. These environments also create opportunities for grooming-related interactions and other harmful conduct to develop across sustained conversations [1], [2], [3]. Many moderation systems continue to rely on keyword filtering and user reports, which remain useful first-line controls but are often insufficient for complex, context-dependent threats [4], [5].

Traditional moderation methods primarily detect explicit terms or predefined patterns. They can identify straightforward violations such as profanity, yet altered spellings, special characters, coded language, and other obfuscation techniques can bypass static rules [6], [7], [8]. More importantly, an ordinary-looking message may acquire a different meaning when interpreted with surrounding turns, speaker behavior, and the progression of the interaction [2], [9]. Reliance on user reporting is also reactive and may delay review of interactions that do not contain immediately obvious violations [5].

A central challenge is therefore the number of harmful or concerning interactions that conventional systems may miss. In a safety-oriented moderation setting, false negatives are especially important because every missed conversation represents an interaction that receives no timely review. Improving detection coverage requires methods capable of combining local language context with evidence that develops across multiple turns.

Advances in machine learning and natural language processing provide a practical basis for moving beyond isolated-message filtering [9], [10]. Transformer models can represent a message in relation to its preceding context, while sequence models can learn how scores and behavioral indicators change over time. Together, these techniques support a moderation architecture that analyzes both what is being communicated and how the interaction develops.

This study develops GroomShield, an AI-powered moderation module that combines contextual language analysis with behavioral sequence modeling. Layer 1 uses DistilBERT to evaluate the current turn together with up to two preceding turns. Layer 2 uses an LSTM to aggregate a chronological sequence of seven trajectory features reflecting score level and change, semantic movement, and speaker-turn structure. GroomShield complements keyword filters and reporting mechanisms by identifying conversations that warrant human review, with recall and false-negative reduction as its central performance priorities.

To evaluate the proposed architecture, the study selected the PAN-2012 Sexual Predator Identification corpus because its scale, chronological conversations, persistent speaker identifiers, and official predator-author list support contextual and behavioral sequence analysis [13]. The dataset provides a reproducible basis for comparing the complete two-layer module with keyword, static-score, and recurrent alternatives.

The completed two-layer prototype demonstrates how contextual language analysis and behavioral sequence modeling can reduce the interactions missed by conventional moderation approaches. It also contributes to Sustainable Development Goal 9 through innovation in AI-assisted digital-safety infrastructure and to Sustainable Development Goal 16 by supporting more accountable and responsive mechanisms for identifying potentially harmful online interactions.

## 1.2 Statement of the Problem

Existing chat moderation systems are widely used, yet grooming-related and other harmful interactions persist [1], [2], [3]. Keyword-based filters, rule-based systems, and user-reporting mechanisms are effective for explicit and readily recognizable violations, but they are less capable of handling communication whose meaning depends on conversational context and behavioral progression [4], [5], [9].

The research problem addressed by this study is how an AI-powered moderation module can combine natural language processing, contextual analysis, and behavioral trajectory modeling to identify concerning interactions that static or isolated-message approaches may miss. The study develops a complete two-layer architecture and evaluates whether recurrent aggregation of chronological evidence improves detection coverage, particularly recall and false-negative reduction.

This study seeks to answer the following questions:

1. How effective are existing chat moderation systems in detecting grooming-related interactions?
2. What are the limitations of keyword-based and rule-based moderation approaches in handling context-dependent communication?
3. How can machine learning and natural language processing be utilized to analyze behavioral patterns and conversational context in chat systems?
4. To what extent can an AI-driven moderation module improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

For quantitative evaluation, the study tests these questions through a common conversation-level task and four controlled comparison methods: a training-derived keyword rule, maximum Layer 1 proxy aggregation, a validation-fitted weighted trajectory scorer, and LSTM-based sequence models. This design directly measures whether contextual and behavioral trajectory modeling improves recall, false-negative reduction, and precision-recall performance over the comparison methods.

Accordingly, the system's operative output is a conversation-level priority for moderator review. Turn-level values are intermediate signals used to model the developing interaction; the evaluated decision does not assign an offender identity to a user or label a particular message as the onset of grooming. This distinction keeps the research questions, model output, and reported results aligned to one measurable task.

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

The evaluation dataset consists of eligible dyadic conversations from the PAN12 training corpus. After the required validity and conversation-structure checks, the candidate pool contains 18,567 conversations and 218,114 turns. The official predator-author list supplies the supervision used by the experiment: Layer 1 learns from current-author membership, while Layer 2 learns the corresponding conversation-level outcome.

The study compares the proposed seven-feature LSTM with a training-derived keyword rule, maximum Layer 1 proxy aggregation, and a validation-fitted weighted trajectory scorer. A secondary LSTM supplemented with 768-dimensional base DistilBERT embeddings is evaluated separately. All methods use identical author-disjoint conversation partitions. F2 is the principal final-cutoff selection criterion, supported by recall, false-negative counts, precision, PR-AUC, and paired performance differences.

### 1.4.2 Limitations of the Study

PAN12 provides verified predator-author membership rather than exhaustive grooming labels for every training message. The study therefore uses author membership as Layer 1 supervision and evaluates the resulting architecture through the consistent conversation-level endpoint. A turn written by a listed author is positive for the Layer 1 training target even when its isolated wording is ordinary; message-level grooming classification, stage recognition, and onset localization require separately reviewed annotations.

The completed evaluation uses one established historical benchmark; locally generated synthetic conversations and other unreviewed candidate datasets are excluded. The controlled experiment establishes the architecture's performance under the selected dataset conditions. Dedicated external evaluation on representative contemporary communication, including current slang, newly developed obfuscation strategies, Filipino or Taglish communication, and other platform environments, is needed to measure transfer. No independent English-language filter was applied.

The completed study evaluates detection effectiveness through controlled offline sequential replay rather than live-platform integration. A separate local CPU benchmark measures per-turn HTTP latency and sequential throughput for both LSTM variants on synthetic chats. Representative-platform evaluation remains the next stage for concurrency, scalability, moderator outcomes, fairness, and privacy performance. The module is designed to prioritize human review, not to perform autonomous enforcement.

The system builds upon pretrained language models and a dyadic conversation design. Its performance is therefore influenced by the limitations of those models, the age and composition of the selected corpus, class imbalance, and the extent to which the selected trajectory features represent behavior in other environments.

## 1.5 Significance of the Study

This section explains the academic, practical, societal, and future-research value of the completed AI-powered moderation module.

### 1.5.1 Academic Contribution

This research contributes to computer science, artificial intelligence, cybersecurity, and online-safety research by demonstrating how contextual natural language processing can be integrated with behavioral trajectory analysis in a complete moderation architecture. Rather than reducing an interaction to isolated keywords or a single message score, the proposed system represents how evidence evolves across an ordered conversation.

The study contributes a two-layer design consisting of a context-conditioned DistilBERT classifier, seven interpretable trajectory features, and recurrent LSTM aggregation. The matched comparison between the seven-feature LSTM and a weighted scorer receiving the same information provides direct empirical evidence that learned sequence modeling adds predictive value beyond static feature combination. The primary LSTM's improvements in recall and false-negative reduction also address the study's central safety-oriented performance objective.

The research additionally contributes a reproducible evaluation framework for conversational data: connected-author partitioning, training-only construction of derived resources, validation-based checkpoint and threshold selection, preserved test-score artifacts, and component-grouped uncertainty estimation. These controls distinguish model learning from operating-threshold analysis and support repeatable comparison of the same methods.

### 1.5.2 Industry and Practical Applications

For chat platforms, gaming communities, social networks, and collaborative systems, the research demonstrates a practical architecture for augmenting existing moderation workflows. The module combines contextual language processing with an auditable sequence representation, allowing its trajectory features and conversation scores to be inspected rather than functioning only as an opaque end-to-end decision.

The approach is particularly relevant to moderation workflows seeking broader detection coverage, including conversations not identified by keyword filters or reports. Keyword rules, contextual classifiers, sequence models, and human escalation policies operate as complementary safeguards. F2 aligns the conversation-level decision rule with the study's priority of reducing missed positive conversations; precision and false-positive counts document the accompanying tradeoff.

The completed prototype establishes technical feasibility in controlled offline evaluation. Adaptation to a specific platform would still require representative local data, calibration, privacy and fairness assessment, performance engineering, and evaluation with actual moderators; these are deployment requirements rather than limitations on the architectural contribution demonstrated here.

### 1.5.3 Societal Benefits

Online grooming and related forms of exploitation pose serious threats to user well-being, particularly for children, adolescents, and users with limited digital literacy. By improving the ability of a moderation system to identify conversations missed by static keyword rules, this study contributes to the development of more responsive digital-safety tools.

The module strengthens the technical basis for human-reviewed detection by prioritizing false-negative reduction and supporting more consistent attention to concerning interactions. It is designed for decision support, with qualified moderators retaining responsibility for interpreting evidence and determining action.

The architecture and evaluation process provide a transferable starting point for organizations with limited moderation resources. Platform adaptation can combine the module with appropriate governance, representative data, and qualified human oversight.

### 1.5.4 Implications for Future Research

This research establishes a foundation for future investigations into AI-powered moderation systems and behavioral analysis in digital communication. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media.

Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy. Future research can also explore the integration of multimodal analysis (text, images, video) for comprehensive content moderation.

The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field.

### 1.5.5 Sustainable Development Goal (SDG) Contribution

This study supports Sustainable Development Goal 9 (Industry, Innovation and Infrastructure) through the development of an AI-driven moderation prototype that combines machine learning, natural language processing, and behavioral trajectory analysis to advance digital-safety infrastructure. It also supports Sustainable Development Goal 16 (Peace, Justice and Strong Institutions) by contributing a reproducible method for improving the identification and human review of potentially harmful online interactions. The controlled held-out evaluation supplies empirical evidence for this contribution, while the architecture and evaluation controls provide a basis for broader future adaptation.

## 1.6 Definition of Terms

Artificial Intelligence (AI) - The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions.

Behavioral Pattern Analysis - A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns.

Chat Moderation System - An automated or semi-automated system designed to monitor, prioritize, filter, or regulate user communications in chat environments to reduce harmful interactions and support moderator action.

Contextual Analysis - The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation.

Conversation-Level Endpoint - The primary measurable outcome used in the experiment: whether a dyadic PAN12 conversation contains at least one author included in the official predator-author list.

F2 Score - A precision-recall summary that places greater weight on recall. Validation F2 selects the final conversation cutoffs, aligning the operating policy with false-negative reduction.

GroomShield - The proposed conversation-analysis module combining context-conditioned DistilBERT scoring with LSTM-based behavioral sequence modeling.

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

The chapter establishes the scholarly and theoretical foundation for the proposed two-layer moderation module. It connects contextual transformer modeling, behavioral-feature research, sequence learning, and the Online Grooming Discourse Model to the study's design, with PAN12 serving as the selected dataset for empirical evaluation.

## 2.1 Review of Related Literature

Recent research in chat moderation has shifted from traditional rule-based filtering toward AI-driven contextual analysis models. Earlier moderation approaches relied primarily on keyword blacklists to detect violations such as profanity or explicit harmful language. However, these systems are limited in their ability to interpret conversational intent, allowing malicious users to bypass filters through techniques such as altered spellings, coded language, or multi-message grooming strategies.

Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior. Schurger-Foy et al. [9] demonstrated that approximately 67% of toxic messages in multiplayer gaming environments are context dependent, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history. Similarly, Yang et al. [6] introduced the ToxBuster architecture, which incorporates message history and speaker metadata into text classification models. Their results showed significant improvements in detection accuracy, achieving up to 95% precision in identifying harmful interactions through sequence-based moderation rather than single message evaluation.

These findings suggest that integrating conversational context and historical behavioral patterns improves moderation effectiveness compared to static filtering methods. Transformer-based NLP architectures such as BERT, RoBERTa, and DistilBERT have consequently emerged as standard tools for understanding linguistic patterns in chat environments. 

Furthermore, longitudinal behavioral analysis has been shown to be a strong predictive indicator of future harmful activity. Studies indicate that tracking interaction patterns over time can achieve up to 74% balanced accuracy in forecasting future toxic behavior, reinforcing the importance of behavioral modeling in proactive moderation systems. 

Despite these advancements, moderation research remains constrained by legacy datasets that may not adequately represent modern communication styles, slang, or evolving evasion techniques used by malicious actors.

## 2.2 Related Studies

Several empirical studies have explored the application of artificial intelligence to grooming-related interactions and other context-dependent harms in online environments.

The PAN-2012 Sexual Predator Identification task introduced by Inches and Crestani [13] provides the empirical benchmark selected for this study. PAN12 defined related participant-identification and distinctive-line tasks. The present experiment uses the official predator-author list to construct consistent training and conversation-level evaluation targets; the distinctive-line task serves a separate benchmark purpose.

These dataset properties motivated its selection: PAN12 provides the scale, chronological message order, and persistent speaker identifiers required for trajectory construction and connected-author evaluation. They allow the study to examine behavioral progression across turns while testing generalization to conversations involving unseen authors.

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

The study translates this theoretical orientation into computationally inspectable trajectory signals. Proxy-score level and change represent the accumulation and fluctuation of contextual evidence; spike and spike-then-drop features represent abrupt increases and subsequent retreat; semantic distance from a training-derived benign centroid represents movement away from ordinary conversational content; and cumulative turn-taking imbalance represents asymmetry in participation.

| OGDM-informed conversational property | Operational indicators | Role in the trajectory model |
|---|---|---|
| Accumulation and persistence of contextual evidence | Peak proxy score, current proxy score, and spike count | Represent whether concerning contextual evidence appears and persists across turns |
| Escalation, boundary testing, and retreat | Rate of change and spike-then-drop | Represent abrupt changes and subsequent reduction in the proxy trajectory |
| Movement away from ordinary conversational content | Topic distance from the training-derived benign centroid | Represent semantic deviation from the benign training reference |
| Interaction structure within the dyad | Cumulative turn-taking imbalance | Represent sustained asymmetry in participation |

This mapping provides the theoretical motivation for each feature family. The features operationalize cross-turn properties for model testing; they are not direct annotations of OGDM stages, which would require independently reviewed discourse-stage labels.

OGDM guides why cross-turn dynamics are modeled, which forms of progression are considered relevant, and why a recurrent architecture is appropriate. The empirical experiment tests whether the resulting sequence representation improves conversation-level detection compared with static aggregation. The theory informs feature design and architectural hypotheses, while the selected dataset provides the controlled evaluation.

Sequence-learning theory provides the computational complement to OGDM. LSTMs are designed to preserve and update information across ordered observations, allowing the model to learn whether the order, persistence, and interaction of trajectory signals contribute to a final decision. The matched comparison with a weighted scorer tests this proposition directly because both methods receive the same seven inputs, while only the LSTM learns recurrent aggregation.

Current moderation research also supports hybrid systems that combine automated triage with human review. Such systems can process large volumes of communication while reserving contextual judgment and consequential decisions for qualified moderators. This layered principle is implemented in the proposed module: contextual and behavioral modeling prioritizes conversations, while qualified moderators retain authority over interpretations of intent, identity, and enforcement decisions.

Together, OGDM, contextual NLP, behavioral analysis, and recurrent sequence learning establish a coherent foundation for the study. The proposed module operationalizes that foundation through a two-layer architecture that integrates conversational history, interpretable trajectory features, and learned temporal aggregation to enhance existing chat-moderation approaches.

# III. METHODOLOGY

## 3.1 Research Design

This study uses a developmental and experimental research design [15] to build and evaluate GroomShield, an offline conversation-analysis prototype. The research centers on the two-layer contextual and behavioral sequence architecture. PAN12 was selected as an appropriate evaluation corpus, with the measurable outcome operationalized as **conversation-level identification of conversations containing at least one author on the dataset's official predator list**. This outcome is applied consistently across model development and evaluation.

The proposed system has two learned layers. Layer 1 fine-tunes DistilBERT using the official predator-author list as weak supervision. For each current turn, it processes that turn together with the two preceding turns and produces a **predator-author proxy score**. Layer 2 uses the chronological sequence of features constructed from proxy-score dynamics, base-encoder topic distance, and cumulative turn structure to estimate whether the conversation contains a listed predator. The LSTM is the sequence model, while a weighted scorer, an aggregated raw Layer 1 score, and a keyword rule serve as comparison methods.

Model development and detection evaluation use chronological offline replay of dataset conversations. A separate local HTTP benchmark measures warmed per-turn latency and throughput on synthetic conversations; it does not test platform integration, live users, or autonomous moderation. The output is intended as decision support for human review. A below-threshold result is not a determination that a conversation or participant is safe.

The experiment tests whether an LSTM using the same seven trajectory inputs as the weighted scorer improves the approved conversation-level endpoint. A larger LSTM that additionally receives a 768-dimensional base DistilBERT embedding is evaluated separately as an enhanced-input model so that an input-capacity difference is not misreported as an architectural advantage. No superiority result is assumed in advance.

## 3.2 Relevant Technology

### 3.2.1 Python Programming Language

Python is used as the primary programming language for the development and evaluation of the proposed moderation module. It was selected due to its extensive support for machine learning, natural language processing, and data analysis through established libraries and frameworks.

### 3.2.2 Hugging Face Transformers and PyTorch

The study utilizes the Hugging Face Transformers library together with the PyTorch deep learning framework for model training and inference. These technologies provide pre-trained transformer architectures and efficient tools for fine-tuning NLP models for text classification tasks.	

### 3.2.3 DistilBERT

DistilBERT serves as the text encoder and Layer 1 sequence classifier. It is a lightweight transformer-based model derived from BERT that retains contextual language representations while reducing computational requirements. In the revised experiment, the fine-tuned classifier estimates the author-derived training target for the current turn under preceding conversational context, producing the trajectory signal used by Layer 2. A separate, unchanged `distilbert-base-uncased` encoder supplies the 768-dimensional embedding used by topic-distance computation and the enhanced-input LSTM.

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

PAN12 was selected as the evaluation corpus because it provides a large established collection with chronological conversations, persistent speaker identifiers, and an official author list suitable for reproducible sequence modeling [13]. After strict removal of rows that fail the required conversation, chronology, author, or label checks and restriction to dyadic conversations, the locked candidate pool contains 218,114 turns across 18,567 conversations, including 454 positive conversations and 34,686 distinct author identifiers. Invalid records are excluded rather than assigning a missing author label to the negative class.

For conversation \(c\), let \(A_c\) be its set of authors and \(P\) the official PAN12 predator-author set. The primary ground-truth label is

\[
Y_c = \mathbf{1}[A_c \cap P \neq \varnothing].
\]

Thus, a positive case is a conversation containing at least one officially listed predator author. For Layer 1 only, the weak target for turn \(t\), authored by \(a_t\), is

\[
Z_t = \mathbf{1}[a_t \in P].
\]

Because \(Z_t\) repeats an author-level identity label on that author's turns, it does not establish that a particular turn contains grooming behavior. The Layer 1 output is therefore called a predator-author proxy score rather than a grooming-message probability.

These properties support sequence construction at scale and permit every connected group of authors to be assigned wholly to one partition.

The author-derived target supplies consistent weak supervision for contextualized turns. Layer 1's training target and Layer 2's conversation label remain distinct throughout the pipeline, and no per-message field is treated as exhaustive grooming ground truth.

### 3.3.2 Inclusion and Preprocessing

The primary corpus is restricted to conversations with exactly two distinct authors to match the dyadic interaction scope and the implemented turn-taking feature. Empty messages and rows without a valid conversation identifier, chronological line identifier, author identifier, or binary official predator-author status are excluded. Original conversation and line identifiers are retained. Each usable row receives a stable key based on dataset source, conversation identifier, and line identifier so that duplicate text cannot overwrite another turn's cached score.

Conversations are ordered by their original line identifier. Layer 1 receives a prefix-only context consisting of the current turn and up to two immediately preceding turns from the same conversation. Neutral turn separators are inserted, but raw author identifiers, predator-list membership, the project `is_suspicious` field, source-revealing role names, future turns, and conversation labels are never included in model text. Training and inference use the identical context-construction function. The DistilBERT tokenizer truncates each context to 128 tokens and applies dynamic padding within each batch.

Text normalization is deliberately conservative: character encoding and whitespace are standardized, while altered spellings and obfuscations are retained so that evaluation does not benefit from a hand-written correction rule unavailable to the learned model. The primary experiment does not add synthetic conversations or separately collected chat logs.

### 3.3.3 Connected-Author Data Partitioning

The dataset is partitioned before negative sampling, context caching, centroid construction, model fitting, or threshold selection. Conversations are represented as vertices in a graph; any conversations sharing an author are connected. Every resulting connected component is assigned wholly to one partition, creating zero conversation overlap and zero author overlap across training, validation, and final test data.

This design prevents the same participant's recurring language and interaction patterns from appearing in both development and evaluation data. The final test therefore measures transfer to author-connected groups that were unseen during training and validation, rather than recognition of participants already encountered by the model.

The locked manifest assigns 13,031 conversations to training, 1,827 to validation, and 1,862 to the final test; an additional 1,847 conversations are excluded from the primary experiment. The corresponding positive-conversation counts are 319, 49, 44, and 42. Partition assignment uses connected-component membership, partition size, and class balance rather than model scores or text-derived features. The manifest records zero conversation, author, and connected-component overlap across all groups together with the random seed, source-data hash, and manifest hash.

The training partition is used for parameter estimation. After partitioning, negative Layer 1 training rows were downsampled to three negatives per positive row; validation and test distributions remained untouched. Validation supplies checkpoint selection, hyperparameter selection, comparator fitting, and threshold selection. The original test evaluation produced preserved conversation scores; the revised F2 policy is evaluated from those same scores using validation-selected cutoffs, as described in Section 3.5.2.

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

Optimization uses fused AdamW on an NVIDIA RTX 3060 Ti, BF16 mixed precision, TF32, gradient clipping at 1.0, and random seed 42. The completed run uses five epochs, learning rate \(2\times10^{-5}\), weight decay 0.01, warm-up ratio 0.10, three sampled training negatives per positive row, physical training batch size 8, validation batch size 16, gradient accumulation 1, and early-stopping patience of two epoch evaluations. The checkpoint was selected using validation PR-AUC, and its original diagnostic binary threshold was selected using F0.5. Layer 2 consumes the continuous positive-class score, not this diagnostic binary decision; the Layer 1 checkpoint and diagnostic threshold remain unchanged. The selected checkpoint, tokenizer, configuration, metrics history, and row manifest are saved together.

The positive-class softmax output is denoted \(R_t\). It estimates the contextualized author-derived training target and serves as the trajectory signal used for feature construction and conversation-level sequence modeling.

### 3.4.2 LSTM-Based Trajectory Scoring Model

The primary Layer 2 model is an LSTM that receives the chronological sequence of the same seven features supplied to the weighted scorer. Padding masks ensure that padded turns do not affect hidden-state computation. A secondary enhanced-input LSTM concatenates the 768-dimensional base DistilBERT embedding with the seven trajectory features, producing a 775-dimensional turn vector; its result is reported separately and is not used to claim a matched-input architectural advantage.

The selected primary model is a unidirectional, single-layer LSTM with hidden dimension 128 and dropout 0.20, trained with batch size 32, Adam learning rate 0.001, weight decay 0.0001, gradient clipping at 1.0, a maximum of 20 epochs, and early-stopping patience of four validation evaluations. The selected enhanced model uses the same hidden dimension, layer count, dropout, batch size, and stopping rule with learning rate 0.0005. Both completed searches used seed 42 and validation PR-AUC with validation F0.5 as the first tie-break criterion. These checkpoints are retained; F2 changes their final conversation cutoffs, not the training loss, learned weights, or checkpoint selection.

Layer 2 is trained only against the valid conversation label \(Y_c\). `BCEWithLogitsLoss` is applied to the output at the final valid turn using a positive-class weight of 39.8495, computed solely from the 12,712 negative and 319 positive training conversations. No turn-level loss or cumulative `is_suspicious` target is used. Validation selects the LSTM checkpoint and its conversation flagging threshold. Intermediate prefix scores demonstrate sequence processing, and the first threshold crossing is summarized as an exploratory prefix statistic.

### 3.4.3 Comparison Models

Four comparisons are evaluated on the same conversation endpoint and locked partitions:

1. **Aggregated raw Layer 1:** the maximum \(R_t\) in a conversation, using its independently selected validation threshold.
2. **Weighted trajectory scorer:** a validation-fitted combination of the seven trajectory features, with its own validation-selected weights and threshold.
3. **Keyword rule:** a fixed lexicon derived only from the revised training partition; a conversation is positive when any turn matches the rule. Lexicon construction and matching rules are frozen before final testing.
4. **Enhanced-input LSTM:** the 775-input LSTM reported separately from the primary matched seven-feature LSTM.

The principal architecture comparison is the seven-feature LSTM versus the seven-feature weighted scorer. The F2 analysis holds learned parameters, weighted-scorer coefficients, keyword resources, and feature definitions fixed and selects each scored method's final cutoff independently on validation data. It compares fixed models under an F2 operating policy, not a new F2-directed hyperparameter search or weighted-scorer refit. The raw Layer 1 baseline uses its actual positive-class score directly and is not passed through the weighted scorer or another sigmoid.

## 3.5 Evaluation/Validation

### 3.5.1 Threshold Selection

GroomShield separates learning a conversation score from choosing the cutoff that converts that score into a flag. The trained models and scoring functions remain fixed. For method \(m\), conversation \(c\), score \(s_m(c)\), and cutoff \(\theta_m\), the decision is

\[
\widehat{Y}_{m,c}=\mathbf{1}[s_m(c)\geq\theta_m].
\]

A positive decision flags the conversation for human review. F2 is the selection criterion because GroomShield is a screening module intended to detect conversations that might otherwise receive no attention, rather than an autonomous enforcement system. The operating policy therefore gives greater emphasis to recall while retaining precision in the objective. F1 remains a supplementary reporting measure rather than the criterion used to choose the final cutoff.

The threshold-selection procedure is:

1. **Retain the fitted scoring functions.** Use the selected DistilBERT and LSTM checkpoints, weighted-scorer coefficients, keyword lexicon, and seven-feature definitions without retraining or reselection.
2. **Use validation conversations only.** Read the saved final conversation scores for the same 1,827 validation conversations, including 49 positives, for every method. Model scores, rather than test outcomes, define the candidate cutoffs.
3. **Evaluate candidate cutoffs.** For each method, consider every distinct score observed on validation. At each cutoff, apply the greater-than-or-equal decision rule and compute precision, recall, and F2 against the conversation labels.
4. **Select the maximum-validation-F2 cutoff.** Resolve equal F2 values by higher recall, then higher precision, then the higher cutoff. Each method receives its own cutoff because its score distribution differs.
5. **Apply the selected cutoff unchanged.** Use the retained full-precision value on the saved test scores through Section 3.5.2. No cutoff is chosen or adjusted using test outcomes.

The selected conversation cutoffs are:

| Method | Validation-selected F2 cutoff |
|---|---:|
| Primary LSTM | 0.275535285 |
| Enhanced LSTM | 0.000971102 |
| Maximum Layer 1 | 0.961438656 |
| Weighted scorer | 0.696637128 |
| Keyword rule | 1.000000000 |

*Table 3.3. Final conversation cutoffs selected by validation F2. Displayed values are rounded to nine decimal places; calculations retain full precision.*

The keyword rule produces binary scores, so its selected cutoff of 1.0 gives exactly the same decisions as the original 0.5 cutoff. These conversation cutoffs are separate from the Layer 1 diagnostic threshold and the spike/drop thresholds used to construct trajectory features; those existing thresholds remain unchanged. The numerical cutoffs are model-specific decision boundaries, not calibrated probabilities of grooming.

F2 is selected because the research aims to identify positive conversations missed by keyword and static-score approaches. Its formulation assigns a coefficient of four to false negatives and one to false positives, emphasizing recall without ignoring precision. This is a recall-oriented precision-recall objective, not unconstrained recall maximization or an empirically established four-to-one operational harm ratio. False alerts remain reported, while reducing moderator workload is not the principal optimization claim.

### 3.5.2 Test-Score Analysis and Verification

The F2 policy was adopted after the original F0.5 test evaluation. Its cutoffs are selected exclusively from the 1,827 validation conversations and applied unchanged to the saved scores for the 1,862-conversation test partition. These F2 results are a revised-policy analysis of the previously evaluated, author-disjoint test partition, not a new untouched holdout. No test-score threshold search, retraining, checkpoint reselection, or new model inference is performed.

The analysis verifies identical validation populations across methods, reproduces the original test predictions and metrics, and preserves the original evaluation artifacts. Every method is evaluated on the same test conversation IDs, and all outcomes are retained regardless of which method performs best. F2 applies to the final conversation decision; existing Layer 1 diagnostic and feature-construction thresholds remain unchanged.

### 3.5.3 Metrics and Comparative Analysis

The unit of evaluation is the conversation, with \(Y_c\) as ground truth. The primary reporting measures are recall, false-negative count, and F2. Precision, false-positive count, specificity, F1, PR-AUC, and ROC-AUC characterize the complete detection tradeoff. Let \(P\) and \(R\) denote precision and recall:

\[
P=\frac{TP}{TP+FP}, \qquad
R=\frac{TP}{TP+FN},
\]

\[
F_1=\frac{2PR}{P+R}, \qquad
F_2=\frac{5PR}{4P+R}
=\frac{5TP}{5TP+4FN+FP}.
\]

Validation PR-AUC selected the retained checkpoints. PR-AUC remains important because positive conversations are rare; a cutoff change does not change PR-AUC or ROC-AUC. Ninety-five-percent percentile intervals and paired method-difference intervals use 2,000 bootstrap resamples of connected-author components with seed 42. All conversations in each sampled component remain grouped, with identical draws across methods. Threshold-dependent intervals are recalculated for F2 decisions; unchanged ranking-metric intervals are retained after scores and point estimates are verified. These intervals are conditional on fixed models and selected cutoffs and do not incorporate selection uncertainty.

Prefix-level scores show how the conversation score develops as evidence accumulates. The primary result uses the final valid turn; intermediate values and first threshold crossings are not validated grooming-onset labels. A separate onset study requires expert-reviewed first-onset annotations and time-to-detection evaluation.

### 3.5.4 Local Per-Turn Latency Benchmark

To test the panel's operational-performance question separately from detection accuracy, the two selected LSTM checkpoints are benchmarked through the local `/api/score` HTTP endpoint on CPU. Each timed request submits the complete conversation prefix and selects either the primary or enhanced LSTM. The current prototype recomputes contextual DistilBERT scores, base-encoder embeddings, seven trajectory features, and the selected LSTM output for that prefix; therefore the timing includes the complete model path, server-side redaction, request handling, JSON serialization, and localhost transport. The two variants use the same upstream processing, and the only model-path difference is the LSTM input and checkpoint. Models are loaded before timing.

The fixed, unlabeled synthetic workload contains 1-, 4-, 8-, and 16-turn prefixes of the same chat. After three warm-up requests per model and prefix length, 40 requests are timed for each of the eight model-length combinations (160 per model). The order of cases is randomized with seed 42, at concurrency one. Elapsed client-side round-trip time is summarized by median, 95th percentile, and 99th percentile. Sequential throughput is completed requests divided by the cumulative duration of those timed requests. An equally weighted mixture of the four prefix lengths is reported in addition to length-specific values. The machine is an 11th-generation Intel Core i5-11400H with 12 logical processors, six PyTorch intra-operation threads, Windows 11, and CPU inference. This benchmark does not use PAN12 test conversations, change thresholds, or retrain models; it tests this local prototype, not production traffic, network conditions, parallel load, or moderator response time.

## 3.6 Ethical Considerations

All datasets used in this study are handled in accordance with applicable data-protection and research-ethics principles. PAN12 is a research benchmark used under its applicable access and usage conditions. In the local demonstration interface, common direct identifiers—including email addresses, phone numbers, URLs, IPv4 addresses, and common account handles—are masked on the server before model scoring; the masked history then replaces the browser's active conversation history and displayed text. Responses are marked as non-cacheable, and resetting the demonstration clears the browser's active conversation state. Raw text remains briefly in the local browser while a request is processed. These safeguards reduce exposure but do not guarantee complete anonymization: automatic pattern matching may miss names, indirect identifiers, unusual formats, or identifying combinations of details. Real sensitive information must therefore not be entered into the prototype, and any research data still requires access control and manual privacy review.

The study does not involve direct interaction with real users. The experiment is evaluated offline using the selected research dataset. Locally retained synthetic candidate data and separately collected conversation files are excluded from primary training, validation, and testing unless a later study completes appropriate provenance, licensing, privacy, and independent annotation review.

The moderation module is designed as a support tool for human moderators rather than an autonomous decision-making mechanism. A model flag prioritizes a conversation for human review before any moderation action; it is not an offender determination, an inference of intent from an isolated message, or a declaration that an unflagged conversation is safe.

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
