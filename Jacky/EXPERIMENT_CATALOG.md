# Experiment catalog (whole project)

One table of load-bearing experiments across the repo, **ordered chronologically**
so the progression is readable. No attribution by person.

Dates are approximate from git history and report freezes (the working
chronology log was retired; git is the authority). Within a phase, rows follow
the scientific story when many results landed on the same day. Joshua’s early
QCT Colab scripts (`Joshua/`) are omitted by request — they predate the SLICER
pipeline and do not have archived Δρ in `Runjia/results/`.

**How to read the columns**

| column | meaning |
|---|---|
| **Experiment** | Short name of the analysis |
| **Finding** | What it showed (key numbers) |
| **Code** | Committed runner; evidence under `Runjia/results/` unless noted |
| **Project impact** | How it moved the overall story |

**Frames:** **[P]** = Noshay published 13,880-guide matrix; **[C]** = crisprHAL curated ~33.5k.

---

## Timeline (at a glance)

| Phase | When (approx.) | What moved |
|---|---|---|
| 0 | Jul–Aug 2026 | Shared five-seed baseline; early personal feature probes |
| 1 | ≈ Sep – early Oct 2026 | Decode published matrix; discover Family A **[P]**; rule out named families |
| 2 | ≈ 5–12 Oct 2026 | Guo/ceiling hygiene; intergenic orientation → TSS controls |
| 3 | ≈ 13–25 Oct 2026 | Pivot to curated **[C]**; Family A +0.164; crisprHAL parity + cost; kingdom wall (shared cols) |
| 4 | 16 Oct 2026 | Human Tier 1: locate + Family A ladder (+0.052); transfer still negative |
| 5 | ≈ 26–31 Oct 2026 | Redescription / recoverability prelude; Cui CRISPRi null → essentiality shock → strand control restores localisation |
| 6 | 2 Nov 2026 | Human Tier 2–3: chromatin null; Family A flips cross-kingdom transfer positive |
| 7 | ≈ 8 Nov 2026 | Rousset replicates strand story; within-strand residual; inference cost; interpretability |
| 8 | 16 Nov 2026 | Human strand audit: cutting ≠ CRISPRi; Family A survives gene-strand |

---

## Phase 0 — Shared baseline & early probes (Jul–Aug 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Shared five-seed baseline harness | Leakage-safe XGBoost CV (seeds 41–45, top-300, 400 trees) is the common comparator. | Root `USE THIS!! FINAL_baseline_ecoli_sgRNA_model_5seeds.py`; also `Jacky/FINAL_baseline_model_5seeds.py` | Gave every later arm a reproducible baseline to beat. |
| Early personal human XGBoost (historical) | Quoted ρ≈0.472 at 400 features / 1000 estimators (pre-harness). | Settings in `Jacky/human-boundary/HUMAN_BASELINE_SETTINGS.md`; original personal script **not in repo** | Motivated the later human re-tune; not the current harness. |
| Guide index / QCT tables (infra) | Locate published guides on NC_000913.2; learn QCT k-mer lookup tables. | `Runjia/sgrna/build_guide_index.py`, `qct.py` — evidence: `Runjia/data/interim/…` | Prerequisite for every Family A / mechanism experiment. |
| Feature / matrix build (infra) | Build eleven feature families and the assembled matrix. | `Runjia/sgrna/build_features.py`, `build_matrix.py`, `features/*.py` | Shared featurisation path for ablations. |

---

