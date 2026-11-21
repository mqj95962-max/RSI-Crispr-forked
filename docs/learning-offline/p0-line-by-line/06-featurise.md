# P0 line-by-line: `Runjia/sgrna/build/featurise.py`
**Why this file matters:** Rebuild ~6,169 published feature columns from a 20-letter DNA spacer alone.
**Length:** 125 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Given only 20 DNA letters, rebuild almost the entire published feature spreadsheet the same way every time.

---
### Lines 1–34
```python
"""Generate the published feature representation for guides outside the matrix.

Why this exists
---------------
The project was capped at 13,880 rows because that is how many guides Noshay
et al. published features for. Two pieces of reverse engineering lift the cap:

  * `qct.learn_lookup_tables` recovers the 316 quantum tensor columns as exact
    k-mer -> value tables (all 4/16/64/256 k-mers present, no conflicts);
  * `decode_v_columns` identifies 5,853 of the 5,887 `V####` columns as
    (position, k-mer) one-hot indicators, verified at 100% on 1.17 million
    rebuilt values.

Together that is 6,169 of 6,232 columns -- 99.0% of the published matrix --
regenerable from a 20 nt protospacer alone.

What is deliberately left out
-----------------------------
The ~31 hand-named columns (`AAsgRNA.raw`, `sgRNA.gcsgRNA.raw`, `PAM.C0`,
`pam.distance0`, ...) are **not** pure functions of the protospacer: the base
counts disagree with a direct count by up to 13, `sgRNA.temp` takes exactly 14
distinct values spaced 2.05 apart, and the PAM columns take fractions like
0.25 and 0.4. They have been discretised or aggregated somewhere upstream in a
way the published matrix does not document. Rather than guess, this module
omits them, along with the 34 V columns that could not be identified.

That matters for how you use the output: **featurise everything the same way.**
Do not mix rows from the published CSV with rows built here -- rebuild the old
rows through this module too, so every row has the same 6,169 columns computed
by the same code. `build_expanded_dataset` does exactly that.

    from sgrna.build import featurise
    X, names = featurise.matrix(["ACGT...", "TTGC..."])
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 36
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 38
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 39
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 41
```python
from .. import config
```
**Plain English:** Load a project module from this repo: `from .. import config`.

### Line 42
```python
from . import qct
```
**Plain English:** Load a project module from this repo: `from . import qct`.

### Line 43
```python
from .decode_v_columns import UNITS, SPACER_LENGTH
```
**Plain English:** Load an external or local module: `from .decode_v_columns import UNITS, SPACER_LENGTH`.

### Line 44
```python
from .decode_v_columns import load as load_v_mapping
```
**Plain English:** Load an external or local module: `from .decode_v_columns import load as load_v_mapping`.

### Line 47
```python
def feature_names(v_mapping: dict | None = None, tables: dict | None = None):
```
**Plain English:** Defines a reusable recipe named `feature_names`. Inputs in parentheses: `v_mapping: dict | None = None, tables: dict | None = None`. Nothing runs yet until something *calls* `feature_names(...)`.

### Line 48
```python
    """Ordered column names: the identified V columns, then the QCT columns."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Ordered column names: the identified V columns, then the QCT columns.

### Line 49
```python
    v_mapping = v_mapping or load_v_mapping()
```
**Plain English:** Store a value: the name `v_mapping` now holds the result of `v_mapping or load_v_mapping()`. Whenever you later write that name, you mean this value.

### Line 50
```python
    tables = tables or qct.load_tables()
```
**Plain English:** Store a value: the name `tables` now holds the result of `tables or qct.load_tables()`. Whenever you later write that name, you mean this value.

### Line 52
```python
    v_names = sorted(v_mapping["mapping"])
```
**Plain English:** Store a value: the name `v_names` now holds the result of `sorted(v_mapping["mapping"])`. Whenever you later write that name, you mean this value.

### Line 53
```python
    qct_names = []
```
**Plain English:** Store a value: the name `qct_names` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 54
```python
    for unit, props in sorted(tables.items()):
