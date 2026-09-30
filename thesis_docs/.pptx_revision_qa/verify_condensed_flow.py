"""Validate the condensed slide order, evidence, and embedded narration."""
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
SRC = ROOT / 'WASD - Thesis 2 - F2 and latency revised.pptx'
DST = QA / 'condensed_flow_staged.pptx'
manifest = json.loads((QA / 'condensed_flow_manifest.json').read_text(encoding='utf-8'))
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def rels(z, path):
    rp = posixpath.join(posixpath.dirname(path), '_rels', posixpath.basename(path) + '.rels')
    return {n.get('Id'): (n.get('Type').split('/')[-1], posixpath.normpath(posixpath.join(posixpath.dirname(path), n.get('Target'))))
            for n in ET.fromstring(z.read(rp))}
def slides(z):
    r = rels(z, 'ppt/presentation.xml')
    return [r[n.get('{' + NS['r'] + '}id')][1] for n in ET.fromstring(z.read('ppt/presentation.xml')).findall('.//p:sldId', NS)]
def content(z, part):
    return ' '.join(n.text or '' for n in ET.fromstring(z.read(part)).findall('.//a:t', NS))
def table(z, part):
    root = ET.fromstring(z.read(part))
    return [[''.join(n.text or '' for n in cell.findall('.//a:t', NS)) for cell in row.findall('a:tc', NS)]
            for row in root.findall('.//a:tbl/a:tr', NS)]
def chart_data(z, part):
    root = ET.fromstring(z.read(part))
    return tuple((tuple(n.text for n in s.findall('.//c:cat//c:pt/c:v', NS)),
                  tuple(n.text for n in s.findall('.//c:val//c:pt/c:v', NS)))
                 for s in root.findall('.//c:ser', NS))

with ZipFile(SRC) as source, ZipFile(DST) as final:
    assert final.testzip() is None
    before, after = slides(source), slides(final)
    assert len(before) == 43 and len(after) == 31
    hidden = [i for i, p in enumerate(after, 1) if ET.fromstring(final.read(p)).get('show') == '0']
    assert hidden == list(range(25, 32)), hidden
    for i, item in enumerate(manifest['slides']):
        part = after[i]
        if item['source_index'] is not None:
            expected_content = content(source, before[item['source_index'] - 1])
            if i + 1 == 24:
                assert expected_content.endswith('37')
                expected_content = expected_content[:-2] + '24'
            assert content(final, part) == expected_content, (i + 1, item['source_index'])
        note = next(p for kind, p in rels(final, part).values() if kind == 'notesSlide')
        root = ET.fromstring(final.read(note))
        body = next(sh for sh in root.findall('.//p:sp', NS)
                    if sh.find('.//p:ph', NS) is not None and sh.find('.//p:ph', NS).get('type') == 'body')
        actual = '\n'.join(''.join(t.text or '' for t in p.findall('.//a:t', NS))
                           for p in body.findall('.//a:p', NS)).replace('\r', '\n').strip()
        assert actual == item['notes'].strip(), f'Slide {i+1} notes mismatch'
    assert table(final, after[5]) == table(source, before[7])
    assert table(final, after[6]) == table(source, before[8])
    assert table(final, after[8]) == table(source, before[15])
    assert table(final, after[15]) == table(source, before[25])
    assert table(final, after[25]) == table(source, before[37])
    actual_policy = table(final, after[18])
    assert actual_policy[0] == ['Model', 'Policy', 'Found', 'Missed', 'False alerts', 'Precision', 'Recall']
    for row, expected in zip(actual_policy[1:], manifest['policy_rows'], strict=True):
        assert row[1:] == expected[1:], (row, expected)
        assert row[0] == ('Embedding-and-Feature LSTM' if expected[0].startswith('Embedding') else 'Trajectory-Feature LSTM')
    source_charts = [p for p in source.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml', p)]
    final_charts = [p for p in final.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml', p)]
    assert len(source_charts) == 4 and len(final_charts) == 3
    removed_chart = next(p for kind, p in rels(source, before[27]).values() if kind == 'chart')
    assert Counter(chart_data(final, p) for p in final_charts) == Counter(chart_data(source, p) for p in source_charts if p != removed_chart)
    script = (QA / 'condensed_speaker_script_staged.md').read_text(encoding='utf-8')
    heads = list(re.finditer(r'^## Slide (\d+):', script, re.M))
    assert len(heads) == 31 and [int(h[1]) for h in heads] == list(range(1, 32))
    assert '## Presenter reference: exact approved objectives' in script
    report = {'status': 'PASSED', 'main_slides': 24, 'hidden_evidence': 2,
              'hidden_template_resources': 5, 'notes_synced': 31,
              'approved_research_question_and_objective_slides_preserved': True,
              'early_alignment_tables_preserved': 2,
              'f2_result_table_preserved': True, 'combined_policy_rows_verified': 6,
              'native_charts_retained_with_values_unchanged': 3,
              'source_sha256': hashlib.sha256(SRC.read_bytes()).hexdigest(),
              'staged_sha256': hashlib.sha256(DST.read_bytes()).hexdigest()}
(QA / 'condensed_flow_receipt.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
