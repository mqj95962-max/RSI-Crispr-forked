# RSI09 findings log

Running record of what we found, when, and what it means — kept so the paper
can be written from evidence rather than memory. Newest entries at the bottom.

Companion documents, all current:

| file | what it is for |
|---|---|
| [`PROGRESS_REPORT.md`](PROGRESS_REPORT.md) | the whole project in plain language, with a glossary — **start here** |
| [`../results/RESULTS.md`](../results/RESULTS.md) | every number and what it means |
| ~~`NOVELTY.md`~~ | merged into `PROGRESS_REPORT.md` on 2026-10-02; the file is now a pointer |
| [`../lit_review/beyond_QCT_literature_review.md`](../lit_review/beyond_QCT_literature_review.md) | why each feature family was tried |
| this file | the chronological record, newest at the bottom |

(`results/INTERPRETATION.md` was merged into `RESULTS.md` on 2026-09-13 and has
since been removed — everything it held is in `RESULTS.md` §1 and §3–8.)

## Superseded claims — read this before quoting an old entry

Entries are kept as written, so earlier ones can be wrong. The corrections that
matter:

| earlier claim | where | corrected by |
|---|---|---|
| "label curation is worth +0.003, i.e. nothing" | 2026-09-13 | **2026-09-15** — true for the baseline, false for family A, which gains +0.164 on curated rows against +0.080 on published ones |
| "the local ±10 nt is two thirds of the flank gain" | 2026-09-14 | **2026-09-15** — true on the noisy label; on the curated label the long-range windows are the larger half (0.660 vs 0.618) |
| "we are ~0.054 behind crisprHAL 2" | 2026-09-14 | **2026-09-15** — that compared different row sets; on identical rows it is parity (0.707 vs 0.697) |
| "parity, but against their *published* figure rather than a re-run" | 2026-09-15 | **2026-10-02** — their model re-run on our folds scores 0.6971 ± 0.0067; paired, ours is ahead by +0.0107 in 5/5 folds |
| "the abundance effect is not GC bias; by elimination it is genuine local chromosome state" | 2026-09-13 | **2026-10-02** — GC was tested against the *label* (+0.03 to +0.06) instead of against the read-density track (up to −0.70). GC + 25-mer uniqueness reproduce the whole gain from the genome alone, and add nothing on top of family A |
| "DNA abundance is the single largest unexplained effect left" | 2026-09-15 (Part 10) | **2026-10-02** — decomposes into replication timing (no rank gain), GC/mappability (already in family A), and ≈+0.007 R² that is actually new |
| "the flank effect transfers to another organism; the *E. coli*-only caveat is retired" | 2026-10-02 (evening) | **2026-10-02 (night)** — the cross-*enzyme* half holds under `arc5`, but the only other-organism screen covers 4.3% of one chromosome and cannot test the long-range gradient at all |
| "LightGBM fits in 0.3 s, ~25,000× faster than crisprHAL" | September onward | **2026-10-03** — the 0.3 s is real (`model_comparison.csv`, 0.291 s) but is the *fit alone*, excluding feature selection at ~13× that. End to end: ~35 s/fold, ~3 min for five, against their 105 min — **~30–36×**, at comparable memory (3.55 vs 4.55 GB). Timings vary 13–116 s on this host because it swaps; see `results/timing.csv` |
| "we are ahead of crisprHAL 2 by +0.0107, a small but consistent advantage" | 2026-10-02 | **2026-10-03 (later)** — tuning our own model alone is worth **+0.0103** (`tuning.csv`), so the margin sits inside the tuning effect. The claim reverts to **parity**; the tuned 0.7181 may be quoted only as tuned-vs-untuned |
| "√0.810 ≈ 0.90 is a *conservative* ceiling, since the enzymes differ" | September onward | **2026-10-03 (later)** — the two screens share their **guide library** (100% identical sequences) and eSpCas9 is WT plus three point mutations, so 0.810 is the best case for agreement. **0.90 is an optimistic upper bound** |
| "the permutation floor is −0.0018 to +0.0014" | September onward | **2026-10-03 (later)** — that is `a_flank`'s floor, quoted for all nine families. Measured per family and paired fold-by-fold, **`h_offtarget` is below its own floor** (0.8×) and **`f_methylation` is marginal** (3.0×) |
| "windowed composition beats a CNN four times over, +0.164 against +0.019" | 2026-09-15 | **2026-10-03 (later)** — different datasets. Like for like on the original 13,880 rows it is **+0.080 against +0.019**, still 4.2×; `RESULTS.md` §13 had this right all along |

---

## 2026-09-08 — the matrix contains the sequences

**Finding.** The published feature matrix never stores a guide sequence, but
`p{i}monomer.No.electronsraw` takes exactly four values across all 13,880
guides — 42, 48, 50, 56 — which are the **valence-electron counts** of
cytosine, thymine, adenine and guanine. The 20 nt protospacer therefore reads
straight back out of the matrix, one position at a time.

**Verification.** 13,879 of 13,880 guides decoded (one row has a missing
descriptor); every one found in NC_000913.2 with an **NGG PAM immediately 3′**;
13,877 single-copy. Cumulative GC skew puts the origin at 3,923,620 against an
annotated *oriC* near 3,923,800.

**Consequence.** Five of the eight planned feature families became possible.

## 2026-09-08 — the quantum tensors are exactly recoverable

**Finding.** Every QCT column is a pure function of the k-mer at its position,
so each inverts into a lookup table. All 4 monomers, 16 dimers, 64 trimers and
**256 tetramers** appear in the 13,880 guides with **zero conflicts**.

**Consequence.** Noshay et al.'s quantum parameterisation is recovered
*exactly*, not approximated, and can be applied to sequence the paper never
encoded — the PAM, the bases after it, the flanking DNA.

## 2026-09-12 — first ablation, and a leakage trap

**Finding.** Positional features can identify a locus, and the library puts ~20
guides in every gene, so plain KFold rewards the model for memorising "guides
around here score about this much".

**Action.** Added grouped cross-validation: whole genes, 100 kb blocks, and
five contiguous chromosome arcs. **Any positional family must be reported
grouped.** Gene-level grouping is not enough — neighbouring genes share
supercoiling domains, so 100 kb blocks are the routine setting and contiguous
arcs the publication setting.

## 2026-09-12 — the supercoiling result is not supercoiling

> ⚠️ **Partly superseded.** The headline stands — the effect is read density, not torsion — but the closing attribution does not. GC bias was ruled out here by testing GC against the *label*; tested against the read-density track it explains most of it. See **2026-10-02 (later)**, and `RESULTS.md` §3, and the superseded-claims table at the top of this file. Entry kept as written.

**Finding.** `d_supercoiling` gives +0.047 R² under 100 kb-blocked CV, but the
raw GapR tracks correlate −0.83 to −0.97 with distance from *oriC*, and the
**untagged no-antibody control predicts cutting as well as the ChIP does**.

**Dissection** (3 seeds, 100 kb-grouped, baseline 0.2924):

| given to the model | cols | ΔR² |
|---|---:|---:|
| whole family | 26 | +0.0465 |
| raw read density only, no ratios | 16 | **+0.0453** |
| untagged control alone | 4 | +0.0091 |
| ratios only — the supercoiling-specific part | 10 | **+0.0040** |
| analytic *oriC*-distance proxy | 4 | +0.0127 |

**Conclusion.** 97% of the effect is raw sequencing read density. It is *not*
the smooth replication gradient (the analytic proxy recovers a quarter of it)
and *not* GC bias (local GC correlates +0.03 with cut score). It survives
holding out whole 500 kb blocks and whole contiguous arcs. **Do not write
"supercoiling predicts sgRNA efficiency."** Write "a measured profile of local
chromosomal DNA abundance does", and say the mechanism is open.

**Action.** Columns renamed `eng.sc.abund.*` / `eng.sc.torsion.*`.

## 2026-09-12 — three positional families are one variable

**Finding.** `d_supercoiling`, `e_nucleoid` and `g_transcription` have pairwise
|ρ| of 0.77–0.96 between their leading features — Hi-C contacts and ChIP
coverage are both read counts, so both inherit the copy-number gradient.
Individually they give +0.047 / +0.017 / +0.016; **stacked, +0.051**.

**Conclusion.** Report them as one result. Two thirds of the apparent combined
evidence is double-counting.

## 2026-09-12 — the thermodynamic families are GC content

**Finding.** `d_mechanics` and `b_energy` correlate 0.90–0.96 with
`sgRNA.gcsgRNA.raw`, a column the matrix always had. Their gains are a
better-*shaped* GC variable, not new information: `d_mechanics` wins (+0.020 vs
+0.007) because it says *where* the duplex is weak rather than how GC-rich it
is overall.

**Mechanism.** GC-rich protospacers cut worse (ρ −0.20); a stronger RNA:DNA
hybrid goes with *lower* activity (ρ −0.21). That is **strand-invasion
limited**, not hybridisation limited — the duplex has to open first.

## 2026-09-12 — two replications and one transfer failure

- **Alkan's N+1 penalty replicates in bacteria.** A G immediately 3′ of the NGG
  is the single strongest column in family A (ρ −0.108), matching the ~12.6%
  cost reported in human cells.
- **Moreb & Lynch's folding thresholds replicate.** 4.0% of guides fall below
  −5 kcal/mol spacer MFE and 8.2% below −15 kcal/mol spacer:scaffold duplex
  stability, both associated with lower activity, in a dataset they never used.
- **Alkan's ΔG efficiency window does *not* transfer.** Guides inside the human-
  derived −64.5 to −47.1 kcal/mol optimum are, if anything, *less* active in
  *E. coli* (ρ −0.133). Only visible after the window bug was fixed.

## 2026-09-12 — the flank wants the opposite of the protospacer

**Finding.** Guide GC correlates −0.20 with activity; flanking GC correlates
**+0.05**. Opposite signs, two length scales.

**Follow-up 2026-09-13.** Widening the windows to 1 kb located the boundary:
the flank effect peaks at **250–500 nt** (ρ +0.051 up, +0.039 down) and decays
by 1 kb (+0.032 / +0.022). **This question is now closed — do not widen
further.**

## 2026-09-13 — three code fixes

1. **ΔG window bug.** `hyb_offset` / `hyb_in_window` used the raw hybridisation
   term where Alkan's window refers to the position-weighted one. Before: 0% of
   guides inside the window, indicator constant. After: 63.7%. Gain unchanged
   (+0.0071), but it exposed the transfer failure above.
2. **Family D2 renamed** to `abund` / `torsion`.
3. **Family A widened and pruned.** The seventeen tensor summaries per window
   were near-copies of flank GC (ρ 0.998); replaced by four spread series plus
   explicit composition, windows extended to 1 kb. **348 columns instead of
   408, four times the reach, and a larger gain (+0.0867 vs +0.0834).** Fewer,
   better-chosen columns beat more redundant ones.

## 2026-09-13 — 5-seed results, and the combined model

Family A gives **exactly +0.0867 R² under both random-row and contiguous-arc
CV** — a sequence family should be indifferent to how the chromosome is split,
and it is.

Combined (`a_flank` + `d_supercoiling` + `d_mechanics`, arc CV): **+0.1050 R²**
against a sum of ~+0.15 alone, so 70% additive. But in Spearman the combination
adds only **+0.004** over family A by itself.

**Conclusion.** Chromosomal position improves the *calibration* of the
prediction, not its *ranking* — and ranking is what guide selection uses. **For
picking guides, sequence is nearly the whole story.**

## 2026-09-13 — three "obvious" improvements, all tested, all dead

> ⚠️ **Partly superseded.** The label-curation line (+0.003, "i.e. nothing") is true for the baseline only; family A gains +0.164 on curated rows. See **2026-09-15**, and the superseded-claims table at the top of this file. Entry kept as written.

Before spending effort on the usual levers, each was measured.

**Label curation: no effect.** crisprHAL's read-count-filtered scores cover
8,617 of our 13,880 guides and correlate +0.945 with the published `cut.score`.
On those *same rows*:

| label | baseline ρ | + family A ρ |
|---|---:|---:|
| published `cut.score` | 0.5387 | 0.6279 |
| crisprHAL curated | 0.5370 | **0.6305** |

A difference of +0.003, inside the noise. **The value of "curation" is dropping
the bad rows, not relabelling the good ones** — the 8,617-row subset scores
ρ 0.628 against 0.607 on all 13,880, so the 5,263 guides crisprHAL discards are
measurement noise that caps the model.

**Feature cap: not binding.** Raising the top-300 selector cap changes nothing.

| n_features | family A ρ |
|---:|---:|
| 300 | 0.6068 |
| 600 | 0.6079 |
| 1200 | 0.6082 |

**More rows: saturates at ~20,000.** See the next entry.

## 2026-09-13 — the 13,880-row cap is lifted

**Finding.** 5,853 of the 5,887 opaque `V####` columns are (position, k-mer)
one-hot indicators. Identified by matching bit patterns across 13,880 guides:
**zero ambiguous, 100% verification on 1.17 million rebuilt values.**

With the QCT tables, that is **6,169 of 6,232 columns — 99.0% of the published
matrix — regenerable from a 20 nt protospacer alone**, confirmed at 100%
agreement over 6,169 columns × 500 guides.

*Not* reproducible: the ~31 hand-named columns (`AAsgRNA.raw`,
`sgRNA.gcsgRNA.raw`, `PAM.C0`, …). They are not pure functions of the
protospacer — base counts disagree with a direct count by up to 13,
`sgRNA.temp` takes exactly 14 values spaced 2.05 apart, PAM columns take
fractions like 0.25. Discretised or aggregated somewhere undocumented. Omitted
rather than guessed.

**Consequence.** Any bacterial Cas9 screen can now be featurised in the
published representation. The curated Guo release has 33,567 guides, 24,950 of
them new.

**Learning curve** (held-out 20%, same test set at every size, 2 seeds):

| training rows | Spearman |
|---:|---:|
| 4,000 | 0.488 |
| 8,000 | 0.520 |
| 13,880 | 0.535 |
| 20,000 | 0.544 |
| 26,000 | **0.545** |

**Doubling the data buys +0.010 Spearman and then stops.** The curve is flat
between 20k and 26k.

---

## Where that leaves the project

Four of the five levers anyone would reach for have now been measured and
found empty: more rows (+0.010, saturating), a cleaner label (0.000), more
model capacity (+0.001), and wider flanks (saturated at 250–500 nt). The one
that worked is **sequence context outside the 20-mer, +0.080 Spearman**, and it
is already banked.

So the remaining headroom is not data volume, not the label, and not capacity.
It is one of:

1. **Model class.** crisprHAL's CNN/BiGRU reaches ρ 0.63–0.68 on this data
   where gradient boosting on 6,580 engineered columns reaches 0.61. That gap
   is about architecture, not features, and it is now testable on equal footing
   because we can featurise the same rows.
2. **Features nobody has tried.** The flank result says local sequence context
   matters over hundreds of bases; nothing in the current set describes that
   context structurally rather than compositionally.
3. **Irreducible measurement noise.** The curated-subset result suggests a
   meaningful fraction of the screen is noise, and the learning curve suggests
   we are close to what this assay can support.

Distinguishing (3) from (1) and (2) is the single most useful next experiment:
train on the 26,000-row curated set with family A features and see whether the
plateau moves. If it does not, the ceiling is the assay, and the paper's
contribution is mechanistic — which, given the replications and the transfer
failure above, is the stronger contribution anyway.

---

## 2026-09-13 (evening) — measuring the two axes, and model class

Written up in full as `results/RESULTS.md` §11–12. `results/INTERPRETATION.md`
was merged into `RESULTS.md` on this date and is now a pointer stub.

### New code

`src/sgrna/evaluate.py` — metrics that were previously asserted rather than
measured:

- **Predictive power:** R², Spearman, top-decile precision, expected pick
  percentile (draw 10 guides, take the model's favourite, record its true
  percentile — 20,000 draws), calibration slope.
- **Interpretability:** Kuncheva selection stability, importance concentration
  (features for 50%/90%, Gini, effective count), method agreement (gain vs
  permutation importance), faithfulness (drop top-20 vs drop 20 random),
  direction consistency.

```bash
python -m sgrna.evaluate --what prediction --models xgboost lightgbm ridge
python -m sgrna.evaluate --what interpretability --models lightgbm random_forest
```

### Finding 1 — CatBoost has the best top-decile precision while sitting third on R²

Ranking models by R² picks the wrong model for guide selection. Of the five
predictive metrics, **expected pick percentile** and **top-decile precision**
are the ones that correspond to the experiment a bench scientist runs, and they
do not agree with R² on the ordering.

### Finding 2 — model choice spans 0.09 R² but only 1.8 percentile points on the guide you pick

3 seeds × 5 folds, identical folds and identical selected features (XGBoost
gain, top 300), only the predictor swapped (`results/model_comparison.csv`):
LightGBM 0.3824 / ρ 0.6086, XGBoost 0.3812 / 0.6076, CatBoost 0.3615 / 0.6010,
Ridge 0.3406 / 0.5770, elastic net 0.3401, MLP 0.3387, extra trees 0.3021,
random forest 0.2915 / 0.5497.

Two sub-findings:

- **Boosting wins, bagging loses** by 0.05–0.06 Spearman, despite both being
  tree ensembles.
- **Ridge gets within 0.03 Spearman of boosting**, so most of the signal is
  additive. That is a statement about the biology: the determinants of cutting
  efficiency behave largely independently, and everything boosting's
  interactions buy is worth ~0.03 ρ.

### Finding 3 — XGBoost's two importance methods disagree (ρ −0.02)

Each model selecting with its own importances, seed 41, 3 folds
(`results/interpretability.csv`):

| model | ρ | stability | method agreement | faithfulness | features for 50% |
|---|---:|---:|---:|---:|---:|
| LightGBM | 0.609 | 0.72 | +0.44 | +0.008 | 151 |
| XGBoost | 0.608 | 0.49 | −0.02 | +0.003 | 330 |
| random forest | 0.550 | 0.91 | +0.30 | +0.022 | 175 |
| Ridge | 0.577 | 0.45 | +0.28 | −0.012 | 1,371 |

Split gain and permutation importance rank XGBoost's top 40 features
essentially independently. **Any mechanistic claim read off an XGBoost gain
plot is one plotting choice away from a different story** — which matters more
here than usual, because the project's framing is explainable AI.

Ridge's faithfulness is *negative*: dropping its top features hurts less than
dropping random ones. Coefficient magnitude on 6,580 correlated columns is not
an explanation.

Random forest is the worst predictor (ρ 0.550) and the most trustworthy
explainer (stability 0.91, faithfulness 0.022) — the cleanest demonstration in
this project that the two axes are separate.

### Decisions taken

1. **Champion switches from XGBoost to LightGBM.** Same accuracy (+0.001 ρ),
   1.5× more stable selection, importance methods that agree, half as many
   features carrying the story. The frozen XGBoost numbers stay as the
   historical baseline so the ablation record remains comparable.
2. **Every mechanistic claim gets confirmed under random forest** before it
   goes in the paper.
3. **Ridge is reported as a reference row** — "a linear model gets within
   0.03" is a finding, and it costs 0.02 s.
4. **No single importance method is ever quoted alone.** Report gain,
   permutation, and the correlation between them.

---

## 2026-09-14 — why the new libraries didn't help, and sixteen model classes

Full write-up in `results/RESULTS.md` §12–13. New module: `src/sgrna/diagnose.py`
(`python -m sgrna.diagnose --what all`) and `src/sgrna/seqnet.py`.

### The question

Eight feature families, each with a mechanism and a dataset behind it, and six
moved Spearman by less than 0.01. Is something broken?

### Finding 1 — the published matrix is a lossless encoding of the protospacer

Every one of the 20 positions carries at least three of its four mononucleotide
indicators among the `V####` columns (14 positions carry all four), so the
fourth is one minus the others. The 20-mer is exactly recoverable from the
matrix.

**Consequence: any feature that is a deterministic function of the 20 nt guide
adds zero information.** It can only re-express what is already there.

### Finding 2 — the gain tracks "outside the 20-mer", not "good biology"

Out-of-fold R² of predicting each new column by *linear* regression on
position-specific mono- and dinucleotide indicators (`results/redundancy.csv`):

| family | median R² from the 20-mer | share > 0.9 | its Δρ |
|---|---:|---:|---:|
| `b_energy` | 0.984 | 70% | +0.007 |
| `d_mechanics` | 0.845 | 50% | +0.020 |
| `c_folding` | 0.297 | 0% | +0.007 |
| `f_methylation` | 0.141 | 0% | +0.004 |
| `a_flank` | −0.012 | 0% | +0.080 |
| `d_supercoiling` | −0.013 | 0% | +0.045 |
| `e_nucleoid` | −0.016 | 0% | +0.016 |
| `g_transcription` | −0.016 | 0% | +0.015 |
| `h_offtarget` | −0.022 | 0% | +0.000 |

Nearest-neighbour thermodynamics is by construction a weighted dinucleotide
count, and CRISPRoff's ΔG is dominated by the same term — so importing them was
importing the matrix back into itself. **Every family with R² ≈ 0 delivered;
every family with high R² did not.** This is now the screening test to run
before building any future feature.

### Finding 3 — the model is out of material, not underfitting

Champion's out-of-fold residuals (ρ 0.606) against every column
(`results/headroom.csv`): **zero of the 6,480 columns the model was given has
|ρ| above 0.10 with its own residual; the maximum is 0.035.** The only features
with anything left are the held-back positional ones (`d_supercoiling` 0.154,
`e_nucleoid` 0.151, `g_transcription` 0.146) — and §4 already showed those are
one variable.

### Finding 4 — the label is not the ceiling

WT-SpCas9 and eSpCas9 screens of the same library share 33,567 protospacers and
agree at **ρ 0.810** (`results/ceiling.json`). By the attenuation argument the
ceiling against a single observed cut score is √0.810 ≈ **0.90** — conservative,
since the enzymes differ. Also: 85% of cut-score variance is within-gene, so the
label measures guide quality rather than gene essentiality; and published
`cut.score` vs the crisprHAL re-derivation is ρ 0.945.

### Finding 5 — a CNN on raw sequence ties on the guide and loses on the flanks

Conv–conv–BiGRU, same rows and folds (`results/seqnet.csv`, `src/sgrna/seqnet.py`):

| model | input | R² | ρ |
|---|---|---:|---:|
| CNN | 20 nt + PAM | 0.257 | 0.498 |
| XGBoost | 6,232 published columns | 0.294 | 0.527 |
| CNN | + ±100 nt genome | 0.272 | 0.516 |
| LightGBM | published + `a_flank` | 0.382 | 0.609 |

Raw context buys the CNN +0.019; engineered windowed composition buys boosting
+0.080. The flank effect is a long-range compositional average with no motif, so
a 5 nt convolution with pooling is the wrong tool. (A first attempt with one
mean-pooled encoder over the whole window scored ρ 0.11 — the guide is 10% of
the positions and got drowned; fixed with separate guide and context branches.)

### Finding 6 — sixteen model classes span 0.116 ρ and 3.3 percentile points

Eight new predictors added to `evaluate.py` (`MODELS_EXTRA`): hist gradient
boosting, DART, Huber-loss LightGBM, SVR-RBF, Nyström+ridge, k-NN, PLS, and a
stacked blend. Full table in `results/model_comparison.csv`.

- **Stacked blend is the new best row** — ρ 0.6108, +0.002 over LightGBM at 48×
  the cost. Its fitted weights: LightGBM 0.775, Ridge 0.324, **random forest
  −0.003**. The forest's errors are not complementary; the ensemble is really
  two members, one of them linear.
- **k-NN 0.495** — the signal is not local, consistent with a largely additive
  response.
- **Huber-loss LightGBM: R² 0.192 but ρ 0.568** — the robust loss destroys
  calibration while preserving rank. A clean argument for reporting both.

### Finding 7 — the combination does work; the ablations understate it

All nine families together with LightGBM: **ρ 0.641, 73.4th pick percentile**
(seed 41, 5 folds, random-row CV, `results/best_current_model.csv`), against the
published baseline's 0.527 and ~70th. **+0.114 Spearman**, distributed across
families rather than sitting in one. (Random-row CV flatters the positional
families; the honest arc figure for A+D2+D1 is ρ 0.615.)

### Where that leaves the project

The remaining headroom (≈0.61 → 0.90) is **not** in the current features
(residuals exhausted), **not** in the model (sixteen classes), **not** in the
guide's representation (a CNN ties), and **not** in the label (two screens agree
at 0.810). It is in features outside the 20-mer that nobody has built.

