# Human baseline ρ ≈ 0.472 — settings for Runjia (item 4)

**Config that produced the quoted ρ ≈ 0.472** (Jacky’s early personal run):

| knob | value |
|---|---|
| `n_features` (selected columns) | **400** |
| `n_estimators` | **1000** |
| other XGBoost knobs | **not changed** (library defaults) |

## Caveats (please keep in the report)

1. This was Jacky’s **own early XGBoost script**, **before** the team merged
   pipelines — **not** the current SLICER / `Runjia/sgrna` harness that writes
   `results/human_transfer.csv` (that file’s within-human CV is ~0.404).
2. On human, **number of features** had a usable sweet spot; **`n_estimators`
   kept improving R²** with no clear plateau (unlike bacteria). So 0.472 is a
   point on that curve, not a locked global optimum.
3. Original script is **not** in `src/`. If 400/1000 under the current harness
   does not reproduce ~0.472, treat 0.472 as **historical** and keep the
   cross-kingdom claim on the **sign** of transfer (CIs already exclude zero).

## Suggested report wording

> A teammate’s earlier personal XGBoost grid on the human matrix reached
> ρ ≈ 0.472 at 400 selected features and 1000 estimators (defaults otherwise).
> That run is not the current harness; within-harness human CV is ~0.40. The
> cross-kingdom conclusion does not depend on 0.472: transfer is negative both
> ways with bootstrap intervals excluding zero.