## Phase 1 — Decode the matrix & find Family A on published data (≈ Sep – early Oct 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Portability audit (V-column decode) | 5,853 of 5,887 `V` columns decode; ~99% of 6,232 published columns regenerate from a 20-mer. | `Runjia/sgrna/expand.py`, `decode_v_columns.py` — evidence: `portability_audit.csv` | Established the published matrix as mostly guide re-encoding. |
| Portable 412-column reduction **[P]** | 412 computable columns match all 6,232 at ρ≈0.00003. | `Runjia/sgrna/portability.py` — evidence: `portability.csv`, `portability_364.csv` | Showed a portable reduced pool on the published cohort. |
| Published Family A ablation **[P]** | Flanking DNA composition **+0.080 ρ** — the large effect on the published matrix. | `Runjia/sgrna/run_ablation.py` — evidence: `ablation_main.csv` | Discovered the one large effect that the project pivots around. |
| Within-gene flank gain **[P]** | Not gene ranking: +0.061 within-gene. | `Runjia/sgrna/run_ablation.py` (`--grouping gene`) — evidence: `ablation_grouped.csv`; also `Jacky/agent-notes/results/within_gene_metrics.json` | Practitioner claim: better guides *inside* a gene. |
| Circular shift null | Texture-preserving shift destroys the effect: 8% at 1 kb, 0 at 10 kb. | `Runjia/sgrna/shiftnull.py` — evidence: `shift_null.csv` | Localised the effect spatially. |
| GC strata (published) | Not target GC in disguise: conditioning raises +0.044 → +0.082. | `Runjia/sgrna/gcstrata.py` — evidence: `gc_strata_corr.csv`, `gc_strata_ablation.csv` | Target GC is a suppressor, not a confound. |
| Abundance / mappability split | Claimed gain +0.078 → +0.051 on high-uniqueness; one `uniq` definition later unreproducible. | `Runjia/sgrna/run_ablation.py` (`--tag abund_split`) — evidence: `ablation_abund_split.csv`; `abund_local_vs_mappability.csv` **not reproducible** | Intended to close sequencing-artefact objection; later flagged. |
| Periodicity family null | GC skew / helical periodicity null (−0.001 alone, +0.0004 on A). | `Runjia/sgrna/run_ablation.py` (`--families j_periodicity`) — evidence: `ablation_jper.csv` | Ruled out helical-phasing mechanism. |
| Shape family null | Shape is a reparameterisation of composition (+0.0007 on A). | `Runjia/sgrna/run_ablation.py` (`--families i_shape`) — evidence: `ablation_shape_joint.csv` | Ruled out DNA-shape-as-new-signal. |
| Supercoiling dissection | Read-density mostly gene dosage; no-Ab control ≈ ChIP. | `Runjia/sgrna/make_diagnostic_blocks.py` / `rederive.py` — evidence: `dissection_supercoiling.csv` | Overturned the named “supercoiling” family via its own control. |
| K-mer order / gradient | Tetramers buy nothing (−0.0019); motif order fails. | `Runjia/sgrna/rederive.py` / `curated_ladder.py` — evidence: `kmer_order_noselect.csv` | Gradient-not-motif claim. |
| SeqNet matched windows | CNN flat then declines (±250 best 0.525) vs windowed means +0.080. | `Runjia/sgrna/seqnet.py` — evidence: `seqnet_matched.csv` | Windowed composition beats a naive CNN on sample efficiency. |
| Permutation floors | Family A shuffled floor ≈ baseline; periodicity shuffled > real. | `Runjia/sgrna/floors.py` — evidence: archived `permutation_floors.csv` | Family A gain is above selector/noise floor. |
| Expression-banded asymmetry null | PAM-side asymmetry flat across expression terciles. | `Runjia/sgrna/asymmetry.py` — evidence: archived `asymmetry_expression.csv` | Closed expression-scaled transcription account on coding guides. |
| Strand audit (coding matrix) | Orientation-conditioned asymmetry impossible on Noshay coding matrix (~all template). | `Runjia/sgrna/asymmetry.py` (`--audit`) — evidence: `asymmetry_strand_audit.csv` | Explained why an intergenic rebuild was required. |
| Noshay iRF replication | iRF 0.479 vs SLICER 0.606 on Noshay data. | `Runjia/sgrna/noshay_replicate.py` — evidence: `noshay_replication.csv` | Beat prior published model mostly via Family A. |
| Bacterial transfer (nuclease / organism) | Retain ~88% / 91% across nuclease and nuclease+organism. | `Runjia/sgrna/transfer.py` — evidence: `transfer_model.csv`, `transfer.csv` | Effect “belongs to the DNA” across enzyme/host. |
| Training cost / complexity (early cost panel) | ~150× CPU-seconds, 92× wall-clock; 6,348 leaf values vs 790,533 params. | `Runjia/sgrna/cost.py`, `complexity.py` — evidence: `cost_*.csv`, `complexity.json` | Lightweight-model story begins. |
| Sample complexity / learning curve | Lead is small-data: +0.013 at 26.9k, +0.002 at 47.6k. | `Runjia/sgrna/sample_complexity.py` — evidence: `sample_complexity.csv`, `learning_curve.csv` | Reconciled fold wins vs parity-at-scale. |
| Importance cross-model | Native importance agrees poorly across models (~0.05) vs SHAP (~0.50). | `Runjia/sgrna/importance_models.py` — evidence: archived importance tables | Importance instability is matrix redundancy. |
| Faithfulness drop-and-refit | Drop-top-*k*-and-refit is uninterpretable on a redundant matrix. | `Runjia/sgrna/faithfulness.py` — evidence: archived faithfulness tables | Motivated fixed-model attribution later. |
| Residual headroom scan | After base+A, no held-back column correlates with residuals above ~0.03. | **No committed runner** — evidence: archived `headroom.csv` | Model is material-limited after Family A. |
| Two-enzyme ceiling (negative) | SpCas9 vs eSpCas9 disagreement partly biology; killed two-enzyme 0.90–0.93 as primary ceiling. | `Runjia/sgrna/ceiling2.py` — evidence: `Jacky/agent-notes/results/ceiling_from_runjia.json` | Forced the Fig 2b/2c ceiling route. |

