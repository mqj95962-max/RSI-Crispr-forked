# SLICER — what determines whether a CRISPR guide cuts, in *E. coli*

**S**imple **L**ightweight **I**nterpretable **C**RISPR **E**fficiency **R**anker.
RSI09, as of 11 October 2026. **The analysis is frozen** (Part 4).

**In one paragraph.** A 2023 resource published 6,232 quantum-chemical and
positional features for 13,880 *E. coli* guides but not the guide sequences,
making it unusable for new targets. We decoded it, which revealed that its
columns are an elaborate spelling of 20 letters — 427 of them do the same job as
all 6,232 — and that explained why eight imported feature families added almost
nothing. The signal the matrix lacks is outside the guide: **DNA composition in
windows of 50–1,000 nt around the cut site is worth +0.080 ρ**, the largest effect
found here, and a smooth compositional gradient rather than a motif. The part
that *decides the comparison* is long-range: on the ±189/166 nt span the state of
the art already reads, its convolutions beat our windowed composition by 0.025,
and our lead comes from the 250–1,000 nt windows its input never reaches.
**The contribution is access to long-range context, not a better encoding of the
same bases.** The resulting model
reaches **ρ 0.721 against 0.704** for the published state of the art with both
tuned, on identical folds and on the prior model's own split, for **~150× less
CPU time** and about **half the training data**.

**How this document is organised.** Part 1 is the findings, each with the
evidence it rests on and the limit of what it supports. Part 2 states the three
contributions. Part 3 is where the work stops. Part 4 is the freeze and what
remains. Part 5 is what the control phase changed, including the claims it
cost us. Everything that supports a finding without being one — control
experiments, extension questions, clarifications, the full cost panel — is in the
appendices. Protocols and per-fold numbers are in `../results/RESULTS.md`; the
chronological record, including withdrawn claims, is in `FINDINGS_LOG.md`.

---

## Part 1 — Findings

### 1. The published feature set is recoverable from sequence

5,853 of 5,887 anonymous `V####` columns are position-specific k-mer indicators,
none ambiguous; the 316 quantum columns are exact k-mer lookup tables with no
conflicts. Together **6,169 of 6,232 columns (99.0%) regenerate from any 20 nt
protospacer**, verified at **100.000000%** over 1.17 million rebuilt values.
13,879 of 13,880 guides were located in NC_000913.2 with the required PAM in the
right place; 13,877 are unique.

*Rests on:* exact agreement, not a fit. *Limit:* the ~63 hand-named columns are
not pure functions of the protospacer and are not reproduced.

### 2. Those 6,232 columns contain about 20 variables

A 20-mer carries at most 40 bits; the matrix spends 6,232 columns on it in three
overlapping spellings. **74 mononucleotide indicators are a lossless encoding** —
every position carries at least three of its four, so the fourth is implied — and
recover 96.4% of full-matrix ρ. Adding the 63 non-sequence columns gives **427
columns at ρ 0.5249 against 0.5272**: loss **+0.0023, 95% CI [−0.0008, +0.0054]**,
formally **non-inferior against a pre-declared 0.005 ρ margin** (one-sided
p = 0.035). The matrix decomposes as **74 sequence + 63 non-sequence + ~6,095
restatement**.

Three results elsewhere are corollaries: sixteen model classes span only 0.116 ρ;
quadrupling the selected columns changes nothing; nothing correlates with the
model's residuals above 0.031.

**And the reduced set is portable** (`portability.py`), which matters for any
move to another cohort. Of the 63 hand-named columns, 26 are computable from the
20-mer and its PAM, 2 need gene annotation, and 34 are undecoded `V` columns — of
which 19 are reconstructible (R² ≥ 0.95 against mono+di indicators) and **15 are
not**. Dropping those 15 *costs nothing*, and the ladder below says where to stop.
All arms from one protocol, 5 seeds × 5 folds, same rows:

| arm | columns | ρ | vs full matrix |
|---|---:|---:|---:|
| mononucleotide only | 74 | 0.5081 ± 0.0010 | −0.0191 |
| mono + dinucleotide | 364 | 0.5189 ± 0.0009 | −0.0083 |
| reduced | 427 | 0.5249 ± 0.0014 | −0.0023 |
| **portable** | **412** | **0.52713 ± 0.0011** | **−0.00003** |
| published full | 6,232 | 0.52716 ± 0.0022 | — |

**412 is the stopping point.** Dropping the 15 non-portable columns is +0.0022 ρ,
i.e. slightly *better* than the 427, and lands **0.00003 ρ** from all 6,232. Going
further down to the 364 sequence indicators alone *does* cost something — **0.0083
ρ** — so the 48 portable hand-named columns earn their place rather than surviving
by inertia. **412 columns computable for any 20-mer plus the reference genome
match all 6,232**, with no lookup into the published matrix, which is the property
a move to another cohort actually needs.

*Already in force on the curated cohort.* The curated arms carry 6,517 columns =
6,169 reconstructable + 348 flank, so the 63 hand-named columns are **already
absent** there. Any claim about "the 427" on crisprHAL's rows was therefore never
about the columns actually used; the portable 412 is what the claim should name.

*Limit:* "non-inferior by 0.005" is the claim, not "identical". Higher-order
k-mers do carry a little — see Finding 8.

### 3. A feature that restates what the model has cannot help — one direction only

Out-of-fold R² of predicting each new column from position-specific mono- and
dinucleotide indicators, against that family's measured gain:

| family | R² from the 20-mer | Δρ |
|---|---:|---:|
| `b_energy` (CRISPRoff ΔG) | **0.984** | +0.007 |
| `d_mechanics` (duplex stability) | **0.845** | +0.020 |
| `c_folding` | 0.297 | +0.007 |
| `f_methylation` | 0.141 | +0.004 |
| `a_flank` | −0.012 | **+0.080** |
| `d_supercoiling` | −0.013 | +0.045 |
| `e_nucleoid` | −0.016 | +0.016 |
| `g_transcription` | −0.016 | +0.015 |
| `h_offtarget` | −0.022 | +0.000 |
| `j_periodicity` | −0.022 | −0.001 |

