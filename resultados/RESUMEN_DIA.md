# Resumen del día (solo números, sin interpretar)

**Regla de calificación principal: estricta** (en no-thinking cuenta solo si la respuesta NO llegó al límite de tokens; en thinking equivale a la normal). La regla de texto completo aparece solo como nota en la tabla 4. Mismos 100 problemas fijos (salvo `dia_nothink_mit500`: los 500). IC por corrida: Wilson 95%. IC agrupado y de diferencias: bootstrap por problema (10000 remuestreos, semilla fija) sobre promedios por problema. Semilla 0 = corridas de anoche/pilotos.

## 1. Corridas individuales

| Corrida | Semilla | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Tokens medios | Tiempo min |
|---|---|---|---|---|---|---|---|
| linea_base_vllm | 0 | 100 | 7 | 7.0 (3.4–13.7) | 93.0 (86.3–96.6) | 31039 | 59.5 |
| linea_base_vllm | 1 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 30665 | 54.4 |
| linea_base_vllm | 2 | 100 | 6 | 6.0 (2.8–12.5) | 94.0 (87.5–97.2) | 31091 | 55.2 |
| linea_base_vllm | 3 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 30284 | 53.5 |
| cero_edicion_no_thinking | 0 | 100 | 48 | 48.0 (38.5–57.7) | 14.0 (8.5–22.1) | 8506 | 14.2 |
| cero_edicion_no_thinking | 1 | 100 | 49 | 49.0 (39.4–58.7) | 15.0 (9.3–23.3) | 8598 | 12.5 |
| cero_edicion_no_thinking | 2 | 100 | 57 | 57.0 (47.2–66.3) | 11.0 (6.3–18.6) | 7949 | 11.2 |
| cero_edicion_no_thinking | 3 | 100 | 52 | 52.0 (42.3–61.5) | 8.0 (4.1–15.0) | 6767 | 9.5 |
| cero_edicion_rep110 | 0 | 100 | 21 | 21.0 (14.2–30.0) | 76.0 (66.8–83.3) | 27192 | 46.9 |
| cero_edicion_rep110 | 1 | 100 | 21 | 21.0 (14.2–30.0) | 75.0 (65.7–82.5) | 27500 | 47.4 |
| cero_edicion_rep110 | 2 | 100 | 26 | 26.0 (18.4–35.4) | 72.0 (62.5–79.9) | 26721 | 45.5 |
| cero_edicion_rep110 | 3 | 100 | 28 | 28.0 (20.1–37.5) | 67.0 (57.3–75.4) | 25520 | 42.8 |
| cero_edicion_presence0 | 0 | 100 | 2 | 2.0 (0.6–7.0) | 98.0 (93.0–99.4) | 32162 | 58.0 |
| cero_edicion_presence2 | 0 | 100 | 9 | 9.0 (4.8–16.2) | 91.0 (83.8–95.2) | 30571 | 53.9 |
| cero_edicion_rep105 | 0 | 100 | 15 | 15.0 (9.3–23.3) | 85.0 (76.7–90.7) | 28957 | 50.7 |
| dia_nothink_mit100 | 0 | 100 | 50 | 50.0 (40.4–59.6) | 25.0 (17.5–34.3) | 3352 | 2.4 |
| dia_nothink_mit500 | 0 | 500 | 224 | 44.8 (40.5–49.2) | 31.8 (27.9–36.0) | 3810 | 13.5 |

Corridas FALTANTES (no existe su CSV): ninguna

## 2. Promedio sobre las semillas disponibles (100 problemas)

| Configuración | Semillas | Muestras | Precisión % (IC bootstrap) | Al límite % (IC bootstrap) |
|---|---|---|---|---|
| linea_base_vllm | [0, 1, 2, 3] | 400 | 7.8 (4.0–12.0) | 92.2 (88.0–96.0) |
| cero_edicion_no_thinking | [0, 1, 2, 3] | 400 | 51.5 (43.8–59.2) | 12.0 (7.8–16.5) |
| dia_nothink_mit100 | [0] | 100 | 50.0 (40.0–60.0) | 25.0 (17.0–34.0) |
| cero_edicion_presence0 | [0] | 100 | 2.0 (0.0–5.0) | 98.0 (95.0–100.0) |
| cero_edicion_presence2 | [0] | 100 | 9.0 (4.0–15.0) | 91.0 (85.0–96.0) |
| cero_edicion_rep105 | [0] | 100 | 15.0 (8.0–22.0) | 85.0 (78.0–91.0) |
| cero_edicion_rep110 | [0, 1, 2, 3] | 400 | 24.0 (17.5–30.8) | 72.5 (65.5–79.2) |

