"""Genera, desde paper/draft.md, la versión para leer y la versión LaTeX. El draft con comentarios de fuente no se toca.

  paper/paper_para_leer.html   HTML con las figuras incrustadas, sin comentarios de fuente
  paper/latex/main.tex         preprint de una columna; figuras en paper/latex/figures/, bibliografía en references.bib

Al final revisa el .tex sin compilarlo: etiquetas, citas, figuras, llaves, caracteres y ancho de las tablas.
Uso, desde la raíz del proyecto: python scripts/construir_paper.py
"""
import base64, re, shutil, sys
from pathlib import Path
import mistune

RAIZ = Path(__file__).resolve().parents[1]
PAPER = RAIZ / "paper"
LATEX = PAPER / "latex"

CITAS = {
    "(Messing, 2026; prompt shown in his thread)": r"\citep[prompt shown in his thread]{messing2026}",
    "Lightman et al. (2023)": r"\citet{lightman2023}",
    "(Takehi et al., 2026)": r"\citep{takehi2026}", "(RikiyaT, 2026)": r"\citep{takehi2026logs}", "(Qwen Team, 2026)": r"\citep{qwen2026}",
    "(Messing, 2026)": r"\citep{messing2026}", "(Arditi et al., 2024)": r"\citep{arditi2024}", "(Muennighoff et al., 2025)": r"\citep{muennighoff2025}",
    "(Hu et al., 2022)": r"\citep{hu2022}", "(Han et al., 2026)": r"\citep{han2026}", "(Hendrycks et al., 2021)": r"\citep{hendrycks2021}",
    "(Cobbe et al., 2021)": r"\citep{cobbe2021}", "(Zhou et al., 2023)": r"\citep{zhou2023}", "(Kwon et al., 2023)": r"\citep{kwon2023}",
    "(Kydlíček, 2026)": r"\citep{mathverify}", "(Gao et al., 2023)": r"\citep{lmeval}", "(Wilson, 1927)": r"\citep{wilson1927}",
    "(McNemar, 1947)": r"\citep{mcnemar1947}", "(Holm, 1979)": r"\citep{holm1979}", "(Efron, 1979)": r"\citep{efron1979}",
}
# Peso relativo de cada columna; tabularx reparte el ancho de la página, así que la suma nunca lo excede.
ANCHOS = {
    "1": [1.9, .95, 1.3, .7, .7, 1.05, 1.15, .9], "2": [.8, 1.7, 1.6, .7, .9, .7], "frac": [2.6, .5, .5, .5, 1.5], "3": [1.2, .8, .8, .9, 1.7, .8],
    "4": [2.1, .7, .8, .8, .9, .8], "5": [.7, .8, 1.3, .75, 1.75, .6, 1], "6": [.9, .75, .55, 1.3, 1.75, .6, 1], "7": [.6, 1.3, 1.4, .8, .7, .8], "8": [2.4, 1, 1],
}
SUP = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")


def limpio():
    """Draft sin comentarios de fuente y sin el espacio que dejaban antes de la puntuación."""
    t = (PAPER / "draft.md").read_text(encoding="utf-8")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"^> .*\n", "", t, flags=re.M)
    t = re.sub(r"[ \t]+([.,;:)])", r"\1", t)
    return re.sub(r"\n{3,}", "\n\n", t)


def html(t):
    def img(m):
        return f"![{m.group(1)}](data:image/png;base64,{base64.b64encode((PAPER / m.group(2)).read_bytes()).decode()})"
    s = re.sub(r"!\[(.*?)\]\((figuras/out/.*?\.png)\)", img, t).replace("\\boxed", "\\\\boxed")
    cuerpo = mistune.create_markdown(escape=False, plugins=["table", "strikethrough"])(s)
    css = """body{font:17px/1.6 Georgia,serif;color:#222;max-width:42rem;margin:0 auto;padding:1rem}
h1{font-size:1.5rem;line-height:1.25}h2{font-size:1.25rem;margin-top:2.2rem}h3{font-size:1.05rem}img{max-width:100%;height:auto}
table{border-collapse:collapse;font:13px/1.35 system-ui,sans-serif;display:block;overflow-x:auto}th,td{border:1px solid #ccc;padding:.3rem .45rem}
th{background:#f2f2f2}code{font-size:.9em;overflow-wrap:anywhere}hr{border:0;border-top:1px solid #ddd;margin:2rem 0}li{margin:.3rem 0}"""
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>Decomposing the Gain</title><style>{css}</style><body>{cuerpo}</body></html>")


