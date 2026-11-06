"""Que fraccion de la ganancia del editado (p50c thinking vs orig thinking) recupera el original SIN thinking.
fraccion = (NT - OT) / (ED - OT), con NT = orig no-thinking, OT = orig thinking, ED = p50c thinking.
Se calcula la precision por problema (promedio de semillas disponibles de cada brazo), bootstrap por problema
(10,000 remuestras, MISMOS problemas en los 3 brazos, semilla fija). Regla estricta en no-thinking.
Salida: resultados/fraccion_ganancia.csv  (solo numeros)."""
import numpy as np, pandas as pd
import analisis_ronda2 as A2
from analisis_ronda2 import cargar, R

B, RNG = 10000, np.random.default_rng(20261105)

CASOS = [
    # nombre, OT, ED, NT, restringir semilla 0 en todos (comparacion con las mismas semillas)
    ("MATH-500 (100) · no-think muestreo MIT", ["linea_base_vllm"], ["r2_ed_think"], ["dia_nothink_mit100", "r2_orig_nothinkmit"], None),
    ("MATH-500 (100) · no-think 32k", ["linea_base_vllm"], ["r2_ed_think"], ["cero_edicion_no_thinking"], None),
    ("GSM8K sub.1 (100) · no-think muestreo MIT", ["r2_gsm8k_orig_think"], ["r2_gsm8k_ed_think"], ["r2_gsm8k_orig_nothink"], None),
    ("IFEval (100) · no-think muestreo MIT", ["r2_ifeval_orig_think"], ["r2_ifeval_ed_think"], ["r2_ifeval_orig_nothink"], None),
]


def pp(d):
    return d.groupby("id").correcto.mean()


def main():
    filas = []
    for nombre, ot, ed, nt, _ in CASOS:
        dO, dE, dN = cargar(ot), cargar(ed), cargar(nt)
        if dO is None or dE is None or dN is None:
            print("FALTA", nombre); continue
        sem = lambda d: " ".join(str(int(x)) for x in sorted(d.semilla.unique()))   # sin np.int64(...)
        o, e, n = pp(dO), pp(dE), pp(dN)
        ids = sorted(set(o.index) & set(e.index) & set(n.index))
        o, e, n = o[ids].values, e[ids].values, n[ids].values
        idx = RNG.integers(0, len(ids), (B, len(ids)))
        O, E, N = o[idx].mean(1), e[idx].mean(1), n[idx].mean(1)
        den = E - O
        ok = den > 0
        frac = (N - O)[ok] / den[ok]
        f0 = (n.mean() - o.mean()) / (e.mean() - o.mean())
        # intervalo sobre la diferencia en puntos (mas estable que el cociente)
        filas.append(dict(caso=nombre, problemas=len(ids), OT=100 * o.mean(), ED=100 * e.mean(), NT=100 * n.mean(),
                          ganancia_ED_pts=100 * (e.mean() - o.mean()),
                          ganancia_ED_ic_lo=100 * np.percentile(den, 2.5), ganancia_ED_ic_hi=100 * np.percentile(den, 97.5),
                          ganancia_NT_pts=100 * (n.mean() - o.mean()),
                          ganancia_NT_ic_lo=100 * np.percentile(N - O, 2.5), ganancia_NT_ic_hi=100 * np.percentile(N - O, 97.5),
                          fraccion=f0, fraccion_ic_lo=np.percentile(frac, 2.5), fraccion_ic_hi=np.percentile(frac, 97.5),
                          remuestras_den_no_positivo=int((~ok).sum()), semillas_OT=sem(dO), semillas_ED=sem(dE),
                          semillas_NT=sem(dN)))
    df = pd.DataFrame(filas)
    df.to_csv(f"{R}/fraccion_ganancia.csv", index=False, float_format="%.4f")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    for r in filas:
        print(f"{r['caso']}: n={r['problemas']} | OT {r['OT']:.1f} ED {r['ED']:.1f} NT {r['NT']:.1f} | "
              f"gan.ED {r['ganancia_ED_pts']:+.1f} ({r['ganancia_ED_ic_lo']:+.1f}…{r['ganancia_ED_ic_hi']:+.1f}) | "
              f"gan.NT {r['ganancia_NT_pts']:+.1f} ({r['ganancia_NT_ic_lo']:+.1f}…{r['ganancia_NT_ic_hi']:+.1f}) | "
              f"FRACCION {100*r['fraccion']:.0f}% ({100*r['fraccion_ic_lo']:.0f}–{100*r['fraccion_ic_hi']:.0f}%) | den<=0: {r['remuestras_den_no_positivo']} | {info_de(r)}")


def info_de(r):
    return f"OT sem [{r['semillas_OT']}], ED sem [{r['semillas_ED']}], NT sem [{r['semillas_NT']}]"


if __name__ == "__main__":
    main()
