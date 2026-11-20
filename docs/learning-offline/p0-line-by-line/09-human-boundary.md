# P0 line-by-line: `Jacky/human-boundary/scripts/run_human_boundary.py`
**Why this file matters:** Port the E. coli story to human Cas9 cutting (decode → locate on hg38 → Family A → ladder → transfer).
**Length:** 635 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Repeat the E. coli playbook on human data: decode letters, find them in the human genome, build Family A, score the model, and test whether E. coli knowledge transfers.

---
### Line 1
```python
#!/usr/bin/env python3
```
**Plain English:** Human-only note (Python ignores it): !/usr/bin/env python3

### Lines 2–11
```python
"""Tier-1 human boundary experiments.

1. Decode protospacers from the Noshay human matrix (QCT electron columns).
2. Locate unique NGG-flanked copies on hg38 (stream chromosomes).
3. Build Family A (a_flank) on located guides.
4. Human-only ladder: shared-cols / regenerated base / base+A.
5. Transfer autopsy: does an E. coli model fail mainly via the GC rule?

Outputs under Jacky/human-boundary/results/.
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 12
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 14
```python
import argparse
```
**Plain English:** Load toolbox code: `import argparse` — used here for **command-line switches like `--flank 1000`**.

### Line 15
```python
import gzip
```
**Plain English:** Load toolbox code: `import gzip` — used here for **read compressed `.gz` files**.

### Line 16
```python
import json
```
**Plain English:** Load toolbox code: `import json` — used here for **read/write JSON text files**.

### Line 17
```python
import os
```
**Plain English:** Load toolbox code: `import os` — used here for **talk to the operating system (paths, env vars)**.

### Line 18
```python
import sys
```
**Plain English:** Load toolbox code: `import sys` — used here for **Python runtime (arguments, exit codes)**.

### Line 19
```python
import time
```
**Plain English:** Load toolbox code: `import time` — used here for **clocks and timers**.

### Line 20
```python
from pathlib import Path
```
**Plain English:** Load toolbox code: `from pathlib import Path` — used here for **friendly file-path objects**.

### Line 22
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 23
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 24
```python
from scipy.stats import spearmanr
```
**Plain English:** Load toolbox code: `from scipy.stats import spearmanr` — used here for **scientific stats (Spearman/Pearson)**.

### Line 26
```python
_REPO = Path(__file__).resolve().parents[3]
```
**Plain English:** Store a value: the name `_REPO` now holds the result of `Path(__file__).resolve().parents[3]`. Whenever you later write that name, you mean this value.

### Line 27
```python
ROOT = Path(os.environ.get("RSI09_ROOT", str(_REPO / "Runjia"))).resolve()
```
**Plain English:** Store a value: the name `ROOT` now holds the result of `Path(os.environ.get("RSI09_ROOT", str(_REPO / "Runjia"))).resolve()`. Whenever you later write that name, you mean this value.

### Line 28
```python
os.environ["RSI09_ROOT"] = str(ROOT)
```
**Plain English:** Store a value: the name `os.environ["RSI09_ROOT"]` now holds the result of `str(ROOT)`. Whenever you later write that name, you mean this value.

### Line 29
```python
(ROOT / "external_data").mkdir(parents=True, exist_ok=True)
```
**Plain English:** Store a value: the name `(ROOT / "external_data").mkdir(parents` now holds the result of `True, exist_ok=True)`. Whenever you later write that name, you mean this value.

### Line 30
```python
(ROOT / "data" / "raw").mkdir(parents=True, exist_ok=True)
```
**Plain English:** Store a value: the name `(ROOT / "data" / "raw").mkdir(parents` now holds the result of `True, exist_ok=True)`. Whenever you later write that name, you mean this value.

### Line 31
```python
sys.path.insert(0, str(ROOT))
```
**Plain English:** Run this instruction: `sys.path.insert(0, str(ROOT))`.

### Line 33
```python
from sgrna import config, featurise, genome, qct  # noqa: E402
```
**Plain English:** Load a project module from this repo: `from sgrna import config, featurise, genome, qct  # noqa: E402`.

### Line 34
```python
from sgrna.features import a_flank  # noqa: E402
```
**Plain English:** Load toolbox code: `from sgrna.features import a_flank  # noqa: E402` — used here for **text pattern matching (regular expressions)**.

### Line 35
```python
from sgrna.run_ablation import cross_validate, _impute  # noqa: E402
```
**Plain English:** Load toolbox code: `from sgrna.run_ablation import cross_validate, _impute  # noqa: E402` — used here for **talk to the operating system (paths, env vars)**.

### Line 37
```python
OUT = _REPO / "Jacky" / "human-boundary" / "results"
```
**Plain English:** Store a value: the name `OUT` now holds the result of `_REPO / "Jacky" / "human-boundary" / "results"`. Whenever you later write that name, you mean this value.

### Line 38
```python
CACHE = config.INTERIM / "human_boundary"
```
**Plain English:** Store a value: the name `CACHE` now holds the result of `config.INTERIM / "human_boundary"`. Whenever you later write that name, you mean this value.

### Line 39
```python
OUT.mkdir(parents=True, exist_ok=True)
```
**Plain English:** Run this instruction: `OUT.mkdir(parents=True, exist_ok=True)`.

### Line 40
```python
CACHE.mkdir(parents=True, exist_ok=True)
```
**Plain English:** Run this instruction: `CACHE.mkdir(parents=True, exist_ok=True)`.

### Line 42
```python
HUMAN_MATRIX = config.RAW / "human_feature_matrix.csv"
```
**Plain English:** Store a value: the name `HUMAN_MATRIX` now holds the result of `config.RAW / "human_feature_matrix.csv"`. Whenever you later write that name, you mean this value.

### Line 43
```python
HG38_FA = config.REFERENCE / "hg38.fa"
```
**Plain English:** Store a value: the name `HG38_FA` now holds the result of `config.REFERENCE / "hg38.fa"`. Whenever you later write that name, you mean this value.

### Line 44
```python
HG38_GZ = config.REFERENCE / "hg38.fa.gz"
```
**Plain English:** Store a value: the name `HG38_GZ` now holds the result of `config.REFERENCE / "hg38.fa.gz"`. Whenever you later write that name, you mean this value.

### Line 45
```python
FLANK = 1000
```
**Plain English:** How many DNA letters to keep on each side of the target (**1000 nt**). Family A summarises these flanks.

### Line 46
```python
SEED = 41
```
**Plain English:** Store a value: the name `SEED` now holds the result of `41`. Whenever you later write that name, you mean this value.

### Line 47
```python
ELECTRONS_TO_BASE = qct.ELECTRONS_TO_BASE
```
**Plain English:** Lookup table: valence-electron count → DNA letter. 42→C, 48→T, 50→A, 56→G. This is how hidden sequences are decoded from the matrix.

### Line 48
```python
REVCOMP = genome.revcomp
```
**Plain English:** Store a value: the name `REVCOMP` now holds the result of `genome.revcomp`. Whenever you later write that name, you mean this value.

### Line 51
```python
def _spearman(y, p):
```
**Plain English:** Defines a reusable recipe named `_spearman`. Inputs in parentheses: `y, p`. Nothing runs yet until something *calls* `_spearman(...)`.

### Line 52
```python
    y = np.asarray(y, float)
```
**Plain English:** Store a value: the name `y` now holds the result of `np.asarray(y, float)`. Whenever you later write that name, you mean this value.

### Line 53
```python
    p = np.asarray(p, float)
```
**Plain English:** Store a value: the name `p` now holds the result of `np.asarray(p, float)`. Whenever you later write that name, you mean this value.

### Line 54
```python
    m = np.isfinite(y) & np.isfinite(p)
```
**Plain English:** Store a value: the name `m` now holds the result of `np.isfinite(y) & np.isfinite(p)`. Whenever you later write that name, you mean this value.

### Line 55
```python
    if m.sum() < 3:
```
**Plain English:** Decision: run the indented block only when this condition is true → `m.sum() < 3`.

### Line 56
```python
        return float("nan")
```
**Plain English:** Finish this function and send back: `float("nan")`.

### Line 57
```python
    r = spearmanr(y[m], p[m]).statistic
```
**Plain English:** Store a value: the name `r` now holds the result of `spearmanr(y[m], p[m]).statistic`. Whenever you later write that name, you mean this value.

### Line 58
```python
    return float(r) if np.isfinite(r) else float("nan")
```
**Plain English:** Finish this function and send back: `float(r) if np.isfinite(r) else float("nan")`.

### Line 61
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 62
```python
# 1. Decode
```
**Plain English:** Human-only note (Python ignores it): 1. Decode

### Line 63
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 66
```python
def decode_human(force: bool = False) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `decode_human`. Inputs in parentheses: `force: bool = False`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `decode_human(...)`.

### Line 67
```python
    path = CACHE / "human_decoded.csv"
```
**Plain English:** Store a value: the name `path` now holds the result of `CACHE / "human_decoded.csv"`. Whenever you later write that name, you mean this value.

### Line 68
```python
    if path.exists() and not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `path.exists() and not force`.

### Line 69
```python
        print(f"  cached decode {path}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  cached decode {path}", flush=True)`.

### Line 70
```python
        return pd.read_csv(path)
```
**Plain English:** Finish this function and send back: `pd.read_csv(path)`.

### Line 72
```python
    print(f"  reading QCT electron columns from {HUMAN_MATRIX.name} ...", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  reading QCT electron columns from {HUMAN_MATRIX.name} ...", flush=True)`.

### Line 73
```python
    cols = [config.ID_COL, config.TARGET_COL] + [
```
**Plain English:** Store a value: the name `cols` now holds the result of `[config.ID_COL, config.TARGET_COL] + [`. Whenever you later write that name, you mean this value.

### Line 74
```python
        f"p{i}monomer.No.electronsraw" for i in range(1, 21)
```
**Plain English:** Run this instruction: `f"p{i}monomer.No.electronsraw" for i in range(1, 21)`.

### Line 75
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 76
```python
    df = pd.read_csv(
```
**Plain English:** Store a value: the name `df` now holds the result of `pd.read_csv(`. Whenever you later write that name, you mean this value.

### Line 77
```python
        HUMAN_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, usecols=cols, low_memory=False
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 78
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 79
```python
    mat = df[[f"p{i}monomer.No.electronsraw" for i in range(1, 21)]].to_numpy(float)
```
**Plain English:** Store a value: the name `mat` now holds the result of `df[[f"p{i}monomer.No.electronsraw" for i in range(1, 21)]].to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 80
```python
    seqs = ["".join(ELECTRONS_TO_BASE.get(v, "N") for v in row) for row in mat]
```
**Plain English:** Lookup table: valence-electron count → DNA letter. 42→C, 48→T, 50→A, 56→G. This is how hidden sequences are decoded from the matrix.

### Line 81
```python
    out = pd.DataFrame({
```
**Plain English:** Store a value: the name `out` now holds the result of `pd.DataFrame({`. Whenever you later write that name, you mean this value.

### Line 82
```python
        config.ID_COL: df[config.ID_COL].astype(str),
```
**Plain English:** Run this instruction: `config.ID_COL: df[config.ID_COL].astype(str),`.

### Line 83
```python
        "y": pd.to_numeric(df[config.TARGET_COL], errors="coerce"),
```
**Plain English:** Run this instruction: `"y": pd.to_numeric(df[config.TARGET_COL], errors="coerce"),`.

### Line 84
```python
        "protospacer": seqs,
```
**Plain English:** Run this instruction: `"protospacer": seqs,`.

### Line 85
```python
    })
```
**Plain English:** Run this instruction: `})`.

### Line 86
```python
    out["decoded_ok"] = ~out["protospacer"].str.contains("N")
```
**Plain English:** Store a value: the name `out["decoded_ok"]` now holds the result of `~out["protospacer"].str.contains("N")`. Whenever you later write that name, you mean this value.

### Line 87
```python
    out.to_csv(path, index=False)
```
**Plain English:** Run this instruction: `out.to_csv(path, index=False)`.

