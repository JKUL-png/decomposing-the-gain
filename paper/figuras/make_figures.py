"""Regenerates every paper figure from the CSVs in resultados/.

Usage (from the project root):  .venv/Scripts/python.exe paper/figuras/make_figures.py
No plotted value is typed here: this file holds only labels, styles and label offsets.
See ESPECIFICACION.md for what each figure shows and which column feeds it.
"""
from decimal import ROUND_HALF_EVEN, Decimal
from math import hypot
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "resultados"
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

# ---- One style for all figures --------------------------------------------------------
# Okabe-Ito palette. Color = model; marker shape = how the model is run;
# filled marker = 4 seeds, hollow marker = 1-2 seeds.
C_ORIG, C_P50C, C_PLACEBO = "#0072B2", "#D55E00", "#7F7F7F"
C_LOOPED, C_FINISHED = "#009E73", "#CC79A7"  # Fig. 2: problem groups, not models
INK, MUTED, GRID = "#222222", "#666666", "#E4E4E4"
WIDE = 7.0  # two-column width, inches

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7.5, "legend.fontsize": 7.5,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6, "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK, "ytick.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "legend.frameon": False,
    "pdf.fonttype": 42, "svg.fonttype": "none",
})

MARKERS = {"thinking": "o", "nothink_mit": "D", "nothink_32k": "v", "penalty": "s", "card": "*",
           "retry": "^", "force": "P"}
SEED_DTYPES = {c: str for c in ("semilla", "semillas", "semillas_comunes",
                                "semillas_OT", "semillas_ED", "semillas_NT")}


def load(name):
    return pd.read_csv(RES / name, dtype=SEED_DTYPES)


def fmt1(value):
    """One decimal, exact halves to even (28.75 -> 28.8, 51.25 -> 51.2), ignoring float noise."""
    return str(Decimal(str(round(float(value), 6))).quantize(Decimal("0.1"), rounding=ROUND_HALF_EVEN))


def signed(value):
    text = fmt1(value)
    return text.replace("-", "−") if text.startswith("-") else f"+{text}"


def n_seeds(value):
    return len(str(value).split())


def one(df, **filters):
    """Returns the single row matching the filters; fails loudly otherwise."""
    for col, val in filters.items():
        df = df[df[col] == val]
    if len(df) != 1:
        raise ValueError(f"expected 1 row for {filters}, found {len(df)}")
    return df.iloc[0]


def model_color(arm):
    for prefix, color in (("orig", C_ORIG), ("p50c", C_P50C), ("placebo", C_PLACEBO)):
        if arm.startswith(prefix):
            return color
    raise ValueError(f"unknown model in arm: {arm}")


def marker_for(arm):
    if "no-think 32k" in arm:
        return MARKERS["nothink_32k"]
    if "no-think" in arm:
        return MARKERS["nothink_mit"]
    if "ficha" in arm:
        return MARKERS["card"]
    if "rep " in arm or "presence" in arm:
        return MARKERS["penalty"]
    return MARKERS["thinking"]


def point(ax, x, y, lo, hi, color, marker, seeds, size=5.5, z=3):
    """Point with a 95% CI; hollow when it rests on fewer than 4 seeds."""
    ax.errorbar(x, y, yerr=[[y - lo], [hi - y]], fmt="none", ecolor=color, elinewidth=0.8,
                alpha=0.45, capsize=0, zorder=z - 1)
    ax.plot([x], [y], marker=marker, ms=size * (1.45 if marker == "*" else 1), mew=1.0,
            mec=color, mfc=color if seeds >= 4 else "white", ls="none", zorder=z)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def seed_legend():
    return [Line2D([], [], marker="o", ls="none", mec=MUTED, mfc=MUTED, ms=5, label="4 seeds"),
            Line2D([], [], marker="o", ls="none", mec=MUTED, mfc="white", ms=5, label="1–2 seeds")]


