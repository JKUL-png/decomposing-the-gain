#!/bin/bash
# Cola: config de la ficha de Qwen (thinking, temp 1.0; resto = BASE_MIT) en GSM8K (subconjunto 1) e IFEval,
# original y editado (p50c). Primero el editado. UNO a la vez; si uno falla, guarda el error y sigue
# (sin reintentar). Sin commit automático.
# Argumento opcional $1 = semillas (default "0"; ej. "1,2,3"). correr_vllm_multi.py salta las semillas que ya existen.
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
P=/workspace/decomposing-the-gain
R=$P/resultados
SEM=${1:-0}
TAG=$(echo "$SEM" | tr ',' '_')
LOCK=$HOME/cola_ficha_otras.lock
for L in cola_ficha_otras cola_ficha_sem cola_ficha cola_r3 cola_r2 cola_dia cola_noche; do
  if [ -e "$HOME/$L.lock" ]; then echo "Hay un candado ($L.lock). No lanzo."; exit 1; fi
done
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
M0=$HOME/modelos/Qwen3.5-0.8B
ME=$HOME/modelos/Qwen3.5-0.8B-p50c
echo "=== Cola ficha GSM8K/IFEval (semillas $SEM) iniciada $(date) ==="
# modelo | ids | jsonl | prefijo | tarea
ITEMS=(
  "$ME|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_ed_ficha|gsm8k"
  "$ME|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_ed_ficha|ifeval"
  "$M0|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_orig_ficha|gsm8k"
  "$M0|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_orig_ficha|ifeval"
)
for ITEM in "${ITEMS[@]}"; do
  IFS='|' read -r MOD IDS JSONL PREF TAREA <<< "$ITEM"
  LOG="$HOME/ficha_otras_${PREF}_s${TAG}.log"
  echo "=== [$PREF] modelo=$(basename $MOD) tarea=$TAREA semillas $SEM inicio $(date) ==="
  python $P/scripts/correr_vllm_multi.py "$MOD" ficha_qwen $IDS $JSONL "$R/$PREF" $SEM $TAREA > "$LOG" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    { echo "ítem: $PREF ($(basename $MOD), ficha_qwen, semillas $SEM, $TAREA)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$LOG"; } > "$R/errores_ficha_otras_${PREF}_s${TAG}.txt"
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
done
echo "=== Cola ficha GSM8K/IFEval (semillas $SEM) terminada $(date) ==="
