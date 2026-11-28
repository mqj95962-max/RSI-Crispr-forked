# P0 line-by-line: `Runjia/sgrna/features/a_flank.py`
**Why this file matters:** Family A: measure DNA *around* the cut site, not just the 20-letter spacer.
**Length:** 239 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Zoom out from the 20-letter target and measure the surrounding DNA — that’s where the big signal lived.

---
### Lines 1–44
```python
"""Family A -- sequence and quantum descriptors outside the 20 nt protospacer.

Why this one first
------------------
The published matrix stops at the protospacer. Curated re-analysis of this
very screen (Browne et al. 2025, PeerJ) found that widening the input window
raised Spearman by 0.143 -- more than any feature family reported anywhere for
bacterial Cas9 -- with the strongest contribution from roughly the first 11
nucleotides 3' of the PAM, and a broader AT-richness effect extending past
100 nt on both sides. crisprHAL, the strongest bacterial model published,
feeds on 28 nt for the same reason.

What makes this more than one-hot encoding
------------------------------------------
`qct.learn_lookup_tables` recovers the paper's own quantum chemical tensors as
exact k-mer -> value tables (all 4/16/64/256 k-mers are present in the 13,880
guides, so the recovery is complete, not approximate). That means the same
quantum parameterisation Noshay et al. applied to positions 1-20 can be
applied to the PAM, to the nucleotides downstream of it, and to the flanking
DNA -- sequence the original encoding never touched. The claim moves from
"quantum descriptors of the protospacer" to "quantum descriptors of the
target locus", without introducing a single new assumption.

Two changes after the first ablation
------------------------------------
That first pass gave +0.083 R2, of which 62% came from the wide-flank window
summaries -- and those summaries turned out to be **almost exactly flank GC
content** (rho 0.998 between `win.up250.trimer.Hbondenergy.mean` and
`comp.up250.gc`). Averaging a per-position tensor over hundreds of bases
collapses it onto base composition, so emitting all seventeen unit/property
combinations per window was seventeen near-copies of one number.

So: the summary block now carries a small, deliberately spread set of four
tensor series plus explicit composition, and the windows reach **1 kb** rather
than 250 nt, because the effect showed no sign of saturating at the old
boundary. Fewer columns, four times the reach.

Columns
-------
eng.flank.seq.*    one-hot base identity at u10..u1, the PAM's N, d1..d15
eng.flank.qct.*    per-position monomer and dimer tensors at those positions
eng.flank.win.*    mean/sd of four spread tensor series at 50/250/500/1000 nt
eng.flank.comp.*   GC fraction, purine fraction, longest homopolymer run
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 46
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 48
```python
import numpy as np
```
**Plain English:** Load toolbox code: `import numpy as np` — used here for **numerical arrays & maths**.

### Line 49
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 51
```python
from .. import config
```
**Plain English:** Load a project module from this repo: `from .. import config`.

### Line 52
```python
from ..build import qct
```
**Plain English:** Load a project module from this repo: `from ..build import qct`.

### Line 53
```python
from ..io_utils import save_block
```
**Plain English:** Load an external or local module: `from ..io_utils import save_block`.

### Line 55
```python
PREFIX = "eng.flank"
```
**Plain English:** Store a value: the name `PREFIX` now holds the result of `"eng.flank"`. Whenever you later write that name, you mean this value.

### Line 57
```python
# Positions encoded one base at a time. u1 is the nucleotide immediately 5' of
```
**Plain English:** Human-only note (Python ignores it): Positions encoded one base at a time. u1 is the nucleotide immediately 5' of

### Line 58
```python
# protospacer position 1; d1 is the first nucleotide 3' of the NGG PAM.
```
**Plain English:** Human-only note (Python ignores it): protospacer position 1; d1 is the first nucleotide 3' of the NGG PAM.

### Line 59
```python
N_UPSTREAM = config.UPSTREAM_POSITIONS      # 10
```
**Plain English:** Store a value: the name `N_UPSTREAM` now holds the result of `config.UPSTREAM_POSITIONS      # 10`. Whenever you later write that name, you mean this value.