---

## Phase 2 — Ceiling hygiene & orientation thread (≈ 5–12 Oct 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Guo tables inventory / label provenance | No per-guide replicates in Data S1–S7; `cut.score` ↔ Guo S4 Cas9 ρ≈1.0. | **No dedicated runner** — evidence: `Jacky/agent-notes/results/guo_*`, `label_provenance.json` | Settled what the published label is. |
| Guo reliability ceiling | Fig 2c tiling ceiling ≈0.937; working figure ~0.94. | **No dedicated runner** — evidence: `Jacky/agent-notes/results/guo_reliability_ceiling.json` | Same-enzyme ceiling without SRA. |
| High-uniqueness flank stratum (rebuild) | High-uniqueness quartile: Δρ +0.078 → +0.051 (n=4,949). | `Jacky/agent-notes/scripts/workplan.py` — evidence: `Jacky/agent-notes/results/flank_high_uniqueness_stratum.csv` | Independent rebuild supporting mappability survival. |
| Transfer bootstrap CIs | *E. coli*↔*C. rodentium* CIs with guide-overlap hygiene. | `Jacky/agent-notes/scripts/workplan.py` — evidence: `Jacky/agent-notes/results/transfer_bootstrap.csv` | CIs for bacterial transfer claims. |
| Cross-kingdom bootstrap (early) | Both directions negative (−0.048 / −0.056) before human re-tune. | `Jacky/agent-notes/scripts/workplan.py` — evidence: `Jacky/agent-notes/results/cross_kingdom_bootstrap.json` | First kingdom-wall measurement (later re-scoped). |
| Spacer GC quadratic shape | *E. coli* linear ρ −0.201; human quadratic peak GC≈0.57. | `Jacky/agent-notes/scripts/workplan.py` — evidence: `gc_quadratic_proper.json` | “Different GC shape across kingdoms” hypothesis. |
| ΔrecA flank ablation | Absolute flank gain shrinks on ΔrecA but relative Δ/baseline does not. | `Jacky/agent-notes/scripts/run_reca_and_orientation.py` — evidence: `Jacky/agent-notes/results/reca_flank_summary.csv` | Repair account not supported (saturating-assay caveat). |
| Replichore asymmetry null | Left/right matched asymmetry ~0.049 / 0.048 — no sign flip. | `Jacky/agent-notes/scripts/workplan.py` — evidence: `Jacky/agent-notes/results/asymmetry_replichore*.csv` | Closed replication-fork co-orientation account. |
| Intergenic orientation (nearest-gene) | Opposite asymmetry ≈0.047 vs same ≈0.005 (S6 Good). | `Jacky/orientation-controls/scripts/run_intergenic_orientation.py` — evidence: `Jacky/orientation-controls/results/intergenic_orientation_summary.csv` | Re-opened transcription/orientation on both-strand intergenic guides. |
| Orientation Δ bootstrap (nearest-gene) | Opp 0.040 [0.015, 0.063]; Δ 0.026 [−0.006, 0.058]; P(Δ≤0)=0.054. | `Jacky/orientation-controls/scripts/run_orientation_ci.py` — evidence: `intergenic_orientation_delta_ci.csv` | Pattern supported; nearest-gene Δ borderline. |
| Orientation controls (TSS / operon / match) | TSS opp−same Δ **0.051 [0.020, 0.082]**; nearest-gene dies under matching. | `Jacky/orientation-controls/scripts/run_orientation_controls.py` — evidence: `Jacky/orientation-controls/results/intergenic_orientation_controls_delta_ci.csv` | Paper should lead with TSS, not nearest gene. |

