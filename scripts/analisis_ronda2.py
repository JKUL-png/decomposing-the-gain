"""Ronda 2 (sin GPU): 2x2 edicion x modo, McNemar pareado entre todos los brazos, precision solo entre las que
terminaron, GSM8K/IFEval, normas de la edicion. Solo numeros -> resultados/RESUMEN_RONDA2.md.
Regla principal: ESTRICTA (en no-thinking cuenta solo si NO llego al limite). Bootstrap por problema, semilla fija."""
import os, re, glob, json, math, itertools
import numpy as np, pandas as pd
from fractions import Fraction

R = "/workspace/decomposing-the-gain/resultados"
RNG = np.random.default_rng(20261104)
B = 10000


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * max(0, c - h), 100 * min(1, c + h)


def rutas(pref):
    out = {}
    if os.path.exists(f"{R}/{pref}.csv"):
        out[0] = f"{R}/{pref}.csv"
    for f in glob.glob(f"{R}/{pref}_s*.csv"):
        m = re.search(r"_s(\d+)\.csv$", f)
        if m:
            out[int(m.group(1))] = f
    return dict(sorted(out.items()))


def cargar(prefijos):
    fr = []
    for pref in ([prefijos] if isinstance(prefijos, str) else prefijos):
        for s, f in rutas(pref).items():
            d = pd.read_csv(f)
            d["semilla"] = s
            d["_pref"] = pref
            m = f + ".meta.json"
            d["_seg"] = json.load(open(m))["segundos"] if os.path.exists(m) else np.nan
            fr.append(d)
    if not fr:
        return None
    d = pd.concat(fr, ignore_index=True)
    est = ((d["correcto"] == 1) & (d["llego_limite"] == 0)).astype(int)
    d["completo"] = d["correcto"]
    d["correcto"] = np.where(d["modo"] == "no-thinking", est, d["correcto"]).astype(int)
    return d


# nombre del brazo -> prefijos (se combinan semillas de varios prefijos)
MATH = {
    "orig · thinking MIT": ["linea_base_vllm"],
    "orig · no-think muestreo MIT": ["dia_nothink_mit100", "r2_orig_nothinkmit"],
    "orig · no-think 32k": ["cero_edicion_no_thinking"],
    "p50c · thinking MIT": ["r2_ed_think"],
    "p50c · no-think muestreo MIT": ["r2_ed_nothinkmit"],
    "p50c · no-think 32k": ["r2_ed_nothink32k"],
    "placebo · thinking MIT": ["r2_pla_think"],
    "orig · rep 1.1 (thinking)": ["cero_edicion_rep110"],
    "orig · rep 1.05 (thinking)": ["cero_edicion_rep105"],
    "orig · presence 0 (thinking)": ["cero_edicion_presence0"],
    "orig · presence 2 (thinking)": ["cero_edicion_presence2"],
}
OTRAS = {
    "GSM8K orig · thinking MIT": ["r2_gsm8k_orig_think"],
    "GSM8K orig · no-think muestreo MIT": ["r2_gsm8k_orig_nothink"],
    "GSM8K p50c · thinking MIT": ["r2_gsm8k_ed_think"],
    "GSM8K p50c · no-think muestreo MIT": ["r2_gsm8k_ed_nothink"],
    "IFEval orig · thinking MIT": ["r2_ifeval_orig_think"],
    "IFEval orig · no-think muestreo MIT": ["r2_ifeval_orig_nothink"],
    "IFEval p50c · thinking MIT": ["r2_ifeval_ed_think"],
    "IFEval p50c · no-think muestreo MIT": ["r2_ifeval_ed_nothink"],
}
ESPERADO_R2 = {"r2_ed_think": [0, 1, 2, 3], "r2_ed_nothinkmit": [0, 1, 2, 3], "r2_ed_nothink32k": [0, 1, 2, 3],
               "r2_orig_nothinkmit": [1, 2, 3], "r2_pla_think": [0, 1]}
for _v in OTRAS.values():
    ESPERADO_R2[_v[0]] = [0]


