"""Crea (en WSL, CPU) dos modelos: p50c (la edición del MIT, reconstruida con hash verificado) y un PLACEBO.
Placebo: mismos 2 tensores (layers 15 y 19 mlp.down_proj), mismas columnas tocadas (64 por tensor), rango 1
(a b^T con a y b aleatorios), y la MISMA norma ||ΔW||_F que la edición real. Semilla fija. No sobrescribe.
Escribe resultados/ediciones_norma.csv con ||ΔW||_F y ||ΔW||/||W|| medidos sobre los pesos bf16 finales."""
import os, sys, json, shutil, csv, numpy as np
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts/mit_codigo")
import st_numpy as S, apply_edit as A
HOME = os.path.expanduser("~"); BASE_DIR = f"{HOME}/modelos/Qwen3.5-0.8B"
FILE = "model.safetensors-00001-of-00001.safetensors"
R = "/workspace/decomposing-the-gain"; SEMILLA = 20261104
NOMBRES = ["model.language_model.layers.15.mlp.down_proj.weight", "model.language_model.layers.19.mlp.down_proj.weight"]

def preparar_dir(dst):
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(BASE_DIR):
        if f != FILE and os.path.isfile(f"{BASE_DIR}/{f}"): shutil.copyfile(f"{BASE_DIR}/{f}", f"{dst}/{f}")

def f32(bits): return S.bf16_to_f32(bits).astype(np.float64)

def main():
    d_p50, d_pla = f"{HOME}/modelos/Qwen3.5-0.8B-p50c", f"{HOME}/modelos/Qwen3.5-0.8B-placebo50"
    if os.path.exists(f"{d_p50}/{FILE}") or os.path.exists(f"{d_pla}/{FILE}"):
        print("Ya existen; no sobrescribo"); return
    base = S.load(f"{BASE_DIR}/{FILE}")
    # 1) p50c con el código del MIT (verifica hashes)
    preparar_dir(d_p50)
    A.main(f"{BASE_DIR}/{FILE}", f"{R}/datos/mit_exp8/edits/p50c", f"{d_p50}/{FILE}")
    ed = S.load(f"{d_p50}/{FILE}")
    # 2) placebo
    rng = np.random.default_rng(SEMILLA)
    pla = {k: v for k, v in base.items()}
    filas = []
    for n in NOMBRES:
        W = f32(base[n][1]); E = f32(ed[n][1]); D = E - W
        cols = np.where(np.abs(D).sum(0) > 0)[0]; objetivo = np.linalg.norm(D)
        a = rng.standard_normal(W.shape[0]); a /= np.linalg.norm(a)
        b = rng.standard_normal(len(cols)); b /= np.linalg.norm(b)
        escala = objetivo
        for _ in range(6):   # el redondeo a bf16 cambia un poco la norma: se ajusta la escala
            Wp = W.copy(); Wp[:, cols] += escala * np.outer(a, b)
            bits = S.bf16_bits(Wp.astype(np.float32)).reshape(base[n][1].shape)
            Dp = f32(bits) - W; escala *= objetivo / np.linalg.norm(Dp)
        pla[n] = ("BF16", bits)
        nW = np.linalg.norm(W)
        filas.append(dict(tensor=n, modelo="p50c_MIT", norma_dW=round(objetivo, 5), norma_W=round(nW, 4),
                          cambio_relativo=round(objetivo / nW, 6), columnas=len(cols)))
        filas.append(dict(tensor=n, modelo="placebo", norma_dW=round(np.linalg.norm(Dp), 5), norma_W=round(nW, 4),
                          cambio_relativo=round(np.linalg.norm(Dp) / nW, 6), columnas=int((np.abs(Dp).sum(0) > 0).sum())))
    preparar_dir(d_pla); S.save(f"{d_pla}/{FILE}", pla, {"format": "pt"})
    with open(f"{R}/resultados/ediciones_norma.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)
    for r in filas: print(r["modelo"], r["tensor"].split(".")[3], "||dW||", r["norma_dW"], "rel", r["cambio_relativo"], "cols", r["columnas"])
    # comprobación: el modelo guardado difiere de la base solo en 2 tensores
    for d in (d_p50, d_pla):
        t = S.load(f"{d}/{FILE}")
        dif = [k for k in base if not np.array_equal(base[k][1], t[k][1])]
        print(os.path.basename(d), "tensores distintos de la base:", len(dif))

if __name__ == "__main__": main()
