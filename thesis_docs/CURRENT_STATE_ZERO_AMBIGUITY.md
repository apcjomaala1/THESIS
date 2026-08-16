# Current Thesis Model State — Authoritative Report

**As of:** 2026-08-12  
**Authority:** This file supersedes earlier progress summaries and handoffs when
their wording conflicts with this report.

## Executive Summary

There are two trained model layers, not one model trained on one combined label.

1. **Layer 1 is DistilBERT.** The active weights were produced by the newer
   context-window/F1-selected trainer supplied by the user, not by the stale
   trainer currently stored beside the copied model. The best-supported label
   mode is `suspicious`, but the custom CLI flag and exact dataset manifest were
   not serialized with the checkpoint.
2. **Layer 2 is the LSTM.** The newest checkpoint is the August 12
   author-disjoint LSTM under `grooming-detector`. It uses a separate turn-level
   loss and conversation-level loss; it does not merge the two labels into one.
3. The saved LSTM produced stronger recorded numbers than the two displayed
   comparators on the frozen Layer 2 author-disjoint test split. A later audit
   found that this was **not a fair confirmed baseline victory**: only the LSTM
   received a threshold selected on that validation split, and the displayed
   current-score-only row was mathematically unable to cross the inherited
   threshold.
4. The result is not yet a fully clean end-to-end experiment because Layer 1
   was trained under an independently created conversation split rather than
   the same connected-author split.
5. PAN12's diff file is correction metadata. The project incorrectly turned it
   into a column called `is_suspicious`. It is not genuine message-level
   grooming or grooming-onset ground truth. This label-semantics problem remains
   even though the correct newer trainer was used.

## Confidence Key

- **Confirmed:** directly established by source code, model hashes, serialized
  checkpoint metadata, saved logs, or machine-readable results.
- **Strongly supported:** multiple independent records agree, but the decisive
  custom setting was not serialized into the model artifact.
- **Unknown:** the required provenance record was never saved and cannot be
  reconstructed conclusively from the current files.

## Directory Authority

| Directory | Role | Authority |
|---|---|---|
| `grooming-detector` | Active integrated pipeline and latest LSTM | **Canonical; continue work here** |
| `Groomer Thesis` | Original/newer Layer 1 trainer source and corpus workspace | Evidence/source only |
| `grooming-detector-main` | Deleted older Don pipeline/model copy | Deleted after validation; relevant history is recorded in the cleanup manifest |
| `grooming-detector-main-2` | Deleted bundle that contained the latest trained Layer 1 model and its supplied trainer | Deleted after the final weights, exact trainer, training data candidates, and trainer-state evidence were preserved |

Continue implementation only in `grooming-detector`. `Groomer Thesis` remains a
small provenance source; the two `*-main*` duplicate trees no longer exist.

## Layer 1 DistilBERT — What Is Actually Known

### Active weights

- Canonical runtime path:
  `grooming-detector/trained_model_distillbert/final_moderation_model/model.safetensors`
- SHA-256:
  `F90DB66B877587D36C4A38BDA9C4A4553D13D07902F4839170EE78BEC06E392B`
- Before cleanup, the same hash occurred at the final model and
  `checkpoint-750` under `grooming-detector-main-2`. Those were copies of the
  same latest trained Layer 1 model, not separate trained models. The retained
  canonical weights are therefore byte-identical to the model that was in that
  bundle. **Confirmed by pre-deletion hashing and the user's explicit
  provenance confirmation.**

### Trainer identity

The user-provided trainer is an exact line-for-line match for:

`Groomer Thesis/pan12-sexual-predator-identification-training-corpus-2012-05-01/train_distillbert.py`

The attachment displayed `_file_` and `_name_` because double underscores were
mangled during pasting; the saved Python source correctly uses `__file__` and
`__name__`.

The model's serialized `TrainingArguments` and `trainer_state.json` match this
newer trainer:

- three epochs;
- batch size 16, evaluation batch size 32;
- learning rate 2e-5;
- FP16 enabled;
- evaluation and saving each epoch;
- best-model selection by F1;
- best checkpoint 750;
- best validation F1 0.782752, recall 0.833801, precision 0.737593.