# ---- Figure 1 -------------------------------------------------------------------------
FIG1_LABELS = {  # brazo -> (label, x offset, y offset, ha), offsets in points
    "orig · thinking MIT": ("Original, thinking", 7, 0, "left"),
    "orig · no-think muestreo MIT": ("Original, no-think (MIT sampling)", 8, -4, "left"),
    "orig · no-think 32k": ("Original, no-think (32k)", 0, -31, "center"),
    "p50c · thinking MIT": ("Edited, thinking", 7, 5, "left"),
    "p50c · no-think muestreo MIT": ("Edited, no-think (MIT sampling)", 16, 2, "left"),
    "p50c · no-think 32k": ("Edited,\nno-think\n(32k)", 7, 0, "left"),
    "placebo · thinking MIT": ("Placebo, thinking", -2, 22, "left"),
    "orig · rep 1.1 (thinking)": ("Repetition penalty 1.1", 7, 6, "left"),
    "orig · rep 1.05 (thinking)": ("Repetition penalty 1.05", -16, -5, "right"),
    "orig · presence 0 (thinking)": ("Presence penalty 0", -8, 0, "right"),
    "orig · presence 2 (thinking)": ("Presence penalty 2", -16, -8, "right"),
    "orig · thinking ficha Qwen (temp 1.0)": ("Original, model card", -8, -2, "right"),
    "p50c · thinking ficha Qwen (temp 1.0)": ("Edited, model card", -8, 0, "right"),
}


def fig1():
    arms = load("tabla_r2_math_brazos.csv")
    # Repetition penalty 1.1 uses the interval the paper cites, from tabla_dia_promedios.csv.
    rep = one(load("tabla_dia_promedios.csv"), configuracion="cero_edicion_rep110")
    arm = arms.brazo == "orig · rep 1.1 (thinking)"
    if arm.sum() != 1 or abs(arms.loc[arm, "precision_pct"].iloc[0] - rep.precision_pct) > 1e-9:
        raise ValueError("repetition penalty 1.1: the two tables disagree on accuracy")
    arms.loc[arm, ["precision_boot_lo", "precision_boot_hi"]] = [rep.precision_boot_lo, rep.precision_boot_hi]
    rows = [(r.brazo, r.al_limite_pct, r.precision_pct, r.precision_boot_lo, r.precision_boot_hi,
             n_seeds(r.semillas)) for r in arms.itertuples()]
    card = load("tabla_ficha_4sem_corridas.csv")
    card = card[(card.semilla == "0 1 2 3") & card.brazo.str.contains("ficha Qwen \\(temp 1.0\\)")]
    rows += [(r.brazo, r.al_limite_pct, r.precision_pct, r.ic_lo, r.ic_hi, n_seeds(r.semilla))
             for r in card.itertuples()]

    fig, ax = plt.subplots(figsize=(WIDE, 3.9))
    for arm, x, y, lo, hi, seeds in rows:
        point(ax, x, y, lo, hi, model_color(arm), marker_for(arm), seeds)
        label, dx, dy, ha = FIG1_LABELS[arm]
        # Labels sit next to their point; only a label pushed away by a neighbor gets a short leader.
        leader = dict(arrowstyle="-", color="#AAAAAA", lw=0.5, shrinkA=1, shrinkB=3) if 12 < hypot(dx, dy) < 20 else None
        ax.annotate(label, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                    fontsize=7, color=INK, linespacing=1.05, arrowprops=leader)
    ax.set_xlim(-2, 102)
    ax.set_ylim(0, 70)
    ax.set_xlabel("Responses hitting the token limit (%)")
    ax.set_ylabel("MATH-500 accuracy (%, 100 fixed problems)")
    models = [Patch(color=C_ORIG, label="Original"), Patch(color=C_P50C, label="Edited (p50c)"),
              Patch(color=C_PLACEBO, label="Placebo"),
              Line2D([], [], marker="o", ls="none", mec=MUTED, mfc="white", ms=5,
                     label="Hollow marker: 1–2 seeds (filled: 4)")]
    shapes = [Line2D([], [], marker=MARKERS[k], ls="none", mec=MUTED, mfc=MUTED, ms=m, label=t)
              for k, t, m in (("thinking", "Thinking, MIT config", 5), ("penalty", "Thinking, other penalty", 5),
                              ("card", "Thinking, model card", 7.5), ("nothink_mit", "No-think, MIT sampling", 5),
                              ("nothink_32k", "No-think, 32k", 5))]
    block = dict(loc="upper left", columnspacing=1.3, handletextpad=0.5, alignment="left",
                 title_fontproperties={"size": 7.5, "weight": "bold"})
    colors = ax.legend(handles=models, ncol=4, title="Color: model. Fill: seeds", bbox_to_anchor=(-0.02, -0.13), **block)
    ax.add_artist(colors)
    ax.legend(handles=shapes, ncol=3, title="Shape: configuration", bbox_to_anchor=(-0.02, -0.27), **block)
    save(fig, "fig1")


