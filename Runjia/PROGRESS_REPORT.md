# SLICER — what determines whether a CRISPR guide cuts, in *E. coli*

**S**imple **L**ightweight **I**nterpretable **C**RISPR **E**fficiency **R**anker.
RSI09, as of 11 October 2026. **The analysis is frozen** (Part 4).

**In one paragraph.** A 2023 resource published 6,232 quantum-chemical and
positional features for 13,880 *E. coli* guides but not the guide sequences,
making it unusable for new targets. We decoded it, which revealed that its
columns are an elaborate spelling of 20 letters — on that matrix, under a
300-column selection budget, 427 of them do the same job as all 6,232, and 412 of
those are computable for any guide (the reduction does *not* survive on the
curated cohort with selection removed, Finding 2). That settles by
arithmetic why two imported biophysical families could not have helped: they are
deterministic functions of the guide. Six others failed for unrelated reasons,
which is a list of null results rather than a pattern (Appendix B2). The signal the matrix lacks is outside the guide: **DNA composition in
windows of 50–1,000 nt around the cut site is worth +0.080 ρ**, the largest effect
found here, and a smooth compositional gradient rather than a motif. The part
that *decides the comparison* is long-range: on the ±189/166 nt span the state of
the art already reads, its convolutions beat our windowed composition, and our
lead comes from the 250–1,000 nt windows its input never reaches. **Handed that
same reach, the state of the art gets worse, not better** (0.6799 → 0.6299),
so the contribution is an encoding of long-range composition that a tuned
convolutional network does not recover — not merely access to it. The resulting
model
reaches **ρ 0.721 against 0.704** for the published state of the art with both
tuned, on identical folds and on the prior model's own split, for **~150× less
CPU time** and about **half the training data**. **That lead is a small-data
lead.** Run once on crisprHAL 2's own eSpCas9 split, where 47,591 guides are
available for training instead of 26,853, the two models tie — 0.7842 against
0.7821 — and their model is ahead on three of six metrics. The data-efficiency
claim is the one that survives a larger screen; the ranking claim is not.

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

*The first of those was circular until 15 October, and survives being made
non-circular.* "Model class barely matters" was measured on a representation with
no large effect in it — the published matrix without family A — so it could have
been a statement about a flat representation rather than about model classes.
Re-run on the curated base **with** family A (`curated_models.py`, one seed ×
five folds, same registry and folds):

| | ρ | | | ρ |
|---|---:|---|---|---:|
| XGBoost | **0.7084** | | ridge | 0.6473 |
| LightGBM | 0.7082 | | PLS | 0.6450 |
| extra trees | 0.6537 | | elastic net | 0.6369 |
| random forest | 0.6482 | | k-NN | 0.6007 |

**Spread 0.1076 ρ across eight classes, against 0.116 across sixteen without
family A.** Adding the one feature family that matters does not widen the gap
between model classes at all, while the family itself is worth +0.164. The
boosting-over-everything margin (+0.055 over ridge) is also unchanged in
character. So the corollary is not an artefact of measuring it on a
representation with nothing in it.

**And the reduced set is portable** (`portability.py`), which matters for any
move to another cohort. Of the 63 hand-named columns, 26 are computable from the
20-mer and its PAM, 2 need gene annotation, and 34 are undecoded `V` columns — of
which 19 are reconstructible (R² ≥ 0.95 against mono+di indicators) and **15 are
not**. Dropping those 15 *costs nothing*, and the ladder below says where to stop.
All arms from one protocol, 5 seeds × 5 folds, same rows:

| arm | columns | ρ | vs full matrix |
|---|---:|---:|---:|
| mononucleotide only | 74 | 0.5081 ± 0.0010 | −0.0191 |
| + dinucleotide | 364 | 0.5189 ± 0.0009 | −0.0083 |
| + non-sequence features | 427 | 0.5249 ± 0.0014 | −0.0023 |
| − 15 undecoded (**portable**) | **412** | **0.52713 ± 0.0011** | **−0.00003** |
| published full | 6,232 | 0.52716 ± 0.0022 | — |

*Protocol caveat, added 13 October.* Every arm here selects **300 columns from
its candidate pool** — `cross_validate` resolves `n_features=None` to
`config.N_FEATURES`, so "all columns" was never tested. The arms are therefore
not on identical footing: the 74-column arm has fewer candidates than 300 and
uses all of them, while the 6,232-column arm selects 300 from 6,232. The
comparison is still internally consistent, and 412 ≈ the full matrix stands, but
the ladder measures *candidate pools under a fixed selection budget*, not
representations in full.

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

**Re-run on the curated cohort with the caveat removed, the reduction does not
hold.** `curated_ladder.py`, 3 seeds × 5 folds, **no selection in any arm** —
`n_features` set to each arm's own column count, so this is representations
compared in full rather than candidate pools under a budget:

| arm | columns | ρ | vs full |
|---|---:|---:|---:|
| mononucleotide only | 74 | 0.5198 ± 0.0021 | −0.0251 |
| + dinucleotide | 364 | 0.5331 ± 0.0010 | −0.0118 |
| **regenerated base** | **6,169** | **0.5449 ± 0.0013** | — |
| 364 + family A | 712 | 0.6937 ± 0.0010 | −0.0142 |
| base + family A | 6,517 | **0.7079 ± 0.0004** | — |

**Two results, and they point in opposite directions.**

*`n_features = 300` costs nothing, in either direction.* Selecting 300 from 6,169
gives 0.5445 against 0.5449 using all of them, and 300 from 6,517 gives 0.7084
against 0.7079. **±0.0005.** The selection budget was never the binding
constraint, which retires both the protocol caveat above and the `n_features`
row in Part 4.

*But the reduced representation is **not** non-inferior here.* 364 columns lose
**0.0118** and 712 lose **0.0142** — two to three times the pre-declared 0.005 ρ
margin that 427 passed on the published matrix. The reduction claim therefore
does not transfer: **"412 ≈ all 6,232" is a statement about the published matrix
under a 300-column budget**, and on the curated cohort with every column
available the higher-order k-mer columns are worth 0.012–0.014. That is Finding
7 seen from the other side — higher-order k-mers help once selection is removed —
and it means the paper must state the reduction with both qualifiers or not at
all. What does transfer is the *lossless* part: 74 columns recover 95.4% of full
ρ here against 96.4% there.

**A consequence that is often stated as a theorem, and is false.** If the matrix
encodes the 20-mer losslessly, it is tempting to conclude that *any* deterministic
function of the 20-mer adds nothing to a model trained on it. **That holds for an
unconstrained learner and not for ours.** Three families on the curated cohort
are built from the guide and nothing else, and all three pay: `b_energy`
**+0.019**, `c_folding` **+0.014**, and the guide-only part of `d_mechanics`
(below). None of this is a feature-selection artefact — on the full
`d_mechanics` arm, using every column rather than selecting 300 gives the same
gain, +0.0993 against +0.0988 (`results/selector_control.csv`).

*Correction, 13 October — the clean cases are the other two.* **Eight of
`d_mechanics`'s thirty columns are not functions of the 20-mer at all**:
`eng.mech.flank.{up,dn}{25,100}` are duplex thermodynamics of the flanking DNA,
which the base does not contain. So its +0.099 mixes this claim with family A's
mechanism. Found by reconstructing each column from the base's 364 mono- and
dinucleotide indicators out of fold:

| `d_mechanics` columns | out-of-fold R² from the base |
|---|---:|
| 9 ΔG/ΔH/ΔS sums over the protospacer and its windows | **1.0000** |
| 4 melting temperatures | 0.997–0.9995 |
| 7 stacking and slide summaries (means, sd, extrema, argmax) | 0.20–0.98 |
| **8 flank thermodynamics (±25, ±100 nt)** | **−0.006 to +0.042** |

The nine exact ones are the arithmetic the argument needs, and the probe
recovers them to four decimals. The eight flank columns are new DNA.

**Split into its two halves, `d_mechanics` says the opposite of what it was
quoted for** (`no_information.py`, same base, same 5 × 5 protocol):

| arm | columns | ρ | Δρ |
|---|---:|---:|---:|
| base | 6,169 | 0.5445 | — |
| + the 22 **protospacer** columns | 6,191 | 0.5555 | **+0.0110** |
| + the 8 **flank** columns | 6,177 | 0.6418 | **+0.0973** |
| + all 30 | 6,199 | 0.6437 | +0.0991 |

**Eight columns of flanking-DNA thermodynamics carry 98% of the gain, and the
22 columns that cannot carry information are worth +0.011.** The arm that was
the report's cleanest case for representation-over-information was mostly family
A's effect wearing another family's name.

So the effect is real and it is **small**. Three independent guide-only
measurements now agree on its size: `d_mechanics`'s protospacer half **+0.011**,
`c_folding` (ViennaRNA on the spacer and its scaffold) **+0.014**, and
`b_energy` (CRISPRoff on the 23-mer) **+0.019**. A deterministic function of the
guide buys a depth-limited tree one to two hundredths of a correlation — not a
tenth.

**So a feature can add no information and still add performance — about
+0.015 of it.** A depth-limited gradient-boosted tree over one-hot indicators
cannot cheaply compute "sum of position-wise energies", and handed that sum
precomputed it gains; the gain is consistent across three families and an order
of magnitude below what family A's access to new DNA is worth (+0.164). **The
distance between what a representation *contains* and what a model can *use* is
real and it is not where this project's effect size lives.** What does the work
is access to DNA outside the 20-mer — Finding 3, and the reason the head-to-head
against crisprHAL turns on input width rather than on encoding.

What survives of the original claim is narrower: a deterministic function of the
20-mer adds no **information**, so it cannot raise the ceiling, and it is a poor
bet when the model can already compute it. The measurements, and why they do
**not** support a general screen, are in Appendix B2.

*Limit:* "non-inferior by 0.005" is the claim, not "identical". Higher-order
k-mers do carry a little — see Finding 7.

### 3. The DNA around the cut site predicts cutting — the one large effect

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

### 4. It is a gradient, not a motif

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

**And then we gave their architecture the same reach, which is the test that
decides it.** Their input width is a parameter, so crisprHAL 2 was retrained at
four widths on the same rows, label and fold. cuDNN cannot allocate the GRU
workspace at 2,023 nt and their published batch of 1,024, so every width was
re-run at batch 256; the 378 nt arm at both batches brackets that cost at
**−0.011**, a fifth of the effect below.

| crisprHAL 2 input | ρ (batch 256, fold 1) | vs their 378 nt design point |
|---:|---:|---:|
| 23 nt (guide + PAM) | 0.5494 | −0.131 |
| **378 nt (as published)** | **0.6799** | — |
| 1,023 nt | 0.6602 | **−0.020** |
| 2,023 nt | 0.6299 | **−0.050** |

**Their model peaks at the width it was designed for and declines monotonically
beyond it.** Handed the DNA family A reads, it gets worse, not better — roughly
7× its across-fold sd. The head-to-head on the same fold:

| DNA both models see | SLICER | crisprHAL 2 | lead |
|---|---:|---:|---|
| guide + PAM only | 0.5473 | 0.5494 | **tied** (0.002) |
| their 378 nt span | 0.6568 | 0.6799 | crisprHAL **+0.023** |
| ±1,000 nt | **0.6944** | 0.6299 | **SLICER +0.065** |

So the three input widths tell three different stories, and only the last one is
ours: on the guide alone the two architectures are **indistinguishable**; on
their design width **theirs is better**; and at the reach family A uses, **ours
is better by more than either of those gaps** — because width helps us and hurts
them.

*This partially restores a claim withdrawn above, and the restored version is
narrower.* "Not recoverable by a convolutional network given the same DNA" was
withdrawn because the only CNN tested at width was our own weak one. What is now
supported is: **crisprHAL 2, at its published hyperparameters, is degraded by
input wider than it was designed for.** Not "CNNs cannot learn this" — its 48
epochs and every other setting were tuned at 378 nt, and **a re-tune at each
width is the control we have not run.** One fold, one seed. State that limit
beside the result.

*Is "as published, with more of the genome" a fair test?* It is a fair test of
one thing and not of another, and the distinction decides what Finding 4 can
claim. Equalising the input DNA removes the information asymmetry — in fact it
reverses it, since they receive **raw** sequence over the window while family A
receives a 348-column lossy summary of it, so on information they are ahead.
What it does not equalise is the *opportunity to use* that DNA. Their 48 epochs,
dropout, filter count and GRU width were all chosen at 378 nt; stretching the
input to 2,023 nt multiplies the flattened layer by ~5 while leaving its
regularisation and training budget untouched. So the measurement supports

> **the published configuration, used as published, is degraded by input wider
> than it was tuned for**

