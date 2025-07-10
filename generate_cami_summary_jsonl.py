import os
import json

LECTURE_MD_DIR = os.path.join("pathophysiology - data", "lecture_transcript_markdown")
CAMI_MD_DIR = os.path.join("pathophysiology - data", "cami_markdown")
OUTPUT_JSONL = os.path.join("data", "study_summaries_cami.jsonl")

PROMPT_TEMPLATE = (
    "You are a medical study assistant. Given the following lecture transcript, generate a concise, exam-focused cami summary in markdown format.\n\nLecture Transcript:\n\n{lecture}\n\nCami Summary:"
)

def get_matching_cami_file(lecture_filename):
    # Assumes matching by base name (ignoring extension)
    base = os.path.splitext(lecture_filename)[0]
    for ext in [".md", ".markdown"]:
        cami_path = os.path.join(CAMI_MD_DIR, base + ext)
        if os.path.exists(cami_path):
            return cami_path
    return None

def main():
    entries = []
    for fname in os.listdir(LECTURE_MD_DIR):
        if not fname.endswith(".md"):
            continue
        lecture_path = os.path.join(LECTURE_MD_DIR, fname)
        cami_path = get_matching_cami_file(fname)
        if not cami_path:
            print(f"No matching cami summary for {fname}")
            continue
        with open(lecture_path, "r") as f:
            lecture_md = f.read().strip()
        with open(cami_path, "r") as f:
            cami_md = f.read().strip()
        prompt = PROMPT_TEMPLATE.format(lecture=lecture_md)
        entry = {
            "prompt": prompt,
            "response": cami_md,
            "summary_type": "cami",
            "source": fname
        }
        entries.append(entry)
    with open(OUTPUT_JSONL, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Wrote {len(entries)} entries to {OUTPUT_JSONL}")

if __name__ == "__main__":
    main()
