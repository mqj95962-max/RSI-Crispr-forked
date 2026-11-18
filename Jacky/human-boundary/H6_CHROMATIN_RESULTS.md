# H6 — matched cell-line chromatin (first pass)

**Date:** 19 November 2026 (Asia/Singapore)  
**Runner:** `scripts/run_h6_chromatin.py`  
**Tracks:** `Runjia/data/reference/chromatin/h6/` (downloaded; not git-versioned)

## Setup

Noshay’s human matrix mixes Doench A375 with a curated multi-line pool
(HCT116, HEK293T, HeLa, HL60). There are **no per-guide cell-line labels**, so
each ENCODE track is tested as a locus feature on the whole located set
(16,490 guides), ±500 nt around the protospacer midpoint.

| Track | ENCODE file | Cell |
|---|---|---|
| HCT116 ATAC | ENCFF153PRF | HCT116 |
| HCT116 DNase | ENCFF251RIU | HCT116 |
| HCT116 H3K27ac | ENCFF585BWA | HCT116 |
| HEK293T DNase | ENCFF148BGE | HEK293T |
| HeLa-S3 DNase | ENCFF830FDL | HeLa-S3 |
| HeLa-S3 H3K27ac | ENCFF010QGR | HeLa-S3 |
| HL-60 DNase | ENCFF634ZUJ | HL-60 |

A375 released GRCh38 DNase/ATAC signal was not found in ENCODE for this sweep.

## Results (seed 41)

Baselines: base **0.382**, base+Family A **0.434**.

| Track | Δρ on base | Δρ on base+A |
|---|---:|---:|
| Best single (HeLa H3K27ac / DNase) | ~**+0.011 to +0.012** | ~0 to +0.002 |
| HCT116 H3K27ac | +0.010 | +0.003 |
| Panel DNase mean | +0.008 | +0.007 |
| Most other tracks | +0.00 to +0.01 | ~0 |

## Meaning

Matched-line chromatin is a bit less null than K562 was, but still **tiny**
versus Family A (+0.05) or capacity (+0.09). Given Family A, chromatin adds
almost nothing. Chromatin is unlikely to be the missing cross-kingdom
representation on this matrix at ±500 nt — unless we get per-guide cell-line
labels or A375-matched tracks for the Doench subset.
