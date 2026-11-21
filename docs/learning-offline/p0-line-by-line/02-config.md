# P0 line-by-line: `Runjia/sgrna/config.py`
**Why this file matters:** One shared address book for folders, file names, and modelling settings.
**Length:** 198 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Think of this as the project’s address book and settings panel — one place everyone looks up paths.

---
### Lines 1–11
```python
"""Project paths and shared constants.

Works in three places without edits:

  1. In a notebook, after `sgrna.notebook.setup()` -- which is how this
     project is normally driven (see notebooks/RSI09_pipeline.ipynb).
  2. Locally, when you run anything from inside the project folder.
  3. From anywhere else, if you set the environment variable RSI09_ROOT.

Nothing else in the package hardcodes a path -- if a file moves, change it here.
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 13
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 15
```python
import os
```
**Plain English:** Load toolbox code: `import os` — used here for **talk to the operating system (paths, env vars)**.

### Line 16
```python
from pathlib import Path
```
**Plain English:** Load toolbox code: `from pathlib import Path` — used here for **friendly file-path objects**.

### Line 18
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 19
```python
# Project root
```
**Plain English:** Human-only note (Python ignores it): Project root

### Line 20
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 22
```python
_MARKERS = ("data/raw", "external_data")
```
**Plain English:** Two folders that must exist for a directory to count as the project root: `data/raw` and `external_data`.

### Line 25
```python
def _looks_like_root(p: Path) -> bool:
```
**Plain English:** Defines a reusable recipe named `_looks_like_root`. Inputs in parentheses: `p: Path`. Returns type hint: bool. Nothing runs yet until something *calls* `_looks_like_root(...)`.

### Line 26
```python
    return all((p / m).exists() for m in _MARKERS)
```
**Plain English:** Finish this function and send back: `all((p / m).exists() for m in _MARKERS)`.

### Line 29
```python
def find_project_root() -> Path:
```
**Plain English:** Defines a reusable recipe named `find_project_root`. Inputs in parentheses: `(none)`. Returns type hint: Path. Nothing runs yet until something *calls* `find_project_root(...)`.

### Line 30
```python
    env = os.environ.get("RSI09_ROOT")
```
**Plain English:** Environment variable escape hatch: if set, that path *is* the project root (needed when scripts live outside `Runjia/`).

### Line 31
```python
    if env:
```
**Plain English:** Decision: run the indented block only when this condition is true → `env`.

### Line 32
```python
        p = Path(env).expanduser().resolve()
```
**Plain English:** Store a value: the name `p` now holds the result of `Path(env).expanduser().resolve()`. Whenever you later write that name, you mean this value.

### Line 33
```python
        if not p.exists():
```
**Plain English:** Decision: run the indented block only when this condition is true → `not p.exists()`.

### Line 34
```python
            raise FileNotFoundError(f"RSI09_ROOT points at {p}, which does not exist.")
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(f"RSI09_ROOT points at {p}, which does not exist.")`.

### Line 35
```python
        return p
```
**Plain English:** Finish this function and send back: `p`.

### Line 37
```python
    # Walk up from this file: src/sgrna/config.py -> src/sgrna -> src -> ROOT
```
**Plain English:** Human-only note (Python ignores it): Walk up from this file: src/sgrna/config.py -> src/sgrna -> src -> ROOT

### Line 38
```python
    here = Path(__file__).resolve()
```
**Plain English:** Store a value: the name `here` now holds the result of `Path(__file__).resolve()`. Whenever you later write that name, you mean this value.

### Line 39
```python
    for parent in here.parents:
```
**Plain English:** Loop: repeat the indented block once for each item → `parent in here.parents`.

### Line 40
```python
        if _looks_like_root(parent):
```
**Plain English:** Decision: run the indented block only when this condition is true → `_looks_like_root(parent)`.

### Line 41
```python
            return parent
```
**Plain English:** Finish this function and send back: `parent`.

### Line 43
```python
    # Walk up from the current working directory (covers notebooks).
