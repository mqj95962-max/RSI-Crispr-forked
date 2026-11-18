# The CRISPR story, start to finish

*A narration of what our team actually did, in chronological order, with the real numbers. Written so you can read it top to bottom like watching a long explainer video — no assumed background beyond “CRISPR guides cut DNA, and we want to predict which guides work.”*

**Who this is for:** You, before a mentor meeting.  
**What this is not:** A paper abstract. It’s the plot.

---

## Cold open — what problem were we even solving?

Imagine you want to edit a gene with CRISPR-Cas9. You pick a short 20-letter DNA sequence (the **guide** / **sgRNA** / **protospacer**). Some guides cut efficiently. Some barely work. Predicting that from sequence alone is a known hard problem.

Our project started with a public resource from **Noshay et al. 2023**: a huge spreadsheet of ~6,000 “features” for thousands of *E. coli* guides — quantum chemistry, k-mers, melting temperatures, etc. The pitch of that paper was: these fancy features help explain guide efficiency.

Our team’s evolving goals became two linked questions:

1. **Can we predict guide efficiency well** — especially with something simple and trustworthy?
2. **Does what we learn transfer** — to another enzyme, another bacterium, or to **human**? And if transfer fails, *why*?

That second question is why human work exists. Cross-species wasn’t an afterthought in the *goal*; it became an afterthought in the *calendar* because bacteria had to be solid first.

---

## Act 1 — “Wait… what even is this spreadsheet?”

### The setup

Early work (Jacky, Joshua, shared baseline scripts) was classic student ML: take the Noshay matrix, train XGBoost, try new features (regional QCT, PAM weights, structure proxies, essentiality…), compare five-seed CV scores.

That phase built intuition and a shared **leakage-safe baseline** (feature selection only on training folds; seeds 41–45). But the deep story starts when Runjia treated the matrix as something to **decode**, not just feed into a model.

### Finding: most of the matrix is the guide, written 6,000 times

A 20-letter DNA word only holds so much information. The published matrix has **6,232 columns**.

What Runjia showed (Finding 1):

- **5,853** anonymous `V####` columns are position-specific k-mer indicators (“is position 7 a C?”, “is positions 3–4 CG?”, …).
- **316** quantum columns are lookup tables of physical properties of those same letters.
- Together, **~99%** of columns (**6,169 / 6,232**) can be regenerated from the 20-mer alone — exact arithmetic, not a fuzzy model fit.

**What that means in human words:**  
If Feature Family X is a deterministic function of the guide sequence, it **cannot** tell the model anything the matrix didn’t already encode. A lot of “we tried a new biophysical family and it didn’t help” was doomed *before* training.

**Why it mattered:** It reframed the project. The missing signal, if any, had to live **outside** the 20 letters — in the DNA around the cut site, or in assay biology the matrix never measured.

---

## Act 2 — The one large effect: flanking DNA (“Family A”)

### What Family A is

**Family A (`a_flank`)** = summaries of the DNA **around** the target: GC content, purine content, composition in windows like ±50, ±250, ±500, ±1000 nucleotides. Not “find a motif.” More like: “what’s the neighbourhood like?”

Built by locating each guide on the *E. coli* genome and cutting those flanks.

### The number that became the spine of the project

On crisprHAL’s **curated** ~33.5k-guide *E. coli* SpCas9 set (the cohort we eventually trained on):

| Model features | Spearman ρ (roughly “how well ranks match”) |
|---|---:|
| Guide-derived “base” only | ~0.54 |
| Base + Family A | ~0.71 |
| **Gain from flanks** | **+0.164** |

That **+0.164** is the largest feature-family effect in the whole bacterial analysis.

On genes completely held out through development (**sealed** evaluation):

- Same gain is still **+0.156**.

So it’s not “we overfit the genes we stared at.”

On the older **published** Noshay 13,880-row matrix the gain was smaller but real: about **+0.080**. Same phenomenon, both labels/cohorts.

### Shape of the effect (why we say “gradient, not motif”)

Several controls, in plain language:

1. **Spatial shift null.** Take the flank features but read them from DNA shifted along the chromosome (texture-preserving shuffle of *where* you look).
   - At **1 kb** shift: only ~**8%** of the gain survives.
   - At **10 kb**: gain ≈ **gone**.
   - Meaning: the useful context is **local** to the cut, not a vague chromosome vibe.

2. **Window widths.** Using slightly different window sets barely changes the gain (~+0.1634 vs +0.1638). We’re not cherry-picking one magic width.

3. **K-mer order.** Going to tetramer “motifs” doesn’t buy useful extra signal. It’s smooth composition, not a sharp word.

4. **Not target GC in disguise.** Guide GC and flank GC both relate to activity, but **in opposite directions** in *E. coli*:
   - Higher **guide** GC → tends to **worse** cutting (in this assay).
   - Higher **flank** GC → tends to **better** cutting.
   - If you hold target GC fixed, the flank association **gets stronger**, not weaker.
   - So the naive objection “it’s just GC” fails.

5. **Within genes.** Even predicting *inside* a gene (not just ranking easy vs hard genes), flanks help (on the published cohort, about **+0.061** within-gene).

**What Family A means for the story:**  
*E. coli* Cas9 cutting efficiency depends on the DNA neighbourhood. That is the core scientific claim.

**What Family A does *not* mean yet:**  
We still don’t know the molecular mechanism (repair? melting? polymerase traffic? something else?).

---

## Act 3 — Killing wrong explanations (the “disprove” era)

This is the part that feels like “we only disprove things.” That’s partly true — and it’s how you earn the right to claim Family A is real.

### Supercoiling, shape, periodicity, Chi sites, etc.

Named feature families from literature/intuition were tested as ablations:

- **DNA shape** of flanks on top of Family A ≈ **nothing** (shape is largely a reparameterisation of composition).
- **Helical periodicity / GC skew** ≈ **null**.
- **“Supercoiling” tracks** — the no-antibody control predicted about as well as the ChIP signal; a lot of it was **gene dosage** (distance to origin), not mystical topology.
- **Chi sites** (RecBCD repair motif) looked like any GC-matched octamer — **not** a special repair story at that resolution.
- **Essentiality** as an interaction story mostly failed; weak expression signals exist but aren’t the Family A story.

**Meeting sentence:**  
“We tried the tidy biological stories. Several collapsed into composition, dosage, or assay artefacts. We’re not assigning a pathway yet.”

### Redescription / recoverability (why “more nonlinear features” didn’t save us)

Runjia also asked: if a column is almost determined by the guide, can it still help?

Short version:

- Random fake tables shaped like real ones → **null**.
- Columns the guide fully determines → tiny gains (~**+0.008**).
- Columns *outside* the guide → huge (~**+0.20** class).
- Real RNA folding energy helps a little (~**+0.012**) and shuffled folds don’t — so *some* physics is real, but it’s small next to flanks.

**Meaning:** The project’s gains aren’t from “XGBoost magic on redundant encodings.” They’re from **information the guide doesn’t contain**.

---

## Act 4 — Pivot to crisprHAL and parity with the deep model

### Why the pivot (13 October 2026-ish)

Noshay’s published matrix used `cut.score`. crisprHAL 2 released a **curated** Guo-screen derivative with an ALDEx2 score and became the community baseline to beat.

Important: the two labels agree in *rank* on overlapping guides (ρ ~0.95) but are **different quantities**. Every number belongs to one frame or the other.

### Head-to-head with crisprHAL 2

On **crisprHAL’s own published eSpCas9 split** (their train/test, their weights):

| Model | Spearman ρ |
|---|---:|
| crisprHAL 2 | 0.7821 |
| SLICER (our boosted trees + flanks) | **0.7842** |
| Difference | **+0.0021** (95% CI [−0.0031, +0.0072]) |

That CI includes zero inside a pre-declared ±0.01 equivalence margin → **statistical parity**, not a claimed win.

SpCas9 split: similarly about **+0.005**.