Nearest-neighbour thermodynamics is a sum over adjacent pairs, so binding energy
is a 2nd-order quantity the matrix already holds. Importing CRISPRoff was
importing the matrix back into itself.

*The rule runs one way.* **High R² ⇒ cannot help has held 8 times out of 8.**
Low R² is a *filter*, not a prediction: `h_offtarget` and `j_periodicity` both
pass it and deliver nothing, so the "should help" direction is 7 of 9. Quote it
as a screen, never as a forecast.

### 4. The DNA around the cut site predicts cutting — the one large effect

Windowed composition of the flanking DNA (GC, purine, longest run, quantum-table
averages at 50/250/500/1,000 nt each side, plus the nearest 10 bases) is worth
**+0.080 ρ** on the original label and **+0.164** on a read-depth-filtered one —
larger than every other idea tested here combined. Cas9 does not read this DNA.

**The effect is spatially local, shown with a control that preserves genomic
texture.** Re-assigning each guide the flank track read from a position offset by
a circular chromosome shift keeps every column's distribution, smoothness and
long-range autocorrelation and breaks only the correspondence (Appendix A):

| flanks read from | ρ | gain over no flanks |
|---|---:|---:|
| **the right place** | **0.6060** | **+0.0769** |
| 1 kb away | 0.5353 | +0.0062 (8% of the effect) |
| 10 kb away | 0.5160 | −0.0131 |
| 100 kb – 2 Mb away | 0.5194–0.5229 | −0.006 to −0.010 |

At 1 kb the shifted columns are still 0.41 correlated with the real ones and only
8% of the gain survives; by 10 kb the gain is gone. So this is not an artefact of
chromosome-scale structure, and the effect is sharply localised.

### 5. It is a gradient, not a motif

A convolutional network of the same architecture family as the best published
competitor, given raw DNA on the same rows and folds:

| sequence given | ρ |
|---|---:|
| protospacer + PAM | 0.4980 |
| ±100 nt | 0.5203 |
| ±250 nt | **0.5247** |
| ±1,000 nt | 0.5190 |

**Flat from ±100 and then declining.** Given the exact DNA the windows summarise,
the network adds **+0.019** where the windowed means add **+0.080**.

*What this does and does not show.* Not a receptive-field limit — the sequence was
there and went unused; the context branch mean-pools, so a windowed average is
representable. The barrier is **inductive bias and sample efficiency**: the prior
"the right summary of 500 positions is their unweighted mean" is free to assert
and expensive to learn from 33,567 noisy examples. Nothing here shows a
representational limit for CNNs.

**But a *tuned* CNN is not so easily beaten on the DNA it actually holds, and
this is the result that bounds the claim.** crisprHAL 2's released rows are 378
nt for a 23 nt target — **189 nt upstream, 166 downstream** — so its network
already sees that span. Restricting family A to the columns that fit inside it
(the 50 nt windows and the near-cut sequence and quantum columns; the
250/500/1,000 nt windows reach past their input and are dropped) gives a
like-for-like contest in which neither model holds sequence the other lacks:

| arm | flank columns | ρ | vs crisprHAL 2 |
|---|---:|---:|---:|
| no flank | 0 | 0.5440 | — |
| near-cut only (±10 nt) | 260 | 0.6178 | −0.079 |
| **matched to their span (±189 / ±166)** | **282** | **0.6724 ± 0.0094** | **−0.025** |
| full family A | 348 | **0.7072** | **+0.010** |

**Inside their own receptive span, their convolutions beat our windowed
composition by 0.025.** Our lead is not a better encoding of the same bases: it
comes from the 250–1,000 nt windows their input never reaches, worth
0.7072 − 0.6724 = **+0.035** on top of a matched-span representation.

*What this costs and what it buys.* It costs the reading that windowed means are
simply a smarter encoding than convolution — on equal DNA they are not. It buys
a cleaner statement of the contribution: **the signal is long-range, and the
advantage is access to it**, not a representational trick. It also makes the
in-house CNN of the table above the weaker comparison it always was — a tuned
CNN does considerably better than ours on the same span, so "CNNs cannot learn
this" was never the right conclusion, and only the sample-efficiency reading
survives.

### 6. The effect belongs to the DNA, and transfers

| test | result |
|---|---|
| different enzyme (WT-SpCas9 → TevSpCas9) | ρ 0.700 against 0.825 for a locally-trained model |
| different organism (*E. coli* → *C. rodentium*) | 0.701 [0.683, 0.704]; reverse 0.627 [0.617, 0.636] |
| different kingdom (bacteria ↔ human) | **negative both ways**, CIs excluding zero |
| read-depth / mappability artefact? | survives a high-uniqueness stratum, +0.078 → +0.051 |
| gene ranking in disguise? | within-gene ρ 0.571 against 0.606 global; flanks worth **+0.061 inside genes** |

*Mechanism, as a hypothesis.* Target GC correlates **−0.201** with the score;
the effect survives a change of enzyme and of organism; and the model run
backwards prefers GC-poor targets (35% against a 51% mean). That is consistent
with a duplex-opening step limited by local GC. **It is not an intervention** —
the assay measures depletion, not cutting — so it is stated as a hypothesis, and
distinguishing a strand-invasion-limited from a hybridisation-limited step would
need kinetic data.

**The GC account survives conditioning, which is the test that matters**
(`gcstrata.py`). Flank GC's *marginal* association with the label is weak —
+0.044 for the ±500 nt mean, and no flank GC column at any window exceeds +0.051
(Spearman) or +0.079 (Pearson). But target GC is a **suppressor**: it correlates
−0.201 with the label and +0.176 with flank GC, so it masks the flank term.
Partialling it out *raises* flank GC's association to **+0.082** — double the
marginal value — and the sign is positive in all five target-GC strata.

The full ablation inside each stratum, where target composition is near-constant
by construction:

| target GC | n | baseline ρ | + family A | Δ |
|---|---:|---:|---:|---:|
| 0.20–0.40 | 2,776 | 0.3353 | 0.4630 | **+0.128** |
| 0.40–0.50 | 2,776 | 0.4045 | 0.4797 | +0.075 |
| 0.50–0.55 | 2,775 | 0.4627 | 0.5221 | +0.059 |
| 0.55–0.60 | 2,776 | 0.4760 | 0.5220 | +0.046 |
| 0.60–0.85 | 2,776 | 0.4443 | 0.5023 | +0.058 |

**Family A is not target GC in disguise** — it is worth between +0.046 and +0.128
inside every stratum. *Limit:* the gain is largest where the target is GC-poor,
but it is **not monotone** (the top stratum rises again), and it covaries with
headroom — the GC-poor stratum has the lowest baseline and so the most room to
gain. So the ordering is an observation, not a dose-response curve, and it should
not be read as quantitative support for the duplex-opening account.

*Withdrawn here:* an earlier version of this paragraph quoted **flank GC +0.159**.
That figure does not reproduce against the published label by either correlation
measure; −0.201 for target GC reproduces exactly. The conditional analysis above
replaces it.

### 7. The long-range asymmetry depends on orientation — and it is transcription-start-site orientation, not nearest-gene

The PAM side is worth more than the other side (+0.072 against +0.027;
count-matched +0.0790 against +0.0782, so it is the side and not the column
budget). Short range has a mechanistic account from PAM-first engagement. Long
range does not, and two candidates have been tested:

- **Replication** — ruled out. No sign flip between replichores (0.0493, 0.0483).
- **Transcription** — *supported, with the right annotation*. Expression level
  does not scale the asymmetry on the coding library, but orientation does on
  Guo's intergenic sub-library, where both strands exist by design.

**The controls are now done** (Jacky; `Jacky/orientation-controls/`). Δ is
opposite-minus-same asymmetry, with a 2,000× block bootstrap over 47 genomic
blocks, primary set n = 8,954:

| orientation defined against | opposite | same | **Δ [95% CI]** | P(Δ≤0) |
|---|---:|---:|---|---:|
| **RegulonDB TSS** | 0.061 | 0.011 | **0.051 [0.020, 0.082]** | **0.000** |
| RegulonDB operon | 0.053 | 0.031 | 0.023 [−0.008, 0.055] | 0.085 |
| nearest gene | 0.040 | 0.014 | 0.026 [−0.006, 0.058] | 0.054 |
| nearest gene, matched on distance + flank GC | 0.029 | 0.022 | **0.007 [−0.024, 0.038]** | **0.337** |
| TSS, matched on distance + flank GC | 0.048 | 0.023 | 0.025 [−0.003, 0.053] | 0.041 |

**Three things changed, two of them against us.**

1. **Lead with TSS, not nearest gene.** Against a curated TSS the interaction is
   unambiguous — Δ 0.051 with a CI clear of zero.
2. **The nearest-gene version — which is what this report previously quoted — is
   largely a cohort confound.** Matched on distance-to-gene and flank GC it
   collapses to 0.007 (P = 0.34). Orientation relative to the nearest gene was
   partly standing in for *where* those guides sit.
3. **Even TSS attenuates by half under the same matching** to Δ 0.025, and its
   95% CI then just includes zero while the one-sided P is 0.041. The honest
   phrasing is **"survives matching directionally, borderline at 95%"** — not
   "significant".

*Also corrected:* the figures previously quoted here, "0.047 against the nearest
gene, 0.005 with it", were **unweighted point estimates**. The block bootstrap
over 47 genomic blocks puts the same comparison at 0.040 against 0.014, Δ 0.026.
The earlier numbers were not wrong, but they were the optimistic form of a
quantity that needed an interval, and the interval includes zero.

*Still limited:* promoter and RBS guides show the **same sign** (Δ 0.024 and
0.038) but their splits are underpowered, so no kind-specific claim is made;
operon strand is weaker than TSS and stays supporting rather than lead. **Part 4
item 3 is closed.**

### 8. Higher-order k-mers help, but only once feature selection is removed

Measured through the top-300 selector, adding trimers *hurt*. Without selection it
helps, paired over 3 seeds × 5 folds:

| contrast | mean Δρ | folds | paired *t* |
|---|---:|---:|---:|
| **+ trimers** | **+0.0035** | 12/15 | **p = 0.025** |
| **+ tetramers on top** | **−0.0028** | 4/15 | **p = 0.013** |
| net | +0.0007 | 8/15 | p = 0.62 |

Both are significant and they cancel. The usable order stops at three: 4,343
tetramer columns for 256 possible 4-mers per position are too sparse to carry
anything. **A conclusion drawn downstream of feature selection is a statement
about the selector until proven otherwise** — this ladder produced three confident
wrong answers before that was understood.

### 9. The model is out of material, and the reduction does not change that

Correlating every column against the champion's out-of-fold residuals:

| model | strongest \|ρ\| among columns it has | among columns held back |
|---|---:|---:|
| all 6,232 | 0.028 | **0.147** — family A |
| the 427 | 0.022 | **0.146** — family A |
| 427 + family A | 0.028 | 0.070, none above 0.10 |

Rows one and two are the point: **dropping 5,805 columns did not change what the
model is missing.** The test is trustworthy because it has a positive control — it
flagged family A at 0.147 *before* family A existed, and family A was then worth
+0.080.

### 10. Importance rankings are unstable per column and stable per block — and gain is the culprit

Across seven model families (two boosters, two forests, two linear, CatBoost):

| method | agreement between models, per column | per block |
|---|---:|---:|
| the library default (gain / impurity / coef) | **0.050** | 0.531 |
| permutation | 0.258 | 0.581 |
| **SHAP** | **0.496** | **0.800** |

The instability is a property of the matrix, not of boosting — it survives bagged
forests and penalised linear models. But **the "models prefer different kinds of
column" finding was an artefact of split gain**: XGBoost's share on binary
indicators falls from 57% to 31% under SHAP and lands on LightGBM's 31% exactly.
The largest between-model gap on any kind of column goes from 31 points to 0.3.

*Consequence:* report SHAP, at block level, and never gain.

### 11. The standard faithfulness probe is uninterpretable on a redundant matrix

