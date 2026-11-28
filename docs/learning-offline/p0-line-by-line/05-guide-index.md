# P0 line-by-line: `Runjia/sgrna/build/build_guide_index.py`
**Why this file matters:** Step 0: turn anonymous spreadsheet rows into guides with real genomic addresses and flanking DNA.
**Length:** 165 lines.
**How to read this guide:** each block shows the real code, then plain English. If you see “same idea as…”, that pattern already appeared earlier.
**Prerequisite:** skim [`00-glossary.md`](00-glossary.md) once.
---
## Big picture

Each row used to be just a weird ID. This file finds where that guide sits on the E. coli chromosome and saves the DNA neighbourhood around it.

---
### Lines 1–29
```python
"""Step 0 -- turn 13,880 anonymous rows into located guides.

The published matrix identifies each guide only by a name like
`aaeAb3241_107_Cas9`. Nothing downstream of family A can be built from that:
supercoiling, nucleoid structure, methylation, transcription and off-target
burden all need to know *where on the chromosome* the guide sits. This script
recovers that, and writes one table everything else reads.

What it does
------------
1. Decodes the 20 nt protospacer from the QCT electron-count columns
   (see `qct.py` for why that works).
2. Finds each protospacer in NC_000913.2 on either strand, and records the
   coordinates, the strand, the real PAM and the flanking sequence.
3. Checks every hit: the PAM must be NGG, and a guide that matches the genome
   more than once is flagged rather than silently averaged.
4. Learns the QCT k-mer lookup tables so family A can extend the published
   quantum descriptors into the flanks.

Run from a notebook cell (the usual way):

    import sgrna.notebook as nb
    nb.setup()
    nb.build_index()

or from a terminal:

    python -m sgrna.build_guide_index
"""
```
**Plain English:** This is a **docstring** — a multi-line note describing the file or function. Python stores it as documentation but does not treat it as an instruction to compute something. Read it like a preface.

### Line 31
```python
from __future__ import annotations
```
**Plain English:** Turns on newer Python typing behaviours so annotations like `list[str]` work on older Python versions.

### Line 33
```python
import argparse
```
**Plain English:** Load toolbox code: `import argparse` — used here for **command-line switches like `--flank 1000`**.

### Line 34
```python
import sys
```
**Plain English:** Load toolbox code: `import sys` — used here for **Python runtime (arguments, exit codes)**.

### Line 36
```python
import pandas as pd
```
**Plain English:** Load toolbox code: `import pandas as pd` — used here for **spreadsheet-like tables**.

### Line 38
```python
from .. import config
```
**Plain English:** Load a project module from this repo: `from .. import config`.

### Line 39
```python
from . import genome
```
**Plain English:** Load a project module from this repo: `from . import genome`.

### Line 40
```python
from . import qct
```
**Plain English:** Load a project module from this repo: `from . import qct`.

### Line 41
```python
from .qct import parse_sgrna_id
```
**Plain English:** Load a project module from this repo: `from .qct import parse_sgrna_id`.

### Line 44
```python
def build(flank: int = config.FLANK, verbose: bool = True) -> pd.DataFrame:
```
**Plain English:** Defines a reusable recipe named `build`. Inputs in parentheses: `flank: int = config.FLANK, verbose: bool = True`. Returns type hint: pd.DataFrame. Nothing runs yet until something *calls* `build(...)`.

### Line 45
```python
    say = print if verbose else (lambda *a, **k: None)
```
**Plain English:** Store a value: the name `say` now holds the result of `print if verbose else (lambda *a, **k: None)`. Whenever you later write that name, you mean this value.

### Line 47
```python
    say(f"Reading {config.BASE_MATRIX.name} ...")
```
**Plain English:** Run this instruction: `say(f"Reading {config.BASE_MATRIX.name} ...")`.

### Line 48
```python
    frame = qct.load_qct_frame(verbose=verbose)
```
**Plain English:** Store a value: the name `frame` now holds the result of `qct.load_qct_frame(verbose=verbose)`. Whenever you later write that name, you mean this value.

### Line 49
```python
    decoded = qct.decode_protospacers(frame)
```
**Plain English:** Store a value: the name `decoded` now holds the result of `qct.decode_protospacers(frame)`. Whenever you later write that name, you mean this value.

### Line 50
```python
    say(f"  {len(decoded):,} guides, {decoded['decoded_ok'].sum():,} fully decoded")
```
**Plain English:** Run this instruction: `say(f"  {len(decoded):,} guides, {decoded['decoded_ok'].sum():,} fully decoded")`.

