# --- cell 3 (v3) -- paste over cell 3 and re-run -----------------------------
# WHY v3: v2 still scored an untrained model. crisprHAL's train() catches its own
# exception and returns None either way, so a failed fit is indistinguishable
# from a successful one at the call site -- and predict() then happily runs on
# randomly-initialised weights, returning finite, correctly-shaped,
# non-degenerate values. wide_2023 came back as rho 0.0434 in 0.36 min, which is
# an untrained network, not a measurement.
#
# FIX: bypass their wrappers and call Keras directly, which raises. The batch
# fallback then actually triggers. A floor check on rho is kept as a backstop,
# not as the primary defence.
#
# Also: whichever batch the 2,023 nt arm needs, every other width is re-run at
# that SAME batch, so the width curve is read within one optimiser setting.
import os, sys, time
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

HAL_DIR, DATA = "/content/crisprHAL", "/content/crisprhal_widewindow_input.csv.gz"
OUT = "/content/crisprhal_wide_window_results.csv"
MODEL, HALF, CORE, SEED, FOLD = "WT-SPCAS9", 1000, 23, 41, 1
WIDTHS = [("core_23", 0, 0), ("native_378", 189, 166),
          ("mid_1023", 500, 500), ("wide_2023", 1000, 1000)]

sys.path.insert(0, HAL_DIR)
_cwd = os.getcwd(); os.chdir(HAL_DIR)
try:
    import models as hal_models
    from models import models
    from processing import processing
finally:
    os.chdir(_cwd)
proc = processing()
EPOCHS = hal_models.modelVersionDefaultEpochs[MODEL]

df = pd.read_csv(DATA)
y = df["y"].to_numpy(dtype=float); full = df["seq"].to_numpy()
tr, va = list(KFold(5, shuffle=True, random_state=SEED).split(np.arange(len(y))))[FOLD - 1]
import tensorflow as tf


def fit(name, up, down, batch):
    length = up + CORE + down
    lo, hi = HALF - up, HALF + CORE + down
    seqs = np.array([s[lo:hi] for s in full])
    hal_models.modelVersionInputLength[MODEL][0] = length
    tf.keras.backend.clear_session(); tf.keras.utils.set_random_seed(SEED)
    m = models(MODEL, summary=False)
    if getattr(m, "model", None) is None or m.model.input_shape[1] != length:
        raise RuntimeError(f"{name}: did not build at {length} nt")
    X = proc.onehotencode(seqs[tr]).astype("float32")
    Xv = proc.onehotencode(seqs[va]).astype("float32")
    t0 = time.time()
    # Keras directly, NOT m.train / m.predict -- those swallow the exception.
    m.model.fit(X, y[tr], epochs=EPOCHS, batch_size=batch, verbose=0)
    pred = np.asarray(m.model.predict(Xv, batch_size=batch, verbose=0)).ravel()
    if pred.shape[0] != len(va) or not np.isfinite(pred).all() or np.std(pred) == 0:
        raise RuntimeError(f"{name}: degenerate predictions")
    rho = float(spearmanr(y[va], pred).statistic)
    if rho < 0.30:          # backstop: an untrained net lands near 0
        raise RuntimeError(f"{name}: rho {rho:.4f} implies the fit did not take")
    return dict(arm=name, input_nt=length, batch=batch, fold=FOLD,
                n_train=len(tr), n_test=len(va), spearman=rho,
                r2=float(r2_score(y[va], pred)),
                fit_minutes=round((time.time() - t0) / 60, 2))


def run(name, up, down, batches):
    for b in batches:
        try:
            r = fit(name, up, down, b)
            print(f"  {name:>11} ({r['input_nt']:>4} nt, batch {b:>4}): "
                  f"rho {r['spearman']:.4f}   {r['fit_minutes']:.1f} min", flush=True)
            return r
        except Exception as e:
            print(f"  {name} FAILED at batch {b}: {str(e)[:110]}", flush=True)
    return None


# Step 1: find the largest batch the widest arm can actually train at.
print("== finding a workable batch for 2,023 nt ==", flush=True)
wide = run("wide_2023", 1000, 1000, (256, 64, 16))
if wide is None:
    raise SystemExit("2,023 nt will not train at any batch tried")
B = wide["batch"]
print(f"\n== re-running every width at batch {B} so the curve is comparable ==", flush=True)

rows = [wide]
for name, up, down in WIDTHS[:-1]:
    r = run(name, up, down, (B,))
    if r: rows.append(r)
    pd.DataFrame(rows).to_csv(OUT, index=False)

out = pd.DataFrame(rows).sort_values("input_nt")
print()
print(out[["arm", "input_nt", "batch", "spearman", "fit_minutes"]].to_string(index=False))
print("\nSLICER, same fold 1 split: 0.5473 (20-mer) / 0.6568 (matched) / 0.6944 (full family A)")