### Line 60
```python
N_DOWNSTREAM = config.DOWNSTREAM_POSITIONS  # 15
```
**Plain English:** Store a value: the name `N_DOWNSTREAM` now holds the result of `config.DOWNSTREAM_POSITIONS  # 15`. Whenever you later write that name, you mean this value.

### Line 62
```python
# Per-position tensors. Restricted to the two shortest molecular units, which
```
**Plain English:** Human-only note (Python ignores it): Per-position tensors. Restricted to the two shortest molecular units, which

### Line 63
```python
# keeps the block manageable; the longer units enter through the summaries.
```
**Plain English:** Human-only note (Python ignores it): keeps the block manageable; the longer units enter through the summaries.

### Line 64
```python
PER_POSITION_UNITS = ("monomer", "dimer")
```
**Plain English:** Store a value: the name `PER_POSITION_UNITS` now holds the result of `("monomer", "dimer")`. Whenever you later write that name, you mean this value.

### Line 66
```python
# Windows (nt) used for the summary statistics, out to 1 kb.
```
**Plain English:** Human-only note (Python ignores it): Windows (nt) used for the summary statistics, out to 1 kb.

### Line 67
```python
SUMMARY_WINDOWS = config.FLANK_WINDOWS
```
**Plain English:** Store a value: the name `SUMMARY_WINDOWS` now holds the result of `config.FLANK_WINDOWS`. Whenever you later write that name, you mean this value.

### Line 69
```python
# Four tensor series chosen to span the descriptor space -- one per molecular
```
**Plain English:** Human-only note (Python ignores it): Four tensor series chosen to span the descriptor space -- one per molecular

### Line 70
```python
# unit, and not all the same physical property. Averaging any of these over a
```
**Plain English:** Human-only note (Python ignores it): unit, and not all the same physical property. Averaging any of these over a

### Line 71
```python
# long window partly collapses onto composition, which is why `comp.*` is
```
**Plain English:** Human-only note (Python ignores it): long window partly collapses onto composition, which is why `comp.*` is

### Line 72
```python
# emitted alongside: it makes the redundancy visible instead of hiding it in
```
**Plain English:** Human-only note (Python ignores it): emitted alongside: it makes the redundancy visible instead of hiding it in

### Line 73
```python
# seventeen correlated columns.
```
**Plain English:** Human-only note (Python ignores it): seventeen correlated columns.

### Line 74
```python
SUMMARY_SERIES = (
```
**Plain English:** Store a value: the name `SUMMARY_SERIES` now holds the result of `(`. Whenever you later write that name, you mean this value.

### Line 75
```python
    ("monomer", "HLgap.eVraw"),
```
**Plain English:** Run this instruction: `("monomer", "HLgap.eVraw"),`.

### Line 76
```python
    ("dimer", "Hbond.stackingraw"),
```
**Plain English:** Run this instruction: `("dimer", "Hbond.stackingraw"),`.

### Line 77
```python
    ("trimer", "Hbond.energyraw"),
```
**Plain English:** Run this instruction: `("trimer", "Hbond.energyraw"),`.

### Line 78
```python
    ("tetramer", "Hbond.stackingraw"),
```
**Plain English:** Run this instruction: `("tetramer", "Hbond.stackingraw"),`.

### Line 79
```python
)
```
**Plain English:** Run this instruction: `)`.

### Line 81
```python
BASES = ("A", "C", "G", "T")
```
**Plain English:** Store a value: the name `BASES` now holds the result of `("A", "C", "G", "T")`. Whenever you later write that name, you mean this value.

### Line 84
```python
def _positions() -> list[str]:
```
**Plain English:** Defines a reusable recipe named `_positions`. Inputs in parentheses: `(none)`. Returns type hint: list[str]. Nothing runs yet until something *calls* `_positions(...)`.

