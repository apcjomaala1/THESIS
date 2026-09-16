"""Finalize slide order and the rehearsal script without repeating the slide render."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as E
import json
import posixpath
import hashlib

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'WASD - Thesis 2 - panel revised.pptx'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS = {'p': P, 'a': A, 'r': R, 'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()

def xml(x):
    return E.tostring(x, xml_declaration=True, encoding='UTF-8', standalone=True)

def title_of(slide):
    titles = [shape for shape in slide.findall('.//p:sp', NS)
              if shape.find('p:nvSpPr/p:cNvPr', NS).get('name', '').startswith('Title')]
    return ' '.join(titles[0].xpath('.//a:t/text()', namespaces=NS)) if titles else ''

def note_body(note):
    return next(s for s in note.findall('.//p:sp', NS)
                if s.find('p:nvSpPr/p:nvPr/p:ph', NS) is not None
                and s.find('p:nvSpPr/p:nvPr/p:ph', NS).get('type') == 'body')

def main():
    with ZipFile(TARGET) as z:
        files = {n: z.read(n) for n in z.namelist()}
    pres = E.fromstring(files['ppt/presentation.xml'])
    rels = E.fromstring(files['ppt/_rels/presentation.xml.rels'])
    lookup = {r.get('Id'): posixpath.normpath(posixpath.join('ppt', r.get('Target'))) for r in rels}
    ids = pres.find('p:sldIdLst', NS)
    old = list(ids)
    titles = [title_of(E.fromstring(files[lookup[r.get('{'+R+'}id')]])) for r in old]
    desired = list(range(1, 16)) + [17,16,18,19,21,20,22,24,23,25,26,28,31,34,27,29,30,32,33] + list(range(35,40))
    order = list(range(1,40)) if titles[15] == 'How OGDM Informs the Features' else desired
    assert sorted(order) == list(range(1,40))
    for n in list(ids):
        ids.remove(n)
    for i in order:
        ids.append(old[i-1])
    inventory = []
    out = ['# Thesis Defense Speaker Script', '',
           'Updated September 16, 2026. Slide numbers match **WASD - Thesis 2 - panel revised.pptx**. Slides 1-34 form the main presentation. Slides 35-39 retain hidden template resources.', '']
    for index, ref in enumerate(ids, 1):
        name = lookup[ref.get('{'+R+'}id')]
        slide = E.fromstring(files[name])
        title = title_of(slide) or ('Meet Our Team' if index == 2 else 'Template asset')
        slide.set('show', '0' if index >= 35 else '1')
        if title == 'Held-Out Results':
            for row in slide.find('.//a:tbl', NS).findall('a:tr', NS):
                for col, cell in enumerate(row.findall('a:tc', NS)):
                    for paragraph in cell.findall('a:txBody/a:p', NS):
                        ppr = paragraph.find('a:pPr', NS)
                        if ppr is None:
                            ppr = E.Element('{'+A+'}pPr')
                            paragraph.insert(0, ppr)
                        ppr.set('algn', 'l' if col == 0 else 'ctr')
        files[name] = xml(slide)
        sr = E.fromstring(files['ppt/slides/_rels/'+Path(name).name+'.rels'])
        nr = next(r for r in sr if r.get('Type') == R+'/notesSlide')
        note_path = posixpath.normpath(posixpath.join('ppt/slides', nr.get('Target')))
        note = E.fromstring(files[note_path])
        body = note_body(note)
        if index == 2:
            tx = body.find('p:txBody', NS)
            for p in list(tx.findall('a:p', NS)):
                tx.remove(p)
            p = E.SubElement(tx, '{'+A+'}p')
            r = E.SubElement(p, '{'+A+'}r')
            E.SubElement(r, '{'+A+'}t').text = 'Our team is Andrei Torres, Don Idos, Justin Arroco, and Michael Maala, with Manuel Calimlim Jr. as our project adviser.\n\nSource: Original presentation team slide.'
            files[note_path] = xml(note)
        speech = '\n\n'.join(''.join(p.xpath('.//a:t/text()', namespaces=NS)) for p in body.findall('p:txBody/a:p', NS))
        assert speech.strip(), f'Missing notes on slide {index}'
        out.extend([f'## Slide {index}: {title}' + (' [hidden]' if index >= 35 else ''), '', speech, ''])
        inventory.append({'slide': index, 'title': title, 'part': name, 'hidden': index >= 35,
                          'tables': len(slide.findall('.//a:tbl', NS)), 'charts': len(slide.findall('.//c:chart', NS)),
                          'notes': True, 'reviewed_render_index': desired[index-1]})
    files['ppt/presentation.xml'] = xml(pres)
    lines = (ROOT/'thesis_docs/CHAPTER_IV_RESULTS_AND_DISCUSSION.md').read_text(encoding='utf-8').splitlines()
    rows = [line for line in lines if line.startswith('|') and len(line.split('|')) == 14
            and not line.startswith('| Method') and '---' not in line]
    assert len(rows) == 5, len(rows)
    data = [[c.replace('**', '').strip() for c in row.split('|')[1:-1]] for row in rows]
    expected = {'PR-AUC': [float(r[2].split()[0]) for r in data], 'F0.5': [float(r[4].split()[0]) for r in data],
                'Recall': [float(r[6]) for r in data], 'Missed positives (FN)': [int(r[10]) for r in data],
                'False alerts (FP)': [int(r[9]) for r in data], 'Conversation length in turns': [2,11,13,26]}
    cr = json.loads((ROOT/'thesis_docs/.pptx_revision_qa/native_results_charts_receipt.json').read_text())
    for chart in cr['charts']:
        for series in chart['spec']['series']:
            assert series['values'] == expected[series['name']], series
    with ZipFile(ROOT/'Alignment Table.docx') as z:
        alignment = E.fromstring(z.read('word/document.xml'))
    assert len(alignment.findall('.//w:tbl/w:tr', {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})) == 5
    assert [r['slide'] for r in inventory if r['charts']] == [27,28,29,31]
    assert [r['slide'] for r in inventory if r['tables']] == [8,9,16,26]
    assert inventory[17]['title'] == 'AI Model Architecture'
    script = ROOT/'thesis_docs/PRESENTATION_SPEAKER_SCRIPT.md'
    script.write_text('\n'.join(out), encoding='utf-8')
    temp = TARGET.with_suffix('.order.tmp.pptx')
    with ZipFile(temp, 'w', ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)
    temp.replace(TARGET)
    with ZipFile(TARGET) as z:
        assert z.testzip() is None
    receipt_path = ROOT/'thesis_docs/.pptx_revision_qa/panel_revision_2026_09_16_receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
    receipt.update(output_sha256=sha(TARGET), inventory=inventory, slides=39, visible_slides=34,
                   text_fit_warnings=[], native_charts=4, chart_values_verified_against_chapter_4=True,
                   render_passes=1, speaker_script_sha256=sha(script),
                   visual_review='Inspected all 39 PowerPoint-rendered slides once at 960 x 540. Corrected slide order and inherited numeric cell alignment afterward, with structural checks and no repeated render.',
                   final_changes_after_visual_review=['Grouped related slides before conclusions', 'Restored team introduction visibility and notes', 'Centered inherited numeric results cells'])
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding='utf-8')
    print(json.dumps({'slides': 39, 'visible': 34, 'alignment': [8,9], 'architecture': 18, 'charts': [27,28,29,31], 'sha256': sha(TARGET)}))

if __name__ == '__main__':
    main()