Priorities now: describe the flanks *structurally* (curvature, bendability,
duplex breathing — all computable from the genome); identify what the
read-density signal from §3 actually is, since it is the largest residual
correlation left; and screen every future dataset with the redundancy test
before spending effort on it.

---

## 2026-09-14 (later) — positioning against the published state of the art

> ⚠️ **Partly superseded.** The "~0.054 behind crisprHAL 2" bar compared different row sets. See **2026-09-15**, then **2026-10-02** for the re-run on identical folds, and the superseded-claims table at the top of this file. Entry kept as written.

Written up as `docs/NOVELTY.md`. New result: `results/flank_sides.csv`.

### The bar

| model | year | data | 5CV ρ |
|---|---|---|---:|
| crisprHAL 2 (`WT`) | 2026 | *E. coli* SpCas9, 33,495 curated | **0.697** |
| crisprHAL 1 | 2023 | *E. coli* SpCas9, 40,308 | 0.627 |
| Guo et al. | 2018 | uncurated | 0.542 |
| **Noshay et al. — the paper we extend** | 2023 | 40,468 guides, 6,232 QCT features, iRF | R² **0.249**, Pearson **0.502** |
| this project, all nine families + LightGBM | — | 13,880 | 0.641 |

**We are ~0.054 behind crisprHAL 2 and should not claim otherwise.** What we can
claim on prediction is narrower and solid: on the Noshay feature set, R² 0.249 →
0.38 and Pearson 0.502 → ~0.62.

Eukaryotic numbers (DeepCC9 2026, ρ 0.861 on 55k human sgRNAs) are **not
comparable** — different readout, and crisprHAL showed eukaryotic models
transfer to bacteria at ρ −0.2 to 0.1.

### Finding — the flank gain splits into local and long-range, additively

`results/flank_sides.csv` (LightGBM, seed 41, 5 folds, arms comparable within
the run):

| added to baseline | Δρ |
|---|---:|
| upstream only | +0.019 |
| downstream only | +0.065 |
| ±10 nt immediate context | +0.049 |
| windowed composition 50–1000 nt | +0.026 |
| everything | +0.075 |

Downstream beats upstream 3.4:1 — consistent with crisprHAL 1's +8 nt
downstream result — but **upstream is independently positive here**, where
crisprHAL 1 reported that upstream sequence "immediately decreased predictive
ability" in a CNN. Two thirds of the gain sits in the ±10 nt that published
bacterial tools already read; one third is in the long windows.

> ⚠️ **Superseded on the noisy label only.** That two-thirds/one-third split
> reverses on the curated label, where the long windows are the larger half
> (0.660 vs 0.618). See **2026-09-15**.

Caveat found in the literature check: **crisprHAL 2's *E. coli* SpCas9 model
already uses 189 nt upstream + 166 nt downstream**, so long-range context is not
ours to claim as a discovery. What appears to be ours is its *shape* — a CNN on
the same raw bases gains +0.019 total against +0.075 for windowed composition,
so the long-range signal is a smooth compositional gradient with no motif.

### What is original vs imported

Imported and openly so: `b_energy` (CRISPRoff), `c_folding` (ViennaRNA),
`f_methylation` (regex), `h_offtarget`, and the GapR-seq / Hi-C / RegulonDB
datasets. Five of six were measured against a control and found empty.

Original: (1) reverse-engineering the published matrix — protospacer decoded
from valence-electron counts, QCT tables recovered exactly, 5,853 `V####`
columns identified, 99% of 6,232 columns regenerable from any 20-mer;
(2) the lossless-encoding result and the redundancy screen that follows from it,
which generalises to any sequence model with hand-added thermodynamic features;
(3) the untagged-control result reinterpreting `d_supercoiling` as read density;
(4) interpretability measured rather than asserted, including that the source
paper's own importance method is internally inconsistent (gain vs permutation,
ρ −0.02); (5) the reproducibility ceiling (two screens agree at ρ 0.810 → ~0.90);
(6) the flank decomposition above.

### Framing decision

The paper is **"what determines sgRNA efficiency in *E. coli*, and how to tell
whether a proposed determinant can possibly help"** — not "a better predictor".
The results support the first and not the second.

**Highest-value next experiment:** featurise the 33,495-row curated crisprHAL
set through `sgrna.featurise` (possible only because of item 1), add family A,
train LightGBM, and compare to crisprHAL 2 on *identical rows*. Either the gap
closes or it quantifies what the CNN architecture is worth — both publishable;
the current unequal-rows comparison is not.

---

## 2026-09-15 — the head-to-head, and parity with crisprHAL 2

> ⚠️ **Partly superseded.** "Parity against their *published* figure, not a re-run" is retired: their model has now been re-run on these exact folds. See **2026-10-02**, and the superseded-claims table at the top of this file. Entry kept as written.

New module `src/sgrna/headtohead.py`; results in `results/headtohead.csv`;
written up as `results/RESULTS.md` §14 and `docs/NOVELTY.md` (rewritten for a
reader outside the project).

### The experiment

Featurised all 33,567 curated crisprHAL WT-SpCas9 guides through
`sgrna.featurise` (possible only because of the matrix decoding), located every
one of them in NC_000913.2 for ±1 kb of flank, built family A with the same
builder used for the 13,880, and ran 5-fold CV with their label.

| arm | rows | cols | ρ | R² | pick %ile |
|---|---:|---:|---:|---:|---:|
| published rows, base features | 8,617 | 6,169 | 0.536 | 0.299 | 69.5 |
| all curated rows, base features | 33,567 | 6,169 | 0.544 | 0.305 | 69.6 |
| + immediate ±10 nt | 33,567 | 6,429 | 0.618 | 0.383 | 72.9 |
| + windowed composition 50–1000 nt | 33,567 | 6,257 | 0.660 | 0.468 | 74.0 |
| **+ all of family A** | **33,567** | **6,517** | **0.707 ± 0.008** | **0.522** | **75.9** |
| *crisprHAL 2 as published* | *33,495* | — | *0.697* | — | — |

Seed 41 → 0.7078, seed 42 → 0.7062 over 8 folds total. **Claim is parity, not
victory**: +0.010 is inside the fold spread, and it is a comparison against
their published number rather than a re-run on our splits.

### Three findings from the decomposition

**1. Four times the rows buys +0.008.** The learning curve from §9 confirmed on
real data rather than extrapolated. The assay saturates near 20,000 guides;
a bigger screen is not the route to a better predictor.

**2. The label was hiding the flank effect, not damping it.** Family A is worth
+0.080 ρ on the published scores and **+0.164 on the curated scores, same
rows**. §9's conclusion that curation is worth +0.003 stands *for the baseline*
and is wrong for family A. Curation does not improve the model directly; it
makes a real biological signal visible. Correct the §9 framing wherever it is
quoted.

**3. On a clean label the long-range half is the bigger half.** Windowed
composition to 1 kb alone reaches 0.660 against 0.618 for the immediate ±10 nt —
reversing the ordering seen on the noisy label (§6: +0.049 local, +0.026
long-range). The signal furthest from the cut site survives curation best.

### Why this is not a subset of crisprHAL 2

**Information:** largely yes — they already feed 189 nt upstream + 166
downstream, so nearly everything family A measures is inside their window.

**Representation:** no. They give raw bases to a CNN–BiGRU; we give windowed
composition to a tree. Measured on the same rows: raw bases into our own
conv+BiGRU gain **+0.019**, windowed composition gains **+0.164**. So the flank
effect is a **smooth compositional gradient, not a motif** — a 5 nt convolution
must approximate "GC content of the next 500 bases" while a windowed mean
computes it. That is a biological claim they do not make and their architecture
cannot easily test, and it is the mechanistic reason a 0.3 s CPU tree matches a
GPU network.

> ⚠️ **"0.3 s" is wrong**, measured 2026-10-03: it counted only the final
> LightGBM fit and omitted the XGBoost feature selection that produces its
> inputs. End to end a fold is ~35 s and five folds ~3 min, against 105 min for
> crisprHAL — about 36×, not the implied thousands. See `RESULTS.md` §14 and
> the 2026-10-03 entry. Entry kept as written.

**Question asked:** entirely different. Theirs is a prediction paper; this is a
mechanism-and-method paper.

### Honest disadvantages to keep in the write-up

- Comparison is to a published figure, not a re-run of their model on our folds.
- crisprHAL 2 generalises across organisms and nucleases (*C. rodentium*,
  *S. enterica*); this project is *E. coli* SpCas9 only.

> ⚠️ **Misattributed, checked 2026-10-02.** Those cross-species results are
> crisprHAL **1**'s (*Nat Commun* 2023), not crisprHAL 2's, and the
> *S. enterica* arm is a 2 kb cloned fragment of ~300 guides inside *E. coli*
> rather than a screen in that organism. See the correction at the end of this
> file. Entry kept as written.

### Next

1. Re-run crisprHAL 2 on these exact folds — their code and weights are public.
2. Test whether windowed composition transfers to *C. rodentium* and
   *S. enterica*, where generalisation is currently their advantage.

---

## 2026-10-02 — family I (flank DNA shape) fails, and the crisprHAL re-run begins

Two of the four Part 10 next-steps actioned. New module
`src/sgrna/features/i_shape.py`, parameters in
`data/reference/dinucleotide_shape_scales.tsv`; results in
`results/ablation_shape.csv`, `results/ablation_shape_joint.csv`,
`results/headroom_with_shape.csv`, `results/crisprhal_rerun.csv`.

### The experiment (Part 10 item 3)

The error analysis said the remaining room was in describing the flanks
*structurally* rather than compositionally. Family I does that: nine
dinucleotide-step scales (bending propensity toward each groove, shift/slide
flexibility, and five elastic stiffness constants) summarised as mean and SD
over 10/25/50/250 nt windows on each side, plus `curv`, a phased bend sum that
adds bends reinforcing each other at the ~10.5 bp helical repeat and cancels
those that do not. 152 features, 13,879/13,880 guides.

Flanks only, by design: `diagnose.redundancy` established the published matrix
as a lossless encoding of the 20-mer, so shape descriptors *of the protospacer*
would add exactly zero information. The same logic is why family I is worth
testing at all — the flanks are outside that encoding.

| arm | R² | ρ | ΔR² |
|---|---:|---:|---:|
| baseline | 0.2934 | 0.5272 | — |
| family I alone | 0.3310 | 0.5627 | +0.038 |
| family I, labels permuted | 0.2913 | 0.5249 | −0.002 |
| family A alone (`ablation_main`) | 0.3805 | 0.6068 | +0.087 |
| **family A + family I together** | **0.3811** | **0.6078** | **+0.088** |

### Finding — shape is a reparameterisation of flank composition, and a worse one

**+0.0007 R² on top of family A, against a seed spread of ±0.0032.** The
+0.038 family I earns alone is family A's effect reached by another route, and
family A gets more than twice as much from the same underlying information.

The residual test agrees independently: the best of all 152 shape features
correlates with the champion's errors at **0.028**, below the 0.035 dust level
of the features the model already uses. Including `curv` (0.025) — the one
component letter composition *cannot* express. So the novel part is empty too,
not merely the redundant part.

**This is the counter-example that makes the `d_mechanics` result credible.**
There, a physical reparameterisation of the same information beat raw GC by
+0.020; here it loses to the composition it was derived from. The difference is
that family A is not a letter count — it is position-resolved composition over
four window sizes, which already spans what a 2 nt-step average can express.
"Better-shaped variable" is therefore a claim that has now been tested twice
and gone both ways, which is worth saying in the paper rather than quoting only
the success.

Count for the write-up: **seven** well-motivated feature groups shown unable to
help, and the redundancy/residual pair predicted this one before the ablation
confirmed it.

### Two data corrections, recorded because they would be invisible later

The source scale table carries two defects, left as fetched in the TSV and
handled explicitly in the module:

- `stiff_roll` — AA/TT and GA/TC are 0.02 where every other step is 16–26.
  Treated as corrupt and excluded.
- `bend_major`, `bend_minor` — not reverse-complement symmetric as published
  (AA 1.18 vs TT 1.09), which a duplex step property must be. Symmetrised;
  without this every feature would depend on which strand a guide targets.

### Part 10 item 1 — the crisprHAL re-run, in progress

`src/sgrna/crisprhal_rerun.py` trains their WT-SpCas9 architecture, their
hyper-parameters, their 48 epochs, imported unchanged from
`external_data/crisprHAL`, on our rows and our folds.

Completed the same day; all five folds in `results/crisprhal_rerun.csv`.

| arm | ρ | note |
|---|---:|---|
| `their_split` (their shipped split) | **0.6940** | against their published hold-out 0.695 |
| `our_folds` (mean of 5) | **0.6971 ± 0.0067** | against their published 5-fold 0.697 |

Two independent reproductions of their own published numbers to three decimals,
so the harness is faithful rather than flattering us. Paired against ours on the
same folds and label (seed 41): **+0.0107, ahead in 5 of 5 folds**, paired
t-test p = 0.0006, sign test p = 0.0625 (quote both — n = 5).

**Write it as a small but consistent advantage, not a victory.** +0.011 ρ is a
fraction of one pick percentile. Their arm is one seed against our two, and
their hyper-parameters were theirs rather than re-tuned here. The honest
headline is the cost ratio: 0.3 s of CPU against 125 min for their five folds.

> ⚠️ **Both halves of that ratio are wrong**, measured 2026-10-03. "0.3 s"
> counted only the final fit, not the feature selection, and it was compared
> against their *whole* five-fold run. Like for like: ~3 min against 105 min,
> about **36×**. Entry kept as written.

The §14 caveat "comparison is to a published figure, not a re-run" is retired,
as is the matching entry in Part 10 of the progress report.

### Next

Item 3 is closed. Item 4 — what the DNA-abundance signal actually is — is now
the highest-value remaining work, and the residual table says so numerically:
abundance at 0.155, HU dependence 0.152, origin distance 0.148, against 0.035
for everything the model already uses. First test needs no new download: in a
growing population, loci near the replication origin are physically present in
more copies, so check whether abundance is simply replication-timing copy
number.

---

## 2026-10-02 (later) — item 4: the DNA-abundance signal, mostly explained

New diagnostic blocks in `src/sgrna/make_diagnostic_blocks.py`
(`build_abundance_split`, `build_mapgc`); results in
`results/ablation_abund_split.csv`, `results/ablation_abund_cause.csv`,
`results/abund_local_vs_mappability.csv`. All arcs are `arc5`, 3 seeds × 5
folds, so these are directly comparable to `dissection_supercoiling.csv`.

### Finding 1 — it is not replication timing, and that part is worthless anyway

Each abundance track was split non-parametrically: the mean density of the
100 kb bin the guide sits in (`z_abund_smooth`) against the within-bin residual
(`z_abund_local`). `z_dosage` had already shown the analytic 2^-2f gradient
worth +0.013 of abundance's +0.045, but that proxy is a rigid shape; this is the
same question without a functional form.

| block | ΔR² | Δρ |
|---|---:|---:|
| `z_abund_smooth` — the 100 kb positional component | +0.0134 | **−0.0017** |
| `z_abund_local` — the within-bin residual | **+0.0356** | **+0.0326** |

The smooth component buys **no rank improvement at all**, and its ΔR² matches
`z_dosage` to three decimals. Replication timing is real, is confined to the
smooth component, and is useless for choosing a guide. Everything that matters
is local.

### Finding 2 — the effect is computable from the reference genome alone

Two sequence-intrinsic candidates, both window-matched to the tracks:
`uniq.w*`, the fraction of positions whose canonical 25-mer is unique in
NC_000913.2 (97.35% of the genome), and `gc.w*`. Local density tracks them
hard — rifampicin.w500 against gc.w500 at **r = −0.70**, signal.w2000 against
gc.w2000 at −0.44, and the untagged control's 10 kb density against
uniq.w10000 at **−0.69**. So the depth variation is GC bias in library prep
plus ambiguous mapping in repeats, not biology.

| arm | cols | ΔR² | Δρ |
|---|---:|---:|---:|
| `z_abund_local` — measured read density | 16 | +0.0356 | +0.0326 |
| **`z_mapgc` — genome only, no sequencing data** | **8** | **+0.0377** | +0.0299 |

**Eight columns from the reference genome reproduce the whole GapR-seq gain.**
The GEO download, the ChIP track, the untagged control and the rifampicin arm
are all unnecessary to capture this effect — which also means it transfers to
any organism with a reference genome, at no data cost.

### Finding 3 — against family A, almost all of it disappears

The `arc5` baseline has no family A in it, so the above had to be re-asked with
A present. Paired across the same 15 folds:

| arm | Δρ vs `a_flank` alone | folds won | p |
|---|---:|---:|---:|
| `a_flank` + `z_mapgc` | **−0.0002** | 8/15 | 0.84 |
| `a_flank` + `z_abund_local` | **+0.0061** | **15/15** | 2.5e-05 |

Mappability-and-GC adds **nothing** on top of family A: the sequence-intrinsic
explanation of abundance *is* windowed flank composition under another name.
This is the fourth family to collapse into that one variable (§4 had three).

Measured abundance does retain a small, unambiguous residual — +0.0061 ρ,
winning every fold — which is **not** reproducible from the genome. That is the
genuinely unexplained part, and it is about a tenth of what the standalone
+0.045 implied.

### Consequence for the write-up — Part 10 item 4 was overstated

"The single largest unexplained effect left" has to come down. Decomposed:
replication timing (no rank gain) + GC bias and mappability (genome-computable,
and already inside family A) + **≈+0.007 R² that is actually new**. The
remaining ~0.2 ρ of headroom is not hiding in abundance.

This is good for the paper's framing rather than bad: the flank-composition
result now absorbs what looked like a separate chromosomal effect, so the
project has one explanation doing more work instead of two competing ones.

### Next

The +0.007 residual needs new data to identify — local protein occupancy,
nucleotide pools, or something assay-specific. Candidates are no longer
testable from what is on disk, which makes this a natural stopping point for
the current round.

---

## 2026-10-02 (evening) — item 2: the flank effect transfers to another nuclease and another organism

New module `src/sgrna/transfer.py`; results in `results/transfer.csv`; written
up as `RESULTS.md` §15. New data: *C. rodentium* ICC168 NC_013716.1 downloaded
to `external_data/C_rodentium/` (5,346,659 bp, 54.7% GC) — the one download this
round, and only because the question could not be asked without it.

### The experiment

Family A was established on one screen. crisprHAL ships three more; two can be
used. Same protocol as §14 throughout, so the deltas are comparable.

| screen | rows | base | + family A | Δρ | folds won | p |
|---|---:|---:|---:|---:|---:|---:|
| WT-SpCas9, *E. coli* (§14) | 33,567 | 0.544 | 0.707 | **+0.163** | — | — |
| eSpCas9, *E. coli*, different enzyme | 59,489 | 0.680 | **0.784** | **+0.103** | 5/5 | 2.6e-06 |
| TevSpCas9, *C. rodentium* | 25,210 | 0.707 | **0.766** | **+0.060** | 5/5 | 2.9e-05 |

TevSaCas9 excluded: SaCas9 reads NNGRRT, so only 45% of its sites are NGG and
this pipeline's position labels would be misaligned. It would have produced
numbers.

For the *C. rodentium* set, flanks came from locating each protospacer in
NC_013716.1 and cutting ±1 kb: 25,210/25,244 located, and the PAM read back
**from the genome** is NGG for 100% of them — an independent alignment check,
since the PAM played no part in placing them.

### Finding — the effect belongs to the DNA, not to SpCas9 or to *E. coli*

Every fold improves in both new screens, by margins second and third only to
the original. The gradient **+0.163 → +0.103 → +0.060** tracks distance from the
original context: the effect weakens as the setting changes but never nears the
floor.

This retires the standing caveat "*E. coli* SpCas9 only", which has been
crisprHAL 2's clearest advantage since September. Evidence now spans **two
organisms and three nucleases**.

### What it does not say — state these explicitly in the write-up

1. **The feature family transfers; a trained model has not been shown to.**
   Every screen is trained and tested within itself. "Windowed flank composition
   is informative in *C. rodentium*" is the claim; "an *E. coli*-trained model
   ranks *C. rodentium* guides" is not, and is the next experiment.
2. **Absolute ρ is not comparable across screens** — eSpCas9's baseline is 0.680
   against WT's 0.544, which is that screen's label, not its enzyme. Only
   within-screen deltas mean anything.
3. **The Tev arm confounds organism with enzyme** (TevSpCas9 is a I-TevI fusion
   needing its own motif). eSpCas9 is the clean separation, and carries the
   larger of the two new gains.

### Three bugs, two of which returned confident wrong numbers

Recorded because the failure modes generalise, and because two of them would
have produced a publishable-looking table:

- `a_flank` silently returned **zero features** for every row: it skips rows
  whose `located` flag is unset, which only the genome-lookup path sets. No
  error. (All 33,567 curated guides were located, so §14 is unaffected — checked,
  not assumed.)
- **An off-by-one in PAM detection scored 1.000 while being wrong.** NGG's two
  Gs sit at +21 and +22 from the protospacer start; testing +20 and +21 also
  scores perfectly, one base off. Caught only by demanding the detector return
  189 for WT-SpCas9, which `crisprhal_rerun.py` independently hard-codes. **A
  validation a wrong answer can pass is not a validation** — the same failure as
  the 2026-09-13 GC elimination, which tested the candidate against the outcome
  rather than the mediator. Second instance; worth a line in the methods.
- A tuple passed where an array was expected, which at least failed loudly.

### Next

Finish this question rather than opening another. In order:

1. **Decompose family A in the new screens** the way §14 decomposed it in
   *E. coli* — immediate ±10 nt against the 50–1000 nt windows. If the
   long-range half is again the larger one, the *shape* of the effect transfers
   and not merely its sign, which is the mechanistic claim.
2. **Check the mechanism claims replicate**: GC-rich targets cutting worse,
   downstream outweighing upstream, the 250–500 nt distance peak.
3. **Then** the true model transfer — train on *E. coli*, rank *C. rodentium*.

---

## 2026-10-02 (night) — correcting the transfer result: one clean answer, one unusable dataset

Correction to this morning's entry, which reported the transfer numbers under
**random-row** cross-validation. Flank features are positional, so §8's own
rule says they must be validated grouped — and I had not done it. Re-run
properly, with `results/transfer.csv` now carrying a `cv` column.

### Finding 1 — the *C. rodentium* screen cannot answer the question

Applying `arc5` to it failed outright: **98% of its 25,210 guides sit in one
500 kb arc**, giving a one-group fold and a `nan`. Measuring the spread:

| screen | located | spread | density |
|---|---:|---|---:|
| eSpCas9 | **59,489 / 59,489** in NC_000913.2 | **all five arcs** | genome-wide |
| TevSpCas9 | 25,210 / 25,244 in NC_013716.1 | **229 kb — 4.3% of the chromosome** | **110 guides/kb** |

A 50–1000 nt compositional gradient needs genome-scale variation to exist.
Across 229 kb there is none, which shows up directly: flank GC correlates
**−0.022** with the label there, against +0.159 and +0.138 in the two *E. coli*
screens. **This dataset cannot test the long-range hypothesis under any CV.**
Check a screen's genomic span before asking it about long-range structure.

### Finding 2 — the leakage hypothesis was tested and rejected

I expected the gains to shrink under grouped CV. They did not.

| screen | CV | base | + family A | Δ |
|---|---|---:|---:|---:|
| eSpCas9 | random | 0.6804 | 0.7837 | +0.1033 |
| eSpCas9 | **arc5** | 0.6849 | **0.7892** | **+0.1043** |
| TevSpCas9 | random | 0.7066 | 0.7662 | +0.0596 |
| TevSpCas9 | **bin10k** | 0.7039 | **0.7641** | **+0.0602** |

Strict and loose agree to three decimals in both. Worth recording that the
suspicion was wrong: the reason to doubt the *C. rodentium* number was never
leakage, it was that the screen does not span enough genome for the question.

### Finding 3 — the cross-enzyme result is solid, and the *shape* transfers

Under `arc5`, eSpCas9 gains **+0.1043** (5/5 folds, p = 7.4e-06), and the
long-range half again beats the local half (**+0.0331**, 5/5, p = 0.0012) —
the same ordering as §14's 0.660 vs 0.618. In *C. rodentium* the two halves are
identical instead (−0.0008, 3/5, p = 0.94).

So the compositional-gradient finding is not an artifact of SpCas9: within
*E. coli* it survives changing the enzyme, in both magnitude and shape.

