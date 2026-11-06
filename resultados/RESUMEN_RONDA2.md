# Resumen ronda 2 (solo números, sin interpretar)

**Regla principal: estricta** (en no-thinking cuenta solo si NO llegó al límite de tokens). MATH-500: mismos 100 problemas fijos (salvo la tabla de 500). Modelos: orig = Qwen3.5-0.8B; p50c = edición del MIT (la de 48.1% en su informe, reconstruida con hash verificado); placebo = edición aleatoria de rango 1, mismos tensores y columnas, misma norma. IC por corrida: Wilson 95%. IC agrupado y de diferencias: bootstrap por problema (10000, semilla fija). Pruebas pareadas: McNemar exacto bilateral sobre parejas problema+semilla comunes; p ajustado por Holm dentro de la tabla (las semillas del mismo problema no son independientes).

## 1. Corridas individuales

| Prefijo | Semilla | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron | Precisión entre las que terminaron % (Wilson) | Tokens medios | Min |
|---|---|---|---|---|---|---|---|---|---|
| linea_base_vllm | 0 | 100 | 7 | 7.0 (3.4–13.7) | 93.0 (86.3–96.6) | 7 | 100.0 (64.6–100.0) | 31039 | 59.5 |
| linea_base_vllm | 1 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 9 | 100.0 (70.1–100.0) | 30665 | 54.4 |
| linea_base_vllm | 2 | 100 | 6 | 6.0 (2.8–12.5) | 94.0 (87.5–97.2) | 6 | 100.0 (61.0–100.0) | 31091 | 55.2 |
| linea_base_vllm | 3 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 9 | 100.0 (70.1–100.0) | 30284 | 53.5 |
| dia_nothink_mit100 | 0 | 100 | 50 | 50.0 (40.4–59.6) | 25.0 (17.5–34.3) | 75 | 66.7 (55.4–76.3) | 3352 | 2.4 |
| r2_orig_nothinkmit | 1 | 100 | 45 | 45.0 (35.6–54.8) | 29.0 (21.0–38.5) | 71 | 63.4 (51.8–73.6) | 3399 | 2.6 |
| r2_orig_nothinkmit | 2 | 100 | 40 | 40.0 (30.9–49.8) | 37.0 (28.2–46.8) | 63 | 63.5 (51.1–74.3) | 3786 | 4.4 |
| r2_orig_nothinkmit | 3 | 100 | 46 | 46.0 (36.6–55.7) | 25.0 (17.5–34.3) | 75 | 61.3 (50.0–71.5) | 3013 | 4.6 |
| cero_edicion_no_thinking | 0 | 100 | 48 | 48.0 (38.5–57.7) | 14.0 (8.5–22.1) | 86 | 55.8 (45.3–65.8) | 8506 | 14.2 |
| cero_edicion_no_thinking | 1 | 100 | 49 | 49.0 (39.4–58.7) | 15.0 (9.3–23.3) | 85 | 57.6 (47.0–67.6) | 8598 | 12.5 |
| cero_edicion_no_thinking | 2 | 100 | 57 | 57.0 (47.2–66.3) | 11.0 (6.3–18.6) | 89 | 64.0 (53.7–73.2) | 7949 | 11.2 |
| cero_edicion_no_thinking | 3 | 100 | 52 | 52.0 (42.3–61.5) | 8.0 (4.1–15.0) | 92 | 56.5 (46.3–66.2) | 6767 | 9.5 |
| r2_ed_think | 0 | 100 | 51 | 51.0 (41.3–60.6) | 36.0 (27.3–45.8) | 64 | 79.7 (68.3–87.7) | 21899 | 33.7 |
| r2_ed_think | 1 | 100 | 51 | 51.0 (41.3–60.6) | 28.0 (20.1–37.5) | 72 | 70.8 (59.5–80.1) | 21573 | 32.4 |
| r2_ed_think | 2 | 100 | 50 | 50.0 (40.4–59.6) | 29.0 (21.0–38.5) | 71 | 70.4 (59.0–79.8) | 21650 | 32.8 |
| r2_ed_think | 3 | 100 | 53 | 53.0 (43.3–62.5) | 24.0 (16.7–33.2) | 76 | 69.7 (58.7–78.9) | 20621 | 30.5 |
| r2_ed_nothinkmit | 0 | 100 | 52 | 52.0 (42.3–61.5) | 26.0 (18.4–35.4) | 74 | 70.3 (59.1–79.5) | 3528 | 2.4 |
| r2_ed_nothinkmit | 1 | 100 | 45 | 45.0 (35.6–54.8) | 28.0 (20.1–37.5) | 72 | 62.5 (51.0–72.8) | 3619 | 2.5 |
| r2_ed_nothinkmit | 2 | 100 | 48 | 48.0 (38.5–57.7) | 29.0 (21.0–38.5) | 71 | 67.6 (56.1–77.3) | 3433 | 2.2 |
| r2_ed_nothinkmit | 3 | 100 | 47 | 47.0 (37.5–56.7) | 26.0 (18.4–35.4) | 74 | 63.5 (52.1–73.6) | 3347 | 2.2 |
| r2_ed_nothink32k | 0 | 100 | 53 | 53.0 (43.3–62.5) | 1.0 (0.2–5.4) | 99 | 53.5 (43.8–63.0) | 6864 | 7.7 |
| r2_ed_nothink32k | 1 | 100 | 53 | 53.0 (43.3–62.5) | 0.0 (0.0–3.7) | 100 | 53.0 (43.3–62.5) | 6428 | 7.1 |
| r2_ed_nothink32k | 2 | 100 | 51 | 51.0 (41.3–60.6) | 0.0 (0.0–3.7) | 100 | 51.0 (41.3–60.6) | 6475 | 7.3 |
| r2_ed_nothink32k | 3 | 100 | 49 | 49.0 (39.4–58.7) | 0.0 (0.0–3.7) | 100 | 49.0 (39.4–58.7) | 5844 | 6.8 |
| r2_pla_think | 0 | 100 | 13 | 13.0 (7.8–21.0) | 87.0 (79.0–92.2) | 13 | 100.0 (77.2–100.0) | 29370 | 58.3 |
| r2_pla_think | 1 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 9 | 100.0 (70.1–100.0) | 30427 | 54.4 |
| cero_edicion_rep110 | 0 | 100 | 21 | 21.0 (14.2–30.0) | 76.0 (66.8–83.3) | 24 | 87.5 (69.0–95.7) | 27192 | 46.9 |
| cero_edicion_rep110 | 1 | 100 | 21 | 21.0 (14.2–30.0) | 75.0 (65.7–82.5) | 25 | 84.0 (65.3–93.6) | 27500 | 47.4 |
| cero_edicion_rep110 | 2 | 100 | 26 | 26.0 (18.4–35.4) | 72.0 (62.5–79.9) | 28 | 92.9 (77.4–98.0) | 26721 | 45.5 |
| cero_edicion_rep110 | 3 | 100 | 28 | 28.0 (20.1–37.5) | 67.0 (57.3–75.4) | 33 | 84.8 (69.1–93.3) | 25520 | 42.8 |
| cero_edicion_rep105 | 0 | 100 | 15 | 15.0 (9.3–23.3) | 85.0 (76.7–90.7) | 15 | 100.0 (79.6–100.0) | 28957 | 50.7 |
| cero_edicion_presence0 | 0 | 100 | 2 | 2.0 (0.6–7.0) | 98.0 (93.0–99.4) | 2 | 100.0 (34.2–100.0) | 32162 | 58.0 |
| cero_edicion_presence2 | 0 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 9 | 100.0 (70.1–100.0) | 30571 | 53.9 |
| r2_gsm8k_orig_think | 0 | 100 | 16 | 16.0 (10.1–24.4) | 84.0 (75.6–89.9) | 16 | 100.0 (80.6–100.0) | 28145 | 49.7 |
| r2_gsm8k_orig_nothink | 0 | 100 | 54 | 54.0 (44.3–63.4) | 6.0 (2.8–12.5) | 94 | 57.4 (47.4–67.0) | 1205 | 1.0 |
| r2_gsm8k_orig_nothink | 1 | 100 | 51 | 51.0 (41.3–60.6) | 6.0 (2.8–12.5) | 94 | 54.3 (44.2–64.0) | 1261 | 1.0 |
| r2_gsm8k_orig_nothink | 2 | 100 | 58 | 58.0 (48.2–67.2) | 8.0 (4.1–15.0) | 92 | 63.0 (52.8–72.2) | 1594 | 1.2 |
| r2_gsm8k_orig_nothink | 3 | 100 | 50 | 50.0 (40.4–59.6) | 2.0 (0.6–7.0) | 98 | 51.0 (41.3–60.7) | 1158 | 1.0 |
| r2_gsm8k_ed_think | 0 | 100 | 71 | 71.0 (61.5–79.0) | 7.0 (3.4–13.7) | 93 | 76.3 (66.8–83.8) | 11672 | 13.3 |
| r2_gsm8k_ed_think | 1 | 100 | 68 | 68.0 (58.3–76.3) | 6.0 (2.8–12.5) | 94 | 72.3 (62.6–80.4) | 11947 | 13.9 |
| r2_gsm8k_ed_think | 2 | 100 | 63 | 63.0 (53.2–71.8) | 7.0 (3.4–13.7) | 93 | 67.7 (57.7–76.4) | 11333 | 13.0 |
| r2_gsm8k_ed_think | 3 | 100 | 68 | 68.0 (58.3–76.3) | 4.0 (1.6–9.8) | 96 | 70.8 (61.1–79.0) | 11554 | 13.7 |
| r2_gsm8k_ed_nothink | 0 | 100 | 49 | 49.0 (39.4–58.7) | 4.0 (1.6–9.8) | 96 | 51.0 (41.2–60.8) | 1071 | 1.0 |
| r2_gsm8k_ed_nothink | 1 | 100 | 58 | 58.0 (48.2–67.2) | 5.0 (2.2–11.2) | 95 | 61.1 (51.0–70.2) | 1489 | 1.1 |
| r2_gsm8k_ed_nothink | 2 | 100 | 55 | 55.0 (45.2–64.4) | 2.0 (0.6–7.0) | 98 | 56.1 (46.3–65.5) | 1286 | 1.0 |
| r2_gsm8k_ed_nothink | 3 | 100 | 50 | 50.0 (40.4–59.6) | 4.0 (1.6–9.8) | 96 | 52.1 (42.2–61.8) | 1203 | 1.0 |
| r2_ifeval_orig_think | 0 | 100 | 21 | 21.0 (14.2–30.0) | 69.0 (59.4–77.2) | 31 | 67.7 (50.1–81.4) | 23733 | 41.8 |
| r2_ifeval_orig_nothink | 0 | 100 | 51 | 51.0 (41.3–60.6) | 1.0 (0.2–5.4) | 99 | 51.5 (41.8–61.1) | 294 | 0.7 |
| r2_ifeval_orig_nothink | 1 | 100 | 52 | 52.0 (42.3–61.5) | 1.0 (0.2–5.4) | 99 | 52.5 (42.8–62.1) | 323 | 0.7 |
| r2_ifeval_orig_nothink | 2 | 100 | 51 | 51.0 (41.3–60.6) | 0.0 (0.0–3.7) | 100 | 51.0 (41.3–60.6) | 226 | 0.2 |
| r2_ifeval_orig_nothink | 3 | 100 | 51 | 51.0 (41.3–60.6) | 0.0 (0.0–3.7) | 100 | 51.0 (41.3–60.6) | 275 | 0.5 |
| r2_ifeval_ed_think | 0 | 100 | 58 | 58.0 (48.2–67.2) | 0.0 (0.0–3.7) | 100 | 58.0 (48.2–67.2) | 3310 | 2.2 |
| r2_ifeval_ed_think | 1 | 100 | 59 | 59.0 (49.2–68.1) | 1.0 (0.2–5.4) | 99 | 59.6 (49.7–68.7) | 3755 | 4.0 |
| r2_ifeval_ed_think | 2 | 100 | 63 | 63.0 (53.2–71.8) | 2.0 (0.6–7.0) | 98 | 64.3 (54.4–73.1) | 4001 | 4.6 |
| r2_ifeval_ed_think | 3 | 100 | 52 | 52.0 (42.3–61.5) | 1.0 (0.2–5.4) | 99 | 52.5 (42.8–62.1) | 3572 | 4.0 |
| r2_ifeval_ed_nothink | 0 | 100 | 43 | 43.0 (33.7–52.8) | 0.0 (0.0–3.7) | 100 | 43.0 (33.7–52.8) | 236 | 0.3 |
| r2_ifeval_ed_nothink | 1 | 100 | 49 | 49.0 (39.4–58.7) | 0.0 (0.0–3.7) | 100 | 49.0 (39.4–58.7) | 228 | 0.2 |
| r2_ifeval_ed_nothink | 2 | 100 | 46 | 46.0 (36.6–55.7) | 0.0 (0.0–3.7) | 100 | 46.0 (36.6–55.7) | 260 | 0.4 |
| r2_ifeval_ed_nothink | 3 | 100 | 46 | 46.0 (36.6–55.7) | 0.0 (0.0–3.7) | 100 | 46.0 (36.6–55.7) | 231 | 0.2 |

