"""Retain PowerPoint-authored note XML while preserving every other PPTX part."""
from pathlib import Path
from zipfile import ZipFile
import re

ROOT = Path(__file__).resolve().parents[2]
QA = Path(__file__).resolve().parent
source = ROOT / 'WASD - Thesis 2 - F2 and latency revised.pptx'
office_staged = QA / 'narrative_notes_staged.pptx'
notes_only = QA / 'narrative_notes_only.pptx'
if notes_only.exists():
    raise FileExistsError(notes_only)
with ZipFile(source) as original, ZipFile(office_staged) as edited, ZipFile(notes_only, 'w') as output:
    assert set(original.namelist()) == set(edited.namelist())
    count = 0
    for info in original.infolist():
        path = info.filename
        if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', path):
            data = edited.read(path)
            count += 1
        else:
            data = original.read(path)
        output.writestr(info, data)
assert count == 43
print(f'Packaged {count} edited notes parts and preserved all other original parts.')