---

## Phase 3 — Curated pivot, parity, and the shared-column kingdom wall (≈ 13–25 Oct 2026)

*Pivot (13 Oct 2026): Noshay published / `cut.score` → crisprHAL curated ~33.5k / ALDEx2.*

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Curated Family A ablation **[C]** | Flanking DNA composition is the largest effect: **+0.164 ρ**. | `Runjia/sgrna/curated_ablation.py` — evidence: `ablation_curated.csv` | The one large effect on the cohort that becomes the freeze baseline. |
| Gene-grouped curated ablation | Survives whole-gene holdout; loses only ~6% grouping tax. | `Runjia/sgrna/curated_ablation.py` (`--grouping gene`) — evidence: `ablation_curated_gene.csv`, `grouped_retention.csv` | Ruled out locus memorisation for Family A. |
| Window robustness | Alt windows: +0.1634 vs published +0.1638. | `Runjia/sgrna/window_robustness.py` — evidence: `window_robustness.csv` | Confirmed smooth gradient, not window-size cherry-pick. |
| Curated representation ladder | No reduced set is non-inferior (−0.012 / −0.014); quantum tables beat full k-mers by +0.011. | `Runjia/sgrna/curated_ladder.py` — evidence: `curated_ladder.csv` | “412 ≈ all” does not transfer after the pivot. |
| Hand-named column split | Of 63 hand-named columns, the 46 guide-computable carry +0.0065 vs −0.0007. | `Runjia/sgrna/handnamed_split.py` — evidence: `handnamed_split.csv` | Closed guide-scale annotation distance as a source of gain. |
| No-information / `d_mechanics` split | Deterministic guide functions add +0.011–0.019 performance but no new information; `d_mechanics` flank half is +0.097 of +0.099. | `Runjia/sgrna/no_information.py` — evidence: `no_information.csv`, `d_mechanics_reconstructibility.csv` | Separated re-description from true outside-guide signal. |
| Joint family overlap | Summing the family table overstates ~3.5×. | `Runjia/sgrna/curated_joint.py` — evidence: `curated_joint.csv` | Prevented stacking independent family Δρ as additive biology. |
| Model class span | Eight model classes span only ~0.11 ρ with/without Family A. | `Runjia/sgrna/curated_models.py` — evidence: `curated_models.csv` | Architecture almost irrelevant once representation is fixed. |
| Transcription interactions | Essentiality null; expression +0.0213; family’s interaction rule fails. | `Runjia/sgrna/txn_interactions.py` — evidence: `txn_interactions.csv` | Closed essentiality confound on curated. |
| Selector budget control | 300-column budget and selector are free (±0.0005). | `Runjia/sgrna/rederive.py` (`--only selector_control`) — evidence: `selector_control.csv` | Selection ≠ representation reduction. |
| Curated label ceiling | From crisprHAL replicate counts: **0.946 [0.944, 0.948]**. | `Runjia/sgrna/curated_ceiling.py` — evidence: `curated_ceiling.json` | Model within ~0.22 ρ of the label ceiling. |
| Sealed holdout (adaptivity) | Adaptive overfitting +0.0087 [+0.0020, +0.0153]; Family A +0.165 pool vs +0.156 sealed. | `Runjia/sgrna/sealed_holdout.py` — evidence: `sealed_holdout.csv` | Freeze hygiene: quote sealed Δ or both. |
| Why inflation / label swap | 3.3× inflation is row population not label. | `Runjia/sgrna/why_inflation.py` — evidence: `why_inflation.csv`, `ablation_label_*.csv` | Separated curation-label vs cohort-composition effects. |
| Curation variance (slope) | Steeper flank-GC slope outside Guo’s 1,222-gene panel (β +5.4 → +17.0). | `Runjia/sgrna/curation_variance.py` — evidence: `curation_variance.csv` | Explained cohort gain inflation as a slope ratio. |
| Cohort grouped-CV meaning | Within-gene share of label 0.844 → 0.713 after pivot. | `Runjia/sgrna/cohort_groups.py` — evidence: `cohort_groups.csv` | Grouped CV still required after the pivot. |
| Final eval eSpCas9 parity | On their eSpCas9 split/weights: Δρ +0.0021 [−0.0031, +0.0072]. | `Runjia/sgrna/final_eval.py` — evidence: `final_eval_espcas9.csv` | Parity claim under their protocol. |
| Their SpCas9 split | Parity on SpCas9 split: +0.005. | `Runjia/sgrna/rederive.py` / `data_ablation.py` — evidence: `their_split_slicer.csv` | Second parity arm on the shipped split. |
| Held-out paired compare | On our folds, paired on guides: +0.0115 / +0.0172 / +0.0043. | `Runjia/sgrna/heldout_compare.py` — evidence: `heldout_compare.csv` | Condition-dependent lead (not a universal win). |
| crisprHAL matched HPO search | Search of their own finds nothing better than the published config (~0.699). | **Colab:** `Runjia/colab/crisprhal_tune_matched.py` — evidence: `matched_search_folds.csv`, `crisprhal_matched_folds.csv` | Closed unequal-search objection. |
| Conservative tuned margin | Against their best known config: +0.0161. | `Runjia/sgrna/tune.py` — evidence: `crisprhal_tuned_folds.csv`, `tuning.csv` | Quotable upper-bound margin on our folds. |
| Data ablation (rows vs features) | Label +0.006, which rows +0.008, how many +0.030; feature set still +0.155. | `Runjia/sgrna/data_ablation.py` — evidence: `data_ablation.csv` | Parity is bought with rows; features dominate. |
| crisprHAL wide-window | Equal DNA: theirs +0.023 at 378 nt; ours +0.065 at ±1 kb. | **Colab:** `Runjia/colab/crisprhal_wide_window.py` — evidence: `crisprhal_wide_window.csv` | Lead is access to long-range DNA, not better encoding of the same span. |
| Width re-tune (not run) | Script written to re-tune other HPs at each width; GPU deferred. | **Colab:** `Runjia/colab/crisprhal_tune_by_width.py` — **no results yet** | Pre-registered optional control; not a completed claim. |
| Cui final exam (both models) | On assay neither trained on, theirs transfers better (−0.026). | `Runjia/sgrna/cui_final_exam.py` — evidence: `cui_final_exam.csv` | Cross-assay: deep net better zero-shot on silencing. |
| Kingdom transfer (shared columns) | No useful transfer either way on shared cols (−0.039; reverse ≈0 after human re-tune). | `Runjia/sgrna/kingdom_transfer.py` — evidence: `kingdom_transfer.csv`, `kingdom_transfer_boot.csv` | Kingdom wall on guide-derived representation. |
| Human baseline re-tune | Reproduces at teammate settings: 0.508 vs 0.472 quoted; gap is HPs (+0.10), not columns. | `Runjia/sgrna/human_baseline.py` — evidence: `human_baseline.csv`, `human_baseline_knobs.csv` | Fixed undertuned human arm; one transfer direction became compatible with zero. |
| Human additivity | Human far less additive: ridge/boosting 63.7% vs *E. coli* 95.6%. | `Runjia/sgrna/human_baseline.py` (`--additivity`) — evidence: `human_additivity.csv` | Explains why the *E. coli* champion is the wrong shape for human. |
| Rederivation audit | 12/13 lost producers re-derived; ridge-collapse claim withdrawn; one mappability file unreproducible. | `Runjia/sgrna/rederive.py` — evidence: `rederivation_check.csv`, `results/rederived/` | Evidence hygiene; withdrew unregenerable claims. |