# ---- Figure 2 -------------------------------------------------------------------------
FIG2_LABELS = {
    "cero_edicion_no_thinking": "No-think\n(32k)", "nothink_mit_4sem": "No-think\n(MIT sampling)",
    "cero_edicion_rep110": "Repetition\npenalty 1.1", "cero_edicion_rep105": "Repetition\npenalty 1.05",
    "cero_edicion_presence2": "Presence\npenalty 2.0", "cero_edicion_presence0": "Presence\npenalty 0",
}


def fig2():
    # This arm has 4 seeds in its own CSV; the older table only holds seed 0.
    t = load("tabla_dia_pareado_dos_grupos.csv")
    t = pd.concat([t[t.variante != "dia_nothink_mit100"], load("tabla_fig2_nothink_mit_4sem.csv")])
    t = t.sort_values("dif_total_pts", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(WIDE, 3.0))
    ax.bar(t.index, t.antes_limite_contribucion_pts, width=0.5, color=C_LOOPED,
           label="Problems where the baseline looped")
    ax.bar(t.index, t.ya_terminaban_contribucion_pts, width=0.5, color=C_FINISHED,
           label="Problems the baseline already finished")
    ax.axhline(0, color=MUTED, lw=0.8)
    for i, r in t.iterrows():
        seeds = n_seeds(r.semillas_comunes)
        ax.errorbar(i + 0.36, r.dif_total_pts,
                    yerr=[[r.dif_total_pts - r.dif_total_boot_lo], [r.dif_total_boot_hi - r.dif_total_pts]],
                    fmt="none", ecolor=INK, elinewidth=0.8, capsize=2, capthick=0.8, zorder=3)
        ax.plot([i + 0.36], [r.dif_total_pts], marker="o", ms=4.5, mec=INK, mew=0.9,
                mfc=INK if seeds >= 4 else "white", ls="none", zorder=4)
        ax.annotate(signed(r.dif_total_pts), (i + 0.36, r.dif_total_boot_hi), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=7, color=INK)
    ax.set_xticks(t.index, [f"{FIG2_LABELS[v]}\n({n_seeds(s)} seed{'s' if n_seeds(s) > 1 else ''})"
                            for v, s in zip(t.variante, t.semillas_comunes)])
    ax.tick_params(axis="x", length=0)
    ax.set_xlim(-0.6, len(t) - 0.2)
    ax.set_ylabel("Change in accuracy vs. baseline\n(percentage points)")
    handles, _ = ax.get_legend_handles_labels()
    total = Line2D([], [], marker="o", ls="none", mec=INK, mfc=INK, ms=4.5, label="Total, with 95% CI")
    ax.legend(handles=handles + [total], loc="upper right")
    save(fig, "fig2")


# ---- Figure 3 -------------------------------------------------------------------------
FIG3_LABELS = {
    "MATH-500 (100) · no-think muestreo MIT": "MATH-500\n(no-think, MIT sampling)",
    "MATH-500 (100) · no-think 32k": "MATH-500\n(no-think, 32k)",
    "GSM8K sub.1 (100) · no-think muestreo MIT": "GSM8K",
    "IFEval (100) · no-think muestreo MIT": "IFEval",
}


