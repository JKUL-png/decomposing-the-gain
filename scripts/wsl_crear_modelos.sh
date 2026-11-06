#!/bin/bash
source "$HOME/venv-vllm/bin/activate"; python /workspace/decomposing-the-gain/scripts/crear_modelos_editados.py 2>&1 | tail -n 14 | cut -c1-220; ls -la $HOME/modelos/ | cut -c1-90