### Finding 4 — the strand-invasion mechanism replicates; the flank gradient does not

| screen | target GC | flank GC (dn250) |
|---|---:|---:|
| WT-SpCas9 | −0.147 | +0.159 |
| eSpCas9 | −0.107 | +0.138 |
| TevSpCas9 | **−0.379** | **−0.022** |

The target-GC penalty holds in all three and is *strongest* in *C. rodentium* —
as expected for a claim about the physics of prying a duplex open. The flank
benefit tracks the span problem, not the organism.

### The claim, corrected

**Was:** "the flank effect transfers to another nuclease and another organism;
the *E. coli*-only caveat is retired."

**Is:** the effect is a property of the DNA rather than of SpCas9 — shown on a
genome-wide screen with a different nuclease, under the strictest CV this
project uses. **Cross-species remains untested**, because the only available
other-organism screen covers 4.3% of one chromosome. Testing it needs a
genome-wide screen in another organism.

### Next

1. The honest cross-species test needs a genome-wide bacterial screen outside
   *E. coli* — a dataset search, not an analysis.
2. The model-transfer question (train on one screen, rank another's guides) is
   still open and is answerable with what is on disk, between the two *E. coli*
   screens.

### Correction — the competition's cross-species claim was misattributed here

Checked while writing up the transfer work, because "they generalise across
species, we do not" had become a standing concession.

**It is crisprHAL 1's claim.** The cross-species results are in Ham, Browne et
al., *Nat Commun* 14:5514 (2023). crisprHAL 2 (*PeerJ* 2026) — the model the
§14 head-to-head is against — is a data-curation paper, described by its own
repository as rebuilding two prior *E. coli* datasets and producing an improved
*E. coli* eSpCas9 model. Earlier entries here and in `RESULTS.md` credited the
cross-species work to crisprHAL 2; that is wrong and has been corrected in both.

**And the evidence is thinner than "three species" suggests:**

| organism | what it is | guides | their ρ |
|---|---|---:|---:|
| *E. coli* | training + held-out test | 45,010 / 7,821 | 0.657–0.682 |
| *C. rodentium* | a screen in that organism | 31,796 | 0.635, 0.612 |
| *S. enterica* | **2 kb of its *katG* gene cloned into *E. coli*** | **~270–300** | 0.678, 0.648 |

The *S. enterica* arm is foreign *sequence* in an *E. coli* cell — no
*Salmonella* chromosome, no *Salmonella* cellular context. And the
*C. rodentium* arm is the same data measured in this entry: 229 kb, 4.3% of a
chromosome, 110 guides/kb.

**Consequence for positioning.** Not "they solved cross-species and we did
not", but: nobody has the dataset the question needs — a genome-wide Cas9
screen in a non-*E. coli* bacterium — and this project is the one that measured
why the existing substitutes cannot stand in for it. The concession in §14 and
Part 10 has been rewritten accordingly.

**Caveat on these numbers:** taken from abstracts, summaries and repositories,
not the full PDFs (PeerJ returned 403, and two sources differ on the
*S. enterica* count: 268 vs 296). Verify against the PDFs before any manuscript
quotes them.

### Model transfer — train on one organism, rank another's guides

`transfer.transfer_model`; results in `results/transfer_model.csv`. Fits on all
of one screen, predicts all of another.

| train → test | base | + family A | family A adds | target's own ρ | retained |
|---|---:|---:|---:|---:|---:|
| *E. coli* WT → *C. rodentium* | 0.626 | **0.700** | +0.074 | 0.764 | **92%** |
| *C. rodentium* → *E. coli* WT | 0.478 | **0.628** | **+0.150** | 0.707 | **89%** |
| *E. coli* eSp → *C. rodentium* | 0.587 | 0.656 | +0.069 | 0.764 | 86% |
| *E. coli* WT → *E. coli* eSp | 0.591 | 0.689 | +0.098 | 0.789 | 87% |

**Finding 1 — cross-organism transfer works at ~90% retention.** Sequence-
disjoint and organism-disjoint, both directions.

**Finding 2 — family A is the portable part.** It improves every direction, and
most in the hardest: *C. rodentium* → *E. coli* goes 0.478 → 0.628 (+0.150).
The published representation alone transfers poorly; the flank encoding is what
survives a change of organism.

**Caveat — the WT → eSp arm is not a generalisation test.** Those screens share
**100% of their guides** (same library, two nucleases), so every test sequence
was in training. Reported because it isolates the enzyme change with sequence
held constant; must not be quoted as evidence about unseen DNA.

**Finding 3 — this resolves the apparent contradiction with the entry above.**
The long-range gradient cannot be *learned* from the *C. rodentium* screen
(229 kb; flank GC ρ −0.022 there), yet a model that learned it in *E. coli*
*transfers* it there successfully. Both hold. Together they localise the
limitation to the available **data** rather than the biology — a distinction
only the model-transfer arm can make, and one the within-screen arms cannot.

**Where the species question now stands.** Shown: a flank-aware model trained
in *E. coli* ranks another organism's guides at ~90% of a locally-trained one,
and family A is responsible. Not shown: that the long-range gradient is
*detectable* in another organism. That still needs a genome-wide non-*E. coli*
screen, which no one in this literature has.

### Transfer decomposition — the long-range half is what crosses, and a correction

| train → test | base | + local | + long-range | + full A |
|---|---:|---:|---:|---:|
| *E. coli* → *C. rodentium* | 0.6261 | 0.6614 (+0.035) | **0.6647 (+0.039)** | 0.7002 (+0.074) |
| *C. rodentium* → *E. coli* | 0.4785 | 0.5365 (+0.058) | **0.5855 (+0.107)** | 0.6282 (+0.150) |

**Finding — the long-range windows carry the transfer**, in both directions,
and dominate in the hard one: 88 long-range columns beat 260 local ones by
+0.107 to +0.058 crossing out of *C. rodentium*, 71% of the total family A gain.

**Correction to this morning's entry.** "This dataset cannot test the
long-range hypothesis, whatever CV is used" was too strong. Correctly: a
*correlation* measured inside a 236 kb window cannot reveal the gradient —
there is not enough spread in flank composition — but a *model* trained in that
window still learns a flank-to-efficiency function that extrapolates across an
entire other genome. **Discovery and verification have different data
requirements.** Conflating them is what made the within-screen reading look
conclusive.

Also corrected: the 236 kb span is the authors' stated design (*"A 236-kb
fragment of the Citrobacter rodentium DBS100 genome was screened"*, Ham et al.
2023), not a defect found here. Our 230 kb measurement matches it; that is a
mutual check, not a discovery, and the earlier wording claimed too much.

### Does the *E. coli* model beat *C. rodentium*'s own model on *C. rodentium*?

Both out-of-sample on the same 25,210 guides:

| | its own model | the *E. coli* model |
|---|---:|---:|
| base | **0.7039** | 0.6261 |
| + family A | **0.7641** | 0.7002 |
| *family A's contribution* | *+0.0602* | ***+0.0741*** |
| *of which long-range* | *+0.0325* | ***+0.0386*** |

No overall — the local model wins by 0.064 — but **all of its advantage is in
the base features** (+0.078): its own label scale, nuclease and 20-mer mapping.
The *E. coli* model extracts **more from *C. rodentium*'s flanks** than
*C. rodentium*'s own model does.

**The flank-to-efficiency relationship is better learned from a genome-wide
screen in the wrong organism than from a narrow screen in the right one.**
Breadth of genomic context beats species match for this component.

**Follow-up worth running:** a hybrid — flank component fitted on *E. coli*,
enzyme/label component on the target screen — which this decomposition predicts
should beat both. Nobody in this literature has tried it.

### crisprHAL figures, verified against the full text

Checked against *Nat Commun* 14:5514 (2023) rather than summaries, as the
earlier entry flagged:

- *C. rodentium*: *"A 236-kb fragment of the Citrobacter rodentium DBS100
  genome was screened for 5'-NGG-3' PAM sequences and 31,596 sites were
  identified"*; ρ 0.635 and 0.612.
- *S. enterica*: *"We cloned a 2-kb fragment of the katG gene from Salmonella
  enterica Typhimurium LT2 into pTox to create pTox+KatG. We designed a pool
  containing 296 sgRNAs targeting the katG sequence"*; ρ 0.678 and 0.648. The
  count is **296** (the 268 figure seen elsewhere was wrong), and the fragment
  sits on a **plasmid**, not in the *E. coli* chromosome.

Both non-*E. coli* validations are therefore confined fragments — 236 kb and
2 kb — and one is foreign sequence on a plasmid inside *E. coli*.

### The hybrid — tested and rejected, with a useful by-product

Predicted by the decomposition: fit the flank component where the genomic
variation is (*E. coli*), the label/enzyme component where the labels are
(*C. rodentium*), and beat both. Stage 1 trains on *E. coli* with family A
alone — no base columns, so the prior carries only the flank relationship — and
scores every *C. rodentium* guide; stage 2 is ordinary `bin10k` CV on
*C. rodentium* with that one extra column. No target label enters stage 1
(`results/hybrid.csv`). The prior alone correlates with the *C. rodentium*
label at ρ 0.227.

| arm | ρ | against the arm above |
|---|---:|---|
| base | 0.7039 | — |
| **base + prior** | **0.7513** | +0.0474, 5/5 folds, p = 0.0039 |
| base + family A | 0.7641 | +0.0128, 5/5, p = 0.029 |
| base + family A + prior | 0.7644 | **+0.0002**, 3/5, p = 0.80 |

**Rejected.** On top of the local flank features the import adds nothing.

**Correction to the entry above.** It claimed the flank relationship is "better
learned from a genome-wide screen in the wrong organism than from a narrow
screen in the right one", based on the *E. coli* model gaining +0.074 from
flanks against the local model's +0.060. That comparison is unsound: the gains
sit on different baselines (0.626 vs 0.704), so the weaker starting model shows
a larger gain for free. The hybrid is the controlled version and it says the
two sources are **redundant**, not complementary. Corrected in `RESULTS.md` §15
and the progress report.

**The by-product is worth keeping:** one imported column does 78% of what 348
local ones do (+0.047 of +0.060), trailing the full local block by 0.013. A
compression result, not an information one — and it strengthens the
conserved-relationship claim. A prior fitted on *E. coli* could not substitute
for 348 locally-computed columns at 78% strength if the flank-to-efficiency
function were organism-specific.

Practical note for anyone applying this: a flank model transfers as **a single
feature**, which is far cheaper than recomputing 348 windowed columns against a
new genome.

---

## 2026-10-02 (late) — the human boundary: where everything here stops

`results/human_transfer.csv`. Noshay et al.'s *H. sapiens* matrix
(`data/raw/human_feature_matrix.csv`, 17,421 guides) shares **6,216 columns**
with the *E. coli* one, so a model crosses with no change of representation —
which makes this the cleanest cross-kingdom test available: a failure cannot be
blamed on mismatched features.

| arm | ρ |
|---|---:|
| *E. coli* within-screen CV | **0.5305** (frozen baseline 0.5278 — harness check) |
| human within-screen CV | 0.4043 |
| ***E. coli* → human** | **−0.048** |
| **human → *E. coli*** | **−0.017** |

**Finding 1 — cross-kingdom transfer is useless in both directions**, slightly
worse than random. Reproduces crisprHAL's −0.2 to 0.1 for human models on
bacteria, now measured both ways on an identical feature set.

**Finding 2 — the mechanism inverts, which is why it is negative not merely
weak.**

| | *E. coli* | human |
|---|---:|---:|
| GC content → cut score | **−0.201** | +0.017 |
| melting temperature → cut score | **−0.201** | +0.017 |
| guide secondary structure → cut score | +0.071 | +0.028 |

The strand-invasion result (§6) — the project's strongest single mechanism —
**has no counterpart in human cells**. An *E. coli*-trained model applies
"avoid GC-rich targets", which is inert in human data. Whatever limits human
editing (chromatin, repair choice, delivery) is not in these features.

**Finding 3 — the distance gradient is now complete:**

| setting change | ρ retained vs a locally-trained model |
|---|---:|
| different nuclease, same organism (shared guides) | 87% |
| different organism, same kingdom | **89–92%** |
| **different kingdom** | **0%** |

**Consequence.** Every claim in this project is explicitly **bacterial**, with
the boundary measured rather than assumed — which is a stronger position than
hedging, and worth stating in the paper's scope section.

**Caveats.** The labels measure different quantities (human `cut.score` is a
0–1 fraction, the *E. coli* score a 0–48 depletion value; Spearman handles the
scale but not the difference in meaning), and the human arm carries no family A
because that needs 17,421 guides located in hg38.

---

## 2026-10-03 — the speed claim was never measured

Prompted by a simple question: where did "0.3 s" come from? Nowhere — it
appears in the README, `RESULTS.md` (§1, §14), the progress report and two log
entries, and no measurement for it exists anywhere in the repo. Measured now
(`results/timing.csv`), §14 configuration, 33,567 × 6,517, one fold:

| stage | time |
|---|---:|
| impute | ~1.8 s |
| **XGBoost feature selection, 6,517 → 300** | **~31 s** |
| LightGBM fit on the 300 | ~2.4 s |
| **one fold, end to end** | **~35 s** |

**Two errors.** The 0.3 s counted **only the final fit**, excluding the feature
selection that produces its 300 inputs — the stage that actually dominates, at
~13× the fit. And the fit alone measures 1.5–2.4 s here anyway.

A third error was introduced on 2026-10-02: comparing that single fit against
crisprHAL's *entire five-fold training* and calling it "~25,000×". Like for
like, five folds against five folds on the same machine: **~3 min against
105 min, about 36×**.

**Health warning, recorded because it matters more than the number.** Four
measurements of identical work gave 13.0, 34.7, 116.2 and 35.4 s per fold; the
selection stage alone ranged 9.6–112.7 s. This host has 16 GB against a 198 MB
matrix, a 250 MB matrix and several GB of caches, and has logged 970k
pageouts — the timings measure memory pressure as much as computation. The
~35 s figure is the median of the two agreeing isolated runs.

**So the defensible claim is qualitative**: minutes against hours, on a CPU,
for equal predictive performance. A precise multiple needs a quiet machine with
enough RAM not to swap. Do not quote a specific figure in the paper without
re-measuring there.

**The lesson generalises, and it is the third instance this week.** A number
that sounds precise, is repeated across documents, and has no recorded
measurement behind it is folklore. The GC elimination (§3) and the PAM detector
(§15) failed the same way: a claim that nobody re-derived because it looked
settled. Numbers in these documents should cite the file that produced them.

### Correction to the entry above, and what the audit actually found

The entry above says the speed claim "was never measured". **That is wrong, and
it was my own unchecked claim** — I grepped the prose and not the data.
`model_comparison.csv` has a `fit_seconds` column, and LightGBM's fit is
recorded there at **0.291 s**, tightly reproducible across 15 folds
(0.28–0.31).

So the failure was **scope, not fabrication**: a correctly measured number
describing the wrong quantity. The 0.291 s is the final fit on 300
already-selected columns; the XGBoost pass that picks those 300 out of 6,517 —
about 13× more expensive — was simply not counted. That is harder to catch than
an invented figure, because tracing it to its source *confirms* it.

**The rest of the audit came out clean.** Every other quantitative claim traces
to a results file, and the ones re-derived today all matched:

| claim | checked |
|---|---|
| 5,853 of 5,887 `V####` columns identified | **5,853** ✓ |
| 6,169 of 6,232 regenerable (99.0%) | 5,853 V + 316 QCT = **6,169** ✓ |
| 100% agreement with the published matrix | **100.000000%**, 6,169 cols × 500 guides ✓ |
| 13,877 guides appear exactly once | **13,877** of 13,880 ✓ |
| oriC at 3,923,620 from GC skew | **3,923,620** ✓ |
| ridge "costs 0.02 seconds" | **0.022 s** ✓ |
| stacking wins "+0.002 at 48× the cost" | 14.02 s / 0.291 s = **48×** ✓ |

Last night's generalisation — that numbers in these documents are folklore —
was an overcorrection from a single example. The accurate lesson is narrower:
**state what a measured number measures.** A fit time is not a training time.

### Memory, measured — the saving is time, not footprint

| | per fold | five folds | peak RSS |
|---|---:|---:|---:|
| this project, end to end | ~35 s | ~3 min | **3.55 GB** |
| crisprHAL 2 | 1,037–1,266 s | 105 min | **4.55 GB** |
| ratio | ~30–36× | ~30–36× | **1.28×** |

Peak memory is comparable. Our cost is a 33,567 × 6,517 float32 table carried
through imputation and XGBoost (1.0 GB resident, 3.5 GB peak); theirs is a
310 MB one-hot input expanded by a network across 48 epochs. **Do not claim the
tree pipeline is light on RAM** — it is not; it is light on time.

Both are **CPU-to-CPU on the same machine**. crisprHAL 2 as published is
GPU-trained, so what was measured is that their architecture needs ~30× more
CPU time for equal accuracy — not that this project beats a GPU.

### Controlled timing, and the selector that is 3× cheaper for free

The 13–116 s spread was **our own fault, twice over**: `n_jobs=-1` let the
selector take whatever cores were free, and the matrix was held resident and
copied twice, pushing a 16 GB host into swap. Fixing threads at 8 and reading
the matrix by `mmap` gives **IQR 0.71 s over 5 repeats**
(`results/timing_controlled.csv`).

| | per fold (IQR) | five folds | peak RSS | vs crisprHAL |
|---|---:|---:|---:|---:|
| current pipeline (XGBoost selector) | **17.07 s** (±0.71) | 1.42 min | 4.03 GB | **74×** |
| with a LightGBM selector | **6.63 s** (±0.37) | 0.55 min | 4.03 GB | **191×** |
| crisprHAL 2 | 1,266 s | 105 min | 4.55 GB | — |

Conservative: 8 threads against their 10. **So the sequence of estimates has
been 25,000× (wrong method), 30–36× (right method, contaminated measurement),
74× (controlled).** Only the last has a spread small enough to quote.

**Selector comparison** (`selector_comparison.csv`), five selectors, same folds,
same downstream champion:

| selector | ρ | vs current | select |
|---|---:|---:|---:|
| LightGBM gain, 300 trees | **0.7033** | +0.0008 (p = 0.029) | **3.25 s** |
| XGBoost gain, 100 trees | 0.7007 | −0.0018 (p = 0.12) | 5.95 s |
| XGBoost gain, 300 trees (current) | 0.7025 | — | 10.29 s |
| variance filter (label-free) | 0.6968 | −0.0057 (p = 0.006) | 0.07 s |
| \|correlation\| filter | 0.6751 | **−0.0274** (p < 0.001) | 0.55 s |

**LightGBM selection is a free 3×.** Not adopted: `selector_params` is marked
"identical to the frozen baseline script", so changing it means every recorded
number came from a selector the code no longer describes. Switch deliberately,
re-run the headline arms, then change the default.

**The univariate filter is the worst**, which is a real finding: gain ranking
captures conditional structure that single-column association cannot. The
feature that predicts best alone is not the feature a tree wants.

**What the variance filter means.** A label-free filter losing only 0.006 is
not evidence that selection can ignore the label. It is a scale artifact plus a
restatement of redundancy:

| | QCT | family A | V indicators | median variance of picks |
|---|---:|---:|---:|---:|
| variance-selected | 148 | 127 | 25 | 14.02 |
| gain-selected | 98 | 77 | 125 | 0.066 |

The two sets **share only 114 of 300 columns**. Ranking by raw variance ranks
by *units* — continuous QCT and windowed columns have wide numeric ranges while
one-hot indicators are capped at 0.25 — so it takes the continuous columns and
drops the indicators gain prefers, and still lands within 0.006.

Two nearly disjoint subsets performing equally is a statement about **the
matrix**: the signal is spread across many correlated columns, as §4, §5 and
§13 each found by other routes. It also belongs beside §11 — that section
showed 19.8 *permuted* family A columns were still selected as "important";
this shows a selector that never sees the label scores within 0.006 of one that
does. Selection is weak evidence about what matters.

### A process note

The previous entry's doc updates were reported as applied when two of them had
silently failed — a batched edit script asserted and exited before writing, and
the failure was not checked before reporting. The README and progress report
carried stale figures through one commit. Verify writes landed before saying
they did.

---

## 2026-10-03 (later) — four questions from outside the project, and two headline numbers withdrawn

Prompted by a read-through from someone not working on the modelling. Four of
the questions landed on real errors; two of those change headline claims.
New code: `src/sgrna/tune.py`, `src/sgrna/floors.py`. New data:
`results/tuning.csv`, `results/permutation_floors.csv`.

### Finding 1 — tuning is worth as much as the entire head-to-head margin

**The question:** "would tuning hyperparameters on crisprHAL 2 and our model
lead to parity again, or would one outperform the other?"

Nobody had asked. The §14 comparison is untuned against untuned, and the word
"hyper-parameter" appeared in this log only in reference to *theirs*.

Measured (`tune.py`, 12 random draws, search run on an inner split of each
training fold so the validation fold is scored exactly once):

| | ρ |
|---|---:|
| default settings | 0.7078 |
| tuned | **0.7181** |
| gain | **+0.0103 ± 0.0030, 5/5 folds, p = 0.0015** |

Per fold +0.0087, +0.0125, +0.0143, +0.0077, +0.0081.

**Our lead over crisprHAL 2 is +0.0107. Tuning our own model is +0.0103.** The
margin is inside the tuning effect, so it cannot support an advantage claim.
Tuning theirs is ~a day of CPU (one config = 105 min for five folds), so the
comparison stays untuned-vs-untuned and **the claim reverts to parity**.
"A small but consistent advantage" is withdrawn from §14 and the progress
report. Our tuned 0.7181 is still the highest number reported on these rows and
can be stated as that — explicitly a tuned-vs-untuned comparison.

### Finding 2 — the ceiling argument was backwards

**The question:** "eSpCas9 is different from but still very similar to
WT-SpCas9 — of course testing similar enzymes gives similar conclusions."

Correct, and it breaks the ceiling derivation. The 0.810 cross-screen agreement
was called a **conservative** bound "since the enzymes differ, so part of the
shortfall is real biology". But the two screens use the **same guide library** —
100% identical target sequences — and eSpCas9 is WT plus three point mutations.
So 0.810 is two measurements of nearly the same quantity on exactly the same
DNA: the **best case** for agreement. Genuinely independent repeats would agree
*less*, putting the real ceiling *below* 0.90.

**√0.810 ≈ 0.90 is an optimistic upper bound, not a conservative one.** The
100%-shared-library fact was already in this log — but only as a caveat on the
WT→eSp transfer arm, never carried across to the ceiling. Corrected in
`RESULTS.md` §13 and the report. The conclusion that neither model is near the
limit survives either way.

This is the same failure mode as the GC elimination and the PAM detector:
**a claim nobody re-derived because it looked settled.** Fourth instance.

### Finding 3 — the permutation floor was one family's floor quoted for nine

**The question:** "the supercoiling effect was disproven by its control — has
this control been run on every other feature?"

It had not. Four families had a permutation control; five did not, and the
project was quoting `a_flank`'s floor (−0.0018) as if it were global. It is not:
the floor depends on how many columns a family contributes and how many survive
top-300 selection by luck.

Ran the missing five, and recomputed every delta **paired on (seed, fold)** —
previously a three-seed family was differenced against a five-seed baseline,
mixing the effect with seed spread (`floors.py`):

| family | real Δρ | own floor | ratio | verdict |
|---|---:|---:|---:|---|
| `a_flank` | +0.0795 | −0.0009 | 88× | clear |
| `d_mechanics` | +0.0201 | +0.0001 | 153× | clear |
| `b_energy` | +0.0074 | −0.0001 | 92× | clear |
| `c_folding` | +0.0074 | +0.0010 | 7.7× | clear |
| `f_methylation` | +0.0034 | +0.0011 | 3.0× | **marginal** |
| `h_offtarget` | +0.0003 | +0.0004 | 0.8× | **below its own floor** |

**`h_offtarget` is a null result**, not a small positive one, and
**`f_methylation` is marginal**. Both were being listed with nominal gains.

Also distinguished two things the documents had been conflating: a *permutation*
control (is this better than noise?) and a *source-experiment* control (is my
biological reading right?). The second exists for **exactly one** data source —
GapR-seq, where it was run and did overturn the result. For `e_nucleoid` the
check was only indirect, via its 0.77–0.96 correlation with tracks the untagged
arm had already discredited. Coverage table now in §17.

