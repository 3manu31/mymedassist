import sys
import os
import fitz  # PyMuPDF
from markdownify import markdownify as md
import re

def pdf_to_html(pdf_path):
    doc = fitz.open(pdf_path)
    html = ""
    for page in doc:
        html += page.get_text("html")
    return html

def heuristic_postprocess(markdown):
    # Remove 3 or more dashes at the start of a line, even if followed by text (keep the text)
    markdown = re.sub(r'^-{3,}', '', markdown, flags=re.MULTILINE)
    # Remove lines that are just a sequence of dashes or similar symbols (even at the start)
    markdown = re.sub(r'^(\s*[-=~_]{3,}\s*)$', '', markdown, flags=re.MULTILINE)
    # Replace Unicode bullets with markdown dashes (but keep the text)
    markdown = re.sub(r'^[\u25cf\u25cb]\s*', '- ', markdown, flags=re.MULTILINE)
    # Add a space after periods if not already present
    markdown = re.sub(r'([a-zA-Z0-9])\.([A-Z])', r'\1. \2', markdown)
    # Add newlines after sentence-ending punctuation followed by a capital letter
    markdown = re.sub(r'([.!?]) ([A-Z])', r'\1\n\n\2', markdown)
    # Add newlines between a lowercase letter and a capitalized word (for smashed-together headings/sections)
    markdown = re.sub(r'([a-z])([A-Z][a-z]+)', r'\1\n\2', markdown)
    # Add newlines between two capitalized words (for headings)
    markdown = re.sub(r'([A-Z][a-z]+)([A-Z][a-z]+)', r'\1\n\2', markdown)
    # Add newlines before section headers (lines in ALL CAPS or Title Case)
    markdown = re.sub(r'(\n|^)([A-Z][A-Z\s]{2,}|[A-Z][a-z]+( [A-Z][a-z]+){0,3}:)', r'\1\n\2', markdown)
    # Remove excessive blank lines
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    # Group lines after bullets or Describe/Define/Explain prompts
    markdown = group_bullet_and_describe_sections(markdown)
    return markdown

def group_bullet_and_describe_sections(markdown):
    lines = markdown.split('\n')
    output = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        # Detect bullet or 'Describe ...' line
        if line.startswith('- ') or re.match(r'^(Describe|Define|Explain|List|Discuss|What is|How does|Why does|When does|Where does|Name|State|Give|Classify|Enumerate|Write short note on|Write about) .+', line):
            # Start a new list item or section
            item = [line]
            i += 1
            # Collect following lines that are not a new bullet, heading, or blank
            while i < len(lines):
                next_line = lines[i].rstrip()
                if next_line.startswith('- ') or re.match(r'^(Describe|Define|Explain|List|Discuss|What is|How does|Why does|When does|Where does|Name|State|Give|Classify|Enumerate|Write short note on|Write about) .+', next_line):
                    break
                if re.match(r'^#+ ', next_line):  # markdown heading
                    break
                if next_line.strip() == '':
                    break
                # Indent for markdown list if bullet, else just append
                if line.startswith('- '):
                    item.append('  ' + next_line)
                else:
                    item.append(next_line)
                i += 1
            output.append('\n'.join(item))
        else:
            output.append(line)
            i += 1
    return '\n'.join(output)