FIG3_ARMS = {  # caso -> (benchmark table filter, OT arm, NT arm, ED arm)
    "MATH-500 (100) · no-think muestreo MIT": (None, "orig · thinking MIT", "orig · no-think muestreo MIT", "p50c · thinking MIT"),
    "MATH-500 (100) · no-think 32k": (None, "orig · thinking MIT", "orig · no-think 32k", "p50c · thinking MIT"),
    "GSM8K sub.1 (100) · no-think muestreo MIT": ("GSM8K subconjunto 1 (100 problemas)", "orig · thinking MIT (solo semilla 0)",
                                                  "orig · no-think muestreo MIT", "p50c · thinking MIT"),
    "IFEval (100) · no-think muestreo MIT": ("IFEval (100 problemas, estricto a nivel de prompt)", "orig · thinking MIT (solo semilla 0)",
                                             "orig · no-think muestreo MIT", "p50c · thinking MIT"),
}


def fig3():
    t = load("fraccion_ganancia.csv")
    math, r3 = load("tabla_r2_math_brazos.csv"), load("tabla_r3_brazos.csv")
    fig, ax = plt.subplots(figsize=(WIDE, 3.2))
    w = 0.26
    single_seed_baseline = False
    for i, r in t.iterrows():
        one_seed = n_seeds(r.semillas_OT) < 4
        single_seed_baseline |= one_seed
        ax.bar(i - w, r.OT, w * 0.92, color=C_ORIG)
        ax.bar(i, r.NT, w * 0.92, facecolor="white", edgecolor=C_ORIG, hatch="////", lw=0.8)
        ax.bar(i + w, r.ED, w * 0.92, color=C_P50C)
        task, ot, nt, ed = FIG3_ARMS[r.caso]
        table = math if task is None else r3[r3.tabla == task]
        for x, mid, arm, star in ((i - w, r.OT, ot, one_seed), (i, r.NT, nt, False), (i + w, r.ED, ed, False)):
            a = one(table, brazo=arm)
            if abs(a.precision_pct - mid) > 1e-3:
                raise ValueError(f"{arm}: {a.precision_pct} does not match fraccion_ganancia.csv ({mid})")
            ax.errorbar(x, mid, yerr=[[mid - a.precision_boot_lo], [a.precision_boot_hi - mid]], fmt="none",
                        ecolor=INK, elinewidth=0.8, capsize=2, capthick=0.8)
            ax.annotate(f"{fmt1(mid)}{'*' if star else ''}", (x, a.precision_boot_hi), xytext=(0, 2),
                        textcoords="offset points", ha="center", fontsize=7, color=INK)
        ax.text(i, 83, f"recovered\nwithout editing:\n{r.fraccion * 100:.0f}% "
                       f"[{r.fraccion_ic_lo * 100:.0f}–{r.fraccion_ic_hi * 100:.0f}%]",
                ha="center", va="bottom", fontsize=7, color=INK)
    ax.set_xticks(t.index, [FIG3_LABELS[c] for c in t.caso])
    ax.tick_params(axis="x", length=0)
    ax.set_ylim(0, 80)
    ax.set_ylabel("Accuracy (%)")
    handles = [Patch(color=C_ORIG, label="Original, thinking"),
               Patch(facecolor="white", edgecolor=C_ORIG, hatch="////", label="Original, no-think (no edit)"),
               Patch(color=C_P50C, label="Edited (p50c), thinking")]
    if single_seed_baseline:
        handles.append(Line2D([], [], ls="none", label="* baseline: 1 seed"))
    ax.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.17),
              columnspacing=1.4, handlelength=1.6)
    save(fig, "fig3")


# ---- Figure 4 -------------------------------------------------------------------------
MODE_LABELS = {"thinking MIT": "Thinking\n(MIT)", "no-think muestreo MIT": "No-think\n(MIT sampling)",
               "no-think 32k": "No-think\n(32k)"}
