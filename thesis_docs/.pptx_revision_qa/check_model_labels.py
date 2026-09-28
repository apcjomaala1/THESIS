"""Read-only text/chart/style checks; deliberately performs no rendering."""
from collections import Counter
from io import BytesIO
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DECK = "WASD - Thesis 2 - F2 and latency revised.pptx"
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "c": "http://schemas.openxmlformats.org/drawingml/2006/chart"}
baseline = ZipFile(BytesIO(subprocess.check_output(["git", "show", f"HEAD:{DECK}"], cwd=ROOT)))
current = ZipFile(ROOT / DECK)
bad = []
for member in current.namelist():
    if re.match(r"ppt/(slides/slide|notesSlides/notesSlide)\d+\.xml$", member):
        root = ET.fromstring(current.read(member))
        text = " ".join(node.text or "" for node in root.findall(".//a:t", NS))
        if re.search(r"\b(primary|enhanced)\b", text, re.I):
            bad.append((member, text))
        if member == "ppt/slides/slide26.xml":
            for row in root.findall(".//a:tr", NS):
                label = " ".join(n.text or "" for n in row.findall(".//a:t", NS))
                if "LSTM" in label:
                    bold = Counter(n.get("b", "unset") for n in row.findall(".//a:rPr", NS))
                    fills = [ET.tostring(n, encoding="unicode") for n in row.findall(".//a:tcPr/a:solidFill", NS)]
                    print("RESULT ROW", label, "BOLD", dict(bold), "FILLS", fills)
    if re.match(r"ppt/charts/chart\d+\.xml$", member):
        new_root = ET.fromstring(current.read(member))
        old_root = ET.fromstring(baseline.read(member))
        def numbers(root):
            return [n.text for ser in root.findall(".//c:ser", NS)
                    for n in ser.findall(".//c:val//c:pt/c:v", NS)]
        assert numbers(new_root) == numbers(old_root), f"Numeric chart values changed: {member}"
        categories = [n.text for n in new_root.findall(".//c:cat//c:pt/c:v", NS)]
        print("CHART", member, categories)
        if member != "ppt/charts/chart4.xml":
            assert "7-feature LSTM" in categories and "775-input LSTM" in categories
for member, text in bad:
    print("REMAINING OLD TERM", member, text)
assert not bad, "Old hierarchical labels remain in presentation text/notes"
print("All deck numeric chart values unchanged; no old model terms in slides or notes.")
