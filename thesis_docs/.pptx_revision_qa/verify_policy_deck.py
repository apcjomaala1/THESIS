"""Structural checks only: no rendering, training, or inference."""
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
SOURCE = ROOT / 'WASD - Thesis 2 - F2 and latency revised.pptx'
STAGED = QA / 'policy_comparison_staged.pptx'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}
def relationships(z, path):
    rel = posixpath.join(posixpath.dirname(path), '_rels', posixpath.basename(path) + '.rels')
    return {n.get('Id'): (n.get('Type').rsplit('/', 1)[-1], posixpath.normpath(posixpath.join(posixpath.dirname(path), n.get('Target')))) for n in ET.fromstring(z.read(rel))}
def ordered_slides(z):
    rels = relationships(z, 'ppt/presentation.xml')
    return [rels[n.get('{'+NS['r']+'}id')][1] for n in ET.fromstring(z.read('ppt/presentation.xml')).findall('.//p:sldId', NS)]
def xmltext(root):
    return ' '.join(n.text or '' for n in root.findall('.//a:t', NS))

content = json.loads((QA / 'policy_deck_content.json').read_text(encoding='utf-8'))
source, staged = ZipFile(SOURCE), ZipFile(STAGED)
parts = ordered_slides(staged)
assert len(parts) == 43
assert [i + 1 for i, p in enumerate(parts) if ET.fromstring(staged.read(p)).get('show') == '0'] == list(range(38, 44))
checked_notes = 0
for i, part in enumerate(parts):
    root = ET.fromstring(staged.read(part))
    assert not re.search(r'\b(primary|enhanced) LSTM\b', xmltext(root), re.I)
    notespart = next(v[1] for v in relationships(staged, part).values() if v[0] == 'notesSlide')
    notes = ET.fromstring(staged.read(notespart))
    body = next(sh for sh in notes.findall('.//p:sp', NS) if sh.find('.//p:ph', NS) is not None and sh.find('.//p:ph', NS).get('type') == 'body')
    actual = '\n'.join(''.join(n.text or '' for n in p.findall('.//a:t', NS)) for p in body.findall('.//a:p', NS)).replace('\r', '\n').strip()
    assert actual == content['slides'][i]['notes'].replace('\r', '\n').strip(), f'Notes mismatch {i+1}'
    checked_notes += 1

def table_rows(index):
    root = ET.fromstring(staged.read(parts[index - 1]))
    table = root.find('.//a:tbl', NS)
    return [[''.join(n.text or '' for n in cell.findall('.//a:t', NS)) for cell in row.findall('a:tc', NS)] for row in table.findall('a:tr', NS)]
assert table_rows(30)[1:] == content['tables']['lstm_enhanced775']
assert table_rows(31)[1:] == content['tables']['lstm_trajectory7']
expected = []
for key, name in [('raw_layer1', 'Maximum Layer 1'), ('weighted', 'Weighted scorer'), ('keyword', 'Keyword rule')]:
    expected.extend([[name] + row for row in content['tables'][key]])
assert table_rows(38)[1:] == expected

charts = [p for p in source.namelist() if re.fullmatch(r'ppt/charts/chart\d+\.xml', p)]
for p in charts:
    assert p in staged.namelist()
    def data(z):
        root = ET.fromstring(z.read(p))
        return [(xmltext(ser), [n.text for n in ser.findall('.//c:cat//c:pt/c:v', NS)], [n.text for n in ser.findall('.//c:val//c:pt/c:v', NS)]) for ser in root.findall('.//c:ser', NS)]
    assert data(source) == data(staged), f'Chart data changed {p}'
assert len(charts) == 4
error_chart = ET.fromstring(staged.read('ppt/charts/chart3.xml'))
assert error_chart.find('.//c:valAx/c:scaling/c:max', NS).get('val') == '90'
for index in (30, 31, 38):
    root = ET.fromstring(staged.read(parts[index - 1]))
    header = root.find('.//a:tbl/a:tr', NS)
    for cell in header.findall('a:tc', NS):
        colors = cell.findall('.//a:rPr/a:solidFill/a:srgbClr', NS)
        assert colors and all(n.get('val').upper() == 'FFFFFF' for n in colors)
for index in (3, 13, 17, 24, 37):
    root = ET.fromstring(staged.read(parts[index - 1]))
    badge = next(sh for sh in root.findall('.//p:sp', NS) if sh.find('p:nvSpPr/p:cNvPr', NS).get('name') == 'Correct divider number')
    assert xmltext(badge) == str(index)
    color = badge.find('p:spPr/a:solidFill/a:srgbClr', NS).get('val')
    assert color.upper() not in ('000000', 'FFFFFF'), color
assert table_rows(26) == [[''.join(n.text or '' for n in cell.findall('.//a:t', NS)) for cell in row.findall('a:tc', NS)] for row in ET.fromstring(source.read(ordered_slides(source)[25])).findall('.//a:tbl/a:tr', NS)]
report = {'status': 'STRUCTURAL_CHECKS_PASSED', 'slides': 43, 'visible': 37, 'hidden': 6,
          'policy_rows_verified_against_receipt': 15, 'speaker_notes_verified': checked_notes,
          'existing_native_charts_unchanged': 4, 'f2_result_table_unchanged': True,
          'error_chart_axis_maximum': 90, 'policy_header_contrast_checked': True,
          'divider_numbers_checked': True,
          'staged_sha256': hashlib.sha256(STAGED.read_bytes()).hexdigest(),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'fonts': {'Calibri': 'reference', 'Calibri Light': 'reference'},
          'visual_qa_passes_allowed': 1,
          'rendered_slides_in_single_batch': len(list((QA / 'policy_visual_pass_2026-09-29').glob('slide-*.png'))),
          'post_pass_corrections_visual_recheck': False}
(QA / 'policy_deck_structural_receipt.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
