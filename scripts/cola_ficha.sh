#!/bin/bash
# Un solo ítem: config de thinking de la ficha de Qwen (temp 1.0; resto = BASE_MIT), modelo original,
# MATH-500 (100 fijos), semilla 0. Sin reintentos; si falla guarda el error. Sin commit automático.
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_ficha.lock
for L in cola_ficha cola_r3 cola_r2 cola_dia cola_noche; do
  if [ -e "$HOME/$L.lock" ]; then echo "Hay un candado ($L.lock). No lanzo."; exit 1; fi
done
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
# Argumentos opcionales: $1 = carpeta del modelo (default original), $2 = prefijo de salida
MODELO=${1:-$HOME/modelos/Qwen3.5-0.8B}
PREF=${2:-cero_edicion_ficha_qwen}
echo "=== [$PREF] inicio $(date) modelo=$MODELO ==="
python $P/scripts/correr_vllm_multi.py "$MODELO" ficha_qwen math500_subset100_ids.txt math500_subset100.jsonl "$R/$PREF" 0 math > "$HOME/ficha_$PREF.log" 2>&1
CODE=$?
if [ $CODE -ne 0 ]; then
  { echo "ítem: $PREF"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/ficha_$PREF.log"; } > "$R/errores_ficha_$PREF.txt"
  echo "[$PREF] terminó con errores (código $CODE) $(date)"
else
  echo "[$PREF] OK $(date)"
fi
