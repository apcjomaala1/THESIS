"""Synchronize descriptive chart labels and native embedded data, without rendering.

Office ChartData activation stalls locally. This narrow package edit preserves
all chart numeric values and makes the existing embedded workbooks match them.
"""
from copy import deepcopy
from io import BytesIO
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "WASD - Thesis 2 - F2 and latency revised.pptx"
C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"c": C, "s": S}

def packed(source, replacements):
    output = BytesIO()
    with ZipFile(output, "w") as target:
        for info in source.infolist():
            target.writestr(info, replacements.get(info.filename, source.read(info.filename)))
    return output.getvalue()

def encoded(root):
    return E.tostring(root, encoding="UTF-8", xml_declaration=True, standalone=True)

replacements = {}
with ZipFile(PATH) as deck:
    for number in range(1, 5):
        member = f"ppt/charts/chart{number}.xml"
        root = E.fromstring(deck.read(member))
        series = root.findall(".//c:ser", NS)
        values = [[n.text for n in ser.findall(".//c:val//c:pt/c:v", NS)] for ser in series]
        categories = (["Keyword", "Maximum L1", "Weighted", "7-feature LSTM", "775-input LSTM"]
                      if number != 4 else ["Missed case 1", "Missed case 2", "Missed case 3"])
        assert all(len(v) == len(categories) for v in values)
        rels = E.fromstring(deck.read(f"ppt/charts/_rels/chart{number}.xml.rels"))
        target = next(n.get("Target") for n in rels if n.get("Type", "").endswith("/package"))
        workbook_member = "ppt/" + target.removeprefix("../")
        with ZipFile(BytesIO(deck.read(workbook_member))) as workbook:
            book = E.fromstring(workbook.read("xl/workbook.xml"))
            sheet_name = book.find("s:sheets/s:sheet", NS).get("name")
            worksheet = E.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
            data = worksheet.find("s:sheetData", NS)
            data.clear()
            names = ["Method"] + [ser.findtext("c:tx/c:v", namespaces=NS) or f"Series {i+1}" for i, ser in enumerate(series)]
            for row_index in range(len(categories) + 1):
                row = E.SubElement(data, f"{{{S}}}row", r=str(row_index + 1))
                row_values = names if row_index == 0 else [categories[row_index-1]] + [v[row_index-1] for v in values]
                for column, value in enumerate(row_values):
                    is_string = row_index == 0 or column == 0
                    cell = E.SubElement(row, f"{{{S}}}c", r=f"{chr(65+column)}{row_index+1}", t="inlineStr" if is_string else "n")
                    if is_string:
                        E.SubElement(E.SubElement(cell, f"{{{S}}}is"), f"{{{S}}}t").text = value
                    else:
                        E.SubElement(cell, f"{{{S}}}v").text = value
            worksheet.find("s:dimension", NS).set("ref", f"A1:{chr(65+len(series))}{len(categories)+1}")
            replacements[workbook_member] = packed(workbook, {"xl/worksheets/sheet1.xml": encoded(worksheet)})
        for i, ser in enumerate(series):
            cat = ser.find("c:cat", NS)
            cat.clear()
            ref = E.SubElement(cat, f"{{{C}}}strRef")
            E.SubElement(ref, f"{{{C}}}f").text = f"'{sheet_name}'!$A$2:$A${len(categories)+1}"
            cache = E.SubElement(ref, f"{{{C}}}strCache")
            E.SubElement(cache, f"{{{C}}}ptCount", val=str(len(categories)))
            for j, label in enumerate(categories):
                E.SubElement(E.SubElement(cache, f"{{{C}}}pt", idx=str(j)), f"{{{C}}}v").text = label
            val = ser.find("c:val", NS)
            existing_cache = next(n for n in val.iter() if E.QName(n).localname in {"numLit", "numCache"})
            numeric_cache = deepcopy(existing_cache)
            numeric_cache.tag = f"{{{C}}}numCache"
            val.clear()
            ref = E.SubElement(val, f"{{{C}}}numRef")
            column = chr(66+i)
            E.SubElement(ref, f"{{{C}}}f").text = f"'{sheet_name}'!${column}$2:${column}${len(categories)+1}"
            ref.append(numeric_cache)
        replacements[member] = encoded(root)
    updated = packed(deck, replacements)
PATH.write_bytes(updated)
print("Synchronized four chart category caches and native worksheets; numeric chart values unchanged.")
