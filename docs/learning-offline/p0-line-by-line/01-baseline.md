# P0 line-by-line: `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py`
**Why this file matters:** The champion E. coli cutting model — what every later experiment is compared to.
**Length:** 642 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Imagine grading a student with a practice test and a real exam, five different times, and never letting exam questions leak into studying. That is this whole file.

---
### Line 1
```python
# ============================================================
```
**Plain English:** Human-only note (Python ignores it): ============================================================

### Line 2
```python
# FIVE-SEED BASELINE MODEL: E. coli CRISPR sgRNA Cut-Score Prediction
```
**Plain English:** Human-only note (Python ignores it): FIVE-SEED BASELINE MODEL: E. coli CRISPR sgRNA Cut-Score Prediction

### Line 3
```python
# Project: Enhancing sgRNA efficiency in CRISPR-Cas9 genome editing
```
**Plain English:** Human-only note (Python ignores it): Project: Enhancing sgRNA efficiency in CRISPR-Cas9 genome editing

### Line 4
```python
#
```
**Plain English:** Empty comment line — ignored by Python; just spacing for humans.

### Line 5
```python
# Purpose:
```
**Plain English:** Human-only note (Python ignores it): Purpose:

### Line 6
```python
#   Leakage-safe baseline evaluation across five seeds: 41, 42, 43, 44, 45.
```
**Plain English:** Human-only note (Python ignores it): Leakage-safe baseline evaluation across five seeds: 41, 42, 43, 44, 45.

### Line 7
```python
#   For every seed and every CV fold, feature selection is fit on the TRAIN
```
**Plain English:** Human-only note (Python ignores it): For every seed and every CV fold, feature selection is fit on the TRAIN

### Line 8
```python
#   split only. Validation folds never influence imputation, feature ranking,
```
**Plain English:** Human-only note (Python ignores it): split only. Validation folds never influence imputation, feature ranking,

### Line 9
```python
#   model fitting, or feature selection.
```
**Plain English:** Human-only note (Python ignores it): model fitting, or feature selection.

### Line 10
```python
#
```
**Plain English:** Empty comment line — ignored by Python; just spacing for humans.

### Line 11
```python
# Report/trust the five-seed CV scores from CELL 7 / output CSVs.
```
**Plain English:** Human-only note (Python ignores it): Report/trust the five-seed CV scores from CELL 7 / output CSVs.

### Line 12
```python
# The final model trained on all data in CELL 8 is for production/inference only;
```
**Plain English:** Human-only note (Python ignores it): The final model trained on all data in CELL 8 is for production/inference only;

### Line 13
```python
# it is not a validation score.
```
**Plain English:** Human-only note (Python ignores it): it is not a validation score.

### Line 14
```python
# ============================================================
```
**Plain English:** Human-only note (Python ignores it): ============================================================

### Line 16
```python
# %% CELL 0 — Install missing packages if needed
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 0 — Install missing packages if needed**.

### Line 17
```python
import sys
```
**Plain English:** Load toolbox code: `import sys` — used here for **Python runtime (arguments, exit codes)**.

### Line 18
```python
import subprocess
```
**Plain English:** Load toolbox code: `import subprocess` — used here for **run other programs (e.g. pip install)**.

### Line 21
```python
def install_if_missing(import_name, pip_name=None):
```
**Plain English:** Defines a reusable recipe named `install_if_missing`. Inputs in parentheses: `import_name, pip_name=None`. Nothing runs yet until something *calls* `install_if_missing(...)`.

### Line 22
```python
    pip_name = pip_name or import_name
```
**Plain English:** Store a value: the name `pip_name` now holds the result of `pip_name or import_name`. Whenever you later write that name, you mean this value.

### Line 23
```python
    try:
```
**Plain English:** Try: run the indented block, but be ready to catch errors without crashing.

### Line 24
```python
        __import__(import_name)
```
**Plain English:** Run this instruction: `__import__(import_name)`.

### Line 25
```python
    except ImportError:
```
**Plain English:** If the `try` block fails with this kind of error, run this recovery block instead → `except ImportError:`.

### Line 26
```python
        print(f"Installing {pip_name}...")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Installing {pip_name}...")`.

### Line 27
```python
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
```
**Plain English:** Run this instruction: `subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])`.

### Line 30
```python
for _mod, _pip in [
```
**Plain English:** Loop: repeat the indented block once for each item → `_mod, _pip in [`.

### Line 31
```python
    ("numpy", None), ("pandas", None), ("sklearn", "scikit-learn"),
```
**Plain English:** Run this instruction: `("numpy", None), ("pandas", None), ("sklearn", "scikit-learn"),`.

### Line 32
```python
    ("scipy", None), ("xgboost", None), ("joblib", None),
```
**Plain English:** Run this instruction: `("scipy", None), ("xgboost", None), ("joblib", None),`.

### Line 33
```python
]:
```
**Plain English:** Run this instruction: `]:`.

### Line 34
```python
    install_if_missing(_mod, _pip)
```
**Plain English:** Run this instruction: `install_if_missing(_mod, _pip)`.

### Line 36
```python
# %% CELL 1 — Imports
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 1 — Imports**.

### Line 37
```python
import os
```
**Plain English:** Load toolbox code: `import os` — used here for **talk to the operating system (paths, env vars)**.

### Line 38
```python
import json
```
**Plain English:** Load toolbox code: `import json` — used here for **read/write JSON text files**.

### Line 39
```python
import hashlib
```
**Plain English:** Load toolbox code: `import hashlib` — used here for **fingerprints (hashes) of text**.

### Line 40
```python
import warnings
```
**Plain English:** Load toolbox code: `import warnings` — used here for **control warning messages**.

### Line 41
```python
from collections import Counter
```
**Plain English:** Load toolbox code: `from collections import Counter` — used here for **extra containers like Counter / defaultdict**.

### Line 43
```python
warnings.filterwarnings("ignore")
```
**Plain English:** Run this instruction: `warnings.filterwarnings("ignore")`.

### Line 45
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 46
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 47
```python
import xgboost as xgb
```
**Plain English:** Load toolbox code: `import xgboost as xgb` — used here for **the gradient-boosted tree learner**.

### Line 48
```python
import joblib
```
**Plain English:** Load toolbox code: `import joblib` — used here for **save/load Python objects to disk**.

### Line 49
```python
from scipy.stats import spearmanr, pearsonr
```
**Plain English:** Load toolbox code: `from scipy.stats import spearmanr, pearsonr` — used here for **scientific stats (Spearman/Pearson)**.

### Line 50
```python
from sklearn.model_selection import KFold
```
**Plain English:** Load toolbox code: `from sklearn.model_selection import KFold` — used here for **classic ML helpers (splits, metrics)**.

### Line 51
```python
from sklearn.metrics import r2_score, mean_squared_error
```
**Plain English:** Load toolbox code: `from sklearn.metrics import r2_score, mean_squared_error` — used here for **classic ML helpers (splits, metrics)**.

### Line 53
```python
from google.colab import drive
```
**Plain English:** Colab-only: connect Google Drive so the script can see your CSV files. On a normal laptop this line would fail — comment it out and set a local path.

### Line 54
```python
drive.mount("/content/drive")
```
**Plain English:** Run this instruction: `drive.mount("/content/drive")`.

### Line 56
```python
# %% CELL 2 — Config
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 2 — Config**.

### Line 57
```python
# Put this script in the same folder as ecoli_feature_matrix.csv, or edit DATA_PATH.
```
**Plain English:** Human-only note (Python ignores it): Put this script in the same folder as ecoli_feature_matrix.csv, or edit DATA_PATH.

### Line 59
```python
#Ecoli data:
```
**Plain English:** Human-only note (Python ignores it): Ecoli data:

### Line 60
```python
#DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/ecoli_feature_matrix.csv"
```
**Plain English:** Human-only note (Python ignores it): DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/ecoli_feature_matrix.csv"

### Line 61
```python
DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/ecoli_feature_matrix_seed_nonadd.csv"
```
**Plain English:** Full path to the big feature spreadsheet on Google Drive. Change this if your file lives elsewhere.

### Line 63
```python
#Human data
```
**Plain English:** Human-only note (Python ignores it): Human data

### Line 64
```python
#DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/human_feature_matrix.csv"
```
**Plain English:** Human-only note (Python ignores it): DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/human_feature_matrix.csv"

### Line 65
```python
#DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/human_feature_matrix_seed_nonadd.csv"
```
**Plain English:** Human-only note (Python ignores it): DATA_PATH = "/content/drive/MyDrive/CRISPR_Project/human_feature_matrix_seed_nonadd.csv"

### Line 67
```python
TARGET_COLUMN = "cut.score"
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 69
```python
# Frozen baseline settings.
```
**Plain English:** Human-only note (Python ignores it): Frozen baseline settings.

### Line 70
```python
N_FEATURES = 300
```
**Plain English:** Store a value: the name `N_FEATURES` now holds the result of `300`. Whenever you later write that name, you mean this value.

### Line 71
```python
N_ESTIMATORS = 400
```
**Plain English:** **How many trees** the champion XGBoost forest grows (400). More trees ≈ more capacity, slower training.

### Line 73
```python
N_SPLITS = 5
```
**Plain English:** **How many CV folds** (5). Each fold holds out ~20% of rows as the exam.

### Line 74
```python
SEEDS = [41, 42, 43, 44, 45]
```
**Plain English:** **Random seeds** `[41..45]`. Re-run the whole 5-fold exam five times with different shuffles, then average — so one lucky shuffle can’t fool you.

### Line 75
```python
FINAL_PRODUCTION_SEED = 42
```
**Plain English:** Store a value: the name `FINAL_PRODUCTION_SEED` now holds the result of `42`. Whenever you later write that name, you mean this value.

### Line 76
```python
SHUFFLE = True
```
**Plain English:** Store a value: the name `SHUFFLE` now holds the result of `True`. Whenever you later write that name, you mean this value.

### Line 78
```python
OUTPUT_DIR = "five_seed_champion_ecoli_xgboost_baseline"
```
**Plain English:** Store a value: the name `OUTPUT_DIR` now holds the result of `"five_seed_champion_ecoli_xgboost_baseline"`. Whenever you later write that name, you mean this value.

### Line 79
```python
os.makedirs(OUTPUT_DIR, exist_ok=True)
```
**Plain English:** Run this instruction: `os.makedirs(OUTPUT_DIR, exist_ok=True)`.

### Line 80
```python
CV_MODEL_DIR = os.path.join(OUTPUT_DIR, "cv_models")
```
**Plain English:** Store a value: the name `CV_MODEL_DIR` now holds the result of `os.path.join(OUTPUT_DIR, "cv_models")`. Whenever you later write that name, you mean this value.

### Line 81
```python
CV_FOLD_DIR = os.path.join(OUTPUT_DIR, "cv_folds")
```
**Plain English:** Store a value: the name `CV_FOLD_DIR` now holds the result of `os.path.join(OUTPUT_DIR, "cv_folds")`. Whenever you later write that name, you mean this value.

### Line 82
```python
os.makedirs(CV_MODEL_DIR, exist_ok=True)
```
**Plain English:** Run this instruction: `os.makedirs(CV_MODEL_DIR, exist_ok=True)`.

### Line 83
```python
os.makedirs(CV_FOLD_DIR, exist_ok=True)
```
**Plain English:** Run this instruction: `os.makedirs(CV_FOLD_DIR, exist_ok=True)`.

### Line 84
```python
cv_manifest_entries = {}
```
**Plain English:** Store a value: the name `cv_manifest_entries` now holds the result of `{}`. Whenever you later write that name, you mean this value.

### Line 86
```python
NON_FEATURE_COLUMNS = [
```
**Plain English:** Store a value: the name `NON_FEATURE_COLUMNS` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 87
```python
    "sgRNAID", "sequence", "Sequence", "sgRNA", "sgrna",
```
**Plain English:** Run this instruction: `"sgRNAID", "sequence", "Sequence", "sgRNA", "sgrna",`.

### Line 88
```python
    "guide", "Guide", "guide_sequence", "GuideSequence",
```
**Plain English:** Run this instruction: `"guide", "Guide", "guide_sequence", "GuideSequence",`.

### Line 89
```python
    "target_sequence", "TargetSequence",
```
**Plain English:** Run this instruction: `"target_sequence", "TargetSequence",`.

### Line 90
```python
]
```
**Plain English:** Run this instruction: `]`.

### Line 92
```python
# Prefixes for engineered feature columns if they appear in a future CSV.
```
**Plain English:** Human-only note (Python ignores it): Prefixes for engineered feature columns if they appear in a future CSV.

### Line 93
```python
# This baseline script does not create engineered features; this is only metadata.
```
**Plain English:** Human-only note (Python ignores it): This baseline script does not create engineered features; this is only metadata.

### Line 94
```python
ENGINEERED_PREFIXES = ("regional_qct", "eng.")
```
**Plain English:** Store a value: the name `ENGINEERED_PREFIXES` now holds the result of `("regional_qct", "eng.")`. Whenever you later write that name, you mean this value.

### Line 97
```python
def is_engineered_feature(name) -> bool:
```
**Plain English:** Defines a reusable recipe named `is_engineered_feature`. Inputs in parentheses: `name`. Returns type hint: bool. Nothing runs yet until something *calls* `is_engineered_feature(...)`.

### Line 98
```python
    return str(name).strip().startswith(ENGINEERED_PREFIXES)
