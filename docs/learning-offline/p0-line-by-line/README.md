# P0 line-by-line pack (beginner)

These guides explain the **9 P0 files** as literally as possible, for readers with **no coding background**.

1. Read [`00-glossary.md`](00-glossary.md) first (15–20 min).
2. Then read 01 → 09 in order.
3. Keep the real `.py` file open beside the guide if you can; if not, the guide quotes every line.

| # | Guide | Source file |
|---|---|---|
| 01 | [01-baseline.md](01-baseline.md) | `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py` |
| 02 | [02-config.md](02-config.md) | `Runjia/sgrna/config.py` |
| 03 | [03-io-utils.md](03-io-utils.md) | `Runjia/sgrna/io_utils.py` |
| 04 | [04-qct.md](04-qct.md) | `Runjia/sgrna/build/qct.py` |
| 05 | [05-guide-index.md](05-guide-index.md) | `Runjia/sgrna/build/build_guide_index.py` |
| 06 | [06-featurise.md](06-featurise.md) | `Runjia/sgrna/build/featurise.py` |
| 07 | [07-a-flank.md](07-a-flank.md) | `Runjia/sgrna/features/a_flank.py` |
| 08 | [08-run-ablation.md](08-run-ablation.md) | `Runjia/sgrna/harness/run_ablation.py` |
| 09 | [09-human-boundary.md](09-human-boundary.md) | `Jacky/human-boundary/scripts/run_human_boundary.py` |

Also see parent folder `LEARNING-ORDER.md` for P1+ priorities.


## Prefer readable pages (not raw Markdown)?

Open the pre-rendered HTML pack instead:

- Start at **[`html/index.html`](html/index.html)**
- Works offline in any phone/laptop browser
- Want PDF? Open an HTML file → Print → **Save as PDF**

Also see `html/HOW-TO-OPEN.txt` for device tips and free online converters (Dillinger, StackEdit, md-to-pdf).
