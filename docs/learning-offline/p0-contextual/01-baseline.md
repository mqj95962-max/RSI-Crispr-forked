# P0 #1 — The baseline model (contextual guide)

**Source file:** `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py` (~642 lines)  
**Audience:** little/no coding background  
**Job of this file in the project:** prove how well we can predict E. coli Cas9 cutting efficiency from a big spreadsheet of guide features — fairly, without cheating.

---

## Where this sits in the whole pipeline

```text
Lab measured cut.score for ~14k guides
        +
Published / engineered feature columns (thousands of numbers per guide)
        │
        ▼
 ★ THIS SCRIPT ★
 Leakage-safe XGBoost evaluation (5 seeds × 5 folds)
        │
        ▼
Official numbers you quote (≈ R² 0.29, Spearman ≈ 0.53)
        │
        ▼
Later: Family A, ablations, human transfer all ask
“did we beat THIS baseline?”
```

If you only remember one thing: **this script is the yardstick**. Everything Runjia/Jacky/Joshua add later is compared to the scores CELL 7 prints here.

---

## The scientific question in plain English

Each row is one CRISPR guide. Columns are measurements / encodings of that guide’s DNA (and sometimes engineered extras). One special column, `cut.score`, is the lab’s answer: how well that guide cut.

We want a computer model that, given the other columns, predicts `cut.score`.

**Fairness rule (called “leakage-safe”):** when we grade the model, it must not have peeked at the exam answers while studying. In code terms: for every train/validation split, blank-filling and “which 300 columns matter?” are decided using **training rows only**.

---

## How to read this file (map, not every keystroke)

The script is written as Colab “cells” (`# %% CELL …`). Think of them as chapters of one experiment:

| Cell | Purpose in the workflow |
|---|---|
| 0–1 | Make sure toolboxes exist; connect Drive (Colab only) |
| 2 | Settings: which CSV, 300 features, 400 trees, seeds 41–45 |
| 3 | Helper recipes reused every fold (impute, score, model knobs) |
| 4 | Load spreadsheet → numeric matrix `X` and label vector `y` |
| 5 | **Core science:** one seed’s 5-fold CV |
| 6 | Repeat for all five seeds; write CSVs |
| 7 | **Report** the averages (trust these) |
| 8–9 | Train a “production” model on all data (deploy, don’t quote as validation) |
| 10–11 | Save a contract test + verify 25 fold artifacts |

Below we walk those chapters with **why**, then show the important code grouped by intent.

---

## Chapter A — Settings that freeze the experiment (CELL 2)

**Why it exists:** so everyone re-runs the *same* protocol. If Joshua changes `N_FEATURES` to 500 and Jacky keeps 300, their Spearman numbers are not comparable.

```python
DATA_PATH = ".../ecoli_feature_matrix_seed_nonadd.csv"
TARGET_COLUMN = "cut.score"
N_FEATURES = 300
N_ESTIMATORS = 400
N_SPLITS = 5
SEEDS = [41, 42, 43, 44, 45]
```

| Name | Role in the CRISPR/ML story |
|---|---|
| `DATA_PATH` | **Input:** the big feature table (E. coli). Comment/uncomment lines swap E. coli vs human CSVs. |
| `TARGET_COLUMN` | **Output we’re predicting:** measured cutting efficiency. |
| `N_FEATURES` | After ranking all columns, keep only the top 300 for the real model. Shrinks noise and matches the frozen paper figure. |
| `N_ESTIMATORS` | Champion forest size (400 trees). |
| `N_SPLITS` / `SEEDS` | 5 exam splits × 5 different shuffles → 25 mini-exams, then average. |

`NON_FEATURE_COLUMNS` lists ID/sequence-looking names that must **not** be treated as predictors (they identify the guide; they aren’t chemistry features).

`ENGINEERED_PREFIXES` / `is_engineered_feature` only **label** columns that start with `eng.` or `regional_qct`. This baseline does not *create* Family A; it can still *notice* engineered columns if your CSV already contains them.

**Outputs of this chapter:** a folder `five_seed_champion_ecoli_xgboost_baseline/` for CSVs, models, and fold metadata.

---

## Chapter B — Helper recipes (CELL 3)

These are small tools CELL 5 calls repeatedly. Understanding them once unlocks the whole CV loop.

### Filling blanks without cheating

```python
def median_impute_train_val(X_train, X_val):
    medians = np.nanmedian(X_train, axis=0)   # from TRAIN only
    # … fill NaNs in train AND val using those medians …
```

**Workflow meaning:** real screens have missing chemistry values. We fill blanks with the column’s middle value. Using validation rows to compute that middle value would leak exam information — so medians come from train only, then get applied to both sets.

`median_impute_full` is the same idea for CELL 8’s production model (all rows allowed, because there is no held-out exam in that chapter).

### Scoring predictions