---

## Phase 4 — Human boundary Tier 1 (16 Oct 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Human locate + Family A build | Unique locate 12,222/13,138 → 16,490 usable rows; `a_flank` on hg38. | `Jacky/human-boundary/scripts/run_human_boundary.py` — evidence: `Jacky/human-boundary/results/human_locate_audit.json` | Unblocked the human flank chapter. |
| Human ladder (Tier 1) | Regenerated base 0.382 → +Family A 0.434 (**+0.052**); A-alone 0.341. | Same runner — evidence: `Jacky/human-boundary/results/human_ladder.csv` | Family A is real on human cutting (smaller than curated *E. coli*). |
| Transfer autopsy (“wrong GC”) | Shared-col transfer ≈−0.049; GC² residualise still −0.049. | Same runner — evidence: `Jacky/human-boundary/results/transfer_autopsy.json` | Wrong-GC-rule is a symptom, not the whole failure. |
| Human label sanity | y∈[0,1], mean 0.248; 13,138 unique spacers. | Evidence: `Jacky/human-boundary/results/human_label_sanity.json` | Assay/label hygiene for the human arm. |
| Human GC+GC² feature ablation | base 0.382 → +GC/GC² 0.381 (null). | Evidence: `Jacky/human-boundary/results/human_gc_feature_ablation.csv` (boundary harness) | Kingdom break ≠ “forgot GC² features.” |

