# Workspace Cleanup Manifest

**Started:** 2026-08-12  
**Workspace:** `C:\Projects\THESIS`

## User-Requested Outcome

- Consolidate project-level Markdown records in one folder.
- Remove nested Git repositories.
- Initialize one Git repository at the THESIS workspace root.
- Remove obsolete duplicate repository trees while preserving the active
  pipeline, authoritative paper, results, datasets needed next, and provenance
  evidence.

## Pre-Cleanup Inventory

| Directory | Approximate size | Decision |
|---|---:|---|
| `grooming-detector` | 1.538 GiB | Keep as canonical active code/model tree. |
| `Groomer Thesis` | 0.001 GiB | Keep: small, unique trainer/corpus provenance source. |
| `grooming-detector-main` | 6.925 GiB | Delete: obsolete Don copy dominated by old checkpoints and duplicated Git objects. |
| `grooming-detector-main-2` | 9.172 GiB | Delete after extracting unique synthetic CSVs and trainer-state evidence. |

## Nested Git Repositories Before Removal

| Path | HEAD | Branch | Remote |
|---|---|---|---|
| `grooming-detector/.git` | `7aa8a161131f3767627102ba6cee2a2c8d48d217` | `main` | `https://github.com/apcdlidos/grooming-detector` |
| `grooming-detector-main/grooming-detector-trajectory-pipeline/.git` | `fc61d853c39663f8367084dc6f824dcbf75bae3e` | `main` | `https://github.com/den332z/WASD-Thesis.git` |
| `grooming-detector-main-2/grooming-detector-main/grooming-detector-trajectory-pipeline/.git` | `fc61d853c39663f8367084dc6f824dcbf75bae3e` | `main` | `https://github.com/den332z/WASD-Thesis.git` |

The active nested repository contained uncommitted thesis changes and generated
artifacts. Those working-tree files are preserved in place; only the nested Git
metadata/history is being removed at the user's explicit request.

## Preserved From the Duplicate Trees

| New path | SHA-256 | Purpose |
|---|---|---|
| `grooming-detector/data_sources/synthetic/synthetic_grooming_data.csv` | `D5B9B47E1264C7C3FDFB21275E19F9D4C2B2E71A1D1557644290DB686E3D08CF` | Unique synthetic positive-source data for later provenance audit. |
| `grooming-detector/data_sources/synthetic/synthetic_safe_data.csv` | `F354FEA481D07DE210D44F7175BC4F686F657E4097AB0F36139F306DE38FF6B4` | Unique synthetic safe-source data for later provenance audit. |
| `thesis_docs/evidence/layer1_checkpoint_750_trainer_state.json` | `2F3BAB204AFC0EA4BE5EF1B9C9E4DD55136E55A46BEBCA8102AD02E5CC313C17` | Best-checkpoint Layer 1 metrics and original output provenance. |
| `thesis_docs/evidence/layer1_full_run_trainer_state.json` | `232FCF27C0DE0143C010736BE9C24F04D004425B1D13BCDF715DAC45FBF88D50` | Full three-epoch Layer 1 training history. |
| `grooming-detector/data_sources/layer1_training_archive/pan12_final_dataset.csv` | `15F6CE23C72A446A6577B146A18B2C5AB27612F6D898BD464014A661142F7DCB` | Exact archived PAN CSV colocated with the likely Layer 1 training data; differs from the newer active PAN CSV. |
| `grooming-detector/data_sources/layer1_training_archive/train_distillbert.py` | `94D33F7A7E20B46CF3AEE9B0DFAEECF28C4F0917583D64E8F8BD4C073B96893A` | Exact archived trainer from the workspace that produced the checkpoint lineage. |

The active Layer 1 best model is already preserved at
`grooming-detector/trained_model_distillbert/final_moderation_model`; its model
weights are byte-identical to the archived best checkpoint.

The newer active PAN CSV has SHA-256
`4131DC7B78865BBE2A48D155F770DD3743236D161B8430893328FBED5A42D408`;
it is not the same file as the archived Layer 1 PAN CSV. Both are now preserved
under clearly separate provenance paths.

## Git Consolidation

