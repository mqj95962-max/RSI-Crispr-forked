# P0 line-by-line: `Runjia/sgrna/harness/run_ablation.py`
**Why this file matters:** The shared experiment engine: fair train/test splits, feature picking, and family ablations.
**Length:** 559 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

A shared laboratory protocol: same fair exams, same model recipe, swap which feature ‘ingredients’ you add.

---
### Lines 1–36
```python
"""Step 3 -- the ablation harness. One family at a time, leakage-safe.

This reproduces the frozen protocol the project already trusts -- five seeds
(41-45), five folds, top-300 features by XGBoost gain, 400-tree champion --
with one rule that matters more than any of the settings: **every fit happens
inside the training split**. Median imputation, feature ranking and selection
all see the training fold only. A validation fold that has influenced which
features were chosen is not a validation fold.

From a notebook cell (the usual way):

    nb.ablate()                                        # baseline only
    nb.ablate(["a_flank"])
    nb.ablate(["d_supercoiling"], group="bin100k", permute=True)
    nb.ablate(["a_flank", "b_energy"], together=True)

or from a terminal:

    python -m sgrna.run_ablation --families a_flank
    python -m sgrna.run_ablation --families a_flank b_energy --together
    python -m sgrna.run_ablation --families d_supercoiling --group bin100k --permute
    python -m sgrna.run_ablation --baseline-only

Reading the output
------------------
Four things decide whether a family earned its place:

  d_spearman   change against the baseline in the same run
  permuted     the same family with its rows shuffled -- the noise floor
  group        hold out whole genes or 100 kb blocks instead of random rows;
               mandatory for any positional family (D2, E, G)
  selected     how many of the family's columns survived into the top 300

A family whose delta is inside the permuted band did not work, however many
of its columns got selected. Run with --permute before claiming anything.
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 38
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 40
```python
import argparse
```
**Plain English:** Load toolbox code: `import argparse` — used here for **command-line switches like `--flank 1000`**.

### Line 41
```python
import json
```
**Plain English:** Load toolbox code: `import json` — used here for **read/write JSON text files**.

### Line 42
```python
import sys
```
**Plain English:** Load toolbox code: `import sys` — used here for **Python runtime (arguments, exit codes)**.

### Line 43
```python
import time
```
**Plain English:** Load toolbox code: `import time` — used here for **clocks and timers**.

### Line 44
```python
from datetime import datetime
```
**Plain English:** Load toolbox code: `from datetime import datetime` — used here for **clocks and timers**.

### Line 46
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 47
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 48
```python
from scipy.stats import pearsonr, spearmanr
```
**Plain English:** Load toolbox code: `from scipy.stats import pearsonr, spearmanr` — used here for **scientific stats (Spearman/Pearson)**.

### Line 49
```python
from sklearn.metrics import mean_squared_error, r2_score
```
**Plain English:** Load toolbox code: `from sklearn.metrics import mean_squared_error, r2_score` — used here for **classic ML helpers (splits, metrics)**.

### Line 50
```python
from sklearn.model_selection import KFold
```
**Plain English:** Load toolbox code: `from sklearn.model_selection import KFold` — used here for **classic ML helpers (splits, metrics)**.

### Line 52
```python
from .. import config
```
**Plain English:** Load a project module from this repo: `from .. import config`.

### Line 53
```python
from ..build.build_matrix import load_dataset
```
**Plain English:** Load an external or local module: `from ..build.build_matrix import load_dataset`.

### Line 54
```python
from ..features import ALL
```
**Plain English:** Load toolbox code: `from ..features import ALL` — used here for **text pattern matching (regular expressions)**.

### Line 57
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 58
```python
# Model settings -- identical to the frozen baseline script
```
**Plain English:** Human-only note (Python ignores it): Model settings -- identical to the frozen baseline script

### Line 59
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 62
```python
def selector_params(seed: int) -> dict:
```
**Plain English:** Defines a reusable recipe named `selector_params`. Inputs in parentheses: `seed: int`. Returns type hint: dict. Nothing runs yet until something *calls* `selector_params(...)`.

### Line 63
```python
    return dict(
```
**Plain English:** Finish this function and send back: `dict(`.

### Line 64
```python
        n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `300, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 65
```python
        colsample_bytree=0.8, reg_alpha=0.0, reg_lambda=1.0, min_child_weight=1,
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, reg_alpha=0.0, reg_lambda=1.0, min_child_weight=1,`. Whenever you later write that name, you mean this value.

### Line 66
```python
        random_state=seed, n_jobs=-1, tree_method="hist", importance_type="gain",
```
**Plain English:** Store a value: the name `random_state` now holds the result of `seed, n_jobs=-1, tree_method="hist", importance_type="gain",`. Whenever you later write that name, you mean this value.

### Line 67
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 70
```python
def make_selector(seed: int, kind: str | None = None):
```
**Plain English:** Defines a reusable recipe named `make_selector`. Inputs in parentheses: `seed: int, kind: str | None = None`. Nothing runs yet until something *calls* `make_selector(...)`.

### Lines 71–75
```python
    """The throwaway model whose only job is to rank columns.

    Its predictions are never used, so the choice is about speed and ordering.
    `selector_params` is kept as the XGBoost settings of the frozen baseline.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 76
```python
    kind = kind or config.SELECTOR
```
**Plain English:** Store a value: the name `kind` now holds the result of `kind or config.SELECTOR`. Whenever you later write that name, you mean this value.

### Line 77
```python
    if kind == "xgboost":
```
**Plain English:** Decision: run the indented block only when this condition is true → `kind == "xgboost"`.

### Line 78
```python
        import xgboost as xgb
```
**Plain English:** Load toolbox code: `import xgboost as xgb` — used here for **the gradient-boosted tree learner**.

### Line 79
```python
        return xgb.XGBRegressor(**selector_params(seed))
```
**Plain English:** Finish this function and send back: `xgb.XGBRegressor(**selector_params(seed))`.

### Line 80
```python
    if kind == "lightgbm":
```
**Plain English:** Decision: run the indented block only when this condition is true → `kind == "lightgbm"`.

### Line 81
```python
        import lightgbm as lgb
```
**Plain English:** Load an external or local module: `import lightgbm as lgb`.

### Line 82
```python
        return lgb.LGBMRegressor(
```
**Plain English:** Finish this function and send back: `lgb.LGBMRegressor(`.

### Line 83
```python
            n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `300, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 84
```python
            colsample_bytree=0.8, random_state=seed, n_jobs=-1, verbose=-1,
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, random_state=seed, n_jobs=-1, verbose=-1,`. Whenever you later write that name, you mean this value.

### Line 85
```python
            importance_type="gain",
```
**Plain English:** Store a value: the name `importance_type` now holds the result of `"gain",`. Whenever you later write that name, you mean this value.

### Line 86
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 87
```python
    raise ValueError(f"unknown selector {kind!r}")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"unknown selector {kind!r}")`.

### Line 90
```python
def champion_params(seed: int) -> dict:
```
**Plain English:** Defines a reusable recipe named `champion_params`. Inputs in parentheses: `seed: int`. Returns type hint: dict. Nothing runs yet until something *calls* `champion_params(...)`.

### Line 91
```python
    return dict(
```
**Plain English:** Finish this function and send back: `dict(`.

### Line 92
```python
        n_estimators=config.N_ESTIMATORS, learning_rate=0.05, max_depth=4,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `config.N_ESTIMATORS, learning_rate=0.05, max_depth=4,`. Whenever you later write that name, you mean this value.

### Line 93
```python
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.0, reg_lambda=1.0,
```
**Plain English:** Store a value: the name `subsample` now holds the result of `0.8, colsample_bytree=0.8, reg_alpha=0.0, reg_lambda=1.0,`. Whenever you later write that name, you mean this value.

### Line 94
```python
        min_child_weight=1, random_state=seed, n_jobs=-1, tree_method="hist",
```
**Plain English:** Store a value: the name `min_child_weight` now holds the result of `1, random_state=seed, n_jobs=-1, tree_method="hist",`. Whenever you later write that name, you mean this value.

### Line 95
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 98
```python
def _impute(X_train: np.ndarray, X_val: np.ndarray):
```
**Plain English:** Defines a reusable recipe named `_impute`. Inputs in parentheses: `X_train: np.ndarray, X_val: np.ndarray`. Nothing runs yet until something *calls* `_impute(...)`.

### Line 99
```python
    """Median impute with statistics from the training fold only."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Median impute with statistics from the training fold only.

### Line 100
```python
    X_train = X_train.astype(np.float32, copy=True)
```
**Plain English:** Store a value: the name `X_train` now holds the result of `X_train.astype(np.float32, copy=True)`. Whenever you later write that name, you mean this value.

### Line 101
```python
    X_val = X_val.astype(np.float32, copy=True)
```
**Plain English:** Store a value: the name `X_val` now holds the result of `X_val.astype(np.float32, copy=True)`. Whenever you later write that name, you mean this value.

### Line 102
```python
    med = np.nanmedian(X_train, axis=0)
```
**Plain English:** Store a value: the name `med` now holds the result of `np.nanmedian(X_train, axis=0)`. Whenever you later write that name, you mean this value.

### Line 103
```python
    med = np.where(np.isnan(med), 0.0, med)
```
**Plain English:** Store a value: the name `med` now holds the result of `np.where(np.isnan(med), 0.0, med)`. Whenever you later write that name, you mean this value.

### Line 104
```python
    r, c = np.where(np.isnan(X_train))
```
**Plain English:** Run this instruction: `r, c = np.where(np.isnan(X_train))`.

### Line 105
```python
    X_train[r, c] = med[c]
```
**Plain English:** Run this instruction: `X_train[r, c] = med[c]`.

### Line 106
```python
    r, c = np.where(np.isnan(X_val))
```
**Plain English:** Run this instruction: `r, c = np.where(np.isnan(X_val))`.

### Line 107
```python
    X_val[r, c] = med[c]
```
**Plain English:** Run this instruction: `X_val[r, c] = med[c]`.

### Line 108
```python
    return X_train, X_val
```
**Plain English:** Finish this function and send back: `X_train, X_val`.

### Line 111
```python
def _safe_spearman(a, b) -> float:
```
**Plain English:** Defines a reusable recipe named `_safe_spearman`. Inputs in parentheses: `a, b`. Returns type hint: float. Nothing runs yet until something *calls* `_safe_spearman(...)`.

### Line 112
```python
    if len(a) < 2:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(a) < 2`.

### Line 113
```python
        return float("nan")
```
**Plain English:** Finish this function and send back: `float("nan")`.

### Line 114
```python
    rho, _ = spearmanr(a, b)
```
**Plain English:** Run this instruction: `rho, _ = spearmanr(a, b)`.

### Line 115
```python
    return 0.0 if np.isnan(rho) else float(rho)
```
**Plain English:** Finish this function and send back: `0.0 if np.isnan(rho) else float(rho)`.

### Line 118
```python
def _safe_pearson(a, b) -> float:
```
**Plain English:** Defines a reusable recipe named `_safe_pearson`. Inputs in parentheses: `a, b`. Returns type hint: float. Nothing runs yet until something *calls* `_safe_pearson(...)`.

### Line 119
```python
    if len(a) < 2:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(a) < 2`.

### Line 120
```python
        return float("nan")
```
**Plain English:** Finish this function and send back: `float("nan")`.

### Line 121
```python
    rho, _ = pearsonr(a, b)
```
**Plain English:** Run this instruction: `rho, _ = pearsonr(a, b)`.

### Line 122
```python
    return 0.0 if np.isnan(rho) else float(rho)
```
**Plain English:** Finish this function and send back: `0.0 if np.isnan(rho) else float(rho)`.

### Line 125
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 126
```python
# Cross-validation
```
**Plain English:** Human-only note (Python ignores it): Cross-validation

### Line 127
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 130
```python
def grouped_folds(groups, n_splits: int, seed: int):
```
**Plain English:** Defines a reusable recipe named `grouped_folds`. Inputs in parentheses: `groups, n_splits: int, seed: int`. Nothing runs yet until something *calls* `grouped_folds(...)`.

### Lines 131–145
```python
    """KFold over *groups* rather than rows.

    Why this matters here: the library puts ~20 guides in every gene, and
    guides in the same gene share a locus. Plain KFold therefore puts guides
    from the same gene in both the training and the validation split. For
    sequence features that is harmless -- the sequences differ. For anything
    positional (supercoiling, nucleoid bin, distance to oriC or to a TSS) it
    is not: those columns identify the locus, so the model can learn "guides
    around here score about this much" and be rewarded for it at validation
    time. The gain is real memorisation, not real prediction.

    Grouping by gene removes that route. Any positional family should be
    reported under `--group gene`; a family whose gain survives grouping is
    the one worth writing up.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 146
```python
    groups = np.asarray(groups, dtype=object)
```
**Plain English:** Store a value: the name `groups` now holds the result of `np.asarray(groups, dtype=object)`. Whenever you later write that name, you mean this value.

### Line 147
```python
    unique = np.unique(groups)
```
**Plain English:** Store a value: the name `unique` now holds the result of `np.unique(groups)`. Whenever you later write that name, you mean this value.

### Line 148
```python
    rng = np.random.default_rng(seed)
```
**Plain English:** Store a value: the name `rng` now holds the result of `np.random.default_rng(seed)`. Whenever you later write that name, you mean this value.

### Line 149
```python
    rng.shuffle(unique)
```
**Plain English:** Run this instruction: `rng.shuffle(unique)`.

### Line 150
```python
    chunks = np.array_split(unique, n_splits)
```
**Plain English:** Store a value: the name `chunks` now holds the result of `np.array_split(unique, n_splits)`. Whenever you later write that name, you mean this value.

### Line 151
```python
    for chunk in chunks:
```
**Plain English:** Loop: repeat the indented block once for each item → `chunk in chunks`.

### Line 152
```python
        mask = np.isin(groups, chunk)
```
**Plain English:** Store a value: the name `mask` now holds the result of `np.isin(groups, chunk)`. Whenever you later write that name, you mean this value.

### Line 153
```python
        yield np.where(~mask)[0], np.where(mask)[0]
```
**Plain English:** Produce one result now but pause the function so the caller can ask for the next one (a generator) → `np.where(~mask)[0], np.where(mask)[0]`.

### Line 156
```python
def fold_checkpoint_path(tag: str):
```
**Plain English:** Defines a reusable recipe named `fold_checkpoint_path`. Inputs in parentheses: `tag: str`. Nothing runs yet until something *calls* `fold_checkpoint_path(...)`.

### Line 157
```python
    return config.RESULTS / f"folds_{tag}.csv"
```
**Plain English:** Finish this function and send back: `config.RESULTS / f"folds_{tag}.csv"`.

### Line 160
```python
def _load_checkpoint(tag: str | None) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `_load_checkpoint`. Inputs in parentheses: `tag: str | None`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `_load_checkpoint(...)`.

### Line 161
```python
    if not tag:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not tag`.

### Line 162
```python
        return pd.DataFrame()
```
**Plain English:** Finish this function and send back: `pd.DataFrame()`.

### Line 163
```python
    path = fold_checkpoint_path(tag)
```
**Plain English:** Store a value: the name `path` now holds the result of `fold_checkpoint_path(tag)`. Whenever you later write that name, you mean this value.

### Line 164
```python
    if not path.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not path.exists()`.

### Line 165
```python
        return pd.DataFrame()
```
**Plain English:** Finish this function and send back: `pd.DataFrame()`.

### Line 166
```python
    return pd.read_csv(path)
```
**Plain English:** Finish this function and send back: `pd.read_csv(path)`.

### Line 169
```python
def _append_checkpoint(tag: str | None, row: dict) -> None:
```
**Plain English:** Defines a reusable recipe named `_append_checkpoint`. Inputs in parentheses: `tag: str | None, row: dict`. Returns type hint: None. Nothing runs yet until something *calls* `_append_checkpoint(...)`.

### Line 170
```python
    if not tag:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not tag`.

### Line 171
```python
        return
```
**Plain English:** Finish this function and send back: `(nothing / None)`.

### Line 172
```python
    path = fold_checkpoint_path(tag)
```
**Plain English:** Store a value: the name `path` now holds the result of `fold_checkpoint_path(tag)`. Whenever you later write that name, you mean this value.

### Line 173
```python
    header = not path.exists()
```
**Plain English:** Store a value: the name `header` now holds the result of `not path.exists()`. Whenever you later write that name, you mean this value.

### Line 174
```python
    pd.DataFrame([row]).to_csv(path, mode="a", header=header, index=False)
```
**Plain English:** Run this instruction: `pd.DataFrame([row]).to_csv(path, mode="a", header=header, index=False)`.

### Line 177
```python
def cross_validate(X, y, feature_names, family_of, n_features=None,
```
**Plain English:** Run this instruction: `def cross_validate(X, y, feature_names, family_of, n_features=None,`.

### Line 178
```python
                   seeds=None, n_splits=None, verbose=True, groups=None,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `None, n_splits=None, verbose=True, groups=None,`. Whenever you later write that name, you mean this value.

### Line 179
```python
                   tag: str | None = None, experiment: str = "unnamed",
```
**Plain English:** Run this instruction: `tag: str | None = None, experiment: str = "unnamed",`.

### Line 180
```python
                   deadline: float | None = None,
```
**Plain English:** Run this instruction: `deadline: float | None = None,`.

### Line 181
```python
                   champion_overrides: dict | None = None,
```
**Plain English:** Run this instruction: `champion_overrides: dict | None = None,`.

### Line 182
```python
                   return_oof: bool = False) -> dict:
```
**Plain English:** Finish this function and send back: `_oof: bool = False) -> dict:`.

### Lines 183–198
```python
    """Leakage-safe CV, resumable one fold at a time.

    Every fold is written to `results/folds_<tag>.csv` as soon as it finishes,
    and a fold already recorded there is skipped. That matters for two
    reasons: a 5-seed run over the 408-column flank family takes about fifteen
    minutes, longer than a dropped Colab session tends to survive; and it lets
    a long experiment be built up over several sittings without ever
    recomputing work. Pass `deadline` (an absolute time.time() value) to stop
    cleanly partway and resume later -- the partial result is still
    summarised, marked incomplete.

    `champion_overrides` replaces named champion hyperparameters for this call
    only -- used by `representation.py` to ask whether a deeper tree can
    recover what a redundant encoding provides. It is deliberately not a config
    setting: the frozen champion is an anchor, not a default to drift from.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 199
```python
    import xgboost as xgb
```
**Plain English:** Load toolbox code: `import xgboost as xgb` — used here for **the gradient-boosted tree learner**.

### Line 201
```python
    n_features = n_features or config.N_FEATURES
```
**Plain English:** Store a value: the name `n_features` now holds the result of `n_features or config.N_FEATURES`. Whenever you later write that name, you mean this value.

### Line 202
```python
    seeds = seeds or config.SEEDS
```
**Plain English:** Store a value: the name `seeds` now holds the result of `seeds or config.SEEDS`. Whenever you later write that name, you mean this value.

### Line 203
```python
    n_splits = n_splits or config.N_SPLITS
```
**Plain English:** Store a value: the name `n_splits` now holds the result of `n_splits or config.N_SPLITS`. Whenever you later write that name, you mean this value.

### Line 205
```python
    family_of = np.asarray(family_of)
```
**Plain English:** Store a value: the name `family_of` now holds the result of `np.asarray(family_of)`. Whenever you later write that name, you mean this value.

### Line 206
```python
    done = _load_checkpoint(tag)
```
**Plain English:** Store a value: the name `done` now holds the result of `_load_checkpoint(tag)`. Whenever you later write that name, you mean this value.

### Line 207
```python
    if len(done):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(done)`.

### Line 208
```python
        done = done[done["experiment"] == experiment]
```
**Plain English:** Store a value: the name `done` now holds the result of `done[done["experiment"] == experiment]`. Whenever you later write that name, you mean this value.

### Line 209
```python
    seen = set(zip(done.get("seed", []), done.get("fold", [])))
```
**Plain English:** Store a value: the name `seen` now holds the result of `set(zip(done.get("seed", []), done.get("fold", [])))`. Whenever you later write that name, you mean this value.

### Line 210
```python
    fold_rows = done.to_dict("records") if len(done) else []
```
**Plain English:** Store a value: the name `fold_rows` now holds the result of `done.to_dict("records") if len(done) else []`. Whenever you later write that name, you mean this value.

### Line 211
```python
    if seen and verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `seen and verbose`.

### Line 212
```python
        print(f"    resuming: {len(seen)} of {len(seeds) * n_splits} folds already done")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"    resuming: {len(seen)} of {len(seeds) * n_splits} folds already done")`.

### Line 214
```python
    oof_pred = np.full(len(y), np.nan, dtype=float) if return_oof else None
```
**Plain English:** Store a value: the name `oof_pred` now holds the result of `np.full(len(y), np.nan, dtype=float) if return_oof else None`. Whenever you later write that name, you mean this value.

### Line 215
```python
    oof_y = np.full(len(y), np.nan, dtype=float) if return_oof else None
```
**Plain English:** Store a value: the name `oof_y` now holds the result of `np.full(len(y), np.nan, dtype=float) if return_oof else None`. Whenever you later write that name, you mean this value.

### Line 217
```python
    stopped_early = False
```
**Plain English:** Store a value: the name `stopped_early` now holds the result of `False`. Whenever you later write that name, you mean this value.

### Line 218
```python
    for seed in seeds:
```
**Plain English:** Loop: repeat the indented block once for each item → `seed in seeds`.

### Line 219
```python
        if stopped_early:
```
**Plain English:** Decision: run the indented block only when this condition is true → `stopped_early`.

### Line 220
```python
            break
```
**Plain English:** Leave the loop early.

### Line 221
```python
        if groups is None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `groups is None`.

### Line 222
```python
            splitter = KFold(
```
**Plain English:** Store a value: the name `splitter` now holds the result of `KFold(`. Whenever you later write that name, you mean this value.

### Line 223
```python
                n_splits=n_splits, shuffle=True, random_state=seed
```
**Plain English:** Store a value: the name `n_splits` now holds the result of `n_splits, shuffle=True, random_state=seed`. Whenever you later write that name, you mean this value.

### Line 224
```python
            ).split(X)
```
**Plain English:** Run this instruction: `).split(X)`.

### Line 225
```python
        else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 226
```python
            splitter = grouped_folds(groups, n_splits, seed)
```
**Plain English:** Store a value: the name `splitter` now holds the result of `grouped_folds(groups, n_splits, seed)`. Whenever you later write that name, you mean this value.

### Line 227
```python
        for fold, (tr, va) in enumerate(splitter, start=1):
```
**Plain English:** Loop: repeat the indented block once for each item → `fold, (tr, va) in enumerate(splitter, start=1)`.

### Line 228
```python
            if (seed, fold) in seen:
```
**Plain English:** Decision: run the indented block only when this condition is true → `(seed, fold) in seen`.

### Line 229
```python
                continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 230
```python
            if deadline and time.time() > deadline:
```
**Plain English:** Decision: run the indented block only when this condition is true → `deadline and time.time() > deadline`.

### Line 231
```python
                stopped_early = True
```
**Plain English:** Store a value: the name `stopped_early` now holds the result of `True`. Whenever you later write that name, you mean this value.

### Line 232
```python
                break
```
**Plain English:** Leave the loop early.

### Line 234
```python
            X_tr, X_va = _impute(X[tr], X[va])
```
**Plain English:** Run this instruction: `X_tr, X_va = _impute(X[tr], X[va])`.

### Line 235
```python
            y_tr, y_va = y[tr], y[va]
```
**Plain English:** Run this instruction: `y_tr, y_va = y[tr], y[va]`.

### Line 237
```python
            selector = make_selector(seed)
```
**Plain English:** Store a value: the name `selector` now holds the result of `make_selector(seed)`. Whenever you later write that name, you mean this value.

### Line 238
```python
            selector.fit(X_tr, y_tr)
```
**Plain English:** Run this instruction: `selector.fit(X_tr, y_tr)`.

### Line 239
```python
            gains = selector.feature_importances_
```
**Plain English:** Store a value: the name `gains` now holds the result of `selector.feature_importances_`. Whenever you later write that name, you mean this value.

### Line 240
```python
            top = np.argsort(gains)[::-1][:n_features]
```
**Plain English:** Store a value: the name `top` now holds the result of `np.argsort(gains)[::-1][:n_features]`. Whenever you later write that name, you mean this value.

### Line 241
```python
            n_engineered = int((family_of[top] != "base").sum())
```
**Plain English:** Store a value: the name `n_engineered` now holds the result of `int((family_of[top] != "base").sum())`. Whenever you later write that name, you mean this value.

### Line 243
```python
            params = champion_params(seed)
```
**Plain English:** Store a value: the name `params` now holds the result of `champion_params(seed)`. Whenever you later write that name, you mean this value.

### Line 244
```python
            if champion_overrides:
```
**Plain English:** Decision: run the indented block only when this condition is true → `champion_overrides`.

### Line 245
```python
                params.update(champion_overrides)
```
**Plain English:** Run this instruction: `params.update(champion_overrides)`.

### Line 246
```python
            model = xgb.XGBRegressor(**params)
```
**Plain English:** Store a value: the name `model` now holds the result of `xgb.XGBRegressor(**params)`. Whenever you later write that name, you mean this value.

### Line 247
```python
            model.fit(X_tr[:, top], y_tr)
```
**Plain English:** Run this instruction: `model.fit(X_tr[:, top], y_tr)`.

### Line 248
```python
            pred = model.predict(X_va[:, top])
```
**Plain English:** Store a value: the name `pred` now holds the result of `model.predict(X_va[:, top])`. Whenever you later write that name, you mean this value.

### Line 249
```python
            if return_oof:
```
**Plain English:** Decision: run the indented block only when this condition is true → `return_oof`.

### Line 250
```python
                oof_pred[va] = np.asarray(pred).ravel()
```
**Plain English:** Store a value: the name `oof_pred[va]` now holds the result of `np.asarray(pred).ravel()`. Whenever you later write that name, you mean this value.

### Line 251
```python
                oof_y[va] = y_va
```
**Plain English:** Store a value: the name `oof_y[va]` now holds the result of `y_va`. Whenever you later write that name, you mean this value.

### Line 253
```python
            row = dict(
```
**Plain English:** Store a value: the name `row` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 254
```python
                experiment=experiment, seed=seed, fold=fold,
```
**Plain English:** Store a value: the name `experiment` now holds the result of `experiment, seed=seed, fold=fold,`. Whenever you later write that name, you mean this value.

### Line 255
```python
                r2=r2_score(y_va, pred),
```
**Plain English:** Store a value: the name `r2` now holds the result of `r2_score(y_va, pred),`. Whenever you later write that name, you mean this value.

### Line 256
```python
                spearman=_safe_spearman(y_va, pred),
```
**Plain English:** Store a value: the name `spearman` now holds the result of `_safe_spearman(y_va, pred),`. Whenever you later write that name, you mean this value.

### Line 257
```python
                pearson=_safe_pearson(y_va, pred),
```
**Plain English:** Store a value: the name `pearson` now holds the result of `_safe_pearson(y_va, pred),`. Whenever you later write that name, you mean this value.

### Line 258
```python
                mse=mean_squared_error(y_va, pred),
```
**Plain English:** Store a value: the name `mse` now holds the result of `mean_squared_error(y_va, pred),`. Whenever you later write that name, you mean this value.

### Line 259
```python
                n_engineered_selected=n_engineered,
```
**Plain English:** Store a value: the name `n_engineered_selected` now holds the result of `n_engineered,`. Whenever you later write that name, you mean this value.

### Line 260
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 261
```python
            fold_rows.append(row)
```
**Plain English:** Run this instruction: `fold_rows.append(row)`.

### Line 262
```python
            _append_checkpoint(tag, row)
```
**Plain English:** Run this instruction: `_append_checkpoint(tag, row)`.

### Line 263
```python
        if verbose and not stopped_early:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose and not stopped_early`.

### Line 264
```python
            last = [r for r in fold_rows if r["seed"] == seed]
```
**Plain English:** Store a value: the name `last` now holds the result of `[r for r in fold_rows if r["seed"] == seed]`. Whenever you later write that name, you mean this value.

### Line 265
```python
            if last:
```
**Plain English:** Decision: run the indented block only when this condition is true → `last`.

### Line 266
```python
                print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 267
```python
                    f"    seed {seed}: R2 {np.mean([r['r2'] for r in last]):.4f}  "
```
**Plain English:** Run this instruction: `f"    seed {seed}: R2 {np.mean([r['r2'] for r in last]):.4f}  "`.

### Line 268
```python
                    f"rho {np.mean([r['spearman'] for r in last]):.4f}"
```
**Plain English:** Run this instruction: `f"rho {np.mean([r['spearman'] for r in last]):.4f}"`.

### Line 269
```python
                )
```
**Plain English:** Run this instruction: `)`.

### Line 271
```python
    folds = pd.DataFrame(fold_rows)
```
**Plain English:** Store a value: the name `folds` now holds the result of `pd.DataFrame(fold_rows)`. Whenever you later write that name, you mean this value.

### Line 272
```python
    complete = len(folds) == len(seeds) * n_splits
```
**Plain English:** Store a value: the name `complete` now holds the result of `len(folds) == len(seeds) * n_splits`. Whenever you later write that name, you mean this value.

### Line 273
```python
    if not complete and verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not complete and verbose`.

### Line 274
```python
        print(f"    INCOMPLETE: {len(folds)} / {len(seeds) * n_splits} folds. "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"    INCOMPLETE: {len(folds)} / {len(seeds) * n_splits} folds. "`.

### Line 275
```python
              f"Re-run the same call to continue.")
```
**Plain English:** Run this instruction: `f"Re-run the same call to continue.")`.

### Line 276
```python
    per_seed = folds.groupby("seed")[["r2", "spearman", "pearson", "mse"]].mean()
```
**Plain English:** Store a value: the name `per_seed` now holds the result of `folds.groupby("seed")[["r2", "spearman", "pearson", "mse"]].mean()`. Whenever you later write that name, you mean this value.

### Line 277
```python
    out = dict(
```
**Plain English:** Store a value: the name `out` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 278
```python
        folds=folds,
```
**Plain English:** Store a value: the name `folds` now holds the result of `folds,`. Whenever you later write that name, you mean this value.

### Line 279
```python
        per_seed=per_seed,
```
**Plain English:** Store a value: the name `per_seed` now holds the result of `per_seed,`. Whenever you later write that name, you mean this value.

### Line 280
```python
        complete=complete,
```
**Plain English:** Store a value: the name `complete` now holds the result of `complete,`. Whenever you later write that name, you mean this value.

### Line 281
```python
        n_folds_done=len(folds),
```
**Plain English:** Store a value: the name `n_folds_done` now holds the result of `len(folds),`. Whenever you later write that name, you mean this value.

### Line 282
```python
        summary={
```
**Plain English:** Store a value: the name `summary` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 283
```python
            m: dict(mean=float(per_seed[m].mean()), sd=float(per_seed[m].std()))
```
**Plain English:** Run this instruction: `m: dict(mean=float(per_seed[m].mean()), sd=float(per_seed[m].std()))`.

### Line 284
```python
            for m in ("r2", "spearman", "pearson", "mse")
```
**Plain English:** Loop: repeat the indented block once for each item → `m in ("r2", "spearman", "pearson", "mse")`.

### Line 285
```python
        },
```
**Plain English:** Run this instruction: `},`.

### Line 286
```python
        selected={"engineered": float(folds["n_engineered_selected"].mean())
```
**Plain English:** Store a value: the name `selected` now holds the result of `{"engineered": float(folds["n_engineered_selected"].mean())`. Whenever you later write that name, you mean this value.

### Line 287
```python
                  if len(folds) else 0.0},
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(folds) else 0.0},`.

### Line 288
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 289
```python
    if return_oof:
```
**Plain English:** Decision: run the indented block only when this condition is true → `return_oof`.

### Line 290
```python
        out["oof_pred"] = oof_pred
```
**Plain English:** Store a value: the name `out["oof_pred"]` now holds the result of `oof_pred`. Whenever you later write that name, you mean this value.

### Line 291
```python
        out["oof_y"] = oof_y
```
**Plain English:** Store a value: the name `out["oof_y"]` now holds the result of `oof_y`. Whenever you later write that name, you mean this value.

### Line 292
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 295
```python
def _permute_families(X, family_of, families, seed=0):
```
**Plain English:** Defines a reusable recipe named `_permute_families`. Inputs in parentheses: `X, family_of, families, seed=0`. Nothing runs yet until something *calls* `_permute_families(...)`.

### Line 296
```python
    """Shuffle the rows of the engineered columns -- the noise floor."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Shuffle the rows of the engineered columns -- the noise floor.

