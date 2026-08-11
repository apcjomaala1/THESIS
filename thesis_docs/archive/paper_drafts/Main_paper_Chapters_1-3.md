*Enhancing Chat Moderation System: Through AI\-Based Behavioral and Contextual Analysis*

 

A Thesis Proposal Submitted to the Faculty 

of the School of Computing and Information Technologies

Asia Pacific College, Makati City

 

 

In Partial Fulfillment of the Requirements of the subject

THESIS1

 

 

By

Justin Bryden G\. Arroco 

Don Victor L\. Idos

John Michael O\. Maala

Andrei Luis M\. Torres

 

 

 

 

 

 

 

 

 

 

# __I\. Introduction__

## __1\.1 Background of the Study__

The rapid growth of online multiplayer games and interactive digital platforms has led to the widespread use of real\-time chat systems as a primary mode of communication among users\. These systems enable collaboration, social interaction, and community building; however, they also introduce significant risks related to harmful user behavior\. Among these, grooming\-related interactions have become increasingly prevalent \[1\], \[2\], \[3\]\. Existing moderation approaches in many platforms rely heavily on keyword\-based filtering and user reporting mechanisms, which are often insufficient in addressing these complex and context\-dependent threats \[4\], \[5\]\.

Traditional chat moderation systems primarily focus on detecting explicit keywords or predefined patterns\. While effective in identifying straightforward violations such as profanity, these systems are easily bypassed through obfuscation techniques, including altered spellings, special characters, or coded language \[6\], \[7\], \[8\]\. More critically, they lack the ability to understand conversational context, intent, and behavioral progression over time—key elements in identifying grooming\-related interactions \[2\], \[9\]\. Additionally, reliance on manual reporting introduces delays in response, allowing harmful interactions to persist before appropriate action is taken \[5\]\.

A critical limitation of existing moderation approaches is their inability to detect a sufficient number of harmful interactions, particularly grooming, resulting in a high number of missed cases \(false negatives\)\. This highlights the need for approaches that improve detection coverage, particularly by increasing recall and reducing false negatives in identifying harmful interactions\.

Recent advancements in artificial intelligence, particularly in machine learning and natural language processing, provide opportunities to enhance moderation systems beyond static keyword detection \[10\]\. By incorporating behavioral pattern recognition and contextual analysis, AI\-driven systems can identify subtle and evolving forms of harmful communication \[9\]\. These approaches enable the detection of suspicious interaction patterns across conversations, rather than relying solely on isolated messages, thereby improving both accuracy and timeliness of moderation\.

This study proposes the development of an AI\-powered moderation system designed to augment existing chat filtering and reporting mechanisms\. The system leverages machine learning, natural language processing, and behavioral pattern analysis to detect grooming\-related interactions within chat environments\. By combining content\-level analysis with user behavior modeling, the proposed approach aims to address the limitations of current moderation systems and contribute to safer and more responsive digital communication platforms\. 

Unlike traditional moderation systems that analyze messages in isolation, the proposed approach integrates conversational context and behavioral pattern tracking across multiple interactions to enable earlier and more accurate detection of grooming\-related interactions\. Grooming is prioritized due to its reliance on contextual and behavioral progression, making it a suitable case for evaluating the effectiveness of the proposed approach\.

The system leverages machine learning, natural language processing, and behavioral pattern analysis to detect grooming\-related interactions within chat environments\. By combining content\-level analysis with user behavior modeling, the proposed approach aims to address the limitations of current moderation systems and contribute to safer and more responsive digital communication platforms\.

## __1\.2 Statement of the Problem__

Existing chat moderation systems are widely used, yet harmful interactions such as grooming\-related interactions persist \[1\]\[2\]\[3\]\. Current approaches rely on keyword‑based filtering, rule‑based systems, and user reporting, which are often ineffective in detecting context‑dependent behaviors \[4\]\[5\]\. These systems analyze messages in isolation and fail to capture conversational context and behavioral patterns over time \[2\]\[9\]\.

Reliance on user reporting also results in delayed and reactive moderation, increasing exposure to harmful interactions \[5\]\. This highlights the need for more proactive and context‑aware solutions\. 

This study explores the use of artificial intelligence, particularly machine learning and natural language processing, to enhance chat moderation through contextual analysis and behavioral pattern recognition \[9\]\[10\]\.

This study seeks to answer the following questions:

1. How effective are existing chat moderation systems in detecting grooming\-related interactions? 
2. What are the limitations of keyword\-based and rule\-based moderation approaches in handling context\-dependent communication? 
3. How can machine learning and natural language processing be utilized to analyze behavioral patterns and conversational context in chat systems? 
4. To what extent can an AI\-driven moderation system improve detection performance, particularly in terms of recall and reduction of false negatives, compared to existing approaches?

## __1\.3 Objectives of the Study__

This section outlines the goals of the research\. It includes:

General Objective: Develop an AI\-powered moderation module that enhances existing chat moderation systems by incorporating behavioral pattern analysis and contextual understanding to detect grooming\-related interactions in chat environments\.

- Specific Objectives \- This study aims:
	1. Evaluate the effectiveness of existing chat moderation systems in detecting grooming\-related interactions\.
	2. Identify the limitations of keyword‑based and rule‑based moderation approaches in handling context‑dependent and evolving chat conversations\.
	3. Design an AI‑based chat moderation module that applies machine learning and NLP techniques to analyze behavioral patterns and conversational context across multiple chat interactions\.
	4. Assess the improvement in detecting harmful interactions achieved by the proposed AI‑driven moderation system compared to traditional moderation approaches\.
	5. Improve the detection performance of harmful interactions by increasing recall and reducing false negatives compared to keyword\-based and report\-driven moderation approaches\.

## __1\.4 Scope and Limitations__

### 1\.4\.1 Scope of the Study

The study includes a comparative analysis with existing moderation approaches, specifically a keyword\-based moderation system, using the same dataset to evaluate improvements in recall and reduction of false negatives\. The proposed module is designed to be platform\-independent and is intended for future integration into various chat\-based environments\. Rather than replacing existing moderation mechanisms, the system aims to augment current approaches by introducing behavioral pattern analysis and contextual understanding\.

The system utilizes natural language processing techniques to analyze chat messages and incorporates machine learning models to identify patterns across conversations\. It is designed to track user interactions over time and detect behavioral indicators associated with grooming\-related interactions\. The module is designed to support real\-time analysis, enabling the identification of suspicious interaction patterns as they develop\.

For evaluation purposes, the system is tested using a combination of publicly available datasets and simulated chat data\. The study includes a comparative analysis with existing moderation approaches to demonstrate the additional capabilities introduced by the proposed module, particularly in handling context\-dependent and behavior\-based threats\.

### 1\.4\.2 Limitations of the Study

This study is limited to the development of a prototype system and does not involve full deployment in a live chat environment\. The scope is further limited to grooming\-related interactions\. As such, the system will not be tested with real users, and its performance is evaluated only through controlled datasets and simulations\.

The study focuses specifically on detecting grooming\-related interactions in English\-language chat data\. 

The study builds upon pre\-trained machine learning models and libraries, which are further adapted and fine\-tuned for the specific task of detecting grooming\-related interactions\. As a result, system performance is influenced by the capabilities and limitations of these underlying models\.

Additionally, while the module is designed to support real\-time analysis, the implementation is conducted within a simulated environment\. Actual performance in real\-world deployment may vary depending on system integration, scalability, and data variability\. The study also does not account for all possible variations in language, cultural context, or evolving evasion techniques used by malicious users\.

## __1\.5 Significance of the Study__

This section explains the importance and potential impact of the research, identifying key beneficiaries and contributions across multiple domains\.

### 1\.5\.1 Academic Contribution

This research contributes to the academic field of computer science, artificial intelligence, and cybersecurity by advancing the understanding of AI\-driven content moderation\. The proposed system bridges a gap in existing literature by demonstrating how machine learning and natural language processing can be effectively combined with behavioral pattern analysis to detect nuanced forms of harmful communication\. This work provides a novel framework for contextual analysis in chat systems that goes beyond traditional keyword\-based approaches\. The findings will be valuable for researchers exploring AI applications in safety and security, offering insights into feature extraction techniques, model architecture, and evaluation methodologies for detecting complex communication patterns\. Additionally, this study contributes to theoretical knowledge in understanding grooming\-related interactions in digital environments, providing empirical evidence on the effectiveness of AI\-driven solutions in this domain\.

 

### 1\.5\.2 Industry and Practical Applications

For the technology industry and online platform providers, this research has significant practical implications\. Chat\-based platforms, gaming communities, social networks, and collaborative tools can leverage the proposed moderation module to enhance user safety and platform integrity\. By automating the detection of harmful interactions, platforms can reduce the burden on manual moderation teams, enabling them to focus on complex cases requiring human judgment\. The real\-time analysis capability of the system allows for immediate detection and flagging of suspicious behavior, reducing response time and limiting prolonged exposure to harmful interactions\. This is particularly critical for platforms serving vulnerable user populations, including minors\. Furthermore, the proposed system can be integrated into existing infrastructure without replacing current filtering mechanisms, offering a scalable and non\-disruptive enhancement to platform safety\. The adoption of such advanced moderation techniques positions platforms as responsible actors in digital safety, potentially building user trust and reducing legal liabilities\.

