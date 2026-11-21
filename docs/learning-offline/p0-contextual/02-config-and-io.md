# P0 #2–#3 — Config & I/O (contextual guide)

**Source files:**  
- `Runjia/sgrna/config.py` (~198 lines)  
- `Runjia/sgrna/io_utils.py` (~87 lines)  

**Job in the project:** one shared “address book + house rules” so every experiment finds the same data and writes features in a joinable format.

> In `LEARNING-ORDER.md` these are P0 items **#2** (`config.py`) and **#3** (`io_utils.py`). Read them together — config says *where*, io_utils says *how to read/write*.

---

## Where this sits in the whole pipeline

```text
                    config.py
         ┌────────────┴────────────┐
         │ ROOT, RAW, INTERIM,     │
         │ FLANK=1000, SEEDS, …    │
         └────────────┬────────────┘
                      │ imported by almost everything
         ┌────────────┼────────────────────────────┐
         ▼            ▼                            ▼
  build_guide_index  a_flank / families/*     run_ablation
  qct, featurise     save_block(...)           load_dataset
         │            │                            │
         └────────────┴── io_utils conventions ────┘
                      eng.* blocks, header=1, guide_index
```

Without these two modules, every script would hardcode `/Users/someone/.../ecoli_feature_matrix.csv` and invent its own column naming — Family A couldn’t be swapped in/out cleanly, and human runners couldn’t point at `Runjia/` via `RSI09_ROOT`.

---

## Part 1 — `config.py`: the project’s shared settings

### Why it exists

The RSI09 package runs in three places:

1. From a notebook after `nb.setup()`
2. From a terminal inside the `Runjia/` tree
3. From Jacky’s scripts *outside* that tree, if `RSI09_ROOT` points at `Runjia/`

`config.py` finds the root once, then defines every important path and modelling default relative to it. **Change a file location here; don’t hunt through 50 scripts.**

### Finding `ROOT`

```python
_MARKERS = ("data/raw", "external_data")

def find_project_root():
    # 1) honor RSI09_ROOT if set
    # 2) else walk up from this file
    # 3) else walk up from the current working directory
```

**Workflow meaning:** a folder “counts” as the project only if it contains both `data/raw` and `external_data`. Jacky human scripts set `RSI09_ROOT` so imports resolve even though the script file lives under `Jacky/`.

`ROOT = find_project_root()` runs **at import time** — the moment another file does `from sgrna import config`, paths are ready.

### Directory map (what later code expects)

| Constant | Typical path | Who uses it |
|---|---|---|
| `RAW` | `data/raw/` | Published E. coli / human matrices |
| `REFERENCE` | `data/reference/` | Genome FASTA, gene tables, hg38 |
| `INTERIM` | `data/interim/` | Caches: guide index, QCT tables, human_boundary/ |
| `FEATURE_DIR` | `data/interim/features/` | One CSV per family (`a_flank.csv`, …) |
| `EXTERNAL` | `external_data/` | GapR, RegulonDB, crisprHAL, … |
| `RESULTS` | `results/` | Ablation CSVs, fold checkpoints |

The loop `for _d in (INTERIM, FEATURE_DIR, …): _d.mkdir(...)` quietly creates folders so first-time runs don’t crash on “directory not found.”

### Key file names

```python
BASE_MATRIX = RAW / "ecoli_feature_matrix.csv"
BASE_MATRIX_HEADER_ROW = 1   # title row quirk
ID_COL = "sgRNAID"
TARGET_COL = "cut.score"
GUIDE_INDEX = INTERIM / "guide_index.csv"
QCT_TABLES = INTERIM / "qct_lookup_tables.json"
```

**How later steps use these:**

- Baseline Colab used a Drive path; the *package* always reads `BASE_MATRIX` with `header=BASE_MATRIX_HEADER_ROW`.
- Step 0 writes `GUIDE_INDEX`; Family A and ablations read it.
- `qct.learn_lookup_tables` writes `QCT_TABLES`; `featurise` and `a_flank` load them to score new DNA.

### Biology + modelling constants (the frozen protocol)