```
**Plain English:** Finish this function and send back: `str(name).strip().startswith(ENGINEERED_PREFIXES)`.

### Line 101
```python
def engineered_family(name) -> str:
```
**Plain English:** Defines a reusable recipe named `engineered_family`. Inputs in parentheses: `name`. Returns type hint: str. Nothing runs yet until something *calls* `engineered_family(...)`.

### Line 102
```python
    s = str(name).strip()
```
**Plain English:** Store a value: the name `s` now holds the result of `str(name).strip()`. Whenever you later write that name, you mean this value.

### Line 103
```python
    if s.startswith("regional_qct"):
```
**Plain English:** Decision: run the indented block only when this condition is true → `s.startswith("regional_qct")`.

### Line 104
```python
        return "regional_qct"
```
**Plain English:** Finish this function and send back: `"regional_qct"`.

### Line 105
```python
    if s.startswith("eng."):
```
**Plain English:** Decision: run the indented block only when this condition is true → `s.startswith("eng.")`.

### Line 106
```python
        return "eng_extra"
```
**Plain English:** Finish this function and send back: `"eng_extra"`.

### Line 107
```python
    return "original"
```
**Plain English:** Finish this function and send back: `"original"`.

### Line 110
```python
# %% CELL 3 — Helpers
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 3 — Helpers**.

### Line 111
```python
def stable_spearman(y_true, y_pred) -> float:
```
**Plain English:** Defines a reusable recipe named `stable_spearman`. Inputs in parentheses: `y_true, y_pred`. Returns type hint: float. Nothing runs yet until something *calls* `stable_spearman(...)`.

### Line 112
```python
    rho, _ = spearmanr(y_true, y_pred)
```
**Plain English:** Compute Spearman correlation (ranking agreement) between true and predicted exam scores.

### Line 113
```python
    return 0.0 if np.isnan(rho) else float(rho)
```
**Plain English:** Finish this function and send back: `0.0 if np.isnan(rho) else float(rho)`.

### Line 116
```python
def stable_pearson(y_true, y_pred) -> float:
```
**Plain English:** Defines a reusable recipe named `stable_pearson`. Inputs in parentheses: `y_true, y_pred`. Returns type hint: float. Nothing runs yet until something *calls* `stable_pearson(...)`.

### Line 117
```python
    rho, _ = pearsonr(y_true, y_pred)
```
**Plain English:** Run this instruction: `rho, _ = pearsonr(y_true, y_pred)`.

### Line 118
```python
    return 0.0 if np.isnan(rho) else float(rho)
```
**Plain English:** Finish this function and send back: `0.0 if np.isnan(rho) else float(rho)`.

### Line 121
```python
def median_impute_train_val(X_train, X_val):
```
**Plain English:** Defines a reusable recipe named `median_impute_train_val`. Inputs in parentheses: `X_train, X_val`. Nothing runs yet until something *calls* `median_impute_train_val(...)`.

### Line 122
```python
    """Median-impute NaNs using stats fit on the TRAIN fold only."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Median-impute NaNs using stats fit on the TRAIN fold only.

### Line 123
```python
    X_train = X_train.astype(np.float32, copy=True)
```
**Plain English:** Store a value: the name `X_train` now holds the result of `X_train.astype(np.float32, copy=True)`. Whenever you later write that name, you mean this value.

### Line 124
```python
    X_val = X_val.astype(np.float32, copy=True)
```
**Plain English:** Store a value: the name `X_val` now holds the result of `X_val.astype(np.float32, copy=True)`. Whenever you later write that name, you mean this value.

### Line 125
```python
    medians = np.nanmedian(X_train, axis=0)
```
**Plain English:** Compute the **median** of each column using training rows only, ignoring NaNs. Median = middle value — robust to outliers. This is the fill-in recipe.

### Line 126
```python
    medians = np.where(np.isnan(medians), 0.0, medians)
```
**Plain English:** Store a value: the name `medians` now holds the result of `np.where(np.isnan(medians), 0.0, medians)`. Whenever you later write that name, you mean this value.

### Line 127
```python
    tr_rows, tr_cols = np.where(np.isnan(X_train))
```
**Plain English:** Run this instruction: `tr_rows, tr_cols = np.where(np.isnan(X_train))`.

### Line 128
```python
    va_rows, va_cols = np.where(np.isnan(X_val))
```
**Plain English:** Run this instruction: `va_rows, va_cols = np.where(np.isnan(X_val))`.

### Line 129
```python
    X_train[tr_rows, tr_cols] = medians[tr_cols]
```
**Plain English:** Run this instruction: `X_train[tr_rows, tr_cols] = medians[tr_cols]`.

### Line 130
```python
    X_val[va_rows, va_cols] = medians[va_cols]
```
**Plain English:** Run this instruction: `X_val[va_rows, va_cols] = medians[va_cols]`.

### Line 131
```python
    return X_train, X_val, medians
```
**Plain English:** Finish this function and send back: `X_train, X_val, medians`.

### Line 134
```python
def median_impute_full(X):
```
**Plain English:** Defines a reusable recipe named `median_impute_full`. Inputs in parentheses: `X`. Nothing runs yet until something *calls* `median_impute_full(...)`.

### Line 135
```python
    """Median-impute full data for the final production model only."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Median-impute full data for the final production model only.

### Line 136
```python
    X = X.astype(np.float32, copy=True)
```
**Plain English:** Store a value: the name `X` now holds the result of `X.astype(np.float32, copy=True)`. Whenever you later write that name, you mean this value.

### Line 137
```python
    medians = np.nanmedian(X, axis=0)
```
**Plain English:** Compute the **median** of each column using training rows only, ignoring NaNs. Median = middle value — robust to outliers. This is the fill-in recipe.

### Line 138
```python
    medians = np.where(np.isnan(medians), 0.0, medians)
```
**Plain English:** Store a value: the name `medians` now holds the result of `np.where(np.isnan(medians), 0.0, medians)`. Whenever you later write that name, you mean this value.

### Line 139
```python
    rows, cols = np.where(np.isnan(X))
```
**Plain English:** Run this instruction: `rows, cols = np.where(np.isnan(X))`.

### Line 140
```python
    X[rows, cols] = medians[cols]
```
**Plain English:** Run this instruction: `X[rows, cols] = medians[cols]`.

### Line 141
```python
    return X, medians
```
**Plain English:** Finish this function and send back: `X, medians`.

### Line 144
```python
def feature_name_hash(feature_names) -> str:
```
**Plain English:** Defines a reusable recipe named `feature_name_hash`. Inputs in parentheses: `feature_names`. Returns type hint: str. Nothing runs yet until something *calls* `feature_name_hash(...)`.

### Line 145
```python
    payload = json.dumps(list(feature_names), separators=(",", ":"), ensure_ascii=False)
```
**Plain English:** Store a value: the name `payload` now holds the result of `json.dumps(list(feature_names), separators=(",", ":"), ensure_ascii=False)`. Whenever you later write that name, you mean this value.

### Line 146
```python
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```
**Plain English:** Finish this function and send back: `hashlib.sha256(payload.encode("utf-8")).hexdigest()`.

### Line 149
```python
def selector_params(seed: int) -> dict:
```
**Plain English:** Defines a reusable recipe named `selector_params`. Inputs in parentheses: `seed: int`. Returns type hint: dict. Nothing runs yet until something *calls* `selector_params(...)`.

### Line 150
```python
    return dict(
```
**Plain English:** Finish this function and send back: `dict(`.

### Line 151
```python
        n_estimators=300,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `300,`. Whenever you later write that name, you mean this value.

### Line 152
```python
        learning_rate=0.05,
```
**Plain English:** Store a value: the name `learning_rate` now holds the result of `0.05,`. Whenever you later write that name, you mean this value.

### Line 153
```python
        max_depth=4,
```
**Plain English:** Store a value: the name `max_depth` now holds the result of `4,`. Whenever you later write that name, you mean this value.

### Line 154
```python
        subsample=0.8,
```
**Plain English:** Store a value: the name `subsample` now holds the result of `0.8,`. Whenever you later write that name, you mean this value.

### Line 155
```python
        colsample_bytree=0.8,
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8,`. Whenever you later write that name, you mean this value.

### Line 156
```python
        reg_alpha=0.0,
```
**Plain English:** Store a value: the name `reg_alpha` now holds the result of `0.0,`. Whenever you later write that name, you mean this value.

### Line 157
```python
        reg_lambda=1.0,
```
**Plain English:** Store a value: the name `reg_lambda` now holds the result of `1.0,`. Whenever you later write that name, you mean this value.

### Line 158
```python
        min_child_weight=1,
```
**Plain English:** Store a value: the name `min_child_weight` now holds the result of `1,`. Whenever you later write that name, you mean this value.

### Line 159
```python
        random_state=seed,
```
**Plain English:** Store a value: the name `random_state` now holds the result of `seed,`. Whenever you later write that name, you mean this value.

### Line 160
```python
        n_jobs=-1,
```
**Plain English:** Store a value: the name `n_jobs` now holds the result of `-1,`. Whenever you later write that name, you mean this value.

### Line 161
```python
        tree_method="hist",
```
**Plain English:** Store a value: the name `tree_method` now holds the result of `"hist",`. Whenever you later write that name, you mean this value.

### Line 162
```python
        importance_type="gain",
```
**Plain English:** Store a value: the name `importance_type` now holds the result of `"gain",`. Whenever you later write that name, you mean this value.

### Line 163
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 166
```python
def champion_params(seed: int) -> dict:
```
**Plain English:** Defines a reusable recipe named `champion_params`. Inputs in parentheses: `seed: int`. Returns type hint: dict. Nothing runs yet until something *calls* `champion_params(...)`.

### Line 167
```python
    return dict(
```
**Plain English:** Finish this function and send back: `dict(`.

### Line 168
```python
        n_estimators=N_ESTIMATORS,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `N_ESTIMATORS,`. Whenever you later write that name, you mean this value.

### Line 169
```python
        learning_rate=0.05,
```
**Plain English:** Store a value: the name `learning_rate` now holds the result of `0.05,`. Whenever you later write that name, you mean this value.

### Line 170
```python
        max_depth=4,
```
**Plain English:** Store a value: the name `max_depth` now holds the result of `4,`. Whenever you later write that name, you mean this value.

### Line 171
```python
        subsample=0.8,
```
**Plain English:** Store a value: the name `subsample` now holds the result of `0.8,`. Whenever you later write that name, you mean this value.

### Line 172
```python
        colsample_bytree=0.8,
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8,`. Whenever you later write that name, you mean this value.

### Line 173
```python
        reg_alpha=0.0,
```
**Plain English:** Store a value: the name `reg_alpha` now holds the result of `0.0,`. Whenever you later write that name, you mean this value.

### Line 174
```python
        reg_lambda=1.0,
```
**Plain English:** Store a value: the name `reg_lambda` now holds the result of `1.0,`. Whenever you later write that name, you mean this value.

### Line 175
```python
        min_child_weight=1,
```
**Plain English:** Store a value: the name `min_child_weight` now holds the result of `1,`. Whenever you later write that name, you mean this value.

### Line 176
```python
        random_state=seed,
```
**Plain English:** Store a value: the name `random_state` now holds the result of `seed,`. Whenever you later write that name, you mean this value.

### Line 177
```python
        n_jobs=-1,
```
**Plain English:** Store a value: the name `n_jobs` now holds the result of `-1,`. Whenever you later write that name, you mean this value.

### Line 178
```python
        tree_method="hist",
```
**Plain English:** Store a value: the name `tree_method` now holds the result of `"hist",`. Whenever you later write that name, you mean this value.

### Line 179
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 182
```python
# %% CELL 4 — Load data
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 4 — Load data**.

### Line 183
```python
print(f"Loading: {DATA_PATH}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Loading: {DATA_PATH}")`.

### Line 184
```python
if not os.path.exists(DATA_PATH):
```
**Plain English:** Decision: run the indented block only when this condition is true → `not os.path.exists(DATA_PATH)`.

### Line 185
```python
    raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 186
```python
        f"Could not find {DATA_PATH!r}. Put this script in the same folder as "
```
**Plain English:** Run this instruction: `f"Could not find {DATA_PATH!r}. Put this script in the same folder as "`.

### Line 187
```python
        "ecoli_feature_matrix.csv, or edit DATA_PATH."
```
**Plain English:** Run this instruction: `"ecoli_feature_matrix.csv, or edit DATA_PATH."`.

### Line 188
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 190
```python
df = pd.read_csv(DATA_PATH, header=1, low_memory=False)  # row 1 is a title row
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 192
```python
required = {"sgRNAID", TARGET_COLUMN}
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 193
```python
missing = required - set(df.columns)
```
**Plain English:** Store a value: the name `missing` now holds the result of `required - set(df.columns)`. Whenever you later write that name, you mean this value.

### Line 194
```python
if missing:
```
**Plain English:** Decision: run the indented block only when this condition is true → `missing`.

### Line 195
```python
    raise ValueError(f"CSV is missing columns {missing}.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"CSV is missing columns {missing}.")`.

### Line 197
```python
# Keep target and sgRNAID rows defined; then convert y to numeric and filter y NaNs.
```
**Plain English:** Human-only note (Python ignores it): Keep target and sgRNAID rows defined; then convert y to numeric and filter y NaNs.

### Line 198
```python
df = df.dropna(subset=["sgRNAID", TARGET_COLUMN])
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 199
```python
y = pd.to_numeric(df[TARGET_COLUMN], errors="coerce").to_numpy(dtype=np.float64)
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 201
```python
drop_cols = [TARGET_COLUMN] + [c for c in NON_FEATURE_COLUMNS if c in df.columns]
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 202
```python
X_df = df.drop(columns=drop_cols).apply(pd.to_numeric, errors="coerce")
```
**Plain English:** Store a value: the name `X_df` now holds the result of `df.drop(columns=drop_cols).apply(pd.to_numeric, errors="coerce")`. Whenever you later write that name, you mean this value.

### Line 204
```python
all_nan_cols = X_df.columns[X_df.isna().all()].tolist()
```
**Plain English:** Store a value: the name `all_nan_cols` now holds the result of `X_df.columns[X_df.isna().all()].tolist()`. Whenever you later write that name, you mean this value.

### Line 205
```python
if all_nan_cols:
```
**Plain English:** Decision: run the indented block only when this condition is true → `all_nan_cols`.

### Line 206
```python
    print(f"Dropping {len(all_nan_cols)} all-NaN feature columns.")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Dropping {len(all_nan_cols)} all-NaN feature columns.")`.

### Line 207
```python
    X_df = X_df.drop(columns=all_nan_cols)
```
**Plain English:** Store a value: the name `X_df` now holds the result of `X_df.drop(columns=all_nan_cols)`. Whenever you later write that name, you mean this value.

### Line 209
```python
feature_names = list(X_df.columns)
```
**Plain English:** Store a value: the name `feature_names` now holds the result of `list(X_df.columns)`. Whenever you later write that name, you mean this value.

### Line 210
```python
engineered_mask = np.array([is_engineered_feature(n) for n in feature_names], dtype=bool)
```
**Plain English:** Store a value: the name `engineered_mask` now holds the result of `np.array([is_engineered_feature(n) for n in feature_names], dtype=bool)`. Whenever you later write that name, you mean this value.

### Line 211
```python
feature_family = np.array([engineered_family(n) for n in feature_names], dtype=object)
```
**Plain English:** Store a value: the name `feature_family` now holds the result of `np.array([engineered_family(n) for n in feature_names], dtype=object)`. Whenever you later write that name, you mean this value.

### Line 212
```python
X_raw = X_df.to_numpy(dtype=np.float32)
```
**Plain English:** Store a value: the name `X_raw` now holds the result of `X_df.to_numpy(dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 214
```python
valid_y = ~np.isnan(y)
```
**Plain English:** Store a value: the name `valid_y` now holds the result of `~np.isnan(y)`. Whenever you later write that name, you mean this value.

### Line 215
```python
if valid_y.sum() < len(y):
```
**Plain English:** Decision: run the indented block only when this condition is true → `valid_y.sum() < len(y)`.

### Line 216
```python
    print(f"Dropping {len(y) - valid_y.sum()} rows with missing {TARGET_COLUMN}.")
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 217
```python
    X_raw = X_raw[valid_y]
```
**Plain English:** Store a value: the name `X_raw` now holds the result of `X_raw[valid_y]`. Whenever you later write that name, you mean this value.

### Line 218
```python
    y = y[valid_y]
```
**Plain English:** Store a value: the name `y` now holds the result of `y[valid_y]`. Whenever you later write that name, you mean this value.

### Line 220
```python
if N_FEATURES > X_raw.shape[1]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `N_FEATURES > X_raw.shape[1]`.

### Line 221
```python
    raise ValueError(f"N_FEATURES={N_FEATURES} exceeds available features ({X_raw.shape[1]}).")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"N_FEATURES={N_FEATURES} exceeds available features ({X_raw.shape[1]}).")`.

### Line 223
```python
feature_hash = feature_name_hash(feature_names)
```
**Plain English:** Store a value: the name `feature_hash` now holds the result of `feature_name_hash(feature_names)`. Whenever you later write that name, you mean this value.

### Line 224
```python
n_eng_loaded = int(engineered_mask.sum())
```
**Plain English:** Store a value: the name `n_eng_loaded` now holds the result of `int(engineered_mask.sum())`. Whenever you later write that name, you mean this value.

### Line 225
```python
n_regional_loaded = int((feature_family == "regional_qct").sum())
```
**Plain English:** Store a value: the name `n_regional_loaded` now holds the result of `int((feature_family == "regional_qct").sum())`. Whenever you later write that name, you mean this value.

### Line 226
```python
n_eng_extra_loaded = int((feature_family == "eng_extra").sum())
```
**Plain English:** Store a value: the name `n_eng_extra_loaded` now holds the result of `int((feature_family == "eng_extra").sum())`. Whenever you later write that name, you mean this value.

### Line 227
```python
print(f"Rows: {X_raw.shape[0]} | Features: {X_raw.shape[1]} | Target: {TARGET_COLUMN}")
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 228
```python
print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 229
```python
    f"Engineered features LOADED: {n_eng_loaded} "
```
**Plain English:** Run this instruction: `f"Engineered features LOADED: {n_eng_loaded} "`.

### Line 230
```python
    f"(regional_qct={n_regional_loaded}, eng.*={n_eng_extra_loaded})"
```
**Plain English:** Run this instruction: `f"(regional_qct={n_regional_loaded}, eng.*={n_eng_extra_loaded})"`.

### Line 231
```python
)
```
**Plain English:** Run this instruction: `)`.

### Line 232
```python
if n_eng_loaded == 0:
```
**Plain English:** Decision: run the indented block only when this condition is true → `n_eng_loaded == 0`.

### Line 233
```python
    print("  -> Looks like the plain/original matrix (no eng.*/regional_qct columns).")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("  -> Looks like the plain/original matrix (no eng.*/regional_qct columns).")`.

### Line 234
```python
else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 235
```python
    print("  -> Engineered columns detected — confirm this matches the CSV you intended.")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("  -> Engineered columns detected — confirm this matches the CSV you intended.")`.

### Line 236
```python
print(f"Feature hash: {feature_hash}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Feature hash: {feature_hash}")`.

### Line 238
```python
# %% CELL 5 — Leakage-safe CV for one seed
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 5 — Leakage-safe CV for one seed**.

### Line 239
```python
def run_cv_for_seed(seed: int, n_features: int = N_FEATURES, n_estimators: int = N_ESTIMATORS):
```
**Plain English:** Defines a reusable recipe named `run_cv_for_seed`. Inputs in parentheses: `seed: int, n_features: int = N_FEATURES, n_estimators: int = N_ESTIMATORS`. Nothing runs yet until something *calls* `run_cv_for_seed(...)`.

### Line 240
```python
    """Run leakage-safe fold-internal feature selection and XGBoost evaluation."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Run leakage-safe fold-internal feature selection and XGBoost evaluation.

