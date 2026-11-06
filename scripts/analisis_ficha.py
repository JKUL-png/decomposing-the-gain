"""Config de thinking de la ficha de Qwen (temp 1.0; resto = BASE_MIT) en original y p50c, MATH-500 (100 fijos), semilla 0.
Sin GPU. Script APARTE para no alterar los números ya exportados (agregar brazos a analisis_ronda2 cambiaría el
estado del RNG del bootstrap y la familia de Holm de tabla_r2_mcnemar).
Comparaciones (pareadas por problema+semilla, solo semilla 0): ficha orig vs ficha p50c; ficha orig vs orig temp 0.6 (config MIT);
ficha p50c vs p50c temp 0.6. McNemar exacto bilateral, Holm dentro de estas 3. Bootstrap por problema (10,000, semilla 20261106).
División de la ganancia en dos grupos según si B (la referencia) llegó al límite.
Salidas: resultados/tabla_ficha_corridas.csv, tabla_ficha_mcnemar.csv, tabla_ficha_dos_grupos.csv, RESUMEN_FICHA.md."""
import numpy as np, pandas as pd
import analisis_ronda2 as A2
from analisis_ronda2 import cargar, wilson, mcnemar_exacto, holm, guardar, fila_mcnemar, R

A2.RNG = np.random.default_rng(20261106)   # ic_boot usa A2.RNG; semilla propia de este análisis
BRAZOS = {
    "orig · thinking ficha Qwen (temp 1.0)": "cero_edicion_ficha_qwen",
    "p50c · thinking ficha Qwen (temp 1.0)": "r2_ed_ficha_qwen",
    "orig · thinking MIT (temp 0.6)": "linea_base_vllm",
    "p50c · thinking MIT (temp 0.6)": "r2_ed_think",
}
COMPARA = [("orig · thinking ficha Qwen (temp 1.0)", "p50c · thinking ficha Qwen (temp 1.0)"),
           ("orig · thinking ficha Qwen (temp 1.0)", "orig · thinking MIT (temp 0.6)"),
           ("p50c · thinking ficha Qwen (temp 1.0)", "p50c · thinking MIT (temp 0.6)")]