### 1\.5\.3 Societal Benefits

Beyond academia and industry, this research has direct societal benefits\. Online harassment and grooming pose serious threats to user well\-being, particularly affecting vulnerable populations such as children, adolescents, and individuals with limited digital literacy\. By improving detection mechanisms, this study contributes to creating safer online environments where users can interact with reduced fear of exploitation or harm\. The development of effective AI\-driven moderation tools can help prevent real\-world harm that originates from online interactions, including trauma, financial loss, and abuse\. Furthermore, the accessibility and scalability of the proposed solution mean that smaller platforms and communities with limited moderation resources can also implement advanced safety measures, democratizing access to robust content moderation technology\.

 

### 1\.5\.4 Implications for Future Research

This research establishes a foundation for future investigations into AI\-powered moderation systems and behavioral analysis in digital communication\. The methodologies, datasets, and frameworks developed in this study can be extended to detect other forms of harmful communication, including hate speech, misinformation, and cyberbullying\. The techniques presented can be adapted for other communication platforms beyond chat systems, such as email, messaging applications, forums, and social media\. Additionally, this work opens avenues for research into more sophisticated machine learning models, including deep learning approaches and transfer learning techniques, that could further improve detection accuracy\. Future research can also explore the integration of multimodal analysis \(text, images, video\) for comprehensive content moderation\. The study also highlights the importance of addressing challenges such as linguistic diversity, cultural context, and adversarial evasion techniques, which present opportunities for continued research and innovation in the field\.

## __1\.6 Definition of Terms__

Artificial Intelligence \(AI\) \- The development and application of computer systems designed to perform tasks that typically require human intelligence, including learning from experience, recognizing patterns, and making decisions\.

Behavioral Pattern Analysis \- A technique that examines sequences and trends in user interactions over time to identify recurring behaviors, including suspicious or harmful activity patterns\.

Chat Moderation System \- An automated or semi\-automated system designed to monitor, filter, and regulate user communications in real\-time chat environments to prevent harmful interactions\.

Contextual Analysis \- The examination of messages or interactions within their broader communicative context, considering surrounding messages, conversation history, and conversational intent rather than analyzing content in isolation\.

Grooming \- A manipulative process in which a malicious user gradually builds trust with a target, typically a minor, to lower their defenses and facilitate exploitation or abuse\.

Machine Learning \- A subset of artificial intelligence that enables computer systems to learn patterns from data and improve their performance without being explicitly programmed for every specific task\.

Natural Language Processing \(NLP\) \- A field of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language in a meaningful and contextually relevant manner\.

Obfuscation Techniques \- Methods used to conceal or disguise harmful content, such as altered spellings, special characters, coded language, or other modifications designed to bypass keyword\-based filters\.

Predatory Behavior \- Actions or communication patterns intended to exploit, manipulate, or harm other users, particularly targeting vulnerable individuals\.

Real\-time Analysis \- The processing and evaluation of data as it is generated or received, without significant delays, enabling immediate detection and response\.

User Reporting Mechanism \- A system feature that allows chat platform users to report suspicious, harmful, or policy\-violating behavior to moderators or automated systems for review and action\.

# II\. RELATED WORK

This chapter presents a critical synthesis of existing literature and empirical studies relevant to the development of AI‑powered moderation systems for detecting harmful interactions in real‑time chat environments\. The review focuses on recent advancements in natural language processing \(NLP\), machine learning‑based moderation frameworks, and behavioral analysis techniques used to identify grooming\-related interactions and related harmful communication patterns‑related interactions in online platforms\.

The purpose of this chapter is to establish the scholarly context of the study, examine existing moderation methodologies, and identify key research gaps that justify the development of a behavioral and context‑aware moderation module\.

## 2\.1 Review of Related Literature

Recent research in chat moderation has shifted from traditional rule‑based filtering toward AI‑driven contextual analysis models\. Earlier moderation approaches relied primarily on keyword blacklists to detect violations such as profanity or explicit harmful language\. However, these systems are limited in their ability to interpret conversational intent, allowing malicious users to bypass filters through techniques such as altered spellings, coded language, or multi‑message grooming strategies\.

