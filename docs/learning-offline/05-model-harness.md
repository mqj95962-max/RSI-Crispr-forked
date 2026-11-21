# 05 — Model harness / `run_ablation.py` (line walkthrough)


> **Updated teaching guide:** for purpose/data-flow explanations (recommended), read [`p0-contextual/05-run-ablation.md`](p0-contextual/05-run-ablation.md).

**File:** `Runjia/sgrna/harness/run_ablation.py` (559 lines)  
*(After reorg: `from sgrna.harness.run_ablation import ...`; older Jacky scripts may still say `from sgrna.run_ablation import ...`.)*

**Role:** The shared experiment engine. Same leakage rules as the baseline, plus family ablations, grouping, permutation floors, and fold resume.

## Docstring (lines 1–36) — how to read a result

One rule above all: **every fit happens inside the training split.**

| Column | Meaning |
|---|---|
| `d_spearman` | Δ vs baseline in the same run |
| `permuted` | same family with shuffled rows (noise floor) |
| `group` | hold out genes/blocks (needed for positional features) |
| `selected` | how many family columns entered top 300 |

If Δ is inside the permutation band → the family didn’t work.

Typical notebook calls:

```python
nb.ablate()                                          # baseline only
nb.ablate(["a_flank"])
nb.ablate(["d_supercoiling"], group="bin100k", permute=True)
nb.ablate(["a_flank", "b_energy"], together=True)
```

---

## Lines 62–108 — model settings (frozen baseline twin)

```text
selector_params(seed)   → 300 trees, depth 4, lr 0.05, …  (rank columns only)
champion_params(seed)   → 400 trees (config.N_ESTIMATORS), same other knobs
make_selector(seed)     → XGBoost by default; LightGBM optional for speed
_impute(X_train, X_val) → median from TRAIN only; apply to both
```

`_impute` converts to float32, computes `nanmedian` on train, fills NaNs in train *and* val with those medians. If a column is all-NaN on train, median becomes 0.

`_safe_spearman` / `_safe_pearson` (111–122): return 0 / NaN-safe so a tiny fold doesn’t crash the summary.

---

## Lines 130–153 — `grouped_folds`

**Why:** ~20 guides per gene share a locus. Random KFold puts the same locus in train *and* val → positional features (supercoiling, nucleoid, oriC distance) can memorise “this neighbourhood scores ~X”.

Algorithm:

1. Unique group labels  
2. Shuffle with seed  
3. Split unique groups into `n_splits` chunks  
4. Yield `(train_row_indices, val_row_indices)` where val = guides whose group is in the held-out chunk  

---

## Lines 156–174 — fold checkpoints

```text
results/folds_<tag>.csv
```

Each finished fold **appends** one row. On restart, those `(seed, fold)` pairs are skipped. Designed for Colab sessions that die mid-run.

---

## Lines 177–292 — `cross_validate` (the heart)

Signature (simplified):

```python
cross_validate(X, y, feature_names, family_of,
               n_features=None, seeds=None, n_splits=None,
               groups=None, tag=None, experiment="unnamed",
               deadline=None, champion_overrides=None, return_oof=False)
```

**Per seed × fold:**

1. Skip if already in checkpoint for this `experiment`  
2. Stop if `deadline` (absolute `time.time()`) has passed  
3. `_impute(X[tr], X[va])`  
4. Fit selector → `feature_importances_` → top `n_features` (default 300)  
5. Count how many selected columns are non-`"base"` → `n_engineered_selected`  
6. Fit champion (merge `champion_overrides` if provided — used for HP capacity tests)  
7. Predict val → R², Spearman, Pearson, MSE  
8. Append checkpoint row  

**Return dict:**

- `folds` — all fold rows  
- `per_seed` — mean metrics per seed  
- `complete` — True only if all seeds×folds done  
- `summary` — `{metric: {mean, sd}}`  ← note **`sd`**, not `std`  
- `selected.engineered` — mean engineered count in top 300  
- optional `oof_pred` / `oof_y` if `return_oof=True`

---

## Lines 295–303 — `_permute_families`

Shuffles **rows** of columns belonging to named families. Keeps column structure; destroys guide↔feature pairing. That is the noise floor: if real Δ ≤ permuted Δ, the family is worthless.

---

## Lines 311–352 — `load_groups`

| `by` | What is held out |
|---|---|
| `gene` | whole gene (`b_number`) |
| `bin5k` / `bin100k` / `bin500k` | contiguous chromosome blocks |
| `arc5` | one fifth of the chromosome (strictest; forces extrapolation) |

Missing-position guides are folded into the mode group so you don’t get a 1-row validation fold that crashes Spearman.

---

## Lines 355–end — `run` + CLI

`run(families, together=..., permute=..., group_by=..., tag=..., force=...)`:

1. Always includes a `"baseline"` arm (no engineered families)  
2. Adds one arm per family, or one combined arm if `together=True`  
3. Optionally adds a permuted twin of each engineered arm  
4. Loads matrix via `load_dataset`  
5. Calls `cross_validate` for each arm  
6. Appends to `results/ablation_<tag>.csv` (skips experiments already present unless `force`)

CLI (`python -m sgrna.run_ablation` / notebook `nb.ablate`) is just argparse → `run`.

---

## Mental link to the baseline script

| Baseline script | Harness |
|---|---|
| CELL 5 `run_cv_for_seed` | `cross_validate` |
| hard-coded CSV path | `load_dataset` joins families |
| no gene grouping | `grouped_folds` + `load_groups` |
| no permutation arm | `_permute_families` / `--permute` |
| no resume | `folds_<tag>.csv` checkpoints |

---

## Checklist

- [ ] I can explain train-only impute + select in one sentence  
- [ ] I know when to use grouped CV (positional families)  
- [ ] I know what a permutation floor is for  
- [ ] I know folds can resume via `folds_<tag>.csv`  
- [ ] I know summary keys use `sd` (not `std`)  
