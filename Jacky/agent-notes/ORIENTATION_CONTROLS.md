# Jacky — orientation controls (all in one place)

This folder is the easy entry point on `main`. Same content as the
`cursor/jacky-orientation-controls-82a3` work, gathered here so you do not
need to switch branches.

**Lead finding:** RegulonDB TSS opposite−same Δ = **0.051 [0.020, 0.082]**
(P(Δ≤0)=0). Nearest-gene Δ does not survive dist+GC matching — lead with TSS.

| path | what |
|---|---|
| `README.md` (this file) | write-up for Runjia / the paper |
| `INTERGENIC_ORIENTATION.md` | earlier nearest-gene + bootstrap CI note |
| `scripts/` | runners |
| `results/` | tables / CIs |

---

# Orientation controls (Part 4 item 3) — DONE

Follow-on to `INTERGENIC_ORIENTATION.md`. Same frozen recipe
(`6,169` base + `348` Family A), primary set **S6 Good** (n = 8,954).

Runner: `scripts/run_orientation_controls.py (paths still point at Jacky/agent-notes/results when run)`.

## What was asked

1. Promoter vs RBS separated  
2. Curated TSS / operon orientation (RegulonDB) instead of nearest gene alone  
3. Match / control distance and GC  
4. Block-bootstrap CI on each orientation interaction  

(Nearest-gene Δ CI was already shipped; this deepens it.)

## Headline Δ CIs (opp − same; 2000× 100 kb block bootstrap)

| analysis | asym opp | asym same | **Δ [95% CI]** | P(Δ≤0) |
|---|---:|---:|---|---:|
| gene (prior) | 0.040 | 0.014 | 0.026 [−0.006, 0.058] | 0.054 |
| **TSS (RegulonDB)** | **0.061** | **0.011** | **0.051 [0.020, 0.082]** | **0.000** |
| operon (RegulonDB) | 0.053 | 0.031 | 0.023 [−0.008, 0.055] | 0.085 |
| promoter × gene | 0.056 | 0.031 | 0.024 [−0.021, 0.068] | 0.137 |
| RBS × gene | 0.026 | −0.011 | 0.038 [−0.008, 0.084] | 0.056 |
| gene, matched dist+GC | 0.029 | 0.022 | 0.007 [−0.024, 0.038] | 0.337 |
| **TSS, matched dist+GC** | **0.048** | **0.023** | **0.025 [−0.003, 0.053]** | **0.041** |

Matched = greedy 1:1 NN on z-scored (`gene_dist` or `tss_dist`, `flank_gc500`),
caliper `0.75√p`.

## Which file to quote (Runjia’s question)

**For the paper, use `intergenic_orientation_controls_delta_ci.csv` only** — not
`summary.csv` for the headline asymmetries or Δ.

| quantity | `summary.csv` | `delta_ci.csv` |
|---|---|---|
| method | mean of **per-fold** Spearman ρ per arm, then `gain_dn_matched − gain_up` | **one** Spearman ρ on **pooled OOF** predictions: ρ(y, pred_dn) − ρ(y, pred_up) |
| TSS opposite asym | 0.0645 | **0.0614** |
| TSS same asym | 0.0104 | **0.0106** |
| TSS Δ | 0.0540 (by subtraction) | **0.0507** (reported; bootstrap uses same OOF point) |

The bootstrap CI [0.020, 0.082] and P(Δ≤0)=0 are tied to the OOF definition.
`summary.csv` is still useful for per-arm fold-mean gains and debugging, but
the ~0.003 gap on TSS opposite is **fold-mean vs pooled-OOF**, not an internal
inconsistency within either file.

## Reading (for Runjia / the paper)

1. **TSS orientation is the cleanest positive control.** Opposite-TSS asymmetry
   is clearly positive; same-TSS is near zero; Δ’s CI excludes 0.
2. **Nearest-gene orientation is partly a cohort confound.** After matching on
   distance + flank GC, the gene Δ collapses (P(Δ≤0)=0.34). Prefer TSS wording
   over “nearest gene” in the main text.
3. **TSS still leans positive after the same matching** (P=0.041), but the 95%
   CI just includes 0 — report as “survives matching directionally; borderline
   at 95%.”
4. **Promoter and RBS both show the same sign pattern** (stronger PAM-side
   advantage when opposite). Split samples are underpowered for Δ; do not claim
   kind-specific differences.
5. **Operon strand is weaker than TSS** (Δ CI includes 0). Keep as supporting,
   not lead.

## Artefacts

| file | content |
|---|---|
| `results/intergenic_orientation_controls_summary.csv` | per-stratum gains |
| `results/intergenic_orientation_controls_delta_ci.csv` | bootstrap Δ table |
| `results/intergenic_orientation_cohort_balance.json` | distance / GC by stratum |
| `results/intergenic_orientation_controls_index_slim.csv` | guide labels (no sequences) |
| `results/intergenic_orientation_controls_asymmetry.csv` | raw arm ρ |

Full sequence-bearing index is local-only (`*_controls_index.csv`, ~19 MB).

## Suggested Part 5 / Part 4 wording

> On Guo’s intergenic library, PAM-side flank asymmetry depends on guide
> orientation relative to the nearest RegulonDB TSS (Δ = 0.051, 95% CI
> [0.020, 0.082]). The effect is in the same direction for promoter and RBS
> guides. Matching on distance-to-TSS and flank GC attenuates but does not
> reverse it. Nearest-gene orientation shows a similar pattern that does **not**
> survive the same matching, so the paper should lead with TSS, not nearest gene.

**Withdrawn for main text:** unweighted “0.047 opposite / 0.005 same” nearest-gene
split from the first intergenic pass; block bootstrap on nearest gene is
0.040 vs 0.014, Δ 0.026 [−0.006, 0.058], and matched dist+GC kills the Δ.