```python
def stable_spearman(y_true, y_pred): ...
def stable_pearson(y_true, y_pred): ...
```

**Workflow meaning:** after the model predicts validation guides, we need a grade.

- **Spearman** — do the *rankings* agree? (Usually the headline for guide design: “pick the better guides.”)
- **Pearson / R² / MSE** — numeric agreement / error size.

`stable_*` returns 0 instead of crashing if the statistic is undefined (tiny/odd folds).

### Two models with different jobs

```python
def selector_params(seed):   # 300 trees — ranks columns
def champion_params(seed):   # 400 trees — real predictor
```

**Workflow meaning:**

1. **Selector** = disposable “which columns look useful?” model. Its predictions are thrown away; we only keep `feature_importances_`.
2. **Champion** = the model whose validation Spearman you report.

Same hyperparameter *style* as later `run_ablation.py` / `config.py`, so Family A ablations stay comparable to this baseline.

---

## Chapter C — Load the spreadsheet into `X` and `y` (CELL 4)

**Input:** CSV at `DATA_PATH`.  
**Output:** `X_raw` (guides × features), `y` (cut.score), `feature_names`.

Critical detail:

```python
df = pd.read_csv(DATA_PATH, header=1, ...)  # row 0 is a title banner
```

Noshay’s table has a junk title row first; real headers are on row 1. Every honest reader in this repo uses `header=1` for that reason (`config.BASE_MATRIX_HEADER_ROW` later).

Then the script:

1. Requires `sgRNAID` + `cut.score`
2. Drops ID/sequence columns so they can’t become fake features
3. Forces remaining columns to numbers (`coerce` → blanks become NaN)
4. Drops all-NaN columns and rows with missing `y`
5. Prints a **feature hash** — a fingerprint of column names so you can prove two runs used the same feature order

**How later code uses this:** CELL 5 indexes into `X_raw` / `y` by row number. Saved fold metadata stores those indices so Joshua’s SHAP script can reload the exact train/val split.

---

## Chapter D — The heart: leakage-safe CV for one seed (CELL 5)

```python
def run_cv_for_seed(seed, ...):
    kf = KFold(n_splits=5, shuffle=True, random_state=seed)
    for fold, (train_idx, val_idx) in enumerate(kf.split(X_raw), start=1):
        # 1) split
        # 2) impute using train medians
        # 3) fit selector on train → pick top 300 columns
        # 4) fit champion on those 300 train columns
        # 5) predict val → record R² / Spearman / Pearson / MSE
        # 6) save model JSON + fold metadata (indices, medians, selected names)
```

### Data flow inside one fold

```text
All guides
   │
   ├─ train_idx ──► X_tr, y_tr ──► medians, selector, champion
   │
   └─ val_idx  ──► X_val, y_val ──► predict & score only
                      ▲
                      └── uses medians + selected columns from TRAIN
```

**Why save fold artifacts?** Downstream interpretability (SHAP) and audits need the *exact* model that produced a fold’s score — not a re-fit that might differ.

**Engineered counts in the fold log** (`eng_selected`, etc.) answer: “when engineered columns are present, how often do they enter the top 300?” On the plain published matrix those stay 0.

---

## Chapter E — Five seeds, then the number you trust (CELLs 6–7)

CELL 6 loops `SEEDS`, concatenates fold rows, writes:

| File | What it’s for |
|---|---|
| `all_seed_fold_results.csv` | Every seed×fold score (raw evidence) |
| `per_seed_summary.csv` | Mean ± spread within each seed |
| `selected_feature_counts.csv` | How often each column was picked across 25 folds |

CELL 7 prints the **overall means across seed means**. Those lines are the project’s frozen baseline (~R² 0.294, Spearman ~0.528). `config.BASELINE` and ablation `d_spearman` later refer back to this idea.

---

## Chapter F — Production model (CELLs 8–9) — useful, but not the grade

```python
# Fit selector + champion on ALL rows (seed 42)
# Save .pkl model, selected indices, imputer medians, metadata JSON
```

**Why it exists:** so you can score a *new* guide later without redoing CV.  
**Why you must not quote its training fit:** it studied every row — there’s no honest exam left.

CELL 10–11 write a tiny inference self-test and verify that all 25 fold models reload with 300 inputs and 400 trees. That’s quality control for the artifact pack, not new biology.

---

## What “success” looks like after this file

You should be able to say:

1. **Input** = feature matrix + `cut.score`  
2. **Process** = 5×5 leakage-safe select-300 + XGBoost  
3. **Output** = CV metrics (CELL 7) + optional production model  
4. **Consumers** = every ablation / human ladder that asks “Δ vs baseline”

---

## Checklist

- [ ] I can draw the train→impute→select→champion→val diagram  
- [ ] I know CELL 7 is reported and CELL 8 is not  
- [ ] I know why medians and feature picks must not use validation rows  
- [ ] I know this file’s scores are the yardstick Family A tries to beat  
