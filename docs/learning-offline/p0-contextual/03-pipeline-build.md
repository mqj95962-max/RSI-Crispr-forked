# P0 pipeline build — QCT → guide index → featurise (contextual guide)

**Source files (LEARNING-ORDER P0 #4–#6):**  
1. `Runjia/sgrna/build/qct.py`  
2. `Runjia/sgrna/build/build_guide_index.py`  
3. `Runjia/sgrna/build/featurise.py`  

**Job in the project:** turn “anonymous spreadsheet rows” into **DNA letters + genomic addresses + regenerable feature matrices** that Family A and human experiments can reuse.

> Treat this as **one pipeline story** across three files, not three unrelated scripts.

---

## The problem these three files solve together

The published E. coli matrix is awkward for biology follow-ups:

| What’s in the CSV | What’s missing |
|---|---|
| Thousands of feature columns | The actual 20-letter protospacer string (not stored plainly) |
| A name like `aaeAb3241_107_Cas9` | Exact chromosome coordinates + flanking DNA |
| Features for 13,880 guides only | A way to featurise *new* guides (human, curated cohort) the same way |

So the pipeline does:

```text
qct.py
  decode letters from electron-count columns
  learn k-mer → chemistry lookup tables
        │
        ▼
build_guide_index.py   (= “step 0”)
  find each 20-mer on NC_000913.2
  store ±1 kb flanks, QC flags, replication landmarks
  write guide_index.csv (+ save QCT tables)
        │
        ▼
featurise.py
  given only a 20-mer, rebuild ~6169 published-style columns
  (so human / new guides match the E. coli representation)
        │
        ▼
Family A / ablations / Jacky human runners
```

**Baseline (P0 #1) can score the published CSV without this pipeline.**  
**Family A and human work cannot** — they need location and/or regenerable features.

---

## File 1 — `qct.py`: decode sequences & learn chemistry dictionaries

### Why “QCT”?

**Quantum Chemical Tensor** columns in the paper describe local DNA chemistry. Crucially, one series — `p{i}monomer.No.electronsraw` — takes only four values across the whole screen, matching the four bases’ valence-electron counts:

| Electrons | Base |
|---:|---|
| 42 | C |
| 48 | T |
| 50 | A |
| 56 | G |

So the matrix secretly *encodes* the 20-mer. `ELECTRONS_TO_BASE` is that codebook.

### Job A — Decode protospacers

```python
def decode_protospacers(frame):
    # read p1…p20 monomer electron columns
    # map each number → letter (or N if missing)
    # return table: sgRNAID, cut.score, protospacer, decoded_ok
```

**Inputs:** QCT slice of the published matrix (via `load_qct_frame`, which caches those ~316 columns so you don’t re-parse a 198 MB CSV every time).  
**Outputs:** readable DNA strings + a flag for incomplete decodes.  
**Consumers:** `build_guide_index`, Jacky’s `decode_human` (same electron idea on the human matrix), any check that needs the 20-mer.

### Job B — Learn lookup tables (extend chemistry beyond the spacer)

```python
def learn_lookup_tables(protospacers, frame):
    # for each (unit, property) QCT column family:
    #   watch which DNA snippet (k-mer) produced which number
    #   demand consistency (same k-mer → same value)
    # return nested dict: unit → property → kmer → float
```

**Workflow meaning:** once you know “dimer `AT` at a position had H-bond stacking = X in the paper,” you can ask for that same X on DNA **outside** the 20-mer (PAM, flanks). Family A’s `qct.profile(...)` does exactly that.

If one k-mer mapped to two different values, the “pure function of sequence” idea would be false — the function **raises** instead of guessing.

`save_tables` / `load_tables` persist this dictionary to `config.QCT_TABLES`.

### Job C — Apply tables to arbitrary DNA

```python
def profile(seq, unit, prop, tables): ...
def summarise(values, prefix): ...
```

**Consumers:** `a_flank.py` window summaries; anywhere you need a chemistry track along a sequence. Unknown k-mers → NaN → later median imputation (same philosophy as the baseline).

### Also: `parse_sgrna_id`

Pulls gene name / b-number / offset out of IDs like `aaeAb3241_107_Cas9` for the guide index metadata — convenience, not chemistry.

---

## File 2 — `build_guide_index.py`: step 0, locate guides on the chromosome

### Why step 0 exists

Supercoiling, transcription context, off-targets, and **Family A flanks** all need to know *where* a guide sits. An ID string is not a coordinate.

### What `build()` does (data flow)

```text
load_qct_frame → decode_protospacers
        │
        ▼
load E. coli genome (NC_000913.2); index NGG sites
        │
        ▼
for each decoded 20-mer:
   locate on +/− strand
   cut upstream / downstream strings of length FLANK (1000)
   record PAM, copy count
        │
        ▼
QC flags: located, unique_in_genome, pam_is_ngg
replication landmarks: ori distance, replichore, leading strand
        │
        ▼
DataFrame ready to write as guide_index.csv
```

Important code ideas (grouped by intent):

```python
hits = genome.locate_protospacer(proto, g)
ctx = genome.guide_context(h["left"], h["right"], h["strand"], flank, g)
# …
out["unique_in_genome"] = out["n_genome_copies"] == 1
out["pam_is_ngg"] = out["pam"].fillna("").str.endswith("GG")
```

| Field | Why biology / ML care |
|---|---|
| `upstream` / `downstream` | Raw DNA Family A summarizes |
| `left` / `right` / `strand` | Locus for GapR, Hi-C, gene strand audits |
| `unique_in_genome` | Multi-copy → ambiguous flanks; don’t silently average |
| `pam_is_ngg` | Cas9 requirement check on the recovered hit |
| `ori_distance` / `replichore` | Replication-context features / controls later |

### What `main()` adds

1. Writes `config.GUIDE_INDEX`  
2. Unless `--skip-qct-tables`, calls `qct.learn_lookup_tables` + `save_tables`  
3. Prints coverage of rare k-mers (will be NaN in flanks → imputed later)

**Outputs this step is famous for:**  
`data/interim/guide_index.csv` and `data/interim/qct_lookup_tables.json`.

**Consumers:** `a_flank.build(index)`, `io_utils.load_guide_index()`, human code that *mirrors* this pattern on hg38, ablation grouping by gene/`left`.

---

## File 3 — `featurise.py`: rebuild the published feature language from a 20-mer alone

### Why it exists

The project was capped at 13,880 rows because that’s how many guides Noshay published features for. Reverse engineering recovered:

- **V columns** ≈ position×k-mer one-hot indicators  
- **QCT columns** ≈ lookup-table chemistry  

Together **~6,169 / 6,232** columns are regenerable from the protospacer alone. Hand-named messy columns (~31) are deliberately omitted (not clean functions of sequence).

### The golden rule

> **Featurise everything the same way.**  
> Do not mix rows from the published CSV with rows from this module. Rebuild old rows through `featurise` too if you need a combined matrix.

Otherwise “same column name” might not mean “same computation,” and human vs E. coli comparisons become unfair.

### What `matrix(protospacers)` returns

```python
X, names = featurise.matrix(["ACGT...20...", ...])
# X shape ≈ (n_guides, 6169) float32
# names = V column names + QCT column names
```

**Inside (intent, not every loop index):**

1. Load V-column mapping + QCT tables (artifacts from earlier reverse-engineering / step 0).  
2. For each V column: look at the DNA snippet at the mapped position → 1 if it matches that column’s k-mer, else 0.  
3. For each QCT column: look up the snippet in the learned table → chemistry float (or NaN).  
4. Horizontally stack V then Q.

**Inputs:** list of 20-mers (and on-disk mappings/tables).  
**Outputs:** numeric matrix in the *published feature dialect*.  
**Consumers:**

- Expanding to crisprHAL’s curated cohort  
- Jacky `build_human_matrices`: `featurise.matrix(loc["protospacer"])` then hstack Family A  
- Any “base” arm in ladders (human base vs base+A)

`verify_against_published` rebuilds real guides and checks cell agreement — the trust check that featurise isn’t inventing a new language.

---

## How the three files connect to the baseline & Family A

```text
USE THIS baseline
  reads published CSV columns directly (no featurise required)

Family A (next P0 topic)
  needs guide_index flanks + QCT tables from step 0 / qct.py

Human Tier-1
  decode (qct idea) → locate on hg38 (guide_index idea)
  → featurise.matrix for “base” → a_flank.build for “+A”
  → same CV spirit as baseline / run_ablation
```

So: **baseline proves prediction on the frozen table**; **this pipeline makes the table portable and location-aware** so new biology can be bolted on without lying about inputs.

---

## Suggested reading order inside this guide

1. Skim the cartoon at the top until it feels inevitable  
2. `qct.py`: decode + learn tables (ignore column-regex helpers on first pass)  
3. `build_guide_index.py`: `build()` then `main()`  
4. `featurise.py`: docstring + `matrix()` only; leave `verify_*` for later  

---

## Checklist

- [ ] I can explain why electron counts reveal DNA letters  
- [ ] I know what `guide_index.csv` enables that the raw CSV doesn’t  
- [ ] I know why unique NGG hits matter for flanks  
- [ ] I know featurise exists to **port** the published feature language to new guides  
- [ ] I know not to mix published rows with featurised rows  
