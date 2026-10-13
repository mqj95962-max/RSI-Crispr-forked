# ============================================================================
# Does crisprHAL 2 close the gap when it is given the DNA it currently cannot
# see?  --  run this in Google Colab on a GPU runtime.
#
# WHY. Our headline is SLICER 0.7072 against crisprHAL 0.697 on the same rows,
# label and folds. But the two models do not see the same DNA. crisprHAL reads
# 378 nt (189 up, 166 down); family A reaches +/-1,000 nt. Restricting family A
# to their span already showed their convolutions WIN by 0.025, so our margin
# comes from DNA they never see -- not from a better encoding. The obvious
# question, and the one a reviewer will ask, is what happens when they are
# handed the same reach.
#
# THE 2x2 THIS COMPLETES
#                     20-mer only    +/-175 nt     +/-1,000 nt
#   SLICER               0.5440        0.6724         0.7072
#   crisprHAL 2            ?           0.697            ?
#
# INTERPRETATION, FIXED IN ADVANCE so the result cannot be read after the fact:
#   * If crisprHAL at +/-1,000 nt reaches ~0.707 or better, our contribution is
#     "we identified the feature", and the efficiency claim stands only as
#     "a deep model is not required to exploit it".
#   * If it stays near 0.697, then a tuned CNN cannot use long-range
#     composition even when handed it, which vindicates the inductive-bias
#     argument on THEIR architecture rather than our in-house control.
#   Either way the 378 nt arm must reproduce ~0.697 or the harness is wrong and
#   nothing else here can be trusted.
#
# Runtime: GPU (Runtime -> Change runtime type -> T4). Their GRU is configured
# for cuDNN's fused kernel, so CPU is many times slower.
# ============================================================================

# --- cell 1 ---------------------------------------------------------------
# Colab ships TensorFlow already, so do NOT pin a version -- Colab's Python is
# often too new for older releases and the install will fail. Just check what is
# there. crisprHAL declares no TF requirement; we run it locally on 2.19.1 with
# Keras 3.15.1, and anything from 2.19 up should behave. The 378 nt positive
# control below is what actually certifies the environment: if it reproduces
# ~0.697, the TF version is fine, whatever it says here.
#
# import tensorflow as tf; print("tensorflow", tf.__version__)
# !git clone -q https://github.com/tbrowne5/crisprHAL.git /content/crisprHAL
#
# Only if the import fails outright:
# !pip -q install "tensorflow>=2.19"    (then Runtime -> Restart session)

# --- cell 2: upload crisprhal_widewindow_input.csv.gz ----------------------
# from google.colab import files; files.upload()

# --- cell 3 ---------------------------------------------------------------
import os, sys, time
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

HAL_DIR = "/content/crisprHAL"
DATA = "/content/crisprhal_widewindow_input.csv.gz"
OUT = "/content/crisprhal_wide_window_results.csv"

MODEL = "WT-SPCAS9"
HALF = 1000                 # the exported file is HALF + 23 + HALF
CORE = 23                   # protospacer + PAM
# (up, down) per arm. 189/166 reproduces their released input exactly.
ARMS = [("native_378", 189, 166),     # positive control -- must land near 0.697
        ("wide_2023", 1000, 1000),    # the decisive cell
        ("core_23", 0, 0),            # completes the 2x2
        ("mid_1023", 500, 500)]
FOLDS = (1,)                # start with fold 1; widen once the answer is clear
SEED = 41

sys.path.insert(0, HAL_DIR)
_cwd = os.getcwd(); os.chdir(HAL_DIR)
try:
    import models as hal_models
    from models import models
    from processing import processing
finally:
    os.chdir(_cwd)
proc = processing()
default_epochs = hal_models.modelVersionDefaultEpochs[MODEL]

df = pd.read_csv(DATA)
y = df["y"].to_numpy(dtype=float)
full = df["seq"].to_numpy()
print(f"{len(df):,} guides, {len(full[0])} nt each, {default_epochs} epochs/fit")


def window(up, down):
    """Slice the stored +/-1,000 nt window down to (up, CORE, down)."""
    lo, hi = HALF - up, HALF + CORE + down
    w = np.array([s[lo:hi] for s in full])
    assert len(w[0]) == up + CORE + down
    return w


def folds(n, seed=SEED):
    return list(KFold(5, shuffle=True, random_state=seed).split(np.arange(n)))


import tensorflow as tf
rows = []
for name, up, down in ARMS:
    seqs = window(up, down)
    length = up + CORE + down
    # Their builder takes input_length as a parameter; patch the registry so
    # models(MODEL) constructs at this width instead of the released 378.
    hal_models.modelVersionInputLength[MODEL][0] = length
    for fold in FOLDS:
        tr, va = folds(len(y))[fold - 1]
        tf.keras.backend.clear_session(); tf.keras.utils.set_random_seed(SEED)
        t0 = time.time()
        m = models(MODEL, summary=False)
        # Their __init__ swallows build errors into a print, leaving self.model
        # unset, so check the width actually took before spending a fit on it.
        assert getattr(m, "model", None) is not None, f"build failed at {length} nt"
        assert m.model.input_shape[1] == length, (
            f"built at {m.model.input_shape[1]} nt, expected {length}")
        m.train(proc.onehotencode(seqs[tr]), y[tr],
                epochs=default_epochs, batch_size=1024, verbose=0)
        pred = np.asarray(m.predict(proc.onehotencode(seqs[va]), verbose=0)).ravel()
        rows.append(dict(arm=name, input_nt=length, up=up, down=down, fold=fold,
                         n_train=len(tr), n_test=len(va),
                         spearman=float(spearmanr(y[va], pred).statistic),
                         r2=float(r2_score(y[va], pred)),
                         fit_minutes=round((time.time() - t0) / 60, 2)))
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print(f"  {name:>11} ({length:>4} nt) fold {fold}: rho "
              f"{rows[-1]['spearman']:.4f}   {rows[-1]['fit_minutes']:.1f} min", flush=True)

r = pd.DataFrame(rows)
print()
print(r.pivot_table(index="arm", values="spearman").round(4).to_string())
print("\nreference on the same folds: SLICER 0.5440 (20-mer) / 0.6724 (matched) "
      "/ 0.7072 (full family A); crisprHAL as published 0.697")

# --- cell 4 ---------------------------------------------------------------
# from google.colab import files; files.download(OUT)
