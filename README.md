# Decomposing the Gain

How much of a weight-space edit's fix for reasoning loops do cheap baselines recover?

An audit of the Qwen3.5-0.8B experiment in [Sparks of Weight-Space Programming](https://rikiyat.github.io/blog/weight-space-programming/). We rebuild the published edit bit for bit and compare it with baselines that change no weights.

- **Blog (interactive):** https://jkul-png.github.io/decomposing-the-gain/
- **Paper:** [paper/decomposing_the_gain.pdf](paper/decomposing_the_gain.pdf)
- **Full model responses:** `full_responses.zip` in the [Releases](https://github.com/JKUL-png/decomposing-the-gain/releases) of this repository

Authors: Juan José Giraldo Márquez and Juan José Gómez.

## Layout

| Folder | Contents |
|---|---|
| `docs/` | The blog, served with GitHub Pages. KaTeX is hosted here, with no CDN. |
| `paper/` | PDF, LaTeX sources, the draft with a source comment next to every number, and the figures with their script. |
| `resultados/` | Results: one CSV per run with one row per problem, the aggregate tables (`tabla_*.csv`) and the summaries. |
| `datos/` | Fixed problem subsets and the published edits. |
| `scripts/` | Runs, analysis, rebuilding the edit, and the paper and blog builds. |

Folder, file and column names and code comments are in Spanish: `resultados` = results, `datos` = data, `semilla` = seed, `correcto` = correct, `llego_limite` = hit the token limit, `ficha` = model card, `cola` = run queue.

## Reproducing

Generation was run with vLLM 0.33.0 under WSL2 on one 8 GB GPU, grading with math-verify 0.9.0.

The scripts expect the repository at `/workspace/decomposing-the-gain` and the models in `~/modelos/`. Clone it there or create a symlink with that name.

1. Environment: `scripts/wsl_instalar_vllm.sh` and `scripts/wsl_instalar_paquetes.sh`.
2. Download Qwen/Qwen3.5-0.8B at revision `2fc06364715b967f1860aea9cf38778875588b17` into `~/modelos/Qwen3.5-0.8B`.
3. Rebuild the edit and the placebo: `scripts/crear_modelos_editados.py`. This checks the published hashes.
4. Runs: the `scripts/cola_*.sh` queues. The whole study took about 35 GPU hours.
5. Analysis, with no GPU: `analisis_dia.py`, `analisis_ronda2.py`, `analisis_ronda3.py`, `analisis_ficha.py`, `fraccion_ganancia.py`, `rango_edicion.py`, `tabla_tiempos.py`.
6. Figures: `paper/figuras/make_figures.py`. Paper: `scripts/construir_paper.py`. Blog: `scripts/construir_datos_blog.py`, which needs the full responses and stops if a number in the blog text is not in the paper.

Some analyses need the full responses: unzip them into `resultados/`. vLLM sampling depends on batch composition, so a rerun will not match token by token.

## License

Code is under the MIT license (see `LICENSE`). The paper, the blog text and the results are under CC BY 4.0 (see `LICENSES/CC-BY-4.0.txt`). Third-party material keeps its own license; see `THIRD_PARTY.md`.

## Citation

```bibtex
@misc{giraldo2026decomposing,
  title  = {Decomposing the Gain: How Much of a Weight-Space Edit's Fix for Reasoning Loops Do Cheap Baselines Recover?},
  author = {Giraldo M{\'a}rquez, Juan Jos{\'e} and G{\'o}mez, Juan Jos{\'e}},
  year   = {2026},
  url    = {https://github.com/JKUL-png/decomposing-the-gain}
}
```
