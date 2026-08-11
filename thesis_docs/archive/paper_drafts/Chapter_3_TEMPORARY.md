3.1 Research Design

This study employs a developmental and experimental research design. The
primary objective is to design and evaluate an AI-powered chat
moderation prototype for detecting grooming-related interactions. The
study focuses on combining message-level contextual analysis using
DistilBERT with conversation-level behavioral trajectory scoring to
improve moderation performance beyond traditional keyword-based
approaches.

The prototype consists of three primary stages: (1) data collection and
preprocessing, (2) message-level model development using DistilBERT, and
(3) comparative evaluation against a rule-based keyword moderation
baseline. In addition, the study proposes a conversation-level
trajectory scoring component that utilizes behavioral indicators derived
from message risk progression across conversations. An LSTM-based
sequence modeling approach is also explored as a proposed extension for
future development.

Rather than replacing existing moderation systems, the proposed approach
is intended to augment current moderation methods by incorporating
contextual NLP analysis together with behavioral pattern tracking. The
study combines machine learning-based risk scoring with rule-based
moderation indicators to evaluate whether contextual and behavioral
analysis can improve detection performance.

The system is validated offline using a combination of PAN12-derived
datasets, real conversation datasets, and synthetically generated
annotated chat data prepared for the study. Performance is evaluated
quantitatively using classification metrics such as recall, precision,
F1-score, and comparative analysis against traditional moderation
approaches.

3.2 Relevant Technology

3.2.1 Python Programming Language

Python is used as the primary programming language for the development
and evaluation of the proposed moderation module. It was selected due to
its extensive support for machine learning, natural language processing,
and data analysis through established libraries and frameworks.

3.2.2 Hugging Face Transformers and PyTorch

The study utilizes the Hugging Face Transformers library together with
the PyTorch deep learning framework for model training and inference.
These technologies provide pre-trained transformer architectures and
efficient tools for fine-tuning NLP models for text classification
tasks.

3.2.3 DistilBERT

DistilBERT serves as the primary message-level language model used in
the study. It is a lightweight transformer-based model derived from BERT
that retains strong contextual language understanding while reducing
computational requirements. The model is suitable for detecting
grooming-related interactions because it can analyze contextual meaning
rather than relying solely on keyword matching.

3.2.4 Development Environment

The prototype system is developed and tested using Jupyter Notebook and
Visual Studio Code within a Python-based experimental environment.
**\[REVISED\]** GPU acceleration is utilized during model training to
improve computational efficiency.

3.3 Data Collection and Processing

3.3.1 Data Collection

The study utilizes a combination of publicly available datasets, real
conversation datasets, and synthetically generated annotated chat data
for model training and evaluation.

The primary public benchmark used is the PAN12 Sexual Predator
Identification corpus, a widely adopted reference dataset in grooming
detection research. This corpus contains real chat logs with
conversation-level labels identifying predatory interactions and is used
to establish baseline performance and enable comparison with prior work
in the literature.

In addition to PAN12-derived data, the study incorporates real
conversation datasets collected and annotated for research purposes.
These datasets contain per-message labels and conversation identifiers,
enabling both message-level analysis and reconstruction of ordered
conversation sequences for behavioral and trajectory-based analysis.

The study also utilizes synthetically generated annotated chat data to
supplement underrepresented interaction patterns not sufficiently
represented in publicly available datasets. These synthetic
conversations are manually structured and annotated to simulate
grooming-related behaviors, conversational progression, obfuscation
techniques, and spike-then-drop interaction patterns associated with
deliberate moderation evasion.

All datasets are organized into a unified structure containing
conversation IDs, message order, participant identifiers, and annotation
labels to support preprocessing, feature engineering, model training,
and evaluation.

Table 3.1 summarizes the datasets used in this study.

  ----------------- ------------------------ ----------------- ------------------
  **Dataset**       **Source**               **Size**          **Label Type**

  PAN12 Sexual      PAN12 Competition Corpus Conversation      Per-conversation
  Predator Dataset                           count determined  
                                             from the          
                                             PAN12-derived     
                                             split used in     
                                             this study        

  Study Dataset     Institutional/platform   Variable          Per-message +
  (provided)        logs (proposed future                      Conversation ID
                    data source)                               

  Simulated Chat    Synthetic data (proposed Supplementary     Per-message
  Data              future augmentation; not                   
                    required in current                        
                    prototype)                                 
  ----------------- ------------------------ ----------------- ------------------

