**Research Title:** GroomShield: Detecting Grooming-Related Interactions in Chat Conversations Using DistilBERT and LSTM-Based Behavioral Sequence Modeling

**SDG Alignment:** SDG 9 (Industry, Innovation and Infrastructure); SDG 16 (Peace, Justice and Strong Institutions)

**Team WASD**

**Authors:**

Justin Bryden G. Arroco<br>
Don Victor L. Idos<br>
John Michael O. Maala<br>
Andrei Luis M. Torres

**Co-Authors:**

Manuel L. Calimlim Jr.<br>
Lorena Rabago

**Research Abstract:**

Online grooming may develop gradually across a chat conversation, making interactions difficult to identify through isolated keywords or messages. This study developed GroomShield, a two-layer AI moderation module that combines contextual DistilBERT scoring with LSTM-based behavioral sequence modeling to identify conversations for human review. The PAN-2012 Sexual Predator Identification corpus was selected for evaluation, with positive conversations defined by official predator-author membership. Connected-author partitioning kept participants separate across training, validation, and test sets. Layer 1 generated context-conditioned turn scores; Layer 2 modeled chronological features describing score patterns, topic movement, and speaker participation. The Trajectory-Feature LSTM was compared with a keyword rule, maximum Layer 1 scoring, and a weighted scorer using the same seven features. An Embedding-and-Feature LSTM additionally received text embeddings. On 1,862 held-out conversations containing 44 positives, the Trajectory-Feature LSTM identified 41 positives, achieving 93.18% recall and 0.8613 F2, with three misses and 21 false alerts. The Embedding-and-Feature LSTM identified all 44 positives, with 41 false alerts. The matched-input LSTM achieved higher F2 and PR-AUC than the weighted scorer, supporting the contribution of learned sequence modeling. GroomShield demonstrates how contextual and behavioral analysis can strengthen conversation-level detection and support human moderation.

**Keywords:** Online Grooming Detection, Chat Moderation, DistilBERT, Long Short-Term Memory, Behavioral Sequence Modeling