### Line 241
```python
    print("\n" + "=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n" + "=" * 70)`.

### Line 242
```python
    print(f"STARTING SEED {seed}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"STARTING SEED {seed}")`.

### Line 243
```python
    print("=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=" * 70)`.

### Line 245
```python
    kf = KFold(n_splits=N_SPLITS, shuffle=SHUFFLE, random_state=seed)
```
**Plain English:** Create a 5-fold splitter. `shuffle=True` mixes rows first; `random_state=seed` makes that mix reproducible for this seed.

### Line 246
```python
    fold_records = []
```
**Plain English:** Store a value: the name `fold_records` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 247
```python
    selected_counter = Counter()
```
**Plain English:** Store a value: the name `selected_counter` now holds the result of `Counter()`. Whenever you later write that name, you mean this value.

### Line 249
```python
    for fold, (train_idx, val_idx) in enumerate(kf.split(X_raw), start=1):
```
**Plain English:** Loop: repeat the indented block once for each item → `fold, (train_idx, val_idx) in enumerate(kf.split(X_raw), start=1)`.

### Line 250
```python
        X_tr_raw, X_val_raw = X_raw[train_idx], X_raw[val_idx]
```
**Plain English:** Run this instruction: `X_tr_raw, X_val_raw = X_raw[train_idx], X_raw[val_idx]`.

### Line 251
```python
        y_tr, y_val = y[train_idx], y[val_idx]
```
**Plain English:** Run this instruction: `y_tr, y_val = y[train_idx], y[val_idx]`.

### Line 253
```python
        # Fit imputer on training fold only.
```
**Plain English:** Human-only note (Python ignores it): Fit imputer on training fold only.

### Line 254
```python
        X_tr, X_val, medians = median_impute_train_val(X_tr_raw, X_val_raw)
```
**Plain English:** Run this instruction: `X_tr, X_val, medians = median_impute_train_val(X_tr_raw, X_val_raw)`.

### Line 256
```python
        # Fit selector on training fold only.
```
**Plain English:** Human-only note (Python ignores it): Fit selector on training fold only.

### Line 257
```python
        selector = xgb.XGBRegressor(**selector_params(seed))
```
**Plain English:** Store a value: the name `selector` now holds the result of `xgb.XGBRegressor(**selector_params(seed))`. Whenever you later write that name, you mean this value.

### Line 258
```python
        selector.fit(X_tr, y_tr)
```
**Plain English:** Train the throwaway **selector** model on training features/labels only. Its predictions are ignored; we only want `feature_importances_` (which columns mattered).

### Line 259
```python
        top_idx = np.argsort(selector.feature_importances_)[::-1][:n_features]
```
**Plain English:** Rank columns by importance (gain) and take the best `n_features` (300). `[::-1]` reverses so largest importance comes first.

### Line 260
```python
        selected_names = [feature_names[i] for i in top_idx]
```
**Plain English:** Store a value: the name `selected_names` now holds the result of `[feature_names[i] for i in top_idx]`. Whenever you later write that name, you mean this value.

### Line 261
```python
        selected_counter.update(selected_names)
```
**Plain English:** Run this instruction: `selected_counter.update(selected_names)`.

### Line 263
```python
        n_eng = int(engineered_mask[top_idx].sum())
```
**Plain English:** Store a value: the name `n_eng` now holds the result of `int(engineered_mask[top_idx].sum())`. Whenever you later write that name, you mean this value.

### Line 264
```python
        n_regional = int((feature_family[top_idx] == "regional_qct").sum())
```
**Plain English:** Store a value: the name `n_regional` now holds the result of `int((feature_family[top_idx] == "regional_qct").sum())`. Whenever you later write that name, you mean this value.

### Line 265
```python
        n_eng_extra = int((feature_family[top_idx] == "eng_extra").sum())
```
**Plain English:** Store a value: the name `n_eng_extra` now holds the result of `int((feature_family[top_idx] == "eng_extra").sum())`. Whenever you later write that name, you mean this value.

### Line 267
```python
        # Train final model on selected features only.
```
**Plain English:** Human-only note (Python ignores it): Train final model on selected features only.

### Line 268
```python
        model = xgb.XGBRegressor(**champion_params(seed))
```
**Plain English:** Store a value: the name `model` now holds the result of `xgb.XGBRegressor(**champion_params(seed))`. Whenever you later write that name, you mean this value.

### Line 269
```python
        model.fit(X_tr[:, top_idx], y_tr)
```
**Plain English:** Run this instruction: `model.fit(X_tr[:, top_idx], y_tr)`.

### Line 271
```python
        # Preserve the exact fitted validation model and its preprocessing contract.
```
**Plain English:** Human-only note (Python ignores it): Preserve the exact fitted validation model and its preprocessing contract.

### Line 272
```python
        artifact_name = f"seed_{seed}_fold_{fold}.json"
```
**Plain English:** Store a value: the name `artifact_name` now holds the result of `f"seed_{seed}_fold_{fold}.json"`. Whenever you later write that name, you mean this value.

### Line 273
```python
        model_path = os.path.join(CV_MODEL_DIR, artifact_name)
```
**Plain English:** Store a value: the name `model_path` now holds the result of `os.path.join(CV_MODEL_DIR, artifact_name)`. Whenever you later write that name, you mean this value.

