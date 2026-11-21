# P1 — Jacky’s human Tier-1→4 and orientation controls

**Source files (human strand):**  
- `Jacky/human_tier1_*.py` / notebooks (Tier-1: fidelity of human transfer)  
- `Jacky/human_tier2_*.py` (Tier-2: broader human panels / stress)  
- `Jacky/human_tier3_*.py` (Tier-3: harder generalization)  
- `Jacky/human_tier4_*.py` (Tier-4: stretch / secondary claims)  
- related reports under `Jacky/` / `docs/` that summarize each tier  

**Source files (orientation / chromatin controls — after human story is clear):**  
- orientation / strand control scripts & notes (intergenic orientation, strand audit helpers)  
- chromatin / H6-adjacent **control** notebooks only if they gate a claim you already make — **not** twin/H6 discovery work  

**Job in the project:** prove the model story still holds when you leave the bacterial comfort zone, then check that **orientation / strand** confounds aren’t faking the signal.

---

## Where this sits

```text
Bacterial Family A story (P0 #8–9, package CV)
        │
        ▼
Human Tier-1 ─── “does the trained idea transfer at all?”
        │
        ▼
Human Tier-2 / Tier-3 ─── broader / harder human settings
        │
        ▼
Human Tier-4 ─── stretch claims (treat as optional until T1–T3 are solid)
        │
        ▼
Orientation / strand controls ─── “is the win an artifact of strand/orientation?”
```

Twin / H6 **discovery** tracks stay out of this learning pack. Use orientation/chromatin pieces only as **controls** on claims you already understand.

---

## 1. Human tiers — one purpose each

| Tier | Question it answers | How to read |
|---|---|---|
| **1** | Can we get a credible human signal with the same leakage discipline? | Primary human entry; compare protocol to bacterial baseline |
| **2** | Does it survive a broader human panel / second stress? | Look for what changed vs Tier-1 (data, labels, features) |
| **3** | Does it survive a harder generalization cut? | Treat as “believe Tier-1 only if Tier-3 doesn’t collapse for the same reason” |
| **4** | Stretch / secondary story | Skim after 1–3; don’t let it redefine the yardstick |

**Shared reading questions for every tier script:**

1. What is the **label** and where does it come from?  
2. What is the **split** (and is it still train-only for impute/select)?  
3. What is compared to what (baseline? shuffled? bacterial model frozen?)?  
4. Which number is the **headline** (usually Spearman / Δρ / success rate — find the CELL-7 analogue)?

---

## 2. How human scripts relate to the bacterial package

| Bacterial package idea | Human-tier analogue |
|---|---|
| `USE THIS` / Family A CV | Tier-1 evaluation protocol |
| `run_ablation` / Δρ | “Did human features / transfer help vs control?” |
| `floors.py` | Human-side go/no-go thresholds (if present in that script’s report) |
| `diagnose_cv_gap` | “Train looks good, human holdout dies” debugging |

You do **not** need to re-derive featurise or QCT tables to read a tier — but you **do** need the P0 mental model of leakage-safe scoring so you don’t trust a human notebook that fits on the full matrix.

---

## 3. Orientation / strand controls

**Why they exist:** sgRNA / genomic context can encode **which strand** or **orientation** a guide sits on. A model can look smart by memorizing strand proxies instead of sequence chemistry.

**What “control” means here:**

```text
Claim: model predicts activity from features F
Control: scramble or stratify by orientation/strand
         → if performance collapses only when orientation is removed,
           or stays high when biology is scrambled but strand is kept,
           the claim is contaminated
```

**Reading order for orientation materials:**

1. Find the **claim** they protect (usually a human or intergenic result)  
2. Find the **control table** (Δρ with vs without orientation, or strand-stratified ρ)  
3. Ignore discovery-style H6/twin rabbit holes unless a mentor explicitly assigns them  

---

## 4. Practical path through Jacky’s stack

1. **Tier-1 only** until you can state the headline metric and the split in one sentence  
2. Skim Tier-2/3 diffs vs Tier-1 (what data changed?)  
3. Glance Tier-4 for “nice to have,” not for redefining success  
4. Open **one** orientation control that matches a claim you already believe  
5. Return to package `floors` / `diagnose` if human CV looks too good to be true  

---

## Checklist

- [ ] I can explain Tier-1’s question in one sentence  
- [ ] I know Tier-4 is stretch, not the new baseline  
- [ ] I ask “what’s the split?” before trusting any human ρ  
- [ ] I treat orientation/strand scripts as **controls**, not a second discovery project  
- [ ] Twin/H6 discovery stays out of this learning pass  