---

## Phase 5 — Redescription depth & Cui CRISPRi correction (≈ 26–31 Oct 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Redescription — random tables | Random position-weight tables add −0.0004 to −0.0015. | `Runjia/sgrna/redescription.py` (`--arm random`) — evidence: `redescription_random.csv` | Null: re-description *as a class* is worthless. |
| Redescription — taxonomy | Guide-determined columns +0.008 vs outside-guide +0.201 (~24×). | `Runjia/sgrna/redescription.py` (`--arm taxonomy`) — evidence: `redescription_taxonomy.csv` | Relocated gain from “family folder” to recoverability. |
| Redescription — family split | `eng.dg.guide_selffold` carries `b_energy`’s whole gain (+0.0116 of +0.0181). | `Runjia/sgrna/redescription.py` (`--arm families`) — evidence: `redescription_family_split.csv` | Physics-bearing re-descriptions pay. |
| Redescription — provenance | `d_mechanics` outside half is flank provenance (+0.0968 vs +0.0019). | `Runjia/sgrna/redescription.py` (`--arm provenance`) — evidence: `redescription_provenance.csv` | Confirmed that arm’s “outside” gain is flanking DNA. |
| Redescription — fold shuffle | Real folding +0.0119 vs shuffled folds ≈0. | `Runjia/sgrna/redescription.py` (`--arm folds`) — evidence: `redescription_folds.csv` | Folding gain is real structure. |
| Redescription — nonlinear random | Recoverability-matched random nonlinear functions are null vs real +0.0117. | `Runjia/sgrna/redescription.py` (`--arm nonlinear`) — evidence: `redescription_nonlinear.csv` | Difficulty without phenotype association buys nothing. |
| Base enrichment (curated + published) | Published 63 hand-named barely cut Family A (+0.0823 → +0.0808). | `Runjia/sgrna/base_enrichment.py` — evidence: `base_enrichment*.csv` | Ruled out base-shape as the cohort-tripling cause. |
| XGBoost untouched knobs | Eleven never-tuned knobs worth nothing; best +0.0069. | `Runjia/sgrna/xgb_knobs.py` — evidence: `xgb_knobs.csv` | Closed “untouched hyperparams hide the lead.” |
| XGBoost knobs verify | `max_depth` 6 beats 4 by +0.0063 — capacity, not grow-policy. | `Runjia/sgrna/xgb_knobs.py` (`--verify`) — evidence: `xgb_knobs_verify.csv` | Not adopted into the freeze. |
| Chi-site repair null | Chi sites indistinguishable from GC-matched octamers (41st percentile of 200). | `Runjia/sgrna/chi_sites.py` — evidence: `chi_sites.csv` | Excluded RecBCD repair route. |
| GC strata (curated) | Flank GC +0.176 → +0.221 partial; marginal 3.6× stronger than published. | `Runjia/sgrna/gcstrata.py` (`--cohort curated`) — evidence: `gc_strata_corr_curated.csv` | Strengthened duplex-opening account on curated rows. |
| Cui CRISPRi screen-wide | Family A −0.009 on dCas9 vs +0.157 on cutting. | `Runjia/sgrna/cui_screen.py` — evidence: `cui_screen.csv` | First localisation: binding ≠ cutting. |
| Cui essentiality split | Inside essential genes Family A reads **+0.27** vs −0.01 non-essential. | `Runjia/sgrna/cui_screen.py` (`--essentiality`) — evidence: `cui_essentiality_split.csv` | Shocked the null; forced strand controls. |
| Cui essential + strand | That +0.27 is the strand rule: strand alone ρ 0.66; Family A then +0.007 / +0.015. | `Runjia/sgrna/cui_screen.py` (`--strand`) — evidence: `cui_essential_strand.csv` | Restored cleavage localisation given strand. |
| Cui essential + position | Bare coordinate alone ρ 0.04 — not a location lookup. | `Runjia/sgrna/cui_screen.py` (`--position`) — evidence: `cui_essential_position.csv` | Ruled out genomic-coordinate explanation. |
| Cui essential marginals | Flank GC null; flank purine +0.40; coding-strand labels −5.07 vs −1.19. | `Runjia/sgrna/cui_screen.py` (`--marginals`) — evidence: `cui_essential_marginals.csv`, `cui_strand_summary.csv` | Identified purine as a CRISPRi strand proxy. |

