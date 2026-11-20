# Offline learning pack

Flight-readable walkthroughs of the first 6 learning-order topics, plus a
checklist of **every** code file in the GitHub repo (including Jacky / Joshua
Colab scripts that have no `.py` extension).

## Guides (read in order)

| # | File | Topic |
|---|---|---|
| 1 | `01-baseline-model.md` | 5-seed XGBoost baseline |
| 2 | `02-core-config.md` | `config.py` + `io_utils.py` |
| 3 | `03-pipeline-build.md` | guide index → featurise → matrix |
| 4 | `04-feature-family-a.md` | Family A (`a_flank.py`) |
| 5 | `05-model-harness.md` | Ablation harness |
| 6 | `06-human-experiments.md` | Jacky human-boundary runners |

## Checklist for Google Docs / Sheets

- `CHECKLIST-all-codes.md` — checkboxes, **grouped by owner** (Jacky → Joshua → Runjia)
- `CHECKLIST-all-codes.tsv` — same list for Sheets import

### How to download this pack from GitHub

1. Open this folder on the PR branch in the GitHub UI
2. Click the raw file you want, then Save As — **or**
3. On the PR branch page: Code → Download ZIP (gets the whole branch; pack is under `docs/learning-offline/`)

Cursor cloud artifact Download can fail for overwritten zips; GitHub is the reliable path.