Corridas FALTANTES: ninguna

## 2. MATH-500 (100 fijos): promedio por brazo

| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |
|---|---|---|---|---|---|---|
| orig · thinking MIT | [0, 1, 2, 3] | 400 | 7.8 (4.0–12.0) | 92.2 | 100.0 (31/31) | 30770 |
| orig · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 45.2 (37.5–53.0) | 29.0 | 63.7 (181/284) | 3388 |
| orig · no-think 32k | [0, 1, 2, 3] | 400 | 51.5 (43.8–59.2) | 12.0 | 58.5 (206/352) | 7955 |
| p50c · thinking MIT | [0, 1, 2, 3] | 400 | 51.2 (43.2–59.2) | 29.2 | 72.4 (205/283) | 21436 |
| p50c · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 48.0 (39.8–56.0) | 27.3 | 66.0 (192/291) | 3482 |
| p50c · no-think 32k | [0, 1, 2, 3] | 400 | 51.5 (44.0–59.0) | 0.2 | 51.6 (206/399) | 6403 |
| placebo · thinking MIT | [0, 1] | 200 | 11.0 (6.0–16.5) | 89.0 | 100.0 (22/22) | 29899 |
| orig · rep 1.1 (thinking) | [0, 1, 2, 3] | 400 | 24.0 (17.8–30.8) | 72.5 | 87.3 (96/110) | 26733 |
| orig · rep 1.05 (thinking) | [0] | 100 | 15.0 (8.0–22.0) | 85.0 | 100.0 (15/15) | 28957 |
| orig · presence 0 (thinking) | [0] | 100 | 2.0 (0.0–5.0) | 98.0 | 100.0 (2/2) | 32162 |
| orig · presence 2 (thinking) | [0] | 100 | 9.0 (4.0–15.0) | 91.0 | 100.0 (9/9) | 30571 |

