"""Verify notes match script and all visual/evidence parts remain unchanged."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
SCRIPT = ROOT / 'thesis_docs/PRESENTATION_SPEAKER_SCRIPT.md'
SOURCE = ROOT / 'WASD - Thesis 2 - F2 and latency revised.pptx'
STAGED = QA / 'narrative_notes_only.pptx'
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

text = SCRIPT.read_text(encoding='utf-8')
matches = list(re.finditer(r'^## Slide (\d+): [^\n]+\n(.*?)(?=^## Slide \d+: |^## Presenter reference:|\Z)', text, re.M | re.S))
assert len(matches) == 43
expected = [m[2].strip().replace('\r\n', '\n') for m in matches]
assert 'Exact approved wording:' not in expected[6]
assert '## Presenter reference: exact approved objectives' in text

def rels(z, part):
    relpart = posixpath.join(posixpath.dirname(part), '_rels', posixpath.basename(part) + '.rels')
    return {n.get('Id'): (n.get('Type').split('/')[-1], posixpath.normpath(posixpath.join(posixpath.dirname(part), n.get('Target'))))
            for n in ET.fromstring(z.read(relpart))}

def slideparts(z):
    r = rels(z, 'ppt/presentation.xml')
    return [r[n.get('{' + NS['r'] + '}id')][1] for n in ET.fromstring(z.read('ppt/presentation.xml')).findall('.//p:sldId', NS)]

with ZipFile(SOURCE) as src, ZipFile(STAGED) as out:
    assert set(src.namelist()) == set(out.namelist())
    differences = [p for p in src.namelist() if src.read(p) != out.read(p)]
    assert all(re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', p) for p in differences), differences
    sp = slideparts(src)
    op = slideparts(out)
    assert sp == op and len(op) == 43
    for i, slide in enumerate(op):
        note = next(target for typ, target in rels(out, slide).values() if typ == 'notesSlide')
        root = ET.fromstring(out.read(note))
        body = next(sh for sh in root.findall('.//p:sp', NS)
                    if sh.find('.//p:ph', NS) is not None and sh.find('.//p:ph', NS).get('type') == 'body')
        paragraphs = [''.join(t.text or '' for t in p.findall('.//a:t', NS))
                      for p in body.findall('.//a:p', NS)]
        actual = '\n'.join(paragraphs).replace('\r', '\n').strip()
        assert actual == expected[i], f'Notes mismatch on slide {i + 1}'
    visual_parts = [p for p in sp if re.fullmatch(r'ppt/slides/slide\d+\.xml', p)]
    assert len(visual_parts) == 43
    report = {
        'status': 'PASSED',
        'spoken_notes_rewritten': 38,
        'embedded_notes_matching_script': 43,
        'non_notes_package_entries_identical': len(src.namelist()) - len(differences),
        'changed_members_only_notes_xml': len(differences),
        'visible_slide_content_charts_and_workbooks_unchanged': True,
        'visual_render_performed': False,
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'staged_sha256': hashlib.sha256(STAGED.read_bytes()).hexdigest(),
    }

(QA / 'narrative_notes_receipt.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