### Line 52
```python
    g = genome.load_genome()
```
**Plain English:** Store a value: the name `g` now holds the result of `genome.load_genome()`. Whenever you later write that name, you mean this value.

### Line 53
```python
    say(f"  genome {config.GENOME_FASTA.name}: {len(g):,} bp")
```
**Plain English:** Run this instruction: `say(f"  genome {config.GENOME_FASTA.name}: {len(g):,} bp")`.

### Line 54
```python
    n_sites = len(genome.protospacer_sites()[0])
```
**Plain English:** Store a value: the name `n_sites` now holds the result of `len(genome.protospacer_sites()[0])`. Whenever you later write that name, you mean this value.

### Line 55
```python
    say(f"  indexed {n_sites:,} NGG-flanked protospacer sites")
```
**Plain English:** Run this instruction: `say(f"  indexed {n_sites:,} NGG-flanked protospacer sites")`.

### Line 57
```python
    ids = decoded[config.ID_COL].map(parse_sgrna_id).apply(pd.Series)
```
**Plain English:** Store a value: the name `ids` now holds the result of `decoded[config.ID_COL].map(parse_sgrna_id).apply(pd.Series)`. Whenever you later write that name, you mean this value.

### Line 58
```python
    records = []
```
**Plain English:** Store a value: the name `records` now holds the result of `[]`. Whenever you later write that name, you mean this value.

### Line 59
```python
    for proto, ok in zip(decoded["protospacer"], decoded["decoded_ok"]):
```
**Plain English:** Loop: repeat the indented block once for each item → `proto, ok in zip(decoded["protospacer"], decoded["decoded_ok"])`.

### Line 60
```python
        if not ok:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not ok`.

### Line 61
```python
            records.append(dict(n_genome_copies=0))
```
**Plain English:** Run this instruction: `records.append(dict(n_genome_copies=0))`.

### Line 62
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 63
```python
        hits = genome.locate_protospacer(proto, g)
```
**Plain English:** Search the E. coli genome for this 20-mer (both strands) and return hit coordinates + PAM.

### Line 64
```python
        if not hits:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not hits`.

### Line 65
```python
            records.append(dict(n_genome_copies=0))
```
**Plain English:** Run this instruction: `records.append(dict(n_genome_copies=0))`.

### Line 66
```python
            continue
```
**Plain English:** Skip the rest of this loop iteration; jump to the next item.

### Line 67
```python
        h = hits[0]
```
**Plain English:** Store a value: the name `h` now holds the result of `hits[0]`. Whenever you later write that name, you mean this value.

### Line 68
```python
        ctx = genome.guide_context(h["left"], h["right"], h["strand"], flank, g)
```
**Plain English:** Cut out upstream/downstream DNA strings of length `flank` around the hit.

### Line 69
```python
        records.append(
```
**Plain English:** Run this instruction: `records.append(`.

### Line 70
```python
            dict(
```
**Plain English:** Run this instruction: `dict(`.

### Line 71
```python
                strand=h["strand"],
```
**Plain English:** Store a value: the name `strand` now holds the result of `h["strand"],`. Whenever you later write that name, you mean this value.

### Line 72
```python
                left=h["left"],
```
**Plain English:** Store a value: the name `left` now holds the result of `h["left"],`. Whenever you later write that name, you mean this value.

### Line 73
```python
                right=h["right"],
```
**Plain English:** Store a value: the name `right` now holds the result of `h["right"],`. Whenever you later write that name, you mean this value.

### Line 74
```python
                pam=h["pam"],
```
**Plain English:** Store a value: the name `pam` now holds the result of `h["pam"],`. Whenever you later write that name, you mean this value.

### Line 75
```python
                n_genome_copies=len(hits),
```
**Plain English:** Store a value: the name `n_genome_copies` now holds the result of `len(hits),`. Whenever you later write that name, you mean this value.

### Line 76
```python
                upstream=ctx["upstream"],
```
**Plain English:** Store a value: the name `upstream` now holds the result of `ctx["upstream"],`. Whenever you later write that name, you mean this value.

### Line 77
```python
                downstream=ctx["downstream"],
```
**Plain English:** Store a value: the name `downstream` now holds the result of `ctx["downstream"],`. Whenever you later write that name, you mean this value.

### Line 78
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 79
```python
        )
```
**Plain English:** Run this instruction: `)`.