---

## Phase 6 — Human Tier 2–3: chromatin & Family-A transfer (2 Nov 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Human chromatin (Tier 2) | K562 DNase/ATAC ±500 nt: Δρ +0.001 to +0.005. | `Jacky/human-boundary/scripts/run_tier2_tier3.py` — evidence: `Jacky/human-boundary/results/human_chromatin.csv` | Accessibility near-null at this resolution (cell-type caveat). |
| Family-A kingdom transfer (Tier 3) | Flanks flip sign: E→H **+0.022**, H→E **+0.017**; flanks alone +0.042 / +0.108. | Same runner — evidence: `Jacky/human-boundary/results/family_a_kingdom_transfer.csv` | Kingdom wall partly “no flanks”; guide-derived half still fails. |
| GC-matched transfer (Tier 3) | Shared-col stays ≈−0.049 under residualise / GC-range / hist-match. | Same runner — evidence: `Jacky/human-boundary/results/gc_matched_transfer.csv` | Representation, not covariate matching, is the fix. |

---

## Phase 7 — CRISPRi replication, strand depth, cost & faithfulness (≈ 8 Nov 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| CRISPRi multi-screen Family A | Rousset replicates the structure; Wang does not (+0.10 / +0.22 essential under blocks). | `Runjia/sgrna/crispri_screens.py` (`--family-a`) — evidence: `crispri_screen_family_a.csv` | Replication boundary; Wang unexplained. |
| CRISPRi strand replication | Rousset ρ(coding strand, label) −0.633 essential / −0.056 non-essential. | `Runjia/sgrna/crispri_screens.py` (`--strand`) — evidence: `crispri_screen_strand.csv` | Strand rule replicates on an untouched screen. |
| Cross-screen agreement | Same library ~0.90 essential; across labs ~0.77–0.79 essential / ~0.27–0.30 non-essential. | `Runjia/sgrna/crispri_screens.py` (`--agreement`) — evidence: `crispri_screen_agreement.csv` | Second ceiling: transfer bounded by cross-screen agreement. |
| Strand families (all 11) | No family beats strand; Family A +0.015 / +0.007 over base+strand. | `Runjia/sgrna/strand_families.py` — evidence: `strand_families.csv` | Strand dominates CRISPRi prediction. |
| Strand recoverable after proxy drop | After dropping \|ρ\|>0.30 proxies, strand still readable (Family A AUC 0.79). | `Runjia/sgrna/strand_recoverable.py` — evidence: `strand_families_recoverable.csv` | Strand is not only a few named proxy columns. |
| Strand held constant (Cui) | Gains on coding strand: Family A +0.12; template near null / negative. | `Runjia/sgrna/strand_families.py` (`--within`) — evidence: `strand_families_within.csv` | Qualified: residual flank signal among coding-strand guides. |
| Within-gene coding-strand (Cui) | Within-gene Family A Δ +0.102 [0.081, 0.164]. | `Runjia/sgrna/strand_within_gene.py` — evidence: `strand_within_gene_cui_*.csv` | Residual coding-strand flank effect is partly within-gene. |
| Strand strata + within-gene (Rousset) | Coding/template +0.159 / −0.019; within-gene coding Δ +0.114. | `Runjia/sgrna/strand_strata.py`, `strand_within_gene.py` — evidence: `strand_strata_rousset.csv`, `strand_within_gene_rousset_summary.csv` | Replicated the within-strand qualification. |
| Strand flip control | True strand ρ 0.646; flipped −0.528; shuffled 0.065. | `Runjia/sgrna/strand_strata.py` (`--flip`) — evidence: `strand_flip.csv` | Strand polarity is load-bearing for the CRISPRi fit. |
| Recoverability trend | Strongest \|ρ\| flat while Δρ collapses +0.180→+0.008; threshold ~R² 0.2. | `Runjia/sgrna/redescription.py` (`--arm trend`) — evidence: `recoverability_trend.csv` | Bound what a column can add; withdrew a mean-\|ρ\| artefact. |
| Recoverability per-column | Most recoverable/associated column still adds alone (+0.0063). | `Runjia/sgrna/redescription.py` (`--arm percolumn`) — evidence: `recoverability_percolumn.csv` | Recoverability bounds the increment; does not forbid one. |
| Recoverability groups | Power tracks how much DNA a group summarises. | **No committed runner** (scratchpad) — evidence: `recoverability_groups.csv` | Single-position indicators ~0; multi-position summaries carry power. |
| Selector gain vs SHAP audit | Gain over-weights binary indicators; accuracy unchanged. | `Runjia/sgrna/selector_audit.py` — evidence: `selector_audit.csv` | Never trust split-gain for mechanism. |
| Selector MRMR redundancy | Redundancy-penalised selection is worse and more binary. | `Runjia/sgrna/selector_audit.py` (redundancy) — evidence: `selector_redundancy.csv` | Informative columns are the redundant dense ones. |
| Replicate weighting | Inv-var weighting costs −0.0050; permuted −0.0041 — not usable. | `Runjia/sgrna/replicate_weight.py` — evidence: `replicate_weight.csv` | Per-guide reliability not usable as training weight. |
| Replicate weighting (raw label) | On raw log-ratio, weighting still costs −0.004; cost is ESS. | `Runjia/sgrna/replicate_weight.py` (`--raw-label`) — evidence: `replicate_weight_raw.csv` | Not ALDEx2 double-counting. |
| Interp sensitivity-*n* | Attributions faithful to fixed model (+0.93 / +0.97). | `Runjia/sgrna/interp_extra.py` (`--sens`) — evidence: `interp_sensitivity_n.csv` | Rescued faithfulness without refit. |
| Interp interactions | Pairwise 14.7% of output variance; single-column 70.2%. | `Runjia/sgrna/interp_extra.py` (`--inter`) — evidence: `interp_interactions.csv` | Mostly additive; interactions minority. |
| Interp counterfactuals | Flank edits move via composition (GC ±5 → large signed Δ; GC-preserving swaps ~0). | `Runjia/sgrna/interp_extra.py` (`--cf`) — evidence: `interp_counterfactual.csv` | Support for composition as the flank mechanism. |
| Inference cost (Colab / T4) | crisprHAL/SLICER CPU ~177–344×; GPU ~12–110× depending on batch/device. | **Colab:** `Runjia/colab/inference_bench_onecore.py`; `Runjia/sgrna/inference_cost.py` — evidence: `inference_onecore.csv`, `inference_t4.csv` | Cost claim: SLICER far cheaper at inference. |
| Inference cost (laptop one-core) | Per core: 329× / 632× / 817× (1 / 100 / 10k guides). | Same bench locally — evidence: `inference_onecore_local.csv` | Confirmed extreme CPU advantage off-Colab. |