"Drop the top features and refit" returns ≈0 on the full matrix for every model,
which this project reported for weeks as evidence that no model had found the
real features. It is not: at a **matched share of attributed importance** (~35%),
the full matrix loses 0.002 and the 775-column reduced set loses **0.015** — six
times the damage for the same share of the explanation removed, while both
concentrate importance almost identically (44 and 37 columns for half of it).

### 12. The label's ceiling is ≈0.94, not 0.90

Two screens of the same library agree at ρ 0.810, which naively gives 0.90 — but
the disagreement is **predictable at ρ 0.546**, so it is enzyme biology, not
noise. Using the source paper's own agreement statistics instead, and accounting
for the published score being a **two-replicate geometric mean**:

| route | r | reliability | ceiling |
|---|---:|---:|---:|
| **tiling library, a *different* library** | 0.878 | 0.878 | **0.937 [0.929, 0.945]** |
| replicate agreement + Spearman–Brown | >0.883 | 0.938 | 0.969 |

**Lead with 0.937.** The replicate route must assume the activity score inherits
the single-arm read counts' reliability, and it cannot: the label is the `|Z|` of
a Cas9/dCas9 **ratio**, and a difference is never more reliable than its
components — at 50% shared signal between arms the implied ceiling is already
0.940. The tiling route needs none of that machinery.

So SLICER at ρ 0.707–0.721 leaves **about 0.22 of ρ unaccounted for**.

---

## Part 2 — Contributions

**1. A published representation decoded, and shown to be redundant.** 99% of it
regenerates from sequence; 427 of 6,232 columns are non-inferior to all of them;
and the redundancy yields a one-line screen for whether a candidate feature can
help, correct 8 of 8 in the direction it is reliable (Findings 1–3).

**2. Genomic flanking context identified and validated as the main new signal.**
+0.080 ρ, the largest effect here; a spatially local compositional gradient, shown
with a texture-preserving null; not a motif, not mappability, not gene ranking;
transfers across enzyme and organism and not across kingdoms (Findings 4–7).

**3. A simple representation that exploits it competitively and cheaply.**
ρ 0.721 against 0.704 with both models tuned, 0.6997 against 0.6940 on the prior
model's own split, for ~150× less CPU time and about half the training data —
leading on nine metrics tuned and eight of nine untuned (Appendix B).

Findings 8–12 support these three. They are not co-equal headlines, with one
exception worth separating for an ML audience: **Findings 10 and 11 are
methodological results about interpretability that generalise beyond this
dataset**, and would be better served by a short companion note than by being
compressed into a biology paper.

---

## Part 3 — Where this stops

- **Everything is bacterial.** Cross-kingdom transfer is ≈0, measured in both
  directions. And our human baseline is **undertuned** — a grid search by a
  teammate reached ρ 0.472 against the 0.404 quoted here — which matters because
  the cross-kingdom claim leans on the human side being weak.
- **One organism and two relatives.** No genome-wide Cas9-cutting screen exists
  outside *Enterobacteriaceae*; what exists elsewhere is CRISPRi, a different
  measured quantity. Closing this needs wet-lab work.
- **The label is survival, not cutting**, and is a folded Z-score of a
  two-replicate Cas9/dCas9 ratio. Every "efficiency" number is that composite.
- **The long-range mechanism is unidentified.** Orientation is a live candidate
  with one ruled-out alternative; the most mechanistically motivated feature built
  to explain it (GC skew and helical periodicity) is a null.
- **Adaptive overfitting.** Many choices were made against the same outer folds.
  See the freeze below.

---

## Part 4 — The freeze, and what remains

**The analysis is frozen as of 11 October 2026.** No further model, feature or
hyperparameter choice is made against the curated five-fold split.

**The designated untouched final evaluation is the eSpCas9 screen (59,489
guides)** — used only for transfer and the ceiling argument, never for selecting a
model, feature family, column set or hyperparameter. Both models, at frozen
configurations, evaluated on it once, reported whichever way it falls.

Two existing external checks, neither a substitute for that: the baseline anchor
reproduces Noshay et al.'s published figure through our harness, and SLICER
scores 0.6997 on crisprHAL 2's own shipped split, a partition untouched during
development. **The curated five-fold figures carry an unknown
adaptive-overfitting component**, and the paper should say so.

Remaining before submission:

| | item | cost |
|---|---|---|
| 1 | eSpCas9 final evaluation, once, frozen configs — **on hold**: a pivot to crisprHAL's cohort reclassifies eSpCas9 as cross-enzyme validation rather than an untouched holdout, so spending the one-shot evaluation now would spend it on the wrong question | ~1 h |
| 2 | crisprHAL 2's search run to **its own** plateau, not extrapolated | 2–4 GPU-h, free Colab tier |
| 3 | ~~orientation controls~~ | **done** — Jacky, Finding 7 |
| 4 | human baseline re-tuned at the teammate's settings — **blocked**: the grid-search settings behind ρ 0.472 are not recorded in the repo or the log, and the script that produced `human_transfer.csv` is not in `src/` | ~1 h once supplied |
| 5 | ~~conditional test of the GC hypothesis within matched GC strata~~ | **done** — Finding 6 |
| 6 | sample-complexity curve repeated across folds and seeds | ~2 h |

**A guide-design tool is not a deliverable.** The findings are the contribution,
the field already has several predictors, and everything needed to build one
later exists (`featurise.matrix()` turns any 20-mer into the published
representation). It should not compete with finishing the paper.

## Part 5 — What the control phase changed

Work resumed on **2 October** after a pause following family A's discovery
(12–13 September) and the first head-to-head (15 September). From **10–13
October** the work was almost entirely adversarial: nulls, matched comparisons,
conditional tests and robustness checks aimed at the claims already made rather
than at new ones. It is worth stating separately what that bought and what it
cost, because the cost was not small.

### What survived, and got stronger

