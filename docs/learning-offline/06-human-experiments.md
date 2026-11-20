# 06 — Human experiments (Jacky runners)

**Folder:** `Jacky/human-boundary/scripts/` (7 runners)  
**Role:** Port the E. coli story to human Cas9 *cutting* and test the cross-kingdom wall.

You don’t need every line of every runner memorised. Learn the **shared pattern**, then the purpose of each script. Depth below is heaviest on Tier 1 (`run_human_boundary.py`), because everything else reuses its caches.

## Shared bootstrap (every Jacky human script)

```text
1. _REPO = Path(__file__).resolve().parents[3]   # repo root
2. ROOT  = RSI09_ROOT or _REPO/Runjia
3. os.environ["RSI09_ROOT"] = ROOT; sys.path.insert(0, ROOT)
4. Cache heavy intermediates under Runjia/data/interim/human_boundary/
5. Write tables/JSON under Jacky/human-boundary/results/
```

Import note: scripts say `from sgrna.run_ablation import …`. After the package reorg the module lives at `sgrna.harness.run_ablation`; a shim or path tweak may be needed locally.

---

## `run_human_boundary.py` — Tier 1 (635 lines)

**Docstring goals:** decode → locate → Family A → human ladder → transfer autopsy.

### Lines 26–48 — paths & constants

| Name | Role |
|---|---|
| `OUT` | `Jacky/human-boundary/results/` |
| `CACHE` | `Runjia/data/interim/human_boundary/` |
| `HUMAN_MATRIX` | Noshay human CSV |
| `HG38_FA` / `HG38_GZ` | reference genome |
| `FLANK = 1000` | same window Family A expects |
| `ELECTRONS_TO_BASE` | QCT electron count → A/C/G/T |

### Lines 66–89 — `decode_human`

1. Read only id, `cut.score`, and `p1…p20 monomer.No.electronsraw` (`header=1`)  
2. Map each electron count → base via `ELECTRONS_TO_BASE`  
3. Flag `decoded_ok` if no `N`s  
4. Cache → `CACHE/human_decoded.csv`

### Lines 97–258 — `locate_on_hg38`

**RAM trick:** stream one chromosome at a time, then `del seq`.

`iter_fasta` — yields `(header, sequence)` from `.fa` or `.fa.gz`.

`linear_guide_context` — for `+` or `−` strand, cut upstream / protospacer / PAM / downstream (±1000). Minus strand uses reverse-complement so the strings are always 5′→3′ relative to the guide.

`locate_on_hg38` scan loop:

1. Build `wanted` = unique decoded 20-mers  
2. For each primary chrom (`chr1…22,X,Y,M`):  
   - Find every `GG` → candidate **forward** PAM (`NGG`); check if 20-mer is wanted  
   - Find every `CC` → candidate **reverse** PAM; reverse-complement the 20-mer  
   - First unique hit stores flanks; a **second** genomic copy → mark multi and drop flanks (ambiguous)  
3. Write audit JSON + `CACHE/human_located.csv` (only unique usable guides)

### Lines 266–~340 — `build_human_matrices`

1. `featurise.matrix(protospacers)` → `X_human_base.npy` (~6169 cols)  
2. `a_flank.build(located_index)` → `a_flank_human.csv`  
3. Drop all-NaN flank columns; `hstack` → `X_human_base_a.npy`  
4. Save `meta_human.json` (y, names, family_of)

### Ladder + transfer (rest of file)

- **Human ladder:** shared-column subset / regenerated base / base+A, each via `cross_validate` (or a local CV helper)  
- **Transfer autopsy:** train on E. coli, predict human; ask whether failure is mostly the GC / composition rule  

**Headline numbers to remember:**

| Setup | Approx Spearman |
|---|---|
| Human base | ~0.38 |
| Human base+A (row-wise) | ~0.43 (+0.05) |
| Twin-honest / deduped Δ | ~+0.023 |

---

## `run_human_strand_audit.py` (356 lines)

**Question:** In CRISPRi, Family A mostly tracked **coding strand**. Does that eat the human *cutting* Family A gain?

Flow:

1. Load Tier-1 caches  
2. Load UCSC `refGene.txt.gz` → gene strand at each locus  
3. Build a strand / purine feature column  
4. CV arms: base / strand / Family A / combinations  
5. Also correlate strand with label and with transfer residuals  

**Answer you already know:** strand ρ≈0 with the label; Family A given strand still ~+0.048 → **does not collapse**. Human cutting is not “secretly a strand assay.”

---

## `run_tier2_tier3.py` (463 lines)

| Arm | Idea | Rough outcome |
|---|---|---|
| D1 | K562 DNase/ATAC at human loci | mostly null |
| E1 | Family A on **both** kingdoms for transfer | flips E→H positive ~+0.02 |
| E2 | GC-matched transfer controls | checks composition confound |

---

## `run_human_discovery.py` — H1–H5 (518 lines)

| ID | Question |
|---|---|
| H1 | Capacity / HP ladder (`HUMAN_HPS`: lr 0.3, depth 6) on base and base+A |
| H2 | Additivity — ridge vs boosting |
| H3 | Gene-grouped CV (stricter than row-wise) |
| H4 | Add `i_shape` / `d_mechanics` / `c_folding` on top of base+A |
| H5 | Cross-kingdom transfer with features present on both sides |

Uses Tier-1 caches; builds extra families only when needed.

---

## `run_h6_chromatin.py` (232 lines)

Matched-line ENCODE tracks (HCT116 / HEK / HeLa / HL60) at guide loci. Tiny Δρ; ~null once Family A is already in the model.

## `run_h6_gc_coverage_control.py` (258 lines)

Asks whether chromatin-track signal is confounded with local GC / coverage. Pair with H6 proper.

## `run_twin_honest_followups.py` (309 lines)

Deduped / twin-honest transfer and CV so the Family A Δ isn’t inflated by near-duplicate guides. The ~+0.023 number comes from this honesty cut.

---

## Dependency order (don’t run out of order)

```text
run_human_boundary.py          ← builds caches everything else needs
        │
        ├─ run_human_strand_audit.py
        ├─ run_tier2_tier3.py
        ├─ run_human_discovery.py
        ├─ run_h6_chromatin.py
        ├─ run_h6_gc_coverage_control.py
        └─ run_twin_honest_followups.py
```

---

## Checklist

- [ ] I can describe decode → locate → Family A → CV  
- [ ] I know why location is required for human Family A  
- [ ] I know the strand-audit conclusion (no collapse)  
- [ ] I know transfer with Family A on both sides is the weak positive bridge  
- [ ] I know twin-honest shrinks the raw +0.05 toward ~+0.023  