### Line 81
```python
    loc = pd.DataFrame(records)
```
**Plain English:** Store a value: the name `loc` now holds the result of `pd.DataFrame(records)`. Whenever you later write that name, you mean this value.

### Line 82
```python
    out = pd.concat(
```
**Plain English:** Store a value: the name `out` now holds the result of `pd.concat(`. Whenever you later write that name, you mean this value.

### Line 83
```python
        [decoded.reset_index(drop=True), ids.reset_index(drop=True), loc], axis=1
```
**Plain English:** Run this instruction: `[decoded.reset_index(drop=True), ids.reset_index(drop=True), loc], axis=1`.

### Line 84
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 86
```python
    # ---- quality control -------------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---- quality control -------------------------------------------------

### Line 87
```python
    out["located"] = out["n_genome_copies"] >= 1
```
**Plain English:** Store a value: the name `out["located"]` now holds the result of `out["n_genome_copies"] >= 1`. Whenever you later write that name, you mean this value.

### Line 88
```python
    out["unique_in_genome"] = out["n_genome_copies"] == 1
```
**Plain English:** True only if exactly one genomic copy — multi-copy guides are ambiguous for locus features.

### Line 89
```python
    out["pam_is_ngg"] = out["pam"].fillna("").str.endswith("GG")
```
**Plain English:** True if the PAM ends with GG (Cas9’s NGG requirement).

### Line 91
```python
    n = len(out)
```
**Plain English:** Store a value: the name `n` now holds the result of `len(out)`. Whenever you later write that name, you mean this value.

### Line 92
```python
    say(f"  located in genome      : {out['located'].sum():,} / {n:,}")
```
**Plain English:** Run this instruction: `say(f"  located in genome      : {out['located'].sum():,} / {n:,}")`.

### Line 93
```python
    say(f"  unique single copy     : {out['unique_in_genome'].sum():,} / {n:,}")
```
**Plain English:** True only if exactly one genomic copy — multi-copy guides are ambiguous for locus features.

### Line 94
```python
    say(f"  NGG PAM confirmed      : {out['pam_is_ngg'].sum():,} / {n:,}")
```
**Plain English:** True if the PAM ends with GG (Cas9’s NGG requirement).

### Line 95
```python
    if out["located"].sum() and not out.loc[out["located"], "pam_is_ngg"].all():
```
**Plain English:** Decision: run the indented block only when this condition is true → `out["located"].sum() and not out.loc[out["located"], "pam_is_ngg"].all()`.

### Line 96
```python
        bad = out.loc[out["located"] & ~out["pam_is_ngg"], config.ID_COL].head(5)
```
**Plain English:** True if the PAM ends with GG (Cas9’s NGG requirement).

### Line 97
```python
        say(f"  !! non-NGG PAMs, e.g. {list(bad)}")
```
**Plain English:** Run this instruction: `say(f"  !! non-NGG PAMs, e.g. {list(bad)}")`.

### Line 99
```python
    # ---- replication landmarks ------------------------------------------
```
**Plain English:** Human-only note (Python ignores it): ---- replication landmarks ------------------------------------------

### Line 100
```python
    lm = genome.replication_landmarks()
```
**Plain English:** Store a value: the name `lm` now holds the result of `genome.replication_landmarks()`. Whenever you later write that name, you mean this value.

### Line 101
```python
    say(
```
**Plain English:** Run this instruction: `say(`.

### Line 102
```python
        f"  GC-skew origin         : {lm['ori']:,} "
```
**Plain English:** Run this instruction: `f"  GC-skew origin         : {lm['ori']:,} "`.

### Line 103
```python
        f"(annotated oriC is near 3,923,800 -- these should agree)"
```
**Plain English:** Run this instruction: `f"(annotated oriC is near 3,923,800 -- these should agree)"`.

### Line 104
```python
    )
```
**Plain English:** Run this instruction: `)`.

### Line 105
```python
    say(f"  GC-skew terminus       : {lm['ter']:,}")