def main():
    datos = {}
    for k, p in BRAZOS.items():
        d = cargar(p)
        if d is None:
            raise SystemExit(f"FALTA {p}")
        datos[k] = d[d.semilla == 0].copy()
    L = ["# Resumen: config de la ficha de Qwen (solo números)", "",
         "MATH-500, 100 fijos, semilla 0, thinking. Ficha = temp 1.0, top_p 0.95, top_k 20, presence 1.5, rep 1.0, 32,768. "
         "IC por corrida: Wilson 95%. McNemar exacto; p Holm dentro de las 3 comparaciones. Bootstrap por problema (10,000, semilla 20261106).", "",
         "## 1. Corridas", "", "| Brazo | Prefijo | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron | Correctas entre terminadas | Tokens medios | Min |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    t1 = []
    for k, d in datos.items():
        n, c, lim = len(d), int(d.correcto.sum()), int(d.llego_limite.sum())
        fin = n - lim; cf = int(d[d.llego_limite == 0].correcto.sum())
        w, wl = wilson(c, n), wilson(lim, n)
        L.append(f"| {k} | {BRAZOS[k]} | {n} | {c} | {100*c/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} ({wl[0]:.1f}–{wl[1]:.1f}) | {fin} | {cf} | {d.tokens.mean():.0f} | {d._seg.iloc[0]/60:.1f} |")
        t1.append(dict(brazo=k, prefijo=BRAZOS[k], semilla=0, n=n, correctos=c, precision_pct=100 * c / n,
                       precision_wilson_lo=w[0], precision_wilson_hi=w[1], al_limite=lim, al_limite_pct=100 * lim / n,
                       al_limite_wilson_lo=wl[0], al_limite_wilson_hi=wl[1], terminaron=fin, correctos_terminaron=cf,
                       tokens_medios=d.tokens.mean(), minutos=d._seg.iloc[0] / 60))
    guardar("tabla_ficha_corridas", t1)

    filas, t3 = [], []
    for a, b_ in COMPARA:
        m = datos[a][["id", "correcto", "llego_limite"]].merge(datos[b_][["id", "correcto", "llego_limite"]], on="id", suffixes=("_a", "_b"))
        b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum()); c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
        dif = m.correcto_a - m.correcto_b
        filas.append((a, b_, len(m), b, c, 100 * dif.mean(), A2.ic_boot(dif.values), mcnemar_exacto(b, c)))
        N = len(m); cut = m[m.llego_limite_b == 1]; fin = m[m.llego_limite_b == 0]
        t3.append(dict(A=a, B=b_, parejas=N, dif_total_pts=100 * dif.mean(),
                       B_al_limite_parejas=len(cut), B_al_limite_correctos_B=int(cut.correcto_b.sum()), B_al_limite_correctos_A=int(cut.correcto_a.sum()),
                       B_al_limite_A_termino=int((cut.llego_limite_a == 0).sum()),
                       B_al_limite_contribucion_pts=100 * (cut.correcto_a.sum() - cut.correcto_b.sum()) / N,
                       B_termino_parejas=len(fin), B_termino_correctos_B=int(fin.correcto_b.sum()), B_termino_correctos_A=int(fin.correcto_a.sum()),
                       B_termino_contribucion_pts=100 * (fin.correcto_a.sum() - fin.correcto_b.sum()) / N))
    ad = holm([f[7] for f in filas])
    guardar("tabla_ficha_mcnemar", [fila_mcnemar("MATH-500 (100 fijos) · ficha Qwen · semilla 0", f, pa) for f, pa in zip(filas, ad)])
    guardar("tabla_ficha_dos_grupos", t3)
    L += ["", "## 2. McNemar (b = A acierta y B no; c = B acierta y A no)", "",
          "| A | B | Parejas | b | c | Dif. A−B pts (IC bootstrap) | p exacto | p Holm |", "|---|---|---|---|---|---|---|---|"]
    for f, pa in zip(filas, ad):
        L.append(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
    L += ["", "## 3. Ganancia A−B en dos grupos (según si B llegó al límite)", "",
          "| A | B | Dif. total | B al límite: parejas | …contribución pts | B terminó: parejas | …contribución pts |", "|---|---|---|---|---|---|---|"]
    for r in t3:
        L.append(f"| {r['A']} | {r['B']} | {r['dif_total_pts']:+.1f} | {r['B_al_limite_parejas']} | {r['B_al_limite_contribucion_pts']:+.1f} | {r['B_termino_parejas']} | {r['B_termino_contribucion_pts']:+.1f} |")
    open(f"{R}/RESUMEN_FICHA.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main4():
    """Semillas 0-3 juntas (confirmación). Archivos aparte (_4sem) para no tocar los de semilla 0.
    Parejas problema+semilla; bootstrap por problema (10,000, semilla 20261107); Holm dentro de las 3 comparaciones."""
    A2.RNG = np.random.default_rng(20261107)
    datos = {}
    for k, p in BRAZOS.items():
        d = cargar(p)
        d = d[d.semilla.isin([0, 1, 2, 3])].copy()
        sem = sorted(int(x) for x in d.semilla.unique())
        if sem != [0, 1, 2, 3]:
            raise SystemExit(f"{p}: semillas {sem}, se esperaban 0-3")
        datos[k] = d
    t1 = []
    L = ["# Resumen: config de la ficha de Qwen, semillas 0-3 (solo números)", "",
         "MATH-500, 100 fijos, thinking. Ficha = temp 1.0; referencias = config MIT (temp 0.6). Por semilla: Wilson 95%. "
         "Juntas: bootstrap por problema (10,000, semilla 20261107). McNemar exacto sobre parejas problema+semilla; Holm dentro de las 3 comparaciones "
         "(las semillas del mismo problema no son independientes: p optimistas; mirar el IC bootstrap).", "",
         "## 1. Por semilla y juntas", "", "| Brazo | Semilla | n | Correctos | Precisión % (IC) | Al límite % | Correctas/terminadas | Tokens medios |", "|---|---|---|---|---|---|---|---|"]
    for k, d in datos.items():
        for s, g in d.groupby("semilla"):
            n, c, lim = len(g), int(g.correcto.sum()), int(g.llego_limite.sum())
            w = wilson(c, n); cf = int(g[g.llego_limite == 0].correcto.sum())
            t1.append(dict(brazo=k, prefijo=BRAZOS[k], semilla=str(int(s)), n=n, correctos=c, precision_pct=100 * c / n,
                           ic_lo=w[0], ic_hi=w[1], tipo_ic="wilson", al_limite_pct=100 * lim / n, terminaron=n - lim,
                           correctos_terminaron=cf, tokens_medios=g.tokens.mean()))
            L.append(f"| {k} | {int(s)} | {n} | {c} | {100*c/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} | {cf}/{n-lim} | {g.tokens.mean():.0f} |")
        pp = d.groupby("id").correcto.mean(); ic = A2.ic_boot(pp.values)
        fin = d[d.llego_limite == 0]
        t1.append(dict(brazo=k, prefijo=BRAZOS[k], semilla="0 1 2 3", n=len(d), correctos=int(d.correcto.sum()), precision_pct=100 * pp.mean(),
                       ic_lo=ic[0], ic_hi=ic[1], tipo_ic="bootstrap_problema", al_limite_pct=100 * d.llego_limite.mean(), terminaron=len(fin),
                       correctos_terminaron=int(fin.correcto.sum()), tokens_medios=d.tokens.mean()))
        L.append(f"| **{k}** | 0–3 | {len(d)} | {int(d.correcto.sum())} | **{100*pp.mean():.1f} ({ic[0]:.1f}–{ic[1]:.1f})** | {100*d.llego_limite.mean():.1f} | {int(fin.correcto.sum())}/{len(fin)} | {d.tokens.mean():.0f} |")
    guardar("tabla_ficha_4sem_corridas", t1)
    filas, t3 = [], []
    for a, b_ in COMPARA:
        m = datos[a][["id", "semilla", "correcto", "llego_limite"]].merge(datos[b_][["id", "semilla", "correcto", "llego_limite"]],
                                                                          on=["id", "semilla"], suffixes=("_a", "_b"))
        b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum()); c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
        dif = m.correcto_a - m.correcto_b
        pp = dif.groupby(m.id).mean()
        filas.append((a, b_, len(m), b, c, 100 * dif.mean(), A2.ic_boot(pp.values), mcnemar_exacto(b, c)))
        N = len(m); cut = m[m.llego_limite_b == 1]; fin = m[m.llego_limite_b == 0]
        t3.append(dict(A=a, B=b_, parejas=N, dif_total_pts=100 * dif.mean(),
                       B_al_limite_parejas=len(cut), B_al_limite_correctos_B=int(cut.correcto_b.sum()), B_al_limite_correctos_A=int(cut.correcto_a.sum()),
                       B_al_limite_A_termino=int((cut.llego_limite_a == 0).sum()),
                       B_al_limite_contribucion_pts=100 * (cut.correcto_a.sum() - cut.correcto_b.sum()) / N,
                       B_termino_parejas=len(fin), B_termino_correctos_B=int(fin.correcto_b.sum()), B_termino_correctos_A=int(fin.correcto_a.sum()),
                       B_termino_contribucion_pts=100 * (fin.correcto_a.sum() - fin.correcto_b.sum()) / N))
    ad = holm([f[7] for f in filas])
    guardar("tabla_ficha_4sem_mcnemar", [fila_mcnemar("MATH-500 (100 fijos) · ficha Qwen · semillas 0-3", f, pa) for f, pa in zip(filas, ad)])
    guardar("tabla_ficha_4sem_dos_grupos", t3)
    L += ["", "## 2. McNemar (b = A acierta y B no; c = B acierta y A no)", "",
          "| A | B | Parejas | b | c | Dif. A−B pts (IC bootstrap) | p exacto | p Holm |", "|---|---|---|---|---|---|---|---|"]
    for f, pa in zip(filas, ad):
        L.append(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
    L += ["", "## 3. Ganancia A−B en dos grupos (según si B llegó al límite)", "",
          "| A | B | Dif. total | B al límite: parejas | …contribución pts | B terminó: parejas | …contribución pts |", "|---|---|---|---|---|---|---|"]
    for r in t3:
        L.append(f"| {r['A']} | {r['B']} | {r['dif_total_pts']:+.1f} | {r['B_al_limite_parejas']} | {r['B_al_limite_contribucion_pts']:+.1f} | {r['B_termino_parejas']} | {r['B_termino_contribucion_pts']:+.1f} |")
    open(f"{R}/RESUMEN_FICHA_4SEM.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


TAREAS_OTRAS = {
    "GSM8K subconjunto 1": dict(of="r2_gsm8k_orig_ficha", ef="r2_gsm8k_ed_ficha", o6="r2_gsm8k_orig_think", e6="r2_gsm8k_ed_think",
                                nt="r2_gsm8k_orig_nothink"),
    "IFEval": dict(of="r2_ifeval_orig_ficha", ef="r2_ifeval_ed_ficha", o6="r2_ifeval_orig_think", e6="r2_ifeval_ed_think",
                   nt="r2_ifeval_orig_nothink"),
}
NOMBRES_OTRAS = dict(of="orig · thinking ficha Qwen (temp 1.0)", ef="p50c · thinking ficha Qwen (temp 1.0)",
                     o6="orig · thinking MIT (temp 0.6)", e6="p50c · thinking MIT (temp 0.6)", nt="orig · no-think muestreo MIT")
COMPARA_OTRAS = [("of", "ef"), ("of", "o6"), ("ef", "e6"), ("ef", "nt")]


def main_otras():
    """GSM8K (sub.1) e IFEval, solo semilla 0 (la ficha se corrió con 1 semilla aquí). Holm dentro de las 4 comparaciones de cada tarea.
    La 4a comparación (p50c ficha vs orig no-think) mira si el residuo de §6 sobrevive a la config de la ficha."""
    A2.RNG = np.random.default_rng(20261108)
    t1, t2, t3 = [], [], []
    L = ["# Resumen: config de la ficha de Qwen en GSM8K (sub.1) e IFEval, semilla 0 (solo números)", "",
         "Thinking con ficha = temp 1.0; referencias en semilla 0. Wilson 95% por corrida; McNemar exacto; Holm dentro de las 4 comparaciones de cada tarea; "
         "bootstrap por problema (10,000, semilla 20261108). No-think = muestreo MIT (8,192), regla estricta.", ""]
    for tarea, P in TAREAS_OTRAS.items():
        datos = {}
        for k, p in P.items():
            d = cargar(p)
            if d is None:
                raise SystemExit(f"FALTA {p}")
            d = d[d.semilla == 0].copy()
            if len(d) != 100:
                raise SystemExit(f"{p}: {len(d)} filas en semilla 0")
            datos[k] = d
        L += [f"## {tarea}", "", "| Brazo | Correctos | Precisión % (Wilson) | Al límite % | Correctas/terminadas | Tokens medios |", "|---|---|---|---|---|---|"]
        for k, d in datos.items():
            n, c, lim = len(d), int(d.correcto.sum()), int(d.llego_limite.sum())
            w = wilson(c, n); cf = int(d[d.llego_limite == 0].correcto.sum())
            t1.append(dict(tarea=tarea, brazo=NOMBRES_OTRAS[k], prefijo=P[k], semilla=0, n=n, correctos=c, precision_pct=100 * c / n,
                           precision_wilson_lo=w[0], precision_wilson_hi=w[1], al_limite_pct=100 * lim / n, terminaron=n - lim,
                           correctos_terminaron=cf, tokens_medios=d.tokens.mean()))
            L.append(f"| {NOMBRES_OTRAS[k]} | {c} | {100*c/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} | {cf}/{n-lim} | {d.tokens.mean():.0f} |")
        filas = []
        for a, b_ in COMPARA_OTRAS:
            m = datos[a][["id", "correcto", "llego_limite"]].merge(datos[b_][["id", "correcto", "llego_limite"]], on="id", suffixes=("_a", "_b"))
            b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum()); c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
            dif = m.correcto_a - m.correcto_b
            filas.append((NOMBRES_OTRAS[a], NOMBRES_OTRAS[b_], len(m), b, c, 100 * dif.mean(), A2.ic_boot(dif.values), mcnemar_exacto(b, c)))
            N = len(m); cut = m[m.llego_limite_b == 1]; fin = m[m.llego_limite_b == 0]
            t3.append(dict(tarea=tarea, A=NOMBRES_OTRAS[a], B=NOMBRES_OTRAS[b_], parejas=N, dif_total_pts=100 * dif.mean(),
                           B_al_limite_parejas=len(cut), B_al_limite_contribucion_pts=100 * (cut.correcto_a.sum() - cut.correcto_b.sum()) / N,
                           B_termino_parejas=len(fin), B_termino_contribucion_pts=100 * (fin.correcto_a.sum() - fin.correcto_b.sum()) / N))
        ad = holm([f[7] for f in filas])
        t2 += [fila_mcnemar(f"{tarea} · ficha Qwen · semilla 0", f, pa) for f, pa in zip(filas, ad)]
        L += ["", "| A | B | b | c | Dif. A−B pts (IC) | p exacto | p Holm |", "|---|---|---|---|---|---|---|"]
        for f, pa in zip(filas, ad):
            L.append(f"| {f[0]} | {f[1]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
        L.append("")
    guardar("tabla_ficha_otras_corridas", t1)
    guardar("tabla_ficha_otras_mcnemar", t2)
    guardar("tabla_ficha_otras_dos_grupos", t3)
    open(f"{R}/RESUMEN_FICHA_OTRAS.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main_otras4():
    """GSM8K (sub.1) e IFEval, semillas 0-3 juntas. Archivos aparte (_4sem): los de semilla 0 no cambian.
    Parejas problema+semilla; bootstrap por problema (10,000, semilla 20261109); Holm dentro de las 4 comparaciones de cada tarea.
    El original a temp 0.6 solo tiene semilla 0: su comparación usa las 100 parejas de esa semilla y su fila lo indica en `semilla`."""
    A2.RNG = np.random.default_rng(20261109)
    t1, t2, t3 = [], [], []
    L = ["# Resumen: config de la ficha de Qwen en GSM8K (sub.1) e IFEval, semillas 0-3 (solo números)", "",
         "Thinking con ficha = temp 1.0. Por semilla: Wilson 95%. Juntas: bootstrap por problema (10,000, semilla 20261109). "
         "McNemar exacto sobre parejas problema+semilla; Holm dentro de las 4 comparaciones de cada tarea (semillas del mismo problema no son "
         "independientes: p optimistas; mirar el IC bootstrap). orig temp 0.6 solo tiene semilla 0. No-think = muestreo MIT (8,192), regla estricta.", ""]
    for tarea, P in TAREAS_OTRAS.items():
        datos = {}
        for k, p in P.items():
            d = cargar(p)
            if d is None:
                raise SystemExit(f"FALTA {p}")
            d = d[d.semilla.isin([0, 1, 2, 3])].copy()
            sem = sorted(int(x) for x in d.semilla.unique())
            if sem != ([0] if k == "o6" else [0, 1, 2, 3]) or len(d) != 100 * len(sem):
                raise SystemExit(f"{p}: semillas {sem}, {len(d)} filas")
            datos[k] = d
        L += [f"## {tarea}", "", "| Brazo | Semilla | n | Correctos | Precisión % (IC) | Al límite % | Correctas/terminadas | Tokens medios |", "|---|---|---|---|---|---|---|---|"]
        for k, d in datos.items():
            comun = dict(tarea=tarea, brazo=NOMBRES_OTRAS[k], prefijo=P[k])
            for s, g in d.groupby("semilla"):
                n, c, lim = len(g), int(g.correcto.sum()), int(g.llego_limite.sum())
                w = wilson(c, n); cf = int(g[g.llego_limite == 0].correcto.sum())
                t1.append(dict(comun, semilla=str(int(s)), n=n, correctos=c, precision_pct=100 * c / n, ic_lo=w[0], ic_hi=w[1], tipo_ic="wilson",
                               al_limite_pct=100 * lim / n, terminaron=n - lim, correctos_terminaron=cf, tokens_medios=g.tokens.mean()))
                L.append(f"| {NOMBRES_OTRAS[k]} | {int(s)} | {n} | {c} | {100*c/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*lim/n:.1f} | {cf}/{n-lim} | {g.tokens.mean():.0f} |")
            if d.semilla.nunique() > 1:
                pp = d.groupby("id").correcto.mean(); ic = A2.ic_boot(pp.values); fin = d[d.llego_limite == 0]
                t1.append(dict(comun, semilla="0 1 2 3", n=len(d), correctos=int(d.correcto.sum()), precision_pct=100 * pp.mean(), ic_lo=ic[0], ic_hi=ic[1],
                               tipo_ic="bootstrap_problema", al_limite_pct=100 * d.llego_limite.mean(), terminaron=len(fin),
                               correctos_terminaron=int(fin.correcto.sum()), tokens_medios=d.tokens.mean()))
                L.append(f"| **{NOMBRES_OTRAS[k]}** | 0–3 | {len(d)} | {int(d.correcto.sum())} | **{100*pp.mean():.1f} ({ic[0]:.1f}–{ic[1]:.1f})** | {100*d.llego_limite.mean():.1f} | {int(fin.correcto.sum())}/{len(fin)} | {d.tokens.mean():.0f} |")
        filas = []
        for a, b_ in COMPARA_OTRAS:
            m = datos[a][["id", "semilla", "correcto", "llego_limite"]].merge(datos[b_][["id", "semilla", "correcto", "llego_limite"]],
                                                                              on=["id", "semilla"], suffixes=("_a", "_b"))
            b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum()); c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
            dif = m.correcto_a - m.correcto_b
            pp = dif.groupby(m.id).mean()
            filas.append((NOMBRES_OTRAS[a], NOMBRES_OTRAS[b_], len(m), b, c, 100 * dif.mean(), A2.ic_boot(pp.values), mcnemar_exacto(b, c)))
            N = len(m); cut = m[m.llego_limite_b == 1]; fin = m[m.llego_limite_b == 0]
            t3.append(dict(tarea=tarea, A=NOMBRES_OTRAS[a], B=NOMBRES_OTRAS[b_], parejas=N, dif_total_pts=100 * dif.mean(),
                           B_al_limite_parejas=len(cut), B_al_limite_contribucion_pts=100 * (cut.correcto_a.sum() - cut.correcto_b.sum()) / N,
                           B_termino_parejas=len(fin), B_termino_contribucion_pts=100 * (fin.correcto_a.sum() - fin.correcto_b.sum()) / N))
        ad = holm([f[7] for f in filas])
        t2 += [fila_mcnemar(f"{tarea} · ficha Qwen · semillas 0-3", f, pa) for f, pa in zip(filas, ad)]
        L += ["", "| A | B | Parejas | b | c | Dif. A−B pts (IC) | p exacto | p Holm |", "|---|---|---|---|---|---|---|---|"]
        for f, pa in zip(filas, ad):
            L.append(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
        L.append("")
    guardar("tabla_ficha_otras_4sem_corridas", t1)
    guardar("tabla_ficha_otras_4sem_mcnemar", t2)
    guardar("tabla_ficha_otras_4sem_dos_grupos", t3)
    open(f"{R}/RESUMEN_FICHA_OTRAS_4SEM.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
    main4()
    main_otras()
    main_otras4()