MODE_MARKER = {"thinking MIT": MARKERS["thinking"], "no-think muestreo MIT": MARKERS["nothink_mit"],
               "no-think 32k": MARKERS["nothink_32k"]}


def split_arm(arm):
    model, mode = arm.split(" · ", 1)
    return model, mode.replace(" (solo semilla 0)", "")


def fig4():
    math = load("tabla_r2_math_brazos.csv")
    r3 = load("tabla_r3_brazos.csv")
    panels = [("MATH-500", math[math.brazo.str.match(r"^(orig|p50c) · (thinking MIT|no-think)")]),
              ("GSM8K (subset 1)", r3[r3.tabla == "GSM8K subconjunto 1 (100 problemas)"]),
              ("IFEval", r3[r3.tabla == "IFEval (100 problemas, estricto a nivel de prompt)"])]
    fig, axes = plt.subplots(1, 3, figsize=(WIDE, 2.9), sharey=True,
                             gridspec_kw={"width_ratios": [3, 2, 2], "wspace": 0.1})
    for ax, (name, t) in zip(axes, panels):
        modes = [m for m in MODE_LABELS if any(split_arm(b)[1] == m for b in t.brazo)]
        for model, color in (("orig", C_ORIG), ("p50c", C_P50C)):
            sub = {split_arm(r.brazo)[1]: r for r in t.itertuples() if split_arm(r.brazo)[0] == model}
            shift = -0.05 if model == "orig" else 0.05
            ax.plot([i + shift for i in range(len(modes))], [sub[m].precision_pct for m in modes],
                    color=color, lw=1.5, zorder=2)
            for i, m in enumerate(modes):
                r = sub[m]
                point(ax, i + shift, r.precision_pct, r.precision_boot_lo,
                      r.precision_boot_hi, color, MODE_MARKER[m], n_seeds(r.semillas))
        ax.set_xticks(range(len(modes)), [MODE_LABELS[m] for m in modes])
        ax.set_xlim(-0.5, len(modes) - 0.5)
        ax.set_ylim(0, 80)
        ax.tick_params(axis="x", length=0)
        ax.text(0.5, 1.01, name, transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color=INK)
    axes[0].set_ylabel("Accuracy (%)")
    handles = [Line2D([], [], color=C_ORIG, lw=1.5, label="Original"),
               Line2D([], [], color=C_P50C, lw=1.5, label="Edited (p50c)")] + seed_legend()
    fig.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 0.0))
    save(fig, "fig4")