```
**Plain English:** Run this instruction: `say(f"  GC-skew terminus       : {lm['ter']:,}")`.

### Line 107
```python
    out["ori_distance"] = [
```
**Plain English:** Store a value: the name `out["ori_distance"]` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 108
```python
        genome.circular_distance(int(p), lm["ori"]) if pd.notna(p) else None
```
**Plain English:** Run this instruction: `genome.circular_distance(int(p), lm["ori"]) if pd.notna(p) else None`.

### Line 109
```python
        for p in out["left"]
```
**Plain English:** Loop: repeat the indented block once for each item → `p in out["left"]`.

### Line 110
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 111
```python
    out["replichore"] = [
```
**Plain English:** Store a value: the name `out["replichore"]` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 112
```python
        genome.replichore(int(p)) if pd.notna(p) else None for p in out["left"]
```
**Plain English:** Run this instruction: `genome.replichore(int(p)) if pd.notna(p) else None for p in out["left"]`.

### Line 113
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 114
```python
    # Is the guide's own strand the leading-strand template here?
```
**Plain English:** Human-only note (Python ignores it): Is the guide's own strand the leading-strand template here?

### Line 115
```python
    out["leading_strand"] = [
```
**Plain English:** Store a value: the name `out["leading_strand"]` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 116
```python
        None
```
**Plain English:** Run this instruction: `None`.

### Line 117
```python
        if pd.isna(p) or not isinstance(s, str)
```
**Plain English:** Decision: run the indented block only when this condition is true → `pd.isna(p) or not isinstance(s, str)`.

### Line 118
```python
        else int((genome.replication_fork_direction(int(p)) == 1) == (s == "+"))
```
**Plain English:** Otherwise: run this indented block when none of the previous conditions matched.

### Line 119
```python
        for p, s in zip(out["left"], out["strand"])
```
**Plain English:** Loop: repeat the indented block once for each item → `p, s in zip(out["left"], out["strand"])`.

### Line 120
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 122
```python
    out["gene_offset_check"] = out["gene_offset"]
```
**Plain English:** Store a value: the name `out["gene_offset_check"]` now holds the result of `out["gene_offset"]`. Whenever you later write that name, you mean this value.

### Line 123
```python
    out = out.rename(columns={config.TARGET_COL: "cut_score"})
```
**Plain English:** Store a value: the name `out` now holds the result of `out.rename(columns={config.TARGET_COL: "cut_score"})`. Whenever you later write that name, you mean this value.

### Line 125
```python
    cols = [
```
**Plain English:** Store a value: the name `cols` now holds the result of `[`. Whenever you later write that name, you mean this value.

### Line 126
```python
        config.ID_COL, "cut_score", "gene_name", "b_number", "gene_offset",
```
**Plain English:** Run this instruction: `config.ID_COL, "cut_score", "gene_name", "b_number", "gene_offset",`.

### Line 127
```python
        "nuclease", "protospacer", "pam", "strand", "left", "right",
```
**Plain English:** Run this instruction: `"nuclease", "protospacer", "pam", "strand", "left", "right",`.

### Line 128
```python
        "n_genome_copies", "located", "unique_in_genome", "pam_is_ngg",
```
**Plain English:** True only if exactly one genomic copy — multi-copy guides are ambiguous for locus features.

### Line 129
```python
        "ori_distance", "replichore", "leading_strand", "upstream", "downstream",
```
**Plain English:** Run this instruction: `"ori_distance", "replichore", "leading_strand", "upstream", "downstream",`.

### Line 130
```python
    ]
```
**Plain English:** Run this instruction: `]`.

### Line 131
```python
    out = out[[c for c in cols if c in out.columns]]
```
**Plain English:** Store a value: the name `out` now holds the result of `out[[c for c in cols if c in out.columns]]`. Whenever you later write that name, you mean this value.

### Line 132
```python
    return out
```
**Plain English:** Finish this function and send back: `out`.

### Line 135
```python
def main(argv=None) -> int:
```
**Plain English:** Defines a reusable recipe named `main`. Inputs in parentheses: `argv=None`. Returns type hint: int. Nothing runs yet until something *calls* `main(...)`.

### Line 136
```python
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
```
**Plain English:** Store a value: the name `ap` now holds the result of `argparse.ArgumentParser(description=__doc__.split("\n")[0])`. Whenever you later write that name, you mean this value.

### Line 137
```python
    ap.add_argument("--flank", type=int, default=config.FLANK,
```
**Plain English:** Run this instruction: `ap.add_argument("--flank", type=int, default=config.FLANK,`.

### Line 138
```python
                    help="nt of flanking sequence to store either side")
```
**Plain English:** Store a value: the name `help` now holds the result of `"nt of flanking sequence to store either side")`. Whenever you later write that name, you mean this value.

### Line 139
```python
    ap.add_argument("--skip-qct-tables", action="store_true",
```
**Plain English:** Run this instruction: `ap.add_argument("--skip-qct-tables", action="store_true",`.

### Line 140
```python
                    help="do not rebuild the QCT k-mer lookup tables")
```
**Plain English:** Store a value: the name `help` now holds the result of `"do not rebuild the QCT k-mer lookup tables")`. Whenever you later write that name, you mean this value.

### Line 141
```python
    args = ap.parse_args(argv)
```
**Plain English:** Store a value: the name `args` now holds the result of `ap.parse_args(argv)`. Whenever you later write that name, you mean this value.

### Line 143
```python
    idx = build(flank=args.flank)
```
**Plain English:** Store a value: the name `idx` now holds the result of `build(flank=args.flank)`. Whenever you later write that name, you mean this value.

### Line 144
```python
    idx.to_csv(config.GUIDE_INDEX, index=False)
```
**Plain English:** Run this instruction: `idx.to_csv(config.GUIDE_INDEX, index=False)`.

### Line 145
```python
    print(f"\nWrote {config.GUIDE_INDEX} ({len(idx):,} rows)")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\nWrote {config.GUIDE_INDEX} ({len(idx):,} rows)")`.

### Line 147
```python
    if not args.skip_qct_tables:
```
**Plain English:** Decision: run the indented block only when this condition is true → `not args.skip_qct_tables`.

### Line 148
```python
        print("\nLearning QCT k-mer lookup tables from the published matrix ...")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print("\nLearning QCT k-mer lookup tables from the published matrix ...")`.

### Line 149
```python
        tables = qct.learn_lookup_tables(idx["protospacer"], qct.load_qct_frame())
```
**Plain English:** Store a value: the name `tables` now holds the result of `qct.learn_lookup_tables(idx["protospacer"], qct.load_qct_frame())`. Whenever you later write that name, you mean this value.

### Line 150
```python
        qct.save_tables(tables)
```
**Plain English:** Run this instruction: `qct.save_tables(tables)`.

### Line 151
```python
        cov = qct.table_coverage(tables)
```
**Plain English:** Store a value: the name `cov` now holds the result of `qct.table_coverage(tables)`. Whenever you later write that name, you mean this value.

### Line 152
```python
        print(cov.to_string(index=False))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(cov.to_string(index=False))`.

### Line 153
```python
        print(f"\nWrote {config.QCT_TABLES}")
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(f"\nWrote {config.QCT_TABLES}")`.

### Line 154
```python
        thin = cov[cov["coverage"] < 0.9]
```
**Plain English:** Store a value: the name `thin` now holds the result of `cov[cov["coverage"] < 0.9]`. Whenever you later write that name, you mean this value.

### Line 155
```python
        if len(thin):
```
**Plain English:** Decision: run the indented block only when this condition is true → `len(thin)`.

### Line 156
```python
            print(
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(`.

### Line 157
```python
                "\nNote: the k-mers below were never seen in the 13,880 guides, so "
```
**Plain English:** Run this instruction: `"\nNote: the k-mers below were never seen in the 13,880 guides, so "`.

### Line 158
```python
                "flank positions containing them will be NaN and median-imputed:"
```
**Plain English:** Run this instruction: `"flank positions containing them will be NaN and median-imputed:"`.

### Line 159
```python
            )
```
**Plain English:** Run this instruction: `)`.

### Line 160
```python
            print(thin.to_string(index=False))
```
**Plain English:** Show a message on the screen so a human can watch progress: `print(thin.to_string(index=False))`.

### Line 161
```python
    return 0
```
**Plain English:** Finish this function and send back: `0`.

### Line 164
```python
if __name__ == "__main__":
```
**Plain English:** Special gate: this block runs only when you execute *this file directly* (not when another file imports it). Common pattern for scripts.

### Line 165
```python
    sys.exit(main())
```
**Plain English:** Run this instruction: `sys.exit(main())`.

---

## End-of-file checklist

- [ ] I can explain this file’s job in one sentence
- [ ] I know which lines are ‘settings’ vs ‘real work’
- [ ] I know what I would change if my CSV path differed

---

## Concept deep-dives

### Why location matters
Supercoiling, transcription, and Family A flanks are properties of **where** the guide sits on the chromosome.  
An ID like `aaeAb3241_107_Cas9` doesn’t give coordinates. This script finds them.

### Unique vs multi-copy
If the same 20-mer appears twice in the genome, you don’t know which locus’s flanks to use → flag it, don’t silently average.