### Line 88
```python
    print(f"  decoded {len(out):,}  ok={int(out.decoded_ok.sum()):,}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  decoded {len(out):,}  ok={int(out.decoded_ok.sum()):,}", flush=True)`.

### Line 89
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 92
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 93
```python
# 2. Locate on hg38
```
**Plain English:** Human-only note (Python ignores it): 2. Locate on hg38

### Line 94
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 97
```python
def iter_fasta(path: Path):
```
**Plain English:** Defines a reusable recipe named `iter_fasta`. Inputs in parentheses: `path: Path`. Nothing runs yet until something *calls* `iter_fasta(...)`.

### Line 98
```python
    """Yield (header, sequence) from .fa or .fa.gz."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Yield (header, sequence) from .fa or .fa.gz.

### Line 99
```python
    opener = gzip.open if str(path).endswith(".gz") else open
```
**Plain English:** Store a value: the name `opener` now holds the result of `gzip.open if str(path).endswith(".gz") else open`. Whenever you later write that name, you mean this value.

### Line 100
```python
    mode = "rt"
```
**Plain English:** Store a value: the name `mode` now holds the result of `"rt"`. Whenever you later write that name, you mean this value.

### Line 101
```python
    name, chunks = None, []
```
**Plain English:** Run this instruction: `name, chunks = None, []`.

### Line 102
```python
    with opener(path, mode) as fh:
```
**Plain English:** Open a resource safely (file, etc.): `opener(path, mode) as fh`. When the indented block ends, Python closes it automatically.

### Line 103
```python
        for line in fh:
```
**Plain English:** Loop: repeat the indented block once for each item → `line in fh`.

### Line 104
```python
            if line.startswith(">"):
```
**Plain English:** Decision: run the indented block only when this condition is true → `line.startswith(">")`.

### Line 105
```python
                if name is not None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `name is not None`.

### Line 106
```python
                    yield name, "".join(chunks).upper()
```
**Plain English:** Produce one result now but pause the function so the caller can ask for the next one (a generator) → `name, "".join(chunks).upper()`.

### Line 107
```python
                name = line[1:].strip().split()[0]
```
**Plain English:** Store a value: the name `name` now holds the result of `line[1:].strip().split()[0]`. Whenever you later write that name, you mean this value.

### Line 108
```python
                chunks = []
```
**Plain English:** Store a value: the name `chunks` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 109
```python
            else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 110
```python
                chunks.append(line.strip())
```
**Plain English:** Run this instruction: `chunks.append(line.strip())`.

### Line 111
```python
        if name is not None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `name is not None`.

### Line 112
```python
            yield name, "".join(chunks).upper()
```
**Plain English:** Produce one result now but pause the function so the caller can ask for the next one (a generator) → `name, "".join(chunks).upper()`.

### Line 115
```python
def slice_linear(g: str, start: int, end: int) -> str:
```
**Plain English:** Defines a reusable recipe named `slice_linear`. Inputs in parentheses: `g: str, start: int, end: int`. Returns type hint: str. Nothing runs yet until something *calls* `slice_linear(...)`.

### Line 116
```python
    """1-based inclusive; clamp to chromosome; pad with N outside."""
```
**Plain English:** A short documentation string attached to the nearest function/module: 1-based inclusive; clamp to chromosome; pad with N outside.

### Line 117
```python
    n = len(g)
```
**Plain English:** Store a value: the name `n` now holds the result of `len(g)`. Whenever you later write that name, you mean this value.

### Line 118
```python
    out = []
```
**Plain English:** Store a value: the name `out` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 119
```python
    for pos in range(start, end + 1):
```
**Plain English:** Loop: repeat the indented block once for each item → `pos in range(start, end + 1)`.

### Line 120
```python
        if 1 <= pos <= n:
```
**Plain English:** Decision: run the indented block only when this condition is true → `1 <= pos <= n`.

### Line 121
```python
            out.append(g[pos - 1])
```
**Plain English:** Run this instruction: `out.append(g[pos - 1])`.

### Line 122
```python
        else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 123
```python
            out.append("N")
```
**Plain English:** Run this instruction: `out.append("N")`.

### Line 124
```python
    return "".join(out)
```
**Plain English:** Finish this function and send back: `"".join(out)`.

### Line 127
```python
def linear_guide_context(left: int, right: int, strand: str, flank: int, g: str) -> dict:
```
**Plain English:** Defines a reusable recipe named `linear_guide_context`. Inputs in parentheses: `left: int, right: int, strand: str, flank: int, g: str`. Returns type hint: dict. Nothing runs yet until something *calls* `linear_guide_context(...)`.

### Line 128
```python
    if strand == "+":
```
**Plain English:** Decision: run the indented block only when this condition is true → `strand == "+"`.

### Line 129
```python
        upstream = slice_linear(g, left - flank, left - 1)
```
**Plain English:** Store a value: the name `upstream` now holds the result of `slice_linear(g, left - flank, left - 1)`. Whenever you later write that name, you mean this value.

### Line 130
```python
        proto = slice_linear(g, left, right)
```
**Plain English:** Store a value: the name `proto` now holds the result of `slice_linear(g, left, right)`. Whenever you later write that name, you mean this value.

### Line 131
```python
        pam = slice_linear(g, right + 1, right + 3)
```
**Plain English:** Store a value: the name `pam` now holds the result of `slice_linear(g, right + 1, right + 3)`. Whenever you later write that name, you mean this value.

### Line 132
```python
        downstream = slice_linear(g, right + 4, right + 3 + flank)
```
**Plain English:** Store a value: the name `downstream` now holds the result of `slice_linear(g, right + 4, right + 3 + flank)`. Whenever you later write that name, you mean this value.

### Line 133
```python
    else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 134
```python
        upstream = REVCOMP(slice_linear(g, right + 1, right + flank))
```
**Plain English:** Store a value: the name `upstream` now holds the result of `REVCOMP(slice_linear(g, right + 1, right + flank))`. Whenever you later write that name, you mean this value.

### Line 135
```python
        proto = REVCOMP(slice_linear(g, left, right))
```
**Plain English:** Store a value: the name `proto` now holds the result of `REVCOMP(slice_linear(g, left, right))`. Whenever you later write that name, you mean this value.

### Line 136
```python
        pam = REVCOMP(slice_linear(g, left - 3, left - 1))
```
**Plain English:** Store a value: the name `pam` now holds the result of `REVCOMP(slice_linear(g, left - 3, left - 1))`. Whenever you later write that name, you mean this value.

### Line 137
```python
        downstream = REVCOMP(slice_linear(g, left - 3 - flank, left - 4))
```
**Plain English:** Store a value: the name `downstream` now holds the result of `REVCOMP(slice_linear(g, left - 3 - flank, left - 4))`. Whenever you later write that name, you mean this value.

### Line 138
```python
    return dict(upstream=upstream, protospacer=proto, pam=pam, downstream=downstream)
```
**Plain English:** Finish this function and send back: `dict(upstream=upstream, protospacer=proto, pam=pam, downstream=downstream)`.

