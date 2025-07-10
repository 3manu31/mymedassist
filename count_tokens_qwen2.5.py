import json
import csv
from transformers import AutoTokenizer
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description="Count tokens for each prompt+response pair in a JSONL file using Qwen2.5 tokenizer.")
parser.add_argument('--input', type=str, default='data/finetune_dataset.jsonl', help='Path to input JSONL file')
parser.add_argument('--output', type=str, default='data/token_counts.csv', help='Path to output CSV file')
parser.add_argument('--prompt_key', type=str, default='prompt', help='Key for prompt in JSONL')
parser.add_argument('--response_key', type=str, default='response', help='Key for response in JSONL')
args = parser.parse_args()

# Load Qwen2.5 tokenizer
print("Loading Qwen2.5 tokenizer...")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B")

results = []

with open(args.input, 'r', encoding='utf-8') as infile:
    for idx, line in enumerate(infile):
        data = json.loads(line)
        prompt = data.get(args.prompt_key, "")
        response = data.get(args.response_key, "")
        full_text = prompt + response
        tokenized = tokenizer(full_text, return_tensors=None)
        token_count = len(tokenized['input_ids'])
        results.append({
            'index': idx,
            'prompt_tokens': len(tokenizer(prompt)['input_ids']),
            'response_tokens': len(tokenizer(response)['input_ids']),
            'total_tokens': token_count
        })
        print(f"Sample {idx}: total_tokens={token_count}")

# Save to CSV
with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['index', 'prompt_tokens', 'response_tokens', 'total_tokens']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in results:
        writer.writerow(row)

print(f"Token counts saved to {args.output}")