def codigo(s):
    s = s.replace("\\", "\x00").replace("{", r"\{").replace("}", r"\}").replace("\x00", r"\textbackslash{}")
    s = s.replace("_", r"\_\allowbreak{}").replace("%", r"\%").replace("&", r"\&").replace("#", r"\#").replace("<", r"\textless{}").replace(">", r"\textgreater{}")
    return r"\texttt{" + s + "}"


def inline(s):
    guardado = []

    def poner(x):
        guardado.append(x)
        return f"\x01{len(guardado) - 1}\x02"

    s = re.sub(r"`([^`]+)`", lambda m: poner(codigo(m.group(1))), s)
    for a, b in sorted(CITAS.items(), key=lambda x: -len(x[0])):
        s = s.replace(a, poner(b))
    s = re.sub(r"§(\d+(?:\.\d+)?)", lambda m: poner(rf"\S\ref{{sec:{m.group(1)}}}"), s)
    s = re.sub(r"\bTable (\d+)", lambda m: poner(rf"Table~\ref{{tab:{m.group(1)}}}"), s)
    s = re.sub(r"\bFigure (\d+)", lambda m: poner(rf"Figure~\ref{{fig:{m.group(1)}}}"), s)
    s = s.replace("\\*", poner(r"$^{*}$"))
    s = s.replace("\\", poner(r"\textbackslash{}"))
    s = s.replace("{", r"\{").replace("}", r"\}")
    s = s.replace("%", r"\%").replace("&", r"\&").replace("#", r"\#").replace("_", r"\_\allowbreak{}")
    s = re.sub(r'"(.+?)"', r"``\1''", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"\\emph{\1}", s)
    s = re.sub(r"10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: f"$10^{{{m.group(1).translate(SUP)}}}$", s)
    for a, b in (("‖ΔW‖\\_\\allowbreak{}F", r"$\|\Delta W\|_F$"), ("‖W‖\\_\\allowbreak{}F", r"$\|W\|_F$"), ("‖ΔW‖", r"$\|\Delta W\|$"), ("‖W‖", r"$\|W\|$"), ("ΔW", r"$\Delta W$"),
                 ("−", "$-$"), ("×", r"$\times$"), ("→", r"$\rightarrow$"), ("±", r"$\pm$"), ("≥", r"$\geq$"), ("·", r"$\cdot$"), ("…", r"\ldots{}"), ("—", "---"), ("–", "--")):
        s = s.replace(a, b)
    return re.sub(r"\x01(\d+)\x02", lambda m: guardado[int(m.group(1))], s)


def celdas(linea):
    return [c.strip() for c in linea.strip().strip("|").split("|")]


def celda(c):
    """Intervalos, conteos b / c y potencias de 10 no se parten en dos líneas."""
    if re.match(r"^\S+ \(.+\)$", c) or "× 10" in c or re.fullmatch(r"\d+ / \d+", c):
        return r"\mbox{" + inline(c) + "}"
    return inline(c)


def tabla(filas, clave):
    pesos = ANCHOS[clave]
    n = len(pesos)
    total = sum(pesos)
    col = "".join(rf">{{\raggedright\arraybackslash\hsize={w * n / total:.3f}\hsize}}X" for w in pesos)
    o = [r"\footnotesize\setlength{\tabcolsep}{4pt}", r"\begin{tabularx}{\linewidth}{" + col + "}", r"\toprule"]
    o.append(" & ".join(r"\textbf{" + inline(c) + "}" for c in filas[0]) + r" \\")
    o.append(r"\midrule")
    for f in filas[2:]:
        if len(f) != n:
            raise SystemExit(f"Tabla {clave}: fila con {len(f)} celdas")
        vacias = sum(1 for c in f[::-1] if c == "") if f[-1] == "" else 0
        if vacias:
            j = n - vacias - 1
            ancho = sum(pesos[j:]) / total * .96
            f = f[:j] + [rf"\multicolumn{{{vacias + 1}}}{{>{{\raggedright\arraybackslash}}p{{{ancho:.2f}\linewidth}}}}{{{inline(f[j])}}}"]
            o.append(" & ".join(celda(c) for c in f[:-1]) + " & " + f[-1] + r" \\")
        else:
            o.append(" & ".join(celda(c) for c in f) + r" \\")
    o += [r"\bottomrule", r"\end{tabularx}"]
    return "\n".join(o)


def lista(items, tipo):
    return f"\\begin{{{tipo}}}[nosep,leftmargin=*]\n" + "\n".join(r"\item " + inline(i) for i in items) + f"\n\\end{{{tipo}}}"


def latex(t):
    lineas = t[t.index("## Abstract"):].split("\n")
    out, parrafo, i = [], [], 0

    def vaciar():
        if parrafo:
            out.append(inline(" ".join(parrafo)) + "\n")
            parrafo.clear()

    def siguiente(k):
        while k < len(lineas) and not lineas[k].strip():
            k += 1
        return k

    resumen = False
    while i < len(lineas):
        l = lineas[i].rstrip()
        if not l.strip() or l.strip() == "---":
            vaciar(); i += 1; continue
        m = re.match(r"## (.+)", l)
        if m:
            vaciar()
            if resumen:
                out.append(r"\end{abstract}" + "\n"); resumen = False
            titulo = m.group(1)
            if titulo == "Abstract":
                out.append(r"\begin{abstract}"); resumen = True
            elif titulo == "References":
                break
            elif re.match(r"\d+\. ", titulo):
                k, nombre = titulo.split(". ", 1)
                titulo_tex = inline(nombre)
                if "$" in titulo_tex:
                    titulo_tex = rf"\texorpdfstring{{{titulo_tex}}}{{{nombre.replace('×', 'x')}}}"
                out.append(rf"\section{{{titulo_tex}}}\label{{sec:{k}}}" + "\n")
            else:
                out.append(rf"\section*{{{inline(titulo)}}}" + "\n")
            i += 1; continue
        m = re.match(r"### (\d+\.\d+) (.+)", l)
        if m:
            vaciar(); out.append(rf"\subsection{{{inline(m.group(2))}}}\label{{sec:{m.group(1)}}}" + "\n"); i += 1; continue
        m = re.match(r"!\[Figure (\d+)\]", l)
        if m:
            vaciar()
            k = siguiente(i + 1)
            c = re.match(r"\*\*Figure \d+ — (.+?)\*\*\s*(.*)", lineas[k])
            pie = inline(c.group(1) + " " + c.group(2))
            out.append(rf"\begin{{figure}}[htbp]" + "\n\\centering\n" + rf"\includegraphics[width=\linewidth]{{figures/fig{m.group(1)}.pdf}}" + "\n" + rf"\caption{{{pie}}}\label{{fig:{m.group(1)}}}" + "\n\\end{figure}\n")
            i = k + 1; continue
        m = re.match(r"\*\*Table (\d+) — (.+?)\*\*$", l)
        if m:
            vaciar()
            k = siguiente(i + 1)
            filas = []
            while k < len(lineas) and lineas[k].startswith("|"):
                filas.append(celdas(lineas[k])); k += 1
            nota = ""
            j = siguiente(k)
            if lineas[j].startswith("\\*"):
                nota = "\n\\par\\smallskip\\footnotesize " + inline(lineas[j]); k = j + 1
            out.append(r"\begin{table}[htbp]" + "\n\\centering\n" + rf"\caption{{{inline(m.group(2))}}}\label{{tab:{m.group(1)}}}" + "\n" + tabla(filas, m.group(1)) + nota + "\n\\end{table}\n")
            i = k; continue
        if l.startswith("|"):
            vaciar()
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                filas.append(celdas(lineas[i])); i += 1
            out.append(r"\begin{center}" + "\n" + tabla(filas, "frac") + "\n\\end{center}\n")
            continue
        if re.match(r"(- |\d+\. )", l):
            vaciar()
            tipo = "itemize" if l.startswith("- ") else "enumerate"
            items = []
            while i < len(lineas) and re.match(r"(- |\d+\. )", lineas[i]):
                items.append(re.sub(r"^(- |\d+\. )", "", lineas[i].rstrip())); i += 1
            out.append(lista(items, tipo) + "\n")
            continue
        parrafo.append(l.strip()); i += 1
    vaciar()
    pre = r"""\documentclass[11pt]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{array,booktabs,tabularx}
\usepackage[font=small,labelfont=bf,skip=6pt]{caption}
\usepackage{enumitem}
\usepackage{microtype}
\usepackage[round,sort]{natbib}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\emergencystretch=2em
% Una figura solo ocupa una pagina propia si la llena al menos en un 80%; si no, comparte pagina con texto.
\renewcommand{\floatpagefraction}{.8}
\renewcommand{\topfraction}{.85}
\renewcommand{\bottomfraction}{.5}
\renewcommand{\textfraction}{.1}
\setcounter{topnumber}{2}
\setcounter{totalnumber}{3}

\title{Decomposing the Gain: How Much of a Weight-Space Edit's Fix for Reasoning Loops Do Cheap Baselines Recover?}
\author{%
  \textbf{Juan Jos\'e Giraldo M\'arquez}\\
  Independent researcher\\
  \href{https://github.com/JKUL-png}{github.com/JKUL-png}
  \and
  \textbf{Juan Jos\'e G\'omez}\\
  Undergraduate student in Data Engineering and Artificial Intelligence\\
  Universidad Aut\'onoma de Occidente (UAO), Cali, Colombia
}
\date{November 2026\\[.6em]
  \small Code and data: \href{https://github.com/JKUL-png/decomposing-the-gain}{github.com/JKUL-png/decomposing-the-gain}}

\begin{document}
\maketitle

"""
    fin = "\n\\bibliographystyle{plainnat}\n\\bibliography{references}\n\n\\end{document}\n"
    return pre + "\n".join(out) + fin


def revisar(tex):
    """Revisión sin compilar. Devuelve la lista de problemas."""
    p = []
    etiquetas = set(re.findall(r"\\label\{(.+?)\}", tex))
    for r in set(re.findall(r"\\ref\{(.+?)\}", tex)) - etiquetas:
        p.append(f"referencia sin etiqueta: {r}")
    bib = (LATEX / "references.bib").read_text(encoding="utf-8")
    claves = set(re.findall(r"@\w+\{(\w+),", bib))
    citadas = set(re.findall(r"\\cite[pt](?:\[[^\]]*\])?\{(\w+)\}", tex))
    for c in citadas - claves:
        p.append(f"cita sin entrada en references.bib: {c}")
    for c in claves - citadas:
        p.append(f"entrada no citada: {c}")
    for f in re.findall(r"\\includegraphics\[.*?\]\{(.+?)\}", tex):
        if not (LATEX / f).exists():
            p.append(f"falta figura: {f}")
    sin = re.sub(r"\\[{}]", "", tex)
    if sin.count("{") != sin.count("}"):
        p.append(f"llaves desbalanceadas: {sin.count('{')} / {sin.count('}')}")
    if tex.count("$") % 2:
        p.append("número impar de $")
    raros = sorted({c for c in tex if ord(c) > 127} - set("áéíóúñčèÁÉÍÓÚ"))
    if raros:
        p.append(f"caracteres sin convertir: {raros}")
    for r in re.findall(r"\(\w[^()]*?, (?:19|20)\d\d\)", tex):
        p.append(f"cita de texto sin convertir: {r}")
    for e in ("begin{table}", "begin{figure}", "begin{tabularx}", "begin{itemize}", "begin{enumerate}", "begin{center}"):
        if tex.count("\\" + e) != tex.count("\\" + e.replace("begin", "end")):
            p.append(f"entorno sin cerrar: {e}")
    if re.findall(r"(?<!\\)%(?!\n)", tex.split("\\begin{document}")[1]):
        p.append("% sin escapar")
    return p, len(etiquetas), len(citadas), len(claves)


def ancho_pt(s, negrita=False):
    """Ancho aproximado en la letra de las tablas (9 pt, como dice el log de compilación)."""
    pts = {".": 2.6, ",": 2.6, "(": 3.6, ")": 3.6, " ": 3.1, "−": 7.2, "+": 7.2, "×": 7.2, "…": 10.3, "–": 4.6, "%": 7.7, "/": 4.6, "·": 2.6}
    return sum(pts.get(c, 4.7) for c in s) * (1.12 if negrita else 1)


def ancho_tablas(md):
    """Estimación: lo que no se puede partir debe caber en su columna (ancho de texto 469.75 pt, tabcolsep 4 pt)."""
    avisos = []
    bloques = re.findall(r"((?:^\|.*\n)+)", md, flags=re.M)
    orden = ["1", "2", "frac", "3", "4", "5", "6", "7", "8"]
    for clave, b in zip(orden, bloques):
        filas = [celdas(x) for x in b.strip().split("\n")]
        pesos = ANCHOS[clave]
        util = 469.75 - 8 * len(pesos)
        for f in [filas[0]] + filas[2:]:
            enc = f is filas[0]
            for j, c in enumerate(f):
                if j >= len(pesos) or not c or (clave == "1" and f[0].startswith("Single") and j == 2):
                    continue
                c = c.replace("`", "")
                entero = not enc and (re.match(r"^\S+ \(.+\)$", c) or "× 10" in c)
                trozo = c if entero else max(re.split(r"[ _]", c), key=len)
                col = util * pesos[j] / sum(pesos)
                if ancho_pt(trozo, enc) > col:
                    avisos.append(f"tabla {clave}, col {j + 1}: «{trozo}» ~{ancho_pt(trozo, enc):.0f} pt, columna {col:.0f} pt")
    return avisos


def main():
    t = limpio()
    (PAPER / "paper_para_leer.html").write_text(html(t), encoding="utf-8")
    (LATEX / "figures").mkdir(parents=True, exist_ok=True)
    for k in range(1, 8):
        shutil.copyfile(PAPER / f"figuras/out/fig{k}.pdf", LATEX / f"figures/fig{k}.pdf")
    tex = latex(t)
    (LATEX / "main.tex").write_text(tex, encoding="utf-8")
    problemas, n_et, n_cit, n_bib = revisar(tex)
    anchos = ancho_tablas(t)
    print(f"main.tex: {len(tex) // 1024} KB, {n_et} etiquetas, {n_cit} citadas de {n_bib} en .bib, {tex.count(chr(92) + 'begin{table}')} tablas, {tex.count(chr(92) + 'begin{figure}')} figuras")
    print("problemas:", problemas or "ninguno")
    print("anchos:", anchos or "todas las palabras caben")
    espacios = re.findall(r".{20} +[.,;:]", re.sub(r"<[^>]+>", "", html(re.sub(r"!\[.*?\]\(.*?\)", "", t))))
    print("espacios antes de puntuación en la versión para leer:", len(espacios), espacios[:3])
    sys.exit(1 if problemas else 0)


if __name__ == "__main__":
    main()
