"""Is the curated table inflated because the base has no dense summaries?

Every family's Δρ roughly tripled when the cohort moved, with the ordering
almost unchanged (rank ρ 0.97, Appendix B3). Two of the four candidate causes
are already eliminated: the **label** moves family A by 0.004 at fixed rows
(`ablation_label_*.csv`), and the **row count** by nothing at all --
13,880 curated rows give +0.170 against 33,567 rows' +0.164
(`why_inflation.py`). What remains is the row population and the base
representation.

The base is testable directly. The published base carried 63 hand-named columns
including guide Tm and GC; the curated base is 6,169 sparse indicators and
carries none. If that absence is what inflates every family, then giving the
base dense continuous guide-derived summaries should shrink the next family's
gain.

The summaries used are the ones already built and known to carry **no
information** beyond the 20-mer (Finding 2): `b_energy`'s 10 columns,
`c_folding`'s 9, and `d_mechanics`'s 22 protospacer columns -- 41 dense
continuous columns, none of which reads a base outside the guide. That matters
for the logic: if family A's gain shrinks against this base, it shrank because
the base gained *summary shape*, not because it gained *information*.

    base                 0.5445      (cached from the curated ablation)
    base + a_flank       0.7084      Δ +0.164
    base + summaries                 Δ ?
    base + summaries + a_flank       Δ(a_flank | summaries) = ?

    python -m sgrna.base_enrichment
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import config
from .curated_ablation import _base, _block

OUT = config.RESULTS / "base_enrichment.csv"
SUMMARIES = ("b_energy", "c_folding", "d_mechanics")
FLANK = ".flank."


def _summary_block(protos):
    """The 41 dense guide-only summary columns, `d_mechanics`'s flanks removed."""
    vals, names = [], []
    for fam in SUMMARIES:
        v, fn = _block(fam, protos)
        keep = np.array([FLANK not in f for f in fn])
        vals.append(v[:, keep])
        names += [f for f, k in zip(fn, keep) if k]
    return np.hstack(vals), names


def run(seeds=None, n_splits=None, n_features=300, verbose: bool = True):
    from .run_ablation import cross_validate

    seeds = list(seeds or config.SEEDS)
    n_splits = n_splits or config.N_SPLITS
    X, y, names, protos = _base()
    S, snames = _summary_block(protos)
    A, anames = _block("a_flank", protos)
    if verbose:
        print(f"  summaries: {S.shape[1]} dense guide-only columns; "
              f"a_flank: {A.shape[1]}")

    arms = {
        "base": (X, names, ["base"] * len(names), "curabl_baseline", "baseline"),
        "base+a_flank": (np.hstack([X, A]), names + anames,
                         ["base"] * len(names) + ["a_flank"] * len(anames),
                         "curabl_a_flank", "a_flank"),
        "base+summaries": (np.hstack([X, S]), names + snames,
                           ["base"] * len(names) + ["sum"] * len(snames),
                           "enrich_summaries", "summaries"),
        "base+summaries+a_flank": (np.hstack([X, S, A]), names + snames + anames,
                                   ["base"] * len(names) + ["sum"] * len(snames)
                                   + ["a_flank"] * len(anames),
                                   "enrich_sum_flank", "summaries+a_flank"),
    }

    rows = []
    for arm, (Xa, nm, fam, tag, exp) in arms.items():
        res = cross_validate(Xa, y, nm, fam, n_features=n_features, seeds=seeds,
                             n_splits=n_splits, verbose=False, tag=tag,
                             experiment=exp)
        rows.append(dict(arm=arm, n_cols=Xa.shape[1],
                         spearman=res["summary"]["spearman"]["mean"],
                         spearman_sd=res["summary"]["spearman"]["sd"]))
        if verbose:
            print(f"  {arm:>24}: rho {rows[-1]['spearman']:.4f}", flush=True)
        pd.DataFrame(rows).to_csv(OUT, index=False)

    out = pd.DataFrame(rows).set_index("arm")
    d_plain = out.loc["base+a_flank", "spearman"] - out.loc["base", "spearman"]
    d_enriched = (out.loc["base+summaries+a_flank", "spearman"]
                  - out.loc["base+summaries", "spearman"])
    if verbose:
        print(f"\n  a_flank over the plain base    : {d_plain:+.4f}")
        print(f"  a_flank over the enriched base : {d_enriched:+.4f}")
        print(f"  shrinkage attributable to base shape: "
              f"{d_plain - d_enriched:+.4f}")
        print(f"written -> {OUT}")
    return out


if __name__ == "__main__":
    run()
