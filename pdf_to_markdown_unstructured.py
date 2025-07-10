import sys
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, NarrativeText, ListItem, Table

# Usage: python pdf_to_markdown_unstructured.py input.pdf output.md

def elements_to_markdown(elements):
    md_lines = []
    for el in elements:
        if isinstance(el, Title):
            level = min(getattr(el.metadata, 'category_depth', 1) or 1, 6)
            md_lines.append(f"{'#' * level} {el.text.strip()}")
        elif isinstance(el, ListItem):
            md_lines.append(f"- {el.text.strip()}")
        elif isinstance(el, Table):
            md_lines.append(el.text.strip())  # Tables as plain text for now
        elif isinstance(el, NarrativeText):
            md_lines.append(el.text.strip())
        else:
            if el.text.strip():
                md_lines.append(el.text.strip())
    return '\n\n'.join(md_lines)

def convert_pdf_to_markdown_unstructured(pdf_path, md_path):
    elements = partition_pdf(filename=pdf_path)
    markdown = elements_to_markdown(elements)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Converted {pdf_path} to {md_path} using unstructured.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_to_markdown_unstructured.py input.pdf output.md")
        sys.exit(1)
    pdf_path = sys.argv[1]
    md_path = sys.argv[2]
    convert_pdf_to_markdown_unstructured(pdf_path, md_path)
