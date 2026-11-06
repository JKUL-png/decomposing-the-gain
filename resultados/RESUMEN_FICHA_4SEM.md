# Resumen: config de la ficha de Qwen, semillas 0-3 (solo números)

MATH-500, 100 fijos, thinking. Ficha = temp 1.0; referencias = config MIT (temp 0.6). Por semilla: Wilson 95%. Juntas: bootstrap por problema (10,000, semilla 20261107). McNemar exacto sobre parejas problema+semilla; Holm dentro de las 3 comparaciones (las semillas del mismo problema no son independientes: p optimistas; mirar el IC bootstrap).

## 1. Por semilla y juntas

| Brazo | Semilla | n | Correctos | Precisión % (IC) | Al límite % | Correctas/terminadas | Tokens medios |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | 0 | 100 | 18 | 18.0 (11.7–26.7) | 82.0 | 18/18 | 29747 |
| orig · thinking ficha Qwen (temp 1.0) | 1 | 100 | 13 | 13.0 (7.8–21.0) | 87.0 | 13/13 | 30022 |
| orig · thinking ficha Qwen (temp 1.0) | 2 | 100 | 23 | 23.0 (15.8–32.2) | 77.0 | 23/23 | 29352 |
| orig · thinking ficha Qwen (temp 1.0) | 3 | 100 | 17 | 17.0 (10.9–25.5) | 83.0 | 17/17 | 29526 |
| **orig · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 71 | **17.8 (12.0–24.0)** | 82.2 | 71/71 | 29662 |
| p50c · thinking ficha Qwen (temp 1.0) | 0 | 100 | 28 | 28.0 (20.1–37.5) | 63.0 | 28/37 | 26141 |
| p50c · thinking ficha Qwen (temp 1.0) | 1 | 100 | 28 | 28.0 (20.1–37.5) | 66.0 | 28/34 | 26788 |
| p50c · thinking ficha Qwen (temp 1.0) | 2 | 100 | 31 | 31.0 (22.8–40.6) | 63.0 | 31/37 | 27038 |
| p50c · thinking ficha Qwen (temp 1.0) | 3 | 100 | 28 | 28.0 (20.1–37.5) | 65.0 | 28/35 | 27061 |
| **p50c · thinking ficha Qwen (temp 1.0)** | 0–3 | 400 | 115 | **28.7 (21.2–37.0)** | 64.2 | 115/143 | 26757 |
| orig · thinking MIT (temp 0.6) | 0 | 100 | 7 | 7.0 (3.4–13.7) | 93.0 | 7/7 | 31039 |
| orig · thinking MIT (temp 0.6) | 1 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 | 9/9 | 30665 |
| orig · thinking MIT (temp 0.6) | 2 | 100 | 6 | 6.0 (2.8–12.5) | 94.0 | 6/6 | 31091 |
| orig · thinking MIT (temp 0.6) | 3 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 | 9/9 | 30284 |
| **orig · thinking MIT (temp 0.6)** | 0–3 | 400 | 31 | **7.8 (4.0–12.0)** | 92.2 | 31/31 | 30770 |
| p50c · thinking MIT (temp 0.6) | 0 | 100 | 51 | 51.0 (41.3–60.6) | 36.0 | 51/64 | 21899 |
| p50c · thinking MIT (temp 0.6) | 1 | 100 | 51 | 51.0 (41.3–60.6) | 28.0 | 51/72 | 21573 |
| p50c · thinking MIT (temp 0.6) | 2 | 100 | 50 | 50.0 (40.4–59.6) | 29.0 | 50/71 | 21650 |
| p50c · thinking MIT (temp 0.6) | 3 | 100 | 53 | 53.0 (43.3–62.5) | 24.0 | 53/76 | 20621 |
| **p50c · thinking MIT (temp 0.6)** | 0–3 | 400 | 205 | **51.2 (43.0–59.5)** | 29.2 | 205/283 | 21436 |

## 2. McNemar (b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B pts (IC bootstrap) | p exacto | p Holm |
|---|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | 400 | 9 | 53 | -11.0 (-15.2…-7.0) | 1.1e-08 | 2.1e-08 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | 400 | 53 | 13 | +10.0 (+5.2…+15.0) | 7.2e-07 | 7.2e-07 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | 400 | 6 | 96 | -22.5 (-28.5…-16.8) | 5.7e-22 | 1.7e-21 |

## 3. Ganancia A−B en dos grupos (según si B llegó al límite)

| A | B | Dif. total | B al límite: parejas | …contribución pts | B terminó: parejas | …contribución pts |
|---|---|---|---|---|---|---|
| orig · thinking ficha Qwen (temp 1.0) | p50c · thinking ficha Qwen (temp 1.0) | -11.0 | 257 | +1.8 | 143 | -12.8 |
| orig · thinking ficha Qwen (temp 1.0) | orig · thinking MIT (temp 0.6) | +10.0 | 369 | +13.2 | 31 | -3.2 |
| p50c · thinking ficha Qwen (temp 1.0) | p50c · thinking MIT (temp 0.6) | -22.5 | 117 | +1.0 | 283 | -23.5 |