Modern studies emphasize the importance of contextual understanding in detecting harmful user behavior\. SchurgerFoy et al\. \(2025\) demonstrated that approximately __67% of toxic messages in multiplayer gaming environments are context dependent__, meaning that they appear harmless when analyzed as isolated text but become problematic when examined within conversational history\.   
Similarly, Yang et al\. \(2023\) introduced the *ToxBuster* architecture, which incorporates message history and speaker metadata into text classification models\. Their results showed significant improvements in detection accuracy, achieving up to __95% precision__ in identifying harmful interactions through sequence\-based moderation rather than single message evaluation\. 

These findings suggest that integrating conversational context and historical behavioral patterns improves moderation effectiveness compared to static filtering methods\. Transformer‑based NLP architectures such as BERT, RoBERTa, and DistilBERT have consequently emerged as standard tools for understanding linguistic patterns in chat environments\. 

Furthermore, longitudinal behavioral analysis has been shown to be a strong predictive indicator of future harmful activity\. Studies indicate that tracking interaction patterns over time can achieve up to __74% balanced accuracy in forecasting future toxic behavior__, reinforcing the importance of behavioral modeling in proactive moderation systems\. 

Despite these advancements, current moderation systems remain constrained by their reliance on legacy datasets such as PAN12, which may not adequately represent modern online communication styles, slang, or evolving evasion techniques used by malicious actors\. 

## 2\.2 Related Studies

Several empirical studies have explored the application of artificial intelligence in detecting grooming\-related interactions within online environments\.

Street et al\. \(2024\) developed a transformer‑based classification approach using BERT and RoBERTa models to identify online grooming interactions by analyzing conversational roles between adults and minors\. Their contextual determination framework improved cross‑dataset robustness in identifying suspicious communication patterns across multiplayer gaming chats\. 

Faraz et al\. \(2024\) proposed *Protectbot*, an AI‑based chatbot that actively simulates user interaction to expose predatory intent\. Utilizing the DialoGPT language model combined with intent classifiers such as fastText and Support Vector Machines, the system achieved an __F‑score of 0\.99__ in detecting grooming behavior within simulated chat environments\. 

Comparative evaluations conducted by Tereshchenko and HÃ¤mÃ¤lÃ¤inen \(2025\) revealed that lightweight transformer models such as DistilBERT provide an optimal balance between computational efficiency and moderation accuracy in high‑volume chat systems\. Their findings showed that while large generative language models offer improved linguistic nuance, they introduce latency issues that hinder real‑time deployment in live environments\. 

In addition, qualitative analyses of real‑time moderation frameworks within child‑centric platforms such as Roblox have highlighted sociotechnical challenges including algorithmic bias, cultural sensitivity issues, and limited transparency in automated decision‑making processes\. 

While these studies demonstrate the effectiveness of AI‑based moderation tools, most implementations analyze localized chat contexts within single sessions\. As a result, they often fail to model behavioral trajectories that evolve across multiple conversations or platforms over time\.

## 2\.3 Theoretical Background

The theoretical foundation of this study is based on advancements in machine learning‑driven natural language processing and behavioral pattern recognition\.

Recent moderation frameworks adopt __sequence modeling techniques__, which evaluate conversations as evolving interaction chains rather than isolated textual inputs\. This approach allows systems to detect behavioral trajectories characteristic of grooming related activities, such as gradual trust‑building, self‑disclosure, or attempts to isolate users within private communication channels\. 

However, current methodologies often evaluate text‑based data in isolation and neglect multimodal behavioral indicators such as spatial interaction patterns or economic incentives within digital environments\. 

These limitations reveal a methodological gap in existing moderation systems, particularly in detecting slow‑developing threats such as grooming behavior, which typically manifest through subtle interaction patterns across multiple messages rather than explicit rule violations\. 

To address these challenges, contemporary research recommends hybrid moderation frameworks combining automated AI‑based triage with human‑in‑the‑loop \(HITL\) review mechanisms\. Such layered architectures enable high‑speed real‑time flagging of suspicious interactions while preserving human oversight for nuanced adjudication and minimizing algorithmic bias\. 

This study adopts these theoretical principles in the development of a behavioral‑contextual moderation module designed to enhance existing chat moderation systems by integrating conversational history analysis and user interaction tracking\.__ __

# III\. METHODOLOGY

## __3\.1 Research Design__