### Line 297
```python
    rng = np.random.default_rng(seed)
```
**Plain English:** Store a value: the name `rng` now holds the result of `np.random.default_rng(seed)`. Whenever you later write that name, you mean this value.

### Line 298
```python
    X = X.copy()
```
**Plain English:** Store a value: the name `X` now holds the result of `X.copy()`. Whenever you later write that name, you mean this value.

### Line 299
```python
    fam = np.asarray(family_of)
```
**Plain English:** Store a value: the name `fam` now holds the result of `np.asarray(family_of)`. Whenever you later write that name, you mean this value.

### Line 300
```python
    idx = np.where(np.isin(fam, families))[0]
```
**Plain English:** Store a value: the name `idx` now holds the result of `np.where(np.isin(fam, families))[0]`. Whenever you later write that name, you mean this value.

### Line 301
```python
    if idx.size:
```
**Plain English:** Decision: run the indented block only when this condition is true → `idx.size`.

### Line 302
```python
        X[:, idx] = X[rng.permutation(X.shape[0])][:, idx]
```
**Plain English:** Run this instruction: `X[:, idx] = X[rng.permutation(X.shape[0])][:, idx]`.

### Line 303
```python
    return X
```
**Plain English:** Finish this function and send back: `X`.

### Line 306
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 307
```python
# Experiment driver
```
**Plain English:** Human-only note (Python ignores it): Experiment driver

