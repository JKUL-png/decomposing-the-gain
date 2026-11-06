#!/bin/bash
# Cola nocturna: corre las 5 variantes de "cero edición", UNA a la vez, en este orden. Si una falla, guarda el error y
# Uso:  nohup bash cola_noche.sh > ~/cola_noche.log 2>&1 &
source "$HOME/venv-vllm/bin/activate"
export VLLM_USE_FLASHINFER_SAMPLER=0   # sin nvcc en WSL
P=/workspace/decomposing-the-gain
R=$P/resultados
LOCK=$HOME/cola_noche.lock
if [ -e "$LOCK" ]; then echo "Ya hay una cola corriendo o quedó un candado ($LOCK). No lanzo."; exit 1; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
cd "$HOME"
echo "=== Cola iniciada $(date) ==="
for V in no_thinking presence0 presence2 rep105 rep110; do
  OUT=$R/cero_edicion_$V.csv
  if [ -e "$OUT" ]; then echo "[$V] ya existe $OUT; lo salto (no sobrescribo)"; continue; fi
  echo "=== [$V] inicio $(date) ==="
  python $P/scripts/correr_vllm.py "$HOME/modelos/Qwen3.5-0.8B" $V math500_subset100_ids.txt "$OUT" > "$HOME/cola_$V.log" 2>&1
  CODE=$?
  if [ $CODE -ne 0 ] || [ ! -e "$OUT" ]; then
    echo "[$V] FALLÓ (código $CODE) $(date)"
    { echo "variante: $V"; echo "código de salida: $CODE"; echo "fecha: $(date)"; echo "--- últimas líneas del log ---"; tail -n 60 "$HOME/cola_$V.log"; } > "$R/errores_$V.txt"
    sleep 20   # deja que la GPU se libere antes de la siguiente
  else
    echo "[$V] OK $(date): $(cat "$OUT.meta.json")"
    sleep 20
  fi
done
echo "=== Resumen y commit $(date) ==="
python $P/scripts/resumen_noche.py > "$HOME/resumen_noche.log" 2>&1 || echo "El resumen falló; ver ~/resumen_noche.log"
cd $P
echo "=== Cola terminada $(date) ==="
rm -f "$LOCK"
