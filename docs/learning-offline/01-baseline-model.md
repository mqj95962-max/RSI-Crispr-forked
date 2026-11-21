# 01 — Baseline model (line walkthrough)


> **Updated teaching guide:** for purpose/data-flow explanations (recommended), read [`p0-contextual/01-baseline.md`](p0-contextual/01-baseline.md) instead of relying only on this shorter summary.

**File:** `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py` (~642 lines)  
**Role:** The trusted E. coli cutting model. Everything later is compared to this.

## Mental model (read this first)

You have a big CSV of guides × features and a label `cut.score`. The script:

1. Loads the matrix  
2. For each of 5 random seeds × 5 CV folds:  
   - split train/val  
   - **impute NaNs using train medians only**  
   - fit a throwaway XGBoost to **rank** features on train  
   - keep top **300**  
   - fit the real (“champion”) XGBoost on those 300  
   - score Spearman / R² / Pearson on val  
3. Averages across seeds → **the number you report**  
4. Optionally trains one production model on *all* data (not for reporting)

**Leakage rule:** validation rows must never influence imputation or which features are chosen.

---

## Lines 1–14 — Header comment

States the purpose: five seeds `41–45`, leakage-safe CV. Tells you to trust CELL 7 scores, not CELL 8’s production fit.

## Lines 16–34 — CELL 0: install packages

`install_if_missing` tries `import`, and if that fails runs `pip install`. Loop installs numpy, pandas, sklearn, scipy, xgboost, joblib. Colab-friendly.

## Lines 36–54 — CELL 1: imports + Drive

Standard science stack. `from google.colab import drive; drive.mount(...)` only works in Colab — locally you’d comment this out and set a local `DATA_PATH`.

## Lines 56–108 — CELL 2: config

| Symbol | Meaning |
|---|---|
| `DATA_PATH` | Which CSV to load (E. coli or human toggled by comments) |
| `TARGET_COLUMN` | `"cut.score"` |
| `N_FEATURES` | 300 columns selected per fold |
| `N_ESTIMATORS` | 400 trees in the champion |
| `N_SPLITS` / `SEEDS` | 5-fold × seeds 41–45 |
| `NON_FEATURE_COLUMNS` | IDs/sequences dropped so they aren’t used as features |
| `ENGINEERED_PREFIXES` | Detects `eng.*` / `regional_qct` if present |

`is_engineered_feature` / `engineered_family` only **label** columns; they don’t create Family A.

## Lines 110–179 — CELL 3: helpers

- `stable_spearman` / `stable_pearson` — return 0 if NaN (avoid crashing summaries)  
- `median_impute_train_val` — **critical**: medians from train; applied to train *and* val  
- `median_impute_full` — for production model only  
- `selector_params` — shallow 300-tree model for ranking  
- `champion_params` — 400-tree model for prediction  

Same hyperparameter recipe later appears in `config.py` / `run_ablation.py`.

## Lines 182–236 — CELL 4: load data

```text
header=1   → row 0 is a title row in Noshay’s CSV; real headers are row 1
```

Steps:

1. Require `sgRNAID` + `cut.score`  
2. Drop ID/sequence columns → numeric feature matrix  
3. Drop all-NaN columns  
4. Drop rows with missing y  
5. Print shape + how many engineered columns were loaded + a hash of feature names (reproducibility)

## Lines 238–324 — CELL 5: `run_cv_for_seed`

For each fold:

1. `KFold(...).split` → `train_idx`, `val_idx`  
2. Impute with train medians  
3. Fit selector → `feature_importances_` → `top_idx` of length 300  
4. Fit champion on `X_tr[:, top_idx]`  
5. Save model JSON + fold metadata (indices, selected names, medians)  
6. Predict val → record R², Spearman, Pearson, MSE  

**This is the scientific core of the whole project.**

## Lines 327–366 — CELL 6: all five seeds

Loops seeds, concatenates fold records, writes:

- `all_seed_fold_results.csv`  
- `per_seed_summary.csv`  
- `selected_feature_counts.csv` (how often each feature was picked)

## Lines 368–391 — CELL 7: report (THE numbers)

Prints mean ± std across seeds. **These are the official baseline numbers** (~R² 0.29, Spearman ~0.53 on the frozen E. coli setup).

## Lines 393–413 — CELL 8: production model

Fits selector + champion on **all** rows with seed 42. Useful for deploying predictions. **Do not quote its training fit as validation.**

## Lines 415–end — CELL 9: save artifacts

Pickles, JSON feature lists, importance CSV, metadata blob, CV manifest for SHAP later.

---

## Checklist for this file

- [ ] I can explain “leakage-safe” in one sentence  
- [ ] I know why imputation uses train medians only  
- [ ] I know selector ≠ champion  
- [ ] I know CELL 7 is reported, CELL 8 is not  
