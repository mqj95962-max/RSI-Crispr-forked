"""The last untouched test: does the flanking-context effect appear in a CRISPRi screen?

Every external check so far has been another Cas9 **cutting** screen, and all of
them are now used for something. Cui et al. (2018) is a dCas9 **CRISPRi** screen
in the same organism -- 85,392 guides, two measurement arms -- and this project
has taken exactly one number from it (the two arms agree at ρ 0.711, quoted once
as a ceiling range). Nothing else: no model, no feature, no hyperparameter, no
split has ever been chosen or evaluated against it.

**It can falsify the mechanism, which is why it is worth spending.** Finding 3's
account is a duplex-opening step limited by local DNA composition at the *cut
site*. dCas9 binds and does not cut, and the measured quantity is fitness under
transcriptional silencing rather than survival after cleavage. So:

    family A still predicts  ->  the effect is about binding or accessibility,
                                 not about cutting, and Finding 3's mechanism
                                 sentence is wrong as written
    family A does not        ->  the effect is specific to cleavage, which is
                                 what Finding 3 claims

Either outcome is a result. Neither is available from another cutting screen.

**Gene-grouped CV is not optional here, it is the whole experiment.** CRISPRi
fitness is dominated by whether the silenced gene is essential, so almost all of
the label's variance is *between* genes. Family A's columns are read from a 2 kb
window and identify the locus, so under random KFold a model can score by
recognising which gene it is looking at and be rewarded for it. That route
would produce a large, entirely spurious family A gain. Both arms are therefore
run under whole-gene holdout, with the random-KFold version reported beside it
to show the size of the trap.

    python -m sgrna.cui_screen --build
    python -m sgrna.cui_screen --run
"""

from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd

from . import config, genome

CACHE = config.INTERIM / "cui_crispri"
OUT = config.RESULTS / "cui_screen.csv"
FLANK = 1000


def load_screen(verbose: bool = True) -> pd.DataFrame:
    """One row per uniquely-targeting guide, labelled by the mean of both arms."""
    d = pd.read_csv(config.BADSEED / "screen_data.csv")
    n0 = len(d)
    d = d[d["ntargets"] == 1]                      # multi-target guides are a
    d = d[d["guide"].str.fullmatch(r"[ACGT]{20}")] # different measurement
    # The two arms (18 and 75 generations) agree at rho 0.711, so their mean is
    # the more reliable label: Spearman-Brown gives 2r/(1+r) = 0.83 against 0.71
    # for either arm alone.
    d = d.groupby("guide", as_index=False).agg(
        fit18=("fit18", "mean"), fit75=("fit75", "mean"),
        gene=("gene", "first"), essential=("essential", "first"),
        pos=("pos", "first"), ori=("ori", "first"))
    d["y"] = d[["fit18", "fit75"]].mean(axis=1)
    if verbose:
        print(f"  {n0:,} rows -> {len(d):,} unique single-target guides")
    return d