# ---- Figure 5 -------------------------------------------------------------------------
def fig5():
    t = load("tabla_r2_math_brazos.csv")
    mc = load("tabla_r2_mcnemar.csv")
    arms = [("orig · thinking MIT", "Original", C_ORIG),
            ("placebo · thinking MIT", "Placebo\n(random, same\nnorm and columns)", C_PLACEBO),
            ("p50c · thinking MIT", "Edited (p50c)", C_P50C)]
    rows = [one(t, brazo=a) for a, _, _ in arms]
    ticks = [f"{lab}\n{n_seeds(r.semillas)} seeds" for (_, lab, _), r in zip(arms, rows)]
    colors = [c for _, _, c in arms]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(WIDE, 2.9), gridspec_kw={"wspace": 0.3})

    a1.bar(range(3), [r.precision_pct for r in rows], 0.55, color=colors)
    for i, r in enumerate(rows):
        a1.errorbar(i, r.precision_pct, yerr=[[r.precision_pct - r.precision_boot_lo],
                                              [r.precision_boot_hi - r.precision_pct]],
                    fmt="none", ecolor=INK, elinewidth=0.8, capsize=2, capthick=0.8)
        a1.annotate(fmt1(r.precision_pct), (i, r.precision_boot_hi), xytext=(0, 2),
                    textcoords="offset points", ha="center", fontsize=7, color=INK)
    a1.set_ylim(0, 70)
    a1.set_ylabel("MATH-500 accuracy\n(%, 100 fixed problems)")
    e = one(mc, A="p50c · thinking MIT", B="placebo · thinking MIT")
    o = one(mc, A="orig · thinking MIT", B="placebo · thinking MIT")
    a1.text(0.02, 0.98, "Paired, same 2 seeds:\nEdited − placebo:\n"
            f"{signed(e.dif_A_menos_B_pts)} pts [{signed(e.dif_boot_lo)}, {signed(e.dif_boot_hi)}]\n"
            "Original − placebo:\n"
            f"{signed(o.dif_A_menos_B_pts)} pts [{signed(o.dif_boot_lo)}, {signed(o.dif_boot_hi)}]",
            transform=a1.transAxes, va="top", fontsize=7, color=INK)

    a2.bar(range(3), [r.al_limite_pct for r in rows], 0.55, color=colors)
    for i, r in enumerate(rows):
        a2.annotate(fmt1(r.al_limite_pct), (i, r.al_limite_pct), xytext=(0, 2),
                    textcoords="offset points", ha="center", fontsize=7, color=INK)
    a2.set_ylim(0, 100)
    a2.set_ylabel("Responses hitting the\n32,768-token limit (%)")
    for ax in (a1, a2):
        ax.set_xticks(range(3), ticks)
        ax.tick_params(axis="x", length=0)
    save(fig, "fig5")


# ---- Figure 6 -------------------------------------------------------------------------
FINAL_CARD_CSV = "tabla_ficha_otras_4sem_corridas.csv"
DRAFT_CARD_CSV = "tabla_ficha_otras_corridas.csv"
CARD_TASKS = (("GSM8K subconjunto 1", "GSM8K (subset 1)"), ("IFEval", "IFEval"))


def ci_cols(table):
    for lo, hi in (("ic_lo", "ic_hi"), ("precision_boot_lo", "precision_boot_hi"),
                   ("precision_wilson_lo", "precision_wilson_hi")):
        if lo in table.columns and hi in table.columns:
            return lo, hi
    raise ValueError("no CI columns found; confirm the CSV's columns in ESPECIFICACION.md")


def most_seeds(table, **filters):
    for col, val in filters.items():
        table = table[table[col] == val]
    if table.empty:
        raise ValueError(f"no rows for {filters}")
    return table.loc[table.semilla.map(n_seeds).idxmax()]


def draw_temperature(ax, points, name):
    """points: {model: [(accuracy, lo, hi, at_limit, seeds) at temp 0.6, same at temp 1.0]}"""
    nudge = {}  # two close points: move the upper label up and the lower one down
    for i in (0, 1):
        o, e = points["orig"][i][0], points["p50c"][i][0]
        if abs(o - e) < 16:
            nudge[("orig", i)], nudge[("p50c", i)] = (9, -9) if o > e else (-9, 9)
    for model, color in (("orig", C_ORIG), ("p50c", C_P50C)):
        vals = points[model]
        shift = -0.03 if model == "orig" else 0.03
        ax.plot([shift, 1 + shift], [v[0] for v in vals], color=color, lw=1.5, zorder=2)
        for i, (y, lo, hi, limit, seeds) in enumerate(vals):
            x = i + shift
            point(ax, x, y, lo, hi, color, MARKERS["thinking"] if i == 0 else MARKERS["card"], seeds)
            side = -1 if i == 0 else 1
            ax.annotate(f"{fmt1(y)}%\n({fmt1(limit)}%\nat limit)", (x, y), xytext=(side * 8, nudge.get((model, i), 0)),
                        textcoords="offset points", ha="right" if i == 0 else "left", va="center",
                        fontsize=6.5, color=INK, linespacing=1.05)
    ax.set_xticks([0, 1], ["0.6\n(MIT config)", "1.0\n(model card)"])
    ax.set_xlim(-0.75, 1.75)
    ax.set_ylim(0, 80)
    ax.tick_params(axis="x", length=0)
    ax.text(0.5, 1.01, name, transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color=INK)