and not

> ~~a convolutional-recurrent architecture cannot exploit long-range context~~.

The second claim needs a re-tune at each width. What makes the first worth
reporting anyway is that **378 nt is their own optimum, not an arbitrary
inherited setting** — see below — so the experiment extends a curve past the
point their own search stopped improving, rather than handicapping them at a
setting nobody chose.

*Their own paper supplies part of that control, and it points the same way.*
Browne et al. (2026) searched input length **per dataset** and stopped at 378 nt
for *E. coli* SpCas9 and 406 nt for eSpCas9, reporting that the gains level off:
+0.00034 ρ per nucleotide upstream and +0.00074 downstream, carrying the model
from 0.554 on the sgRNA alone to 0.697 at 378 nt. So 378 nt is not an arbitrary
inherited setting — it is where **their** search stopped improving, and the
decline we measure at 1,023 and 2,023 nt is the continuation of a curve they had
already flattened. What remains unrun is re-tuning the other hyperparameters at
each width, which is a weaker objection than it was before this was read.

### 5. The effect belongs to the DNA, and transfers

| test | result |
|---|---|
| different enzyme (WT-SpCas9 → TevSpCas9) | ρ 0.700 against 0.825 for a locally-trained model |
| different organism (*E. coli* → *C. rodentium*) | 0.701 [0.683, 0.704]; reverse 0.627 [0.617, 0.636] |
| different kingdom (bacteria ↔ human) | **negative both ways**, CIs excluding zero |
| read-depth / mappability artefact? | survives a high-uniqueness stratum, +0.078 → +0.051 |
| gene ranking in disguise? | within-gene ρ 0.571 against 0.606 global; flanks worth **+0.061 inside genes** |
| **a property of cutting, or of Cas9 binding?** | **cutting.** In a dCas9 CRISPRi screen family A adds **−0.009**, against **+0.157** on the cutting screen under the same gene-grouped protocol |

*Why these five and not other tests.* Each removes one way the effect could be
an artefact of this dataset rather than a property of the DNA. A new **enzyme**
changes the protein but keeps the genome, so a surviving effect is not about
SpCas9's idiosyncrasies. A new **organism** changes the genome too, so a
surviving effect is not about *E. coli*'s composition; the **human** arm going
negative is the control on that control, since a model transferring everywhere
would be evidence of a methodological artefact rather than of biology. The
**uniqueness stratum** removes the mappability explanation by restricting to
guides whose reads cannot be misassigned. The **within-gene** comparison removes
the gene-ranking explanation by asking the question entirely inside genes, where
"which gene" is constant. Nothing here is an intervention, so all five together
still only rule things out.

**The one test that could have falsified the mechanism, and it did not.**
Finding 3's account is a duplex-opening step limited by local DNA composition at
the cut site. Every external check until now has been another Cas9 *cutting*
screen, which cannot distinguish that from a general property of Cas9 binding or
of local chromatin accessibility — both would predict a flank effect too. Cui et
al.'s (2018) dCas9 **CRISPRi** screen can: dCas9 binds and does not cut, and the
measured quantity is fitness under transcriptional silencing rather than survival
after cleavage.

It had never been used for anything here except a single ceiling-range number, so
it was the last genuinely untouched dataset available. 76,325 uniquely-targeting
guides located in NC_000913.2, 70,298 of them inside 4,265 named genes, same
pipeline, same champion, 3 seeds × 5 folds, **whole genes held out** —
mandatory here, because 30% of this label's variance is between genes (within-gene
share 0.704) and essential genes sit 2.05 fitness units below non-essential ones,
so a model that recognised the locus would be richly rewarded:

| arm | CRISPRi (dCas9) | cutting (curated Cas9) |
|---|---:|---:|
| 20-mer base, 6,169 columns | 0.4577 ± 0.0013 | 0.5584 ± 0.0011 |
| base + family A | 0.4484 ± 0.0006 | 0.7151 ± 0.0005 |
| **family A's increment** | **−0.0093** | **+0.1567** |
| family A alone, 348 columns | 0.1333 ± 0.0013 | 0.3408 ± 0.0005 |

**Family A adds nothing to a silencing screen and +0.157 to a cutting screen,
measured the same way.** The flank-only arm is what makes that a clean null
rather than a selection artefact: adding 348 columns to a 6,169-column pool under
a 300-column budget could dilute selection, but family A on its own cannot be
diluted, and on its own it reaches 0.133 against 0.341 on the cutting screen.

*So the effect is specific to cleavage*, which is what Finding 3 claims and what
a binding- or accessibility-based explanation would have contradicted. Two
honest qualifications. The 0.133 is **not zero** — flanking composition does
carry some information about CRISPRi fitness, plausibly because a 2 kb window
around a gene says something about the gene — but it is **redundant with the
20-mer** there, which is the opposite of its behaviour on cutting data. And this
is a different enzyme, library, assay and laboratory at once, so a null has many
possible authors; what makes it interpretable is that the *base* predicts 0.458
on the same rows, so the pipeline plainly works on this screen and the null
belongs to family A rather than to the run.

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

### 6. The long-range asymmetry depends on orientation — and it is transcription-start-site orientation, not nearest-gene

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

### 7. Higher-order k-mers help, but only once feature selection is removed

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

### 8. The model is out of material, and the reduction does not change that

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

### 9. Importance rankings are unstable per column and stable per block — and gain is the culprit

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

### 10. The standard faithfulness probe is uninterpretable on a redundant matrix

"Drop the top features and refit" returns ≈0 on the full matrix for every model,
which this project reported for weeks as evidence that no model had found the
real features. It is not — and the fix is to match what is removed rather than
how many columns are removed. **Why the naive version fails:** on a matrix where
6,095 columns restate 20 variables, dropping the top *k* columns removes almost
no information, because near-duplicates remain to carry it. The probe then
reports ≈0 for every model and every representation, which is a property of the
redundancy, not of the attributions. Equalising the *share of attributed
importance* removed makes the comparison about what each representation actually
loses. At a matched share (~35%),
the full matrix loses 0.002 and the 775-column reduced set loses **0.015** — six
times the damage for the same share of the explanation removed, while both
concentrate importance almost identically (44 and 37 columns for half of it).

### 11. The label's ceiling is ≈0.94, not 0.90

**Measured for the curated label, 15 October: 0.946 [0.944, 0.948]**, and the
route is a replicate-agreement one rather than the inherited figure
(`curated_ceiling.py`). crisprHAL 2's paper reports no replicate statistics, but
their **per-replicate counts are published** — two Cas9 replicates and two
dead-nuclease controls. Pairing Cas9 replicate 1 with control 1 and replicate 2
with control 2 gives two independent estimates of the same quantity, agreeing at
**ρ 0.8097**; Spearman–Brown makes the released two-replicate score's reliability
**0.8948**, and its square root is the highest ρ any predictor can reach against
it. The other pairing gives 0.9453, so the figure does not depend on how the
replicates are matched.

Three things make it trustworthy, and they are why this is worth more than the
inherited number:

| check | result |
|---|---|
| does their **cohort** reproduce? | their R script filters on an average control count of **73**; applying it gives **33,871** guides against the 33,567 they release |
| does their **label** reproduce? | a plain CPM log-ratio of the two conditions correlates **\|ρ\| = 0.957** with their released score, so these are the replicates behind that label |
| is it conservative? | **yes** — ALDEx2's posterior shrinks noisy guides toward the prior, which can only raise reliability above a plain log-ratio's, so 0.946 is a **lower bound** |

So the curated label is *cleaner* than the published one (0.946 against 0.937),
which is what their paper claims curation does, now measured from their own
counts rather than taken on trust. The arithmetic below is retained because it
is the published label's route and the two cohorts' figures are quoted side by
side elsewhere.

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

So SLICER at ρ 0.707–0.721 leaves **about 0.22 of ρ unaccounted for** — 0.225
against the curated label's measured 0.946, and the gap is not a rounding
artefact of an inherited ceiling.

---

## Part 2 — Contributions

**1. A published representation decoded, and shown to be redundant.** 99% of it
regenerates from sequence; 427 of 6,232 columns are non-inferior to all of them;
and the lossless encoding settles, as a matter of arithmetic rather than
measurement, that no deterministic function of the 20-mer can add information to
a model trained on it — which is why several imported biophysical families could
not have helped (Findings 1–2; Appendix B2).

**2. Genomic flanking context identified and validated as the main new signal.**
+0.080 ρ, the largest effect here; a spatially local compositional gradient, shown
with a texture-preserving null; not a motif, not mappability, not gene ranking;
transfers across enzyme and organism and not across kingdoms (Findings 3–6).

**3. A representation of long-range context that a tuned convolutional network
does not extract *at this sample size*.** ρ 0.721 against 0.704 with both models
tuned, 0.6997 against 0.6940 on the prior model's own split, for ~150× less CPU
time and about half the training data — leading on nine metrics tuned and eight
of nine untuned (Appendix B).

**The sample-size qualifier is load-bearing, and the final evaluation is why.**
On crisprHAL's own eSpCas9 split, with 47,591 training guides instead of 26,853,
the two models tie: **0.7842 against 0.7821**, inside the standard error, with
their model ahead on R², top-decile precision and pick percentile (Part 4). Our
advantage is a small-data advantage, which is the claim the sample-complexity
curves support and the only one that survives a dataset 1.8× larger.

The comparison holds up when the DNA is equalised, which is the form that
matters. Given the *same* input, the two architectures are indistinguishable on
the guide alone (0.5473 against 0.5494) and crisprHAL 2 is **better** on its own
378 nt span (0.6568 against 0.6799); given family A's ±1,000 nt reach, crisprHAL
2 **degrades** (0.6799 → 0.6299) while SLICER improves, so SLICER leads by
**0.065** at matched input. So the contribution is not a faster model — it is an
encoding of long-range composition that a tuned CNN does not recover at this
sample size, at its published hyperparameters (Finding 4).

Findings 7–11 support these three. They are not co-equal headlines, with one
exception worth separating for an ML audience: **Findings 9 and 10 are
methodological results about interpretability that generalise beyond this
dataset**, and would be better served by a short companion note than by being
compressed into a biology paper.

---

## Part 3 — Where this stops

- **Everything is bacterial.** Cross-kingdom transfer is ≈0, measured in both
  directions. And our human baseline is **undertuned** — a grid search by a
  teammate reached ρ 0.472 against the 0.404 quoted here — which matters because
  the cross-kingdom claim leans on the human side being weak. **Closing this is
  delegated** (Part 4 item 4): until the settings arrive, the claim rests on the
  *sign* of the transfer, which is negative in both directions with intervals
  excluding zero, and not on the size of the margin.
- **One organism and two relatives.** No genome-wide Cas9-cutting screen exists
  outside *Enterobacteriaceae*; what exists elsewhere is CRISPRi, a different
  measured quantity. Closing this needs wet-lab work.
- **The label is survival, not cutting**, and we train on **crisprHAL 2's curated
  score**, not the published one. Verified: our target is **bit-identical** to
  their released `y` on all 33,567 guides, so the head-to-head compares two models
  on one quantity. But the two cohorts' labels are **different quantities** —
  Noshay's `cut_score` runs 0 to 48.05 with no negative values, crisprHAL's runs
  −9.05 to +6.21 with 47.5% negative. They agree in rank at ρ 0.945 on the 8,617
  overlapping guides and give target GC the same sign (−0.147 against −0.201), so
  nothing downstream reverses — but **every number in this report belongs to one
  label or the other and they are not interchangeable.**
- **The long-range mechanism is unidentified.** Orientation is a live candidate
  with one ruled-out alternative; the most mechanistically motivated feature built
  to explain it (GC skew and helical periodicity) is a null.
- **Adaptive overfitting.** Many choices were made against the same outer folds.
  See the freeze below.

---

## Part 4 — The freeze, and what remains

**The analysis is frozen as of 11 October 2026.** No further model, feature or
hyperparameter choice is made against the curated five-fold split.

**The final evaluation has been run, and the dataset it used was not as clean as
this section claimed.** eSpCas9 was designated "the untouched final evaluation",
to be used once. It was already in use: four feature arms across three seeds and
two CV schemes (`results/transfer.csv`), with a flank gain of +0.104 under `arc5`
quoted in `RESULTS.md`. Nothing was ever *selected* on it — every configuration
was chosen on the published or curated cohort and then confirmed on eSpCas9 — so
the right word for it is **confirmatory**, not untouched, and "evaluated once"
was never available.

What was still untouched is the **comparison**: SLICER against crisprHAL 2 on
crisprHAL's own shipped eSpCas9 partition, using their own published eSpCas9
weights. No split, model, feature set or hyperparameter in it was chosen with
reference to eSpCas9. Run once, on their 11,897-guide test file
(`final_eval.py`):

