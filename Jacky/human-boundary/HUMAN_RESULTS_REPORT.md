# Human arm — results report (Jacky)

**Audience:** team update  
**Scope:** human / cross-kingdom work under `Jacky/human-boundary/`  
**Date of this write-up:** 17 November 2026 (Asia/Singapore)  
**Artefacts:** `Jacky/human-boundary/results/` · runners in `Jacky/human-boundary/scripts/`

---

## 1. Goal

The bacterial work showed that flanking DNA composition (**Family A**) is the large effect in *E. coli* cutting, and that models built only on guide-derived columns do not transfer to human. The human arm asked three linked questions:

1. Does Family A help on **human cutting** once guides are located on hg38?
2. What actually causes the *E. coli* ↔ human transfer failure — wrong GC rule, missing flanks, chromatin, or something else?
3. After the bacterial CRISPRi finding (Family A ≈ a strand proxy on silencing screens), does the same story apply to **human cutting**?

---

## 2. Setup (what we built)

| Step | Outcome |
|---|---|
| Human feature matrix | Noshay human matrix: 17,421 rows; 13,138 unique spacers |
| Decode / shared columns | Rebuilt guide-derived representation with the same *E. coli* QCT/V recipe |
| Locate on hg38 | 12,222 / 13,138 unique locate; **16,490** usable located rows |
| Family A on human | 348 flanking-composition columns cut from hg38 around each guide |
| Baseline HPs | Teammate settings documented (`n_features=400`, `n_estimators=1000`); harness CV on located set uses the SLICER-style regenerated base |

**Code:** `scripts/run_human_boundary.py`, `run_tier2_tier3.py`, `run_human_strand_audit.py`  
**Checklist:** `Jacky/human-boundary/README.md`

---

## 3. Results

### 3.1 Family A is real on human cutting

| Arm | Spearman ρ | Δ vs regenerated base |
|---|---:|---:|
| Regenerated base (guide-derived) | **0.382** | — |
| Base + Family A | **0.434** | **+0.052** |
| Family A alone | 0.341 | — |
| Shared published columns | 0.402 | — |

**Significance.** Flanking DNA context is not an *E. coli*-only artefact. The gain (+0.052) is smaller than the curated *E. coli* Family A jump (+0.164), but it is clearly positive. Flanks matter in both kingdoms.

---

### 3.2 Shared-column transfer fails — and “wrong GC” does not fix it

| Measurement | Result |
|---|---|
| *E. coli* → human on shared / guide-derived columns | ≈ **−0.049** |
| After residualising spacer GC² from errors | still ≈ **−0.048** |
| Correlation of transfer error with spacer GC | ρ ≈ **−0.399** (GC-shaped errors exist) |
| GC-range / histogram matching / residualise controls | shared-col transfer stays ≈ **−0.049** |
| Putting GC + GC² into the **human** model | 0.382 → **0.381** (null) |

**Significance.** Models trained on *E. coli* guide features systematically mis-rank human guides. Errors do correlate with spacer GC (the GC–activity relationship differs across kingdoms: *E. coli* linear ρ ≈ −0.20; human is roughly flat / peaks near GC ≈ 0.57). But matching or residualising GC **does not** rescue transfer, and adding GC/GC² as human features adds nothing. The kingdom break is **not** “we forgot a quadratic GC term.”

---

### 3.3 With Family A on both sides, transfer flips sign

| Feature set | *E. coli* → human | human → *E. coli* |
|---|---:|---:|
| Base (guide-derived) | **−0.049** | −0.010 |
| Family A alone | **+0.042** | **+0.108** |
| Base + Family A | **+0.022** | **+0.017** |

GC controls on the base+A arm leave transfer near +0.02 (still positive; not materially changed).

**Significance.** Part of the old “kingdom wall” was representational: the published shared columns never carried flanks on the human side. Building the same flank family on both genomes flips transfer from negative to (weakly) positive. This is **not** yet a useful predictor — magnitudes are tiny versus within-kingdom anchors — but the **sign change** matters: failure was partly “missing flanks,” not purely incompatible biology.

---

### 3.4 Chromatin accessibility is near-null (at this resolution)

| Track (K562, ±500 nt) | ρ vs cut score | Δρ when added to base |
|---|---:|---:|
| DNase | 0.042 | +0.003 |
| ATAC | 0.027 | +0.001 |
| Both | — | +0.005 |

**Significance.** Local accessibility as measured here does not explain the remaining human gap. Caveat: tracks are **K562**; if the screen’s cell type differs, this null may be the wrong tissue rather than a true biological null.

---

### 3.5 Strand / purine audit — CRISPRi story does **not** port to human cutting

Bacterial CRISPRi context (for contrast): coding-strand alone ρ ≈ 0.66; Family A given strand ≈ +0.01 on the pooled ranking.

| Human cutting test | Result |
|---|---|
| Coding-strand vs cut score | ρ **−0.010** (null) |
| Family A over base | **+0.052** |
| Family A given strand | **+0.048** (~92% of the gain survives) |
| Flank purine vs score | +0.020; as a feature over base +0.001 |
| Family A within coding / template only | **+0.058 / +0.064** |

**Significance.** On human **cutting**, gene/coding strand is not a phenotype driver, and Family A is not a strand proxy. The bacterial “Family A collapses to strand” result is a **silencing / roadblock** property. The cross-kingdom wall is therefore **not** “human was secretly a strand assay.” Live levers remain: flank representation, GC-shape inversion, and whatever still differs after flanks (repair / cell state / label).

---

## 4. Bottom line for the team

1. **Family A works on human** (+0.052 ρ) — flanks are a real, portable idea, smaller than in curated *E. coli*.
2. **Guide-only transfer still fails** (~−0.05); GC mismatch is a symptom, not the whole cause.
3. **Flanks flip cross-kingdom transfer positive** (+0.022 / flanks-alone up to +0.108) — a qualitative win on representation, not yet a practical transferred model.
4. **K562 chromatin and GC² features are nulls** for the remaining gap (with the cell-type caveat on chromatin).
5. **Strand does not explain human cutting or Family A** — do not import the CRISPRi strand account into the human cutting chapter.

---

## 5. Where to look

| Item | Path |
|---|---|
| This report | `Jacky/human-boundary/HUMAN_RESULTS_REPORT.md` |
| Checklist + plain-English takeaway | `Jacky/human-boundary/README.md` |
| Path list for sharing | `Jacky/human-boundary/TEAM_HANDOFF_HUMAN.md` |
| All small result tables | `Jacky/human-boundary/results/` |
| Runners | `Jacky/human-boundary/scripts/` |

---

## 6. Suggested next steps (open)

- Cell-type–matched chromatin / epigenetic tracks for the actual human screen (if known).
- Stronger human-side representation after flanks (repair, local structure, assay/label specifics).
- Keep bacterial CRISPRi strand results and human cutting results **separated by assay** in any write-up.
