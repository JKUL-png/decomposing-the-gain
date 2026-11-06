#!/bin/bash
# Cola nocturna: confirmar el hallazgo de la ficha de Qwen (thinking, temp 1.0; resto = BASE_MIT) con semillas 1-3,
# MATH-500 100 fijos, en editado (p50c, primero: es el hallazgo clave) y original. UNO a la vez; si uno falla,
# guarda el error y sigue (sin reintentar). Sin commit automático (el análisis y el commit se hacen a mano).
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_ficha_sem.lock
for L in cola_ficha_sem cola_ficha cola_r3 cola_r2 cola_dia cola_noche; do
  if [ -e "$HOME/$L.lock" ]; then echo "Hay un candado ($L.lock). No lanzo."; exit 1; fi
done
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
M0=$HOME/modelos/Qwen3.5-0.8B
ME=$HOME/modelos/Qwen3.5-0.8B-p50c
echo "=== Cola ficha semillas 1-3 iniciada $(date) ==="
# modelo | prefijo de salida (el mismo de la semilla 0, para que se junten)
ITEMS=(
  "$ME|r2_ed_ficha_qwen"
  "$M0|cero_edicion_ficha_qwen"
)
for ITEM in "${ITEMS[@]}"; do
  IFS='|' read -r MOD PREF <<< "$ITEM"
  echo "=== [$PREF] modelo=$(basename $MOD) semillas=1,2,3 inicio $(date) ==="
  python $P/scripts/correr_vllm_multi.py "$MOD" ficha_qwen math500_subset100_ids.txt math500_subset100.jsonl "$R/$PREF" 1,2,3 math > "$HOME/ficha_sem_$PREF.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    { echo "ítem: $PREF ($(basename $MOD), ficha_qwen, semillas 1,2,3)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/ficha_sem_$PREF.log"; } > "$R/errores_ficha_sem_$PREF.txt"
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
done
echo "=== Cola ficha semillas terminada $(date) ==="