| | ρ | τ | Pearson | R² | top-decile | pick %ile |
|---|---:|---:|---:|---:|---:|---:|
| **SLICER** — champion XGBoost, 6,517 columns, selection fitted inside their training rows | **0.7842** | 0.5942 | 0.7782 | 0.5979 | 0.488 | 94.8 |
| **crisprHAL 2** — their shipped `ESPCAS9.keras`, evaluated as distributed | 0.7821 | 0.5920 | **0.7801** | **0.6009** | **0.494** | **95.5** |

**Their arm reproduces their published figure.** Browne et al. report ρ 0.782
and Pearson 0.780 for crisprHAL-eSp on this test set; loading their shipped
weights here gives **0.7821 and 0.7801**. The harness is reading their model
correctly, which is what makes the comparison worth quoting.

**A tie.** SLICER leads by **+0.0021 ρ** and loses on R², top-decile precision
and expected pick percentile. On a single test set of 11,898 guides the standard
error of ρ alone is ≈0.009, so the honest statement is that **the two models are
indistinguishable on this screen**, and the direction of the difference depends
on which metric is asked for.

**This is the most informative negative result in the report, because it was
predicted.** Our lead on the curated WT cohort is +0.0133 ρ, paired across five
folds, at ~26,853 training guides. crisprHAL's eSpCas9 split gives **47,591**
training guides — 1.8× more — and the gap closes to nothing. That is exactly
what the sample-complexity curves say should happen (Appendix B): our advantage
is largest where labels are scarce and the curves converge as they stop being
scarce. **So the data-efficiency finding survives and the ranking claim does
not.** "SLICER beats crisprHAL 2" is a claim about the small-data regime, and at
47.6k labelled guides it is false. The paper should say so in those words.

Two caveats worth keeping with those numbers. SLICER sees **more DNA** here, not
less — their eSpCas9 input is 406 nt while family A reaches ±1,000 nt — so the
tie is not an equal-information comparison and it favours them, not us. And
their arm is their *published* model while ours is trained here, which is the
right asymmetry for a final evaluation (no chance for us to have tuned it) but
means their number carries whatever tuning their paper did.

**On both of their own splits, the margin is small and in our favour**, which is
the cleanest summary of the head-to-head available and the one the paper should
lead with:

| their split | their published ρ | SLICER | margin |
|---|---:|---:|---:|
| *E. coli* SpCas9, 26,830 train | 0.695 | **0.6997** | +0.005 |
| *E. coli* eSpCas9, 47,591 train | 0.782 | **0.7842** | +0.002 |

Two independent partitions, chosen by them, neither used for any choice of ours:
**+0.005 and +0.002**. That is a defensible claim of parity with the state of the
art at a fraction of the compute — and it is not a claim of beating it.

**And parity here is a measured equivalence, not a failure to find a
difference.** The two arms predict the same 11,898 guides, so the difference is
bootstrapped **paired on guides** (4,000 resamples) against a margin declared
before the interval was seen — **±0.01 ρ**, twice the 0.005 used for the
column-reduction claim because 0.005 is below either model's fold-to-fold noise
on this screen:

| | value |
|---|---:|
| Δρ, SLICER − crisprHAL 2 | **+0.0021** |
| 95% CI, paired bootstrap | **[−0.0031, +0.0072]** |
| two-sided p | 0.44 |
| inside ±0.01 | **yes** |

The whole interval falls inside the margin, which is the form of claim the data
supports: not "we could not tell them apart" but "they are the same within a
hundredth of a correlation".

### On a held-out fold of the curated cohort: SLICER, by a margin that resolves

The five-fold head-to-head was reported two ways and neither put an interval on
the difference: the fold-level mean has n = 5 and cannot resolve anything below
~0.005, and the pooled nine-metric panel has no uncertainty at all. Every guide
is predicted exactly once by a model that never saw it, so the five validation
folds give **33,567 out-of-fold predictions per model over the same rows**, and
the difference can be bootstrapped **paired on guides** (`heldout_compare.py`):

| pairing | SLICER | crisprHAL 2 | difference | 95% CI | p |
|---|---:|---:|---:|---|---:|
| "both at defaults" † | 0.7083 | 0.6968 | **+0.0115** | [+0.0074, +0.0157] | <0.001 |
| both tuned | 0.7213 | 0.7040 | **+0.0172** | [+0.0136, +0.0209] | <0.001 |
| **ours untuned against theirs tuned** | 0.7083 | 0.7040 | **+0.0043** | [+0.0005, +0.0080] | 0.024 |

**All three intervals clear zero, so on this cohort the difference is real** —
unlike the eSpCas9 split, where the same analysis gives parity. Per fold at seed
41, SLICER at defaults beats crisprHAL at defaults in **5 of 5** folds (0.6944 /
0.7079 / 0.7121 / 0.7112 / 0.7136 against 0.6855 / 0.6988 / 0.6978 / 0.7022 /
0.7012).

† **Our "default" is not a default.** `tune.DEFAULT` is
`n_estimators=400, learning_rate=0.05, num_leaves=16, max_depth=4,
subsample=0.8, colsample_bytree=0.8` — a configuration selected by the
**627-draw search on the published cohort**, not LightGBM's defaults
(`n_estimators=100, learning_rate=0.1, num_leaves=31, max_depth=-1`, no
subsampling). crisprHAL's arm, by contrast, really is its published
configuration. So this row is **also asymmetric in our favour**, and the
asymmetry had not been noticed until the question was asked directly on
15 October. **No row in this table is symmetric in search effort**, which is the
argument for the matched run in Part 4 item 2.

Three things that must be quoted with those numbers:

*The alignment had to be reconstructed, and was checked.* crisprHAL's
predictions were saved one file per fold with no guide key, so the concatenation
is in fold order rather than cohort order. The pairing reconstructs
`KFold(5, shuffle=True, random_state=41)` and asserts that the label vectors
match guide for guide; without that check a plausible-looking but meaningless
interval would have come out of a mis-rotated join.

*The tuned margin is an upper bound.* SLICER's search is 12 draws inside each of
five folds; crisprHAL's is 10 draws on a single inner split of fold 1's training
rows, because each of its fits costs ~17 CPU-minutes. Neither search ever
touches an outer validation fold, so neither number is leaked — but theirs is
the weaker search. The **cross** row is the honest floor on that objection: our
*untuned* model against their *tuned* one is +0.0043, an interval that only just
clears zero.

*And the answer to the search asymmetry is not in this table.* It is the final
evaluation below, against their own **published** weights — their tuning, their
search — where the margin is +0.002 and +0.005. **Read together: we are ahead by
~0.017 on our folds against a model we tuned for them, and level against the
model they tuned themselves.** The most likely reason the two conditions differ
is training-set size, 26,853 here against 47,591 there, which is what the
sample-complexity curves predict.

### Every comparison condition we can construct, and the three different answers

Asked under one condition the head-to-head gives parity; asked under another it
does not. The conditions are listed here because choosing one of them silently
is the main way this comparison could be made to say whatever we want. **Four
conditions, three answers**, and the ordering of the first two is the thing to
explain rather than to pick between.

| condition | what it holds fixed | result |
|---|---|---|
| **same task, our five folds, both tuned here** | rows, label, folds, and the tuning protocol *we* ran for both | **SLICER** — +0.0172, 95% CI [+0.0136, +0.0209], paired on 33,567 guides; +0.0043 [+0.0005, +0.0080] with ours untuned against theirs tuned |
| **same task, their split, each model at its own best input and tuning** | rows, label, split, and each side's own configuration | **parity** — Δρ +0.0021, 95% CI [−0.0031, +0.0072], inside a pre-declared ±0.01; and on their SpCas9 split +0.005 |
| **same task, equal input DNA** | rows, label, split, *and the DNA each model reads* | **depends on the width** — tied on the guide alone (0.5473 / 0.5494), crisprHAL +0.023 inside its own 378 nt span, SLICER +0.065 at ±1,000 nt |
| **different assay, neither model trained on it** | rows, label, and that neither has seen the data | **crisprHAL, reliably** — zero-shot on Cui's CRISPRi screen, \|ρ\| 0.0867 against our 0.0609, difference **−0.0258 [−0.0289, −0.0227]** |

**On their own splits the metric split is noise, not a profile difference.** It
would be easy to read "we win the rank metrics, they win the top-of-list metrics"
as a real difference in character — ours better at global ordering, theirs better
at picking a guide. Bootstrapped paired on the same 11,898 guides, **all six
differences have intervals containing zero**:

| metric | Δ (SLICER − crisprHAL) | 95% CI |
|---|---:|---|
| Spearman ρ | +0.0021 | [−0.0028, +0.0071] |
| Kendall τ | +0.0023 | [−0.0024, +0.0073] |
| Pearson r | −0.0019 | [−0.0066, +0.0030] |
| R² | −0.0030 | [−0.0103, +0.0041] |
| top-decile precision | −0.0059 | [−0.0244, +0.0202] |
| expected pick percentile | −0.70 | [−17.91, +3.98] |

So "they win some, we win others" is the right conclusion *and* the right reason
is not the split itself — a split can reflect a genuine difference in profile.
It is that **no metric resolves a difference at this sample size**, which is
what parity means. The last row also shows why a top-10 statistic should not
carry a headline: its interval is 22 percentile points wide.