### Line 308
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 311
```python
GROUP_CHOICES = {"gene": None, "bin5k": 5_000, "bin100k": 100_000,
```
**Plain English:** Store a value: the name `GROUP_CHOICES` now holds the result of `{"gene": None, "bin5k": 5_000, "bin100k": 100_000,`. Whenever you later write that name, you mean this value.

### Line 312
```python
                 "bin500k": 500_000, "arc5": "arc"}
```
**Plain English:** Run this instruction: `"bin500k": 500_000, "arc5": "arc"}`.

### Line 315
```python
def load_groups(ids, by: str = "gene") -> np.ndarray:
```
**Plain English:** Defines a reusable recipe named `load_groups`. Inputs in parentheses: `ids, by: str = "gene"`. Returns type hint: np.ndarray. Nothing runs yet until something *calls* `load_groups(...)`.

### Lines 316–328
```python
    """Group label per guide, for grouped cross-validation.

    `gene` holds out whole genes. `bin100k` / `bin500k` hold out contiguous
    chromosome blocks, which is the stricter test for anything positional:
    neighbouring genes sit in the same supercoiling domain and the same Hi-C
    neighbourhood, so gene-level grouping alone does not separate them.

    `arc5` is the strictest: it cuts the chromosome into five contiguous arcs,
    so with `n_splits=5` each fold holds out one whole arc. Blocked schemes
    still let the model *interpolate* a smooth ori-to-ter trend from the
    blocks either side; holding out a contiguous fifth forces extrapolation
    instead. Use it to check any claim that a positional feature generalises.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 329
```python
    from ..io_utils import load_guide_index
