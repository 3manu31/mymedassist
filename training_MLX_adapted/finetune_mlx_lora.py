import json
import os
import mlx.core as mx
import mlx.nn as nn
from mlx_lora.models import LoRALinear
from mlx_lora import utils
from tqdm import tqdm

# Path to MLX model
MODEL_PATH = "/Users/emmanu3l/SmallThinker-3B-Preview-mlx"
# Path to dataset
DATA_PATH = "medical_dataset_kaggle.jsonl"
# Training params
EPOCHS = 3
BATCH_SIZE = 2
LEARNING_RATE = 2e-4

# Load model and tokenizer using utils.load (supports Qwen2.5-3b-Instruct MLX format)
model, tokenizer, config = utils.load(MODEL_PATH)

# --- Apply LoRA to all Linear layers ---
def replace_linear_with_lora(module):
    for name, child in module.named_children():
        if isinstance(child, nn.Linear):
            setattr(module, name, LoRALinear.from_linear(child))
        else:
            replace_linear_with_lora(child)
replace_linear_with_lora(model)

# Load dataset
with open(DATA_PATH, "r", encoding="utf-8") as f:
    dataset = [json.loads(line) for line in f]

# Simple prompt/response formatting
examples = []
for entry in dataset:
    prompt = entry["instruction"]
    if entry.get("input"):
        prompt += "\n" + entry["input"]
    response = entry["output"]
    examples.append((prompt, response))

def batch_iter(data, batch_size):
    for i in range(0, len(data), batch_size):
        yield data[i:i+batch_size]

# Training loop
optimizer = mx.optim.Adam(model.parameters(), lr=LEARNING_RATE)
model.train()

for epoch in range(EPOCHS):
    print(f"Epoch {epoch+1}/{EPOCHS}")
    total_loss = 0
    for batch in tqdm(batch_iter(examples, BATCH_SIZE), total=len(examples)//BATCH_SIZE):
        prompts, responses = zip(*batch)
        # Tokenize and concatenate prompt+response for supervised fine-tuning
        inputs = [tokenizer(p + "\n" + r, return_tensors="np") for p, r in zip(prompts, responses)]
        input_ids = [i["input_ids"] for i in inputs]
        # Pad to max length in batch
        max_len = max(len(ids[0]) for ids in input_ids)
        batch_ids = mx.array([list(ids[0]) + [tokenizer.pad_token_id]*(max_len-len(ids[0])) for ids in input_ids])
        # Forward and loss
        logits, _ = model(batch_ids)
        # Shift for next-token prediction
        shift_logits = logits[:, :-1, :]
        shift_labels = batch_ids[:, 1:]
        loss = nn.functional.cross_entropy(shift_logits.reshape(-1, shift_logits.shape[-1]), shift_labels.reshape(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Average loss: {total_loss/len(examples):.4f}")

# Save LoRA adapter weights
if hasattr(model, 'save_lora'):
    model.save_lora("lora_adapter.safetensors")
    print("LoRA adapter saved as lora_adapter.safetensors")
else:
    print("Warning: model does not have save_lora method. Please refer to MLX LoRA example for saving weights.")