On *our* curated folds we sometimes look ahead by ~0.01–0.017 — but search effort wasn’t equalised there, so the **quotable** claim is:

> **Parity on their protocol, at ~150× less CPU and with a tiny model, plus better behaviour when data is scarce.**

Also measured:

- Label reliability ceiling from replicates ≈ **0.946**.
- Best models here ≈ **0.72**.
- Gap ≈ **0.22 ρ** of reproducible biology still unused → more model tuning on the *same* features won’t close everything; new measurements likely needed.

**Why the DNA-neighbourhood story connects to beating/matching a CNN–BiGRU:**  
crisprHAL already reads a few hundred bases of sequence. Our advantage is largely **longer-range flank summaries**. When you equalise DNA span, the story gets more subtle (their convolutions can beat windowed means *inside* their design width; our ±1 kb reach is where we pull ahead). The email’s “simple model matches deep learning” is fair **if** you keep “parity + cost,” not “we dominate every setting.”

---

## Act 5 — Does the flank effect travel? (bacterial transfer)

Train on one system, test on another **without retraining**:

| Transfer | Transfer ρ | Local (trained there) ρ | Roughly retained |
|---|---:|---:|---:|
| *E. coli* SpCas9 → eSpCas9 (same genome, different nuclease) | **~0.689** | **~0.784** | ~**88%** |
| *E. coli* SpCas9 → *C. rodentium* TevSpCas9 | **~0.698** | **~0.766** | ~**91%** |

**Meaning:** A big chunk of what Family A learns is about **DNA context**, not a quirk of one enzyme packaging.  

**Limit:** This is still Enterobacteriaceae / related assays — not “all bacteria.”

---

## Act 6 — Cutting vs CRISPRi: the strand plot twist

This is the most confusing chapter. Stay with it.

### The hope

If Family A were “just Cas9 binding / accessibility,” it should also show up when Cas9 is dead (**dCas9 CRISPRi**): same binding, no cut — phenotype is gene silencing / fitness.

### What happened on Cui (and Rousset)

- Across the whole CRISPRi screen, Family A looked ~**null** (about **−0.009**).
- Inside **essential** genes it looked huge (~**+0.27**) — scary, almost undoes the story.
- Resolution: CRISPRi has a monstrous **strand** effect. Coding-strand guides deplete much more (strand alone ρ ≈ **0.66**).
- Family A’s strongest CRISPRi column was basically a **purine / strand proxy**.
- Hand the model an explicit strand bit → Family A’s pooled gain collapses to ~**+0.007 to +0.015**.
- Among **coding-strand guides alone**, some residual flank signal remains (~**+0.12**) — so not a perfect “zero everywhere.”

Rousset (another CRISPRi screen) **replicates** the strand structure. Wang’s library is coding-strand-only, so the control is vacuous there — and Wang does *not* behave the same. That’s an open asterisk.

**What we say carefully (as in the email):**  
The big pooled flank effect of **cutting** is unlikely to be “binding only.” It’s more consistent with something **break-related**. But:

- CRISPRi ≠ perfect negative control.
- The cellular assay measures **depletion**, not cleavage molecules.
- Residual within-strand CRISPRi effects exist.
- Mechanism remains **unknown**.

---

## Act 7 — Orientation in *E. coli* intergenic DNA (Jacky side quest)

On coding-heavy matrices you can’t study “guide vs transcription direction” cleanly — almost everything is one orientation.

Jacky rebuilt **intergenic** guides and tested orientation to genes / TSS:

- Nearest-gene “opposite vs same” looked promising but got **borderline** under matching.
- **TSS orientation**: opposite minus same Δ ≈ **0.051 [0.020, 0.082]** — clearer.
- Paper-facing takeaway: lead with **TSS**, not nearest gene.

This is supporting bacterial biology context; it’s not the human transfer headline.

---

## Act 8 — Human: why transfer failed, and what we actually learned

### The original kingdom wall

Train on *E. coli* guide-derived columns, predict human (shared published columns only):

