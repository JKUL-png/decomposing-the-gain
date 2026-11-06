import sys, json, pandas as pd
for f in sys.argv[1:]:
    d = pd.read_csv(f); m = json.load(open(f + ".meta.json"))
    n, k, lim = len(d), int(d.correcto.sum()), int(d.llego_limite.sum())
    fin = d[d.llego_limite == 0]
    print(f.split("/")[-1], "| n", n, "| correctos", k, f"({100*k/n:.1f}%)", "| al límite", lim, f"({100*lim/n:.1f}%)",
          "| entre las que terminaron", f"{int(fin.correcto.sum())}/{len(fin)}", "| tokens medios", round(d.tokens.mean()), "| min", round(m["segundos"]/60, 1))
