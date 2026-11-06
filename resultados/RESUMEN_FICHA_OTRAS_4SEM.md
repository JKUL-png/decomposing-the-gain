# Resumen: config de la ficha de Qwen en GSM8K (sub.1) e IFEval, semillas 0-3 (solo números)

Thinking con ficha = temp 1.0. Por semilla: Wilson 95%. Juntas: bootstrap por problema (10,000, semilla 20261109). McNemar exacto sobre parejas problema+semilla; Holm dentro de las 4 comparaciones de cada tarea (semillas del mismo problema no son independientes: p optimistas; mirar el IC bootstrap). orig temp 0.6 solo tiene semilla 0. No-think = muestreo MIT (8,192), regla estricta.

## GSM8K subconjunto 1

| Brazo | Semilla | n | Correctos | Precisión % (IC) | Al límite % | Correctas/terminadas | Tokens medios |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | 0 | 100 | 35 | 35.0 (26.4–44.7) | 63.0 | 35/37 | 26188 |
| orig · thinking ficha Qwen (temp 1.0) | 1 | 100 | 34 | 34.0 (25.5–43.7) | 64.0 | 33/36 | 26454 |
| orig · thinking ficha Qwen (temp 1.0) | 2 | 100 | 41 | 41.0 (31.9–50.8) | 55.0 | 41/45 | 24893 |
| orig · thinking ficha Qwen (temp 1.0) | 3 | 100 | 32 | 32.0 (23.7–41.7) | 65.0 | 32/35 | 26670 |
| **orig · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 142 | **35.5 (28.2–43.0)** | 61.8 | 141/153 | 26051 |
| p50c · thinking ficha Qwen (temp 1.0) | 0 | 100 | 55 | 55.0 (45.2–64.4) | 32.0 | 55/68 | 19803 |
| p50c · thinking ficha Qwen (temp 1.0) | 1 | 100 | 45 | 45.0 (35.6–54.8) | 41.0 | 44/59 | 22407 |
| p50c · thinking ficha Qwen (temp 1.0) | 2 | 100 | 49 | 49.0 (39.4–58.7) | 37.0 | 48/63 | 21859 |
| p50c · thinking ficha Qwen (temp 1.0) | 3 | 100 | 48 | 48.0 (38.5–57.7) | 36.0 | 48/64 | 21912 |
| **p50c · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 197 | **49.2 (41.0–57.2)** | 36.5 | 195/254 | 21495 |
| orig · thinking MIT (temp 0.6) | 0 | 100 | 16 | 16.0 (10.1–24.4) | 84.0 | 16/16 | 28145 |
| p50c · thinking MIT (temp 0.6) | 0 | 100 | 71 | 71.0 (61.5–79.0) | 7.0 | 71/93 | 11672 |
| p50c · thinking MIT (temp 0.6) | 1 | 100 | 68 | 68.0 (58.3–76.3) | 6.0 | 68/94 | 11947 |
| p50c · thinking MIT (temp 0.6) | 2 | 100 | 63 | 63.0 (53.2–71.8) | 7.0 | 63/93 | 11333 |
| p50c · thinking MIT (temp 0.6) | 3 | 100 | 68 | 68.0 (58.3–76.3) | 4.0 | 68/96 | 11554 |
| **p50c · thinking MIT (temp 0.6)** | 0–3 | 400 | 270 | **67.5 (59.8–75.0)** | 6.0 | 270/376 | 11627 |
| orig · no-think muestreo MIT | 0 | 100 | 54 | 54.0 (44.3–63.4) | 6.0 | 54/94 | 1205 |
| orig · no-think muestreo MIT | 1 | 100 | 51 | 51.0 (41.3–60.6) | 6.0 | 51/94 | 1261 |
| orig · no-think muestreo MIT | 2 | 100 | 58 | 58.0 (48.2–67.2) | 8.0 | 58/92 | 1594 |
| orig · no-think muestreo MIT | 3 | 100 | 50 | 50.0 (40.4–59.6) | 2.0 | 50/98 | 1158 |
| **orig · no-think muestreo MIT** | 0–3 | 400 | 213 | **53.2 (46.2–60.2)** | 5.5 | 213/378 | 1305 |