**Bug found while doing this:** `b_energy`'s permuted arm ran on 2026-09-12 and
its 15 folds were in `folds_main.csv` all along, but the summary row was never
written — the resume gate sees the fold checkpoint complete and skips the
experiment before reaching the summary step. Same class as the gate bug fixed on
2026-09-13. A finished result that silently does not appear.

### Finding 4 — the "four times" comparison paired two different datasets

**The question:** "0.164 is not 4 × 0.019 — where did the 4× come from?"

From the right comparison attached to the wrong number. The CNN's +0.019 and the
flank features' **+0.080** are both on the original 13,880 guides: 4.2×. The
+0.164 is on the *curated* 33,567. The progress report had paired +0.019 against
+0.164 and called it four times, which is neither arithmetic nor like-for-like.
`RESULTS.md` §13 had it right throughout. Conclusion unchanged, supporting
arithmetic was wrong; correction note left in place in the report.

### Answered without new work

- **TevSaCas9, "it would have produced numbers"** — too cryptic. Expanded: the
  pipeline would have run to completion with no error and returned
  plausible-looking results measuring the wrong positions, because only 45% of
  SaCas9's NNGRRT sites are NGG. More dangerous than a crash.
- **The 8 columns** (`z_mapgc`) — 25-mer uniqueness fraction and GC fraction, at
  windows of 100/500/2,000/10,000 nt. 2 × 4 = 8, reference genome only.
- **Does the GC penalty generalise to humans?** No, and it is measured:
  −0.201 in *E. coli*, **+0.017** in human. Literature adds the mechanism we
  cannot test here — the published human effect is **non-monotonic** (40–60% GC
  optimal, linear association not significant), and **nucleosomes physically
  block Cas9**, so accessibility is a first-order human determinant with no
  bacterial counterpart. Bacteria are not chromatin-free (HU, H-NS — that was
  `e_nucleoid`) but the packaging is not nucleosomal. Cheap follow-up: test the
  U-shape in the human matrix we already hold.
- **A different phylum?** Searched. **No genome-wide Cas9-*cutting* efficiency
  screen exists outside *Enterobacteriaceae*.** What exists in *Bacillus*,
  *Mycobacterium* etc. is CRISPRi — dCas9 silencing, a different measured
  quantity. So the phylum question needs wet-lab work, and the competition is in
  the same position (their two non-*E. coli* validations are a 236 kb fragment
  and 296 guides on a plasmid inside *E. coli*).

### Restructuring done to the progress report

On request, and worth keeping: Part 4 rewritten from a list of experiments into
one six-step argument; cross-organism results given as a 2×2 train/test table
with a note on why the enzyme necessarily differs between cells (and the 87%
WT→eSp retention that bounds how much that costs); the nine feature families
**grouped into four ideas** in an appendix with the data source for each; a new
Part 0 on what CRISPR is used for and whether a bacteria-only result is worth
having (answered with our own 0% human transfer); and a model name, **SLICER**,
provisional.

### The a priori exercise, which is worth keeping

Also on request: rather than explaining the six failed families with a rule
invented after seeing them, the rule is now applied **as a prediction**, family
by family, with the reasoning stated before the result column. **7 of 10
correct.** The three misses are the valuable part:

- `i_shape` was predicted to help (it is outside the 20-mer) and does not, which
  **finds the rule's limit**: being outside the protospacer is necessary but not
  sufficient — the information must be outside *everything already in the
  model*, and windowed composition at four scales already spans what a
  2 nt-step average expresses. **Refined rule: ask whether a candidate is
  computable from the features you already have, not just from the sequence.**
- `h_offtarget` was predicted to help and does not, because the effect is absent
  rather than redundant — now confirmed as below its own floor.
- The three positional families passed the redundancy rule and then failed a
  *different* test, causation rather than redundancy (§3).

Turning the rule into a scored prediction is a stronger claim than using it as
an explanation, and the misses sharpened it. Recommended for the paper in this
form.

---

## 2026-10-03 (evening) — what the importance disagreement actually means

**The question:** "XGBoost thinks its own features aren't important; LightGBM
thinks its own features are important; they perform about as well, and they
choose pretty different features. What does that mean?"

Tested rather than argued (`src/sgrna/attribution.py`,
`results/attribution.csv`, `results/attribution_summary.csv`). Each model
selects its own 300 features on the same fold; compare the top 50.

| | result |
|---|---|
| columns both models chose | **14 / 50** |
| correlation of the two importance rankings, all columns | +0.692 |
| held-out ρ | 0.6267 (XGB) vs 0.6219 (LGBM) — tied |

### Finding 1 — not different biology, but not simple one-to-one redundancy either

For each column only one model picked, the maximum |correlation| with any
column in the other model's set:

| | median | share > 0.7 |
|---|---:|---:|
| XGBoost-only → LightGBM set | **0.456** | 22% |
| LightGBM-only → XGBoost set | 0.402 | 22% |
| random columns → LightGBM set (null) | **0.069** | 0% |

0.456 against a 0.069 null rules out "they found different things". But only
22% above 0.7 rules out the clean "every column has a near-twin" story I
expected. **Honest reading: substitution is not one-to-one — a tree can rebuild
a dropped column's contribution from several weakly-correlated ones, so
pairwise correlation only puts a floor under replaceability.** Recorded because
the hypothesis was half wrong and the test is what showed it.

### Finding 2 — the disagreement is binary-vs-continuous, and it is algorithmic

Importance share by what the column describes:

| kind | XGBoost | LightGBM |
|---|---:|---:|
| target: position/letter indicators (binary) | **49%** | 18% |
| target: quantum descriptors (continuous) | 19% | **33%** |
| flank windows (continuous) | 9% | **25%** |
| flank, nearest 10 nt | 11% | 17% |
| other published columns | 12% | 6% |

Almost the whole disagreement is one axis: **XGBoost leans on the binary
indicators, LightGBM on the continuous columns** — consistent with
histogram-binned leaf-wise growth making continuous features cheap to split
repeatedly. So a large part of what an importance ranking reflects is **the
splitting algorithm's affinity for a column's data type**, not the column's
relevance. This is the most concrete reason yet not to read mechanism off an
importance plot, and it was not anticipated.

### Finding 3 — it also explains the −0.02

Gain credits whichever of several interchangeable columns a tree used first;
permutation asks what breaks if that column is destroyed, and answers "barely"
when the others can rebuild it. The two diverge most where importance is spread
thinly over many interchangeable columns — XGBoost's exact situation (330
columns for half the importance, mostly binary slivers) against LightGBM's
(151, mostly continuous and individually harder to replace).

**Decisive check, already on file: faithfulness.** Dropping each model's top 20
costs barely more than dropping 20 at random (+0.008 LGBM, +0.003 XGB). So
neither ranking is load-bearing. **Method agreement measures how concentrated
and individually irreplaceable an attribution is — not whether it is right.**

Wording corrected in the report: "LightGBM's two methods agree, so the story is
stable" implied the story is therefore trustworthy. Reproducible ≠ correct.
LightGBM is still the right default, for reproducibility.

### Consequence for the inherited paper, stated carefully

Noshay et al. read "quantum chemistry at the 3′ terminus matters" off an
iterative random forest's importance ranking on this matrix. Kind-level
importance on this matrix swings from 49% to 18% depending on the algorithm, so
**an importance ranking here cannot establish the claim on its own.** It does
not show the claim is false — LightGBM does put its largest share (33%) on the
quantum descriptors, which is consistent with it. Precise criticism, not a
dismissal.

### Policy added to the report

None of the biology in Part 4 came from an importance ranking — it came from
group ablations against shuffled controls, from the sign of named quantities
anyone can recompute in one line (target GC −0.201, flank GC +0.159), and from
transfer across screens. That was lucky rather than principled; it is now
written down as policy.

### Naming

Renamed **FlankQ → SLICER** across all documents, on the point that a tool
name should describe the function, not the headline finding — the tool should
outlive any one result. *SLICER*: it gauges how well a candidate guide will
cut, in a bacterial genome, from the target and its surroundings. Alternatives
noted in the report: CasGauge, LociScore, TERRAIN.

---

## 2026-10-03 (evening) — working the Part 12 list

### Item 4 — the human GC relationship is peaked, not absent

`results/gc_shape.csv`, `gc_shape_vertex.csv`. Fitting GC and GC² against the
cut score on both matrices:

| | linear ρ | linear R² | quadratic R² | curved term | vertex GC | vertex at |
|---|---:|---:|---:|---:|---:|---|
| human | +0.017 | 0.00019 | **0.00423** | F = 70.8, p < 10⁻¹⁵ | **0.571** | **60th** pct |
| *E. coli* | −0.201 | 0.0407 | 0.0452 | F = 64.7, p < 10⁻¹⁵ | 0.294 | **1st** pct |

Both have a significant curved term. **What differs is where the turning point
sits relative to the data.** Human: interior, a real optimum at GC ≈ 0.57 —
decile means run 0.235 (GC 0.43) → **0.262** (GC 0.60) → **0.192** (GC 0.78).
*E. coli*: vertex below the 1st percentile, so monotonic decline across the
bulk.

The quadratic explains **22× more human variance than the linear** (0.0042 vs
0.0002), which is exactly why the linear ρ of +0.017 looked like nothing.

**Upgrade to the cross-kingdom claim**, as item 4 intended: not "the mechanism
does not transfer" but **"the mechanism is replaced by one of a different
shape"**. Consistent with the published human literature (optimum near 40–60%
GC, no significant linear association). Written into `RESULTS.md` §15 and
Part 9 of the report.

### Item 2 — true replicates exist, but the published number is the wrong one

Guo et al. 2018's methods state *"two biological replicates were performed for
each host strain by independent transformations"*, with agreement reported as
**R² > 0.78**. So replicates exist — the report previously said "if any exist".

**But that agreement is on sequencing read counts, not on the derived cut
score.** Read counts are dominated by library composition: abundant guides stay
abundant, so the replicates agree partly for reasons unrelated to cutting. It
is an upper bound on an upper bound, and cannot be converted into a reliability
for the label.

**The route to fixing it is now concrete:** pull per-replicate read counts from
the original BioProject, derive a cut score from each replicate independently,
and correlate those. Public data, a processing job rather than a wet-lab one.

For range: Cui et al.'s dCas9 CRISPRi screen in the same organism (85,392
guides) ships two measurement arms agreeing at **ρ 0.71** → a ceiling of
√0.71 ≈ **0.84**. Different assay, different conditions, *not* a substitute —
but it suggests the honest range is **0.84–0.90 with 0.90 at the optimistic
end**, rather than 0.90 being a floor.

### Item 3 — seeds, in progress

Adding seeds 42 and 43 to every arm that was seed 41 only: the within-screen
transfer arms (eSpCas9 `arc5`, TevSpCas9 `bin10k`), cross-organism model
transfer, and the hybrid. Running; results to follow.

### Items 5 and 6 — confirmed not actionable

Item 5 (the ≈+0.007 abundance residual) needs local protein-occupancy data that
is not on disk and was not found published for this organism at the required
resolution. Item 6 (a genome-wide screen in a distant bacterium) was searched
for again and still does not exist — what exists outside *E. coli* is CRISPRi,
which measures silencing rather than cutting. Both remain correctly described
in Part 12 as needing data nobody has.

### Item 3 — seeds added to every single-seed arm; nothing moves

Seeds 42 and 43 added to the transfer, hybrid, model-transfer and human arms
(grouped CV is deterministic, so the seed varies the model's own randomness —
subsampling, column sampling, tie-breaking — not the folds).

| conclusion | across 3 seeds |
|---|---:|
| eSpCas9 flank gain (`arc5`) | +0.1040 ± 0.0003 |
| eSpCas9: long-range beats local | +0.0330 ± 0.0003 |
| *C. rodentium* flank gain (`bin10k`) | +0.0587 ± 0.0015 |
| *C. rodentium*: halves equal | −0.0010 ± 0.0002 |
| *E. coli* → *C. rodentium* | 0.6980 ± 0.0033 (92%) |
| *C. rodentium* → *E. coli* | 0.6276 ± 0.0009 (89%) |
| WT → eSpCas9 | 0.6891 ± 0.0003 (87%) |
| eSpCas9 → *C. rodentium* | 0.6556 ± 0.0007 (86%) |
| *E. coli* model on human | −0.0474 ± 0.0014 |
| human model on *E. coli* | −0.0184 ± 0.0087 |
| hybrid prior on top of family A | +0.0011 ± 0.0008 |

**Every conclusion survives.** Largest spread anywhere is 0.009, on the
human → *E. coli* arm whose value is ≈0 either way; every headline is within
0.003 of the seed-41 figure.

**One nuance kept rather than rounded away.** The hybrid prior was +0.0002 at
seed 41; over three seeds it is +0.0011 ± 0.0008 and positive in all three. The
conclusion stands (0.001 is an order of magnitude below the flank effect and
below the ±0.003 ablation floor, so the two sources are redundant, not
complementary) — but the sign is consistent rather than genuinely zero, and
seed 41 happened to be the smallest of the three. Worth saying, because
"+0.0002, i.e. nothing" and "+0.0011 ± 0.0008, consistently positive but
negligible" are different sentences and only the second is accurate.

Housekeeping: `transfer_model.csv` had four duplicate rows from a pair re-run
before the local/long-range decomposition was added; de-duplicated on
(source, target, arm, seed) keeping the later run.

---

## 2026-10-04 — the ceiling assumption falsified, the rule vindicated, and the docs split

New code: `src/sgrna/ceiling2.py`, `diagnose.cross_redundancy`. New data:
`results/ceiling_recomputed.json`, `ceiling_recomputed_folds.csv`,
`cross_redundancy_i_shape_from_a_flank.csv`,
`cross_redundancy_a_flank_from_i_shape.csv`.

### Finding 1 — the two screens behind the ceiling are not replicates, and now we can prove it

**Asked to recompute the ceiling from true replicates.** There are none: the
underlying data is raw reads in SRA (crisprHAL's README names PRJNA450978,
PRJNA939699, PRJNA1260991), so replicate-level scores would mean re-running the
authors' counting pipeline. Tested the *assumption* instead.

The attenuation argument needs the disagreement between the two screens to be
**independent noise**. Systematic effects are predictable; noise is not. So: fit
a model to the rank difference between the WT-SpCas9 and eSpCas9 scores for the
same guide.

| | ρ |
|---|---:|
| predicting the cut score (control) | 0.708 |
| **predicting the disagreement** | **0.546** |

**The disagreement is nearly as predictable as the score itself.** It is not
noise — it is a systematic, sequence-dependent difference between two enzymes
engineered to differ in specificity. ~30% of the disagreement's variance is
systematic.

| assumption | reliability | ceiling |
|---|---:|---:|
| all disagreement is noise (what we assumed) | 0.810 | 0.90 |
| the predictable part is biology | 0.866 | **0.93** |

**Reported as a range, 0.90–0.93** — but the real conclusion is that these two
screens cannot establish a ceiling at all, since they differ in a way that is
neither shared signal nor independent noise, and the shared library biases it the
other way again. A trustworthy ceiling needs same-library, same-enzyme,
independent repeats, which nobody has published.

By-product worth keeping: **WT-SpCas9 and eSpCas9 differ in a sequence-predictable
way at ρ 0.546**, which is a measurable statement about the engineered variant.

### Finding 2 — `i_shape` is a confirmation of the rule, not a counter-example

**Asked:** "is DNA bendability and flank composition related? If one can be
computed from the other, the rule still holds and there is no failure."

Correct. `diagnose.cross_redundancy` regresses one family on another:

| direction | median R² | share > 0.5 | share > 0.9 |
|---|---:|---:|---:|
| `i_shape` from `a_flank` | **0.52** | 51% | 11% |
| `a_flank` from `i_shape` | 0.08 | 21% | 6% |

Asymmetric: composition largely determines shape, not the reverse. So shape is a
**lossy re-description of something already in the model**, and adding +0.001 on
top of flanks is what the rule predicts once it is stated as *"computable from
what the model already has"* rather than *"computable from the 20-mer"*.

**The scored prediction exercise goes from 7/10 to 8/8** (two entries were
reclassified, see Finding 3), and the rule's statement is sharper rather than
hedged. The honest reading of the 0.52: about half of a typical shape column is
not linearly explained by composition, and that half is simply uninformative
about cutting — independently confirmed by the residual test (best shape feature
0.028 against a 0.035 dust level, including the phased-bend component at 0.025
that composition provably cannot express).

### Finding 3 — `h_offtarget` is outside the rule's domain, not a failed prediction

**Asked:** "is there a biological reason why we would expect `h_offtarget` to have
an effect? If not, the finding is equivalent to saying a thing we expect to have
no effect has no effect, which puts it outside the rule's domain."

Right. The rule says when a feature **cannot** help; it never claims new
information **must** help. There is a weak mechanism (off-target cuts kill the
cell and inflate depletion; repeated targets are cut multiple times) but *E. coli*
has few exact repeats and the library was largely chosen for uniqueness, so there
was little room for either. Reclassified as **a documented null**, not a test of
the rule.

### Added to the report rather than discovered

- **Part 2, "How to read the numbers"** — new. Why Δρ ratios do not generalise
  across baselines (on the ρ² scale the same Δρ is worth twice as much at 0.85 as
  at 0.53); the simulated ρ → pick-percentile mapping (0.53 → 73rd, 0.71 → 81st,
  0.90 → 88th, perfect → 91st, so the full range spans only 41 points); ρ versus
  R² with our Huber model (R² 0.192, ρ 0.568) as the demonstration; **single-fold
  ρ SE 0.0122 (±0.024 at 95%) against the paired difference SE of 0.0011**, which
  is why every comparison here is paired; why the *t* and Wilcoxon *p*-values
  differ by two orders of magnitude at n = 5; and an **audit of which numbers have
  error estimates** — the weakest being cross-organism transfer, where each cell
  is a single fit with no interval.
- **Why downstream beats upstream (3.4×)** — split into two length scales. For the
  nearest ~30 nt, enzyme geometry is a plausible cause: Cas9 recognises the PAM
  first, the PAM is downstream, the R-loop propagates away from it, and the
  displaced strand exits on that side. For 250–500 nt it cannot be geometry, since
  Cas9 contacts nothing that far away. Untested hypothesis now written down: the
  asymmetry may be a transcription effect, because genes have a direction — test
  by conditioning on coding vs template strand.
- **The transfer paradox** — how a borrowed model sees what the local screen
  cannot. Every *C. rodentium* guide *has* its ±1 kb flanks from that genome; what
  the screen lacks is **variation between guides**, because all 25,210 sit in one
  229 kb window. A relationship cannot be *estimated* from a predictor that barely
  varies, but *applying* one needs no variation at all. **The sequence is not too
  short, it is too uniform.**
- **What read depth is**, and why it correlated: not causation but a shared
  upstream technical cause — GC and repetitiveness affect both the measured depth
  and the cut score, the latter because the score is itself derived from counting
  reads.
- **How column-column correlation is computed** (Pearson on standardised columns,
  Spearman where named, mean-filling biases sparse columns towards zero).