### Line 85
```python
    """Ordered labels of the single-base positions, 5' -> 3'."""
```
**Plain English:** A short documentation string attached to the nearest function/module: Ordered labels of the single-base positions, 5' -> 3'.

### Line 86
```python
    up = [f"u{i}" for i in range(N_UPSTREAM, 0, -1)]
```
**Plain English:** Store a value: the name `up` now holds the result of `[f"u{i}" for i in range(N_UPSTREAM, 0, -1)]`. Whenever you later write that name, you mean this value.

### Line 87
```python
    pam = ["pamN"]  # positions 2 and 3 of an NGG PAM are constant, so skipped
```
**Plain English:** Store a value: the name `pam` now holds the result of `["pamN"]  # positions 2 and 3 of an NGG PAM are constant, so skipped`. Whenever you later write that name, you mean this value.

### Line 88
```python
    down = [f"d{i}" for i in range(1, N_DOWNSTREAM + 1)]
```
**Plain English:** Store a value: the name `down` now holds the result of `[f"d{i}" for i in range(1, N_DOWNSTREAM + 1)]`. Whenever you later write that name, you mean this value.

### Line 89
```python
    return up + pam + down
```
**Plain English:** Finish this function and send back: `up + pam + down`.

### Line 92
```python
def _extended_sequence(row) -> tuple[str, dict[str, int]]:
```
**Plain English:** Defines a reusable recipe named `_extended_sequence`. Inputs in parentheses: `row`. Returns type hint: tuple[str, dict[str, int]]. Nothing runs yet until something *calls* `_extended_sequence(...)`.

### Lines 93–98
```python
    """Concatenate the local context and record where each label sits in it.

    Returned indices are 0-based offsets into the returned string. We keep a
    little extra sequence on both ends so that dimer/trimer/tetramer windows
    starting at the outermost labelled position still have sequence to read.
    """
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 99
```python
    pad = 4
```
**Plain English:** Store a value: the name `pad` now holds the result of `4`. Whenever you later write that name, you mean this value.

### Line 100
```python
    up = str(row["upstream"])
```
**Plain English:** Store a value: the name `up` now holds the result of `str(row["upstream"])`. Whenever you later write that name, you mean this value.

### Line 101
```python
    down = str(row["downstream"])
```
**Plain English:** Store a value: the name `down` now holds the result of `str(row["downstream"])`. Whenever you later write that name, you mean this value.

### Line 102
```python
    proto = str(row["protospacer"])
```
**Plain English:** Store a value: the name `proto` now holds the result of `str(row["protospacer"])`. Whenever you later write that name, you mean this value.

### Line 103
```python
    pam = str(row["pam"])
```
**Plain English:** Store a value: the name `pam` now holds the result of `str(row["pam"])`. Whenever you later write that name, you mean this value.

### Line 105
```python
    left = up[-(N_UPSTREAM + pad):] if len(up) >= N_UPSTREAM + pad else up
```
**Plain English:** Store a value: the name `left` now holds the result of `up[-(N_UPSTREAM + pad):] if len(up) >= N_UPSTREAM + pad else up`. Whenever you later write that name, you mean this value.

### Line 106
```python
    right = down[: N_DOWNSTREAM + pad]
```
**Plain English:** Store a value: the name `right` now holds the result of `down[: N_DOWNSTREAM + pad]`. Whenever you later write that name, you mean this value.

### Line 107
```python
    ext = left + proto + pam + right
```
**Plain English:** Store a value: the name `ext` now holds the result of `left + proto + pam + right`. Whenever you later write that name, you mean this value.

### Line 109
```python
    idx: dict[str, int] = {}
```
**Plain English:** Run this instruction: `idx: dict[str, int] = {}`.

### Line 110
```python
    proto_start = len(left)
```
**Plain English:** Store a value: the name `proto_start` now holds the result of `len(left)`. Whenever you later write that name, you mean this value.

### Line 111
```python
    for i in range(N_UPSTREAM, 0, -1):