Table 3.1. Summary of Datasets Used

3.3.2 Data Preprocessing

The preprocessing procedures are applied to PAN12-derived datasets, real
conversation datasets, and synthetically generated annotated chat data
used for model training and evaluation.

At the message level, text is cleaned to remove formatting
inconsistencies, normalize punctuation, and standardize character
encoding. **\[REVISED\]** Obfuscated terms, such as altered spellings or
special-character substitutions commonly used to bypass moderation
systems, are normalized to their standard forms. Messages are then
tokenized using the DistilBERT tokenizer with a maximum token length of
512 tokens, consistent with the model's architectural constraints.

**\[REVISED\]** Following the data organization performed in Section
3.3.3, preprocessed messages are structured to support both
message-level classification and conversation-level behavioral scoring.

**\[REVISED\]** For trajectory-based analysis, conversation data is
represented as sequential conversation instances corresponding to
message turns. These instances capture how behavioral risk indicators
evolve throughout a conversation, enabling the trajectory scoring model
to analyze risk progression across the full interaction history.

3.3.3 Data Processing

The collected datasets undergo data processing to organize raw chat
records into a structured format suitable for analysis and model
training. Chat logs from different sources are standardized into a
unified dataset structure containing conversation identifiers, message
order, participant labels, timestamps where available, and annotation
labels.

Messages are grouped according to conversation ID to preserve
conversational continuity. Conversations are then arranged
chronologically to maintain the natural progression of interactions.
This organization enables both message-level analysis and
conversation-level behavioral analysis across multiple exchanges.

**\[REVISED\]** Annotation labels indicating predatory, suspicious, or
non-predatory behavior are associated with corresponding messages or
conversations. Synthetic annotated data generated for the study is also
integrated into the same dataset structure to maintain consistency
across all data sources.

The resulting processed datasets are stored in structured formats such
as CSV files to support preprocessing, feature engineering, model
training, and evaluation.

3.3.4 Feature Engineering

Two categories of features are extracted for each conversation snapshot:
message-level features derived from the DistilBERT encoder, and
trajectory-level features derived from the evolving sequence of risk
scores across turns.

Message-level features consist primarily of the 768-dimensional
embedding produced by DistilBERT for each individual message. These
embeddings encode semantic content, contextual intent, and linguistic
register in a continuous vector space where semantically similar
messages occupy proximate positions regardless of surface-level
differences in wording.

Trajectory-level features are computed over conversation history up to
the current turn and used in a weighted trajectory scoring function.
These features capture behavioral progression and are designed to reduce
sensitivity to deliberate score suppression.

Table 3.2 summarizes the features used in the trajectory model.

  ----------------------- ----------------------- -----------------------
  **Feature**             **Description**         **Level**

  DistilBERT message      768-dimensional         Message
  embedding               semantic vector per     
                          message                 

  Per-message risk score  Output of existing      Message
                          predatory classifier    
                          (0--1)                  

  Peak score so far       Highest risk score seen Trajectory
                          at any prior turn       

  Spike-then-drop pattern Detection of deliberate Trajectory
                          score suppression       
                          behavior                

  Rate of score change    Delta between           Trajectory
                          consecutive message     
                          risk scores             

  Topic drift             Cosine distance between Trajectory
                          early and recent        
                          message embeddings      

  Turn-taking imbalance   Ratio of word count     Structural
                          between participants    

  Spike count             Number of times score   Trajectory
                          exceeded risk threshold 
  ----------------------- ----------------------- -----------------------

Table 3.2. Trajectory Features Extracted Per Conversation Snapshot

3.3.5 Data Splitting

The processed dataset is divided into training, validation, and test
sets to support model development and evaluation. Splitting is performed
at the conversation level to prevent data leakage between datasets and
preserve the integrity of conversational context.

The training set is used for model learning, while the validation set is
used for threshold tuning and parameter adjustment. The test set is
reserved for final evaluation of the proposed moderation approach and
comparison against the rule-based baseline model.

This separation ensures that conversations used during evaluation are
not previously seen during training, allowing a more reliable assessment
of model performance.

3.4 Model Development

**3.4.1 Message-Level Classifier**

The message-level classifier is based on DistilBERT, a transformer model
pre-trained on large-scale English text corpora and fine-tuned for
binary sequence classification on the study\'s labeled message dataset.
Fine-tuning adapts the pre-trained model\'s general language
representations to the specific linguistic patterns of grooming-related
communication, including subtle forms of trust-building, isolation
attempts, and PII solicitation.

