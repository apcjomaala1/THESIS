# Midterms Defense Comments Matrix

### 1. Evaluation & Statistical Context

- **Panel Comment:** Provide statistical evidence in the RRL and define objective metrics to measure the new model's performance against existing tools.
- **Action Taken:** Added empirical data to Chapter 2 citing that 67% of toxic gaming messages are context-dependent (Schurger-Foy et al., 2025). Established objective evaluation metrics (Recall, Precision, F1-Score) in the methodology to ensure comparative performance can be objectively evaluated.
- **Location:** Addressed in **Chapter 2** (Section 2.1) and **Chapter 3** (Section 3.5.1).

### 2. Terminology & Precision

- **Panel Comment:** Replace vague terms like "enhance" and "system" with specific descriptions of the detection model.
- **Action Taken:** Changed the paper title from "Enhancing Chat Moderation Systems Through AI-Based Behavioral and Contextual Analysis" to "AI-Based Detection of Grooming-Related Interactions in Chat Conversations Using Contextual and Behavioral Analysis" to remove vague terms. Replaced broad terminology throughout the proposal with precise descriptors such as "chat moderation prototype", "trajectory scoring model", and "chat behavior detection model." Specified that the goal is to measure moderation performance against traditional keyword-based approaches.
- **Location:** Addressed throughout **Chapter 3** (e.g., Sections 3.1, 3.4).

### 3. Behavioral Context

- **Panel Comment:** Incorporate new behavioral factors into the detection model.
- **Action Taken:** Shifted the proposed methodology's focus from single-message classification to tracking trajectory-level features over time. Incorporated new metrics into the model design such as "Rate of score change", "Turn-taking imbalance", and "Topic drift" to accurately model intent.
- **Location:** Addressed in **Chapter 3, Section 3.3.4** (Feature Engineering) and **Table 3.2**.

### 4. Baseline Comparisons

- **Panel Comment:** Compare the model against existing market tools, and provide statistics and objective means to measure performance against existing baselines.
- **Action Taken:** Cited Chapter 2 literature demonstrating behavioral analysis forecasting can reach 74% balanced accuracy. Defined a rule-based keyword moderation baseline that mimics conventional market tools to be used during evaluation. Additionally, referenced the **Online Grooming Detection Model (OGDM)** as a standard baseline for behavioral classification. Proposed the use of McNemar's test alongside standard metrics to objectively measure performance against these baselines.
- **Location:** Addressed in **Chapter 3, Section 3.4.3** (Baseline Comparison Model) and **Section 3.5.2**.

### 5. Scope Feasibility

- **Panel Comment:** Restrict the scope to the English language for feasibility.
- **Action Taken:** Explicitly defined the scope to focus exclusively on English text corpora, and noted that the planned DistilBERT model fine-tuning will be restricted to English-language communication.
- **Location:** Addressed in **Chapter 3, Section 3.4.1** (Message-Level Classifier).

### 6. Latency Constraints

- **Panel Comment:** Address computational latency when handling large datasets.
- **Action Taken:** Selected DistilBERT specifically because it is a lightweight transformer model designed for reduced computational overhead. Additionally, specified the planned utilization of GPU acceleration to further mitigate latency during the model's development.
- **Location:** Addressed in **Chapter 3, Section 3.2.3** (DistilBERT) and **Section 3.2.4** (Development Environment).

### 7. Behavioral Tracking & Expertise

- **Panel Comment:** Analyze behavior across an extended interaction rather than just evaluating isolated chat messages.
- **Action Taken:** Designed the proposed model to track conversational progression and deliberate score-suppression tactics (e.g., "Spike-then-drop pattern"). The model is explicitly structured to evaluate the behavioral trajectory of a user across multiple turns rather than relying on isolated text.
- **Location:** Addressed in **Chapter 3, Section 3.1** (Research Design) and **Section 3.3.4** (Feature Engineering).
