import json
from pathlib import Path

# Choose tokenizer: Hugging Face (transformers) or tiktoken
# We'll use transformers for general compatibility
try:
    from transformers import AutoTokenizer
except ImportError:
    raise ImportError("Please install transformers: pip install transformers")

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

data_path = Path("data/study_summaries_cami.jsonl")

with data_path.open("r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        entry = json.loads(line)
        prompt = entry.get("prompt", "")
        response = entry.get("response", "")
        prompt_tokens = len(tokenizer.tokenize(prompt))
        response_tokens = len(tokenizer.tokenize(response))
        total_tokens = prompt_tokens + response_tokens
        print(f"Entry {i}: Prompt tokens = {prompt_tokens}, Response tokens = {response_tokens}, Total = {total_tokens}")
