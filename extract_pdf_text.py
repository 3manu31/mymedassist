import sys
from PyPDF2 import PdfReader

# Usage: python extract_pdf_text.py input.pdf output.txt

def extract_text(pdf_path, txt_path):
    reader = PdfReader(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as out:
        for page in reader.pages:
            text = page.extract_text()
            if text:
                out.write(text + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python extract_pdf_text.py input.pdf output.txt")
        sys.exit(1)
    extract_text(sys.argv[1], sys.argv[2])
    print(f"Extracted text from {sys.argv[1]} to {sys.argv[2]}")
