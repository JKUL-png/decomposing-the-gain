#!/bin/bash
# Cola del día: 5 ítems en orden de prioridad, UNO a la vez. Si uno falla, guarda el error y sigue (sin reintentar).
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0   # sin nvcc en WSL
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_dia.lock
if [ -e "$LOCK" ] || [ -e "$HOME/cola_noche.lock" ]; then echo "Hay un candado (cola corriendo o interrumpida). No lanzo."; exit 1; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
echo "=== Cola del día iniciada $(date) ==="
# config | ids | jsonl | prefijo de salida | semillas
ITEMS=(
  "nothink_mit|math500_subset100_ids.txt|math500_subset100.jsonl|dia_nothink_mit100|0"
  "nothink_mit|math500_full_ids.txt|math500_full.jsonl|dia_nothink_mit500|0"
  "no_thinking|math500_subset100_ids.txt|math500_subset100.jsonl|cero_edicion_no_thinking|1,2,3"
  "rep110|math500_subset100_ids.txt|math500_subset100.jsonl|cero_edicion_rep110|1,2,3"
  "base_mit|math500_subset100_ids.txt|math500_subset100.jsonl|linea_base_vllm|1,2,3"
)
for ITEM in "${ITEMS[@]}"; do
  IFS='|' read -r CFG IDS JSONL PREF SEEDS <<< "$ITEM"
  echo "=== [$PREF] config=$CFG semillas=$SEEDS inicio $(date) ==="
  python $P/scripts/correr_vllm_multi.py "$HOME/modelos/Qwen3.5-0.8B" $CFG $IDS $JSONL "$R/$PREF" $SEEDS > "$HOME/dia_$PREF.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
    { echo "ítem: $PREF ($CFG, semillas $SEEDS)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/dia_$PREF.log"; } > "$R/errores_dia_$PREF.txt"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
done
echo "=== Análisis sin GPU y commit $(date) ==="
python $P/scripts/analisis_dia.py > "$HOME/analisis_dia.log" 2>&1 || echo "El análisis falló; ver ~/analisis_dia.log"
cd $P
echo "=== Cola del día terminada $(date) ==="
