#!/bin/bash
# Lanzador de la cola de la ronda 3. En primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
nohup bash /workspace/decomposing-the-gain/scripts/cola_ronda3.sh > "$HOME/cola_r3.log" 2>&1
