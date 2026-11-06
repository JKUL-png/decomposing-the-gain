"""Exporta los 500 problemas completos de MATH-500 a datos/math500_full.jsonl y sus IDs a datos/math500_full_ids.txt.
NO toca los 100 fijos (math500_subset100_*). No sobrescribe. Verifica que los 100 fijos estén dentro de los 500."""
import json, os
from datasets import load_dataset

D = r"/workspace/decomposing-the-gain/datos"
ruta, ruta_ids = f"{D}\\math500_full.jsonl", f"{D}\\math500_full_ids.txt"
if os.path.exists(ruta) or os.path.exists(ruta_ids):
    print("Ya existe; no sobrescribo."); raise SystemExit
d = list(load_dataset("HuggingFaceH4/MATH-500", split="test"))
assert len(d) == 500 and len({r["unique_id"] for r in d}) == 500
fijos = [l.strip() for l in open(f"{D}\\math500_subset100_ids.txt", encoding="utf-8") if l.strip() and not l.startswith("#")]
assert set(fijos) <= {r["unique_id"] for r in d} and len(fijos) == 100
d.sort(key=lambda r: r["unique_id"])
with open(ruta, "w", encoding="utf-8", newline="\n") as f:
    for r in d:
        f.write(json.dumps({"id": r["unique_id"], "level": r["level"], "subject": r["subject"],
                            "problem": r["problem"], "answer": r["answer"]}, ensure_ascii=False) + "\n")
with open(ruta_ids, "w", encoding="utf-8", newline="\n") as f:
    f.write("# MATH-500 completo (500 IDs, orden alfabético)\n" + "\n".join(r["unique_id"] for r in d) + "\n")
from collections import Counter
print("ok: 500 problemas; por nivel:", dict(sorted(Counter(r["level"] for r in d).items())))
