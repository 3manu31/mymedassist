# MLX Fine-tuning Setup

This folder contains all files needed to fine-tune SmallThinker-3B-Preview-mlx using LoRA on Apple Silicon (MLX).

## Contents
- `medical_dataset_kaggle.jsonl` — Training data (instruction, input, output)
- `finetune_mlx_lora.py` — Minimal MLX LoRA fine-tuning script
- `mlx_model/` — (symlink or copy) to your MLX model weights

## Usage
1. Ensure you have MLX installed: https://github.com/ml-explore/mlx#installation
2. Place or symlink your model at `mlx_model/` or update the script path.
3. Run the training script:
   ```bash
   python finetune_mlx_lora.py
   ```
4. Monitor training output and check for `lora_adapter.safetensors` or similar output.

## Notes
- You can adjust batch size, epochs, and learning rate in the script.
- The script expects your data in the same format as used for Kaggle (JSONL, one dict per line).
- For more advanced options, see the official MLX LoRA examples: https://github.com/ml-explore/mlx-examples/tree/main/lora
python finetune_mlx_lora.py
