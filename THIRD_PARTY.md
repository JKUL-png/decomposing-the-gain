# Third-party material

License texts are in `LICENSES/`. Checked on 2026-11-06 against each primary source.

| Path | Source | License | Text |
|---|---|---|---|
| `datos/math500_*` | [HuggingFaceH4/MATH-500](https://huggingface.co/datasets/HuggingFaceH4/MATH-500), a 500-problem subset of MATH from [openai/prm800k](https://github.com/openai/prm800k), based on [hendrycks/math](https://github.com/hendrycks/math) | MIT (both upstream repositories; the Hugging Face page lists no license of its own) | `MIT-openai-prm800k.txt`, `MIT-hendrycks-math.txt` |
| `datos/gsm8k_*` | [openai/gsm8k](https://huggingface.co/datasets/openai/gsm8k), from [openai/grade-school-math](https://github.com/openai/grade-school-math) | MIT | `MIT-openai-grade-school-math.txt` |
| `datos/ifeval_*` | [google/IFEval](https://huggingface.co/datasets/google/IFEval) | Apache 2.0 | `Apache-2.0.txt` |
| `datos/mit_exp8/` | Edits and manifests from [RikiyaT/lm_understand-logs](https://github.com/RikiyaT/lm_understand-logs), by the authors of "LLMs can understand and write neural network weights". Unchanged. | CC BY 4.0 | `CC-BY-4.0.txt` |
| `scripts/mit_codigo/` | Scripts from the same repository. Unchanged. | MIT | `MIT-lm_understand-logs.txt` |
| `scripts/ifeval_oficial/` | IFEval checker from [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) | Apache 2.0 for the files with a Google Research header; MIT for the rest | `Apache-2.0.txt`, `MIT-lm-evaluation-harness.txt` |
| `docs/vendor/katex/` | [KaTeX](https://katex.org) 0.19.1. Unchanged. | MIT | `docs/vendor/katex/LICENSE` |

The fixed subsets in `datos/` keep the original problem text and add our own selection and ids.

The Qwen3.5-0.8B weights are not included. The scripts expect them from [Qwen/Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B).