- Transfer ρ ≈ **−0.04 to −0.05** (worse than chance ranking).
- Reverse direction was messy; after properly tuning the human side, one direction became compatible with zero — but the failure mode remained: **guide-only features don’t travel**.

Also: spacer GC vs activity has **different shape** across kingdoms (*E. coli* linear-ish negative; human flatter / peaks near GC ≈ 0.57). That looked like a smoking gun… until we checked.

### “Wrong GC rule” autopsy

Errors of an *E. coli* model on human **do** correlate with spacer GC (ρ ≈ **−0.40**).  
But residualising GC² or matching GC distributions **does not** rescue transfer (still ≈ **−0.049**).  
Putting GC+GC² into the human model also does nothing.

**Meaning:** GC mismatch is a **symptom**, not the whole disease.

### Building Family A on human (Tier 1)

Steps:

1. Decode spacers from the human matrix.
2. Locate unique NGG sites on **hg38** → **16,490** usable located rows.
3. Build the same flank family.
4. Human-only ladder (bacterial champion HPs):

| Arm | ρ |
|---|---:|
| Regenerated base | **0.382** |
| Base + Family A | **0.434** |
| **Gain** | **+0.052** |

Smaller than curated *E. coli*’s +0.164, but clearly positive. **Flanks aren’t an *E. coli*-only quirk.**

### Transfer with flanks on both sides (Tier 3)

| Features | *E. coli* → human |
|---|---:|
| Guide base | **−0.049** |
| Family A alone | **+0.042** |
| Base + Family A | **+0.022** |

**This is the key cross-kingdom sentence:**  
Part of the old “nothing transfers” result was **missing comparable genomic context** on the human side. When you build flanks both places, the sign flips from negative to weakly positive.

**Critical honesty:** +0.022 is **not** a usable cross-kingdom product. It’s a scientific signpost about representation, not a solved engineering problem.

### Human strand audit (after bacterial CRISPRi scare)

Question: “Did Family A on human secretly collapse to strand like CRISPRi?”

Answer:

- Coding-strand vs human cut score ≈ **−0.010** (null).
- Family A given strand still ≈ **+0.048** (almost the full +0.052).
- So: **CRISPRi strand story ≠ human cutting story.** Keep them separated in any talk.

### Chromatin

- First try: **K562** DNase/ATAC → ~null (+0.001–0.005).
- Later H6: matched-ish lines from Noshay’s mix (**HCT116, HEK293T, HeLa, HL-60**) → best ~**+0.01** on base, ~null given Family A.
- Caveat: matrix has **no per-guide cell-line labels**; A375 ENCODE tracks weren’t available in that sweep.

**Meaning:** Local accessibility, as we can measure it, is not the missing +0.16-class effect on this human matrix.

---

## Act 9 — Human discovery: “can we improve human like we improved bacteria?”

You asked for positives, not only nulls. H1–H6:

### H1 — Capacity (the actual new human positive)

Bacterial champion settings underfit human.

| Arm | ρ (seeds 41–43 mean) |
|---|---:|
| Base + bacterial HPs | 0.383 |
| Base + deeper/faster HPs | **0.474** (+0.091) |
| Base + Family A + bacterial HPs | 0.431 |
| Base + Family A + deeper HPs | **0.501** (+0.118) |

**Meaning:** We *can* improve the human model a lot — partly by using a model shape that matches human’s less-additive signal.

**Does this fix transfer?** No. Capacity is a within-human fit change. Transfer still cares about shared biology/representation.

*(Note: discovery used a lighter “400 trees, depth 6” probe for speed, not always the full 1000-tree teammate recipe. Direction matches Runjia’s ~0.51 human baseline story; absolute paper quotes can be pinned with a full re-run if needed.)*

### H2 — Additivity

Ridge reaches only ~**66–68%** of tree performance on human (vs ~96% in *E. coli*). Supports why depth matters.

### H3 — Gene-grouped CV

Family A still helps when whole genes are held out. Good control.

### H4 — Shape / mechanics / folding on human

