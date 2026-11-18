#!/usr/bin/env python3
"""Human discovery phase (H1–H5): what raises human ρ, then retest transfer.

H1  Capacity / HP ladder on base and base+A
H2  Additivity (ridge vs boosting)
H3  Gene-grouped CV
H4  Ablate i_shape / d_mechanics / c_folding on top of base+A
H5  Cross-kingdom transfer for base / A / A+extras (features on both sides)

Uses Tier-1 caches under Runjia/data/interim/human_boundary/.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

_REPO = Path(__file__).resolve().parents[3]
ROOT = Path(os.environ.get("RSI09_ROOT", str(_REPO / "Runjia"))).resolve()
os.environ["RSI09_ROOT"] = str(ROOT)
sys.path.insert(0, str(ROOT))

from sgrna import config, featurise  # noqa: E402
from sgrna.features import a_flank, c_folding, d_mechanics, i_shape  # noqa: E402
from sgrna.run_ablation import (  # noqa: E402
    _impute,
    champion_params,
    cross_validate,
    make_selector,
)

OUT = _REPO / "Jacky" / "human-boundary" / "results"
CACHE = config.INTERIM / "human_boundary"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)
config.FEATURE_DIR.mkdir(parents=True, exist_ok=True)

SEEDS = (41, 42, 43)
SEED = 41
N_TOP = 300

# Capacity probe: deeper / faster-learning than the bacterial champion.
# (Full 1000-tree teammate settings remain in HUMAN_BASELINE_SETTINGS.md;
# discovery uses 400 trees so the sweep is tractable.)
HUMAN_HPS = dict(n_estimators=400, learning_rate=0.3, max_depth=6)


def _spearman(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    m = np.isfinite(y) & np.isfinite(p)
    if m.sum() < 3:
        return float("nan")
    r = spearmanr(y[m], p[m]).statistic
    return float(r) if np.isfinite(r) else float("nan")


def _load_human():
    meta = json.loads((CACHE / "meta_human.json").read_text())
    X = np.load(CACHE / "X_human_base_a.npy")
    y = np.asarray(meta["y"], float)
    names = list(meta["full_names"])
    fam = list(meta["family_of"])
    ids = [str(i) for i in meta["ids"]]
    return X, y, names, fam, ids


def _cv(X, y, names, fam, tag, experiment, seeds=SEEDS, n_features=None,
        overrides=None, groups=None):
    res = cross_validate(
        np.asarray(X, np.float32),
        np.asarray(y, float),
        list(names),
        np.asarray(fam),
        n_features=n_features or config.N_FEATURES,
        seeds=seeds,
        tag=tag,
        experiment=experiment,
        verbose=True,
        champion_overrides=overrides,
        groups=groups,
    )
    sp = res["summary"]["spearman"]
    r2 = res["summary"]["r2"]
    sp_sd = sp.get("sd", sp.get("std", float("nan")))
    if sp_sd is None or (isinstance(sp_sd, float) and not np.isfinite(sp_sd)):
        sp_sd = float("nan")
    return dict(
        experiment=experiment,
        tag=tag,
        n=int(len(y)),
        n_cols=int(X.shape[1]),
        spearman=float(sp["mean"]),
        spearman_sd=float(sp_sd) if np.isfinite(sp_sd) else float("nan"),
        r2=float(r2["mean"]),
        n_folds=int(res.get("n_folds_done", len(seeds) * 5)),
        incomplete=not bool(res.get("complete", True)),
    )


def _build_block(builder, index: pd.DataFrame, cache_name: str) -> pd.DataFrame:
    path = CACHE / cache_name
    if path.exists():
        print(f"  cached {cache_name}", flush=True)
        return pd.read_csv(path)
    print(f"  building {cache_name} for {len(index):,} guides ...", flush=True)
    t0 = time.time()
    block = builder.build(index)
    block.to_csv(path, index=False)
    print(f"  wrote {path.name} {block.shape} in {time.time() - t0:.1f}s", flush=True)
    return block


def _attach(X, names, fam, block: pd.DataFrame, ids, family: str):
    b = block.set_index(config.ID_COL).reindex(ids)
    vals = b.to_numpy(dtype=np.float32)
    good = ~np.all(np.isnan(vals), axis=0)
    new_names = [c for c, ok in zip(b.columns, good) if ok]
    Xn = vals[:, good]
    X2 = np.hstack([X, Xn])
    names2 = list(names) + new_names
    fam2 = list(fam) + [family] * len(new_names)
    return X2, names2, fam2


def _ensure_ecoli_a_flank():
    path = config.FEATURE_DIR / "a_flank.csv"
    if path.exists():
        print(f"  ecoli a_flank present ({path})", flush=True)
        return
    idx = pd.read_csv(config.GUIDE_INDEX)
    print(f"  building E. coli a_flank for {len(idx):,} ...", flush=True)
    t0 = time.time()
    block = a_flank.build(idx)
    block.to_csv(path, index=False)
    print(f"  wrote {path} {block.shape} in {time.time() - t0:.1f}s", flush=True)


def _ecoli_bundle(extra_families: list[str] | None = None):
    """Base + a_flank (+ optional shape/mech/fold) for E. coli, cached per key."""
    extra_families = extra_families or []
    key = "base_a" + (("_" + "_".join(extra_families)) if extra_families else "")
    cache_x = CACHE / f"X_ecoli_{key}.npy"
    cache_m = CACHE / f"meta_ecoli_{key}.json"
    if cache_x.exists() and cache_m.exists():
        meta = json.loads(cache_m.read_text())
        print(f"  cached E. coli {key}: {meta['n']} x {meta['n_full']}", flush=True)
        return (
            np.load(cache_x),
            np.asarray(meta["y"], float),
            list(meta["full_names"]),
            list(meta["family_of"]),
            list(meta["ids"]),
        )

    _ensure_ecoli_a_flank()
    idx = pd.read_csv(config.GUIDE_INDEX)
    has = (
        idx["protospacer"].notna()
        & (idx["protospacer"].astype(str).str.len() == 20)
        & idx["located"].astype(bool)
        & idx["unique_in_genome"].astype(bool)
    )
    idx = idx.loc[has].reset_index(drop=True)
    print(f"  E. coli featurising base for {len(idx):,} ...", flush=True)
    base, base_names = featurise.matrix(idx["protospacer"].tolist(), verbose=True)
    base = np.asarray(base, np.float32)
    flank = pd.read_csv(config.FEATURE_DIR / "a_flank.csv").set_index(config.ID_COL).reindex(idx[config.ID_COL])
    vals = flank.to_numpy(dtype=np.float32)
    good = ~np.all(np.isnan(vals), axis=0)
    flank_names = [c for c, ok in zip(flank.columns, good) if ok]
    X = np.hstack([base, vals[:, good]])
    names = list(base_names) + flank_names
    fam = ["base"] * len(base_names) + ["a_flank"] * len(flank_names)
    ids = idx[config.ID_COL].astype(str).tolist()

    builders = {
        "i_shape": i_shape,
        "d_mechanics": d_mechanics,
        "c_folding": c_folding,
    }
    for fam_name in extra_families:
        print(f"  E. coli building {fam_name} ...", flush=True)
        block = builders[fam_name].build(idx)
        # also cache under FEATURE_DIR for reuse
        block.to_csv(config.FEATURE_DIR / f"{fam_name}.csv", index=False)
        X, names, fam = _attach(X, names, fam, block, ids, fam_name)

    y = pd.to_numeric(idx["cut_score"], errors="coerce").to_numpy(float)
    meta = dict(
        y=y.tolist(), full_names=names, family_of=fam, ids=ids,
        n=len(ids), n_full=int(X.shape[1]),
    )
    np.save(cache_x, X)
    cache_m.write_text(json.dumps(meta))
    return X, y, names, fam, ids


def _align(Xa, na, Xb, nb):
    shared = [c for c in na if c in set(nb)]
    ia = {c: i for i, c in enumerate(na)}
    ib = {c: i for i, c in enumerate(nb)}
    return (
        Xa[:, [ia[c] for c in shared]].astype(np.float32),
        Xb[:, [ib[c] for c in shared]].astype(np.float32),
        shared,
    )


def _transfer(Xtr, ytr, Xte, yte, seed=SEED, n_top=N_TOP, **xgb_kw):
    import xgboost as xgb
    A, B = _impute(Xtr, Xte)
    p0 = champion_params(seed)
    p0.update(n_estimators=300, importance_type="gain")
    p0.update({k: v for k, v in xgb_kw.items() if k != "n_estimators"})
    m0 = xgb.XGBRegressor(**p0)
    m0.fit(A, ytr)
    top = np.argsort(m0.feature_importances_)[::-1][:n_top]
    p = champion_params(seed)
    p.update(xgb_kw)
    m = xgb.XGBRegressor(**p)
    m.fit(A[:, top], ytr)
    pred = np.asarray(m.predict(B[:, top])).ravel()
    return _spearman(yte, pred)


def run_h1_h4_human(seeds=SEEDS):
    print("=== H1/H4 human ladder + family ablations ===", flush=True)
    X, y, names, fam, ids = _load_human()
    ok = np.isfinite(y)
    X, y = X[ok], y[ok]
    ids_ok = [ids[i] for i, k in enumerate(ok) if k]
    fam = list(fam)
    names = list(names)

    loc = pd.read_csv(CACHE / "human_located.csv")
    loc[config.ID_COL] = loc[config.ID_COL].astype(str)
    loc = loc.set_index(config.ID_COL).reindex(ids_ok).reset_index()

    shape = _build_block(i_shape, loc, "i_shape_human.csv")
    mech = _build_block(d_mechanics, loc, "d_mechanics_human.csv")
    fold = _build_block(c_folding, loc, "c_folding_human.csv")

    base_i = [i for i, f in enumerate(fam) if f == "base"]
    both_i = list(range(X.shape[1]))

    rows = []
    # H1 capacity
    for label, cols, nfeat, ov in (
        ("base_champion", base_i, 300, None),
        ("base_human_hps", base_i, 400, HUMAN_HPS),
        ("baseA_champion", both_i, 300, None),
        ("baseA_human_hps", both_i, 400, HUMAN_HPS),
    ):
        print(f"\n-- {label} --", flush=True)
        rows.append(_cv(
            X[:, cols], y, [names[i] for i in cols], [fam[i] for i in cols],
            tag=f"hdisc_{label}", experiment=label, seeds=seeds,
            n_features=nfeat, overrides=ov,
        ))

    # H4 families on top of base+A
    bundles = {
        "baseA_shape": (shape, "i_shape"),
        "baseA_mechanics": (mech, "d_mechanics"),
        "baseA_folding": (fold, "c_folding"),
    }
    for label, (block, family) in bundles.items():
        X2, n2, f2 = _attach(X, names, fam, block, ids_ok, family)
        print(f"\n-- {label} ({X2.shape[1]} cols) --", flush=True)
        rows.append(_cv(
            X2, y, n2, f2, tag=f"hdisc_{label}", experiment=label, seeds=seeds,
        ))

    # all extras stacked on base+A
    X_all, n_all, f_all = _attach(X, names, fam, shape, ids_ok, "i_shape")
    X_all, n_all, f_all = _attach(X_all, n_all, f_all, mech, ids_ok, "d_mechanics")
    X_all, n_all, f_all = _attach(X_all, n_all, f_all, fold, ids_ok, "c_folding")
    print(f"\n-- baseA_shape_mech_fold ({X_all.shape[1]} cols) --", flush=True)
    rows.append(_cv(
        X_all, y, n_all, f_all,
        tag="hdisc_baseA_all", experiment="baseA_shape_mech_fold", seeds=seeds,
    ))
    # also human HPs on the richest set
    print("\n-- baseA_all_human_hps --", flush=True)
    rows.append(_cv(
        X_all, y, n_all, f_all,
        tag="hdisc_baseA_all_hps", experiment="baseA_shape_mech_fold_human_hps",
        seeds=seeds, n_features=400, overrides=HUMAN_HPS,
    ))

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "human_discovery_ladder.csv", index=False)
    print(df.to_string(index=False), flush=True)

    # persist richest human matrix for transfer
    np.save(CACHE / "X_human_discovery_all.npy", X_all)
    (CACHE / "meta_human_discovery_all.json").write_text(json.dumps(dict(
        full_names=n_all, family_of=f_all, ids=ids_ok, y=y.tolist(),
        n=len(ids_ok), n_full=int(X_all.shape[1]),
    )))
    return df, (X_all, n_all, f_all, ids_ok, y)


def run_h2_additivity(seeds=SEEDS):
    print("=== H2 additivity ===", flush=True)
    # Keep additivity comparable to Runjia's human_baseline --additivity, but
    # use a lighter XGB (400 trees, depth 6) so the discovery sweep finishes.
    X, y, names, fam, ids = _load_human()
    ok = np.isfinite(y)
    X, y = X[ok], y[ok]
    fam = np.asarray(fam)
    rows = []
    xgb_add = dict(n_estimators=400, learning_rate=0.3, max_depth=6)
    for arm, mask in (
        ("base", fam == "base"),
        ("baseA", np.ones(len(fam), bool)),
    ):
        Xm = X[:, mask]
        for model in ("ridge", "xgb"):
            fold_rho = []
            for seed in seeds:
                kf = KFold(5, shuffle=True, random_state=seed)
                preds = np.full(len(y), np.nan)
                for tr, va in kf.split(Xm):
                    A, B = _impute(Xm[tr], Xm[va])
                    sel = make_selector(seed)
                    sel.fit(A, y[tr])
                    top = np.argsort(sel.feature_importances_)[::-1][:400]
                    if model == "ridge":
                        m = Ridge(alpha=10.0)
                        m.fit(A[:, top], y[tr])
                        preds[va] = m.predict(B[:, top])
                    else:
                        import xgboost as xgb
                        p = champion_params(seed)
                        p.update(xgb_add)
                        m = xgb.XGBRegressor(**p)
                        m.fit(A[:, top], y[tr])
                        preds[va] = m.predict(B[:, top])
                fold_rho.append(_spearman(y, preds))
                print(f"  {arm}/{model}/seed{seed}: {_spearman(y, preds):.4f}", flush=True)
            rows.append(dict(
                arm=arm, model=model,
                spearman=float(np.mean(fold_rho)),
                spearman_std=float(np.std(fold_rho)),
                n=int(len(y)),
            ))
    df = pd.DataFrame(rows)
    # ratios
    out_rows = []
    for arm in ("base", "baseA"):
        r = float(df.loc[(df.arm == arm) & (df.model == "ridge"), "spearman"].iloc[0])
        x = float(df.loc[(df.arm == arm) & (df.model == "xgb"), "spearman"].iloc[0])
        out_rows.append(dict(arm=arm, ridge=r, xgb=x, ridge_over_xgb=r / x if x else np.nan))
    summary = pd.DataFrame(out_rows)
    df.to_csv(OUT / "human_discovery_additivity_folds.csv", index=False)
    summary.to_csv(OUT / "human_discovery_additivity.csv", index=False)
    print(summary.to_string(index=False), flush=True)
    return summary


def run_h3_grouped(seeds=SEEDS):
    print("=== H3 gene-grouped CV ===", flush=True)
    X, y, names, fam, ids = _load_human()
    st = pd.read_csv(CACHE / "human_strand_annotated.csv")
    st[config.ID_COL] = st[config.ID_COL].astype(str)
    gene = st.set_index(config.ID_COL).reindex(ids)["gene_name"].astype(str).fillna("NA").to_numpy()
    ok = np.isfinite(y)
    X, y, gene = X[ok], y[ok], gene[ok]
    fam = np.asarray(fam)
    rows = []
    for arm, mask in (("base", fam == "base"), ("baseA", np.ones(len(fam), bool))):
        for mode in ("random", "gene"):
            print(f"\n-- {arm}_{mode} --", flush=True)
            rows.append(_cv(
                X[:, mask], y,
                [names[i] for i, m in enumerate(mask) if m],
                [fam[i] for i, m in enumerate(mask) if m],
                tag=f"hdisc_grp_{arm}_{mode}",
                experiment=f"{arm}_{mode}",
                seeds=seeds,
                groups=None if mode == "random" else gene,
            ))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "human_discovery_grouped.csv", index=False)
    print(df.to_string(index=False), flush=True)
    return df


def run_h5_transfer(human_all=None):
    print("=== H5 transfer retest ===", flush=True)
    # human base+A
    Xh, yh, nh, fh, ids_h = _load_human()
    ok_h = np.isfinite(yh)
    Xh, yh = Xh[ok_h], yh[ok_h]
    ids_h = [ids_h[i] for i, k in enumerate(ok_h) if k]
    fh = list(fh)
    nh = list(nh)

    loc = pd.read_csv(CACHE / "human_located.csv")
    loc[config.ID_COL] = loc[config.ID_COL].astype(str)
    loc = loc.set_index(config.ID_COL).reindex(ids_h).reset_index()
    shape = _build_block(i_shape, loc, "i_shape_human.csv")
    mech = _build_block(d_mechanics, loc, "d_mechanics_human.csv")
    fold = _build_block(c_folding, loc, "c_folding_human.csv")

    Xh_s, nh_s, fh_s = _attach(Xh, nh, fh, shape, ids_h, "i_shape")
    Xh_m, nh_m, fh_m = _attach(Xh, nh, fh, mech, ids_h, "d_mechanics")
    Xh_f, nh_f, fh_f = _attach(Xh, nh, fh, fold, ids_h, "c_folding")
    Xh_all, nh_all, fh_all = _attach(Xh_s, nh_s, fh_s, mech, ids_h, "d_mechanics")
    Xh_all, nh_all, fh_all = _attach(Xh_all, nh_all, fh_all, fold, ids_h, "c_folding")

    Xe, ye, ne, fe, ids_e = _ecoli_bundle(["i_shape", "d_mechanics", "c_folding"])
    ok_e = np.isfinite(ye)
    Xe, ye = Xe[ok_e], ye[ok_e]

    def subset(names, fam, want):
        if want == "base":
            return [n for n, f in zip(names, fam) if f == "base"]
        if want == "a_flank":
            return [n for n, f in zip(names, fam) if f == "a_flank"]
        if want == "base+a_flank":
            return [n for n, f in zip(names, fam) if f in ("base", "a_flank")]
        if want == "base+a_flank+shape":
            return [n for n, f in zip(names, fam) if f in ("base", "a_flank", "i_shape")]
        if want == "base+a_flank+mech":
            return [n for n, f in zip(names, fam) if f in ("base", "a_flank", "d_mechanics")]
        if want == "base+a_flank+fold":
            return [n for n, f in zip(names, fam) if f in ("base", "a_flank", "c_folding")]
        if want == "all":
            return list(names)
        raise ValueError(want)

    human_sets = {
        "base": (Xh, nh, fh),
        "a_flank": (Xh, nh, fh),
        "base+a_flank": (Xh, nh, fh),
        "base+a_flank+shape": (Xh_s, nh_s, fh_s),
        "base+a_flank+mech": (Xh_m, nh_m, fh_m),
        "base+a_flank+fold": (Xh_f, nh_f, fh_f),
        "all": (Xh_all, nh_all, fh_all),
    }

    rows = []
    for arm in human_sets:
        Xh_arm, nh_arm, fh_arm = human_sets[arm]
        ne_s = subset(ne, fe, arm)
        nh_s = subset(nh_arm, fh_arm, arm)
        Ae, Ah, shared = _align(
            Xe, ne, Xh_arm, nh_arm,
        )
        # restrict to arm columns among shared
        shared_arm = [c for c in shared if c in set(ne_s) and c in set(nh_s)]
        if not shared_arm:
            print(f"  {arm}: no shared cols", flush=True)
            continue
        ia = {c: i for i, c in enumerate(shared)}
        Ae2 = Ae[:, [ia[c] for c in shared_arm]]
        Ah2 = Ah[:, [ia[c] for c in shared_arm]]
        rho_eh = _transfer(Ae2, ye, Ah2, yh)
        rho_he = _transfer(Ah2, yh, Ae2, ye)
        rows.append(dict(
            arm=arm, n_shared=len(shared_arm),
            ecoli_to_human=rho_eh, human_to_ecoli=rho_he,
            n_ecoli=int(len(ye)), n_human=int(len(yh)),
        ))
        print(f"  {arm}: shared={len(shared_arm)} E→H={rho_eh:+.4f} H→E={rho_he:+.4f}", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "human_discovery_transfer.csv", index=False)
    print(df.to_string(index=False), flush=True)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["h1h4", "h2", "h3", "h5", "all"], default="all")
    ap.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    args = ap.parse_args()
    seeds = tuple(args.seeds)
    t0 = time.time()

    if args.only in ("h1h4", "all"):
        run_h1_h4_human(seeds=seeds)
    if args.only in ("h2", "all"):
        run_h2_additivity(seeds=seeds)
    if args.only in ("h3", "all"):
        run_h3_grouped(seeds=seeds)
    if args.only in ("h5", "all"):
        run_h5_transfer()

    summary = {
        "elapsed_sec": time.time() - t0,
        "seeds": list(seeds),
        "outputs": [
            "human_discovery_ladder.csv",
            "human_discovery_additivity.csv",
            "human_discovery_grouped.csv",
            "human_discovery_transfer.csv",
            "DISCOVERY_PLAN.md",
        ],
    }
    (OUT / "human_discovery_summary.json").write_text(json.dumps(summary, indent=2))
    print("DONE", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
