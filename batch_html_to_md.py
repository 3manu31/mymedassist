import os
import sys
import traceback
from clean_notion_html import clean_notion_html

# Batch convert all HTML files in input_dir to markdown in output_dir

def batch_convert_html_to_md(input_dir, output_dir):
    for fname in os.listdir(input_dir):
        if not fname.lower().endswith('.html'):
            continue
        in_path = os.path.join(input_dir, fname)
        out_name = os.path.splitext(fname)[0] + '.md'
        out_path = os.path.join(output_dir, out_name)
        try:
            clean_notion_html(in_path, out_path)
        except Exception as e:
            print(f"Error processing {in_path}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    # Folders to process
    folders = [
        ("pathophysiology - data/cami_html", "pathophysiology - data/cami_markdown"),
        ("pathophysiology - data/lecture_transcript_html", "pathophysiology - data/lecture_transcript_markdown")
    ]
    for in_dir, out_dir in folders:
        print(f"Converting all HTML in {in_dir} to markdown in {out_dir}")
        batch_convert_html_to_md(in_dir, out_dir)
    print("Batch conversion complete.")
