# 04 — Family A / `a_flank.py` (line-by-line)


> **Updated teaching guide:** for purpose/data-flow explanations (recommended), read [`p0-contextual/04-a-flank.md`](p0-contextual/04-a-flank.md).

**File:** `Runjia/sgrna/features/a_flank.py` (~239 lines)  
**Role:** The project’s big positive biology feature family — DNA *around* the cut, not just the 20-mer.

## Why it exists (docstring lines 1–44)

Published matrix stops at the protospacer. Widening the window (Browne / crisprHAL) helps a lot. Family A:

1. One-hot bases near the PAM  
2. Same QCT tensors as the paper, extended into those positions  
3. Window summaries + **explicit GC/purine** out to 1 kb  

After an early ablation they learned: averaging tensors over long windows ≈ GC (ρ≈0.998), so they emit fewer tensor series + honest `comp.*` columns, and push windows to 1 kb.

---

## Lines 45–81 — Imports & constants

| Constant | Value / role |
|---|---|
| `PREFIX` | `"eng.flank"` — all columns start with this |
| `N_UPSTREAM` / `N_DOWNSTREAM` | 10 / 15 one-hot positions |
| `PER_POSITION_UNITS` | monomer + dimer only for per-base tensors |
| `SUMMARY_WINDOWS` | 50, 250, 500, 1000 |
| `SUMMARY_SERIES` | 4 (unit, property) pairs spanning descriptor space |
| `BASES` | A,C,G,T |

## Lines 84–89 — `_positions`

Builds labels: `u10…u1`, `pamN`, `d1…d15` (5′→3′). PAM positions 2–3 of NGG are constant → skipped.

## Lines 92–116 — `_extended_sequence`

Builds one string: leftover upstream pad + protospacer + PAM + downstream pad. Returns a dict mapping each label → index in that string so later lookups are O(1).

Pad of 4 lets dimer/trimer/tetramer windows still fit at the edges.

## Lines 119–148 — helpers

- `_longest_run` — longest homopolymer  
- `_composition` — GC fraction, purine fraction, maxrun/length  
- `_summarise_window` — mean/sd of a tensor profile (NaN-safe)

## Lines 151–220 — `build(index)` **(the main loop)**

For each guide row:

1. If missing protospacer or not `located` → emit nearly empty row (NaNs imputed later)  
2. Build extended sequence + index  
3. **One-hot:** for each label × base → `eng.flank.seq.{label}.{base}`  
4. **Per-position QCT:** for monomer/dimer properties × each label → `eng.flank.qct...`  
5. **Windows:** take up to 1 kb up and down; for each window size write `comp.*` and `win.*` mean/sd for the four summary series  

Nested windows: compute profile once on the widest segment, then **slice** for 50/250/500/1000 (efficiency).

Returns a DataFrame of all guides × ~348 feature columns (+ id).

## Lines 223–239 — `main`

Load guide index → `build` → `save_block(..., "a_flank")` → print column counts by type.

---

## How this connects to experiments

- Ablations ask: does base+`a_flank` beat base?  
- Human work rebuilds the same family on hg38-located guides  
- CRISPRi work found one Family A column tracks **strand**; human cutting did **not** collapse to strand  

---

## Checklist

- [ ] I can explain “outside the protospacer”  
- [ ] I know what `u*` / `pamN` / `d*` mean  
- [ ] I know why `comp.gc` exists beside window tensor means  
- [ ] I know NaN rows happen for unlocated guides  