- **How representative XGBoost vs LightGBM is** — honestly: a sample of two within
  one family. Widened with the random-forest and ridge measurements already on
  file (ridge's faithfulness is **−0.012**, the starkest case), and the
  data-type prediction flagged as testable but untested.
- **More features folded into a single settings section** with tuning: the
  configuration is worth ~+0.010 and the feature budget ~+0.001, against +0.164
  for the right feature set. **Settings are a rounding error next to features.**

### Document split, on request

`docs/PROGRESS_REPORT.md` is now a clean statement of current conclusions with no
inline corrections. All fourteen withdrawn claims and seven bugs moved to
**`local/MISCONCEPTIONS.md`**, which is outside the repo (`.gitignore` added,
since RSI09 is not itself a git repo today but may become one).

Writing them together surfaced something neither document showed separately.
Sorting the fourteen corrections by how they were caught: **5 by an outsider's
question**, 4 by a later experiment, 3 by a control not yet run, 2 by re-deriving
a number that looked settled. In all five of the first category the data needed
was already on disk. **The bottleneck was not measurement; it was that nobody had
questioned a number repeated often enough to feel established.** That belongs in
the methods section.

### Naming

**SLICER** — Simple Lightweight Interpretable CRISPR Efficiency Ranker. Describes
the function, so it survives any one finding; replaces FlankQ and GuideGauge,
both of which named results instead.

---

## 2026-10-04 (afternoon) — 427 of 6,232 columns, and SHAP survives what gain does not

Three questions from outside the project, each cheap to test, each with a result
that changed something. Two hypotheses I formed along the way were refuted by
their own tests; both are recorded here rather than quietly dropped.

### 1. Memory: can a wiser model choice shrink the footprint? Mostly no

`results/memory_comparison.csv`. Peak RSS, threads pinned, each configuration in
its own process:

| configuration | peak | selection | ρ |
|---|---:|---:|---:|
| imports only (floor) | 0.17 GB | — | — |
| dense + XGBoost selector (current) | 3.35 GB | 10.3 s | 0.7009 |
| dense + LightGBM selector | 2.93 GB | 2.0 s | 0.7011 |
| dense→CSR + XGBoost | 3.51 GB | 2.0 s | 0.7009 |
| dense→CSR + LightGBM | 3.64 GB | 1.8 s | 0.7011 |
| streamed CSR (never dense) + LightGBM | **1.98 GB** | 1.8 s | 0.7011 |

The matrix is 10.1% non-zero with 5,957 of 6,517 columns strictly binary, so as
CSR the data is 0.132 GB against 0.81 GB dense. Three lessons:

- **Model choice is worth ~13%** (3.35 → 2.93 GB). Real but small.
- **Naive sparse conversion is worth −5%.** Building the dense array and *then*
  converting costs more, because both live at once. "Use a sparse matrix" sounds
  like a memory fix and is not, unless you never build the dense one.
- **Representation is worth 41%**, at identical accuracy. Not implemented: it
  changes `_impute` and every caller, the same class of change that moved the
  baseline anchor when the selector was swapped. Noted in the report instead,
  per instruction.

Caveat on the prototype: it took column medians from a 6,000-row sample rather
than the full training fold. Accuracy matched anyway.

### 2. Can we give the model one representation instead of several? Yes — 427 of 6,232

`src/sgrna/representation.py`, `results/representation*.csv`. The redundancy
argument was always about *information*; whether the model can be handed less is
a separate claim and had never been tested. The published matrix partitions
exactly — 5,853 indicators + 316 quantum + 63 remainder = 6,232 — so each part
can go through the standard harness alone. 5 seeds × 5 folds, seed SD
0.001–0.003.

| arm | columns | ρ | vs full |
|---|---:|---:|---:|
| `published_full` | 6,232 | 0.5272 | — |
| `mono_di_364` | 364 | 0.5189 | −0.0083 |
| `qct_only` | 316 | 0.5154 | −0.0118 |
| `v_onehot_only` | 5,853 | 0.5119 | −0.0153 |
| `mono_74` | 74 | 0.5081 | −0.0191 |
| `hand_named_only` | 63 | 0.3044 | −0.2227 |
| `mono_74` + `a_flank` | 422 | **0.5462** | **+0.0190** |
| `published_full` + `a_flank` | 6,580 | 0.6080 | +0.0808 |

`published_full` came back at 0.5272 / 0.2934 against the frozen anchor's
0.5273 / 0.2937 — a harness check for free.

**74 columns recover 96.4% of the full matrix**, and they are a lossless encoding
of the 20-mer. **5,853 indicators score below 364 columns** — restatement
dilutes selection. **422 columns beat all 6,232** by +0.019: one family
describing DNA outside the guide outweighs the entire published feature set.

**Refuted hypothesis — redundancy as pre-computed interaction terms.** The
champion is `max_depth=4`; a tetramer indicator states a four-base interaction in
one split, where mononucleotide indicators need four stacked splits. Prediction:
more depth closes the gap. Result (`representation_depth.csv`): it widens it,
monotonically, at every encoding — `mono_74` 0.5081 → 0.4953 → 0.4739 → 0.4557
for depth 4 → 6 → 8 → 12, and the same shape for 364 and 1,510 columns. Explicit
trimers also *hurt* relative to dimers (0.5163 vs 0.5189). Depth only overfits.

**What accounts for it.** The 63 leftover columns are the one part of the matrix
that is not a function of the protospacer — `gene.distance0` is positional, and
the base counts disagree with a direct count by up to 13. Added back
(`representation_residual.csv`): `mono_di_364 + hand_63` = **427 columns at
ρ 0.5249**, against 0.5272 for all 6,232 — paired across five seeds, mean
difference 0.0023, **p = 0.11, not significant.**

So the published matrix is **74 columns of sequence, 63 of something else, and
~6,095 of restatement.** A 427-column drop-in replacement exists. It is also the
real answer to the memory question above: 427 columns is 23 MB where 6,232 is
350 MB, far more than any model choice buys.

**Unexplained, and flagged as such:** `mono_74 + hand_63` is *worse* than
`mono_74` alone (0.5008 vs 0.5081, a 7σ drop), and the sign flips once
dinucleotide indicators are present. The leftover block only helps on top of a
representation that already carries pair structure. No account offered.

### 3. Do other models rank features the same way, and does SHAP help? Yes, and yes — reversing a prediction

`src/sgrna/importance_models.py`, `results/importance_model_*.csv`. Seven model
families (XGBoost, LightGBM, CatBoost, random forest, extra trees, ridge, elastic
net), three methods, 3 folds, pairs matched to SHAP's coverage so the methods are
compared on identical pairs.

| method | ρ between models, per column | per block |
|---|---:|---:|
| native (gain / impurity / standardised coef) | **0.050** | 0.531 |
| permutation | 0.258 | 0.581 |
| **SHAP** | **0.496** | **0.800** |

**The column-vs-block result holds and widens.** It now covers bagged forests
(independent fits, not residuals) and penalised linear models (no selection step
at all). The instability is a property of the matrix, not of boosting. This
closes the gap the previous log entry flagged as "testable but untested".

**Refuted prediction — that SHAP would fail the same way.** Recorded before
running: Shapley values divide credit for one prediction among its inputs, so two
columns carrying identical information should split it arbitrarily. Wrong.
XGBoost vs LightGBM: **−0.070 by gain, +0.867 by SHAP** (block 0.590 → 0.984).

The mechanism is visible, and it retires a published-in-this-report result:

| share of importance on binary indicators | native | SHAP |
|---|---:|---:|
| XGBoost | **57.4%** | **31.0%** |
| LightGBM | 29.7% | 31.0% |
| CatBoost | 27.3% | 25.1% |
| random forest | 16.0% | 24.0% |
| extra trees | 46.3% | 47.4% |

**The "data-type affinity" axis — XGBoost leaning on binary indicators, LightGBM
on continuous ones — is an artefact of split gain.** XGBoost's share halves under
SHAP and lands on LightGBM's figure exactly. Gain credits fit improvement at
split time, over-rewarding a binary column used in many shallow nodes; SHAP
measures effect on the output. Seven models spanning 0.08 ρ fit nearly the same
function, so measuring the function instead of the fitting procedure makes them
agree.

Under SHAP all five tree models lead with the same two blocks: flank quantum
within 10 nt (≈14%) and protospacer dinucleotide quantum (≈13%); the 3,383
middle-position indicators carry ≈10% between them.

**Consequence.** "Never read mechanism off an importance plot" narrows to **never
read it off gain**. 0.496 per column is substantial, not unanimous, so claims
still belong at block level — but a SHAP ranking is reproducible across model
classes in a way a gain ranking is not, which makes it usable rather than merely
cautionary. Added to Part 12 as a next step: regenerate the importance figures
with SHAP.

### The pattern in today's two refutations

Both wrong hypotheses were mechanistically plausible, specific, and cheap to
test, and both were wrong in the same direction: **they assumed the model's
behaviour was about the data when it was about the measurement.** Depth did not
explain the encoding gap because the gap was an artefact of which columns were in
the arm; gain did not explain attribution because gain is an artefact of split
accounting. The habit worth keeping is not "guess better" — it is that both took
under half an hour to settle, so guessing was cheap.

### One process note

The report was rewritten concurrently by another session while this work was in
progress, and an earlier version of the memory note was lost to that overwrite —
reported as applied when it was no longer in the file. It has been reapplied to
the new structure. The parked-tooling note was also dropped in the rewrite and
has been restored. **When two sessions edit one document, verify the file after
writing, not just the write.**

---

## 2026-10-04 (evening) — SHAP adopted, the asymmetry loses its best explanation, and two memory claims withdrawn

### 1. The importance figures regenerated with SHAP

Running `attribution.py` and `evaluate.py --what interpretability` through SHAP
instead of split gain changes two reported tables and one recommendation.

**The "two models prefer different kinds of column" table collapses**
(`attribution_summary_shap.csv`):

| kind of column | gain: XGB | gain: LGBM | SHAP: XGB | SHAP: LGBM |
|---|---:|---:|---:|---:|
| position/letter indicators (binary) | **49%** | 18% | 21% | 21% |
| quantum descriptors (continuous) | 19% | **33%** | 29% | 29% |
| flank, nearest 10 nt | 11% | 17% | 22% | 22% |
| other published columns | 12% | 6% | 18% | 19% |
| flank windows, downstream | 4% | **14%** | 5% | 5% |
| flank windows, upstream | 4% | **12%** | 4% | 4% |

Largest between-model gap on any kind of column: **31 points under gain, 0.3
under SHAP.** Shared columns in the two top-50s: **14 → 41.**

**The interpretability table changes a decision** (`interpretability.csv`, now
carrying an `importance` column):

| model | importance | stability | method agreement | features for 50% |
|---|---|---:|---:|---:|
| XGBoost | gain | 0.49 | −0.02 | 330 |
| XGBoost | **SHAP** | **0.75** | **+0.39** | **44** |
| LightGBM | gain | 0.72 | +0.44 | 151 |
| LightGBM | **SHAP** | **0.74** | **+0.40** | **43** |

**Changing the method helps more than changing the model**, and the reason to
prefer LightGBM for interpretability disappears — which is convenient, since the
frozen baseline anchor wants XGBoost. Recommendation 1 in RESULTS §12 reversed
accordingly. Ridge remains the outlier: faithfulness −0.004, still spreading
importance over >1,200 columns, so neither its coefficients nor their Shapley
equivalent are an explanation.

`shap_importance()` now lives in `importance.py` and all three modules call it.

### 2. The downstream asymmetry is not a transcription effect

`src/sgrna/asymmetry.py`. Part 12 listed this as cheap. Half of it is impossible.

**The orientation test cannot be run on this screen.** Verified two independent
ways — guide index joined to the gene table, and `g_transcription`'s own
separately-derived column — the library targets the gene's **template strand for
13,825 of 13,879 guides, 4 exceptions.** No variation, no test. Which also means
`eng.txn.gene.template_strand` is a near-constant column, part of why that family
managed only +0.015.

**The expression test runs, and the asymmetry is flat:**

| band | baseline | Δρ up | Δρ down | Δρ down, count-matched | asymmetry |
|---|---:|---:|---:|---:|---:|
| low | 0.4733 | +0.0296 | +0.0782 | +0.0790 | 0.0486 |
| mid | 0.4802 | +0.0177 | +0.0635 | +0.0604 | 0.0458 |
| high | 0.4836 | +0.0177 | +0.0656 | +0.0539 | 0.0479 |

The account predicted a gradient; there is none. One seed per band, so this rules
out a gradient rather than proving independence.

**A control the original sides split never had.** Family A has 194 downstream
columns against 144 upstream, so up to a third of the downstream advantage could
have been column budget. A count-matched downstream arm (144 of the 194 at
random) gives +0.0790 against +0.0782. **It is the side, not the budget.**

### 3. The reduced 427-column set creates no blind spot

`representation.run_headroom`, answering a direct question: how do we know the
model is not simply failing to use what it has, and does that survive the
reduction?

| model | out-of-fold ρ | max \|ρ\| with residuals, columns it has | columns dropped |
|---|---:|---:|---:|
| all 6,232 | 0.531 | 0.028 | 0.147 *(family A, held back)* |
| the 427 | 0.525 | 0.022 | 0.146 *(family A, held back)* |
| 427 + family A | 0.597 | 0.028 | **0.070**, none above 0.10 |

**Dropping 5,805 columns did not change what the model is missing** — same
family-A column, same magnitude. With family A in, the dropped columns top out at
0.070: under the 0.10 threshold but 2.5× the best among the kept columns, and the
leaders are `V####` higher-order k-mer indicators. So a sliver of higher-order
sequence signal exists, consistent with the −0.01 ρ cost, and the depth ladder
already showed why taking it loses money.

Worth stating as method: the residual test is trustworthy **because it has a
demonstrated positive control** — it flagged family A at 0.147 before family A
was added, and family A was then worth +0.080.

### 4. Two memory claims withdrawn, and the measurement rebuilt

The original memory figures came from a script that was never in the repo, which
is why they could not be extended. Rewritten as `src/sgrna/bench.py`: every
repetition in a fresh process, `ru_maxrss`, threads pinned, three repetitions.

**Withdrawn: "model choice is worth ~13% of peak memory."** Two single-shot runs
of the *identical* configuration returned 2.95 and 3.29 GB. Run-to-run spread is
~0.3 GB, the same size as the gap being claimed. The selectors are
indistinguishable on memory; LightGBM's win is 5× on selection time.

**Withdrawn: "427 columns is 23 MB against 350 MB."** That was arithmetic on the
stored matrix, not a measurement of the pipeline, and the pipeline does not
deliver it — subsetting columns after loading saves 14%, because peak RSS is set
by the load.

**What replaced them** (`memory_comparison.csv`, median of 3):

| configuration | columns | peak | selection | ρ |
|---|---:|---:|---:|---:|
| imports only (floor) | — | 0.17 GB | — | — |
| all columns + XGBoost | 6,517 | 3.33 (3.23–3.68) | 12.0 s | 0.6939 |
| all columns + LightGBM | 6,517 | 3.05 (3.05–3.05) | 2.4 s | 0.6945 |
| reduced, subset after loading | 712 | 2.83 | 1.4 s | 0.6823 |
| **reduced, stored reduced** | 712 | **0.65** | 1.4 s | 0.6823 |

**5× less memory, if the reduced matrix is what gets stored.** Also corrected:
the 4.03 GB in the cost table came from one process running both selectors, and
`ru_maxrss` is a high-water mark, so it belonged to neither.

One bug caught before it was believed: the stored-reduced arm first scored ρ 0.532
instead of 0.68, because the flank block was joined on `sgRNAID` while the
expanded dataset is keyed by protospacer — every flank column came back NaN and
was dropped. Fixed to read the same curated block `_assemble` uses.

### 5. Does a neural net get cheaper on the reduced set? Depends which net

| | columns | parameters | train | ρ |
|---|---:|---:|---:|---:|
| dense net, all columns | 6,517 | 1,685,121 | 6.1 s | 0.6413 |
| dense net, reduced columns | 712 | 199,041 | **1.4 s** | 0.6401 |

4.4× faster, 8.5× fewer parameters, accuracy unchanged — almost all of a dense
net's parameters are in its first layer. **But the sequence CNN gains nothing:**
`seqnet.py` and crisprHAL 2 read raw flanking DNA and never touch the feature
table, so their cost is epochs × convolutions over sequence length. For the
architecture this project competes against, the reduction is not a speed-up.

### 6. The report restructured

Parts 1 and 2 were written to answer questions from inside the project and had
become a textbook. Part 1 is now **six places where a reader who knows the
background still gets this dataset wrong**; Part 2 keeps the three metric facts
that changed a conclusion here plus the error-bar audit. The Spearman tutorial,
the paired-test derivation and the correlation formula are gone — background
knowledge replaces them, project-specific traps it does not. ~100 lines shorter
with no finding dropped.

Also fixed: Part 10 still described the human GC U-shape as a literature claim
"we have not tested" while RESULTS §15 had the measurement. The report now
carries the measured version.

### The pattern worth keeping from today

Four claims were withdrawn and every one had the same cause: **a number measured
once, in a process that was doing something else at the same time.** The 4.03 GB
shared high-water mark, the single-shot selector ranking, the arithmetic
substituting for a benchmark, and the stored-subset ρ that was really a dropped
join. Timing already had the fix on file — separate processes, pinned threads,
repetitions — and it was not applied to memory until it produced a wrong answer
twice. **Apply a precaution to every measurement of the same kind, not only to
the one that embarrassed you.**

---

## 2026-10-04 (night) — faithfulness re-measured, the inherited model replicated, both searches scaled up

### 1. The faithfulness probe was measuring the matrix, not the ranking

Prompted by a direct question: dropping a model's top 20 columns costs nothing —
but those 20 columns might all be spellings of the same quantity, so what does
the test actually show? Answer: on this matrix, nothing about the ranking.

`src/sgrna/faithfulness.py`, 3 folds, XGBoost and LightGBM averaged, SHAP-ranked,
every arm refitted from scratch:

| dropped and refitted | full, 6,580 cols | reduced, 775 cols |
|---|---:|---:|
| top 20 | −0.0024 | **−0.0150** |
| 20 at random | +0.0015 | −0.0006 |
| top 50 | −0.0102 | **−0.0453** |
| 50 at random | −0.0008 | −0.0015 |
| top 100 | −0.0226 | **−0.0816** |
| 100 at random | +0.0016 | −0.0054 |

**The normalisation is the whole argument, and the obvious one is wrong.** Twenty
columns is 0.3% of the full matrix and 2.6% of the reduced one. Matching on
column *fraction* makes it worse rather than better: the top 170 of 6,580 (also
2.6%) costs −0.027, but removes **80%** of attributed importance against 35% for
20 of 775. Matching on **share of importance removed** is the comparison that
means something (`faithfulness_shap_share.csv`):

| | top 20 | top 50 | top 100 | columns for 50% of SHAP |
|---|---:|---:|---:|---:|
| full, 6,580 | 34.6% | 53.1% | 68.6% | 44 |
| reduced, 775 | 37.5% | 57.5% | 73.8% | 37 |

At a matched ~35% of the explanation removed, the full matrix loses 0.002 and the
reduced one 0.015 — **six times the damage.** The two concentrate importance
almost identically (44 and 37 columns for half), so this is not about how peaked
the attribution is; it is about whether the information is reachable elsewhere.

**Withdrawn:** "the decisive check says neither model has found the true
features." It was confounded by the redundancy the rest of the project measures.
A faithfulness number computed on a redundant representation describes the
representation.

**A related negative result.** Clustering columns by |r| ≥ 0.7 around each
model's top SHAP columns gives clusters of **1–3 columns** — the leading columns
have almost no close twins — and removing the top five clusters (10–11 columns,
**19% of total SHAP**) still costs nothing on the full matrix. So the protective
substitution is **not pairwise**: a tree rebuilds the function from many
weakly-correlated columns, which is why pairwise correlation only ever put a
floor under replaceability.

### 2. Noshay et al.'s own model, run here

`src/sgrna/noshay_replicate.py` — iRF as their methods section specifies it:
1,000 trees per forest, ten iterations, five-fold CV, full 6,232-column matrix.
Reimplemented from the published algorithm (their Ranger build is not used).

| | Pearson | R² | Spearman |
|---|---:|---:|---:|
| their Table 1 | 0.5019 | 0.2491 | not reported |
| our run | **0.4881 ± 0.0119** | **0.2345 ± 0.0102** | **0.4785** |

**Within 0.014 Pearson on a third of their rows** — Table 1 used 40,468 sgRNAs,
the released matrix covers 13,880 — so the reimplementation is faithful, and it
supplies the Spearman their paper never reported, which is what the comparison
table needed; it had been quoting a Pearson in a Spearman column.

**The like-for-like comparison this buys.** Same 13,880 rows, same 6,232 columns,
same folds: their iRF **0.479**, our gradient-boosted baseline **0.527**. So
**+0.049 from the learner alone**, before any new feature, and family A adds
+0.080 on top of that. Cost: **6.2 min/fold against 17 s**, 2.2 GB against
3.3 GB — 22× the time for 0.049 less ρ. Consistent with the redundancy result:
iterative reweighting has no deep interaction structure to amplify when the
matrix is a re-spelling of 20 letters.

### 3. Both hyperparameter searches scaled to convergence

crisprHAL 2's settings had never been searched, which is why the +0.0107 margin
was never claimed as a win. Both sides now search until they stop improving, with
the curve recorded so the claim is checkable rather than asserted.

- **SLICER** (`tune.py`): 300-draw ceiling per fold, patience 80, every draw
  written to `tuning_trace.csv` with best-so-far. The previous 12-draw result is
  archived as `tuning_trials12.csv` — it is the +0.0103 currently quoted.
- **crisprHAL 2** (`crisprhal_tune.py`): 40-draw ceiling, patience 12, 13-hour
  deadline, then the winner on all five outer folds. Draw 0 is their published
  configuration exactly, so the search cannot report them below their own paper;
  it scored inner ρ **0.6924** in 17.1 min.

**The asymmetry has to be quoted with the result.** SLICER searches inside every
fold; crisprHAL searches one inner 80/20 split of fold 1's training rows, because
each of its fits costs ~17 min. Theirs is the weaker search. If it closes the
gap, parity is the conclusion and the weak search strengthens it; if it does not,
the asymmetry is a live caveat.

**What is being tuned, precisely.** SLICER: nine LightGBM knobs (`n_estimators`,
`learning_rate`, `num_leaves`, `max_depth`, `min_child_samples`,
`colsample_bytree`, `subsample`, `reg_lambda`). crisprHAL: thirteen of their
constructor's arguments (learning rate, CNN filters and window, three dropout
rates, four dense widths, GRU width, epochs, batch size). Their **architecture is
fixed** — four conv blocks plus a bidirectional GRU branch concatenated into a
linear output, Adam with clipnorm 0.5, MSE, their own 378-nt one-hot encoding.
Changing those would stop it being their model.

**And it is tuned on their own data.** The 33,567 guides are their WT-SpCas9
train+test files deduplicated by protospacer, with their 378-nt context, and the
label is **bit-identical** to theirs (verified: all 33,567 matched,
`np.allclose` true). Only the *split* differs — our 5-fold CV instead of their
single shipped hold-out — which is what makes the comparison against SLICER
paired. `crisprhal_rerun --arm their_split` separately confirms the harness
reproduces their own hold-out at 0.6940 against a published 0.695.

### 4. Two reporting ambiguities fixed

**Which library is "the champion".** The report had been saying XGBoost without
qualification. There are two configurations: the **baseline** on 13,880 published
rows is XGBoost (ρ 0.5278), because that is what reproduces the published figure;
the **curated head-to-head** is LightGBM as predictor with XGBoost selecting
columns (ρ 0.7078), and the +0.0103 tuning gain is therefore a LightGBM result.
They differ by ≤0.001 wherever both were run, so nothing substantive turns on it,
but a reader tracking a number needs to know which produced it. Stated once in
Part 3 and used consistently.

**The selector-swap figure.** "+0.0008, indistinguishable" is one arm's number.
Across arms the swap is −0.0027 on the baseline, −0.0002 with the flank family,
+0.0014 on curated. The pattern is that the selector matters most where the
features matter least — thin signal spread over interchangeable columns makes the
choice of 300 partly luck — which is consistent with the redundancy result but
has not been tested separately, and is flagged as such.

### A process note worth keeping

Three failures tonight, all of the same kind: **a job that reported success
without doing the work.**

1. The crisprHAL search crashed on a `TypeError` in the line that *writes* the
   result row, immediately after a 50-minute fit. Nothing was saved. The fix is
   not the bug fix — it is that the write path is now validated end-to-end at one
   epoch before any long run starts.
2. SLICER's 300-draw search "completed" in zero seconds, because `tune.py`
   resumes by `(arm, fold)` and all five folds were already recorded from the
   12-draw run. The log said `stage 1 done`.
3. The overnight queue stalled on its own guard: `pgrep -f "[s]grna.faithfulness"`
   treats `.` as any character, so it matched a shell whose command line
   contained `sgrna/faithfulness.py`.

**A no-op that looks like success is worse than a crash.** All three were caught
by checking the output rather than the exit status, and the standing lesson is
the one already in this file in a different form: verify the write, not the call.

---

## 2026-10-05 — crisprHAL 2 tuned: the margin survives, and widens

The last open item that could move a headline. Both models are now searched, so
the comparison is no longer tuned-against-untuned.

| | default | tuned | gain | folds |
|---|---:|---:|---:|---|
| crisprHAL 2 | 0.6971 ± 0.0067 | **0.7051 ± 0.0092** | +0.0080 | 5/5, p = 0.018 |
| SLICER | 0.7082 | **0.7212 ± 0.0016** | +0.0131 | 5/5, p = 0.0001 |

| paired, by fold | mean | folds | paired *t* |
|---|---:|---:|---:|
| untuned | +0.0111 | 5/5 | p = 0.0002 |
| **both tuned** | **+0.0161** | **5/5** | **p = 0.0003** |

**Tuning both widens the margin**, 0.0111 → 0.0161. The standing objection —
that the lead might only reflect whose defaults suited this screen — is answered.
The claim moves from *parity* to **a small, consistent lead**.

Their winning configuration against their published one: learning rate halved,
convolutions and recurrence wider (128 → 192 filters and units, recurrent dense
128/64 → 256/128), more dropout on the CNN and fusion branches (0.3 → 0.4), 64
epochs instead of 48, batch halved. Coherently "bigger, slower, more
regularised", and 3–4× the fit cost — 21 → 69 min per fold, so their accuracy
gain makes the cost comparison worse for them at the same time as it narrows the
accuracy one.

### The asymmetry, and a measured bound on it

SLICER ran **627** configurations across five folds; crisprHAL ran **10** on one
inner split, because one of its fits costs ~1,000× one of ours. Rather than
hand-wave that, SLICER's own trace says what a 10-draw budget would have found
for us:

| draws | share of total tuning gain captured |
|---:|---:|
| 5 | 47% |
| **10** | **66%** |
| 20 | 74% |
| 40 | 100% |

At 66%, crisprHAL's converged gain would be ≈ +0.012 and its tuned score ≈
0.709 — a lead of ≈ 0.012 rather than 0.016. Erasing it needs +0.024 from their
tuning, three times what was found. **So the correction shrinks the margin by
about a quarter without removing it**, and that is the honest way to report a
search we could not run at equal size.

### A recommendation I made and then had to withdraw

Mid-run I argued that crisprHAL's +0.0088 might be mostly selection noise from
taking the best of ten draws, and that seed-repeats were the priority. **The
outer-fold result had already settled it**: the chosen configuration generalises,
+0.0080 on held-out folds in 5 of 5, p = 0.018. The inner-split figure may be
slightly optimistic, but the tuned score is an honest held-out measurement, so
the experiment I proposed would have answered a question the data had answered.
Recorded because the error is instructive: **I reasoned about what the numbers
could not tell us without first checking what they did.**

### The process failure that cost the most

Two crisprHAL searches ran **concurrently for nearly seven hours**. When
`queue2.sh` was replaced by `queue3.sh`, killing the queue shell left its python
child running, and a second search started alongside it. Consequences:

- Fit times inflated 2–4× (draw 0 alone: 17 min; the same class of configuration
  contended: 43–70 min), which I then **misexplained to the user as larger
  configurations being intrinsically slower**, and separately asserted that the
  search "now has the machine to itself" without checking `ps`.
- The search stopped at 10 draws on a 7-hour deadline belonging to the process I
  thought I had killed, while the 13-hour one was still running.

The accuracy numbers are unaffected — every draw is a legitimate fit on the right
data — but the timing commentary was wrong and had to be retracted. **Managing
processes by pattern-killing their parents is not managing processes.** Verify
with `ps` that what you intended to stop has stopped, and that what you intended
to be alone is alone.

### Could a GPU settle it outright? Yes, for tens of pounds

Matching SLICER's 627 fits for crisprHAL is ~460 h on these ten cores, which is
where a £20–50 rental estimate came from. **That estimate was built on the wrong
premise and has been withdrawn.** The trace analysis in this same entry says 40
draws captured 100% of SLICER's gain — the other 587 confirmed a plateau — so an
equal-footing search means running *their* search to *their* patience criterion,
about **55 fits**. Their model is small (four 1-D convolution blocks plus a
bidirectional GRU over 378 bases), so at 3–5 min per fit on a rented T4 or L4
that is **2–4 GPU-hours: one free Colab session, no spend at all.**

The error is worth recording on its own: I derived "40 draws is enough" and then
budgeted for 627 in the next paragraph. **An estimate has to be rebuilt when the
analysis that feeds it changes, not carried forward from the first framing.** **A TPU would be the wrong instrument**: TPUs pay off on
large dense matmul under XLA, and a sequential GRU loop is the shape that maps
worst onto them.

It would convert the extrapolation into a measurement on equal footing. It would
**not** change the conclusion, and **not** change the cost comparison, which is
already labelled CPU-to-CPU — running their model on the hardware it was designed
for would make our speed advantage look smaller and the write-up more credible.