```
**Plain English:** Load an external or local module: `from ..io_utils import load_guide_index`.

### Line 331
```python
    idx = load_guide_index().set_index(config.ID_COL)
```
**Plain English:** Store a value: the name `idx` now holds the result of `load_guide_index().set_index(config.ID_COL)`. Whenever you later write that name, you mean this value.

### Line 332
```python
    if by == "gene":
```
**Plain English:** Decision: run the indented block only when this condition is true → `by == "gene"`.

### Line 333
```python
        series = idx.reindex(ids)["b_number"]
```
**Plain English:** Store a value: the name `series` now holds the result of `idx.reindex(ids)["b_number"]`. Whenever you later write that name, you mean this value.

### Line 334
```python
    elif by == "arc5":
```
**Plain English:** Otherwise-if: another condition to try if previous `if`/`elif` failed → `by == "arc5"`.

### Line 335
```python
        from ..build import genome
```
**Plain English:** Load a project module from this repo: `from ..build import genome`.

### Line 337
```python
        size = genome.genome_length() / 5
```
**Plain English:** Store a value: the name `size` now holds the result of `genome.genome_length() / 5`. Whenever you later write that name, you mean this value.

### Line 338
```python
        # clamp so the final base does not spill into a sixth, one-guide arc
```
**Plain English:** Human-only note (Python ignores it): clamp so the final base does not spill into a sixth, one-guide arc

### Line 339
```python
        series = (((idx.reindex(ids)["left"] - 1) // size)
```
**Plain English:** Store a value: the name `series` now holds the result of `(((idx.reindex(ids)["left"] - 1) // size)`. Whenever you later write that name, you mean this value.

### Line 340
```python
                  .clip(upper=4).astype("Int64"))
```
**Plain English:** Run this instruction: `.clip(upper=4).astype("Int64"))`.

### Line 341
```python
    else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 342
```python
        size = GROUP_CHOICES.get(by)
```
**Plain English:** Store a value: the name `size` now holds the result of `GROUP_CHOICES.get(by)`. Whenever you later write that name, you mean this value.

### Line 343
```python
        if size is None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `size is None`.

### Line 344
```python
            raise ValueError(f"Unknown grouping {by!r}; choose from {list(GROUP_CHOICES)}")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"Unknown grouping {by!r}; choose from {list(GROUP_CHOICES)}")`.

### Line 345
```python
        series = (idx.reindex(ids)["left"] // size).astype("Int64")
```
**Plain English:** Store a value: the name `series` now holds the result of `(idx.reindex(ids)["left"] // size).astype("Int64")`. Whenever you later write that name, you mean this value.

### Line 346
```python
    # One guide has a missing QCT descriptor and so no genomic position. Left
```
**Plain English:** Human-only note (Python ignores it): One guide has a missing QCT descriptor and so no genomic position. Left

### Line 347
```python
    # as its own group it becomes a one-row validation fold, which crashes the
```
**Plain English:** Human-only note (Python ignores it): as its own group it becomes a one-row validation fold, which crashes the

### Line 348
```python
    # correlation metrics; fold it into the largest group instead.
```
**Plain English:** Human-only note (Python ignores it): correlation metrics; fold it into the largest group instead.

### Line 349
```python
    labels = series.astype(str).replace({"<NA>": None})
```
**Plain English:** Store a value: the name `labels` now holds the result of `series.astype(str).replace({"<NA>": None})`. Whenever you later write that name, you mean this value.

### Line 350
```python
    if labels.isna().any():
```
**Plain English:** Decision: run the indented block only when this condition is true → `labels.isna().any()`.

### Line 351
```python
        labels = labels.fillna(labels.mode().iloc[0])
```
**Plain English:** Store a value: the name `labels` now holds the result of `labels.fillna(labels.mode().iloc[0])`. Whenever you later write that name, you mean this value.

### Line 352
```python
    return labels.to_numpy()
```
**Plain English:** Finish this function and send back: `labels.to_numpy()`.

### Line 355
```python
def run(families, together=False, permute=False, n_features=None,
```
**Plain English:** Run this instruction: `def run(families, together=False, permute=False, n_features=None,`.

### Line 356
```python
        seeds=None, n_splits=None, tag=None, force=False,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `None, n_splits=None, tag=None, force=False,`. Whenever you later write that name, you mean this value.

### Line 357
```python
        group_by=None, time_budget=None, label=None) -> pd.DataFrame:
```
**Plain English:** Store a value: the name `group_by` now holds the result of `None, time_budget=None, label=None) -> pd.DataFrame:`. Whenever you later write that name, you mean this value.

### Lines 358–364
```python
    """Run the requested experiments, appending to results/ablation_<tag>.csv.

    Results accumulate across invocations: an experiment already present in
    the file is skipped unless --force. That makes a long sweep restartable,
    which matters on Colab (sessions drop) and lets you add a family later
    without re-running everything.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 365
```python
    experiments: list[tuple[str, list[str]]] = [("baseline", [])]
```
**Plain English:** Run this instruction: `experiments: list[tuple[str, list[str]]] = [("baseline", [])]`.

### Line 366
```python
    if families:
```
**Plain English:** Decision: run the indented block only when this condition is true → `families`.

### Line 367
```python
        if together:
```
**Plain English:** Decision: run the indented block only when this condition is true → `together`.

### Line 368
```python
            experiments.append(("+".join(families), list(families)))
```
**Plain English:** Run this instruction: `experiments.append(("+".join(families), list(families)))`.

### Line 369
```python
        else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 370
```python
            experiments += [(f, [f]) for f in families]
```
**Plain English:** Run this instruction: `experiments += [(f, [f]) for f in families]`.

### Line 372
```python
    tag = tag or datetime.now().strftime("%Y%m%d-%H%M%S")
```
**Plain English:** Store a value: the name `tag` now holds the result of `tag or datetime.now().strftime("%Y%m%d-%H%M%S")`. Whenever you later write that name, you mean this value.

### Line 373
```python
    out = config.RESULTS / f"ablation_{tag}.csv"
```
**Plain English:** Store a value: the name `out` now holds the result of `config.RESULTS / f"ablation_{tag}.csv"`. Whenever you later write that name, you mean this value.

### Line 374
```python
    # One deadline for the whole call, shared by every experiment in it, so a
```
**Plain English:** Human-only note (Python ignores it): One deadline for the whole call, shared by every experiment in it, so a

### Line 375
```python
    # sweep of ten families still returns inside the budget instead of
```
**Plain English:** Human-only note (Python ignores it): sweep of ten families still returns inside the budget instead of

### Line 376
```python
    # spending the budget ten times over.
```
**Plain English:** Human-only note (Python ignores it): spending the budget ten times over.

### Line 377
```python
    deadline = (time.time() + time_budget) if time_budget else None
```
**Plain English:** Store a value: the name `deadline` now holds the result of `(time.time() + time_budget) if time_budget else None`. Whenever you later write that name, you mean this value.

### Line 379
```python
    rows: list[dict] = []
```
**Plain English:** Run this instruction: `rows: list[dict] = []`.

### Line 380
```python
    if out.exists() and not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `out.exists() and not force`.

### Line 381
```python
        rows = pd.read_csv(out).to_dict("records")
```
**Plain English:** Store a value: the name `rows` now holds the result of `pd.read_csv(out).to_dict("records")`. Whenever you later write that name, you mean this value.

### Line 383
```python
    # What counts as done is decided by the FOLD checkpoint, not by the summary
```
**Plain English:** Human-only note (Python ignores it): What counts as done is decided by the FOLD checkpoint, not by the summary

### Line 384
```python
    # file. A row can land in the summary while its experiment is still short of
```
**Plain English:** Human-only note (Python ignores it): file. A row can land in the summary while its experiment is still short of

### Line 385
```python
    # folds (that used to happen to permuted controls), and trusting the summary
```
**Plain English:** Human-only note (Python ignores it): folds (that used to happen to permuted controls), and trusting the summary

### Line 386
```python
    # then blocked it from ever finishing.
```
**Plain English:** Human-only note (Python ignores it): then blocked it from ever finishing.

### Line 387
```python
    expected = len(seeds or config.SEEDS) * (n_splits or config.N_SPLITS)
```
**Plain English:** Store a value: the name `expected` now holds the result of `len(seeds or config.SEEDS) * (n_splits or config.N_SPLITS)`. Whenever you later write that name, you mean this value.

### Line 388
```python
    done: set[str] = set()
```
**Plain English:** Run this instruction: `done: set[str] = set()`.

### Line 389
```python
    if not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not force`.

### Line 390
```python
        checkpoint = _load_checkpoint(tag)
```
**Plain English:** Store a value: the name `checkpoint` now holds the result of `_load_checkpoint(tag)`. Whenever you later write that name, you mean this value.

### Line 391
```python
        if len(checkpoint):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(checkpoint)`.

### Line 392
```python
            counts = checkpoint.groupby("experiment").size()
```
**Plain English:** Store a value: the name `counts` now holds the result of `checkpoint.groupby("experiment").size()`. Whenever you later write that name, you mean this value.

### Line 393
```python
            done = set(counts[counts >= expected].index)
```
**Plain English:** Store a value: the name `done` now holds the result of `set(counts[counts >= expected].index)`. Whenever you later write that name, you mean this value.

### Line 394
```python
    if done:
```
**Plain English:** Decision: run the indented block only when this condition is true → `done`.

### Line 395
```python
        print(f"Resuming {out.name}: {len(done)} experiment(s) complete "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"Resuming {out.name}: {len(done)} experiment(s) complete "`.

### Line 396
```python
              f"({expected} folds each)")
```
**Plain English:** Run this instruction: `f"({expected} folds each)")`.

### Line 398
```python
    for exp_label, fams in experiments:
```
**Plain English:** Loop: repeat the indented block once for each item → `exp_label, fams in experiments`.

### Line 399
```python
        if deadline and time.time() > deadline:
```
**Plain English:** Decision: run the indented block only when this condition is true → `deadline and time.time() > deadline`.

### Line 400
```python
            print("\n=== time budget reached; re-run the same call to continue")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n=== time budget reached; re-run the same call to continue")`.

### Line 401
```python
            break
```
**Plain English:** Leave the loop early.

### Line 402
```python
        need_main = exp_label not in done
```
**Plain English:** Store a value: the name `need_main` now holds the result of `exp_label not in done`. Whenever you later write that name, you mean this value.

### Line 403
```python
        need_perm = permute and bool(fams) and (exp_label + " (permuted)") not in done
```
**Plain English:** Store a value: the name `need_perm` now holds the result of `permute and bool(fams) and (exp_label + " (permuted)") not in done`. Whenever you later write that name, you mean this value.

### Line 404
```python
        if not need_main and not need_perm:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not need_main and not need_perm`.

### Line 405
```python
            print(f"\n=== {exp_label}: already in {out.name}, skipping")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\n=== {exp_label}: already in {out.name}, skipping")`.

### Line 406
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 407
```python
        print(f"\n=== {exp_label} " + "=" * max(0, 58 - len(exp_label)))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\n=== {exp_label} " + "=" * max(0, 58 - len(exp_label)))`.

### Line 408
```python
        X, y, names, ids, family_of = load_dataset(fams, verbose=True, label=label)
```
**Plain English:** Run this instruction: `X, y, names, ids, family_of = load_dataset(fams, verbose=True, label=label)`.

### Line 409
```python
        print(f"  matrix {X.shape[0]:,} x {X.shape[1]:,}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  matrix {X.shape[0]:,} x {X.shape[1]:,}")`.

### Line 411
```python
        groups = load_groups(ids, group_by) if group_by else None
```
**Plain English:** Store a value: the name `groups` now holds the result of `load_groups(ids, group_by) if group_by else None`. Whenever you later write that name, you mean this value.

### Line 412
```python
        if groups is not None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `groups is not None`.

### Line 413
```python
            print(f"  grouped CV by {group_by}: {len(set(groups)):,} groups")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  grouped CV by {group_by}: {len(set(groups)):,} groups")`.

### Line 415
```python
        if need_main:
```
**Plain English:** Decision: run the indented block only when this condition is true → `need_main`.

### Line 416
```python
            t0 = time.time()
```
**Plain English:** Store a value: the name `t0` now holds the result of `time.time()`. Whenever you later write that name, you mean this value.

### Line 417
```python
            res = cross_validate(X, y, names, family_of, n_features=n_features,
```
**Plain English:** Store a value: the name `res` now holds the result of `cross_validate(X, y, names, family_of, n_features=n_features,`. Whenever you later write that name, you mean this value.

### Line 418
```python
                                 seeds=seeds, n_splits=n_splits, groups=groups,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `seeds, n_splits=n_splits, groups=groups,`. Whenever you later write that name, you mean this value.

### Line 419
```python
                                 tag=tag, experiment=exp_label, deadline=deadline)
```
**Plain English:** Store a value: the name `tag` now holds the result of `tag, experiment=exp_label, deadline=deadline)`. Whenever you later write that name, you mean this value.

### Line 420
```python
            s = res["summary"]
```
**Plain English:** Store a value: the name `s` now holds the result of `res["summary"]`. Whenever you later write that name, you mean this value.

### Line 421
```python
            row = dict(
```
**Plain English:** Store a value: the name `row` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 422
```python
                experiment=exp_label,
```
**Plain English:** Store a value: the name `experiment` now holds the result of `exp_label,`. Whenever you later write that name, you mean this value.

### Line 423
```python
                n_columns=X.shape[1],
```
**Plain English:** Store a value: the name `n_columns` now holds the result of `X.shape[1],`. Whenever you later write that name, you mean this value.

### Line 424
```python
                r2=s["r2"]["mean"], r2_sd=s["r2"]["sd"],
```
**Plain English:** Store a value: the name `r2` now holds the result of `s["r2"]["mean"], r2_sd=s["r2"]["sd"],`. Whenever you later write that name, you mean this value.

### Line 425
```python
                spearman=s["spearman"]["mean"], spearman_sd=s["spearman"]["sd"],
```
**Plain English:** Store a value: the name `spearman` now holds the result of `s["spearman"]["mean"], spearman_sd=s["spearman"]["sd"],`. Whenever you later write that name, you mean this value.

### Line 426
```python
                pearson=s["pearson"]["mean"], mse=s["mse"]["mean"],
```
**Plain English:** Store a value: the name `pearson` now holds the result of `s["pearson"]["mean"], mse=s["mse"]["mean"],`. Whenever you later write that name, you mean this value.

### Line 427
```python
                selected_from_family=res["selected"]["engineered"],
```
**Plain English:** Store a value: the name `selected_from_family` now holds the result of `res["selected"]["engineered"],`. Whenever you later write that name, you mean this value.

### Line 428
```python
                folds_done=res["n_folds_done"],
```
**Plain English:** Store a value: the name `folds_done` now holds the result of `res["n_folds_done"],`. Whenever you later write that name, you mean this value.

### Line 429
```python
                complete=res["complete"],
```
**Plain English:** Store a value: the name `complete` now holds the result of `res["complete"],`. Whenever you later write that name, you mean this value.

### Line 430
```python
                seconds=round(time.time() - t0),
```
**Plain English:** Store a value: the name `seconds` now holds the result of `round(time.time() - t0),`. Whenever you later write that name, you mean this value.

### Line 431
```python
                permuted=False,
```
**Plain English:** Store a value: the name `permuted` now holds the result of `False,`. Whenever you later write that name, you mean this value.

### Line 432
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 433
```python
            if res["complete"]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `res["complete"]`.

### Line 434
```python
                rows = [r for r in rows if r.get("experiment") != exp_label]
```
**Plain English:** Store a value: the name `rows` now holds the result of `[r for r in rows if r.get("experiment") != exp_label]`. Whenever you later write that name, you mean this value.

### Line 435
```python
                rows.append(row)
```
**Plain English:** Run this instruction: `rows.append(row)`.

### Line 436
```python
            else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 437
```python
                print("    not recorded in the summary until all folds finish")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("    not recorded in the summary until all folds finish")`.

### Line 438
```python
            print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 439
```python
                f"  R2 {row['r2']:.4f} +/- {row['r2_sd']:.4f}   "
```
**Plain English:** Run this instruction: `f"  R2 {row['r2']:.4f} +/- {row['r2_sd']:.4f}   "`.

### Line 440
```python
                f"rho {row['spearman']:.4f} +/- {row['spearman_sd']:.4f}   "
```
**Plain English:** Run this instruction: `f"rho {row['spearman']:.4f} +/- {row['spearman_sd']:.4f}   "`.

### Line 441
```python
                f"({row['selected_from_family']:.1f} engineered columns in the top "
```
**Plain English:** Run this instruction: `f"({row['selected_from_family']:.1f} engineered columns in the top "`.

### Line 442
```python
                f"{n_features or config.N_FEATURES})"
```
**Plain English:** Run this instruction: `f"{n_features or config.N_FEATURES})"`.

### Line 443
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 445
```python
        if need_perm:
```
**Plain English:** Decision: run the indented block only when this condition is true → `need_perm`.

### Line 446
```python
            print(f"  permuted control for {exp_label} ...")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  permuted control for {exp_label} ...")`.

### Line 447
```python
            Xp = _permute_families(X, family_of, fams)
```
**Plain English:** Store a value: the name `Xp` now holds the result of `_permute_families(X, family_of, fams)`. Whenever you later write that name, you mean this value.

### Line 448
```python
            resp = cross_validate(Xp, y, names, family_of, n_features=n_features,
```
**Plain English:** Store a value: the name `resp` now holds the result of `cross_validate(Xp, y, names, family_of, n_features=n_features,`. Whenever you later write that name, you mean this value.

### Line 449
```python
                                  seeds=seeds, n_splits=n_splits, verbose=False,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `seeds, n_splits=n_splits, verbose=False,`. Whenever you later write that name, you mean this value.

### Line 450
```python
                                  groups=groups, tag=tag,
```
**Plain English:** Store a value: the name `groups` now holds the result of `groups, tag=tag,`. Whenever you later write that name, you mean this value.

### Line 451
```python
                                  experiment=exp_label + " (permuted)",
```
**Plain English:** Store a value: the name `experiment` now holds the result of `exp_label + " (permuted)",`. Whenever you later write that name, you mean this value.

### Line 452
```python
                                  deadline=deadline)
```
**Plain English:** Store a value: the name `deadline` now holds the result of `deadline)`. Whenever you later write that name, you mean this value.

### Line 453
```python
            sp = resp["summary"]
```
**Plain English:** Store a value: the name `sp` now holds the result of `resp["summary"]`. Whenever you later write that name, you mean this value.

### Line 454
```python
            rows = [r for r in rows
```
**Plain English:** Store a value: the name `rows` now holds the result of `[r for r in rows`. Whenever you later write that name, you mean this value.

### Line 455
```python
                    if r.get("experiment") != exp_label + " (permuted)"]
```
**Plain English:** Decision: run the indented block only when this condition is true → `r.get("experiment") != exp_label + " (permuted)"]`.

### Line 456
```python
            rows.append(
```
**Plain English:** Run this instruction: `rows.append(`.

### Line 457
```python
                dict(
```
**Plain English:** Run this instruction: `dict(`.

### Line 458
```python
                    experiment=exp_label + " (permuted)",
```
**Plain English:** Store a value: the name `experiment` now holds the result of `exp_label + " (permuted)",`. Whenever you later write that name, you mean this value.

### Line 459
```python
                    n_columns=X.shape[1],
```
**Plain English:** Store a value: the name `n_columns` now holds the result of `X.shape[1],`. Whenever you later write that name, you mean this value.

### Line 460
```python
                    r2=sp["r2"]["mean"], r2_sd=sp["r2"]["sd"],
```
**Plain English:** Store a value: the name `r2` now holds the result of `sp["r2"]["mean"], r2_sd=sp["r2"]["sd"],`. Whenever you later write that name, you mean this value.

### Line 461
```python
                    spearman=sp["spearman"]["mean"],
```
**Plain English:** Store a value: the name `spearman` now holds the result of `sp["spearman"]["mean"],`. Whenever you later write that name, you mean this value.

### Line 462
```python
                    spearman_sd=sp["spearman"]["sd"],
```
**Plain English:** Store a value: the name `spearman_sd` now holds the result of `sp["spearman"]["sd"],`. Whenever you later write that name, you mean this value.

### Line 463
```python
                    pearson=sp["pearson"]["mean"], mse=sp["mse"]["mean"],
```
**Plain English:** Store a value: the name `pearson` now holds the result of `sp["pearson"]["mean"], mse=sp["mse"]["mean"],`. Whenever you later write that name, you mean this value.

### Line 464
```python
                    selected_from_family=resp["selected"]["engineered"],
```
**Plain English:** Store a value: the name `selected_from_family` now holds the result of `resp["selected"]["engineered"],`. Whenever you later write that name, you mean this value.

### Line 465
```python
                    folds_done=resp["n_folds_done"],
```
**Plain English:** Store a value: the name `folds_done` now holds the result of `resp["n_folds_done"],`. Whenever you later write that name, you mean this value.

### Line 466
```python
                    complete=resp["complete"],
```
**Plain English:** Store a value: the name `complete` now holds the result of `resp["complete"],`. Whenever you later write that name, you mean this value.

### Line 467
```python
                    seconds=0, permuted=True,
```
**Plain English:** Store a value: the name `seconds` now holds the result of `0, permuted=True,`. Whenever you later write that name, you mean this value.

### Line 468
```python
                )
```
**Plain English:** Run this instruction: `)`.

### Line 469
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 470
```python
            if not resp["complete"]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not resp["complete"]`.

### Line 471
```python
                rows = [r for r in rows
```
**Plain English:** Store a value: the name `rows` now holds the result of `[r for r in rows`. Whenever you later write that name, you mean this value.

### Line 472
```python
                        if r.get("experiment") != exp_label + " (permuted)"]
```
**Plain English:** Decision: run the indented block only when this condition is true → `r.get("experiment") != exp_label + " (permuted)"]`.

### Line 473
```python
                print("    permuted control incomplete; re-run to finish it")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("    permuted control incomplete; re-run to finish it")`.

### Line 474
```python
            print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 475
```python
                f"  permuted: R2 {sp['r2']['mean']:.4f}   "
```
**Plain English:** Run this instruction: `f"  permuted: R2 {sp['r2']['mean']:.4f}   "`.

### Line 476
```python
                f"rho {sp['spearman']['mean']:.4f}"
```
**Plain English:** Run this instruction: `f"rho {sp['spearman']['mean']:.4f}"`.

### Line 477
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 479
```python
    table = pd.DataFrame(rows)
```
**Plain English:** Store a value: the name `table` now holds the result of `pd.DataFrame(rows)`. Whenever you later write that name, you mean this value.

### Line 480
```python
    if "baseline" in set(table["experiment"]):
```
**Plain English:** Decision: run the indented block only when this condition is true → `"baseline" in set(table["experiment"])`.

### Line 481
```python
        base = table.loc[table["experiment"] == "baseline"].iloc[0]
```
**Plain English:** Store a value: the name `base` now holds the result of `table.loc[table["experiment"] == "baseline"].iloc[0]`. Whenever you later write that name, you mean this value.

### Line 482
```python
        table["d_r2"] = table["r2"] - base["r2"]
```
**Plain English:** Store a value: the name `table["d_r2"]` now holds the result of `table["r2"] - base["r2"]`. Whenever you later write that name, you mean this value.

### Line 483
```python
        table["d_spearman"] = table["spearman"] - base["spearman"]
```
**Plain English:** Δ Spearman vs the baseline arm in the same run — the number that decides if a family helped.

### Line 484
```python
    else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 485
```python
        table["d_r2"] = np.nan
```
**Plain English:** Store a value: the name `table["d_r2"]` now holds the result of `np.nan`. Whenever you later write that name, you mean this value.

### Line 486
```python
        table["d_spearman"] = np.nan
```
**Plain English:** Δ Spearman vs the baseline arm in the same run — the number that decides if a family helped.

### Line 488
```python
    table.to_csv(out, index=False)
```
**Plain English:** Run this instruction: `table.to_csv(out, index=False)`.

### Line 489
```python
    (config.RESULTS / f"ablation_{tag}_settings.json").write_text(
```
**Plain English:** Run this instruction: `(config.RESULTS / f"ablation_{tag}_settings.json").write_text(`.

### Line 490
```python
        json.dumps(
```
**Plain English:** Run this instruction: `json.dumps(`.

### Line 491
```python
            dict(
```
**Plain English:** Run this instruction: `dict(`.

### Line 492
```python
                families=list(families), together=together, permute=permute,
```
**Plain English:** Store a value: the name `families` now holds the result of `list(families), together=together, permute=permute,`. Whenever you later write that name, you mean this value.

### Line 493
```python
                n_features=n_features or config.N_FEATURES,
```
**Plain English:** Store a value: the name `n_features` now holds the result of `n_features or config.N_FEATURES,`. Whenever you later write that name, you mean this value.

### Line 494
```python
                seeds=list(seeds or config.SEEDS),
```
**Plain English:** Store a value: the name `seeds` now holds the result of `list(seeds or config.SEEDS),`. Whenever you later write that name, you mean this value.

### Line 495
```python
                n_splits=n_splits or config.N_SPLITS,
```
**Plain English:** Store a value: the name `n_splits` now holds the result of `n_splits or config.N_SPLITS,`. Whenever you later write that name, you mean this value.

### Line 496
```python
                group_by=group_by,
```
**Plain English:** Store a value: the name `group_by` now holds the result of `group_by,`. Whenever you later write that name, you mean this value.

### Line 497
```python
                label=label,
```
**Plain English:** Store a value: the name `label` now holds the result of `label,`. Whenever you later write that name, you mean this value.

### Line 498
```python
                frozen_baseline=config.BASELINE,
```
**Plain English:** Store a value: the name `frozen_baseline` now holds the result of `config.BASELINE,`. Whenever you later write that name, you mean this value.

### Line 499
```python
            ),
```
**Plain English:** Run this instruction: `),`.

### Line 500
```python
            indent=1,
```
**Plain English:** Store a value: the name `indent` now holds the result of `1,`. Whenever you later write that name, you mean this value.

### Line 501
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 502
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 504
```python
    print("\n" + "=" * 70)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\n" + "=" * 70)`.

### Line 505
```python
    cols = ["experiment", "n_columns", "r2", "d_r2", "spearman", "d_spearman",
```
**Plain English:** Δ Spearman vs the baseline arm in the same run — the number that decides if a family helped.

### Line 506
```python
            "selected_from_family"]
```
**Plain English:** Run this instruction: `"selected_from_family"]`.

### Line 507
```python
    print(table[cols].to_string(index=False, float_format=lambda v: f"{v:9.4f}"))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(table[cols].to_string(index=False, float_format=lambda v: f"{v:9.4f}"))`.

### Line 508
```python
    print(f"\nWrote {out}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\nWrote {out}")`.

### Line 509
```python
    print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 510
```python
        f"Frozen reference: R2 {config.BASELINE['r2']:.4f}, "
```
**Plain English:** Run this instruction: `f"Frozen reference: R2 {config.BASELINE['r2']:.4f}, "`.

### Line 511
```python
        f"rho {config.BASELINE['spearman']:.4f}"
```
**Plain English:** Run this instruction: `f"rho {config.BASELINE['spearman']:.4f}"`.

### Line 512
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 513
```python
    return table
```
**Plain English:** Finish this function and send back: `table`.

### Line 516
```python
def main(argv=None) -> int:
```
**Plain English:** Defines a reusable recipe named `main`. Inputs in parentheses: `argv=None`. Returns type hint: int. Nothing runs yet until something *calls* `main(...)`.

### Line 517
```python
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
```
**Plain English:** Store a value: the name `ap` now holds the result of `argparse.ArgumentParser(description=__doc__.split("\n")[0])`. Whenever you later write that name, you mean this value.

### Line 518
```python
    ap.add_argument("--families", nargs="*", default=[], choices=ALL)
```
**Plain English:** Run this instruction: `ap.add_argument("--families", nargs="*", default=[], choices=ALL)`.

### Line 519
```python
    ap.add_argument("--together", action="store_true",
```
**Plain English:** Run this instruction: `ap.add_argument("--together", action="store_true",`.

### Line 520
```python
                    help="stack the families instead of testing each alone")
```
**Plain English:** Store a value: the name `help` now holds the result of `"stack the families instead of testing each alone")`. Whenever you later write that name, you mean this value.

### Line 521
```python
    ap.add_argument("--permute", action="store_true",
```
**Plain English:** Run this instruction: `ap.add_argument("--permute", action="store_true",`.

### Line 522
```python
                    help="also run a row-shuffled control for each family")
```
**Plain English:** Store a value: the name `help` now holds the result of `"also run a row-shuffled control for each family")`. Whenever you later write that name, you mean this value.

### Line 523
```python
    ap.add_argument("--baseline-only", action="store_true")
```
**Plain English:** Run this instruction: `ap.add_argument("--baseline-only", action="store_true")`.

### Line 524
```python
    ap.add_argument("--n-features", type=int, default=None)
```
**Plain English:** Run this instruction: `ap.add_argument("--n-features", type=int, default=None)`.

### Line 525
```python
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
```
**Plain English:** Run this instruction: `ap.add_argument("--seeds", type=int, nargs="*", default=None)`.

### Line 526
```python
    ap.add_argument("--folds", type=int, default=None)
```
**Plain English:** Run this instruction: `ap.add_argument("--folds", type=int, default=None)`.

### Line 527
```python
    ap.add_argument("--tag", default=None,
```
**Plain English:** Run this instruction: `ap.add_argument("--tag", default=None,`.

### Line 528
```python
                    help="results/ablation_<tag>.csv; reruns append to it")
```
**Plain English:** Store a value: the name `help` now holds the result of `"results/ablation_<tag>.csv; reruns append to it")`. Whenever you later write that name, you mean this value.

### Line 529
```python
    ap.add_argument("--force", action="store_true",
```
**Plain English:** Run this instruction: `ap.add_argument("--force", action="store_true",`.

### Line 530
```python
                    help="recompute experiments already in the results file")
```
**Plain English:** Store a value: the name `help` now holds the result of `"recompute experiments already in the results file")`. Whenever you later write that name, you mean this value.

### Line 531
```python
    ap.add_argument("--label", default=None,
```
**Plain English:** Run this instruction: `ap.add_argument("--label", default=None,`.

### Line 532
```python
                    help="use an alternative target from data/interim/labels/")
```
**Plain English:** Store a value: the name `help` now holds the result of `"use an alternative target from data/interim/labels/")`. Whenever you later write that name, you mean this value.

### Line 533
```python
    ap.add_argument("--time-budget", type=float, default=None,
```
**Plain English:** Run this instruction: `ap.add_argument("--time-budget", type=float, default=None,`.

### Line 534
```python
                    help="stop cleanly after this many seconds; re-run to resume")
```
**Plain English:** Store a value: the name `help` now holds the result of `"stop cleanly after this many seconds; re-run to resume")`. Whenever you later write that name, you mean this value.

### Line 535
```python
    ap.add_argument("--group", dest="group_by", choices=list(GROUP_CHOICES),
```
**Plain English:** Run this instruction: `ap.add_argument("--group", dest="group_by", choices=list(GROUP_CHOICES),`.

### Line 536
```python
                    default=None,
```
**Plain English:** Store a value: the name `default` now holds the result of `None,`. Whenever you later write that name, you mean this value.

### Line 537
```python
                    help="hold out whole genes (or 5 kb bins) instead of rows -- "
```
**Plain English:** Store a value: the name `help` now holds the result of `"hold out whole genes (or 5 kb bins) instead of rows -- "`. Whenever you later write that name, you mean this value.

### Line 538
```python
                         "required before believing any positional family")
```
**Plain English:** Run this instruction: `"required before believing any positional family")`.

### Line 539
```python
    args = ap.parse_args(argv)
```
**Plain English:** Store a value: the name `args` now holds the result of `ap.parse_args(argv)`. Whenever you later write that name, you mean this value.

### Line 541
```python
    families = [] if args.baseline_only else args.families
```
**Plain English:** Store a value: the name `families` now holds the result of `[] if args.baseline_only else args.families`. Whenever you later write that name, you mean this value.

### Line 542
```python
    run(
```
**Plain English:** Run this instruction: `run(`.

### Line 543
```python
        families,
```
**Plain English:** Run this instruction: `families,`.

### Line 544
```python
        together=args.together,
```
**Plain English:** Store a value: the name `together` now holds the result of `args.together,`. Whenever you later write that name, you mean this value.

### Line 545
```python
        permute=args.permute,
```
**Plain English:** Store a value: the name `permute` now holds the result of `args.permute,`. Whenever you later write that name, you mean this value.

### Line 546
```python
        n_features=args.n_features,
```
**Plain English:** Store a value: the name `n_features` now holds the result of `args.n_features,`. Whenever you later write that name, you mean this value.

### Line 547
```python
        seeds=tuple(args.seeds) if args.seeds else None,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `tuple(args.seeds) if args.seeds else None,`. Whenever you later write that name, you mean this value.

### Line 548
```python
        n_splits=args.folds,
```
**Plain English:** Store a value: the name `n_splits` now holds the result of `args.folds,`. Whenever you later write that name, you mean this value.

### Line 549
```python
        tag=args.tag,
```
**Plain English:** Store a value: the name `tag` now holds the result of `args.tag,`. Whenever you later write that name, you mean this value.

### Line 550
```python
        force=args.force,
```
**Plain English:** Store a value: the name `force` now holds the result of `args.force,`. Whenever you later write that name, you mean this value.

### Line 551
```python
        group_by=args.group_by,
```
**Plain English:** Store a value: the name `group_by` now holds the result of `args.group_by,`. Whenever you later write that name, you mean this value.

### Line 552
```python
        time_budget=args.time_budget,
```
**Plain English:** Store a value: the name `time_budget` now holds the result of `args.time_budget,`. Whenever you later write that name, you mean this value.

### Line 553
```python
        label=args.label,
```
**Plain English:** Store a value: the name `label` now holds the result of `args.label,`. Whenever you later write that name, you mean this value.

### Line 554
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 555
```python
    return 0
```
**Plain English:** Finish this function and send back: `0`.

### Line 558
```python
if __name__ == "__main__":
```
**Plain English:** Special gate: this block runs only when you execute *this file directly* (not when another file imports it). Common pattern for scripts.

### Line 559
```python
    sys.exit(main())
```
**Plain English:** Run this instruction: `sys.exit(main())`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### Same exam protocol as the baseline
`cross_validate` is CELL 5 of the baseline, packaged as a function: impute → select 300 → fit champion → score.

### Grouped CV
Guides in the same gene share a neighbourhood. Random folds put the same neighbourhood in train *and* val → positional features cheat.  
Grouping holds out whole genes/blocks.

### Permutation floor
Shuffle Family A’s rows (destroy guide↔feature links) and re-run. If real Δρ ≈ permuted Δρ, Family A didn’t help — you only fitted noise.