### Line 141
```python
def locate_on_hg38(decoded: pd.DataFrame, force: bool = False) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `locate_on_hg38`. Inputs in parentheses: `decoded: pd.DataFrame, force: bool = False`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `locate_on_hg38(...)`.

### Lines 142–145
```python
    """Single-pass locate: scan each primary chrom, cut flanks, discard chrom.

    Keeps RAM under ~1× largest chromosome (~250 MB), not full hg38.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 146
```python
    path = CACHE / "human_located.csv"
```
**Plain English:** Store a value: the name `path` now holds the result of `CACHE / "human_located.csv"`. Whenever you later write that name, you mean this value.

### Line 147
```python
    if path.exists() and not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `path.exists() and not force`.

### Line 148
```python
        print(f"  cached locate {path}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  cached locate {path}", flush=True)`.

### Line 149
```python
        return pd.read_csv(path)
```
**Plain English:** Finish this function and send back: `pd.read_csv(path)`.

### Line 151
```python
    fasta = HG38_FA if HG38_FA.exists() else HG38_GZ
```
**Plain English:** Store a value: the name `fasta` now holds the result of `HG38_FA if HG38_FA.exists() else HG38_GZ`. Whenever you later write that name, you mean this value.

### Line 152
```python
    if not fasta.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not fasta.exists()`.

### Line 153
```python
        raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 154
```python
            f"Need {HG38_FA} or {HG38_GZ}. Download hg38.fa.gz from UCSC."
```
**Plain English:** Run this instruction: `f"Need {HG38_FA} or {HG38_GZ}. Download hg38.fa.gz from UCSC."`.

### Line 155
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 157
```python
    wanted = set(decoded.loc[decoded.decoded_ok, "protospacer"].astype(str))
```
**Plain English:** Store a value: the name `wanted` now holds the result of `set(decoded.loc[decoded.decoded_ok, "protospacer"].astype(str))`. Whenever you later write that name, you mean this value.

### Line 158
```python
    # proto -> list of hit dicts (without flanks yet); flanks filled when unique
```
**Plain English:** Human-only note (Python ignores it): proto -> list of hit dicts (without flanks yet); flanks filled when unique

### Line 159
```python
    hits: dict[str, list[dict]] = {s: [] for s in wanted}
```
**Plain English:** Run this instruction: `hits: dict[str, list[dict]] = {s: [] for s in wanted}`.

### Line 160
```python
    primary = {f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY", "chrM"}
```
**Plain English:** Store a value: the name `primary` now holds the result of `{f"chr{i}" for i in range(1, 23)} | {"chrX", "chrY", "chrM"}`. Whenever you later write that name, you mean this value.

### Line 161
```python
    # stash flank contexts for the first hit; invalidate if a second appears
```
**Plain English:** Human-only note (Python ignores it): stash flank contexts for the first hit; invalidate if a second appears

### Line 162
```python
    ctx_by_proto: dict[str, dict] = {}
```
**Plain English:** Run this instruction: `ctx_by_proto: dict[str, dict] = {}`.

### Line 163
```python
    multi = set()
```
**Plain English:** Store a value: the name `multi` now holds the result of `set()`. Whenever you later write that name, you mean this value.

### Line 165
```python
    print(f"  locating {len(wanted):,} unique protospacers on {fasta.name} "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  locating {len(wanted):,} unique protospacers on {fasta.name} "`.

### Line 166
```python
          f"(single-pass) ...", flush=True)
```
**Plain English:** Run this instruction: `f"(single-pass) ...", flush=True)`.

### Line 167
```python
    t0 = time.time()
```
**Plain English:** Store a value: the name `t0` now holds the result of `time.time()`. Whenever you later write that name, you mean this value.

### Line 168
```python
    for chrom, seq in iter_fasta(fasta):
```
**Plain English:** Loop: repeat the indented block once for each item → `chrom, seq in iter_fasta(fasta)`.

### Line 169
```python
        chrom_n = chrom
```
**Plain English:** Store a value: the name `chrom_n` now holds the result of `chrom`. Whenever you later write that name, you mean this value.

### Line 170
```python
        if chrom not in primary:
```
**Plain English:** Decision: run the indented block only when this condition is true → `chrom not in primary`.

### Line 171
```python
            chrom_n = (f"chr{chrom}" if chrom.isdigit() or chrom in ("X", "Y", "M")
```
**Plain English:** Store a value: the name `chrom_n` now holds the result of `(f"chr{chrom}" if chrom.isdigit() or chrom in ("X", "Y", "M")`. Whenever you later write that name, you mean this value.

### Line 172
```python
                       else chrom)
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 173
```python
        if chrom_n not in primary:
```
**Plain English:** Decision: run the indented block only when this condition is true → `chrom_n not in primary`.

### Line 174
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 175
```python
        n = len(seq)
```
**Plain English:** Store a value: the name `n` now holds the result of `len(seq)`. Whenever you later write that name, you mean this value.

### Line 176
```python
        print(f"    scanning {chrom_n} ({n:,} bp) ...", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"    scanning {chrom_n} ({n:,} bp) ...", flush=True)`.

### Line 178
```python
        def record(proto, strand, left, right, pam):
```
**Plain English:** Defines a reusable recipe named `record`. Inputs in parentheses: `proto, strand, left, right, pam`. Nothing runs yet until something *calls* `record(...)`.

### Line 179
```python
            if proto in multi:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto in multi`.

### Line 180
```python
                return
```
**Plain English:** Finish this function and send back: `(nothing / None)`.

### Line 181
```python
            if pam[1:] != "GG":
```
**Plain English:** Decision: run the indented block only when this condition is true → `pam[1:] != "GG"`.

### Line 182
```python
                return
```
**Plain English:** Finish this function and send back: `(nothing / None)`.

### Line 183
```python
            h = dict(chrom=chrom_n, strand=strand, left=left, right=right, pam=pam)
```
**Plain English:** Store a value: the name `h` now holds the result of `dict(chrom=chrom_n, strand=strand, left=left, right=right, pam=pam)`. Whenever you later write that name, you mean this value.

### Line 184
```python
            if proto in ctx_by_proto:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto in ctx_by_proto`.

### Line 185
```python
                # second genomic copy → ambiguous flanks; drop
```
**Plain English:** Human-only note (Python ignores it): second genomic copy → ambiguous flanks; drop

### Line 186
```python
                multi.add(proto)
```
**Plain English:** Second genomic hit for the same 20-mer → mark as multi-copy and drop flanks (ambiguous which locus’s DNA to use).

### Line 187
```python
                ctx_by_proto.pop(proto, None)
```
**Plain English:** Run this instruction: `ctx_by_proto.pop(proto, None)`.

### Line 188
```python
                hits[proto].append(h)
```
**Plain English:** Run this instruction: `hits[proto].append(h)`.

### Line 189
```python
                return
```
**Plain English:** Finish this function and send back: `(nothing / None)`.

### Line 190
```python
            hits[proto].append(h)
```
**Plain English:** Run this instruction: `hits[proto].append(h)`.

### Line 191
```python
            ctx = linear_guide_context(left, right, strand, FLANK, seq)
```
**Plain English:** Store a value: the name `ctx` now holds the result of `linear_guide_context(left, right, strand, FLANK, seq)`. Whenever you later write that name, you mean this value.

### Line 192
```python
            ctx_by_proto[proto] = dict(h, **ctx)
```
**Plain English:** Store a value: the name `ctx_by_proto[proto]` now holds the result of `dict(h, **ctx)`. Whenever you later write that name, you mean this value.

### Line 194
```python
        i = seq.find("GG")
```
**Plain English:** Scan this chromosome for every `GG` (forward PAM candidate). Then check whether the 20 letters before it are a wanted protospacer.

### Line 195
```python
        while i >= 0:
```
**Plain English:** Loop: keep repeating while this stays true → `i >= 0`.

### Line 196
```python
            pam0 = i - 1
```
**Plain English:** Store a value: the name `pam0` now holds the result of `i - 1`. Whenever you later write that name, you mean this value.

### Line 197
```python
            proto0 = pam0 - 20
```
**Plain English:** Store a value: the name `proto0` now holds the result of `pam0 - 20`. Whenever you later write that name, you mean this value.

### Line 198
```python
            if proto0 >= 0:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto0 >= 0`.

### Line 199
```python
                proto = seq[proto0: proto0 + 20]
```
**Plain English:** Store a value: the name `proto` now holds the result of `seq[proto0: proto0 + 20]`. Whenever you later write that name, you mean this value.

### Line 200
```python
                if proto in wanted:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto in wanted`.

### Line 201
```python
                    left = proto0 + 1
```
**Plain English:** Store a value: the name `left` now holds the result of `proto0 + 1`. Whenever you later write that name, you mean this value.

### Line 202
```python
                    right = left + 19
```
**Plain English:** Store a value: the name `right` now holds the result of `left + 19`. Whenever you later write that name, you mean this value.

### Line 203
```python
                    pam = seq[right: right + 3]
```
**Plain English:** Store a value: the name `pam` now holds the result of `seq[right: right + 3]`. Whenever you later write that name, you mean this value.

### Line 204
```python
                    if len(pam) == 3:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(pam) == 3`.

### Line 205
```python
                        record(proto, "+", left, right, pam)
```
**Plain English:** Run this instruction: `record(proto, "+", left, right, pam)`.

### Line 206
```python
            i = seq.find("GG", i + 1)
```
**Plain English:** Store a value: the name `i` now holds the result of `seq.find("GG", i + 1)`. Whenever you later write that name, you mean this value.

### Line 208
```python
        i = seq.find("CC")
```
**Plain English:** Scan for `CC` (reverse-strand PAM candidate). Reverse-complement the DNA to recover the guide’s 20-mer.

### Line 209
```python
        while i >= 0:
```
**Plain English:** Loop: keep repeating while this stays true → `i >= 0`.

### Line 210
```python
            proto0 = i + 3
```
**Plain English:** Store a value: the name `proto0` now holds the result of `i + 3`. Whenever you later write that name, you mean this value.

### Line 211
```python
            if proto0 + 20 <= n:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto0 + 20 <= n`.

### Line 212
```python
                proto = REVCOMP(seq[proto0: proto0 + 20])
```
**Plain English:** Store a value: the name `proto` now holds the result of `REVCOMP(seq[proto0: proto0 + 20])`. Whenever you later write that name, you mean this value.

### Line 213
```python
                if proto in wanted:
```
**Plain English:** Decision: run the indented block only when this condition is true → `proto in wanted`.

### Line 214
```python
                    left = proto0 + 1
```
**Plain English:** Store a value: the name `left` now holds the result of `proto0 + 1`. Whenever you later write that name, you mean this value.

### Line 215
```python
                    right = left + 19
```
**Plain English:** Store a value: the name `right` now holds the result of `left + 19`. Whenever you later write that name, you mean this value.

### Line 216
```python
                    pam = REVCOMP(seq[i: i + 3])
```
**Plain English:** Store a value: the name `pam` now holds the result of `REVCOMP(seq[i: i + 3])`. Whenever you later write that name, you mean this value.

### Line 217
```python
                    record(proto, "-", left, right, pam)
```
**Plain English:** Run this instruction: `record(proto, "-", left, right, pam)`.

### Line 218
```python
            i = seq.find("CC", i + 1)
```
**Plain English:** Store a value: the name `i` now holds the result of `seq.find("CC", i + 1)`. Whenever you later write that name, you mean this value.

### Line 219
```python
        print(f"      unique-so-far={len(ctx_by_proto):,}  multi={len(multi):,}  "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"      unique-so-far={len(ctx_by_proto):,}  multi={len(multi):,}  "`.

### Line 220
```python
              f"elapsed {time.time()-t0:.0f}s", flush=True)
```
**Plain English:** Run this instruction: `f"elapsed {time.time()-t0:.0f}s", flush=True)`.

### Line 221
```python
        del seq  # free chromosome
```
**Plain English:** Run this instruction: `del seq  # free chromosome`.

### Line 223
```python
    audit = dict(
```
**Plain English:** Store a value: the name `audit` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 224
```python
        n_wanted=len(wanted),
```
**Plain English:** Store a value: the name `n_wanted` now holds the result of `len(wanted),`. Whenever you later write that name, you mean this value.

### Line 225
```python
        n_unique=len(ctx_by_proto),
```
**Plain English:** Store a value: the name `n_unique` now holds the result of `len(ctx_by_proto),`. Whenever you later write that name, you mean this value.

### Line 226
```python
        n_multi=len(multi),
```
**Plain English:** Store a value: the name `n_multi` now holds the result of `len(multi),`. Whenever you later write that name, you mean this value.

### Line 227
```python
        n_missing=len(wanted) - len(ctx_by_proto) - len(multi),
```
**Plain English:** Store a value: the name `n_missing` now holds the result of `len(wanted) - len(ctx_by_proto) - len(multi),`. Whenever you later write that name, you mean this value.

### Line 228
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 229
```python
    print(f"  locate audit: {json.dumps(audit)}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  locate audit: {json.dumps(audit)}", flush=True)`.

### Line 230
```python
    (OUT / "human_locate_audit.json").write_text(json.dumps(audit, indent=2))
```
**Plain English:** Store a value: the name `(OUT / "human_locate_audit.json").write_text(json.dumps(audit, indent` now holds the result of `2))`. Whenever you later write that name, you mean this value.

### Line 232
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 233
```python
    for _, r in decoded.iterrows():
```
**Plain English:** Loop: repeat the indented block once for each item → `_, r in decoded.iterrows()`.

### Line 234
```python
        if not r["decoded_ok"]:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not r["decoded_ok"]`.

### Line 235
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 236
```python
        proto = r["protospacer"]
```
**Plain English:** Store a value: the name `proto` now holds the result of `r["protospacer"]`. Whenever you later write that name, you mean this value.

### Line 237
```python
        ctx = ctx_by_proto.get(proto)
```
**Plain English:** Store a value: the name `ctx` now holds the result of `ctx_by_proto.get(proto)`. Whenever you later write that name, you mean this value.

### Line 238
```python
        if ctx is None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `ctx is None`.

### Line 239
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 240
```python
        rows.append(dict(
```
**Plain English:** Run this instruction: `rows.append(dict(`.

### Line 241
```python
            sgRNAID=r[config.ID_COL],
```
**Plain English:** Store a value: the name `sgRNAID` now holds the result of `r[config.ID_COL],`. Whenever you later write that name, you mean this value.

### Line 242
```python
            y=float(r["y"]) if np.isfinite(r["y"]) else np.nan,
```
**Plain English:** Store a value: the name `y` now holds the result of `float(r["y"]) if np.isfinite(r["y"]) else np.nan,`. Whenever you later write that name, you mean this value.

### Line 243
```python
            protospacer=ctx["protospacer"],
```
**Plain English:** Store a value: the name `protospacer` now holds the result of `ctx["protospacer"],`. Whenever you later write that name, you mean this value.

### Line 244
```python
            pam=ctx["pam"],
```
**Plain English:** Store a value: the name `pam` now holds the result of `ctx["pam"],`. Whenever you later write that name, you mean this value.

### Line 245
```python
            upstream=ctx["upstream"],
```
**Plain English:** Store a value: the name `upstream` now holds the result of `ctx["upstream"],`. Whenever you later write that name, you mean this value.

### Line 246
```python
            downstream=ctx["downstream"],
```
**Plain English:** Store a value: the name `downstream` now holds the result of `ctx["downstream"],`. Whenever you later write that name, you mean this value.

### Line 247
```python
            chrom=ctx["chrom"],
```
**Plain English:** Store a value: the name `chrom` now holds the result of `ctx["chrom"],`. Whenever you later write that name, you mean this value.

### Line 248
```python
            strand=ctx["strand"],
```
**Plain English:** Store a value: the name `strand` now holds the result of `ctx["strand"],`. Whenever you later write that name, you mean this value.

### Line 249
```python
            left=ctx["left"],
```
**Plain English:** Store a value: the name `left` now holds the result of `ctx["left"],`. Whenever you later write that name, you mean this value.

### Line 250
```python
            right=ctx["right"],
```
**Plain English:** Store a value: the name `right` now holds the result of `ctx["right"],`. Whenever you later write that name, you mean this value.

### Line 251
```python
            located=True,
```
**Plain English:** Store a value: the name `located` now holds the result of `True,`. Whenever you later write that name, you mean this value.

### Line 252
```python
            unique=True,
```
**Plain English:** Store a value: the name `unique` now holds the result of `True,`. Whenever you later write that name, you mean this value.

### Line 253
```python
        ))
```
**Plain English:** Run this instruction: `))`.

### Line 255
```python
    loc = pd.DataFrame(rows)
```
**Plain English:** Store a value: the name `loc` now holds the result of `pd.DataFrame(rows)`. Whenever you later write that name, you mean this value.

### Line 256
```python
    loc.to_csv(path, index=False)
```
**Plain English:** Run this instruction: `loc.to_csv(path, index=False)`.

### Line 257
```python
    print(f"  located unique usable: {len(loc):,}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  located unique usable: {len(loc):,}", flush=True)`.

### Line 258
```python
    return loc
```
**Plain English:** Finish this function and send back: `loc`.

### Line 261
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 262
```python
# 3. Build matrices
```
**Plain English:** Human-only note (Python ignores it): 3. Build matrices

### Line 263
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 266
```python
def build_human_matrices(loc: pd.DataFrame, force: bool = False):
```
**Plain English:** Defines a reusable recipe named `build_human_matrices`. Inputs in parentheses: `loc: pd.DataFrame, force: bool = False`. Nothing runs yet until something *calls* `build_human_matrices(...)`.

### Line 267
```python
    x_base = CACHE / "X_human_base.npy"
```
**Plain English:** Store a value: the name `x_base` now holds the result of `CACHE / "X_human_base.npy"`. Whenever you later write that name, you mean this value.

### Line 268
```python
    x_full = CACHE / "X_human_base_a.npy"
```
**Plain English:** Store a value: the name `x_full` now holds the result of `CACHE / "X_human_base_a.npy"`. Whenever you later write that name, you mean this value.

### Line 269
```python
    meta_path = CACHE / "meta_human.json"
```
**Plain English:** Store a value: the name `meta_path` now holds the result of `CACHE / "meta_human.json"`. Whenever you later write that name, you mean this value.

### Line 270
```python
    flank_path = CACHE / "a_flank_human.csv"
```
**Plain English:** Store a value: the name `flank_path` now holds the result of `CACHE / "a_flank_human.csv"`. Whenever you later write that name, you mean this value.

### Line 272
```python
    if x_full.exists() and meta_path.exists() and not force:
```
**Plain English:** Decision: run the indented block only when this condition is true → `x_full.exists() and meta_path.exists() and not force`.

### Line 273
```python
        meta = json.loads(meta_path.read_text())
```
**Plain English:** Store a value: the name `meta` now holds the result of `json.loads(meta_path.read_text())`. Whenever you later write that name, you mean this value.

### Line 274
```python
        print(f"  cached matrices {meta['n']} x {meta['n_full']}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  cached matrices {meta['n']} x {meta['n_full']}", flush=True)`.

### Line 275
```python
        return (
```
**Plain English:** Finish this function and send back: `(`.

### Line 276
```python
            np.load(x_base), np.load(x_full),
```
**Plain English:** Run this instruction: `np.load(x_base), np.load(x_full),`.

### Line 277
```python
            np.asarray(meta["y"], float),
```
**Plain English:** Run this instruction: `np.asarray(meta["y"], float),`.

### Line 278
```python
            meta["base_names"], meta["full_names"], meta,
```
**Plain English:** Run this instruction: `meta["base_names"], meta["full_names"], meta,`.

### Line 279
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 281
```python
    print(f"  featurising base for {len(loc):,} human guides ...", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  featurising base for {len(loc):,} human guides ...", flush=True)`.

### Line 282
```python
    base, base_names = featurise.matrix(loc["protospacer"].tolist(), verbose=True)
```
**Plain English:** Run this instruction: `base, base_names = featurise.matrix(loc["protospacer"].tolist(), verbose=True)`.

### Line 283
```python
    base = np.asarray(base, np.float32)
```
**Plain English:** Store a value: the name `base` now holds the result of `np.asarray(base, np.float32)`. Whenever you later write that name, you mean this value.

### Line 284
```python
    base_names = list(base_names)
```
**Plain English:** Store a value: the name `base_names` now holds the result of `list(base_names)`. Whenever you later write that name, you mean this value.

### Line 286
```python
    print("  building a_flank ...", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("  building a_flank ...", flush=True)`.

### Line 287
```python
    idx = loc.copy()
```
**Plain English:** Store a value: the name `idx` now holds the result of `loc.copy()`. Whenever you later write that name, you mean this value.

### Line 288
```python
    idx[config.ID_COL] = idx["sgRNAID"]
```
**Plain English:** Store a value: the name `idx[config.ID_COL]` now holds the result of `idx["sgRNAID"]`. Whenever you later write that name, you mean this value.

### Line 289
```python
    block = a_flank.build(idx)
```
**Plain English:** Store a value: the name `block` now holds the result of `a_flank.build(idx)`. Whenever you later write that name, you mean this value.

### Line 290
```python
    block.to_csv(flank_path, index=False)
```
**Plain English:** Run this instruction: `block.to_csv(flank_path, index=False)`.

### Line 291
```python
    block = block.set_index(config.ID_COL).reindex(idx[config.ID_COL])
```
**Plain English:** Store a value: the name `block` now holds the result of `block.set_index(config.ID_COL).reindex(idx[config.ID_COL])`. Whenever you later write that name, you mean this value.

### Line 292
```python
    vals = block.to_numpy(dtype=np.float32)
```
**Plain English:** Store a value: the name `vals` now holds the result of `block.to_numpy(dtype=np.float32)`. Whenever you later write that name, you mean this value.

### Line 293
```python
    good = ~np.all(np.isnan(vals), axis=0)
```
**Plain English:** Store a value: the name `good` now holds the result of `~np.all(np.isnan(vals), axis=0)`. Whenever you later write that name, you mean this value.

### Line 294
```python
    flank_names = [c for c, k in zip(block.columns, good) if k]
```
**Plain English:** Store a value: the name `flank_names` now holds the result of `[c for c, k in zip(block.columns, good) if k]`. Whenever you later write that name, you mean this value.

### Line 295
```python
    Xf = vals[:, good]
```
**Plain English:** Store a value: the name `Xf` now holds the result of `vals[:, good]`. Whenever you later write that name, you mean this value.

### Line 296
```python
    Xfull = np.hstack([base, Xf])
```
**Plain English:** Store a value: the name `Xfull` now holds the result of `np.hstack([base, Xf])`. Whenever you later write that name, you mean this value.

### Line 297
```python
    full_names = base_names + flank_names
```
**Plain English:** Store a value: the name `full_names` now holds the result of `base_names + flank_names`. Whenever you later write that name, you mean this value.

### Line 298
```python
    family_of = ["base"] * len(base_names) + ["a_flank"] * len(flank_names)
```
**Plain English:** Store a value: the name `family_of` now holds the result of `["base"] * len(base_names) + ["a_flank"] * len(flank_names)`. Whenever you later write that name, you mean this value.

### Line 300
```python
    y = idx["y"].to_numpy(float)
```
**Plain English:** Store a value: the name `y` now holds the result of `idx["y"].to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 301
```python
    meta = dict(
```
**Plain English:** Store a value: the name `meta` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 302
```python
        y=y.tolist(),
```
**Plain English:** Store a value: the name `y` now holds the result of `y.tolist(),`. Whenever you later write that name, you mean this value.

### Line 303
```python
        base_names=base_names,
```
**Plain English:** Store a value: the name `base_names` now holds the result of `base_names,`. Whenever you later write that name, you mean this value.

### Line 304
```python
        full_names=full_names,
```
**Plain English:** Store a value: the name `full_names` now holds the result of `full_names,`. Whenever you later write that name, you mean this value.

### Line 305
```python
        family_of=family_of,
```
**Plain English:** Store a value: the name `family_of` now holds the result of `family_of,`. Whenever you later write that name, you mean this value.

### Line 306
```python
        n_base=len(base_names),
```
**Plain English:** Store a value: the name `n_base` now holds the result of `len(base_names),`. Whenever you later write that name, you mean this value.

### Line 307
```python
        n_full=int(Xfull.shape[1]),
```
**Plain English:** Store a value: the name `n_full` now holds the result of `int(Xfull.shape[1]),`. Whenever you later write that name, you mean this value.

### Line 308
```python
        n=int(len(idx)),
```
**Plain English:** Store a value: the name `n` now holds the result of `int(len(idx)),`. Whenever you later write that name, you mean this value.

### Line 309
```python
        ids=idx[config.ID_COL].astype(str).tolist(),
```
**Plain English:** Store a value: the name `ids` now holds the result of `idx[config.ID_COL].astype(str).tolist(),`. Whenever you later write that name, you mean this value.

### Line 310
```python
        spacer_gc=[(s.count("G") + s.count("C")) / 20 for s in idx["protospacer"]],
```
**Plain English:** Store a value: the name `spacer_gc` now holds the result of `[(s.count("G") + s.count("C")) / 20 for s in idx["protospacer"]],`. Whenever you later write that name, you mean this value.

### Line 311
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 312
```python
    np.save(x_base, base)
```
**Plain English:** Run this instruction: `np.save(x_base, base)`.

### Line 313
```python
    np.save(x_full, Xfull)
```
**Plain English:** Run this instruction: `np.save(x_full, Xfull)`.

### Line 314
```python
    meta_path.write_text(json.dumps(meta))
```
**Plain English:** Run this instruction: `meta_path.write_text(json.dumps(meta))`.

### Line 315
```python
    print(f"  built base {base.shape}  full {Xfull.shape}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  built base {base.shape}  full {Xfull.shape}", flush=True)`.

### Line 316
```python
    return base, Xfull, y, base_names, full_names, meta
```
**Plain English:** Finish this function and send back: `base, Xfull, y, base_names, full_names, meta`.

### Line 319
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 320
```python
# 4. Human-only ladder
```
**Plain English:** Human-only note (Python ignores it): 4. Human-only ladder

### Line 321
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 324
```python
def run_ladder(X_base, X_full, y, base_names, full_names, family_of, meta):
```
**Plain English:** Defines a reusable recipe named `run_ladder`. Inputs in parentheses: `X_base, X_full, y, base_names, full_names, family_of, meta`. Nothing runs yet until something *calls* `run_ladder(...)`.

### Line 325
```python
    print("=== human-only ladder ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== human-only ladder ===", flush=True)`.

### Line 326
```python
    # Also shared-column baseline from raw matrix on the SAME ids
```
**Plain English:** Human-only note (Python ignores it): Also shared-column baseline from raw matrix on the SAME ids

### Line 327
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 328
```python
    arms = {
```
**Plain English:** Store a value: the name `arms` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 329
```python
        "regenerated_base": (X_base, base_names, ["base"] * len(base_names)),
```
**Plain English:** Run this instruction: `"regenerated_base": (X_base, base_names, ["base"] * len(base_names)),`.

### Line 330
```python
        "base_plus_a_flank": (X_full, full_names, family_of),
```
**Plain English:** Run this instruction: `"base_plus_a_flank": (X_full, full_names, family_of),`.

### Line 331
```python
    }
```
**Plain English:** Run this instruction: `}`.

### Line 332
```python
    # a_flank only
```
**Plain English:** Human-only note (Python ignores it): a_flank only

### Line 333
```python
    fam = np.asarray(family_of)
```
**Plain English:** Store a value: the name `fam` now holds the result of `np.asarray(family_of)`. Whenever you later write that name, you mean this value.

### Line 334
```python
    flank_idx = np.where(fam == "a_flank")[0]
```
**Plain English:** Store a value: the name `flank_idx` now holds the result of `np.where(fam == "a_flank")[0]`. Whenever you later write that name, you mean this value.

### Line 335
```python
    if len(flank_idx):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(flank_idx)`.

### Line 336
```python
        arms["a_flank_only"] = (
```
**Plain English:** Store a value: the name `arms["a_flank_only"]` now holds the result of `(`. Whenever you later write that name, you mean this value.

### Line 337
```python
            X_full[:, flank_idx],
```
**Plain English:** Run this instruction: `X_full[:, flank_idx],`.

### Line 338
```python
            list(np.asarray(full_names)[flank_idx]),
```
**Plain English:** Run this instruction: `list(np.asarray(full_names)[flank_idx]),`.

### Line 339
```python
            ["a_flank"] * len(flank_idx),
```
**Plain English:** Run this instruction: `["a_flank"] * len(flank_idx),`.

### Line 340
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 342
```python
    ok = np.isfinite(y)
```
**Plain English:** Store a value: the name `ok` now holds the result of `np.isfinite(y)`. Whenever you later write that name, you mean this value.

### Line 343
```python
    for name, (X, names, fof) in arms.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `name, (X, names, fof) in arms.items()`.

### Line 344
```python
        print(f"  CV {name} n={ok.sum()} cols={X.shape[1]}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  CV {name} n={ok.sum()} cols={X.shape[1]}", flush=True)`.

### Line 345
```python
        res = cross_validate(
```
**Plain English:** Store a value: the name `res` now holds the result of `cross_validate(`. Whenever you later write that name, you mean this value.

### Line 346
```python
            X[ok], y[ok], list(names), np.asarray(fof),
```
**Plain English:** Run this instruction: `X[ok], y[ok], list(names), np.asarray(fof),`.

### Line 347
```python
            seeds=(SEED,), groups=None,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `(SEED,), groups=None,`. Whenever you later write that name, you mean this value.

### Line 348
```python
            tag=f"human_{name}", experiment=name, verbose=True,
```
**Plain English:** Store a value: the name `tag` now holds the result of `f"human_{name}", experiment=name, verbose=True,`. Whenever you later write that name, you mean this value.

### Line 349
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 350
```python
        s = res["summary"]
```
**Plain English:** Store a value: the name `s` now holds the result of `res["summary"]`. Whenever you later write that name, you mean this value.

### Line 351
```python
        rows.append(dict(
```
**Plain English:** Run this instruction: `rows.append(dict(`.

### Line 352
```python
            arm=name, n=int(ok.sum()), n_cols=int(X.shape[1]),
```
**Plain English:** Store a value: the name `arm` now holds the result of `name, n=int(ok.sum()), n_cols=int(X.shape[1]),`. Whenever you later write that name, you mean this value.

### Line 353
```python
            spearman=s["spearman"]["mean"], r2=s["r2"]["mean"],
```
**Plain English:** Store a value: the name `spearman` now holds the result of `s["spearman"]["mean"], r2=s["r2"]["mean"],`. Whenever you later write that name, you mean this value.

### Line 354
```python
        ))
```
**Plain English:** Run this instruction: `))`.

### Line 356
```python
    # shared-column arm from published human matrix (same IDs)
```
**Plain English:** Human-only note (Python ignores it): shared-column arm from published human matrix (same IDs)

### Line 357
```python
    print("  building shared-column matrix for located IDs ...", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("  building shared-column matrix for located IDs ...", flush=True)`.

### Line 358
```python
    eco = pd.read_csv(
```
**Plain English:** Store a value: the name `eco` now holds the result of `pd.read_csv(`. Whenever you later write that name, you mean this value.

### Line 359
```python
        config.BASE_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, nrows=0
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 360
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 361
```python
    hum = pd.read_csv(HUMAN_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, low_memory=False)
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 362
```python
    drop = {config.TARGET_COL, config.ID_COL}
```
**Plain English:** Store a value: the name `drop` now holds the result of `{config.TARGET_COL, config.ID_COL}`. Whenever you later write that name, you mean this value.

### Line 363
```python
    shared = sorted((set(eco.columns) & set(hum.columns)) - drop)
```
**Plain English:** Store a value: the name `shared` now holds the result of `sorted((set(eco.columns) & set(hum.columns)) - drop)`. Whenever you later write that name, you mean this value.

### Line 364
```python
    ids = list(meta["ids"])
```
**Plain English:** Store a value: the name `ids` now holds the result of `list(meta["ids"])`. Whenever you later write that name, you mean this value.

### Line 365
```python
    hum = hum.set_index(config.ID_COL).loc[ids]
```
**Plain English:** Store a value: the name `hum` now holds the result of `hum.set_index(config.ID_COL).loc[ids]`. Whenever you later write that name, you mean this value.

### Line 366
```python
    Xs = hum[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)
```
**Plain English:** Store a value: the name `Xs` now holds the result of `hum[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)`. Whenever you later write that name, you mean this value.

### Line 367
```python
    print(f"  CV shared_published_cols n={ok.sum()} cols={Xs.shape[1]}", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"  CV shared_published_cols n={ok.sum()} cols={Xs.shape[1]}", flush=True)`.

### Line 368
```python
    res = cross_validate(
```
**Plain English:** Store a value: the name `res` now holds the result of `cross_validate(`. Whenever you later write that name, you mean this value.

### Line 369
```python
        Xs[ok], y[ok], shared, np.array(["shared"] * len(shared)),
```
**Plain English:** Run this instruction: `Xs[ok], y[ok], shared, np.array(["shared"] * len(shared)),`.

### Line 370
```python
        seeds=(SEED,), groups=None,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `(SEED,), groups=None,`. Whenever you later write that name, you mean this value.

### Line 371
```python
        tag="human_shared", experiment="shared", verbose=True,
```
**Plain English:** Store a value: the name `tag` now holds the result of `"human_shared", experiment="shared", verbose=True,`. Whenever you later write that name, you mean this value.

### Line 372
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 373
```python
    s = res["summary"]
```
**Plain English:** Store a value: the name `s` now holds the result of `res["summary"]`. Whenever you later write that name, you mean this value.

### Line 374
```python
    rows.append(dict(
```
**Plain English:** Run this instruction: `rows.append(dict(`.

### Line 375
```python
        arm="shared_published_cols", n=int(ok.sum()), n_cols=len(shared),
```
**Plain English:** Store a value: the name `arm` now holds the result of `"shared_published_cols", n=int(ok.sum()), n_cols=len(shared),`. Whenever you later write that name, you mean this value.

### Line 376
```python
        spearman=s["spearman"]["mean"], r2=s["r2"]["mean"],
```
**Plain English:** Store a value: the name `spearman` now holds the result of `s["spearman"]["mean"], r2=s["r2"]["mean"],`. Whenever you later write that name, you mean this value.

### Line 377
```python
    ))
```
**Plain English:** Run this instruction: `))`.

### Line 379
```python
    df = pd.DataFrame(rows)
```
**Plain English:** Store a value: the name `df` now holds the result of `pd.DataFrame(rows)`. Whenever you later write that name, you mean this value.

### Line 380
```python
    df.to_csv(OUT / "human_ladder.csv", index=False)
```
**Plain English:** Run this instruction: `df.to_csv(OUT / "human_ladder.csv", index=False)`.

### Line 381
```python
    print(df.to_string(index=False), flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(df.to_string(index=False), flush=True)`.

### Line 382
```python
    return df
```
**Plain English:** Finish this function and send back: `df`.

### Line 385
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 386
```python
# 5. Transfer autopsy
```
**Plain English:** Human-only note (Python ignores it): 5. Transfer autopsy

### Line 387
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 390
```python
def transfer_autopsy(meta, X_full, y, full_names, family_of):
```
**Plain English:** Defines a reusable recipe named `transfer_autopsy`. Inputs in parentheses: `meta, X_full, y, full_names, family_of`. Nothing runs yet until something *calls* `transfer_autopsy(...)`.

### Line 391
```python
    """Train on E. coli (shared cols), predict human; stratify errors by GC."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Train on E. coli (shared cols), predict human; stratify errors by GC.

