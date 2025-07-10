import os
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

def build_pairs(lecture_dir, summary_dir, _):
    # Manual override for known pairs (full paths)
    manual_pairs = {
        'stds': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/STDs.md',
        'cns infections': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/CNS_infections.md',
        'tropical diseases': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/Tropical_Diseases.md',
        'hiv': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/HIV.md',
        'tb': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/TB.md',
        'non tuberculous mycobacteria': [
            '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/ema_summary/Non-Tuberculous Mycobacteria (NTM).md',
            '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/atlas_summary/Non-Tuberculous_Mycobacteria_atlas.txt'
        ],
        'meningitis': '/Users/emmanu3l/Documents/my apps/mymedassist1/ATLAS:EMA - data/atlas_summary/meningitis_atlas.txt',
    }
    lectures = {normalize(f): os.path.join(lecture_dir, f)
                for f in os.listdir(lecture_dir)
                if os.path.isfile(os.path.join(lecture_dir, f)) and not f.startswith('.') and f != '.DS_Store'}
    summaries = {normalize(f): os.path.join(summary_dir, f)
                 for f in os.listdir(summary_dir)
                 if os.path.isfile(os.path.join(summary_dir, f)) and not f.startswith('.') and f != '.DS_Store'}
    # Add all summaries from all summary dirs for manual pairs
    # (since some are in atlas_summary, some in ema_summary)
    # We'll flatten the manual_pairs dict for summary_dir
    pairs = []
    unmatched_lectures = set(lectures.keys())
    unmatched_summaries = set(summaries.keys())
    for key, summary_paths in manual_pairs.items():
        if key in lectures:
            if isinstance(summary_paths, list):
                for summary_path in summary_paths:
                    if os.path.exists(summary_path):
                        pairs.append((lectures[key], summary_path, key))
            else:
                if os.path.exists(summary_paths):
                    pairs.append((lectures[key], summary_paths, key))
            unmatched_lectures.discard(key)
    # Add automatic pairs
    for key in lectures:
        if key in summaries and (lectures[key], summaries[key], key) not in pairs:
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
    base = os.path.dirname(os.path.abspath(__file__))
    # CAMI
    cami_lecture_dir = os.path.join(base, 'CAMI - data', 'lecture_transcript_markdown')
    cami_summary_dir = os.path.join(base, 'CAMI - data', 'cami_markdown')
    cami_pairs = build_pairs(cami_lecture_dir, cami_summary_dir, '.md')
    cami_prompt = (
        "Summarize the following lecture transcript as a CAMI study guide, optimized for exam preparation. Output only the cami_study_summary in markdown."
    )
    make_jsonl(cami_pairs, cami_prompt, os.path.join(base, 'finetune_dataset_cami.jsonl'))

    # ATLAS
    atlas_lecture_dir = os.path.join(base, 'ATLAS:EMA - data', 'lecture_transcript')
    atlas_summary_dir = os.path.join(base, 'ATLAS:EMA - data', 'atlas_summary')
    atlas_pairs = build_pairs(atlas_lecture_dir, atlas_summary_dir, '.txt')
    atlas_prompt = (
        "Summarize the following lecture transcript as an Atlas study guide, optimized for exam preparation. Output only the atlas_study_summary in markdown."
    )
    make_jsonl(atlas_pairs, atlas_prompt, os.path.join(base, 'finetune_dataset_atlas.jsonl'))

    # EMA
    ema_lecture_dir = os.path.join(base, 'ATLAS:EMA - data', 'lecture_transcript')
    ema_summary_dir = os.path.join(base, 'ATLAS:EMA - data', 'ema_summary')
    ema_pairs = build_pairs(ema_lecture_dir, ema_summary_dir, '.md')
    ema_prompt = (
        "Summarize the following lecture transcript as an EMA study guide, optimized for exam preparation. Output only the ema_study_summary in markdown."
    )
    make_jsonl(ema_pairs, ema_prompt, os.path.join(base, 'finetune_dataset_ema.jsonl'))

if __name__ == '__main__':
    main()
