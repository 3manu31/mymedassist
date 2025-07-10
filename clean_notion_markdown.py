import sys
import re

# Usage: python clean_notion_markdown.py input.md output.md

def clean_notion_markdown(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    cleaned_lines = []
    i = 0
    # Common keywords to split for top-level bullets
    split_keywords = [
        'Definition', 'Describe', 'Explain', 'List', 'Discuss', 'What is', 'How does', 'Why does', 'When does', 'Where does', 'Name', 'State', 'Give', 'Classify', 'Enumerate', 'Write short note on', 'Write about'
    ]
    split_keywords_regex = r'^(%s)\\b[\s:](.+)' % '|'.join([re.escape(k) for k in split_keywords])

    while i < len(lines):
        line = lines[i]
        # Remove image artifacts
        if re.match(r'!\[\]\(.*\)', line.strip()):
            i += 1
            continue
        # Bullet handling
        bullet_match = re.match(r'^(\s*)([●○◆])\s*(.*)', line)
        if bullet_match:
            indent, bullet, text = bullet_match.groups()
            # Gather following lines until next bullet, heading, or end of file
            j = i + 1
            extra = []
            while j < len(lines):
                next_line = lines[j]
                if re.match(r'^(\s*)[●○◆]', next_line):
                    break
                if re.match(r'^\s*#', next_line):  # heading
                    break
                if next_line.strip() == '' and (j + 1 < len(lines) and (re.match(r'^(\s*)[●○◆]', lines[j+1]) or re.match(r'^\s*#', lines[j+1]))):
                    break
                extra.append(next_line.rstrip())
                j += 1
            # Join all lines, removing internal newlines and extra spaces
            full_text = ' '.join([text.strip()] + [l for l in extra if l.strip() != ''])
            if bullet == '●':
                # Special: split at keyword if present
                m = re.match(split_keywords_regex, full_text, re.IGNORECASE)
                if m:
                    keyword, rest = m.groups()
                    cleaned_lines.append(f'- **{keyword.strip()}**\n')
                    cleaned_lines.append(f'{rest.strip()}\n')
                elif ':' in full_text:
                    before_colon, after_colon = full_text.split(':', 1)
                    cleaned_lines.append(f'- **{before_colon.strip()}:**{after_colon}\n')
                else:
                    cleaned_lines.append(f'- **{full_text}**\n')
            elif bullet == '○':
                cleaned_lines.append(f'  - {full_text}\n')
            elif bullet == '◆':
                cleaned_lines.append(f'    - {full_text}\n')
            i = j
            continue
        # Otherwise, keep line as is
        cleaned_lines.append(line)
        i += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    print(f"Cleaned markdown written to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_notion_markdown.py input.md output.md")
        sys.exit(1)
    clean_notion_markdown(sys.argv[1], sys.argv[2])
