#!/bin/bash
# Lanzador: en primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
nohup bash /workspace/decomposing-the-gain/scripts/cola_ficha_semillas.sh > "$HOME/cola_ficha_sem.log" 2>&1
