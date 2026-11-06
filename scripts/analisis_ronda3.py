"""Ronda 3 (sin GPU) -> resultados/RESUMEN_RONDA3.md. Solo numeros.
 1) GSM8K (subconjunto 1, subconjunto b y junto) e IFEval con 4 semillas: precision, McNemar pareado entre configuraciones.
 2) Detectar bucle y reintentar (A) / forzar respuesta (B) en MATH-500 y GSM8K: precision, tokens totales gastados, McNemar.
Regla principal: estricta (en no-thinking cuenta solo si NO llego al limite). Bootstrap por problema, semilla fija."""
import os, itertools
import numpy as np, pandas as pd
import analisis_ronda2 as A2
from analisis_ronda2 import wilson, cargar, ic_boot, mcnemar_exacto, holm, R, guardar, fila_mcnemar

T_BRAZOS, T_MCNEMAR, T_REINT, T_INTENTOS = [], [], [], []   # se escriben como CSV al final

G1 = {"p50c · thinking MIT": ["r2_gsm8k_ed_think"], "p50c · no-think muestreo MIT": ["r2_gsm8k_ed_nothink"],
      "orig · no-think muestreo MIT": ["r2_gsm8k_orig_nothink"], "orig · thinking MIT (solo semilla 0)": ["r2_gsm8k_orig_think"]}
G2 = {"p50c · thinking MIT": ["r3_gsm8kb_ed_think"], "p50c · no-think muestreo MIT": ["r3_gsm8kb_ed_nothink"],
      "orig · no-think muestreo MIT": ["r3_gsm8kb_orig_nothink"]}
IFE = {"p50c · thinking MIT": ["r2_ifeval_ed_think"], "p50c · no-think muestreo MIT": ["r2_ifeval_ed_nothink"],
       "orig · no-think muestreo MIT": ["r2_ifeval_orig_nothink"], "orig · thinking MIT (solo semilla 0)": ["r2_ifeval_orig_think"]}
ESPERADO = {}
for _g in (G1, G2, IFE):
    for _k, _p in _g.items():
        ESPERADO[_p[0]] = [0] if "solo semilla 0" in _k else [0, 1, 2, 3]
REINT = {"MATH-500 (100 fijos)": ("r3_reint_math", "linea_base_vllm", "r2_ed_think"),
         "GSM8K (subconjunto 1)": ("r3_reint_gsm8k", "r2_gsm8k_orig_think", "r2_gsm8k_ed_think")}


def fila_brazo(nombre, d, tabla):
    pp = d.groupby("id").correcto.mean(); ic = ic_boot(pp.values); fin = d[d.llego_limite == 0]
    T_BRAZOS.append(dict(tabla=tabla, brazo=nombre, semillas=" ".join(str(int(x)) for x in sorted(d.semilla.unique())),
                         muestras=len(d), problemas=d.id.nunique(), precision_pct=100 * pp.mean(), precision_boot_lo=ic[0],
                         precision_boot_hi=ic[1], al_limite_pct=100 * d.llego_limite.mean(), terminaron=len(fin),
                         correctos_terminaron=int(fin.correcto.sum()),
                         precision_terminaron_pct=100 * fin.correcto.mean() if len(fin) else np.nan, tokens_medios=d.tokens.mean()))
    fin_txt = f"{100*fin.correcto.mean():.1f} ({int(fin.correcto.sum())}/{len(fin)})" if len(fin) else "n/a"
    return (f"| {nombre} | {[int(x) for x in sorted(d.semilla.unique())]} | {len(d)} | {100*pp.mean():.1f} ({ic[0]:.1f}–{ic[1]:.1f}) | "
            f"{100*d.llego_limite.mean():.1f} | {fin_txt} | {d.tokens.mean():.0f} |")


