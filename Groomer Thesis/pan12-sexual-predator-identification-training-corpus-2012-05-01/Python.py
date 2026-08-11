import xml.etree.ElementTree as ET
import html
import csv

# 1. LOAD YOUR LABEL FILES
print("Loading labels...")
with open('pan12-sexual-predator-identification-training-corpus-predators-2012-05-01.txt') as f:
    predators = set(line.strip() for line in f)

suspicious_lines = set()
with open('pan12-sexual-predator-identification-diff.txt') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) == 2:
            suspicious_lines.add(f"{parts[0]}_{parts[1]}")

# 2. STREAM THE XML AND SAVE DIRECTLY TO CSV
# IMPORTANT: Make sure this filename matches your 100MB XML file exactly
xml_file = 'pan12-sexual-predator-identification-training-corpus-2012-05-01.xml' 

print("Processing XML... this may take a minute for 100MB.")

with open('pan12_final_dataset.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['conv_id', 'line', 'author', 'text', 'is_predator', 'is_suspicious']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    context = ET.iterparse(xml_file, events=('start', 'end'))
    current_conv_id = None
    count = 0

    for event, elem in context:
        if event == 'start' and elem.tag == 'conversation':
            current_conv_id = elem.get('id')
        
        if event == 'end' and elem.tag == 'message':
            line_num = elem.get('line')
            
            # Safely get author
            author_elem = elem.find('author')
            author_id = author_elem.text if author_elem is not None else "unknown"
            
            # Safely get text (FIX for the TypeError)
            text_elem = elem.find('text')
            raw_text = text_elem.text if text_elem is not None and text_elem.text is not None else ""
            
            # Clean and label
            clean_text = html.unescape(raw_text)
            is_predator = 1 if author_id in predators else 0
            is_suspicious = 1 if f"{current_conv_id}_{line_num}" in suspicious_lines else 0
            
            writer.writerow({
                'conv_id': current_conv_id,
                'line': line_num,
                'author': author_id,
                'text': clean_text,
                'is_predator': is_predator,
                'is_suspicious': is_suspicious
            })
            
            count += 1
            if count % 10000 == 0:
                print(f"Processed {count} messages...")
            
            # Memory management
            elem.clear()

print(f"Finished! Successfully created 'pan12_final_dataset.csv' with {count} rows.")