import pdfplumber
import re
import os

# Change the directory path to the new folder
#dir_path = "CAMI - data/cami_summary_-_pathophysiology"
dir_path = "/Users/emmanu3l/Desktop/UNITO/YEAR 3/INFECTIOUS, DERMATO, HEMATO/HEMATO/split pdf"

# Step 1: Find all PDF files in the directory
pdf_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.pdf')]

# Step 2: Define bullet merging function
def merge_bullet_lines(lines):
    bullets = {'●', '○', '◆', '◇'}
    result = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line in bullets and i > 0:
            prev = result.pop() if result else ''
            merged = f"{line} {prev}"
            result.append(merged)
        else:
            result.append(line)
        i += 1
    return result

# Step 3: Process each PDF
for pdf_file in pdf_files:
    pdf_path = os.path.join(dir_path, pdf_file)
    txt_file = os.path.splitext(pdf_file)[0].replace(' ', '_').replace(':', '') + ".txt"
    txt_path = os.path.join(dir_path, txt_file)
    all_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=1)
            if text:
                all_text.extend(text.splitlines())
    processed_lines = merge_bullet_lines(all_text)
    with open(txt_path, "w", encoding="utf-8") as out:
        for line in processed_lines:
            out.write(line + "\n")
    print(f"Saved TXT to: {txt_path}")