def pares(arms, titulo, minimo=50):
    L = [f"**{titulo}** (A vs B; b = A acierta y B no; c = B acierta y A no)", "",
         "| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |", "|---|---|---|---|---|---|---|---|"]
    filas = []
    for a, b_ in itertools.combinations([n for n in arms if arms[n] is not None], 2):
        m = arms[a][["id", "semilla", "correcto"]].merge(arms[b_][["id", "semilla", "correcto"]], on=["id", "semilla"], suffixes=("_a", "_b"))
        if len(m) < minimo:
            continue
        b = int(((m.correcto_a == 1) & (m.correcto_b == 0)).sum()); c = int(((m.correcto_a == 0) & (m.correcto_b == 1)).sum())
        pp = (m.correcto_a - m.correcto_b).groupby(m.id).mean()
        filas.append((a, b_, len(m), b, c, 100 * pp.mean(), ic_boot(pp.values), mcnemar_exacto(b, c)))
    ad = holm([f[7] for f in filas]) if filas else []
    for f, pa in zip(filas, ad):
        L.append(f"| {f[0]} | {f[1]} | {f[2]} | {f[3]} | {f[4]} | {f[5]:+.1f} ({f[6][0]:+.1f}…{f[6][1]:+.1f}) | {f[7]:.2g} | {pa:.2g} |")
        T_MCNEMAR.append(fila_mcnemar(titulo, f, pa))
    return L + [""]


CAB = ["| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |",
       "|---|---|---|---|---|---|---|"]


def bloque(titulo, grupos):
    d = {k: cargar(v) for k, v in grupos.items()}
    L = [f"### {titulo}", ""] + CAB
    for k, x in d.items():
        L.append(fila_brazo(k, x, titulo) if x is not None else f"| {k} | FALTA | | | | | |")
    L.append("")
    return d, L


