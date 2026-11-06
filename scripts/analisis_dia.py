"""Análisis SIN GPU de las corridas guardadas. Genera resultados/RESUMEN_DIA.md (solo números) y
resultados/REVISION_no_thinking_limite.md (casos de no-thinking correctos que llegaron al límite).
Tolera corridas faltantes (las marca). Uso: python analisis_dia.py"""
import os, sys, re, json, glob, math
os.environ.setdefault("PROYECTO_RAIZ", "/workspace/decomposing-the-gain")
sys.path.insert(0, os.path.join(os.environ["PROYECTO_RAIZ"], "scripts"))
import numpy as np, pandas as pd
from comun_math import ultima_caja, BS

R = os.path.join(os.environ["PROYECTO_RAIZ"], "resultados")
D = os.path.join(os.environ["PROYECTO_RAIZ"], "datos")
BASE = "linea_base_vllm"
VARIANTES = ["cero_edicion_no_thinking", "dia_nothink_mit100", "cero_edicion_presence0", "cero_edicion_presence2",
             "cero_edicion_rep105", "cero_edicion_rep110"]
NOTHINK = ["cero_edicion_no_thinking", "dia_nothink_mit100", "dia_nothink_mit500"]
ESPERADAS = {  # lo que debería existir al terminar las colas (prefijo: semillas)
    BASE: [0, 1, 2, 3], "cero_edicion_no_thinking": [0, 1, 2, 3], "cero_edicion_rep110": [0, 1, 2, 3],
    "cero_edicion_presence0": [0], "cero_edicion_presence2": [0], "cero_edicion_rep105": [0],
    "dia_nothink_mit100": [0], "dia_nothink_mit500": [0]}
RNG = np.random.default_rng(20261104)
B = 10000


def wilson(k, n, z=1.96):
    if n == 0: return (float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0, c - h), 100 * min(1, c + h)


def rutas(pref):
    """{semilla: ruta_csv}. Semilla 0 puede ser <pref>.csv (noche) o <pref>_s0.csv (día)."""
    out = {}
    if os.path.exists(f"{R}/{pref}.csv"): out[0] = f"{R}/{pref}.csv"
    for f in glob.glob(f"{R}/{pref}_s*.csv"):
        m = re.search(r"_s(\d+)\.csv$", f)
        if m: out[int(m.group(1))] = f
    return dict(sorted(out.items()))


def cargar(pref):
    frames = []
    for s, f in rutas(pref).items():
        d = pd.read_csv(f); d["semilla"] = s; d["_csv"] = f; frames.append(d)
    if not frames: return None
    d = pd.concat(frames, ignore_index=True)
    # REGLA PRINCIPAL (decidida 2026-11-04): en no-thinking solo cuenta como correcta si NO llegó al límite.
    # 'correcto' pasa a ser la estricta; la regla de texto completo queda en 'correcto_completo' (solo para notas).
    d["correcto_completo"] = d["correcto"]
    estricta = ((d["correcto"] == 1) & (d["llego_limite"] == 0)).astype(int)
    d["correcto"] = np.where(d["modo"] == "no-thinking", estricta, d["correcto"]).astype(int)
    return d


def tiempo_min(f):
    m = f + ".meta.json"
    return round(json.load(open(m))["segundos"] / 60, 1) if os.path.exists(m) else None


def ic_cluster(vals_por_problema):
    """IC 95% bootstrap (percentiles) remuestreando PROBLEMAS; entrada: array de promedios por problema."""
    v = np.asarray(vals_por_problema, float)
    medias = v[RNG.integers(0, len(v), (B, len(v)))].mean(axis=1)
    return 100 * np.percentile(medias, 2.5), 100 * np.percentile(medias, 97.5)


L = ["# Resumen del día (solo números, sin interpretar)", "",
     "**Regla de calificación principal: estricta** (en no-thinking cuenta solo si la respuesta NO llegó al límite de tokens; en thinking "
     "equivale a la normal). La regla de texto completo aparece solo como nota en la tabla 4. "
     "Mismos 100 problemas fijos (salvo `dia_nothink_mit500`: los 500). IC por corrida: Wilson 95%. IC agrupado y de diferencias: "
     f"bootstrap por problema ({B} remuestreos, semilla fija) sobre promedios por problema. Semilla 0 = corridas de anoche/pilotos.", ""]