---

## Phase 8 — Human strand audit (16 Nov 2026)

| Experiment | Finding | Code | How it advanced the project |
|---|---|---|---|
| Human strand / purine audit | Gene-strand vs cut ρ **−0.010**; Family A given strand **+0.048** (survives); purine +0.020; within-strand A +0.058 / +0.064. | `Jacky/human-boundary/scripts/run_human_strand_audit.py` — evidence: `Jacky/human-boundary/results/human_strand_*.csv/json` | Kingdom wall ≠ secret strand assay; CRISPRi collapse does not port to human cutting. |

---

## Notes

1. **Nulls that are claims are included** — ruling something out pushed the project.
2. **Fold dumps** (`Runjia/results/folds_*.csv`) are resumable CV logs, not separate experiments.
3. **Withdrawn / superseded claims** are not listed as current findings — see git history and `Runjia/PROGRESS_REPORT.md` Part 5.
4. Narrative context: `Runjia/PROGRESS_REPORT.md`, `Runjia/README.md`, `Jacky/human-boundary/README.md`, `Jacky/orientation-controls/README.md`.
5. Phase 1 bulk CSVs were checked into the shared tree on **25 Oct 2026**; many of those experiments were run earlier on the published matrix (pre-pivot). Phase placement follows scientific order, not only the sync commit date.
