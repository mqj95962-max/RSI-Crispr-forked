# Human discovery — first results (H1–H5)

**Date:** 18 November 2026 (Asia/Singapore)  
**Runner:** `scripts/run_human_discovery.py`  
**Plan:** `DISCOVERY_PLAN.md`

Primary sweep used seed **41** (5 folds). Capacity arms confirmed on seeds **41–43** in `results/human_discovery_capacity_3seed.csv`.

---

## Headline

The largest human gain we can unlock **right now** is **model capacity / hyperparameters**, not a new sequence family.

| Arm | ρ seed 41 | ρ mean seeds 41–43 | vs base champion (3-seed) |
|---|---:|---:|---:|
| Base + bacterial champion HPs | 0.382 | **0.383** | — |
| Base + deeper/faster HPs (`max_depth=6`, `lr=0.3`, 400 trees, 400 feats) | 0.476 | **0.474** | **+0.091** |
| Base + Family A (champion) | 0.434 | **0.431** | +0.048 |
| Base + Family A + deeper HPs | 0.507 | **0.501** | **+0.118** |
| Base+A + shape / mechanics / folding (seed 41) | 0.422–0.434 | — | ≤0 vs base+A |
| Base+A + all extras + deeper HPs (seed 41) | 0.491 | — | below base+A+HPs |

Shape, mechanics, and folding on top of Family A **do not help** (same pattern as bacteria: shape ≈ reparameterisation of composition).

---

## H2 — Additivity

| Arm | Ridge | XGB (depth 6) | Ridge / XGB |
|---|---:|---:|---:|
| Base | 0.315 | 0.475 | **0.66** |
| Base+A | 0.346 | 0.507 | **0.68** |

Confirms Runjia’s claim: human is far less additive than *E. coli* (~0.96 there). Deeper trees are not a vanity knob — they match the signal shape.

---

## H3 — Gene-grouped CV

| Arm | Random CV | Gene-grouped |
|---|---:|---:|
| Base | 0.382 | 0.297 |
| Base+A | 0.434 | 0.341 |

Family A still helps under gene holdout (+0.044). A large share of human predictability is between genes — grouped CV remains required.

---

## H5 — Transfer (features built on both sides)

| Arm | *E. coli* → human | human → *E. coli* |
|---|---:|---:|
| Base | −0.049 | −0.010 |
| Family A alone | +0.042 | +0.108 |
| Base + A | +0.022 | +0.017 |
| + shape / mech / fold | +0.016 to +0.025 | +0.013 to +0.027 |

Extras do **not** open the wall further. Flanks remain the only representation that flips transfer positive; magnitude stays small.

---

## What this means for the project goal

1. **Improve human model (Goal B):** yes — use human-appropriate capacity (+Family A). ~0.51 ρ on the located set is a real step past the 0.38 champion-HP baseline.
2. **Explain / fix transfer (Goal A):** capacity alone will **not** fix cross-kingdom transfer (it is a within-human fit change). Representation that travels is still **flanks**; guide-derived half still fails.
3. **Next positives** likely need **new data** (H6–H9): cell-type–matched chromatin for A375 / HCT116 / HEK293T / HeLa / HL60 (not K562), expression, or a second human cutting screen — not more QCT/shape/fold variants.

---

## Files

| Artefact | Path |
|---|---|
| Ladder | `results/human_discovery_ladder.csv` |
| Capacity 3-seed confirm | `results/human_discovery_capacity_3seed.csv` |
| Additivity | `results/human_discovery_additivity.csv` |
| Grouped CV | `results/human_discovery_grouped.csv` |
| Transfer | `results/human_discovery_transfer.csv` |
| Log | `/opt/cursor/artifacts/human_discovery_all.log` |
