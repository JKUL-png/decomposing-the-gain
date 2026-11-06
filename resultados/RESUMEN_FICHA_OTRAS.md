# Resumen: config de la ficha de Qwen en GSM8K (sub.1) e IFEval, semilla 0 (solo números)

Thinking con ficha = temp 1.0; referencias en semilla 0. Wilson 95% por corrida; McNemar exacto; Holm dentro de las 4 comparaciones de cada tarea; bootstrap por problema (10,000, semilla 20261108). No-think = muestreo MIT (8,192), regla estricta.

## GSM8K subconjunto 1

| Brazo | Correctos | Precisión % (Wilson) | Al límite % | Correctas/terminadas | Tokens medios |
|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | 35 | 35.0 (26.4–44.7) | 63.0 | 35/37 | 26188 |
| p50c · thinking ficha Qwen (temp 1.0) | 55 | 55.0 (45.2–64.4) | 32.0 | 55/68 | 19803 |
| orig · thinking MIT (temp 0.6) | 16 | 16.0 (10.1–24.4) | 84.0 | 16/16 | 28145 |
| p50c · thinking MIT (temp 0.6) | 71 | 71.0 (61.5–79.0) | 7.0 | 71/93 | 11672 |
| orig · no-think muestreo MIT | 54 | 54.0 (44.3–63.4) | 6.0 | 54/94 | 1205 |

| A | B | b | c | Dif. A−B pts (IC) | p exacto | p Holm |
|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 3 | 23 | -20.0 (-29.0…-11.0) | 8.8e-05 | 0.00026 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 21 | 2 | +19.0 (+11.0…+28.0) | 6.6e-05 | 0.00026 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 1 | 17 | -16.0 (-24.0…-9.0) | 0.00014 | 0.00029 |
| p50c · thinking ficha Qwen (temp 1.0) | orig · no-think muestreo MIT | 13 | 12 | +1.0 (-9.0…+11.0) | 1 | 1 |

## IFEval

| Brazo | Correctos | Precisión % (Wilson) | Al límite % | Correctas/terminadas | Tokens medios |
|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | 58 | 58.0 (48.2–67.2) | 19.0 | 57/81 | 9766 |
| p50c · thinking ficha Qwen (temp 1.0) | 47 | 47.0 (37.5–56.7) | 0.0 | 47/100 | 3409 |
| orig · thinking MIT (temp 0.6) | 21 | 21.0 (14.2–30.0) | 69.0 | 21/31 | 23733 |
| p50c · thinking MIT (temp 0.6) | 58 | 58.0 (48.2–67.2) | 0.0 | 58/100 | 3310 |
| orig · no-think muestreo MIT | 51 | 51.0 (41.3–60.6) | 1.0 | 51/99 | 294 |

| A | B | b | c | Dif. A−B pts (IC) | p exacto | p Holm |
|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 24 | 13 | +11.0 (-1.0…+23.0) | 0.099 | 0.2 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 43 | 6 | +37.0 (+25.0…+48.0) | 5.7e-08 | 2.3e-07 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 6 | 17 | -11.0 (-20.0…-2.0) | 0.035 | 0.1 |
| p50c · thinking ficha Qwen (temp 1.0) | orig · no-think muestreo MIT | 14 | 18 | -4.0 (-15.0…+7.0) | 0.6 | 0.6 |

