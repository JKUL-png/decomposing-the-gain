"""Minutos y tokens de TODAS las corridas guardadas (sin GPU), leídos de resultados/*.csv.meta.json.
Salida: resultados/tabla_tiempos.csv (una fila por corrida). Solo lee; no recalcula nada.
Nota: los meta.json de reintento/forzar (r3_reint_*) cuentan los tokens de TODOS los intentos, incluidos los descartados."""
import os, re, glob, json
import pandas as pd

R = os.path.join(os.environ.get("PROYECTO_RAIZ", "/workspace/decomposing-the-gain"), "resultados")

filas = []
for m in sorted(glob.glob(f"{R}/*.csv.meta.json")):
    csv = os.path.basename(m)[:-len(".meta.json")]
    if csv.startswith("tabla_"):
        continue
    j = json.load(open(m))
    s = re.search(r"_s(\d+)\.csv$", csv)
    filas.append(dict(archivo=csv, prefijo=re.sub(r"(_s\d+)?\.csv$", "", csv),
                      semilla=j.get("semilla", int(s.group(1)) if s else 0), config=j.get("config"), variante=j.get("variante"),
                      problemas=j.get("problemas"), segundos=j.get("segundos"),
                      minutos=round(j["segundos"] / 60, 2) if j.get("segundos") is not None else None,
                      tokens_totales=j.get("tokens_totales"), tok_por_s=j.get("tok_por_s")))
df = pd.DataFrame(filas)
df.to_csv(f"{R}/tabla_tiempos.csv", index=False)
print(f"tabla_tiempos.csv: {len(filas)} corridas")
# Resumen por prefijo (para el paper, §9). Ojo: r3_reint_*_A y _B son la MISMA corrida (comparten el meta), no sumarlas dos veces.
g = df.groupby("prefijo").agg(corridas=("minutos", "size"), semillas=("semilla", lambda s: " ".join(str(int(x)) for x in sorted(s))),
                              minutos_medios=("minutos", "mean"), minutos_total=("minutos", "sum"),
                              tokens_totales_medios=("tokens_totales", "mean"), tok_por_s_medio=("tok_por_s", "mean")).reset_index()
unicos = df[~df.prefijo.str.endswith("_B") | ~df.prefijo.str.startswith("r3_reint_")]
g = pd.concat([g, pd.DataFrame([dict(prefijo="TOTAL (corridas únicas; reint A/B contadas una vez)", corridas=len(unicos),
                                     minutos_total=unicos.minutos.sum())])], ignore_index=True)
g.to_csv(f"{R}/tabla_tiempos_por_prefijo.csv", index=False)
print(f"tabla_tiempos_por_prefijo.csv: {len(g) - 1} prefijos; total {unicos.minutos.sum():.1f} min en {len(unicos)} corridas únicas")