def html_to_markdown(html):
    # Custom rules for markdownify to better handle bold and italics only
    def strong_tag_handler(attrs, content):
        return f'**{content}**'
    def b_tag_handler(attrs, content):
        return f'**{content}**'
    def em_tag_handler(attrs, content):
        return f'*{content}*'
    custom_rules = {
        'strong': strong_tag_handler,
        'b': b_tag_handler,
        'em': em_tag_handler
    }
    markdown = md(html, heading_style="ATX", convert=['b', 'strong', 'em'], custom_rules=custom_rules)
    # Clean up common PDF artifacts
    # Replace Unicode bullets with markdown bullets
    markdown = re.sub(r"[\u25cf\u25cb]", "-", markdown)
    # Remove markdown image references (including base64 images)
    markdown = re.sub(r'!\[.*?\]\(data:image\/[^)]*\)', '', markdown)
    markdown = re.sub(r'!\[.*?\]\(.*?\)', '', markdown)
    # Remove HTML <img ...> tags
    markdown = re.sub(r'<img[^>]*>', '', markdown)
    # Remove lines that are just figure placeholders (e.g., *Fig 1*)
    markdown = re.sub(r'^\*Fig.*$', '', markdown, flags=re.MULTILINE)
    # Remove lines that are only symbols or whitespace (e.g., -, ◆, ▪, etc.)
    markdown = re.sub(r'^\s*([\-\u25cf\u25cb\u25c6\u25a0\u25b2\u25b6\u25c7\u25a1\u25b3\u25b7\u2605\u2606\u2736\u2737\u2738\u2739\u273a\u273b\u273c\u273d\u273e\u273f\u2740\u2741\u2742\u2743\u2744\u2745\u2746\u2747\u2748\u2749\u2756\u2764\u2794\u2b50\u2b1b\u2b1c\u2b1d\u2b1e\u2b1f\u2b20\u2b21\u2b22\u2b23\u2b24\u2b25\u2b26\u2b27\u2b28\u2b29\u2b2a\u2b2b\u2b2c\u2b2d\u2b2e\u2b2f\u2b30\u2b31\u2b32\u2b33\u2b34\u2b35\u2b36\u2b37\u2b38\u2b39\u2b3a\u2b3b\u2b3c\u2b3d\u2b3e\u2b3f\u2b40\u2b41\u2b42\u2b43\u2b44\u2b45\u2b46\u2b47\u2b48\u2b49\u2b4a\u2b4b\u2b4c\u2b4d\u2b4e\u2b4f\u2b50\u2b51\u2b52\u2b53\u2b54\u2b55\u2b56\u2b57\u2b58\u2b59\u2b5a\u2b5b\u2b5c\u2b5d\u2b5e\u2b5f\u2b60\u2b61\u2b62\u2b63\u2b64\u2b65\u2b66\u2b67\u2b68\u2b69\u2b6a\u2b6b\u2b6c\u2b6d\u2b6e\u2b6f\u2b70\u2b71\u2b72\u2b73\u2b74\u2b75\u2b76\u2b77\u2b78\u2b79\u2b7a\u2b7b\u2b7c\u2b7d\u2b7e\u2b7f\u2b80\u2b81\u2b82\u2b83\u2b84\u2b85\u2b86\u2b87\u2b88\u2b89\u2b8a\u2b8b\u2b8c\u2b8d\u2b8e\u2b8f\u2b90\u2b91\u2b92\u2b93\u2b94\u2b95\u2b96\u2b97\u2b98\u2b99\u2b9a\u2b9b\u2b9c\u2b9d\u2b9e\u2b9f]+)\s*$', '', markdown, flags=re.MULTILINE)
    # Remove lines that are very short and contain no alphanumeric characters
    markdown = re.sub(r'^\s*[^a-zA-Z0-9\n]{1,3}\s*$\n?', '', markdown, flags=re.MULTILINE)
    # Remove lines that are just a number and a period (e.g., 1., 2., 3.)
    markdown = re.sub(r'^\s*\d+\.\s*$\n?', '', markdown, flags=re.MULTILINE)
    # Remove excessive blank lines (2 or more newlines to 1)
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    markdown = re.sub(r'(^\s*\n){2,}', '\n', markdown, flags=re.MULTILINE)
    # Heuristic post-processing for paragraphs and sections
    markdown = heuristic_postprocess(markdown)
    return markdown

def convert_pdf_to_markdown(pdf_path, md_path):
    html = pdf_to_html(pdf_path)
    markdown = html_to_markdown(html)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown)
    print(f"Converted {pdf_path} to {md_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf_to_markdown.py input.pdf output.md")
        sys.exit(1)
    pdf_path = sys.argv[1]
    md_path = sys.argv[2]
    convert_pdf_to_markdown(pdf_path, md_path)