```
**Plain English:** Loop: repeat the indented block once for each item → `i in range(N_UPSTREAM, 0, -1)`.

### Line 112
```python
        idx[f"u{i}"] = proto_start - i
```
**Plain English:** Run this instruction: `idx[f"u{i}"] = proto_start - i`.

### Line 113
```python
    idx["pamN"] = proto_start + len(proto)
```
**Plain English:** Store a value: the name `idx["pamN"]` now holds the result of `proto_start + len(proto)`. Whenever you later write that name, you mean this value.

### Line 114
```python
    for i in range(1, N_DOWNSTREAM + 1):
```
**Plain English:** Loop: repeat the indented block once for each item → `i in range(1, N_DOWNSTREAM + 1)`.

### Line 115
```python
        idx[f"d{i}"] = proto_start + len(proto) + 3 + (i - 1)
```
**Plain English:** Run this instruction: `idx[f"d{i}"] = proto_start + len(proto) + 3 + (i - 1)`.

### Line 116
```python
    return ext, idx
```
**Plain English:** Finish this function and send back: `ext, idx`.

### Line 119
```python
def _longest_run(seq: str) -> int:
```
**Plain English:** Defines a reusable recipe named `_longest_run`. Inputs in parentheses: `seq: str`. Returns type hint: int. Nothing runs yet until something *calls* `_longest_run(...)`.

### Line 120
```python
    best = run = 0
```
**Plain English:** Store a value: the name `best` now holds the result of `run = 0`. Whenever you later write that name, you mean this value.

### Line 121
```python
    prev = ""
```
**Plain English:** Store a value: the name `prev` now holds the result of `""`. Whenever you later write that name, you mean this value.

### Line 122
```python
    for ch in seq:
```
**Plain English:** Loop: repeat the indented block once for each item → `ch in seq`.

### Line 123
```python
        run = run + 1 if ch == prev else 1
```
**Plain English:** Store a value: the name `run` now holds the result of `run + 1 if ch == prev else 1`. Whenever you later write that name, you mean this value.

### Line 124
```python
        prev = ch
```
**Plain English:** Store a value: the name `prev` now holds the result of `ch`. Whenever you later write that name, you mean this value.

### Line 125
```python
        best = max(best, run)
```
**Plain English:** Store a value: the name `best` now holds the result of `max(best, run)`. Whenever you later write that name, you mean this value.

### Line 126
```python
    return best
```
**Plain English:** Finish this function and send back: `best`.

### Line 129
```python
def _composition(seq: str, prefix: str) -> dict[str, float]:
```
**Plain English:** Defines a reusable recipe named `_composition`. Inputs in parentheses: `seq: str, prefix: str`. Returns type hint: dict[str, float]. Nothing runs yet until something *calls* `_composition(...)`.

### Line 130
```python
    if not seq:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not seq`.

### Line 131
```python
        return {f"{prefix}.{k}": np.nan for k in ("gc", "purine", "maxrun")}
```
**Plain English:** Finish this function and send back: `{f"{prefix}.{k}": np.nan for k in ("gc", "purine", "maxrun")}`.

### Line 132
```python
    n = len(seq)
```
**Plain English:** Store a value: the name `n` now holds the result of `len(seq)`. Whenever you later write that name, you mean this value.

### Line 133
```python
    gc = sum(seq.count(b) for b in "GC") / n
```
**Plain English:** Store a value: the name `gc` now holds the result of `sum(seq.count(b) for b in "GC") / n`. Whenever you later write that name, you mean this value.

### Line 134
```python
    pur = sum(seq.count(b) for b in "AG") / n