```
**Plain English:** Loop: repeat the indented block once for each item → `unit, props in sorted(tables.items())`.

### Line 55
```python
        span = qct.UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `qct.UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 56
```python
        for prop in sorted(props):
```
**Plain English:** Loop: repeat the indented block once for each item → `prop in sorted(props)`.

### Line 57
```python
            for pos in range(1, SPACER_LENGTH - span + 2):
```
**Plain English:** Loop: repeat the indented block once for each item → `pos in range(1, SPACER_LENGTH - span + 2)`.

### Line 58
```python
                qct_names.append(f"p{pos}{unit}.{prop}")
```
**Plain English:** Run this instruction: `qct_names.append(f"p{pos}{unit}.{prop}")`.

### Line 59
```python
    return v_names, qct_names
```
**Plain English:** Finish this function and send back: `v_names, qct_names`.

### Line 62
```python
def matrix(protospacers, v_mapping: dict | None = None,
```
**Plain English:** Run this instruction: `def matrix(protospacers, v_mapping: dict | None = None,`.

### Line 63
```python
           tables: dict | None = None, verbose: bool = True):
```
**Plain English:** Run this instruction: `tables: dict | None = None, verbose: bool = True):`.

### Line 64
```python
    """(n, 6169) float32 matrix for a list of 20 nt protospacers."""
```
**Plain English:** A short documentation string attached to the nearest function/module: (n, 6169) float32 matrix for a list of 20 nt protospacers.

### Line 65
```python
    v_mapping = v_mapping or load_v_mapping()
```
**Plain English:** Store a value: the name `v_mapping` now holds the result of `v_mapping or load_v_mapping()`. Whenever you later write that name, you mean this value.

### Line 66
```python
    tables = tables or qct.load_tables()
```
**Plain English:** Store a value: the name `tables` now holds the result of `tables or qct.load_tables()`. Whenever you later write that name, you mean this value.

### Line 67
```python
    v_names, qct_names = feature_names(v_mapping, tables)
```
**Plain English:** Run this instruction: `v_names, qct_names = feature_names(v_mapping, tables)`.

### Line 69
```python
    seqs = np.asarray([str(s).upper() for s in protospacers])
```
**Plain English:** Store a value: the name `seqs` now holds the result of `np.asarray([str(s).upper() for s in protospacers])`. Whenever you later write that name, you mean this value.

### Line 70
```python
    n = len(seqs)
```
**Plain English:** Store a value: the name `n` now holds the result of `len(seqs)`. Whenever you later write that name, you mean this value.

### Line 72
```python
    # ---- V columns: (position, k-mer) indicators ------------------------
```
**Plain English:** Human-only note (Python ignores it): ---- V columns: (position, k-mer) indicators ------------------------

### Line 73
```python
    V = np.zeros((n, len(v_names)), dtype=np.float32)