**Where parity fails is the transfer test, and it fails against us.** Scored
zero-shot on a screen neither model trained on, crisprHAL 2's raw-sequence model
carries over better than our engineered representation: \|ρ\| 0.0867 against
0.0609, paired difference −0.0258 with the interval clear of zero
(`cui_final_exam.py`). Both numbers are near-nothing in absolute terms — a model
*trained* on that screen reaches 0.458 — so this is a comparison of two small
quantities, and it should be reported as one. The likely reason is specific and
unflattering: the transferable signal in a dCas9 screen is **guide-sequence**
effects (Cui's own subject is sequence-specific dCas9 toxicity), which is exactly
what their input is, while our advantage is flanking DNA, which Finding 5 shows
contributes nothing to silencing. **Our representation is more specialised to
cutting than theirs.** That is a real cost of the design and belongs in the
paper.

*What this test is and is not.* It is a cross-assay transfer test: both models
predict cutting, Cui's label is growth fitness under silencing, and those are
different constructs, so it measures which inductive bias survives a change of
readout rather than which predicts cutting better. It is **not** a held-out test
of the task either model was built for — no unused cutting screen exists — and
treating it as "the final exam" would quietly swap the question. One asymmetry
to declare: SLICER's feature family had already been evaluated against this label
once, in the mechanism test of Finding 5, where the result was a null; nothing
was selected on it, and crisprHAL had never seen it.

### What "parity" can and cannot mean here

The phrase **"parity under the fairest conditions for both models" should not be
used**, because "fairest" conflates two axes of fairness that point in different
directions. Three things can be equalised, and only two of them are:

| axis | on their splits | effect |
|---|---|---|
| **rows, labels, splits** | equal — theirs, untouched by us | fair |
| **tuning effort** | equal, arguably in their favour: their arm is their *published* model, ours is a config frozen on a different dataset and never tuned for eSpCas9 | fair, or against us |
| **input DNA** | **unequal, in our favour** — family A reads ±1,000 nt, their eSpCas9 input is 406 nt | against them |

So the parity result is "each model at its own best configuration", which is a
real and reportable condition — it is how both models would actually be used —
but it is **not** the equal-information condition. When DNA *is* equalised
(Finding 4), the ranking depends on the width: tied on the guide alone
(0.5473 / 0.5494), **crisprHAL 2 ahead by 0.023** at its own 378 nt design span,
SLICER ahead by 0.065 at ±1,000 nt.

**The sentence that is true on all three axes at once:**

> Given each model its own best input and its own tuning, SLICER is
> statistically equivalent to crisprHAL 2 on both of crisprHAL 2's own published
> splits — Δρ +0.0021, 95% CI [−0.0031, +0.0072] on eSpCas9, +0.005 on SpCas9 —
> at roughly 150× less compute. Under equal input DNA the ranking depends on the
> window: crisprHAL 2 is better inside its own 378 nt span, and SLICER is better
> once the window reaches the 250–1,000 nt its input cannot see.

Two further asymmetries belong beside it. Our features were designed on *E.
coli* WT cutting data, the same organism, so design knowledge leaks into the
eSpCas9 arm in a way no split can remove; and the SpCas9 margin compares our
0.6997 against their *published* 0.695 rather than against a re-run under
identical preprocessing — our own re-run of their model on that split gives
0.6940, so that margin is +0.006 measured our way and +0.005 against their
number.

Two existing external checks, neither a substitute for that: the baseline anchor
reproduces Noshay et al.'s published figure through our harness, and SLICER
scores 0.6997 on crisprHAL 2's own shipped split, a partition untouched during
development. **The curated five-fold figures carry an unknown
adaptive-overfitting component**, and the paper should say so.

Remaining before submission:

| | item | cost |
|---|---|---|
| 1 | ~~eSpCas9 final evaluation~~ | **done, and it is a tie** — ρ 0.7842 against 0.7821 on crisprHAL's own eSpCas9 split with their published weights, at 47,591 training guides. Also corrected: eSpCas9 was never an untouched holdout (above) |
| 2 | crisprHAL 2 given **the search we gave ourselves** — **required, not optional, and reinstated as such on 15 October.** Script ready at `colab/crisprhal_tune_matched.py`: 12 draws × 5 folds with patience, resumable, interpretation pre-declared, draw 0 as positive control. The reasons for skipping it have all expired — see "Is it fair to tune their model to convergence?" in Appendix B | 10–15 GPU-h, free T4 |
| 3 | ~~orientation controls~~ | **done** — Jacky, Finding 6 |
| 4 | human baseline re-tuned at the teammate's settings — **delegated to the teammate**, request drafted (`docs/correspondence/request_human_baseline_settings.md`): the grid-search settings behind ρ 0.472 are not recorded in the repo or the log, and the script that produced `human_transfer.csv` is not in `src/`. If it does not arrive, Part 3's cross-kingdom sentence rests on the *sign* of the transfer and says so | ~1 h once supplied |
| 5 | ~~conditional test of the GC hypothesis within matched GC strata~~ | **done** — Finding 5 |
| 6 | ~~sample-complexity curve repeated across folds and seeds~~ | **done** — Appendix B |
| 7 | re-tune crisprHAL 2 at **each input width** — **partly supplied by their own paper.** Browne et al. searched input length *per dataset* and stopped at 378 nt (*E. coli* SpCas9) and 406 nt (eSpCas9), reporting that gains level off: +0.00034 ρ per upstream nucleotide and +0.00074 per downstream one, from 0.554 on the sgRNA alone to 0.697 at 378 nt. So the width is their optimum, found by their own search, and our 1,023/2,023 nt degradation is the continuation of a curve they had already flattened. What is still unrun is re-tuning the *other* hyperparameters at each width | 2–4 GPU-h, now optional |
| 8 | ~~re-derive the ceiling for the curated label~~ | **done: 0.946 [0.944, 0.948]**, from their own published per-replicate counts, cohort and label both verified to reproduce, and conservative by construction (Finding 11) |
| 9 | ~~re-run the gene-grouped ablation on the curated cohort~~ | **done** — all eleven families, Appendix B3. The three largest effects lose nothing beyond the 6% grouping tax; `e_nucleoid` and `g_transcription` carry a real locus component of 6 and 15 points |

**Paper writing is no longer blocked by this list.** Items 1, 2, 7 and 9 are
closed; item 8 needs the original per-replicate read counts and item 4 needs a
teammate, and **neither gates a draft** — the ceiling can be quoted as inherited
with its caveat, and the human baseline enters only one sentence of Part 3. What
the draft must carry, and what this list exists to make unavoidable:

**The last untouched dataset has now been spent, deliberately, on the one
question that could have falsified the mechanism.** Cui et al.'s dCas9 CRISPRi
screen was the only external set never used for a model, feature, split or
hyperparameter. It was spent on "is the flank effect about cutting or about
binding?", and the answer is cutting: family A adds **−0.009** there against
**+0.157** on the cutting screen (Finding 5). **No untouched dataset remains**,
so the adaptive-overfitting caveat below is permanent rather than pending, and
further external validation needs new data.


* the headline comparison is **parity, not a win** — +0.005 and +0.002 on
  crisprHAL's own two splits — and the data-efficiency result is the claim that
  survives a larger screen;
* the curated five-fold figures carry an **unknown adaptive-overfitting
  component**, because eSpCas9 turned out to be confirmatory rather than
  untouched and nothing fully clean is left;
* the 412-column reduction is a **published-matrix result under a 300-column
  budget** and does not transfer to the curated cohort;
* the ceiling for the label we train on is **0.946 [0.944, 0.948]**, measured;
  0.937 belongs to the published label and should not be quoted for curated
  figures.

The shared Google Doc is **frozen as of 13 October 2026** and is no longer kept
in sync; this report is the single maintained document.

**A guide-design tool is not a deliverable.** The findings are the contribution,
the field already has several predictors, and everything needed to build one
later exists (`featurise.matrix()` turns any 20-mer into the published
representation).

### What the pivot re-opens

Many choices were made under two constraints that no longer bind: the 13,880-row
published matrix, and Noshay's iRF as the baseline. Each of the following was
settled under those constraints and is **not** automatically valid on crisprHAL's
33,567-row curated cohort. None is known to be wrong; all are untested there.

| decision | made under | why it may differ now |
|---|---|---|
| **the 412/427-column reduced set** | non-inferiority on the *published* matrix and label | **closed, and the answer is no.** With no selection on the curated cohort, 364 columns lose 0.0118 and 364 + family A lose 0.0142 — 2–3× the 0.005 margin. Non-inferiority was a published-matrix result under a 300-column budget (Finding 2) |
| **the published Δρ levels** | Noshay's 13,880 rows | **explained, not just re-measured.** The 3.3× inflation is the row population: the 24,950 guides only crisprHAL publishes have 1.34× the label spread and a 2.5× stronger flank-GC correlation. The published matrix understated the effect (Appendix B2a) |
| **the ceiling, 0.937** | Guo's replicate statistics for the published label | **closed, and it was higher as predicted: 0.946 [0.944, 0.948]**, from crisprHAL's own per-replicate counts (Finding 11) |
| **`n_features` = 300** | selector sweep on 6,232 published columns | **closed.** Selecting 300 against using every column: 0.5445 / 0.5449 on the base and 0.7084 / 0.7079 with family A. ±0.0005 in both directions, so the budget is free on this cohort too (Finding 2) |
| **grouped CV by `arc5` / 100 kb block** | 13,880 guides, within-gene variance share 0.844 | **re-measured — it moved.** 0.844 → **0.713** on the curated cohort: gene identity explains 29% of the label there against 16% here, so gene-grouped CV constrains the model *more*, not less (Appendix B) |
| **champion hyperparameters** | 627 draws against the old cohort | **decided: keep the freeze.** The champion XGBoost and LightGBM at its own unrelated defaults land within **0.0002 ρ** of each other on the curated cohort with family A (0.7084 / 0.7082), so the configuration is not a knife-edge and re-tuning has little to win. Stated as a decision with its evidence rather than left as a tension |
| **the family Δρ table** | published matrix and label | **closed — all eleven families re-measured on the curated cohort** (Appendix B3). The *ordering* transfers almost exactly (rank ρ 0.97); every family inflates, median 3.3×. So the published table is still a guide to which families matter, and not to how much |
| **"sixteen model classes span 0.116 ρ"** | published matrix, no family A | **closed, and it holds.** Eight classes on the curated base *with* family A span **0.1076 ρ** (XGBoost 0.7084 → k-NN 0.6007), against 0.116 for sixteen classes without it. Model class spans ~0.11 either way while family A alone is worth +0.164 (Finding 2) |
| **Noshay's iRF as baseline anchor** | the only available comparator | now provenance only; crisprHAL 2 is the baseline |

**The honest framing is that the model layer moved cohorts and the
interpretation layer did not.** The label description in Part 3 was wrong for
exactly this reason until 13 October — it described the published score while we
trained on the curated one. That is the shape of error to look for in the rest of
this list.

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
| the mechanism | a dCas9 **CRISPRi** screen, the last untouched dataset, could have shown the flank effect to be about binding or accessibility rather than cleavage. Family A adds **−0.009** there against **+0.157** on the cutting screen, flank-only 0.133 against 0.341 — so the effect is specific to cutting (Finding 5) |
| the flanking-context thesis | the family table on the curated cohort sorts by **how far outside the 20-mer a family can see**: nothing confined to the guide clears +0.019, nothing above +0.05 is confined to it. Arrived at by withdrawing a claim that pointed the other way (Appendix B3) |

### What it cost — eight claims withdrawn in six days

| withdrawn | replaced by |
|---|---|
| "flank GC +0.159" | does not reproduce by either correlation measure; the conditional analysis (+0.082 partial) replaces it |
| "not recoverable by a convolutional network given the same DNA" | **matched to crisprHAL's own 189/166 nt span, their convolutions beat our windowed composition by 0.025.** Our lead is the 250–1,000 nt windows they cannot see |
| "0.047 against the nearest gene, 0.005 with it" | unweighted point estimates; the block bootstrap gives Δ 0.026 with an interval including zero, and it **collapses to 0.007 under distance+GC matching** |
| "the asymptotes are close … not evidence of a higher ceiling" | paired across five folds the gap is **+0.0133 ρ, p = 0.0058, 5/5 folds** — our own caveat was an artefact of measuring one fold |
| "427 columns are the portable set" | 412; and the curated cohort never carried the 63 hand-named columns at all |
| "eSpCas9 is the designated **untouched** final evaluation, to be evaluated once" | it had already been used for four feature arms across three seeds and two CV schemes. Confirmatory, not untouched; "once" was never available (Part 4) |
| "SLICER beats crisprHAL 2" | **parity.** Δρ +0.0021, 95% CI [−0.0031, +0.0072] on their eSpCas9 split, +0.005 on their SpCas9 split. The lead at 26,853 training guides is +0.0133 and vanishes at 47,591 — a small-data claim, not a ranking |
| "`d_mechanics` adds no new DNA and is worth +0.099 — representation beats information" | 8 of its 30 columns are **flanking-DNA** thermodynamics and carry +0.097 of it. The representation effect is **+0.011 to +0.019**, agreed across three guide-only families |

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

Every control here is written the same way: **what it rules out**, **why the
design rules that out** rather than merely gesturing at it, and **what would be
believed without it**. The third line is the one worth reading — several of these
controls exist because the thing they rule out was, for a while, believed.

### Nulls — is the pairing between feature and label real?

**Permutation floors.** Every family with a gain was re-run with its feature rows
shuffled against the labels.
*Why it works:* shuffling destroys the guide↔feature correspondence while
preserving each column's marginal distribution and the model's capacity exactly,
so the arm measures how much ρ a selector and a boosted tree can manufacture
from 300 columns of correctly-shaped noise. That floor is not zero and has to be
measured rather than assumed.
*Without it:* family A's +0.080 would rest on the assumption that a 6,580-column
search cannot overfit a 13,880-row training split. The measured floor is
**0.5264 against a 0.5272 baseline** — i.e. zero — and `j_periodicity`'s
shuffled arm scores *higher* than its real one, which is what a null family
looks like from the inside.

**The texture-preserving null for family A** (`shiftnull.py`). Each guide is
re-assigned the flank track read from a position offset by a **circular
chromosome shift**: the same track, at the wrong place.
*Why it works:* row shuffling tests a weaker null than family A's claim.
Family A asserts that *this* guide's local DNA predicts *this* guide's activity;
row shuffling breaks that but also destroys genomic autocorrelation, so it
cannot distinguish "local DNA matters" from "DNA-like texture at the right
smoothness matters". A circular shift preserves every column's marginal, its
smoothness and its long-range autocorrelation exactly, and breaks only the
alignment. Verified on `dn500.gc`: the mean moves 0.5103 → 0.497–0.508 while the
correlation with the aligned track falls 1.00 / 0.41 / 0.05 / −0.03 at 0 / 1 kb /
100 kb / 2 Mb.
*Without it:* the family A result would be compatible with a model that has
learned the *texture* of bacterial DNA rather than anything about the cut site.

**One shift would not have been enough**, which is why the shift is swept. At
1 kb the shifted columns are still 0.41 correlated with the real ones, so a
single 1 kb control would have reported a spurious residual effect and a single
2 Mb control would have proved only that a distant genome position is
uninformative. Sweeping converts the control into a measurement: Δρ against
shift distance **is** the autocorrelation length of the effect, read off
independently of the window sizes family A happens to use. Results in Finding 3.
Grouped CV (100 kb blocks) throughout, because a positional feature under random
KFold can score by locus recognition and the shifted arms would inherit that too.

**Negative controls from the source experiment.** Available for exactly one
family: the dCas9 / no-antibody arm of the GapR-seq experiment.
*Why it works:* it is the same assay with the biology removed, so a feature that
predicts equally well from the control track is measuring the assay, not the
phenomenon the track is named after.
*Without it:* `d_supercoiling`'s +0.045 would still be reported as supercoiling.
It is **DNA read density**, and the family was overturned by its own control
rather than by an argument — which is the only reason it was overturned at all.

### Splits — is the gain prediction, or address memorisation?

**Grouped cross-validation.** Anything positional is reported under `arc5`,
100 kb blocks, or whole genes held out.
*Why it works:* the screen puts several guides in every gene, and guides in one
gene share a locus. Plain KFold therefore puts guides from the same gene on both
sides of the split. For a sequence feature that is harmless, because the
sequences differ; for anything positional it is not, because those columns
*identify* the locus, and a model can be rewarded at validation time for
learning "guides around here score about this much". Holding out whole groups
removes that route entirely, since no held-out gene contributes a training row.
*Without it:* the positional families' gains would be indistinguishable from
locus recognition, and the share of label variance that lies *between* genes is
exactly the budget available for that trick — **16% on the published matrix, 29%
on the curated one** (`cohort_groups.py`).
*And the control needs its own calibration.* Families that are functions of the
guide cannot be invalidated by a change of split, so whatever *they* lose under
grouping is the cost of the harder partition rather than memorisation. They lose
6% in aggregate, which sets the benchmark the positional families are read
against — `a_flank`, `d_supercoiling` and `i_shape` lose nothing beyond it,
`e_nucleoid` and `g_transcription` lose 6 and 15 points more (Appendix B3).
Without that calibration every family would appear to lose something.

**Why gene-grouping became necessary on the curated cohort, specifically.** The
grouped arms on the published matrix were a precaution against a small risk:
with 84.4% of label variance inside genes, only ~15% was available to memorise.
The curated cohort is **genome-wide** — 4,013 genes at 7.5 guides each, against a
1,222-gene panel at 11.3 — so gene identity explains **29%** of its label, nearly
twice as much. The risk the control guards against roughly doubled when the
cohort moved, while every curated family number was measured under random KFold.
That is why the re-run was not optional, and the result is in Appendix B3: the
families keep 79–96% of their gains, so the inflation is not memorisation. **A
control that had not been run would have left the single largest table in the
report resting on the assumption that the published cohort's grouping behaviour
transferred — and the variance share says it does not.**

### Matching — is the comparison fair?

**Matched-span head-to-head against crisprHAL 2.** crisprHAL is also run at our
window widths, and SLICER at theirs.
*Why it works:* the two models differ in architecture *and* in how much DNA they
read, and a head-to-head at each side's native width cannot separate them.
Equalising the input DNA leaves architecture as the only difference, in both
directions: at their span our windowed composition loses by 0.025; at ±1,000 nt
we lead by 0.065.
*Without it:* "we out-encode a tuned deep model" — which was claimed, and is
false. The honest claim is access to DNA they never see, and it is narrower and
much harder to attack.

**Distance- and GC-matched orientation comparison, with a block bootstrap**
(Jacky).
*Why it works:* opposite-orientation guides are not a random sample of
same-orientation guides — they sit at different distances from the gene and in
different GC. Matching on distance and flank GC compares like with like, and
bootstrapping over 47 genomic blocks rather than over rows accounts for the fact
that nearby guides are not independent observations, which is what sets the
interval width honestly.
*Without it:* "0.047 against the nearest gene" stands. After matching it is
**0.007 [−0.024, 0.038]**, P = 0.34 — a cohort confound. The effect is real
against a curated **TSS** (Δ 0.051 [0.020, 0.082]), which is a different and
better-specified claim.

**The conditional GC test, within matched target-GC strata.**
*Why it works:* flank GC and target GC are correlated, so a marginal association
between flank GC and activity could be target GC seen through it. Binning on
target GC and measuring inside each bin removes that path by construction.
*Without it:* the GC account would rest on a marginal correlation. Conditioning
*raises* the association, +0.044 marginal → **+0.082** partial, positive in all
five strata — the signature of a suppressor relationship, and the opposite of
what a confound looks like.

### Instruments — is the measurement measuring what its name says?

**The selector control: 300 columns against all of them.**
*Why it works:* every arm selects 300 columns from its candidate pool, so an arm
with more candidates could gain simply by being given more to choose from.
Re-running with selection switched off removes the budget as a variable.
*Without it:* `d_mechanics`'s +0.099 on a base starved of dense columns would be
open to the obvious objection. It is not selection: **+0.0988 selecting 300,
+0.0993 using all 6,199**.

**The reconstructibility probe: each of a family's columns predicted out of fold
from the base.**
*Why it works:* "this feature is a deterministic function of the 20-mer" is a
claim about the feature's *inputs*, and reading the builder is the fast way to
check it — but a probe makes it quantitative and catches columns whose inputs
nobody read. A column the base predicts at R² = 1.0000 adds no information; one
it predicts at R² ≈ 0 is reading something the base does not contain.
*Without it:* the claim that `d_mechanics` adds no new DNA stands, and its
+0.099 remains the report's headline evidence that representation beats
information. Eight of its thirty columns came back at **R² ≈ 0** — flanking-DNA
thermodynamics — and they carry +0.097 of the +0.099 (Finding 2). **This control
cost the report its most quotable claim, and it is the single most useful thing
run in two days.**

**The guide-only / flank-only decomposition** (`no_information.py`) is the
follow-up that same probe demanded: split the family by what its columns read and
run both halves against the same base. +0.011 for the 22 protospacer columns,
+0.097 for the 8 flank columns. *Why it works:* the two halves share the base,
the rows, the folds and the selection budget, so the only difference is reach.

**The faithfulness positive control.**
*Why it works:* an attribution method that assigns importance to real features
and to permuted ones alike is uninformative, so the probe is calibrated by
feeding it a known null and checking what it reports. At a **matched share of
attributed importance** (~35%), permuted columns score 0.258 against real
columns' 0.581.
*Without it:* the standard faithfulness probe's output on a redundant matrix
would read as a measurement rather than as the uninterpretable number it is
(Finding 10).

**TOST non-inferiority with a pre-declared margin.**
*Why it works:* "the reduced set is as good" cannot be established by failing to
reject a difference — absence of significance is not evidence of equivalence.
Declaring a 0.005 ρ margin *before* the test and then showing the confidence
interval falls inside it is the form of claim the data can actually support.
*Without it:* "427 ≈ 6,232" would be an argument from a non-significant p-value,
which is the most common error in this literature.

**The attenuation ceiling** (Spearman–Brown on replicate statistics).
*Why it works:* a model's ρ cannot exceed the label's own reliability, so the
ceiling is a property of the measurement and has to be estimated from replicates
rather than from model performance.
*Without it:* "the model is out of material" would be a claim about the model.
With it, it is a claim about how much signal the label contains — and the figure
is **inherited from the published label and not yet re-derived for the curated
one**, which is Part 4 item 8.

**The cross-assay control: a screen where the mechanism should *not* apply.**
*Why it works:* every other external check is another Cas9 cutting screen, so a
flank effect there is consistent with cutting, with binding, and with local
accessibility alike. dCas9 binds without cutting, so a flank effect that is
about the cleavage step must disappear, while one about binding or accessibility
must survive. The control is the only one here that could have falsified a
mechanism rather than a number.
*Without it:* Finding 3's mechanism sentence would rest on plausibility. Family A
adds **−0.009** to a CRISPRi screen and **+0.157** to a cutting screen under one
protocol, with a flank-only arm (0.133 against 0.341) to rule out selection
dilution (Finding 5).

**The replicate-split ceiling.**
*Why it works:* a ceiling has to come from the measurement, not the model. Two
Cas9 replicates and two controls allow two independent estimates of the same
quantity; their agreement is the reliability of one, and Spearman–Brown converts
that to the reliability of the released mean of two. Two checks make it an
estimate of *their* label rather than of our arithmetic: their cohort reproduces
under their stated cutoff (33,871 against 33,567) and a plain log-ratio
reproduces their score at |ρ| 0.957.
*Without it:* the curated arms would keep quoting 0.937, a figure derived for a
different label by a different route. It is **0.946 [0.944, 0.948]**, and
conservative, since their posterior shrinkage can only raise reliability above a
plain log-ratio's.

### Guards — did the computation actually run?

Five failures in three days produced plausible numbers, destroyed real ones, or
raised a false alarm, from code that reported success. These are not controls in the experimental sense; they are the
assertions that should have existed first.

* **crisprHAL's `train()` catches its own exceptions and returns `None`
  identically on success and failure.** A wide-window run scored ρ 0.0434 in
  0.36 min on an untrained network and passed every sanity check that was being
  applied — finite, right length, non-degenerate. Fixed by calling `model.fit`
  and `model.predict` directly. *The guard that works:* assert the loss moved.
* **`n_features=None` resolves to `config.N_FEATURES`**, so a "no selection" arm
  silently selected 300. Caught only because the two arms agreed to sixteen
  decimal places — i.e. by a coincidence that was too perfect, not by design.
  *The guard that works:* pass `X.shape[1]` explicitly and assert the column
  count used.
* **A cross-check that was wrong in the alarming direction.** Cui's coordinates
  were compared to ours with `|ours − theirs| ≤ 1`, which reported agreement for
  **0.0%** of guides and reads as an assembly mismatch. The offset takes exactly
  two values, +3 and −21, one per strand: they report the PAM-proximal end, and
  every guide agrees exactly. A check that fails loudly is still a failed check,
  and this one would have stopped the last untouched experiment.
* **A grouped run wrote its results into the random-row table and destroyed
  it** — a leftover raw `to_csv(OUT)` in a loop whose other writes had been
  routed to the grouped output. Recovered from the committed copy. Noticed only
  because a comparison table's "random" column came back holding the grouped
  numbers. *The guard that works:* one output path per run, resolved once.
* **`b_energy` wrote a block with 33,567 rows and zero feature columns** and
  reported success, because its builder catches import errors per guide and then
  drops the error column. It would have scored Δρ = 0.000 and read as a clean
  null. *The guard that works, and is now in place:* refuse to write or read a
  block with no populated feature column.

The shape they share: **a computation that fails and reports a number of exactly
the kind expected.** Every one would have entered the report as a result, and two
of them as negative results, which attract the least scrutiny of all.

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
Finding 4). Peak memory falls to 0.65 GB only if the reduced
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