```
**Plain English:** Store a value: the name `pur` now holds the result of `sum(seq.count(b) for b in "AG") / n`. Whenever you later write that name, you mean this value.

### Line 135
```python
    return {
```
**Plain English:** Finish this function and send back: `{`.

### Line 136
```python
        f"{prefix}.gc": gc,
```
**Plain English:** Run this instruction: `f"{prefix}.gc": gc,`.

### Line 137
```python
        f"{prefix}.purine": pur,
```
**Plain English:** Run this instruction: `f"{prefix}.purine": pur,`.

### Line 138
```python
        f"{prefix}.maxrun": _longest_run(seq) / n,
```
**Plain English:** Run this instruction: `f"{prefix}.maxrun": _longest_run(seq) / n,`.

### Line 139
```python
    }
```
**Plain English:** Run this instruction: `}`.

### Line 142
```python
def _summarise_window(values: np.ndarray, key: str) -> dict[str, float]:
```
**Plain English:** Defines a reusable recipe named `_summarise_window`. Inputs in parentheses: `values: np.ndarray, key: str`. Returns type hint: dict[str, float]. Nothing runs yet until something *calls* `_summarise_window(...)`.

### Line 143
```python
    if values.size == 0 or np.all(np.isnan(values)):
```
**Plain English:** Decision: run the indented block only when this condition is true → `values.size == 0 or np.all(np.isnan(values))`.

### Line 144
```python
        return {f"{key}.mean": np.nan, f"{key}.sd": np.nan}
```
**Plain English:** Finish this function and send back: `{f"{key}.mean": np.nan, f"{key}.sd": np.nan}`.

### Line 145
```python
    return {
```
**Plain English:** Finish this function and send back: `{`.

### Line 146
```python
        f"{key}.mean": float(np.nanmean(values)),
```
**Plain English:** Run this instruction: `f"{key}.mean": float(np.nanmean(values)),`.

### Line 147
```python
        f"{key}.sd": float(np.nanstd(values)),
```
**Plain English:** Run this instruction: `f"{key}.sd": float(np.nanstd(values)),`.

### Line 148
```python
    }
```
**Plain English:** Run this instruction: `}`.

### Line 151
```python
def build(index: pd.DataFrame, tables: dict | None = None) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `build`. Inputs in parentheses: `index: pd.DataFrame, tables: dict | None = None`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `build(...)`.

### Line 152
```python
    tables = tables or qct.load_tables()
```
**Plain English:** Store a value: the name `tables` now holds the result of `tables or qct.load_tables()`. Whenever you later write that name, you mean this value.

### Line 153
```python
    labels = _positions()
```
**Plain English:** Store a value: the name `labels` now holds the result of `_positions()`. Whenever you later write that name, you mean this value.

### Line 154
```python
    widest = max(SUMMARY_WINDOWS)
```
**Plain English:** Efficiency trick: compute chemistry profiles once on the widest 1 kb, then slice for 50/250/500/1000 windows instead of recomputing.

### Line 156
```python
    per_pos_pairs = [
```
**Plain English:** Store a value: the name `per_pos_pairs` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 157
```python
        (unit, prop)
```
**Plain English:** Run this instruction: `(unit, prop)`.

### Line 158
```python
        for unit, props in tables.items()
```
**Plain English:** Loop: repeat the indented block once for each item → `unit, props in tables.items()`.

### Line 159
```python
        for prop in props
```
**Plain English:** Loop: repeat the indented block once for each item → `prop in props`.

### Line 160
```python
        if unit in PER_POSITION_UNITS
```
**Plain English:** Decision: run the indented block only when this condition is true → `unit in PER_POSITION_UNITS`.

### Line 161
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 163
```python
    rows = []
```
**Plain English:** Store a value: the name `rows` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 164
```python
    for _, row in index.iterrows():
```
**Plain English:** Loop: repeat the indented block once for each item → `_, row in index.iterrows()`.

### Line 165
```python
        rec: dict[str, float] = {config.ID_COL: row[config.ID_COL]}
```
**Plain English:** Run this instruction: `rec: dict[str, float] = {config.ID_COL: row[config.ID_COL]}`.

### Line 167
```python
        if not isinstance(row.get("protospacer"), str) or not row.get("located", False):
```
**Plain English:** Decision: run the indented block only when this condition is true → `not isinstance(row.get("protospacer"), str) or not row.get("located", False)`.