**Null** on top of Family A. Stops feature fishing in that pond.

### H5 — Transfer after those arms

Still: only flanks flip the sign; extras don’t open the wall further.

### H6 — Matched chromatin

Weak. See above.

---

## The whole plot in one breath

1. We inherited a giant feature matrix that was mostly the guide sequence in disguise.  
2. The real bacterial signal was **flanking DNA composition** (+0.164 curated; +0.156 sealed).  
3. It’s local, not a motif, not target-GC confounding, survives harsh controls.  
4. Mechanism is still open; several pretty stories failed.  
5. Cutting vs CRISPRi suggests the big pooled effect isn’t binding-only; strand dominates silencing assays.  
6. Related bacteria: flanks travel (~88–91% retained).  
7. Human: flanks help (+0.052); guide-only transfer fails; flanks both sides flip transfer weakly positive; strand isn’t the human cutting confound.  
8. Modelling: SLICER ≈ crisprHAL on their splits, far cheaper; ceiling 0.946 says biology remains on the table.  
9. Newest human lesson: **capacity** lifts human to ~0.50; chromatin/shape extras don’t; transfer still isn’t solved.

---

## How to answer “haven’t we mostly disproved things?”

Disproofs are the scaffolding that makes the few positives believable.

**Positives you can plant a flag on:**

1. Matrix decode / redundancy.  
2. Family A in *E. coli* cutting.  
3. Parity + cost vs crisprHAL.  
4. Bacterial transfer of context.  
5. Human Family A exists; representation (not only GC) matters for kingdom wall.  
6. Human capacity gain (~0.38 → ~0.50 with A + deeper HPs).

**Open / unresolved (say this out loud — mentors respect it):**

- Exact molecular mechanism of flanks.  
- Strong cross-kingdom predictor (sign flip ≠ product).  
- What fills the 0.72 → 0.946 gap.  
- Per-guide human cell-line biology (matrix is a mix).

---

## Glossary (30 seconds)

| Term | Meaning |
|---|---|
| **Spearman ρ** | Rank correlation from −1 to 1. 0 = no ranking skill; 1 = perfect ranking. |
| **Family A / flanks** | Features from DNA surrounding the cut site. |
| **Base** | Guide-derived regenerated features (the 20-mer’s encoding). |
| **Sealed genes** | Genes held out of all development; final honest test. |
| **CRISPRi / dCas9** | Dead Cas9; binds and blocks, doesn’t cut. |
| **Transfer** | Train on dataset A, predict dataset B with no retraining. |
| **SLICER** | Our name for the simple tree model + representation. |
| **crisprHAL 2** | Published deep-learning baseline we’re compared against. |

---

## If you only remember five numbers for the meeting

1. **+0.164** — Family A on curated *E. coli*  
2. **+0.156** — same on sealed genes  
3. **0.7842 vs 0.7821** — SLICER vs crisprHAL on their eSpCas9 split (parity)  
4. **0.382 → 0.434** — human Family A under champion HPs; **~0.50** with deeper HPs  
5. **−0.05 → +0.02** — kingdom transfer before vs after building flanks both sides  

---

## Where the receipts live

| Story beat | Start here |
|---|---|
| Full bacterial write-up | `Runjia/PROGRESS_REPORT.md` |
| Claim → CSV index | `Runjia/results/RESULTS.md` |
| Human checklist | `Jacky/human-boundary/README.md` |
| Human discovery H1–H5 | `Jacky/human-boundary/DISCOVERY_RESULTS.md` |
| H6 chromatin | `Jacky/human-boundary/H6_CHROMATIN_RESULTS.md` |
| Experiment catalog (chrono table) | `Jacky/EXPERIMENT_CATALOG.md` |
| Team email-style human report | `Jacky/human-boundary/HUMAN_RESULTS_REPORT.md` |

---

*End of narration. If something still feels fuzzy after one full read, it’s usually either (a) cutting vs CRISPRi strand, or (b) “weakly positive transfer” vs “solved transfer” — those two distinctions carry most of the remaining confusion.*
