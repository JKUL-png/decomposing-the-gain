/* Replays real responses on one shared clock, so all arms advance at the same token rate. */
(function () {
  const data = window.BLOG, MAX = data.maxTokens, SECONDS = 16, SHOW = 2200;
  const NAMES = { original: "unedited · thinking", edited: "p50c · thinking", nothink: "unedited · no-think, 32k" };
  const CHIPS = { edit_still_loops: "p50c hits the limit too", nothink_wrong: "No-think is wrong" };
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => Math.round(n).toLocaleString("en-US");
  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const MATH = /\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\([\s\S]+?\\\)|\$[^$\n]+?\$/g;
  const cache = new Map();
  let example = data.examples[0], arm = "original", t = 0, playing = false, last = 0, lastScreen = 0;

  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

  function formula(raw) {
    if (cache.has(raw)) return cache.get(raw);
    const display = raw.startsWith("$$") || raw.startsWith("\\[");
    const body = raw.replace(/^\$\$|\$\$$|^\$|\$$|^\\\[|\\\]$|^\\\(|\\\)$/g, "");
    let html;
    try {
      html = window.katex.renderToString(body, { displayMode: display, throwOnError: true, output: "html" });
    } catch (e) {
      html = esc(raw);   // a formula the model left broken stays as plain text
    }
    cache.set(raw, html);
    return html;
  }

  function withMath(text) {
    if (!window.katex) return esc(text);
    let out = "", at = 0;
    for (const m of text.matchAll(MATH)) {
      out += esc(text.slice(at, m.index)) + formula(m[0]);
      at = m.index + m[0].length;
    }
    return out + esc(text.slice(at));
  }

  // Cut on a line start, so a formula is never paired across the cut.
  function lastLines(s, n) {
    if (s.length <= n) return s;
    const cut = s.slice(-n), line = cut.indexOf("\n");
    return line === -1 ? cut : cut.slice(line + 1);
  }

  // What the selected arm has written by the time the clock reaches `tokens`.
  function textAt(a, tokens) {
    const c = Math.min(1, tokens / a.tokens) * a.chars;
    const head = a.head.length, loopStart = a.loop ? a.loop.start : a.chars - a.tail.length;
    const preStart = loopStart - a.pre.length;
    if (c <= head) return { before: a.head.slice(0, c), skipped: 0, after: "", reps: 0 };
    const skipped = Math.max(0, Math.min(c, preStart) - head);
    let after = "", reps = 0;
    if (a.loop) {
      after = a.pre.slice(0, Math.max(0, c - preStart));
      if (c >= loopStart) {
        const done = (c - loopStart) / a.loop.period;
        reps = Math.floor(done);
        const keep = Math.min(reps, Math.ceil(SHOW / a.loop.period));
        after += a.loop.unit.repeat(keep) + a.loop.unit.slice(0, (done - reps) * a.loop.period);
      }
    } else {
      after = a.tail.slice(0, Math.max(0, c - loopStart));
    }
    return { before: a.head, skipped, after, reps };
  }

  function drawScreen() {
    const a = example.arms[arm], s = textAt(a, t);
    let html = "";
    if (s.skipped > 0) {
      if (s.after.length < SHOW) html += `<span class="part">${withMath(lastLines(s.before, 500))}</span>`;
      html += `<span class="part skip">[ ${fmt(s.skipped)} characters skipped ]</span>`;
    } else {
      html += `<span class="part">${withMath(s.before)}</span>`;
    }
    if (s.after) html += `<span class="part">${withMath(lastLines(s.after, SHOW))}</span>`;
    $("screen").innerHTML = html;
    $("reps").textContent = s.reps >= 1 ? `repeated ×${fmt(s.reps)}` : "";
  }

  function answerHTML(v) {
    return /^[A-Za-z ]+$/.test(v) ? esc(v) : withMath(`$${v}$`);
  }

  function statusHTML(a, name) {
    if (a.limit) return `${esc(name)}: stopped by the limit at ${fmt(a.tokens)} tokens, with no answer.`;
    const shown = a.answer === null ? "no boxed answer" : answerHTML(a.answer);
    const verdict = a.correct ? "Correct." : `Wrong, the correct answer is ${answerHTML(example.gold)}.`;
    return `${esc(name)}: finished at ${fmt(a.tokens)} tokens. Answer: ${shown}. ${verdict}`;
  }

  function draw(force) {
    Object.keys(NAMES).forEach((k) => {
      const a = example.arms[k], used = Math.min(t, a.tokens), done = t >= a.tokens;
      const lane = document.querySelector(`.lane[data-arm="${k}"]`);
      lane.querySelector(".fill").style.width = `${(used / MAX) * 100}%`;
      lane.querySelector(".lane-val").textContent = done
        ? `${fmt(a.tokens)} · ${a.limit ? "no answer" : a.correct ? "correct ✓" : "wrong ✗"}`
        : `≈ ${fmt(used)}`;
    });
    const now = performance.now();
    if (force || now - lastScreen > 90) { drawScreen(); lastScreen = now; }
    const a = example.arms[arm];
    const html = t >= a.tokens ? statusHTML(a, NAMES[arm]) : `${esc(NAMES[arm])} is still writing…`;
    if ($("status").dataset.html !== html) { $("status").innerHTML = html; $("status").dataset.html = html; }
    $("clock").textContent = `${fmt(t)} / ${fmt(MAX)} tokens`;
    $("play").textContent = playing ? "Pause" : t >= MAX ? "Replay" : "Play";
  }

  function frame(now) {
    if (!playing) return;
    t = Math.min(MAX, t + ((now - last) / 1000) * (MAX / SECONDS));
    last = now;
    if (t >= MAX) playing = false;
    draw(t >= MAX);
    if (playing) requestAnimationFrame(frame);
  }

  function play() {
    if (calm) { t = MAX; playing = false; draw(true); return; }
    if (t >= MAX) t = 0;
    playing = true;
    last = performance.now();
    requestAnimationFrame(frame);
    draw(true);
  }
  function pause() { playing = false; draw(true); }

  function pressed(root, el) {
    root.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === el)));
  }

  function choose(e, button) {
    example = e;
    pressed($("chips"), button);
    $("problem").innerHTML = withMath(e.problem);
    t = 0;
    play();
  }

  data.examples.forEach((e, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = CHIPS[e.category] || `Level ${e.level} · ${e.subject}`;
    b.setAttribute("aria-pressed", String(i === 0));
    b.addEventListener("click", () => choose(e, b));
    $("chips").append(b);
  });

  Object.keys(NAMES).forEach((k) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "lane";
    b.dataset.arm = k;
    b.setAttribute("aria-pressed", String(k === arm));
    b.innerHTML = '<span class="lane-top"><span class="lane-name"></span><span class="lane-val"></span></span><span class="track"><span class="fill"></span></span>';
    b.querySelector(".lane-name").textContent = NAMES[k];
    b.addEventListener("click", () => { arm = k; pressed($("race"), b); draw(true); });
    $("race").append(b);
  });

  $("play").addEventListener("click", () => (playing ? pause() : play()));
  $("restart").addEventListener("click", () => { t = 0; play(); });
  $("problem").innerHTML = withMath(example.problem);

  if (calm) { t = MAX; draw(true); return; }
  draw(true);
  new IntersectionObserver((entries, seen) => {
    if (entries[0].isIntersecting) { seen.disconnect(); play(); }
  }, { threshold: 0.3 }).observe($("player"));
})();
