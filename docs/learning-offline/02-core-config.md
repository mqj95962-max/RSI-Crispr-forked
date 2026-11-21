# 02 — Core config & I/O (line walkthrough)


> **Updated teaching guide:** for purpose/data-flow explanations (recommended), read [`p0-contextual/02-config-and-io.md`](p0-contextual/02-config-and-io.md) instead of relying only on this shorter summary.

**Files:**  
- `Runjia/sgrna/config.py` (~198 lines)  
- `Runjia/sgrna/io_utils.py` (~87 lines)

**Role:** One place for paths and constants so experiments don’t hardcode folders.

---

## `config.py`

### Lines 1–11 — Module docstring

Explains three ways to find the project root: notebook setup, running inside the folder, or `RSI09_ROOT` env var.

### Lines 22–54 — Finding the root

```python
_MARKERS = ("data/raw", "external_data")
```

`_looks_like_root(p)` is true only if both markers exist.

`find_project_root()`:

1. If `RSI09_ROOT` set → use it (must exist)  
2. Else walk up from `config.py`’s path  
3. Else walk up from cwd  
4. Else raise a clear error  

`ROOT = find_project_root()` runs at import time.

### Lines 56–72 — Directory constants

| Name | Path |
|---|---|
| `DATA` | `ROOT/data` |
| `RAW` | published matrices |
| `REFERENCE` | genomes, gene tables |
| `INTERIM` | caches / guide index |
| `FEATURE_DIR` | one CSV per family |
| `EXTERNAL` | GapR, RegulonDB, crisprHAL, … |
| `RESULTS` | experiment outputs |

Creates interim/feature/processed/results dirs if missing.

### Lines 74–94 — Key files

- `BASE_MATRIX` = Noshay E. coli CSV; `BASE_MATRIX_HEADER_ROW = 1` (title row!)  
- `ID_COL`, `TARGET_COL`  
- `GENOME_FASTA`, `GENE_TABLE`  
- `GUIDE_INDEX`, `QCT_TABLES` (outputs of step 0)

### Lines 96–129 — External datasets

Maps GapR GEO files into roles: `signal`, `control` (untagged!), `rifampicin`, `truncated`. Also Hi-C (Lioy), RegulonDB, PRECISE, crisprHAL, etc.

### Lines 131–154 — Biology constants

- `SPCAS9_SCAFFOLD` — constant 3′ of spacer for folding  
- `FLANK = 1000` — how much DNA either side to keep  
- `UPSTREAM_POSITIONS` / `DOWNSTREAM_POSITIONS` — one-hot positions for Family A  
- `FLANK_WINDOWS = (50, 250, 500, 1000)` — summary windows  

### Lines 156–179 — Modelling defaults

Matches the frozen baseline: `SELECTOR`, `N_FEATURES=300`, `N_ESTIMATORS=400`, `N_SPLITS=5`, `SEEDS`, plus `BASELINE` reference scores.

### Lines 182–198 — `describe()`

Prints which key files exist — useful sanity check when something can’t find data.

---

## `io_utils.py`

### Lines 1–7 — Docstring

A **feature block** = CSV keyed by `sgRNAID`, other columns start with `eng.`. Built independently; joined later.

### Lines 18–41 — `block_path` / `save_block`

`save_block` enforces:

1. Has `sgRNAID`  
2. Every other column starts with `eng.`  
3. No duplicate IDs  

Then writes `FEATURE_DIR/{family}.csv`.

### Lines 44–55 — `load_block` / `available_blocks`

Load one family or list what’s built.

### Lines 58–64 — `load_guide_index`

Reads step-0 output; errors if you forgot to build it.

### Lines 67–79 — `load_base_matrix` / `base_matrix_columns`

Always uses `header=1`. Optional `usecols` / `nrows` for speed.

### Lines 82–87 — `one_hot`

Deterministic one-hot: fixed category order → same columns every time.

---

## Checklist

- [ ] I know why `header=1`  
- [ ] I know what `RSI09_ROOT` does  
- [ ] I know a feature block must use `eng.*` column names  
- [ ] I know Family A windows live in `FLANK_WINDOWS`  