Training uses a binary cross-entropy loss function. Given the expected
class imbalance between predatory and non-predatory messages, the
training procedure applies class-weight balancing to prevent the model
from biasing toward the majority class. The classifier outputs a scalar
risk score between 0 and 1 for each message, representing the estimated
probability of predatory content.

\_\_3.4.2 Trajectory Scoring Model and LSTM Extension \_\_

The current trajectory model is a feature-based scoring approach that
takes as input per-message DistilBERT risk scores and per-turn
trajectory features (for example: peak score so far, spike count,
score-change rate, score drop after spike, average score so far, turn
number, and conversation length so far). A weighted combination of these
signals produces a trajectory risk score between 0 and 1 at each turn.
LSTM-based sequence learning remains a proposed extension after baseline
trajectory scoring is fully validated.

The current prototype emphasizes early detection operationally by
recording the first turn where trajectory score exceeds threshold
(time-to-detection). A formal time-aware loss is reserved for future
LSTM training work.

The trajectory risk score is the primary output consumed by the
moderation system. A configurable threshold determines when a
conversation is flagged for human review. The threshold is tuned during
validation to optimize recall --- the study\'s primary metric --- while
maintaining a false positive rate that is operationally sustainable for
the moderation team.

**3.4.3 Baseline Comparison Model**

To evaluate the improvement introduced by the proposed system, a
keyword-based moderation baseline is implemented using the same dataset.
The baseline flags messages containing terms from a predefined
grooming-related keyword lexicon. Conversations in which any message is
flagged by the keyword system are marked as harmful. This mirrors the
behavior of conventional rule-based moderation systems and serves as the
comparison point for all evaluation metrics.

3.5 Evaluation/Validation

3.5.1 Evaluation Metrics

The dataset is divided into training, validation, and test sets at the
conversation level to prevent data leakage across splits. The validation
set is used to tune model parameters, rule-based scoring weights, and
flagging thresholds, while the test set is reserved for final
evaluation.

**\[REVISED\]** The primary evaluation metrics used in this study are
recall, precision, and F1-score. Recall measures the proportion of
actual grooming-related conversations correctly identified by the system
and serves as the study\'s primary metric, given the high cost of missed
detections in a child safety context. Precision measures the proportion
of flagged conversations that are truly predatory, reflecting the
operational burden placed on human moderators. F1-score provides the
harmonic mean of recall and precision to summarize overall
classification performance. These metrics are computed on the held-out
test set for both the proposed system and the keyword-based baseline to
enable direct comparison.

3.5.2 Testing and Validation

**\[REVISED\]** Model robustness is evaluated using adversarial and
evasive conversation patterns identified as limitations of traditional
moderation systems. These include conversations containing obfuscated
text, altered spellings, coded language, and gradual behavioral
progression designed to reduce apparent message risk over time.
Additionally, conversations where risk indicators are distributed across
multiple turns rather than concentrated in individual messages are used
to assess the trajectory scoring component\'s ability to detect
escalation patterns.

**\[REVISED\]** The proposed approach is compared directly against the
keyword-based baseline using the same held-out test set. This comparison
evaluates whether the combination of DistilBERT-based message analysis
and conversation-level behavioral scoring achieves measurable
improvements in detection performance, with emphasis on recall
improvement and false-negative reduction.

**\[REVISED\]** Additional statistical analysis methods, such as
McNemar\'s test, are applied where sample sizes permit to determine
whether observed performance differences between the proposed system and
the baseline are statistically significant.

3.6 Ethical Considerations

All datasets used in this study are handled in accordance with
applicable data protection and research ethics principles. The PAN12
corpus is a publicly available research dataset with established usage
guidelines. Real conversation datasets used in the study are anonymized
by removing or replacing personally identifiable information, including
usernames and other identifying details.

The study does not involve direct interaction with real users. The
prototype is evaluated offline using dataset records, including
PAN12-derived data, anonymized real conversation data, and synthetically
generated annotated chat data. Synthetic data is used only for
controlled research purposes, particularly to represent underrepresented
grooming-related patterns and evasion behaviors.

The system is designed as a support tool for human moderators rather
than an autonomous decision-making system. Flagged conversations are
intended for human review before any moderation action is taken,
preserving human oversight and reducing the risk of algorithmic harm to
falsely flagged users.