*And the gap is specific to this data volume.* The same comparison on
crisprHAL's eSpCas9 split, at 47,591 training guides, is a tie (0.7842 against
0.7821; Part 4). Read together, the two results are one statement: **+0.0133 at
26,853 guides, +0.0021 at 47,591** — a converging gap, measured twice, which is
a stronger and narrower claim than either number alone.

*Protocol note:* the module's printed summary used to report only "share of each
model's own best", which reads as a data-efficiency claim and is not one — two
curves can both reach 95% of themselves at the same n while being far apart in
ρ. It now leads with absolute thresholds and labels the own-best figures
diagnostic.

### Is it fair to tune crisprHAL 2 to convergence? Yes — and that is why it has to be run

The question was put in the right form: if a matched search is the fair
comparison, the fact that it would weaken our margin is not a reason to skip it;
if it is arguably *not* fair, skipping it is legitimate. So the answer has to be
argued on fairness alone.

**"To convergence" is not the right target, but "matched" is.** A deep network
has no canonical convergence point for a hyperparameter search — the result
depends entirely on who draws the search space and when they stop. What *is*
well defined is **equal effort under an equal protocol**: the same number of
draws, the same nesting, the same patience rule, each starting from its own
published configuration. That is what the script runs, and it is the condition
our own tuned-vs-tuned row implicitly claims.

**Every reason we had for not running it has expired.**

| the reason | status |
|---|---|
| ~~17 CPU-hours locally, too expensive~~ | **gone.** 3.1× faster on a free T4; 10–15 GPU-h over two to four sessions |
| ~~their published weights already answer it~~ | **answers a different question.** They settle the comparison *on their splits*, where it is parity. They say nothing about our folds, which is where our +0.0172 lives |
| ~~the defaults-vs-defaults row is a clean like-for-like fallback~~ | **false.** Our "default" is the 627-draw champion from the published cohort; theirs is their published configuration (Part 4) |
| ~~we flagged it as an upper bound, which is honest~~ | **not sufficient.** Flagging a bound you could measure is weaker than measuring it, and we pre-registered the obligation: `crisprhal_tune.py` states that if their tuned score does not close the gap, "the asymmetry is a live caveat and must be quoted alongside the result." It did not close the gap. The caveat is live |

**So no on-our-folds number we report is symmetric in search effort**, and the
matched run is the only thing that would make one. It should be run.