def fig6():
    arms = load("tabla_r2_math_brazos.csv")
    card = load("tabla_ficha_4sem_corridas.csv")
    card = card[card.semilla == "0 1 2 3"]
    math = {}
    for model in ("orig", "p50c"):
        a = one(arms, brazo=f"{model} · thinking MIT")
        c = one(card, brazo=f"{model} · thinking ficha Qwen (temp 1.0)")
        math[model] = [(a.precision_pct, a.precision_boot_lo, a.precision_boot_hi, a.al_limite_pct, n_seeds(a.semillas)),
                       (c.precision_pct, c.ic_lo, c.ic_hi, c.al_limite_pct, n_seeds(c.semilla))]

    final = (RES / FINAL_CARD_CSV).exists()
    other = load(FINAL_CARD_CSV if final else DRAFT_CARD_CSV)
    lo_col, hi_col = ci_cols(other)

    fig, axes = plt.subplots(1, 3, figsize=(WIDE, 3.5), sharey=True, gridspec_kw={"wspace": 0.08})
    draw_temperature(axes[0], math, "MATH-500")
    g06 = one(load("tabla_r2_mcnemar.csv"), A="orig · thinking MIT", B="p50c · thinking MIT")
    g10 = one(load("tabla_ficha_4sem_mcnemar.csv"), A="orig · thinking ficha Qwen (temp 1.0)",
              B="p50c · thinking ficha Qwen (temp 1.0)")
    # A is the original, so the signs flip to read as the edit's gain.
    axes[0].text(0.5, 0.985, "Gain from the edit (paired):\n"
                 f"temp 0.6: {signed(-g06.dif_A_menos_B_pts)} pts [{signed(-g06.dif_boot_hi)}, {signed(-g06.dif_boot_lo)}]\n"
                 f"temp 1.0: {signed(-g10.dif_A_menos_B_pts)} pts [{signed(-g10.dif_boot_hi)}, {signed(-g10.dif_boot_lo)}]",
                 transform=axes[0].transAxes, ha="center", va="top", fontsize=6.5, color=INK)

    for ax, (task, name) in zip(axes[1:], CARD_TASKS):
        pts = {}
        for model in ("orig", "p50c"):
            vals = []
            for suffix in ("thinking MIT (temp 0.6)", "thinking ficha Qwen (temp 1.0)"):
                r = most_seeds(other, tarea=task, brazo=f"{model} · {suffix}")
                vals.append((r.precision_pct, r[lo_col], r[hi_col], r.al_limite_pct, n_seeds(r.semilla)))
            pts[model] = vals
        draw_temperature(ax, pts, name if final else f"{name}\nPROVISIONAL: seed 0 only")
    axes[0].set_ylabel("Accuracy (%)")
    for ax in axes:
        ax.set_xlabel("Temperature")
    handles = [Line2D([], [], color=C_ORIG, lw=1.5, label="Original"),
               Line2D([], [], color=C_P50C, lw=1.5, label="Edited (p50c)")] + seed_legend()
    fig.legend(handles=handles, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 0.0))
    save(fig, "fig6")


