# ============================================================================
# crisprHAL 2 sample-complexity curve, folds 2-5  --  run this in Google Colab
#
# Why this exists: our curve was measured on fold 1 only, which makes "needs
# half the labelled guides" a statement about one test set. This reruns their
# model on the remaining folds so the claim survives the choice of test set.
#
# Runtime: GPU (Runtime -> Change runtime type -> T4 GPU). ~15-25 min total on
# a T4, against ~3.5 h on CPU.
#
# Before running, upload expanded_meta.json when the first cell asks for it.
# ============================================================================

# --- cell 1: dependencies and their code -----------------------------------
# !pip -q install tensorflow==2.17.0
# !git clone -q https://github.com/tbrowne5/crisprHAL.git /content/crisprHAL

# --- cell 2: upload expanded_meta.json --------------------------------------
# from google.colab import files
# files.upload()        # choose expanded_meta.json

# --- cell 3: the run --------------------------------------------------------
import json, os, sys, time
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

HAL_DIR = "/content/crisprHAL"
META = "/content/expanded_meta.json"
OUT = "/content/sample_complexity_crisprhal_folds.csv"

MODEL = "WT-SPCAS9"
UP = 189                      # protospacer starts here in their 378 nt context
SIZES = (4000, 8000, 13880, 20000, 26853)
FOLDS = (2, 3, 4, 5)          # fold 1 already measured locally
SEEDS = (41,)

sys.path.insert(0, HAL_DIR)
_cwd = os.getcwd()
os.chdir(HAL_DIR)             # their module paths are repo-relative
try:
    from models import models, modelVersionDefaultEpochs
    from processing import processing
finally:
    os.chdir(_cwd)
proc = processing()
default_epochs = modelVersionDefaultEpochs[MODEL]


def _read(split):
    d = pd.read_csv(f"{HAL_DIR}/data/WT-SpCas9_{split}ing_data.csv",
                    header=None, names=["seq", "y"])
    d["protospacer"] = d["seq"].str[UP:UP + 20]
    return d


def _fixed_split(n, seed=41, fold=1):
    """Identical construction to the local harness: fold `fold` of KFold(5)."""
    return list(KFold(5, shuffle=True, random_state=seed).split(np.arange(n)))[fold - 1]


def _nested_subsets(train_idx, sizes, seed):
    """Shuffle once, take prefixes, so each subset contains the smaller ones."""
    order = np.random.default_rng(seed).permutation(train_idx)
    return {s: order[:s] for s in sizes if s <= len(order)}


meta = json.loads(open(META).read())
protos = np.asarray(meta["protospacers"])
y = np.asarray(meta["y"], dtype=float)
hal = pd.concat([_read("train"), _read("test")]).drop_duplicates("protospacer")
seqs = hal.set_index("protospacer")["seq"].reindex(protos)
assert not seqs.isna().any(), f"{int(seqs.isna().sum())} guides lack crisprHAL context"
seqs = seqs.to_numpy()
print(f"{len(seqs):,} guides aligned, {default_epochs} epochs per fit")

import tensorflow as tf
rows = []
for fold in FOLDS:
    tr_all, va = _fixed_split(len(y), fold=fold)
    X_va = proc.onehotencode(seqs[va])
    for seed in SEEDS:
        for n, idx in _nested_subsets(tr_all, SIZES, seed).items():
            tf.keras.backend.clear_session()
            tf.keras.utils.set_random_seed(seed)
            t0 = time.time()
            m = models(MODEL, summary=False)
            m.train(proc.onehotencode(seqs[idx]), y[idx],
                    epochs=default_epochs, batch_size=1024, verbose=0)
            pred = np.asarray(m.predict(X_va, verbose=0)).ravel()
            rows.append(dict(model="crisprHAL 2", seed=seed, fold=fold,
                             n_train=int(n), n_test=int(len(va)),
                             spearman=float(spearmanr(y[va], pred).statistic),
                             r2=float(r2_score(y[va], pred)),
                             fit_seconds=round(time.time() - t0, 1)))
            pd.DataFrame(rows).to_csv(OUT, index=False)
            print(f"  fold {fold} n={n:6d} seed {seed}: rho "
                  f"{rows[-1]['spearman']:.4f}  ({rows[-1]['fit_seconds']/60:.1f} min)",
                  flush=True)

print(pd.DataFrame(rows).pivot_table(index="n_train", columns="fold",
                                     values="spearman").round(4).to_string())

# --- cell 4: download -------------------------------------------------------
# from google.colab import files
# files.download(OUT)