**The expected outcome makes the paper stronger, not weaker.** Their own
fully-tuned published WT model lands ~0.005 behind SLICER on their own WT split
at the same data scale, so the matched search is expected to take +0.0172 down to
roughly +0.005. **"Parity with the state of the art at ~150× less compute,
confirmed under a matched search" is a harder claim to attack than "+0.017 under
a search we admit was unequal."** A number that survives the obvious objection
is worth more than a larger number that invites it.

**One asymmetry the matched run will not remove, and it favours us.** SLICER's
tuned arm starts from a configuration already selected by 627 draws on the
published cohort and then adds 12 draws per fold; their matched arm would get 60
draws and no such history. Strict equality of *total* search would need a larger
budget on their side. The matched run removes the largest asymmetry, not all of
it, and the residual should be stated rather than left for a reviewer to find.

### Would renting a TPU settle the tuning asymmetry? Yes, and it should not be a budget item

The margin's weakest point is that crisprHAL got 10 configurations and SLICER
627. Matching 627 draw-for-draw is ~460 CPU-hours, which is where a £20–50
rental estimate came from. **That estimate was wrong**: the trace shows 40 draws
captured 100% of SLICER's gain, so an equal-footing search means running *their*
search to *its own* patience criterion — about **55 fits**.

*And the cost of those fits is now measured rather than guessed, which revises
the estimate upward.* Their published configuration fits one fold in **5.48 min
on a Colab T4** against **17.0 min locally** — a **3.1× speed-up**
(`crisprhal_wide_window.csv`, `crisprhal_rerun.csv`). But a search's draws
average *larger* than their default: the local search's median fit was 44 min
against 17 for the default, so ~14 min/fit is the right T4 budget. Twelve draws
inside each of five folds plus five refits is 65 fits, so **10–15 GPU-hours, two
to four free sessions with resume** — not the "2–4 GPU-hours, one free Colab
session" this section claimed before any Colab timing existed. That figure was
too optimistic by 3–5×, because it priced the *default* configuration for a
search that mostly does not use it.

**What a matched search is expected to buy, bounded rather than extrapolated.**
Their own fully-tuned **published** WT model scores 0.695 on their own WT split,
where SLICER scores 0.6997 at the same data scale (~26.8k training rows). That is
the best available estimate of what their architecture reaches when *its authors*
tune it at this cohort size, and it sits ~0.005 behind us. So the expected
endpoint of a matched search on our folds is the margin narrowing from **+0.0172
to roughly +0.005**, not to zero. The interpretation is fixed in advance in
`colab/crisprhal_tune_matched.py`: at **≥ ~0.716** the margin was mostly a
tuning-effort artefact and parity is the honest conclusion on our folds too; at
**0.704–0.710** it survives and ~+0.005 to +0.010 is the number to quote; **above
0.7213** we lose on our own folds once their search is equalised, and should say
so plainly. Draw 0 is their published configuration, so it doubles as the
positive control — its fold scores must land near 0.686–0.702.

**A TPU would be the wrong instrument.** TPUs earn their keep on large dense
matmul under XLA; this model's recurrent branch is a bidirectional GRU — a
sequential loop, the shape that maps worst onto them. A mid-range GPU is both
cheaper and faster for it.

*When:* once, at data freeze. Re-tuning is required only when rows, label or
folds change (both models) or the feature set changes (SLICER only);
documentation and analyses outside the curated arm require none.

**For the comparison on *their* splits it is moot; for ours it is not.** The
objection applies to *our* runs of their architecture, which is exactly what the
five-fold rows are. On their own two shipped splits we compare
against **their published weights** — their tuning, their search, their
published numbers, which our harness reproduces to three decimals (ρ 0.782 →
0.7821 on eSpCas9) — and the margins are +0.005 and +0.002 (Part 4). Whatever
search budget they used is already inside those numbers. The tuning-matched run
remains worth doing as a *cost* measurement; it is no longer a threat to the
*performance* claim.

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

### Does grouped cross-validation still mean the same thing after the cohort moved?

No, and the direction is the uncomfortable one. Every grouped-CV argument rests
on one number: the share of label variance lying **within** genes rather than
between them. If nearly all of it is within, a model cannot score by memorising
which gene a guide sits in, and a random split and a gene-grouped split measure
nearly the same thing.

| cohort | guides placed in a gene | genes | guides/gene | within-gene share |
|---|---:|---:|---:|---:|
| published (13,880 rows) | 13,829 | 1,222 | 11.3 | **0.843** |
| curated (33,567 rows) | 30,203 | 4,013 | 7.5 | **0.713** |
| published, 100 kb blocks | 13,879 | 47 | 295 | 0.980 |
| curated, 100 kb blocks | 33,567 | 47 | 714 | 0.973 |

**Gene identity explains 16% of the published label and 29% of the curated one.**
The reason is what each cohort is: Noshay's rows target a gene panel, while
crisprHAL's curated release is genome-wide — 4,013 genes at 7.5 guides each. More
genes, fewer guides in each, and more of the variance sits between them.

**The prediction that follows from this is wrong, which is why it was tested.**
Twice the between-gene variance should mean a larger gap between random and
gene-grouped CV. The gap is *smaller*: grouping cost `e_nucleoid` 42% of its gain
on the published matrix and 12% here, `g_transcription` 36% and 21%
(Appendix B3). The missing variable is **guides per gene** — 7.5 here against
11.3 — because between-gene variance sets how much a locus-memorising model could
win while guides per gene sets how well it can learn each locus's mean. Both
moved, in opposite directions, and only the measurement says which won.

Gene assignment is by coordinate on NC_000913.2 against the reference gene
table, not from either dataset's own annotation, so both cohorts are measured the
same way. On the published rows that assignment agrees with Noshay's own for
**97.7%** of guides and gives the same share to three decimals (0.843 against
0.844) — which is the check that the change above is the cohort and not the
method. `python -m sgrna.cohort_groups`, `results/cohort_groups.csv`.

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
nearest-gene proxy, and the highest-value item given Finding 6. From a teammate:
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

## Appendix B2 — Why the imported families failed, and why that is not a screen

This began as a numbered finding: a rule that a feature predictable from the
20-mer cannot help, with a table of eleven families as evidence. **The table does
not support a rule**, and it is demoted here rather than deleted because the
measurements are real and the failure mode is instructive.

Out-of-fold R² of predicting each new column from position-specific mono- and
dinucleotide indicators of the protospacer, over all eleven families:

| family | columns | median R² | **share of columns with R² > 0.9** | Δρ |
|---|---:|---:|---:|---:|
| `b_energy` (CRISPRoff ΔG) | 10 | 0.984 | **70%** | +0.007 |
| `d_mechanics` (duplex stability) | 30 | 0.845 | **50%** | +0.020 |
| `c_folding` | 9 | 0.297 | 0% | +0.007 |
| `f_methylation` | 17 | 0.141 | 0% | +0.004 |
| `a_flank` | 322 | −0.012 | 0% | **+0.080** |
| `d_supercoiling` | 26 | −0.013 | 0% | +0.045 → artefact |
| `g_transcription` | 18 | −0.016 | 0% | +0.015 |
| `e_nucleoid` | 20 | −0.016 | 0% | +0.016 |
| `i_shape` | 152 | −0.017 | 0% | +0.036† |
| `j_periodicity` | 24 | −0.021 | 0% | −0.001 |
| `h_offtarget` | 7 | −0.022 | 0% | +0.000 |

† `i_shape` is the standalone increment over the base, like every other row.
Earlier versions of this table printed +0.001, which is its increment *on top of
family A* — a different quantity, and the one place in the report where a
marginal-on-A figure sat in a column of base-relative gains (Appendix B3).

**Read the last-but-one column, not the median.** The structure is binary: two
families contain columns the 20-mer *determines*, and nine contain none.
`c_folding` and `f_methylation` have middling medians but **no** determined
column — their medians average weak partial fits and detect nothing.
Nearest-neighbour thermodynamics is a sum over adjacent pairs, so binding energy
is a second-order quantity the matrix already holds: importing CRISPRoff was
importing the matrix back into itself.

**Why the nine null families agree so closely.** Out-of-fold R² against a target
with no relationship to the basis is not 0 but a small negative set by the basis
size and the row count, not by the target. All nine land between −0.012 and
−0.022 with 10th percentiles of −0.019 to −0.022: they are sitting on a shared
null floor, which is what "no relationship" looks like rather than a defect.

*Status of this rule.* **A qualitative screen, and it is not quoted with a
score.** Of the two families whose columns are determined, neither produced a
material gain, and that is the direction worth using: if a candidate's columns
are individually reconstructible from the 20-mer, do not build it. The converse
has no force — `h_offtarget` and `j_periodicity` pass the screen and deliver
nothing, and `i_shape` passes it and delivers +0.036 standalone, falling to
+0.001 only once family A is present.

*Withdrawn here:* earlier versions scored this rule as "8 times out of 8" in one
direction and "7 of 9" in the other. **Neither count is supportable.** Only four
families have positive R² at all, no threshold for "high" was ever declared, and
`d_mechanics` — unambiguously high at 0.845 — returned +0.020, the second-largest
gain in the table. The counts were doing rhetorical work the design cannot carry;
the screen stands on its mechanism, not on a tally.


### Why this is not a general screen

Three things, and the first is decisive.

**The rule applies to two families.** Only `b_energy` (R² 0.984) and
`d_mechanics` (0.845) are substantially determined by the 20-mer. Everything else
sits below 0.30. A rule with n = 2 is an observation.

**For the strongest case it is a tautology.** CRISPRoff ΔG is *computed from the
sequence* by nearest-neighbour summation. That it adds no information to a model
holding the sequence losslessly is arithmetic, not an empirical discovery; the R²
of 0.984 confirms the arithmetic. The same applies to `d_mechanics`. So the two
supporting cases are the two cases where no measurement was needed.

**The other nine carry no signal about the rule.** Their R² spans **0.010**
(−0.022 to −0.012) — null-floor variation set by family size, not by
predictability — while their gains span **0.081** (−0.001 to +0.080). Across all
eleven families ρ(R², Δρ) = **0.224, p = 0.508** — it was quoted as 0.489,
p = 0.127 while `i_shape` sat at +0.001, and correcting that entry weakens the
association further. Arranging nulls in a table
sorted by a statistic with no resolving power produces the *appearance* of a
trend from a pile of things that did not work, for unrelated reasons:
`h_offtarget` needs the rest of the genome, `j_periodicity` is a genuine null,
`i_shape` duplicates family A, `d_supercoiling` was an artefact its own control
overturned.

**What survives** is the statement in Finding 2: a deterministic function of the
20-mer cannot add information to a model that already encodes the 20-mer. That is
worth saying because people keep importing such features. It is not a predictive
screen, and this report no longer quotes it as one.

## Appendix B2a — Curation and feature selection are not the same kind of dropping

Both discard data, and it is easy to treat them as interchangeable. They are not.

**Curation drops rows; selection drops columns.** crisprHAL's curation removes
guides whose *label* is unreliable — it is a read-count filter — which reduces
noise in the target. Feature selection removes *inputs* that do not predict,
which changes what the model sees. Neither touches the other's object.

**Only one of them can flatter a score without improving a prediction.**
Selection is fitted **inside each training fold**, so it cannot see the test rows
and cannot leak. Curation is applied to the whole dataset **before splitting**,
so it also removes noisy rows from the *test* set — raising ρ partly by making
the evaluation easier rather than the model better. Our own figure for the value
of curation, ρ 0.607 → 0.628 on restricting to the 8,617 retained rows, contains
both effects and **we have never separated them**.

**What curation is worth here, measured.** On the 8,617 guides both cohorts
share, swapping Noshay's label for crisprHAL's changes almost nothing — baseline
0.5387 → 0.5370, with family A 0.6279 → 0.6305, a difference of +0.003 inside the
noise. The value is in *which rows survive*, not in how the survivors are scored.

**The two cohorts are not nested**: 8,617 shared, 24,950 only in crisprHAL,
**5,263 only in Noshay**. So curation is not a filter applied to Noshay's
selection — it is a different, larger draw from the same Guo screen with a
quality threshold. The guides crisprHAL drops look unremarkable on copy number
and uniqueness; their only visible signature is a compressed label range.

**What the procedure actually is** (Browne et al., 2026, read 15 October — this
was an open gap in every earlier version of this report, and we train on their
label):

* **The score is not a read-count ratio.** It is the ALDEx2 `diff.btw` log2
  fold-change between the experimental (Cas9) and control (dead-nuclease) arms —
  *"the expected value of a Bayesian posterior derived from the data"*, over two
  control and two experimental replicates. That matters for the ceiling argument
  below: a posterior mean is shrunk toward the prior, so its reliability is a
  property of the prior as well as of the read counts, and the Spearman–Brown
  machinery we applied to Noshay's two-replicate geometric mean does not carry
  over unchanged.