def build(force: bool = False, verbose: bool = True):
    """Locate every guide in NC_000913.2, cut its flanks, featurise."""
    CACHE.mkdir(parents=True, exist_ok=True)
    x_path, meta_path = CACHE / "X.npy", CACHE / "meta.json"
    if x_path.exists() and meta_path.exists() and not force:
        return (np.load(x_path, mmap_mode="r"),
                json.loads(meta_path.read_text()))

    from . import featurise
    from .features import a_flank

    d = load_screen(verbose=verbose)
    g = genome.load_genome()
    seqs, lefts, strands = genome.protospacer_sites()
    # Guides with more than one NGG site in the genome are dropped: their flanks
    # are ambiguous, and Cui's own ntargets column counts targets rather than
    # genomic copies.
    counts = pd.Series(seqs).value_counts()
    site = {s: (l, t) for s, l, t in zip(seqs, lefts, strands)}
    d["n_sites"] = d["guide"].map(counts).fillna(0).astype(int)
    found = d[d["n_sites"] == 1].reset_index(drop=True)
    if verbose:
        print(f"  {len(found):,} located uniquely in NC_000913.2 "
              f"({(d['n_sites'] == 0).sum():,} not found, "
              f"{(d['n_sites'] > 1).sum():,} multi-copy)")

    # Their coordinates are a free consistency check on the assembly -- but the
    # conventions differ, so a naive |ours - theirs| <= 1 test reports 0% and
    # looks like an assembly mismatch. The offset takes exactly two values,
    # +3 and -21, one per strand: they report the PAM-proximal end rather than
    # the protospacer's left edge. Checking that, every guide agrees exactly,
    # which confirms NC_000913.2 and our placement.
    ours = np.array([site[s][0] for s in found["guide"]])
    strand = np.array([site[s][1] for s in found["guide"]])
    off = ours - found["pos"].to_numpy()
    exact = float(np.mean(np.where(strand == 1, off == 3, off == -21)))
    if verbose:
        print(f"  their `pos` matches ours exactly for {exact:.1%} of guides "
              f"(offset +3 on the plus strand, -21 on the minus: they report "
              f"the PAM-proximal end)")
        if exact < 0.99:
            print(f"  ! offsets seen: "
                  f"{pd.Series(off).value_counts().head(5).to_dict()}")

    rows = []
    for s in found["guide"]:
        left, strand = site[s]
        ctx = genome.guide_context(int(left), int(left) + 19,
                                   "+" if strand == 1 else "-", FLANK, g)
        rows.append((ctx["upstream"], ctx["pam"], ctx["downstream"],
                     "+" if strand == 1 else "-", int(left)))
    found[["upstream", "pam", "downstream", "strand", "left"]] = pd.DataFrame(
        rows, index=found.index)
    found["protospacer"] = found["guide"]
    found[config.ID_COL] = found["guide"]
    found["located"] = True
    found["right"] = found["left"] + 19

    base, base_names = featurise.matrix(found["protospacer"].tolist(),
                                        verbose=verbose)
    block = a_flank.build(found)
    block = block.set_index(config.ID_COL).reindex(found["protospacer"])
    vals = block.to_numpy(dtype=np.float32)
    keep = ~np.all(np.isnan(vals), axis=0)
    X = np.hstack([np.asarray(base, dtype=np.float32), vals[:, keep]])
    names = list(base_names) + [c for c, k in zip(block.columns, keep) if k]

    np.save(x_path, X)
    meta_path.write_text(json.dumps(dict(
        y=found["y"].tolist(), fit18=found["fit18"].tolist(),
        fit75=found["fit75"].tolist(), names=names, n_base=len(base_names),
        # pandas 3 keeps missing values through `astype(str)` rather than
        # writing "nan", so they are filled explicitly -- otherwise the gene
        # column comes back as a mix of str and float and every grouped run
        # dies sorting it.
        gene=found["gene"].fillna("").astype(str).tolist(),
        essential=found["essential"].fillna("").astype(str).tolist(),
        left=found["left"].tolist(), protospacers=found["protospacer"].tolist())))
    if verbose:
        print(f"  built {X.shape[0]:,} x {X.shape[1]:,} "
              f"({len(base_names):,} base + {X.shape[1] - len(base_names)} family A)")
    return np.load(x_path, mmap_mode="r"), json.loads(meta_path.read_text())


def run(seeds=(41, 42, 43), n_splits=None, verbose: bool = True):
    from .run_ablation import cross_validate

    n_splits = n_splits or config.N_SPLITS
    X, meta = build(verbose=verbose)
    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(meta["y"], dtype=float)
    names = list(meta["names"])
    n_base = int(meta["n_base"])
    gene = np.asarray([g if isinstance(g, str) else "" for g in meta["gene"]],
                      dtype=object)

    # Intergenic guides have no gene to hold out, so they are dropped from the
    # grouped arms rather than each forming its own group.
    has_gene = (gene != "") & (gene != "nan") & (gene != "None")
    if verbose:
        print(f"  {has_gene.sum():,} guides inside a named gene "
              f"({len(np.unique(gene[has_gene])):,} genes), "
              f"{(~has_gene).sum():,} intergenic")

    rows = []
    for scheme in ("gene", "random"):
        if scheme == "gene":
            Xs, ys, groups = X[has_gene], y[has_gene], gene[has_gene]
        else:
            Xs, ys, groups = X[has_gene], y[has_gene], None
        for arm, cols in (("base", slice(0, n_base)),
                          ("base+a_flank", slice(0, X.shape[1]))):
            Xa = Xs[:, cols]
            nm = names[cols]
            res = cross_validate(Xa, ys, nm, ["arm"] * len(nm),
                                 n_features=config.N_FEATURES, seeds=list(seeds),
                                 n_splits=n_splits, verbose=False, groups=groups,
                                 tag=f"cui_{scheme}_{arm.replace('+', '_')}",
                                 experiment=arm)
            rows.append(dict(cv=scheme, arm=arm, n_rows=int(len(ys)),
                             n_cols=Xa.shape[1],
                             spearman=res["summary"]["spearman"]["mean"],
                             spearman_sd=res["summary"]["spearman"]["sd"]))
            if verbose:
                print(f"  {scheme:>6} / {arm:>12}: rho "
                      f"{rows[-1]['spearman']:.4f} ± {rows[-1]['spearman_sd']:.4f}",
                      flush=True)
            pd.DataFrame(rows).to_csv(OUT, index=False)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    if verbose:
        for scheme in ("gene", "random"):
            a = out[(out.cv == scheme)].set_index("arm")["spearman"]
            print(f"\n  family A under {scheme:>6} CV: "
                  f"{a['base+a_flank'] - a['base']:+.4f}")
        print(f"written -> {OUT}")
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    if a.build or not a.run:
        build(force=a.force)
    if a.run:
        run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
