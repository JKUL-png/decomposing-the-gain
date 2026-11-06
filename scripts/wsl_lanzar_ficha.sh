#!/bin/bash
# Lanzador: en primer plano dentro de un wsl.exe oculto (así WSL no se apaga).
# Sin argumentos = modelo original. Con argumentos se pasan a cola_ficha.sh (modelo, prefijo).
nohup bash /workspace/decomposing-the-gain/scripts/cola_ficha.sh "$@" > "$HOME/cola_ficha${2:+_$2}.log" 2>&1
