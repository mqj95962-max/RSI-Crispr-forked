# P0 line-by-line: `Runjia/sgrna/io_utils.py`
**Why this file matters:** Rules for reading the big spreadsheet and saving feature-family tables.
**Length:** 87 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Think of this as the librarian rules: how to check out the big book and how to shelve new chapters.

---
### Lines 1–7
```python
"""Shared conventions for reading the base matrix and writing feature blocks.

A *feature block* is one CSV per family in `data/interim/features/`, keyed by
sgRNAID, whose other columns all start with `eng.`. Blocks are built
independently and joined only at the last moment, so a family can be rebuilt
or dropped without touching anything else.
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 9
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 11
```python
from pathlib import Path
```
**Plain English:** Load toolbox code: `from pathlib import Path` — used here for **friendly file-path objects**.

### Line 13
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 15
```python
from . import config
```
**Plain English:** Load a project module from this repo: `from . import config`.

### Line 18
```python
def block_path(family: str) -> Path:
```
**Plain English:** Defines a reusable recipe named `block_path`. Inputs in parentheses: `family: str`. Returns type hint: Path. Nothing runs yet until something *calls* `block_path(...)`.

### Line 19
```python
    return config.FEATURE_DIR / f"{family}.csv"
```
**Plain English:** Finish this function and send back: `config.FEATURE_DIR / f"{family}.csv"`.

### Line 22
```python
def save_block(df: pd.DataFrame, family: str) -> Path:
```
**Plain English:** Defines a reusable recipe named `save_block`. Inputs in parentheses: `df: pd.DataFrame, family: str`. Returns type hint: Path. Nothing runs yet until something *calls* `save_block(...)`.

### Line 23
```python
    """Write a feature block after checking the naming conventions hold."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Write a feature block after checking the naming conventions hold.

### Line 24
```python
    if config.ID_COL not in df.columns:
```
**Plain English:** Decision: run the indented block only when this condition is true → `config.ID_COL not in df.columns`.

### Line 25
```python
        raise ValueError(f"Feature block '{family}' has no {config.ID_COL} column.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"Feature block '{family}' has no {config.ID_COL} column.")`.

### Line 26
```python
    bad = [
```
**Plain English:** Store a value: the name `bad` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 27
```python
        c
```
**Plain English:** Run this instruction: `c`.

### Line 28
```python
        for c in df.columns
```
**Plain English:** Loop: repeat the indented block once for each item → `c in df.columns`.

### Line 29
```python
        if c != config.ID_COL and not c.startswith("eng.")
```
**Plain English:** Decision: run the indented block only when this condition is true → `c != config.ID_COL and not c.startswith("eng.")`.

### Line 30
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 31
```python
    if bad:
```
**Plain English:** Decision: run the indented block only when this condition is true → `bad`.

### Line 32
```python
        raise ValueError(
```
**Plain English:** Stop and report a problem on purpose → `ValueError(`.

### Line 33
```python
            f"Feature block '{family}' has columns that do not start with 'eng.': "
```
**Plain English:** Run this instruction: `f"Feature block '{family}' has columns that do not start with 'eng.': "`.

### Line 34
```python
            f"{bad[:8]}"
```
**Plain English:** Run this instruction: `f"{bad[:8]}"`.

### Line 35
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 36
```python
    if df[config.ID_COL].duplicated().any():
```
**Plain English:** Decision: run the indented block only when this condition is true → `df[config.ID_COL].duplicated().any()`.

### Line 37
```python
        raise ValueError(f"Feature block '{family}' has duplicate sgRNAIDs.")
```
**Plain English:** Stop and report a problem on purpose → `ValueError(f"Feature block '{family}' has duplicate sgRNAIDs.")`.

### Line 39
```python
    path = block_path(family)
```
**Plain English:** Store a value: the name `path` now holds the result of `block_path(family)`. Whenever you later write that name, you mean this value.

### Line 40
```python
    df.to_csv(path, index=False)
```
**Plain English:** Run this instruction: `df.to_csv(path, index=False)`.

### Line 41
```python
    return path
```
**Plain English:** Finish this function and send back: `path`.

### Line 44
```python
def load_block(family: str) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `load_block`. Inputs in parentheses: `family: str`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `load_block(...)`.

### Line 45
```python
    path = block_path(family)
```
**Plain English:** Store a value: the name `path` now holds the result of `block_path(family)`. Whenever you later write that name, you mean this value.

### Line 46
```python
    if not path.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not path.exists()`.

### Line 47
```python
        raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 48
```python
            f"No feature block for '{family}'. Build it with "
```
**Plain English:** Run this instruction: `f"No feature block for '{family}'. Build it with "`.

### Line 49
```python
            f"`python -m sgrna.build_features --families {family}`."
```
**Plain English:** Run this instruction: `f"`python -m sgrna.build_features --families {family}`."`.

### Line 50
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 51
```python
    return pd.read_csv(path, low_memory=False)
```
**Plain English:** Finish this function and send back: `pd.read_csv(path, low_memory=False)`.

### Line 54
```python
def available_blocks() -> list[str]:
```
**Plain English:** Defines a reusable recipe named `available_blocks`. Inputs in parentheses: `(none)`. Returns type hint: list[str]. Nothing runs yet until something *calls* `available_blocks(...)`.

### Line 55
```python
    return sorted(p.stem for p in config.FEATURE_DIR.glob("*.csv"))
```
**Plain English:** Finish this function and send back: `sorted(p.stem for p in config.FEATURE_DIR.glob("*.csv"))`.

### Line 58
```python
def load_guide_index() -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `load_guide_index`. Inputs in parentheses: `(none)`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `load_guide_index(...)`.

### Line 59
```python
    if not config.GUIDE_INDEX.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not config.GUIDE_INDEX.exists()`.

### Line 60
```python
        raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 61
```python
            f"{config.GUIDE_INDEX} not found -- run "
```
**Plain English:** Run this instruction: `f"{config.GUIDE_INDEX} not found -- run "`.

### Line 62
```python
            "`python -m sgrna.build_guide_index` first."
```
**Plain English:** Run this instruction: `"`python -m sgrna.build_guide_index` first."`.

### Line 63
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 64
```python
    return pd.read_csv(config.GUIDE_INDEX, low_memory=False)
```
**Plain English:** Finish this function and send back: `pd.read_csv(config.GUIDE_INDEX, low_memory=False)`.

### Line 67
```python
def load_base_matrix(usecols=None, nrows=None) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `load_base_matrix`. Inputs in parentheses: `usecols=None, nrows=None`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `load_base_matrix(...)`.

### Line 68
```python
    """Read the published matrix, skipping its title row."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Read the published matrix, skipping its title row.

