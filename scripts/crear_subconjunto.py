"""Crea el subconjunto FIJO de 100 problemas de MATH-500 (estratificado por nivel).
Semilla fija. NO volver a correr salvo para verificar: el archivo de IDs es la fuente de verdad."""
import random, hashlib, csv, os
from collections import defaultdict
from datasets import load_dataset

SEMILLA, K = 20261103, 100
d = load_dataset("HuggingFaceH4/MATH-500", split="test")
por_nivel = defaultdict(list)
for r in d:
    por_nivel[r["level"]].append(r["unique_id"])

# cuota por nivel = método del mayor resto (suma exacta = K)
tot = len(d)
cuota = {l: K * len(v) / tot for l, v in por_nivel.items()}
base = {l: int(c) for l, c in cuota.items()}
faltan = K - sum(base.values())
for l in sorted(cuota, key=lambda l: (-(cuota[l] - base[l]), l))[:faltan]:
    base[l] += 1

rng = random.Random(SEMILLA)
elegidos = []
for l in sorted(por_nivel):
    elegidos += rng.sample(sorted(por_nivel[l]), base[l])
elegidos.sort()

os.makedirs(r"/workspace/decomposing-the-gain/datos", exist_ok=True)
ruta = r"/workspace/decomposing-the-gain/datos/math500_subset100_ids.txt"
if os.path.exists(ruta):
    previo = open(ruta, encoding="utf-8").read().split("#")[-1].split()
    assert previo == elegidos, "¡El subconjunto cambió! No sobrescribo."
    print("Verificado: coincide con el archivo existente."); raise SystemExit
meta = {r["unique_id"]: r for r in d}
with open(ruta, "w", encoding="utf-8", newline="\n") as f:
    f.write(f"# Subconjunto fijo de 100 problemas de HuggingFaceH4/MATH-500 (test, 500)\n"
            f"# estratificado por nivel, semilla={SEMILLA}, cuotas={dict(sorted(base.items()))}\n"
            f"# sha256 de la lista: {hashlib.sha256(chr(10).join(elegidos).encode()).hexdigest()[:16]}\n#\n")
    f.write("\n".join(elegidos) + "\n")
print("cuotas por nivel:", dict(sorted(base.items())), "| total:", len(elegidos))
