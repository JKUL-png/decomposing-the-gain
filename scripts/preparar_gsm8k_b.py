"""Segundo subconjunto FIJO de 100 problemas de GSM8K (test), semilla 20261105, SIN solaparse con el primero
(datos/gsm8k_subset100_ids.txt). Escribe datos/gsm8k_subset100b_ids.txt/.jsonl. NO sobrescribe. Nunca regenerar."""
import os, json, random
from datasets import load_dataset
D = "/workspace/decomposing-the-gain/datos"; SEMILLA = 20261105
ids_f, js_f = f"{D}/gsm8k_subset100b_ids.txt", f"{D}/gsm8k_subset100b.jsonl"
if os.path.exists(ids_f) or os.path.exists(js_f):
    print("ya existe; no lo toco"); raise SystemExit
usados = {l.strip() for l in open(f"{D}/gsm8k_subset100_ids.txt") if l.strip()}
g = load_dataset("openai/gsm8k", "main", split="test")
libres = [i for i in range(len(g)) if f"gsm8k_test_{i}" not in usados]
idx = sorted(random.Random(SEMILLA).sample(libres, 100))
filas = [dict(id=f"gsm8k_test_{i}", problem=g[i]["question"], level="", answer=g[i]["answer"].split("####")[-1].strip().replace(",", "")) for i in idx]
open(ids_f, "w").write("\n".join(r["id"] for r in filas) + "\n")
with open(js_f, "w", encoding="utf-8") as f:
    for r in filas: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("escritos", len(filas), "| libres", len(libres), "| solapamiento con el primero:", len({r["id"] for r in filas} & usados))
