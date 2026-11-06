"""Genera resultados/RESUMEN_NOCHE.md: línea base + 5 variantes. Solo números, sin interpretar.
Uso (WSL): python resumen_noche.py"""
import os, sys, json, math
os.environ["PROYECTO_RAIZ"] = "/workspace/decomposing-the-gain"
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
import pandas as pd
from comun_math import ORDEN_NOCHE, CERO_EDICION, BASE_MIT

R = "/workspace/decomposing-the-gain/resultados"

def wilson(k, n, z=1.96):
    if n == 0: return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0, c - h), 100 * min(1, c + h)

def fila(nombre, csv_path, cambio):
    meta_p = csv_path + ".meta.json"
    if not os.path.exists(csv_path):
        err = f"{R}/errores_{nombre}.txt"
        return f"| {nombre} | {cambio} | - | - | - | - | - | FALLÓ o no corrió (ver `errores_{nombre}.txt`)" + (" [existe]" if os.path.exists(err) else " [no existe]") + " |"
    d = pd.read_csv(csv_path); n = len(d); k = int(d.correcto.sum()); l = int(d.llego_limite.sum())
    a, b = wilson(k, n); la, lb = wilson(l, n)
    t = d[d.llego_limite == 0]
    meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
    seg = meta.get("segundos"); tiempo = f"{seg/60:.1f} min" if seg else "(sin dato)"
    ec = meta.get("errores_calificacion", "?")
    return (f"| {nombre} | {cambio} | {k}/{n} = {100*k/n:.1f}% ({a:.1f}–{b:.1f}) | {l}/{n} = {100*l/n:.1f}% ({la:.1f}–{lb:.1f}) "
            f"| {int(t.correcto.sum())}/{len(t)} | {d.tokens.mean():.0f} | {tiempo} | errores de calificación: {ec} |")

lineas = ["# Resumen de la noche (solo números, sin interpretar)", "",
          "Mismos 100 problemas fijos, seed 0, prompt y calificador (math-verify 0.9.0) del MIT. Intervalos: Wilson 95%, entre paréntesis.", "",
          "| Brazo | Cambio vs. línea base | Precisión | % al límite (32,768) | Correctos entre las que terminaron | Tokens medios | Tiempo | Errores |",
          "|---|---|---|---|---|---|---|---|",
          fila("linea_base", f"{R}/linea_base_vllm.csv", "ninguno (MIT: thinking, temp 0.6, top_p 0.95, top_k 20, presence 1.5, rep 1.0)")]
cambios = {"no_thinking": "thinking apagado (muestreo igual a la base)", "presence0": "presence_penalty 0",
           "presence2": "presence_penalty 2.0", "rep105": "repetition_penalty 1.05", "rep110": "repetition_penalty 1.1"}
for v in ORDEN_NOCHE:
    lineas.append(fila(v, f"{R}/cero_edicion_{v}.csv", cambios[v]))
lineas += ["", "Archivos: `resultados/cero_edicion_<variante>.csv` (+ `.jsonl` textos, `.meta.json` tiempos), `resultados/linea_base_vllm.csv`.",
           "Nota: no-thinking se califica sobre el texto completo (no hay `</think>`).", ""]
open(f"{R}/RESUMEN_NOCHE.md", "w", encoding="utf-8").write("\n".join(lineas))
print("\n".join(lineas))
