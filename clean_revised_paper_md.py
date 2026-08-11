import re

file_path = r"c:\Projects\THESIS\Finals_Revised_Paper_WASD.md"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Unescape escaped markdown punctuation
content = content.replace(r"\-", "-")
content = content.replace(r"\_", "_")
content = content.replace(r"\[", "[")
content = content.replace(r"\]", "]")
content = content.replace(r"\(", "(")
content = content.replace(r"\)", ")")
content = content.replace(r"\.", ".")

# 2. Clean up section heading bold wrappers like "# __1.1 Background__" -> "## 1.1 Background"
content = re.sub(r"^(#+)\s*__\s*(.*?)\s*__", r"\1 \2", content, flags=re.MULTILINE)
content = re.sub(r"^(#+)\s*\*\*\s*(.*?)\s*\*\*", r"\1 \2", content, flags=re.MULTILINE)

# 3. Reduce 3+ consecutive blank lines down to 2
content = re.sub(r"\n{3,}", "\n\n", content)

# Write back cleaned markdown
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")

print(f"Cleaned up {file_path} successfully!")