### Line 392
```python
    print("=== transfer autopsy ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== transfer autopsy ===", flush=True)`.

### Line 393
```python
    import xgboost as xgb
```
**Plain English:** Load toolbox code: `import xgboost as xgb` — used here for **the gradient-boosted tree learner**.

### Line 395
```python
    eco = pd.read_csv(
```
**Plain English:** Store a value: the name `eco` now holds the result of `pd.read_csv(`. Whenever you later write that name, you mean this value.

### Line 396
```python
        config.BASE_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, low_memory=False
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 397
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 398
```python
    hum = pd.read_csv(HUMAN_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, low_memory=False)
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 399
```python
    drop = {config.TARGET_COL, config.ID_COL}
```
**Plain English:** Store a value: the name `drop` now holds the result of `{config.TARGET_COL, config.ID_COL}`. Whenever you later write that name, you mean this value.

### Line 400
```python
    shared = sorted((set(eco.columns) & set(hum.columns)) - drop)
```
**Plain English:** Store a value: the name `shared` now holds the result of `sorted((set(eco.columns) & set(hum.columns)) - drop)`. Whenever you later write that name, you mean this value.

### Line 402
```python
    ye = pd.to_numeric(eco[config.TARGET_COL], errors="coerce").to_numpy(float)
```
**Plain English:** Store a value: the name `ye` now holds the result of `pd.to_numeric(eco[config.TARGET_COL], errors="coerce").to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 403
```python
    Xe = eco[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)
