# --- cell 3 (REVISED) -- paste over the previous cell 3 and re-run -----------
# Two changes from the first version:
#   1. HARD FAILURE DETECTION. crisprHAL's train() and predict() catch their own
#      exceptions and print them, so a failed fit returns None and the script
#      happily scores garbage. Every fit is now checked and raises instead.
#   2. BATCH-SIZE FALLBACK. At 2,023 nt the GRU sees 1,012 timesteps, and cuDNN
#      cannot allocate its workspace at their published batch of 1,024 on a T4.
#      Wide arms retry at smaller batches, and the batch actually used is
#      recorded. If a wide arm needs a smaller batch, 378 nt is re-run at the
#      SAME batch so the comparison is not confounded by the optimiser.
import os, sys, time
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

HAL_DIR, DATA = "/content/crisprHAL", "/content/crisprhal_widewindow_input.csv.gz"
OUT = "/content/crisprhal_wide_window_results.csv"
MODEL, HALF, CORE, SEED, FOLD = "WT-SPCAS9", 1000, 23, 41, 1
BATCHES = (1024, 256, 64)          # try in order until cuDNN is happy

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
    """One fit. Raises on any failure instead of scoring a silent None."""
    length = up + CORE + down
    lo, hi = HALF - up, HALF + CORE + down
    seqs = np.array([s[lo:hi] for s in full])
    assert len(seqs[0]) == length
    hal_models.modelVersionInputLength[MODEL][0] = length
    tf.keras.backend.clear_session(); tf.keras.utils.set_random_seed(SEED)
    m = models(MODEL, summary=False)
    if getattr(m, "model", None) is None or m.model.input_shape[1] != length:
        raise RuntimeError(f"{name}: model did not build at {length} nt")
    X = proc.onehotencode(seqs[tr]).astype("float32")
    Xv = proc.onehotencode(seqs[va]).astype("float32")
    t0 = time.time()
    m.train(X, y[tr], epochs=EPOCHS, batch_size=batch, verbose=0)
    pred = m.predict(Xv, batch_size=batch, verbose=0)
    if pred is None:
        raise RuntimeError(f"{name}: train/predict failed at batch {batch}")
    pred = np.asarray(pred).ravel()
    if pred.shape[0] != len(va):
        raise RuntimeError(f"{name}: got {pred.shape[0]} predictions, want {len(va)}")
    if not np.isfinite(pred).all() or np.std(pred) == 0:
        raise RuntimeError(f"{name}: degenerate predictions")
    return dict(arm=name, input_nt=length, up=up, down=down, batch=batch, fold=FOLD,
                n_train=len(tr), n_test=len(va),
                spearman=float(spearmanr(y[va], pred).statistic),
                r2=float(r2_score(y[va], pred)),
                fit_minutes=round((time.time() - t0) / 60, 2))


def run(name, up, down):
    """Try each batch size in turn; report which one worked."""
    for b in BATCHES:
        try:
            r = fit(name, up, down, b)
            print(f"  {name:>11} ({r['input_nt']:>4} nt, batch {b:>4}): "
                  f"rho {r['spearman']:.4f}   {r['fit_minutes']:.1f} min", flush=True)
            return r
        except Exception as e:
            print(f"  {name} failed at batch {b}: {str(e)[:120]}", flush=True)
    raise RuntimeError(f"{name}: no batch size worked")


rows = []
if os.path.exists(OUT):
    rows = pd.read_csv(OUT).to_dict("records")      # keep the 378 nt control

for name, up, down in [("core_23", 0, 0), ("mid_1023", 500, 500), ("wide_2023", 1000, 1000)]:
    rows.append(run(name, up, down))
    pd.DataFrame(rows).to_csv(OUT, index=False)

# If a wide arm needed a smaller batch, re-run 378 nt at that batch so width is
# not confounded with the optimiser.
used = {r["arm"]: r.get("batch", 1024) for r in rows}
if used.get("wide_2023", 1024) != 1024:
    b = used["wide_2023"]
    rows.append(fit("native_378_batch%d" % b, 189, 166, b))
    print(f"  control re-run at batch {b}: rho {rows[-1]['spearman']:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)

print()
print(pd.DataFrame(rows)[["arm", "input_nt", "batch", "spearman", "fit_minutes"]].to_string(index=False))
print("\nSLICER on this split: 0.5440 (20-mer) / 0.6724 (matched) / 0.7072 (full family A)")
