"""Crea los subconjuntos FIJOS de 100 problemas de GSM8K (test) e IFEval (541), semilla 20261104.
Escribe datos/gsm8k_subset100_ids.txt/.jsonl y datos/ifeval_subset100_ids.txt/.jsonl. NO sobrescribe."""
import os, json, random
from datasets import load_dataset
D = "/workspace/decomposing-the-gain/datos"
SEMILLA = 20261104

def escribir(nombre, filas):
    ids_f, js_f = f"{D}/{nombre}_subset100_ids.txt", f"{D}/{nombre}_subset100.jsonl"
    if os.path.exists(ids_f) or os.path.exists(js_f):
        print(nombre, "ya existe; no lo toco"); return
    open(ids_f, "w").write("\n".join(r["id"] for r in filas) + "\n")
    with open(js_f, "w", encoding="utf-8") as f:
        for r in filas: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(nombre, len(filas), "problemas escritos")

g = load_dataset("openai/gsm8k", "main", split="test")
idx = sorted(random.Random(SEMILLA).sample(range(len(g)), 100))
escribir("gsm8k", [dict(id=f"gsm8k_test_{i}", problem=g[i]["question"], level="",
                        answer=g[i]["answer"].split("####")[-1].strip().replace(",", "")) for i in idx])

f = load_dataset("google/IFEval", split="train")
idx = sorted(random.Random(SEMILLA).sample(range(len(f)), 100))
escribir("ifeval", [dict(id=f"ifeval_{f[i]['key']}", problem=f[i]["prompt"], level="", answer="",
                         key=f[i]["key"], instruction_id_list=f[i]["instruction_id_list"], kwargs=f[i]["kwargs"]) for i in idx])
print("GSM8K total", len(g), "| IFEval total", len(f))
