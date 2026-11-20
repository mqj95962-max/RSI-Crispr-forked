# P0 line-by-line: `Runjia/sgrna/build/qct.py`
**Why this file matters:** How hidden DNA letters are decoded from electron-count columns, and how those chemistry numbers get reused on new DNA.
**Length:** 287 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

The spreadsheet never wrote down the DNA letters, but it wrote chemistry codes that secretly encode them. This file cracks that code and builds a dictionary to reuse on new DNA.

---
### Lines 1–30
```python
"""Quantum chemical tensor (QCT) decoding and extension.

Two jobs.

1. **Decode.** The published feature matrix never stores the guide sequence,
   but it does store per-position QCT descriptors, and those are a pure
   function of the nucleotide at that position. `p{i}monomer.No.electronsraw`
   takes exactly four values across all 13,880 guides -- the valence-electron
   counts of the four bases:

       C4H5N3O   cytosine  16 + 5 + 15 + 6  = 42
       C5H6N2O2  thymine   20 + 6 + 10 + 12 = 48
       C5H5N5    adenine   20 + 5 + 25      = 50
       C5H5N5O   guanine   20 + 5 + 25 + 6  = 56

   so the 20 nt protospacer can be read straight back out of the matrix. Every
   decoded guide is then confirmed by finding it in the reference genome with
   an NGG immediately 3' of it, which is the real check that the mapping is
   right.

2. **Extend.** Once the sequence is known, every QCT column can be inverted
   into a lookup table: k-mer -> descriptor value, learned from the matrix
   itself. That means the *same* quantum parameterisation used in the paper
   can be applied to sequence the paper never encoded -- the flanking DNA, the
   PAM, the nucleotides downstream of it. No new quantum chemistry, no new
   assumptions, just the published tensors read off at new positions.

The k-mer span of each molecular unit follows the column counts in the matrix
(20 monomer positions, 19 dimer, 18 trimer, 17 tetramer over a 20 nt window).
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 32
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 34
```python
import json
```
**Plain English:** Load toolbox code: `import json` — used here for **read/write JSON text files**.

### Line 35
```python
import re
```
**Plain English:** Load toolbox code: `import re` — used here for **text pattern matching (regular expressions)**.

### Line 36
```python
from collections import defaultdict
```
**Plain English:** Load toolbox code: `from collections import defaultdict` — used here for **extra containers like Counter / defaultdict**.

### Line 37
```python
from pathlib import Path
```
**Plain English:** Load toolbox code: `from pathlib import Path` — used here for **friendly file-path objects**.

### Line 39
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 40
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 42
```python
from .. import config
```
**Plain English:** Load a project module from this repo: `from .. import config`.

### Line 44
```python
ELECTRONS_TO_BASE = {42.0: "C", 48.0: "T", 50.0: "A", 56.0: "G"}
```
**Plain English:** Lookup table: valence-electron count → DNA letter. 42→C, 48→T, 50→A, 56→G. This is how hidden sequences are decoded from the matrix.

### Line 45
```python
BASES = ("A", "C", "G", "T")
```
**Plain English:** Store a value: the name `BASES` now holds the result of `("A", "C", "G", "T")`. Whenever you later write that name, you mean this value.

### Line 47
```python
# Molecular unit -> how many consecutive nucleotides it spans.
```
**Plain English:** Human-only note (Python ignores it): Molecular unit -> how many consecutive nucleotides it spans.

### Line 48
```python
UNIT_SPAN = {"monomer": 1, "basepair": 1, "dimer": 2, "trimer": 3, "tetramer": 4}
```
**Plain English:** Store a value: the name `UNIT_SPAN` now holds the result of `{"monomer": 1, "basepair": 1, "dimer": 2, "trimer": 3, "tetramer": 4}`. Whenever you later write that name, you mean this value.

### Line 50
```python
_COL_RE = re.compile(r"^p(\d+)([A-Za-z]+)\.(.+)$")
```
**Plain English:** Store a value: the name `_COL_RE` now holds the result of `re.compile(r"^p(\d+)([A-Za-z]+)\.(.+)$")`. Whenever you later write that name, you mean this value.

### Line 53
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 54
```python
# Column bookkeeping
```
**Plain English:** Human-only note (Python ignores it): Column bookkeeping

### Line 55
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 58
```python
def parse_qct_column(col: str) -> tuple[int, str, str] | None:
```
**Plain English:** Defines a reusable recipe named `parse_qct_column`. Inputs in parentheses: `col: str`. Returns type hint: tuple[int, str, str] | None. Nothing runs yet until something *calls* `parse_qct_column(...)`.

### Line 59
```python
    """'p18dimer.Hbond.stackingraw' -> (18, 'dimer', 'Hbond.stackingraw')."""
