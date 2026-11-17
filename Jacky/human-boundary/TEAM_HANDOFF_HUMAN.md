# Jacky — human-boundary work (for the team)

All paths are relative to the repo root (`RSI-Crispr-forked`).

## Docs

- Checklist / findings: `Jacky/human-boundary/README.md`
- Human baseline HP settings: `Jacky/human-boundary/HUMAN_BASELINE_SETTINGS.md`

## Code (runners)

| What | Path |
|---|---|
| Tier 1 (locate, Family A, ladder, transfer autopsy) | `Jacky/human-boundary/scripts/run_human_boundary.py` |
| Tier 2–3 (chromatin, Family-A transfer, GC-matched transfer) | `Jacky/human-boundary/scripts/run_tier2_tier3.py` |
| Strand audit (gene-strand / Family A / purine) | `Jacky/human-boundary/scripts/run_human_strand_audit.py` |

## Experiments → result files

| Experiment | Result path(s) |
|---|---|
| Shared-column cross-kingdom bootstrap (early) | `Jacky/human-boundary/results/cross_kingdom_bootstrap.json` |
| Spacer GC shape (*E. coli* vs human) | `Jacky/human-boundary/results/gc_quadratic_proper.json`<br>`Jacky/human-boundary/results/human_gc_shape.json` |
| hg38 locate audit | `Jacky/human-boundary/results/human_locate_audit.json` |
| Human ladder (base → +Family A) | `Jacky/human-boundary/results/human_ladder.csv` |
| Transfer autopsy (“wrong GC”) | `Jacky/human-boundary/results/transfer_autopsy.json`<br>`Jacky/human-boundary/results/transfer_autopsy_by_gc_decile.csv` |
| Label / assay sanity | `Jacky/human-boundary/results/human_label_sanity.json` |
| GC + GC² feature ablation | `Jacky/human-boundary/results/human_gc_feature_ablation.csv` |
| Chromatin (K562 DNase / ATAC) | `Jacky/human-boundary/results/human_chromatin.csv` |
| Family A on both sides (kingdom transfer) | `Jacky/human-boundary/results/family_a_kingdom_transfer.csv` |
| GC-matched transfer | `Jacky/human-boundary/results/gc_matched_transfer.csv` |
| Tier 2–3 summary bundle | `Jacky/human-boundary/results/tier2_tier3_summary.json` |
| Strand / purine audit | `Jacky/human-boundary/results/human_strand_audit.json`<br>`Jacky/human-boundary/results/human_strand_family_a.csv`<br>`Jacky/human-boundary/results/human_strand_marginals.csv` |

## How to re-run

```bash
python3 Jacky/human-boundary/scripts/run_human_boundary.py
python3 Jacky/human-boundary/scripts/run_tier2_tier3.py
python3 Jacky/human-boundary/scripts/run_human_strand_audit.py
```

Needs: human + *E. coli* feature matrices, `qct_lookup_tables.json`, `v_column_mapping.json`, `hg38.fa.gz`.  
Optional for chromatin: ENCODE bigWigs under `data/reference/chromatin/`.

## Out of scope for this list

Bacterial-only Jacky work (orientation / TSS, Guo ceiling, recA, etc.) and Runjia runners (`human_baseline.py`, `kingdom_transfer.py`) are not listed here.
