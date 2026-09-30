"""Prepare deck content from the existing script and verified policy receipt."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
script_path = ROOT / 'thesis_docs/PRESENTATION_SPEAKER_SCRIPT.md'
text = script_path.read_text(encoding='utf-8')
matches = list(re.finditer(r'^## Slide (\d+): (.+)$', text, re.M))
assert len(matches) == 40, 'Run once against the 40-slide source script.'
slides = []
for i, match in enumerate(matches):
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    slides.append({'title': match[2], 'notes': text[match.end():end].strip()})

def revise(n, notes):
    slides[n - 1]['notes'] = notes.strip()

revise(17, '''I will now explain the architecture, how we separated the data, and how validation selects the conversation cutoff. The trained models stay fixed when we compare different cutoff policies.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Chapter III''')
revise(19, '''We preserve conversation and turn identifiers, maintain chronological context, and keep connected authors in one partition. Training supplies the learned models and derived resources. Validation selects checkpoints and operating cutoffs. The original evaluation used F0.5; the later F1 and F2 comparison applies validation-selected cutoffs to the same saved test scores. We did not retrain or rerun model inference.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.3 and 3.5''')
revise(23, '''F0.5 emphasizes precision, F1 balances precision and recall, and F2 gives recall more weight. Our main reporting policy is F2 because the study focuses on reducing missed positive conversations. We maximize each method's F2 on validation to select its cutoff; this does not mean training the model with F2. We still report precision and false alerts so the screening cost is clear. The original test evaluation used F0.5. The later F1/F2 comparison reuses saved test scores with cutoffs selected on validation, not on test. The results section shows what each policy changes.

Sources: thesis_docs/Finals_Revised_Paper_WASD.md, Sections 3.5.1-3.5.3; thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1''')
revise(24, '''The next table and graphs show the Chapter IV F2 results. We then compare F0.5, F1, and F2 to explain the detection and false-alert tradeoff. The local benchmark addresses the panel's latency question.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1, 4.1a, and 4.4''')
revise(25, '''Training contains 13,031 conversations with 319 positives; validation has 1,827 with 49 positives; test has 1,862 with 44 positives. Every connected-author group stays in one partition, with zero author overlap. The original evaluation used F0.5. The later F1/F2 comparison used cutoffs selected only on validation and the same saved test scores, without new training or inference. All confusion counts in this presentation count conversations.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Sections 4.1 and 4.2.1''')
slides[25]['title'] = 'Conversation Results: F2 Policy'
revise(33, '''These conclusions answer the unchanged research objectives. First, the comparison quantifies the missed positives and false alerts of the tested static methods. Second, we developed a complete contextual and behavioral module with a review interface. Third, under F2 the Trajectory-Feature LSTM reduced weighted scoring's six misses to three, while the Embedding-and-Feature LSTM found all 44 positives. The paired comparison supports the trajectory model's F2 and ranking gains over weighted scoring. The policy comparison then makes the review workload explicit: the embedding model at F1 finds 43 positives with 14 false alerts. Together, these findings show how sequence modeling can broaden conversation coverage and how cutoff selection changes the review tradeoff.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Sections 5.1-5.2''')
revise(34, '''Our next step is an independent evaluation on contemporary chats with the models and cutoffs fixed in advance. For a workflow with limited review capacity, compare the Embedding-and-Feature LSTM's F1 option against F2: in this test, F1 found 43 of 44 positives with 14 false alerts, while F2 found all 44 with 41 false alerts. That is 27 additional false alerts to catch one more positive. The workflow study should measure missed-case costs, moderator capacity, and review outcomes rather than assume either option is best everywhere. We also recommend longer-history and concurrent-load latency tests, caching or incremental processing, and independently reviewed onset annotations for a separate early-detection study.

Sources: thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Section 5.3, especially Recommendation 7; thesis_docs/PANEL_COMMENTS_MATRIX.md''')
revise(35, '''GroomShield provides two tested sequence models. Under the F2 policy, the Trajectory-Feature LSTM found 41 of 44 positives with 21 false alerts and improved F2 over static scoring of the same seven features. The Embedding-and-Feature LSTM found all 44 with 41 false alerts. Its F1 option found 43 with 14 false alerts, making it a clear candidate for a capacity-limited review study. The contribution is the architecture, the measured sequence-model advantage, and an explicit view of the operating-policy tradeoff. Thank you. We welcome your questions.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Tables 4.1-4.2; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Sections 5.2-5.3''')

new_slides = [
    {'title': 'Embedding Model: Three Cutoff Policies', 'notes': '''This is the Embedding-and-Feature LSTM with the same trained weights under three validation-selected cutoff policies. TP means correctly detected positives; FN means missed positives; FP means false alerts; TN means correctly rejected negatives. There are 44 positives and 1,818 negatives in every row. F0.5 finds 41 positives with six false alerts. F1 finds 43 with 14 false alerts. F2 finds all 44 with 41 false alerts. From F1 to F2, we catch one additional positive and add 27 false alerts. F2 remains our recall-first reporting policy. F1 is the option we recommend evaluating when review capacity is limited, not a universally proven operating choice. These are the same saved test scores; only the cutoff changes.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1 and Table 4.1a; thesis_docs/CHAPTER_V_SUMMARY_CONCLUSIONS_AND_RECOMMENDATIONS.md, Recommendation 7'''},
    {'title': 'Trajectory Model: Three Cutoff Policies', 'notes': '''This is the Trajectory-Feature LSTM, again with fixed trained weights. F0.5 finds 40 of 44 positives with seven false alerts. F1 also finds 40, but produces nine false alerts. F2 finds 41 with 21 false alerts. F1 is not automatically a better middle option: here it adds false alerts without catching an additional positive. F2 reduces the misses from four to three. We chose each cutoff using validation, not by searching these test results. Full baseline policy counts are in the backup slide.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Section 4.2.1 and Table 4.1a'''}]
slides[29:29] = new_slides
slides.insert(37, {'title': 'Baseline Policy Comparison [hidden]', 'notes': '''Backup evidence for the three static baselines. All rows use the same test partition: 1,862 conversations, including 44 positives and 1,818 negatives. Cutoff policies appear in F0.5, F1, F2 order. Maximum Layer 1 increases detections from 23 to 26 to 39, but false alerts increase from 18 to 21 to 78. Weighted scoring makes the same F0.5 and F1 decisions, then catches two additional positives under F2 with 11 additional false alerts. The keyword rule is binary, so all three selected policies make the same decisions. TP/FN/FP/TN mean detected positives, missed positives, false alerts, and correctly rejected negatives. Policy labels describe the validation selection objective, not the metric value on these test rows.

Sources: thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md, Table 4.1a; thesis_docs/.threshold_analysis/test_threshold_policy_comparison.json'''})
assert len(slides) == 43
header = '# Thesis Defense Speaker Script\n\nUpdated September 29, 2026. Slide numbers match **WASD - Thesis 2 - F2 and latency revised.pptx**. Slides 1-37 form the main presentation. Slide 38 is a hidden policy-comparison backup; slides 39-43 retain hidden template resources.\n\n'
script_path.write_text(header + '\n\n'.join(f'## Slide {n}: {s["title"]}\n\n{s["notes"]}' for n, s in enumerate(slides, 1)) + '\n', encoding='utf-8')
receipt = json.loads((ROOT / 'thesis_docs/.threshold_analysis/test_threshold_policy_comparison.json').read_text(encoding='utf-8'))
assert receipt['test_conversations'] == 1862 and receipt['test_positive'] == 44
tables = {}
for key, model in receipt['results'].items():
    tables[key] = [[p, str(v['tp']), str(v['fn']), str(v['fp']), str(v['tn']), f'{v["precision"]:.2%}', f'{v["recall"]:.2%}'] for p, v in model['policies'].items()]
manifest = {'slides': slides, 'tables': tables, 'source_receipt': str(ROOT / 'thesis_docs/.threshold_analysis/test_threshold_policy_comparison.json')}
(QA / 'policy_deck_content.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print('Prepared 43 slide scripts and 15 verified policy rows.')
