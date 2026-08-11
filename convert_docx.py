import mammoth
import os

input_path = r"c:\Users\JM\Asia Pacific College\WASD PBL-Thesis - Documents\Thesis WASD\Main Paper\Chapter 3 TEMPORARY.docx"
output_dir = r"c:\Projects\THESIS"
output_md = os.path.join(output_dir, "Chapter_3_TEMPORARY.md")
images_dir = os.path.join(output_dir, "images")

os.makedirs(images_dir, exist_ok=True)

image_counter = [0]

def convert_image(image):
    image_counter[0] += 1
    extension = image.content_type.split("/")[-1]
    if extension == "jpeg":
        extension = "jpg"
    filename = f"image_{image_counter[0]}.{extension}"
    filepath = os.path.join(images_dir, filename)
    with image.open() as img_bytes:
        with open(filepath, "wb") as f:
            f.write(img_bytes.read())
    return {"src": f"images/{filename}"}

with open(input_path, "rb") as docx_file:
    result = mammoth.convert_to_markdown(
        docx_file,
        convert_image=mammoth.images.img_element(convert_image)
    )

markdown = result.value

# Print any conversion warnings
if result.messages:
    print("Conversion messages:")
    for msg in result.messages:
        print(f"  - {msg}")

with open(output_md, "w", encoding="utf-8") as f:
    f.write(markdown)

print(f"\nConverted successfully!")
print(f"  Markdown: {output_md}")
print(f"  Images extracted: {image_counter[0]}")
print(f"  File size: {os.path.getsize(output_md):,} bytes")
