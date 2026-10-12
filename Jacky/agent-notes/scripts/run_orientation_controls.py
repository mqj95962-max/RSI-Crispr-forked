#!/usr/bin/env python3
"""Orientation controls beyond nearest-gene (Part 4 item 3).

Extends the frozen intergenic asymmetry protocol with:
  1. Promoter vs RBS separated (gene-orientation Δ inside each kind)
  2. Curated RegulonDB TSS orientation (sequence-anchored onto NC_000913.2)
  3. Curated RegulonDB operon orientation
  4. Cohort balance + 1:1 matching on distance-to-gene/TSS and flank GC
  5. Block-bootstrap CI on each orientation interaction

Primary set: Data S6 Quality=Good. Feature recipe unchanged (6169 base + a_flank).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(os.environ.get("RSI09_ROOT", "/workspace/Runjia")).resolve()
os.environ["RSI09_ROOT"] = str(ROOT)
(ROOT / "external_data").mkdir(parents=True, exist_ok=True)
(ROOT / "data" / "raw").mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))

from sgrna import config, genome  # noqa: E402
from sgrna.asymmetry import _side_of  # noqa: E402
from sgrna.features.g_transcription import anchored_promoters  # noqa: E402
from sgrna.run_ablation import cross_validate  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_intergenic_orientation import (  # noqa: E402
    OUT, CACHE, FLANK_NT, bin100k_groups, build_matrix,
    load_intergenic_catalog, load_sets, locate_and_orient, summarise,
)
from run_orientation_ci import (  # noqa: E402
    N_BOOT, SEED, ALPHA, MIN_N, _rho, arm_columns, bootstrap_delta, oof_for_arm,
)

GENOME_LEN = 4_639_675
ARMS_KEEP = ("baseline", "upstream_only", "downstream_matched")
TAG = "s6_good"


def circular_dist(a: np.ndarray, b: np.ndarray, n: int = GENOME_LEN) -> np.ndarray:
    d = np.abs(a - b) % n
    return np.minimum(d, n - d)


def load_operons() -> pd.DataFrame:
    path = config.REGULONDB / "OperonSet.tsv"
    op = pd.read_csv(path, sep="\t", comment="#", header=None)
    # RegulonDB: name, left, right, strand(forward/reverse), n_genes, genes, ...
    op = op.iloc[:, :6].copy()
    op.columns = ["name", "left", "right", "strand_raw", "n_genes", "genes"]
    op["left"] = pd.to_numeric(op["left"], errors="coerce")
    op["right"] = pd.to_numeric(op["right"], errors="coerce")
    op = op.dropna(subset=["left", "right", "strand_raw"])
    op["strand"] = op["strand_raw"].map(
        {"forward": "+", "reverse": "-", "+": "+", "-": "-"}
    )
    op = op.dropna(subset=["strand"]).reset_index(drop=True)
    return op


def annotate_tss_operon(idx: pd.DataFrame) -> pd.DataFrame:
    """Add nearest RegulonDB TSS / operon orientation and distances."""
    out = idx.copy()
    mid = ((out["left"] + out["right"]) / 2).to_numpy(float)
    gseq = genome.load_genome()
    # flank GC over ±500 nt of the guide-oriented context already in idx
    def flank_gc(row):
        up = str(row.get("upstream", ""))[-500:]
        dn = str(row.get("downstream", ""))[:500]
        seg = up + dn
        if not seg:
            return np.nan
        return (seg.count("G") + seg.count("C")) / len(seg)

    out["flank_gc500"] = [flank_gc(r) for _, r in out.iterrows()]

    # --- TSS ---
    tss = anchored_promoters()
    tss_pos = tss["tss"].to_numpy(float)
    tss_strand = tss["strand"].astype(str).to_numpy()
    # vector nearest for each guide mid
    # For ~9k x ~4k this is fine as a broadcast in chunks
    nearest_i = np.empty(len(mid), dtype=int)
    nearest_d = np.empty(len(mid), dtype=float)
    chunk = 500
    for start in range(0, len(mid), chunk):
        m = mid[start:start + chunk][:, None]
        d = circular_dist(m, tss_pos[None, :])
        j = np.argmin(d, axis=1)
        nearest_i[start:start + chunk] = j
        nearest_d[start:start + chunk] = d[np.arange(len(j)), j]
    out["near_tss"] = tss["promoter"].to_numpy()[nearest_i]
    out["tss_pos"] = tss_pos[nearest_i]
    out["tss_strand"] = tss_strand[nearest_i]
    out["tss_dist"] = nearest_d
    out["relative_tss"] = np.where(
        out["strand"].astype(str).to_numpy() == out["tss_strand"].to_numpy(),
        "same_as_tss", "opposite_tss",
    )

    # --- Operon ---
    op = load_operons()
    # Operon coords are on U00096.3; for coarse orientation we still use them
    # as a curated strand label. Distance uses the same coordinate numbers;
    # anchors that disagree with NC_000913.2 are a known ~kb-level limit.
    op_left = op["left"].to_numpy(float)
    op_right = op["right"].to_numpy(float)
    op_strand = op["strand"].astype(str).to_numpy()
    op_name = op["name"].astype(str).to_numpy()
    # distance to operon body (0 if overlapping), circular-aware via mid clamp
    # Use linear distance on the linearised chromosome (same as gene_dist).
    nearest_i = np.empty(len(mid), dtype=int)
    nearest_d = np.empty(len(mid), dtype=float)
    for i, m in enumerate(mid):
        inside = (m >= op_left) & (m <= op_right)
        if inside.any():
            # prefer the shortest operon containing the guide
            cand = np.where(inside)[0]
            widths = op_right[cand] - op_left[cand]
            j = cand[int(np.argmin(widths))]
            nearest_i[i] = j
            nearest_d[i] = 0.0
        else:
            d = np.minimum(np.abs(m - op_left), np.abs(m - op_right))
            j = int(np.argmin(d))
            nearest_i[i] = j
            nearest_d[i] = float(d[j])
    out["near_operon"] = op_name[nearest_i]
    out["operon_strand"] = op_strand[nearest_i]
    out["operon_dist"] = nearest_d
    out["relative_operon"] = np.where(
        out["strand"].astype(str).to_numpy() == out["operon_strand"].to_numpy(),
        "same_as_operon", "opposite_operon",
    )
    _ = gseq  # silence unused if locate already loaded genome
    return out


def cohort_balance(idx: pd.DataFrame, orient_col: str, pos_lab: str, neg_lab: str) -> dict:
    a = idx[idx[orient_col] == pos_lab]
    b = idx[idx[orient_col] == neg_lab]

    def stats(df, col):
        x = pd.to_numeric(df[col], errors="coerce")
        return dict(
            n=int(len(df)),
            mean=float(np.nanmean(x)),
            median=float(np.nanmedian(x)),
            q25=float(np.nanquantile(x, 0.25)),
            q75=float(np.nanquantile(x, 0.75)),
        )

    cols = ["gene_dist", "tss_dist", "operon_dist", "flank_gc500", "y"]
    out = {"orient_col": orient_col, "pos": pos_lab, "neg": neg_lab}
    for c in cols:
        if c not in idx.columns:
            continue
        out[c] = {pos_lab: stats(a, c), neg_lab: stats(b, c)}
    # kind mix
    out["kind"] = {
        pos_lab: a["kind"].value_counts().astype(int).to_dict(),
        neg_lab: b["kind"].value_counts().astype(int).to_dict(),
    }
    return out


def match_on_covariates(idx: pd.DataFrame, orient_col: str, pos_lab: str, neg_lab: str,
                        covars: list[str], caliper: float = 0.75) -> pd.DataFrame:
    """Greedy 1:1 nearest-neighbour match of pos onto neg in z-scored covar space."""
    df = idx.copy()
    for c in covars:
        x = pd.to_numeric(df[c], errors="coerce").to_numpy(float)
        mu, sd = np.nanmean(x), np.nanstd(x)
        sd = sd if sd > 1e-8 else 1.0
        df[f"z_{c}"] = (x - mu) / sd

    pos = df[df[orient_col] == pos_lab].copy()
    neg = df[df[orient_col] == neg_lab].copy()
    zcols = [f"z_{c}" for c in covars]
    pos_z = pos[zcols].to_numpy(float)
    neg_z = neg[zcols].to_numpy(float)
    neg_ids = neg[config.ID_COL].to_numpy()
    used = set()
    kept_pos, kept_neg = [], []
    # match rarer onto more common
    if len(pos) <= len(neg):
        order = np.arange(len(pos))
        rng = np.random.default_rng(SEED)
        rng.shuffle(order)
        for i in order:
            d = np.sqrt(((neg_z - pos_z[i]) ** 2).sum(axis=1))
            # mask used
            for u in used:
                d[u] = np.inf
            j = int(np.argmin(d))
            if not np.isfinite(d[j]) or d[j] > caliper * np.sqrt(len(covars)):
                continue
            used.add(j)
            kept_pos.append(pos.iloc[i][config.ID_COL])
            kept_neg.append(neg_ids[j])
    else:
        order = np.arange(len(neg))
        rng = np.random.default_rng(SEED)
        rng.shuffle(order)
        pos_ids = pos[config.ID_COL].to_numpy()
        for j in order:
            d = np.sqrt(((pos_z - neg_z[j]) ** 2).sum(axis=1))
            for u in used:
                d[u] = np.inf
            i = int(np.argmin(d))
            if not np.isfinite(d[i]) or d[i] > caliper * np.sqrt(len(covars)):
                continue
            used.add(i)
            kept_pos.append(pos_ids[i])
            kept_neg.append(neg_ids[j])

    keep = set(kept_pos) | set(kept_neg)
    matched = df[df[config.ID_COL].isin(keep)].copy()
    matched.attrs["n_pairs"] = len(kept_pos)
    return matched


def run_asymmetry_strata(X, y, names, family_of, groups, labels, tag: str,
                         arms_keep=ARMS_KEEP) -> pd.DataFrame:
    names = np.asarray(names)
    family_of = np.asarray(family_of)
    base = np.where(family_of == "base")[0]
    flank = np.where(family_of != "base")[0]
    side = np.array([_side_of(n) for n in names[flank]])
    up_idx = flank[side == "up"]
    dn_idx = flank[side == "dn"]
    rng = np.random.default_rng(SEED)
    dn_matched = rng.choice(dn_idx, size=min(len(up_idx), len(dn_idx)), replace=False)
    arms = {
        "baseline": base,
        "upstream_only": np.sort(np.concatenate([base, up_idx])),
        "downstream_matched": np.sort(np.concatenate([base, dn_matched])),
    }
    arms = {k: v for k, v in arms.items() if k in arms_keep}

    rows = []
    strata = {}
    for lab in sorted(set(labels)):
        strata[lab] = np.asarray(labels) == lab
    for sname, mask in strata.items():
        if mask.sum() < 200:
            print(f"  skip {sname}: n={mask.sum()}", flush=True)
            continue
        for arm, cols in arms.items():
            print(f"  CV {tag}/{sname}/{arm} n={mask.sum()}", flush=True)
            res = cross_validate(
                X[mask][:, cols], y[mask], list(names[cols]), family_of[cols],
                seeds=(SEED,), groups=groups[mask],
                tag=f"orientctl_{tag}_{sname}_{arm}", experiment=arm,
                verbose=True)
            s = res["summary"]
            rows.append(dict(
                analysis=tag, stratum=sname, arm=arm, n=int(mask.sum()),
                spearman=s["spearman"]["mean"], r2=s["r2"]["mean"]))
    return pd.DataFrame(rows)


def ci_for_orientation(X, y, names, family_of, groups, relative, tag: str,
                       pos_lab: str, neg_lab: str) -> dict:
    """Bootstrap Δ = asym(pos) - asym(neg) using OOF up vs dn_matched."""
    arms, names, family_of = arm_columns(names, family_of, seed=SEED)
    oof = {}
    for stratum in (pos_lab, neg_lab):
        mask = np.asarray(relative) == stratum
        if mask.sum() < MIN_N:
            return dict(analysis=tag, error=f"too few in {stratum}", n=int(mask.sum()))
        for arm, cols in arms.items():
            key = f"{stratum}:{arm}"
            print(f"  OOF-CI {tag}/{key} n={mask.sum()}", flush=True)
            pred = oof_for_arm(
                X[mask], y[mask], names, family_of, cols, groups[mask],
                tag=f"{tag}_{stratum}", arm=arm)
            oof[key] = dict(y=y[mask], pred=pred, groups=groups[mask], n=int(mask.sum()))

    ci = bootstrap_delta(
        oof[f"{pos_lab}:downstream_matched"]["y"],
        oof[f"{pos_lab}:upstream_only"]["pred"],
        oof[f"{pos_lab}:downstream_matched"]["pred"],
        oof[f"{pos_lab}:downstream_matched"]["groups"],
        oof[f"{neg_lab}:downstream_matched"]["y"],
        oof[f"{neg_lab}:upstream_only"]["pred"],
        oof[f"{neg_lab}:downstream_matched"]["pred"],
        oof[f"{neg_lab}:downstream_matched"]["groups"],
        n_boot=N_BOOT, seed=0,
    )
    # bootstrap_delta names fields opposite/same; remap to pos/neg
    ci.update(
        analysis=tag,
        pos_lab=pos_lab,
        neg_lab=neg_lab,
        asymmetry_pos=ci.pop("asymmetry_opposite"),
        asymmetry_neg=ci.pop("asymmetry_same"),
        n_pos=oof[f"{pos_lab}:downstream_matched"]["n"],
        n_neg=oof[f"{neg_lab}:downstream_matched"]["n"],
        n_groups_pos=ci.pop("n_groups_opposite"),
        n_groups_neg=ci.pop("n_groups_same"),
    )
    return ci


def main():
    if not config.QCT_TABLES.exists() or not (config.INTERIM / "v_column_mapping.json").exists():
        raise SystemExit("Need qct_lookup_tables.json and v_column_mapping.json")

    print("=== load + locate s6_good ===", flush=True)
    lib = load_intergenic_catalog()
    sets = load_sets(lib)
    raw = locate_and_orient(sets[TAG])
    print(f"  located: {len(raw)}  kind={raw.kind.value_counts().to_dict()}", flush=True)

    print("=== annotate TSS + operon ===", flush=True)
    idx = annotate_tss_operon(raw)
    idx_path = OUT / "intergenic_orientation_controls_index.csv"
    idx.to_csv(idx_path, index=False)
    print(f"  wrote {idx_path}", flush=True)
    print(f"  relative_tss: {idx.relative_tss.value_counts().to_dict()}", flush=True)
    print(f"  relative_operon: {idx.relative_operon.value_counts().to_dict()}", flush=True)

    balance = {
        "gene": cohort_balance(idx, "relative", "opposite_gene", "same_as_gene"),
        "tss": cohort_balance(idx, "relative_tss", "opposite_tss", "same_as_tss"),
        "operon": cohort_balance(idx, "relative_operon", "opposite_operon", "same_as_operon"),
    }
    (OUT / "intergenic_orientation_cohort_balance.json").write_text(
        json.dumps(balance, indent=2))

    print("=== build matrix (force once so meta carries enriched labels) ===", flush=True)
    for p in CACHE.glob(f"*_{TAG}.*"):
        p.unlink(missing_ok=True)
    X, y, names, meta = build_matrix(idx, TAG, force=True)
    # Keep idx in the same row order as the matrix
    idx = idx.set_index(config.ID_COL).loc[list(meta["ids"])].reset_index()
    X, y = np.asarray(X), np.asarray(y)
    family_of = meta["family_of"]
    groups = bin100k_groups(idx["left"].to_numpy())
    names = list(names)

    asym_frames = []
    ci_rows = []

    # --- 1. Promoter / RBS × gene orientation ---
    for kind in ("promoter", "RBS"):
        mask = (idx["kind"].to_numpy() == kind)
        print(f"\n=== kind={kind} n={mask.sum()} ===", flush=True)
        df = run_asymmetry_strata(
            X[mask], y[mask], names, family_of, groups[mask],
            idx.loc[mask, "relative"].to_numpy(),
            tag=f"kind_{kind}_by_gene")
        asym_frames.append(df)
        ci = ci_for_orientation(
            X[mask], y[mask], names, family_of, groups[mask],
            idx.loc[mask, "relative"].to_numpy(),
            tag=f"kind_{kind}_gene",
            pos_lab="opposite_gene", neg_lab="same_as_gene")
        ci_rows.append(ci)
        print(json.dumps({k: ci[k] for k in ci if k in (
            "analysis", "asymmetry_pos", "asymmetry_neg", "delta",
            "delta_lo", "delta_hi", "p_delta_le_0", "n_pos", "n_neg")}, indent=2),
              flush=True)

    # --- 2. TSS orientation (all kinds) ---
    print("\n=== TSS orientation ===", flush=True)
    df = run_asymmetry_strata(
        X, y, names, family_of, groups,
        idx["relative_tss"].to_numpy(), tag="tss")
    asym_frames.append(df)
    ci = ci_for_orientation(
        X, y, names, family_of, groups, idx["relative_tss"].to_numpy(),
        tag="tss", pos_lab="opposite_tss", neg_lab="same_as_tss")
    ci_rows.append(ci)
    print(json.dumps({k: ci[k] for k in ci if not k.startswith("method")}, indent=2),
          flush=True)

    # --- 3. Operon orientation ---
    print("\n=== Operon orientation ===", flush=True)
    df = run_asymmetry_strata(
        X, y, names, family_of, groups,
        idx["relative_operon"].to_numpy(), tag="operon")
    asym_frames.append(df)
    ci = ci_for_orientation(
        X, y, names, family_of, groups, idx["relative_operon"].to_numpy(),
        tag="operon", pos_lab="opposite_operon", neg_lab="same_as_operon")
    ci_rows.append(ci)

    # --- 4. Matched gene orientation (distance + GC) ---
    print("\n=== matched gene orientation (gene_dist + flank_gc500) ===", flush=True)
    matched = match_on_covariates(
        idx, "relative", "opposite_gene", "same_as_gene",
        covars=["gene_dist", "flank_gc500"], caliper=0.75)
    n_pairs = matched.attrs.get("n_pairs", len(matched) // 2)
    print(f"  matched pairs: {n_pairs} (n={len(matched)})", flush=True)
    m_ids = set(matched[config.ID_COL].astype(str))
    m_mask = idx[config.ID_COL].astype(str).isin(m_ids).to_numpy()
    balance["gene_matched"] = cohort_balance(
        idx[m_mask], "relative", "opposite_gene", "same_as_gene")
    balance["gene_matched"]["n_pairs"] = int(n_pairs)
    (OUT / "intergenic_orientation_cohort_balance.json").write_text(
        json.dumps(balance, indent=2))

    df = run_asymmetry_strata(
        X[m_mask], y[m_mask], names, family_of, groups[m_mask],
        idx.loc[m_mask, "relative"].to_numpy(), tag="gene_matched_dist_gc")
    asym_frames.append(df)
    ci = ci_for_orientation(
        X[m_mask], y[m_mask], names, family_of, groups[m_mask],
        idx.loc[m_mask, "relative"].to_numpy(),
        tag="gene_matched_dist_gc",
        pos_lab="opposite_gene", neg_lab="same_as_gene")
    ci_rows.append(ci)

    # --- 5. Matched TSS orientation (tss_dist + GC) ---
    print("\n=== matched TSS orientation (tss_dist + flank_gc500) ===", flush=True)
    matched_t = match_on_covariates(
        idx, "relative_tss", "opposite_tss", "same_as_tss",
        covars=["tss_dist", "flank_gc500"], caliper=0.75)
    n_pairs_t = matched_t.attrs.get("n_pairs", len(matched_t) // 2)
    print(f"  matched pairs: {n_pairs_t} (n={len(matched_t)})", flush=True)
    mt_ids = set(matched_t[config.ID_COL].astype(str))
    mt_mask = idx[config.ID_COL].astype(str).isin(mt_ids).to_numpy()
    balance["tss_matched"] = cohort_balance(
        idx[mt_mask], "relative_tss", "opposite_tss", "same_as_tss")
    balance["tss_matched"]["n_pairs"] = int(n_pairs_t)
    (OUT / "intergenic_orientation_cohort_balance.json").write_text(
        json.dumps(balance, indent=2))

    df = run_asymmetry_strata(
        X[mt_mask], y[mt_mask], names, family_of, groups[mt_mask],
        idx.loc[mt_mask, "relative_tss"].to_numpy(), tag="tss_matched_dist_gc")
    asym_frames.append(df)
    ci = ci_for_orientation(
        X[mt_mask], y[mt_mask], names, family_of, groups[mt_mask],
        idx.loc[mt_mask, "relative_tss"].to_numpy(),
        tag="tss_matched_dist_gc",
        pos_lab="opposite_tss", neg_lab="same_as_tss")
    ci_rows.append(ci)

    raw = pd.concat(asym_frames, ignore_index=True)
    # summarise per analysis
    rows = []
    for analysis, sub in raw.groupby("analysis"):
        for stratum, ssub in sub.groupby("stratum"):
            piv = ssub.set_index("arm")["spearman"]
            b = float(piv.get("baseline", np.nan))
            row = dict(analysis=analysis, stratum=stratum,
                       n=int(ssub["n"].iloc[0]), baseline=b)
            for arm in ("upstream_only", "downstream_matched"):
                if arm in piv.index:
                    row[f"gain_{arm}"] = float(piv[arm] - b)
            if "gain_downstream_matched" in row and "gain_upstream_only" in row:
                row["asymmetry_matched"] = (
                    row["gain_downstream_matched"] - row["gain_upstream_only"])
            rows.append(row)
    summ = pd.DataFrame(rows)

    raw.to_csv(OUT / "intergenic_orientation_controls_asymmetry.csv", index=False)
    summ.to_csv(OUT / "intergenic_orientation_controls_summary.csv", index=False)

    # flatten CIs
    ci_flat = []
    for r in ci_rows:
        if "error" in r:
            ci_flat.append(r)
            continue
        ci_flat.append({k: r[k] for k in (
            "analysis", "pos_lab", "neg_lab", "asymmetry_pos", "asymmetry_neg",
            "delta", "delta_lo", "delta_hi", "delta_se", "p_delta_le_0",
            "n_pos", "n_neg", "n_boot", "n_groups_pos", "n_groups_neg") if k in r})
    (OUT / "intergenic_orientation_controls_delta_ci.json").write_text(
        json.dumps(ci_rows, indent=2, default=float))
    pd.DataFrame(ci_flat).to_csv(
        OUT / "intergenic_orientation_controls_delta_ci.csv", index=False)

    print("\n=== SUMMARY ===", flush=True)
    print(summ.to_string(index=False), flush=True)
    print("\n=== DELTA CI ===", flush=True)
    print(pd.DataFrame(ci_flat).to_string(index=False), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
