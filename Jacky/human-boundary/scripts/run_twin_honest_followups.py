#!/usr/bin/env python3
"""Twin-honest follow-ups left open by Runjia's NOTE / §21.6.

1. Within-human Family A under twin-grouped folds on Jacky's cached
   base+A matrix (confirms Runjia's +0.0226 on our artifact path).
2. Cross-kingdom Family A transfer with human rows kept as-is vs
   deduplicated to one row per protospacer (the outstanding transfer
   re-run from NOTE_human_twin_leak.md).

Usage:
  python Jacky/human-boundary/scripts/run_twin_honest_followups.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

_REPO = Path(__file__).resolve().parents[3]
ROOT = Path(os.environ.get("RSI09_ROOT", str(_REPO / "Runjia"))).resolve()
os.environ["RSI09_ROOT"] = str(ROOT)
sys.path.insert(0, str(ROOT))

from sgrna import config  # noqa: E402
from sgrna.harness.run_ablation import _impute, cross_validate  # noqa: E402

OUT = _REPO / "Jacky" / "human-boundary" / "results"
CACHE = config.INTERIM / "human_boundary"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 41
SEEDS = (41,)  # one seed is enough to confirm Runjia's 3-seed §21.6 on our caches
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


def _human_base_a():
    meta = json.loads((CACHE / "meta_human.json").read_text())
    X = np.load(CACHE / "X_human_base_a.npy")
    y = np.asarray(meta["y"], float)
    names = list(meta["full_names"])
    fam = list(meta["family_of"])
    ids = [str(i) for i in meta["ids"]]
    return X, y, names, fam, ids


def _human_protos(ids):
    loc = pd.read_csv(CACHE / "human_located.csv")
    loc[config.ID_COL] = loc[config.ID_COL].astype(str)
    m = loc.set_index(config.ID_COL).reindex(ids)
    return m["protospacer"].astype(str).to_numpy()


def _ecoli_base_a():
    """Prefer Jacky human-boundary ecoli cache; else slice base+A from discovery matrix."""
    cache_x = CACHE / "X_ecoli_base_a.npy"
    cache_m = CACHE / "meta_ecoli_base_a.json"
    if cache_x.exists() and cache_m.exists():
        meta = json.loads(cache_m.read_text())
        return (
            np.load(cache_x),
            np.asarray(meta["y"], float),
            list(meta["full_names"]),
            list(meta["family_of"]),
            list(meta["ids"]),
        )

    rich_x = CACHE / "X_ecoli_base_a_i_shape_d_mechanics_c_folding.npy"
    rich_m = CACHE / "meta_ecoli_base_a_i_shape_d_mechanics_c_folding.json"
    if rich_x.exists() and rich_m.exists():
        meta = json.loads(rich_m.read_text())
        names = list(meta["full_names"])
        fam = list(meta["family_of"])
        keep = [i for i, f in enumerate(fam) if f in ("base", "a_flank")]
        X = np.load(rich_x)[:, keep]
        print(f"  E. coli base+A sliced from discovery cache ({X.shape})", flush=True)
        return (
            X,
            np.asarray(meta["y"], float),
            [names[i] for i in keep],
            [fam[i] for i in keep],
            list(meta["ids"]),
        )

    idx = pd.read_csv(config.INTERIM / "guide_index.csv")
    has = (
        idx["protospacer"].notna()
        & (idx["protospacer"].astype(str).str.len() == 20)
        & idx.get("located", True).astype(bool)
        & idx.get("unique_in_genome", True).astype(bool)
    )
    idx = idx.loc[has].reset_index(drop=True)
    from sgrna.build import featurise  # local fallback only
    print(f"  E. coli featurising portable base for {len(idx):,} ...", flush=True)
    base, base_names = featurise.matrix(idx["protospacer"].tolist(), verbose=True)
    base = np.asarray(base, np.float32)
    flank = pd.read_csv(config.FEATURE_DIR / "a_flank.csv")
    flank = flank.set_index(config.ID_COL).reindex(idx[config.ID_COL])
    vals = flank.to_numpy(dtype=np.float32)
    good = ~np.all(np.isnan(vals), axis=0)
    flank_names = [c for c, k in zip(flank.columns, good) if k]
    Xf = vals[:, good]
    X = np.hstack([base, Xf])
    names = list(base_names) + flank_names
    fam = ["base"] * len(base_names) + ["a_flank"] * len(flank_names)
    y = pd.to_numeric(idx["cut_score"], errors="coerce").to_numpy(float)
    ids = idx[config.ID_COL].astype(str).tolist()
    meta = dict(y=y.tolist(), full_names=names, family_of=fam, ids=ids, n=len(ids))
    np.save(cache_x, X)
    cache_m.write_text(json.dumps(meta))
    return X, y, names, fam, ids


def _align(Xa, na, Xb, nb):
    shared = [c for c in na if c in set(nb)]
    ia = {c: i for i, c in enumerate(na)}
    ib = {c: i for i, c in enumerate(nb)}
    A = Xa[:, [ia[c] for c in shared]].astype(np.float32)
    B = Xb[:, [ib[c] for c in shared]].astype(np.float32)
    return A, B, shared


def _transfer(Xtr, ytr, Xte, yte, seed=SEED, n_top=N_TOP, **xgb_kw):
    A, B = _impute(Xtr, Xte)
    m0 = _xgb(seed=seed, n_estimators=300, **{k: v for k, v in xgb_kw.items() if k != "n_estimators"})
    m0.fit(A, ytr)
    top = np.argsort(m0.feature_importances_)[::-1][:n_top]
    m = _xgb(seed=seed, **xgb_kw)
    m.fit(A[:, top], ytr)
    pred = np.asarray(m.predict(B[:, top])).ravel()
    return pred, _spearman(yte, pred)


def _dedupe_by_proto(X, y, names, fam, ids, protos):
    """One row per protospacer: mean label, first feature row."""
    df = pd.DataFrame({"proto": protos, "y": y, "idx": np.arange(len(y))})
    # keep first occurrence features; average y across twins
    y_mean = df.groupby("proto", sort=False)["y"].mean()
    first = df.groupby("proto", sort=False)["idx"].first()
    keep = first.to_numpy()
    order = first.index.tolist()
    return (
        X[keep],
        y_mean.loc[order].to_numpy(float),
        names,
        fam,
        [ids[i] for i in keep],
        np.asarray(order, dtype=object),
    )


def run_family_a_twin_cv():
    print("=== Within-human Family A, twin-grouped CV ===", flush=True)
    X, y, names, fam, ids = _human_base_a()
    protos = _human_protos(ids)
    ok = np.isfinite(y) & pd.notna(protos)
    X, y, protos = X[ok], y[ok], protos[ok]
    groups = pd.factorize(protos)[0]
    base_i = [i for i, f in enumerate(fam) if f == "base"]
    rows = []
    for folds, groups_arg in (("row-wise", None), ("twin-grouped", groups)):
        for arm, cols in (("base", base_i), ("base+a_flank", list(range(len(names))))):
            print(f"  {folds} / {arm} ...", flush=True)
            res = cross_validate(
                np.asarray(X[:, cols], np.float32), y,
                [names[i] for i in cols],
                [fam[i] for i in cols],
                n_features=300, seeds=SEEDS, groups=groups_arg,
                tag=f"twin2_{folds}_{arm}".replace("+", "p"), experiment=f"{folds}:{arm}",
                verbose=True,
            )
            sp = res["summary"]["spearman"]
            rows.append(dict(
                folds=folds, arm=arm,
                spearman=float(sp["mean"]),
                spearman_sd=float(sp.get("sd", sp.get("std", float("nan")))),
                n=int(len(y)), n_groups=int(len(np.unique(groups))),
            ))
    df = pd.DataFrame(rows)
    # increments
    out = []
    for folds in ("row-wise", "twin-grouped"):
        b = df[(df.folds == folds) & (df.arm == "base")].iloc[0]
        a = df[(df.folds == folds) & (df.arm == "base+a_flank")].iloc[0]
        out.append(dict(
            folds=folds, base=b.spearman, base_a=a.spearman,
            family_a_delta=a.spearman - b.spearman,
            base_sd=b.spearman_sd, base_a_sd=a.spearman_sd,
            n=b.n, n_groups=b.n_groups,
        ))
    summary = pd.DataFrame(out)
    df.to_csv(OUT / "human_family_a_twin_cv_arms.csv", index=False)
    summary.to_csv(OUT / "human_family_a_twin_cv.csv", index=False)
    print(summary.to_string(index=False), flush=True)
    return summary


def run_transfer_deduped():
    print("=== Cross-kingdom transfer: full vs deduped human ===", flush=True)
    Xe, ye, ne, fe, _ = _ecoli_base_a()
    Xh, yh, nh, fh, ids = _human_base_a()
    protos = _human_protos(ids)

    ok_e = np.isfinite(ye)
    Xe, ye = Xe[ok_e], ye[ok_e]

    variants = {
        "human_all_rows": (Xh, yh, nh, fh, protos),
    }
    Xd, yd, nd, fd, idsd, protos_d = _dedupe_by_proto(Xh, yh, nh, fh, ids, protos)
    variants["human_deduped_proto"] = (Xd, yd, nd, fd, protos_d)

    def subset(names, fam, want):
        if want == "base":
            return [n for n, f in zip(names, fam) if f == "base"]
        if want == "a_flank":
            return [n for n, f in zip(names, fam) if f == "a_flank"]
        return list(names)

    rows = []
    for human_mode, (Xh_m, yh_m, nh_m, fh_m, _) in variants.items():
        ok_h = np.isfinite(yh_m)
        Xh_m, yh_m = Xh_m[ok_h], yh_m[ok_h]
        for arm in ("base", "a_flank", "base+a_flank"):
            want = "all" if arm == "base+a_flank" else arm
            ne_s = subset(ne, fe, want)
            nh_s = subset(nh_m, fh_m, want)
            ie = {c: i for i, c in enumerate(ne)}
            ih = {c: i for i, c in enumerate(nh_m)}
            A, B, shared = _align(
                Xe[:, [ie[c] for c in ne_s]], ne_s,
                Xh_m[:, [ih[c] for c in nh_s]], nh_s,
            )
            print(f"  {human_mode} / {arm}: shared {len(shared)}  "
                  f"n_h={len(yh_m):,}", flush=True)
            _, rho_eh = _transfer(A, ye, B, yh_m)
            _, rho_he = _transfer(B, yh_m, A, ye)
            rows.append(dict(
                human_mode=human_mode, arm=arm, n_shared=len(shared),
                n_ecoli=int(len(ye)), n_human=int(len(yh_m)),
                ecoli_to_human=rho_eh, human_to_ecoli=rho_he,
            ))
            print(f"    E→H {rho_eh:+.4f}  H→E {rho_he:+.4f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "family_a_kingdom_transfer_twin.csv", index=False)
    print(df.to_string(index=False), flush=True)
    return df


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--transfer-only", action="store_true")
    ap.add_argument("--cv-only", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    tr = cv = None
    if not a.cv_only:
        tr_path = OUT / "family_a_kingdom_transfer_twin.csv"
        if tr_path.exists() and a.transfer_only:
            tr = pd.read_csv(tr_path)
            print("  reusing", tr_path, flush=True)
        else:
            tr = run_transfer_deduped()
    if not a.transfer_only:
        cv = run_family_a_twin_cv()
    manifest = {
        "seeds": list(SEEDS),
        "note": (
            "Within-human Family A twin CV confirms Runjia §21.6 on Jacky caches. "
            "Transfer compares all human rows vs one-row-per-protospacer."
        ),
        "elapsed_sec": time.time() - t0,
        "family_a_twin_cv": None if cv is None else cv.to_dict(orient="records"),
        "transfer": None if tr is None else tr.to_dict(orient="records"),
    }
    (OUT / "human_twin_honest_summary.json").write_text(json.dumps(manifest, indent=2))
    print("DONE", json.dumps(manifest, indent=2)[:2000], flush=True)


if __name__ == "__main__":
    main()