```
**Plain English:** A short documentation string attached to the nearest function/module: 'p18dimer.Hbond.stackingraw' -> (18, 'dimer', 'Hbond.stackingraw').

### Line 60
```python
    m = _COL_RE.match(col)
```
**Plain English:** Store a value: the name `m` now holds the result of `_COL_RE.match(col)`. Whenever you later write that name, you mean this value.

### Line 61
```python
    if not m:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not m`.

### Line 62
```python
        return None
```
**Plain English:** Finish this function and send back: `None`.

### Line 63
```python
    pos, unit, prop = int(m.group(1)), m.group(2).lower(), m.group(3)
```
**Plain English:** Run this instruction: `pos, unit, prop = int(m.group(1)), m.group(2).lower(), m.group(3)`.

### Line 64
```python
    if unit not in UNIT_SPAN:
```
**Plain English:** Decision: run the indented block only when this condition is true → `unit not in UNIT_SPAN`.

### Line 65
```python
        return None
```
**Plain English:** Finish this function and send back: `None`.

### Line 66
```python
    return pos, unit, prop
```
**Plain English:** Finish this function and send back: `pos, unit, prop`.

### Line 69
```python
def qct_columns(header: list[str]) -> dict[tuple[str, str], dict[int, str]]:
```
**Plain English:** Defines a reusable recipe named `qct_columns`. Inputs in parentheses: `header: list[str]`. Returns type hint: dict[tuple[str, str], dict[int, str]]. Nothing runs yet until something *calls* `qct_columns(...)`.

### Line 70
```python
    """Group QCT columns as {(unit, property): {position: column name}}."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Group QCT columns as {(unit, property): {position: column name}}.

### Line 71
```python
    out: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
```
**Plain English:** Run this instruction: `out: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)`.

### Line 72
```python
    for col in header:
```
**Plain English:** Loop: repeat the indented block once for each item → `col in header`.

### Line 73
```python
        parsed = parse_qct_column(col)
```
**Plain English:** Store a value: the name `parsed` now holds the result of `parse_qct_column(col)`. Whenever you later write that name, you mean this value.

### Line 74
```python
        if parsed is None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `parsed is None`.

### Line 75
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 76
```python
        pos, unit, prop = parsed
```
**Plain English:** Run this instruction: `pos, unit, prop = parsed`.

### Line 77
```python
        out[(unit, prop)][pos] = col
```
**Plain English:** Run this instruction: `out[(unit, prop)][pos] = col`.

### Line 78
```python
    return dict(out)
```
**Plain English:** Finish this function and send back: `dict(out)`.

### Line 81
```python
def read_header(path=None, header_row=None) -> list[str]:
```
**Plain English:** Defines a reusable recipe named `read_header`. Inputs in parentheses: `path=None, header_row=None`. Returns type hint: list[str]. Nothing runs yet until something *calls* `read_header(...)`.

### Line 82
```python
    path = path or config.BASE_MATRIX
```
**Plain English:** Store a value: the name `path` now holds the result of `path or config.BASE_MATRIX`. Whenever you later write that name, you mean this value.

### Line 83
```python
    header_row = config.BASE_MATRIX_HEADER_ROW if header_row is None else header_row
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 84
```python
    return list(
```
**Plain English:** Finish this function and send back: `list(`.

### Line 85
```python
        pd.read_csv(path, header=header_row, nrows=0, low_memory=False).columns
```
**Plain English:** Run this instruction: `pd.read_csv(path, header=header_row, nrows=0, low_memory=False).columns`.

### Line 86
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 89
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 90
```python
# Cached slice of the base matrix
```
**Plain English:** Human-only note (Python ignores it): Cached slice of the base matrix

### Line 91
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 93
```python
QCT_CACHE = config.INTERIM / "qct_columns.csv"
```
**Plain English:** Store a value: the name `QCT_CACHE` now holds the result of `config.INTERIM / "qct_columns.csv"`. Whenever you later write that name, you mean this value.

### Line 96
```python
def load_qct_frame(force: bool = False, verbose: bool = True) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `load_qct_frame`. Inputs in parentheses: `force: bool = False, verbose: bool = True`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `load_qct_frame(...)`.

### Lines 97–103
```python
    """ID, target and all 316 QCT columns, cached.

    The published matrix is 198 MB across 6,234 columns, and pandas has to
    tokenise all of it however few columns you ask for -- about a minute a
    pass. Everything that needs the quantum columns goes through this cache
    instead, so that cost is paid once.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 104
