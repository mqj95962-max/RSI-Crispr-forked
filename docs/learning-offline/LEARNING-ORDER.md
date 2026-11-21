# Recommended learning order (full repo)

Updated after a full inventory of **every** code file (197), including Jacky/Joshua
extensionless Colab scripts.

You do **not** need to read 197 files line-by-line. Follow **P0 → P1 → P2**; treat **P3** as optional.

## The spine (P0) — do these first

These nine files are the whole project in miniature. Match them to offline guides 01–06.

| # | File | Why |
|---|---|---|
| 1 | `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py` | What “the model” is (leakage-safe 5-seed XGBoost) |
| 2 | `Runjia/sgrna/config.py` | Paths, windows, seeds, constants |
| 3 | `Runjia/sgrna/io_utils.py` | Feature-block conventions (`eng.*`) |
| 4 | `Runjia/sgrna/build/build_guide_index.py` | Anonymous rows → located guides + flanks |
| 5 | `Runjia/sgrna/build/qct.py` | How sequences are decoded from electron columns |
| 6 | `Runjia/sgrna/build/featurise.py` | Rebuild the published base from a 20-mer |
| 7 | `Runjia/sgrna/features/a_flank.py` | Family A — the big biology win |
| 8 | `Runjia/sgrna/harness/run_ablation.py` | How ρ / Δρ is measured |
| 9 | `Jacky/human-boundary/scripts/run_human_boundary.py` | Your human Tier-1 runner (decode→locate→A→ladder) |

Offline guides `01`–`06` already cover 1–9 (qct is inside the pipeline guide).



## Contextual guides (preferred — rewritten after feedback)

Purpose + data-flow teaching for the **full P0 spine** (not syntax line-by-line):

| Topic | File | P0 coverage |
|---|---|---|
| Baseline | [`p0-contextual/01-baseline.md`](p0-contextual/01-baseline.md) | #1 |
| Config + I/O | [`p0-contextual/02-config-and-io.md`](p0-contextual/02-config-and-io.md) | #2–#3 |
| Pipeline build | [`p0-contextual/03-pipeline-build.md`](p0-contextual/03-pipeline-build.md) | #4–#6 |
| Family A | [`p0-contextual/04-a-flank.md`](p0-contextual/04-a-flank.md) | #7 |
| Ablation harness | [`p0-contextual/05-run-ablation.md`](p0-contextual/05-run-ablation.md) | #8 |
| Human Tier-1 | [`p0-contextual/06-human-boundary.md`](p0-contextual/06-human-boundary.md) | #9 |

HTML: `p0-contextual/html/index.html`.

The older `p0-line-by-line/` guides remain as optional literal notes.


## Next wave (P1)

| File | Why |
|---|---|
| `Runjia/sgrna/build/genome.py` | Circular genome / locate helpers |
| `Runjia/sgrna/build/build_features.py` + `build_matrix.py` | Glue that builds & joins families |
| `Runjia/sgrna/harness/notebook.py` | How the team actually drives the pipeline |
| `Runjia/sgrna/controls/floors.py` + `diagnose.py` | Permutation floors & “why didn’t it help?” |
| `Joshua/FINAL_baseline_ecoli_sgRNA_model_5seeds.py` | Teammate baseline (compare to USE THIS) |
| `Joshua/shap_baseline_analysis.py` | How SHAP is done on saved folds |
| `Joshua/XGBoost 300 features` | Joshua’s Colab **template** — read this one, then skim his variants |
| `Jacky/FINAL_baseline_model_5seeds.py` | Your baseline copy |
| `Jacky/.../run_human_strand_audit.py` | Strand does **not** collapse human Family A |
| `Jacky/.../run_tier2_tier3.py` | Chromatin null + transfer with A on both sides |
| `Jacky/.../run_human_discovery.py` | H1–H5 capacity / grouped / extras |
| `Jacky/.../run_twin_honest_followups.py` | Twin-honest Δ (~+0.023) — **P2/optional for this pack** |
| `Jacky/orientation-controls/scripts/run_intergenic_orientation.py` | Orientation story (prefer this copy, not agent-notes/) |

### P1 contextual guides (preferred)

Same purpose/data-flow style as P0 contextual. Twin/H6 discovery stays in P2.

| Topic | File | P1 coverage |
|---|---|---|
| Build glue | [`p1-contextual/01-build-glue.md`](p1-contextual/01-build-glue.md) | genome / build_features / build_matrix / notebook |
| Controls | [`p1-contextual/02-controls-floors-diagnose.md`](p1-contextual/02-controls-floors-diagnose.md) | floors + diagnose |
| Joshua + baselines | [`p1-contextual/03-joshua-and-baselines.md`](p1-contextual/03-joshua-and-baselines.md) | teammate baselines, Colab template, SHAP |
| Jacky human + orientation | [`p1-contextual/04-jacky-human-and-orientation.md`](p1-contextual/04-jacky-human-and-orientation.md) | human Tier-1→4 + orientation/strand controls |

HTML: `p1-contextual/html/index.html`.

## Deepen (P2)

- Other families after A: `d_mechanics`, `d_supercoiling`, `g_transcription`, `c_folding`, `i_shape`
- Human follow-ups: `run_h6_chromatin.py`, `run_h6_gc_coverage_control.py`, twin-honest follow-ups
- Cross-screen: `screens/kingdom_transfer.py`, `human_baseline.py`, `cui_screen.py`
- Strand (E. coli CRISPRi): `strand/strand_families.py`
- One Joshua regional-QCT Colab + his random-control test
- `Jacky/Features A-D builder` (early Colab feature work)

## Later / optional (P3)

- Remaining Jacky/Joshua Colab variants (same recipe, different feature paste)
- Duplicate scripts under `Jacky/agent-notes/scripts/` (copies of orientation-controls)
- Most of `post_freeze/`, Colab benches, figure scripts
- `__init__.py` stubs

## Suggested flight plan

1. `p0-contextual/` guides 01–06 + tick every **P0** checkbox  
2. `p1-contextual/` 01–04 (glue → controls → Joshua/SHAP → human tiers + orientation)  
3. One P2 family + H6 / twin honesty only when you need those claims  
4. Everything else only when you need it for a claim

See `CHECKLIST-all-codes.md` for the full tick-list with priority tags.


## Literal line-by-line (beginner)

For zero coding background, use **`p0-line-by-line/`** (glossary + every line of the 9 P0 files explained in plain English).
Start at `p0-line-by-line/README.md` / `00-glossary.md`.
