import os
from pathlib import Path
from PyPDF2 import PdfReader

# Folder containing the PDF files
target_folder = '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/lecture transcript - infectious diseases'

def pdf_to_txt(pdf_path, txt_path):
    try:
        reader = PdfReader(pdf_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Converted: {pdf_path} -> {txt_path}")
    except Exception as e:
        print(f"Failed to convert {pdf_path}: {e}")

def convert_all_pdfs(folder):
    for file in os.listdir(folder):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(folder, file)
            txt_path = os.path.splitext(pdf_path)[0] + '.txt'
            pdf_to_txt(pdf_path, txt_path)

if __name__ == "__main__":
    convert_all_pdfs(target_folder)