This study employs a developmental and experimental research design\. The primary objective is to design, implement, and evaluate an AI\-powered chat moderation module for grooming\-related interaction detection\. The current implemented prototype progresses across three phases: \(1\) data preparation and preprocessing, \(2\) message\-level model development with DistilBERT, and \(3\) comparative evaluation against a keyword\-based moderation baseline\. Conversation\-level trajectory modeling is implemented first as feature\-based scoring, while LSTM\-based sequence modeling is treated as a proposed enhancement\.

The system does not replace existing moderation mechanisms\. Instead, it functions as an augmentation layer that combines message\-level DistilBERT risk scoring with conversation\-level trajectory indicators alongside rule\-based filtering\.

The system is validated offline using real datasets available in the current study environment, primarily PAN12\-derived data and derived splits\. Performance is evaluated quantitatively using classification metrics and time\-to\-detection, which reflects the system's ability to identify harmful conversations early\.

## __3\.2 System Architecture__

The implemented system consists of two processing stages that operate in sequence: a message\-level classification pipeline and a conversation\-level aggregation stage\. Together, these components assess both individual message content and conversation progression over time\.

### __3\.2\.1 Message\-Level Pipeline__

Each incoming message is independently processed by a fine\-tuned DistilBERT classifier\. DistilBERT, a distilled variant of the BERT transformer architecture, encodes each message into a 768\-dimensional semantic embedding that captures contextual meaning, intent, and linguistic patterns relevant to grooming\-related communication\. This embedding is passed through a classification head that outputs a per\-message risk score between 0 and 1, representing the probability that the message contains predatory content\.

DistilBERT is selected over alternatives such as TF\-IDF or Bag\-of\-Words representations because semantic similarity in vector space corresponds to semantic similarity in meaning\. Messages with different surface forms but similar predatory intent — for example, "let's talk somewhere private" and "don't tell your parents about this" — are encoded as nearby vectors, enabling the classifier to generalize beyond surface\-level keyword patterns\. This is particularly important given that malicious actors frequently employ obfuscation techniques to bypass keyword\-based filters\.

### __3\.2\.2 Conversation\-Level Pipeline__

The sequence of per\-message risk scores produced by the message\-level pipeline is grouped by conversation ID and processed as an ordered time series\. In the current implementation, trajectory risk is computed using engineered per\-turn features and a weighted scoring rule\. An LSTM sequence model is retained as a proposed extension for later experimentation\.

Conversations vary in length from a few messages to hundreds of turns, so the implemented trajectory stage uses incremental, turn\-by\-turn feature updates that preserve sequence order without requiring a recurrent network in the first prototype\.

A critical design consideration is score suppression: a malicious actor may tone down language after suspicious behavior to avoid detection\. To address this, the implemented trajectory stage tracks explicit features such as peak score so far, spike count, score\-change rate, and score drop after spikes\.

### __3\.2\.3 Full System Flow__

The complete pipeline from incoming message to moderation decision operates as follows\. Each message is scored by DistilBERT, appended to its conversation history, and used to update trajectory features\. A trajectory score is then computed using a weighted combination of current and historical indicators\. If this score exceeds a configurable threshold, the conversation is flagged and the first flagged turn is recorded as time\-to\-detection\. Human\-in\-the\-loop retraining and production feedback queues are proposed as future enhancements\.

## __3\.3 Data Collection and Dataset__

The study utilizes publicly available datasets in the current implementation, with PAN12\-derived data as the primary source for training, validation, and testing\.

The primary public benchmark used is the PAN12 Sexual Predator Identification corpus, a widely adopted reference dataset in grooming detection research\. This corpus contains real chat logs with conversation\-level labels identifying predatory interactions\. It is used to establish baseline performance and enable comparison with prior work in the literature\.

The working dataset contains per\-message labels and conversation IDs\. This structure supports message\-level training and reconstruction of ordered conversation sequences for trajectory feature extraction\.

Where necessary, simulated chat data is generated to supplement training examples for underrepresented behavioral patterns, particularly conversations exhibiting spike\-then\-drop score patterns indicative of deliberate evasion\.

Table 3\.1 summarizes the datasets used in this study\.

__Dataset__

__Source__

__Size__

__Label Type__

PAN12 Sexual Predator Dataset

PAN12 Competition Corpus

Conversation count determined from the PAN12\-derived split used in this study

Per\-conversation

Study Dataset \(provided\)

Institutional/platform logs \(proposed future data source\)

Variable

Per\-message \+ Conversation ID

Simulated Chat Data

Synthetic data \(proposed future augmentation; not required in current prototype\)

Supplementary

Per\-message

*Table 3\.1\. Summary of Datasets Used*

## __3\.4 Data Preprocessing__

Raw chat data undergoes a multi\-stage preprocessing pipeline before being used for model training or inference\.

