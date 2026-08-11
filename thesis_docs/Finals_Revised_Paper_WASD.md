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

The study focuses specifically on detecting grooming-related interactions in English-language chat data. 

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

By supporting the detection of harmful interactions, platforms can reduce the burden on manual moderation teams, enabling them to focus on complex cases requiring human judgment. The real-time analysis capability of the module may allow earlier detection and flagging of suspicious behavior, reducing response time and limiting prolonged exposure to harmful interactions. This is particularly critical for platforms serving vulnerable user populations, including minors. 

Furthermore, the proposed module can be adapted into existing moderation workflows without replacing current filtering mechanisms, offering a scalable and non-disruptive enhancement to platform safety. The adoption of such advanced moderation techniques positions platforms as responsible actors in digital safety, potentially building user trust and reducing legal liabilities.

### 1.5.3 Societal Benefits

Beyond academia and industry, this research has direct societal benefits. Online harassment and grooming pose serious threats to user well-being, particularly affecting vulnerable populations such as children, adolescents, and individuals with limited digital literacy. By improving detection mechanisms, this study contributes to creating safer online environments where users can interact with reduced fear of exploitation or harm. The development of effective AI-driven moderation tools can help prevent real-world harm that originates from online interactions, including trauma and abuse. 

In the context of the Philippines, which features a highly active youth demographic deeply engaged in online gaming, social media, and digital communication platforms, the risk of digital exploitation remains a critical national concern. The localized application of this AI-driven moderation module offers vital implications for Philippine cyber-safety frameworks. By equipping local platform administrators and digital safety advocates with context-aware tools to proactively detect predatory behaviors—especially those masked in modern chat interactions—this research supports broader, nationwide efforts to protect Filipino minors from online exploitation and abuse.

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

Real-time Analysis - The processing and evaluation of data as it is generated or received, without significant delays, enabling immediate detection and response.

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

This study will employ a developmental and experimental research design. The primary objective is to design and evaluate an AI-powered moderation module for detecting grooming-related interactions in chat conversations. The study focuses on combining message-level contextual analysis using DistilBERT with conversation-level behavioral trajectory scoring to improve moderation performance beyond traditional keyword-based approaches.

The prototype consists of three primary stages: (1) data collection and preprocessing, (2) message-level model development using DistilBERT, and (3) comparative evaluation against a rule-based keyword moderation baseline. In addition, the study proposes a conversation-level trajectory scoring model based on a Long Short-Term Memory (LSTM) network, which processes these engineered behavioral indicators sequentially across conversation turns to capture the chronological, progressive risk profile of online grooming.

Rather than replacing existing moderation systems, the proposed approach is intended to augment current moderation methods by incorporating contextual NLP analysis together with behavioral pattern tracking. The study combines machine learning-based risk scoring with rule-based moderation indicators to evaluate whether contextual and behavioral analysis can improve detection performance.

The proposed models will be validated offline using PAN12-derived data as the primary benchmark, with real conversation datasets and synthetically generated annotated chat data used where applicable to supplement underrepresented interaction patterns. Performance will be evaluated quantitatively using classification metrics such as recall, precision, F1-score, and comparative analysis against traditional moderation approaches.

## 3.2 Relevant Technology

### 3.2.1 Python Programming Language

Python is used as the primary programming language for the development and evaluation of the proposed moderation module. It was selected due to its extensive support for machine learning, natural language processing, and data analysis through established libraries and frameworks.

### 3.2.2 Hugging Face Transformers and PyTorch

The study utilizes the Hugging Face Transformers library together with the PyTorch deep learning framework for model training and inference. These technologies provide pre-trained transformer architectures and efficient tools for fine-tuning NLP models for text classification tasks.	

### 3.2.3 DistilBERT

DistilBERT serves as the primary message-level language model used in the study. It is a lightweight transformer-based model derived from BERT that retains strong contextual language understanding while reducing computational requirements. The model is suitable for detecting grooming-related interactions because it can analyze contextual meaning rather than relying solely on keyword matching.

### 3.2.4 Development Environment

The prototype system is developed and tested using Jupyter Notebook and Visual Studio Code within a Python-based experimental environment. GPU acceleration may be utilized during model training to improve computational efficiency.

## 3.3 Data Collection and Processing

### 3.3.1 Data Collection

The study utilizes a combination of publicly available datasets, real conversation datasets, and synthetically generated annotated chat data for model training and evaluation. 

The primary public benchmark used is the PAN12 Sexual Predator Identification corpus, a widely adopted reference dataset in grooming detection research. This corpus contains real chat logs with conversation-level labels identifying predatory interactions and is used to establish baseline performance and enable comparison with prior work in the literature. 

In addition to PAN12-derived data, the study incorporates real conversation datasets collected and annotated for research purposes. These datasets contain per-message labels and conversation identifiers, enabling both message-level analysis and reconstruction of ordered conversation sequences for behavioral and trajectory-based analysis. 