### Line 274
```python
        fold_path = os.path.join(CV_FOLD_DIR, artifact_name)
```
**Plain English:** Store a value: the name `fold_path` now holds the result of `os.path.join(CV_FOLD_DIR, artifact_name)`. Whenever you later write that name, you mean this value.

### Line 275
```python
        model.save_model(model_path)
```
**Plain English:** Run this instruction: `model.save_model(model_path)`.

### Line 276
```python
        fold_metadata = {
```
**Plain English:** Store a value: the name `fold_metadata` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 277
```python
            "seed": int(seed),
```
**Plain English:** Run this instruction: `"seed": int(seed),`.

### Line 278
```python
            "fold": int(fold),
```
**Plain English:** Run this instruction: `"fold": int(fold),`.

### Line 279
```python
            "train_indices": train_idx.tolist(),
```
**Plain English:** Run this instruction: `"train_indices": train_idx.tolist(),`.

### Line 280
```python
            "validation_indices": val_idx.tolist(),
```
**Plain English:** Run this instruction: `"validation_indices": val_idx.tolist(),`.

### Line 281
```python
            "selected_feature_indices": top_idx.tolist(),
```
**Plain English:** Run this instruction: `"selected_feature_indices": top_idx.tolist(),`.

### Line 282
```python
            "selected_feature_names": selected_names,
```
**Plain English:** Run this instruction: `"selected_feature_names": selected_names,`.

### Line 283
```python
            "n_selected_features": int(len(top_idx)),
```
**Plain English:** Run this instruction: `"n_selected_features": int(len(top_idx)),`.

### Line 284
```python
            "imputer_medians": medians.tolist(),
```
**Plain English:** Run this instruction: `"imputer_medians": medians.tolist(),`.

### Line 285
```python
            "n_train": int(len(train_idx)),
```
**Plain English:** Run this instruction: `"n_train": int(len(train_idx)),`.

### Line 286
```python
            "n_val": int(len(val_idx)),
```
**Plain English:** Run this instruction: `"n_val": int(len(val_idx)),`.

### Line 287
```python
            "feature_order_hash": feature_hash,
```
**Plain English:** Run this instruction: `"feature_order_hash": feature_hash,`.

### Line 288
```python
            "target_column": TARGET_COLUMN,
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 289
```python
        }
```
**Plain English:** Run this instruction: `}`.

### Line 290
```python
        with open(fold_path, "w", encoding="utf-8") as handle:
```
**Plain English:** Open a resource safely (file, etc.): `open(fold_path, "w", encoding="utf-8") as handle`. When the indented block ends, Python closes it automatically.

### Line 291
```python
            json.dump(fold_metadata, handle, indent=2, allow_nan=False)
```
**Plain English:** Run this instruction: `json.dump(fold_metadata, handle, indent=2, allow_nan=False)`.

### Line 292
```python
        cv_manifest_entries[(int(seed), int(fold))] = {
```
**Plain English:** Run this instruction: `cv_manifest_entries[(int(seed), int(fold))] = {`.

### Line 293
```python
            "seed": int(seed), "fold": int(fold),
```
**Plain English:** Run this instruction: `"seed": int(seed), "fold": int(fold),`.

### Line 294
```python
            "model_path": "cv_models/" + artifact_name,
```
**Plain English:** Run this instruction: `"model_path": "cv_models/" + artifact_name,`.

### Line 295
```python
            "metadata_path": "cv_folds/" + artifact_name,
```
**Plain English:** Run this instruction: `"metadata_path": "cv_folds/" + artifact_name,`.

### Line 296
```python
            "n_selected_features": int(len(top_idx)),
```
**Plain English:** Run this instruction: `"n_selected_features": int(len(top_idx)),`.

### Line 297
```python
            "selected_feature_names": selected_names,
```
**Plain English:** Run this instruction: `"selected_feature_names": selected_names,`.

### Line 298
```python
            "selected_feature_indices": top_idx.tolist(),
```
**Plain English:** Run this instruction: `"selected_feature_indices": top_idx.tolist(),`.

### Line 299
```python
        }
```
**Plain English:** Run this instruction: `}`.

### Line 300
```python
        preds = model.predict(X_val[:, top_idx])
```
**Plain English:** Ask the champion for predictions on the **validation** rows (exam set), using the same 300 columns.

### Line 302
```python
        row = {
```
**Plain English:** Store a value: the name `row` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 303
```python
            "seed": seed,
```
**Plain English:** Run this instruction: `"seed": seed,`.

### Line 304
```python
            "fold": fold,
```
**Plain English:** Run this instruction: `"fold": fold,`.

### Line 305
```python
            "n_train": int(len(train_idx)),
```
**Plain English:** Run this instruction: `"n_train": int(len(train_idx)),`.

### Line 306
```python
            "n_val": int(len(val_idx)),
```
**Plain English:** Run this instruction: `"n_val": int(len(val_idx)),`.

### Line 307
```python
            "r2": float(r2_score(y_val, preds)),
```
**Plain English:** Compute R² on the exam: 1 = perfect numeric fit, 0 = no better than predicting the mean.

### Line 308
```python
            "spearman": stable_spearman(y_val, preds),
```
**Plain English:** Compute Spearman correlation (ranking agreement) between true and predicted exam scores.

### Line 309
```python
            "pearson": stable_pearson(y_val, preds),
```
**Plain English:** Run this instruction: `"pearson": stable_pearson(y_val, preds),`.

### Line 310
```python
            "mse": float(mean_squared_error(y_val, preds)),
```
**Plain English:** Run this instruction: `"mse": float(mean_squared_error(y_val, preds)),`.

### Line 311
```python
            "eng_selected": n_eng,
```
**Plain English:** Run this instruction: `"eng_selected": n_eng,`.

### Line 312
```python
            "regional_qct_selected": n_regional,
```
**Plain English:** Run this instruction: `"regional_qct_selected": n_regional,`.

### Line 313
```python
            "eng_extra_selected": n_eng_extra,
```
**Plain English:** Run this instruction: `"eng_extra_selected": n_eng_extra,`.

### Line 314
```python
            "selected_feature_names": " | ".join(selected_names),
```
**Plain English:** Run this instruction: `"selected_feature_names": " | ".join(selected_names),`.

### Line 315
```python
        }
```
**Plain English:** Run this instruction: `}`.

### Line 316
```python
        fold_records.append(row)
```
**Plain English:** Run this instruction: `fold_records.append(row)`.

### Line 317
```python
        print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 318
```python
            f"Seed {seed}, fold {fold}: "
```
**Plain English:** Run this instruction: `f"Seed {seed}, fold {fold}: "`.

### Line 319
```python
            f"R^2={row['r2']:.4f} | Spearman={row['spearman']:.4f} | "
```
**Plain English:** Run this instruction: `f"R^2={row['r2']:.4f} | Spearman={row['spearman']:.4f} | "`.

### Line 320
```python
            f"Pearson={row['pearson']:.4f} | MSE={row['mse']:.4f} | "
```
**Plain English:** Store a value: the name `f"Pearson` now holds the result of `{row['pearson']:.4f} | MSE={row['mse']:.4f} | "`. Whenever you later write that name, you mean this value.

### Line 321
```python
            f"eng={n_eng} (regional_qct={n_regional}, eng.*={n_eng_extra})"
```
**Plain English:** Store a value: the name `f"eng` now holds the result of `{n_eng} (regional_qct={n_regional}, eng.*={n_eng_extra})"`. Whenever you later write that name, you mean this value.

### Line 322
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 324
```python
    return fold_records, selected_counter
```
**Plain English:** Finish this function and send back: `fold_records, selected_counter`.

### Line 327
```python
# %% CELL 6 — Run all five seeds
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 6 — Run all five seeds**.

### Line 328
```python
all_fold_records = []
```
**Plain English:** Store a value: the name `all_fold_records` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 329
```python
overall_selected_counter = Counter()
```
**Plain English:** Store a value: the name `overall_selected_counter` now holds the result of `Counter()`. Whenever you later write that name, you mean this value.

### Line 331
```python
for seed in SEEDS:
```
**Plain English:** Loop: repeat the indented block once for each item → `seed in SEEDS`.

### Line 332
```python
    fold_records, selected_counter = run_cv_for_seed(seed)
```
**Plain English:** Run this instruction: `fold_records, selected_counter = run_cv_for_seed(seed)`.

### Line 333
```python
    all_fold_records.extend(fold_records)
```
**Plain English:** Run this instruction: `all_fold_records.extend(fold_records)`.

### Line 334
```python
    overall_selected_counter.update(selected_counter)
```
**Plain English:** Run this instruction: `overall_selected_counter.update(selected_counter)`.

### Line 336
```python
fold_df = pd.DataFrame(all_fold_records)
```
**Plain English:** Store a value: the name `fold_df` now holds the result of `pd.DataFrame(all_fold_records)`. Whenever you later write that name, you mean this value.

### Line 337
```python
fold_df.to_csv(os.path.join(OUTPUT_DIR, "all_seed_fold_results.csv"), index=False)
```
**Plain English:** Run this instruction: `fold_df.to_csv(os.path.join(OUTPUT_DIR, "all_seed_fold_results.csv"), index=False)`.

### Line 339
```python
summary_rows = []
```
**Plain English:** Store a value: the name `summary_rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 340
```python
for seed, g in fold_df.groupby("seed", sort=True):
```
**Plain English:** Loop: repeat the indented block once for each item → `seed, g in fold_df.groupby("seed", sort=True)`.

### Line 341
```python
    summary_rows.append({
```
**Plain English:** Run this instruction: `summary_rows.append({`.

### Line 342
```python
        "seed": int(seed),
```
**Plain English:** Run this instruction: `"seed": int(seed),`.

### Line 343
```python
        "mean_r2": float(g["r2"].mean()),
```
**Plain English:** Run this instruction: `"mean_r2": float(g["r2"].mean()),`.

### Line 344
```python
        "std_r2": float(g["r2"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"std_r2": float(g["r2"].std(ddof=0)),`.

### Line 345
```python
        "mean_spearman": float(g["spearman"].mean()),
```
**Plain English:** Run this instruction: `"mean_spearman": float(g["spearman"].mean()),`.

### Line 346
```python
        "std_spearman": float(g["spearman"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"std_spearman": float(g["spearman"].std(ddof=0)),`.

### Line 347
```python
        "mean_pearson": float(g["pearson"].mean()),
```
**Plain English:** Run this instruction: `"mean_pearson": float(g["pearson"].mean()),`.

### Line 348
```python
        "std_pearson": float(g["pearson"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"std_pearson": float(g["pearson"].std(ddof=0)),`.

### Line 349
```python
        "mean_mse": float(g["mse"].mean()),
```
**Plain English:** Run this instruction: `"mean_mse": float(g["mse"].mean()),`.

### Line 350
```python
        "std_mse": float(g["mse"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"std_mse": float(g["mse"].std(ddof=0)),`.

### Line 351
```python
        "mean_eng_selected": float(g["eng_selected"].mean()),
```
**Plain English:** Run this instruction: `"mean_eng_selected": float(g["eng_selected"].mean()),`.

### Line 352
```python
        "mean_regional_qct_selected": float(g["regional_qct_selected"].mean()),
```
**Plain English:** Run this instruction: `"mean_regional_qct_selected": float(g["regional_qct_selected"].mean()),`.

### Line 353
```python
        "mean_eng_extra_selected": float(g["eng_extra_selected"].mean()),
```
**Plain English:** Run this instruction: `"mean_eng_extra_selected": float(g["eng_extra_selected"].mean()),`.

### Line 354
```python
    })
```
**Plain English:** Run this instruction: `})`.

### Line 355
```python
summary_df = pd.DataFrame(summary_rows)
```
**Plain English:** Store a value: the name `summary_df` now holds the result of `pd.DataFrame(summary_rows)`. Whenever you later write that name, you mean this value.

### Line 356
```python
summary_df.to_csv(os.path.join(OUTPUT_DIR, "per_seed_summary.csv"), index=False)
```
**Plain English:** Run this instruction: `summary_df.to_csv(os.path.join(OUTPUT_DIR, "per_seed_summary.csv"), index=False)`.

### Line 358
```python
selected_counts_df = pd.DataFrame([
```
**Plain English:** Store a value: the name `selected_counts_df` now holds the result of `pd.DataFrame([`. Whenever you later write that name, you mean this value.

### Line 359
```python
    {
```
**Plain English:** Run this instruction: `{`.

### Line 360
```python
        "feature_name": name,
```
**Plain English:** Run this instruction: `"feature_name": name,`.

### Line 361
```python
        "number_of_seed_folds_selected": count,
```
**Plain English:** Run this instruction: `"number_of_seed_folds_selected": count,`.

### Line 362
```python
        "out_of_total_seed_folds": len(SEEDS) * N_SPLITS,
```
**Plain English:** Run this instruction: `"out_of_total_seed_folds": len(SEEDS) * N_SPLITS,`.

### Line 363
```python
    }
```
**Plain English:** Run this instruction: `}`.

