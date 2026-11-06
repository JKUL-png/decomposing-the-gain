#!/bin/bash
# Lanzador de la cola nocturna. Se deja en primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
nohup bash /workspace/decomposing-the-gain/scripts/cola_noche.sh > "$HOME/cola_noche.log" 2>&1
