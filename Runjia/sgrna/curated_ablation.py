"""Feature-family ablations on crisprHAL's curated cohort.

Every Δρ in Appendix C was measured on the published 13,880-row matrix against
the published label. The model layer moved to crisprHAL's 33,567 curated guides
and their curated score, and the family measurements did not follow -- so their
*relative* ranking there is unverified. Family A is the one family that has been
re-measured, and it doubled (+0.080 → +0.164), which is reason enough not to
assume the others carry over.

This runs the same ablation design on the curated cohort: base representation
(the 6,169 columns regenerable from the 20-mer) against base + one family, five
seeds by five folds, feature selection fitted inside each training split.

    python -m sgrna.curated_ablation --families b_energy c_folding
    python -m sgrna.curated_ablation --all
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from . import config

OUT = config.RESULTS / "ablation_curated.csv"
FAMILIES = ("a_flank", "b_energy", "c_folding", "d_mechanics", "d_supercoiling",
            "e_nucleoid", "f_methylation", "g_transcription", "h_offtarget",
            "i_shape", "j_periodicity")


def _base():
    """The curated cohort: 6,169 regenerated columns, their label, their order."""
    meta = json.loads((config.INTERIM / "expanded_meta.json").read_text())
    X = np.asarray(np.load(config.INTERIM / "expanded_X.npy", mmap_mode="r"),
                   dtype=np.float32)
    y = np.asarray(meta["y"], dtype=float)
    return X, y, list(meta["feature_names"]), np.asarray(meta["protospacers"])


def _block(fam: str, protos: np.ndarray):
    """One family, aligned to the curated guides. Returns (values, names)."""
    path = config.INTERIM / "features" / f"{fam}_curated.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path.name} not built")
    b = pd.read_csv(path).set_index(config.ID_COL).reindex(protos)
    v = b.to_numpy(dtype=np.float32)
    keep = ~np.all(np.isnan(v), axis=0)          # drop columns empty on this cohort
    if keep.sum() == 0:
        # b_energy built "successfully" with zero feature columns on this cohort,
        # which save_block accepts. An empty block is a failed build, not a null
        # result -- refuse it rather than reporting a delta of exactly zero.
        raise FileNotFoundError(f"{path.name} has no populated feature columns")
    return v[:, keep], [c for c, k in zip(b.columns, keep) if k]


def run(families=FAMILIES, seeds=None, n_splits=None, n_features=300,
        verbose: bool = True):
    from .run_ablation import cross_validate

    seeds = list(seeds or config.SEEDS)
    n_splits = n_splits or config.N_SPLITS
    X, y, names, protos = _base()
    if verbose:
        print(f"  curated cohort: {X.shape[0]:,} guides, {X.shape[1]:,} base columns")

    rows = []
    res = cross_validate(X, y, names, ["base"] * len(names), n_features=n_features,
                         seeds=seeds, n_splits=n_splits, verbose=False,
                         tag="curabl_baseline", experiment="baseline")
    base_rho = res["summary"]["spearman"]["mean"]
    rows.append(dict(family="baseline", n_cols=X.shape[1], spearman=base_rho,
                     spearman_sd=res["summary"]["spearman"]["sd"], d_spearman=0.0))
    if verbose:
        print(f"  {'baseline':>16}: rho {base_rho:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)

    for fam in families:
        try:
            v, fnames = _block(fam, protos)
        except FileNotFoundError as exc:
            if verbose:
                print(f"  {fam:>16}: skipped -- {exc}", flush=True)
            continue
        Xa = np.hstack([X, v])
        res = cross_validate(Xa, y, names + fnames,
                             ["base"] * len(names) + [fam] * len(fnames),
                             n_features=n_features, seeds=seeds, n_splits=n_splits,
                             verbose=False, tag=f"curabl_{fam}", experiment=fam)
        rho = res["summary"]["spearman"]["mean"]
        rows.append(dict(family=fam, n_cols=Xa.shape[1], spearman=rho,
                         spearman_sd=res["summary"]["spearman"]["sd"],
                         d_spearman=rho - base_rho))
        if verbose:
            print(f"  {fam:>16}: rho {rho:.4f}   delta {rho - base_rho:+.4f}  "
                  f"({len(fnames)} cols)", flush=True)
        pd.DataFrame(rows).to_csv(OUT, index=False)

    out = pd.DataFrame(rows)
    if verbose:
        print()
        print(out.round(4).to_string(index=False))
        print(f"written -> {OUT}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--families", nargs="*", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--seeds", type=int, nargs="*", default=None)
    ap.add_argument("--n-features", type=int, default=300)
    a = ap.parse_args(argv)
    fams = tuple(a.families) if a.families else FAMILIES
    run(families=fams, seeds=a.seeds, n_features=a.n_features)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
