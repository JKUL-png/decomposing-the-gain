"""Corre UNA configuración sobre un conjunto fijo de problemas en vLLM (dentro de WSL).
Uso: python correr_vllm.py <modelo> <config> <ids_file> <salida.csv>
Escribe: <salida.csv>.jsonl (textos, ANTES de calificar), <salida.csv> (calificado con math-verify) y
<salida.csv>.meta.json (tiempo, tokens, errores de calificación)."""
import sys, os, csv, time, json
os.environ["PROYECTO_RAIZ"] = "/workspace/decomposing-the-gain"
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
from comun_math import *

CONFIGS = dict({"base_mit": dict(BASE_MIT, thinking=True), "piloto_presence0": dict(PILOTO_PRESENCE0, thinking=True)},
               **CERO_EDICION)


def main():
    from vllm import LLM, SamplingParams
    modelo, config, ids_file, salida = sys.argv[1:5]
    P = CONFIGS[config]
    pensando = P["thinking"]
    muestreo = {k: v for k, v in P.items() if k != "thinking"}
    probs = cargar_problemas(ids_file)
    llm = LLM(modelo, dtype="bfloat16", max_model_len=P["max_tokens"] + 1024,
              gpu_memory_utilization=0.80, seed=0)
    tok = llm.get_tokenizer()
    prompts = [tok.apply_chat_template([{"role": "user", "content": construir_prompt(p["problem"])}], tokenize=False,
               add_generation_prompt=True, enable_thinking=pensando) for p in probs]
    sp = SamplingParams(temperature=P["temperature"], top_p=P["top_p"], top_k=P["top_k"],
                        presence_penalty=P["presence_penalty"], repetition_penalty=P["repetition_penalty"],
                        max_tokens=P["max_tokens"], seed=0)
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    seg = time.time() - t0
    # 1) guardar textos primero (si la calificación fallara, no se pierde la generación)
    res = []
    with open(salida + ".jsonl", "w", encoding="utf-8") as fj:
        for p, o in zip(probs, outs):
            c = o.outputs[0]
            res.append((p, c.text, len(c.token_ids), c.finish_reason))
            fj.write(json.dumps(dict(id=p["id"], texto=c.text, finish=c.finish_reason), ensure_ascii=False) + "\n")
    # 2) calificar
    filas, errores_calif, tot = [], 0, 0
    for p, texto, nt, fin in res:
        try:
            ok, err = int(es_correcta(texto, p["answer"], thinking=pensando)), 0
        except Exception:
            ok, err = 0, 1; errores_calif += 1
        tot += nt
        filas.append(dict(motor="vllm", modo="thinking" if pensando else "no-thinking", config=config, id=p["id"],
                          nivel=p["level"], tokens=nt, llego_limite=int(fin == "length"), correcto=ok,
                          error_calificacion=err, **muestreo))
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)
    meta = dict(config=config, problemas=len(probs), segundos=round(seg, 1), tokens_totales=tot,
                tok_por_s=round(tot / seg, 1), correctos=sum(r["correcto"] for r in filas),
                limite=sum(r["llego_limite"] for r in filas), errores_calificacion=errores_calif)
    json.dump(meta, open(salida + ".meta.json", "w"))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
