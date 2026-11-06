# Resumen ronda 3 (solo números, sin interpretar)

**Regla principal: estricta** (en no-thinking cuenta solo si NO llegó al límite de tokens). Modelos: orig = Qwen3.5-0.8B; p50c = edición del MIT (hash verificado). Thinking MIT = temp 0.6, top_p 0.95, top_k 20, presence 1.5, 32,768. No-think muestreo MIT = temp 0.7, top_p 0.8, top_k 20, presence 1.5, 8,192. IC por corrida: Wilson 95%; IC agrupado y de diferencias: bootstrap por problema (10000, semilla fija); McNemar exacto bilateral sobre parejas problema+semilla; Holm dentro de cada tabla (las semillas del mismo problema no son independientes).

## 1. GSM8K e IFEval con 4 semillas (0–3)

### GSM8K subconjunto 1 (100 problemas)

| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |
|---|---|---|---|---|---|---|
| p50c · thinking MIT | [0, 1, 2, 3] | 400 | 67.5 (59.8–75.0) | 6.0 | 71.8 (270/376) | 11627 |
| p50c · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 53.0 (45.8–60.2) | 3.8 | 55.1 (212/385) | 1262 |
| orig · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 53.2 (46.0–60.5) | 5.5 | 56.3 (213/378) | 1305 |
| orig · thinking MIT (solo semilla 0) | [0] | 100 | 16.0 (9.0–24.0) | 84.0 | 100.0 (16/16) | 28145 |

### GSM8K subconjunto b (100 problemas distintos, semilla 20261105)

| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |
|---|---|---|---|---|---|---|
| p50c · thinking MIT | [0, 1, 2, 3] | 400 | 65.8 (57.8–73.2) | 9.2 | 72.5 (263/363) | 12940 |
| p50c · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 55.8 (48.2–63.2) | 3.5 | 57.8 (223/386) | 1229 |
| orig · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 56.8 (48.8–64.5) | 3.2 | 58.7 (227/387) | 1014 |

### GSM8K subconjuntos 1 + b juntos (200 problemas)

| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |
|---|---|---|---|---|---|---|
| p50c · thinking MIT | [0, 1, 2, 3] | 800 | 66.6 (61.1–72.0) | 7.6 | 72.1 (533/739) | 12283 |
| p50c · no-think muestreo MIT | [0, 1, 2, 3] | 800 | 54.4 (49.1–59.6) | 3.6 | 56.4 (435/771) | 1246 |
| orig · no-think muestreo MIT | [0, 1, 2, 3] | 800 | 55.0 (49.8–60.4) | 4.4 | 57.5 (440/765) | 1159 |

### IFEval (100 problemas, estricto a nivel de prompt)

| Brazo | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % | Precisión entre las que terminaron % (correctas/terminaron) | Tokens medios |
|---|---|---|---|---|---|---|
| p50c · thinking MIT | [0, 1, 2, 3] | 400 | 58.0 (50.5–65.8) | 1.0 | 58.6 (232/396) | 3659 |
| p50c · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 46.0 (38.0–54.0) | 0.0 | 46.0 (184/400) | 239 |
| orig · no-think muestreo MIT | [0, 1, 2, 3] | 400 | 51.2 (43.2–59.0) | 0.5 | 51.5 (205/398) | 279 |
| orig · thinking MIT (solo semilla 0) | [0] | 100 | 21.0 (13.0–29.0) | 69.0 | 67.7 (21/31) | 23733 |

## 2. McNemar pareado

**GSM8K subconjunto 1** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| p50c · thinking MIT | p50c · no-think muestreo MIT | 400 | 89 | 31 | +14.5 (+8.0…+20.8) | 1.1e-07 | 2.2e-07 |
| p50c · thinking MIT | orig · no-think muestreo MIT | 400 | 82 | 25 | +14.2 (+9.0…+19.5) | 2.9e-08 | 1.2e-07 |
| p50c · thinking MIT | orig · thinking MIT (solo semilla 0) | 100 | 55 | 0 | +55.0 (+45.0…+65.0) | 5.6e-17 | 3.3e-16 |
| p50c · no-think muestreo MIT | orig · no-think muestreo MIT | 400 | 51 | 52 | -0.2 (-5.8…+5.2) | 1 | 1 |
| p50c · no-think muestreo MIT | orig · thinking MIT (solo semilla 0) | 100 | 36 | 3 | +33.0 (+23.0…+43.0) | 3.6e-08 | 1.2e-07 |
| orig · no-think muestreo MIT | orig · thinking MIT (solo semilla 0) | 100 | 39 | 1 | +38.0 (+28.0…+48.0) | 7.5e-11 | 3.7e-10 |

