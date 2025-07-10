import os
import pdfplumber
import sys
import subprocess

# Path to the folder containing PDFs
folders = [
    '/Users/emmanu3l/Documents/my apps/train data/infectious diseases - data/lecture transcript - infectious diseases',
    '/Users/emmanu3l/Documents/my apps/train data/infectious diseases - data/atlas summary - infectious diseases'
]

def install_pdfplumber():
    try:
        import pdfplumber  # noqa: F401
    except ImportError:
        print('pdfplumber not found. Installing...')
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pdfplumber'])

install_pdfplumber()

for directory in folders:
    print(f'Processing folder: {directory}')
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            txt_path = os.path.splitext(pdf_path)[0] + '.txt'
            print(f'Converting {filename} to {os.path.basename(txt_path)}...')
            with pdfplumber.open(pdf_path) as pdf:
                all_text = ''
                for page in pdf.pages:
                    all_text += page.extract_text() or ''
                    all_text += '\n'
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(all_text)
print('Conversion complete.')