def main():
    L = ["# Resumen ronda 3 (solo números, sin interpretar)", "",
         "**Regla principal: estricta** (en no-thinking cuenta solo si NO llegó al límite de tokens). Modelos: orig = Qwen3.5-0.8B; p50c = edición del MIT (hash verificado). "
         "Thinking MIT = temp 0.6, top_p 0.95, top_k 20, presence 1.5, 32,768. No-think muestreo MIT = temp 0.7, top_p 0.8, top_k 20, presence 1.5, 8,192. "
         "IC por corrida: Wilson 95%; IC agrupado y de diferencias: bootstrap por problema (10000, semilla fija); McNemar exacto bilateral sobre parejas problema+semilla; "
         "Holm dentro de cada tabla (las semillas del mismo problema no son independientes).", ""]
    # ---------- 1 GSM8K / IFEval
    L += ["## 1. GSM8K e IFEval con 4 semillas (0–3)", ""]
    d1, l = bloque("GSM8K subconjunto 1 (100 problemas)", G1); L += l
    d2, l = bloque("GSM8K subconjunto b (100 problemas distintos, semilla 20261105)", G2); L += l
    juntos = {}
    for k in G2:
        a, b = d1.get(k), d2.get(k)
        if a is not None and b is not None:
            juntos[k] = pd.concat([a, b], ignore_index=True)
    L += ["### GSM8K subconjuntos 1 + b juntos (200 problemas)", ""] + CAB
    for k, x in juntos.items():
        L.append(fila_brazo(k, x, "GSM8K subconjuntos 1 + b juntos (200 problemas)"))
    L.append("")
    di, l = bloque("IFEval (100 problemas, estricto a nivel de prompt)", IFE); L += l
    L += ["## 2. McNemar pareado", ""]
    L += pares(d1, "GSM8K subconjunto 1", 50)
    L += pares(d2, "GSM8K subconjunto b", 50)
    L += pares(juntos, "GSM8K 1 + b juntos", 50)
    L += pares(di, "IFEval", 50)
    # ---------- 3 reintento / forzar
    L += ["## 3. Detectar el bucle: reintentar (A) y forzar la respuesta (B), modelo original en thinking, semilla 0", "",
          "Detector: ventana de 300 caracteres del final repetida ≥3 veces en los últimos 6,000 (revisado cada 512 tokens). A: hasta 3 intentos (semilla+1000·k); "
          "B: al detectar el bucle en el intento 1 se recorta el texto en la primera copia, se cierra el pensamiento y el modelo contesta (máx. 4,096 tokens; si llega al tope sin cerrar cuenta como incorrecta). "
          "'Tokens totales' incluyen los intentos descartados. 'Terminaron' = la generación aceptada terminó sola (en B, los forzados cuentan aparte).", ""]
    ref_prom = {}
    for nombre, (pref, base, ed) in REINT.items():
        a, b = cargar(f"{pref}_A"), cargar(f"{pref}_B"); o, e = cargar(base), cargar(ed)
        if o is not None: o = o[o.semilla == 0]
        e0 = e[e.semilla == 0] if e is not None else None
        L += [f"### {nombre}", "",
              "| Brazo | n | Correctos | Precisión % (Wilson) | Terminaron % | Forzados | Forzados que llegaron al tope de 4,096 sin cerrar (incorrectos) | Intentos medios | Tokens totales por problema (media) | Tokens totales (suma) |", "|---|---|---|---|---|---|---|---|---|---|"]
        brazos = {"orig · thinking MIT (referencia, 1 intento)": o, "A · reintento (hasta 3)": a, "B · forzar respuesta": b,
                  "p50c · thinking MIT (misma semilla 0)": e0}
        for k, x in brazos.items():
            if x is None:
                L.append(f"| {k} | FALTA | | | | | | | | |"); continue
            n, kk = len(x), int(x.correcto.sum()); w = wilson(kk, n)
            forz = int(x["forzado"].sum()) if "forzado" in x.columns else 0
            nocerro = int(x["forzada_no_cerro"].sum()) if "forzada_no_cerro" in x.columns else 0
            intent = f"{x['intentos'].mean():.2f}" if "intentos" in x.columns else "1"
            L.append(f"| {k} | {n} | {kk} | {100*kk/n:.1f} ({w[0]:.1f}–{w[1]:.1f}) | {100*(1-x.llego_limite.mean()):.1f} | {forz} | {nocerro} | {intent} | {x.tokens.mean():.0f} | {int(x.tokens.sum())} |")
            T_REINT.append(dict(tarea=nombre, brazo=k, semilla=0, n=n, correctos=kk, precision_pct=100 * kk / n,
                                precision_wilson_lo=w[0], precision_wilson_hi=w[1], terminaron_pct=100 * (1 - x.llego_limite.mean()),
                                forzados=forz, forzados_tope_sin_cerrar=nocerro,
                                intentos_medios=x["intentos"].mean() if "intentos" in x.columns else 1.0,
                                tokens_totales_por_problema=x.tokens.mean(), tokens_totales_suma=int(x.tokens.sum())))
        L.append("")
        if e is not None and nombre.startswith("MATH"):
            L += [f"Referencia p50c thinking, 4 semillas: precisión {100*e.groupby('id').correcto.mean().mean():.1f}%, tokens medios {e.tokens.mean():.0f}.", ""]
        L += pares({"A · reintento": a, "B · forzar": b, "orig · thinking (ref.)": o, "p50c · thinking": e0}, f"McNemar {nombre} (semilla 0)", 50)
        ip = f"{R}/{pref}_intentos_s0.csv"
        if os.path.exists(ip):
            it = pd.read_csv(ip); por = it.groupby("id").agg(n=("intento", "max"), loops=("corte", lambda s: int((s == "loop").sum())))
            L += [f"Intentos por problema: 1 intento = {int((por.n==1).sum())}, 2 = {int((por.n==2).sum())}, 3 = {int((por.n==3).sum())}; "
                  f"problemas con ≥1 bucle detectado = {int((por.loops>=1).sum())}; intentos abortados por bucle = {int(por.loops.sum())}.", ""]
            T_INTENTOS.append(dict(tarea=nombre, semilla=0, problemas_1_intento=int((por.n == 1).sum()),
                                   problemas_2_intentos=int((por.n == 2).sum()), problemas_3_intentos=int((por.n == 3).sum()),
                                   problemas_con_bucle_detectado=int((por.loops >= 1).sum()), intentos_abortados_por_bucle=int(por.loops.sum())))
    falt = [f"{pref} semillas {sorted(set(ss) - set(A2.rutas(pref)))}" for pref, ss in ESPERADO.items() if set(ss) - set(A2.rutas(pref))]
    for pref, _, _ in REINT.values():
        for v in ("A", "B"):
            if not A2.rutas(f"{pref}_{v}"):
                falt.append(f"{pref}_{v}")
    L += ["Corridas FALTANTES: " + ("; ".join(falt) if falt else "ninguna"), ""]
    open(f"{R}/RESUMEN_RONDA3.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    guardar("tabla_r3_brazos", T_BRAZOS); guardar("tabla_r3_mcnemar", T_MCNEMAR)
    guardar("tabla_r3_reintento", T_REINT); guardar("tabla_r3_intentos", T_INTENTOS)
    print("RESUMEN_RONDA3.md escrito")


if __name__ == "__main__":
    main()