**GSM8K subconjunto b** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| p50c · thinking MIT | p50c · no-think muestreo MIT | 400 | 76 | 36 | +10.0 (+3.8…+16.2) | 0.0002 | 0.00059 |
| p50c · thinking MIT | orig · no-think muestreo MIT | 400 | 72 | 36 | +9.0 (+3.0…+15.5) | 0.00068 | 0.0014 |
| p50c · no-think muestreo MIT | orig · no-think muestreo MIT | 400 | 46 | 50 | -1.0 (-6.8…+4.8) | 0.76 | 0.76 |

**GSM8K 1 + b juntos** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| p50c · thinking MIT | p50c · no-think muestreo MIT | 800 | 165 | 67 | +12.2 (+7.9…+16.8) | 1e-10 | 3e-10 |
| p50c · thinking MIT | orig · no-think muestreo MIT | 800 | 154 | 61 | +11.6 (+7.6…+15.8) | 1.8e-10 | 3.7e-10 |
| p50c · no-think muestreo MIT | orig · no-think muestreo MIT | 800 | 97 | 102 | -0.6 (-4.6…+3.1) | 0.78 | 0.78 |

**IFEval** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| p50c · thinking MIT | p50c · no-think muestreo MIT | 400 | 95 | 47 | +12.0 (+4.8…+19.3) | 6.9e-05 | 0.00028 |
| p50c · thinking MIT | orig · no-think muestreo MIT | 400 | 80 | 53 | +6.8 (+0.0…+13.5) | 0.024 | 0.048 |
| p50c · thinking MIT | orig · thinking MIT (solo semilla 0) | 100 | 40 | 3 | +37.0 (+26.0…+47.0) | 3e-09 | 1.8e-08 |
| p50c · no-think muestreo MIT | orig · no-think muestreo MIT | 400 | 31 | 52 | -5.2 (-10.0…-0.8) | 0.028 | 0.048 |
| p50c · no-think muestreo MIT | orig · thinking MIT (solo semilla 0) | 100 | 29 | 7 | +22.0 (+11.0…+33.0) | 0.00031 | 0.00094 |
| orig · no-think muestreo MIT | orig · thinking MIT (solo semilla 0) | 100 | 33 | 3 | +30.0 (+20.0…+40.0) | 2.3e-07 | 1.1e-06 |

## 3. Detectar el bucle: reintentar (A) y forzar la respuesta (B), modelo original en thinking, semilla 0

Detector: ventana de 300 caracteres del final repetida ≥3 veces en los últimos 6,000 (revisado cada 512 tokens). A: hasta 3 intentos (semilla+1000·k); B: al detectar el bucle en el intento 1 se recorta el texto en la primera copia, se cierra el pensamiento y el modelo contesta (máx. 4,096 tokens; si llega al tope sin cerrar cuenta como incorrecta). 'Tokens totales' incluyen los intentos descartados. 'Terminaron' = la generación aceptada terminó sola (en B, los forzados cuentan aparte).

### MATH-500 (100 fijos)

| Brazo | n | Correctos | Precisión % (Wilson) | Terminaron % | Forzados | Forzados que llegaron al tope de 4,096 sin cerrar (incorrectos) | Intentos medios | Tokens totales por problema (media) | Tokens totales (suma) |
|---|---|---|---|---|---|---|---|---|---|
| orig · thinking MIT (referencia, 1 intento) | 100 | 7 | 7.0 (3.4–13.7) | 7.0 | 0 | 0 | 1 | 31039 | 3103931 |
| A · reintento (hasta 3) | 100 | 13 | 13.0 (7.8–21.0) | 13.0 | 0 | 0 | 2.69 | 23773 | 2377304 |
| B · forzar respuesta | 100 | 34 | 34.0 (25.5–43.7) | 34.0 | 87 | 62 | 1.00 | 11268 | 1126842 |
| p50c · thinking MIT (misma semilla 0) | 100 | 51 | 51.0 (41.3–60.6) | 64.0 | 0 | 0 | 1 | 21899 | 2189869 |

