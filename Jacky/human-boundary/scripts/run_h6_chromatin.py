#!/usr/bin/env python3
"""H6 — cell-type–matched chromatin on the human cutting matrix.

Noshay's human matrix mixes Doench A375 with a curated multi-line pool
(HCT116 / HEK293T / HeLa / HL60). We lack per-guide cell-line labels, so this
samples ENCODE signal at each located locus for several of those lines and asks
whether any track (or a panel mean/max) raises ρ over base / base+Family A.

Tracks live under Runjia/data/reference/chromatin/h6/ (not versioned).
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
from sgrna.run_ablation import cross_validate  # noqa: E402

OUT = _REPO / "Jacky" / "human-boundary" / "results"
CACHE = config.INTERIM / "human_boundary"
TRACK_DIR = config.REFERENCE / "chromatin" / "h6"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 41
WINDOW = 500

# label -> (filename, encode_file, cell, assay)
TRACKS = {
    "HCT116_ATAC": ("HCT116_ATAC.bigWig", "ENCFF153PRF", "HCT116", "ATAC"),
    "HCT116_DNase": ("HCT116_DNase.bigWig", "ENCFF251RIU", "HCT116", "DNase"),
    "HCT116_H3K27ac": ("HCT116_H3K27ac.bigWig", "ENCFF585BWA", "HCT116", "H3K27ac"),
    "HEK293T_DNase": ("HEK293T_DNase.bigWig", "ENCFF148BGE", "HEK293T", "DNase"),
    "HeLaS3_DNase": ("HeLaS3_DNase.bigWig", "ENCFF830FDL", "HeLa-S3", "DNase"),
    "HeLaS3_H3K27ac": ("HeLaS3_H3K27ac.bigWig", "ENCFF010QGR", "HeLa-S3", "H3K27ac"),
    "HL60_DNase": ("HL60_DNase.bigWig", "ENCFF634ZUJ", "HL-60", "DNase"),
}


def _spearman(y, p):
    y = np.asarray(y, float)
    p = np.asarray(p, float)
    m = np.isfinite(y) & np.isfinite(p)
    if m.sum() < 3:
        return float("nan")
    r = spearmanr(y[m], p[m]).statistic
    return float(r) if np.isfinite(r) else float("nan")


def _sample_track(path: Path, loc: pd.DataFrame) -> np.ndarray:
    import pyBigWig
    bw = pyBigWig.open(str(path))
    chroms = set(bw.chroms().keys())
    vals = np.full(len(loc), np.nan, dtype=np.float64)
    try:
        for i, r in enumerate(loc.itertuples(index=False)):
            chrom = str(r.chrom)
            c = chrom if chrom in chroms else (
                "chr" + chrom if ("chr" + chrom) in chroms else chrom.replace("chr", "")
            )
            if c not in chroms:
                continue
            mid = int((int(r.left) + int(r.right)) // 2)
            lo, hi = max(0, mid - WINDOW), mid + WINDOW
            hi = min(hi, int(bw.chroms()[c]))
            if hi <= lo:
                continue
            arr = bw.values(c, lo, hi, numpy=True)
            arr = np.asarray(arr, float)
            arr = arr[np.isfinite(arr)]
            if len(arr):
                vals[i] = float(np.mean(arr))
    finally:
        bw.close()
    return vals


def _load_human():
    meta = json.loads((CACHE / "meta_human.json").read_text())
    X = np.load(CACHE / "X_human_base_a.npy")
    y = np.asarray(meta["y"], float)
    names = list(meta["full_names"])
    fam = list(meta["family_of"])
    ids = [str(i) for i in meta["ids"]]
    return X, y, names, fam, ids


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

    X, y, names, fam, ids = _load_human()
    # align loc to matrix order
    loc = loc.set_index(config.ID_COL).reindex(ids).reset_index()
    ok = np.isfinite(y) & loc["left"].notna()
    X, y = X[ok.to_numpy()], y[ok.to_numpy()]
    loc = loc.loc[ok].reset_index(drop=True)
    fam = list(fam)
    names = list(names)
    base_i = [i for i, f in enumerate(fam) if f == "base"]
    both_i = list(range(len(names)))

    signal_path = CACHE / "h6_chromatin_signals.csv"
    if signal_path.exists():
        print(f"  cached signals {signal_path}", flush=True)
        sig = pd.read_csv(signal_path)
        # ensure row order matches current loc
        if len(sig) != len(loc) or list(sig[config.ID_COL].astype(str)) != list(loc[config.ID_COL].astype(str)):
            print("  signal cache order mismatch — rebuilding", flush=True)
            sig = None
    else:
        sig = None

    if sig is None:
        rows = {config.ID_COL: loc[config.ID_COL].astype(str)}
        for label, (fname, enc, cell, assay) in TRACKS.items():
            path = TRACK_DIR / fname
            if not path.exists():
                raise SystemExit(f"missing track {path}")
            print(f"  sampling {label} ({path.name}) ...", flush=True)
            t1 = time.time()
            rows[label] = _sample_track(path, loc)
            print(f"    done in {time.time() - t1:.1f}s  finite={np.isfinite(rows[label]).sum()}", flush=True)
        sig = pd.DataFrame(rows)
        # panel features
        dnase_cols = [c for c in TRACKS if TRACKS[c][3] == "DNase"]
        all_cols = list(TRACKS)
        sig["panel_dnase_mean"] = sig[dnase_cols].mean(axis=1, skipna=True)
        sig["panel_dnase_max"] = sig[dnase_cols].max(axis=1, skipna=True)
        sig["panel_all_mean"] = sig[all_cols].mean(axis=1, skipna=True)
        sig["panel_all_max"] = sig[all_cols].max(axis=1, skipna=True)
        sig.to_csv(signal_path, index=False)

    feature_cols = list(TRACKS) + [
        "panel_dnase_mean", "panel_dnase_max", "panel_all_mean", "panel_all_max",
    ]

    # marginal associations
    marg = []
    for c in feature_cols:
        v = sig[c].to_numpy(float)
        marg.append(dict(
            feature=c, n_finite=int(np.isfinite(v).sum()),
            spearman_vs_y=_spearman(y, v),
            mean=float(np.nanmean(v)),
        ))
    pd.DataFrame(marg).to_csv(OUT / "human_h6_marginals.csv", index=False)
    print(pd.DataFrame(marg).to_string(index=False), flush=True)

    base_rho = _cv_rho(
        X[:, base_i], y, [names[i] for i in base_i], ["base"] * len(base_i),
        tag="h6_base", experiment="base",
    )
    baseA_rho = _cv_rho(
        X[:, both_i], y, names, fam,
        tag="h6_baseA", experiment="baseA",
    )
    print(f"baselines: base={base_rho:.4f} baseA={baseA_rho:.4f}", flush=True)

    rows = [
        dict(arm="base", track="", spearman=base_rho, delta_vs_base=0.0, delta_vs_baseA=np.nan),
        dict(arm="baseA", track="", spearman=baseA_rho, delta_vs_base=baseA_rho - base_rho, delta_vs_baseA=0.0),
    ]

    for c in feature_cols:
        v = sig[c].to_numpy(float).reshape(-1, 1)
        # base + track
        Xb = np.hstack([X[:, base_i], v.astype(np.float32)])
        nb = [names[i] for i in base_i] + [c]
        fb = ["base"] * len(base_i) + ["chromatin"]
        rho_b = _cv_rho(Xb, y, nb, fb, tag=f"h6_base_{c}", experiment=f"base+{c}")
        rows.append(dict(
            arm="base+track", track=c, spearman=rho_b,
            delta_vs_base=rho_b - base_rho, delta_vs_baseA=np.nan,
        ))
        # baseA + track
        Xa = np.hstack([X[:, both_i], v.astype(np.float32)])
        na = names + [c]
        fa = fam + ["chromatin"]
        rho_a = _cv_rho(Xa, y, na, fa, tag=f"h6_baseA_{c}", experiment=f"baseA+{c}")
        rows.append(dict(
            arm="baseA+track", track=c, spearman=rho_a,
            delta_vs_base=rho_a - base_rho, delta_vs_baseA=rho_a - baseA_rho,
        ))
        print(f"  {c}: base+ {rho_b:.4f} (Δ{rho_b-base_rho:+.4f})  "
              f"baseA+ {rho_a:.4f} (Δ{rho_a-baseA_rho:+.4f})", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "human_h6_chromatin.csv", index=False)

    manifest = {
        "window_nt": WINDOW,
        "n_guides": int(len(y)),
        "tracks": {k: dict(file=v[0], encode=v[1], cell=v[2], assay=v[3]) for k, v in TRACKS.items()},
        "note": (
            "No per-guide cell-line labels in the Noshay matrix; each track is "
            "tested as a locus feature for the whole pool. A375 ENCODE DNase/ATAC "
            "was not available as a released GRCh38 signal in this sweep."
        ),
        "elapsed_sec": time.time() - t0,
        "base_rho": base_rho,
        "baseA_rho": baseA_rho,
    }
    (OUT / "human_h6_summary.json").write_text(json.dumps(manifest, indent=2))
    print(df.to_string(index=False), flush=True)
    print("DONE", json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
