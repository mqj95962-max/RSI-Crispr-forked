# P0 #9 — Jacky human Tier-1 / `run_human_boundary.py` (contextual guide)

**Source file:** `Jacky/human-boundary/scripts/run_human_boundary.py` (~635 lines)  
**Job in the project:** port the E. coli story to **human Cas9 cutting** — decode → locate on hg38 → build Family A → human CV ladder → transfer autopsy — and write results under `Jacky/human-boundary/results/`.

---

## Where this sits in the whole pipeline

```text
E. coli spine you already learned
  baseline protocol + qct decode idea + featurise + a_flank + cross_validate
        │
        ▼
 ★ run_human_boundary.py ★
  same ideas, human matrix + hg38
        │
        ▼
 caches: interim/human_boundary/
 results: human_ladder.csv, transfer_autopsy*.json/csv, …
        │
        ▼
 Later Jacky scripts (strand audit, tier2/3, discovery, twin, H6)
 all assume these caches exist
```

This is **Tier 1**. Other human runners are P1+; they consume what this file builds.

---

## Shared bootstrap (why the top of the file looks loud)

```python
ROOT = RSI09_ROOT or repo/Runjia
sys.path.insert(0, ROOT)
from sgrna import config, featurise, ...
from sgrna.features import a_flank
from sgrna.run_ablation import cross_validate, _impute
```

**Intent:** Jacky’s script lives outside `Runjia/`, but all data/constants live inside it. Setting `RSI09_ROOT` makes `config.find_project_root()` succeed (see P0 config guide). Heavy intermediates go to `config.INTERIM / "human_boundary"`; publishable tables go to `Jacky/human-boundary/results/`.

---

## The five jobs (read as a pipeline, not as 600 lines)

### Job 1 — Decode human protospacers

```python
def decode_human(...):
    # read electron columns p1…p20 from human_feature_matrix.csv (header=1)
    # map via ELECTRONS_TO_BASE → protospacer string
    # cache human_decoded.csv
```

**Same idea as `qct.decode_protospacers`**, pointed at the human matrix.  
**Output:** id, `y` (cut.score), `protospacer`, `decoded_ok`.

Also runs `gc_shape_report` — how spacer GC relates to the human label (context for the transfer autopsy).

### Job 2 — Locate unique NGG hits on hg38

```python
def locate_on_hg38(decoded, ...):
    # stream each primary chromosome (RAM-friendly)
    # find GG (forward) / CC (reverse) PAM candidates
    # keep flanks (±1000) only for unique hits; multi-copy → drop
    # write human_located.csv + locate audit JSON
```

**Same job as `build_guide_index`, different genome.**  
**Why unique matters:** Family A needs one unambiguous neighborhood.  
**Why stream chromosomes:** hg38 is huge; load → scan → `del seq`.

### Job 3 — Build matrices

```python
def build_human_matrices(loc, ...):
    base = featurise.matrix(protospacers)          # ~6169 “published dialect” cols
    block = a_flank.build(located_index)           # eng.flank.*
    X_full = hstack(base, flank)
    # cache X_human_base.npy, X_human_base_a.npy, meta_human.json
```

**Intent:** human “base” and “base+A” arms speak the **same feature languages** as E. coli package code — so later transfer / discovery comparisons are meaningful.

### Job 4 — Human-only ladder

```python
def run_ladder(...):
    # CV arms: regenerated_base, base_plus_a_flank, a_flank_only,
    #          shared_published_cols (intersection of E. coli & human CSV columns)
    # each via cross_validate (same harness as P0 #8)
    # → human_ladder.csv
```

**Question:** on located human guides, how much does Family A add under the frozen exam protocol?  
**Headline to remember:** base ~0.38 → base+A ~0.43 (row-wise); twin-honest follow-ups later shrink the Δ — but Tier 1 establishes the raw ladder.

### Job 5 — Transfer autopsy

```python
def transfer_autopsy(...):
    # train selector+champion on E. coli shared columns
    # predict human shared columns
    # report overall Spearman + by GC decile
    # residualise y & pred against GC + GC² — does transfer change?
```

**Question:** when E. coli→human transfer fails, is it largely a **GC habit** of the bacterial model?  
Not “train human model” — **diagnose cross-kingdom failure modes**.

---

## `main()` control flow

```text
require human matrix, QCT tables, V-column mapping
decode (+ GC shape)
if --skip-locate: lightweight transfer path on all decoded rows; exit
else:
  locate → require enough unique hits
  build matrices → ladder → transfer autopsy
```

`--force` rebuilds caches. `--skip-locate` is for debugging transfer without hg38.

---

## Inputs / outputs cheat sheet

| Stage | Inputs | Outputs |
|---|---|---|
| Decode | `human_feature_matrix.csv` | `human_decoded.csv` |
| Locate | decoded + hg38 FASTA | `human_located.csv`, `human_locate_audit.json` |
| Matrices | located + featurise + a_flank + QCT/V maps | `X_human_base*.npy`, `a_flank_human.csv`, `meta_human.json` |
| Ladder | matrices | `human_ladder.csv` |
| Transfer | E. coli + human shared cols | `transfer_autopsy.json`, `transfer_autopsy_by_gc_decile.csv` |

**Downstream consumers (don’t run them first):** strand audit, tier2/3, discovery H1–H5, twin-honest, H6 — all expect Tier-1 caches.

---

## How this connects to P0 #1–#8

| E. coli piece | Human Tier-1 analogue |
|---|---|
| Baseline / `cross_validate` | Ladder + autopsy scoring |
| `qct` electron decode | `decode_human` |
| `build_guide_index` | `locate_on_hg38` |
| `featurise.matrix` | human base matrix |
| `a_flank.build` | human Family A block |
| `config` / `RSI09_ROOT` | bootstrap at top of file |

You are not learning a new sport — you are playing the **same sport on another field**.

---

## Checklist

- [ ] I can narrate decode → locate → matrices → ladder → autopsy  
- [ ] I know why location is required for human Family A  
- [ ] I know Tier-1 caches unlock later Jacky scripts  
- [ ] I know transfer autopsy diagnoses E→H failure, not just scores human CV  
- [ ] I know twin/H6 are *later* honesty/chromatin checks, not part of this file’s core job  
