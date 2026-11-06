#!/bin/bash
# Cola de la ronda 3, UN ítem a la vez, en orden. Si uno falla, guarda el error y sigue (sin reintentar).
#  Parte 1 (A): GSM8K e IFEval, semillas 1-3 (la 0 ya existe), editado thinking / editado no-think / original no-think
#  Prueba corta del reintento (si falla, se saltan los ítems de la Parte 2) -> Parte 2: reintento (A) y forzar respuesta (B)
#  Parte 3: segundo subconjunto fijo de GSM8K (b), semillas 0-3, 3 configuraciones
#  Al final: análisis sin GPU (RESUMEN_RONDA3.md) y commit.
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_r3.lock
if [ -e "$LOCK" ] || [ -e "$HOME/cola_r2.lock" ] || [ -e "$HOME/cola_dia.lock" ] || [ -e "$HOME/cola_noche.lock" ]; then echo "Hay un candado (cola corriendo o interrumpida). No lanzo."; exit 1; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
M0=$HOME/modelos/Qwen3.5-0.8B
ME=$HOME/modelos/Qwen3.5-0.8B-p50c
echo "=== Cola ronda 3 iniciada $(date) ==="

correr_multi() {   # modelo | config | ids | jsonl | prefijo | semillas | tarea
  IFS='|' read -r MOD CFG IDS JSONL PREF SEEDS TAREA <<< "$1"
  echo "=== [$PREF] modelo=$(basename $MOD) config=$CFG semillas=$SEEDS tarea=$TAREA inicio $(date) ==="
  python $P/scripts/correr_vllm_multi.py "$MOD" $CFG $IDS $JSONL "$R/$PREF" $SEEDS $TAREA > "$HOME/r3_$PREF.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
    { echo "ítem: $PREF ($(basename $MOD), $CFG, semillas $SEEDS, tarea $TAREA)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/r3_$PREF.log"; } > "$R/errores_r3_$PREF.txt"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
  return $CODE
}

correr_reint() {   # ids | jsonl | prefijo | semilla | extra
  IDS=$1; JSONL=$2; PREF=$3; SEED=$4; EXTRA=$5
  echo "=== [$PREF] reintento+forzar (modelo original) semilla=$SEED $EXTRA inicio $(date) ==="
  python $P/scripts/correr_vllm_reintento.py "$M0" $IDS $JSONL "$R/$PREF" $SEED $EXTRA > "$HOME/r3_$PREF.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ]; then
    echo "[$PREF] terminó con errores (código $CODE) $(date)"
    { echo "ítem: $PREF (reintento/forzar, $IDS, semilla $SEED $EXTRA)"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/r3_$PREF.log"; } > "$R/errores_r3_$PREF.txt"
  else
    echo "[$PREF] OK $(date)"
  fi
  sleep 20
  return $CODE
}

# ---- Parte 1 (A): semillas 1,2,3 de GSM8K e IFEval (mismo prefijo que la semilla 0 de ayer)
correr_multi "$ME|base_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_ed_think|1,2,3|gsm8k"
correr_multi "$ME|nothink_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_ed_nothink|1,2,3|gsm8k"
correr_multi "$M0|nothink_mit|gsm8k_subset100_ids.txt|gsm8k_subset100.jsonl|r2_gsm8k_orig_nothink|1,2,3|gsm8k"
correr_multi "$ME|base_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_ed_think|1,2,3|ifeval"
correr_multi "$ME|nothink_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_ed_nothink|1,2,3|ifeval"
correr_multi "$M0|nothink_mit|ifeval_subset100_ids.txt|ifeval_subset100.jsonl|r2_ifeval_orig_nothink|1,2,3|ifeval"

# ---- Prueba corta del reintento (6 problemas, tope 12,000 tokens). Si falla, no se corre la Parte 2.
correr_reint math500_subset100_ids.txt math500_subset100.jsonl r3_prueba 0 "--n 6 --max-tokens 12000"
if [ $? -eq 0 ] && [ -e "$R/r3_prueba_A_s0.csv" ] && [ -e "$R/r3_prueba_B_s0.csv" ]; then
  echo "Prueba corta OK: sigo con la Parte 2"
  # ---- Parte 2: reintento (A) y forzar (B), semilla 0
  correr_reint math500_subset100_ids.txt math500_subset100.jsonl r3_reint_math 0 ""
  correr_reint gsm8k_subset100_ids.txt gsm8k_subset100.jsonl r3_reint_gsm8k 0 ""
else
  echo "Prueba corta FALLÓ: se SALTA la Parte 2 (ver errores_r3_r3_prueba.txt)"
fi
rm -f "$R"/r3_prueba_*    # archivos de la prueba (son nuestros y temporales)

# ---- Parte 3: segundo subconjunto fijo de GSM8K (b), semillas 0-3
correr_multi "$ME|base_mit|gsm8k_subset100b_ids.txt|gsm8k_subset100b.jsonl|r3_gsm8kb_ed_think|0,1,2,3|gsm8k"
correr_multi "$ME|nothink_mit|gsm8k_subset100b_ids.txt|gsm8k_subset100b.jsonl|r3_gsm8kb_ed_nothink|0,1,2,3|gsm8k"
correr_multi "$M0|nothink_mit|gsm8k_subset100b_ids.txt|gsm8k_subset100b.jsonl|r3_gsm8kb_orig_nothink|0,1,2,3|gsm8k"

echo "=== Análisis sin GPU y commit $(date) ==="
python $P/scripts/analisis_ronda3.py > "$HOME/analisis_r3.log" 2>&1 || echo "El análisis falló; ver ~/analisis_r3.log"
cd $P
echo "=== Cola ronda 3 terminada $(date) ==="