def ic_boot(v):
    v = np.asarray(v, float)
    m = v[RNG.integers(0, len(v), (B, len(v)))].mean(axis=1)
    return 100 * np.percentile(m, 2.5), 100 * np.percentile(m, 97.5)


def mcnemar_exacto(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    p = 2 * sum(Fraction(math.comb(n, i), 2 ** n) for i in range(k + 1))
    return float(min(Fraction(1), p))


def guardar(nombre, filas):
    """Escribe resultados/<nombre>.csv con números sin redondear (para el paper: todo número sale de un CSV)."""
    pd.DataFrame(filas).to_csv(f"{R}/{nombre}.csv", index=False)


def fila_mcnemar(tabla, f, p_holm):
    """f = (A, B, parejas, b, c, dif_pts, (ic_lo, ic_hi), p_exacto)."""
    return dict(tabla=tabla, A=f[0], B=f[1], parejas=f[2], b=f[3], c=f[4], dif_A_menos_B_pts=f[5],
                dif_boot_lo=f[6][0], dif_boot_hi=f[6][1], p_mcnemar_exacto=f[7], p_holm=p_holm)


def holm(ps):
    o = sorted(range(len(ps)), key=lambda i: ps[i])
    adj = [0] * len(ps)
    mx = 0
    for r, i in enumerate(o):
        mx = max(mx, min(1, (len(ps) - r) * ps[i]))
        adj[i] = mx
    return adj


def main():
    L = ["# Resumen ronda 2 (solo números, sin interpretar)", "",
         "**Regla principal: estricta** (en no-thinking cuenta solo si NO llegó al límite de tokens). MATH-500: mismos 100 problemas fijos (salvo la tabla de 500). "
         "Modelos: orig = Qwen3.5-0.8B; p50c = edición del MIT (la de 48.1% en su informe, reconstruida con hash verificado); placebo = edición aleatoria de rango 1, mismos tensores y columnas, misma norma. "
         "IC por corrida: Wilson 95%. IC agrupado y de diferencias: bootstrap por problema (10000, semilla fija). Pruebas pareadas: McNemar exacto bilateral sobre parejas problema+semilla comunes; "
         "p ajustado por Holm dentro de la tabla (las semillas del mismo problema no son independientes).", ""]
    datos = {k: cargar(v) for k, v in {**MATH, **OTRAS}.items()}
    # 1 corridas individuales
    L += ["## 1. Corridas individuales", "",
          "| Prefijo | Semilla | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron | Precisión entre las que terminaron % (Wilson) | Tokens medios | Min |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    vistos = {}
    t1 = []
    for nombre, d in datos.items():
        if d is None:
            continue
        for (pref, s), g in d.groupby(["_pref", "semilla"]):
            n, k, lim = len(g), int(g.correcto.sum()), int(g.llego_limite.sum())
            fin = n - lim
            kf = int(g[g.llego_limite == 0].correcto.sum())
            w, wl, wf = wilson(k, n), wilson(lim, n), wilson(kf, fin)
            fin_txt = f"{100*kf/fin:.1f} ({wf[0]:.1f}–{wf[1]:.1f})" if fin else "n/a"
            L.append(f"| {pref} | {s} | {n} | {k} | {100*k/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} ({wl[0]:.1f}–{wl[1]:.1f}) | {fin} | {fin_txt} | {g.tokens.mean():.0f} | {g._seg.iloc[0]/60:.1f} |")
            t1.append(dict(brazo=nombre, prefijo=pref, semilla=int(s), n=n, correctos=k, precision_pct=100 * k / n,
                           precision_wilson_lo=w[0], precision_wilson_hi=w[1], al_limite=lim, al_limite_pct=100 * lim / n,
                           al_limite_wilson_lo=wl[0], al_limite_wilson_hi=wl[1], terminaron=fin, correctos_terminaron=kf,
                           precision_terminaron_pct=100 * kf / fin if fin else np.nan,
                           precision_terminaron_wilson_lo=wf[0] if fin else np.nan, precision_terminaron_wilson_hi=wf[1] if fin else np.nan,
                           tokens_medios=g.tokens.mean(), minutos=g._seg.iloc[0] / 60))
            vistos.setdefault(pref, set()).add(int(s))
    guardar("tabla_r2_corridas", t1)
    d5 = cargar("r2_orig_nothink32k_500")
    faltan = []
    for p, ss in ESPERADO_R2.items():
        f = sorted(set(ss) - vistos.get(p, set()))
        if f:
            faltan.append(f"{p} semillas {f}")
    if d5 is None:
        faltan.append("r2_orig_nothink32k_500")
    L += ["", "Corridas FALTANTES: " + ("; ".join(faltan) if faltan else "ninguna"), ""]
    # 2 promedio por brazo
    L += ["## 2. MATH-500 (100 fijos): promedio por brazo", "",
          "| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |",
          "|---|---|---|---|---|---|---|"]
    t2 = []
    for nombre in MATH:
        d = datos[nombre]
        if d is None:
            continue
        pp = d.groupby("id").correcto.mean()
        ic = ic_boot(pp.values)
        fin = d[d.llego_limite == 0]
        fin_txt = f"{100*fin.correcto.mean():.1f} ({int(fin.correcto.sum())}/{len(fin)})" if len(fin) else "n/a"
        sem = [int(x) for x in sorted(d.semilla.unique())]
        L.append(f"| {nombre} | {sem} | {len(d)} | {100*pp.mean():.1f} ({ic[0]:.1f}–{ic[1]:.1f}) | {d.llego_limite.mean()*100:.1f} | {fin_txt} | {d.tokens.mean():.0f} |")
        t2.append(dict(tarea="MATH-500 (100 fijos)", brazo=nombre, semillas=" ".join(map(str, sem)), muestras=len(d),
                       precision_pct=100 * pp.mean(), precision_boot_lo=ic[0], precision_boot_hi=ic[1],
                       al_limite_pct=100 * d.llego_limite.mean(), terminaron=len(fin), correctos_terminaron=int(fin.correcto.sum()),
                       precision_terminaron_pct=100 * fin.correcto.mean() if len(fin) else np.nan, tokens_medios=d.tokens.mean()))
    guardar("tabla_r2_math_brazos", t2)
    # 3 McNemar
    L += ["", "## 3. McNemar pareado (A vs B; b = A acierta y B no; c = B acierta y A no)", "",
          "| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |", "|---|---|---|---|---|---|---|---|"]
    filas = []
    for a, b_ in itertools.combinations([n for n in MATH if datos[n] is not None], 2):
        da = datos[a][["id", "semilla", "correcto"]]
        db = datos[b_][["id", "semilla", "correcto"]]
        m = da.merge(db, on=["id", "semilla"], suffixes=("_a", "_b"))
        if len(m) < 50:
            continue
        b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum())
        c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
        pp = (m.correcto_a - m.correcto_b).groupby(m.id).mean()
        filas.append((a, b_, len(m), b, c, 100 * pp.mean(), ic_boot(pp.values), mcnemar_exacto(b, c)))
    ad = holm([f[7] for f in filas]) if filas else []
    for f, pa in zip(filas, ad):
        L.append(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
    guardar("tabla_r2_mcnemar", [fila_mcnemar("MATH-500 (100 fijos)", f, pa) for f, pa in zip(filas, ad)])
    # 4 los 500
    L += ["", "## 4. No-thinking con parámetros de la línea base (32,768) en los 500 problemas, semilla 0", ""]
    if d5 is None:
        L.append("(no existe)")
    else:
        L += ["| Grupo | n | Correctos (estricta) | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron: precisión % | Tokens medios |", "|---|---|---|---|---|---|---|"]
        grupos = [("TODOS", d5)] + [(f"nivel {l}", g) for l, g in d5.groupby("nivel")]
        t4 = []
        for nom, g in grupos:
            n, k, lim = len(g), int(g.correcto.sum()), int(g.llego_limite.sum())
            w, wl = wilson(k, n), wilson(lim, n)
            fin = g[g.llego_limite == 0]
            fin_txt = f"{100*fin.correcto.mean():.1f}" if len(fin) else "n/a"
            L.append(f"| {nom} | {n} | {k} | {100*k/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} ({wl[0]:.1f}–{wl[1]:.1f}) | {fin_txt} | {g.tokens.mean():.0f} |")
            t4.append(dict(config="orig · no-think 32k", semilla=0, grupo=nom, n=n, correctos_estricta=k, precision_pct=100 * k / n,
                           precision_wilson_lo=w[0], precision_wilson_hi=w[1], al_limite_pct=100 * lim / n,
                           al_limite_wilson_lo=wl[0], al_limite_wilson_hi=wl[1],
                           precision_terminaron_pct=100 * fin.correcto.mean() if len(fin) else np.nan,
                           tokens_medios=g.tokens.mean(), correctos_texto_completo=int(g.completo.sum())))
        guardar("tabla_r2_math500_nothink32k", t4)
        L.append("")
        L.append(f"Nota (texto completo, no principal): {int(d5.completo.sum())}/{len(d5)} = {100*d5.completo.mean():.1f}%. "
                 "Referencia externa: el informe del MIT da 48.1% para p50c con thinking (MATH-500, 500 problemas x 4 muestras); no es comparable 1 a 1 (otro modo, otra muestra).")
    # 5 GSM8K / IFEval
    L += ["", "## 5. GSM8K e IFEval (100 fijos cada uno, semilla 0; IFEval = estricto a nivel de prompt, corrector oficial de lm-eval)", "",
          "| Brazo | n | Correctos | Precisión % (Wilson) | Al límite % | Terminaron: precisión % |", "|---|---|---|---|---|---|"]
    t5 = []
    for nombre in OTRAS:
        d = datos[nombre]
        if d is None:
            L.append(f"| {nombre} | FALTA | | | | |")
            continue
        # La tabla 5 es de la semilla 0 (así se escribió en la ronda 2). Desde la ronda 3 algunos prefijos tienen
        # semillas 1-3: se filtran aquí para que la tabla siga diciendo lo que su título dice.
        d = d[d.semilla == 0]
        n, k = len(d), int(d.correcto.sum())
        w = wilson(k, n)
        fin = d[d.llego_limite == 0]
        fin_txt = f"{100*fin.correcto.mean():.1f} ({int(fin.correcto.sum())}/{len(fin)})" if len(fin) else "n/a"
        L.append(f"| {nombre} | {n} | {k} | {100*k/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*d.llego_limite.mean():.1f} | {fin_txt} |")
        t5.append(dict(brazo=nombre, semilla=0, n=n, correctos=k, precision_pct=100 * k / n, precision_wilson_lo=w[0],
                       precision_wilson_hi=w[1], al_limite_pct=100 * d.llego_limite.mean(), terminaron=len(fin),
                       correctos_terminaron=int(fin.correcto.sum()),
                       precision_terminaron_pct=100 * fin.correcto.mean() if len(fin) else np.nan))
    guardar("tabla_r2_gsm8k_ifeval_s0", t5)
    # 6 normas
    L += ["", "## 6. Tamaño de la edición (medido sobre los pesos bf16 finales)", ""]
    f = f"{R}/ediciones_norma.csv"
    if os.path.exists(f):
        e = pd.read_csv(f)
        L += ["| Modelo | Tensor | ‖ΔW‖_F | ‖W‖_F | ‖ΔW‖/‖W‖ | Columnas tocadas |", "|---|---|---|---|---|---|"]
        for _, r in e.iterrows():
            capa = r.tensor.split(".")[3]
            L.append(f"| {r.modelo} | capa {capa} mlp.down_proj | {r.norma_dW} | {r.norma_W} | {r.cambio_relativo} | {r.columnas} |")
    open(f"{R}/RESUMEN_RONDA2.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("RESUMEN_RONDA2.md escrito;", len(filas), "pares McNemar")


if __name__ == "__main__":
    main()
