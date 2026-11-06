#!/bin/bash
# Lanzador de la cola del día. En primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
nohup bash /workspace/decomposing-the-gain/scripts/cola_dia.sh > "$HOME/cola_dia.log" 2>&1