```python
FLANK = 1000
UPSTREAM_POSITIONS = 10
DOWNSTREAM_POSITIONS = 15
FLANK_WINDOWS = (50, 250, 500, 1000)

SELECTOR = "xgboost"
N_FEATURES = 300
N_ESTIMATORS = 400
N_SPLITS = 5
SEEDS = (41, 42, 43, 44, 45)
BASELINE = {"r2": 0.29368, "spearman": 0.52782, ...}
```

| Constant | Ties back to the science |
|---|---|
| `FLANK` / windows | How much DNA around the cut Family A is allowed to summarize |
| `UPSTREAM` / `DOWNSTREAM` | One-hot neighborhood sizes in `a_flank.py` |
| `SELECTOR` / `N_*` / `SEEDS` | Same recipe as the USE THIS baseline → ablations stay comparable |
| `BASELINE` | Numeric yardstick printed next to `d_spearman` in ablation tables |
| `SPCAS9_SCAFFOLD` | Constant 3′ RNA for folding features (Family C) — not needed for P0 #1–3, but lives here |

`GAPR_SAMPLES`, Hi-C paths, etc. feed **later** families (supercoiling, nucleoid). Skim for awareness; you don’t need them to understand the P0 spine.

### `describe()`

Prints which key files exist. Sanity check when something “can’t find the matrix.”

---

## Part 2 — `io_utils.py`: house rules for data tables

### Why it exists

Feature engineering is modular on purpose:

```text
a_flank.py  →  features/a_flank.csv
b_energy.py →  features/b_energy.csv
…
build_matrix / load_dataset joins only the families you ask for
```

That only works if every family CSV obeys the same contract. `io_utils` enforces that contract.

### The feature-block contract

```python
def save_block(df, family):
    # must have sgRNAID
    # every other column must start with "eng."
    # no duplicate IDs
    # write FEATURE_DIR/{family}.csv
```

**Workflow meaning:**

| Rule | Why |
|---|---|
| Keyed by `sgRNAID` | Join to the base matrix / guide index without guessing |
| `eng.*` prefix | Engineered columns never silently collide with published names like `p1monomer...` |
| Unique IDs | Duplicate keys would duplicate rows when joining and fake the sample size |

`load_block` / `available_blocks` are the read side: ablation code discovers what’s already built.

### Reading shared inputs

```python
def load_guide_index():
    # error if step 0 wasn’t run

def load_base_matrix(usecols=None, nrows=None):
    # always header=BASE_MATRIX_HEADER_ROW
```

**Workflow meaning:** callers shouldn’t re-implement the title-row quirk or the “forgot build_guide_index” error. One function, one correct behavior.

`base_matrix_columns()` reads headers only (`nrows=0`) — useful when you need names without loading 198 MB.

### `one_hot`

```python
def one_hot(values, prefix, categories):
    # fixed category order → stable column names every run
```

**Workflow meaning:** machine-learning joins break if “A,C,G,T” columns shuffle order between runs. This helper makes encoding deterministic for any categorical series (strand, etc.).

---

## Mental model: config vs io_utils vs baseline

| Need | Where it lives |
|---|---|
| “Where is the E. coli CSV?” | `config.BASE_MATRIX` |
| “How do I open it correctly?” | `io_utils.load_base_matrix` |
| “What are seeds / top-300?” | `config.SEEDS`, `config.N_FEATURES` (mirrors USE THIS script) |
| “How do I save Family A?” | `io_utils.save_block(df, "a_flank")` |
| “Where do ablation results go?” | `config.RESULTS` |

The USE THIS baseline **duplicates** some constants inline (Colab-friendly). The package path is: import `config` + `io_utils` instead of hardcoding.

---

## What you should feel after this guide

- `config.py` is not “boring paths” — it’s the **shared protocol** (flank width, seeds, baseline numbers) that makes Jacky’s human Δρ comparable to Runjia’s E. coli Δρ.
- `io_utils.py` is the **adapter plate** between independent biology modules and one model matrix.

---

## Checklist

- [ ] I know why `RSI09_ROOT` exists for Jacky scripts  
- [ ] I know why `header=1` / `BASE_MATRIX_HEADER_ROW`  
- [ ] I can explain the `eng.*` feature-block rule in one sentence  
- [ ] I know `GUIDE_INDEX` and `QCT_TABLES` are outputs of step 0 that Family A consumes  