```
**Plain English:** Human-only note (Python ignores it): Walk up from the current working directory (covers notebooks).

### Line 44
```python
    for parent in [Path.cwd(), *Path.cwd().parents]:
```
**Plain English:** Loop: repeat the indented block once for each item → `parent in [Path.cwd(), *Path.cwd().parents]`.

### Line 45
```python
        if _looks_like_root(parent):
```
**Plain English:** Decision: run the indented block only when this condition is true → `_looks_like_root(parent)`.

### Line 46
```python
            return parent
```
**Plain English:** Finish this function and send back: `parent`.

### Line 48
```python
    raise FileNotFoundError(
```
**Plain English:** Stop and report a problem on purpose → `FileNotFoundError(`.

### Line 49
```python
        "Could not find the project root. Set RSI09_ROOT to the folder that "
```
**Plain English:** Environment variable escape hatch: if set, that path *is* the project root (needed when scripts live outside `Runjia/`).

### Line 50
```python
        "contains data/ and external_data/."
```
**Plain English:** Run this instruction: `"contains data/ and external_data/."`.

### Line 51
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 54
```python
ROOT = find_project_root()
```
**Plain English:** Run the finder once at import time; every other path hangs off `ROOT`.

### Line 56
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 57
```python
# Directories
```
**Plain English:** Human-only note (Python ignores it): Directories

### Line 58
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 60
```python
DATA = ROOT / "data"
```
**Plain English:** Store a value: the name `DATA` now holds the result of `ROOT / "data"`. Whenever you later write that name, you mean this value.

### Line 61
```python
RAW = DATA / "raw"
```
**Plain English:** Store a value: the name `RAW` now holds the result of `DATA / "raw"`. Whenever you later write that name, you mean this value.

### Line 62
```python
REFERENCE = DATA / "reference"
```
**Plain English:** Store a value: the name `REFERENCE` now holds the result of `DATA / "reference"`. Whenever you later write that name, you mean this value.

### Line 63
```python
INTERIM = DATA / "interim"
```
**Plain English:** Store a value: the name `INTERIM` now holds the result of `DATA / "interim"`. Whenever you later write that name, you mean this value.

### Line 64
```python
FEATURE_DIR = INTERIM / "features"
```
**Plain English:** Store a value: the name `FEATURE_DIR` now holds the result of `INTERIM / "features"`. Whenever you later write that name, you mean this value.

### Line 65
```python
PROCESSED = DATA / "processed"
```
**Plain English:** Store a value: the name `PROCESSED` now holds the result of `DATA / "processed"`. Whenever you later write that name, you mean this value.

### Line 67
```python
EXTERNAL = ROOT / "external_data"
```
**Plain English:** Store a value: the name `EXTERNAL` now holds the result of `ROOT / "external_data"`. Whenever you later write that name, you mean this value.

### Line 68
```python
RESULTS = ROOT / "results"
```
**Plain English:** Store a value: the name `RESULTS` now holds the result of `ROOT / "results"`. Whenever you later write that name, you mean this value.

### Line 69
```python
DOCS = ROOT / "docs"
```
**Plain English:** Store a value: the name `DOCS` now holds the result of `ROOT / "docs"`. Whenever you later write that name, you mean this value.

### Line 71
```python
for _d in (INTERIM, FEATURE_DIR, PROCESSED, RESULTS):
```
**Plain English:** Loop: repeat the indented block once for each item → `_d in (INTERIM, FEATURE_DIR, PROCESSED, RESULTS)`.

### Line 72
```python
    _d.mkdir(parents=True, exist_ok=True)
```
**Plain English:** Run this instruction: `_d.mkdir(parents=True, exist_ok=True)`.

### Line 74
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 75
```python
# Key files
```
**Plain English:** Human-only note (Python ignores it): Key files

### Line 76
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 78
```python
# Noshay et al. 2023 supplementary table 2, unchanged. Row 1 is a title row,
```
**Plain English:** Human-only note (Python ignores it): Noshay et al. 2023 supplementary table 2, unchanged. Row 1 is a title row,

### Line 79
```python
# so every reader in this project passes header=1.
```
**Plain English:** Human-only note (Python ignores it): so every reader in this project passes header=1.

### Line 80
```python
BASE_MATRIX = RAW / "ecoli_feature_matrix.csv"
```
**Plain English:** Store a value: the name `BASE_MATRIX` now holds the result of `RAW / "ecoli_feature_matrix.csv"`. Whenever you later write that name, you mean this value.

### Line 81
```python
BASE_MATRIX_HEADER_ROW = 1
```
**Plain English:** **Critical CSV quirk:** row 0 is a title banner, so real column names are on row 1. `header=1` tells pandas ‘treat row index 1 as the header’.

### Line 83
```python
ID_COL = "sgRNAID"
```
**Plain English:** Name of the guide ID column: `sgRNAID` (each row’s unique name).

### Line 84
```python
TARGET_COL = "cut.score"
```
**Plain English:** Name of the answer column: **`cut.score`** — measured cutting efficiency. Everything else is an input feature trying to predict this.

### Line 86
```python
# Reference genome. NC_000913.2 (U00096.2), 4,639,675 bp -- the build the
```
**Plain English:** Human-only note (Python ignores it): Reference genome. NC_000913.2 (U00096.2), 4,639,675 bp -- the build the

### Line 87
```python
# GapR-seq wiggles and the Bikard screen use. Coordinates in this project are
```
**Plain English:** Human-only note (Python ignores it): GapR-seq wiggles and the Bikard screen use. Coordinates in this project are

### Line 88
```python
# always NC_000913.2 unless a column name says otherwise.
```
**Plain English:** Human-only note (Python ignores it): always NC_000913.2 unless a column name says otherwise.

### Line 89
```python
GENOME_FASTA = REFERENCE / "NC_000913.2.fasta"
```
**Plain English:** Store a value: the name `GENOME_FASTA` now holds the result of `REFERENCE / "NC_000913.2.fasta"`. Whenever you later write that name, you mean this value.

### Line 90
```python
GENE_TABLE = REFERENCE / "genes_NC_000913.2.tsv"
```
**Plain English:** Store a value: the name `GENE_TABLE` now holds the result of `REFERENCE / "genes_NC_000913.2.tsv"`. Whenever you later write that name, you mean this value.

### Line 92
```python
# Outputs of step 0
```
**Plain English:** Human-only note (Python ignores it): Outputs of step 0

### Line 93
```python
GUIDE_INDEX = INTERIM / "guide_index.csv"
```
**Plain English:** Store a value: the name `GUIDE_INDEX` now holds the result of `INTERIM / "guide_index.csv"`. Whenever you later write that name, you mean this value.

### Line 94
```python
QCT_TABLES = INTERIM / "qct_lookup_tables.json"
```
**Plain English:** Store a value: the name `QCT_TABLES` now holds the result of `INTERIM / "qct_lookup_tables.json"`. Whenever you later write that name, you mean this value.

### Line 96
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 97
```python
# External datasets
```
**Plain English:** Human-only note (Python ignores it): External datasets

### Line 98
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 100
```python
GAPR_WIG_DIR = EXTERNAL / "GapR-seq" / "wig"
```
**Plain English:** Store a value: the name `GAPR_WIG_DIR` now holds the result of `EXTERNAL / "GapR-seq" / "wig"`. Whenever you later write that name, you mean this value.

### Line 101
```python
# GSE152880 sample roles, from the GEO sample titles.
```
**Plain English:** Human-only note (Python ignores it): GSE152880 sample roles, from the GEO sample titles.

### Line 102
```python
GAPR_SAMPLES = {
```
**Plain English:** Store a value: the name `GAPR_SAMPLES` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 103
```python
    "signal": [  # GapR-3xFLAG, exponential phase, +aTc
```
**Plain English:** Run this instruction: `"signal": [  # GapR-3xFLAG, exponential phase, +aTc`.

### Line 104
```python
        "GSM4628313_D18-11475-3531L_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4628313_D18-11475-3531L_norm.wig.gz",`.

### Line 105
```python
        "GSM4628314_D19-11570-4278G_MG1655_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4628314_D19-11570-4278G_MG1655_norm.wig.gz",`.

### Line 106
```python
    ],
```
**Plain English:** Run this instruction: `],`.

### Line 107
```python
    "control": [  # untagged GapR -- the no-ChIP background
```
**Plain English:** Run this instruction: `"control": [  # untagged GapR -- the no-ChIP background`.

### Line 108
```python
        "GSM4628311_D19-5504-3883G_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4628311_D19-5504-3883G_norm.wig.gz",`.

### Line 109
```python
        "GSM4628312_D19-11573-4278G_MG1655_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4628312_D19-11573-4278G_MG1655_norm.wig.gz",`.

### Line 110
```python
    ],
```
**Plain English:** Run this instruction: `],`.

### Line 111
```python
    "rifampicin": [  # GapR-3xFLAG + rifampicin: transcription switched off
```
**Plain English:** Run this instruction: `"rifampicin": [  # GapR-3xFLAG + rifampicin: transcription switched off`.

### Line 112
```python
        "GSM4628315_D18-11479-3531L_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4628315_D18-11479-3531L_norm.wig.gz",`.

### Line 113
```python
    ],
```
**Plain English:** Run this instruction: `],`.

### Line 114
```python
    "truncated": [  # GapR(1-76)-3xFLAG control
```
**Plain English:** Run this instruction: `"truncated": [  # GapR(1-76)-3xFLAG control`.

### Line 115
```python
        "GSM4989042_D20-5423-4700M_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4989042_D20-5423-4700M_norm.wig.gz",`.

### Line 116
```python
        "GSM4989043_D20-5424-4700M_norm.wig.gz",
```
**Plain English:** Run this instruction: `"GSM4989043_D20-5424-4700M_norm.wig.gz",`.

### Line 117
```python
    ],
```
**Plain English:** Run this instruction: `],`.

### Line 118
```python
}
```
**Plain English:** Run this instruction: `}`.

### Line 120
```python
LIOY_DIR = EXTERNAL / "E_coli_analysis" / "data"
```
**Plain English:** Store a value: the name `LIOY_DIR` now holds the result of `EXTERNAL / "E_coli_analysis" / "data"`. Whenever you later write that name, you mean this value.

### Line 121
```python
LIOY_XYZ = LIOY_DIR / "3Dcoor_ecoli_5kb_3_3_copie.xyz"
```
**Plain English:** Store a value: the name `LIOY_XYZ` now holds the result of `LIOY_DIR / "3Dcoor_ecoli_5kb_3_3_copie.xyz"`. Whenever you later write that name, you mean this value.

### Line 122
```python
LIOY_MATRIX_DIR = LIOY_DIR / "matrices_5kb"
```
**Plain English:** Store a value: the name `LIOY_MATRIX_DIR` now holds the result of `LIOY_DIR / "matrices_5kb"`. Whenever you later write that name, you mean this value.

### Line 123
```python
LIOY_BIN_SIZE = 5000
```
**Plain English:** Store a value: the name `LIOY_BIN_SIZE` now holds the result of `5000`. Whenever you later write that name, you mean this value.

### Line 125
```python
REGULONDB = EXTERNAL / "RegulonDB"
```
**Plain English:** Store a value: the name `REGULONDB` now holds the result of `EXTERNAL / "RegulonDB"`. Whenever you later write that name, you mean this value.

### Line 126
```python
PRECISE1K = EXTERNAL / "precise1k" / "data"
```
**Plain English:** Store a value: the name `PRECISE1K` now holds the result of `EXTERNAL / "precise1k" / "data"`. Whenever you later write that name, you mean this value.

### Line 127
```python
CRISPRHAL = EXTERNAL / "crisprHAL" / "data"
```
**Plain English:** Store a value: the name `CRISPRHAL` now holds the result of `EXTERNAL / "crisprHAL" / "data"`. Whenever you later write that name, you mean this value.

### Line 128
```python
CRISPROFF = EXTERNAL / "crisproff"
```
**Plain English:** Store a value: the name `CRISPROFF` now holds the result of `EXTERNAL / "crisproff"`. Whenever you later write that name, you mean this value.

### Line 129
```python
BADSEED = EXTERNAL / "CRISPRBact" / "badSeed_public"
```
**Plain English:** Store a value: the name `BADSEED` now holds the result of `EXTERNAL / "CRISPRBact" / "badSeed_public"`. Whenever you later write that name, you mean this value.

### Line 131
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 132
```python
# Biology constants
```
**Plain English:** Human-only note (Python ignores it): Biology constants

### Line 133
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 135
```python
# SpCas9 sgRNA scaffold (the constant region 3' of the 20 nt spacer), as used
```
**Plain English:** Human-only note (Python ignores it): SpCas9 sgRNA scaffold (the constant region 3' of the 20 nt spacer), as used

### Line 136
```python
# in the Guo et al. E. coli library. Needed to fold the transcript that is
```
**Plain English:** Human-only note (Python ignores it): in the Guo et al. E. coli library. Needed to fold the transcript that is

### Line 137
```python
# actually expressed rather than the bare spacer.
```
**Plain English:** Human-only note (Python ignores it): actually expressed rather than the bare spacer.

### Line 138
```python
SPCAS9_SCAFFOLD = (
```
**Plain English:** Store a value: the name `SPCAS9_SCAFFOLD` now holds the result of `(`. Whenever you later write that name, you mean this value.

### Line 139
```python
    "GUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC"
```
**Plain English:** Run this instruction: `"GUUUUAGAGCUAGAAAUAGCAAGUUAAAAUAAGGCUAGUCCGUUAUCAACUUGAAAAAGUGGCACCGAGUCGGUGC"`.

### Line 140
```python
)
```
**Plain English:** Run this instruction: `)`.

### Line 142
```python
# How far either side of the protospacer to keep in the guide index. The
```
**Plain English:** Human-only note (Python ignores it): How far either side of the protospacer to keep in the guide index. The

### Line 143
```python
# curated re-analysis of this screen found signal out to ~190 nt upstream and
```
**Plain English:** Human-only note (Python ignores it): curated re-analysis of this screen found signal out to ~190 nt upstream and

### Line 144
```python
# ~166 nt downstream; the first ablation here found the wide-flank summaries
```
**Plain English:** Human-only note (Python ignores it): ~166 nt downstream; the first ablation here found the wide-flank summaries

### Line 145
```python
# carrying 62% of family A's gain and showing no sign of saturating at 250 nt,
```
**Plain English:** Human-only note (Python ignores it): carrying 62% of family A's gain and showing no sign of saturating at 250 nt,

### Line 146
```python
# so the window was widened to 1 kb to find where it does.
```
**Plain English:** Human-only note (Python ignores it): so the window was widened to 1 kb to find where it does.

### Line 147
```python
FLANK = 1000
```
**Plain English:** How many DNA letters to keep on each side of the target (**1000 nt**). Family A summarises these flanks.

### Line 149
```python
# Positions, relative to the protospacer, that family A encodes one-hot.
```
**Plain English:** Human-only note (Python ignores it): Positions, relative to the protospacer, that family A encodes one-hot.

### Line 150
```python
UPSTREAM_POSITIONS = 10    # -1 .. -10, immediately 5' of protospacer position 1
```
**Plain English:** Store a value: the name `UPSTREAM_POSITIONS` now holds the result of `10    # -1 .. -10, immediately 5' of protospacer position 1`. Whenever you later write that name, you mean this value.

### Line 151
```python
DOWNSTREAM_POSITIONS = 15  # +1 .. +15, immediately 3' of the NGG PAM
```
**Plain English:** Store a value: the name `DOWNSTREAM_POSITIONS` now holds the result of `15  # +1 .. +15, immediately 3' of the NGG PAM`. Whenever you later write that name, you mean this value.

### Line 153
```python
# Windows (nt) for compositional and tensor summaries of the flanks.
```
**Plain English:** Human-only note (Python ignores it): Windows (nt) for compositional and tensor summaries of the flanks.

### Line 154
```python
FLANK_WINDOWS = (50, 250, 500, 1000)
```
**Plain English:** How many DNA letters to keep on each side of the target (**1000 nt**). Family A summarises these flanks.

### Line 156
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 157
```python
# Modelling defaults -- match the frozen baseline so ablations are comparable
```
**Plain English:** Human-only note (Python ignores it): Modelling defaults -- match the frozen baseline so ablations are comparable

### Line 158
```python
# --------------------------------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): --------------------------------------------------------------------------

### Line 160
```python
# Which model ranks the columns before the champion is fitted. The ranking
```
**Plain English:** Human-only note (Python ignores it): Which model ranks the columns before the champion is fitted. The ranking

### Line 161
```python
# model is trained and thrown away, so only its speed and its ordering matter.
```
**Plain English:** Human-only note (Python ignores it): model is trained and thrown away, so only its speed and its ordering matter.

### Line 162
```python
# Measured on 2026-10-03 (`results/selector_comparison.csv`): LightGBM gain
```
**Plain English:** Human-only note (Python ignores it): Measured on 2026-10-03 (`results/selector_comparison.csv`): LightGBM gain

### Line 163
```python
# matches XGBoost gain (rho 0.7033 vs 0.7025) at 3x the speed, taking a fold
```
**Plain English:** Human-only note (Python ignores it): matches XGBoost gain (rho 0.7033 vs 0.7025) at 3x the speed, taking a fold

### Line 164
```python
# from 17.1 s to 6.6 s. Everything recorded before that date used "xgboost";
```
**Plain English:** Human-only note (Python ignores it): from 17.1 s to 6.6 s. Everything recorded before that date used "xgboost";

### Line 165
```python
# set it back to reproduce those runs exactly.
```
**Plain English:** Human-only note (Python ignores it): set it back to reproduce those runs exactly.

### Line 166
```python
# Default is "xgboost": it is what the frozen baseline used, and switching
```
**Plain English:** Human-only note (Python ignores it): Default is "xgboost": it is what the frozen baseline used, and switching

### Line 167
```python
# costs the exact reproduction of the published figure (R2 0.2937 / rho 0.5278
```
**Plain English:** Human-only note (Python ignores it): costs the exact reproduction of the published figure (R2 0.2937 / rho 0.5278

### Line 168
```python
# becomes 0.2897 / 0.5251), which is the project's harness check. "lightgbm"
```
**Plain English:** Human-only note (Python ignores it): becomes 0.2897 / 0.5251), which is the project's harness check. "lightgbm"

### Line 169
```python
# ranks just as well (rho 0.7033 vs 0.7025 on the curated set) at 3x the speed
```
**Plain English:** Human-only note (Python ignores it): ranks just as well (rho 0.7033 vs 0.7025 on the curated set) at 3x the speed

### Line 170
```python
# -- use it for exploratory sweeps where the anchor does not matter.
```
**Plain English:** Human-only note (Python ignores it): -- use it for exploratory sweeps where the anchor does not matter.

### Line 171
```python
SELECTOR = "xgboost"
```
**Plain English:** Store a value: the name `SELECTOR` now holds the result of `"xgboost"`. Whenever you later write that name, you mean this value.

### Line 173
```python
N_FEATURES = 300
```
**Plain English:** Store a value: the name `N_FEATURES` now holds the result of `300`. Whenever you later write that name, you mean this value.

### Line 174
```python
N_ESTIMATORS = 400
```
**Plain English:** **How many trees** the champion XGBoost forest grows (400). More trees ≈ more capacity, slower training.

### Line 175
```python
N_SPLITS = 5
```
**Plain English:** **How many CV folds** (5). Each fold holds out ~20% of rows as the exam.

### Line 176
```python
SEEDS = (41, 42, 43, 44, 45)
```
**Plain English:** **Random seeds** `[41..45]`. Re-run the whole 5-fold exam five times with different shuffles, then average — so one lucky shuffle can’t fool you.

### Line 178
```python
# Reference numbers from five_seed_champion_ecoli_xgboost_baseline.
```
**Plain English:** Human-only note (Python ignores it): Reference numbers from five_seed_champion_ecoli_xgboost_baseline.

### Line 179
```python
BASELINE = {"r2": 0.29368, "spearman": 0.52782, "pearson": 0.54244}
```
**Plain English:** Frozen reference scores from the trusted five-seed run (R²≈0.294, Spearman≈0.528). Ablations compare against these.

### Line 182
```python
def describe() -> str:
```
**Plain English:** Defines a reusable recipe named `describe`. Inputs in parentheses: `(none)`. Returns type hint: str. Nothing runs yet until something *calls* `describe(...)`.

### Line 183
```python
    lines = [f"project root : {ROOT}"]
```
**Plain English:** Store a value: the name `lines` now holds the result of `[f"project root : {ROOT}"]`. Whenever you later write that name, you mean this value.

### Line 184
```python
    for name, p in [
```
**Plain English:** Loop: repeat the indented block once for each item → `name, p in [`.

### Line 185
```python
        ("base matrix", BASE_MATRIX),
```
**Plain English:** Run this instruction: `("base matrix", BASE_MATRIX),`.

### Line 186
```python
        ("genome", GENOME_FASTA),
```
**Plain English:** Run this instruction: `("genome", GENOME_FASTA),`.

### Line 187
```python
        ("gene table", GENE_TABLE),
```
**Plain English:** Run this instruction: `("gene table", GENE_TABLE),`.

### Line 188
```python
        ("guide index", GUIDE_INDEX),
```
**Plain English:** Run this instruction: `("guide index", GUIDE_INDEX),`.

### Line 189
```python
        ("feature dir", FEATURE_DIR),
```
**Plain English:** Run this instruction: `("feature dir", FEATURE_DIR),`.

### Line 190
```python
        ("external", EXTERNAL),
```
**Plain English:** Run this instruction: `("external", EXTERNAL),`.

### Line 191
```python
    ]:
```
**Plain English:** Run this instruction: `]:`.

### Line 192
```python
        mark = "ok " if p.exists() else "MISSING"
```
**Plain English:** Store a value: the name `mark` now holds the result of `"ok " if p.exists() else "MISSING"`. Whenever you later write that name, you mean this value.

### Line 193
```python
        lines.append(f"{name:12s} : [{mark}] {p}")
```
**Plain English:** Run this instruction: `lines.append(f"{name:12s} : [{mark}] {p}")`.

### Line 194
```python
    return "\n".join(lines)
```
**Plain English:** Finish this function and send back: `"\n".join(lines)`.

### Line 197
```python
if __name__ == "__main__":
```
**Plain English:** Special gate: this block runs only when you execute *this file directly* (not when another file imports it). Common pattern for scripts.

### Line 198
```python
    print(describe())
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(describe())`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### Why one config file?
If every script hardcodes `/Users/me/.../data`, moving laptops breaks everything.  
`config.py` computes `ROOT` once; all other paths are `ROOT / "data" / ...`.

### `RSI09_ROOT`
When Jacky scripts live under `Jacky/` but data lives under `Runjia/`, they set:
`export RSI09_ROOT=/path/to/Runjia` so `find_project_root()` doesn’t get confused.