**And the headline does not depend on it**, which is the real answer to whether
it needs funding. The primary comparison should be untuned-against-untuned
(+0.0111, 5/5 folds), because defaults are what a user installing either tool
gets, and that comparison carries no search-size caveat at all. The tuned
comparison is a robustness check — it shows the margin is not a defaults
artefact — and 10 draws against 627 is adequate for that. **Re-tuning is only
required when rows, label or folds change** (both models) **or the feature set
changes** (SLICER only); documentation and analyses outside the curated arm
require none. So: tune once, at freeze, free.

---

## 2026-10-05 (later) — the ceiling was too low, and the correction came from a teammate

Jacky's work plan challenged two things in Part 10. Both challenges were right.
Verified against Guo et al. 2018 (*NAR* 46:7052) rather than taken on trust,
because Jacky's own note marked the figures "verify".

### 1. "A trustworthy ceiling needs replicates nobody has published" — wrong

Confirmed from the paper: **two biological replicates per condition, by
independent transformation**, and the read counts "were averaged as the geometric
mean". So the replicates were run, their agreement *was* published, and — the
part this report had missed entirely — **the label we train on is already a
two-replicate average.**

That breaks the old arithmetic in two places at once. The attenuation bound
applies to predicting *one noisy observation*; our target is a mean of two. Under
Spearman–Brown a 2-item mean has reliability `2r/(1+r)`, which is **higher** than
`r`. The two-enzyme estimate had erred in both directions simultaneously: it
treated enzyme biology as noise (which `ceiling2.py` had already disproved,
ρ 0.546) while ignoring that the target is an average.

| route | published statistic | r | reliability | ceiling |
|---|---|---:|---:|---:|
| **tiling library (Fig 2c)**, 901 shared guides, a *different* library | R² = 0.771 | 0.878 | 0.878 | **0.937** |
| replicate agreement (Fig 2b) + Spearman–Brown | R² > 0.78 | >0.883 | 0.938 | **0.969** |
| colony counting (Fig 2d), 15 sgRNAs | R² = 0.840 | 0.917 | 0.917 | 0.957 |

**Revised: ≈0.94–0.97, not 0.90–0.93.** Lead with the tiling figure — it is a
test–retest of the exact published quantity using a different library, which is
precisely the objection the two-enzyme estimate could never answer, and it is
conservative because library design differences are not label noise.

Three caveats keep it a range: the published values are Pearson R² on read-count
scale while the ceiling is quoted in Spearman; Fig 2b is an inequality across ten
libraries, so 0.883 is a floor; and the Spearman–Brown step assumes the activity
score inherits the read counts' reliability, which is the weakest link in the
chain.

**Consequence: SLICER at 0.707–0.721 is 74–77% of the way, not ~80%.** The
headroom is *larger* than claimed, which makes the saturation results in Part 10
more interesting, not less — the model stops improving well short of a limit that
is further away than we thought.

### 2. "The orientation test is impossible on this screen" — too strong

`asymmetry.py --audit` found 13,825 of 13,879 guides on one strand and I
concluded the transcription-orientation test could not be run. Jacky's reading is
better: that is the **coding** sub-library, repurposed from a CRISPRi design that
binds one strand by construction. The paper's Methods say of the intergenic
library: *"the sgRNAs were designed to target either of the two DNA strands in
this new library, in contrast to the sgRNAs in our previous library, which bind
only the nontemplate strand."* Verified coverage: **10,257 intergenic sgRNAs** —
5,559 across 3,146 promoters and 4,698 across 4,140 RBSs.

So the test has a population, if those guides survive into Guo's high-quality
Cas9 set (Table S10). It would be weaker than the one originally designed —
orientation relative to the adjacent operon rather than a host gene — but it is
not impossible, and Table S10 is a download rather than a computation. That makes
it the highest-value item on Jacky's data checklist.

### The pattern, which is the one already in this file

Both corrections came from **reading the source paper more carefully**, not from
new computation. The ceiling error in particular is the fourth time this project
has been caught by a number that felt settled: the data needed was in a figure
legend of a paper we had already cited. And both arrived from **outside the
work** — the single largest category in `local/MISCONCEPTIONS.md`. The remedy is
not more measurement, it is that someone who has not been staring at it reads the
claim and asks where it came from.

---

## 2026-10-10 — Jacky's intergenic result re-opens the transcription account; the two ceiling routes compared

### 1. The orientation test runs after all, and the asymmetry depends on orientation

I had concluded the transcription-orientation test was impossible: 13,825 of
13,879 guides in the published matrix sit on the gene's template strand. That was
true **of the matrix** and false as a general claim, which Jacky's work plan
caught and Jacky's agent then acted on.

The coding sub-library binds one strand because it was repurposed from a CRISPRi
design. The **intergenic** sub-library was built to target either strand (10,257
guides: 5,559 over 3,146 promoters, 4,698 over 4,140 RBSs) and is **not in the
published feature matrix**, so features had to be rebuilt from the genome. 8,954
located, flanks cut with family A's recipe, orientation against the nearest gene,
grouped CV by 100 kb bins:

| stratum | n | upstream | downstream matched | asymmetry |
|---|---:|---:|---:|---:|
| all intergenic | 8,954 | +0.081 | +0.115 | **0.034** |
| opposite the nearest gene | 4,361 | +0.061 | +0.108 | **0.047** |
| same way as the nearest gene | 4,593 | +0.102 | +0.107 | **0.005** |

Stricter set (Data S4 HQ, n = 3,645): 0.064 against −0.015.

**That is what a transcription account predicts and the opposite of what pure
PAM/R-loop geometry predicts**, which should be flat across orientation.

**Holding this together with our own flat expression-band result.** They are not
in conflict: expression *level* and *orientation* are different variables, and
only the second is what an "asymmetric DNA around a transcription unit" account
requires. The simplest reading is that the effect tracks the **geometry** of the
local transcription unit rather than its **traffic**. Caveats for the paper:
orientation is vs nearest gene rather than a curated operon annotation;
intergenic targets are promoters and RBSs, a different context; one seed, no
bootstrap on the orientation difference; and it does not separate polymerase
traffic from other gene-asymmetric features.

Also closed by the same batch: **the asymmetry is not the replication fork** — no
sign flip between replichores (0.0493 left, 0.0483 right).

### 2. Which ceiling estimate is better — theirs or mine

Both use Guo's published agreement statistics; they lead with 0.968 (Fig 2b
replicate agreement + Spearman–Brown), I led with 0.937 (Fig 2c tiling library).
The two are not equally safe and the error directions are known.

**Their route needs the activity score to inherit the read counts' reliability,
and it cannot.** Guo's label is the `|Z|` of a **Cas9/dCas9 ratio** — two count
measurements. A difference is never more reliable than its components, and how
much less depends on how much true signal the two arms share. The dCas9 arm
exists precisely to share the library-abundance structure, so that fraction is
large. Taking each log-count's reliability at the Fig 2b floor of 0.883:

| shared signal between arms | ratio-score reliability | ceiling |
|---:|---:|---:|
| 0% (what their route assumes) | 0.883 | **0.968** |
| 30% | 0.841 | 0.956 |
| 50% | 0.791 | **0.940** |
| 70% | 0.694 | 0.905 |

**0.968 holds only if the control arm shares nothing with the treatment arm**,
which is the one thing it is designed not to do. Upper bound, plausibly loose.

**The tiling route needs none of that machinery.** Both sides of Fig 2c are
already the published score, so r = 0.878 *is* its reliability — no count-noise
propagation, no Spearman–Brown, no assumption about the ratio. Sampling error on
901 guides gives r ∈ [0.863, 0.893], so **ceiling 0.937 [0.929, 0.945]**, and its
bias is conservative (a different library adds design variance that is not label
noise).

**Verdict: quote ≈0.94 as the working figure with 0.94–0.97 as the range**, and
label which is which. SLICER at 0.707–0.721 is ~77% of the working figure. The
substantive agreement with Jacky stands — the old 0.90–0.93 bracket was too low
and "replicates nobody published" was wrong — the disagreement is only about
which published statistic to lead with.

### 3. Pipeline modules reconciled

Jacky's agent modified three modules in `Runjia/sgrna/`, which their follow-up
report says were "not pushed unless you ask" — they were pushed. Checked all
three: **purely additive and backwards-compatible.** `cross_validate` gains an
opt-in `return_oof=False`; `transfer.build` backfills `protospacers` into cached
meta; `evaluate.py` gains four helpers (grouped/ungrouped bootstrap CIs,
within-gene ρ, within-gene pick-percentile). Nothing reported in the progress
report is affected.

One of their changes **fixes a bug of mine**: `transfer.model_transfer` computed
`src_p` and then never used it, so `guide_overlap` was hard-coded NaN in every
row of `transfer_model.csv`. It now computes the real overlap. The column was
only ever a diagnostic, so no reported number changes — but it was dead code that
looked live, which is the class of error this project keeps finding.

Adopted all three into `src/sgrna` so the next sync does not silently revert
them. **Lesson for a shared package: a teammate's additive change to your module
is a merge you have to perform, not a conflict you can ignore** — I would have
reverted all of it on my next `cp`.

---

## 2026-10-10 (later) — four questions from outside, one withdrawn claim, one artefact caught

### 1. Withdrawn: "4.2× from the same DNA"

The CNN-versus-hand-features comparison is **not matched on input**. `seqnet.py`
was given **±100 nt**; family A's windows run to **±1,000 nt** (50/250/500/1,000
each side). So part of the hand features' advantage is simply more sequence, and
the phrase "from the same DNA" was false. Worse, `sequence_context.csv` caches
only ±250 nt, so **the matched test cannot be run without rebuilding that
cache** — it has never been run.

What survives, and needs no comparison: splitting family A by distance gives
**+0.049 from the ±10 nt** and **+0.026 from the 50–1,000 nt windows**, so about
a third of the gain lies beyond anything a 378 nt input can reach at all. That is
a statement about where the signal is, not about who extracts it better.

The report now carries a ⚠️ on the passage and the narrowed claim. **Nothing
here shows a representational limit for CNNs** — only that hand-computed windows
inject the uniform-average prior for free while a network would have to learn it
from 33,567 noisy examples against a +0.08 effect.

**Caught by:** being asked "doesn't that mean the CNN doesn't have access to the
same information, making the comparison invalid?" It does, and it did.

### 2. Additivity holds on the reduced basis — and redundancy was hiding it

`results/additivity_reduced.csv`, 5 folds, no selection step:

| columns | ridge | LightGBM | XGBoost | boosting − ridge |
|---|---:|---:|---:|---:|
| **427** (mono+di+hand) | 0.5029 | 0.5258 | 0.5255 | **+0.0230** |
| **775** (+ family A) | 0.5618 | 0.5993 | 0.5962 | **+0.0375** |
| 6,232 (base only) | 0.4233 | 0.5298 | 0.5267 | +0.1064 |
| 6,580 (+ family A) | 0.4941 | 0.6100 | 0.6070 | +0.1160 |

On 427 columns ridge reaches **95.6%** of boosting's ρ, consistent with the
original top-300 figure. Two new things:

**Ridge on the raw matrix collapses to 0.423.** That is collinearity across
thousands of near-duplicate columns, not biology. So the redundancy was
*concealing* additivity from the linear model, not creating the appearance of it
— removing it is worth **+0.08 to ridge**. Worth stating because it reverses the
intuition: the honest version of "a linear model gets close" is *a linear model
gets close once you stop feeding it 6,232 restatements*.

**The gap widens when family A is added** (0.023 → 0.038), so the flanking-DNA
columns carry proportionally more non-additive structure than the protospacer
columns do. New and unexplained.

### 3. An artefact I nearly reported as a finding: iRF on the reduced set

First run looked dramatic — iRF **0.275** on 427 columns against **0.495** on
6,232, i.e. "iRF needs the redundancy". It is an artefact of my own
implementation. `_grow` draws `mtry` columns **once per tree** and grows the whole
tree in that subspace, rather than resampling candidates per split as a real
random forest does. The iRF reweighting requires the candidate set to be chosen
externally, so that is the natural implementation — but it means **absolute
`mtry` sets tree capacity**, and `sqrt(p)` is not portable across matrices of
different width (`results/irf_mtry_sweep.csv`):

| columns | mtry | ρ |
|---:|---:|---:|
| 427 | 20 = √427 (the default) | **0.2749** |
| 427 | 78 = √6232 (matched) | **0.4892** |
| 427 | 200 | **0.5010** |
| 427 | 427 (every column) | 0.4974 |
| 6,232 | 78 | 0.4950 / 0.4860 |

The completed sweep settles it further: the curve is **flat from 78 upward** and
peaks near half the columns, so the collapse at 20 is a starved-tree effect, not
a property of the basis. Giving every tree all 427 columns is no better than
giving it 200, which is what you expect once subspace randomisation stops being
the binding constraint.

**At matched absolute `mtry`, iRF does the same on 427 columns as on 6,232.** The
reduced basis is fine; the reweighting simply has no haystack left to search.
0.21 of Spearman separated two runs of the same algorithm on the same
information, purely from how many columns each tree could see. Warning written
into `noshay_replicate.py`'s docstring: compare iRF across column counts at
matched absolute `mtry`, never at matched sqrt(p).

**The near-miss is the lesson.** The first number was plausible, had a tidy story
("iRF needs many columns to reweight among"), and was wrong. What caught it was
asking *why* before writing it down.

### 4. Pipeline merge, and the Guo ceiling disagreement

Jacky's three additive edits to `Runjia/sgrna/` adopted into `src/sgrna`; see the
earlier entry today. Ceiling disagreement resolved in favour of the tiling route
(≈0.94 working figure) on the grounds that the label is a |Z| of a Cas9/dCas9
**ratio**, so the replicate route's assumption that the score inherits
single-arm read-count reliability cannot hold. Message drafted for Jacky covering
both.

---

## 2026-10-10 (night) — the k-mer ladder reverses once the selector is removed

Prompted by a question I had answered too confidently: are higher-order k-mers
just pre-computed binding energies, and if not, would keeping *only* them (rather
than all the restatement) capture the higher-order effects better?

**They are not binding energies.** Nearest-neighbour thermodynamics is a sum over
*adjacent pairs*, so duplex stability is a 2nd-order quantity and mono+di already
contains it — which is exactly why `b_energy` regressed onto the k-mer basis at
R² 0.984 and `d_mechanics` at 0.845. What 3rd/4th order can add is different in
kind: homopolymer runs (a tetramer phenomenon, and the model-inversion result
found poly-A/poly-C blocks in the worst guide), terminator-like motifs, and shape
beyond nearest-neighbour.

**And the earlier ladder was confounded by feature selection.** Every arm in
`representation_depth.csv` ran through the top-300 selector, so "adding trimers
hurts" (0.5189 → 0.5163) was a dilution measurement, not an information one.
Re-run with **no selection** (`kmer_order_noselect.csv`, LightGBM, 5 folds):

| columns | n | ρ |
|---|---:|---:|
| mono | 74 | 0.5083 |
| mono+di | 364 | 0.5180 |
| **mono+di+tri** | 1,510 | **0.5229** |
| mono+di+tri+tetra | 5,853 | 0.5190 |
| mono+di + hand | 427 | 0.5258 |
| all indicators + hand | 5,916 | 0.5266 |
| everything published | 6,232 | 0.5298 |
| mono+di + hand + family A | 775 | 0.5993 |
| all indicators + hand + family A | 6,264 | 0.6062 |

Paired across **3 seeds × 5 folds** on identical splits
(`kmer_order_paired.csv`), because the unpaired differences sit inside one fold
sd:

| contrast | mean | folds | paired *t* | Wilcoxon |
|---|---:|---:|---:|---:|
| **+trimers** | **+0.0035** | 12/15 | **p = 0.025** | **p = 0.018** |
| **+tetramers on top** | **−0.0028** | 4/15 | **p = 0.013** | **p = 0.018** |
| tetramers vs mono+di (net) | +0.0007 | 8/15 | p = 0.62 | p = 0.72 |

**So the trimer gain is real and the tetramer loss is real, and they cancel.**
The usable order stops at three: 4,343 tetramer columns for 256 possible 4-mers
per position is too sparse to carry anything, and it costs what the trimers
earned.

Two consequences for the report. The depth-ladder sentence "supplying explicit
trimers hurts" must become **"hurts under selection, helps without it"**. And the
427-column recommendation needs a condition attached: **it is the right basis
while the selector stays, but if the selector is dropped — which is where most of
the FLOP saving lives — keep the trimers, giving ~1,573 columns.**

Also noted: "everything published" (0.5298) beats mono+di+hand (0.5258) by
+0.0040 without selection, so the 316 quantum columns do earn their keep once the
model can see everything. Informationally they are fixed k-mer lookups — pure
restatement — but they are **continuous**, and a histogram learner splits a
continuous column far more cheaply than a sparse binary one. The same
expressivity argument as the trimers, from the other side.

**The pattern, for the third time on this one ladder.** Every wrong answer here
came from measuring through the selector and reading the result as a fact about
information. *A conclusion drawn downstream of feature selection is a statement
about the selector until proven otherwise.*

---

## 2026-10-11 — matched CNN test, the cost panel, and family J is a null

### 1. The CNN claim restated on matched input, and the explanation narrowed

`seqnet_matched.csv`, five folds each, same architecture and epochs, only the
sequence given changes:

| flank | input width | ρ | CPU/fold |
|---:|---:|---:|---:|
| 0 | 23 nt | 0.4980 | 22 s |
| 100 | 223 nt | 0.5203 | 84 s |
| **250** | 523 nt | **0.5247** | 184 s |
| 500 | 1,023 nt | 0.5214 | 372 s |
| **1,000** | **2,023 nt** | **0.5190** | 686 s |

Flat from ±100 and then declining. **The withdrawal was over-cautious**: the
"4.2×" was unsound as stated but the conclusion survives the matched test, now
at **4.3× on the same ±1,000 nt**.

More useful than the ratio: the matched test says *which* explanation was right.
**Not receptive field** — the sequence was there and went unused. The context
branch mean-pools, so a windowed average is representable; it is never found,
from 33,567 examples against a +0.08 effect. The barrier is **inductive bias and
sample efficiency, not capacity.** With far more data it presumably could. The
prior is free and the data is not.

### 2. Cost: a panel, because no single number is architecture-independent

| | SLICER | crisprHAL 2 | ratio |
|---|---:|---:|---:|
| training FLOPs | 1.79 × 10¹¹ | 4.21 × 10¹⁴ | 2,360× |
| CPU-seconds/fold | 65.8 | ~10,000 | ~150× |
| wall-clock/fold, 10 cores | 13.8 s | ~21 min | 91× |
| peak memory | 3.8 GB | 4.6 GB | 1.2× |

Minimum-cost SLICER: **7.5 CPU-s, 2.45 × 10¹⁰ FLOPs (17,200× fewer)** for
−0.0125 ρ. Ridge on the same columns: **3.4 CPU-s**, ρ 0.627 — still above the
CNN at any input width.

**The measure that matters and was missing: arithmetic intensity.** FLOPs per
byte moved is **0.25 for our histogram construction and 64 for their
convolutions**, against the ~10–30 a modern CPU needs to be compute-bound. Their
work is compute-bound; **ours is memory-bandwidth-bound.** So counting arithmetic
captures nearly all of their cost and about a quarter of ours, and **2,360× is an
upper bound on the real advantage.** There is no single architecture-independent
number; quote the panel.

### 3. Family J — GC skew and helical periodicity — is a null, and it matters

Built to explain the one thing this project cannot: the long-range asymmetry is
strand-asymmetric and GC content is symmetric under strand swap, so family J used
three quantities that are neither GC nor composition — GC skew, A-tract phase
power in the 9.5–11.5 bp band, and the same spectral measure on a dinucleotide
bendability track, at 50/250/500/1,000 nt each side.

Spectral measure validated first: pure 10.5 bp sine **0.961**, white noise
**0.020**, 25 bp sine **0.000**.

**All 24 columns pass the Part 6 filter** — median R² from the k-mer basis
−0.022, max −0.011, none above 0.9.

**And they carry nothing** (5 seeds × 5 folds):

| arm | columns | ρ |
|---|---:|---:|
| baseline | 6,232 | 0.5272 ± 0.0022 |
| + family J | 6,256 | **0.5264 ± 0.0007** |
| + family J, permuted | 6,256 | 0.5273 ± 0.0006 |
| family A | 6,580 | 0.6068 ± 0.0017 |
| family A + J | 6,604 | **0.6072 ± 0.0024** |

Alone **−0.0008**, with its own permutation control scoring *higher*. On top of
family A, **+0.0004** — a fifth of the seed spread.

Two reasons this is a result and not a footnote. It is a negative on the **most
mechanistically motivated candidate left**, the one feature actually shaped like
the effect it was built to explain, which makes the long-range asymmetry harder
to explain rather than easier. And it is the **second case showing Part 6's rule
runs one way only**: high R² reliably means a feature cannot help (8 of 8), but
low R² is a filter, not a prediction (7 of 9). `h_offtarget` was the first and was
explained away as outside scope; family J is squarely inside it. The report now
says so with a ⚠️ on the rule.

---

## 2026-10-11 (later) — sample complexity for both models, their split, and a metric we lose

### 1. Sample complexity — the architecture-free comparison, finally run

Same fixed test set (fold 1, 6,714 guides), nested training subsets, published
settings at every size, no tuning (`sample_complexity.csv`):

| training guides | SLICER | crisprHAL 2 | gap |
|---:|---:|---:|---:|
| 4,000 | **0.6374** | 0.5072 | **0.130** |
| 8,000 | **0.6672** | 0.6207 | 0.047 |
| 13,880 | **0.6844** | 0.6632 | 0.021 |
| 20,000 | **0.6904** | 0.6811 | 0.009 |
| 26,853 | **0.6944** | 0.6877 | 0.007 |

| to reach | SLICER | crisprHAL 2 |
|---|---:|---:|
| 90% of own best | **4,000** | 8,000 |
| 95% of own best | **8,000** | 13,880 |
| 99% of own best | 20,000 | 20,000 |

**About half the data for most of the way**, and the gap collapses monotonically
— the signature of a sample-complexity difference, not a ceiling difference. By
20,000 both are within 1% of their own best, so this is a **small-data property,
not a general one**, and it must be stated that way.

Why it matters more than the FLOP ratio: it is the only measure that does not
depend on how the computation is organised, so **no amount of hardware erodes
it** — and the practical case the paper should make is a new organism or enzyme
starting from a few thousand measured guides, which is exactly the regime where
the gap is 0.13 rather than 0.007.

It also re-explains Part 10's flat learning curve: ours is flat past 20,000
because we are already near our ceiling there, not because more data cannot help.

### 2. The adversarial test: their split, and SLICER still wins

Asked whether a setup favouring crisprHAL would reverse the result. The strongest
such setup is not a metric but **their own shipped train/test partition** — the
one they designed, published 0.695 for, and which we never touched while building
anything. 26,830 train / 6,737 test:

| | ρ | R² |
|---|---:|---:|
| **SLICER, default settings** | **0.6997** | 0.5168 |
| crisprHAL 2, our rerun on that split | 0.6940 | 0.5108 |
| crisprHAL 2, published | 0.695 | — |

**Untuned SLICER beats them on their own split**, against both our rerun and
their published number. So the margin is not a property of our folds.

### 3. Withdrawn: "SLICER leads on all nine metrics, tuned and untuned"

It leads on **9 of 9 tuned and 8 of 9 untuned**. The exception is calibration
slope:

| | slope | distance from 1 |
|---|---:|---:|
| SLICER, untuned | 1.0972 | 0.0972 |
| **crisprHAL 2, untuned** | **1.0493** | **0.0493** |
| **SLICER, tuned** | **1.0234** | **0.0234** |
| crisprHAL 2, tuned | 1.0655 | 0.0655 |

**Untuned, crisprHAL is twice as well calibrated as we are.** Tuning reverses it.
The exception is now quoted in Part 11 rather than buried, and it makes a sharper
point than the clean sweep did: a model trained directly on MSE *should* win on
scale, and untuned it does. We win on ranking; they win on calibration until we
tune.

**How the error happened, because the pattern is familiar.** I read nine columns
off the panel, saw SLICER ahead on eight of them in the direction "bigger is
better", and did not notice that calibration slope is the one metric whose target
is **1 and not infinity**. *A panel of metrics needs its directions written down
next to it; "leads on every measure" is a claim about an ordering that only
exists once you have said which way each one points.*

---

## 2026-10-11 (end of day) — documentation pass