Those controls do not match the stale simplified trainer currently beside the
active copied weights. Therefore, the newer user-supplied trainer family
produced the active Layer 1 model. **Confirmed.**

The user has additionally confirmed that `grooming-detector-main-2` was the
bundle containing the latest trained Layer 1 model together with the trainer
script supplied earlier. Before that bundle was deleted, its exact trainer was
preserved at
`grooming-detector/data_sources/layer1_training_archive/train_distillbert.py`,
and its final model was verified byte-for-byte against the surviving canonical
weights. This resolves the bundle/model/trainer identity; it does not by itself
recover an executed command or serialize the custom `--label-mode` value.

### Layer 1 target

The newer trainer supports three mutually exclusive modes:

- `predator`: author-level `is_predator` repeated on message rows;
- `suspicious`: message-row `is_suspicious` only;
- `either`: logical OR of those two columns.

Its default is `suspicious`. The recovered history says Justin was instructed
to run `--label-mode suspicious` and subsequently reports the retrained model as
the suspicious-label version. However, `label_mode` is a custom script argument
and was not stored in Hugging Face `training_args.bin`. Therefore:

> The active checkpoint was most likely trained in `suspicious` mode; this is
> strongly supported, but the checkpoint artifact alone cannot prove the flag.

It should not be described as trained on both labels unless evidence appears
that `--label-mode either` was used.

### Layer 1 input and split

- Each classification input contains the current message plus up to two
  preceding messages separated by `[SEP]`. Despite the help text saying
  “before and after,” the implementation uses only current/past context.
- Duplicate context/label rows are removed.
- All positives are retained and negatives are downsampled according to the
  negative ratio, default 1:1.
- `GroupShuffleSplit` creates an 80/20 split by conversation ID.
- It is conversation-disjoint, not connected-author-disjoint. The same author
  can occur in Layer 1 training and evaluation through different conversations.

These behaviors are **confirmed from the trainer code**.

### Confirmed Layer 1 live-inference mismatch

The active `MessageClassifier.score(text)` and `score_batch(texts)` tokenize
each supplied string exactly as received. The live demo currently calls
`score(text)` with only the newly typed message. It does not construct the
current-plus-two-preceding-message `[SEP]` input used by the recovered trainer.
Therefore, the displayed live Layer-1 probability is not an input-protocol
match to the checkpoint's training procedure.

This also affects interpretation of the downstream live LSTM score: the LSTM
does process the accumulated sequence, but one of its seven trajectory inputs
is built from these isolated-message Layer-1 probabilities. The frozen LSTM
evaluation remains an internally comparable fixed-pipeline result because all
three Layer-2 methods used the same preserved Layer-1 cache, but neither the
live scores nor that frozen comparison establish performance for a corrected
context-window Layer 1.

**Required correction before presenting the live values as model evidence:**
construct Layer-1 inputs exactly as during training, regenerate all Layer-1
scores/cache under that protocol, and then retrain and reevaluate Layer 2. The
consultation UI may still demonstrate software mechanics if this limitation is
stated explicitly.

### Exact Layer 1 dataset

The archived data directory contains:

- `pan12_final_dataset.csv`;
- `synthetic_grooming_data.csv`;
- `synthetic_safe_data.csv`.

The recovered history says the model used PAN12 plus synthetic data, and the
checkpoint step counts are consistent with a larger pool than one minimal PAN
subset. But no dataset manifest, row hashes, or executed command was serialized.

> PAN12 plus both synthetic files is strongly supported; the exact rows and
> exact dataset hashes used are unknown.

## PAN12 Label Semantics — Confirmed Correction

PAN12 provides a predator-author list, which supports author/conversation-level
predator identification.

PAN12's bundled `readme.txt` describes
`pan12-sexual-predator-identification-diff.txt` as conversation and line
locations of **modified text**. It does not describe those locations as
grooming, suspicious behavior, or grooming onset.

The project's `Python.py` nevertheless sets `is_suspicious = 1` when a message
appears in that diff file. Therefore:

- PAN `is_predator` is a valid author-level label from the provided predator
  list.
