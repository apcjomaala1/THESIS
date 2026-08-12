# Grooming Detection — Trajectory Pipeline

Current two-stage experimental pipeline:

1. **Layer 1 — DistilBERT message classifier** (`../trained_model_distillbert/`)
   retained as a fixed checkpoint. Its PAN `is_suspicious` supervision has a
   confirmed label-provenance limitation; see
   `../../thesis_docs/CURRENT_STATE_ZERO_AMBIGUITY.md` before making claims.
2. **Layer 2 — Author-disjoint trajectory LSTM**, using the message embedding
   plus seven trajectory features per turn. The tuned weighted trajectory
   scorer and Layer-1-only score are retained as comparators.

## File map

```
trained_model_distillbert/
  Python.py              # builds pan12_final_dataset.csv from raw PAN12
  train_distillbert.py   # Layer 1 training (is_suspicious + class weights)
  final_moderation_model/  # output of train_distillbert.py

grooming-detector-trajectory-pipeline/
  data_loader.py             # PAN12 loaders + 2-author filter
  features.py                # MessageEncoder + 7 trajectory features
  privacy.py                 # direct-identifier masking for prototype inputs
  message_classifier.py      # thin wrapper that loads final_moderation_model
  compute_benign_centroid.py # precomputes the topic-drift baseline
  weighted_scorer.py         # Layer 2: weighted aggregation
  trajectory_model_lstm.py   # Layer 2: active LSTM architecture
  trajectory_model_author_disjoint.pt  # latest provisional checkpoint
  tune_weights.py            # grid search on val set
  main.py                    # end-to-end driver
  evaluation.py              # metrics + keyword baseline + ablation
  capture_environment.py     # print/check the current software environment
  environment_snapshot.json  # observed 2026-08-12 rerun/demo versions
  demo/
    scoring_core.py          # LSTM + weighted-comparator offline turn driver
    replay.py                # PAN12 conversation replay
    app.py                   # local Flask offline-replay UI
    templates/chat.html
    static/{style.css,app.js}
```

## Historical run order - do not use for the corrected final experiment

The commands below reproduce the superseded pipeline only. They still depend on
the invalid PAN correction/diff-derived `is_suspicious` target and must not be
used to generate final thesis evidence. Follow
`../../thesis_docs/CURRENT_STATE_ZERO_AMBIGUITY.md` for the corrected rescue
protocol.

```bash
# 0. Install
pip install -r requirements.txt

# 1. Build the per-message CSV from raw PAN12 (already done if pan12_final_dataset.csv exists)
cd ../trained_model_distillbert
python Python.py

# 2. Train Layer 1 (DistilBERT) on is_suspicious with class weights
python train_distillbert.py    # writes ./final_moderation_model

# 3. Precompute benign-chat centroid for topic_drift baseline
cd ../grooming-detector-trajectory-pipeline
python compute_benign_centroid.py \
  --csv ../trained_model_distillbert/pan12_final_dataset.csv \
  --out benign_centroid.npy

# 4. Build val features and tune weighted scorer
python main.py \
  --csv ../trained_model_distillbert/pan12_final_dataset.csv \
  --centroid benign_centroid.npy \
  --scorer-config weighted_scorer.json \
  --dump-val-features val_features.npz   # writes default scorer + val features

python tune_weights.py --val-features val_features.npz --out weighted_scorer.json

# 5. Final evaluation on test set with the tuned scorer
python main.py \
  --csv ../trained_model_distillbert/pan12_final_dataset.csv \
  --centroid benign_centroid.npy \
  --scorer-config weighted_scorer.json

# 6. Provisional fixed-Layer-1 LSTM demos
python -m demo.replay \
  --csv ../trained_model_distillbert/pan12_final_dataset.csv \
  --conv-id <some_predator_conv_id>

python -m demo.app   # then open http://127.0.0.1:5000
```

The local browser demo loads the saved author-disjoint Layer 2 LSTM and shows its
historical development outputs. Its three-method table is explicitly marked as
an invalid final comparison because comparator tuning was unmatched and the
current-score-only threshold made positive predictions impossible. It is a
consultation mechanism demonstration, not model-performance evidence or a
deployment-ready safety determination. It is an offline sequential simulation,
not a live platform integration. Common direct identifiers are masked before
model input and in-memory retention, responses use no-store headers, and reset
deletes the in-process conversation object. Pattern masking cannot recognize
every name, address, or indirect identifier, so real sensitive data must not be
entered.

The consultation interface leads with the selected turn's LSTM sequence score,
its development threshold, distance to threshold, and accumulated sequence
length. It also includes a score-over-turn chart, human-readable trajectory
features, two-speaker auto-alternation, keyboard-accessible turn inspection,
loading/error states, and a prominent statement that a below-threshold output
does not mean a conversation is safe. Known protocol corrections and the
historical table are retained in collapsed audit panels rather than presented
as final evidence.