No new measurements. Recording what changed so the next session does not have to
diff the repo.

**READMEs.** The repo-root README now opens with where the project stands —
ρ 0.721 against 0.704 for the published state of the art, both tuned, for ~150×
less CPU time and about half the training data — because a reader arriving at the
folder table had no way to tell whether any of it worked. Module count 43 → 47.
`sgrna/README.md` gains `cost.py`, `panel.py` and `sample_complexity.py`, and the
features row now says ten families rather than nine, naming `j_periodicity` as
the most recent null so nobody rebuilds it hoping.

**The progress report gains a one-paragraph summary** at the top. It had grown to
2,000 lines with no statement of what the project concluded, so a reader had to
get to Part 3 before learning whether the model was any good.

**Figures tried and reverted.** Three Mermaid `xychart-beta` blocks were added
and then removed the same day: GitHub's renderer returned *"maximum text size
exceeded"* on them. They have been stripped along with the log-scaled text bar
chart, and the report is back to tables only. Nothing was lost, because every
chart had been placed next to the table it was drawn from — which is the reason
that convention was worth keeping.

**What the sample-complexity figure was for went into the prose instead**, since
the visual point was the substantive one: the two columns are **two saturating
curves approaching their own asymptotes at different rates**, not a gap that
happens to shrink. Both are saturating at full size (our last 6,853 guides buy
+0.004, theirs +0.007) and the asymptotes are close (0.694 and 0.688). What
differs is the rate. Written out explicitly, because it bounds the claim: this is
**not** evidence of a higher ceiling — the ceilings are within 0.007, inside the
fold spread — it is evidence of reaching the ceiling on less evidence.

---

## 2026-10-11 (night) — the texture-preserving null, and the report restructured

### The shift-distance null: the flank effect is sharply local

Review point 3, and the sharpest control anyone has proposed for family A. Row
permutation destroys genomic autocorrelation as well as the pairing, so it tested
a weaker null than claimed. `shiftnull.py` instead re-assigns each guide the flank
track read from a position offset by a **circular chromosome shift** — same
track, wrong place — which preserves every column's marginal, its smoothness and
its long-range autocorrelation exactly.

Verified before trusting it, on `dn500.gc`: mean 0.5103 → 0.497–0.508 while
correlation with the aligned track falls 1.00 / 0.41 / 0.05 / −0.03 at 0 / 1 kb /
100 kb / 2 Mb. **That 0.41 at 1 kb is why one shifted null would have been
inadequate**, and why the shift was swept — which turns a control into a
measurement of the effect's autocorrelation length.

3 seeds × 5 folds, grouped CV by 100 kb blocks, against a completed no-flank
baseline of ρ 0.5291 ± 0.0033:

| flanks read from | ρ | gain | share of the real gain |
|---|---:|---:|---:|
| **the right place** | **0.6060** | **+0.0769** | 100% |
| 1 kb away | 0.5353 | +0.0062 | **8%** |
| 10 kb away | 0.5160 | −0.0131 | — |
| 100 kb away | 0.5229 | −0.0062 | — |
| 500 kb – 2 Mb | 0.5194–0.5207 | −0.009 | — |

**The effect is not an artefact of chromosome-scale structure**, and it is far
more localised than the window sizes alone implied: 1 kb away retains 8% of it,
and by 10 kb it is gone. The slightly *negative* values past 10 kb are what a
true null looks like with a selector in the loop — 348 noise columns diluting the
top-300 choice.

Worth noting what this does to Finding 4's standing: it was the one large effect
with a control that a reviewer could legitimately call weak, and it now has one
that preserves everything except the thing being tested.

### The report restructured

Condensed from ~2,200 lines to 602: **twelve numbered findings**, each with its
evidence and the limit of what it supports, then the three contributions, where
the work stops, and the freeze. Everything that supports a finding without being
one moved to appendices — the controls and nulls, the questions asked along the
way and their answers (cost measures, how light the pipeline gets, the TPU
question, data structures, CV adequacy, model-class choice, candidate long-range
features, the nine-metric table, how to read ρ), the feature sets with teammates'
work credited, the sources, and a pointer to the withdrawn claims.

The long version is preserved in git history. Detail that the appendices
compress still lives in full in `RESULTS.md` and in this log, which is what makes
the condensation safe: **the report is now the layer that states conclusions, not
the layer that stores evidence.**

---

## 11 October 2026 — the conditional GC test, a withdrawn correlation, and a portable representation

**Item 5 of the pre-submission list is closed, and it caught a bad number.**
`src/sgrna/gcstrata.py`. Flank GC's marginal association with the published
label is +0.044 (±500 nt mean) and no flank GC column at any window exceeds
+0.051 Spearman / +0.079 Pearson. Target GC is a **suppressor** — −0.201 with
the label, +0.176 with flank GC — so partialling it out *raises* the flank term
to **+0.082**, double the marginal value. The full ablation inside five
target-GC strata (grouped CV, 100 kb blocks, 3 seeds × 5 folds):

| target GC | n | baseline | + family A | Δ |
|---|---:|---:|---:|---:|
| 0.20–0.40 | 2,776 | 0.3353 | 0.4630 | +0.128 |
| 0.40–0.50 | 2,776 | 0.4045 | 0.4797 | +0.075 |
| 0.50–0.55 | 2,775 | 0.4627 | 0.5221 | +0.059 |
| 0.55–0.60 | 2,776 | 0.4760 | 0.5220 | +0.046 |
| 0.60–0.85 | 2,776 | 0.4443 | 0.5023 | +0.058 |

Family A is not target GC in disguise. The gain is largest for GC-poor targets
but **not monotone**, and it covaries with headroom, so the ordering is not a
dose-response curve.

**Withdrawn (claim 20): "flank GC +0.159".** Does not reproduce by either
correlation measure against the published label. Target GC's −0.201 reproduces
exactly, so it is that one figure, not the analysis. Cause: not traceable to a
script — most likely a different label or window than the one recorded. The
lesson is the one already in the report's closing line: the number had been
repeated often enough to feel settled.

**The reduced representation is portable.** `src/sgrna/portability.py`. The 63
hand-named columns audit as 26 computable from the 20-mer and its PAM, 2 needing
gene annotation, and 34 undecoded `V` columns — 19 reconstructible at R² ≥ 0.95
against mono+di indicators, **15 not** (worst `V2049` at 0.056; that R² is
in-sample, so an upper bound). Dropping the 15 **costs nothing**:

| arm | columns | ρ |
|---|---:|---:|
| reduced | 427 | 0.5249 ± 0.0014 |
| **portable** | **412** | **0.5271 ± 0.0011** |
| published full | 6,232 | 0.52716 ± 0.0022 |

All three arms from one run. The portable arm sits **0.00003 ρ** from the full
matrix, so 412 columns computable for any 20-mer match all 6,232, with no lookup
into the published matrix. This removes the stated blocker on migrating to
crisprHAL's cohort.

**Appendix D rewritten in APA 7**, every entry verified against Crossref rather
than transcribed — which corrected a wrong Guo 2018 DOI and supplied Noshay's
full 11-author list. RegulonDB v14.5 and PRECISE-1K are flagged as needing
canonical form rather than guessed.

**On hold / blocked.** The eSpCas9 one-shot evaluation is on hold: a pivot to
crisprHAL's cohort reclassifies it as cross-enzyme validation rather than an
untouched holdout, so spending it now spends it on the wrong question. The human
baseline re-tune is blocked — the settings behind ρ 0.472 are not recorded here
and the script behind `human_transfer.csv` is not in `src/`.

---

## 12 October 2026 — the matched-width test refutes the framing it was meant to support

**Intent.** crisprHAL 2's released rows are 378 nt for a 23 nt target — 189 nt
upstream, 166 downstream — so their network already *sees* most of what family A
summarises. The test was proposed on the expectation that our windowed encoding
would still win on that span, which would have made "a gradient, not a motif" a
statement about *their* tuned architecture rather than our in-house control.

**It does not.** New arm `curated_matched` in `headtohead.py` keeps only flank
columns inside their span (the 50 nt windows plus the near-cut sequence and
quantum columns; 250/500/1,000 nt windows dropped). Seed 41, 5 folds, 33,567
curated rows, their label:

| arm | flank columns | ρ | vs crisprHAL 2 |
|---|---:|---:|---:|
| no flank | 0 | 0.5440 | — |
| near-cut only | 260 | 0.6178 | −0.079 |
| **matched to their span** | **282** | **0.6724 ± 0.0094** | **−0.025** |
| full family A | 348 | 0.7072 | +0.010 |

**Inside their own receptive span their convolutions beat our windowed
composition by 0.025.** Our lead is not a better encoding of the same bases; it
is the 250–1,000 nt windows their input never reaches, worth +0.035 on top of a
matched-span representation.

**Consequences, all deflationary and all now in the report.**
1. The one-paragraph summary no longer says the effect is "not recoverable by a
   convolutional network given the same DNA". It now says the decisive part is
   long-range and that on the shared span their model wins.
2. Finding 5 gains the table above and an explicit statement of what the result
   costs: the reading that windowed means are a smarter encoding than convolution
   does not survive on equal DNA.
3. The in-house CNN control is demoted. A tuned CNN does considerably better than
   ours on the same span, so "CNNs cannot learn this" was never supportable; only
   the sample-efficiency reading survives.
4. The cost appendix's "still above the convolutional network at any input width"
   now says *our in-house* control, since it is not above crisprHAL 2.

**What it buys.** A cleaner contribution: the signal is long-range and the
advantage is access to it. That is a narrower claim than the one it replaces and
a much harder one to attack, because it no longer depends on out-encoding a
tuned deep model on DNA both sides hold.

**Also added.** Appendix C0 records Python 3.12.15, numpy 2.5.3, pandas 3.0.6,
scipy 1.18.1, scikit-learn 1.9.1, LightGBM 4.7.0, XGBoost 3.4.1, CatBoost 1.2.10,
SHAP 0.52.0, PyTorch 2.14.1, the seed and fold policy, and the resumable-fold
protocol — the reproducibility gap flagged when the paper draft went into the
shared doc.

---

## 12 October 2026 — where the reduced representation should actually stop

Prompted by a teammate's review of the pivot proposal, which argued the portable
set should be the 364 mono+dinucleotide indicators plus family A. Measured
instead of argued, 5 seeds × 5 folds, same rows:

| arm | columns | ρ | vs full |
|---|---:|---:|---:|
| mononucleotide only | 74 | 0.5081 ± 0.0010 | −0.0191 |
| mono + dinucleotide | 364 | 0.5189 ± 0.0009 | −0.0083 |
| reduced | 427 | 0.5249 ± 0.0014 | −0.0023 |
| **portable** | **412** | **0.52713 ± 0.0011** | **−0.00003** |
| published full | 6,232 | 0.52716 ± 0.0022 | — |

**412 is the stopping point.** Cutting to 364 costs 0.0083 ρ, so the 48 portable
hand-named columns are load-bearing, not inertia. Their proposal was one step too
deep; their direction was right.

**Their column-count inference was exactly right and is confirmed**: the curated
arms carry 6,517 = 6,169 + 348, so the 63 hand-named columns are already absent
on that cohort. Any statement about "the 427" on crisprHAL's rows was never about
the columns in use.

**A number of mine was wrong and is now decomposed.** I quoted +0.089 for the
flank gain in a message while the report says +0.080. They are different
quantities:

| rows | label | Δρ |
|---|---|---:|
| 13,880 published | published | **+0.080** (canonical, `ablation_main`) |
| curated overlap | published | +0.089 |
| curated overlap | crisprHAL | +0.094 |
| all 33,567 curated | crisprHAL | **+0.164** |

The provenance table for the paper is +0.080 → +0.164; the middle rows separate
the label change (+0.005) from the extra rows (+0.070), which is a sharper claim
than "robust to curation".

**Sample complexity: the criticism was half right.** The report's table already
uses common absolute thresholds and reproduces exactly from
`results/sample_complexity.csv` (ρ ≥ 0.62 → 4,000 vs 8,000; 0.66 → 8,000 vs
13,880; 0.68 → 13,880 vs 20,000). But `sample_complexity.py` *printed* only
"share of each model's own best", which is where the impression came from. The
summary now prints absolute thresholds first and labels the own-best figures
"diagnostic only, NOT a data-efficiency claim". The genuine limitation is
unchanged and still open: one fixed test fold, SLICER 2 seeds, crisprHAL 1 seed.

---

## 13 October 2026 — sample complexity across all five folds: the claim survives, and a caveat of ours does not

Both curves now run over all five folds (`sample_complexity.py --folds`). 25
crisprHAL fits, ~3.5 h on CPU in `.venv-crisprhal`.

| guides | SLICER | sd | crisprHAL 2 | sd |
|---:|---:|---:|---:|---:|
| 4,000 | 0.6501 | 0.0095 | 0.5235 | 0.0138 |
| 8,000 | 0.6817 | 0.0081 | 0.6323 | 0.0146 |
| 13,880 | 0.6985 | 0.0081 | 0.6733 | 0.0092 |
| 20,000 | 0.7046 | 0.0076 | 0.6879 | 0.0054 |
| 26,853 | 0.7082 | 0.0076 | 0.6950 | 0.0072 |

**Fold 1 is the hardest fold for both models**, so measuring only fold 1 was
conservative rather than flattering — but not equally for the two: it understated
SLICER by ~0.014 ρ and crisprHAL by ~0.007.

**Thresholds, five-fold means:** ρ ≥ 0.62 → 4,000 vs 8,000 (unchanged); ρ ≥ 0.66
→ 8,000 vs 13,880 (unchanged); ρ ≥ 0.68 → **8,000 vs 20,000**, up from 13,880 vs
20,000, so the ratio goes 1.4× → **2.5×**; and a new ρ ≥ 0.70 → 20,000 vs never
reached on the data available.

**Withdrawn (claim 21): "the asymptotes are close (0.694, 0.688) … within 0.007,
inside the fold spread … not evidence of a higher ceiling."** Paired across five
folds at full size the difference is **+0.0133 ρ, sd 0.0055, paired t = 5.36,
p = 0.0058, 5/5 folds favouring SLICER**. The single-fold version of this
comparison had no power to see it.

*What replaces it is narrower than "higher ceiling".* Neither curve has
converged — the last 6,853 guides still buy +0.004 and +0.007 — so this is a gap
at full available data, not a demonstrated difference in asymptote. It is also
the same gap the head-to-head already reports, not independent evidence.

*Limit:* SLICER averages two seeds per fold, crisprHAL one, so crisprHAL's
per-fold values are noisier. Pairing by fold is valid; a second crisprHAL seed
would tighten the interval.

**Operational note.** These 25 fits ran on CPU and took ~3.5 h. crisprHAL's GRU
is explicitly configured for cuDNN's fused kernel (`recurrent_dropout=0.0`,
`unroll=False`, `reset_after=True`) and its builder is named
`build_crisprHAL_GPU`; we have no CUDA and no `tensorflow-metal`, so every
crisprHAL fit in this project has run on the slowest available path. Appendix B's
arithmetic-intensity figures (0.25 vs 49 FLOP/byte) already said which workload
belongs on a GPU — we computed the diagnostic and did not act on it.

---

## 13 October 2026 — Jacky's orientation controls close Part 4 item 3, and move Finding 7's ground

Read from `Jacky/orientation-controls/`; numbers verified against
`results/intergenic_orientation_controls_delta_ci.csv` rather than the write-up.
Δ is opposite-minus-same asymmetry, 2,000× block bootstrap over 47 genomic
blocks, primary set n = 8,954.

| orientation against | opposite | same | Δ [95% CI] | P(Δ≤0) |
|---|---:|---:|---|---:|
| **RegulonDB TSS** | 0.061 | 0.011 | **0.051 [0.020, 0.082]** | 0.000 |
| operon | 0.053 | 0.031 | 0.023 [−0.008, 0.055] | 0.085 |
| nearest gene | 0.040 | 0.014 | 0.026 [−0.006, 0.058] | 0.054 |
| nearest gene, matched dist+GC | 0.029 | 0.022 | 0.007 [−0.024, 0.038] | 0.337 |
| TSS, matched dist+GC | 0.048 | 0.023 | 0.025 [−0.003, 0.053] | 0.041 |

**What it gives us.** A clean positive control: against a curated TSS the
orientation interaction has a CI clear of zero. Finding 7 now leads with TSS.

**What it takes away, and this is the part to be straight about.** The
nearest-gene version is what Finding 7 previously rested on, and it **does not
survive matching on distance and flank GC** — Δ 0.007, P = 0.34. Orientation
relative to the nearest gene was partly standing in for where those guides sit.
TSS also halves under the same matching (Δ 0.025) and its CI then includes zero
while the one-sided P is 0.041, so the phrasing is "survives matching
directionally, borderline at 95%".

**Withdrawn (claim 22): "0.047 against the nearest gene, 0.005 with it."** Those
were unweighted point estimates. The block bootstrap over genomic blocks puts the
same comparison at 0.040 against 0.014, Δ 0.026 [−0.006, 0.058]. Not wrong, but
the optimistic form of a quantity that needed an interval — and the interval
includes zero.

*Minor inconsistency noted for Jacky:* `..._summary.csv` gives the unmatched TSS
asymmetries as 0.0645 / 0.0104 (Δ 0.0540) where `..._delta_ci.csv` gives
0.0614 / 0.0106 (Δ 0.0507). Each file is internally consistent, so this is most
likely point estimate versus bootstrap mean, but the paper should quote one of
them and say which.

---

## 13 October 2026 — the redundancy screen was being quoted with a score it cannot carry

Runjia noticed that Finding 3's table did not support the sentences under it.
It did not.

**The counts were wrong.** "High R² ⇒ cannot help, 8 times out of 8" — only
**four** of the families have positive R² at all. "The should-help direction is
7 of 9" — of the low-R² families, four helped, and one of those four
(`d_supercoiling`, +0.045) was later overturned by its own dCas9 control, so it
is really three. No threshold for "high" was ever declared, which made the first
claim unfalsifiable as stated. And `d_mechanics`, unambiguously high at R²
0.845, returned **+0.020** — the second-largest gain in the table, sitting
inside the table meant to demonstrate that high R² means no gain.

**The table was also incomplete.** `i_shape` had never been run through the
screen, and `j_periodicity` lived in a separate file with a different schema.
Rerun over all eleven families into one file (`redundancy.csv`;
the nine-family version preserved as `redundancy_backup_9fam.csv`):

| family | columns | median R² | share R² > 0.9 |
|---|---:|---:|---:|
| b_energy | 10 | 0.984 | **70%** |
| d_mechanics | 30 | 0.845 | **50%** |
| c_folding | 9 | 0.297 | 0% |
| f_methylation | 17 | 0.141 | 0% |
| a_flank | 322 | −0.012 | 0% |
| d_supercoiling | 26 | −0.013 | 0% |
| g_transcription | 18 | −0.016 | 0% |
| e_nucleoid | 20 | −0.016 | 0% |
| **i_shape** | **152** | **−0.017** | **0%** |
| j_periodicity | 24 | −0.021 | 0% |
| h_offtarget | 7 | −0.022 | 0% |

**The median was the wrong statistic.** Share-above-0.9 shows the real structure,
which is binary: two families contain columns the 20-mer determines, nine contain
none. `c_folding` (0.297) and `f_methylation` (0.141) have middling medians and
**no** determined column — their medians average weak partial fits.

**Also answered: why the nulls cluster so tightly.** Out-of-fold R² against a
target with no relationship to the basis is not 0 but a small negative set by the
basis size and row count, not by the target. All nine nulls land between −0.012
and −0.022 with 10th percentiles −0.019 to −0.022. They are sitting on a shared
null floor, which is the signature of "no relationship" rather than a defect —
the agreement is evidence the estimator is behaving.

**Withdrawn (claim 23): the "8 of 8" and "7 of 9" scorecard**, in Finding 3 and
in Contribution 1. The screen is kept as a qualitative filter, which is how the
report already said it should be quoted; the numbers were doing rhetorical work
the design cannot support.

---

## 13 October 2026 — we gave crisprHAL the DNA it could not see, and it got worse

Runjia asked whether the head-to-head was fair: without flanks nothing beats a
tuned CNN, and with flanks we hold DNA they do not. The answer was to hand their
architecture the same reach. Their input width is a parameter, so this is a
config change plus retraining.

**Run on Colab, T4, fold 1, same rows and label.** cuDNN cannot allocate the GRU
workspace at 2,023 nt and their published batch of 1,024, so all widths were
re-run at batch 256; the 378 nt arm at both batches brackets the batch cost at
−0.011 (0.6906 → 0.6799).

| crisprHAL 2 input | ρ @ batch 256 | vs 378 nt |
|---:|---:|---:|
| 23 nt | 0.5494 | −0.131 |
| 378 nt (published) | 0.6799 | — |
| 1,023 nt | 0.6602 | −0.020 |
| 2,023 nt | 0.6299 | −0.050 |

Monotone decline past their design point, about 7× their across-fold sd.

| DNA both see | SLICER | crisprHAL 2 | lead |
|---|---:|---:|---|
| guide + PAM | 0.5473 | 0.5494 | tied |
| 378 nt | 0.6568 | 0.6799 | crisprHAL +0.023 |
| ±1,000 nt | 0.6944 | 0.6299 | **SLICER +0.065** |

**Three widths, three different answers**, and only the last is ours: the
architectures are indistinguishable on the guide, theirs is better at its design
width, and ours is better at family A's reach — because width helps us and hurts
them.

**Partially restores a claim withdrawn on 12 October**, in a narrower form. "Not
recoverable by a CNN given the same DNA" fell because the only CNN tested at
width was our own weak one. Supported now: *crisprHAL 2, at its published
hyperparameters, is degraded by input wider than it was designed for.* Their 48
epochs and everything else were tuned at 378 nt and **a re-tune at each width is
the control we have not run**. One fold, one seed.

**Two harness bugs of mine, both caught by the data rather than by review.**
First: crisprHAL's `train()` and `predict()` catch their own exceptions and
print, so a failed fit returns None exactly as a successful one does. v2 scored
an untrained network at ρ 0.0434 in 0.36 min — finite, correctly shaped,
non-degenerate, and past every check I had written. v3 calls `m.model.fit` and
`m.model.predict` directly so failures raise. Second: I had guarded the model
*build* against that same swallowing `except` two messages earlier and did not
extend the guard to train/predict.

**Also corrected: "on sequence alone they beat us by 0.153."** That compared
SLICER with no context against crisprHAL with its full 378 nt. Measured
like-for-like the gap is 0.002–0.022 depending on batch — I overstated their
architectural advantage roughly sevenfold, in the message immediately after
warning against that exact comparison.

---

## 13 October 2026 — the redundancy screen is demoted to an appendix

Runjia's objection: the families that did not help are negative results, and
arranging them against "if it correlates with sequence it should not help" makes
a pile of unrelated nulls look like datapoints supporting a trend. Correct, and
the arithmetic is worse than the objection.

**The rule applies to two families.** Only `b_energy` (R² 0.984) and
`d_mechanics` (0.845) are substantially determined by the 20-mer. Everything else
is below 0.30.

**For the strongest case it is a tautology.** CRISPRoff ΔG is computed from the
sequence by nearest-neighbour summation, so its uninformativeness to a model
holding the sequence losslessly is arithmetic. The R² of 0.984 confirms the
arithmetic rather than discovering anything.

**The other nine carry no signal about the rule.** Their R² spans **0.010**
(−0.022 to −0.012), null-floor variation set by family size, while their gains
span **0.081** (−0.001 to +0.080). Across all eleven, ρ(R², Δρ) = 0.489,
**p = 0.127** — not significant. The nine failed for unrelated reasons:
`h_offtarget` needs the rest of the genome, `j_periodicity` is a genuine null,
`i_shape` duplicates family A, `d_supercoiling` was an artefact overturned by its
own control.

**Action.** Finding 3 removed from Part 1; findings 4–12 renumbered to 3–11 with
all fourteen cross-references updated. Its content and tables move to **Appendix
B2**, which now states explicitly why it is not a screen. What survives sits in
Finding 2 as a one-paragraph consequence of the lossless encoding: a
deterministic function of the 20-mer cannot add information to a model that
already encodes the 20-mer. That is a theorem worth stating, not a predictive
rule.

Contribution 1 and the opening summary rewritten to match — the summary had said
the decoding "explained why eight imported feature families added almost
nothing", where it explains two.