| claim | what the control added |
|---|---|
| family A is real and local | a **texture-preserving** null, not just row shuffling: aligned +0.0769, 1 kb retains 8%, ≥10 kb is null. Converts a control into a measurement of the effect's autocorrelation length |
| the GC account | conditioning *raises* flank GC's association (+0.044 marginal → **+0.082** partial), positive in all five target-GC strata, and family A is worth +0.046 to +0.128 inside every stratum |
| the reduced representation | **412 columns** computable from any 20-mer land 0.00003 ρ from all 6,232 — portability, not just sufficiency |
| orientation | against a curated RegulonDB TSS, Δ **0.051 [0.020, 0.082]** with the interval clear of zero (Jacky) |
| data efficiency | survives all five folds; the ρ ≥ 0.68 ratio goes **1.4× → 2.5×** |

### What it cost — five claims withdrawn in four days

| withdrawn | replaced by |
|---|---|
| "flank GC +0.159" | does not reproduce by either correlation measure; the conditional analysis (+0.082 partial) replaces it |
| "not recoverable by a convolutional network given the same DNA" | **matched to crisprHAL's own 189/166 nt span, their convolutions beat our windowed composition by 0.025.** Our lead is the 250–1,000 nt windows they cannot see |
| "0.047 against the nearest gene, 0.005 with it" | unweighted point estimates; the block bootstrap gives Δ 0.026 with an interval including zero, and it **collapses to 0.007 under distance+GC matching** |
| "the asymptotes are close … not evidence of a higher ceiling" | paired across five folds the gap is **+0.0133 ρ, p = 0.0058, 5/5 folds** — our own caveat was an artefact of measuring one fold |
| "427 columns are the portable set" | 412; and the curated cohort never carried the 63 hand-named columns at all |

### What that means

**The three contributions survive; several of the sentences supporting them did
not.** The decoding and the flanking-context effect came through every control
intact or stronger. What changed is the *framing* of the third: we do not
out-encode a tuned deep model on DNA both sides hold, we have access to DNA it
never sees. That is a narrower claim and a much harder one to attack.

Four of the five withdrawals were caught by **our own tests**, and the fifth —
the nearest-gene orientation confound — by a teammate's. None were caught by
re-reading the text. The pattern from Appendix E holds: the data needed was
already on disk, and the bottleneck was that nobody had asked the number to
defend itself.

---
---

# Appendices

Everything below supports a finding without being one: the controls, the
questions asked along the way and their answers, the cost detail, and the
provenance. Nothing here should appear in the main text of a paper.

## Appendix A — Controls and nulls

**Permutation floors.** Every family with a gain was re-run with its rows
shuffled. Family A's shuffled control scores **0.5264** against a 0.5272
baseline — i.e. zero — and `j_periodicity`'s control scores *higher* than the
real thing, which is the signature of noise.

**The texture-preserving null for family A** (`shiftnull.py`). Row shuffling
destroys genomic autocorrelation as well as the pairing, so it tests a weaker
null than claimed. Instead each guide is re-assigned the flank track read from a
position offset by a **circular chromosome shift**: same track, wrong place, so
every column's marginal, smoothness and long-range autocorrelation are preserved
exactly. Verified on `dn500.gc` — mean moves 0.5103 → 0.497–0.508 while its
correlation with the aligned track falls 1.00 / 0.41 / 0.05 / −0.03 at 0 / 1 kb /
100 kb / 2 Mb.

**One shift would not have been enough**, and that is why it is swept: at 1 kb
the shifted columns are still 0.41 correlated with the real ones. Sweeping turns
the control into a measurement — Δρ against shift distance is the autocorrelation
length of the effect, independent of the window sizes family A happens to use.
Results in Finding 4. Grouped CV (100 kb blocks) throughout, because a positional
feature under random KFold can score by locus recognition and the shifted arms
would inherit that too.

**Negative controls from the source experiment.** Available for exactly one
family: the dCas9 arm of the same screen, which is why the "supercoiling" result
could be overturned by its own control rather than by an argument.

**Grouped cross-validation.** The screen puts ~20 guides in every gene, so plain
KFold lets a model score by recognising a locus rather than reading a guide —
84.5% of label variance is *within* gene, so the remaining ~15% is learnable by
memorising addresses. Anything positional is reported under `arc5` or 100 kb
blocks.

## Appendix B — Questions asked along the way, and the answers

### Is peak memory a measure of computational cost?

No — it is a **constraint**, not a cost: it answers "will this run on my laptop",
which is binary. It barely separates the two models (3.76 GB against 4.55 GB) and
is set by loading the matrix, not by the model. Better cost measures, each biased
differently:

| | SLICER | crisprHAL 2 | ratio |
|---|---:|---:|---:|
| training FLOPs | 1.79 × 10¹¹ | 4.21 × 10¹⁴ | 2,360× |
| bytes moved | 7.1 × 10¹¹ | 8.5 × 10¹² | 12× |
| **CPU-seconds per fold** | **65.8** | ~10,000 | **152×** |
| wall-clock, 8 threads | 13.8 s | 21 min | 92× |
| arithmetic intensity | 0.25 FLOP/byte | 49 | — |

**Lead with CPU-seconds.** FLOPs flatters us: our histogram construction is
**memory-bandwidth-bound** at 0.25 FLOP/byte and their convolutions are
**compute-bound** at 49, against the ~10–30 a CPU needs to be compute-bound — so
counting arithmetic captures nearly all of their cost and a quarter of ours, and
2,360× is an upper bound while 12× is the matching lower bound. Noted against our
own interest: their CPU-per-wall ratio is 7.9 against our 4.8, so they
parallelise better and our wall-clock advantage understates the CPU-seconds one.

*Protocol:* one configuration per process, repeated. `ru_maxrss` is a high-water
mark that never falls, which is how 4.03 GB was once attributed to both selectors
at the same time; run-to-run spread for one arm is ~0.3 GB.

*Energy* would be the physically honest total and is not measured —
`powermetrics` needs elevated privileges here.

### How light can the pipeline get?

**7.5 CPU-seconds and 2.45 × 10¹⁰ FLOPs** — 8.8× and 7.3× below the published
configuration, 17,200× below crisprHAL — for −0.0125 ρ, by dropping the
feature-selection pass (86% of the FLOPs, and its only output is an ordering) and
training on the reduced columns. A plain **ridge** regression on those columns
costs **3.4 CPU-seconds** and reaches ρ 0.627, still above **our in-house**
convolutional control at any input width (not above crisprHAL 2 — see
Finding 5). Peak memory falls to 0.65 GB only if the reduced
matrix is what gets *stored*; subsetting after loading saves 14%.