* **The filter is an average control-condition read count across the two control
  replicates**, and the threshold is **73** for the *E. coli* SpCas9 set we train
  on (31 for eSpCas9, 56 for *C. rodentium* TevSpCas9). So "a read-count filter"
  was the right inference.
* **The threshold is itself a fitted quantity** — chosen by 5-fold
  cross-validation on the training set. Curation is therefore not a fixed
  data-cleaning rule but a hyperparameter optimised for model performance, which
  is worth knowing before describing their cohort as independently cleaner.
* **And it is applied before the split.** Their Table 2 reports the cutoffs
  against the unfiltered pools, before the 80/20 partition — their own text flags
  the tension with the hold-out being untouched. This confirms the concern above
  from their methods rather than from our inference: curation cleans the test set
  too, and our 0.607 → 0.628 figure still contains both effects.

### Why the columns behave *qualitatively* differently after curation

The objection is the right one: if curation only removed noise, every family's
gain should have been scaled by a single attenuation factor and nothing should
have changed in kind. `i_shape` should not have looked like a null and then like
a third-largest effect; `d_mechanics` should not have gone from +0.020 to +0.099.
Noise removal does not reorganise a table.

**It did not only remove noise. Four things changed at once, and three of them
are not about noise at all.**

| what changed | is it noise removal? |
|---|---|
| the **label** — crisprHAL's read-count-filtered score replaces `cut_score` | yes |
| **which rows** — not nested: 8,617 shared, 24,950 only crisprHAL, 5,263 only Noshay; genome-wide (4,013 genes at 7.5 guides) against a panel (1,222 at 11.3) | no — a different draw |
| **how many rows** — 13,880 → 33,567, 2.4× | no |
| the **base representation** — the curated base is the 6,169 regenerated columns and carries **none** of the published base's 63 hand-named summaries | no — a different comparison |

**The part that is noise removal is nearly inert, and this is measured.** At
fixed rows — the 8,617 both cohorts share, published base, same folds — swapping
the label moves family A from **+0.0892** against `cut_score` to **+0.0936**
against the curated score. A **0.004** move, against a cohort move of +0.080 →
+0.164. Whatever tripled the table, it was not the label, and the attenuation
argument is bounded at a few per cent of the effect rather than 230% of it.

**Still, noise removal *can* change behaviour in kind, and it is worth being
precise about why**, because the intuition that it cannot is the thing that makes
this surprising. Two reasons:

*Feature selection and tree splitting are not continuous in signal-to-noise.* A
family is only worth anything if its columns are selected into the top 300 and
then split on. Both are threshold operations. A weak-but-real column sitting just
below the selector's cut contributes **exactly zero**, not a small amount; drop
the label noise slightly and the same column crosses the threshold and
contributes its full value. So a small change in reliability can produce a step
change in measured Δρ. This is the mechanism by which "just less noise" shows up
as a qualitative difference, and it is specific to a pipeline with a hard
selection budget — which ours has, at 300.

*Label noise is not uniform across rows, so removing noisy rows is not a
null operation on the covariates.* A read-count filter removes
low-abundance guides preferentially, and abundance is **not** spatially random —
we measured that directly when `d_supercoiling`'s gain turned out to be DNA read
density rather than supercoiling. A filter on read count is therefore a filter
that touches the joint distribution of every positional feature and the label,
not just the label's variance. That is a change of population, and it is the one
the table is most likely responding to.

**The pattern in the data points at the fourth row of that table.** The
inflation is nearly uniform — rank correlation 0.97 between the published and
curated columns, median 3.3× — and a uniform multiplier is the signature of
something that changed the *scale of the measurement*, not the biology. The base
losing its 63 hand-named dense columns does exactly that: every family that
supplies dense continuous summaries is now measured against a weaker comparison,
and the weaker the base, the more any such family is worth. It predicts
multiplication with the ordering preserved, which is what is observed.

**All four were tested, and the answer is the rows.** Each row below holds
everything else fixed and changes one thing:

| candidate | test | effect on family A's Δρ |
|---|---|---:|
| the **label** | same 8,617 rows, published base, swap `cut_score` for the curated score | **+0.004** (+0.0892 → +0.0936) |
| **row count** | random 13,880-row subsamples of the curated cohort, 3 draws | **−0.003** (+0.1672 ± 0.0027 against +0.1638 at 33,567) |
| the **base** | add 41 dense guide-only summary columns to the curated base, then measure family A on top | **+0.013** (+0.1638 → +0.1504) |
| **which rows** | the remainder of a +0.084 gap | **≈ +0.070** |

Row count is not merely small, it is **absent**: at the published cohort's own
row count, the curated cohort still gives family A **+0.167**. The base matters a
little — giving the base `b_energy`, `c_folding` and `d_mechanics`'s 22 dense
guide-only columns raises it from 0.5445 to 0.5692 and takes 0.013 off family
A — which is 8% of the gap, not the explanation. The label is 5%.

**The 24,950 guides crisprHAL has and Noshay never published are a different
population, and the flank effect is 2.5× stronger in them.** The cleanest form of
this needs no model at all — the marginal rank correlation between a single
flank-GC column and activity:

| rows | label | `up500.gc` | `up50.gc` | `dn500.gc` |
|---|---|---:|---:|---:|
| the 8,617 **shared** | Noshay's `cut_score` | +0.069 | +0.056 | +0.052 |
| the 8,617 **shared** | crisprHAL's score | +0.067 | +0.060 | +0.054 |
| the 24,950 **crisprHAL-only** | crisprHAL's score | **+0.172** | **+0.150** | **+0.180** |

**Same rows, two labels: identical. Different rows, same label: 2.5× to 3.5×.**
That is the whole answer to the original objection, in a statistic with no
selector, no tree and no folds in it.

*What is different about those rows, as far as we can see.* They are not an
obviously different class of gene — 6.9% essential against 8.0%, 6.8 guides per
gene against 7.4. What differs is **dynamic range**: within the same curated
label, the added rows have **1.34×** the label spread (sd 3.46 against 2.58) and
**1.21×** the flank-GC spread (0.052 against 0.043). A correlation is
scale-invariant, so spread alone changes nothing — but spread in the *signal*
with the noise floor unchanged raises reliability, and attenuation is
multiplicative in exactly the way the family table is. Noshay published the
subset of the screen with the least room to measure anything in.

*What would separate "more dynamic range" from "different biology" properly:*
the per-guide read counts, which give a noise variance per row and hence a
reliability per subset. We do not have them, and they are in the same PeerJ
supplement nobody has read. Until then, "the added rows have more dynamic range,
and that is sufficient to explain a 2–2.5× attenuation difference" is as far as
this goes.

**So the premise of the objection was right.** If curation had only removed noise
from the label, the columns should not have changed behaviour — and the label
change is worth 0.004. What changed behaviour is that crisprHAL's release is a
**different and wider draw from the Guo screen**, four fifths of which Noshay
never published, and in which the effect this project is about is simply easier
to see.

*Consequence for the findings, and it is a favourable one.* The published matrix
**understated** the flanking-context effect, because it is the narrower,
lower-range subset. The curated figures are the ones that describe genome-wide
guide design; the published figures describe a 1,222-gene panel. Nothing in
Part 1 needs weakening, and Finding 3's effect size needs *raising* when it is
restated on this cohort — but the restatement has to carry this appendix with it,
because a reader comparing +0.080 to +0.164 across cohorts without it will think
the model got better.

## Appendix B3 — The family ablations on the curated cohort, and what they measure

Every Δρ in Appendix C was measured on the published 13,880-row matrix. The model
layer moved to crisprHAL's 33,567 curated guides and the family measurements did
not follow, so **all eleven families were re-run there**: same design, base
representation against base + one family, 5 seeds × 5 folds, selection inside
each training split, `python -m sgrna.curated_ablation --all`.

| family | columns added | published Δρ | **curated Δρ** | ratio |
|---|---:|---:|---:|---:|
| `a_flank` | 348 | +0.080 | **+0.164** | 2.1× |
| `d_supercoiling` | 26 | +0.045 | **+0.139** | 3.1× |
| `i_shape` | 152 | +0.036 | **+0.120** | 3.4× |
| `d_mechanics` | 30 | +0.020 | **+0.099** | 4.9× |
| `e_nucleoid` | 20 | +0.016 | **+0.072** | 4.6× |
| `g_transcription` | 19 | +0.015 | **+0.058** | 4.0× |
| `b_energy` | 10 | +0.007 | +0.019 | 2.5× |
| `c_folding` | 9 | +0.007 | +0.014 | 1.9× |
| `j_periodicity` | 24 | −0.001 | +0.011 | — |
| `f_methylation` | 17 | +0.003 | +0.008 | 2.3× |
| `h_offtarget` | 13 | +0.000 | +0.001 | 3.8× |

Baseline ρ 0.5445 ± 0.0010 on the curated cohort. The published column takes each
family from its own run (`ablation_main`, `ablation_grouped` for the three
positional families, `ablation_shape`, `ablation_jper`), so its baselines differ
slightly between rows — 0.5272 random-row, 0.5283 100 kb-grouped.

**The ranking transfers; the scale does not.** Rank correlation between the two
columns is **ρ = 0.97**, and every family gains, with a median inflation of
**3.3×**. That is the opposite of what the migration was expected to show. The
cohort change does not reorder which families matter — it multiplies all of them
by roughly the same factor.

*Correction, 13 October.* An earlier version of this table gave `i_shape`'s
published Δρ as +0.001 and called the curated +0.120 a reversal from a flat null.
**+0.001 was the wrong quantity**: it is `i_shape`'s increment *on top of family
A* (`a_flank+i_shape` 0.6078 against `a_flank` 0.6068), while every other row is
an increment over the base. Standalone, `i_shape` was **+0.036** on the published
matrix, third-largest then as it is now. The family is a near-duplicate of family
A, which is why its marginal value there is ~0 — a real and reported result, but
not a null, and not an entry that belonged in a column of base-relative gains.
The same substitution appears in Appendix B2's screen table and Appendix C, both
now corrected.

**It does not measure the selector.** The curated base is 6,169 sparse indicator
columns with none of the 63 hand-named summaries the published base carried, and
300 are selected. The obvious hypothesis was starvation. Tested directly on
`d_mechanics`:

| arm | ρ |
|---|---:|
| base, select 300 | 0.5443 |
| base + `d_mechanics`, select 300 | 0.6432 |
| base, **all 6,169 columns** | 0.5439 |
| base + `d_mechanics`, **all 6,199 columns** | 0.6432 |

**+0.0988 with selection, +0.0993 without.** The gain is not an artefact of
selecting 300 columns.

### What it does measure

The inflation tracks **what kind of column a family supplies**. Counting columns
that take more than ten distinct values on the cohort as dense and continuous
(`--shape-audit`, `results/ablation_curated_shape.csv`):

| family | columns | dense continuous | curated Δρ |
|---|---:|---:|---:|
| `a_flank` | 348 | 155 | +0.164 |
| `d_supercoiling` | 26 | 26 | +0.139 |
| `i_shape` | 152 | 152 | +0.120 |
| `d_mechanics` | 30 | 29 | +0.099 |
| `e_nucleoid` | 20 | 20 | +0.072 |
| `g_transcription` | 19 | 12 | +0.058 |
| `b_energy` | 10 | 9 | +0.019 |
| `c_folding` | 9 | 7 | +0.014 |
| `j_periodicity` | 24 | 24 | +0.011 |
| `f_methylation` | 17 | 2 | +0.008 |
| `h_offtarget` | 13 | 1 | +0.001 |

**ρ(dense continuous columns, Δρ) = 0.882, p = 0.0003, n = 11.** The published
base already contained dense summaries among its 63 hand-named columns, including
guide Tm; the curated base contains none, so families that restore them are paid
for it.

**Supply is not sufficient, which is the useful part.** `j_periodicity` supplies
24 dense continuous columns — as many as `d_supercoiling`'s 26 — and returns
+0.011 against +0.139. Column shape buys a family the *chance* to help; what it
measures decides whether it does.

**And supply is not the whole account.** Dense continuous columns and reach
beyond the 20-mer are themselves correlated — a family that measures something
about 2 kb of DNA naturally reports it as real numbers — so ρ = 0.882 is not
evidence that shape is the operative variable. The section below separates
them, and reach wins.

### What it measures, second answer: how far outside the 20-mer a family can see

The shape account above is a correlation, and it is confounded. Sorting the same
eleven families by **what DNA or data they are allowed to read** separates them
better than any property of their columns:

