# Request — the settings behind the human baseline (ρ 0.472)

**What I need:** the grid-search configuration that produced the human-screen
baseline of **ρ 0.472**, and the script that wrote `results/human_transfer.csv`.

**Why it is blocking.** It is item 4 of the pre-submission list and the only one
that cannot be closed from this side. Part 3 says our human baseline is
*undertuned*, on the strength of your 0.472 against the 0.404 we measure — and
that admission is what weakens the cross-kingdom claim. The claim is that
transfer is ≈0 in both directions (−0.048 *E. coli* → human, −0.017 the other
way). If the human model we transfer *into* is simply a weak model, the negative
transfer is partly our baseline's fault rather than a fact about kingdoms. So
the sentence needs either your settings, so the human side is as strong as it
can be, or a frank caveat.

Right now 0.472 has no recorded provenance anywhere on my side: it is not in
`results/human_transfer.csv` (that file has 0.404, 0.396, 0.393 across three
seeds), the grid and winning configuration are not in the repo or the findings
log, and the script that produced the CSV is not in `src/`.

**Specifically, any of these would unblock it** — in descending order of
usefulness:

1. the script itself, in whatever state it is in;
2. the grid that was searched (parameter names and value lists) plus the winning
   configuration;
3. just the winning configuration, if the grid is gone — enough to re-run it
   once and confirm the number reproduces.

**What happens either way.** If it arrives, I re-run it at those settings on the
same rows and the baseline keeps its number with a provenance line. If it does
not, the report states that the human baseline is quoted from an unreproducible
run and the cross-kingdom claim rests on the *sign* of the transfer rather than
on the margin — which is still a result, just a weaker one.

**Current state of the number**, for reference (`results/human_transfer.csv`):

| arm | ρ | sd | n_train | n_test |
|---|---:|---:|---:|---:|
| human within-screen CV | 0.4043 | 0.0125 | 13,936 | 3,484 |
| *E. coli* within-screen CV | 0.5305 | 0.0121 | 11,104 | 2,776 |

The 0.472 figure is not in this file, which is part of the problem — it is
quoted in the report from a run whose output was not kept.