## 3. McNemar pareado (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| orig · thinking MIT | orig · no-think muestreo MIT | 400 | 5 | 155 | -37.5 (-44.8…-30.5) | 1.2e-39 | 5.9e-38 |
| orig · thinking MIT | orig · no-think 32k | 400 | 4 | 179 | -43.8 (-51.2…-36.2) | 7.5e-48 | 4e-46 |
| orig · thinking MIT | p50c · thinking MIT | 400 | 0 | 174 | -43.5 (-51.0…-36.0) | 8.4e-53 | 4.6e-51 |
| orig · thinking MIT | p50c · no-think muestreo MIT | 400 | 2 | 163 | -40.2 (-47.8…-32.8) | 5.9e-46 | 3e-44 |
| orig · thinking MIT | p50c · no-think 32k | 400 | 2 | 177 | -43.8 (-50.7…-37.0) | 4.2e-50 | 2.3e-48 |
| orig · thinking MIT | placebo · thinking MIT | 200 | 6 | 12 | -3.0 (-7.0…+1.0) | 0.24 | 1 |
| orig · thinking MIT | orig · rep 1.1 (thinking) | 400 | 4 | 69 | -16.2 (-21.5…-11.5) | 2.4e-16 | 1e-14 |
| orig · thinking MIT | orig · rep 1.05 (thinking) | 100 | 1 | 9 | -8.0 (-14.0…-2.0) | 0.021 | 0.37 |
| orig · thinking MIT | orig · presence 0 (thinking) | 100 | 6 | 1 | +5.0 (+0.0…+10.0) | 0.12 | 1 |
| orig · thinking MIT | orig · presence 2 (thinking) | 100 | 5 | 7 | -2.0 (-9.0…+5.0) | 0.77 | 1 |
| orig · no-think muestreo MIT | orig · no-think 32k | 400 | 35 | 60 | -6.2 (-11.8…-0.8) | 0.013 | 0.27 |
| orig · no-think muestreo MIT | p50c · thinking MIT | 400 | 35 | 59 | -6.0 (-11.0…-1.0) | 0.017 | 0.32 |
| orig · no-think muestreo MIT | p50c · no-think muestreo MIT | 400 | 42 | 53 | -2.8 (-7.5…+2.0) | 0.3 | 1 |
| orig · no-think muestreo MIT | p50c · no-think 32k | 400 | 47 | 72 | -6.2 (-12.2…-0.2) | 0.027 | 0.44 |
| orig · no-think muestreo MIT | placebo · thinking MIT | 200 | 74 | 1 | +36.5 (+29.0…+44.0) | 4e-21 | 1.8e-19 |
| orig · no-think muestreo MIT | orig · rep 1.1 (thinking) | 400 | 105 | 20 | +21.2 (+15.5…+27.0) | 4.1e-15 | 1.5e-13 |
| orig · no-think muestreo MIT | orig · rep 1.05 (thinking) | 100 | 36 | 1 | +35.0 (+25.0…+45.0) | 5.5e-10 | 1.5e-08 |
| orig · no-think muestreo MIT | orig · presence 0 (thinking) | 100 | 48 | 0 | +48.0 (+38.0…+58.0) | 7.1e-15 | 2.6e-13 |
| orig · no-think muestreo MIT | orig · presence 2 (thinking) | 100 | 41 | 0 | +41.0 (+32.0…+51.0) | 9.1e-13 | 3e-11 |
| orig · no-think 32k | p50c · thinking MIT | 400 | 51 | 50 | +0.2 (-5.5…+6.0) | 1 | 1 |
| orig · no-think 32k | p50c · no-think muestreo MIT | 400 | 54 | 40 | +3.5 (-2.0…+9.0) | 0.18 | 1 |
| orig · no-think 32k | p50c · no-think 32k | 400 | 59 | 59 | +0.0 (-6.0…+6.0) | 1 | 1 |
| orig · no-think 32k | placebo · thinking MIT | 200 | 76 | 1 | +37.5 (+29.5…+45.5) | 1e-21 | 4.9e-20 |
| orig · no-think 32k | orig · rep 1.1 (thinking) | 400 | 125 | 15 | +27.5 (+21.0…+34.0) | 8.9e-23 | 4.3e-21 |
| orig · no-think 32k | orig · rep 1.05 (thinking) | 100 | 35 | 2 | +33.0 (+23.0…+43.0) | 1e-08 | 2.6e-07 |
| orig · no-think 32k | orig · presence 0 (thinking) | 100 | 46 | 0 | +46.0 (+36.0…+56.0) | 2.8e-14 | 9.9e-13 |
| orig · no-think 32k | orig · presence 2 (thinking) | 100 | 40 | 1 | +39.0 (+29.0…+49.0) | 3.8e-11 | 1.1e-09 |
| p50c · thinking MIT | p50c · no-think muestreo MIT | 400 | 55 | 42 | +3.2 (-2.0…+8.5) | 0.22 | 1 |
| p50c · thinking MIT | p50c · no-think 32k | 400 | 49 | 50 | -0.2 (-6.5…+6.0) | 1 | 1 |
| p50c · thinking MIT | placebo · thinking MIT | 200 | 80 | 0 | +40.0 (+32.0…+48.5) | 1.7e-24 | 8.1e-23 |
| p50c · thinking MIT | orig · rep 1.1 (thinking) | 400 | 115 | 6 | +27.3 (+21.2…+33.2) | 3e-27 | 1.5e-25 |
| p50c · thinking MIT | orig · rep 1.05 (thinking) | 100 | 38 | 2 | +36.0 (+26.0…+46.0) | 1.5e-09 | 4e-08 |
| p50c · thinking MIT | orig · presence 0 (thinking) | 100 | 49 | 0 | +49.0 (+39.0…+59.0) | 3.6e-15 | 1.4e-13 |
| p50c · thinking MIT | orig · presence 2 (thinking) | 100 | 43 | 1 | +42.0 (+32.0…+52.0) | 5.1e-12 | 1.6e-10 |
| p50c · no-think muestreo MIT | p50c · no-think 32k | 400 | 52 | 66 | -3.5 (-9.8…+2.5) | 0.23 | 1 |
| p50c · no-think muestreo MIT | placebo · thinking MIT | 200 | 78 | 3 | +37.5 (+29.0…+46.0) | 7.3e-20 | 3.2e-18 |
| p50c · no-think muestreo MIT | orig · rep 1.1 (thinking) | 400 | 113 | 17 | +24.0 (+17.8…+30.2) | 1.4e-18 | 5.9e-17 |
| p50c · no-think muestreo MIT | orig · rep 1.05 (thinking) | 100 | 40 | 3 | +37.0 (+26.0…+48.0) | 3e-09 | 7.9e-08 |
| p50c · no-think muestreo MIT | orig · presence 0 (thinking) | 100 | 50 | 0 | +50.0 (+41.0…+60.0) | 1.8e-15 | 6.9e-14 |
| p50c · no-think muestreo MIT | orig · presence 2 (thinking) | 100 | 44 | 1 | +43.0 (+33.0…+53.0) | 2.6e-12 | 8.4e-11 |
| p50c · no-think 32k | placebo · thinking MIT | 200 | 88 | 4 | +42.0 (+34.0…+50.5) | 1.2e-21 | 5.4e-20 |
| p50c · no-think 32k | orig · rep 1.1 (thinking) | 400 | 129 | 19 | +27.5 (+20.8…+34.5) | 2.8e-21 | 1.2e-19 |
| p50c · no-think 32k | orig · rep 1.05 (thinking) | 100 | 40 | 2 | +38.0 (+28.0…+48.0) | 4.1e-10 | 1.2e-08 |
| p50c · no-think 32k | orig · presence 0 (thinking) | 100 | 51 | 0 | +51.0 (+41.0…+61.0) | 8.9e-16 | 3.6e-14 |
| p50c · no-think 32k | orig · presence 2 (thinking) | 100 | 44 | 0 | +44.0 (+34.0…+54.0) | 1.1e-13 | 3.9e-12 |
| placebo · thinking MIT | orig · rep 1.1 (thinking) | 200 | 6 | 26 | -10.0 (-15.5…-5.0) | 0.00054 | 0.012 |
| placebo · thinking MIT | orig · rep 1.05 (thinking) | 100 | 6 | 8 | -2.0 (-9.0…+5.0) | 0.79 | 1 |
| placebo · thinking MIT | orig · presence 0 (thinking) | 100 | 12 | 1 | +11.0 (+4.0…+18.0) | 0.0034 | 0.072 |
| placebo · thinking MIT | orig · presence 2 (thinking) | 100 | 10 | 6 | +4.0 (-4.0…+12.0) | 0.45 | 1 |
| orig · rep 1.1 (thinking) | orig · rep 1.05 (thinking) | 100 | 11 | 5 | +6.0 (-2.0…+14.0) | 0.21 | 1 |
| orig · rep 1.1 (thinking) | orig · presence 0 (thinking) | 100 | 19 | 0 | +19.0 (+11.0…+27.0) | 3.8e-06 | 9.2e-05 |
| orig · rep 1.1 (thinking) | orig · presence 2 (thinking) | 100 | 17 | 5 | +12.0 (+3.0…+21.0) | 0.017 | 0.32 |
| orig · rep 1.05 (thinking) | orig · presence 0 (thinking) | 100 | 13 | 0 | +13.0 (+7.0…+20.0) | 0.00024 | 0.0056 |
| orig · rep 1.05 (thinking) | orig · presence 2 (thinking) | 100 | 9 | 3 | +6.0 (-1.0…+13.0) | 0.15 | 1 |
| orig · presence 0 (thinking) | orig · presence 2 (thinking) | 100 | 1 | 8 | -7.0 (-13.0…-2.0) | 0.039 | 0.59 |

