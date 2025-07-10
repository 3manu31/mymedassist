import sys
import re
from bs4 import BeautifulSoup

# Usage: python clean_notion_html.py input.html output.md

def clean_notion_html(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    raw_lines = []
    for el in soup.find_all(['p', 'li', 'div']):
        text = el.get_text().rstrip()
        # Remove image tags
        if hasattr(el, 'find') and el.find('img'):
            continue
        # Remove lines that are just divider-like symbols (asterisks, dashes, underscores, etc.)
        if re.match(r'^[\s\-*_=~]{3,}$', text):
            continue
        raw_lines.append(text)

    # Pass 1: For each line, split at every bullet (●, ○, ◆, ◇), so each bullet and its text starts a new line
    processed_lines = []
    bullet_pattern = r'([●○◆◇])'
    for line in raw_lines:
        # Split at every bullet, keep the bullet with its text
        parts = re.split(bullet_pattern, line)
        buffer = ''
        for idx, part in enumerate(parts):
            if part in {'●', '○', '◆', '◇'}:
                if buffer.strip():
                    processed_lines.append(buffer.strip())
                buffer = part
            else:
                if buffer and buffer in {'●', '○', '◆', '◇'}:
                    processed_lines.append((buffer + ' ' + part.strip()).strip())
                    buffer = ''
                else:
                    buffer += part
        if buffer.strip():
            processed_lines.append(buffer.strip())

    # Pass 1b: For each line, split at every numbered item (e.g., 1. 2. 3.), so each number and its text starts a new line
    numbered_lines = []
    number_pattern = r'(\d+\.)'
    for line in processed_lines:
        # Only split if there are multiple numbers in the line
        if len(re.findall(number_pattern + r' ', line)) > 1:
            # Split at every number followed by a space, keep the number with its text
            parts = re.split(number_pattern + r' ', line)
            buffer = ''
            for idx, part in enumerate(parts):
                if idx == 0 and part.strip():
                    buffer = part.strip()
                elif part and re.match(r'^\d+\.$', part):
                    if buffer.strip():
                        numbered_lines.append(buffer.strip())
                    buffer = part
                else:
                    buffer += ' ' + part.strip()
            if buffer.strip():
                numbered_lines.append(buffer.strip())
        else:
            numbered_lines.append(line)

    # Pass 2: For lines that are just a bullet, check the next line: if it’s not a bullet and not empty, join it to the bullet line.
    i = 0
    joined_lines = []
    while i < len(numbered_lines):
        line = numbered_lines[i]
        if re.match(r'^[●○◆◇]\s*$', line):
            # Look ahead to next line
            if i + 1 < len(numbered_lines):
                next_line = numbered_lines[i+1]
                if next_line.strip() and not re.match(r'^[●○◆◇]', next_line.strip()):
                    # Join bullet and next line
                    joined_lines.append(f'{line} {next_line.strip()}')
                    i += 2
                    continue
        joined_lines.append(line)
        i += 1

    # Now continue with your previous formatting logic
    output_lines = []
    split_keywords = [
        'Definition', 'Describe', 'Explain', 'List', 'Discuss', 'What is', 'How does', 'Why does', 'When does', 'Where does', 'Name', 'State', 'Give', 'Classify', 'Enumerate', 'Write short note on', 'Write about'
    ]
    split_keywords_regex = r'^(%s)\\b[\s:](.+)' % '|'.join([re.escape(k) for k in split_keywords])

    for text in joined_lines:
        # ●: bold, no bullet, add blank line before
        if text.startswith('●'):
            content = text[1:].strip()
            m = re.match(split_keywords_regex, content, re.IGNORECASE)
            # Always add a blank line before a bolded line from ●
            if output_lines and output_lines[-1].strip() != '':
                output_lines.append('')
            if m:
                keyword, rest = m.groups()
                output_lines.append(f'**{keyword.strip()}**')
                output_lines.append(rest.strip())
            elif ':' in content:
                before_colon, after_colon = content.split(':', 1)
                output_lines.append(f'**{before_colon.strip()}:**{after_colon.strip()}')
            else:
                output_lines.append(f'**{content}**')
            continue
        # ○: indent (2 spaces)
        if text.startswith('○'):
            content = text[1:].strip()
            output_lines.append(f'  {content}')
            continue
        # ◆: indent (4 spaces)
        if text.startswith('◆'):
            content = text[1:].strip()
            output_lines.append(f'    {content}')
            continue
        # ◇: indent (6 spaces)
        if text.startswith('◇'):
            content = text[1:].strip()
            output_lines.append(f'      {content}')
            continue
        # Otherwise, keep as is
        output_lines.append(text)

    # Post-process: join consecutive non-empty, non-special lines into a single line
    final_lines = []
    buffer = []
    def is_special(line):
        # Only treat as special if line is blank, bold, heading, or a true indented bullet/marker
        return (
            line.strip() == '' or
            line.startswith('**') or
            line.startswith('#') or
            re.match(r'^  ([-*●○◆◇])', line)
        )
    for line in output_lines:
        if is_special(line):
            if buffer:
                final_lines.append(' '.join(buffer))
                buffer = []
            final_lines.append(line)
        else:
            buffer.append(line.strip())
    if buffer:
        final_lines.append(' '.join(buffer))

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in final_lines:
            f.write(line + '\n')
    print(f"Cleaned markdown written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_notion_html.py input.html output.md")
        sys.exit(1)
    clean_notion_html(sys.argv[1], sys.argv[2])
