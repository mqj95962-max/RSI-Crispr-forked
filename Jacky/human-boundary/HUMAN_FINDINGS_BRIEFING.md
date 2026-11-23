# Human findings briefing (for writing the report)

Plain briefing, not paper prose. Every block answers: **what experiment**, **what was compared**, **numbers**, **what it means**, **what you can / cannot claim**.

Metric throughout: **Spearman ρ** (rank agreement between predicted and true activity). Higher = better ranking of guides. Near 0 = no usable ranking. Negative = rankings go the wrong way on average.

---

## Vocabulary you need first

| Term | Meaning |
|---|---|
| **Base / guide-derived features** | Features computed from the 20-nt spacer (and closely related chemistry), *without* looking at the genome around the cut. |
| **Family A / flanks / `a_flank`** | Features from DNA *around* the target (±50…±1000 nt): GC, purine, composition windows. Needs a unique genomic location. |
| **Shared published columns** | Column names that exist in *both* the E. coli and human published matrices. Used so transfer is fair: same feature *names* on both sides. |
| **Transfer** | Train the model on one kingdom, predict the other. No retraining on the test kingdom. |
| **Human-only ladder / CV** | Train and test *only on human* (cross-validation). Measures “can we predict human from human,” not transfer. |
| **Located rows** | Human guides that hit a unique NGG site on hg38. Needed for Family A. Story number: **16,490** usable located guides. |
| **Bacterial champion HPs** | Hyperparameters frozen from the E. coli XGBoost protocol (trees/depth/etc.). Fair comparison to the bacterial exam. |
| **Capacity / deeper HPs** | Stronger XGBoost settings (more/deeper trees, etc.) tried on human because bacterial HPs underfit. |

**Two different questions — never mix them in one sentence:**

1. **Within-human:** Does adding flanks / capacity improve human CV ρ?  
2. **Transfer:** Does a model trained on E. coli rank human guides?

---

## Finding 1 — Guide-only cross-kingdom transfer fails

### Experiment
**Kingdom transfer / transfer autopsy** (early `kingdom_transfer` screen + Tier-1 `transfer_autopsy` in `run_human_boundary.py`).

- Take feature columns shared by name between E. coli and human published matrices (**guide-derived only** at this stage — no Family A yet).  
- Train selector + champion on **E. coli**.  
- Predict **human** activity with that frozen model.  
- Score Spearman ρ between predictions and human labels.

### Numbers
- E. coli → human transfer ρ ≈ **−0.04 to −0.05** (story quote often **−0.049**).  
- Reverse (human → E. coli) was messy; after proper human-side tuning one direction was compatible with ~0. The stable claim is still: **guide-only features do not travel**.

### What “negative ρ” means
The model’s ranking of human guides is slightly *anti*-correlated with truth — worse than a coin flip for picking better guides.

### Significance / claim
- **Claim:** Spacer / guide-derived chemistry learned in E. coli is **not** a portable ranking rule for this human cutting matrix.  
- **Do not claim:** “CRISPR doesn’t transfer” in general — you only tested this feature dialect + these two matrices.  
- **Why it matters in the paper:** Establishes the **kingdom wall** that later flank and capacity experiments try to explain or chip at.

---

## Finding 2 — The “wrong GC rule” autopsy (why GC looked like the answer)

### Context (why this experiment exists)
People noticed that **spacer GC vs activity** looks different across kingdoms:

- E. coli: roughly **linear negative** (higher GC → lower activity-ish).  
- Human: **flatter**, with a peak near GC ≈ **0.57**.

So a natural hypothesis: the E. coli model mainly learned an E. coli GC habit; apply it to human → fail. That *looked* like a smoking gun until you tested whether fixing GC fixes transfer.

### Experiment
Inside **transfer autopsy** (same E. coli→human shared-column setup as Finding 1):

1. Correlate **prediction error** with spacer GC.  
2. **Residualise** human y and predictions against GC and GC² (remove linear/quadratic GC effects), re-score transfer.  
3. **Match / stratify** by GC deciles (compare within similar GC bins).  
4. Optionally add GC+GC² as features on the human side (does GC alone buy within-human signal?).

### Numbers
- Error vs GC: ρ ≈ **−0.40** (errors *do* track GC).  
- After residualising / matching: transfer still ≈ **−0.049** (not rescued).  
- Putting GC+GC² into the human model: **does nothing** useful for the transfer story.

### What this means in plain English
Yes, the failed E. coli model is *wrong in a GC-correlated way*. That does **not** mean GC mismatch is the whole disease. Cleaning GC does not make rankings travel.

### Significance / claim
- **Claim:** GC-shape mismatch is a **symptom** of failed transfer, not a sufficient explanation or fix.  
- **Do not claim:** “GC is irrelevant to CRISPR.” GC still matters biologically; it just doesn’t open the kingdom wall here.  
- **Paper use:** One short paragraph after the transfer failure — “we checked the obvious GC story; it does not rescue ρ.”

