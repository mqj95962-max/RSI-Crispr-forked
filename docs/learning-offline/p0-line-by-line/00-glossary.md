# Words you need before reading code (no prior background assumed)

Read this once. Every P0 guide assumes these meanings.

## What a computer program is doing here

A **program** is a recipe of instructions. Python reads it **top to bottom**.
A **line** is one instruction (sometimes continued with indentation under a header).

| Idea | Plain English |
|---|---|
| **Variable** | A sticky note with a name that holds a value (`x = 3` puts 3 on the note named `x`) |
| **Function** | A reusable mini-recipe (`def cook(...):`). Calling `cook(a)` runs that recipe with input `a` |
| **Import** | “Bring in a toolbox someone else already wrote” (`import pandas as pd`) |
| **List / array** | An ordered row of values: `[1, 2, 3]` |
| **Dictionary** | A lookup table of name→value pairs: `{"seed": 41}` |
| **DataFrame** | A spreadsheet in memory (rows × named columns), from the `pandas` toolbox |
| **NumPy array** | A grid of numbers optimised for maths (often written `X` for features, `y` for the answer) |
| **NaN** | “Not a Number” — a blank / missing cell |
| **CSV** | A plain-text spreadsheet file (comma-separated values) |
| **Path / folder** | Where a file lives on disk |

## Biology words used in this project

| Word | Meaning here |
|---|---|
| **sgRNA / guide** | A short RNA that tells Cas9 where to cut DNA |
| **Protospacer / 20-mer** | The 20 DNA letters the guide matches |
| **PAM (NGG)** | A 3-letter DNA tag Cas9 needs next to the target (`N` = any base, then `GG`) |
| **cut.score** | The lab’s measured cutting efficiency for that guide (the number we try to predict) |
| **Flank / upstream / downstream** | DNA to the left/right of the target on the chromosome |
| **QCT** | “Quantum chemical tensor” numbers describing local DNA chemistry (from the published paper’s columns) |

## Machine-learning words used in this project

| Word | Meaning here |
|---|---|
| **Feature** | One measurable input column (e.g. “GC content of the flank”) |
| **Label / target** | The answer we want to predict (`cut.score`) |
| **Train / validation** | “Study questions” vs “exam questions” the model must not have memorised |
| **Cross-validation (CV)** | Repeat the exam with different study/exam splits and average the scores |
| **Fold** | One of those splits (5-fold = 5 exams) |
| **Seed** | A fixed random-number starter so shuffling is repeatable |
| **Imputation** | Filling blank cells with a guess (here: the **median** of that column on the *training* rows only) |
| **Feature selection** | Picking the top 300 most useful columns before the final model |
| **XGBoost** | A popular “forest of decision trees” learning method |
| **Selector vs champion** | Throwaway model that *ranks* columns vs the real model that *predicts* |
| **Spearman ρ** | How well the *ranking* of predictions matches the ranking of true scores (−1 to +1; higher is better) |
| **R²** | How much of the numeric variance is explained (1 = perfect, 0 = useless) |
| **Pearson** | Linear correlation between predicted and true scores |
| **Leakage** | Accidentally letting exam answers influence studying — makes scores look fake-good |

## The golden rule of this whole repo

> Validation (exam) rows must **never** influence filling blanks, ranking features, or fitting the model.

If you remember only one sentence, remember that.