- PAN `is_suspicious` is a misleading project column name for correction/diff
  membership.
- PAN `is_suspicious` must not be presented as genuine message-level grooming
  annotation or grooming-onset ground truth.

This conclusion is **confirmed from the corpus documentation and preprocessing
code**. It is independent of which trainer was used.

### Separate official PAN12 line ground truth

PAN12 did define a second competition problem: identify lines most distinctive
of predator behavior. This does **not** validate the project's training
`is_suspicious` column:

- The official PAN overview states that no Problem-2 training labels were
  released. The organizers instead judged submitted test lines after the
  competition, using a TREC-style pooling process and a single trained expert
  under time constraints.
- The locally retained test ground-truth file contains 6,478 judged suspicious
  conversation/line pairs across 834 test conversations:
  `Groomer Thesis/pan12-sexual-predator-identification-test-corpus-2012-05-21/pan12-sexual-predator-identification-groundtruth-problem2.txt`
- Those pairs have zero conversation-ID overlap with both the training-corpus
  diff file and the current PAN training CSV. The corresponding PAN12 test XML
  is not present in the cleaned workspace, so the judged line IDs cannot
  presently be joined to message text.
- The training `diff.txt` contains 16,948 modified-text locations across 1,064
  different training conversations. It is a separate artifact with a separate
  purpose.

Therefore, all PAN-derived `is_suspicious` values in the current training CSV
are reliable only as **diff-membership indicators**: `1` means listed as
modified text and `0` means not listed. Neither value is reliable as a grooming
message label. The official Problem-2 test judgments are potentially useful as
a qualified external evaluation resource if the exact matching test corpus is
legitimately recovered, but they do not unblock Layer 1 training and should not
be relabeled as ordinary complete training annotations.

**Usage decision:** Problem 2 is acceptable only as a frozen, qualified
external **message-level evaluation** set. It is not approved for training,
validation, threshold selection, early stopping, hyperparameter selection, or
manual annotation guidance. Even for evaluation, it must be described as
pooled/single-expert PAN12 judgments rather than exhaustive gold truth: only
lines submitted by at least one PAN participant were manually judged (covering
91% of predator lines), so a genuinely relevant line outside the pool can be
scored as a false positive. A defensible run therefore requires the exact
matching test XML, prediction at the original conversation/line identifiers,
and reporting the official precision, recall, and recall-weighted F3 metric.
The local ground-truth ID file alone is not executable because the matching
message texts are absent.

The other PAN-related thesis sources do not supply a replacement training
target. Villatoro-Tello et al. derive suspicious **conversations** from predator
presence and approach the line task without line-level training labels. Street
et al. perform message-level **Adult-versus-Child speaker-role** classification,
not message-level grooming-behavior annotation.

### Alternative grooming datasets and acquisition decision

There is no large, modern, openly downloadable dataset that is a clean drop-in
replacement for independently reviewed message-level grooming labels. The most
relevant documented alternatives found in the literature are:

| Resource | What it actually contains | Decision for this thesis |
|---|---|---|
| Cook et al., AIES 2023, *Protecting Children from Online Exploitation* | 24 Perverted Justice chats (12,942 total messages); 6,771 offender messages coded for 11 non-exclusive predatory communication strategies plus a null class. Two forensic-psychology authors developed and applied the framework; full repeat coding was infeasible and agreement was sample-tested. | **Highest-priority data request for Layer 1.** No public dataset package was located. If the authors grant access, retain the multilabel codes, define any binary mapping explicitly, add safe/general-chat negatives separately, and create a new conversation/author-disjoint split rather than reuse the paper's message-level stratified split. |
| Cano Basave et al., SocInfo 2014, *Detecting Child Grooming Behaviour Patterns on Social Media* | Predator messages from 50 Perverted Justice transcripts labelled by two trained analysts as Trust Development, Grooming, Physical Approach, or Other; only overlapping annotations were retained. Reported pre-balancing counts are 1,225, 3,304, 2,700, and 10,871 respectively. | **Strong secondary Layer-1 request.** No public dataset package was located. It supplies within-grooming-chat `Other` examples but not representative general-chat negatives. |
| Gupta et al. 2012 | 75 of 502 Perverted Justice chats, comprising 47,416 lines, annotated by a professional psychologist for six grooming stages. | Potential stage/trajectory evidence, but it is positive-chat-only, apparently single-annotator, and no public annotation package was located. Request only if the two stronger sources are unavailable. |
| ChatCoder2 and PANC (Vogt et al., ACL 2021) | ChatCoder2 has 497 complete Perverted Justice positive chats; the paper reports phase labels in 155. PANC combines those positives with PAN12 negative segments and provides an early-detection protocol and preprocessing code. | Useful as a **supplementary Layer-2/eSPD benchmark**, not fresh independent Layer-1 truth. ChatCoder2 has no negative chats, PANC adds no new message-level onset labels, and both can overlap with existing PJ/PAN material. Source access is by request. |
| VTPAN / other PAN12 reorganizations | Filtered, segmented, or reformatted PAN12 data. | Not a new dataset or a repair for PAN label semantics. Do not count it as independent evidence. |
| LiveMe restricted research corpus (Lykousas and Patsakis, 2020) | 39,382,838 public livestream-chat messages with interaction metadata, available to researchers/law enforcement on request. Grooming-related subsets were identified through keywords, embeddings, and topic analysis rather than exhaustive expert message annotation. | Potential modern-domain robustness research only; **not approved as supervised grooming ground truth**. |

All Perverted Justice-derived acquisitions must be treated as potentially
overlapping. Before merging any of them, recover stable transcript/offender
identifiers, hash normalized text, audit exact and near duplicates against PAN12
and every other source, and freeze connected-author assignments. Dataset access
also requires confirmation of licensing, ethics, and storage conditions.

**Current action:** contact the Cook et al. and Cano Basave et al. authors for
the labelled data, coding guide, identifiers, access terms, and reviewer records.
Until usable files are received and audited, the existing 1,335-row independent
annotation task remains the only controllable way to unblock Layer-1 training.

Primary source links:

- Cook et al. (2023): https://doi.org/10.1145/3600211.3604696
- Cano Basave et al. (2014): https://doi.org/10.1007/978-3-319-13734-6_30
- Gupta et al. (2012): https://doi.org/10.48550/arXiv.1208.4324
- Vogt et al. (2021): https://aclanthology.org/2021.acl-long.386/
- PANC preprocessing resources: https://early-sexual-predator-detection.gitlab.io/
- Lykousas and Patsakis (2020): https://doi.org/10.48550/arXiv.2004.08205

### Synthetic label audit

The two preserved synthetic files have now been audited from their CSVs and
generator code:

- `synthetic_grooming_data.csv` has 739 messages in 60 conversations. Its code
  sets both `is_predator` and `is_suspicious` directly from the generated
  speaker tag. Consequently, every `Predator_Sim` message is positive and every
  `Minor_Sim` message is negative, including ordinary setup talk. This is
  speaker-role-derived weak supervision, not independent message annotation.
- `synthetic_safe_data.csv` has 596 messages in 56 nonempty conversations. Its
  code assigns zero to every message because the prompt requested safe
  scenarios. The messages were not independently validated as hard negatives.
- Both generators record only the local model name `dolphin-llama3` and
  temperature 0.8. They do not preserve a model digest/version, generation
  seed, raw responses, human reviewers, or adjudication.
- Placeholder author IDs are reused across unrelated generations. They must be
  treated as conversation-local identities after review, not as real authors
  connecting all synthetic conversations.

Therefore, both synthetic sources are **excluded from final Layer 1 training
pending independent message review**. A deterministic audit manifest and a
1,335-row two-reviewer worksheet have been generated. The current approved
training-row count is zero; Layer 1 retraining is deliberately blocked until
the review and adjudication gate is complete.

## Layer 2 LSTM — Latest Model

### Checkpoint

- Path:
  `grooming-detector/grooming-detector-trajectory-pipeline/trajectory_model_author_disjoint.pt`
- Saved: 2026-08-12 02:46:59.
- This is the newest trained model overall. **Confirmed.**

### Data and inputs