### Line 168
```python
            rows.append(rec)  # everything stays NaN; imputed downstream
```
**Plain English:** Run this instruction: `rows.append(rec)  # everything stays NaN; imputed downstream`.

### Line 169
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 171
```python
        ext, idx = _extended_sequence(row)
```
**Plain English:** Run this instruction: `ext, idx = _extended_sequence(row)`.

### Line 173
```python
        # ---- one-hot base identity -------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---- one-hot base identity -------------------------------------

### Line 174
```python
        for label in labels:
```
**Plain English:** Loop: repeat the indented block once for each item → `label in labels`.

### Line 175
```python
            pos = idx[label]
```
**Plain English:** Store a value: the name `pos` now holds the result of `idx[label]`. Whenever you later write that name, you mean this value.

### Line 176
```python
            base = ext[pos] if 0 <= pos < len(ext) else "N"
```
**Plain English:** Store a value: the name `base` now holds the result of `ext[pos] if 0 <= pos < len(ext) else "N"`. Whenever you later write that name, you mean this value.

### Line 177
```python
            for b in BASES:
```
**Plain English:** Loop: repeat the indented block once for each item → `b in BASES`.

### Line 178
```python
                rec[f"{PREFIX}.seq.{label}.{b}"] = int(base == b)
```
**Plain English:** One-hot base identity: four columns per position (A/C/G/T), exactly one is 1.

### Line 180
```python
        # ---- per-position quantum tensors ------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---- per-position quantum tensors ------------------------------

### Line 181
```python
        for unit, prop in per_pos_pairs:
```
**Plain English:** Loop: repeat the indented block once for each item → `unit, prop in per_pos_pairs`.

### Line 182
```python
            span = qct.UNIT_SPAN[unit]
```
**Plain English:** Store a value: the name `span` now holds the result of `qct.UNIT_SPAN[unit]`. Whenever you later write that name, you mean this value.

### Line 183
```python
            table = tables[unit][prop]
```
**Plain English:** Store a value: the name `table` now holds the result of `tables[unit][prop]`. Whenever you later write that name, you mean this value.

### Line 184
```python
            short = prop.replace(".", "").replace("raw", "")
```
**Plain English:** Store a value: the name `short` now holds the result of `prop.replace(".", "").replace("raw", "")`. Whenever you later write that name, you mean this value.

### Line 185
```python
            for label in labels:
```
**Plain English:** Loop: repeat the indented block once for each item → `label in labels`.

### Line 186
```python
                pos = idx[label]
```
**Plain English:** Store a value: the name `pos` now holds the result of `idx[label]`. Whenever you later write that name, you mean this value.

### Line 187
```python
                kmer = ext[pos : pos + span]
```
**Plain English:** Store a value: the name `kmer` now holds the result of `ext[pos : pos + span]`. Whenever you later write that name, you mean this value.

### Line 188
```python
                rec[f"{PREFIX}.qct.{unit}.{short}.{label}"] = (
```
**Plain English:** Run this instruction: `rec[f"{PREFIX}.qct.{unit}.{short}.{label}"] = (`.

### Line 189
```python
                    table.get(kmer, np.nan) if len(kmer) == span else np.nan
```
**Plain English:** Run this instruction: `table.get(kmer, np.nan) if len(kmer) == span else np.nan`.

### Line 190
```python
                )
```
**Plain English:** Run this instruction: `)`.

### Line 192
```python
        # ---- window summaries over the wider flanks --------------------
```
**Plain English:** Human-only note (Python ignores it): ---- window summaries over the wider flanks --------------------

### Line 193
```python
        #
```
**Plain English:** Empty comment line — ignored by Python; just spacing for humans.

### Line 194
```python
        # The windows are nested, so each tensor profile is computed once over
```
**Plain English:** Human-only note (Python ignores it): The windows are nested, so each tensor profile is computed once over