### Is there an architecture-independent measure of cost?

**No, and FLOPs is not one** — it is hardware-independent but computed *from* the
architecture, so it cannot adjudicate between architectures without assuming what
work costs. The only genuinely architecture-free measure is **sample
complexity**, because it says nothing about how the computation is done:

| guides needed to reach | SLICER | crisprHAL 2 |
|---|---:|---:|
| ρ ≥ 0.62 | **4,000** | 8,000 |
| ρ ≥ 0.66 | **8,000** | 13,880 |
| ρ ≥ 0.68 | **13,880** | 20,000 |

About half the data at every absolute threshold.

**The table above was fold 1 only, and fold 1 is the hardest fold for both
models.** A claim of the form "needs half the labelled guides" has to survive the
choice of test set, and this one had never been asked to. It now has:
`sample_complexity.py` takes a fold and both curves run over all five.

| guides | SLICER | sd | crisprHAL 2 | sd |
|---:|---:|---:|---:|---:|
| 4,000 | **0.6501** | 0.0095 | 0.5235 | 0.0138 |
| 8,000 | **0.6817** | 0.0081 | 0.6323 | 0.0146 |
| 13,880 | **0.6985** | 0.0081 | 0.6733 | 0.0092 |
| 20,000 | **0.7046** | 0.0076 | 0.6879 | 0.0054 |
| 26,853 | **0.7082** | 0.0076 | 0.6950 | 0.0072 |

**The claim survives, and at one threshold it strengthens:**

| guides needed to reach | SLICER | crisprHAL 2 | was (fold 1) |
|---|---:|---:|---|
| ρ ≥ 0.62 | **4,000** | 8,000 | unchanged |
| ρ ≥ 0.66 | **8,000** | 13,880 | unchanged |
| ρ ≥ 0.68 | **8,000** | 20,000 | was 13,880 vs 20,000 |
| ρ ≥ 0.70 | **20,000** | never reached | new |

At ρ ≥ 0.68 the ratio goes from 1.4× to **2.5×**, because fold 1 understated
SLICER by ~0.014 ρ while barely moving crisprHAL. SLICER reaches ρ 0.70 on
20,000 guides; crisprHAL does not reach it on all 26,853.

**One of our own caveats does not survive.** The previous text said the
asymptotes were "close (0.694, 0.688) … within 0.007, inside the fold spread" and
that this was "not evidence of a higher ceiling". Paired across the five folds at
full size:

| | value |
|---|---:|
| mean paired difference | **+0.0133 ρ** |
| sd across folds | 0.0055 |
| paired *t* | t = 5.36, **p = 0.0058** |
| folds favouring SLICER | **5 / 5** |

So at the data we have, the two are *not* indistinguishable. **The honest
statement is narrower than "higher ceiling"**: neither curve has converged — the
last 6,853 guides still buy +0.004 and +0.007 — so this is a gap at full
available data, not a proven difference in asymptote. It is also the same gap the
head-to-head reports, not an independent finding.

*Limit:* SLICER averages two seeds per fold, crisprHAL one, so crisprHAL's
per-fold values are noisier; the pairing is by fold, which is valid, but a second
crisprHAL seed would tighten it.

*Protocol note:* the module's printed summary used to report only "share of each
model's own best", which reads as a data-efficiency claim and is not one — two
curves can both reach 95% of themselves at the same n while being far apart in
ρ. It now leads with absolute thresholds and labels the own-best figures
diagnostic.

### Would renting a TPU settle the tuning asymmetry? Yes, and it should not be a budget item

The margin's weakest point is that crisprHAL got 10 configurations and SLICER
627. Matching 627 draw-for-draw is ~460 CPU-hours, which is where a £20–50
rental estimate came from. **That estimate was wrong**: the trace shows 40 draws
captured 100% of SLICER's gain, so an equal-footing search means running *their*
search to *its own* patience criterion — about **55 fits, 2–4 GPU-hours, one free
Colab session**.

**A TPU would be the wrong instrument.** TPUs earn their keep on large dense
matmul under XLA; this model's recurrent branch is a bidirectional GRU — a
sequential loop, the shape that maps worst onto them. A mid-range GPU is both
cheaper and faster for it.

*When:* once, at data freeze. Re-tuning is required only when rows, label or
folds change (both models) or the feature set changes (SLICER only);
documentation and analyses outside the curated arm require none.

### Could a cleverer data structure avoid the 3.8 GB table?

Yes, and the decoding makes it almost absurd. The matrix is 10.1% non-zero with
5,957 strictly binary columns, so as CSR the data is 0.132 GB against 0.81 GB
dense — but **naive conversion makes peak memory worse** (both copies live at
once). Storing the reduced matrix gives a measured 3.33 → **0.65 GB**. And since
6,169 columns are a deterministic function of the 20-mer, the entire 33,567-guide
dataset is **40 bits per guide ≈ 168 KB** of actual information; everything else
is a cache. We pay 3.8 GB to avoid recomputing it.

### Is five-fold cross-validation enough?

For the paired comparisons it is used for, yes. A single fold's ρ has SE ≈ 0.012,
but every comparison is **paired on the same folds**, which gives a paired SE of
0.0011 — eleven times smaller. Where five bites: Wilcoxon cannot go below
p = 0.0625 at n = 5, so both the paired *t* and the sign test are always quoted,
and the sd estimate has four degrees of freedom. **The fix is more seeds, not
more folds** — more folds shrinks each training set. Ablations use 5 seeds × 5
folds; the head-to-head uses one seed because each crisprHAL fit costs ~21 min.

Power, for reference: ~5 folds resolve an effect of 0.013, ~20 folds resolve
0.005, and 0.002 would need ~100 — out of reach at crisprHAL's cost.

### Why does boosting beat random forest, and ridge beat both forests?

| | ρ |
|---|---:|
| LightGBM / XGBoost | 0.609 / 0.608 |
| **Ridge** | **0.577** |
| extra trees / random forest | 0.556 / 0.550 |
| k-NN | 0.495 |

