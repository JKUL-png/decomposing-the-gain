#!/bin/bash
# Instala solo paquetes pequeños para GSM8K/IFEval (no toca vllm/torch).
source "$HOME/venv-vllm/bin/activate"
UV=$(command -v uv || ls $HOME/.local/bin/uv $HOME/.cargo/bin/uv 2>/dev/null | head -1)
echo "uv: $UV"
$UV pip install datasets langdetect nltk immutabledict absl-py 2>&1 | tail -n 4 | cut -c1-160
python -c "import nltk; print(nltk.download('punkt_tab', quiet=True), nltk.download('punkt', quiet=True))"
python -c "import torch, vllm; print('torch', torch.__version__, 'vllm', vllm.__version__)" 2>&1 | tail -n 1
