#!/usr/bin/env python3
"""Human cutting-screen strand / purine audit — cross-species wall check.

Goal: ask whether Runjia's CRISPRi finding (Family A ≈ coding-strand via flank
purine) also eats the human *cutting* Family A gain. If strand collapses human
Family A, that would reframe the kingdom wall. If Family A survives, the wall
is not "human is secretly a strand assay."

Also reports how strand / purine relate to the label and to transfer residuals,
because the research goal is explaining (or shrinking) cross-species difference.

Requires Tier-1 caches (human_located.csv, X_human_base*.npy, a_flank_human.csv,
meta_human.json) and UCSC refGene.txt.gz under data/reference/.
"""
from __future__ import annotations

import gzip
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

_REPO = Path(__file__).resolve().parents[3]
ROOT = Path(os.environ.get("RSI09_ROOT", str(_REPO / "Runjia"))).resolve()
os.environ["RSI09_ROOT"] = str(ROOT)
sys.path.insert(0, str(ROOT))

from sgrna import config  # noqa: E402
from sgrna.run_ablation import _impute, cross_validate  # noqa: E402

OUT = _REPO / "Jacky" / "human-boundary" / "results"
CACHE = config.INTERIM / "human_boundary"
REFGENE = config.REFERENCE / "refGene.txt.gz"
SEED = 41
N_TOP = 300