At the message level, text is cleaned to remove formatting artifacts, normalize punctuation, and standardize character encodings\. Obfuscated terms — such as altered spellings or special character substitutions — are normalized using a custom lexical mapping built from known evasion patterns documented in the literature\. Messages are then tokenized using the DistilBERT tokenizer with a maximum token length of 512, consistent with the model's architectural constraints\.

At the conversation level, messages are grouped by conversation ID and sorted chronologically by timestamp to reconstruct the true sequential order of each conversation\. Each conversation is then transformed into a sequence of training snapshots, one per message turn\. The label assigned to each snapshot is defined as whether any predatory message has occurred in the conversation up to and including that turn\. This formulation — sometimes called a cumulative label — enables the model to learn when in a conversation danger begins to emerge, rather than only whether a conversation eventually becomes harmful\. It is critical to note that this cumulative label is a training signal only; the model's actual output is a continuous risk score, not a binary classification\.

## __3\.5 Feature Engineering__

Two categories of features are extracted for each conversation snapshot: message\-level features derived from the DistilBERT encoder, and trajectory\-level features derived from the evolving sequence of risk scores across turns\.

Message\-level features consist primarily of the 768\-dimensional embedding produced by DistilBERT for each individual message\. These embeddings encode semantic content, contextual intent, and linguistic register in a continuous vector space where semantically similar messages occupy proximate positions regardless of surface\-level differences in wording\.

Trajectory\-level features are computed over conversation history up to the current turn and used in a weighted trajectory scoring function\. These features capture behavioral progression and are designed to reduce sensitivity to deliberate score suppression\.

Table 3\.2 summarizes the features used in the trajectory model\.

__Feature__

__Description__

__Level__

DistilBERT message embedding

768\-dimensional semantic vector per message

Message

Per\-message risk score

Output of existing predatory classifier \(0–1\)

Message

Peak score so far

Highest risk score seen at any prior turn

Trajectory

Spike\-then\-drop pattern

Detection of deliberate score suppression behavior

Trajectory

Rate of score change

Delta between consecutive message risk scores

Trajectory

Topic drift

Cosine distance between early and recent message embeddings

Trajectory

Turn\-taking imbalance

Ratio of word count between participants

Structural

Spike count

Number of times score exceeded risk threshold

Trajectory

*Table 3\.2\. Trajectory Features Extracted Per Conversation Snapshot*

## __3\.6 Model Development__

### __3\.6\.1 Message\-Level Classifier__

The message\-level classifier is based on DistilBERT, a transformer model pre\-trained on large\-scale English text corpora and fine\-tuned for binary sequence classification on the study's labeled message dataset\. Fine\-tuning adapts the pre\-trained model's general language representations to the specific linguistic patterns of grooming\-related communication, including subtle forms of trust\-building, isolation attempts, and PII solicitation\.

Training uses a binary cross\-entropy loss function\. Given the expected class imbalance between predatory and non\-predatory messages, the training procedure applies class\-weight balancing to prevent the model from biasing toward the majority class\. The classifier outputs a scalar risk score between 0 and 1 for each message, representing the estimated probability of predatory content\.

### __3\.6\.2 Trajectory Scoring Model and LSTM Extension __

The current trajectory model is a feature\-based scoring approach that takes as input per\-message DistilBERT risk scores and per\-turn trajectory features \(for example: peak score so far, spike count, score\-change rate, score drop after spike, average score so far, turn number, and conversation length so far\)\. A weighted combination of these signals produces a trajectory risk score between 0 and 1 at each turn\. LSTM\-based sequence learning remains a proposed extension after baseline trajectory scoring is fully validated\.

The current prototype emphasizes early detection operationally by recording the first turn where trajectory score exceeds threshold \(time\-to\-detection\)\. A formal time\-aware loss is reserved for future LSTM training work\.

The trajectory risk score is the primary output consumed by the moderation system\. A configurable threshold determines when a conversation is flagged for human review\. The threshold is tuned during validation to optimize recall — the study's primary metric — while maintaining a false positive rate that is operationally sustainable for the moderation team\.

### __3\.6\.3 Baseline Comparison Model__

To evaluate the improvement introduced by the proposed system, a keyword\-based moderation baseline is implemented using the same dataset\. The baseline flags messages containing terms from a predefined grooming\-related keyword lexicon\. Conversations in which any message is flagged by the keyword system are marked as harmful\. This mirrors the behavior of conventional rule\-based moderation systems and serves as the comparison point for all evaluation metrics\.