### Line 195
```python
        # the widest segment and then sliced. Recomputing it per window would
```
**Plain English:** Human-only note (Python ignores it): the widest segment and then sliced. Recomputing it per window would

### Line 196
```python
        # quadruple the cost of the whole family for no new information.
```
**Plain English:** Human-only note (Python ignores it): quadruple the cost of the whole family for no new information.

### Line 197
```python
        up_full = str(row["upstream"])[-widest:]
```
**Plain English:** Efficiency trick: compute chemistry profiles once on the widest 1 kb, then slice for 50/250/500/1000 windows instead of recomputing.

### Line 198
```python
        down_full = str(row["downstream"])[:widest]
```
**Plain English:** Efficiency trick: compute chemistry profiles once on the widest 1 kb, then slice for 50/250/500/1000 windows instead of recomputing.

### Line 200
```python
        for side, seg in (("up", up_full), ("dn", down_full)):
```
**Plain English:** Loop: repeat the indented block once for each item → `side, seg in (("up", up_full), ("dn", down_full))`.

### Line 201
```python
            profiles = {
```
**Plain English:** Store a value: the name `profiles` now holds the result of `{`. Whenever you later write that name, you mean this value.

### Line 202
```python
                (unit, prop): qct.profile(seg, unit, prop, tables)
```
**Plain English:** Run this instruction: `(unit, prop): qct.profile(seg, unit, prop, tables)`.

### Line 203
```python
                for unit, prop in SUMMARY_SERIES
```
**Plain English:** Loop: repeat the indented block once for each item → `unit, prop in SUMMARY_SERIES`.

### Line 204
```python
            }
```
**Plain English:** Run this instruction: `}`.

### Line 205
```python
            for w in SUMMARY_WINDOWS:
```
**Plain English:** Loop: repeat the indented block once for each item → `w in SUMMARY_WINDOWS`.

### Line 206
```python
                sub = seg[-w:] if side == "up" else seg[:w]
```
**Plain English:** Store a value: the name `sub` now holds the result of `seg[-w:] if side == "up" else seg[:w]`. Whenever you later write that name, you mean this value.

### Line 207
```python
                rec.update(_composition(sub, f"{PREFIX}.comp.{side}{w}"))
```
**Plain English:** Run this instruction: `rec.update(_composition(sub, f"{PREFIX}.comp.{side}{w}"))`.

### Line 208
```python
                for (unit, prop), prof in profiles.items():
```
**Plain English:** Loop: repeat the indented block once for each item → `(unit, prop), prof in profiles.items()`.

### Line 209
```python
                    short = prop.replace(".", "").replace("raw", "")
```
**Plain English:** Store a value: the name `short` now holds the result of `prop.replace(".", "").replace("raw", "")`. Whenever you later write that name, you mean this value.

### Line 210
```python
                    # upstream windows are suffixes of the segment, downstream
```
**Plain English:** Human-only note (Python ignores it): upstream windows are suffixes of the segment, downstream

### Line 211
```python
                    # windows are prefixes -- slice the profile the same way
```
**Plain English:** Human-only note (Python ignores it): windows are prefixes -- slice the profile the same way

### Line 212
```python
                    part = prof[-w:] if side == "up" else prof[:w]
```
**Plain English:** Store a value: the name `part` now holds the result of `prof[-w:] if side == "up" else prof[:w]`. Whenever you later write that name, you mean this value.

### Line 213
```python
                    rec.update(
```
**Plain English:** Run this instruction: `rec.update(`.

### Line 214
```python
                        _summarise_window(
```
**Plain English:** Run this instruction: `_summarise_window(`.

### Line 215
```python
                            part, f"{PREFIX}.win.{side}{w}.{unit}.{short}"
```
**Plain English:** Run this instruction: `part, f"{PREFIX}.win.{side}{w}.{unit}.{short}"`.

### Line 216
```python
                        )
```
**Plain English:** Run this instruction: `)`.

