# Resumen: config de la ficha de Qwen (solo números)

MATH-500, 100 fijos, semilla 0, thinking. Ficha = temp 1.0, top_p 0.95, top_k 20, presence 1.5, rep 1.0, 32,768. IC por corrida: Wilson 95%. McNemar exacto; p Holm dentro de las 3 comparaciones. Bootstrap por problema (10,000, semilla 20261106).

## 1. Corridas

| Brazo | Prefijo | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron | Correctas entre terminadas | Tokens medios | Min |
|---|---|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | cero_edicion_ficha_qwen | 100 | 18 | 18.0 (11.7–26.7) | 82.0 (73.3–88.3) | 18 | 18 | 29747 | 51.6 |
| p50c · thinking ficha Qwen (temp 1.0) | r2_ed_ficha_qwen | 100 | 28 | 28.0 (20.1–37.5) | 63.0 (53.2–71.8) | 37 | 28 | 26141 | 44.1 |
| orig · thinking MIT (temp 0.6) | linea_base_vllm | 100 | 7 | 7.0 (3.4–13.7) | 93.0 (86.3–96.6) | 7 | 7 | 31039 | 59.5 |
| p50c · thinking MIT (temp 0.6) | r2_ed_think | 100 | 51 | 51.0 (41.3–60.6) | 36.0 (27.3–45.8) | 64 | 51 | 21899 | 33.7 |

## 2. McNemar (b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B pts (IC bootstrap) | p exacto | p Holm |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 100 | 2 | 12 | -10.0 (-17.0…-3.0) | 0.013 | 0.025 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 100 | 14 | 3 | +11.0 (+3.0…+19.0) | 0.013 | 0.025 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 100 | 2 | 25 | -23.0 (-32.0…-14.0) | 5.6e-06 | 1.7e-05 |

## 3. Ganancia A−B en dos grupos (según si B llegó al límite)

| A | B | Dif. total | B al límite: parejas | …contribución pts | B terminó: parejas | …contribución pts |
|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | -10.0 | 63 | +2.0 | 37 | -12.0 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | +11.0 | 93 | +14.0 | 7 | -3.0 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | -23.0 | 36 | +1.0 | 64 | -24.0 |
