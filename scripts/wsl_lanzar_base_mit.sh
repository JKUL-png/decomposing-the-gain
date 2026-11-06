#!/bin/bash
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0   # sin nvcc en WSL
cd "$HOME"
python /workspace/decomposing-the-gain/scripts/correr_vllm.py "$HOME/modelos/Qwen3.5-0.8B" base_mit \
  math500_subset100_ids.txt /workspace/decomposing-the-gain/resultados/linea_base_vllm.csv > "$HOME/linea_base_vllm.log" 2>&1
echo "EXIT=$?" >> "$HOME/linea_base_vllm.log"
