#!/bin/bash
# Cola de la ronda 2: ítems en orden de prioridad, UNO a la vez. Si uno falla, guarda el error y sigue (sin reintentar).
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0   # sin nvcc en WSL
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_r2.lock
if [ -e "$LOCK" ] || [ -e "$HOME/cola_dia.lock" ] || [ -e "$HOME/cola_noche.lock" ]; then echo "Hay un candado (cola corriendo o interrumpida). No lanzo."; exit 1; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
M0=$HOME/modelos/Qwen3.5-0.8B            # original
ME=$HOME/modelos/Qwen3.5-0.8B-p50c       # edición del MIT (p50c)
MP=$HOME/modelos/Qwen3.5-0.8B-placebo50  # placebo (edición aleatoria, misma norma)
S100="math500_subset100_ids.txt|math500_subset100.jsonl"
echo "=== Cola ronda 2 iniciada $(date) ==="
# modelo | config | ids | jsonl | prefijo de salida | semillas | tarea
ITEMS=(
  "$M0|no_thinking|math500_full_ids.txt|math500_full.jsonl|r2_orig_nothink32k_500|0|math"
  "$ME|base_mit|$S100|r2_ed_think|0,1,2,3|math"
  "$ME|nothink_mit|$S100|r2_ed_nothinkmit|0,1,2,3|math"
  "$ME|no_thinking|$S100|r2_ed_nothink32k|0,1,2,3|math"
  "$M0|nothink_mit|$S100|r2_orig_nothinkmit|1,2,3|math"
  "$MP|base_mit|$S100|r2_pla_think|0,1|math"
  "$M0|nothink_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_orig_nothink|0|gsm8k"
  "$M0|nothink_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_orig_nothink|0|ifeval"
  "$ME|nothink_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_ed_nothink|0|gsm8k"
  "$ME|nothink_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_ed_nothink|0|ifeval"
  "$ME|base_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_ed_think|0|gsm8k"
  "$ME|base_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_ed_think|0|ifeval"
  "$M0|base_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_orig_think|0|gsm8k"
  "$M0|base_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_orig_think|0|ifeval"
)
for ITEM in "${ITEMS[@]}"; do
  IFS='|' read -r MOD CFG IDS JSONL PREF SEEDS TAREA <<< "$ITEM"
  echo "=== [$PREF] modelo=$(basename $MOD) config=$CFG semillas=$SEEDS tarea=$TAREA inicio $(date) ==="
  python $P/scripts/correr_vllm_multi.py "$MOD" $CFG $IDS $JSONL "$R/$PREF" $SEEDS $TAREA > "$HOME/r2_$PREF.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
    { echo "ítem: $PREF ($(basename $MOD), $CFG, semillas $SEEDS, tarea $TAREA)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/r2_$PREF.log"; } > "$R/errores_r2_$PREF.txt"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
done
echo "=== Análisis sin GPU (McNemar, etc.) y commit $(date) ==="
python $P/scripts/analisis_ronda2.py > "$HOME/analisis_r2.log" 2>&1 || echo "El análisis falló; ver ~/analisis_r2.log"
cd $P
echo "=== Cola ronda 2 terminada $(date) ==="