Verify the current runtime against the recorded reproducibility snapshot with:

```bash
python capture_environment.py --check environment_snapshot.json
```

## Tests

The pipeline has a pytest suite covering trajectory features, scoring,
data-loader filters, split integrity, evaluation, data-provenance auditing,
and the LSTM-backed demo core:

```bash
pip install pytest
python -m pytest tests/ -v --basetemp=.pytest_tmp_consultation
```

The suite currently covers:
* every trajectory feature individually (peak, current, spike count,
  spike-then-drop with the parameter actually honored, rate of change,
  topic drift against the centroid in both close and far directions,
  turn-taking imbalance for balanced / one-sided / single-author cases),
* the data loader's predator-list, suspicious-lines, and 2-author filter,
* the weighted scorer's shape validation, monotonicity, save/load,
* the evaluation metrics including time-to-detection and the keyword
  baseline aggregation,
* the tuner's metric math and `search` returning a valid config dict,
* connected-author-disjoint split integrity and the Layer-1 dataset audit,
* LSTM offline-demo flagging while preserving the weighted comparator,
* direct-identifier masking, no-cache response headers, and opaque local IDs,
* reproducibility checks against `environment_snapshot.json`.

If you change any feature-engineering or scoring logic, run the suite first
— it will tell you exactly which behavior broke.

## Superseded methodology notes (historical only; do not cite)

The material below records the original weighted-scorer design and is retained
only for code history. It is superseded by
`../../thesis_docs/CURRENT_STATE_ZERO_AMBIGUITY.md` and the saved
author-disjoint LSTM experiment. In particular, its Layer-1 label claims and
statement that Layer 2 is not an LSTM are no longer authoritative.

Decisions are documented in
`C:\Users\vyD\.claude\plans\silly-drifting-cat.md`. Key points:

- **Layer 1 label** is `is_suspicious` (per-message), NOT `is_predator`
  (author-level). The author-level label trains the model to predict
  "was this author ever a predator" instead of "is this message grooming."
- **No undersampling**; instead `CrossEntropyLoss(weight=...)` with weight
  `N_neg / N_pos` on the positive class. Preserves the real prior so that
  the 0.5 spike threshold corresponds to the natural binary decision boundary.
- **Thesis 1 corpus = dyadic conversations only.** OGDM (Lorenzo-Dus et al.,
  2016) is explicitly dyadic; PAN12 author-level predator labels are reliable
  for dyadic convs ("predator in conv" ≈ "grooming in conv") but introduce
  label noise in multi-party rooms (predators participated in many benign
  chat rooms too). PAN12's dyadic subset = 41 predator convs out of 18.5k
  2-author convs. Multi-party detection is deferred to Thesis 2.
  Controlled by `--require-dyadic` (default ON) in `main.py` and
  `compute_benign_centroid.py`. For already-dyadic external datasets
  (ChatCoder2, synthetic), the filter is a no-op.
- **Turn-taking imbalance uses a *dominant-dyad* reduction** even though we
  filter to dyadic convs — same formula either way (top-2 turn contributors),
  so the feature is forward-compatible with multi-party data in Thesis 2
  without code changes. The implementation counts turns, not words.
- **Topic drift** is measured from a precomputed centroid of benign
  conversations, not the conversation's own first message — this avoids
  silently nulling the feature when a predator opens with risky content.
- **Layer 2 is a weighted sum**, not an LSTM. Each weight ties to an OGDM
  construct, every score is auditable, and the architecture matches what
  Ch 1–2 actually requires ("behavioral and contextual analysis"). LSTM is
  preserved in `experimental/` for a future iteration.
- **Weights, spike-drop magnitude, and flagging threshold** are tuned by
  `tune_weights.py` on the val set to maximize recall at **precision ≥ 0.15**
  (was 0.5 in the original plan). At the dyadic base rate of ~0.2% precision
  0.5 is mathematically blocked even with a strong classifier; 0.15 is ~3×
  the base rate and corresponds to a defensible triage operating point.

## Dataset contract — canonical schema

The pipeline operates on a single canonical schema. Every loader in
`data_loader.py` emits a pandas DataFrame with these columns:

| Column | Type | Meaning |
|---|---|---|
| `conversation_id`   | str | namespaced `<dataset_name>:<original_id>` |
| `line`              | int | 1-indexed turn order within the conversation |
| `author_id`         | str | speaker ID (anonymized) |
| `text`              | str | non-empty message text |
| `is_suspicious`     | int | 1 if this message is grooming-relevant, else 0 |
| `author_is_predator`| int | 1 if this author was ever a confirmed predator |
| `dataset_source`    | str | dataset_name (carried through to every snapshot) |

