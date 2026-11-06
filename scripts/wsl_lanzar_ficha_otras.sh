#!/bin/bash
# Lanzador: en primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
# Argumento opcional: semillas (ej. 1,2,3); sin argumento = semilla 0.
SEM=${1:-0}
nohup bash /workspace/decomposing-the-gain/scripts/cola_ficha_otras.sh "$SEM" > "$HOME/cola_ficha_otras_s$(echo $SEM | tr ',' '_').log" 2>&1
