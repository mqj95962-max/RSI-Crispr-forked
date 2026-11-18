# Human discovery phase — experiment list

**Goal.** Match the bacterial program’s *positive* loop: find what **raises human ρ**, then re-test whether that representation **crosses kingdoms**. Nulls already closed (shared-col GC, K562 chromatin-as-tested, strand) stay frozen.

**Two linked questions**

1. What improves the **human** model?
2. Does that same representation make **transfer** less awful?

---

## A. Runnable now (on-disk data)

| ID | Experiment | Why | Code / output |
|---|---|---|---|
| H1 | **Capacity / HP ladder** on base and base+A | Human signal is less additive; champion HPs may leave +0.10 on the table | `scripts/run_human_discovery.py` → `results/human_discovery_ladder.csv` |
| H2 | **Additivity** (ridge vs boosting) on base and base+A | Quantify interaction order; ties to depth result | → `results/human_discovery_additivity.csv` |
| H3 | **Gene-grouped CV** for base and base+A | Is the human gain locus identity vs within-gene? | → `results/human_discovery_grouped.csv` |
| H4 | **Build + ablate sequence/flank families on human**: shape (`i_shape`), mechanics (`d_mechanics`), folding (`c_folding`) on top of base+A | Bacteria-style “what else helps?” on features we can compute without new downloads | → `results/human_discovery_families.csv` + caches under `Runjia/data/interim/human_boundary/` |
| H5 | **Transfer retest** *E. coli*↔human for base / A / A+new families (same features both sides) | Ties every human gain back to the original project goal | → `results/human_discovery_transfer.csv` |

**Runner:** `python3 Jacky/human-boundary/scripts/run_human_discovery.py`

---

## B. Needs online / external data (high value)

| ID | Experiment | Data to fetch | Why it could help |
|---|---|---|---|
| H6 | **Cell-type–matched chromatin / histone marks** at guide loci | Noshay human matrix mixes sources: A375 melanoma (1,278) plus curated multi-line set (HCT116, HEK293T, HeLa, HL60). Prefer **A375 / HCT116 / HEK293T** ENCODE or Roadmap bigWigs (DNase, ATAC, H3K27ac) — not K562 | K562 was a null; wrong tissue may have hidden a real effect |
| H7 | **Expression / gene essentiality context** | GTEx or cell-line RNA-seq for the screen’s line; DepMap essentiality if relevant | Human cutting may depend on locus activity more than local sequence |
| H8 | **Second human cutting dataset** (transfer within human / different library) | Another published SpCas9 cutting screen with sequences + scores | Separates “kingdom” from “this one matrix” |
| H9 | **Repair-pathway / chromatin state annotations** | ChromHMM / Segway for matched cell type | Tests whether flank gain is really “openness / repair neighbourhood” |

We can search and download these once the screen’s cell type is confirmed.

---

## C. Interpretation rules (so we don’t thrash)

- A human arm is “real” if Δρ ≳ **+0.02** on ≥3 seeds (or clear of noise vs base+A).
- Transfer “opens” if *E. coli*→human moves from ≈−0.05 toward **≥0** on the same feature set built both sides.
- Do **not** reopen strand / shared-col GC residualise / K562±500 unless new data changes the premise.
- Improving human CV without improving transfer is still a win for Goal B; report both numbers every time.

---

## D. Success criteria for this phase

1. At least one **new positive** human effect beyond Family A, **or** a clear ceiling that base+A (+ capacity) is already near the best sequence/flank representation we can build.
2. An updated transfer table: which feature halves travel, which don’t.
3. A short team note: what to download next (H6–H9) vs what to stop.

---

## E. Status

| ID | Status |
|---|---|
| H1–H5 | **DONE** — see `DISCOVERY_RESULTS.md` (capacity is the large human gain; shape/mech/fold null; transfer unchanged) |
| H6 | **DONE** — matched-line ENCODE tracks (HCT116/HEK293T/HeLa/HL60 DNase/ATAC/H3K27ac); tiny Δρ on base (≲+0.013), ~null given Family A. See `results/human_h6_*.csv` |
| H7–H9 | **Next** — expression / second human cutting screen / repair annotations |