### Line 69
```python
    return pd.read_csv(
```
**Plain English:** Finish this function and send back: `pd.read_csv(`.

### Line 70
```python
        config.BASE_MATRIX,
```
**Plain English:** Run this instruction: `config.BASE_MATRIX,`.

### Line 71
```python
        header=config.BASE_MATRIX_HEADER_ROW,
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 72
```python
        usecols=usecols,
```
**Plain English:** Store a value: the name `usecols` now holds the result of `usecols,`. Whenever you later write that name, you mean this value.

### Line 73
```python
        nrows=nrows,
```
**Plain English:** Store a value: the name `nrows` now holds the result of `nrows,`. Whenever you later write that name, you mean this value.

### Line 74
```python
        low_memory=False,
```
**Plain English:** Store a value: the name `low_memory` now holds the result of `False,`. Whenever you later write that name, you mean this value.

### Line 75
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 78
```python
def base_matrix_columns() -> list[str]:
```
**Plain English:** Defines a reusable recipe named `base_matrix_columns`. Inputs in parentheses: `(none)`. Returns type hint: list[str]. Nothing runs yet until something *calls* `base_matrix_columns(...)`.

### Line 79
```python
    return list(load_base_matrix(nrows=0).columns)
```
**Plain English:** Finish this function and send back: `list(load_base_matrix(nrows=0).columns)`.

### Line 82
```python
def one_hot(values: pd.Series, prefix: str, categories) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `one_hot`. Inputs in parentheses: `values: pd.Series, prefix: str, categories`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `one_hot(...)`.

### Line 83
```python
    """Deterministic one-hot encoding: always the same columns, in order."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Deterministic one-hot encoding: always the same columns, in order.

### Line 84
```python
    out = {}
```
**Plain English:** Store a value: the name `out` now holds the result of `{}`. Whenever you later write that name, you mean this value.

### Line 85
```python
    for cat in categories:
```
**Plain English:** Loop: repeat the indented block once for each item → `cat in categories`.

### Line 86
```python
        out[f"{prefix}.{cat}"] = (values == cat).astype("int8")
```
**Plain English:** Run this instruction: `out[f"{prefix}.{cat}"] = (values == cat).astype("int8")`.

### Line 87
```python
    return pd.DataFrame(out, index=values.index)
```
**Plain English:** Finish this function and send back: `pd.DataFrame(out, index=values.index)`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### What is a “feature block”?
A small CSV with:
- one ID column `sgRNAID`
- many columns all named `eng....`  
Each biology family (A, B, C…) writes its own block. Later, `build_matrix` joins them.  
That way you can rebuild Family A without touching Family G.
