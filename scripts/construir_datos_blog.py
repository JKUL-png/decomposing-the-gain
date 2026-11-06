"""Construye los datos del blog desde resultados/ y datos/. Ningún número se escribe a mano.

Salidas:
  resultados/blog_bucles_semilla0.csv   una fila por problema de MATH-500 (semilla 0): bucle del original y resultado de los 3 brazos
  resultados/blog_ejemplos_bucle.csv    los ejemplos elegidos y la regla que cumple cada uno
  docs/data/data.js                     window.BLOG = números de las figuras + ejemplos del reproductor
  docs/index.html                       docs/src/index.template.html con {{clave}} reemplazado

Se detiene con error si un número no coincide entre tablas o no aparece en paper/draft.md.
Uso, desde la raíz del proyecto: python scripts/construir_datos_blog.py [--preview archivo.html]
"""
import base64, csv, json, re, sys
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
RES, DATOS, BLOG = RAIZ / "resultados", RAIZ / "datos", RAIZ / "docs"
ARMS = {"original": "linea_base_vllm", "edited": "r2_ed_think_s0", "nothink": "cero_edicion_no_thinking"}
LIMITE = 32768
HEAD, PRE, TAIL, CORTO = 900, 300, 700, 2400   # caracteres que se muestran; el resto se marca como omitido
MIN_CICLO = 300
EJEMPLOS = [  # legibles, elegidos a mano entre los que cumplen la regla "both_fixed" (se comprueba abajo)
    ("test/algebra/2789.json", "both_fixed"),
    ("test/algebra/305.json", "both_fixed"),
    ("test/number_theory/515.json", "both_fixed"),
]


def tabla(nombre):
    with open(RES / nombre, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def una(filas, **filtro):
    r = [x for x in filas if all(x[k] == v for k, v in filtro.items())]
    if len(r) != 1:
        raise SystemExit(f"Se esperaba 1 fila para {filtro}, hay {len(r)}")
    return r[0]


def num(x):
    return round(float(x), 6)


def f1(x, signo=False):
    """1 decimal; las mitades exactas redondean al par, igual que el paper."""
    d = Decimal(str(round(float(x), 6))).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN)
    return (f"{d:+}" if signo else f"{d}").replace("-", "−")


def si(x):
    return str(x).strip().lower() in ("1", "1.0", "true")


def respuestas(pref):
    filas = {r["id"]: r for r in tabla(f"{pref}.csv")}
    textos = {}
    with open(RES / f"{pref}.csv.jsonl", encoding="utf-8") as f:
        for linea in f:
            d = json.loads(linea)
            textos[d["id"]] = d["texto"]
    if set(filas) != set(textos) or len(filas) != 100:
        raise SystemExit(f"{pref}: filas y textos no coinciden")
    return filas, textos