---

## Finding 3 — Family A helps on human cutting (within-human ladder)

### Experiment
**Tier 1 human ladder** (`run_human_boundary.py` → `human_ladder.csv`).

Pipeline:

1. Decode human protospacers from the matrix.  
2. Locate unique NGG hits on **hg38** → **16,490** located rows.  
3. Build **regenerated base** matrix (same featurise dialect as E. coli).  
4. Build **Family A** flanks from ± windows around those loci.  
5. Cross-validate under **bacterial champion HPs**:
   - arm: base only  
   - arm: base + Family A  
   - (also arms like A-only / shared published cols exist; headline comparison is base vs base+A)

This is **not** transfer. Train/test folds are all human.

### Numbers

| Arm | Spearman ρ |
|---|---:|
| Regenerated base | **0.382** |
| Base + Family A | **0.434** |
| Gain (Δρ) | **+0.052** |

Compare to curated E. coli Family A gain ≈ **+0.164** (sealed ~**+0.156**).

### Significance / claim
- **Claim:** Local flanking composition improves human guide ranking under the same exam protocol; flanks are **not** an E. coli-only artifact.  
- **Claim carefully:** The human gain is **real but smaller** (~⅓ of the bacterial curated gain).  
- **Do not claim:** Human flanks “work as well as” bacterial flanks.  
- **Paper use:** Primary positive within-human biology result before honesty controls.

---

## Finding 4 — “Flanks on both sides” transfer (the confusing one)

### Context (why this exists)
Finding 1 used **shared published columns** — mostly guide chemistry that exists in both CSVs. Family A was **never in that transfer**, because flanks are *built from genomes*, not shipped as matching published columns by default.

So the old “nothing transfers” result mixed two issues:

1. Biology might not transfer.  
2. Or you never gave both sides the **same genomic-context features**.

“Flanks on both sides” fixes (2): build Family A on E. coli *and* on located human, align by feature name, then transfer.

### Experiment
**Tier 2/3** (`run_tier2_tier3.py`, E1-style) and related twin-honest follow-ups.

- Train on E. coli with a chosen feature set.  
- Predict human with the **same feature set** (columns matched by name).  
- Compare three feature sets:

| Feature set | What the model sees |
|---|---|
| Guide base | Spacer/chemistry only |
| Family A alone | Only flank summaries |
| Base + Family A | Both |

### Numbers (E. coli → human)

| Features | Transfer ρ |
|---|---:|
| Guide base | **−0.049** |
| Family A alone | **+0.042** |
| Base + Family A | **+0.022** |

Later **twin-honest** follow-ups (`run_twin_honest_followups.py`) put the honest flank-related Δ in the ~**+0.023** class (stricter bookkeeping; use when you need the conservative quote).

### What “sign flip” means
With guide-only features, transfer ρ is **negative**.  
With flank features present on both kingdoms, transfer ρ becomes **weakly positive**.

That does **not** mean you have a good cross-kingdom product. ρ ≈ 0.02–0.04 is tiny next to within-human ~0.43–0.50.

### Significance / claim
- **Claim:** Part of the early kingdom wall was a **representation gap** (missing comparable flank context), not only irreducible biology mismatch.  
- **Claim:** Even with flanks, transfer remains **scientifically interesting but practically weak**.  
- **Do not claim:** “We solved cross-kingdom prediction.”  
- **Paper use:** One clear sentence: guide-only fails; adding aligned flanks flips sign weakly; productization is not claimed.

---

## Finding 5 — Human strand audit (CRISPRi scare does not apply)

### Context
In **E. coli CRISPRi** (dCas9 silencing), Family A’s pooled gain largely collapsed once you gave the model an explicit **coding-strand** bit — flanks were partly a strand/purine proxy. That threatened the cutting story: maybe “flanks” were never real.

So you must ask: on **human cutting**, does the same collapse happen?

### Experiment
`run_human_strand_audit.py` on located human cutting data.

- Correlate coding-strand with human cut score.  
- Re-run Family A gain **conditional on / given strand**.

### Numbers
- Coding strand vs cut score ≈ **−0.010** (essentially null).  
- Family A gain given strand ≈ **+0.048** vs raw ladder gain **+0.052**.

### Significance / claim
- **Claim:** On this human cutting matrix, Family A is **not** a strand confound.  
- **Claim:** CRISPRi strand biology and human cutting flank biology must be **narrated separately**.  
- **Do not** import the CRISPRi collapse as if it invalidated human A.

---

## Finding 6 — Chromatin / accessibility (mostly null)

### Experiments
1. **Tier 2 chromatin** (`run_tier2_tier3.py`): ENCODE **K562** DNase/ATAC at located loci, add as features, measure Δρ.  
2. **H6 matched chromatin** (`run_h6_chromatin.py`): tracks closer to Noshay’s mixed lines (**HCT116, HEK293T, HeLa, HL-60**), because the human matrix is not a single clean cell line.

