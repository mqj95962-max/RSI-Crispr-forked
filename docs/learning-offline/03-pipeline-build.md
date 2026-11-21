# 03 — Pipeline build (guide index → featurise → matrix)


> **Updated teaching guide:** for purpose/data-flow explanations (recommended), read [`p0-contextual/03-pipeline-build.md`](p0-contextual/03-pipeline-build.md) instead of relying only on this shorter summary.

**Primary files:**  
- `Runjia/sgrna/build/build_guide_index.py` (~165)  
- `Runjia/sgrna/build/featurise.py` (~125)  
- Also skim: `build_features.py`, `build_matrix.py`

**Role:** Turn anonymous published rows into located guides and regenerable feature matrices.

## Pipeline cartoon

```text
published CSV (no real sequence stored)
        │
        ▼
  decode protospacer from QCT electron columns   (qct.py)
        │
        ▼
  locate on NC_000913.2 + store ±1 kb flanks     (build_guide_index.py)
        │
        ▼
  regenerate ~6169 base columns from 20-mer      (featurise.py)
        │
        ▼
  build Family A/B/... blocks                    (features/*.py via build_features.py)
        │
        ▼
  join into one matrix for ablation              (build_matrix.py)
```

---

## `build_guide_index.py` — step 0

### Docstring (lines 1–29)

Why: matrix IDs like `aaeAb3241_107_Cas9` don’t tell you *where* the cut is. Supercoiling, nucleoid, transcription, Family A flanks all need coordinates.

### `build()` (lines 44–132) — walkthrough

1. **Load + decode** (`qct.load_qct_frame`, `decode_protospacers`) → 20-mer strings  
2. **Load genome**, index NGG sites  
3. **For each guide:** `genome.locate_protospacer` → strand, left/right, PAM, copy count; `guide_context` → upstream/downstream strings of length `flank`  
4. **QC flags:** `located`, `unique_in_genome`, `pam_is_ngg`  
5. **Replication landmarks:** distance to oriC, replichore, whether guide is on leading strand  
6. Rename target to `cut_score`, keep a clean column list  

### `main()` (lines 135–165)

Writes `GUIDE_INDEX` CSV, then learns QCT k-mer lookup tables so Family A can extend tensors into flanks. Warns about rare k-mers that will be NaN later.

**What you should be able to say:** step 0 turns anonymous rows into (sequence + genomic locus + flanks).

---

## `featurise.py` — regenerating the published base

### Docstring (lines 1–34)

Reverse-engineering claim: **6,169 / 6,232** published columns are pure functions of the 20-mer (V one-hots + QCT tables). Hand-named columns (~31) are omitted because they aren’t clean functions of sequence.

Rule: **don’t mix** published CSV rows with featurise rows — rebuild everything the same way.

### `feature_names` (47–59)

Builds ordered names: identified V columns, then QCT `p{pos}{unit}.{prop}` names.

### `matrix` (62–99) — the workhorse

Input: list of 20-mers. Output: `(n, 6169)` float32 + name list.

1. **V block:** for each mapped column, check if the k-mer at that position equals the column’s k-mer → 0/1  
2. **QCT block:** look up each k-mer in the learned tables → published tensor value (or NaN)  
3. `hstack` V and Q  

### `verify_against_published` (102–125)

Rebuilds real guides and checks cell-by-cell agreement with the published matrix (should be ~100% on shared columns).

---

## `build_features.py` / `build_matrix.py` (skim)

- `build_features` — CLI/notebook wrapper: for each family name, call `features.<fam>.build(index)` and `save_block`  
- `build_matrix` — join base + selected blocks into a cached `.npy` + metadata for ablations  

---

## Checklist

- [ ] I can draw the pipeline cartoon from memory  
- [ ] I know why location is required for Family A  
- [ ] I know featurise rebuilds base columns from the 20-mer only  
- [ ] I know not to mix published rows with featurise rows  