Referencia p50c thinking, 4 semillas: precisión 51.2%, tokens medios 21436.

**McNemar MATH-500 (100 fijos) (semilla 0)** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| A · reintento | B · forzar | 100 | 0 | 21 | -21.0 (-29.0…-13.0) | 9.5e-07 | 2.9e-06 |
| A · reintento | orig · thinking (ref.) | 100 | 8 | 2 | +6.0 (+0.0…+12.0) | 0.11 | 0.11 |
| A · reintento | p50c · thinking | 100 | 2 | 40 | -38.0 (-48.0…-28.0) | 4.1e-10 | 2.1e-09 |
| B · forzar | orig · thinking (ref.) | 100 | 27 | 0 | +27.0 (+18.0…+36.0) | 1.5e-08 | 6e-08 |
| B · forzar | p50c · thinking | 100 | 4 | 21 | -17.0 (-26.0…-8.0) | 0.00091 | 0.0018 |
| orig · thinking (ref.) | p50c · thinking | 100 | 0 | 44 | -44.0 (-54.0…-34.0) | 1.1e-13 | 6.8e-13 |

Intentos por problema: 1 intento = 13, 2 = 5, 3 = 82; problemas con ≥1 bucle detectado = 87; intentos abortados por bucle = 247.

### GSM8K (subconjunto 1)

| Brazo | n | Correctos | Precisión % (Wilson) | Terminaron % | Forzados | Forzados que llegaron al tope de 4,096 sin cerrar (incorrectos) | Intentos medios | Tokens totales por problema (media) | Tokens totales (suma) |
|---|---|---|---|---|---|---|---|---|---|
| orig · thinking MIT (referencia, 1 intento) | 100 | 16 | 16.0 (10.1–24.4) | 16.0 | 0 | 0 | 1 | 28145 | 2814505 |
| A · reintento (hasta 3) | 100 | 25 | 25.0 (17.5–34.3) | 27.0 | 0 | 0 | 2.66 | 17016 | 1701623 |
| B · forzar respuesta | 100 | 57 | 57.0 (47.2–66.3) | 62.0 | 87 | 36 | 1.00 | 8698 | 869833 |
| p50c · thinking MIT (misma semilla 0) | 100 | 71 | 71.0 (61.5–79.0) | 93.0 | 0 | 0 | 1 | 11672 | 1167221 |

**McNemar GSM8K (subconjunto 1) (semilla 0)** (A vs B; b = A acierta y B no; c = B acierta y A no)

| A | B | Parejas | b | c | Dif. A−B (pts) (IC bootstrap) | p McNemar exacto | p Holm |
|---|---|---|---|---|---|---|---|
| A · reintento | B · forzar | 100 | 2 | 34 | -32.0 (-42.0…-22.0) | 1.9e-08 | 5.8e-08 |
| A · reintento | orig · thinking (ref.) | 100 | 14 | 5 | +9.0 (+1.0…+17.0) | 0.064 | 0.064 |
| A · reintento | p50c · thinking | 100 | 0 | 46 | -46.0 (-56.0…-36.0) | 2.8e-14 | 1.4e-13 |
| B · forzar | orig · thinking (ref.) | 100 | 43 | 2 | +41.0 (+31.0…+51.0) | 5.9e-11 | 2.4e-10 |
| B · forzar | p50c · thinking | 100 | 7 | 21 | -14.0 (-24.0…-4.0) | 0.013 | 0.025 |
| orig · thinking (ref.) | p50c · thinking | 100 | 0 | 55 | -55.0 (-65.0…-45.0) | 5.6e-17 | 3.3e-16 |

Intentos por problema: 1 intento = 13, 2 = 8, 3 = 79; problemas con ≥1 bucle detectado = 87; intentos abortados por bucle = 237.

Corridas FALTANTES: ninguna

