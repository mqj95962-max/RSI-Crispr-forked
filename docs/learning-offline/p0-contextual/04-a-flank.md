# P0 #7 — Family A / `a_flank.py` (contextual guide)

**Source file:** `Runjia/sgrna/features/a_flank.py` (~239 lines)  
**Job in the project:** build the feature family that measures DNA **around** the cut — not just the 20-letter protospacer — and save it as a reusable `eng.*` block.

---

## Where this sits in the whole pipeline

```text
guide_index.csv          QCT lookup tables
(upstream/downstream,    (from qct.learn_lookup_tables)
 located flags)
        │                        │
        └──────────┬─────────────┘
                   ▼
            ★ a_flank.build ★
                   │
                   ▼
     features/a_flank.csv   (eng.flank.* columns)
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  run_ablation            Jacky human Tier-1
  (base vs base+A)        (same builder on hg38 flanks)
```

**Depends on:** step 0 (`build_guide_index` + QCT tables) and `config` flank/window constants.  
**Feeds:** every “does Family A help?” experiment — E. coli ablations, human ladder, transfer with A on both sides.

If the baseline (P0 #1) is the yardstick, **Family A is the first biology upgrade that consistently moves that yardstick**.

---

## The scientific question in plain English

The published matrix stops at the 20-mer. Cas9 does not: nearby DNA (composition, local chemistry) carries a large signal in this screen and in related work (Browne / crisprHAL wider windows).

Family A asks: **if we encode the neighborhood of the cut the same way the paper encoded the spacer’s chemistry, does prediction improve?**

---

## What `build(index)` takes and returns

| | |
|---|---|
| **Input** | A guide-index-like table: at least `sgRNAID`, `protospacer`, `pam`, `upstream`, `downstream`, `located` |
| **Also needs** | QCT lookup tables on disk (`qct.load_tables()`) |
| **Output** | One row per guide; columns all `eng.flank.*` (plus id) — ready for `save_block(..., "a_flank")` |

Guides that aren’t located (or lack a protospacer string) get a nearly empty row (NaNs). Downstream CV **median-imputes** those blanks on the training fold only — same philosophy as the baseline.

---

## The four kinds of columns (intent groups)

Think in **four products**, not 200+ individual names:

### 1. One-hot local bases — `eng.flank.seq.*`

Positions walking 5′→3′:

- `u10…u1` — ten bases immediately before the spacer  
- `pamN` — the variable base of the NGG PAM (positions 2–3 are always G, so skipped)  
- `d1…d15` — fifteen bases after the PAM  

For each position × {A,C,G,T} → a 0/1 column.  
**Why:** lets the model see exact letters near the PAM without assuming a chemistry model.

### 2. Per-position QCT — `eng.flank.qct.*`

At those same labels, look up **monomer/dimer** chemistry from the learned tables (same language as the published spacer QCT).  
**Why:** “extend the paper’s tensors outside the 20-mer” — no new quantum simulations.

### 3. Window composition — `eng.flank.comp.*`

For upstream and downstream segments at 50 / 250 / 500 / 1000 nt:

- GC fraction  
- purine fraction  
- longest homopolymer run (scaled)

**Why:** after early ablations, long-window tensor *means* were almost exactly GC (ρ≈0.998). Emitting `comp.*` makes that redundancy **visible** instead of hiding it in seventeen correlated tensor columns.

### 4. Window tensor summaries — `eng.flank.win.*`

Mean/sd of four deliberately spread series (one monomer, dimer, trimer, tetramer property) on the same nested windows.  
**Why:** keep a thin slice of chemistry summaries out to 1 kb without cloning GC seventeen times.

**Efficiency intent:** compute chemistry profiles once on the widest 1 kb, then **slice** for smaller windows — nested windows share work.

---

## How the code is organized (map)

| Piece | Role |
|---|---|
| Constants (`PREFIX`, `N_UPSTREAM`, `SUMMARY_WINDOWS`, `SUMMARY_SERIES`) | Frozen design choices aligned with `config.FLANK*` |
| `_positions()` | Builds the ordered label list `u* / pamN / d*` |
| `_extended_sequence(row)` | Glue upstream pad + spacer + PAM + downstream pad; map each label → index in that string |
| `_composition` / `_longest_run` / `_summarise_window` | Building blocks for `comp.*` and `win.*` |
| `build(index)` | Main loop over guides → records → DataFrame |
| `main()` | `load_guide_index` → `build` → `save_block(..., "a_flank")` → print column counts |

You do **not** need every loop index on first read. You need: **located flanks in → eng.flank block out**.

---

## How later code uses Family A

| Consumer | What it does with the block |
|---|---|
| `run_ablation` / `load_dataset(["a_flank"])` | Joins base + A; reports `d_spearman` vs baseline |
| Jacky `build_human_matrices` | Calls `a_flank.build` on hg38-located guides; hstacks with `featurise.matrix` |
| Strand / twin / H6 follow-ups | Ask whether A’s gain collapses to strand, duplicates, or chromatin |

Headline intuition to remember: on E. coli, A is the big positive family; on human cutting, A still helps but less, and **does not** collapse to coding-strand (that’s a later Jacky audit).

---

## Checklist

- [ ] I can explain “outside the protospacer” in one sentence  
- [ ] I know why `guide_index` flanks are required  
- [ ] I know why `comp.gc` sits beside window tensor means  
- [ ] I know the output is an `eng.*` block other tools join, not a full model by itself  