### Line 364
```python
    for name, count in overall_selected_counter.most_common()
```
**Plain English:** Loop: repeat the indented block once for each item → `name, count in overall_selected_counter.most_common()`.

### Line 365
```python
])
```
**Plain English:** Run this instruction: `])`.

### Line 366
```python
selected_counts_df.to_csv(os.path.join(OUTPUT_DIR, "selected_feature_counts.csv"), index=False)
```
**Plain English:** Run this instruction: `selected_counts_df.to_csv(os.path.join(OUTPUT_DIR, "selected_feature_counts.csv"), index=False)`.

### Line 368
```python
# %% CELL 7 — Print five-seed CV report
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 7 — Print five-seed CV report**.

### Line 369
```python
print("\n" + "=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n" + "=" * 70)`.

### Line 370
```python
print("PER-SEED SUMMARY")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("PER-SEED SUMMARY")`.

### Line 371
```python
print("=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=" * 70)`.

### Line 372
```python
print(summary_df.to_string(index=False))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(summary_df.to_string(index=False))`.

### Line 374
```python
print("\n" + "=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n" + "=" * 70)`.

### Line 375
```python
print("OVERALL BASELINE SUMMARY ACROSS 5 SEEDS")
```
**Plain English:** This printed block is the **official number you report** — average performance across seeds.

### Line 376
```python
print("=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=" * 70)`.

### Line 377
```python
print(f"Mean R^2:       {summary_df['mean_r2'].mean():.6f} ± {summary_df['mean_r2'].std(ddof=0):.6f}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Mean R^2:       {summary_df['mean_r2'].mean():.6f} ± {summary_df['mean_r2'].std(ddof=0):.6f}")`.

### Line 378
```python
print(f"Mean Spearman:  {summary_df['mean_spearman'].mean():.6f} ± {summary_df['mean_spearman'].std(ddof=0):.6f}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Mean Spearman:  {summary_df['mean_spearman'].mean():.6f} ± {summary_df['mean_spearman'].std(ddof=0):.6f}")`.

### Line 379
```python
print(f"Mean Pearson:   {summary_df['mean_pearson'].mean():.6f} ± {summary_df['mean_pearson'].std(ddof=0):.6f}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Mean Pearson:   {summary_df['mean_pearson'].mean():.6f} ± {summary_df['mean_pearson'].std(ddof=0):.6f}")`.

### Line 380
```python
print(f"Mean MSE:       {summary_df['mean_mse'].mean():.6f} ± {summary_df['mean_mse'].std(ddof=0):.6f}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Mean MSE:       {summary_df['mean_mse'].mean():.6f} ± {summary_df['mean_mse'].std(ddof=0):.6f}")`.

### Line 381
```python
print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 382
```python
    f"Mean eng. selected per fold (avg over seeds): "
```
**Plain English:** Run this instruction: `f"Mean eng. selected per fold (avg over seeds): "`.

### Line 383
```python
    f"{summary_df['mean_eng_selected'].mean():.2f} "
```
**Plain English:** Run this instruction: `f"{summary_df['mean_eng_selected'].mean():.2f} "`.

### Line 384
```python
    f"(regional_qct={summary_df['mean_regional_qct_selected'].mean():.2f}, "
```
**Plain English:** Run this instruction: `f"(regional_qct={summary_df['mean_regional_qct_selected'].mean():.2f}, "`.

### Line 385
```python
    f"eng.*={summary_df['mean_eng_extra_selected'].mean():.2f})"
```
**Plain English:** Run this instruction: `f"eng.*={summary_df['mean_eng_extra_selected'].mean():.2f})"`.

### Line 386
```python
)
```
**Plain English:** Run this instruction: `)`.

### Line 388
```python
print("\n" + "=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n" + "=" * 70)`.

### Line 389
```python
print("TOP SELECTED BASELINE FEATURES ACROSS ALL SEEDS")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("TOP SELECTED BASELINE FEATURES ACROSS ALL SEEDS")`.

### Line 390
```python
print("=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=" * 70)`.

### Line 391
```python
print(selected_counts_df.head(30).to_string(index=False))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(selected_counts_df.head(30).to_string(index=False))`.

### Line 393
```python
# %% CELL 8 — Train final production model on all data using seed 42
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 8 — Train final production model on all data using seed 42**.

### Line 394
```python
# This is for deployment only. Do not report its in-sample fit as validation performance.
```
**Plain English:** Human-only note (Python ignores it): This is for deployment only. Do not report its in-sample fit as validation performance.

### Line 395
```python
print("\nTraining final production selector/model on all data using seed 42...")
```
**Plain English:** Production fit on *all* rows. Useful for deploying predictions later. **Do not quote its training fit as validation.**

### Line 396
```python
X_full, imputer_medians = median_impute_full(X_raw)
```
**Plain English:** Run this instruction: `X_full, imputer_medians = median_impute_full(X_raw)`.

### Line 398
```python
final_selector = xgb.XGBRegressor(**selector_params(FINAL_PRODUCTION_SEED))
```
**Plain English:** Store a value: the name `final_selector` now holds the result of `xgb.XGBRegressor(**selector_params(FINAL_PRODUCTION_SEED))`. Whenever you later write that name, you mean this value.

### Line 399
```python
final_selector.fit(X_full, y)
```
**Plain English:** Train the throwaway **selector** model on training features/labels only. Its predictions are ignored; we only want `feature_importances_` (which columns mattered).

### Line 401
```python
importance_df = pd.DataFrame({
```
**Plain English:** Store a value: the name `importance_df` now holds the result of `pd.DataFrame({`. Whenever you later write that name, you mean this value.

### Line 402
```python
    "feature_index": np.arange(len(feature_names)),
```
**Plain English:** Run this instruction: `"feature_index": np.arange(len(feature_names)),`.

### Line 403
```python
    "feature_name": feature_names,
```
**Plain English:** Run this instruction: `"feature_name": feature_names,`.

### Line 404
```python
    "importance_gain": final_selector.feature_importances_,
```
**Plain English:** Run this instruction: `"importance_gain": final_selector.feature_importances_,`.

### Line 405
```python
}).sort_values("importance_gain", ascending=False)
```
**Plain English:** Run this instruction: `}).sort_values("importance_gain", ascending=False)`.

### Line 407
```python
selected_feature_indices = importance_df.head(N_FEATURES)["feature_index"].to_numpy()
```
**Plain English:** Store a value: the name `selected_feature_indices` now holds the result of `importance_df.head(N_FEATURES)["feature_index"].to_numpy()`. Whenever you later write that name, you mean this value.

### Line 408
```python
selected_feature_names = [feature_names[i] for i in selected_feature_indices]
```
**Plain English:** Store a value: the name `selected_feature_names` now holds the result of `[feature_names[i] for i in selected_feature_indices]`. Whenever you later write that name, you mean this value.

### Line 409
```python
X_selected = X_full[:, selected_feature_indices]
```
**Plain English:** Store a value: the name `X_selected` now holds the result of `X_full[:, selected_feature_indices]`. Whenever you later write that name, you mean this value.

### Line 411
```python
champion_model = xgb.XGBRegressor(**champion_params(FINAL_PRODUCTION_SEED))
```
**Plain English:** Store a value: the name `champion_model` now holds the result of `xgb.XGBRegressor(**champion_params(FINAL_PRODUCTION_SEED))`. Whenever you later write that name, you mean this value.

### Line 412
```python
champion_model.fit(X_selected, y)
```
**Plain English:** Train the real **champion** model, but only on the selected 300 columns of the training fold.

### Line 413
```python
print("Final production model trained.")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("Final production model trained.")`.

### Line 415
```python
# %% CELL 9 — Save artifacts and metadata
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 9 — Save artifacts and metadata**.

### Line 416
```python
joblib.dump(champion_model, os.path.join(OUTPUT_DIR, "champion_xgboost_model.pkl"))
```
**Plain English:** Run this instruction: `joblib.dump(champion_model, os.path.join(OUTPUT_DIR, "champion_xgboost_model.pkl"))`.

### Line 417
```python
joblib.dump(final_selector, os.path.join(OUTPUT_DIR, "feature_selector_model.pkl"))
```
**Plain English:** Run this instruction: `joblib.dump(final_selector, os.path.join(OUTPUT_DIR, "feature_selector_model.pkl"))`.

### Line 418
```python
joblib.dump(selected_feature_indices, os.path.join(OUTPUT_DIR, "selected_feature_indices.pkl"))
```
**Plain English:** Run this instruction: `joblib.dump(selected_feature_indices, os.path.join(OUTPUT_DIR, "selected_feature_indices.pkl"))`.

### Line 419
```python
np.save(os.path.join(OUTPUT_DIR, "imputer_medians.npy"), imputer_medians)
```
**Plain English:** Run this instruction: `np.save(os.path.join(OUTPUT_DIR, "imputer_medians.npy"), imputer_medians)`.

### Line 421
```python
with open(os.path.join(OUTPUT_DIR, "full_feature_names_ordered.json"), "w") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "full_feature_names_ordered.json"), "w") as f`. When the indented block ends, Python closes it automatically.

### Line 422
```python
    json.dump(feature_names, f, indent=2)
```
**Plain English:** Run this instruction: `json.dump(feature_names, f, indent=2)`.

### Line 423
```python
with open(os.path.join(OUTPUT_DIR, "selected_feature_names_ordered.json"), "w") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "selected_feature_names_ordered.json"), "w") as f`. When the indented block ends, Python closes it automatically.

### Line 424
```python
    json.dump(selected_feature_names, f, indent=2)
```
**Plain English:** Run this instruction: `json.dump(selected_feature_names, f, indent=2)`.

### Line 426
```python
importance_df.to_csv(os.path.join(OUTPUT_DIR, "final_feature_importance_ranking.csv"), index=False)
```
**Plain English:** Run this instruction: `importance_df.to_csv(os.path.join(OUTPUT_DIR, "final_feature_importance_ranking.csv"), index=False)`.

### Line 428
```python
metadata = {
```
**Plain English:** Store a value: the name `metadata` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 429
```python
    "experiment": "five_seed_baseline_xgboost_top300",
```
**Plain English:** Run this instruction: `"experiment": "five_seed_baseline_xgboost_top300",`.

### Line 430
```python
    "project": "Enhancing sgRNA efficiency in CRISPR-Cas9 genome editing",
```
**Plain English:** Run this instruction: `"project": "Enhancing sgRNA efficiency in CRISPR-Cas9 genome editing",`.

### Line 431
```python
    "species": "Escherichia coli",
```
**Plain English:** Run this instruction: `"species": "Escherichia coli",`.

### Line 432
```python
    "data_path": DATA_PATH,
```
**Plain English:** Run this instruction: `"data_path": DATA_PATH,`.

### Line 433
```python
    "target_column": TARGET_COLUMN,
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 434
```python
    "dropped_columns": drop_cols,
```
**Plain English:** Run this instruction: `"dropped_columns": drop_cols,`.

### Line 435
```python
    "all_nan_columns_dropped": all_nan_cols,
```
**Plain English:** Run this instruction: `"all_nan_columns_dropped": all_nan_cols,`.

### Line 436
```python
    "x_shape_full": list(X_raw.shape),
```
**Plain English:** Run this instruction: `"x_shape_full": list(X_raw.shape),`.

### Line 437
```python
    "x_shape_selected_final_production": list(X_selected.shape),
```
**Plain English:** Run this instruction: `"x_shape_selected_final_production": list(X_selected.shape),`.

### Line 438
```python
    "seeds": SEEDS,
```
**Plain English:** Run this instruction: `"seeds": SEEDS,`.

### Line 439
```python
    "n_splits": N_SPLITS,
```
**Plain English:** Run this instruction: `"n_splits": N_SPLITS,`.

### Line 440
```python
    "n_features": N_FEATURES,
```
**Plain English:** Run this instruction: `"n_features": N_FEATURES,`.

### Line 441
```python
    "n_estimators_selector": 300,
```
**Plain English:** Run this instruction: `"n_estimators_selector": 300,`.

### Line 442
```python
    "n_estimators_final_model": N_ESTIMATORS,
```
**Plain English:** Run this instruction: `"n_estimators_final_model": N_ESTIMATORS,`.

### Line 443
```python
    "final_production_seed": FINAL_PRODUCTION_SEED,
```
**Plain English:** Run this instruction: `"final_production_seed": FINAL_PRODUCTION_SEED,`.

### Line 444
```python
    "feature_order_hash": feature_hash,
```
**Plain English:** Run this instruction: `"feature_order_hash": feature_hash,`.

### Line 445
```python
    "selector_params_production_seed": selector_params(FINAL_PRODUCTION_SEED),
```
**Plain English:** Run this instruction: `"selector_params_production_seed": selector_params(FINAL_PRODUCTION_SEED),`.

### Line 446
```python
    "champion_params_production_seed": champion_params(FINAL_PRODUCTION_SEED),