| reach | families | curated Δρ |
|---|---|---|
| the 20-mer and its PAM only | `b_energy`, `c_folding`, `d_mechanics` (22 of 30 cols) | **+0.011 to +0.019** |
| a short flank as well | `f_methylation` (±20 nt at the PAM) | +0.008 |
| the flanking DNA | `a_flank` (±1,000 nt), `i_shape`, `d_mechanics` (8 of 30) | **+0.097 to +0.164** |
| the rest of the genome, or external measurement | `d_supercoiling`, `e_nucleoid`, `g_transcription` | +0.058 to +0.139 |
| position on the chromosome | `j_periodicity`, `h_offtarget` | +0.001 to +0.011 |

**Nothing confined to the 20-mer exceeds +0.019, and nothing above +0.05 is
confined to it.** Access to information outside the guide is necessary for a
large gain here and not sufficient — `j_periodicity` and `h_offtarget` read the
whole chromosome and return nothing. That is a sharper statement than the column
shape correlation, it is the same conclusion Finding 3 reaches from the other
direction, and it survives the correction that produced it.

*What this appendix said until 13 October.* That `d_mechanics` adds **no new DNA
at all** and is therefore "the cleanest available demonstration that
representation matters independently of information" at +0.099. Eight of its
thirty columns are flanking-DNA thermodynamics, and those eight carry +0.097 of
the +0.099 (Finding 2). The representation effect is real at **+0.011 to +0.019**
across three guide-only arms; the claim was inflated nine-fold by a family whose
column list nobody had read.

**Family G is the one family carrying genuinely new non-sequence information**
— RegulonDB TSS positions and PRECISE-1K expression, neither computable from the
genome — and at +0.058 it is now sixth. On the published matrix it was +0.015 and
read as a near-null replication of Guo's reported absence of an expression
effect. That reading does not survive the cohort change, and the interaction
discipline this family was built with (Appendix C) has not been re-applied here:
**+0.058 is a family-level number, and no interaction term has been checked on
this cohort.** Until that is done it is not evidence for the transcription
mechanism, only evidence that the family is no longer flat.

### Getting the last three families onto this cohort

Three families were missing from the first curated run, each for a different
reason, and all three failures were silent:

* **`b_energy`** built a file containing 33,567 sgRNAIDs and **zero feature
  columns**, and reported success. The vendored CRISPRoff pipeline needs
  Biopython and its folding needs ViennaRNA; neither was installed in the main
  venv, and `b_energy.build` catches exceptions *per guide* and then drops the
  error column. Fed to the ablation it would have scored Δρ = 0.000 and read as a
  clean null. Both installed, it builds in 2 s, and 60% of guides fall inside
  Alkan's efficient-hybridisation window — against 64% on the published matrix,
  the check that the ΔG convention is still right.
* **`c_folding`** failed the same way for ViennaRNA alone, and recovered with it.
* **`g_transcription`** needed four index columns crisprHAL's CSVs do not carry:
  `ori_distance`, `replichore`, `leading_strand` and a per-gene **b-number** for
  the expression join. The reference gene table gives coordinates and gene names
  but no locus tags; PRECISE-1K's `gene_info.csv` gives locus tags keyed by gene
  name. So the host gene is assigned **by coordinate** on NC_000913.2 and the
  b-number by name: 30,203 of 33,567 guides land inside a gene, 29,097 get an
  expression row. `build_curated_features.augment()`.

`curated_ablation._block` now refuses a block with no populated feature column,
and `build_curated_features.run` refuses to write one, because the failure mode
is not a crash — it is a plausible-looking zero.

### Under gene-grouped cross-validation: the gains are not locus memorisation

Every number above is from random KFold, and on this cohort that needed
checking rather than assuming — gene identity explains **29%** of the curated
label against 16% of the published one, so there is nearly twice as much
available to memorise (Appendix A). All eleven families were therefore re-run
with **whole genes held out**: `curated_ablation --grouping gene`, the 30,203
guides that fall inside an annotated gene, 4,013 gene groups, 5 seeds × 5 folds,
baseline ρ 0.5584.

| family | reach | random-row Δρ | **gene-grouped Δρ** | retained |
|---|---|---:|---:|---:|
| `a_flank` | flanks | +0.164 | **+0.157** | 96% |
| `d_supercoiling` | external | +0.139 | **+0.131** | 94% |
| `i_shape` | flanks | +0.120 | **+0.112** | 94% |
| `d_mechanics` | guide + flanks | +0.099 | **+0.092** | 92% |
| `e_nucleoid` | external | +0.072 | **+0.063** | 88% |
| `g_transcription` | external | +0.058 | **+0.046** | 79% |
| `b_energy` | guide | +0.019 | +0.017 | 91% |
| `c_folding` | guide | +0.014 | +0.014 | 97% |
| `j_periodicity` | position | +0.011 | +0.007 | 64% |
| `f_methylation` | guide | +0.008 | +0.007 | 93% |
| `h_offtarget` | genome | +0.001 | +0.000 | 23% |

**The guide-only families calibrate the control, which is what makes the rest of
the column readable.** `b_energy`, `c_folding` and `f_methylation` are functions
of the guide, so grouping *cannot* invalidate them — a sequence feature does not
become less true when the split changes. They nevertheless retain only **94% in
aggregate**, and that 6% is the **grouping tax**: holding out whole genes is a
harder task for reasons that have nothing to do with memorisation (less locus
diversity in training, and 4,013 groups split five ways is a coarser partition
than 30,203 rows split five ways). Without that calibration a family retaining
94% would read as having lost 6% to memorisation, when the right reading is that
it lost nothing.

Against the 94% benchmark:

* **`a_flank` (96%), `d_supercoiling` (94%) and `i_shape` (94%) lose nothing at
  all.** The three largest effects in the table survive gene-grouping intact.
* **`e_nucleoid` (88%) and `g_transcription` (79%)** carry a real locus
  component, 6 and 15 percentage points beyond the tax. Both read external
  tracks indexed by position, so this is the expected direction and the expected
  families.
* **`j_periodicity` (64%) and `h_offtarget` (23%)** lose most of their gain, but
  their gains are +0.011 and +0.001. Large relative losses of nothing.

**This is a smaller memorisation component than the published cohort showed**,
where grouping cost `e_nucleoid` 42% of its gain and `g_transcription` 36%. The
apparent paradox — twice the between-gene variance, half the memorisation — is
resolved by what else changed: the curated cohort has **7.5 guides per gene
against 11.3**. Between-gene variance sets how much a locus-memorising model
*could* win; guides per gene sets how well it can *learn* each locus's mean. The
two moved in opposite directions, and the measurement says the second dominated.
That is not something that could have been reasoned out from the variance share
alone, which is the argument for running the control rather than arguing about
it.

*Caveat on levels.* The grouped arms run on 30,203 guides, not 33,567, because
3,364 fall outside every annotated gene and were dropped rather than given
singleton groups. Its baseline is accordingly different (0.5584 against 0.5445),
so the Δρ columns compare and the ρ columns do not.

### How to read these numbers, and how not to

**They are not comparable to the published Δρ column as levels, and the reason is
now known.** The two cohorts have different baselines (0.544 against 0.527),
different labels and different base representations — but none of those is what
tripled the table. **The rows are** (Appendix B2a): the label is worth 0.004, the
row count nothing, the weaker base 0.013, and the remaining ~0.070 of family A's
+0.084 gap belongs to the 24,950 guides crisprHAL publishes and Noshay did not,
in which a single flank-GC column's marginal correlation with activity is 2.5×
higher. The *ordering* transfers (ρ = 0.97); the magnitudes describe a different
and wider population.

**They are not clean estimates of each family's biological contribution.** A
family that supplies dense summaries is rewarded for its shape as well as its
content on this base. Separating the two requires adding the portable hand-named
summaries to the curated base and re-measuring, which has not been done.

**They are single-family increments over a common base, nothing more.** No joint
arm has been run on this cohort, and the published cohort's joint arms are the
reason to expect heavy overlap: `i_shape` on top of family A was worth +0.001
there, and the three positional families collapsed into one variable. Summing
this column would give +0.70 ρ of improvement, which is not a real quantity.

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

### Ours — eleven families, four distinct ideas

Δρ below is on the **published** 13,880-row matrix, which is what these were
built against. All eleven have since been re-measured on the curated cohort,
where the ordering is nearly identical and every figure is about three times
larger — Appendix B3 has that table and the reason.

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
| `i_shape` | flank bendability / deformability | published dinucleotide scales | +0.036 (+0.001 on top of `a_flank`) |
| `j_periodicity` | GC skew, helical-repeat periodicity | reference genome | −0.001 |

Groups 1 (`b`,`c`,`d_mechanics`,`f`) are redundant by construction (Appendix B2); group 2 (`a`) is
the one that worked; group 3 (`d_supercoiling`, `e`, `g`) collapse into one
positional variable; group 4 (`h`) needs the rest of the genome.

### Teammates' — on the published 13,880-row matrix, quoted in R²

Not directly comparable with the Δρ column above; recorded so the paper does not
under-credit them.

| set | who | result |
|---|---|---|
| **gene essentiality** | Jacky | **+0.0037 R²** over 0.2927, **selected in 5/5 folds** — the only non-QCT idea on that matrix with a consistent gain, and it is not a function of the 20-mer |
| **orientation controls** | Jacky | closes Part 4 item 3 and **rewrites Finding 6**: curated RegulonDB TSS replaces nearest gene as the orientation variable (Δ 0.051 [0.020, 0.082]), and the nearest-gene version we had been quoting is shown to be largely a distance/GC cohort confound (Δ 0.007, P = 0.34 after matching). Block bootstrap over 47 genomic blocks, promoter/RBS separated, operon compared |
| seed non-additive QCT | Joshua | ~+0.005 R²; absolute-difference forms carry more SHAP than signed (1.09 against 0.92) |
| log-ratio QCT forms | Joshua | ~+0.005 R², best seed 0.3015 |
| regional QCT summaries | Joshua | +0.0013 R², against a permuted control at 0.2857 |
| PAM-weighted, profile-shape, coupling, HOMO–LUMO asymmetry | Joshua | −0.0010 to +0.0006 — null |

The non-additive families are **independent evidence for Finding 7**: they gain
from exactly the higher-order structure the k-mer ladder found worth +0.0035 ρ
once the selector was removed.

## Appendix D — Sources (APA 7th edition)

Browne, T. S., Edgell, D. R., & Gloor, G. B. (2026). Better data for better
predictions: Data curation improves deep learning for sgRNA/Cas9 prediction.
*PeerJ*, *14*, e20706. https://doi.org/10.7717/peerj.20706
— the state of the art; code and curated label re-run here as the baseline.

Cui, L., Vigouroux, A., Rousset, F., Varet, H., Khanna, V., & Bikard, D. (2018).
A CRISPRi screen in *E. coli* reveals sequence-specific toxicity of dCas9.
*Nature Communications*, *9*, 1912. https://doi.org/10.1038/s41467-018-04209-5
— the dCas9 CRISPRi screen used as the final untouched test (Finding 5); its two
measurement arms also set the ceiling range quoted in Appendix B.

Guo, J., Wang, T., Guan, C., Liu, B., Luo, C., Xie, Z., Zhang, C., & Xing, X.
(2018). Improved sgRNA design in bacteria via genome-wide activity profiling.
*Nucleic Acids Research*, *46*(14), 7052–7069. https://doi.org/10.1093/nar/gky572
— the screen behind the label; Figure 2b and 2c agreement statistics for the
published label's ceiling; the intergenic sub-library. Its per-replicate counts,
as re-released by Browne et al., give the curated label's ceiling (Finding 11).

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

Twenty-nine claims have been withdrawn and thirteen bugs found. They are not listed
here, so that this document reads as a statement rather than a diary; they are in
`docs/FINDINGS_LOG.md` in date order and in `local/MISCONCEPTIONS.md`, outside
the repo, with the cause of each.

Three of the eleven bugs share one shape and are worth naming as a class:
**a computation that fails and reports success.** `b_energy` wrote a feature
block with zero feature columns because its builder catches import errors per
guide; a selector control compared 300 columns against 300 because
`n_features=None` resolves to `config.N_FEATURES`; and a wide-window crisprHAL
run scored an untrained network because `train()` returns `None` identically on
success and failure. None raised. Each produced a number of exactly the kind
expected, and the first two would have entered the report as clean null
results.

The pattern is worth one line, because it is the most transferable thing here:
**the largest single category is an outsider's question**, and in every one of
those cases the data needed to catch the error was already on disk. The
bottleneck was never measurement — it was that nobody had questioned a number
repeated often enough to feel settled.