- Dataset: PAN12 canonical CSV only, restricted to two-author conversations.
- Per turn input: 768-dimensional base `distilbert-base-uncased` CLS embedding
  plus seven trajectory features, for 775 dimensions total.
- The seven features include the fine-tuned Layer 1 current risk score, peak
  score, spike count, spike-then-drop indicator, topic drift, turn-taking
  imbalance, and conversation velocity.
- The 768-dimensional embedding comes from the base DistilBERT encoder; the
  fine-tuned Layer 1 classifier supplies risk scores used in trajectory
  features. These are related but distinct inputs.
- The LSTM therefore receives 775 values per turn, while the weighted scorer
  receives only the seven trajectory features. The current comparison cannot
  isolate the effect of sequence modeling from the effect of giving the LSTM
  768 additional text features.
- The saved benign centroid predates the author-disjoint run. Its source-row
  manifest was not serialized, and the available driver constructs it from a
  pooled corpus before splitting. Exclusion of test conversations from that
  artifact is therefore unproven.

### Training targets

The LSTM uses two separate losses:

1. A turn-level cumulative loss derived from the project `is_suspicious`
   column.
2. A conversation-level max-over-turn loss derived from whether the
   conversation contains a listed predator author.

It does not combine both fields into a single label. Multi-objective training is
legitimate in principle. In this experiment, however, the PAN turn-level target
is correction metadata and cannot be interpreted as grooming-message truth.
The conversation-level target is the defensible PAN target.

### Layer 2 split

Conversations sharing any dataset-namespaced author were joined into connected
components. Components were assigned wholesale to train, validation, or test.

| Partition | Conversations | Positive conversations |
|---|---:|---:|
| Train | 14,893 | 363 |
| Validation | 1,828 | 49 |
| Test | 1,847 | 42 |

The audit verifies zero shared conversations, zero shared authors, and zero
shared predator authors across every Layer 2 partition pair. **Confirmed.**

This split does not retroactively alter the earlier Layer 1 training split.
Thus Layer 2 is author-disjoint internally, while the full two-layer pipeline is
not yet proven author-disjoint end to end.

## Frozen Layer 2 Test Result — Historical Development Result

The LSTM checkpoint was selected using validation conversation F0.5 with
conversation AUC as tie-breaker. Its threshold was selected from the new
author-disjoint validation partition before the test partition was evaluated.
The comparator protocol was not equivalent, as detailed below.

| Metric | LSTM | Weighted scorer* | Current-score-only weighted ablation* |
|---|---:|---:|---:|
| Recall | 0.8333 | 0.3333 | 0.0000 |
| Precision | 0.8750 | 0.1842 | 0.0000 |
| F1 | 0.8537 | 0.2373 | 0.0000 |
| F0.5 | 0.8663 | 0.2023 | 0.0000 |
| AUC-ROC | 0.9904 | 0.8841 | 0.8559 |
| True positives | 35 | 14 | 0 |
| False negatives | 7 | 28 | 42 |
| False positives | 5 | 62 | 0 |
| Mean first-flag turn | 10.77 | 62.86 | N/A |

The asterisks are material:

- The weighted scorer retained weights and a `0.7` threshold selected under an
  older validation setup, rather than being independently tuned on the same
  author-disjoint validation partition as the LSTM.
- The so-called current-score-only row was not raw DistilBERT. It retained only
  Layer 1's probability, multiplied it by the weighted scorer's `0.1` current-
  score weight, and applied another sigmoid. For a Layer 1 probability in
  `[0,1]`, its possible output is only approximately `[0.500,0.525]`; applying
  the inherited `0.7` threshold made every positive prediction impossible.
  Its zero recall and F0.5 are therefore an evaluation artifact, not evidence
  that the classifier failed.
- The LSTM used 768 additional base-encoder dimensions that neither displayed
  comparator received.

Consequently, the table preserves what the software emitted, but it does
**not** establish that the LSTM fairly outperformed the weighted scorer or a
raw Layer 1 classifier. Even the otherwise threshold-independent AUC comparison
does not isolate architecture benefit because the methods receive different
information. The test partition has now been inspected and must not be tuned
against during the corrected experiment.