datos = {p: cargar(p) for p in ESPERADAS}

# ---- Tabla 1: una fila por corrida
L += ["## 1. Corridas individuales", "", "| Corrida | Semilla | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Tokens medios | Tiempo min |", "|---|---|---|---|---|---|---|---|"]
faltan = []
T1, T2, T3, T4, T5 = [], [], [], [], []   # se escriben como CSV (resultados/tabla_dia_*.csv) al final
for p, ss in ESPERADAS.items():
    d = datos[p]; hay = set() if d is None else set(d.semilla)
    for s in ss:
        if s not in hay: faltan.append(f"{p} s{s}"); continue
        g = d[d.semilla == s]; n = len(g); k = int(g.correcto.sum()); l = int(g.llego_limite.sum())
        a, b = wilson(k, n); la, lb = wilson(l, n)
        L.append(f"| {p} | {s} | {n} | {k} | {100*k/n:.1f} ({a:.1f}–{b:.1f}) | {100*l/n:.1f} ({la:.1f}–{lb:.1f}) | {g.tokens.mean():.0f} | {tiempo_min(g._csv.iloc[0])} |")
        T1.append(dict(prefijo=p, semilla=int(s), n=n, correctos=k, precision_pct=100 * k / n, precision_wilson_lo=a, precision_wilson_hi=b,
                       al_limite=l, al_limite_pct=100 * l / n, al_limite_wilson_lo=la, al_limite_wilson_hi=lb,
                       tokens_medios=g.tokens.mean(), minutos=tiempo_min(g._csv.iloc[0])))
L += ["", "Corridas FALTANTES (no existe su CSV): " + (", ".join(faltan) if faltan else "ninguna"), ""]

# ---- Tabla 2: agrupado por configuración (promedio sobre semillas)
L += ["## 2. Promedio sobre las semillas disponibles (100 problemas)", "",
      "| Configuración | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % (IC bootstrap) |", "|---|---|---|---|---|"]
for p in [BASE] + VARIANTES:
    d = datos.get(p)
    if d is None: continue
    pp = d.groupby("id").agg(c=("correcto", "mean"), l=("llego_limite", "mean"))
    a, b = ic_cluster(pp.c); la, lb = ic_cluster(pp.l)
    L.append(f"| {p} | {sorted(set(d.semilla))} | {len(d)} | {100*pp.c.mean():.1f} ({a:.1f}–{b:.1f}) | {100*pp.l.mean():.1f} ({la:.1f}–{lb:.1f}) |")
    T2.append(dict(configuracion=p, semillas=" ".join(str(int(x)) for x in sorted(set(d.semilla))), muestras=len(d),
                   precision_pct=100 * pp.c.mean(), precision_boot_lo=a, precision_boot_hi=b,
                   al_limite_pct=100 * pp.l.mean(), al_limite_boot_lo=la, al_limite_boot_hi=lb))
L.append("")