**The signal is overwhelmingly additive** — a straight line gets within 0.03, so
the interactions boosting captures are worth ~0.03 ρ. Boosting reduces bias
sequentially, which is the right move for a sum of many small independent
effects; bagging reduces variance, which is not the binding constraint. Random
forest's `max_features='sqrt'` offers only ~81 of 6,517 columns per node, most of
them restatement. And **k-NN failing confirms the shape**: guides with similar
features do not have similar scores, which is what many small additive terms
look like.

Checked on a basis with the redundancy removed, because the gap was measured on
selected columns: on 427 columns ridge reaches **95.6%** of boosting's ρ, and
ridge on the raw 6,232 collapses to 0.423 from collinearity. **The redundancy was
concealing the additivity from the linear model, not manufacturing it.**

### What other long-range features could be built without new data?

From the genome alone: **GC skew** (strand-asymmetric, unlike GC content),
**A-tract phasing** and **bendability periodicity** at the helical repeat
(periodicity, not composition), **k-mer entropy**, **Chi sites**
(`GCTGGTGG`, RecBCD hotspots), homopolymer run-length, REP element density. From
RegulonDB, already on disk: **distance and orientation to the nearest annotated
TSS, terminator and operon boundary** — the properly-annotated version of the
nearest-gene proxy, and the highest-value item given Finding 7. From a teammate:
distance to the nearest essential gene.

The first three were built as family J and are a **null** (−0.001 alone, +0.0004
on top of family A, with its permutation control scoring higher) despite passing
the screen at median R² −0.022. That is the most mechanistically motivated
candidate left, and it makes the long-range asymmetry harder to explain, not
easier.

### The nine-metric comparison

| | ρ | τ | Pearson | R² | calib. | top-decile | NDCG@10 | pick %ile | within-gene |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **SLICER, tuned** | **0.7213** | **0.5303** | **0.7385** | **0.5450** | **1.023** | **0.2991** | **0.8738** | **76.36** | **77.99** |
| SLICER, untuned | 0.7083 | 0.5182 | 0.7257 | 0.5225 | 1.097 | 0.2904 | 0.8708 | 75.86 | 77.50 |
| crisprHAL 2, tuned | 0.7040 | 0.5139 | 0.7273 | 0.5248 | 1.066 | 0.2681 | 0.8650 | 75.37 | 75.60 |
| crisprHAL 2, untuned | 0.6968 | 0.5073 | 0.7212 | 0.5167 | **1.049** | 0.2696 | 0.8654 | 76.21 |

**Nine of nine tuned, eight of nine untuned**: before tuning, crisprHAL 2 is the
better calibrated of the two (slope 1.049 against 1.097), which is what a model
trained directly on MSE should achieve and must be reported. Largest gap in our
favour is **top-decile precision, +11%**, where the decision lives; most
deflationary is NDCG@10, which puts all four within 0.009.

### How to read the headline number

ρ measures whether the ordering is right, which is the right headline because
nobody needs a guide's exact efficiency. But **ratios of Δρ are not ratios of
information** — on the ρ² scale the same Δρ is worth twice as much higher up — so
this report quotes paired differences and raw ρ, not percentages. On the decision
scale: given ten candidate guides, a model at ρ 0.71 picks one landing at the
**81st percentile**, against the 50th for blind choice and the 88th at the
ceiling. The whole range from useless to perfect spans the 50th to the 91st,
because ten random candidates may not contain a great one.

**Report ρ and R² together.** A LightGBM with a robust loss scored R² 0.192 with
ρ 0.568 — the same model looking broken on one metric and respectable on the
other.

## Appendix C0 — Reproducibility: versions, seeds and protocol

Recorded so a rerun is a rerun, not an approximation.

| | |
|---|---|
| Python | 3.12.15 |
| numpy / pandas / scipy | 2.5.3 / 3.0.6 / 1.18.1 |
| scikit-learn | 1.9.1 |
| LightGBM / XGBoost / CatBoost | 4.7.0 / 3.4.1 / 1.2.10 |
| SHAP | 0.52.0 |
| PyTorch (the CNN controls) | 2.14.1 |

**Seeds.** `config.SEEDS = (41, 42, 43, 44, 45)`; `config.N_SPLITS = 5`. Ablations
use all five seeds × five folds (25 fits per arm). The head-to-head against
crisprHAL 2 uses seed 41 only, because each of their fits costs ~21 min. The
shift-distance null and the GC-strata test use three seeds × five folds. Every
seed is passed explicitly to the model, the selector and the fold splitter, so
no arm depends on global RNG state.

**Selector.** `config.SELECTOR = "xgboost"` — the throwaway model whose only job
is to rank columns; its predictions are never used. Feature selection is fitted
**inside the training split of each fold**, never on the full data.

**Resumability.** Every fold is written to `results/folds_<tag>.csv` as it
finishes and a fold already recorded there is skipped, so a long run can be
rebuilt over several sittings without recomputing work — and so that a crash
loses one fold rather than an experiment.

## Appendix C — Feature sets and data sources

### Ours — ten families, four distinct ideas

| set | what it measures | source | Δρ |
|---|---|---|---:|
| `a_flank` | composition and quantum averages outside the 20-mer, 50–1,000 nt | reference genome | **+0.080** |
| `b_energy` | guide–DNA binding energy by component | CRISPRoff, unchanged | +0.007 |
| `c_folding` | whether the guide RNA folds on itself | ViennaRNA | +0.007 |
| `d_mechanics` | duplex opening, position by position | SantaLucia & Hicks (2004) | +0.020 |
| `d_supercoiling` | positive-supercoiling density | GapR-seq, GSE152880 | +0.045 → artefact |
| `e_nucleoid` | 3D contact structure, NAP dependence | Lioy et al. 2018 Hi-C | +0.016 |
| `f_methylation` | Dam/Dcm motifs at PAM and seed | reference genome | +0.004 |
| `g_transcription` | TSS distance, strand, expression | RegulonDB + PRECISE-1K | +0.015 |
| `h_offtarget` | off-target burden, target copies | reference genome | +0.000 |
| `i_shape` | flank bendability / deformability | published dinucleotide scales | +0.001 |
| `j_periodicity` | GC skew, helical-repeat periodicity | reference genome | −0.001 |