```
**Plain English:** Store a value: the name `V` now holds the result of `np.zeros((n, len(v_names)), dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 74
```python
    windows: dict[tuple[str, int], np.ndarray] = {}
```
**Plain English:** Run this instruction: `windows: dict[tuple[str, int], np.ndarray] = {}`.

### Line 75
```python
    for j, name in enumerate(v_names):
```
**Plain English:** Loop: repeat the indented block once for each item → `j, name in enumerate(v_names)`.

### Line 76
```python
        spec = v_mapping["mapping"][name]
```
**Plain English:** Store a value: the name `spec` now holds the result of `v_mapping["mapping"][name]`. Whenever you later write that name, you mean this value.

### Line 77
```python
        k = UNITS[spec["unit"]]
```
**Plain English:** Store a value: the name `k` now holds the result of `UNITS[spec["unit"]]`. Whenever you later write that name, you mean this value.

### Line 78
```python
        pos = spec["position"]
```
**Plain English:** Store a value: the name `pos` now holds the result of `spec["position"]`. Whenever you later write that name, you mean this value.

### Line 79
```python
        key = (spec["unit"], pos)
```
**Plain English:** Store a value: the name `key` now holds the result of `(spec["unit"], pos)`. Whenever you later write that name, you mean this value.

### Line 80
```python
        if key not in windows:
```
**Plain English:** Decision: run the indented block only when this condition is true → `key not in windows`.

### Line 81
```python
            windows[key] = np.array([s[pos - 1 : pos - 1 + k] for s in seqs])
```
**Plain English:** Store a value: the name `windows[key]` now holds the result of `np.array([s[pos - 1 : pos - 1 + k] for s in seqs])`. Whenever you later write that name, you mean this value.

### Line 82
```python
        V[:, j] = (windows[key] == spec["kmer"]).astype(np.float32)
```
**Plain English:** One-hot style: 1 if this guide’s DNA snippet at that position equals the column’s k-mer, else 0.

### Line 83
```python
    if verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose`.

### Line 84
```python
        print(f"  V columns: {V.shape[1]:,}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  V columns: {V.shape[1]:,}")`.

### Line 86
```python
    # ---- QCT columns: k-mer -> published tensor value -------------------
```
**Plain English:** Human-only note (Python ignores it): ---- QCT columns: k-mer -> published tensor value -------------------

### Line 87
```python
    Q = np.full((n, len(qct_names)), np.nan, dtype=np.float32)
```
**Plain English:** Store a value: the name `Q` now holds the result of `np.full((n, len(qct_names)), np.nan, dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 88
```python
    for j, name in enumerate(qct_names):
```
**Plain English:** Loop: repeat the indented block once for each item → `j, name in enumerate(qct_names)`.

### Line 89
```python
        pos, unit, prop = qct.parse_qct_column(name)
```
**Plain English:** Run this instruction: `pos, unit, prop = qct.parse_qct_column(name)`.

### Line 90
```python
        span = qct.UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `qct.UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 91
```python
        table = tables[unit][prop]
```
**Plain English:** Store a value: the name `table` now holds the result of `tables[unit][prop]`. Whenever you later write that name, you mean this value.

### Line 92
```python
        kmers = windows.get((unit, pos))
```
**Plain English:** Store a value: the name `kmers` now holds the result of `windows.get((unit, pos))`. Whenever you later write that name, you mean this value.

### Line 93
```python
        if kmers is None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `kmers is None`.

### Line 94
```python
            kmers = np.array([s[pos - 1 : pos - 1 + span] for s in seqs])
```
**Plain English:** Store a value: the name `kmers` now holds the result of `np.array([s[pos - 1 : pos - 1 + span] for s in seqs])`. Whenever you later write that name, you mean this value.

### Line 95
```python
        Q[:, j] = [table.get(km, np.nan) for km in kmers]
```
**Plain English:** Run this instruction: `Q[:, j] = [table.get(km, np.nan) for km in kmers]`.

### Line 96
```python
    if verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose`.

### Line 97
```python
        print(f"  QCT columns: {Q.shape[1]:,}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  QCT columns: {Q.shape[1]:,}")`.

### Line 99
```python
    return np.hstack([V, Q]), v_names + qct_names
```
**Plain English:** Finish this function and send back: `np.hstack([V, Q]), v_names + qct_names`.

### Line 102
```python
def verify_against_published(n: int = 500, verbose: bool = True) -> dict:
```
**Plain English:** Defines a reusable recipe named `verify_against_published`. Inputs in parentheses: `n: int = 500, verbose: bool = True`. Returns type hint: dict. Nothing runs yet until something *calls* `verify_against_published(...)`.

### Line 103
```python
    """Rebuild the published matrix for real guides and compare, cell by cell."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Rebuild the published matrix for real guides and compare, cell by cell.

### Line 104
```python
    from .build_matrix import build_cache
```
**Plain English:** Load an external or local module: `from .build_matrix import build_cache`.

### Line 105
```python
    from ..io_utils import load_guide_index
```
**Plain English:** Load an external or local module: `from ..io_utils import load_guide_index`.

### Line 107
```python
    X, meta = build_cache(verbose=False)
```
**Plain English:** Run this instruction: `X, meta = build_cache(verbose=False)`.

### Line 108
```python
    names = meta["feature_names"]
```
**Plain English:** Store a value: the name `names` now holds the result of `meta["feature_names"]`. Whenever you later write that name, you mean this value.

### Line 109
```python
    ids = meta["ids"]
```
**Plain English:** Store a value: the name `ids` now holds the result of `meta["ids"]`. Whenever you later write that name, you mean this value.

### Line 110
```python
    idx = load_guide_index().set_index(config.ID_COL).reindex(ids)
```
**Plain English:** Store a value: the name `idx` now holds the result of `load_guide_index().set_index(config.ID_COL).reindex(ids)`. Whenever you later write that name, you mean this value.

### Line 111
```python
    seqs = idx["protospacer"].fillna("N" * SPACER_LENGTH).to_numpy()[:n]
```
**Plain English:** Store a value: the name `seqs` now holds the result of `idx["protospacer"].fillna("N" * SPACER_LENGTH).to_numpy()[:n]`. Whenever you later write that name, you mean this value.

### Line 113
```python
    rebuilt, rb_names = matrix(seqs, verbose=False)
```
**Plain English:** Run this instruction: `rebuilt, rb_names = matrix(seqs, verbose=False)`.

### Line 114
```python
    col_of = {nm: i for i, nm in enumerate(names)}
```
**Plain English:** Store a value: the name `col_of` now holds the result of `{nm: i for i, nm in enumerate(names)}`. Whenever you later write that name, you mean this value.

### Line 115
```python
    Xv = np.asarray(X)[:n]
```
**Plain English:** Store a value: the name `Xv` now holds the result of `np.asarray(X)[:n]`. Whenever you later write that name, you mean this value.

### Line 117
```python
    shared = [c for c in rb_names if c in col_of]
```
**Plain English:** Store a value: the name `shared` now holds the result of `[c for c in rb_names if c in col_of]`. Whenever you later write that name, you mean this value.

### Line 118
```python
    a = rebuilt[:, [rb_names.index(c) for c in shared]]
```
**Plain English:** Store a value: the name `a` now holds the result of `rebuilt[:, [rb_names.index(c) for c in shared]]`. Whenever you later write that name, you mean this value.

### Line 119
```python
    b = Xv[:, [col_of[c] for c in shared]]
```
**Plain English:** Store a value: the name `b` now holds the result of `Xv[:, [col_of[c] for c in shared]]`. Whenever you later write that name, you mean this value.

### Line 120
```python
    both = ~(np.isnan(a) | np.isnan(b))
```
**Plain English:** Store a value: the name `both` now holds the result of `~(np.isnan(a) | np.isnan(b))`. Whenever you later write that name, you mean this value.

### Line 121
```python
    match = float(np.isclose(a[both], b[both], atol=1e-6).mean())
```
**Plain English:** Store a value: the name `match` now holds the result of `float(np.isclose(a[both], b[both], atol=1e-6).mean())`. Whenever you later write that name, you mean this value.

### Line 122
```python
    if verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose`.

### Line 123
```python
        print(f"  rebuilt {len(shared):,} columns x {n:,} guides: "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  rebuilt {len(shared):,} columns x {n:,} guides: "`.

### Line 124
```python
              f"{match:.6%} of values identical to the published matrix")
```
**Plain English:** Run this instruction: `f"{match:.6%} of values identical to the published matrix")`.

### Line 125
```python
    return dict(columns=len(shared), guides=n, agreement=match)
```
**Plain English:** Finish this function and send back: `dict(columns=len(shared), guides=n, agreement=match)`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### Why rebuild features instead of reusing the CSV?
So *new* guides (human, curated cohort) get the **same** 6,169 columns computed the **same** way.  
Mixing published rows with featurised rows would compare apples to oranges.

### V columns vs QCT columns
- **V**: mostly “is this exact DNA snippet present at this position?” (0/1)  
- **QCT**: chemistry lookup values for snippets at each position