## 4. No-thinking con parámetros de la línea base (32,768) en los 500 problemas, semilla 0

| Grupo | n | Correctos (estricta) | Precisión % (Wilson) | Al límite % (Wilson) | Terminaron: precisión % | Tokens medios |
|---|---|---|---|---|---|---|
| TODOS | 500 | 247 | 49.4 (45.0–53.8) | 7.2 (5.2–9.8) | 53.2 | 7561 |
| nivel 1 | 43 | 35 | 81.4 (67.4–90.3) | 0.0 (0.0–8.2) | 81.4 | 2144 |
| nivel 2 | 90 | 73 | 81.1 (71.8–87.9) | 0.0 (0.0–4.1) | 81.1 | 2469 |
| nivel 3 | 105 | 59 | 56.2 (46.6–65.3) | 9.5 (5.3–16.6) | 62.1 | 6626 |
| nivel 4 | 128 | 48 | 37.5 (29.6–46.1) | 9.4 (5.4–15.7) | 41.4 | 9236 |
| nivel 5 | 134 | 32 | 23.9 (17.5–31.8) | 10.4 (6.3–16.8) | 26.7 | 11851 |

Nota (texto completo, no principal): 247/500 = 49.4%. Referencia externa: el informe del MIT da 48.1% para p50c con thinking (MATH-500, 500 problemas x 4 muestras); no es comparable 1 a 1 (otro modo, otra muestra).

