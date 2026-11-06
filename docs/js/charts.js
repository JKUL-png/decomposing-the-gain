/* Interactive figures. Bars are plain HTML, so they reflow on a phone; scatter plots are SVG redrawn at the real width. */
(function () {
  const F = window.BLOG.figures;
  const $ = (id) => document.getElementById(id);
  const n1 = (v) => {
    // One decimal, exact halves to even, as in the paper.
    const x = Math.round(Math.abs(v) * 1e6) / 1e6, s = x * 10, f = Math.floor(s);
    const r = Math.abs(s - f - 0.5) < 1e-9 ? (f % 2 ? f + 1 : f) : Math.round(s);
    return (r / 10).toFixed(1);
  };
  const sg = (v) => (v < 0 ? "−" : "+") + n1(v);
  const pc = (v) => n1(v) + "%";
  const int = (v) => Math.round(v).toLocaleString("en-US");
  const seedNote = (s) => (s === 4 ? "4 seeds" : s === 1 ? "1 seed" : `${s} seeds`);
  const h = (tag, cls, html) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html !== undefined) e.innerHTML = html;
    return e;
  };
  const NS = "http://www.w3.org/2000/svg";
  const s = (tag, a, text) => {
    const e = document.createElementNS(NS, tag);
    Object.entries(a || {}).forEach(([k, v]) => e.setAttribute(k, v));
    if (text !== undefined) e.textContent = text;
    return e;
  };

  function tabs(root, label, options, onPick, start) {
    const g = h("div", "seg");
    g.setAttribute("role", "group");
    g.setAttribute("aria-label", label);
    const set = (value) => {
      g.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.v === value)));
      onPick(value);
    };
    options.forEach(([value, text]) => {
      const b = h("button", "", text);
      b.type = "button";
      b.dataset.v = value;
      b.addEventListener("click", () => set(value));
      g.append(b);
    });
    root.append(g);
    return { el: g, set, start };
  }

  // rows: {label, value, lo, hi, cls, ghost, side}
  function bars(box, rows, max) {
    box.textContent = "";
    rows.forEach((r) => {
      const row = h("div", "bar-row");
      const top = h("div", "bar-top");
      top.append(h("span", "bar-name", r.label), h("span", "bar-val", r.text));
      const tr = h("div", "bar-track");
      const fill = h("div", `bar-fill ${r.cls}`);
      fill.style.width = `${(r.value / max) * 100}%`;
      tr.append(fill);
      if (r.lo !== undefined) {
        const ci = h("div", "bar-ci");
        ci.style.left = `${(r.lo / max) * 100}%`;
        ci.style.width = `${((r.hi - r.lo) / max) * 100}%`;
        tr.append(ci);
      }
      if (r.ghost !== undefined) {
        const gh = h("div", "bar-ghost");
        gh.style.left = `${(r.ghost / max) * 100}%`;
        tr.append(gh);
      }
      row.append(top, tr);
      if (r.side) row.append(h("div", "bar-side", r.side));
      box.append(row);
    });
    const ax = h("div", "bar-axis");
    [0, 0.25, 0.5, 0.75, 1].forEach((f) => {
      const t = h("span", "", String(Math.round(max * f)));
      t.style.left = `${f * 100}%`;
      ax.append(t);
    });
    box.append(ax);
  }

  function table(root, head, rows) {
    const d = h("details", "data");
    d.append(h("summary", "", "Data table"));
    const w = h("div", "table-wrap");
    const t = h("table");
    t.innerHTML = `<thead><tr>${head.map((c) => `<th>${c}</th>`).join("")}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join("")}</tr>`).join("")}</tbody>`;
    w.append(t);
    d.append(w);
    root.append(d);
  }

  const cls = (m) => (m === "p50c" ? "c-edit" : m === "placebo" ? "c-placebo" : "c-orig");
  const mark = (mode, r) => {
    const q = r * 1.25;
    if (mode === "nt_mit") return `M0 ${-q}L${q} 0L0 ${q}L${-q} 0Z`;
    if (mode === "force") return `M0 ${-q}L${q} ${r * 0.8}L${-q} ${r * 0.8}Z`;
    if (mode === "nt_32k") return `M${-q} ${-r * 0.8}L${q} ${-r * 0.8}L0 ${q}Z`;
    if (mode === "penalty" || mode === "retry") return `M${-r} ${-r}H${r}V${r}H${-r}Z`;
    if (mode === "card") {
      let p = "";
      for (let i = 0; i < 10; i++) {
        const a = (Math.PI / 5) * i - Math.PI / 2, d = i % 2 ? r * 0.6 : r * 1.5;
        p += `${i ? "L" : "M"}${(d * Math.cos(a)).toFixed(1)} ${(d * Math.sin(a)).toFixed(1)}`;
      }
      return p + "Z";
    }
    return `M${-r} 0a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
  };

  // pts: {x, y, lo, hi, model, mode, hollow, text}; o: {xs, xmin, xmax, ymax, xticks, xlabel, labels}
  function scatter(box, read, getPts, o) {
    let selected = null;
    function draw() {
      const pts = getPts();
      const W = Math.max(280, box.clientWidth), H = Math.round(Math.min(380, W * 0.82));
      const L = 30, R = 10, T = 8, B = 40;
      const X = (v) => L + o.scale(v) * (W - L - R), Y = (v) => T + (1 - v / o.ymax) * (H - T - B);
      const g = s("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": o.aria });
      for (let v = 0; v <= o.ymax; v += 20) {
        g.append(s("line", { x1: L, x2: W - R, y1: Y(v), y2: Y(v), class: "grid" }));
        g.append(s("text", { x: L - 6, y: Y(v) + 4, "text-anchor": "end", class: "tick" }, v));
      }
      o.xticks.forEach(([v, t]) => g.append(s("text", { x: X(v), y: H - B + 15, "text-anchor": "middle", class: "tick" }, t)));
      g.append(s("text", { x: (L + W - R) / 2, y: H - 6, "text-anchor": "middle", class: "tick" }, o.xlabel));
      pts.forEach((p) => {
        g.append(s("line", { x1: X(p.x), x2: X(p.x), y1: Y(p.lo), y2: Y(p.hi), class: `ci ${cls(p.model)}` }));
      });
      pts.forEach((p, i) => {
        const on = selected === i;
        const m = s("path", { d: mark(p.mode, on ? 6.5 : 5), transform: `translate(${X(p.x)} ${Y(p.y)})`, class: `pt ${cls(p.model)}${p.hollow ? " hollow" : ""}${on ? " on" : ""}` });
        g.append(m);
        const lab = o.labels && W >= 520 && o.labels[p.key];   // on small screens only the tappable points remain
        if (lab) g.append(s("text", { x: X(p.x) + lab[0], y: Y(p.y) + lab[1], "text-anchor": lab[2], class: "dl" }, p.short || p.text));
      });
      pts.forEach((p, i) => {
        const hit = s("circle", { cx: X(p.x), cy: Y(p.y), r: 17, class: "hit", tabindex: 0, role: "button", "aria-label": p.read });
        const pick = () => { selected = i; read.textContent = p.read; draw(); };
        hit.addEventListener("click", pick);
        hit.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); } });
        g.append(hit);
      });
      box.replaceChildren(g);
    }
    new ResizeObserver(() => { if (box.clientWidth) draw(); }).observe(box);
    draw();
    return { redraw: () => { selected = null; read.textContent = o.hint; draw(); } };
  }

  function legendMarks(root, items) {
    const l = h("div", "legend");
    items.forEach(([c, mode, text, hollow]) => {
      const e = h("span", "lg");
      const g = s("svg", { width: 18, height: 18, viewBox: "-9 -9 18 18", "aria-hidden": "true" });
      g.append(s("path", { d: mark(mode, 5), class: `pt ${c}${hollow ? " hollow" : ""}` }));
      e.append(g, document.createTextNode(text));
      l.append(e);
    });
    root.append(l);
  }

  /* Figure 1 */
  (function () {
    const root = $("fig1");
    const box = h("div", "plot"), read = h("p", "read", "Tap a point to see its numbers.");
    root.append(box, read);
    const pts = F.fig1.map((p) => ({
      key: p.label, x: p.limit, y: p.acc, lo: p.lo, hi: p.hi, model: p.model, mode: p.mode, hollow: p.seeds < 4, text: p.label,
      read: `${p.label}: ${pc(p.acc)} accuracy (CI ${n1(p.lo)}–${n1(p.hi)}), ${pc(p.limit)} at the limit, ${seedNote(p.seeds)}.`,
    }));
    pts.forEach((p) => {
      p.short = { "unedited · thinking": "unedited, thinking", "p50c · thinking": "p50c, thinking", "unedited · no-think, 32k": "no-think, 32k" }[p.key];
    });
    scatter(box, read, () => pts, {
      scale: (v) => v / 100, ymax: 80, xticks: [[0, "0"], [25, "25"], [50, "50"], [75, "75"], [100, "100"]], xlabel: "Responses hitting the token limit (%)",
      aria: "Accuracy against the share of responses at the token limit", hint: "Tap a point to see its numbers.",
      labels: { "unedited · thinking": [-12, 15, "end"], "p50c · thinking": [11, 4, "start"], "unedited · no-think, 32k": [2, -34, "middle"] },
    });
    legendMarks(root, [["c-orig", "thinking", "unedited"], ["c-edit", "thinking", "p50c"], ["c-placebo", "thinking", "placebo"], ["c-orig", "nt_mit", "no-think, MIT sampling"], ["c-orig", "nt_32k", "no-think, 32k"], ["c-orig", "penalty", "penalty change"], ["c-orig", "card", "model-card config"], ["c-orig", "thinking", "1–2 seeds", true]]);
    table(root, ["Configuration", "Accuracy %", "CI", "At limit %", "Seeds"], F.fig1.map((p) => [p.label, n1(p.acc), `${n1(p.lo)}–${n1(p.hi)}`, n1(p.limit), p.seeds]));
  })();

  /* Figure 2 */
  (function () {
    const root = $("fig2");
    const lo = -10, hi = 50, X = (v) => ((v - lo) / (hi - lo)) * 100;
    const box = h("div", "div-bars");
    F.fig2.forEach((r) => {
      const row = h("div", "bar-row");
      const top = h("div", "bar-top");
      top.append(h("span", "bar-name", r.label), h("span", "bar-val", `${sg(r.total)} (${sg(r.lo)}…${sg(r.hi)})`));
      const tr = h("div", "bar-track plain");
      const up = h("div", "seg-up"), dn = h("div", "seg-down"), z = h("div", "zero");
      up.style.left = `${X(0)}%`; up.style.width = `${X(Math.max(0, r.looped)) - X(0)}%`;
      const neg = Math.min(0, r.finished) + Math.min(0, r.looped);
      dn.style.left = `${X(neg)}%`; dn.style.width = `${X(0) - X(Math.min(0, r.finished))}%`;
      z.style.left = `${X(0)}%`;
      tr.append(up, dn, z);
      row.append(top, tr);
      box.append(row);
    });
    root.append(box);
    root.append(h("div", "legend", '<span class="lg"><i class="sw sw-up"></i>Problems where the baseline hit the limit</span><span class="lg"><i class="sw sw-down"></i>Problems the baseline already finished</span>'));
    table(root, ["Variant", "Total pts", "CI", "Looped", "Finished", "Seeds"], F.fig2.map((r) => [r.label, sg(r.total), `${sg(r.lo)}…${sg(r.hi)}`, sg(r.looped), sg(r.finished), r.seeds]));
  })();

  /* Figure 3 */
  (function () {
    const root = $("fig3");
    const box = h("div"), out = h("p", "big-read");
    const names = ["unedited · thinking (OT)", "unedited · no-think (NT)", "p50c · thinking (ED)"], css = ["c-orig", "c-orig hatch", "c-edit"];
    const pick = (i) => {
      const c = F.fig3[+i];
      bars(box, c.arms.map((a, k) => ({ label: names[k] + (a.seeds < 4 ? " · 1 seed" : ""), value: a.acc, lo: a.lo, hi: a.hi, cls: css[k], text: pc(a.acc) })), 80);
      out.innerHTML = `Recovered: <strong>${Math.round(c.fraction * 100)}%</strong> <span>(${Math.round(c.lo * 100)}–${Math.round(c.hi * 100)}%)</span>`;
    };
    const t = tabs(root, "Benchmark and profile", F.fig3.map((c, i) => [String(i), c.case.replace(", no-think", " ·").replace(" subset 1", "")]), pick);
    root.append(out, box);
    t.set("0");
    table(root, ["Benchmark", "OT %", "NT %", "ED %", "Recovered"], F.fig3.map((c) => [c.case, n1(c.arms[0].acc), n1(c.arms[1].acc), n1(c.arms[2].acc), `${Math.round(c.fraction * 100)}% (${Math.round(c.lo * 100)}–${Math.round(c.hi * 100)}%)`]));
  })();

  /* Figure 4 */
  (function () {
    const root = $("fig4");
    const box = h("div"), modeBox = h("div");
    const MODES = { thinking: "Thinking", nt_mit: "No-think, MIT sampling", nt_32k: "No-think, 32k" };
    let bench = "math", mode = "thinking", modeTabs;
    const draw = () => {
      const rows = F.fig4[bench].filter((a) => a.mode === mode).sort((a) => (a.model === "orig" ? -1 : 1));
      bars(box, rows.map((a) => ({ label: a.label + (a.seeds < 4 ? " · 1 seed" : ""), value: a.acc, lo: a.lo, hi: a.hi, cls: cls(a.model), text: pc(a.acc) })), 80);
    };
    const setModes = () => {
      const avail = [...new Set(F.fig4[bench].map((a) => a.mode))];
      if (!avail.includes(mode)) mode = "thinking";
      modeBox.textContent = "";
      modeTabs = tabs(modeBox, "Mode", avail.map((m) => [m, MODES[m]]), (v) => { mode = v; draw(); });
      modeTabs.set(mode);
    };
    const t = tabs(root, "Benchmark", [["math", "MATH-500"], ["gsm8k", "GSM8K"], ["ifeval", "IFEval"]], (v) => { bench = v; setModes(); });
    root.append(modeBox, box);
    t.set("math");
    const all = ["math", "gsm8k", "ifeval"].flatMap((k) => F.fig4[k].map((a) => [k === "math" ? "MATH-500" : k === "gsm8k" ? "GSM8K subset 1" : "IFEval", a.label, n1(a.acc), `${n1(a.lo)}–${n1(a.hi)}`, a.seeds]));
    table(root, ["Benchmark", "Configuration", "Accuracy %", "CI", "Seeds"], all);
  })();

  /* Figure 5 */
  (function () {
    const root = $("fig5");
    const a = h("div"), b = h("div");
    const name = (p) => `${p.label} · ${seedNote(p.seeds)}`;
    root.append(h("p", "panel", "Accuracy (%)"), a, h("p", "panel", "Responses hitting the 32,768-token limit (%)"), b);
    bars(a, F.fig5.arms.map((p) => ({ label: name(p), value: p.acc, lo: p.lo, hi: p.hi, cls: cls(p.model), text: pc(p.acc) })), 80);
    bars(b, F.fig5.arms.map((p) => ({ label: p.label, value: p.limit, cls: cls(p.model), text: pc(p.limit) })), 100);
    root.append(h("p", "read", `Paired, on the same 2 seeds: the real edit is ${sg(F.fig5.vs_edit)} points above the placebo (CI ${sg(F.fig5.vs_edit_lo)}…${sg(F.fig5.vs_edit_hi)}). These do not equal the difference between bar heights, because two of the bars use 4 seeds.`));
    table(root, ["Model", "Accuracy %", "CI", "At limit %", "Seeds"], F.fig5.arms.map((p) => [p.label, n1(p.acc), `${n1(p.lo)}–${n1(p.hi)}`, n1(p.limit), p.seeds]));
  })();

  /* Figure 6 */
  (function () {
    const root = $("fig6");
    const box = h("div"), out = h("p", "big-read");
    let bench = "math", temp = 0;
    const draw = () => {
      const get = (m, md) => F.fig6[bench].find((a) => a.model === m && a.mode === md);
      const now = temp ? "card" : "thinking", other = temp ? "thinking" : "card";
      bars(box, ["orig", "p50c"].map((m) => {
        const a = get(m, now), g = get(m, other);
        return { label: `${m === "orig" ? "unedited" : "p50c"}${a.seeds < 4 ? " · 1 seed" : ""}`, value: a.acc, lo: a.lo, hi: a.hi, cls: cls(m), text: pc(a.acc), ghost: g.acc, side: `${pc(a.limit)} at the limit` };
      }), 80);
      const q = F.fig6.gain[bench][temp];
      out.innerHTML = `Gain from the edit: <strong>${sg(q.pts)}</strong> <span>points (${sg(q.lo)}…${sg(q.hi)})${q.seed0 ? ", seed 0 only" : ""}</span>`;
    };
    const t1 = tabs(root, "Benchmark", [["math", "MATH-500"], ["gsm8k", "GSM8K"], ["ifeval", "IFEval"]], (v) => { bench = v; draw(); });
    const t2 = tabs(root, "Temperature", [["0", "Temp 0.6 (MIT config)"], ["1", "Temp 1.0 (model card)"]], (v) => { temp = +v; draw(); });
    root.append(out, box);
    t1.el.querySelector("button").setAttribute("aria-pressed", "true");
    t2.set("0");
    const all = ["math", "gsm8k", "ifeval"].flatMap((k) => F.fig6[k].map((a) => [k === "math" ? "MATH-500" : k === "gsm8k" ? "GSM8K subset 1" : "IFEval", a.mode === "card" ? "1.0" : "0.6", a.model === "orig" ? "unedited" : "p50c", n1(a.acc), `${n1(a.lo)}–${n1(a.hi)}`, n1(a.limit), a.seeds]));
    table(root, ["Benchmark", "Temp", "Model", "Accuracy %", "CI", "At limit %", "Seeds"], all);
  })();

  /* Figure 7 */
  (function () {
    const root = $("fig7");
    const box = h("div", "plot"), hint = "Tap a point to see its numbers.", read = h("p", "read", hint);
    let task = "math", chart;
    const lg = (v) => (Math.log10(v) - Math.log10(700)) / (Math.log10(45000) - Math.log10(700));
    const pts = () => F.fig7[task].map((p) => ({
      key: p.label, x: p.tokens, y: p.acc, lo: p.lo, hi: p.hi, model: p.model, mode: p.mode, hollow: true, text: p.label,
      read: `${p.label}: ${pc(p.acc)} accuracy (Wilson ${n1(p.lo)}–${n1(p.hi)}), ${int(p.tokens)} tokens per problem.`,
    }));
    const t = tabs(root, "Benchmark", [["math", "MATH-500"], ["gsm8k", "GSM8K"]], (v) => { task = v; if (chart) chart.redraw(); });
    root.append(box, read);
    t.el.querySelector("button").setAttribute("aria-pressed", "true");
    chart = scatter(box, read, pts, {
      scale: lg, ymax: 80, xticks: [[1000, "1,000"], [3000, "3,000"], [10000, "10,000"], [30000, "30,000"]], xlabel: "Tokens per problem, incl. discarded attempts (log scale)",
      aria: "Accuracy against tokens per problem", hint,
    });
    legendMarks(root, [["c-orig", "thinking", "unedited thinking", true], ["c-edit", "thinking", "p50c thinking", true], ["c-orig", "retry", "A · retry", true], ["c-orig", "force", "B · force answer", true], ["c-orig", "nt_mit", "no-think, MIT sampling", true], ["c-orig", "nt_32k", "no-think, 32k (MATH-500 only)", true]]);
    const all = ["math", "gsm8k"].flatMap((k) => F.fig7[k].map((p) => [k === "math" ? "MATH-500" : "GSM8K subset 1", p.label, n1(p.acc), `${n1(p.lo)}–${n1(p.hi)}`, int(p.tokens)]));
    table(root, ["Benchmark", "Arm", "Accuracy %", "Wilson CI", "Tokens"], all);
  })();

  /* Citation */
  const copy = $("copy");
  if (copy) copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("bibtex").textContent);
      copy.textContent = "Copied";
    } catch (e) {
      copy.textContent = "Select the text to copy";
    }
    setTimeout(() => { copy.textContent = "Copy citation"; }, 1800);
  });
})();