**Withdrawn (claim 24): the redundancy screen as a predictive rule**, in all its
forms. This is the third correction to the same finding in two days: first the
"8 of 8 / 7 of 9" scorecard, then the median-versus-share-above-0.9 framing, now
the finding itself. The common cause is that it was promoted to a headline on
the strength of a mechanism that only ever covered two families.

---

## 13 October 2026 — what crisprHAL is trained on, and a label description that was wrong

Runjia asked whether crisprHAL 2 is trained on the same target as SLICER, noting
that its paper may measure cutting efficiency differently. Checked rather than
assumed.

**The head-to-head is valid.** Our target is **bit-identical** to crisprHAL's
released `y` on all 33,567 guides — Spearman and Pearson both exactly 1.0,
`np.allclose` true. `expand.py` sets `y = hal["score"]` straight from their data,
so both models fit the same quantity on the same rows under the same folds.

**But the report described the wrong label.** Part 3 said the label is "a folded
Z-score of a two-replicate Cas9/dCas9 ratio". That is Noshay's `cut_score`:

| label | range | negative values | mean | sd |
|---|---|---:|---:|---:|
| Noshay `cut_score` (13,880) | 0 → 48.05 | **0%** | 24.70 | 10.63 |
| crisprHAL curated (33,567) | −9.05 → +6.21 | **47.5%** | −0.36 | 3.29 |

A folded score cannot be negative; the one we train on is negative nearly half
the time. The description had been carried over from the published cohort and
never revisited when the model layer moved.

**Nothing downstream reverses.** The two labels agree at ρ 0.945 on the 8,617
overlapping guides, and target GC has the same sign against both (−0.147 curated,
−0.201 published). So the GC account and the flanking result survive. But the two
are different quantities and the report now says so.

**Consequence for the ceiling.** The 0.937 figure was derived from Guo's
replicate statistics for the *published* label. crisprHAL's curation changes the
label's noise properties by design — that is the claim of their paper — so the
curated ceiling is probably higher and is currently unmeasured. Finding 11 now
carries that warning, and re-deriving it is item 8 of the pre-submission list.

**The general lesson, written into Part 4 as "What the pivot re-opens".** The
model layer moved to crisprHAL's cohort and the interpretation layer did not. The
same exposure applies to the 412-column reduced set, `n_features` = 300, the
grouped-CV block choice, the champion hyperparameters, the family Δρ table and
the sixteen-model-class spread — all settled on the published matrix and none
re-tested on the curated one. None is known to be wrong; all are untested.

**Also recorded.** Paper writing is deferred; the shared Google Doc is frozen as
of today and this report is the single maintained document. Items 3, 5 and 6 of
the pre-submission list are closed; items 7 (re-tune crisprHAL at each width) and
8 (curated-label ceiling) are added.

---

## 13 October 2026 — a feature with no information is worth +0.099, and a "theorem" of mine is false

The family ablations were re-run on crisprHAL's curated cohort (ten families
rebuilt there; ViennaRNA and Biopython installed to recover two more).
**Every family inflated**, and `i_shape` went from +0.001 — a family I had cited
as passing the redundancy screen and delivering nothing — to **+0.120**, the
third-largest effect.

| family | published Δρ | curated Δρ |
|---|---:|---:|
| a_flank | +0.080 | **+0.164** |
| d_supercoiling | +0.045 | **+0.139** |
| **i_shape** | **+0.001** | **+0.120** |
| d_mechanics | +0.020 | **+0.099** |
| e_nucleoid | +0.016 | **+0.072** |
| j_periodicity | −0.001 | +0.011 |
| f_methylation | +0.004 | +0.008 |
| h_offtarget | +0.000 | +0.001 |

**The obvious explanation was the selector**, since the curated base is 6,169
sparse indicators with none of the 63 hand-named summaries and we select 300.
Tested on `d_mechanics`: **+0.0988 selecting 300, +0.0993 using all 6,199
columns.** Not the selector.

**So `d_mechanics` adds +0.099 ρ while adding no information.** Nearest-neighbour
duplex energies are sums of dinucleotide parameters — deterministic functions of
the 20-mer, which the base encodes losslessly. A depth-limited GBM over one-hot
indicators cannot cheaply compute a sum over positions; handed it precomputed, it
gains 0.099.

**Withdrawn (claim 25): the "theorem" in Finding 2.** I wrote that a
deterministic function of the 20-mer "adds nothing to a model trained on it" and
called it arithmetic rather than a result. **That is false for our model class.**
It holds for an unconstrained learner. What survives is narrower: such a feature
adds no *information*, so it cannot raise the ceiling — but it can add a great
deal of *performance*. The distance between what a representation contains and
what a model can use is the whole value of feature engineering.

**This is the cleanest evidence in the project for the summarisation account**,
because it removes family A's confound. Family A mixes summarisation with new
DNA; `d_mechanics` adds no new DNA at all.

**What the curated table does not license.** It is not comparable to the
published column (different baselines, labels and base representations), and it
is not a clean estimate of biological contribution — the inflation tracks whether
a family supplies *dense continuous* columns, which the curated base lacks
entirely. Separating shape from content needs the portable hand-named summaries
added to the base and a re-measure. Written into Appendix B3 with those limits
stated rather than as a finding.

**Three silent failures caught today, all the same shape.** `b_energy`'s builder
caught a missing Biopython import *per guide*, dropped the error column, and
wrote a file with zero features while reporting success — it would have scored
Δρ = 0.000 and read as a clean null. My first selector control compared 300
columns against 300, because `cross_validate` resolves `n_features=None` to
`config.N_FEATURES`; it was caught only because the two arms matched to sixteen
decimal places. The same `None` is passed by `portability.py`, so that ladder's
arms are not on identical footing — the 74-column arm uses all its candidates
while the 6,232-column arm selects 300 — and Finding 2 now says so.

**Also added: Appendix B2a, on curation versus selection.** They drop different
objects (rows against columns) and only one can flatter a score: selection is
fitted inside each training fold and cannot leak, while curation is applied
before splitting and so removes noisy rows from the *test* set too. Our ρ 0.607 →
0.628 figure for the value of curation contains both effects and has never been
separated. Relabelling is worth +0.003; the value is in which rows survive. The
two cohorts are not nested — 8,617 shared, 24,950 only crisprHAL, 5,263 only
Noshay. The curation *procedure* remains unread; nobody here has read the PeerJ
methods, and we train on their label.

## 13 October 2026 (later) — the migration to the curated cohort, finished

**All eleven feature families are now measured on crisprHAL's 33,567 curated
guides.** The three that were missing are in, and each had been failing
silently: `b_energy` wrote a file with 33,567 IDs and zero feature columns while
reporting success (missing Biopython and ViennaRNA, caught per guide and dropped
with the error column); `c_folding` the same for ViennaRNA alone;
`g_transcription` needed four index columns crisprHAL's CSVs never carried, of
which the b-number for the expression join was the real blocker. Host genes are
now assigned by coordinate on NC_000913.2 and b-numbers by gene name through
PRECISE-1K's annotation — 30,203 of 33,567 guides inside a gene, 29,097 with
expression. `build_curated_features.py` is the module; it refuses to write a
block with no populated feature column, and `curated_ablation._block` refuses to
read one.

New numbers: `g_transcription` **+0.058** (sixth, and the only family carrying
information that is not in the genome), `b_energy` +0.019, `c_folding` +0.014.

**The migration's headline result is the opposite of what was expected.** The
family ranking transfers almost exactly — rank ρ **0.97** between the published
and curated columns — while every family inflates by a median of **3.3×**. The
cohort change does not reorder which families matter; it rescales all of them.
And the inflation is explained by column shape: ρ(dense continuous columns, Δρ)
= **0.882, p = 0.0003** across eleven families. `j_periodicity` breaks the rule
in the useful direction — 24 dense continuous columns, as many as
`d_supercoiling`'s 26, and +0.011 against +0.139 — so supply buys the chance to
help and content decides whether it does.

**Withdrawn claim 26: `i_shape`'s "reversal from a flat null".** Its published Δρ
was tabled as +0.001 in three places. That figure is its increment *on top of
family A*, not over the base, while every other entry in those columns is
base-relative. Standalone it was **+0.036** — third-largest then, third-largest
now on the curated cohort at +0.120. So there was no reversal, only the same ~3×
inflation as everything else, and the "caution about the published table" that
B3 drew from it was drawn from a transcription error of ours. Knock-on:
ρ(R², Δρ) in Appendix B2 is **0.224, p = 0.508**, not 0.489, p = 0.127 — the
screen's association is weaker still, which is the direction that appendix
already argued.

**Also re-measured: the within-gene variance share, and it moved.** 0.844 on the
published rows against **0.713** on the curated cohort — gene identity explains
29% of the curated label against 16% of the published one, because crisprHAL's
release is genome-wide (4,013 genes at 7.5 guides each) while Noshay's rows
target a panel (1,222 genes at 11.3). Gene-grouped CV therefore constrains the
model *more* here than the published-matrix experience suggests, and the grouped
ablation needs re-running on this cohort — now item 9 in Part 4. Assignment is by
coordinate for both cohorts; on the published rows it agrees with Noshay's own
annotation for 97.7% of guides and gives the same share to three decimals, which
is what makes the comparison a cohort effect rather than a method effect.
`python -m sgrna.cohort_groups`.

## 13 October 2026 (later still) — withdrawn claim 27, the biggest one today

**`d_mechanics` does not add "no new DNA at all", and its +0.099 was not a
measurement of representation.** Eight of its thirty columns —
`eng.mech.flank.{up,dn}{25,100}.{dG37,dG_per_bp}` — are duplex thermodynamics of
the flanking DNA, which the base representation does not contain. Found by
reconstructing each column out of fold from the base's 364 mono- and
dinucleotide indicator columns: nine ΔG/ΔH/ΔS sums came back at R² = **1.0000**,
four melting temperatures at 0.997–0.9995, and the eight flank columns at
**−0.006 to +0.042**. A column that the base predicts at R² ≈ 0 is not a
function of the 20-mer.

Split into halves (`no_information.py`, same base, same 5 seeds × 5 folds):

    base                                 0.5445
    + 22 protospacer columns             0.5555   +0.0110
    + 8 flank columns                    0.6418   +0.0973
    + all 30                             0.6437   +0.0991

**Eight columns of flanking DNA carry 98% of the gain.** The arm the report
called "the cleanest available demonstration that representation matters
independently of information" was mostly family A's effect under another
family's name, and the claim was inflated about nine-fold.

**What survives, and it is consistent.** The representation effect is real and
small, with three independent guide-only measurements agreeing:
`d_mechanics`'s protospacer half +0.011, `c_folding` +0.014, `b_energy` +0.019.
A deterministic function of the guide buys a depth-limited tree one to two
hundredths of a correlation. Family A's access to new DNA is worth +0.164.

**The replacement account of the curated table is better than the one it
replaces.** Sorting the eleven families by *how far outside the 20-mer they can
see*: nothing confined to the guide exceeds +0.019, and nothing above +0.05 is
confined to it. Necessary, not sufficient — `j_periodicity` and `h_offtarget`
read the whole chromosome and return +0.011 and +0.001. The dense-continuous
column correlation (ρ = 0.882) is confounded with reach, since a family
measuring 2 kb of DNA reports it as real numbers, so it is no longer offered as
the explanation.

This is the second time in one day that a family-level number turned out to be a
different quantity than its label (the first was `i_shape`'s +0.001). Both were
caught by reading a column list rather than by running anything new.

## 13 October 2026 (evening) — gene-grouped on the curated cohort, and why the table inflated

**All eleven families re-run with whole genes held out** (30,203 guides in 4,013
gene groups, baseline ρ 0.5584). **The three largest effects lose nothing.**
`a_flank` retains 96% of its gain, `d_supercoiling` 94%, `i_shape` 94%.

The reading depends on a calibration that was not obvious before running it:
**the guide-only families set the grouping tax.** `b_energy`, `c_folding` and
`f_methylation` are functions of the guide, so a change of split cannot
invalidate them, yet they retain only 94% in aggregate. That 6% is what holding
out whole genes costs for reasons unrelated to memorisation. Against it,
`e_nucleoid` (88%) and `g_transcription` (79%) carry a real locus component of 6
and 15 points — the expected direction and the expected two families — and
`j_periodicity` (64%) and `h_offtarget` (23%) lose most of gains worth +0.011 and
+0.001.

**Less memorisation than the published cohort showed**, where grouping cost
`e_nucleoid` 42% and `g_transcription` 36%, despite the curated cohort having
twice the between-gene variance share. The resolution: 7.5 guides per gene
against 11.3. Between-gene variance sets how much a locus-memorising model could
win; guides per gene sets how well it can learn each locus's mean. They moved
oppositely and the second won — not derivable from the variance share, which is
the argument for running controls rather than reasoning about them.

**Why the whole table inflated ~3×, narrowed to two candidates.** Four things
changed with the cohort and two are now eliminated:

* **the label** — at fixed rows (the 8,617 shared), family A is +0.0892 against
  `cut_score` and +0.0936 against the curated score. A 0.004 move. *Not it.*
* **row count** — on a random **13,880-row subsample of the curated cohort**,
  family A is **+0.170** and `d_mechanics` **+0.105**, i.e. the full-cohort
  figures (+0.164, +0.099) at the published cohort's row count. *Not it.*
* **which rows** (genome-wide against a 1,222-gene panel) and **the base**
  (6,169 sparse indicators with none of the published base's 63 hand-named
  summaries) — one or both. `base_enrichment.py` is running the base test:
  give the curated base 41 dense guide-only summary columns that carry no
  information beyond the 20-mer, and see how much of family A's +0.164 survives.

So the answer to "surely removing noise shouldn't change behaviour" is that
**noise removal is the one thing that provably did not do it.** Written up in
Appendix B2a, including the two mechanisms by which noise removal *could* have
changed behaviour qualitatively (a hard selection budget makes feature inclusion
a threshold operation, and a read-count filter is not spatially random because
abundance is not).

**Bug 12, caught by a sanity check and not by the code.** The gene-grouped run
wrote its results into `ablation_curated.csv`, the random-row table, destroying
it — a leftover `to_csv(OUT)` in the family loop that my earlier patch to
`_write(rows, OUT_)` had missed. Noticed because the "random" column of a
comparison table came back holding the grouped numbers. Recovered from the
committed copy. The lesson is the same as the other three silent failures: the
run reported success, and the only signal was a number that did not look right
in a table built for a different purpose.

**Also written: Appendix A now gives every control three lines** — what it rules
out, why the design rules that out, and what would be believed without it. The
third line is the useful one; several of these controls exist because the thing
they rule out was believed for weeks.

## 13 October 2026 (night) — why the family table tripled: it is the rows

All four candidate causes tested, each holding the others fixed. Family A's gap
between cohorts is +0.080 → +0.164, i.e. +0.084:

    the label        same 8,617 rows, swap cut_score for the curated score   +0.004
    row count        random 13,880-row subsamples of the curated cohort      -0.003
    the base         41 dense guide-only summary columns added to the base   +0.013
    which rows       the remainder                                          ~+0.070

**Row count is absent, not small.** At the published cohort's own row count the
curated cohort gives family A **+0.1672 ± 0.0027** across three draws, against
+0.1638 at 33,567. **The base matters a little** — giving it `b_energy`,
`c_folding` and `d_mechanics`'s 22 guide-only columns raises the base from
0.5445 to 0.5692 and takes 0.013 off family A, 8% of the gap. **The label is 5%.**

**The decisive statistic has no model in it.** Marginal rank correlation of
`up500.gc` with activity: on the 8,617 shared rows it is +0.069 under Noshay's
label and +0.067 under crisprHAL's — identical. On the 24,950 rows only
crisprHAL publishes it is **+0.172**. Same rows two labels: nothing. Different
rows same label: 2.5×.

**What is different about those rows:** not gene class (6.9% essential against
8.0%, 6.8 guides per gene against 7.4) but **dynamic range** — within the same
label, 1.34× the label spread (sd 3.46 against 2.58) and 1.21× the flank-GC
spread. Correlation is scale-invariant, so spread alone is inert; spread in the
signal with the noise floor unchanged raises reliability, and attenuation is
multiplicative in the way the table is. Noshay published the subset of the Guo
screen with the least room to measure anything in. Separating "more range" from
"different biology" properly needs per-guide read counts for a per-subset
reliability — in the PeerJ supplement, still unread.

**So the objection's premise was right and its conclusion is the finding.**
Removing noise from the label did not change how the columns behave, because it
is worth 0.004. What changed is that crisprHAL's release is a wider draw from the
same screen, four fifths of which Noshay never published, in which the effect is
easier to see. **The published matrix understated the flanking-context effect**,
so the curated levels are the ones that describe genome-wide guide design and
Finding 3's effect size goes up rather than down when restated there.

## 15 October 2026 — the pre-submission list, mostly closed

**Item 1, the final evaluation: a tie, and the dataset was not what Part 4 said.**
eSpCas9 was designated "the untouched final evaluation, evaluated once". It was
already in use — four feature arms across three seeds and two CV schemes in
`transfer.csv`, with a +0.104 `arc5` flank gain quoted in `RESULTS.md`. Nothing
was ever *selected* on it, so it is confirmatory rather than untouched, and
"once" was never available. What was still untouched is the comparison: SLICER
against crisprHAL 2 on **their** shipped eSpCas9 partition with **their**
published weights.

    SLICER     rho 0.7842  tau 0.5942  Pearson 0.7782  R2 0.5979  top-dec 0.488
    crisprHAL  rho 0.7821  tau 0.5920  Pearson 0.7801  R2 0.6009  top-dec 0.494

Their arm reproduces their published figure (0.782 / 0.780 → 0.7821 / 0.7801),
which is what makes the comparison quotable. **+0.0021 to us, three of six
metrics to them, on 11,898 guides where the SE of rho alone is ~0.009 — a tie.**

**And it was predicted.** Our +0.0133 lead is at 26,853 training guides; this
split gives 47,591, and the sample-complexity curves say the gap closes as
labels stop being scarce. So **the data-efficiency claim survives and the
ranking claim does not**: "SLICER beats crisprHAL 2" is a small-data claim and is
false at 47.6k guides. On their own two splits the margins are +0.005 (SpCas9)
and +0.002 (eSpCas9) — parity at a fraction of the compute.

**crisprHAL's methods, finally read** (Browne et al. 2026, PeerJ e20706; this
had been an open gap while we trained on their label):

* the score is the **ALDEx2 `diff.btw` log2 fold-change** — a Bayesian posterior
  expectation over 2 control and 2 experimental replicates, not a read-count
  ratio;
* the filter is an **average control-condition read count across the two control
  replicates**, threshold **73** for the *E. coli* SpCas9 set we train on;
* **the threshold is itself fitted**, by 5-fold CV on the training set, so
  curation is a hyperparameter rather than a fixed cleaning rule;
* it is **applied before the 80/20 split** (their Table 2; their own text flags
  the tension), confirming from their methods that curation cleans the test set
  too — which Appendix B2a had inferred.

**Item 8's route through their paper is closed**: they report no replicate-to-
replicate correlation for any dataset, and a posterior mean is shrunk toward its
prior, so Spearman–Brown on a two-replicate geometric mean does not apply to
their label. Only the per-replicate recomputation from the original read counts
remains.

**Item 7 is mostly closed by their paper too.** They searched input length *per
dataset* and stopped at 378 nt (*E. coli* SpCas9) and 406 nt (eSpCas9), reporting
gains that level off: +0.00034 rho per upstream nucleotide, +0.00074 downstream,
0.554 on the sgRNA alone to 0.697 at 378 nt. So 378 is **their** optimum from
**their** search, and our 1,023/2,023 nt decline continues a curve they had
already flattened. **Item 2 is closed by argument**: the tuning asymmetry was an
objection to our runs of their model, and the final evaluation uses their
published weights.

**The reduced-representation ladder, re-run on the curated cohort with no
selection** (`curated_ladder.py`, 3 seeds × 5 folds, `n_features` = each arm's
own column count):

    mono              74   0.5198     base_full        6169   0.5449
    mono_di          364   0.5331     mono_di+flank     712   0.6937
                                      base_full+flank  6517   0.7079

Two results pointing opposite ways. **`n_features` = 300 costs ±0.0005** in both
directions (0.5445/0.5449 and 0.7084/0.7079), which retires the protocol caveat
and that open row. **But the reduction is not non-inferior here**: 364 columns
lose 0.0118 and 712 lose 0.0142, two to three times the pre-declared 0.005
margin. "412 ≈ all 6,232" is a published-matrix result under a 300-column budget
and does not transfer; what does transfer is the lossless part, 74 columns
recovering 95.4% of full rho against 96.4% there.

**"Model class barely matters" was circular, and survives being made
non-circular.** It was measured on a representation with no large effect in it.
Re-run on the curated base *with* family A: eight classes span **0.1076 rho**
(XGBoost 0.7084 → k-NN 0.6007) against 0.116 for sixteen classes without it.
Adding the one family that matters does not widen the gap between model classes,
while the family is worth +0.164.

**Champion hyperparameters: keep the freeze, with evidence.** The champion
XGBoost and LightGBM at unrelated defaults land within **0.0002 rho** on the
curated cohort with family A, so the configuration is not a knife-edge and
re-tuning has little to win.

**Still open:** item 4 (the teammate's human-baseline settings; request drafted
at `docs/correspondence/request_human_baseline_settings.md`) and item 8 (the
per-replicate read counts). Neither gates a draft.

## 15 October 2026 (later) — the last untouched test, and it could have gone the other way

**Cui et al.'s dCas9 CRISPRi screen, spent on the one question that could
falsify Finding 3's mechanism.** Every external check so far has been another
Cas9 *cutting* screen, which cannot separate "a duplex-opening step limited by
local composition at the cut site" from a general property of Cas9 *binding* or
of local accessibility — both would predict a flank effect. dCas9 binds and does
not cut, and the label is fitness under silencing rather than survival after
cleavage, so this screen can tell them apart.

76,325 uniquely-targeting guides located in NC_000913.2, 70,298 inside 4,265
named genes, same pipeline and champion, 3 seeds × 5 folds, **whole genes held
out** — mandatory, since 30% of this label's variance is between genes
(within-gene share 0.704, essentially the same as the curated Cas9 cohort's
0.713) and essential genes sit 2.05 fitness units below the rest.

    arm                      CRISPRi (dCas9)    cutting (curated Cas9)
    20-mer base                     0.4577              0.5584
    base + family A                 0.4484              0.7151
    family A's increment           -0.0093             +0.1567
    family A alone                  0.1333              0.3408

**Family A adds nothing to a silencing screen and +0.157 to a cutting screen,
measured the same way.** The flank-only arm is what makes it a clean null rather
than a selection artefact — 348 columns competing for 300 slots in a 6,517-column
pool could dilute selection, but family A alone cannot be diluted, and alone it
reaches 0.133 against 0.341.

**So the effect is specific to cleavage.** That is what Finding 3 claims, and a
binding or accessibility explanation would have contradicted it. Two
qualifications kept with it: 0.133 is not zero, so flanks do carry some
information about CRISPRi fitness — plausibly because 2 kb around a gene says
something about the gene — but it is *redundant with the 20-mer* there, the
opposite of its behaviour on cutting data; and this changes enzyme, library,
assay and laboratory at once, so what makes the null interpretable is that the
base predicts 0.458 on the same rows. The pipeline works on this screen; the
null belongs to family A.

**There is now no untouched external dataset left.** The adaptive-overfitting
caveat on the curated five-fold figures is permanent, not pending, and further
external validation needs new data.

**Parity, made quantitative.** The eSpCas9 tie was an unresolved difference,
which is not equivalence. Paired bootstrap on the same 11,898 guides, 4,000
resamples, margin declared first at ±0.01 ρ: **Δρ +0.0021, 95% CI [−0.0031,
+0.0072], p = 0.44, whole interval inside the margin.** And "fairest conditions
for both models" is the wrong phrase — rows/labels/splits are equal, tuning is
equal or against us, but **input DNA is unequal in our favour** (±1,000 nt
against their 406). Under equal DNA the ranking depends on width: tied on the
guide alone, crisprHAL ahead by 0.023 inside its 378 nt design span, us ahead by
0.065 at ±1,000 nt. The report now carries the sentence that is true on all
three axes.

**Bug 13, mine, caught by a sanity print.** The coordinate cross-check reported
that Cui's `pos` agreed with ours for 0.0% of guides, which reads as an assembly
mismatch. The offset takes exactly two values, +3 and −21, one per strand: they
report the PAM-proximal end. Every guide agrees exactly. A check that is wrong in
the alarming direction is still a wrong check.
