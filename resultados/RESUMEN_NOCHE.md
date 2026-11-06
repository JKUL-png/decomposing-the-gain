# Resumen de la noche (solo números, sin interpretar)

Mismos 100 problemas fijos, seed 0, prompt y calificador (math-verify 0.9.0) del MIT. Intervalos: Wilson 95%, entre paréntesis.

| Brazo | Cambio vs. línea base | Precisión | % al límite (32,768) | Correctos entre las que terminaron | Tokens medios | Tiempo | Errores |
|---|---|---|---|---|---|---|---|
| linea_base | ninguno (MIT: thinking, temp 0.6, top_p 0.95, top_k 20, presence 1.5, rep 1.0) | 7/100 = 7.0% (3.4–13.7) | 93/100 = 93.0% (86.3–96.6) | 7/7 | 31039 | 59.5 min | errores de calificación: 0 |
| no_thinking | thinking apagado (muestreo igual a la base) | 49/100 = 49.0% (39.4–58.7) | 14/100 = 14.0% (8.5–22.1) | 48/86 | 8506 | 14.2 min | errores de calificación: 0 |
| presence0 | presence_penalty 0 | 2/100 = 2.0% (0.6–7.0) | 98/100 = 98.0% (93.0–99.4) | 2/2 | 32162 | 58.0 min | errores de calificación: 0 |
| presence2 | presence_penalty 2.0 | 9/100 = 9.0% (4.8–16.2) | 91/100 = 91.0% (83.8–95.2) | 9/9 | 30571 | 53.9 min | errores de calificación: 0 |
| rep105 | repetition_penalty 1.05 | 15/100 = 15.0% (9.3–23.3) | 85/100 = 85.0% (76.7–90.7) | 15/15 | 28957 | 50.7 min | errores de calificación: 0 |
| rep110 | repetition_penalty 1.1 | 21/100 = 21.0% (14.2–30.0) | 76/100 = 76.0% (66.8–83.3) | 21/24 | 27192 | 46.9 min | errores de calificación: 0 |

Archivos: `resultados/cero_edicion_<variante>.csv` (+ `.jsonl` textos, `.meta.json` tiempos), `resultados/linea_base_vllm.csv`.
Nota: no-thinking se califica sobre el texto completo (no hay `</think>`).