Groups 1 (`b`,`c`,`d_mechanics`,`f`) are redundant by Finding 3; group 2 (`a`) is
the one that worked; group 3 (`d_supercoiling`, `e`, `g`) collapse into one
positional variable; group 4 (`h`) needs the rest of the genome.

### Teammates' — on the published 13,880-row matrix, quoted in R²

Not directly comparable with the Δρ column above; recorded so the paper does not
under-credit them.

| set | who | result |
|---|---|---|
| **gene essentiality** | Jacky | **+0.0037 R²** over 0.2927, **selected in 5/5 folds** — the only non-QCT idea on that matrix with a consistent gain, and it passes Finding 3's screen |
| **orientation controls** | Jacky | closes Part 4 item 3 and **rewrites Finding 7**: curated RegulonDB TSS replaces nearest gene as the orientation variable (Δ 0.051 [0.020, 0.082]), and the nearest-gene version we had been quoting is shown to be largely a distance/GC cohort confound (Δ 0.007, P = 0.34 after matching). Block bootstrap over 47 genomic blocks, promoter/RBS separated, operon compared |
| seed non-additive QCT | Joshua | ~+0.005 R²; absolute-difference forms carry more SHAP than signed (1.09 against 0.92) |
| log-ratio QCT forms | Joshua | ~+0.005 R², best seed 0.3015 |
| regional QCT summaries | Joshua | +0.0013 R², against a permuted control at 0.2857 |
| PAM-weighted, profile-shape, coupling, HOMO–LUMO asymmetry | Joshua | −0.0010 to +0.0006 — null |

The non-additive families are **independent evidence for Finding 8**: they gain
from exactly the higher-order structure the k-mer ladder found worth +0.0035 ρ
once the selector was removed.

## Appendix D — Sources (APA 7th edition)

Browne, T. S., Edgell, D. R., & Gloor, G. B. (2026). Better data for better
predictions: Data curation improves deep learning for sgRNA/Cas9 prediction.
*PeerJ*, *14*, e20706. https://doi.org/10.7717/peerj.20706
— the state of the art; code and curated label re-run here as the baseline.

Guo, J., Wang, T., Guan, C., Liu, B., Luo, C., Xie, Z., Zhang, C., & Xing, X.
(2018). Improved sgRNA design in bacteria via genome-wide activity profiling.
*Nucleic Acids Research*, *46*(14), 7052–7069. https://doi.org/10.1093/nar/gky572
— the screen behind the label; Figure 2b and 2c agreement statistics for the
ceiling; the intergenic sub-library.

Guo, M. S., Kawamura, R., Littlehale, M. L., Marko, J. F., & Laub, M. T. (2021).
High-resolution, genome-wide mapping of positive supercoiling in chromosomes.
*eLife*, *10*, e67236. https://doi.org/10.7554/eLife.67236
— GapR-seq; positive-supercoiling density (GEO accession GSE152880).

Ham, D. T., Browne, T. S., Banglorewala, P. N., Wilson, T. L., Michael, R. K.,
Gloor, G. B., & Edgell, D. R. (2023). A generalizable Cas9/sgRNA prediction
model using machine transfer learning with small high-quality datasets. *Nature
Communications*, *14*(1), 5514. https://doi.org/10.1038/s41467-023-41143-7
— the *C. rodentium* screen used for cross-organism transfer.

Lioy, V. S., Cournac, A., Marbouty, M., Duigou, S., Mozziconacci, J., Espéli, O.,
Boccard, F., & Koszul, R. (2018). Multiscale structuring of the *E. coli*
chromosome by nucleoid-associated and condensin proteins. *Cell*, *172*(4),
771–783.e18. https://doi.org/10.1016/j.cell.2017.12.027
— Hi-C contact structure and nucleoid-associated protein dependence.

Noshay, J. M., Walker, T., Alexander, W. G., Klingeman, D. M., Romero, J.,
Walker, A. M., Prates, E., Eckert, C., Irle, S., Kainer, D., & Jacobson, D. A.
(2023). Quantum biological insights into CRISPR-Cas9 sgRNA efficiency from
explainable-AI driven feature engineering. *Nucleic Acids Research*, *51*(19),
10147–10161. https://doi.org/10.1093/nar/gkad736
— the feature matrix decoded here; their iRF re-runs in our harness at Pearson
0.4881 against their reported 0.5019, on a third of their rows.

SantaLucia, J., & Hicks, D. (2004). The thermodynamics of DNA structural motifs.
*Annual Review of Biophysics and Biomolecular Structure*, *33*(1), 415–440.
https://doi.org/10.1146/annurev.biophys.32.110601.141800
— nearest-neighbour thermodynamic parameters.

Sastry, A. V., Gao, Y., Szubin, R., Hefner, Y., Xu, S., Kim, D., Choudhary, K. S.,
Yang, L., King, Z. A., & Palsson, B. O. (2019). The *Escherichia coli*
transcriptome mostly consists of independently regulated modules. *Nature
Communications*, *10*(1), 5536. https://doi.org/10.1038/s41467-019-13483-w
— the iModulon decomposition behind the PRECISE expression compendium.

**Two database citations still need their canonical form**, because Crossref
does not resolve them from the version strings we use and they should not be
guessed: **RegulonDB v14.5** (release citation) and **PRECISE-1K** (the 1,035-run
compendium, successor to Sastry et al. 2019). Everything above was verified
against Crossref metadata rather than transcribed from memory.

## Appendix E — Withdrawn claims

Nineteen claims have been withdrawn and eight bugs found. They are not listed
here, so that this document reads as a statement rather than a diary; they are in
`local/MISCONCEPTIONS.md`, outside the repo, with the cause of each.

The pattern is worth one line, because it is the most transferable thing here:
**the largest single category is an outsider's question**, and in every one of
those cases the data needed to catch the error was already on disk. The
bottleneck was never measurement — it was that nobody had questioned a number
repeated often enough to feel settled.