```
**Plain English:** Store a value: the name `Xe` now holds the result of `eco[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)`. Whenever you later write that name, you mean this value.

### Line 404
```python
    ok_e = np.isfinite(ye)
```
**Plain English:** Store a value: the name `ok_e` now holds the result of `np.isfinite(ye)`. Whenever you later write that name, you mean this value.

### Line 405
```python
    Xe, ye = Xe[ok_e], ye[ok_e]
```
**Plain English:** Run this instruction: `Xe, ye = Xe[ok_e], ye[ok_e]`.

### Line 407
```python
    ids = list(meta["ids"])
```
**Plain English:** Store a value: the name `ids` now holds the result of `list(meta["ids"])`. Whenever you later write that name, you mean this value.

### Line 408
```python
    hum_i = hum.set_index(config.ID_COL).loc[ids]
```
**Plain English:** Store a value: the name `hum_i` now holds the result of `hum.set_index(config.ID_COL).loc[ids]`. Whenever you later write that name, you mean this value.

### Line 409
```python
    Xh = hum_i[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)
```
**Plain English:** Store a value: the name `Xh` now holds the result of `hum_i[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)`. Whenever you later write that name, you mean this value.

### Line 410
```python
    yh = np.asarray(y, float)
```
**Plain English:** Store a value: the name `yh` now holds the result of `np.asarray(y, float)`. Whenever you later write that name, you mean this value.

### Line 411
```python
    gc = np.asarray(meta["spacer_gc"], float)
```
**Plain English:** Store a value: the name `gc` now holds the result of `np.asarray(meta["spacer_gc"], float)`. Whenever you later write that name, you mean this value.

### Line 413
```python
    A, B = _impute(Xe, Xh)
```
**Plain English:** Run this instruction: `A, B = _impute(Xe, Xh)`.

### Line 414
```python
    # select 300