## 3. Análisis pareado contra la línea base (misma pareja problema+semilla)

Grupo = estado de la LÍNEA BASE en esa pareja: 'antes al límite' (llegó a 32,768) o 'ya terminaba'. Contribución = (correctos variante − correctos base en el grupo) / total de parejas × 100 (puntos de precisión). Cortó = en 'antes al límite', la variante NO llegó al límite.

| Variante | Semillas comunes | Parejas | Dif. total (pts) (IC) | Antes al límite: parejas | …correctos base | …correctos variante | …cortó el bucle | Contribución (pts) | Ya terminaban: parejas | …correctos base | …correctos variante | …perdidos | …ganados | Contribución (pts) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cero_edicion_no_thinking | [0, 1, 2, 3] | 400 | +43.8 (+36.2…+51.2) | 369 | 0 | 179 | 321 | +44.8 | 31 | 31 | 27 | 4 | 0 | -1.0 |
| dia_nothink_mit100 | [0] | 100 | +43.0 (+33.0…+53.0) | 93 | 0 | 44 | 68 | +44.0 | 7 | 7 | 6 | 1 | 0 | -1.0 |
| cero_edicion_presence0 | [0] | 100 | -5.0 (-10.0…+0.0) | 93 | 0 | 1 | 1 | +1.0 | 7 | 7 | 1 | 6 | 0 | -6.0 |
| cero_edicion_presence2 | [0] | 100 | +2.0 (-5.0…+9.0) | 93 | 0 | 7 | 7 | +7.0 | 7 | 7 | 2 | 5 | 0 | -5.0 |
| cero_edicion_rep105 | [0] | 100 | +8.0 (+2.0…+14.0) | 93 | 0 | 9 | 9 | +9.0 | 7 | 7 | 6 | 1 | 0 | -1.0 |
| cero_edicion_rep110 | [0, 1, 2, 3] | 400 | +16.2 (+11.2…+21.5) | 369 | 0 | 69 | 83 | +17.2 | 31 | 31 | 27 | 4 | 0 | -1.0 |

## 4. Nota: no-thinking, regla estricta (principal, usada en todas las tablas) vs. regla de texto completo (solo nota)

| Corrida | Semilla | n | Precisión estricta % (principal) | Precisión texto completo % (nota) | Correctos que llegaron al límite |
|---|---|---|---|---|---|
| cero_edicion_no_thinking | 0 | 100 | 48.0 | 49.0 | 1 |
| cero_edicion_no_thinking | 1 | 100 | 49.0 | 49.0 | 0 |
| cero_edicion_no_thinking | 2 | 100 | 57.0 | 57.0 | 0 |
| cero_edicion_no_thinking | 3 | 100 | 52.0 | 52.0 | 0 |
| dia_nothink_mit100 | 0 | 100 | 50.0 | 50.0 | 0 |
| dia_nothink_mit500 | 0 | 500 | 44.8 | 45.4 | 3 |

## 5. No-thinking (muestreo no-thinking del MIT) en los 500 problemas completos

| Grupo | n | Correctos | Precisión % (Wilson) | Al límite % (Wilson) | Tokens medios |
|---|---|---|---|---|---|
| TODOS | 500 | 224 | 44.8 (40.5–49.2) | 31.8 (27.9–36.0) | 3810 |
| nivel 1 | 43 | 36 | 83.7 (70.0–91.9) | 4.7 (1.3–15.5) | 1489 |
| nivel 2 | 90 | 60 | 66.7 (56.4–75.5) | 8.9 (4.6–16.6) | 1925 |
| nivel 3 | 105 | 53 | 50.5 (41.1–59.9) | 26.7 (19.1–35.8) | 3579 |
| nivel 4 | 128 | 46 | 35.9 (28.1–44.5) | 37.5 (29.6–46.1) | 4396 |
| nivel 5 | 134 | 29 | 21.6 (15.5–29.4) | 54.5 (46.0–62.7) | 5440 |

Nota (regla de texto completo, no principal): 227/500 = 45.4%.

Control de reproducibilidad (mismos 100 fijos, misma configuración, misma semilla, distinto lote): precisión en el lote de 500 = 52/100; en el lote de 100 = 50/100; mismo resultado correcto/incorrecto en 80/100 problemas; mismos tokens exactos en 27/100.
