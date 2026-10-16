# Family A, and why *E. coli* → human fails

Jacky’s entry point for the human chapter. E. coli science is largely frozen;
this folder tracks what explains the kingdom boundary.

---

## 1. What is Family A?

**Family A (`a_flank`) = features from DNA *around* the cut site, not inside the
20 nt guide.**

The published Noshay matrix only describes the protospacer (the 20 letters the
guide matches). Family A adds:

| block | what |
|---|---|
| Near-cut sequence | one-hot bases just upstream of the spacer, the PAM’s N, and ~15 nt downstream of the PAM |
| Near-cut QCT | same quantum k-mer tables as the paper, applied to those positions |
| Wide windows | composition (GC, purine, longest run) and windowed quantum summaries at **50 / 250 / 500 / 1000 nt** on both sides |

**Why it mattered in bacteria:** it was the only large new signal
(~**+0.08 ρ** on the published *E. coli* label, ~**+0.16 ρ** on the curated
33k label). Most of the wide-window signal is flank GC / composition — a
smooth gradient, not a motif. The head-to-head with crisprHAL is decided by
the **250–1000 nt** reach their network never sees.

**Why human never had it:** Family A needs each guide **located on a reference
genome** so flanks can be cut. The human arm of the transfer used the shared
6,216 matrix columns only — **no hg38 locate, no flanks**.

Plain English: Family A asks *“what’s the DNA neighborhood like?”* The old
matrix only asked *“what’s the 20-letter word?”*

---

## 2. Checklist — explain *E. coli* → human failure

Status key: **DONE** / **PARTIAL** / **BLOCKED** / **TODO**

### A. Close E. coli loose ends

| # | item | status | notes |
|---|---|---|---|
| A1 | Tell Runjia human ρ 0.472 settings | **DONE (this folder)** | `n_features=400`, `n_estimators=1000`; old personal XGBoost, not SLICER harness — see `HUMAN_BASELINE_SETTINGS.md` |
| A2 | E. coli orientation / pivot / parity | **DONE** (Runjia + Jacky) | Not Jacky’s queue unless asked |

### B. Already measured (reuse; don’t re-run unless refreshing)

| # | item | status | artefact |
|---|---|---|---|
| B1 | Shared-column transfer both ways | **DONE** | *E. coli*→human **−0.048** [−0.062, −0.033]; human→*E. coli* **−0.056** [−0.073, −0.038] — `../agent-notes/results/cross_kingdom_bootstrap.json` |
| B2 | Within-kingdom anchors | **DONE** | *E. coli*→*E. coli* ~0.51; human→human ~0.38 (same shared cols) |
| B3 | Spacer GC shape differs | **DONE** | *E. coli* linear ρ **−0.201**, vertex below data; human linear ~0, quadratic peak at GC≈**0.57** — `../agent-notes/results/gc_quadratic_proper.json` |
| B4 | Hypothesis written | **DONE** | Not “no mechanism” — **mechanism replaced by a different shape**; chromatin/repair likely outside these features |

### C. Tier 1 — next science (needs uploads)

| # | item | status | needs | success criterion |
|---|---|---|---|---|
| C1 | Obtain human feature matrix | **BLOCKED** | `Runjia/data/raw/human_feature_matrix.csv` (~250 MB) | File readable; ~17k rows; `cut.score` |
| C2 | Decode / share columns with *E. coli* recipe | **BLOCKED** on C1 + QCT/V maps | Also `qct_lookup_tables.json`, `v_column_mapping.json` (or *E. coli* matrix to rebuild) | Same portable base featurisation path |
| C3 | Locate human guides on **hg38** | **BLOCKED** | hg38 fasta (or 2bit) + guide sequences from matrix / decode | Location rate + uniqueness reported |
| C4 | Build **Family A on human** | **BLOCKED** on C3 | Same `a_flank` recipe | `a_flank_human.csv` or cache |
| C5 | Human-only ladder | **TODO** after C2–C4 | — | ρ for: shared-cols baseline → +portable → +Family A; does Family A move human ρ? |
| C6 | Transfer autopsy (“wrong GC rule”) | **TODO** after C1 | Predictions of *E. coli*-trained model on human | Errors enriched in high-GC human guides? Transfer improve after GC match / residualise? |

### D. Tier 2 — mechanism sharpeners

| # | item | status | needs |
|---|---|---|---|
| D1 | Chromatin / accessibility at guide loci | **TODO** | Public tracks (DNase/ATAC) for located hg38 coords |
| D2 | GC + GC² as model features on human (ablation) | **TODO** | C1; optional without flanks |
| D3 | Label / assay sanity (score dist, uniqueness) | **TODO** | C1 |

### E. Tier 3 — later

| # | item | status |
|---|---|---|
| E1 | Cross-kingdom with Family A on both sides | after C4 |
| E2 | Human→*E. coli* with GC² / matched GC | after D2 |

---

## 3. What to upload (priority order)

**Minimum to unblock Tier 1**

| priority | path under `Runjia/` | what |
|---|---|---|
| 1 | `data/raw/human_feature_matrix.csv` | Noshay human matrix (~17k guides, ~250 MB) — **required** |
| 2 | `data/interim/qct_lookup_tables.json` | For Family A quantum windows |
| 3 | `data/interim/v_column_mapping.json` | For regenerating base columns |
| *or* 2–3 | `data/raw/ecoli_feature_matrix.csv` | Rebuild 2–3 from this instead |

**For locate + Family A**

| priority | path | what |
|---|---|---|
| 4 | hg38 genome | e.g. `data/reference/hg38.fa` or a Drive link — large; or we fetch from UCSC/NCBI if egress allows |
| 5 | Optional: gene / TSS annotation for human | only if we extend orientation-style controls |

**Nice to have**

| path | what |
|---|---|
| Old personal XGBoost script that hit ρ 0.472 | Provenance for Runjia’s item 4 |
| Any existing `human_transfer.csv` / locate caches from Runjia | Skip rebuilds |

Drive / direct links are fine — drop files into the workspace or paste URLs.

---

## 4. What we completed in this pass (no human matrix on disk)

- [x] Explained Family A (this README)
- [x] Wrote the checklist above
- [x] Recorded 400 / 1000 human settings for Runjia (`HUMAN_BASELINE_SETTINGS.md`)
- [x] Pointed at existing transfer + GC-shape results (B1–B4)
- [ ] C1–C6 — **blocked** until `human_feature_matrix.csv` (and QCT/V or ecoli matrix) are available

Once uploads land, say so in chat and we run C2→C6 in order.
