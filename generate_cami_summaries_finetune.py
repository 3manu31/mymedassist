# ... previous code ...
torch.cuda.empty_cache()
torch.cuda.ipc_collect()

trainer = SFTTrainer(
    model=model,
    train_dataset=tokenized_dataset,
    args=training_args,
)
trainer.train()import os
import json
import re

def normalize(name):
    """Normalize filenames for matching: lowercase, remove extension, replace underscores/dashes/spaces, remove non-alphanum, remove '_atlas', ignore file extension."""
    name = name.lower()
    name = os.path.splitext(name)[0]
    name = name.replace('_atlas', '')
    name = name.replace('_', ' ').replace('-', ' ')
    name = re.sub(r'[^a-z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        print(f'UnicodeDecodeError: Could not read file as UTF-8: {path}')
        return None

def build_pairs(lecture_dir, summary_dir):
    lectures = {normalize(f): os.path.join(lecture_dir, f)
                for f in os.listdir(lecture_dir)
                if os.path.isfile(os.path.join(lecture_dir, f)) and not f.startswith('.') and f != '.DS_Store'}
    summaries = {normalize(f): os.path.join(summary_dir, f)
                 for f in os.listdir(summary_dir)
                 if os.path.isfile(os.path.join(summary_dir, f)) and not f.startswith('.') and f != '.DS_Store'}
    pairs = []
    unmatched_lectures = set(lectures.keys())
    unmatched_summaries = set(summaries.keys())
    for key in lectures:
        if key in summaries:
            pairs.append((lectures[key], summaries[key], key))
            unmatched_lectures.discard(key)
            unmatched_summaries.discard(key)
    if unmatched_lectures or unmatched_summaries:
        print('Unmatched lecture files:', [lectures[k] for k in unmatched_lectures])
        print('Unmatched summary files:', [summaries[k] for k in unmatched_summaries])
    return pairs

def make_jsonl(pairs, prompt_template, output_path):
    with open(output_path, 'w', encoding='utf-8') as out:
        for lecture_path, summary_path, key in pairs:
            lecture = read_file(lecture_path)
            summary = read_file(summary_path)
            if lecture is None or summary is None:
                print(f'Skipping pair due to read error: {lecture_path}, {summary_path}')
                continue
            prompt = prompt_template.replace('{lecture}', lecture)
            entry = {
                'instruction': prompt,
                'input': '',
                'output': summary
            }
            out.write(json.dumps(entry, ensure_ascii=False) + '\n')

def main():
    lecture_dir = '/Users/emmanu3l/Documents/my apps/mymedassist    python3 mlx_convert_quant.py/CAMI - data/lecture_transcript_pathophysiology_txt'
    summary_dir = '/Users/emmanu3l/Documents/my apps/mymedassist1/CAMI - data/cami_summary_pathophysiology_txt'
    output_path = '/Users/emmanu3l/Documents/my apps/mymedassist1/data/cami_summaries_finetune.jsonl'
    prompt = (
        "Summarize the following lecture transcript as a CAMI study guide, optimized for exam preparation. Output only the cami_study_summary in markdown."
    )
    pairs = build_pairs(lecture_dir, summary_dir)
    make_jsonl(pairs, prompt, output_path)

if __name__ == '__main__':
    main()