It must not yet be called a fully leakage-free, end-to-end unseen-author result.

## Meaning of “Time to Detection” in the Current Report

The evaluator records the turn index where a positive conversation is first
flagged. Because PAN lacks valid grooming-onset annotations, this is not elapsed
time from a known grooming onset.

Use the term **mean first-flag turn** or **early-flagging turn** for the current
result. Do not claim “10.77 turns after grooming began.”

## Overfitting Status

- Training and validation used separate Layer 2 author components.
- The frozen Layer 2 test result is not worse than validation, so there is no
  obvious classic train-versus-validation collapse in the saved metrics.
- A single held-out split cannot rule out model-selection variance.
- The larger concern is upstream Layer 1 split/provenance and invalid PAN turn
  labels, not demonstrated classic LSTM overfitting.

## What Can Be Claimed Now

Defensible wording:

> A functioning LSTM produced a strong provisional development result on an
> internally author-disjoint PAN12 Layer 2 partition. Subsequent audit found
> invalid turn supervision, upstream provenance issues, unmatched comparator
> tuning, and an invalid classifier-ablation threshold; therefore no fair
> baseline-superiority or final grooming-detection claim is made from that run.

Not yet defensible:

- fully end-to-end unseen-author generalization;
- genuine message-level grooming detection from PAN diff annotations;
- grooming-onset detection delay;
- a claim that the exact Layer 1 training rows are fully known;
- a claim that the Layer 1 model was trained on both labels;
- a claim that the current LSTM has fairly beaten either baseline.

## Required Time-Constrained Primary Experiment

**Scope decision (approved by the adviser on 2026-08-17):** the final empirical
endpoint is conversation-level identification of PAN12 conversations containing
a listed predator. This is the only large, locally available target with
defensible provenance. The revised implementation must:

1. Preserve the current checkpoint, evaluation JSON, and split audit unchanged
   as historical development artifacts.
2. Before building another model, freeze a new connected-author final holdout
   from component groups whose outcome was not previously inspected. Serialize
   IDs and hashes using metadata only. If time forces reuse of the old test
   partition, disclose the evaluation as retrospective rather than pristine.
3. Remove PAN `is_suspicious` from every row filter, label, loss, selection,
   feature-construction decision, and evaluation target.
4. Rebuild Layer 1 on the new training partition only, using the current
   speaker's valid `is_predator` value as explicitly author-derived weak
   supervision. Use exactly the current message plus two preceding messages at
   both training and inference; downsample only training negatives. Call its
   output a predator-author proxy score, not a grooming probability.
5. Generate a context-matched score cache keyed by stable conversation/line
   IDs, with source hashes, split assignment, command, seed, package versions,
   model digest, and checkpoint-selection record.
6. Recompute the benign centroid from training-partition data only and
   serialize its exact source IDs and digest.
7. Retrain Layer 2 with the valid conversation target only. The turn-level loss
   must be truly disabled rather than merely outweighed.
8. Independently tune every learned method on the same validation endpoint.
   Compare raw Layer 1 with its own threshold, the weighted scorer with its own
   weights and threshold, and the paper-promised keyword baseline.
9. For the primary architecture comparison, give the LSTM and weighted scorer
   the same seven trajectory inputs. Report the 775-dimensional full LSTM as a
   separate enhanced model, or add matched embedding-only/full-input
   ablations; do not attribute an unequal-input win solely to the LSTM.
10. Lock all code, checkpoints, thresholds, and reporting rules before the one
    final holdout run. Report the outcome even if the LSTM does not win.
11. Update the paper only from that final report. The historical run may remain
    as a clearly labelled development diagnostic, not an ablation victory.

### Revised Layer 1 training package — ready, not yet trained

The adviser-approved Layer 1 package was completed on 2026-08-17 on branch
`methodology/author-level-layer1`:

- The accepted active PAN CSV has SHA-256
  `4131dc7b78865bbe2a48d155f770dd3743236d161b8430893328fbed5a42d408`.
  Seven malformed rows with missing author labels and one resulting negative
  validation conversation are excluded rather than silently converted to zero.