## __3\.7 System Implementation__

The system is implemented in Python using Hugging Face Transformers for DistilBERT fine\-tuning and inference\. Conversation\-level processing in the current prototype is performed offline by grouping messages by conversation ID and sorting by turn order to compute trajectory features and scores\.

The moderation decision engine reads the trajectory score at each turn and compares it against a configured threshold\. Flagged conversations are recorded with their first flagged turn to support comparative evaluation and early\-detection analysis in the offline prototype\.

The implementation is designed to be platform\-independent at the data\-processing level\. A REST API integration layer is proposed for future deployment work\.

## __3\.8 Evaluation Metrics__

Evaluation is conducted on a held\-out test set not seen during training\. All metrics are computed at the conversation level — a conversation is considered correctly detected if the trajectory risk score exceeds the flagging threshold at any point before the conversation's final turn\.

Given the study's stated goal of reducing false negatives and improving recall compared to existing moderation approaches, recall is treated as the primary evaluation metric\. Secondary metrics provide a complete picture of system performance and operational feasibility\.

Table 3\.3 summarizes the evaluation metrics used and their rationale\.

__Metric__

__Rationale__

Recall

Primary metric — measures coverage of detected harmful conversations\. Reducing false negatives is the core objective\.

Precision

Controls false positive rate, which determines moderator workload\.

F1\-Score

Harmonic mean balancing precision and recall for overall model quality\.

AUC\-ROC

Discriminative ability of the trajectory risk score across all thresholds\.

Time\-to\-Detection

Turn number at which the model first correctly flags a harmful conversation\. Earlier detection indicates stronger trajectory modeling\.

Baseline Comparison

All metrics computed against keyword\-based moderation system on the same dataset to demonstrate improvement\.

*Table 3\.3\. Evaluation Metrics and Rationale*

## __3\.9 Testing and Validation__

The dataset is split into training, validation, and test sets at the conversation level to prevent leakage across splits\. The validation set is used for hyperparameter tuning, including trajectory\-score weights and flagging threshold, while the test set is reserved for final evaluation\.

Model robustness is additionally tested against two specific adversarial conditions identified as critical limitations of prior systems: \(1\) conversations in which the suspect deliberately reduces language risk after an initial spike, and \(2\) conversations that employ obfuscation techniques such as altered spellings or coded language\. Performance on these subsets is reported separately to characterize the system's resilience to evasion strategies\.

The proposed system's metrics are compared directly against a keyword\-based baseline on the same test set\. Statistical significance testing with McNemar's test is proposed as future analysis once final prediction pairs are frozen\.

## __3\.10 Ethical Considerations__

All datasets used in this study are handled in accordance with applicable data protection principles\. The PAN12 corpus is a publicly available research dataset with established usage guidelines\. Additional institutional datasets, if later incorporated, will be used under corresponding governance constraints\.

The study does not involve direct interaction with real users\. The current prototype is evaluated offline on dataset records\. Synthetic data generation and live moderator interface components are optional future extensions\.

The system is designed as a support tool for human moderators rather than an autonomous decision\-making system\. All flagging decisions are subject to human review before any action is taken against a user account, preserving human oversight and minimizing the risk of algorithmic harm to falsely flagged users\.

## __3\.11 Limitations of the Methodology__

Several limitations apply to the methodology described in this chapter\. First, the system is evaluated in a simulated environment and does not reflect the full complexity of real\-world deployment, including latency constraints, concurrent conversation volume, and integration with live platform infrastructure\.

Second, the study is scoped to English\-language chat data\. The linguistic patterns and evasion techniques captured by the trained models may not generalize to other languages or multilingual conversations without retraining on appropriate corpora\.

Third, conversation\-level scoring performance is bounded by the quality of per\-message risk scores produced by the message\-level classifier\. Errors or systematic biases in message\-level outputs propagate into trajectory features and downstream conversation flags\.

Fourth, while the spike\-then\-drop trajectory feature partially addresses adversarial score suppression, the system may not fully account for sophisticated, long\-horizon evasion strategies in which a suspect deliberately maintains low risk scores across many turns before executing a harmful intent in a single message\. This represents an open challenge for future work\.

## __3\.12 Summary of Methodology__

This chapter described the research design, system architecture, data preparation, feature engineering, model development, implementation, and evaluation strategy for a trajectory\-aware grooming detection prototype\.

The core contribution of the implemented methodology is a two\-stage architecture: a DistilBERT message\-level classifier, followed by conversation\-level trajectory feature scoring that accumulates risk signals across turns\. This architecture addresses limitations of purely keyword\-based systems by modeling conversational progression and score\-suppression patterns\. An LSTM trajectory model is retained as a future enhancement\.

