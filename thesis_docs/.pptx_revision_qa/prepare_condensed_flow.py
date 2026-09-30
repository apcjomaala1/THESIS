"""One narrative map for both the concise deck and its read-aloud script."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
SCRIPT = ROOT / 'thesis_docs/PRESENTATION_SPEAKER_SCRIPT.md'
text = SCRIPT.read_text(encoding='utf-8')
heads = list(re.finditer(r'^## Slide (\d+): (.+)$', text, re.M))
assert len(heads) == 43 and [int(m[1]) for m in heads] == list(range(1, 44))
old = {}
for i, h in enumerate(heads):
    end = heads[i + 1].start() if i + 1 < len(heads) else text.index('## Presenter reference:')
    block = text[h.end():end].strip()
    citation = re.search(r'^(?:Source|Sources): .+$', block, re.M)
    assert citation, h[1]
    old[int(h[1])] = {'title': h[2], 'spoken': block[:citation.start()].strip(),
                      'citation': citation[0].split(': ', 1)[1]}

# No source slide is duplicated in the main flow. Short-case evidence and all
# baseline-policy rows remain available as hidden backup, not presenter detours.
sequence = [1, 2, 4, 6, 7, 8, 9, 14, 16, 18, 11, 20, 21, 25, 23,
            26, 27, 29, None, 32, 34, 35, 36, 37, 33, 38, 39, 40, 41, 42, 43]
assert len(sequence) == 31 and len([n for n in sequence if n is not None]) == 30

custom = {
3: ("Background of the Study", """A single message can be hard to judge without the exchange around it. Keyword filters catch explicit wording, but gradual or indirect interactions may only make sense across several turns. User reports also depend on someone recognizing the problem first. That gap motivates a module that follows how contextual evidence develops across a conversation and helps prioritize what a moderator should review.""", [4, 5]),
8: ("Why Context and Sequence Matter", """DistilBERT helps interpret a turn in its nearby conversational context. The LSTM then follows how evidence changes over the full exchange. The Online Grooming Discourse Model motivated this attention to developing, recurring interaction rather than a fixed list of words or a rigid sequence of stages. We turn that motivation into measurable signals on the next slide.""", [14, 15]),
10: ("AI Model Architecture", """A new turn enters with recent context. Layer 1 produces an author-derived proxy score, while a fixed encoder supplies a current-turn embedding. Seven features track the conversation as it unfolds. The Trajectory-Feature LSTM receives those seven features; the Embedding-and-Feature LSTM receives them plus 768 embedding values. Each produces a conversation score, which a validation-selected cutoff turns into a flag for human review.""", [18, 10]),
12: ("Why Authors Stay in One Partition", """We preserve conversation order and construct derived resources using training data only. We also partition by connected authors, not by individual rows. If one chat has A and B and another has B and C, both chats stay in the same partition through their shared author. This prevents recurring participants from appearing in both development and test. We verified zero author overlap across the partitions.""", [20, 19]),
14: ("Frozen Experimental Setup", """Training contains 13,031 conversations, validation 1,827, and test 1,862. Only 44 test conversations are positive, so missed-case and false-alert counts matter alongside percentages. Connected authors stay in one partition. We selected operating cutoffs on validation and applied them to preserved test scores. The original evaluation used F0.5; the later F1 and F2 comparisons did not retrain the models or rerun inference.""", [25, 22]),
17: ("Detection Performance Across Methods", """PR-AUC describes how well a method ranks positive conversations across possible cutoffs; F2 describes our recall-oriented operating point. The embedding model has the highest observed PR-AUC, while the trajectory model has the highest observed F2. Neither figure alone declares a universal winner. For the specific sequence-model claim, compare the trajectory LSTM with weighted scoring: both use the same seven inputs, but only one learns their order.""", [27, 28]),
19: ("Cutoff Choice: Coverage and Alerts", """These six rows use the same two trained LSTMs and the same saved test scores; only the validation-selected cutoff changes. For the embedding model, F1 finds 43 of 44 positives with 14 false alerts, while F2 finds all 44 with 41 false alerts. That last positive adds 27 alerts in this test. The trajectory model behaves differently: F1 adds two alerts over F0.5 without finding another positive. F2 remains our main recall-first reporting policy. The table shows why a later moderator-workflow study must choose its operating point deliberately.""", [30, 31]),
23: ("Next Evaluation Steps", """We would first test the fixed models and cutoffs on contemporary chats and measure how moderators handle the resulting queue. The embedding model's F1 and F2 settings are the clearest workflow comparison: one additional positive at F2 came with 27 additional alerts in this test. The three trajectory-model misses were short conversations, so fixed-prefix testing also deserves attention. Production work still needs longer chats and concurrent-load measurement; onset detection requires independent expert annotations.""", [36, 33]),
}

slides = []
for index, source_index in enumerate(sequence, 1):
    if index in custom:
        title, spoken, refs = custom[index]
    else:
        assert source_index is not None
        title, spoken, refs = old[source_index]['title'], old[source_index]['spoken'], [source_index]
    citations = '; '.join(old[n]['citation'] for n in refs)
    slides.append({'index': index, 'source_index': source_index, 'title': title,
                   'spoken': spoken, 'citation': citations,
                   'notes': spoken + '\n\nSources: ' + citations,
                   'hidden': index >= 25})

assert [s['source_index'] for s in slides[24:26]] == [33, 38]
assert all(s['source_index'] in range(39, 44) for s in slides[26:])
receipt = json.loads((ROOT / 'thesis_docs/.threshold_analysis/test_threshold_policy_comparison.json').read_text(encoding='utf-8'))
rows = []
for key, short in [('lstm_enhanced775', 'Embedding + features'), ('lstm_trajectory7', 'Trajectory features')]:
    for policy in ('F0.5', 'F1', 'F2'):
        v = receipt['results'][key]['policies'][policy]
        rows.append([short, policy, str(v['tp']), str(v['fn']), str(v['fp']),
                     f'{v["precision"]:.1%}', f'{v["recall"]:.1%}'])
manifest = {'source_slide_count': 43, 'main_slide_count': 24,
            'backup_slide_count': 2, 'template_slide_count': 5,
            'slides': slides, 'policy_rows': rows}
(QA / 'condensed_flow_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

reference = text[text.index('## Presenter reference:'):].strip()
header = ("# Thesis Defense Speaker Script\n\n"
          "Updated September 30, 2026 for the 24-slide main presentation in "
          "**WASD - Thesis 2 - F2 and latency revised.pptx**. Slides 25-26 are hidden evidence backup; "
          "slides 27-31 are retained hidden template resources. Citations and the approved "
          "objective wording below are presenter references, not lines to read aloud.\n\n")
draft_script = header + '\n\n'.join(
    f'## Slide {s["index"]}: {s["title"]}{" [hidden]" if s["hidden"] and s["index"] in (25,26) and not s["title"].endswith("[hidden]") else ""}\n\n{s["notes"]}'
    for s in slides) + '\n\n' + reference + '\n'
(QA / 'condensed_speaker_script_staged.md').write_text(draft_script, encoding='utf-8')
print('Prepared 24 main slides, two evidence backups, five template resources, and 31 aligned scripts.')
