# Layer 1 Data Sources and Annotation Gate

The current Layer 1 retraining gate is **blocked**. None of the preserved labels
is yet acceptable as final independent message-level grooming ground truth.

## Generated Evidence

- `layer1_dataset_manifest.json` records hashes, schemas, counts, label origins,
  frozen PAN split coverage, source decisions, and required remediation.
- `layer1_annotation_candidates.csv` contains 1,335 synthetic messages prepared
  for two independent reviews. The existing generated label is evidence only;
  reviewers must not copy it automatically.
- Regenerate both files by running `python audit_layer1_dataset.py` from
  `grooming-detector-trajectory-pipeline/`.

## Binary Message Label Rubric

Label the **current message**, using at most the two preceding messages for
context:

- `1` - the current message contains observable grooming-related behavior,
  such as targeted personal/age/location probing, sexualization, boundary
  testing, secrecy requests, isolation/manipulation, migration to private
  contact, requests for images/contact/meeting, or escalation toward
  exploitation.
- `0` - the current message does not contain observable grooming-related
  behavior. Generic greetings, ordinary game discussion, and neutral responses
  remain `0` even when spoken by a scripted predator role.
- `U` - genuinely ambiguous from the available context. Do not force `U` to a
  binary value before adjudication.

Do not infer a positive label from the speaker name, PAN predator identity,
synthetic scenario, or PAN diff membership.

## Review Procedure

1. Freeze this worksheet and its SHA-256 hash before review.
2. Reviewer 1 and Reviewer 2 work independently and record `0`, `1`, or `U`,
   their reviewer IDs, and short notes where needed.
3. Compare reviews only after both are complete. Report raw agreement and
   Cohen's kappa.
4. An adjudicator resolves disagreements and all `U` rows without seeing the
   generated label as authoritative.
5. Set `include_for_training` only after adjudication. Record a reason for every
   excluded row.
6. Generate the final frozen train/validation/test row manifest. Keep all rows
   from a synthetic conversation in one partition; treat placeholder identities
   as conversation-local only after confirming each conversation was generated
   independently.

PAN may optionally provide explicitly described weak author-level supervision,
but only PAN conversations assigned to `train` in the frozen author-disjoint
audit may enter fitting. PAN validation/test conversations may never be used
for Layer 1 fitting or checkpoint selection.