```
**Plain English:** Human-only note (Python ignores it): select 300

### Line 415
```python
    m = xgb.XGBRegressor(
```
**Plain English:** Store a value: the name `m` now holds the result of `xgb.XGBRegressor(`. Whenever you later write that name, you mean this value.

### Line 416
```python
        n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `300, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 417
```python
        colsample_bytree=0.8, random_state=SEED, n_jobs=-1, tree_method="hist",
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, random_state=SEED, n_jobs=-1, tree_method="hist",`. Whenever you later write that name, you mean this value.

### Line 418
```python
        importance_type="gain",
```
**Plain English:** Store a value: the name `importance_type` now holds the result of `"gain",`. Whenever you later write that name, you mean this value.

### Line 419
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 420
```python
    m.fit(A, ye)
```
**Plain English:** Run this instruction: `m.fit(A, ye)`.

### Line 421
```python
    top = np.argsort(m.feature_importances_)[::-1][:300]
```
**Plain English:** Store a value: the name `top` now holds the result of `np.argsort(m.feature_importances_)[::-1][:300]`. Whenever you later write that name, you mean this value.

### Line 422
```python
    m2 = xgb.XGBRegressor(
```
**Plain English:** Store a value: the name `m2` now holds the result of `xgb.XGBRegressor(`. Whenever you later write that name, you mean this value.

### Line 423
```python
        n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `400, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 424
```python
        colsample_bytree=0.8, random_state=SEED, n_jobs=-1, tree_method="hist",
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, random_state=SEED, n_jobs=-1, tree_method="hist",`. Whenever you later write that name, you mean this value.

### Line 425
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 426
```python
    m2.fit(A[:, top], ye)
```
**Plain English:** Run this instruction: `m2.fit(A[:, top], ye)`.

### Line 427
```python
    pred = np.asarray(m2.predict(B[:, top])).ravel()
```
**Plain English:** Store a value: the name `pred` now holds the result of `np.asarray(m2.predict(B[:, top])).ravel()`. Whenever you later write that name, you mean this value.

### Line 429
```python
    overall = _spearman(yh, pred)
```
**Plain English:** Store a value: the name `overall` now holds the result of `_spearman(yh, pred)`. Whenever you later write that name, you mean this value.

### Line 430
```python
    # GC deciles
```
**Plain English:** Human-only note (Python ignores it): GC deciles

### Line 431
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 432
```python
    qs = np.quantile(gc[np.isfinite(gc)], np.linspace(0, 1, 11))
```
**Plain English:** Store a value: the name `qs` now holds the result of `np.quantile(gc[np.isfinite(gc)], np.linspace(0, 1, 11))`. Whenever you later write that name, you mean this value.

### Line 433
```python
    for i in range(10):
```
**Plain English:** Loop: repeat the indented block once for each item → `i in range(10)`.

### Line 434
```python
        lo, hi = qs[i], qs[i + 1]
```
**Plain English:** Run this instruction: `lo, hi = qs[i], qs[i + 1]`.

### Line 435
```python
        if i < 9:
```
**Plain English:** Decision: run the indented block only when this condition is true → `i < 9`.

### Line 436
```python
            msk = (gc >= lo) & (gc < hi) & np.isfinite(yh)
```
**Plain English:** Store a value: the name `msk` now holds the result of `(gc >= lo) & (gc < hi) & np.isfinite(yh)`. Whenever you later write that name, you mean this value.

### Line 437
```python
        else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 438
```python
            msk = (gc >= lo) & (gc <= hi) & np.isfinite(yh)
```
**Plain English:** Store a value: the name `msk` now holds the result of `(gc >= lo) & (gc <= hi) & np.isfinite(yh)`. Whenever you later write that name, you mean this value.

### Line 439
```python
        rows.append(dict(
```
**Plain English:** Run this instruction: `rows.append(dict(`.

### Line 440
```python
            gc_decile=i + 1,
```
**Plain English:** Store a value: the name `gc_decile` now holds the result of `i + 1,`. Whenever you later write that name, you mean this value.

### Line 441
```python
            gc_lo=float(lo), gc_hi=float(hi),
```
**Plain English:** Store a value: the name `gc_lo` now holds the result of `float(lo), gc_hi=float(hi),`. Whenever you later write that name, you mean this value.

### Line 442
```python
            n=int(msk.sum()),
```
**Plain English:** Store a value: the name `n` now holds the result of `int(msk.sum()),`. Whenever you later write that name, you mean this value.

### Line 443
```python
            mean_gc=float(np.mean(gc[msk])) if msk.any() else np.nan,
```
**Plain English:** Store a value: the name `mean_gc` now holds the result of `float(np.mean(gc[msk])) if msk.any() else np.nan,`. Whenever you later write that name, you mean this value.

### Line 444
```python
            transfer_rho=_spearman(yh[msk], pred[msk]),
```
**Plain English:** Store a value: the name `transfer_rho` now holds the result of `_spearman(yh[msk], pred[msk]),`. Whenever you later write that name, you mean this value.

### Line 445
```python
            mean_y=float(np.mean(yh[msk])) if msk.any() else np.nan,
```
**Plain English:** Store a value: the name `mean_y` now holds the result of `float(np.mean(yh[msk])) if msk.any() else np.nan,`. Whenever you later write that name, you mean this value.

### Line 446
```python
            mean_pred=float(np.mean(pred[msk])) if msk.any() else np.nan,
```
**Plain English:** Store a value: the name `mean_pred` now holds the result of `float(np.mean(pred[msk])) if msk.any() else np.nan,`. Whenever you later write that name, you mean this value.

### Line 447
```python
        ))
```
**Plain English:** Run this instruction: `))`.

### Line 449
```python
    # Residualise human y and pred against GC / GC^2 — does transfer improve?
```
**Plain English:** Human-only note (Python ignores it): Residualise human y and pred against GC / GC^2 — does transfer improve?

### Line 450
```python
    ok = np.isfinite(yh) & np.isfinite(pred) & np.isfinite(gc)
```
**Plain English:** Store a value: the name `ok` now holds the result of `np.isfinite(yh) & np.isfinite(pred) & np.isfinite(gc)`. Whenever you later write that name, you mean this value.

### Line 451
```python
    Z = np.c_[gc[ok], gc[ok] ** 2]
```
**Plain English:** Store a value: the name `Z` now holds the result of `np.c_[gc[ok], gc[ok] ** 2]`. Whenever you later write that name, you mean this value.

### Line 452
```python
    # project out GC from y and pred
```
**Plain English:** Human-only note (Python ignores it): project out GC from y and pred

### Line 453
```python
    from sklearn.linear_model import LinearRegression
```
**Plain English:** Load toolbox code: `from sklearn.linear_model import LinearRegression` — used here for **classic ML helpers (splits, metrics)**.

### Line 454
```python
    ry = yh[ok] - LinearRegression().fit(Z, yh[ok]).predict(Z)
```
**Plain English:** Store a value: the name `ry` now holds the result of `yh[ok] - LinearRegression().fit(Z, yh[ok]).predict(Z)`. Whenever you later write that name, you mean this value.

### Line 455
```python
    rp = pred[ok] - LinearRegression().fit(Z, pred[ok]).predict(Z)
```
**Plain English:** Store a value: the name `rp` now holds the result of `pred[ok] - LinearRegression().fit(Z, pred[ok]).predict(Z)`. Whenever you later write that name, you mean this value.

### Line 456
```python
    rho_resid = _spearman(ry, rp)
```
**Plain English:** Store a value: the name `rho_resid` now holds the result of `_spearman(ry, rp)`. Whenever you later write that name, you mean this value.

### Line 458
```python
    # Match on GC: bin human and ecoli? Simpler: within each human GC decile,
```
**Plain English:** Human-only note (Python ignores it): Match on GC: bin human and ecoli? Simpler: within each human GC decile,

### Line 459
```python
    # report rho — already above. Also: correlation of (pred error) with GC.
```
**Plain English:** Human-only note (Python ignores it): report rho — already above. Also: correlation of (pred error) with GC.

### Line 460
```python
    err = pred - yh
```
**Plain English:** Store a value: the name `err` now holds the result of `pred - yh`. Whenever you later write that name, you mean this value.

### Line 461
```python
    rho_err_gc = _spearman(gc, err)
```
**Plain English:** Store a value: the name `rho_err_gc` now holds the result of `_spearman(gc, err)`. Whenever you later write that name, you mean this value.

### Line 463
```python
    out = dict(
```
**Plain English:** Store a value: the name `out` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 464
```python
        overall_transfer_rho=overall,
```
**Plain English:** Store a value: the name `overall_transfer_rho` now holds the result of `overall,`. Whenever you later write that name, you mean this value.

### Line 465
```python
        transfer_rho_after_residualising_gc2=rho_resid,
```
**Plain English:** Store a value: the name `transfer_rho_after_residualising_gc2` now holds the result of `rho_resid,`. Whenever you later write that name, you mean this value.

### Line 466
```python
        spearman_error_vs_spacer_gc=rho_err_gc,
```
**Plain English:** Store a value: the name `spearman_error_vs_spacer_gc` now holds the result of `rho_err_gc,`. Whenever you later write that name, you mean this value.

### Line 467
```python
        n_human=int(len(yh)),
```
**Plain English:** Store a value: the name `n_human` now holds the result of `int(len(yh)),`. Whenever you later write that name, you mean this value.

### Line 468
```python
        n_ecoli_train=int(len(ye)),
```
**Plain English:** Store a value: the name `n_ecoli_train` now holds the result of `int(len(ye)),`. Whenever you later write that name, you mean this value.

### Line 469
```python
        n_shared_cols=len(shared),
```
**Plain English:** Store a value: the name `n_shared_cols` now holds the result of `len(shared),`. Whenever you later write that name, you mean this value.

### Line 470
```python
        note=("If residualising GC² raises transfer rho toward zero/positive, "
```
**Plain English:** Store a value: the name `note` now holds the result of `("If residualising GC² raises transfer rho toward zero/positive, "`. Whenever you later write that name, you mean this value.

### Line 471
```python
              "the E. coli GC rule is a load-bearing failure mode."),
```
**Plain English:** Run this instruction: `"the E. coli GC rule is a load-bearing failure mode."),`.

### Line 472
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 473
```python
    (OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent=2))
```
**Plain English:** Store a value: the name `(OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent` now holds the result of `2))`. Whenever you later write that name, you mean this value.

### Line 474
```python
    pd.DataFrame(rows).to_csv(OUT / "transfer_autopsy_by_gc_decile.csv", index=False)
```
**Plain English:** Run this instruction: `pd.DataFrame(rows).to_csv(OUT / "transfer_autopsy_by_gc_decile.csv", index=False)`.

### Line 475
```python
    print(json.dumps(out, indent=2), flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(json.dumps(out, indent=2), flush=True)`.

### Line 476
```python
    print(pd.DataFrame(rows).to_string(index=False), flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(pd.DataFrame(rows).to_string(index=False), flush=True)`.

### Line 478
```python
    # Optional: does Family A help *within* human enough to matter for the story?
```
**Plain English:** Human-only note (Python ignores it): Optional: does Family A help *within* human enough to matter for the story?

### Line 479
```python
    if X_full is not None:
```
**Plain English:** Decision: run the indented block only when this condition is true → `X_full is not None`.

### Line 480
```python
        fam = np.asarray(family_of)
```
**Plain English:** Store a value: the name `fam` now holds the result of `np.asarray(family_of)`. Whenever you later write that name, you mean this value.

### Line 481
```python
        base_i = np.where(fam == "base")[0]
```
**Plain English:** Store a value: the name `base_i` now holds the result of `np.where(fam == "base")[0]`. Whenever you later write that name, you mean this value.

### Line 482
```python
        both_i = np.arange(X_full.shape[1])
```
**Plain English:** Store a value: the name `both_i` now holds the result of `np.arange(X_full.shape[1])`. Whenever you later write that name, you mean this value.

### Line 483
```python
        for label, cols in (("human_base_cv", base_i), ("human_base_a_cv", both_i)):
```
**Plain English:** Loop: repeat the indented block once for each item → `label, cols in (("human_base_cv", base_i), ("human_base_a_cv", both_i))`.

### Line 484
```python
            res = cross_validate(
```
**Plain English:** Store a value: the name `res` now holds the result of `cross_validate(`. Whenever you later write that name, you mean this value.

### Line 485
```python
                X_full[:, cols][ok], yh[ok],
```
**Plain English:** Run this instruction: `X_full[:, cols][ok], yh[ok],`.

### Line 486
```python
                list(np.asarray(full_names)[cols]), fam[cols],
```
**Plain English:** Run this instruction: `list(np.asarray(full_names)[cols]), fam[cols],`.

### Line 487
```python
                seeds=(SEED,), tag=label, experiment=label, verbose=True,
```
**Plain English:** Store a value: the name `seeds` now holds the result of `(SEED,), tag=label, experiment=label, verbose=True,`. Whenever you later write that name, you mean this value.

### Line 488
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 489
```python
            out[label] = res["summary"]["spearman"]["mean"]
```
**Plain English:** Store a value: the name `out[label]` now holds the result of `res["summary"]["spearman"]["mean"]`. Whenever you later write that name, you mean this value.

### Line 490
```python
        (OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent=2))
```
**Plain English:** Store a value: the name `(OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent` now holds the result of `2))`. Whenever you later write that name, you mean this value.

### Line 491
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 494
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 495
```python
# GC shape refresh on spacer GC (authoritative)
```
**Plain English:** Human-only note (Python ignores it): GC shape refresh on spacer GC (authoritative)

### Line 496
```python
# ---------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---------------------------------------------------------------------------

### Line 499
```python
def gc_shape_report(decoded: pd.DataFrame):
```
**Plain English:** Defines a reusable recipe named `gc_shape_report`. Inputs in parentheses: `decoded: pd.DataFrame`. Nothing runs yet until something *calls* `gc_shape_report(...)`.

### Line 500
```python
    from sklearn.linear_model import LinearRegression
```
**Plain English:** Load toolbox code: `from sklearn.linear_model import LinearRegression` — used here for **classic ML helpers (splits, metrics)**.

### Line 501
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 502
```python
    for label, path, decode_fn in (
```
**Plain English:** Loop: repeat the indented block once for each item → `label, path, decode_fn in (`.

### Line 503
```python
        ("human", None, None),
```
**Plain English:** Run this instruction: `("human", None, None),`.

### Line 504
```python
    ):
```
**Plain English:** Run this instruction: `):`.

### Line 505
```python
        pass
```
**Plain English:** Do nothing placeholder (keeps Python’s indentation rules happy).

### Line 506
```python
    # human from decoded
```
**Plain English:** Human-only note (Python ignores it): human from decoded

### Line 507
```python
    d = decoded[decoded.decoded_ok].copy()
```
**Plain English:** Store a value: the name `d` now holds the result of `decoded[decoded.decoded_ok].copy()`. Whenever you later write that name, you mean this value.

### Line 508
```python
    d["gc"] = d["protospacer"].map(lambda s: (s.count("G") + s.count("C")) / 20)
```
**Plain English:** Store a value: the name `d["gc"]` now holds the result of `d["protospacer"].map(lambda s: (s.count("G") + s.count("C")) / 20)`. Whenever you later write that name, you mean this value.

### Line 509
```python
    y = d["y"].to_numpy(float)
```
**Plain English:** Store a value: the name `y` now holds the result of `d["y"].to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 510
```python
    g = d["gc"].to_numpy(float)
```
**Plain English:** Store a value: the name `g` now holds the result of `d["gc"].to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 511
```python
    ok = np.isfinite(y) & np.isfinite(g)
```
**Plain English:** Store a value: the name `ok` now holds the result of `np.isfinite(y) & np.isfinite(g)`. Whenever you later write that name, you mean this value.

### Line 512
```python
    g, y = g[ok], y[ok]
```
**Plain English:** Run this instruction: `g, y = g[ok], y[ok]`.

### Line 513
```python
    Z1, Z2 = g.reshape(-1, 1), np.c_[g, g ** 2]
```
**Plain English:** Run this instruction: `Z1, Z2 = g.reshape(-1, 1), np.c_[g, g ** 2]`.

### Line 514
```python
    r1 = LinearRegression().fit(Z1, y)
```
**Plain English:** Store a value: the name `r1` now holds the result of `LinearRegression().fit(Z1, y)`. Whenever you later write that name, you mean this value.

### Line 515
```python
    r2 = LinearRegression().fit(Z2, y)
```
**Plain English:** Store a value: the name `r2` now holds the result of `LinearRegression().fit(Z2, y)`. Whenever you later write that name, you mean this value.

### Line 516
```python
    a, b = r2.coef_[1], r2.coef_[0]
```
**Plain English:** Run this instruction: `a, b = r2.coef_[1], r2.coef_[0]`.

### Line 517
```python
    turn = float(-b / (2 * a)) if a != 0 else float("nan")
```
**Plain English:** Store a value: the name `turn` now holds the result of `float(-b / (2 * a)) if a != 0 else float("nan")`. Whenever you later write that name, you mean this value.

### Line 518
```python
    pred1, pred2 = r1.predict(Z1), r2.predict(Z2)
```
**Plain English:** Run this instruction: `pred1, pred2 = r1.predict(Z1), r2.predict(Z2)`.

### Line 519
```python
    out = dict(
```
**Plain English:** Store a value: the name `out` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 520
```python
        label="human_spacer_gc",
```
**Plain English:** Store a value: the name `label` now holds the result of `"human_spacer_gc",`. Whenever you later write that name, you mean this value.

### Line 521
```python
        n=int(len(g)),
```
**Plain English:** Store a value: the name `n` now holds the result of `int(len(g)),`. Whenever you later write that name, you mean this value.

### Line 522
```python
        linear_rho=_spearman(y, pred1),
```
**Plain English:** Store a value: the name `linear_rho` now holds the result of `_spearman(y, pred1),`. Whenever you later write that name, you mean this value.

### Line 523
```python
        linear_r2=float(1 - np.mean((y - pred1) ** 2) / np.var(y)),
```
**Plain English:** Store a value: the name `linear_r2` now holds the result of `float(1 - np.mean((y - pred1) ** 2) / np.var(y)),`. Whenever you later write that name, you mean this value.

### Line 524
```python
        quadratic_r2=float(1 - np.mean((y - pred2) ** 2) / np.var(y)),
```
**Plain English:** Store a value: the name `quadratic_r2` now holds the result of `float(1 - np.mean((y - pred2) ** 2) / np.var(y)),`. Whenever you later write that name, you mean this value.

### Line 525
```python
        turning_point=turn,
```
**Plain English:** Store a value: the name `turning_point` now holds the result of `turn,`. Whenever you later write that name, you mean this value.

### Line 526
```python
        mean_gc=float(np.mean(g)),
```
**Plain English:** Store a value: the name `mean_gc` now holds the result of `float(np.mean(g)),`. Whenever you later write that name, you mean this value.

### Line 527
```python
        turning_point_data_percentile=float(np.mean(g <= turn)),
```
**Plain English:** Store a value: the name `turning_point_data_percentile` now holds the result of `float(np.mean(g <= turn)),`. Whenever you later write that name, you mean this value.

### Line 528
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 529
```python
    (OUT / "human_gc_shape.json").write_text(json.dumps(out, indent=2))
```
**Plain English:** Store a value: the name `(OUT / "human_gc_shape.json").write_text(json.dumps(out, indent` now holds the result of `2))`. Whenever you later write that name, you mean this value.

### Line 530
```python
    print("GC shape:", json.dumps(out, indent=2), flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("GC shape:", json.dumps(out, indent=2), flush=True)`.

### Line 531
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 534
```python
def main():
```
**Plain English:** Defines a reusable recipe named `main`. Inputs in parentheses: `(none)`. Nothing runs yet until something *calls* `main(...)`.

### Line 535
```python
    ap = argparse.ArgumentParser()
```
**Plain English:** Store a value: the name `ap` now holds the result of `argparse.ArgumentParser()`. Whenever you later write that name, you mean this value.

### Line 536
```python
    ap.add_argument("--force", action="store_true")
```
**Plain English:** Run this instruction: `ap.add_argument("--force", action="store_true")`.

### Line 537
```python
    ap.add_argument("--skip-locate", action="store_true",
```
**Plain English:** Run this instruction: `ap.add_argument("--skip-locate", action="store_true",`.

### Line 538
```python
                    help="decode + autopsy only (no hg38)")
```
**Plain English:** Store a value: the name `help` now holds the result of `"decode + autopsy only (no hg38)")`. Whenever you later write that name, you mean this value.

### Line 539
```python
    args = ap.parse_args()
```
**Plain English:** Store a value: the name `args` now holds the result of `ap.parse_args()`. Whenever you later write that name, you mean this value.

### Line 541
```python
    if not HUMAN_MATRIX.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not HUMAN_MATRIX.exists()`.

### Line 542
```python
        raise SystemExit(f"missing {HUMAN_MATRIX}")
```
**Plain English:** Stop and report a problem on purpose → `SystemExit(f"missing {HUMAN_MATRIX}")`.

### Line 543
```python
    if not config.QCT_TABLES.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not config.QCT_TABLES.exists()`.

### Line 544
```python
        raise SystemExit("missing qct_lookup_tables.json — run build_guide_index")
```
**Plain English:** Stop and report a problem on purpose → `SystemExit("missing qct_lookup_tables.json — run build_guide_index")`.

### Line 545
```python
    if not (config.INTERIM / "v_column_mapping.json").exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not (config.INTERIM / "v_column_mapping.json").exists()`.

### Line 546
```python
        raise SystemExit("missing v_column_mapping.json — run decode_v_columns")
```
**Plain English:** Stop and report a problem on purpose → `SystemExit("missing v_column_mapping.json — run decode_v_columns")`.

### Line 548
```python
    print("=== decode human ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== decode human ===", flush=True)`.

### Line 549
```python
    decoded = decode_human(force=args.force)
```
**Plain English:** Store a value: the name `decoded` now holds the result of `decode_human(force=args.force)`. Whenever you later write that name, you mean this value.

### Line 550
```python
    gc_shape_report(decoded)
```
**Plain English:** Run this instruction: `gc_shape_report(decoded)`.

### Line 552
```python
    if args.skip_locate:
```
**Plain English:** Decision: run the indented block only when this condition is true → `args.skip_locate`.

### Line 553
```python
        print("skip-locate: building meta from decode for autopsy only", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("skip-locate: building meta from decode for autopsy only", flush=True)`.

### Line 554
```python
        # autopsy doesn't need locate — use all decoded rows
```
**Plain English:** Human-only note (Python ignores it): autopsy doesn't need locate — use all decoded rows

### Line 555
```python
        # fabricate meta from human matrix order
```
**Plain English:** Human-only note (Python ignores it): fabricate meta from human matrix order

### Line 556
```python
        print("=== transfer autopsy (all decoded human rows) ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== transfer autopsy (all decoded human rows) ===", flush=True)`.

### Line 557
```python
        # lightweight path
```
**Plain English:** Human-only note (Python ignores it): lightweight path

### Line 558
```python
        import xgboost as xgb
```
**Plain English:** Load toolbox code: `import xgboost as xgb` — used here for **the gradient-boosted tree learner**.

### Line 559
```python
        from sklearn.linear_model import LinearRegression
```
**Plain English:** Load toolbox code: `from sklearn.linear_model import LinearRegression` — used here for **classic ML helpers (splits, metrics)**.

### Line 560
```python
        eco = pd.read_csv(config.BASE_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, low_memory=False)
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 561
```python
        hum = pd.read_csv(HUMAN_MATRIX, header=config.BASE_MATRIX_HEADER_ROW, low_memory=False)
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 562
```python
        drop = {config.TARGET_COL, config.ID_COL}
```
**Plain English:** Store a value: the name `drop` now holds the result of `{config.TARGET_COL, config.ID_COL}`. Whenever you later write that name, you mean this value.

### Line 563
```python
        shared = sorted((set(eco.columns) & set(hum.columns)) - drop)
```
**Plain English:** Store a value: the name `shared` now holds the result of `sorted((set(eco.columns) & set(hum.columns)) - drop)`. Whenever you later write that name, you mean this value.

### Line 564
```python
        ye = pd.to_numeric(eco[config.TARGET_COL], errors="coerce").to_numpy(float)
```
**Plain English:** Store a value: the name `ye` now holds the result of `pd.to_numeric(eco[config.TARGET_COL], errors="coerce").to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 565
```python
        Xe = eco[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)
```
**Plain English:** Store a value: the name `Xe` now holds the result of `eco[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)`. Whenever you later write that name, you mean this value.

### Line 566
```python
        ok_e = np.isfinite(ye)
```
**Plain English:** Store a value: the name `ok_e` now holds the result of `np.isfinite(ye)`. Whenever you later write that name, you mean this value.

### Line 567
```python
        Xe, ye = Xe[ok_e], ye[ok_e]
```
**Plain English:** Run this instruction: `Xe, ye = Xe[ok_e], ye[ok_e]`.

### Line 568
```python
        yh = pd.to_numeric(hum[config.TARGET_COL], errors="coerce").to_numpy(float)
```
**Plain English:** Store a value: the name `yh` now holds the result of `pd.to_numeric(hum[config.TARGET_COL], errors="coerce").to_numpy(float)`. Whenever you later write that name, you mean this value.

### Line 569
```python
        Xh = hum[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)
```
**Plain English:** Store a value: the name `Xh` now holds the result of `hum[shared].apply(pd.to_numeric, errors="coerce").to_numpy(np.float32)`. Whenever you later write that name, you mean this value.

### Line 570
```python
        # spacer GC from decode aligned by ID
```
**Plain English:** Human-only note (Python ignores it): spacer GC from decode aligned by ID

### Line 571
```python
        dec = decoded.set_index(config.ID_COL)
```
**Plain English:** Store a value: the name `dec` now holds the result of `decoded.set_index(config.ID_COL)`. Whenever you later write that name, you mean this value.

### Line 572
```python
        hum_ids = hum[config.ID_COL].astype(str)
```
**Plain English:** Store a value: the name `hum_ids` now holds the result of `hum[config.ID_COL].astype(str)`. Whenever you later write that name, you mean this value.

### Line 573
```python
        gc = []
```
**Plain English:** Store a value: the name `gc` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 574
```python
        for gid in hum_ids:
```
**Plain English:** Loop: repeat the indented block once for each item → `gid in hum_ids`.

### Line 575
```python
            if gid in dec.index and bool(dec.loc[gid, "decoded_ok"]):
```
**Plain English:** Decision: run the indented block only when this condition is true → `gid in dec.index and bool(dec.loc[gid, "decoded_ok"])`.

### Line 576
```python
                s = str(dec.loc[gid, "protospacer"])
```
**Plain English:** Store a value: the name `s` now holds the result of `str(dec.loc[gid, "protospacer"])`. Whenever you later write that name, you mean this value.

### Line 577
```python
                gc.append((s.count("G") + s.count("C")) / 20)
```
**Plain English:** Run this instruction: `gc.append((s.count("G") + s.count("C")) / 20)`.

### Line 578
```python
            else:
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 579
```python
                gc.append(np.nan)
```
**Plain English:** Run this instruction: `gc.append(np.nan)`.

### Line 580
```python
        gc = np.asarray(gc, float)
```
**Plain English:** Store a value: the name `gc` now holds the result of `np.asarray(gc, float)`. Whenever you later write that name, you mean this value.

### Line 581
```python
        ok = np.isfinite(yh) & np.isfinite(Xh).any(axis=1) & np.isfinite(gc)
```
**Plain English:** Store a value: the name `ok` now holds the result of `np.isfinite(yh) & np.isfinite(Xh).any(axis=1) & np.isfinite(gc)`. Whenever you later write that name, you mean this value.

### Line 582
```python
        Xh, yh, gc = Xh[ok], yh[ok], gc[ok]
```
**Plain English:** Run this instruction: `Xh, yh, gc = Xh[ok], yh[ok], gc[ok]`.

### Line 583
```python
        A, B = _impute(Xe, Xh)
```
**Plain English:** Run this instruction: `A, B = _impute(Xe, Xh)`.

### Line 584
```python
        m = xgb.XGBRegressor(
```
**Plain English:** Store a value: the name `m` now holds the result of `xgb.XGBRegressor(`. Whenever you later write that name, you mean this value.

### Line 585
```python
            n_estimators=300, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `300, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 586
```python
            colsample_bytree=0.8, random_state=SEED, n_jobs=-1, tree_method="hist",
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, random_state=SEED, n_jobs=-1, tree_method="hist",`. Whenever you later write that name, you mean this value.

### Line 587
```python
            importance_type="gain")
```
**Plain English:** Store a value: the name `importance_type` now holds the result of `"gain")`. Whenever you later write that name, you mean this value.

### Line 588
```python
        m.fit(A, ye)
```
**Plain English:** Run this instruction: `m.fit(A, ye)`.

### Line 589
```python
        top = np.argsort(m.feature_importances_)[::-1][:300]
```
**Plain English:** Store a value: the name `top` now holds the result of `np.argsort(m.feature_importances_)[::-1][:300]`. Whenever you later write that name, you mean this value.

### Line 590
```python
        m2 = xgb.XGBRegressor(
```
**Plain English:** Store a value: the name `m2` now holds the result of `xgb.XGBRegressor(`. Whenever you later write that name, you mean this value.

### Line 591
```python
            n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
```
**Plain English:** Store a value: the name `n_estimators` now holds the result of `400, learning_rate=0.05, max_depth=4, subsample=0.8,`. Whenever you later write that name, you mean this value.

### Line 592
```python
            colsample_bytree=0.8, random_state=SEED, n_jobs=-1, tree_method="hist")
```
**Plain English:** Store a value: the name `colsample_bytree` now holds the result of `0.8, random_state=SEED, n_jobs=-1, tree_method="hist")`. Whenever you later write that name, you mean this value.

### Line 593
```python
        m2.fit(A[:, top], ye)
```
**Plain English:** Run this instruction: `m2.fit(A[:, top], ye)`.

### Line 594
```python
        pred = np.asarray(m2.predict(B[:, top])).ravel()
```
**Plain English:** Store a value: the name `pred` now holds the result of `np.asarray(m2.predict(B[:, top])).ravel()`. Whenever you later write that name, you mean this value.

### Line 595
```python
        Z = np.c_[gc, gc ** 2]
```
**Plain English:** Store a value: the name `Z` now holds the result of `np.c_[gc, gc ** 2]`. Whenever you later write that name, you mean this value.

### Line 596
```python
        ry = yh - LinearRegression().fit(Z, yh).predict(Z)
```
**Plain English:** Store a value: the name `ry` now holds the result of `yh - LinearRegression().fit(Z, yh).predict(Z)`. Whenever you later write that name, you mean this value.

### Line 597
```python
        rp = pred - LinearRegression().fit(Z, pred).predict(Z)
```
**Plain English:** Store a value: the name `rp` now holds the result of `pred - LinearRegression().fit(Z, pred).predict(Z)`. Whenever you later write that name, you mean this value.

### Line 598
```python
        out = dict(
```
**Plain English:** Store a value: the name `out` now holds the result of `dict(`. Whenever you later write that name, you mean this value.

### Line 599
```python
            overall_transfer_rho=_spearman(yh, pred),
```
**Plain English:** Store a value: the name `overall_transfer_rho` now holds the result of `_spearman(yh, pred),`. Whenever you later write that name, you mean this value.

### Line 600
```python
            transfer_rho_after_residualising_gc2=_spearman(ry, rp),
```
**Plain English:** Store a value: the name `transfer_rho_after_residualising_gc2` now holds the result of `_spearman(ry, rp),`. Whenever you later write that name, you mean this value.

### Line 601
```python
            spearman_error_vs_spacer_gc=_spearman(gc, pred - yh),
```
**Plain English:** Store a value: the name `spearman_error_vs_spacer_gc` now holds the result of `_spearman(gc, pred - yh),`. Whenever you later write that name, you mean this value.

### Line 602
```python
            n_human=int(len(yh)), n_ecoli_train=int(len(ye)),
```
**Plain English:** Store a value: the name `n_human` now holds the result of `int(len(yh)), n_ecoli_train=int(len(ye)),`. Whenever you later write that name, you mean this value.

### Line 603
```python
            n_shared_cols=len(shared),
```
**Plain English:** Store a value: the name `n_shared_cols` now holds the result of `len(shared),`. Whenever you later write that name, you mean this value.

### Line 604
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 605
```python
        rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 606
```python
        qs = np.quantile(gc, np.linspace(0, 1, 11))
```
**Plain English:** Store a value: the name `qs` now holds the result of `np.quantile(gc, np.linspace(0, 1, 11))`. Whenever you later write that name, you mean this value.

### Line 607
```python
        for i in range(10):
```
**Plain English:** Loop: repeat the indented block once for each item → `i in range(10)`.

### Line 608
```python
            lo, hi = qs[i], qs[i + 1]
```
**Plain English:** Run this instruction: `lo, hi = qs[i], qs[i + 1]`.

### Line 609
```python
            msk = (gc >= lo) & (gc < hi) if i < 9 else (gc >= lo) & (gc <= hi)
```
**Plain English:** Store a value: the name `msk` now holds the result of `(gc >= lo) & (gc < hi) if i < 9 else (gc >= lo) & (gc <= hi)`. Whenever you later write that name, you mean this value.

### Line 610
```python
            rows.append(dict(
```
**Plain English:** Run this instruction: `rows.append(dict(`.

### Line 611
```python
                gc_decile=i + 1, gc_lo=float(lo), gc_hi=float(hi),
```
**Plain English:** Store a value: the name `gc_decile` now holds the result of `i + 1, gc_lo=float(lo), gc_hi=float(hi),`. Whenever you later write that name, you mean this value.

### Line 612
```python
                n=int(msk.sum()), mean_gc=float(gc[msk].mean()),
```
**Plain English:** Store a value: the name `n` now holds the result of `int(msk.sum()), mean_gc=float(gc[msk].mean()),`. Whenever you later write that name, you mean this value.

### Line 613
```python
                transfer_rho=_spearman(yh[msk], pred[msk]),
```
**Plain English:** Store a value: the name `transfer_rho` now holds the result of `_spearman(yh[msk], pred[msk]),`. Whenever you later write that name, you mean this value.

### Line 614
```python
            ))
```
**Plain English:** Run this instruction: `))`.

### Line 615
```python
        (OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent=2))
```
**Plain English:** Store a value: the name `(OUT / "transfer_autopsy.json").write_text(json.dumps(out, indent` now holds the result of `2))`. Whenever you later write that name, you mean this value.

### Line 616
```python
        pd.DataFrame(rows).to_csv(OUT / "transfer_autopsy_by_gc_decile.csv", index=False)
```
**Plain English:** Run this instruction: `pd.DataFrame(rows).to_csv(OUT / "transfer_autopsy_by_gc_decile.csv", index=False)`.

### Line 617
```python
        print(json.dumps(out, indent=2), flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(json.dumps(out, indent=2), flush=True)`.

### Line 618
```python
        print("DONE (skip-locate)", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("DONE (skip-locate)", flush=True)`.

### Line 619
```python
        return
```
**Plain English:** Finish this function and send back: `(nothing / None)`.

### Line 621
```python
    print("=== locate on hg38 ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== locate on hg38 ===", flush=True)`.

### Line 622
```python
    loc = locate_on_hg38(decoded, force=args.force)
```
**Plain English:** Store a value: the name `loc` now holds the result of `locate_on_hg38(decoded, force=args.force)`. Whenever you later write that name, you mean this value.

### Line 623
```python
    if len(loc) < 500:
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(loc) < 500`.

### Line 624
```python
        raise SystemExit(f"too few located guides: {len(loc)}")
```
**Plain English:** Stop and report a problem on purpose → `SystemExit(f"too few located guides: {len(loc)}")`.

### Line 626
```python
    print("=== build matrices ===", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("=== build matrices ===", flush=True)`.

### Line 627
```python
    Xb, Xf, y, bn, fn, meta = build_human_matrices(loc, force=args.force)
```
**Plain English:** Run this instruction: `Xb, Xf, y, bn, fn, meta = build_human_matrices(loc, force=args.force)`.

### Line 628
```python
    family_of = meta["family_of"]
```
**Plain English:** Store a value: the name `family_of` now holds the result of `meta["family_of"]`. Whenever you later write that name, you mean this value.

### Line 629
```python
    run_ladder(Xb, Xf, y, bn, fn, family_of, meta)
```
**Plain English:** Run this instruction: `run_ladder(Xb, Xf, y, bn, fn, family_of, meta)`.

### Line 630
```python
    transfer_autopsy(meta, Xf, y, fn, family_of)
```
**Plain English:** Run this instruction: `transfer_autopsy(meta, Xf, y, fn, family_of)`.

### Line 631
```python
    print("DONE", flush=True)
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("DONE", flush=True)`.

### Line 634
```python
if __name__ == "__main__":
```
**Plain English:** Special gate: this block runs only when you execute *this file directly* (not when another file imports it). Common pattern for scripts.

### Line 635
```python
    main()
```
**Plain English:** Run this instruction: `main()`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### The human pipeline in one breath
Decode 20-mers from electron columns → find unique NGG hits on hg38 → build Family A on those flanks → CV ladder (base vs base+A) → train on E. coli shared columns and predict human (transfer autopsy).

### Why stream chromosomes?
hg38 is huge. Loading all chromosomes at once can exhaust RAM. This script loads one chromosome, scans it, then deletes it.

### What “transfer autopsy” is asking
If an E. coli-trained model fails on human mostly because of GC habits, residualising GC should change the transfer correlation. That diagnoses *why* transfer fails, not just that it fails.
