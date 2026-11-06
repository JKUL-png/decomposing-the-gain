"""Calibra (CPU) un detector de bucles sobre textos ya generados: ¿en qué punto saltaría y se equivoca con los que sí terminan?
Detector: cada PASO caracteres, mira la ventana final de W caracteres; si esa ventana aparece >= K veces en los últimos L caracteres => bucle."""
import sys, json, csv, glob
R = "/workspace/decomposing-the-gain/resultados"
W, K, L, PASO = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), 1500
def dispara(t):
    for n in range(L, len(t) + PASO, PASO):
        n = min(n, len(t)); cola = t[max(0, n - L):n]
        if len(cola) >= W and cola.count(cola[-W:]) >= K: return n
        if n == len(t): break
    return None
def cargar(pref, semillas):
    out = []
    for s in semillas:
        f = f"{R}/{pref}_s{s}.csv"
        import os
        if not os.path.exists(f): f = f"{R}/{pref}.csv"
        import os
        if not os.path.exists(f): continue
        filas = {r["id"]: r for r in csv.DictReader(open(f, encoding="utf-8"))}
        j = f + ".jsonl" if os.path.exists(f + ".jsonl") else f.replace(".csv", ".jsonl")
        for l in open(j, encoding="utf-8"):
            d = json.loads(l); r = filas[d["id"]]; out.append((d["texto"], int(r["tokens"]), int(r["llego_limite"]), int(r["correcto"])))
    return out
FILAS = []   # se exportan a resultados/calibracion_detector_bucle.csv (una fila por conjunto y parámetros)
for nombre, pref, sem in (("MATH original thinking", "linea_base_vllm", [0,1,2,3]), ("GSM8K original thinking", "r2_gsm8k_orig_think", [0]),
                          ("MATH p50c thinking", "r2_ed_think", [0,1,2,3])):
    datos = cargar(pref, sem)
    if not datos: print(nombre, "sin datos"); continue
    cortadas = [d for d in datos if d[2]]; ok = [d for d in datos if not d[2]]
    dc = [(dispara(t), tok, len(t)) for t, tok, _, _ in cortadas]; do = [dispara(t) for t, _, _, _ in ok]
    det = [(n / ln * tok) for n, tok, ln in dc if n]      # tokens aproximados al disparar
    det.sort()
    FILAS.append(dict(conjunto=nombre, prefijo=pref, semillas=" ".join(map(str, sem)), ventana_W=W, repeticiones_K=K,
                      ultimos_L=L, paso_chars=PASO, respuestas=len(datos), llegaron_limite=len(cortadas),
                      detectadas=sum(1 for n, _, _ in dc if n), terminaron=len(ok), falsos_positivos=sum(1 for n in do if n),
                      tokens_al_disparar_mediana=round(det[len(det)//2]) if det else None,
                      tokens_al_disparar_p90=round(det[int(len(det)*0.9)]) if det else None))
    print(f"{nombre}: n={len(datos)} | cortadas={len(cortadas)} detectadas={sum(1 for n,_,_ in dc if n)} | terminaron={len(ok)} FALSOS positivos={sum(1 for n in do if n)} | "
          f"tokens al disparar (cortadas): mediana={det[len(det)//2]:.0f} p90={det[int(len(det)*0.9)]:.0f}" if det else f"{nombre}: nada detectado")
salida = f"{R}/calibracion_detector_bucle.csv"
with open(salida, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(FILAS[0])); w.writeheader(); w.writerows(FILAS)
print("escrito", salida)
