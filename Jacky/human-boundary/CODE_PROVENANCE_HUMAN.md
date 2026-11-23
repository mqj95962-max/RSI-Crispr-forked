# Human paper numbers → code provenance

Rule for the report: every quoted result needs a runnable script in the repo that produces (or regenerates) it.

## Status summary

| Claim / number | Code on disk? | Where |
|---|---|---|
| Guide-only E→H ≈ −0.05 | **Yes** | Jacky Tier-1 autopsy + Runjia `kingdom_transfer.py` |
| GC residualise does not rescue | **Yes** | `run_human_boundary.py` → `transfer_autopsy*.json/csv` |
| Ladder 0.382 → 0.434 (+0.052) | **Yes** | `run_human_boundary.py` → `human_ladder.csv` (+ fold CSVs under `Runjia/results/`) |
| Flanks both sides +0.022 / +0.042 | **Yes** | `run_tier2_tier3.py` → `family_a_kingdom_transfer.csv` |
| Twin-honest A gain ≈ **+0.023** | **Yes (misnamed earlier)** | Runjia `human_shape.py --stage 7 --twin` (not a Jacky `run_twin_honest_*`) |
| Strand audit (A survives) | **Yes** | `run_human_strand_audit.py` |
| K562 chromatin null | **Yes** | `run_tier2_tier3.py` → `human_chromatin.csv` |
| H6 matched chromatin | **Yes** | `run_h6_chromatin.py` |
| H1–H5 discovery | **Yes** | `run_human_discovery.py` |
| Twin-grouped capacity / additivity | **Yes** | Runjia `human_additivity_twin.py`, `human_twin_check.py` |
| H6 GC/coverage control | **Missing** | Never committed; was only planned/paused |
| Original writer of early `human_transfer.csv` | **Superseded** | Docstring in `kingdom_transfer.py` says old script not in tree; **use** `python -m sgrna.compare.kingdom_transfer` |

---

## 1. Guide-only kingdom wall (≈ −0.04 to −0.05)

| Item | Path |
|---|---|
| Jacky | `scripts/run_human_boundary.py` → `results/transfer_autopsy.json`, `transfer_autopsy_by_gc_decile.csv` |
| Runjia (bootstrapped / both directions) | `Runjia/sgrna/compare/kingdom_transfer.py` → `Runjia/results/kingdom_transfer.csv`, `kingdom_transfer_boot.csv` |
| Evidence also cited | `Runjia/results/human_transfer.csv` (historical; regenerate via `kingdom_transfer.py`) |

## 2. GC autopsy (symptom, not rescue)

| Item | Path |
|---|---|
| Code | `run_human_boundary.py` (`transfer_autopsy`, residualise GC/GC², deciles) |
| Outputs | `transfer_autopsy.json`, `transfer_autopsy_by_gc_decile.csv`, `human_gc_shape.json`, `gc_quadratic_proper.json`, `gc_matched_transfer.csv` |

## 3. Within-human Family A ladder (+0.052 row-wise)

| Item | Path |
|---|---|
| Code | `run_human_boundary.py` (`run_ladder`) |
| Primary table | `results/human_ladder.csv` |
| Fold-level | `Runjia/results/folds_human_base_cv.csv`, `folds_human_base_a_cv.csv` (and related `folds_human_*`) |

## 4. Flanks on both sides (sign flip)

| Item | Path |
|---|---|
| Code | `run_tier2_tier3.py` |
| Output | `results/family_a_kingdom_transfer.csv` (base −0.049; a_flank +0.042; base+A +0.022 class) |

## 5. Twin-honest / twin-grouped Family A ≈ +0.023

**Important correction:** There is **no** `Jacky/.../run_twin_honest_followups.py` in git history or on disk. That name was a project-notes placeholder.

The **+0.023** (measured **+0.0226**) is Runjia’s twin-grouped re-run of the human flank increment:

| Item | Path |
|---|---|
| Code | `Runjia/sgrna/compare/human_shape.py` with `--stage 7 --twin` |
| Related | `human_twin_check.py`, `human_additivity_twin.py` |
| Numbers | EXTENSION_LOG §21 / PROGRESS_REPORT: base 0.3063 → base+A 0.3289, Δ **+0.0226** |
| Outputs | `Runjia/results/post_freeze/human_shape_ablation_twin.csv`, `human_additivity_twin*.csv`, `human_twin_check.csv` |

**Paper rule:** Quote +0.023 only with the twin-grouped runner above, not as if it came from Jacky’s row-wise ladder.

## 6. Strand audit

| Item | Path |
|---|---|
| Code | `scripts/run_human_strand_audit.py` |
| Outputs | `human_strand_audit.json`, `human_strand_family_a.csv`, `human_strand_marginals.csv` |

## 7. Chromatin

| Item | Path |
|---|---|
| K562 Tier 2 | `run_tier2_tier3.py` → `human_chromatin.csv` |
| H6 matched lines | `run_h6_chromatin.py` → `human_h6_*.csv/json` |
| H6 GC/coverage control | **NOT FOUND** — no file, no git add. Tracker had it as paused. **Cannot cite “chromatin is not just GC/coverage” until this script exists and is run.** |

## 8. Discovery H1–H5

| Item | Path |
|---|---|
| Code | `scripts/run_human_discovery.py` |
| Outputs | `human_discovery_*.csv/json` |

---

## Truly missing / action needed

1. **`run_h6_gc_coverage_control.py`** — never landed. Either rewrite from the H6 commit notes / Part 6 intent, or drop any claim that depends on it.  
2. **Do not hunt for `run_twin_honest_followups.py`** — use Runjia twin-grouped scripts instead; update briefing language accordingly.  
3. If the paper cites early `human_transfer.csv` numbers, pin them to **`kingdom_transfer.py`** (current) rather than the missing pre-`src/` writer.

## Jacky scripts present (complete for human boundary)

```
run_human_boundary.py
run_human_strand_audit.py
run_tier2_tier3.py
run_human_discovery.py
run_h6_chromatin.py
```