```python
    if QCT_CACHE.exists() and not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `QCT_CACHE.exists() and not force`.

### Line 105
```python
        return pd.read_csv(QCT_CACHE, low_memory=False)
```
**Plain English:** Finish this function and send back: `pd.read_csv(QCT_CACHE, low_memory=False)`.

### Line 107
```python
    if verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose`.

### Line 108
```python
        print(f"  caching QCT columns from {config.BASE_MATRIX.name} (one-off, ~1 min)")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  caching QCT columns from {config.BASE_MATRIX.name} (one-off, ~1 min)")`.

### Line 109
```python
    header = read_header()
```
**Plain English:** Store a value: the name `header` now holds the result of `read_header()`. Whenever you later write that name, you mean this value.

### Line 110
```python
    qcols = [c for c in header if parse_qct_column(c) is not None]
```
**Plain English:** Store a value: the name `qcols` now holds the result of `[c for c in header if parse_qct_column(c) is not None]`. Whenever you later write that name, you mean this value.

### Line 111
```python
    df = pd.read_csv(
```
**Plain English:** Store a value: the name `df` now holds the result of `pd.read_csv(`. Whenever you later write that name, you mean this value.

### Line 112
```python
        config.BASE_MATRIX,
```
**Plain English:** Run this instruction: `config.BASE_MATRIX,`.

### Line 113
```python
        header=config.BASE_MATRIX_HEADER_ROW,
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 114
```python
        usecols=[config.ID_COL, config.TARGET_COL] + qcols,
```
**Plain English:** Store a value: the name `usecols` now holds the result of `[config.ID_COL, config.TARGET_COL] + qcols,`. Whenever you later write that name, you mean this value.

### Line 115
```python
        low_memory=False,
```
**Plain English:** Store a value: the name `low_memory` now holds the result of `False,`. Whenever you later write that name, you mean this value.

### Line 116
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 117
```python
    df = df[[config.ID_COL, config.TARGET_COL] + qcols]
```
**Plain English:** Store a value: the name `df` now holds the result of `df[[config.ID_COL, config.TARGET_COL] + qcols]`. Whenever you later write that name, you mean this value.

### Line 118
```python
    df.to_csv(QCT_CACHE, index=False)
```
**Plain English:** Run this instruction: `df.to_csv(QCT_CACHE, index=False)`.

### Line 119
```python
    if verbose:
```
**Plain English:** Decision: run the indented block only when this condition is true → `verbose`.

### Line 120
```python
        print(f"  wrote {QCT_CACHE} ({df.shape[0]:,} x {df.shape[1]:,})")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  wrote {QCT_CACHE} ({df.shape[0]:,} x {df.shape[1]:,})")`.

### Line 121
```python
    return df
```
**Plain English:** Finish this function and send back: `df`.

### Line 124
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 125
```python
# 1. Decoding
```
**Plain English:** Human-only note (Python ignores it): 1. Decoding