```
**Plain English:** Run this instruction: `"champion_params_production_seed": champion_params(FINAL_PRODUCTION_SEED),`.

### Line 447
```python
    "overall_mean_r2_across_seed_means": float(summary_df["mean_r2"].mean()),
```
**Plain English:** Run this instruction: `"overall_mean_r2_across_seed_means": float(summary_df["mean_r2"].mean()),`.

### Line 448
```python
    "overall_std_r2_across_seed_means": float(summary_df["mean_r2"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"overall_std_r2_across_seed_means": float(summary_df["mean_r2"].std(ddof=0)),`.

### Line 449
```python
    "overall_mean_spearman_across_seed_means": float(summary_df["mean_spearman"].mean()),
```
**Plain English:** Run this instruction: `"overall_mean_spearman_across_seed_means": float(summary_df["mean_spearman"].mean()),`.

### Line 450
```python
    "overall_std_spearman_across_seed_means": float(summary_df["mean_spearman"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"overall_std_spearman_across_seed_means": float(summary_df["mean_spearman"].std(ddof=0)),`.

### Line 451
```python
    "overall_mean_pearson_across_seed_means": float(summary_df["mean_pearson"].mean()),
```
**Plain English:** Run this instruction: `"overall_mean_pearson_across_seed_means": float(summary_df["mean_pearson"].mean()),`.

### Line 452
```python
    "overall_std_pearson_across_seed_means": float(summary_df["mean_pearson"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"overall_std_pearson_across_seed_means": float(summary_df["mean_pearson"].std(ddof=0)),`.

### Line 453
```python
    "overall_mean_mse_across_seed_means": float(summary_df["mean_mse"].mean()),
```
**Plain English:** Run this instruction: `"overall_mean_mse_across_seed_means": float(summary_df["mean_mse"].mean()),`.

### Line 454
```python
    "overall_std_mse_across_seed_means": float(summary_df["mean_mse"].std(ddof=0)),
```
**Plain English:** Run this instruction: `"overall_std_mse_across_seed_means": float(summary_df["mean_mse"].std(ddof=0)),`.

### Line 455
```python
    "engineered_features_loaded": n_eng_loaded,
```
**Plain English:** Run this instruction: `"engineered_features_loaded": n_eng_loaded,`.

### Line 456
```python
    "regional_qct_loaded": n_regional_loaded,
```
**Plain English:** Run this instruction: `"regional_qct_loaded": n_regional_loaded,`.

### Line 457
```python
    "eng_extra_loaded": n_eng_extra_loaded,
```
**Plain English:** Run this instruction: `"eng_extra_loaded": n_eng_extra_loaded,`.

### Line 458
```python
    "overall_mean_eng_selected_across_seed_means": float(
```
**Plain English:** Run this instruction: `"overall_mean_eng_selected_across_seed_means": float(`.

### Line 459
```python
        summary_df["mean_eng_selected"].mean()
```
**Plain English:** Run this instruction: `summary_df["mean_eng_selected"].mean()`.

### Line 460
```python
    ),
```
**Plain English:** Run this instruction: `),`.

### Line 461
```python
    "overall_mean_regional_qct_selected_across_seed_means": float(
```
**Plain English:** Run this instruction: `"overall_mean_regional_qct_selected_across_seed_means": float(`.

### Line 462
```python
        summary_df["mean_regional_qct_selected"].mean()
```
**Plain English:** Run this instruction: `summary_df["mean_regional_qct_selected"].mean()`.

### Line 463
```python
    ),
```
**Plain English:** Run this instruction: `),`.

### Line 464
```python
    "overall_mean_eng_extra_selected_across_seed_means": float(
```
**Plain English:** Run this instruction: `"overall_mean_eng_extra_selected_across_seed_means": float(`.

### Line 465
```python
        summary_df["mean_eng_extra_selected"].mean()
```
**Plain English:** Run this instruction: `summary_df["mean_eng_extra_selected"].mean()`.

### Line 466
```python
    ),
```
**Plain English:** Run this instruction: `),`.

### Line 467
```python
    "note": (
```
**Plain English:** Run this instruction: `"note": (`.

### Line 468
```python
        "Leakage-safe five-seed XGBoost evaluation. "
```
**Plain English:** Run this instruction: `"Leakage-safe five-seed XGBoost evaluation. "`.

### Line 469
```python
        "If DATA_PATH is the plain matrix, eng counts are 0; if it is an engineered "
```
**Plain English:** Run this instruction: `"If DATA_PATH is the plain matrix, eng counts are 0; if it is an engineered "`.

### Line 470
```python
        "CSV (eng.*/regional_qct*), those columns are included as features. "
```
**Plain English:** Run this instruction: `"CSV (eng.*/regional_qct*), those columns are included as features. "`.

### Line 471
```python
        "Feature selection and imputation are fit inside each CV training fold only. "
```
**Plain English:** Run this instruction: `"Feature selection and imputation are fit inside each CV training fold only. "`.

### Line 472
```python
        "The final production model is trained on all data and is not a validation score."
```
**Plain English:** Production fit on *all* rows. Useful for deploying predictions later. **Do not quote its training fit as validation.**

### Line 473
```python
    ),
```
**Plain English:** Run this instruction: `),`.

### Line 474
```python
}
```
**Plain English:** Run this instruction: `}`.

### Line 475
```python
with open(os.path.join(OUTPUT_DIR, "model_metadata.json"), "w") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "model_metadata.json"), "w") as f`. When the indented block ends, Python closes it automatically.

### Line 476
```python
    json.dump(metadata, f, indent=2)
```
**Plain English:** Run this instruction: `json.dump(metadata, f, indent=2)`.

### Line 478
```python
# %% CELL 10 — Save inference contract test
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 10 — Save inference contract test**.

### Line 479
```python
inference_test_code = f'''
```
**Plain English:** Store a value: the name `inference_test_code` now holds the result of `f'''`. Whenever you later write that name, you mean this value.

### Line 480
```python
import json
```
**Plain English:** Load toolbox code: `import json` — used here for **read/write JSON text files**.

### Line 481
```python
import joblib
```
**Plain English:** Load toolbox code: `import joblib` — used here for **save/load Python objects to disk**.

### Line 482
```python
import hashlib
```
**Plain English:** Load toolbox code: `import hashlib` — used here for **fingerprints (hashes) of text**.

### Line 483
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 485
```python
MODEL_DIR = "{OUTPUT_DIR}"
```
**Plain English:** Store a value: the name `MODEL_DIR` now holds the result of `"{OUTPUT_DIR}"`. Whenever you later write that name, you mean this value.

### Line 488
```python
def feature_name_hash(feature_names):
```
**Plain English:** Defines a reusable recipe named `feature_name_hash`. Inputs in parentheses: `feature_names`. Nothing runs yet until something *calls* `feature_name_hash(...)`.

### Line 489
```python
    payload = json.dumps(list(feature_names), separators=(",", ":"), ensure_ascii=False)
```
**Plain English:** Store a value: the name `payload` now holds the result of `json.dumps(list(feature_names), separators=(",", ":"), ensure_ascii=False)`. Whenever you later write that name, you mean this value.

### Line 490
```python
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
```
**Plain English:** Finish this function and send back: `hashlib.sha256(payload.encode("utf-8")).hexdigest()`.

### Line 493
```python
model = joblib.load(MODEL_DIR + "/champion_xgboost_model.pkl")
```
**Plain English:** Store a value: the name `model` now holds the result of `joblib.load(MODEL_DIR + "/champion_xgboost_model.pkl")`. Whenever you later write that name, you mean this value.

### Line 494
```python
selected_feature_indices = joblib.load(MODEL_DIR + "/selected_feature_indices.pkl")
```
**Plain English:** Store a value: the name `selected_feature_indices` now holds the result of `joblib.load(MODEL_DIR + "/selected_feature_indices.pkl")`. Whenever you later write that name, you mean this value.

### Line 495
```python
imputer_medians = np.load(MODEL_DIR + "/imputer_medians.npy")
```
**Plain English:** Store a value: the name `imputer_medians` now holds the result of `np.load(MODEL_DIR + "/imputer_medians.npy")`. Whenever you later write that name, you mean this value.

### Line 496
```python
with open(MODEL_DIR + "/full_feature_names_ordered.json") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(MODEL_DIR + "/full_feature_names_ordered.json") as f`. When the indented block ends, Python closes it automatically.

### Line 497
```python
    full_feature_names = json.load(f)
```
**Plain English:** Store a value: the name `full_feature_names` now holds the result of `json.load(f)`. Whenever you later write that name, you mean this value.

### Line 498
```python
with open(MODEL_DIR + "/model_metadata.json") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(MODEL_DIR + "/model_metadata.json") as f`. When the indented block ends, Python closes it automatically.

### Line 499
```python
    metadata = json.load(f)
```
**Plain English:** Store a value: the name `metadata` now holds the result of `json.load(f)`. Whenever you later write that name, you mean this value.

### Line 501
```python
assert feature_name_hash(full_feature_names) == metadata["feature_order_hash"], "Feature-name hash mismatch."
```
**Plain English:** Run this instruction: `assert feature_name_hash(full_feature_names) == metadata["feature_order_hash"], "Feature-name hash mismatch."`.

### Line 502
```python
assert len(selected_feature_indices) == metadata["n_features"], "Selected feature count mismatch."
```
**Plain English:** Run this instruction: `assert len(selected_feature_indices) == metadata["n_features"], "Selected feature count mismatch."`.

### Line 503
```python
assert len(imputer_medians) == len(full_feature_names), "Imputer median length mismatch."
```
**Plain English:** Run this instruction: `assert len(imputer_medians) == len(full_feature_names), "Imputer median length mismatch."`.

### Line 505
```python
dummy_X = np.zeros((1, len(full_feature_names)), dtype=np.float32)
```
**Plain English:** Store a value: the name `dummy_X` now holds the result of `np.zeros((1, len(full_feature_names)), dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 506
```python
pred = model.predict(dummy_X[:, selected_feature_indices])
```
**Plain English:** Ask the champion for predictions on the **validation** rows (exam set), using the same 300 columns.

### Line 507
```python
assert len(pred) == 1 and np.isfinite(pred[0])
```
**Plain English:** Run this instruction: `assert len(pred) == 1 and np.isfinite(pred[0])`.

### Line 508
```python
print("Inference contract test passed. Dummy prediction:", pred[0])
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("Inference contract test passed. Dummy prediction:", pred[0])`.

### Lines 509–509
```python
'''
with open(os.path.join(OUTPUT_DIR, "test_inference_contract.py"), "w") as f:
    f.write(inference_test_code)

print(f"\nSaved five-seed baseline outputs and production artifacts to: {OUTPUT_DIR}/")
print("Key files:")
for filename in [
    "all_seed_fold_results.csv",
    "per_seed_summary.csv",
    "selected_feature_counts.csv",
    "model_metadata.json",
    "champion_xgboost_model.pkl",
    "feature_selector_model.pkl",
    "selected_feature_indices.pkl",
    "imputer_medians.npy",
    "full_feature_names_ordered.json",
    "selected_feature_names_ordered.json",
    "final_feature_importance_ranking.csv",
    "test_inference_contract.py",
]:
    print(f" - {filename}")

print("\nTop 15 final production selected features:")
for i, name in enumerate(selected_feature_names[:15], start=1):
    print(f"{i:2d}. {name}")

# %% CELL 11 — Save CV manifest and verify exact saved CV artifacts
cv_manifest = {
    "seeds": SEEDS,
    "n_splits": N_SPLITS,
    "n_features": N_FEATURES,
    "n_estimators_selector": 300,
    "n_estimators_final": N_ESTIMATORS,
    "feature_order_hash": feature_hash,
    "dataset_path": os.path.abspath(DATA_PATH),
    "target_column": TARGET_COLUMN,
    "n_samples": int(X_raw.shape[0]),
    "feature_names_path": "full_feature_names_ordered.json",
    "index_reference": "Row indices refer to X_raw after the original CELL 4 filtering.",
    "models": [cv_manifest_entries[key] for key in sorted(cv_manifest_entries)],
}
with open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), "w", encoding="utf-8") as handle:
    json.dump(cv_manifest, handle, indent=2, allow_nan=False)


def verify_cv_artifacts():
    """Reload saved CV artifacts and validate their exact feature/split contract."""
    expected_names = {
        f"seed_{seed}_fold_{fold}.json"
        for seed in SEEDS for fold in range(1, N_SPLITS + 1)
    }
    for directory in (CV_MODEL_DIR, CV_FOLD_DIR):
        actual = {name for name in os.listdir(directory) if name.endswith(".json")}
        if actual != expected_names:
            raise ValueError(
                f"CV artifact files differ in {directory}: "
                f"missing={sorted(expected_names - actual)}, unexpected={sorted(actual - expected_names)}"
            )
    with open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    entries = manifest["models"]
    if len(entries) != len(expected_names):
        raise ValueError("Manifest must contain exactly 25 seed-fold entries.")
    if {(entry["seed"], entry["fold"]) for entry in entries} != set(cv_manifest_entries):
        raise ValueError("Manifest seed-fold entries are duplicated or missing.")
    with open(os.path.join(OUTPUT_DIR, "full_feature_names_ordered.json"), encoding="utf-8") as handle:
        saved_names = json.load(handle)
    if saved_names != feature_names or feature_name_hash(saved_names) != feature_hash:
        raise ValueError("Saved original feature ordering/hash differs from baseline.")
    if manifest["feature_order_hash"] != feature_hash:
        raise ValueError("Manifest feature-order hash differs from baseline.")
    reloadable = 0
    for entry in entries:
        label = f"seed {entry['seed']}, fold {entry['fold']}"
        with open(os.path.join(OUTPUT_DIR, entry["metadata_path"]), encoding="utf-8") as handle:
            info = json.load(handle)
        required = {"seed", "fold", "train_indices", "validation_indices",
                    "selected_feature_indices", "selected_feature_names",
                    "n_selected_features", "imputer_medians", "n_train", "n_val",
                    "feature_order_hash", "target_column"}
        if required - info.keys():
            raise ValueError(f"{label}: missing metadata fields {sorted(required - info.keys())}.")
        if (info["seed"], info["fold"]) != (entry["seed"], entry["fold"]):
            raise ValueError(f"{label}: metadata seed/fold mismatch.")
        selected = info["selected_feature_indices"]
        if len(selected) != N_FEATURES or len(set(selected)) != N_FEATURES:
            raise ValueError(f"{label}: expected 300 unique selected indices.")
        if any(type(i) is not int or i < 0 or i >= len(saved_names) for i in selected):
            raise ValueError(f"{label}: invalid selected feature index.")
        if info["selected_feature_names"] != [saved_names[i] for i in selected]:
            raise ValueError(f"{label}: selected feature names and indices disagree.")
        for field in ("n_selected_features", "selected_feature_names", "selected_feature_indices"):
            if entry[field] != info[field]:
                raise ValueError(f"{label}: manifest and fold metadata disagree on {field}.")
        if info["n_selected_features"] != N_FEATURES:
            raise ValueError(f"{label}: selected feature count is not 300.")
        if info["feature_order_hash"] != feature_hash or info["target_column"] != TARGET_COLUMN:
            raise ValueError(f"{label}: feature hash or target column mismatch.")
        medians_saved = np.asarray(info["imputer_medians"], dtype=np.float32)
        if medians_saved.shape != (len(saved_names),) or not np.isfinite(medians_saved).all():
            raise ValueError(f"{label}: missing, malformed or nonfinite imputation medians.")
        train, val = info["train_indices"], info["validation_indices"]
        if any(type(i) is not int or i < 0 or i >= len(X_raw) for i in train + val):
            raise ValueError(f"{label}: invalid observation indices.")
        if len(train) != info["n_train"] or len(val) != info["n_val"] or not train or not val:
            raise ValueError(f"{label}: split sizes disagree or are empty.")
        if len(set(train)) != len(train) or len(set(val)) != len(val) or set(train) & set(val):
            raise ValueError(f"{label}: duplicate or overlapping train/validation indices.")
        if set(train) | set(val) != set(range(len(X_raw))):
            raise ValueError(f"{label}: train/validation indices do not cover the full dataset.")
        restored = xgb.XGBRegressor()
        try:
            restored.load_model(os.path.join(OUTPUT_DIR, entry["model_path"]))
        except Exception as error:
            raise ValueError(f"{label}: saved model could not be loaded: {error}") from error
        if restored.get_booster().num_features() != N_FEATURES:
            raise ValueError(f"{label}: saved model does not have 300 input features.")
        if restored.get_booster().num_boosted_rounds() != N_ESTIMATORS:
            raise ValueError(f"{label}: saved model does not have 400 boosting rounds.")
        reloadable += 1
    print("\\n" + "=" * 60)
    print("CV MODEL ARTIFACT VERIFICATION")
    print("=" * 60)
    print(f"{len(expected_names)}/25 CV models saved")
    print(f"{len(expected_names)}/25 fold metadata files saved")
    print(f"{reloadable}/25 models successfully reloadable")
    print("All folds contain 300 selected features")
    print("All folds contain imputation medians")
    print("All train/validation splits verified")
    print("Feature-order hashes verified")


verify_cv_artifacts()

```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 510
```python
with open(os.path.join(OUTPUT_DIR, "test_inference_contract.py"), "w") as f:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "test_inference_contract.py"), "w") as f`. When the indented block ends, Python closes it automatically.

### Line 511
```python
    f.write(inference_test_code)
```
**Plain English:** Run this instruction: `f.write(inference_test_code)`.

### Line 513
```python
print(f"\nSaved five-seed baseline outputs and production artifacts to: {OUTPUT_DIR}/")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\nSaved five-seed baseline outputs and production artifacts to: {OUTPUT_DIR}/")`.

### Line 514
```python
print("Key files:")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("Key files:")`.

### Line 515
```python
for filename in [
```
**Plain English:** Loop: repeat the indented block once for each item → `filename in [`.

### Line 516
```python
    "all_seed_fold_results.csv",
```
**Plain English:** Run this instruction: `"all_seed_fold_results.csv",`.

### Line 517
```python
    "per_seed_summary.csv",
```
**Plain English:** Run this instruction: `"per_seed_summary.csv",`.

### Line 518
```python
    "selected_feature_counts.csv",
```
**Plain English:** Run this instruction: `"selected_feature_counts.csv",`.

### Line 519
```python
    "model_metadata.json",
```
**Plain English:** Run this instruction: `"model_metadata.json",`.

### Line 520
```python
    "champion_xgboost_model.pkl",
```
**Plain English:** Run this instruction: `"champion_xgboost_model.pkl",`.

### Line 521
```python
    "feature_selector_model.pkl",
```
**Plain English:** Run this instruction: `"feature_selector_model.pkl",`.

### Line 522
```python
    "selected_feature_indices.pkl",
```
**Plain English:** Run this instruction: `"selected_feature_indices.pkl",`.

### Line 523
```python
    "imputer_medians.npy",
```
**Plain English:** Run this instruction: `"imputer_medians.npy",`.

### Line 524
```python
    "full_feature_names_ordered.json",
```
**Plain English:** Run this instruction: `"full_feature_names_ordered.json",`.

### Line 525
```python
    "selected_feature_names_ordered.json",
```
**Plain English:** Run this instruction: `"selected_feature_names_ordered.json",`.

### Line 526
```python
    "final_feature_importance_ranking.csv",
```
**Plain English:** Run this instruction: `"final_feature_importance_ranking.csv",`.

### Line 527
```python
    "test_inference_contract.py",
```
**Plain English:** Run this instruction: `"test_inference_contract.py",`.

### Line 528
```python
]:
```
**Plain English:** Run this instruction: `]:`.

### Line 529
```python
    print(f" - {filename}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f" - {filename}")`.

### Line 531
```python
print("\nTop 15 final production selected features:")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\nTop 15 final production selected features:")`.

### Line 532
```python
for i, name in enumerate(selected_feature_names[:15], start=1):
```
**Plain English:** Loop: repeat the indented block once for each item → `i, name in enumerate(selected_feature_names[:15], start=1)`.

### Line 533
```python
    print(f"{i:2d}. {name}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"{i:2d}. {name}")`.

### Line 535
```python
# %% CELL 11 — Save CV manifest and verify exact saved CV artifacts
```
**Plain English:** Notebook-style section marker. Marks the start of a new logical block: **CELL 11 — Save CV manifest and verify exact saved CV artifacts**.

### Line 536
```python
cv_manifest = {
```
**Plain English:** Store a value: the name `cv_manifest` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 537
```python
    "seeds": SEEDS,
```
**Plain English:** Run this instruction: `"seeds": SEEDS,`.

### Line 538
```python
    "n_splits": N_SPLITS,
```
**Plain English:** Run this instruction: `"n_splits": N_SPLITS,`.

### Line 539
```python
    "n_features": N_FEATURES,
```
**Plain English:** Run this instruction: `"n_features": N_FEATURES,`.

### Line 540
```python
    "n_estimators_selector": 300,
```
**Plain English:** Run this instruction: `"n_estimators_selector": 300,`.

### Line 541
```python
    "n_estimators_final": N_ESTIMATORS,
```
**Plain English:** Run this instruction: `"n_estimators_final": N_ESTIMATORS,`.

### Line 542
```python
    "feature_order_hash": feature_hash,
```
**Plain English:** Run this instruction: `"feature_order_hash": feature_hash,`.

### Line 543
```python
    "dataset_path": os.path.abspath(DATA_PATH),
```
**Plain English:** Run this instruction: `"dataset_path": os.path.abspath(DATA_PATH),`.

### Line 544
```python
    "target_column": TARGET_COLUMN,
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 545
```python
    "n_samples": int(X_raw.shape[0]),
```
**Plain English:** Run this instruction: `"n_samples": int(X_raw.shape[0]),`.

### Line 546
```python
    "feature_names_path": "full_feature_names_ordered.json",
```
**Plain English:** Run this instruction: `"feature_names_path": "full_feature_names_ordered.json",`.

### Line 547
```python
    "index_reference": "Row indices refer to X_raw after the original CELL 4 filtering.",
```
**Plain English:** Run this instruction: `"index_reference": "Row indices refer to X_raw after the original CELL 4 filtering.",`.

### Line 548
```python
    "models": [cv_manifest_entries[key] for key in sorted(cv_manifest_entries)],
```
**Plain English:** Run this instruction: `"models": [cv_manifest_entries[key] for key in sorted(cv_manifest_entries)],`.

### Line 549
```python
}
```
**Plain English:** Run this instruction: `}`.

### Line 550
```python
with open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), "w", encoding="utf-8") as handle:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), "w", encoding="utf-8") as handle`. When the indented block ends, Python closes it automatically.

### Line 551
```python
    json.dump(cv_manifest, handle, indent=2, allow_nan=False)
```
**Plain English:** Run this instruction: `json.dump(cv_manifest, handle, indent=2, allow_nan=False)`.

### Line 554
```python
def verify_cv_artifacts():
```
**Plain English:** Defines a reusable recipe named `verify_cv_artifacts`. Inputs in parentheses: `(none)`. Nothing runs yet until something *calls* `verify_cv_artifacts(...)`.

### Line 555
```python
    """Reload saved CV artifacts and validate their exact feature/split contract."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Reload saved CV artifacts and validate their exact feature/split contract.

### Line 556
```python
    expected_names = {
```
**Plain English:** Store a value: the name `expected_names` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 557
```python
        f"seed_{seed}_fold_{fold}.json"
```
**Plain English:** Run this instruction: `f"seed_{seed}_fold_{fold}.json"`.

### Line 558
```python
        for seed in SEEDS for fold in range(1, N_SPLITS + 1)
```
**Plain English:** Loop: repeat the indented block once for each item → `seed in SEEDS for fold in range(1, N_SPLITS + 1)`.

### Line 559
```python
    }
```
**Plain English:** Run this instruction: `}`.

### Line 560
```python
    for directory in (CV_MODEL_DIR, CV_FOLD_DIR):
```
**Plain English:** Loop: repeat the indented block once for each item → `directory in (CV_MODEL_DIR, CV_FOLD_DIR)`.

### Line 561
```python
        actual = {name for name in os.listdir(directory) if name.endswith(".json")}
```
**Plain English:** Store a value: the name `actual` now holds the result of `{name for name in os.listdir(directory) if name.endswith(".json")}`. Whenever you later write that name, you mean this value.

### Line 562
```python
        if actual != expected_names:
```
**Plain English:** Decision: run the indented block only when this condition is true → `actual != expected_names`.

### Line 563
```python
            raise ValueError(
```
**Plain English:** Stop and report a problem on purpose → `ValueError(`.

### Line 564
```python
                f"CV artifact files differ in {directory}: "
```
**Plain English:** Run this instruction: `f"CV artifact files differ in {directory}: "`.

### Line 565
```python
                f"missing={sorted(expected_names - actual)}, unexpected={sorted(actual - expected_names)}"
```
**Plain English:** Store a value: the name `f"missing` now holds the result of `{sorted(expected_names - actual)}, unexpected={sorted(actual - expected_names)}"`. Whenever you later write that name, you mean this value.

### Line 566
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 567
```python
    with open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), encoding="utf-8") as handle:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "cv_model_manifest.json"), encoding="utf-8") as handle`. When the indented block ends, Python closes it automatically.

### Line 568
```python
        manifest = json.load(handle)
```
**Plain English:** Store a value: the name `manifest` now holds the result of `json.load(handle)`. Whenever you later write that name, you mean this value.

### Line 569
```python
    entries = manifest["models"]
```
**Plain English:** Store a value: the name `entries` now holds the result of `manifest["models"]`. Whenever you later write that name, you mean this value.

### Line 570
```python
    if len(entries) != len(expected_names):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(entries) != len(expected_names)`.

### Line 571
```python
        raise ValueError("Manifest must contain exactly 25 seed-fold entries.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError("Manifest must contain exactly 25 seed-fold entries.")`.

### Line 572
```python
    if {(entry["seed"], entry["fold"]) for entry in entries} != set(cv_manifest_entries):
```
**Plain English:** Decision: run the indented block only when this condition is true → `{(entry["seed"], entry["fold"]) for entry in entries} != set(cv_manifest_entries)`.

### Line 573
```python
        raise ValueError("Manifest seed-fold entries are duplicated or missing.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError("Manifest seed-fold entries are duplicated or missing.")`.

### Line 574
```python
    with open(os.path.join(OUTPUT_DIR, "full_feature_names_ordered.json"), encoding="utf-8") as handle:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, "full_feature_names_ordered.json"), encoding="utf-8") as handle`. When the indented block ends, Python closes it automatically.

### Line 575
```python
        saved_names = json.load(handle)
```
**Plain English:** Store a value: the name `saved_names` now holds the result of `json.load(handle)`. Whenever you later write that name, you mean this value.

### Line 576
```python
    if saved_names != feature_names or feature_name_hash(saved_names) != feature_hash:
```
**Plain English:** Decision: run the indented block only when this condition is true → `saved_names != feature_names or feature_name_hash(saved_names) != feature_hash`.

### Line 577
```python
        raise ValueError("Saved original feature ordering/hash differs from baseline.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError("Saved original feature ordering/hash differs from baseline.")`.

### Line 578
```python
    if manifest["feature_order_hash"] != feature_hash:
```
**Plain English:** Decision: run the indented block only when this condition is true → `manifest["feature_order_hash"] != feature_hash`.

### Line 579
```python
        raise ValueError("Manifest feature-order hash differs from baseline.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError("Manifest feature-order hash differs from baseline.")`.

### Line 580
```python
    reloadable = 0
```
**Plain English:** Store a value: the name `reloadable` now holds the result of `0`. Whenever you later write that name, you mean this value.

### Line 581
```python
    for entry in entries:
```
**Plain English:** Loop: repeat the indented block once for each item → `entry in entries`.

### Line 582
```python
        label = f"seed {entry['seed']}, fold {entry['fold']}"
```
**Plain English:** Store a value: the name `label` now holds the result of `f"seed {entry['seed']}, fold {entry['fold']}"`. Whenever you later write that name, you mean this value.

### Line 583
```python
        with open(os.path.join(OUTPUT_DIR, entry["metadata_path"]), encoding="utf-8") as handle:
```
**Plain English:** Open a resource safely (file, etc.): `open(os.path.join(OUTPUT_DIR, entry["metadata_path"]), encoding="utf-8") as handle`. When the indented block ends, Python closes it automatically.

### Line 584
```python
            info = json.load(handle)
```
**Plain English:** Store a value: the name `info` now holds the result of `json.load(handle)`. Whenever you later write that name, you mean this value.

### Line 585
```python
        required = {"seed", "fold", "train_indices", "validation_indices",
```
**Plain English:** Store a value: the name `required` now holds the result of `{"seed", "fold", "train_indices", "validation_indices",`. Whenever you later write that name, you mean this value.

### Line 586
```python
                    "selected_feature_indices", "selected_feature_names",
```
**Plain English:** Run this instruction: `"selected_feature_indices", "selected_feature_names",`.

### Line 587
```python
                    "n_selected_features", "imputer_medians", "n_train", "n_val",
```
**Plain English:** Run this instruction: `"n_selected_features", "imputer_medians", "n_train", "n_val",`.

### Line 588
```python
                    "feature_order_hash", "target_column"}
```
**Plain English:** Run this instruction: `"feature_order_hash", "target_column"}`.

### Line 589
```python
        if required - info.keys():
```
**Plain English:** Decision: run the indented block only when this condition is true → `required - info.keys()`.

### Line 590
```python
            raise ValueError(f"{label}: missing metadata fields {sorted(required - info.keys())}.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: missing metadata fields {sorted(required - info.keys())}.")`.

### Line 591
```python
        if (info["seed"], info["fold"]) != (entry["seed"], entry["fold"]):
```
**Plain English:** Decision: run the indented block only when this condition is true → `(info["seed"], info["fold"]) != (entry["seed"], entry["fold"])`.

### Line 592
```python
            raise ValueError(f"{label}: metadata seed/fold mismatch.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: metadata seed/fold mismatch.")`.

### Line 593
```python
        selected = info["selected_feature_indices"]
```
**Plain English:** Store a value: the name `selected` now holds the result of `info["selected_feature_indices"]`. Whenever you later write that name, you mean this value.

### Line 594
```python
        if len(selected) != N_FEATURES or len(set(selected)) != N_FEATURES:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(selected) != N_FEATURES or len(set(selected)) != N_FEATURES`.

### Line 595
```python
            raise ValueError(f"{label}: expected 300 unique selected indices.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: expected 300 unique selected indices.")`.

### Line 596
```python
        if any(type(i) is not int or i < 0 or i >= len(saved_names) for i in selected):
```
**Plain English:** Decision: run the indented block only when this condition is true → `any(type(i) is not int or i < 0 or i >= len(saved_names) for i in selected)`.

### Line 597
```python
            raise ValueError(f"{label}: invalid selected feature index.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: invalid selected feature index.")`.

### Line 598
```python
        if info["selected_feature_names"] != [saved_names[i] for i in selected]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `info["selected_feature_names"] != [saved_names[i] for i in selected]`.

### Line 599
```python
            raise ValueError(f"{label}: selected feature names and indices disagree.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: selected feature names and indices disagree.")`.

### Line 600
```python
        for field in ("n_selected_features", "selected_feature_names", "selected_feature_indices"):
```
**Plain English:** Loop: repeat the indented block once for each item → `field in ("n_selected_features", "selected_feature_names", "selected_feature_indices")`.

### Line 601
```python
            if entry[field] != info[field]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `entry[field] != info[field]`.

### Line 602
```python
                raise ValueError(f"{label}: manifest and fold metadata disagree on {field}.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: manifest and fold metadata disagree on {field}.")`.

### Line 603
```python
        if info["n_selected_features"] != N_FEATURES:
```
**Plain English:** Decision: run the indented block only when this condition is true → `info["n_selected_features"] != N_FEATURES`.

### Line 604
```python
            raise ValueError(f"{label}: selected feature count is not 300.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: selected feature count is not 300.")`.

### Line 605
```python
        if info["feature_order_hash"] != feature_hash or info["target_column"] != TARGET_COLUMN:
```
**Plain English:** Decision: run the indented block only when this condition is true → `info["feature_order_hash"] != feature_hash or info["target_column"] != TARGET_COLUMN`.

### Line 606
```python
            raise ValueError(f"{label}: feature hash or target column mismatch.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: feature hash or target column mismatch.")`.

### Line 607
```python
        medians_saved = np.asarray(info["imputer_medians"], dtype=np.float32)
```
**Plain English:** Store a value: the name `medians_saved` now holds the result of `np.asarray(info["imputer_medians"], dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 608
```python
        if medians_saved.shape != (len(saved_names),) or not np.isfinite(medians_saved).all():
```
**Plain English:** Decision: run the indented block only when this condition is true → `medians_saved.shape != (len(saved_names),) or not np.isfinite(medians_saved).all()`.

### Line 609
```python
            raise ValueError(f"{label}: missing, malformed or nonfinite imputation medians.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: missing, malformed or nonfinite imputation medians.")`.

### Line 610
```python
        train, val = info["train_indices"], info["validation_indices"]
```
**Plain English:** Run this instruction: `train, val = info["train_indices"], info["validation_indices"]`.

### Line 611
```python
        if any(type(i) is not int or i < 0 or i >= len(X_raw) for i in train + val):
```
**Plain English:** Decision: run the indented block only when this condition is true → `any(type(i) is not int or i < 0 or i >= len(X_raw) for i in train + val)`.

### Line 612
```python
            raise ValueError(f"{label}: invalid observation indices.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: invalid observation indices.")`.

### Line 613
```python
        if len(train) != info["n_train"] or len(val) != info["n_val"] or not train or not val:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(train) != info["n_train"] or len(val) != info["n_val"] or not train or not val`.

### Line 614
```python
            raise ValueError(f"{label}: split sizes disagree or are empty.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: split sizes disagree or are empty.")`.

### Line 615
```python
        if len(set(train)) != len(train) or len(set(val)) != len(val) or set(train) & set(val):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(set(train)) != len(train) or len(set(val)) != len(val) or set(train) & set(val)`.

### Line 616
```python
            raise ValueError(f"{label}: duplicate or overlapping train/validation indices.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: duplicate or overlapping train/validation indices.")`.

### Line 617
```python
        if set(train) | set(val) != set(range(len(X_raw))):
```
**Plain English:** Decision: run the indented block only when this condition is true → `set(train) | set(val) != set(range(len(X_raw)))`.

### Line 618
```python
            raise ValueError(f"{label}: train/validation indices do not cover the full dataset.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: train/validation indices do not cover the full dataset.")`.

### Line 619
```python
        restored = xgb.XGBRegressor()
```
**Plain English:** Store a value: the name `restored` now holds the result of `xgb.XGBRegressor()`. Whenever you later write that name, you mean this value.

### Line 620
```python
        try:
```
**Plain English:** Try: run the indented block, but be ready to catch errors without crashing.

### Line 621
```python
            restored.load_model(os.path.join(OUTPUT_DIR, entry["model_path"]))
```
**Plain English:** Run this instruction: `restored.load_model(os.path.join(OUTPUT_DIR, entry["model_path"]))`.

### Line 622
```python
        except Exception as error:
```
**Plain English:** If the `try` block fails with this kind of error, run this recovery block instead → `except Exception as error:`.

### Line 623
```python
            raise ValueError(f"{label}: saved model could not be loaded: {error}") from error
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: saved model could not be loaded: {error}") from error`.

### Line 624
```python
        if restored.get_booster().num_features() != N_FEATURES:
```
**Plain English:** Decision: run the indented block only when this condition is true → `restored.get_booster().num_features() != N_FEATURES`.

### Line 625
```python
            raise ValueError(f"{label}: saved model does not have 300 input features.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: saved model does not have 300 input features.")`.

### Line 626
```python
        if restored.get_booster().num_boosted_rounds() != N_ESTIMATORS:
```
**Plain English:** Decision: run the indented block only when this condition is true → `restored.get_booster().num_boosted_rounds() != N_ESTIMATORS`.

### Line 627
```python
            raise ValueError(f"{label}: saved model does not have 400 boosting rounds.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"{label}: saved model does not have 400 boosting rounds.")`.

### Line 628
```python
        reloadable += 1
```
**Plain English:** Run this instruction: `reloadable += 1`.

### Line 629
```python
    print("\\n" + "=" * 60)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\\n" + "=" * 60)`.

### Line 630
```python
    print("CV MODEL ARTIFACT VERIFICATION")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("CV MODEL ARTIFACT VERIFICATION")`.

### Line 631
```python
    print("=" * 60)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=" * 60)`.

### Line 632
```python
    print(f"{len(expected_names)}/25 CV models saved")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"{len(expected_names)}/25 CV models saved")`.

### Line 633
```python
    print(f"{len(expected_names)}/25 fold metadata files saved")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"{len(expected_names)}/25 fold metadata files saved")`.

### Line 634
```python
    print(f"{reloadable}/25 models successfully reloadable")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"{reloadable}/25 models successfully reloadable")`.

### Line 635
```python
    print("All folds contain 300 selected features")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("All folds contain 300 selected features")`.

### Line 636
```python
    print("All folds contain imputation medians")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("All folds contain imputation medians")`.

### Line 637
```python
    print("All train/validation splits verified")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("All train/validation splits verified")`.

### Line 638
```python
    print("Feature-order hashes verified")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("Feature-order hashes verified")`.

### Line 641
```python
verify_cv_artifacts()
```
**Plain English:** Run this instruction: `verify_cv_artifacts()`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives (read when a line feels opaque)

### What is “leakage-safe” in kitchen language?
You are studying for an exam. If you accidentally read the exam paper while studying, your practice score looks amazing but you’re cheating.  
**Leakage** = using validation (exam) rows when filling blanks or picking which 300 features to keep.  
This script forbids that: for every fold, medians and feature ranking come from **train only**.

### Selector vs champion
1. **Selector** (300 trees): a disposable model whose only job is to rank columns.  
2. Keep top **300** columns.  
3. **Champion** (400 trees): the real predictor, trained only on those 300.  
You never report the selector’s predictions.

### Why five seeds × five folds?
One lucky shuffle can flatter you. Five seeds × five folds = 25 mini-exams. CELL 7 averages them → the number you trust.

### What Spearman is, intuitively
Sort guides by true cut.score. Sort by predicted score. Spearman asks: do those two orderings agree?  
`1.0` = identical ranking; `0` = no relationship; negative = backwards.
