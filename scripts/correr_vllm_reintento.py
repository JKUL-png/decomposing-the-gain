"""Detectar bucle y reintentar (variante A) / forzar respuesta (variante B). Modelo ORIGINAL, thinking, config MIT.
Uso: python correr_vllm_reintento.py <modelo> <ids_file> <jsonl> <prefijo_salida> <semilla> [--n N] [--max-tokens M]

Para cada problema:
  intento 1 en STREAMING (una sola generacion continua, asi el presence_penalty sigue contando todos los tokens).
  Cada 512 tokens se revisa el final del texto: si una ventana de 300 caracteres aparece >= 3 veces en los ultimos 6000
  => bucle => se ABORTA la generacion.
  Variante A (reintento): si hubo bucle, se vuelve a generar desde cero con otra semilla (semilla + 1000*k), hasta 3 intentos
     en total. Se acepta el primer intento que termina solo. Si los 3 hacen bucle, cuenta el ultimo (cortado = incorrecto).
  Variante B (forzar respuesta): si el intento 1 hizo bucle, se recorta el texto donde empieza la repeticion (queda UNA copia),
     se agrega un cierre de pensamiento (</think>) y se deja que el modelo conteste (maximo 4,096 tokens; si la respuesta forzada no cierra dentro de ese tope cuenta como INCORRECTA
     y se reporta cuantas llegaron al tope). No hay mas intentos.
  Ambas variantes comparten el intento 1. Tokens 'totales' cuentan TODO lo generado, incluidos los intentos descartados.
Salidas: <prefijo>_A_s<sem>.csv, <prefijo>_B_s<sem>.csv (+ .jsonl con textos, .meta.json) y <prefijo>_intentos_s<sem>.csv.
No sobrescribe."""
import sys, os, csv, json, time, asyncio, traceback
os.environ["PROYECTO_RAIZ"] = "/workspace/decomposing-the-gain"
os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")
sys.path.insert(0, "/workspace/decomposing-the-gain/scripts")
from comun_math import *

W, K, L, CADA = 300, 3, 6000, 512          # detector (calibrado sobre textos guardados)
MAX_INTENTOS = 3
FORZAR = "\n\nOkay, I have thought about this enough. I will stop here and give my final answer now.\n</think>\n\n"
MAX_RESP_FORZADA = 4096   # decidido (2026-11-05, corregido de 2,048 a 4,096): si la respuesta forzada no cierra en este tope => incorrecta, y se reporta cuantas llegan al tope


def hay_bucle(texto):
    cola = texto[-L:]
    return len(cola) >= W and cola.count(cola[-W:]) >= K


def recortar_en_bucle(texto):
    """Deja el texto hasta la PRIMERA copia de la ventana repetida (una sola copia)."""
    cola = texto[-L:]
    w = cola[-W:]
    i = cola.find(w)
    return texto[:len(texto) - len(cola) + i + W]


def parametros(semilla, max_tokens, max_dentro=None):
    from vllm import SamplingParams
    from vllm.sampling_params import RequestOutputKind
    P = dict(BASE_MIT)
    return SamplingParams(temperature=P["temperature"], top_p=P["top_p"], top_k=P["top_k"],
                          presence_penalty=P["presence_penalty"], repetition_penalty=P["repetition_penalty"],
                          max_tokens=max_tokens, seed=semilla, output_kind=RequestOutputKind.DELTA)


async def generar(engine, prompt, sp, rid, vigilar):
    """Genera en streaming. Si vigilar=True y se detecta bucle, aborta. Devuelve dict(texto, tokens, corte)."""
    texto, ntok, ultimo, corte = "", 0, 0, "length"
    agen = engine.generate(prompt, sp, rid)
    try:
        async for out in agen:
            c = out.outputs[0]
            texto += c.text
            ntok += len(c.token_ids)
            if out.finished:
                corte = "stop" if c.finish_reason == "stop" else "length"
                break
            if vigilar and ntok - ultimo >= CADA:
                ultimo = ntok
                if hay_bucle(texto):
                    corte = "loop"
                    break
    finally:
        if corte == "loop":
            try:
                await engine.abort(rid)
            except Exception:
                pass
        try:
            await agen.aclose()
        except Exception:
            pass
    return dict(texto=texto, tokens=ntok, corte=corte)


async def resolver(engine, tok, p, prompt, semilla, max_tokens, max_len, sem):
    async with sem:
        intentos = []
        for k in range(MAX_INTENTOS):
            r = await generar(engine, prompt, parametros(semilla + 1000 * k, max_tokens), f"{p['id']}|a{k}|{semilla}", True)
            r["k"] = k + 1
            intentos.append(r)
            if r["corte"] != "loop":
                break
        A = intentos[-1]
        # variante B: a partir del intento 1
        a1 = intentos[0]
        if a1["corte"] == "loop":
            parcial = recortar_en_bucle(a1["texto"]) + FORZAR
            n_prompt = len(tok(prompt + parcial).input_ids)
            mt = max(64, min(MAX_RESP_FORZADA, max_len - n_prompt - 8))
            r2 = await generar(engine, prompt + parcial, parametros(semilla + 7777, mt), f"{p['id']}|forz|{semilla}", False)
            B = dict(texto=parcial + r2["texto"], tokens_final=r2["tokens"], tokens=a1["tokens"] + r2["tokens"],
                     corte=r2["corte"], forzado=1)
        else:
            B = dict(texto=a1["texto"], tokens_final=a1["tokens"], tokens=a1["tokens"], corte=a1["corte"], forzado=0)
        return p, intentos, A, B