def bucle(t):
    """Ciclo exacto al final del texto: periodo más corto repetido 3 veces, extendido hacia atrás.
    Debe cubrir al menos MIN_CICLO caracteres (la ventana del detector), para no contar finales con un carácter repetido."""
    for p in range(1, min(6000, len(t) // 3)):
        if t[-p:] == t[-2 * p:-p] == t[-3 * p:-2 * p]:
            i = len(t) - p - 1
            while i >= 0 and t[i] == t[i + p]:
                i -= 1
            inicio = i + 1
            if len(t) - inicio < MIN_CICLO:
                continue
            salto = t.find("\n", inicio, inicio + p)     # que cada copia empiece en una línea nueva
            if salto != -1:
                inicio = salto + 1
            return dict(start=inicio, period=p, copies=(len(t) - inicio) // p, unit=t[inicio:inicio + p])
    return None


def caja(t):
    """Último \\boxed{...} después de </think>, con llaves balanceadas."""
    t = t.split("</think>")[-1]
    i = t.rfind("\\boxed{")
    if i < 0:
        return None
    j, nivel = i + 7, 1
    while j < len(t) and nivel:
        nivel += {"{": 1, "}": -1}.get(t[j], 0)
        j += 1
    return t[i + 7:j - 1] if nivel == 0 else None


def brazo(fila, texto):
    b = dict(tokens=int(fila["tokens"]), limit=si(fila["llego_limite"]), correct=si(fila["correcto"]), chars=len(texto),
             answer=None if si(fila["llego_limite"]) else caja(texto), loop=None)
    lp = bucle(texto) if b["limit"] else None
    if lp and lp["copies"] >= 3:
        b["loop"] = lp
        b["head"] = texto[:min(HEAD, lp["start"])]
        b["pre"] = texto[max(len(b["head"]), lp["start"] - PRE):lp["start"]]
        b["tail"] = ""
    elif len(texto) <= CORTO:
        b.update(head=texto, pre="", tail="")
    else:
        b.update(head=texto[:HEAD], pre="", tail=texto[-TAIL:])
    return b


def categoria(o, e, n):
    if not (si(o["llego_limite"]) and not si(o["correcto"])):
        return "other"
    e_ok = si(e["correcto"]) and not si(e["llego_limite"])
    n_ok = si(n["correcto"]) and not si(n["llego_limite"])
    if e_ok and n_ok:
        return "both_fixed"
    if si(e["llego_limite"]) and n_ok:
        return "edit_still_loops"
    if e_ok and not si(n["llego_limite"]) and not si(n["correcto"]):
        return "nothink_wrong"
    return "other"


def ejemplos():
    r = {k: respuestas(p) for k, p in ARMS.items()}
    problemas = {}
    with open(DATOS / "math500_subset100.jsonl", encoding="utf-8") as f:
        for linea in f:
            d = json.loads(linea)
            problemas[d["id"]] = d
    filas = []
    for i, p in problemas.items():
        o, e, n = (r[k][0][i] for k in ARMS)
        lo = bucle(r["original"][1][i]) if si(o["llego_limite"]) else None
        le = bucle(r["edited"][1][i]) if si(e["llego_limite"]) else None
        filas.append(dict(id=i, nivel=p["level"], materia=p["subject"], categoria=categoria(o, e, n),
                          orig_limite=int(si(o["llego_limite"])), orig_periodo_chars=lo["period"] if lo else "",
                          orig_inicio_char=lo["start"] if lo else "", orig_copias=lo["copies"] if lo else "",
                          orig_chars=len(r["original"][1][i]), orig_tokens=o["tokens"], orig_correcto=int(si(o["correcto"])),
                          ed_limite=int(si(e["llego_limite"])), ed_periodo_chars=le["period"] if le else "",
                          ed_tokens=e["tokens"], ed_correcto=int(si(e["correcto"])),
                          nt_limite=int(si(n["llego_limite"])), nt_tokens=n["tokens"], nt_correcto=int(si(n["correcto"]))))
    with open(RES / "blog_bucles_semilla0.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)

    def primero(cat, clave):
        c = [x for x in filas if x["categoria"] == cat and x["orig_periodo_chars"] != "" and clave(x) is not None]
        if not c:
            raise SystemExit(f"Sin candidatos para {cat}")
        return min(c, key=lambda x: (x["nivel"], clave(x), x["id"]))["id"]

    elegidos = list(EJEMPLOS)
    # Los dos casos de fallo salen por regla, no a mano: nivel más bajo y ciclo más corto.
    elegidos.append((primero("edit_still_loops", lambda x: x["orig_periodo_chars"]), "edit_still_loops"))
    elegidos.append((primero("nothink_wrong", lambda x: x["orig_periodo_chars"]), "nothink_wrong"))
    por_id = {x["id"]: x for x in filas}
    salida = []
    for i, cat in elegidos:
        if por_id[i]["categoria"] != cat:
            raise SystemExit(f"{i} no cumple la regla {cat}")
        p = problemas[i]
        salida.append(dict(id=i, category=cat, level=p["level"], subject=p["subject"], problem=p["problem"], gold=p["answer"],
                           arms={k: brazo(r[k][0][i], r[k][1][i]) for k in ARMS}))
    with open(RES / "blog_ejemplos_bucle.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "regla", "seleccion"])
        for n_, (i, cat) in enumerate(elegidos):
            w.writerow([i, cat, "a mano por legibilidad" if n_ < len(EJEMPLOS) else "nivel más bajo, luego ciclo más corto"])
    cuenta = {c: sum(x["categoria"] == c for x in filas) for c in ("both_fixed", "edit_still_loops", "nothink_wrong")}
    cuenta.update(problems=len(filas), orig_limit=sum(x["orig_limite"] for x in filas),
                  orig_exact_cycle=sum(x["orig_periodo_chars"] != "" for x in filas))
    return salida, cuenta


MODOS = [("no-think muestreo MIT", "nt_mit", "no-think, MIT sampling"), ("no-think 32k", "nt_32k", "no-think, 32k"), ("ficha Qwen", "card", "model-card config"),
         ("rep 1.1", "penalty", "repetition_penalty 1.1"), ("rep 1.05", "penalty", "repetition_penalty 1.05"), ("presence 0", "penalty", "presence_penalty 0"),
         ("presence 2", "penalty", "presence_penalty 2.0"), ("thinking MIT", "thinking", "thinking")]
MODELOS = {"orig": "unedited", "p50c": "p50c", "placebo": "placebo"}


def etiqueta(brazo):
    """Mismas etiquetas que las tablas del paper."""
    m, _, resto = brazo.partition(" · ")
    for clave, modo, texto in MODOS:
        if clave in resto:
            return dict(model=m, mode=modo, label=f"{MODELOS[m]} · {texto}")
    raise SystemExit(f"Brazo sin etiqueta: {brazo}")


def figuras():
    m = tabla("tabla_r2_math_brazos.csv"); card = tabla("tabla_ficha_4sem_corridas.csv"); otras = tabla("tabla_ficha_otras_4sem_corridas.csv")
    r3 = tabla("tabla_r3_brazos.csv"); mc = tabla("tabla_r2_mcnemar.csv"); mc4 = tabla("tabla_ficha_4sem_mcnemar.csv"); mco = tabla("tabla_ficha_otras_4sem_mcnemar.csv")
    mc3 = tabla("tabla_r3_mcnemar.csv"); rep = una(tabla("tabla_dia_promedios.csv"), configuracion="cero_edicion_rep110")
    reint = tabla("tabla_r3_reintento.csv"); frac = tabla("fraccion_ganancia.csv")

    def p(r, lo="precision_boot_lo", hi="precision_boot_hi", sem="semillas"):
        return dict(etiqueta(r["brazo"]), acc=num(r["precision_pct"]), lo=num(r[lo]), hi=num(r[hi]), limit=num(r["al_limite_pct"]), seeds=len(r[sem].split()))

    f1_ = [p(r) for r in m]
    for r, x in zip(m, f1_):
        if r["brazo"] == "orig · rep 1.1 (thinking)":
            if abs(x["acc"] - num(rep["precision_pct"])) > 1e-6:
                raise SystemExit("rep 1.1: las tablas no coinciden")
            x["lo"], x["hi"] = num(rep["precision_boot_lo"]), num(rep["precision_boot_hi"])
    c4 = [r for r in card if r["semilla"] == "0 1 2 3" and "temp 1.0" in r["brazo"]]
    f1_ += [p(r, "ic_lo", "ic_hi", "semilla") for r in c4]

    NOMBRE2 = {"cero_edicion_no_thinking": "no-think, 32k", "nothink_mit_4sem": "no-think, MIT sampling", "cero_edicion_rep110": "repetition_penalty 1.1",
               "cero_edicion_rep105": "repetition_penalty 1.05", "cero_edicion_presence2": "presence_penalty 2.0", "cero_edicion_presence0": "presence_penalty 0"}
    g = [r for r in tabla("tabla_dia_pareado_dos_grupos.csv") if r["variante"] != "dia_nothink_mit100"] + tabla("tabla_fig2_nothink_mit_4sem.csv")
    f2 = sorted((dict(label=NOMBRE2[r["variante"]], total=num(r["dif_total_pts"]), lo=num(r["dif_total_boot_lo"]), hi=num(r["dif_total_boot_hi"]),
                      looped=num(r["antes_limite_contribucion_pts"]), finished=num(r["ya_terminaban_contribucion_pts"]), seeds=len(r["semillas_comunes"].split())) for r in g),
                key=lambda x: -x["total"])

    T1, TI = "GSM8K subconjunto 1 (100 problemas)", "IFEval (100 problemas, estricto a nivel de prompt)"
    CASOS = {"MATH-500 (100) · no-think muestreo MIT": ("MATH-500, no-think MIT sampling", None, "orig · thinking MIT", "orig · no-think muestreo MIT"),
             "MATH-500 (100) · no-think 32k": ("MATH-500, no-think 32k", None, "orig · thinking MIT", "orig · no-think 32k"),
             "GSM8K sub.1 (100) · no-think muestreo MIT": ("GSM8K subset 1, no-think MIT sampling", T1, "orig · thinking MIT (solo semilla 0)", "orig · no-think muestreo MIT"),
             "IFEval (100) · no-think muestreo MIT": ("IFEval, no-think MIT sampling", TI, "orig · thinking MIT (solo semilla 0)", "orig · no-think muestreo MIT")}
    f3 = []
    for r in frac:
        nombre, t_, ot, nt = CASOS[r["caso"]]
        fuente = m if t_ is None else [x for x in r3 if x["tabla"] == t_]
        filas = []
        for b, v in ((ot, "OT"), (nt, "NT"), ("p50c · thinking MIT", "ED")):
            a = una(fuente, brazo=b)
            if abs(num(a["precision_pct"]) - num(r[v])) > 1e-3:
                raise SystemExit(f"{b}: no coincide con fraccion_ganancia.csv")
            filas.append(p(a))
        f3.append(dict(case=nombre, arms=filas, fraction=num(r["fraccion"]), lo=num(r["fraccion_ic_lo"]), hi=num(r["fraccion_ic_hi"])))

    f4 = dict(math=[p(r) for r in m if r["brazo"].split(" · ")[0] in ("orig", "p50c") and etiqueta(r["brazo"])["mode"] in ("thinking", "nt_mit", "nt_32k")],
              gsm8k=[p(r) for r in r3 if r["tabla"] == T1], ifeval=[p(r) for r in r3 if r["tabla"] == TI])
    pla = una(mc, A="p50c · thinking MIT", B="placebo · thinking MIT"); pl0 = una(mc, A="orig · thinking MIT", B="placebo · thinking MIT")
    f5 = dict(arms=[p(una(m, brazo=b)) for b in ("orig · thinking MIT", "placebo · thinking MIT", "p50c · thinking MIT")],
              vs_edit=num(pla["dif_A_menos_B_pts"]), vs_edit_lo=num(pla["dif_boot_lo"]), vs_edit_hi=num(pla["dif_boot_hi"]), vs_orig=num(pl0["dif_A_menos_B_pts"]))

    def t(tarea):
        filas = [r for r in otras if r["tarea"] == tarea and r["semilla"] == "0 1 2 3"]
        filas += [r for r in otras if r["tarea"] == tarea and r["brazo"] == "orig · thinking MIT (temp 0.6)"]
        return [p(r, "ic_lo", "ic_hi", "semilla") for r in filas if "no-think" not in r["brazo"]]

    FICHA = ("orig · thinking ficha Qwen (temp 1.0)", "p50c · thinking ficha Qwen (temp 1.0)")
    g06 = una(mc, A="orig · thinking MIT", B="p50c · thinking MIT")
    g10 = una(mc4, A=FICHA[0], B=FICHA[1])

    def otra(tarea, a, b):
        return una(mco, tabla=f"{tarea} · ficha Qwen · semillas 0-3", A=a, B=b)

    gg, gi = otra("GSM8K subconjunto 1", *FICHA), otra("IFEval", *FICHA)
    rg, ri = (otra(k, FICHA[1], "orig · no-think muestreo MIT") for k in ("GSM8K subconjunto 1", "IFEval"))
    e6 = {k: una(mc3, tabla=k, A="p50c · thinking MIT", B="orig · thinking MIT (solo semilla 0)") for k in ("GSM8K subconjunto 1", "IFEval")}

    def ganancia(r, signo=-1, semilla0=False):
        a, b = signo * num(r["dif_boot_lo"]), signo * num(r["dif_boot_hi"])
        return dict(pts=signo * num(r["dif_A_menos_B_pts"]), lo=min(a, b), hi=max(a, b), seed0=semilla0)

    f6 = dict(math=[p(una(m, brazo="orig · thinking MIT")), p(una(m, brazo="p50c · thinking MIT"))] + [p(r, "ic_lo", "ic_hi", "semilla") for r in c4],
              gsm8k=t("GSM8K subconjunto 1"), ifeval=t("IFEval"),
              gain=dict(math=[ganancia(g06), ganancia(g10)], gsm8k=[ganancia(e6["GSM8K subconjunto 1"], 1, True), ganancia(gg)], ifeval=[ganancia(e6["IFEval"], 1, True), ganancia(gi)]))

    corr = [r for r in tabla("tabla_r2_corridas.csv") if r["semilla"] == "0"]
    N7 = {"o": "unedited thinking", "A": "A · retry", "B": "B · force answer", "p": "p50c thinking"}
    f7 = dict(math=[], gsm8k=[])
    for r in reint:
        k = "math" if r["tarea"].startswith("MATH") else "gsm8k"
        f7[k].append(dict(label=N7[r["brazo"][0]], model="p50c" if r["brazo"][0] == "p" else "orig", mode={"o": "thinking", "A": "retry", "B": "force", "p": "thinking"}[r["brazo"][0]],
                          tokens=num(r["tokens_totales_por_problema"]), acc=num(r["precision_pct"]), lo=num(r["precision_wilson_lo"]), hi=num(r["precision_wilson_hi"])))
    for pref, k, mo, nombre in (("dia_nothink_mit100", "math", "nt_mit", "no-think, MIT sampling"), ("cero_edicion_no_thinking", "math", "nt_32k", "no-think, 32k"), ("r2_gsm8k_orig_nothink", "gsm8k", "nt_mit", "no-think, MIT sampling")):
        r = una(corr, prefijo=pref)
        f7[k].append(dict(label=nombre, model="orig", mode=mo, tokens=num(r["tokens_medios"]), acc=num(r["precision_pct"]), lo=num(r["precision_wilson_lo"]), hi=num(r["precision_wilson_hi"])))

    a = {x["label"]: x for x in f1_}
    tok = {r["brazo"]: float(r["tokens_medios"]) for r in m}
    fr = {x["case"]: x for x in f3}
    re_ = {(r["tarea"][:4], r["brazo"][0]): r for r in reint}
    b_vs = {k: una(mc3, tabla=f"McNemar {n} (semilla 0)", A="B · forzar", B="p50c · thinking") for k, n in (("MATH", "MATH-500 (100 fijos)"), ("GSM8", "GSM8K (subconjunto 1)"))}
    pool = una(mc3, tabla="GSM8K 1 + b juntos", A="p50c · thinking MIT", B="orig · no-think muestreo MIT")
    ifr = una(mc3, tabla="IFEval", A="p50c · thinking MIT", B="orig · no-think muestreo MIT")
    tie = una(mc, A="orig · no-think 32k", B="p50c · thinking MIT")
    tot = una(tabla("tabla_tiempos_por_prefijo.csv"), corridas="99")
    pct = lambda x: f"{Decimal(str(round(float(x) * 100, 6))).quantize(Decimal('1'), rounding=ROUND_HALF_EVEN)}"
    lim = {(x["model"], k): x["limit"] for k in ("gsm8k", "ifeval") for x in f6[k] if x["mode"] == "thinking"}
    lim1 = {(x["model"], k): x["limit"] for k in ("gsm8k", "ifeval") for x in f6[k] if x["mode"] == "card"}
    claves = {
        "orig": f1(a["unedited · thinking"]["acc"]), "edit": f1(a["p50c · thinking"]["acc"]), "nothink": f1(a["unedited · no-think, 32k"]["acc"]),
        "edit_nothink": f1(a["p50c · no-think, 32k"]["acc"]), "nothink_mit": f1(a["unedited · no-think, MIT sampling"]["acc"]), "placebo": f1(a["placebo · thinking"]["acc"]),
        "orig_limit": f1(a["unedited · thinking"]["limit"]), "edit_limit": f1(a["p50c · thinking"]["limit"]), "placebo_limit": f1(a["placebo · thinking"]["limit"]),
        "edit_limit_card": f1(a["p50c · model-card config"]["limit"]), "rep11": f1(a["unedited · repetition_penalty 1.1"]["acc"]),
        "gain06": f1(f6["gain"]["math"][0]["pts"], True), "gain10": f1(f6["gain"]["math"][1]["pts"], True),
        "gain_gsm": f1(f6["gain"]["gsm8k"][1]["pts"], True), "gain_gsm_lo": f1(f6["gain"]["gsm8k"][1]["lo"], True), "gain_gsm_hi": f1(f6["gain"]["gsm8k"][1]["hi"], True),
        "gain_gsm06": f1(f6["gain"]["gsm8k"][0]["pts"], True), "gain_if06": f1(f6["gain"]["ifeval"][0]["pts"], True),
        "if_rev": f1(gi["dif_A_menos_B_pts"]), "if_rev_lo": f1(gi["dif_boot_lo"], True), "if_rev_hi": f1(gi["dif_boot_hi"], True),
        "lim_gsm06": f1(lim[("p50c", "gsm8k")]), "lim_gsm10": f1(lim1[("p50c", "gsm8k")]), "lim_if": f1(lim1[("p50c", "ifeval")]),
        "res_pool": f1(pool["dif_A_menos_B_pts"], True), "res_pool_lo": f1(pool["dif_boot_lo"], True), "res_pool_hi": f1(pool["dif_boot_hi"], True), "res_if06": f1(ifr["dif_A_menos_B_pts"], True),
        "res_gsm": f1(rg["dif_A_menos_B_pts"], True), "res_gsm_lo": f1(rg["dif_boot_lo"], True), "res_gsm_hi": f1(rg["dif_boot_hi"], True),
        "res_ifeval": f1(ri["dif_A_menos_B_pts"], True), "res_if_lo": f1(ri["dif_boot_lo"], True), "res_if_hi": f1(ri["dif_boot_hi"], True),
        "frac_mit": pct(fr["MATH-500, no-think MIT sampling"]["fraction"]), "frac_gsm": pct(fr["GSM8K subset 1, no-think MIT sampling"]["fraction"]), "frac_if": pct(fr["IFEval, no-think MIT sampling"]["fraction"]),
        "tie": f1(-num(tie["dif_A_menos_B_pts"]) * -1, True), "tie_lo": f1(tie["dif_boot_lo"], True), "tie_hi": f1(tie["dif_boot_hi"], True),
        "pla_gap": f1(f5["vs_edit"]), "force_math": f1(re_[("MATH", "B")]["precision_pct"]), "force_gsm": f1(re_[("GSM8", "B")]["precision_pct"]),
        "retry_math": f1(re_[("MATH", "A")]["precision_pct"]), "retry_gsm": f1(re_[("GSM8", "A")]["precision_pct"]),
        "force_tok": f"{round(float(re_[('MATH', 'B')]['tokens_totales_por_problema'])):,}", "edit_tok0": f"{round(float(re_[('MATH', 'p')]['tokens_totales_por_problema'])):,}",
        "force_gap_math": f1(abs(num(b_vs["MATH"]["dif_A_menos_B_pts"]))), "force_gap_gsm": f1(abs(num(b_vs["GSM8"]["dif_A_menos_B_pts"]))),
        "tok_orig": f"{round(tok['orig · thinking MIT']):,}", "tok_edit": f"{round(tok['p50c · thinking MIT']):,}", "tok_nt": f"{round(tok['orig · no-think 32k']):,}", "tok_ntm": f"{round(tok['orig · no-think muestreo MIT']):,}",
        "runs": tot["corridas"], "minutes": f"{round(float(tot['minutos_total'])):,}", "max_tokens": f"{LIMITE:,}",
    }
    return dict(fig1=f1_, fig2=f2, fig3=f3, fig4=f4, fig5=f5, fig6=f6, fig7=f7), claves


def comprobar(html):
    """El blog no afirma nada que el paper no diga: cada número del texto (salvo la nota de selección de ejemplos) debe estar en el draft."""
    paper = re.sub(r"<!--.*?-->", "", (RAIZ / "paper/draft.md").read_text(encoding="utf-8"), flags=re.S).replace("−", "-")
    t = re.sub(r'<p class="note" data-select>.*?</p>', " ", html, flags=re.S)
    t = re.sub(r"<(script|style|pre|a\b)[^>]*>.*?</\1>", " ", t, flags=re.S)
    t = re.sub(r"<head>.*?</head>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", " ", t).replace("−", "-")
    faltan = sorted({n for n in re.findall(r"\d[\d,]*\.?\d*", t) if n.rstrip(".,") not in paper})
    if faltan:
        raise SystemExit(f"Números del blog que no están en el paper: {faltan}")


def main():
    figs, claves = figuras()
    ej, cuenta = ejemplos()
    claves.update({f"n_{k}": str(v) for k, v in cuenta.items()})
    (BLOG / "data").mkdir(parents=True, exist_ok=True)
    js = "window.BLOG=" + json.dumps(dict(figures=figs, examples=ej, counts=cuenta, maxTokens=LIMITE), ensure_ascii=False, separators=(",", ":")) + ";\n"
    (BLOG / "data/data.js").write_text(js, encoding="utf-8")
    html = (BLOG / "src/index.template.html").read_text(encoding="utf-8")
    html = re.sub(r"\{\{(\w+)\}\}", lambda m: claves[m.group(1)], html)
    comprobar(html)
    (BLOG / "index.html").write_text(html, encoding="utf-8")
    print(f"data.js {len(js) // 1024} KB; html {len(html) // 1024} KB; {len(claves)} claves; números del texto: todos en el paper")
    print("conteos:", cuenta)
    if "--preview" in sys.argv:
        preview(html, js, Path(sys.argv[sys.argv.index("--preview") + 1]))


def preview(html, js, destino):
    """Un solo archivo, con KaTeX y sus fuentes incrustados, para abrir en el celular."""
    K = BLOG / "vendor/katex"
    kcss = (K / "katex.min.css").read_text(encoding="utf-8")
    kcss = re.sub(r"url\(fonts/([\w-]+\.woff2)\)", lambda m: "url(data:font/woff2;base64," + base64.b64encode((K / "fonts" / m.group(1)).read_bytes()).decode() + ")", kcss)
    kcss = re.sub(r",url\(fonts/[^)]*\) format\(\"(?:woff|truetype)\"\)", "", kcss)
    h = html.replace('<link rel="stylesheet" href="vendor/katex/katex.min.css">', f"<style>{kcss}</style>")
    h = h.replace('<link rel="stylesheet" href="style.css">', "<style>" + (BLOG / "style.css").read_text(encoding="utf-8") + "</style>")
    for src, texto in (("vendor/katex/katex.min.js", (K / "katex.min.js").read_text(encoding="utf-8")), ("data/data.js", js),
                       ("js/player.js", (BLOG / "js/player.js").read_text(encoding="utf-8")), ("js/charts.js", (BLOG / "js/charts.js").read_text(encoding="utf-8"))):
        h = h.replace(f'<script src="{src}"></script>', "<script>" + texto.replace("</script", "<\\/script") + "</script>")
    destino.write_text(h, encoding="utf-8")


if __name__ == "__main__":
    main()