### Line 126
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 129
```python
def decode_protospacers(frame: pd.DataFrame | None = None,
```
**Plain English:** Run this instruction: `def decode_protospacers(frame: pd.DataFrame | None = None,`.

### Line 130
```python
                        n_positions: int = 20) -> pd.DataFrame:
```
**Plain English:** Run this instruction: `n_positions: int = 20) -> pd.DataFrame:`.

### Lines 131–135
```python
    """Read the electron-count columns and reconstruct each 20 nt protospacer.

    Returns a frame with sgRNAID, cut.score and `protospacer`. Rows whose
    descriptors are missing get 'N' at that position and are flagged.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 136
```python
    df = load_qct_frame() if frame is None else frame
```
**Plain English:** Store a value: the name `df` now holds the result of `load_qct_frame() if frame is None else frame`. Whenever you later write that name, you mean this value.

### Line 137
```python
    mat = df[[f"p{i}monomer.No.electronsraw" for i in range(1, n_positions + 1)]]
```
**Plain English:** Pull the 20 electron-count columns (one per spacer position). Each cell is 42/48/50/56 → one DNA letter.

### Line 138
```python
    mat = mat.to_numpy(dtype=float)
```
**Plain English:** Store a value: the name `mat` now holds the result of `mat.to_numpy(dtype=float)`. Whenever you later write that name, you mean this value.

### Line 140
```python
    unknown = sorted(set(np.unique(mat[~np.isnan(mat)])) - set(ELECTRONS_TO_BASE))
```
**Plain English:** Lookup table: valence-electron count → DNA letter. 42→C, 48→T, 50→A, 56→G. This is how hidden sequences are decoded from the matrix.

### Line 141
```python
    if unknown:
```
**Plain English:** Decision: run the indented block only when this condition is true → `unknown`.

### Line 142
```python
        raise ValueError(
```
**Plain English:** Stop and report a problem on purpose → `ValueError(`.

### Line 143
```python
            "Unexpected electron counts in the monomer columns: "
```
**Plain English:** Run this instruction: `"Unexpected electron counts in the monomer columns: "`.

### Line 144
```python
            f"{unknown}. The decoding table only knows {sorted(ELECTRONS_TO_BASE)}."
```
**Plain English:** Run this instruction: `f"{unknown}. The decoding table only knows {sorted(ELECTRONS_TO_BASE)}."`.

### Line 145
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 147
```python
    seqs = ["".join(ELECTRONS_TO_BASE.get(v, "N") for v in row) for row in mat]
```
**Plain English:** Lookup table: valence-electron count → DNA letter. 42→C, 48→T, 50→A, 56→G. This is how hidden sequences are decoded from the matrix.

### Line 148
```python
    out = df[[config.ID_COL, config.TARGET_COL]].copy()
```
**Plain English:** Store a value: the name `out` now holds the result of `df[[config.ID_COL, config.TARGET_COL]].copy()`. Whenever you later write that name, you mean this value.

### Line 149
```python
    out["protospacer"] = seqs
```
**Plain English:** Store a value: the name `out["protospacer"]` now holds the result of `seqs`. Whenever you later write that name, you mean this value.

### Line 150
```python
    out["decoded_ok"] = ~out["protospacer"].str.contains("N")
```
**Plain English:** Store a value: the name `out["decoded_ok"]` now holds the result of `~out["protospacer"].str.contains("N")`. Whenever you later write that name, you mean this value.

### Line 151
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 154
```python
def parse_sgrna_id(sgrna_id: str) -> dict:
```
**Plain English:** Defines a reusable recipe named `parse_sgrna_id`. Inputs in parentheses: `sgrna_id: str`. Returns type hint: dict. Nothing runs yet until something *calls* `parse_sgrna_id(...)`.

### Line 155
```python
    """'aaeAb3241_107_Cas9' -> gene aaeA, b-number b3241, offset 107."""
```
**Plain English:** A short documentation string attached to the nearest function/module: 'aaeAb3241_107_Cas9' -> gene aaeA, b-number b3241, offset 107.

### Line 156
```python
    m = re.match(r"^(?P<gene>.*?)(?P<bnum>[bB]\d+)_(?P<offset>\d+)_(?P<nuclease>.+)$",
```
**Plain English:** Store a value: the name `m` now holds the result of `re.match(r"^(?P<gene>.*?)(?P<bnum>[bB]\d+)_(?P<offset>\d+)_(?P<nuclease>.+)$",`. Whenever you later write that name, you mean this value.

### Line 157
```python
                 str(sgrna_id))
```
**Plain English:** Run this instruction: `str(sgrna_id))`.

### Line 158
```python
    if not m:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not m`.

### Line 159
```python
        return dict(gene_name=None, b_number=None, gene_offset=None, nuclease=None)
```
**Plain English:** Finish this function and send back: `dict(gene_name=None, b_number=None, gene_offset=None, nuclease=None)`.

### Line 160
```python
    return dict(
```
**Plain English:** Finish this function and send back: `dict(`.

### Line 161
```python
        gene_name=m.group("gene") or None,
```
**Plain English:** Store a value: the name `gene_name` now holds the result of `m.group("gene") or None,`. Whenever you later write that name, you mean this value.

### Line 162
```python
        b_number=m.group("bnum").lower(),
```
**Plain English:** Store a value: the name `b_number` now holds the result of `m.group("bnum").lower(),`. Whenever you later write that name, you mean this value.

### Line 163
```python
        gene_offset=int(m.group("offset")),
```
**Plain English:** Store a value: the name `gene_offset` now holds the result of `int(m.group("offset")),`. Whenever you later write that name, you mean this value.

### Line 164
```python
        nuclease=m.group("nuclease"),
```
**Plain English:** Store a value: the name `nuclease` now holds the result of `m.group("nuclease"),`. Whenever you later write that name, you mean this value.

### Line 165
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 168
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 169
```python
# 2. Lookup tables
```
**Plain English:** Human-only note (Python ignores it): 2. Lookup tables

### Line 170
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 173
```python
def learn_lookup_tables(
```
**Plain English:** Run this instruction: `def learn_lookup_tables(`.

### Line 174
```python
    protospacers: pd.Series,
```
**Plain English:** Run this instruction: `protospacers: pd.Series,`.

### Line 175
```python
    frame: pd.DataFrame | None = None,
```
**Plain English:** Run this instruction: `frame: pd.DataFrame | None = None,`.

### Line 176
```python
) -> dict:
```
**Plain English:** Run this instruction: `) -> dict:`.

### Lines 177–183
```python
    """Invert the matrix's QCT columns into {unit: {property: {kmer: value}}}.

    Consistency is checked, not assumed: if one k-mer ever maps to two
    different values for the same descriptor the function raises, because that
    would mean the descriptor is not a pure function of sequence and the whole
    extension idea is unsound.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 184
```python
    df = load_qct_frame() if frame is None else frame
```
**Plain English:** Store a value: the name `df` now holds the result of `load_qct_frame() if frame is None else frame`. Whenever you later write that name, you mean this value.

### Line 185
```python
    groups = qct_columns(list(df.columns))
```
**Plain English:** Store a value: the name `groups` now holds the result of `qct_columns(list(df.columns))`. Whenever you later write that name, you mean this value.

### Line 186
```python
    seqs = protospacers.to_numpy()[: len(df)]
```
**Plain English:** Store a value: the name `seqs` now holds the result of `protospacers.to_numpy()[: len(df)]`. Whenever you later write that name, you mean this value.

### Line 188
```python
    tables: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)
```
**Plain English:** Run this instruction: `tables: dict[str, dict[str, dict[str, float]]] = defaultdict(dict)`.

### Line 189
```python
    conflicts: list[str] = []
```
**Plain English:** Run this instruction: `conflicts: list[str] = []`.

### Line 191
```python
    for (unit, prop), pos_map in groups.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `(unit, prop), pos_map in groups.items()`.

### Line 192
```python
        span = UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 193
```python
        acc: dict[str, set] = defaultdict(set)
```
**Plain English:** Run this instruction: `acc: dict[str, set] = defaultdict(set)`.

### Line 194
```python
        for pos, col in pos_map.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `pos, col in pos_map.items()`.

### Line 195
```python
            values = df[col].to_numpy(dtype=float)
```
**Plain English:** Store a value: the name `values` now holds the result of `df[col].to_numpy(dtype=float)`. Whenever you later write that name, you mean this value.

### Line 196
```python
            start = pos - 1
```
**Plain English:** Store a value: the name `start` now holds the result of `pos - 1`. Whenever you later write that name, you mean this value.

### Line 197
```python
            for seq, val in zip(seqs, values):
```
**Plain English:** Loop: repeat the indented block once for each item → `seq, val in zip(seqs, values)`.

### Line 198
```python
                if np.isnan(val):
```
**Plain English:** Decision: run the indented block only when this condition is true → `np.isnan(val)`.

### Line 199
```python
                    continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 200
```python
                kmer = seq[start : start + span]
```
**Plain English:** Store a value: the name `kmer` now holds the result of `seq[start : start + span]`. Whenever you later write that name, you mean this value.

### Line 201
```python
                if len(kmer) < span or "N" in kmer:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(kmer) < span or "N" in kmer`.

### Line 202
```python
                    continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 203
```python
                acc[kmer].add(round(float(val), 6))
```
**Plain English:** Run this instruction: `acc[kmer].add(round(float(val), 6))`.

### Line 204
```python
        table = {}
```
**Plain English:** Store a value: the name `table` now holds the result of `{}`. Whenever you later write that name, you mean this value.

### Line 205
```python
        for kmer, vals in acc.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `kmer, vals in acc.items()`.

### Line 206
```python
            if len(vals) > 1:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(vals) > 1`.

### Line 207
```python
                conflicts.append(f"{unit}.{prop}[{kmer}] -> {sorted(vals)}")
```
**Plain English:** If the same DNA snippet maps to two different chemistry values, the ‘pure function of sequence’ idea is broken — collect that as an error.

### Line 208
```python
            table[kmer] = float(sorted(vals)[0])
```
**Plain English:** Store a value: the name `table[kmer]` now holds the result of `float(sorted(vals)[0])`. Whenever you later write that name, you mean this value.

### Line 209
```python
        tables[unit][prop] = table
```
**Plain English:** Store a value: the name `tables[unit][prop]` now holds the result of `table`. Whenever you later write that name, you mean this value.

### Line 211
```python
    if conflicts:
```
**Plain English:** Decision: run the indented block only when this condition is true → `conflicts`.

### Line 212
```python
        raise ValueError(
```
**Plain English:** Stop and report a problem on purpose → `ValueError(`.

### Line 213
```python
            "QCT descriptors are not a pure function of k-mer identity:\n  "
```
**Plain English:** Run this instruction: `"QCT descriptors are not a pure function of k-mer identity:\n  "`.

### Line 214
```python
            + "\n  ".join(conflicts[:10])
```
**Plain English:** Run this instruction: `+ "\n  ".join(conflicts[:10])`.

### Line 215
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 216
```python
    return {k: dict(v) for k, v in tables.items()}
```
**Plain English:** Finish this function and send back: `{k: dict(v) for k, v in tables.items()}`.

### Line 219
```python
def table_coverage(tables: dict) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `table_coverage`. Inputs in parentheses: `tables: dict`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `table_coverage(...)`.

### Line 220
```python
    """How much of each k-mer space the learned tables cover."""
```
**Plain English:** A short documentation string attached to the nearest function/module: How much of each k-mer space the learned tables cover.

### Line 221
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 222
```python
    for unit, props in tables.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `unit, props in tables.items()`.

### Line 223
```python
        span = UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 224
```python
        total = 4 ** span
```
**Plain English:** Store a value: the name `total` now holds the result of `4 ** span`. Whenever you later write that name, you mean this value.

### Line 225
```python
        for prop, table in props.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `prop, table in props.items()`.

### Line 226
```python
            rows.append(
```
**Plain English:** Run this instruction: `rows.append(`.

### Line 227
```python
                dict(
```
**Plain English:** Run this instruction: `dict(`.

### Line 228
```python
                    unit=unit,
```
**Plain English:** Store a value: the name `unit` now holds the result of `unit,`. Whenever you later write that name, you mean this value.

### Line 229
```python
                    property=prop,
```
**Plain English:** Store a value: the name `property` now holds the result of `prop,`. Whenever you later write that name, you mean this value.

### Line 230
```python
                    span=span,
```
**Plain English:** Store a value: the name `span` now holds the result of `span,`. Whenever you later write that name, you mean this value.

### Line 231
```python
                    observed=len(table),
```
**Plain English:** Store a value: the name `observed` now holds the result of `len(table),`. Whenever you later write that name, you mean this value.

### Line 232
```python
                    possible=total,
```
**Plain English:** Store a value: the name `possible` now holds the result of `total,`. Whenever you later write that name, you mean this value.

### Line 233
```python
                    coverage=len(table) / total,
```
**Plain English:** Store a value: the name `coverage` now holds the result of `len(table) / total,`. Whenever you later write that name, you mean this value.

### Line 234
```python
                )
```
**Plain English:** Run this instruction: `)`.

### Line 235
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 236
```python
    return pd.DataFrame(rows).sort_values(["unit", "property"]).reset_index(drop=True)
```
**Plain English:** Finish this function and send back: `pd.DataFrame(rows).sort_values(["unit", "property"]).reset_index(drop=True)`.

### Line 239
```python
def save_tables(tables: dict, path=None) -> Path:
```
**Plain English:** Defines a reusable recipe named `save_tables`. Inputs in parentheses: `tables: dict, path=None`. Returns type hint: Path. Nothing runs yet until something *calls* `save_tables(...)`.

### Line 240
```python
    path = Path(path or config.QCT_TABLES)
```
**Plain English:** Store a value: the name `path` now holds the result of `Path(path or config.QCT_TABLES)`. Whenever you later write that name, you mean this value.

### Line 241
```python
    path.write_text(json.dumps(tables, indent=1, sort_keys=True))
```
**Plain English:** Run this instruction: `path.write_text(json.dumps(tables, indent=1, sort_keys=True))`.

### Line 242
```python
    return path
```
**Plain English:** Finish this function and send back: `path`.

### Line 245
```python
def load_tables(path=None) -> dict:
```
**Plain English:** Defines a reusable recipe named `load_tables`. Inputs in parentheses: `path=None`. Returns type hint: dict. Nothing runs yet until something *calls* `load_tables(...)`.

### Line 246
```python
    path = Path(path or config.QCT_TABLES)
```
**Plain English:** Store a value: the name `path` now holds the result of `Path(path or config.QCT_TABLES)`. Whenever you later write that name, you mean this value.

### Line 247
```python
    if not path.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not path.exists()`.

### Line 248
```python
        raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 249
```python
            f"{path} not found -- run `python -m sgrna.build_guide_index` first."
```
**Plain English:** Run this instruction: `f"{path} not found -- run `python -m sgrna.build_guide_index` first."`.

### Line 250
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 251
```python
    return json.loads(path.read_text())
```
**Plain English:** Finish this function and send back: `json.loads(path.read_text())`.

### Line 254
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 255
```python
# 3. Applying tables to new sequence
```
**Plain English:** Human-only note (Python ignores it): 3. Applying tables to new sequence

### Line 256
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 259
```python
def profile(seq: str, unit: str, prop: str, tables: dict) -> np.ndarray:
```
**Plain English:** Defines a reusable recipe named `profile`. Inputs in parentheses: `seq: str, unit: str, prop: str, tables: dict`. Returns type hint: np.ndarray. Nothing runs yet until something *calls* `profile(...)`.

### Lines 260–265
```python
    """Descriptor value at every position of `seq` for one (unit, property).

    Returns an array of length len(seq) - span + 1. Unknown k-mers (an N, or a
    tetramer the 13,880 guides never contained) come back as NaN, which the
    downstream models already handle by median imputation.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 266
```python
    span = UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 267
```python
    table = tables[unit][prop]
```
**Plain English:** Store a value: the name `table` now holds the result of `tables[unit][prop]`. Whenever you later write that name, you mean this value.

### Line 268
```python
    n = len(seq) - span + 1
```
**Plain English:** Store a value: the name `n` now holds the result of `len(seq) - span + 1`. Whenever you later write that name, you mean this value.

### Line 269
```python
    if n <= 0:
```
**Plain English:** Decision: run the indented block only when this condition is true → `n <= 0`.

### Line 270
```python
        return np.zeros(0)
```
**Plain English:** Finish this function and send back: `np.zeros(0)`.

### Line 271
```python
    out = np.full(n, np.nan)
```
**Plain English:** Store a value: the name `out` now holds the result of `np.full(n, np.nan)`. Whenever you later write that name, you mean this value.

### Line 272
```python
    for i in range(n):
```
**Plain English:** Loop: repeat the indented block once for each item → `i in range(n)`.

### Line 273
```python
        out[i] = table.get(seq[i : i + span], np.nan)
```
**Plain English:** Look up this DNA snippet in the learned table; if never seen, return NaN (blank).

### Line 274
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 277
```python
def summarise(values: np.ndarray, prefix: str) -> dict[str, float]:
```
**Plain English:** Defines a reusable recipe named `summarise`. Inputs in parentheses: `values: np.ndarray, prefix: str`. Returns type hint: dict[str, float]. Nothing runs yet until something *calls* `summarise(...)`.

### Line 278
```python
    """Mean / sd / min / max / sum of a descriptor profile, NaN-safe."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Mean / sd / min / max / sum of a descriptor profile, NaN-safe.

### Line 279
```python
    if values.size == 0 or np.all(np.isnan(values)):
```
**Plain English:** Decision: run the indented block only when this condition is true → `values.size == 0 or np.all(np.isnan(values))`.

### Line 280
```python
        return {f"{prefix}.{s}": np.nan for s in ("mean", "sd", "min", "max", "sum")}
```
**Plain English:** Finish this function and send back: `{f"{prefix}.{s}": np.nan for s in ("mean", "sd", "min", "max", "sum")}`.

### Line 281
```python
    return {
```
**Plain English:** Finish this function and send back: `{`.

### Line 282
```python
        f"{prefix}.mean": float(np.nanmean(values)),
```
**Plain English:** Run this instruction: `f"{prefix}.mean": float(np.nanmean(values)),`.

### Line 283
```python
        f"{prefix}.sd": float(np.nanstd(values)),
```
**Plain English:** Run this instruction: `f"{prefix}.sd": float(np.nanstd(values)),`.

### Line 284
```python
        f"{prefix}.min": float(np.nanmin(values)),
```
**Plain English:** Run this instruction: `f"{prefix}.min": float(np.nanmin(values)),`.

### Line 285
```python
        f"{prefix}.max": float(np.nanmax(values)),
```
**Plain English:** Run this instruction: `f"{prefix}.max": float(np.nanmax(values)),`.

### Line 286
```python
        f"{prefix}.sum": float(np.nansum(values)),
```
**Plain English:** Run this instruction: `f"{prefix}.sum": float(np.nansum(values)),`.

### Line 287
```python
    }
```
**Plain English:** Run this instruction: `}`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### How can electron counts reveal DNA letters?
Each DNA base has a fixed valence-electron count in the paper’s encoding:  
C=42, T=48, A=50, G=56.  
Column `p7monomer.No.electronsraw` = 50 → position 7 is Adenine. Twenty such columns → full 20-mer.

### What does “extend QCT into flanks” mean?
From the published columns, learn a dictionary: DNA snippet → chemistry number.  
Then apply that dictionary to DNA *outside* the 20-mer (Family A). Same chemistry rules, new positions — no new quantum simulations.
