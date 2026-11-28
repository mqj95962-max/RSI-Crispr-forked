#!/usr/bin/env python3
"""H6 confound control (Runjia Part 6 / commit note for Jacky).

Question: does local GC (or the raw coverage-like bigWig mean itself) predict
as well as the accessibility / histone signal — i.e. is the tiny H6 Δρ a
GC/coverage artefact like GapR vs untagged control?

Design:
  * Local GC in the same ±500 nt neighbourhood used for H6 (from the
    upstream/protospacer/downstream sequences already in human_located.csv).
  * Best H6 track signal(s) as the "accessibility" arm.
  * Arms: GC alone, track alone, base+GC, base+track, base+GC+track,
    baseA+GC, baseA+track, baseA+GC+track.
  * Also report corr(track, local GC) and marginal ρ vs y.

Usage:
  python Jacky/human-boundary/scripts/run_h6_gc_coverage_control.py
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
from sgrna.harness.run_ablation import cross_validate  # noqa: E402

OUT = _REPO / "Jacky" / "human-boundary" / "results"
CACHE = config.INTERIM / "human_boundary"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 41
WINDOW = 500

# Tracks that gave the least-null H6 gains (~+0.01 on base).
# Keep the two most informative for the GC confound (high GC corr + best Δρ).
FOCUS = [
    "HeLaS3_H3K27ac",   # strongest corr with local GC among singles
    "panel_dnase_mean", # highest track↔GC corr (ρ≈0.70)
]


def _spearman(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    m = np.isfinite(y) & np.isfinite(p)
    if m.sum() < 3:
        return float("nan")
    r = spearmanr(y[m], p[m]).statistic
    return float(r) if np.isfinite(r) else float("nan")


def _gc_frac(seq: str) -> float:
    s = "".join(ch for ch in str(seq).upper() if ch in "ACGT")
    if not s:
        return float("nan")
    return (s.count("G") + s.count("C")) / len(s)


def _local_gc_pm500(row) -> float:
    """GC of ±WINDOW around protospacer midpoint, from oriented flanks."""
    up = str(row.upstream)
    down = str(row.downstream)
    proto = str(row.protospacer)
    pam = str(row.pam) if pd.notna(row.pam) else ""
    # upstream is 5' of protospacer in guide orientation; take last WINDOW nt
    left = up[-WINDOW:] if len(up) >= WINDOW else up
    # need WINDOW nt on the 3' side of midpoint ≈ half protospacer + PAM + down
    right_budget = WINDOW
    right = (proto + pam + down)[:right_budget]
    return _gc_frac(left + right)


def _cv_rho(X, y, names, fam, tag, experiment, n_features=300):
    res = cross_validate(
        np.asarray(X, np.float32), np.asarray(y, float),
        list(names), np.asarray(fam),
        n_features=n_features, seeds=(SEED,),
        tag=tag, experiment=experiment, verbose=True,
    )
    return float(res["summary"]["spearman"]["mean"])


def main():
    t0 = time.time()
    loc = pd.read_csv(CACHE / "human_located.csv")
    loc[config.ID_COL] = loc[config.ID_COL].astype(str)
    meta = json.loads((CACHE / "meta_human.json").read_text())
    X = np.load(CACHE / "X_human_base_a.npy")
    y = np.asarray(meta["y"], float)
    names = list(meta["full_names"])
    fam = list(meta["family_of"])
    ids = [str(i) for i in meta["ids"]]

    loc = loc.set_index(config.ID_COL).reindex(ids).reset_index()
    ok = np.isfinite(y) & loc["left"].notna() & loc["upstream"].notna()
    X, y = X[ok.to_numpy()], y[ok.to_numpy()]
    loc = loc.loc[ok].reset_index(drop=True)

    base_i = [i for i, f in enumerate(fam) if f == "base"]
    both_i = list(range(len(names)))

    print("  computing local GC ±500 ...", flush=True)
    local_gc = loc.apply(_local_gc_pm500, axis=1).to_numpy(float)
    spacer_gc = np.asarray(meta["spacer_gc"], float)[ok.to_numpy()]

    sig = pd.read_csv(CACHE / "h6_chromatin_signals.csv")
    if len(sig) != len(loc) or list(sig[config.ID_COL].astype(str)) != list(loc[config.ID_COL].astype(str)):
        # rebuild alignment by id
        sig = sig.set_index(config.ID_COL).reindex(loc[config.ID_COL].astype(str)).reset_index()

    # marginals
    marg = [
        dict(feature="local_gc_pm500", n_finite=int(np.isfinite(local_gc).sum()),
             spearman_vs_y=_spearman(y, local_gc), mean=float(np.nanmean(local_gc))),
        dict(feature="spacer_gc", n_finite=int(np.isfinite(spacer_gc).sum()),
             spearman_vs_y=_spearman(y, spacer_gc), mean=float(np.nanmean(spacer_gc))),
    ]
    for c in FOCUS:
        v = sig[c].to_numpy(float)
        marg.append(dict(
            feature=c, n_finite=int(np.isfinite(v).sum()),
            spearman_vs_y=_spearman(y, v),
            spearman_vs_local_gc=_spearman(local_gc, v),
            mean=float(np.nanmean(v)),
        ))
    marg_df = pd.DataFrame(marg)
    marg_df.to_csv(OUT / "human_h6_gc_coverage_marginals.csv", index=False)
    print(marg_df.to_string(index=False), flush=True)

    # Reuse H6 baselines when present (same matrix, seed, folds).
    prev = OUT / "human_h6_chromatin.csv"
    base_rho = baseA_rho = None
    if prev.exists():
        prev_df = pd.read_csv(prev)
        if (prev_df.arm == "base").any():
            base_rho = float(prev_df.loc[prev_df.arm == "base", "spearman"].iloc[0])
        if (prev_df.arm == "baseA").any():
            baseA_rho = float(prev_df.loc[prev_df.arm == "baseA", "spearman"].iloc[0])
        if base_rho is not None and baseA_rho is not None:
            print(f"  reused H6 baselines base={base_rho:.4f} baseA={baseA_rho:.4f}", flush=True)
    if base_rho is None or baseA_rho is None:
        print("  baselines ...", flush=True)
        base_rho = _cv_rho(
            X[:, base_i], y, [names[i] for i in base_i], ["base"] * len(base_i),
            tag="h6ctl_base", experiment="base",
        )
        baseA_rho = _cv_rho(
            X[:, both_i], y, names, fam,
            tag="h6ctl_baseA", experiment="baseA",
        )
        print(f"  base={base_rho:.4f} baseA={baseA_rho:.4f}", flush=True)

    gc_col = local_gc.reshape(-1, 1).astype(np.float32)
    rows = [
        dict(arm="base", track="", spearman=base_rho, delta_vs_base=0.0, delta_vs_baseA=np.nan),
        dict(arm="baseA", track="", spearman=baseA_rho, delta_vs_base=baseA_rho - base_rho, delta_vs_baseA=0.0),
    ]

    # GC-only arms
    for label, cols, nms, fms, Xmat in (
        ("base+local_gc", base_i, [names[i] for i in base_i] + ["local_gc_pm500"],
         ["base"] * len(base_i) + ["gc"], np.hstack([X[:, base_i], gc_col])),
        ("baseA+local_gc", both_i, names + ["local_gc_pm500"],
         fam + ["gc"], np.hstack([X[:, both_i], gc_col])),
        ("local_gc_only", None, ["local_gc_pm500"], ["gc"], gc_col),
    ):
        rho = _cv_rho(Xmat, y, nms, fms, tag=f"h6ctl_{label}", experiment=label,
                      n_features=min(300, Xmat.shape[1]))
        rows.append(dict(
            arm=label, track="local_gc_pm500", spearman=rho,
            delta_vs_base=rho - base_rho, delta_vs_baseA=rho - baseA_rho,
        ))
        print(f"  {label}: {rho:.4f}", flush=True)

    for c in FOCUS:
        v = sig[c].to_numpy(float).reshape(-1, 1).astype(np.float32)
        vg = np.hstack([v, gc_col])
        arms = [
            ("base+track", [names[i] for i in base_i] + [c],
             ["base"] * len(base_i) + ["chromatin"], np.hstack([X[:, base_i], v])),
            ("base+gc+track", [names[i] for i in base_i] + ["local_gc_pm500", c],
             ["base"] * len(base_i) + ["gc", "chromatin"], np.hstack([X[:, base_i], vg])),
            ("baseA+track", names + [c], fam + ["chromatin"], np.hstack([X[:, both_i], v])),
            ("baseA+gc+track", names + ["local_gc_pm500", c], fam + ["gc", "chromatin"],
             np.hstack([X[:, both_i], vg])),
        ]
        for arm, nms, fms, Xmat in arms:
            rho = _cv_rho(
                Xmat, y, nms, fms, tag=f"h6ctl_{arm}_{c}", experiment=f"{arm}:{c}",
                n_features=min(300, Xmat.shape[1]),
            )
            rows.append(dict(
                arm=arm, track=c, spearman=rho,
                delta_vs_base=rho - base_rho, delta_vs_baseA=rho - baseA_rho,
            ))
            print(f"  {arm} / {c}: {rho:.4f} (Δbase {rho-base_rho:+.4f}, "
                  f"ΔA {rho-baseA_rho:+.4f})", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "human_h6_gc_coverage_control.csv", index=False)

    # Compact verdict table: for each track, track vs GC on base
    verdict = []
    base_gc = df[(df.arm == "base+local_gc")].iloc[0].spearman
    for c in FOCUS:
        tr = df[(df.arm == "base+track") & (df.track == c)]
        both = df[(df.arm == "base+gc+track") & (df.track == c)]
        a_tr = df[(df.arm == "baseA+track") & (df.track == c)]
        if tr.empty:
            continue
        verdict.append(dict(
            track=c,
            base=base_rho,
            base_plus_gc=base_gc,
            base_plus_track=float(tr.iloc[0].spearman),
            base_plus_gc_track=float(both.iloc[0].spearman) if len(both) else np.nan,
            track_delta_vs_gc=float(tr.iloc[0].spearman) - base_gc,
            baseA_plus_track_delta=float(a_tr.iloc[0].spearman) - baseA_rho if len(a_tr) else np.nan,
            track_vs_local_gc=float(
                marg_df.loc[marg_df.feature == c, "spearman_vs_local_gc"].iloc[0]
            ),
        ))
    verd = pd.DataFrame(verdict)
    verd.to_csv(OUT / "human_h6_gc_coverage_verdict.csv", index=False)

    manifest = {
        "window_nt": WINDOW,
        "n_guides": int(len(y)),
        "focus_tracks": FOCUS,
        "base_rho": base_rho,
        "baseA_rho": baseA_rho,
        "base_plus_local_gc": float(base_gc),
        "elapsed_sec": time.time() - t0,
        "reading": (
            "If track_delta_vs_gc ≈ 0 and track correlates with local GC, the H6 "
            "signal is GC/coverage-like (GapR analogue). If track beats GC and "
            "survives given GC, accessibility is doing real work."
        ),
    }
    (OUT / "human_h6_gc_coverage_summary.json").write_text(json.dumps(manifest, indent=2))
    print(verd.to_string(index=False), flush=True)
    print("DONE", json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