- `locked_split_manifest.json` freezes 13,031 training conversations, 1,827
  validation conversations, 1,862 newly held-out final-test conversations, and
  1,847 previously inspected historical-test conversations that are excluded
  from the revised run. It proves zero conversation, author, and component
  overlap. The manifest file SHA-256 is
  `4f0da3ec1db130cfbef5d41d7085a590ca22e53d0f98137016e1d355ca30a0c0`.
- `train_layer1_author_proxy.py` reads only the official author label, constructs
  current-plus-two-preceding prefix contexts, downsamples negatives only in
  training, selects the checkpoint by validation PR-AUC and threshold by
  validation F0.5, records CUDA/GPU/package/data/model hashes, and does not
  score either final-test group.
- The sendable transfer ZIP includes the exact locked CSV and has SHA-256
  `ed11c4c774704262f1a4ebf97d3ba7a7765b69966e78093402b1cb8626802b24`.
- Verification passed: deterministic split regeneration, six focused package
  tests, all 68 existing pipeline tests, a full-corpus dry run, PowerShell and
  Python syntax checks, extracted-ZIP tests/dry run, and a one-step CUDA/BF16
  DistilBERT smoke train. No full revised Layer 1 training or final-test scoring
  was performed locally.

If the adviser requires genuine message-level grooming or onset detection as
the primary endpoint, this fast route is unavailable. Complete two independent
blinded reviews and adjudication of the generated 1,335-row worksheet or obtain
a suitable genuinely annotated corpus. The current worksheet must first be
converted into reviewer-specific blinded sheets because it exposes source,
proxy label, and role-bearing names such as `Predator_Sim`.

### Decision: OGDM-guided LLM-assisted annotation

Using an LLM to assist annotation is approved only as a **weak-supervision or
pre-annotation stage**, not as a replacement for independent ground truth.
This is a material improvement over using PAN diff membership, but an LLM-only
label set would merely replace one unverified proxy with another.

The annotation target must remain the **current message**, presented with the
same preceding context that Layer 1 will receive at inference. OGDM should
define the observable behavior rubric: for example, deceptive trust
development, sexual solicitation or sexualization, compliance/boundary
testing, secrecy or isolation, and requests to migrate contact, exchange
images, or meet. A message may have multiple strategy tags; a derived binary
target may be `1` when at least one approved grooming-behavior tag is present,
`0` when none is present, and `U` when the available context is insufficient.
Speaker identity, the PAN predator list, PAN diff membership, and the source
scenario must be hidden from annotators.

The seven numeric trajectory features are **not** annotation labels. They must
continue to be computed deterministically from the corrected Layer-1 score
sequence, message embeddings, and turn history. Asking an LLM to directly
assign `peak_score`, `spike_count`, `rate_of_change`, `topic_drift`, or
`turn_taking_imbalance` would make the engineered pipeline circular and less
reproducible.

Required protocol:

1. Freeze author-disjoint raw-data partitions before prompt or rubric tuning.
2. Obtain approval for a written OGDM-derived codebook and examples from the
   thesis adviser or an appropriately qualified reviewer.
3. Create a stratified pilot set and have at least two trained human reviewers
   label it independently; adjudicate disagreements and report agreement.
4. Run a fixed, versioned LLM prompt on the same pilot, saving model/version,
   parameters, prompt, input/output, row IDs, hashes, and failures. Measure its
   agreement and per-class errors against the adjudicated human labels before
   scaling.
5. If pilot quality is acceptable, use the LLM to pre-label or pseudo-label the
   training partition. Humans must review disagreements/uncertain cases and a
   random audit sample. LLM-reported confidence alone is not ground truth.
6. Keep validation and test labels human-reviewed and adjudicated; never tune
   the prompt, model, classifier, threshold, or LSTM against the final test set.
7. Describe unreviewed LLM labels as `LLM-generated pseudo-labels` or
   `LLM-assisted weak supervision`, not manual annotation or gold truth.
8. Confirm corpus licence, research-ethics, privacy, and external-processing
   permission before sending sexual-abuse chat text to a hosted LLM; use an
   approved local model when external transmission is not permitted.
