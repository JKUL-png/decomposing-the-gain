#!/bin/bash
# Instala vLLM en un entorno de Python dentro de WSL2 (sin sudo). Log: ~/instalar_vllm.log
export PATH="$HOME/.local/bin:$PATH"
cd "$HOME" || exit 1
uv venv --python 3.12 venv-vllm || exit 1
source venv-vllm/bin/activate
uv pip install vllm --torch-backend=auto > "$HOME/instalar_vllm.log" 2>&1
echo "EXIT=$?" >> "$HOME/instalar_vllm.log"