def _spearman(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    m = np.isfinite(y) & np.isfinite(p)
    if m.sum() < 3:
        return float("nan")
    r = spearmanr(y[m], p[m]).statistic
    return float(r) if np.isfinite(r) else float("nan")


def _xgb(seed=SEED, **kw):
    import xgboost as xgb
    p = dict(
        n_estimators=400, learning_rate=0.05, max_depth=4, subsample=0.8,
        colsample_bytree=0.8, random_state=seed, n_jobs=-1, tree_method="hist",
        importance_type="gain",
    )
    p.update(kw)
    return xgb.XGBRegressor(**p)


# ---------------------------------------------------------------------------
# Gene / transcription strand from refGene
# ---------------------------------------------------------------------------


def load_refgene(path: Path) -> pd.DataFrame:
    """UCSC refGene: chrom, strand, txStart, txEnd, name2 (0-based half-open)."""
    cols = [
        "bin", "name", "chrom", "strand", "txStart", "txEnd", "cdsStart", "cdsEnd",
        "exonCount", "exonStarts", "exonEnds", "score", "name2", "cdsStartStat",
        "cdsEndStat", "exonFrames",
    ]
    rows = []
    with gzip.open(path, "rt") as fh:
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 13:
                continue
            chrom, strand = parts[2], parts[3]
            if "_" in chrom:  # skip alts / random
                continue
            rows.append(dict(
                chrom=chrom, strand=strand,
                start=int(parts[4]), end=int(parts[5]),
                gene=parts[12],
            ))
    g = pd.DataFrame(rows)
    # collapse isoforms to gene intervals (union is overkill; keep longest tx)
    g["len"] = g["end"] - g["start"]
    g = g.sort_values("len", ascending=False).drop_duplicates(["chrom", "gene", "strand"])
    return g.reset_index(drop=True)


def assign_gene_strand(loc: pd.DataFrame, genes: pd.DataFrame) -> pd.DataFrame:
    """Nearest overlapping gene by midpoint; coding_strand = guide strand == gene strand."""
    by_chrom = {c: sub.reset_index(drop=True) for c, sub in genes.groupby("chrom")}
    out_gene, out_gstrand, out_same, out_dist = [], [], [], []
    for _, r in loc.iterrows():
        chrom = str(r["chrom"])
        mid = (int(r["left"]) + int(r["right"])) // 2  # 1-based coords from locate
        # refGene is 0-based; convert mid to 0-based for overlap
        mid0 = mid - 1
        gstrand = r["strand"]
        sub = by_chrom.get(chrom)
        if sub is None or len(sub) == 0:
            out_gene.append(None)
            out_gstrand.append(None)
            out_same.append(np.nan)
            out_dist.append(np.nan)
            continue
        # overlapping transcripts
        hits = sub[(sub["start"] <= mid0) & (sub["end"] > mid0)]
        if len(hits):
            # prefer protein-coding-looking names without MIR/RNA heuristics: longest
            hit = hits.iloc[0]
            dist = 0
        else:
            # nearest by midpoint distance
            centers = (sub["start"] + sub["end"]) / 2.0
            j = int(np.argmin(np.abs(centers - mid0)))
            hit = sub.iloc[j]
            dist = float(min(abs(mid0 - hit["start"]), abs(mid0 - hit["end"])))
            if mid0 >= hit["start"] and mid0 < hit["end"]:
                dist = 0.0
        out_gene.append(hit["gene"])
        out_gstrand.append(hit["strand"])
        out_same.append(1.0 if gstrand == hit["strand"] else 0.0)
        out_dist.append(dist)
    loc = loc.copy()
    loc["gene_name"] = out_gene
    loc["gene_strand"] = out_gstrand
    loc["coding_strand"] = out_same  # 1 = same strand as gene (= sense / coding-like)
    loc["gene_dist"] = out_dist
    loc["genic"] = (loc["gene_dist"] == 0).astype(float)
    return loc


# ---------------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------------


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not REFGENE.exists():
        raise SystemExit(f"missing {REFGENE}")
    for p in ("human_located.csv", "X_human_base.npy", "X_human_base_a.npy",
              "meta_human.json", "a_flank_human.csv"):
        if not (CACHE / p).exists():
            raise SystemExit(f"missing cache {CACHE / p} — run run_human_boundary.py first")

    print("=== load located guides + Family A ===", flush=True)
    loc = pd.read_csv(CACHE / "human_located.csv")
    meta = json.loads((CACHE / "meta_human.json").read_text())
    Xb = np.load(CACHE / "X_human_base.npy")
    Xf = np.load(CACHE / "X_human_base_a.npy")
    y = np.asarray(meta["y"], float)
    names = list(meta["full_names"])
    fam = list(meta["family_of"])
    assert len(loc) == len(y) == Xb.shape[0]

    flank = pd.read_csv(CACHE / "a_flank_human.csv", low_memory=False)
    flank["sgRNAID"] = flank["sgRNAID"].astype(str)
    loc["sgRNAID"] = loc["sgRNAID"].astype(str)
    flank = flank.drop_duplicates("sgRNAID").set_index("sgRNAID").reindex(loc["sgRNAID"])
    pur_cols = [c for c in flank.columns if "purine" in c]
    gc_cols = [c for c in flank.columns if ".gc" in c]
    print(f"  purine cols: {pur_cols[:8]} ... ({len(pur_cols)})", flush=True)
    print(f"  gc cols: {gc_cols[:8]} ... ({len(gc_cols)})", flush=True)
    print(f"  flank rows aligned: {flank['eng.flank.comp.up1000.purine'].notna().sum() if 'eng.flank.comp.up1000.purine' in flank.columns else 0}/{len(loc)}", flush=True)

    up_pur = flank["eng.flank.comp.up1000.purine"].to_numpy(float) if "eng.flank.comp.up1000.purine" in flank.columns else np.full(len(loc), np.nan)
    dn_pur = flank["eng.flank.comp.dn1000.purine"].to_numpy(float) if "eng.flank.comp.dn1000.purine" in flank.columns else np.full(len(loc), np.nan)
    up_gc = flank["eng.flank.comp.up1000.gc"].to_numpy(float) if "eng.flank.comp.up1000.gc" in flank.columns else np.full(len(loc), np.nan)
    print("=== assign gene / transcription strand (refGene) ===", flush=True)
    genes = load_refgene(REFGENE)
    print(f"  refGene genes: {len(genes):,}", flush=True)
    loc = assign_gene_strand(loc, genes)
    coding = loc["coding_strand"].to_numpy(float)
    genic = loc["genic"].to_numpy(float)

    # --- marginal associations ---
    rows = []
    for label, arr in (
        ("coding_strand", coding),
        ("genic", genic),
        ("up1000_purine", up_pur),
        ("dn1000_purine", dn_pur),
        ("up1000_gc", up_gc),
        ("guide_strand_plus", (loc["strand"] == "+").astype(float).to_numpy()),
    ):
        rows.append(dict(
            feature=label,
            n=int(np.isfinite(arr).sum()),
            spearman_vs_y=_spearman(y, arr),
            mean=float(np.nanmean(arr)),
        ))
    # purine vs coding strand (is purine a strand proxy on human too?)
    rows.append(dict(
        feature="up1000_purine_vs_coding_strand",
        n=int(np.isfinite(up_pur).sum() & np.isfinite(coding).sum()),
        spearman_vs_y=_spearman(coding, up_pur),
        mean=float("nan"),
    ))
    marg = pd.DataFrame(rows)
    marg.to_csv(OUT / "human_strand_marginals.csv", index=False)
    print(marg.to_string(index=False), flush=True)

    # --- Family A with strand supplied / held constant ---
    print("=== Family A vs strand controls ===", flush=True)
    ok = np.isfinite(y) & np.isfinite(coding)
    # strand as a single column
    strand_col = coding[ok].reshape(-1, 1).astype(np.float32)
    Xb_ok, Xf_ok, y_ok = Xb[ok], Xf[ok], y[ok]
    base_i = np.where(np.asarray(fam) == "base")[0]
    a_i = np.where(np.asarray(fam) == "a_flank")[0]

    arms = []

    def cv_arm(X, y_arm, feature_names, family_of, tag):
        res = cross_validate(
            X, y_arm, list(feature_names), np.asarray(family_of),
            seeds=(SEED,), tag=tag, experiment=tag, verbose=True,
        )
        return res["summary"]["spearman"]["mean"]

    # base
    rho_base = cv_arm(Xb_ok, y_ok, [names[i] for i in base_i], ["base"] * len(base_i), "hstrand_base")
    arms.append(dict(arm="base", n=int(ok.sum()), spearman=rho_base, delta_vs_base=0.0))

    # base + Family A
    rho_ba = cv_arm(Xf_ok, y_ok, names, fam, "hstrand_base_a")
    arms.append(dict(arm="base+a_flank", n=int(ok.sum()), spearman=rho_ba, delta_vs_base=rho_ba - rho_base))

    # base + strand
    X_bs = np.hstack([Xb_ok, strand_col])
    rho_bs = cv_arm(
        X_bs, y_ok, [names[i] for i in base_i] + ["coding_strand"],
        ["base"] * len(base_i) + ["strand"], "hstrand_base_strand",
    )
    arms.append(dict(arm="base+strand", n=int(ok.sum()), spearman=rho_bs, delta_vs_base=rho_bs - rho_base))

    # base + strand + Family A  ← key: does A survive?
    X_bsa = np.hstack([Xf_ok, strand_col])
    rho_bsa = cv_arm(
        X_bsa, y_ok, names + ["coding_strand"],
        list(fam) + ["strand"], "hstrand_base_strand_a",
    )
    arms.append(dict(
        arm="base+strand+a_flank", n=int(ok.sum()), spearman=rho_bsa,
        delta_vs_base=rho_bsa - rho_base,
        delta_vs_base_strand=rho_bsa - rho_bs,
    ))

    # base + up1000 purine (the bacterial proxy column)
    pur_ok = up_pur[ok]
    finite_pur = np.isfinite(pur_ok)
    if finite_pur.mean() > 0.5:
        X_bp = np.hstack([Xb_ok[finite_pur], pur_ok[finite_pur].reshape(-1, 1).astype(np.float32)])
        rho_bp = cv_arm(
            X_bp, y_ok[finite_pur], [names[i] for i in base_i] + ["up1000_purine"],
            ["base"] * len(base_i) + ["proxy"], "hstrand_base_purine",
        )
        arms.append(dict(
            arm="base+up1000_purine", n=int(finite_pur.sum()),
            spearman=rho_bp, delta_vs_base=rho_bp - rho_base,
        ))
    else:
        print(f"  skip purine arm: only {finite_pur.sum()}/{ok.sum()} finite", flush=True)

    # within coding / template strata (strand held constant)
    for strand_val, label in ((1.0, "coding"), (0.0, "template")):
        m = ok & (coding == strand_val)
        if m.sum() < 500:
            continue
        Xb_s, Xf_s, y_s = Xb[m], Xf[m], y[m]
        rb = cv_arm(Xb_s, y_s, [names[i] for i in base_i], ["base"] * len(base_i), f"hstrand_{label}_base")
        ra = cv_arm(Xf_s, y_s, names, fam, f"hstrand_{label}_base_a")
        arms.append(dict(
            arm=f"within_{label}:base", n=int(m.sum()), spearman=rb, delta_vs_base=0.0,
        ))
        arms.append(dict(
            arm=f"within_{label}:base+a_flank", n=int(m.sum()), spearman=ra,
            delta_vs_base=ra - rb,
        ))

    # genic only (almost all guides — keep as sanity check)
    m = ok & (genic == 1.0)
    if m.sum() >= 500:
        y_g = y[m]
        rb = cv_arm(Xb[m], y_g, [names[i] for i in base_i], ["base"] * len(base_i), "hstrand_genic_base")
        ra = cv_arm(Xf[m], y_g, names, fam, "hstrand_genic_base_a")
        rs = cv_arm(
            np.hstack([Xb[m], coding[m].reshape(-1, 1).astype(np.float32)]),
            y_g, [names[i] for i in base_i] + ["coding_strand"],
            ["base"] * len(base_i) + ["strand"], "hstrand_genic_base_strand",
        )
        rsa = cv_arm(
            np.hstack([Xf[m], coding[m].reshape(-1, 1).astype(np.float32)]),
            y_g, names + ["coding_strand"], list(fam) + ["strand"],
            "hstrand_genic_base_strand_a",
        )
        arms.append(dict(arm="genic:base", n=int(m.sum()), spearman=rb, delta_vs_base=0.0))
        arms.append(dict(arm="genic:base+a_flank", n=int(m.sum()), spearman=ra, delta_vs_base=ra - rb))
        arms.append(dict(arm="genic:base+strand", n=int(m.sum()), spearman=rs, delta_vs_base=rs - rb))
        arms.append(dict(
            arm="genic:base+strand+a_flank", n=int(m.sum()), spearman=rsa,
            delta_vs_base=rsa - rb, delta_vs_base_strand=rsa - rs,
        ))

    arms_df = pd.DataFrame(arms)
    arms_df.to_csv(OUT / "human_strand_family_a.csv", index=False)
    print(arms_df.to_string(index=False), flush=True)

    # --- summary JSON for the cross-species story ---
    # Family A gain with vs without strand
    a_gain = float(rho_ba - rho_base)
    a_gain_given_strand = float(rho_bsa - rho_bs)
    summary = dict(
        n_located=int(len(loc)),
        n_with_strand=int(ok.sum()),
        frac_genic=float(np.nanmean(genic)),
        frac_coding_strand=float(np.nanmean(coding[ok])),
        spearman_coding_strand_vs_y=_spearman(y[ok], coding[ok]),
        spearman_up1000_purine_vs_y=_spearman(y, up_pur),
        spearman_up1000_purine_vs_coding=_spearman(coding, up_pur),
        spearman_up1000_gc_vs_y=_spearman(y, up_gc),
        family_a_delta_over_base=a_gain,
        family_a_delta_given_strand=a_gain_given_strand,
        family_a_survives_strand=bool(a_gain_given_strand > 0.5 * a_gain) if np.isfinite(a_gain) else None,
        interpretation=(
            "If family_a_delta_given_strand ≈ family_a_delta_over_base, human cutting "
            "Family A is NOT a CRISPRi-style strand proxy — kingdom wall is not strand. "
            "If it collapses toward 0, reframe: human flanks were partly orientation."
        ),
        cross_species_note=(
            "Bacterial CRISPRi: strand alone ρ≈0.66, Family A given strand ≈+0.01 pooled. "
            "Human cutting numbers above are the analogue test on the wrong assay by design — "
            "expected survival of Family A if cutting ≠ silencing."
        ),
    )
    (OUT / "human_strand_audit.json").write_text(json.dumps(summary, indent=2))
    # save annotated loc slim
    loc[["sgRNAID", "chrom", "strand", "left", "right", "y", "gene_name",
         "gene_strand", "coding_strand", "gene_dist", "genic"]].to_csv(
        CACHE / "human_strand_annotated.csv", index=False
    )
    print(json.dumps(summary, indent=2), flush=True)
    print("DONE human strand audit", flush=True)


if __name__ == "__main__":
    main()