## 5. GSM8K e IFEval (100 fijos cada uno, semilla 0; IFEval = estricto a nivel de prompt, corrector oficial de lm-eval)

| Brazo | n | Correctos | Precisión % (Wilson) | Al límite % | Terminaron: precisión % |
|---|---|---|---|---|---|
| GSM8K orig · thinking MIT | 100 | 16 | 16.0 (10.1–24.4) | 84.0 | 100.0 (16/16) |
| GSM8K orig · no-think muestreo MIT | 100 | 54 | 54.0 (44.3–63.4) | 6.0 | 57.4 (54/94) |
| GSM8K p50c · thinking MIT | 100 | 71 | 71.0 (61.5–79.0) | 7.0 | 76.3 (71/93) |
| GSM8K p50c · no-think muestreo MIT | 100 | 49 | 49.0 (39.4–58.7) | 4.0 | 51.0 (49/96) |
| IFEval orig · thinking MIT | 100 | 21 | 21.0 (14.2–30.0) | 69.0 | 67.7 (21/31) |
| IFEval orig · no-think muestreo MIT | 100 | 51 | 51.0 (41.3–60.6) | 1.0 | 51.5 (51/99) |
| IFEval p50c · thinking MIT | 100 | 58 | 58.0 (48.2–67.2) | 0.0 | 58.0 (58/100) |
| IFEval p50c · no-think muestreo MIT | 100 | 43 | 43.0 (33.7–52.8) | 0.0 | 43.0 (43/100) |

## 6. Tamaño de la edición (medido sobre los pesos bf16 finales)

| Modelo | Tensor | ‖ΔW‖_F | ‖W‖_F | ‖ΔW‖/‖W‖ | Columnas tocadas |
|---|---|---|---|---|---|
| p50c_MIT | capa 15 mlp.down_proj | 1.74889 | 16.4428 | 0.106362 | 64 |
| placebo | capa 15 mlp.down_proj | 1.74889 | 16.4428 | 0.106362 | 64 |
| p50c_MIT | capa 19 mlp.down_proj | 1.39876 | 17.2553 | 0.081063 | 64 |
| placebo | capa 19 mlp.down_proj | 1.39876 | 17.2553 | 0.081063 | 64 |
