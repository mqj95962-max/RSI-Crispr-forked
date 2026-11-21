# P1 — Teammate baselines, Joshua’s Colab template, and SHAP

**Source files:**  
- `USE THIS!! FINAL_baseline_…` *(you already know — yardstick)*  
- `Joshua/FINAL_baseline_ecoli_sgRNA_model_5seeds.py`  
- `Jacky/FINAL_baseline_model_5seeds.py`  
- `Joshua/XGBoost 300 features` *(extensionless Colab script)*  
- `Joshua/shap_baseline_analysis.py`  

**Job in the project:** see how the **same baseline idea** was copied/adapted by teammates, learn Joshua’s **feature-test template**, and understand how **SHAP** explains saved fold models without retraining.

---

## Where this sits

```text
P0 #1 USE THIS baseline  ──official protocol / CELL 7 numbers──► config.BASELINE
        │
        ├─ Joshua/FINAL_baseline_…     compare: same spirit, watch for drift
        ├─ Jacky/FINAL_baseline_…      your working copy
        │
        ├─ Joshua/XGBoost 300 features ──template for “does this feature set help?”
        │         │
        │         └─ (his other Colab variants = same skeleton, different paste)
        │
        └─ Joshua/shap_baseline_analysis.py
              reads saved fold models + medians + selected indices
              explains validation predictions (does not train a new champion)
```

---

## 1. Three baseline scripts — what to compare

| File | Role |
|---|---|
| `USE THIS!! …` | Canonical leakage-safe 5-seed story; trust CELL 7 |
| `Joshua/FINAL_baseline_…` | Teammate port — read to see shared structure; diff carefully before treating numbers as identical |
| `Jacky/FINAL_baseline_…` | Your copy for local/Colab edits |

**Learning intent (not busywork):** open Joshua’s or Jacky’s next to USE THIS and ask:

- Same `header=1`, train-only impute, selector→300→champion?  
- Same seeds / estimators?  
- Any extra engineered CSV path that would change CELL 7?

If the protocol drifted, Δρ vs “baseline” in a notebook may not match `config.BASELINE`.

---

## 2. `Joshua/XGBoost 300 features` — the Colab **template**

**Why read this one first among Joshua’s Colabs:** his other files (regional QCT, HOMO-LUMO, secondary-structure proxies, …) mostly **swap the feature paste** into the same evaluation skeleton.

**Workflow pattern:**

```text
Load matrix (often with extra engineered columns)
  → leakage-aware split / top-300 style evaluation
  → report whether the new feature set beats the plain base
```

**How it connects to Runjia’s package world:**

| Joshua Colab habit | Package analogue |
|---|---|
| One big script + Drive CSV | `build_features` + `load_dataset` + `run_ablation` |
| Paste new columns into the matrix | `save_block` / `eng.*` families |
| Manual “did Spearman go up?” | `d_spearman` + `floors.py` |

After you understand this template, **skim** other Joshua Colabs for the biology claim; don’t re-learn CV each time.

---

## 3. `shap_baseline_analysis.py` — explain, don’t re-train

**Hard rule in the docstring:** load artifacts from a finished baseline run; **never train** a new model for SHAP.

**Artifact contract (conceptually):**

| Piece | Why SHAP needs it |
|---|---|
| Per-fold saved model | Exact champion that scored that fold |
| Selected feature indices/names | Which 300 inputs the model saw |
| Training medians | Same impute transform as training |
| Feature name order / hashes | Prove you’re explaining the same matrix |

**Pipeline role:** turns “top 300” into **which columns pushed validation predictions** (mean |SHAP|, etc.) for interpretability write-ups — complementary to ablation’s “did the family help?” 

**Preflight:** the script checks the contract before computing anything; missing fold JSON ⇒ fail loudly (good).

---

## Practical reading order

1. Diff `Joshua/FINAL_baseline` headers/settings vs USE THIS (15–20 min)  
2. Read `XGBoost 300 features` as the feature-test template  
3. Skim one other Joshua Colab only for the *feature idea*  
4. Read SHAP script’s docstring + preflight — then you know what baseline runs must save  

---

## Checklist

- [ ] I know USE THIS is the yardstick; copies can drift  
- [ ] I treat Joshua’s Colabs as **one template × many feature pastes**  
- [ ] I know SHAP explains **saved** fold models; it doesn’t replace CELL 7  
- [ ] I know package ablations are the long-term home for feature tests  
