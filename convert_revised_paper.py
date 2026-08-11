import mammoth
import os

input_path = r"c:\Projects\THESIS\Finals Revised Paper WASD.docx"
output_md = r"c:\Projects\THESIS\Finals_Revised_Paper_WASD.md"

with open(input_path, "rb") as docx_file:
    result = mammoth.convert_to_markdown(docx_file)

with open(output_md, "w", encoding="utf-8") as f:
    f.write(result.value)

print(f"Successfully converted {input_path} to {output_md}")
print(f"Output size: {len(result.value):,} characters")