Feature engineering, scoring, evaluation, and the demos consume the snapshots
produced by `build_conversation_snapshots` and never touch raw CSV columns.

### Loading one or more datasets

The pipeline ships with a generic CSV loader, `load_canonical_csv`, that
handles known column aliases (`conv_id` / `convo_id` → `conversation_id`,
`author` → `author_id`, `is_predator` → `author_is_predator`) and silently
drops out-of-scope columns (e.g. `image_type`). Wrap one or more sources
together with `load_datasets`:

```python
from data_loader import load_datasets

snapshots = load_datasets(
    [
        ("pan12",       "../trained_model_distillbert/pan12_final_dataset.csv"),
        ("roblox_run",  "../dataset/RobloxPredatorTriesToRun.csv"),
        ("yt_dyadic",   "../dataset/WeGotARobloxPredatorArrested.csv"),
        ("yt_dyadic2",  "../dataset/WeGotARobloxPredatorArrested2.csv"),
    ],
    require_dyadic=True,
)
```

The CLI mirror is `--datasets NAME=PATH [NAME=PATH ...]`:

```powershell
python main.py `
  --datasets pan12=../trained_model_distillbert/pan12_final_dataset.csv `
             roblox_run=../dataset/RobloxPredatorTriesToRun.csv `
             yt_dyadic=../dataset/WeGotARobloxPredatorArrested.csv `
             yt_dyadic2=../dataset/WeGotARobloxPredatorArrested2.csv `
  --centroid benign_centroid.npy `
  --scorer-config weighted_scorer.json
```

The same `--datasets` flag is accepted by `compute_benign_centroid.py`. For
a more representative benign centroid you typically want to mix PAN12 with
real-world benign chats:

```powershell
python compute_benign_centroid.py `
  --datasets pan12=../trained_model_distillbert/pan12_final_dataset.csv `
             discord=../dataset/DiscordCommunityChat.csv `
             groupchat=../dataset/anonymized_group_chat_dataset.csv `
  --no-require-dyadic `
  --out benign_centroid.npy
```

### Using eSPD / PANC / ChatCoder2 exports

If you generate datasets with the official eSPD preprocessing stack
(`PAN12`, `ChatCoder2`, `PANC`), this repo now supports both of the common
handoff formats:

1. **CSV / TSV table exports** from the eSPD repo's `create_csv.py`
   loader path.
   `load_canonical_csv` now auto-detects comma vs tab delimiters and accepts
   common eSPD-style aliases such as `chatName`, `sender`, `message`,
   `label`, and `predator`.
2. **Datapack JSON exports** from the eSPD repo's `create_datapack.py`
   path.
   Convert them once to this repo's canonical message-level schema with:

```powershell
python import_espd_datapack.py `
  --input ..\dataset\PANC-datapack-someid.json `
  --output ..\dataset\PANC-canonical.csv
```

Then use the converted file like any other source:

```powershell
python main.py `
  --datasets pan12=../trained_model_distillbert/pan12_final_dataset.csv `
             panc=../dataset/PANC-canonical.csv `
  --centroid benign_centroid.npy `
  --scorer-config weighted_scorer.json
```

Important: this trajectory pipeline needs **message-level chat structure**.
If an external export collapses an entire segment into one row without
per-message author / order information, use the datapack JSON instead of the
flattened segment file.

### Conversation-ID namespacing

Two source CSVs can independently use the same raw conversation ID (`yt_01`,
`1`, etc.) without colliding — the loader prefixes the `dataset_name` onto
every `conversation_id`, e.g. `roblox_run:yt_01` vs `yt_dyadic:yt_01`. This
also makes every downstream log line (snapshots, evaluation rows, errors)
self-identifying about which source produced it.

### Stratified split across sources

`main.stratified_split` stratifies jointly on `(dataset_source, label)` so
every source contributes its positives and negatives proportionally to
train / val / test. Source-strata with fewer than 4 conversations are
collapsed into a per-label "rare" bucket so `sklearn.model_selection`
doesn't refuse the split.

### Adding a new dataset

1. Get the CSV into (something close to) the canonical schema. Acceptable
   column names today: any of `conv_id` / `convo_id` / `conversation_id`,
   `author` / `author_id`, `is_predator` / `author_is_predator`, plus
   `line`, `text`, and `is_suspicious`. Extra columns are dropped.
2. Drop the file in `dataset/`.
3. Add `name=path` to your `--datasets` invocation. **No code changes.**
4. If the CSV uses a different alias, extend `COLUMN_ALIASES` in
   `data_loader.py` (one line). The smoke tests in
   `tests/test_canonical_csv.py` pin the contract — add a row there for any
   new alias you introduce.