# ---- Tabla 3: pareado contra la línea base, por grupo
L += ["## 3. Análisis pareado contra la línea base (misma pareja problema+semilla)", "",
      "Grupo = estado de la LÍNEA BASE en esa pareja: 'antes al límite' (llegó a 32,768) o 'ya terminaba'. "
      "Contribución = (correctos variante − correctos base en el grupo) / total de parejas × 100 (puntos de precisión). "
      "Cortó = en 'antes al límite', la variante NO llegó al límite.", "",
      "| Variante | Semillas comunes | Parejas | Dif. total (pts) (IC) | Antes al límite: parejas | …correctos base | …correctos variante | …cortó el bucle | Contribución (pts) | Ya terminaban: parejas | …correctos base | …correctos variante | …perdidos | …ganados | Contribución (pts) |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
db = datos[BASE]
for p in VARIANTES:
    dv = datos.get(p)
    if dv is None or db is None: L.append(f"| {p} | (sin datos) |" + " |" * 13); continue
    comunes = sorted(set(db.semilla) & set(dv.semilla))
    if not comunes: L.append(f"| {p} | ninguna |" + " |" * 13); continue
    m = db[db.semilla.isin(comunes)][["id", "semilla", "correcto", "llego_limite"]].merge(
        dv[dv.semilla.isin(comunes)][["id", "semilla", "correcto", "llego_limite"]], on=["id", "semilla"], suffixes=("_b", "_v"))
    N = len(m); dif = (m.correcto_v - m.correcto_b)
    pp = dif.groupby(m.id).mean(); a, b = ic_cluster(pp)
    cut = m[m.llego_limite_b == 1]; fin = m[m.llego_limite_b == 0]
    c1 = 100 * (cut.correcto_v.sum() - cut.correcto_b.sum()) / N
    c2 = 100 * (fin.correcto_v.sum() - fin.correcto_b.sum()) / N
    perd = int(((fin.correcto_b == 1) & (fin.correcto_v == 0)).sum()); gan = int(((fin.correcto_b == 0) & (fin.correcto_v == 1)).sum())
    L.append(f"| {p} | {comunes} | {N} | {100*dif.mean():+.1f} ({a:+.1f}…{b:+.1f}) | {len(cut)} | {int(cut.correcto_b.sum())} | {int(cut.correcto_v.sum())} "
             f"| {int((cut.llego_limite_v == 0).sum())} | {c1:+.1f} | {len(fin)} | {int(fin.correcto_b.sum())} | {int(fin.correcto_v.sum())} | {perd} | {gan} | {c2:+.1f} |")
    T3.append(dict(variante=p, semillas_comunes=" ".join(str(int(x)) for x in comunes), parejas=N, dif_total_pts=100 * dif.mean(),
                   dif_total_boot_lo=a, dif_total_boot_hi=b,
                   antes_limite_parejas=len(cut), antes_limite_correctos_base=int(cut.correcto_b.sum()),
                   antes_limite_correctos_variante=int(cut.correcto_v.sum()), antes_limite_corto_bucle=int((cut.llego_limite_v == 0).sum()),
                   antes_limite_contribucion_pts=c1, ya_terminaban_parejas=len(fin), ya_terminaban_correctos_base=int(fin.correcto_b.sum()),
                   ya_terminaban_correctos_variante=int(fin.correcto_v.sum()), ya_terminaban_perdidos=perd, ya_terminaban_ganados=gan,
                   ya_terminaban_contribucion_pts=c2))
L.append("")

# ---- Tabla 4: no-thinking, regla de calificación
L += ["## 4. Nota: no-thinking, regla estricta (principal, usada en todas las tablas) vs. regla de texto completo (solo nota)", "",
      "| Corrida | Semilla | n | Precisión estricta % (principal) | Precisión texto completo % (nota) | Correctos que llegaron al límite |", "|---|---|---|---|---|---|"]
revisar = []
for p in NOTHINK:
    d = datos.get(p)
    if d is None: continue
    for s in sorted(set(d.semilla)):
        g = d[d.semilla == s]
        cl = g[(g.correcto_completo == 1) & (g.llego_limite == 1)]
        L.append(f"| {p} | {s} | {len(g)} | {100*g.correcto.mean():.1f} | {100*g.correcto_completo.mean():.1f} | {len(cl)} |")
        T4.append(dict(corrida=p, semilla=int(s), n=len(g), precision_estricta_pct=100 * g.correcto.mean(),
                       precision_texto_completo_pct=100 * g.correcto_completo.mean(), correctos_al_limite=len(cl)))
        for _, r in cl.iterrows(): revisar.append((p, s, r))
L.append("")

# ---- Tabla 5: MATH-500 completo
d5 = datos.get("dia_nothink_mit500")
L += ["## 5. No-thinking (muestreo no-thinking del MIT) en los 500 problemas completos", ""]
if d5 is None:
    L += ["(sin datos: la corrida no existe)", ""]
else:
    L += ["| Grupo | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Tokens medios |", "|---|---|---|---|---|---|"]
    for nom, g in [("TODOS", d5)] + [(f"nivel {n}", g) for n, g in d5.groupby("nivel")]:
        n = len(g); k = int(g.correcto.sum()); l = int(g.llego_limite.sum()); a, b = wilson(k, n); la, lb = wilson(l, n)
        L.append(f"| {nom} | {n} | {k} | {100*k/n:.1f} ({a:.1f}–{b:.1f}) | {100*l/n:.1f} ({la:.1f}–{lb:.1f}) | {g.tokens.mean():.0f} |")
        T5.append(dict(config="orig · no-think muestreo MIT (8,192)", semilla=0, grupo=nom, n=n, correctos=k, precision_pct=100 * k / n,
                       precision_wilson_lo=a, precision_wilson_hi=b, al_limite_pct=100 * l / n, al_limite_wilson_lo=la,
                       al_limite_wilson_hi=lb, tokens_medios=g.tokens.mean(), correctos_texto_completo=int(g.correcto_completo.sum())))
    L += ["", f"Nota (regla de texto completo, no principal): {int(d5.correcto_completo.sum())}/{len(d5)} = {100*d5.correcto_completo.mean():.1f}%."]
    d1 = datos.get("dia_nothink_mit100")
    if d1 is not None:
        fijos = [l.strip() for l in open(f"{D}/math500_subset100_ids.txt") if l.strip() and not l.startswith("#")]
        a5 = d5[d5.id.isin(fijos)].set_index("id").sort_index(); a1 = d1[d1.semilla == 0].set_index("id").sort_index()
        com = a5.index.intersection(a1.index)
        L += ["", f"Control de reproducibilidad (mismos 100 fijos, misma configuración, misma semilla, distinto lote): precisión en el lote de 500 = "
              f"{int(a5.loc[com].correcto.sum())}/{len(com)}; en el lote de 100 = {int(a1.loc[com].correcto.sum())}/{len(com)}; "
              f"mismo resultado correcto/incorrecto en {int((a5.loc[com].correcto == a1.loc[com].correcto).sum())}/{len(com)} problemas; "
              f"mismos tokens exactos en {int((a5.loc[com].tokens == a1.loc[com].tokens).sum())}/{len(com)}.", ""]
        pd.DataFrame([dict(comparacion="mismos 100 fijos, nothink muestreo MIT, semilla 0: lote de 500 vs lote de 100", problemas=len(com),
                           correctos_lote500=int(a5.loc[com].correcto.sum()), correctos_lote100=int(a1.loc[com].correcto.sum()),
                           mismo_resultado=int((a5.loc[com].correcto == a1.loc[com].correcto).sum()),
                           mismos_tokens_exactos=int((a5.loc[com].tokens == a1.loc[com].tokens).sum()))]).to_csv(
            f"{R}/tabla_dia_reproducibilidad.csv", index=False)

open(f"{R}/RESUMEN_DIA.md", "w", encoding="utf-8").write("\n".join(L))
for _nom, _t in [("corridas", T1), ("promedios", T2), ("pareado_dos_grupos", T3), ("regla_nothink", T4), ("math500_nothinkmit", T5)]:
    pd.DataFrame(_t).to_csv(f"{R}/tabla_dia_{_nom}.csv", index=False)

# ---- Revisión de los no-thinking correctos que llegaron al límite
M = ["# Revisión: no-thinking correctos que llegaron al límite de tokens", "",
     f"Casos: {len(revisar)}. Para cada uno: tokens, nº de cajas de respuesta, dónde está la última (fracción del texto), respuesta extraída vs. oficial, "
     "y el final del texto.", ""]
oficial = {}
for l in open(f"{D}/math500_full.jsonl", encoding="utf-8"):
    j = json.loads(l); oficial[j["id"]] = j["answer"]
for p, s, r in revisar:
    jl = r["_csv"] + ".jsonl"
    texto = next((json.loads(l)["texto"] for l in open(jl, encoding="utf-8") if json.loads(l)["id"] == r["id"]), None)
    M += [f"## {p} · semilla {s} · {r['id']} · nivel {r['nivel']}", ""]
    if texto is None: M += ["(no se encontró el texto)", ""]; continue
    i = texto.rfind(BS + "boxed"); cola = texto[int(len(texto) * 0.8):].split("\n")
    M += [f"- tokens: {r['tokens']} | caracteres: {len(texto)} | cajas: {texto.count(BS + 'boxed')} | última caja en la posición {100*i/len(texto):.0f}% del texto",
          f"- extraída: `{ultima_caja(texto)}` | oficial: `{oficial.get(r['id'])}`",
          f"- líneas distintas en el último 20%: {len(set(cola))} de {len(cola)}",
          f"- tras la última caja (120 caracteres): `{texto[i:i+120]!r}`" if i >= 0 else "- sin caja",
          f"- final del texto: `{texto[-250:]!r}`", ""]
open(f"{R}/REVISION_no_thinking_limite.md", "w", encoding="utf-8").write("\n".join(M))
print("\n".join(L))
print(f"\nRevisión: {len(revisar)} casos -> REVISION_no_thinking_limite.md")