The study also utilizes synthetically generated annotated chat data to supplement underrepresented interaction patterns not sufficiently represented in publicly available datasets. These synthetic conversations are manually structured and annotated to simulate grooming-related behaviors, conversational progression, obfuscation techniques, and spike-then-drop interaction patterns associated with deliberate moderation evasion. Crucially, to align with current digital environments, the synthetic datasets are explicitly constructed using modern online lingo, contemporary gaming slang, and current communication phrasing to ensure the models are trained on the linguistic realities of today's chat platforms. 

All datasets are organized into a unified structure containing conversation IDs, message order, participant identifiers, and annotation labels to support preprocessing, feature engineering, model training, and evaluation.

Table 3.1 summarizes the datasets used in this study.

__Dataset__

__Source__

__Size__

__Label Type__

PAN12 Sexual Predator Dataset

PAN12 Competition Corpus

Conversation count determined from the PAN12-derived split used in this study

Per-conversation \+ suspicious-line annotations

Study Dataset (provided)

Institutional/platform logs (proposed future data source)

Variable

Per-message \+ Conversation ID

Simulated Chat Data

Manually generated synthetic datasets

Supplementary

Per-message

*Table 3.1. Summary of Datasets Used*

### 3.3.2 Data Preprocessing

The preprocessing procedures are applied to PAN12-derived datasets, real conversation datasets, and synthetically generated annotated chat data used for model training and evaluation.

At the message level, text is cleaned to remove formatting inconsistencies, normalize punctuation, and standardize character encoding. Obfuscated terms, such as altered spellings or special-character substitutions commonly used to bypass moderation systems, are normalized where applicable. Messages are then tokenized using the DistilBERT tokenizer with a maximum token length of 512 tokens, consistent with the model’s architectural constraints.

At the conversation level, messages are grouped according to conversation ID and arranged chronologically to preserve the sequential flow of interactions. This organization enables the study to analyze conversational progression and behavioral patterns across multiple message exchanges rather than evaluating messages in isolation.

For trajectory-based analysis, conversation data is represented as sequential conversation instances corresponding to message turns. These instances support the analysis of how behavioral risk indicators evolve throughout a conversation. The processed data is then used for message-level classification and conversation-level behavioral scoring.

### 3.3.3 Data Processing

The collected datasets undergo data processing to organize raw chat records into a structured format suitable for analysis and model training. Chat logs from different sources are standardized into a unified dataset structure containing conversation identifiers, message order, participant labels, timestamps where available, and annotation labels.

Annotation labels indicating predatory, suspicious, or non-predatory behavior are associated with corresponding messages or conversations. Synthetic annotated data generated for the study is also integrated into the same dataset structure to maintain consistency across all data sources.

The resulting processed datasets are stored in structured formats such as CSV files to support preprocessing, feature engineering, model training, and evaluation.

### 3.3.4 Feature Engineering

Two categories of features are extracted for each conversation snapshot: message-level features derived from the DistilBERT encoder, and trajectory-level features derived from the evolving sequence of risk scores across turns.

Message-level features consist of the 768-dimensional embedding produced by the fine-tuned DistilBERT model for each individual message. While pre-trained transformers map general semantic similarity, the fine-tuning process warps this continuous vector space so that proximity is determined by pragmatic intent and behavioral alignment relative to the predatory register. Consequently, messages sharing subtle grooming markers (such as boundary-probing or isolation attempts) are projected into proximate vector regions, even when their surface-level lexical content appears completely benign.

Trajectory-level features are computed over conversation history up to the current turn and serve as chronological sequence inputs to the LSTM trajectory scoring model. These features capture behavioral progression and are designed to reduce sensitivity to deliberate score suppression.

Topic drift is computed as the cosine distance between the current turn's message embedding and a precomputed benign-chat centroid. While traditional drift metrics measure changes relative to the conversation's initial turn, this approach is vulnerable if a predator bypasses small-talk and initiates predatory language immediately. By measuring cosine distance against a static, precomputed centroid of safe/benign chat language, the topic drift feature remains highly sensitive to immediate risk escalation on turn one.

Table 3.2 summarizes the features used in the trajectory model.

__Feature__

__Description__

__Level__

DistilBERT message embedding

768-dimensional semantic vector per message

Message

Per-message risk score

Output of the message-level DistilBERT classifier (0-1)

Message

Peak score so far

Highest risk score seen at any prior turn

Trajectory

Spike-then-drop pattern

Detection of deliberate score suppression behavior

Trajectory

Rate of score change

Delta between consecutive message risk scores

Trajectory

Topic drift

Cosine distance between the current message embedding and a precomputed centroid of benign-chat conversations

Trajectory

Turn-taking imbalance

Ratio of word count between participants

Structural

Spike count

Number of times score exceeded risk threshold

Trajectory

*Table 3.2. Trajectory Features Extracted Per Conversation Snapshot*

