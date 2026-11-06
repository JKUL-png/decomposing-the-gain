"""Paired analysis of no-think (MIT sampling) vs. the baseline with 4 seeds (no GPU).

Same method as table 3 of analisis_dia.py, which only has seed 0 for this arm: same pairing, strict rule
and bootstrap by problem. Writes a NEW file and leaves tabla_dia_pareado_dos_grupos.csv untouched.
Seed 0 of this arm is dia_nothink_mit100; seeds 1-3 are r2_orig_nothinkmit.
Usage: .venv/Scripts/python.exe scripts/fig2_nothink_mit_4sem.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1] / "resultados"
RNG = np.random.default_rng(20261106)
B = 10000
COLS = ["id", "correcto", "llego_limite", "modo"]


def read(path, seed):
    d = pd.read_csv(path)[COLS]
    d["semilla"] = seed
    return d


base = pd.concat([read(R / "linea_base_vllm.csv", 0)] +
                 [read(R / f"linea_base_vllm_s{s}.csv", s) for s in (1, 2, 3)], ignore_index=True)
var = pd.concat([read(R / "dia_nothink_mit100_s0.csv", 0)] +
                [read(R / f"r2_orig_nothinkmit_s{s}.csv", s) for s in (1, 2, 3)], ignore_index=True)
assert set(var.modo) == {"no-thinking"}, set(var.modo)
# Strict rule: in no-thinking, a response that hit the limit counts as wrong.
var["correcto"] = ((var.correcto == 1) & (var.llego_limite == 0)).astype(int)

m = base.merge(var, on=["id", "semilla"], suffixes=("_b", "_v"))
assert len(m) == 400, len(m)
n = len(m)
dif = m.correcto_v - m.correcto_b
per_problem = dif.groupby(m.id).mean().to_numpy()
means = per_problem[RNG.integers(0, len(per_problem), (B, len(per_problem)))].mean(axis=1)
lo, hi = 100 * np.percentile(means, 2.5), 100 * np.percentile(means, 97.5)
looped, finished = m[m.llego_limite_b == 1], m[m.llego_limite_b == 0]

row = dict(
    variante="nothink_mit_4sem", semillas_comunes="0 1 2 3", parejas=n, dif_total_pts=100 * dif.mean(),
    dif_total_boot_lo=lo, dif_total_boot_hi=hi,
    antes_limite_parejas=len(looped), antes_limite_correctos_base=int(looped.correcto_b.sum()),
    antes_limite_correctos_variante=int(looped.correcto_v.sum()),
    antes_limite_corto_bucle=int((looped.llego_limite_v == 0).sum()),
    antes_limite_contribucion_pts=100 * (looped.correcto_v.sum() - looped.correcto_b.sum()) / n,
    ya_terminaban_parejas=len(finished), ya_terminaban_correctos_base=int(finished.correcto_b.sum()),
    ya_terminaban_correctos_variante=int(finished.correcto_v.sum()),
    ya_terminaban_perdidos=int(((finished.correcto_b == 1) & (finished.correcto_v == 0)).sum()),
    ya_terminaban_ganados=int(((finished.correcto_b == 0) & (finished.correcto_v == 1)).sum()),
    ya_terminaban_contribucion_pts=100 * (finished.correcto_v.sum() - finished.correcto_b.sum()) / n,
)

# Must agree with the tables already in the paper.
arms = pd.read_csv(R / "tabla_r2_math_brazos.csv").set_index("brazo")
assert abs(100 * m.correcto_v.mean() - arms.loc["orig · no-think muestreo MIT", "precision_pct"]) < 1e-9
assert abs(100 * m.correcto_b.mean() - arms.loc["orig · thinking MIT", "precision_pct"]) < 1e-9
frac = pd.read_csv(R / "fraccion_ganancia.csv").set_index("caso")
assert abs(row["dif_total_pts"] - frac.loc["MATH-500 (100) · no-think muestreo MIT", "ganancia_NT_pts"]) < 1e-9

pd.DataFrame([row]).to_csv(R / "tabla_fig2_nothink_mit_4sem.csv", index=False)
print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()})