The three verified nested `.git` directories were recursively removed. One new
repository was initialized at `C:\Projects\THESIS\.git` on branch `main`.
No commit has been created yet. A workspace-root `.gitignore` excludes large
model weights, caches, raw PAN corpus files, logs, and recovered transcripts
from ordinary Git tracking.

## Documentation Consolidation

All 15 project-level Markdown files formerly at the workspace root were moved
to `thesis_docs/`. Package-specific README files remain beside their code.

On the subsequent redundancy pass, the four fully superseded model-state
documents (`MODEL_AUTHORITY_MAP.md`, `LABEL_PROVENANCE_AUDIT.md`,
`PROGRESS_REPORT_2026-08-12.md`, and `NEXT_AGENT_HANDOFF.md`) were removed after
their current facts were verified as present in
`CURRENT_STATE_ZERO_AMBIGUITY.md`, `AUTHOR_DISJOINT_EXPERIMENT.md`, and the
chronological log. Nine non-authoritative but potentially useful older drafts,
plans, and raw recovery records were moved under `thesis_docs/archive/` rather
than deleted. The root of `thesis_docs/` now exposes six authoritative Markdown
files, including its index.

## Recovery Notice

Recursive deletion of nested `.git` histories and obsolete duplicate trees is
not recoverable from this workspace. The original remote URLs and HEAD commit
IDs above may allow code-history recovery from their upstream servers, but
uncommitted files that existed only inside deleted duplicate trees will not be
recoverable after deletion.

## Completed Deletions

- Deleted `C:\Projects\THESIS\grooming-detector-main` after validation and
  evidence extraction.
- Deleted `C:\Projects\THESIS\grooming-detector-main-2` after validation and
  evidence extraction.
- Removed regenerable Python `__pycache__` directories and project-local pytest
  temporary directories from the canonical project.
- Removed the final permission-locked `.pytest_cache` using approval restricted
  to that exact cache path. No Python or pytest cache directory remains in the
  canonical project.

Post-cleanup workspace size is approximately 0.795 GiB across 152 files,
reduced from approximately 17.6 GiB across the four former project trees. The
two obsolete directories no longer exist.

## Post-Cleanup User Confirmation

The user explicitly confirmed that `grooming-detector-main-2` was the bundle
containing the latest trained Layer 1 model and the trainer script supplied
earlier. This is consistent with the pre-deletion artifact audit:

- its final/checkpoint-750 weights were byte-identical to the surviving active
  Layer 1 weights (`F90DB66B...E392B`);
- its exact trainer is retained under
  `grooming-detector/data_sources/layer1_training_archive/`;
- its distinct PAN CSV, both synthetic CSVs, and both trainer-state records
  were preserved before deletion.

The latest Layer 1 model itself was therefore not lost. Deleted intermediate
checkpoint copies, optimizer/scheduler states, and nested local Git histories
were not retained and are not locally recoverable. This confirmation resolves
which deleted bundle was the latest Layer 1 source, but it does not reconstruct
the exact executed command or prove the unserialized custom `--label-mode`.

## Post-Cleanup Verification

- Only `C:\Projects\THESIS\.git` exists; no nested `.git` directory remains.
- Root branch is `main` and the Git top-level is `C:\Projects\THESIS`.
- The latest author-disjoint LSTM checkpoint still exists with size 6,340,994
  bytes.
- Its evaluation JSON, the active Layer 1 model weights, and the authoritative
  paper DOCX still exist.
- All project-level Markdown records, including the author-disjoint experiment
  record, are now inside `thesis_docs/`. Only package README files remain beside
  code.

Final retained-artifact hashes:

| Artifact | SHA-256 |
|---|---|
| Latest author-disjoint LSTM | `399865913F51E5FD9E1F372C29D4C0C423BFEED34D51E20D692833E2BBDD24CC` |
| Author-disjoint evaluation JSON | `2E9679A2291AF2DC196592EA8398773332946FDBF9A72427E8E0015F9DF86035` |
| Active Layer 1 DistilBERT weights | `F90DB66B877587D36C4A38BDA9C4A4553D13D07902F4839170EE78BEC06E392B` |
| Authoritative paper DOCX | `F51DC5AF95D9157C1AD4EFA3D1ACC82BCD7ACD6FDB6B476CFD47359392372CAC` |