async def main_async(modelo, ids_file, jsonl, prefijo, semilla, n, max_tokens):
    from vllm import AsyncEngineArgs
    from vllm.v1.engine.async_llm import AsyncLLM
    from transformers import AutoTokenizer
    salidas = {"A": f"{prefijo}_A_s{semilla}.csv", "B": f"{prefijo}_B_s{semilla}.csv"}
    if any(os.path.exists(f) for f in salidas.values()):
        print("Las salidas ya existen; no hago nada."); return 0
    probs = cargar_problemas(ids_file, jsonl)
    if n:
        probs = probs[:n]
    tok = AutoTokenizer.from_pretrained(modelo)
    prompts = [tok.apply_chat_template([{"role": "user", "content": construir_prompt(p["problem"])}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=True) for p in probs]
    max_len = max_tokens + 1024 + MAX_RESP_FORZADA
    engine = AsyncLLM.from_engine_args(AsyncEngineArgs(model=modelo, dtype="bfloat16", max_model_len=max_len,
                                                      gpu_memory_utilization=0.80, seed=0))
    sem = asyncio.Semaphore(len(probs))
    t0 = time.time()
    try:
        res = await asyncio.gather(*[resolver(engine, tok, p, pr, semilla, max_tokens, max_len, sem) for p, pr in zip(probs, prompts)])
    finally:
        try:
            engine.shutdown()
        except Exception:
            pass
    seg = time.time() - t0
    muestreo = {k: v for k, v in BASE_MIT.items()}
    tot = {"A": 0, "B": 0}
    filas = {"A": [], "B": []}
    log = []
    textos = {"A": [], "B": []}
    for p, intentos, A, B in res:
        for r in intentos:
            log.append(dict(id=p["id"], intento=r["k"], tokens=r["tokens"], corte=r["corte"]))
        for v, r in (("A", A), ("B", B)):
            texto = r["texto"]
            try:
                ok, err = int(es_correcta(texto, p["answer"], thinking=True)), 0
            except Exception:
                ok, err = 0, 1
            no_cerro = int(v == "B" and B["forzado"] == 1 and B["corte"] != "stop")
            if no_cerro:
                ok = 0   # regla del usuario: respuesta forzada que no cierra en 4,096 tokens (llega al tope) = incorrecta
            if v == "A":
                gastados = sum(x["tokens"] for x in intentos)
                extra = dict(intentos=len(intentos), tokens_final=A["tokens"], forzado=0)
                termino = A["corte"] == "stop"
            else:
                gastados = B["tokens"]
                extra = dict(intentos=1, tokens_final=B["tokens_final"], forzado=B["forzado"])
                termino = B["corte"] == "stop"
            tot[v] += gastados
            filas[v].append(dict(motor="vllm", modo="thinking", config="reintento_A" if v == "A" else "forzar_B", semilla=semilla,
                                 id=p["id"], nivel=p["level"], tokens=gastados, llego_limite=int(not termino), corte=r["corte"],
                                 correcto=ok, error_calificacion=err, forzada_no_cerro=no_cerro, **extra, **muestreo))
            textos[v].append(dict(id=p["id"], texto=texto, corte=r["corte"]))
    for v in ("A", "B"):
        with open(salidas[v] + ".jsonl", "w", encoding="utf-8") as f:
            for t in textos[v]:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        with open(salidas[v], "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=filas[v][0].keys()); w.writeheader(); w.writerows(filas[v])
        meta = dict(variante=v, semilla=semilla, problemas=len(probs), segundos=round(seg, 1), tokens_totales=tot[v],
                    correctos=sum(r["correcto"] for r in filas[v]), no_terminaron=sum(r["llego_limite"] for r in filas[v]),
                    forzadas=sum(r["forzado"] for r in filas[v]), forzadas_no_cerraron=sum(r["forzada_no_cerro"] for r in filas[v]),
                    max_resp_forzada=MAX_RESP_FORZADA, max_tokens=max_tokens, detector=dict(W=W, K=K, L=L, cada=CADA), intentos_max=MAX_INTENTOS)
        json.dump(meta, open(salidas[v] + ".meta.json", "w"))
        print(json.dumps(meta), flush=True)
    with open(f"{prefijo}_intentos_s{semilla}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=log[0].keys()); w.writeheader(); w.writerows(log)
    return 0


def main():
    args = sys.argv[1:]
    n, max_tokens = 0, BASE_MIT["max_tokens"]
    if "--n" in args:
        i = args.index("--n"); n = int(args[i + 1]); del args[i:i + 2]
    if "--max-tokens" in args:
        i = args.index("--max-tokens"); max_tokens = int(args[i + 1]); del args[i:i + 2]
    modelo, ids_file, jsonl, prefijo, semilla = args[:5]
    try:
        sys.exit(asyncio.run(main_async(modelo, ids_file, jsonl, prefijo, int(semilla), n, max_tokens)))
    except Exception:
        open(f"{prefijo}_s{semilla}.ERROR.txt", "w").write(traceback.format_exc()[-4000:])
        print("FALLO; ver el archivo ERROR", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
