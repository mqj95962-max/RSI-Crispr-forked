# P1 — Build glue: genome, build_features, build_matrix, notebook

**Source files:**  
- `Runjia/sgrna/build/genome.py`  
- `Runjia/sgrna/build/build_features.py`  
- `Runjia/sgrna/build/build_matrix.py`  
- `Runjia/sgrna/harness/notebook.py`  

**Job in the project:** the “how you actually run the factory” layer — locate DNA on a circular chromosome, build every feature family the same way, cache a joinable matrix, and drive it all from one notebook API.

---

## Where this sits (after P0)

```text
P0 taught: baseline exam + config + step0/qct/featurise + a_flank + ablation + human Tier-1

P1 glue answers: “How does the team *operate* that machinery day to day?”

  genome.py          ← primitives step0 / orientation / positional features call
  build_features.py  ← loop: for each family → build(index) → save_block
  build_matrix.py    ← cache published base; join eng.* blocks → load_dataset
  notebook.py        ← nb.setup(); nb.build_index(); nb.ablate([...])
```

You already met **what** Family A and ablation are. These files are **how batches get produced** without re-pasting Colab cells.

---

## 1. `genome.py` — circular-chromosome helpers

**Why it exists:** E. coli’s chromosome is a circle. A guide near coordinate 1 has a normal upstream flank that wraps past the last base. Naive string slicing would invent fake DNA or crash.

**What it provides (intent groups):**

| Capability | Used by |
|---|---|
| Load NC_000913.2 FASTA | `build_guide_index`, anything needing sequence |
| Reverse-complement | Minus-strand hits |
| Index / locate NGG-flanked protospacers | Step 0 location |
| `guide_context` (± flank strings) | Family A inputs |
| Replication landmarks (ori/ter, replichore, fork direction) | Guide-index columns; later positional biology |

**Mental model:** step 0’s “find the guide” chapter is mostly orchestration; the geometry lives here. Human Tier-1 reimplements a **linear** hg38 locate instead — different genome topology, same *job*.

---

## 2. `build_features.py` — step 1: one family at a time

```text
load_guide_index()
for name in families:
    block = REGISTRY[name].build(index)
    save_block(block, name)   # eng.* CSV under FEATURE_DIR
```

**Why it exists:** Families are independent modules (`a_flank`, `c_folding`, …). Rebuilding A must not touch G. Missing GapR data should fail `d_supercoiling` alone, not kill the whole run (`try/except` per family).

**Inputs:** guide index (+ each family’s own external files).  
**Outputs:** `data/interim/features/{family}.csv`.  
**CLI / notebook:** `--all`, `--families a_flank …`, or `--self-contained` (no external datasets).

**Connection to P0:** `a_flank.main()` is the single-family version of this loop. Ablation later only *reads* blocks that this step wrote.

---

## 3. `build_matrix.py` — step 2: cache base + join blocks

**Problem:** the published CSV is ~198 MB; pandas tokenization is slow. Ablating ten families must not re-parse it ten times.

**Solution:**

1. `build_cache()` → `interim/base_X.npy` + `base_meta.json` (ids, y, feature names)  
2. `load_dataset(families)` → load cache, left-join each family’s `eng.*` columns, build `family_of` tags (`"base"` vs `"a_flank"` …)  
3. Optional `--export csv` → Colab-shaped merge so teammates can point `DATA_PATH` at it

**Consumers:** `run_ablation.run` / `cross_validate` via `load_dataset`; diagnose/floors analyses that need the same matrix language.

**Rule you already know:** don’t mix featurise-rebuilt rows with raw published rows unless everything went through one path.

---

## 4. `notebook.py` — the team’s steering wheel

**Why it exists:** `!python -m sgrna.build_features` in Colab dumps text and returns nothing to inspect. `nb.build_features(...)` prints a short summary and returns objects.

**Typical session:**

```python
import sgrna.notebook as nb
nb.setup()                 # find ROOT, install deps if needed, import config
nb.build_index()           # step 0
nb.build_features("all")   # or ["a_flank"]
nb.cache_matrix()
nb.ablate(["a_flank"], group="bin100k", permute=True)
```

**Important:** almost no duplicated science — wrappers **delegate** to the modules you studied in P0/P1. A bugfix in `run_ablation` shows up here automatically.

`setup()` also handles Colab vs local quirks (Drive, `RSI09_ROOT`, requirement installs).

---

## How these four connect

```text
genome ──used by──► build_guide_index (P0)
                         │
                         ▼
                  build_features ──► FEATURE_DIR/*.csv
                         │
                         ▼
                  build_matrix / load_dataset ──► X, y, family_of
                         │
                         ▼
                  run_ablation / diagnose / floors
                         ▲
                  notebook.py calls all of the above
```

---

## Checklist

- [ ] I know why the chromosome being circular matters for flanks  
- [ ] I can explain “one CSV per family” as the modularity strategy  
- [ ] I know why the base matrix is cached as `.npy`  
- [ ] I know `nb.*` is a front end, not a second implementation  