| A | B | Parejas | b | c | Dif. A−B pts (IC) | p exacto | p Holm |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 400 | 27 | 82 | -13.8 (-19.8…-7.8) | 1.3e-07 | 3.8e-07 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 100 | 21 | 2 | +19.0 (+11.0…+28.0) | 6.6e-05 | 0.00013 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 400 | 16 | 89 | -18.2 (-23.8…-12.8) | 1.9e-13 | 7.5e-13 |
| p50c · thinking ficha Qwen (temp 1.0) | orig · no-think muestreo MIT | 400 | 52 | 68 | -4.0 (-10.5…+2.5) | 0.17 | 0.17 |

## IFEval

| Brazo | Semilla | n | Correctos | Precisión % (IC) | Al límite % | Correctas/terminadas | Tokens medios |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | 0 | 100 | 58 | 58.0 (48.2–67.2) | 19.0 | 57/81 | 9766 |
| orig · thinking ficha Qwen (temp 1.0) | 1 | 100 | 51 | 51.0 (41.3–60.6) | 20.0 | 50/80 | 9707 |
| orig · thinking ficha Qwen (temp 1.0) | 2 | 100 | 50 | 50.0 (40.4–59.6) | 17.0 | 50/83 | 9234 |
| orig · thinking ficha Qwen (temp 1.0) | 3 | 100 | 55 | 55.0 (45.2–64.4) | 22.0 | 55/78 | 10814 |
| **orig · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 214 | **53.5 (46.5–60.5)** | 19.5 | 212/322 | 9880 |
| p50c · thinking ficha Qwen (temp 1.0) | 0 | 100 | 47 | 47.0 (37.5–56.7) | 0.0 | 47/100 | 3409 |
| p50c · thinking ficha Qwen (temp 1.0) | 1 | 100 | 44 | 44.0 (34.7–53.8) | 2.0 | 44/98 | 3867 |
| p50c · thinking ficha Qwen (temp 1.0) | 2 | 100 | 50 | 50.0 (40.4–59.6) | 1.0 | 50/99 | 4205 |
| p50c · thinking ficha Qwen (temp 1.0) | 3 | 100 | 45 | 45.0 (35.6–54.8) | 1.0 | 45/99 | 3823 |
| **p50c · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 186 | **46.5 (39.0–54.2)** | 1.0 | 186/396 | 3826 |
| orig · thinking MIT (temp 0.6) | 0 | 100 | 21 | 21.0 (14.2–30.0) | 69.0 | 21/31 | 23733 |
| p50c · thinking MIT (temp 0.6) | 0 | 100 | 58 | 58.0 (48.2–67.2) | 0.0 | 58/100 | 3310 |
| p50c · thinking MIT (temp 0.6) | 1 | 100 | 59 | 59.0 (49.2–68.1) | 1.0 | 59/99 | 3755 |
| p50c · thinking MIT (temp 0.6) | 2 | 100 | 63 | 63.0 (53.2–71.8) | 2.0 | 63/98 | 4001 |
| p50c · thinking MIT (temp 0.6) | 3 | 100 | 52 | 52.0 (42.3–61.5) | 1.0 | 52/99 | 3572 |
| **p50c · thinking MIT (temp 0.6)** | 0–3 | 400 | 232 | **58.0 (50.5–65.5)** | 1.0 | 232/396 | 3659 |
| orig · no-think muestreo MIT | 0 | 100 | 51 | 51.0 (41.3–60.6) | 1.0 | 51/99 | 294 |
| orig · no-think muestreo MIT | 1 | 100 | 52 | 52.0 (42.3–61.5) | 1.0 | 52/99 | 323 |
| orig · no-think muestreo MIT | 2 | 100 | 51 | 51.0 (41.3–60.6) | 0.0 | 51/100 | 226 |
| orig · no-think muestreo MIT | 3 | 100 | 51 | 51.0 (41.3–60.6) | 0.0 | 51/100 | 275 |
| **orig · no-think muestreo MIT** | 0–3 | 400 | 205 | **51.2 (43.2–59.2)** | 0.5 | 205/398 | 279 |

| A | B | Parejas | b | c | Dif. A−B pts (IC) | p exacto | p Holm |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 400 | 83 | 55 | +7.0 (+0.2…+13.8) | 0.021 | 0.042 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 100 | 43 | 6 | +37.0 (+25.0…+48.0) | 5.7e-08 | 2.3e-07 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 400 | 38 | 84 | -11.5 (-17.5…-5.8) | 3.8e-05 | 0.00011 |
| p50c · thinking ficha Qwen (temp 1.0) | orig · no-think muestreo MIT | 400 | 58 | 77 | -4.8 (-12.2…+2.5) | 0.12 | 0.12 |

