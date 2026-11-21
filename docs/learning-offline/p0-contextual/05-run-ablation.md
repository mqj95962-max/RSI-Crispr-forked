# P0 #8 — Model harness / `run_ablation.py` (contextual guide)

**Source file:** `Runjia/sgrna/harness/run_ablation.py` (~559 lines)  
*(Imports may say `sgrna.run_ablation` or `sgrna.harness.run_ablation` depending on reorg/shims.)*

**Job in the project:** the shared **experiment engine** — same leakage-safe exam protocol as the USE THIS baseline, plus family ablations, grouped CV, permutation floors, and resumable fold checkpoints.

---

## Where this sits in the whole pipeline

```text
BASE matrix (+ optional feature blocks from FEATURE_DIR)
        │
        ▼
  load_dataset(families)     ← joins eng.* columns; tags family_of
        │
        ▼
 ★ cross_validate / run ★
   impute → select top 300 → champion → score
        │
        ▼
 results/ablation_<tag>.csv
   spearman, d_spearman, permuted arms, selected counts
```

**Depends on:** `config` defaults (seeds, 300/400, baseline reference), `build_matrix.load_dataset`, feature blocks like `a_flank`.  
**Feeds:** every “did family X help?” table in the report; Jacky scripts import `cross_validate` / `_impute` so human numbers use the **same exam rules**.

---

## The scientific question in plain English

Adding columns is easy. Proving they help — without cheating — is the hard part.

This harness answers, for one or more feature families:

1. Does base+family beat **base alone** under the frozen CV recipe? (`d_spearman`)  
2. Is that gain bigger than a **noise floor** (row-shuffled family columns)?  
3. For positional biology, does the gain survive **holding out whole genes/blocks**?

If Δρ sits inside the permutation band, the family did not earn a write-up — no matter how many of its columns entered the top 300.

---

## Two layers: library vs driver

| Layer | Functions | Role |
|---|---|---|
| **Core exam** | `selector_params`, `champion_params`, `_impute`, `cross_validate` | Same spirit as baseline CELL 5 |
| **Experiment driver** | `run`, `load_groups`, `_permute_families`, CLI/`main` | Decide *which* matrices to exam and how to log them |

Jacky often imports only the core exam pieces and builds its own matrices.

---

## Core exam — `cross_validate` data flow

```text
For each seed:
  For each fold (random KFold OR grouped_folds):
      skip if already in folds_<tag>.csv
      impute with TRAIN medians only
      fit selector → top n_features (default 300)
      count how many selected columns are non-"base"
      fit champion (optional champion_overrides for HP probes)
      score val → append checkpoint row
Summarise mean ± sd across seed means  (keys use "sd", not "std")
```

**Outputs of one call:** dict with `folds`, `per_seed`, `summary`, `complete`, `selected.engineered`, optional OOF predictions.

**Why checkpoints?** A flank-family 5-seed run can outlast a Colab session. Finished `(seed, fold)` pairs are skipped on resume.

---

## Grouped CV — when random folds lie

```python
def grouped_folds(groups, n_splits, seed): ...
def load_groups(ids, by="gene"|"bin100k"|...): ...
```

**Problem:** ~20 guides/gene share a locus. Random splits put the same neighborhood in train *and* val → positional features (supercoiling, ori distance, …) can memorize “this region scores ~X.”

**Fix:** hold out whole genes or chromosome bins/`arc5`.  
**Rule of thumb:** report positional families under grouped CV before believing them. Family A’s sequence flanks are less about locus ID, but human gene-grouped checks still matter for honesty.

---

## Permutation floor — `_permute_families`

Shuffle **rows** of columns belonging to named families (keep column structure; break guide↔feature pairing). Re-run CV.  

**Interpretation:** real Δρ should clearly beat permuted Δρ. Otherwise you fitted noise that happens to look like a family.

---

## Driver — `run(families, …)`

Always includes a `"baseline"` arm (no engineered families). Then:

- one arm per family, **or** one stacked arm if `together=True`  
- optional `"(permuted)"` twin when `permute=True`  
- writes/appends `results/ablation_<tag>.csv`  
- computes `d_r2` / `d_spearman` vs the baseline row in that table  
- saves `ablation_<tag>_settings.json` (seeds, group_by, frozen `config.BASELINE`, …)

**CLI / notebook:** `nb.ablate(["a_flank"])` or `python -m … --families a_flank --permute --group gene`.

---

## Mental link to the USE THIS baseline

| Baseline script | Harness |
|---|---|
| CELL 5 `run_cv_for_seed` | `cross_validate` |
| Hard-coded Drive CSV | `load_dataset` joins blocks |
| No gene grouping | `grouped_folds` + `load_groups` |
| No permutation arm | `_permute_families` |
| No resume | `folds_<tag>.csv` |

Hyperparameters intentionally match so **Δρ vs baseline is apples-to-apples**.

---

## How Jacky / later code use this

- Human ladder calls `cross_validate` on regenerated base / base+A matrices  
- Discovery / H6 / twin scripts reuse `_impute` + `cross_validate` (sometimes with HP overrides)  
- Reading results: trust `d_spearman` only alongside permutation + appropriate grouping  

---

## Checklist

- [ ] I can explain train-only impute + select in one sentence  
- [ ] I know what `d_spearman` compares against  
- [ ] I know when grouped CV is required  
- [ ] I know what a permutation floor is for  
- [ ] I know fold checkpoints let long runs resume  
