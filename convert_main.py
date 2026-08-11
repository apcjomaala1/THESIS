import mammoth
import os

input_path = r"c:\Users\JM\Asia Pacific College\WASD PBL-Thesis - Documents\Thesis WASD\Main Paper\Main paper Chapters 1-3.docx"
output_dir = r"c:\Projects\THESIS"
output_md = os.path.join(output_dir, "Main_paper_Chapters_1-3.md")

with open(input_path, "rb") as docx_file:
    result = mammoth.convert_to_markdown(docx_file)

markdown = result.value

if result.messages:
    print("Conversion messages:")
    for msg in result.messages:
        print(f"  - {msg}")

with open(output_md, "w", encoding="utf-8") as f:
    f.write(markdown)

print(f"Converted successfully!")
print(f"  File size: {os.path.getsize(output_md):,} bytes")
print(f"  Lines: {len(markdown.splitlines())}")