9. Train the context-matched Layer 1, regenerate its score cache, and then
   retrain and reevaluate the LSTM and both comparators from the frozen splits.

For immediate work, pilot this procedure on a manageable stratified subset or
the existing 1,335-row synthetic worksheet rather than automatically labeling
the full PAN corpus. An LLM-only training experiment may still be useful as an
explicit weak-supervision ablation, provided its final evaluation uses separate
human-reviewed labels.

## Comment Matrix 2 implementation status (corrected 2026-08-13)

The earlier Comment Matrix revision went beyond the user's requested boundary.
That wider paper/deck rewrite has been corrected. Only changes that can be made
without deciding the central methodology are applied now.

- Applied now in the paper and deck: item 1 privacy safeguards and residual-risk
  wording; item 2 Philippine relevance with no Filipino/Taglish validation
  claim; item 5 the short `Conversation Trajectory Lab` module title; item 7
  formulas and ranges for the seven implemented trajectory features; item 8
  the current rerun/demo software versions; and item 9 explicit offline replay
  and deployment limitations.
- Retained in code because the work is independent of model labels and
  evaluation: local-demo direct-identifier masking before scoring and in-memory
  retention, server-generated opaque conversation IDs, rejection of unknown
  IDs, no-store response headers, the environment snapshot/checker, and SciPy
  dependency coverage.
- Intentionally deferred until adviser approval: item 3 dataset-table changes,
  item 4 final label definitions, item 6 the corrected evaluation design, and
  item 10 DistilBERT training/label-alignment remediation. The paper and deck do
  not pre-emptively change research questions, objectives, endpoints, training,
  baselines, or final evaluation around those items.
- Slides 20-23 explain the completed items in ordinary language and identify
  the deferred items as pending. They do not expose the detailed methodology
  audit as if it were already an approved study redesign.
- The verified presentation is currently `WASD - Thesis 2 - corrected.pptx`.
  The original file was open in PowerPoint, so Windows blocked safe in-place
  replacement; use the corrected copy until the original is closed.
- Verification after the correction: 68/68 pipeline tests passed; the current
  environment matched its snapshot; JavaScript syntax passed; and the deck
  passed visual review of edited slides, template fidelity, and element-bounds
  inspection.

The detailed chronological record, including the superseded wider batch and
this correction, is in `THESIS_RECOVERY_NEXT_STEPS.md`.

The detailed chronological record is in `THESIS_RECOVERY_NEXT_STEPS.md`.

## Authoritative Evidence Files

- `CURRENT_STATE_ZERO_AMBIGUITY.md` — this report.
- `THESIS_RECOVERY_NEXT_STEPS.md` — chronological activity log; earlier rows
  may be superseded by later corrections.
- `AUTHOR_DISJOINT_EXPERIMENT.md` — frozen Layer 2 protocol, commands, and
  result.
- `WORKSPACE_CLEANUP_MANIFEST.md` — pre-deletion hashes and preserved Layer 1
  provenance artifacts.
- `grooming-detector/data_sources/layer1_training_archive/train_distillbert.py`
- `Groomer Thesis/pan12-sexual-predator-identification-test-corpus-2012-05-21/pan12-sexual-predator-identification-groundtruth-readme.txt`
- `Groomer Thesis/pan12-sexual-predator-identification-test-corpus-2012-05-21/pan12-sexual-predator-identification-groundtruth-problem2.txt`
- `grooming-detector/data_sources/layer1_dataset_manifest.json`
- `grooming-detector/data_sources/layer1_annotation_candidates.csv`
- `grooming-detector/data_sources/README.md`
- `grooming-detector/grooming-detector-trajectory-pipeline/audit_layer1_dataset.py`
- `thesis_docs/evidence/layer1_checkpoint_750_trainer_state.json`
- `thesis_docs/evidence/layer1_full_run_trainer_state.json`
- `grooming-detector/grooming-detector-trajectory-pipeline/author_disjoint_split_audit.json`
- `grooming-detector/grooming-detector-trajectory-pipeline/lstm_author_disjoint_evaluation.json`
- `grooming-detector/grooming-detector-trajectory-pipeline/trajectory_model_author_disjoint.pt`