The system is evaluated against a keyword\-based baseline using recall\-oriented metrics, consistent with the objective of reducing false negatives in harmful interaction detection\. Human\-in\-the\-loop feedback and continuous retraining are proposed future enhancements for deployment\-stage adaptation\.

# References

\[1\] “Parents’ Perspectives of Pre\-Pubescent Aged Children’s Access to Online Gaming: Risks of Exposure to Grooming,” Purdue University Global Research Repository\. \[Online\]\. Available: [https://purdueglobal\.dspacedirect\.org/items/c7f44da9\-a59f\-46a5\-a2e1\-cbb560bfe2d9](https://purdueglobal.dspacedirect.org/items/c7f44da9-a59f-46a5-a2e1-cbb560bfe2d9)\. \[Accessed: Apr\. 13, 2026\]\.

\[2\] “Enhanced Online Grooming Detection Employing Context Determination and Message\-Level Analysis,” arXiv preprint arXiv:2409\.07958\. \[Online\]\. Available: [https://arxiv\.org/abs/2409\.07958](https://arxiv.org/abs/2409.07958)\. \[Accessed: Apr\. 13, 2026\]\.

\[3\] “Enhancing Child Safety in Online Gaming: The Development and Application of Protectbot, an AI\-Powered Chatbot Framework,” Information, vol\. 15, no\. 4, 2024\. \[Online\]\. Available: [https://www\.mdpi\.com/2078\-2489/15/4/233](https://www.mdpi.com/2078-2489/15/4/233)\. \[Accessed: Apr\. 13, 2026\]\.

\[4\] Roblox Corporation, “Roblox Launches Real\-Time Chat Rephrasing to Maintain Civility and Gameplay Flow,” 2026\. \[Online\]\. Available: [https://ir\.roblox\.com/news/news\-details/2026/Roblox\-Launches\-Real\-Time\-Chat\-Rephrasing\-to\-Maintain\-Civility\-and\-Gameplay\-Flow/default\.aspx](https://ir.roblox.com/news/news-details/2026/Roblox-Launches-Real-Time-Chat-Rephrasing-to-Maintain-Civility-and-Gameplay-Flow/default.aspx)\. \[Accessed: Apr\. 13, 2026\]\.

\[5\] “Efficient Toxicity Detection in Gaming Chats: A Comparative Study of Embeddings, Fine\-Tuned Transformers and LLMs,” arXiv preprint arXiv:2510\.17924\. \[Online\]\. Available: [https://arxiv\.org/abs/2510\.17924](https://arxiv.org/abs/2510.17924)\. \[Accessed: Apr\. 13, 2026\]\.

\[6\] “Towards Detecting Contextual Real\-Time Toxicity for In\-Game Chat,” arXiv preprint arXiv:2310\.18330\. \[Online\]\. Available: [https://arxiv\.org/abs/2310\.18330](https://arxiv.org/abs/2310.18330)\. \[Accessed: Apr\. 13, 2026\]\.

\[7\] “AI Moderation and Legal Frameworks in Child\-Centric Social Media: A Case Study of Roblox,” Laws, vol\. 14, no\. 3, 2025\. \[Online\]\. Available: [https://www\.mdpi\.com/2075\-471X/14/3/29](https://www.mdpi.com/2075-471X/14/3/29)\. \[Accessed: Apr\. 13, 2026\]\.

\[8\] “Online Hate Speech and Platform Moderation,” SAGE Journals\. \[Online\]\. Available: [https://journals\.sagepub\.com/doi/full/10\.1177/2053951717736335](https://journals.sagepub.com/doi/full/10.1177/2053951717736335)\. \[Accessed: Apr\. 13, 2026\]\.

\[9\] “Context\-Aware Toxicity Detection in Multiplayer Games: Integrating Domain\-Adaptive Pretraining and Match Metadata,” alphaXiv\. \[Online\]\. Available: [https://www\.alphaxiv\.org/overview/2504\.01534](https://www.alphaxiv.org/overview/2504.01534)\. \[Accessed: Apr\. 13, 2026\]\.

\[10\] “Artificial Intelligence and Pattern Recognition Applications,” Sensors, vol\. 16, no\. 8, 2016\. \[Online\]\. Available: [https://www\.mdpi\.com/1424\-8220/16/8/1264](https://www.mdpi.com/1424-8220/16/8/1264)\. \[Accessed: Apr\. 13, 2026\]\.

