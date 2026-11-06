"""Califica con math-verify (correr en WSL) las generaciones de cualquier brazo y rellena la columna 'correcto' del CSV.
Uso: python calificar_jsonl.py <salida.csv>   (lee <salida.csv>.jsonl)"""
import os, sys, json
os.environ["PROYECTO_RAIZ"] = "/workspace/decomposing-the-gain"
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
import pandas as pd
from comun_math import *

ruta = sys.argv[1]
oficial = {p["id"]: p["answer"] for p in cargar_problemas("math500_subset100_ids.txt")}
gen = {j["id"]: j["texto"] for j in map(json.loads, open(ruta + ".jsonl", encoding="utf-8"))}
d = pd.read_csv(ruta)
d["correcto"] = [int(es_correcta(gen[i], oficial[i])) for i in d["id"]]
d.to_csv(ruta, index=False)
print("calificado:", ruta, "| correctos:", int(d.correcto.sum()), "de", len(d))
