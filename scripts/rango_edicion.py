"""Rango de ΔW (SVD) de p50c y del placebo, en las dos matrices editadas. Solo CPU, en WSL. No toca la GPU.
ΔW = pesos bf16 finales - pesos bf16 base (en float64). El placebo se construyó como rango 1 exacto y luego se
redondeó a bf16, así que sirve de referencia: muestra cuánto "ruido de rango" agrega solo el redondeo.
Escribe resultados/ediciones_rango.csv y resultados/ediciones_valores_singulares.csv."""
import os, sys, csv, numpy as np
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts/mit_codigo")
import st_numpy as S
HOME = os.path.expanduser("~"); FILE = "model.safetensors-00001-of-00001.safetensors"
R = "/workspace/decomposing-the-gain/resultados"
NOMBRES = ["model.language_model.layers.15.mlp.down_proj.weight", "model.language_model.layers.19.mlp.down_proj.weight"]
MODELOS = {"p50c_MIT": "Qwen3.5-0.8B-p50c", "placebo": "Qwen3.5-0.8B-placebo50"}

def f64(bits): return S.bf16_to_f32(bits).astype(np.float64)
def rango_energia(e, frac): return int(np.searchsorted(np.cumsum(e), frac) + 1)

base = S.load(f"{HOME}/modelos/Qwen3.5-0.8B/{FILE}", NOMBRES)
filas, sing = [], []
for modelo, carpeta in MODELOS.items():
    ed = S.load(f"{HOME}/modelos/{carpeta}/{FILE}", NOMBRES)
    for n in NOMBRES:
        W, E = f64(base[n][1]), f64(ed[n][1]); D = E - W
        cols = np.where(np.abs(D).sum(0) > 0)[0]
        U, s, Vt = np.linalg.svd(D, full_matrices=False)
        tol = s[0] * max(D.shape) * np.finfo(np.float64).eps      # tolerancia estándar de matrix_rank
        e = s**2 / (s**2).sum()
        # ¿La aproximación de rango 1, redondeada a bf16, reproduce los pesos editados?
        D1 = s[0] * np.outer(U[:, 0], Vt[0])
        r1 = f64(S.bf16_bits((W + D1).astype(np.float32)).reshape(W.shape))
        sub = np.ix_(np.arange(W.shape[0]), cols)
        filas.append(dict(
            tensor=n, modelo=modelo, forma=f"{D.shape[0]}x{D.shape[1]}", columnas=len(cols),
            norma_dW=round(float(np.linalg.norm(D)), 5),
            rango_numerico=int((s > tol).sum()), tolerancia=f"{tol:.3e}",
            sv1=round(float(s[0]), 6), sv2=round(float(s[1]), 6), sv3=round(float(s[2]), 6),
            sv2_sobre_sv1=round(float(s[1] / s[0]), 6),
            energia_sv1=round(float(e[0]), 6),
            rango_99=rango_energia(e, 0.99), rango_999=rango_energia(e, 0.999),
            residuo_rango1_rel=round(float(np.sqrt(max(1 - e[0], 0))), 6),
            pct_entradas_iguales_rango1_bf16=round(float((r1[sub] == E[sub]).mean() * 100), 3)))
        for i, v in enumerate(s[:70]):
            sing.append(dict(tensor=n, modelo=modelo, indice=i + 1, valor_singular=f"{v:.6e}"))

for nombre, datos in (("ediciones_rango.csv", filas), ("ediciones_valores_singulares.csv", sing)):
    with open(f"{R}/{nombre}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=datos[0].keys()); w.writeheader(); w.writerows(datos)
for r in filas: print({k: v for k, v in r.items() if k != "tensor"}, r["tensor"].split(".")[3])