Caveat baked into the design: matrix has **no per-guide cell-line labels**; A375 tracks weren’t available in that sweep. H6 GC/coverage control (`run_h6_gc_coverage_control.py`) was started to ask whether tiny Δρ is just GC/coverage — **paused / incomplete** in the tracker.

### Numbers
- K562 DNase/ATAC: ~**+0.001 to +0.005** (null).  
- H6 best: ~**+0.01** on base; ~**null once Family A is already in**.

### Significance / claim
- **Claim:** Local accessibility as measured here does **not** explain a +0.16-class effect and does not beat flanks.  
- **Hedge:** Measurement/matching limits (mixed lines, missing labels) mean you report a **null under these assays**, not “chromatin never matters in CRISPR.”

---

## Finding 7 — Capacity (H1): the big within-human modeling win

### Context
Bacterial champion HPs were frozen for fairness. On human they **underfit**: the signal looks less additive than E. coli, so deeper/faster trees help.

### Experiment
**Human discovery H1** (`run_human_discovery.py`): same human matrices, swap HP recipe.

### Numbers (seeds 41–43 mean in the story)

| Arm | ρ | vs bacterial HPs |
|---|---:|---:|
| Base + bacterial HPs | 0.383 | — |
| Base + deeper/faster HPs | **0.474** | **+0.091** |
| Base + A + bacterial HPs | 0.431 | — |
| Base + A + deeper HPs | **0.501** | **+0.118** |

Note: discovery sometimes used a lighter probe (e.g. 400 trees / depth 6) for speed; direction matches Runjia’s ~**0.51** human baseline story. Pin absolute paper quotes with a full re-run if the report needs one canonical number.

### Significance / claim
- **Claim:** Human predictive performance can be raised substantially by **model capacity**, with or without Family A.  
- **Claim:** Capacity is a **within-human fit** story; it does **not** by itself fix E→H transfer.  
- **Do not** present 0.50 as “transfer solved.”

---

## Finding 8 — Additivity (H2)

### Experiment
Compare **ridge** (linear) vs **trees** on human under the discovery protocol.

### Numbers
- Ridge reaches only ~**66–68%** of tree performance on human.  
- In E. coli the same comparison was ~**96%** (nearly additive).

### Significance
Supports H1: human needs nonlinear capacity; flanks + deeper trees are not optional cosmetics.

---

## Finding 9 — Gene-grouped CV (H3)

### Experiment
Hold out **whole genes** (not random rows) so the model can’t cheat via gene identity leakage when scoring Family A.

### Result (qualitative in story)
Family A **still helps** under gene-grouped CV.

### Significance
Honesty control: flank gain is not “memorize which gene is easy.”

---

## Finding 10 — Shape / mechanics / folding on human (H4) + transfer retest (H5)

### Experiment
Add i_shape / d_mechanics / c_folding-style families **on top of Family A** in human discovery; then recheck transfer.

### Result
- **Null** on top of A (stops feature fishing).  
- Transfer: still only flanks flip the sign; these extras don’t open the wall further (H5).

---

## Suggested claim order when you write

1. Kingdom wall: guide-only transfer ρ ≈ −0.05.  
2. GC autopsy: error tracks GC, but fixing GC does not rescue transfer.  
3. Within-human Family A: 0.382 → 0.434 (+0.052) on 16,490 located guides.  
4. Strand audit: not a CRISPRi-style confound on human cutting.  
5. Flanks both sides: transfer sign flips to ~+0.02–0.04; honesty ~+0.023 class — scientific signpost, not a product.  
6. Chromatin/shape: nulls / negligible.  
7. Capacity: human ρ → ~0.47–0.50; ridge≪trees; transfer still unsolved.

**One-sentence thesis:** Human cutting shows a modest, strand-robust flank gain and a weak transfer sign-flip when flanks are aligned across kingdoms; guide-only transfer fails for reasons beyond GC; accessibility extras are null here; capacity raises within-human fit without closing the kingdom gap.

---

## Scripts ↔ findings (quick map)

| Finding | Main script(s) |
|---|---|
| Guide-only transfer / GC autopsy | `run_human_boundary.py` (transfer_autopsy), `screens/kingdom_transfer.py` |
| Human ladder +0.052 | `run_human_boundary.py` (ladder) |
| Flanks both sides | `run_tier2_tier3.py`; honesty: `run_twin_honest_followups.py` |
| Strand | `run_human_strand_audit.py` |
| Chromatin | `run_tier2_tier3.py`, `run_h6_chromatin.py` (+ paused GC/coverage control) |
| H1–H5 | `run_human_discovery.py` |

---

## Still soft / paused (don’t over-quote)

- **Twin-honest** full CSV and **H6 GC/coverage control** were paused mid-run in the project tracker — treat ~+0.023 and “chromatin not just GC” as directions to confirm if the report needs final locked numbers.  
- Discovery HP probe vs full 1000-tree recipe: pin before camera-ready tables.