### 3.3.5 Data Splitting

The processed dataset is divided into training, validation, and test sets to support model development and evaluation. Splitting is performed at the conversation level to prevent data leakage between datasets and preserve the integrity of conversational context.

The training set is used for model learning, while the validation set is used for threshold tuning and parameter adjustment. The test set is reserved for final evaluation of the proposed moderation approach and comparison against the rule-based baseline model.

This separation ensures that conversations used during evaluation are not previously seen during training, allowing a more reliable assessment of model performance.

## 3.4 Model Development

### 3.4.1 Message-Level Classifier

The message-level classifier is based on DistilBERT, a transformer model pre-trained on large-scale English text corpora and fine-tuned for binary sequence classification on the study's labeled message dataset. Fine-tuning adapts the pre-trained model's general language representations to the specific linguistic patterns of grooming-related communication, including subtle forms of trust-building, isolation attempts, and PII solicitation.

Training uses a binary cross-entropy loss function. Given the expected class imbalance between predatory and non-predatory messages, the training procedure applies class-weight balancing to prevent the model from biasing toward the majority class. The classifier outputs a scalar risk score between 0 and 1 for each message, representing the estimated probability of predatory content.

### 3.4.2 LSTM-Based Trajectory Scoring Model

The trajectory model utilizes a Long Short-Term Memory (LSTM) network that takes as input a sequence of turn-level feature vectors containing the message-level DistilBERT risk score and per-turn trajectory feature. Before feature extraction, a precomputation step is run over a corpus of benign chats to calculate the benign-chat centroid used for topic-drift measurement. The LSTM processes this sequence of feature vectors chronologically, automatically learning to map the sequential progression of these behavioral indicators to a real-time trajectory risk score between 0 and 1 at each turn.

The LSTM model is trained using binary cross-entropy loss against cumulative conversation-level labels, optimizing its internal gating weights to detect threat escalation. The system emphasizes early detection operationally by recording the first turn where the LSTM's trajectory score exceeds the tuned flagging threshold (time-to-detection).

The trajectory risk score is the primary output consumed by the moderation module. A configurable threshold determines when a conversation is flagged for human review. The threshold is tuned during validation to optimize recall — the study's primary metric — while maintaining a false positive rate that is operationally sustainable for the moderation team.

### 3.4.3 Baseline Comparison Model

To evaluate the improvement introduced by the proposed approach, a keyword-based moderation baseline will be implemented using the same dataset. The baseline will utilize a keyword lexicon extracted via term-frequency analysis from the predatory class of the PAN12 training split to flag messages. Conversations in which any message is flagged by the baseline will be marked as harmful. This mirrors the behavior of conventional rule-based moderation systems and serves as the comparison point for all evaluation metrics.

## 3.5 Evaluation/Validation

### 3.5.1 Evaluation Metrics

The dataset is divided into training, validation, and test sets at the conversation level to prevent data leakage across splits. The validation set is used to tune model parameters, evaluating early-detection thresholds and LSTM sequence length bounds, while the test set is reserved for final comparative evaluation against the baseline.

Model robustness is also evaluated using cases that represent common moderation challenges, including obfuscated text and conversations where risk indicators appear across multiple turns. These cases help assess whether the proposed approach can detect grooming-related interactions beyond isolated keyword matches.

The proposed approach is compared against a keyword-based or rule-based baseline using the same test set and evaluation metrics. This comparison determines whether the combination of DistilBERT-based message analysis and conversation-level behavioral scoring improves detection performance, particularly in terms of recall and false-negative reduction.

### 3.5.2 Testing and Validation

Model robustness is evaluated using adversarial or evasive conversation patterns identified as limitations of traditional moderation systems. These include conversations containing obfuscated text, altered spellings, coded language, or gradual behavioral progression intended to reduce apparent message risk over time.

The proposed approach is compared directly against a keyword-based or rule-based baseline using the same evaluation dataset and metrics. Comparative evaluation focuses primarily on recall, false-negative reduction, and overall moderation performance.

Where applicable, additional statistical analysis methods, such as McNemar’s test, may be explored in future work to further validate differences between moderation approaches.

## 3.6 Ethical Considerations

All datasets used in this study are handled in accordance with applicable data protection and research ethics principles. The PAN12 corpus is a publicly available research dataset with established usage guidelines. Real conversation datasets used in the study are anonymized by removing or replacing personally identifiable information, including usernames and other identifying details. To rigorously protect user privacy and conform to ethical data standards, the study ensures that all sensitive information—such as real names, contact details, precise location identifiers, and personal accounts—will be strictly redacted and completely anonymized prior to any data processing or model training. 

The study does not involve direct interaction with real users. The prototype is evaluated offline using dataset records, including PAN12-derived data, anonymized real conversation data, and synthetically generated annotated chat data. Synthetic data is used only for controlled research purposes, particularly to represent underrepresented grooming-related patterns and evasion behaviors. 

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
