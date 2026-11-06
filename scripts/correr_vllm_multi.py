"""Corre UNA configuración con varias semillas (un modelo cargado una sola vez) en vLLM, dentro de WSL.
Uso: python correr_vllm_multi.py <modelo> <config> <ids_file> <jsonl> <prefijo_salida> <semillas, ej. 1,2,3> [tarea: math|gsm8k|ifeval]
Tarea gsm8k = mismo prompt/calificador que math; ifeval = prompt crudo + corrector oficial estricto (lm-eval).
Por cada semilla s escribe <prefijo>_s<s>.csv (+ .jsonl textos, .meta.json). Si una semilla falla guarda
<prefijo>_s<s>.ERROR.txt y sigue con la siguiente (sin reintentar). No sobrescribe salidas que ya existen."""
import sys, os, csv, time, json, traceback
os.environ["PROYECTO_RAIZ"] = "/workspace/decomposing-the-gain"
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
from comun_math import *

CONFIGS = dict({"base_mit": dict(BASE_MIT, thinking=True), "nothink_mit": NOTHINK_MIT}, **CERO_EDICION)


TAREA = "math"

def calificar_ifeval(p, texto, pensando):
    """IFEval estricto a nivel de prompt (corrector oficial de lm-eval). Con thinking, solo cuenta lo que va tras </think>."""
    sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
    from ifeval_oficial import utils as U
    resp = quitar_pensamiento(texto) if pensando else texto
    doc = dict(key=p["key"], instruction_id_list=p["instruction_id_list"], prompt=p["problem"], kwargs=p["kwargs"])
    return bool(U.process_results(doc, [resp])["prompt_level_strict_acc"])


def prompt_de(p):
    return p["problem"] if TAREA == "ifeval" else construir_prompt(p["problem"])


def correr_semilla(llm, tok, probs, P, config, semilla, salida):
    from vllm import SamplingParams
    pensando = P["thinking"]
    muestreo = {k: v for k, v in P.items() if k != "thinking"}
    prompts = [tok.apply_chat_template([{"role": "user", "content": prompt_de(p)}], tokenize=False,
               add_generation_prompt=True, enable_thinking=pensando) for p in probs]
    sp = SamplingParams(temperature=P["temperature"], top_p=P["top_p"], top_k=P["top_k"],
                        presence_penalty=P["presence_penalty"], repetition_penalty=P["repetition_penalty"],
                        max_tokens=P["max_tokens"], seed=semilla)
    t0 = time.time()
    outs = llm.generate(prompts, sp)
    seg = time.time() - t0
    res = []
    with open(salida + ".jsonl", "w", encoding="utf-8") as fj:   # textos primero
        for p, o in zip(probs, outs):
            c = o.outputs[0]
            res.append((p, c.text, len(c.token_ids), c.finish_reason))
            fj.write(json.dumps(dict(id=p["id"], texto=c.text, finish=c.finish_reason), ensure_ascii=False) + "\n")
    filas, errores_calif, tot = [], 0, 0
    for p, texto, nt, fin in res:
        try:
            ok, err = int(calificar_ifeval(p, texto, pensando) if TAREA == "ifeval" else es_correcta(texto, p["answer"], thinking=pensando)), 0
        except Exception:
            ok, err = 0, 1; errores_calif += 1
        tot += nt
        filas.append(dict(motor="vllm", modo="thinking" if pensando else "no-thinking", config=config, semilla=semilla,
                          id=p["id"], nivel=p["level"], tokens=nt, llego_limite=int(fin == "length"), correcto=ok,
                          error_calificacion=err, **muestreo))
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)
    meta = dict(config=config, semilla=semilla, problemas=len(probs), segundos=round(seg, 1), tokens_totales=tot,
                tok_por_s=round(tot / seg, 1), correctos=sum(r["correcto"] for r in filas),
                limite=sum(r["llego_limite"] for r in filas), errores_calificacion=errores_calif)
    json.dump(meta, open(salida + ".meta.json", "w"))
    print(json.dumps(meta), flush=True)


def main():
    from vllm import LLM
    global TAREA
    modelo, config, ids_file, jsonl, prefijo, semillas = sys.argv[1:7]
    TAREA = sys.argv[7] if len(sys.argv) > 7 else "math"
    assert TAREA in ("math", "gsm8k", "ifeval")
    P = CONFIGS[config]
    probs = cargar_problemas(ids_file, jsonl)
    pendientes = [int(s) for s in semillas.split(",") if not os.path.exists(f"{prefijo}_s{int(s)}.csv")]
    if not pendientes:
        print("Todas las salidas ya existen; no hago nada."); return
    llm = LLM(modelo, dtype="bfloat16", max_model_len=P["max_tokens"] + 1024, gpu_memory_utilization=0.80, seed=0)
    tok = llm.get_tokenizer()
    hubo_error = False
    for s in pendientes:
        salida = f"{prefijo}_s{s}.csv"
        try:
            correr_semilla(llm, tok, probs, P, config, s, salida)
        except Exception:
            hubo_error = True
            open(f"{prefijo}_s{s}.ERROR.txt", "w").write(traceback.format_exc()[-4000:])
            print(f"semilla {s} FALLÓ; sigo con la siguiente", flush=True)
    sys.exit(1 if hubo_error else 0)


if __name__ == "__main__":
    main()