# ---- Figure 7 -------------------------------------------------------------------------
FIG7_RETRY = {  # brazo -> (label, color, marker)
    "orig · thinking MIT (referencia, 1 intento)": ("Original (thinking)", C_ORIG, MARKERS["thinking"]),
    "A · reintento (hasta 3)": ("Retry ×3", C_ORIG, MARKERS["retry"]),
    "B · forzar respuesta": ("Force answer", C_ORIG, MARKERS["force"]),
    "p50c · thinking MIT (misma semilla 0)": ("Edited p50c (thinking)", C_P50C, MARKERS["thinking"]),
}
FIG7_NOTHINK = {
    "MATH-500 (100 fijos)": (("dia_nothink_mit100", "No-think (MIT sampling)", MARKERS["nothink_mit"]),
                             ("cero_edicion_no_thinking", "No-think (32k)", MARKERS["nothink_32k"])),
    "GSM8K (subconjunto 1)": (("r2_gsm8k_orig_nothink", "No-think (MIT sampling)", MARKERS["nothink_mit"]),),
}
FIG7_OFFSETS = {  # (task, label) -> (dx, dy, ha)
    ("MATH-500 (100 fijos)", "No-think (MIT sampling)"): (-8, 0, "right"),
    ("MATH-500 (100 fijos)", "No-think (32k)"): (-7, 0, "right"),
    ("MATH-500 (100 fijos)", "Edited p50c (thinking)"): (0, 36, "center"),
    ("MATH-500 (100 fijos)", "Original (thinking)"): (-8, -5, "right"),
    ("MATH-500 (100 fijos)", "Retry ×3"): (-8, 0, "right"),
    ("MATH-500 (100 fijos)", "Force answer"): (-8, 0, "right"),
    ("GSM8K (subconjunto 1)", "No-think (MIT sampling)"): (8, 0, "left"),
    ("GSM8K (subconjunto 1)", "Edited p50c (thinking)"): (-8, 0, "right"),
    ("GSM8K (subconjunto 1)", "Original (thinking)"): (-8, -5, "right"),
    ("GSM8K (subconjunto 1)", "Retry ×3"): (-8, 0, "right"),
    ("GSM8K (subconjunto 1)", "Force answer"): (8, 0, "left"),
}


def fig7():
    retry = load("tabla_r3_reintento.csv")
    runs = load("tabla_r2_corridas.csv")
    runs = runs[runs.semilla == "0"]
    fig, axes = plt.subplots(1, 2, figsize=(WIDE, 3.1), sharey=True, sharex=True, gridspec_kw={"wspace": 0.07})
    for ax, (task, name) in zip(axes, (("MATH-500 (100 fijos)", "MATH-500"),
                                       ("GSM8K (subconjunto 1)", "GSM8K (subset 1)"))):
        pts = []
        for r in retry[retry.tarea == task].itertuples():
            label, color, marker = FIG7_RETRY[r.brazo]
            pts.append((label, color, marker, r.tokens_totales_por_problema, r.precision_pct,
                        r.precision_wilson_lo, r.precision_wilson_hi))
        for prefix, label, marker in FIG7_NOTHINK[task]:
            r = one(runs, prefijo=prefix)
            pts.append((label, C_ORIG, marker, r.tokens_medios, r.precision_pct,
                        r.precision_wilson_lo, r.precision_wilson_hi))
        for label, color, marker, x, y, lo, hi in pts:
            point(ax, x, y, lo, hi, color, marker, seeds=1)
            dx, dy, ha = FIG7_OFFSETS[(task, label)]
            text = label if label.startswith("Original") else label.replace(" (", "\n(")
            ax.annotate(text, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                        fontsize=7, color=INK, linespacing=1.05)
        ax.set_xscale("log")
        ax.set_xlim(700, 45000)
        ax.set_ylim(0, 80)
        ax.set_xticks([1000, 3000, 10000, 30000], ["1,000", "3,000", "10,000", "30,000"])
        ax.minorticks_off()
        ax.text(0.5, 1.01, name, transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color=INK)
    axes[0].set_ylabel("Accuracy (%)")
    fig.supxlabel("Tokens generated per problem (incl. discarded attempts)", fontsize=8, color=INK, y=0.0)
    handles = [Line2D([], [], marker="o", ls="none", mec=C_ORIG, mfc="white", ms=5, label="Original"),
               Line2D([], [], marker="o", ls="none", mec=C_P50C, mfc="white", ms=5, label="Edited (p50c)")]
    fig.legend(handles=handles, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.02))
    save(fig, "fig7")


if __name__ == "__main__":
    for make in (fig1, fig2, fig3, fig4, fig5, fig6, fig7):
        make()
    print(f"Done: {OUT}")