### Line 217
```python
                    )
```
**Plain English:** Run this instruction: `)`.

### Line 218
```python
        rows.append(rec)
```
**Plain English:** Run this instruction: `rows.append(rec)`.

### Line 220
```python
    return pd.DataFrame(rows)
```
**Plain English:** Finish this function and send back: `pd.DataFrame(rows)`.

### Line 223
```python
def main() -> None:
```
**Plain English:** Defines a reusable recipe named `main`. Inputs in parentheses: `(none)`. Returns type hint: None. Nothing runs yet until something *calls* `main(...)`.

### Line 224
```python
    from ..io_utils import load_guide_index
```
**Plain English:** Load an external or local module: `from ..io_utils import load_guide_index`.

### Line 226
```python
    idx = load_guide_index()
```
**Plain English:** Store a value: the name `idx` now holds the result of `load_guide_index()`. Whenever you later write that name, you mean this value.

### Line 227
```python
    block = build(idx)
```
**Plain English:** Store a value: the name `block` now holds the result of `build(idx)`. Whenever you later write that name, you mean this value.

### Line 228
```python
    path = save_block(block, "a_flank")
```
**Plain English:** Store a value: the name `path` now holds the result of `save_block(block, "a_flank")`. Whenever you later write that name, you mean this value.

### Line 229
```python
    n_seq = sum(c.startswith(f"{PREFIX}.seq") for c in block.columns)
```
**Plain English:** Store a value: the name `n_seq` now holds the result of `sum(c.startswith(f"{PREFIX}.seq") for c in block.columns)`. Whenever you later write that name, you mean this value.

### Line 230
```python
    n_qct = sum(c.startswith(f"{PREFIX}.qct") for c in block.columns)
```
**Plain English:** Store a value: the name `n_qct` now holds the result of `sum(c.startswith(f"{PREFIX}.qct") for c in block.columns)`. Whenever you later write that name, you mean this value.

### Line 231
```python
    n_win = sum(c.startswith((f"{PREFIX}.win", f"{PREFIX}.comp"))
```
**Plain English:** Store a value: the name `n_win` now holds the result of `sum(c.startswith((f"{PREFIX}.win", f"{PREFIX}.comp"))`. Whenever you later write that name, you mean this value.

### Line 232
```python
                for c in block.columns)
```
**Plain English:** Loop: repeat the indented block once for each item → `c in block.columns)`.

### Line 233
```python
    print(f"a_flank: {block.shape[0]:,} rows x {block.shape[1] - 1:,} features "
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"a_flank: {block.shape[0]:,} rows x {block.shape[1] - 1:,} features "`.

### Line 234
```python
          f"({n_seq} one-hot, {n_qct} per-position tensors, {n_win} window "
```
**Plain English:** One-hot base identity: four columns per position (A/C/G/T), exactly one is 1.

### Line 235
```python
          f"summaries out to {max(SUMMARY_WINDOWS)} nt) -> {path}")
```
**Plain English:** Run this instruction: `f"summaries out to {max(SUMMARY_WINDOWS)} nt) -> {path}")`.

### Line 238
```python
if __name__ == "__main__":
```
**Plain English:** Special gate: this block runs only when you execute *this file directly* (not when another file imports it). Common pattern for scripts.

### Line 239
```python
    main()
```
**Plain English:** Run this instruction: `main()`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### Why Family A helped so much
The published matrix stops at the 20-mer. Biology doesn’t. Nearby DNA (especially composition / AT-richness) carries a large signal for bacterial Cas9.

### Why emit `comp.gc` next to window tensor means?
Averaging chemistry numbers over hundreds of bases ≈ GC content (ρ≈0.998).  
Making GC explicit stops you from fooling yourself that seventeen correlated columns are seventeen independent discoveries.

### Labels `u10…u1`, `pamN`, `d1…d15`
Positions walking 5′→3′: ten bases before the spacer, the variable base of the PAM, fifteen bases after the PAM.
