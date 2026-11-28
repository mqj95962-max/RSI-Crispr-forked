# P1 — Controls: permutation floors & “why didn’t it help?”

**Source files:**  
- `Runjia/sgrna/controls/floors.py`  
- `Runjia/sgrna/controls/diagnose.py`  

**Job in the project:** after ablation numbers exist, ask two harder questions — (1) is Δρ above that family’s **noise floor**? (2) if a family barely moved Spearman, **why** (redundancy / leftover signal / label ceiling)?

---

## Where this sits

```text
run_ablation → folds_<tag>.csv + ablation_<tag>.csv
        │
        ├─► floors.py     paired Δ vs baseline & vs permuted arms
        │
        └─► diagnose.py   redundancy / headroom / ceiling diagnostics
```

P0 taught you to **run** fair exams. P1 controls teach you to **interpret** boring or exciting Δρ without kidding yourself.

---

## 1. `floors.py` — per-family permutation floors, paired fairly

### Why a single “a_flank floor” is wrong

Early on, the project sometimes quoted one permutation floor measured on Family A as if it applied to every family. It doesn’t: floor height depends on **how many columns** a family has and how easily they enter the top 300.

### What this module fixes

1. **Per-family floors** from fold-level logs (`folds_<tag>.csv`), not a hand-waved global number.  
2. **Paired deltas on `(seed, fold)`** — both arms see the same split. Differencing a 3-seed family mean against a 5-seed baseline mean mixes biology with seed noise.

```text
For each experiment name in folds:
  merge with baseline rows on (seed, fold)
  compute d_rho per fold → mean, sd, #positive folds, paired t-test
Also compare real family arm vs "family (permuted)" when present
→ results/permutation_floors.csv
```

**How to read it:** a family “works” only if its paired Δρ is clearly above its own permutation band (and preferably consistently positive across folds).

**Depends on:** you already ran ablation with the same `tag` (and ideally `--permute`).

---

## 2. `diagnose.py` — three explanations for “features didn’t help”

When six families move Spearman by &lt;0.01, the instinct is “pipeline broken.” This module tests three alternatives.

| Diagnostic | Question | Intuition |
|---|---|---|
| **`redundancy()`** | How much of each new column is already determined by the 20-mer? | If a feature is a deterministic rewrite of the spacer, it adds **no new information** — trees may still like the summary, but you’re not measuring new biology. |
| **`headroom()`** | Do unused features still correlate with champion **residuals**? | If nothing correlates with leftovers, this feature set is tapped out. If something does, the model left signal on the table. |
| **`ceiling()`** | How reproducible is the label across screens? | Two screens of the same library only agree so much — that caps how high any sequence model can go. |

**Inputs:** matrices via `load_dataset`, guide sequences, sometimes replicate/screen tables.  
**Outputs:** `results/redundancy.csv`, `headroom.csv`, `ceiling.json`.  
**CLI:** `python -m sgrna.diagnose --what all` (or individual pieces).

**Connection to P0:** uses the same `_impute` / selector / champion helpers as the harness so diagnostics aren’t a different modelling universe.

---

## How these change how you read Family A / human Δρ

| Situation | What to do |
|---|---|
| Ablation shows +0.02 ρ | Check `floors` — is +0.02 inside that family’s permutation noise? |
| Family looks null | Check `redundancy` — is it mostly a 20-mer rewrite? |
| Everything looks null | Check `ceiling` — maybe the label isn’t that predictable |
| Human Tier-1 Δρ | Same spirit: later twin-honest / strand audits are human-side “is this real?” cousins of floors/diagnose |

---

## Checklist

- [ ] I know why floors must be **per family** and **paired by fold**  
- [ ] I can state the three diagnose questions in plain English  
- [ ] I know these modules **consume** ablation outputs; they don’t replace ablation  
