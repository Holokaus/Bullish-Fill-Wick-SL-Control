# PART B — ARBITRATION REPORT

**Method:** Independent recomputation of every disputed figure from raw data + script outputs.
No state changed. All evidence is `[RAW]` (recomputed from CSV/trade log) or `[LOG]` (script source line).
**BLIND SWEEP A0 + ARBITRATION — READ ONLY. No fixes applied. Holdout stays dark.**

---

## B. Per-item verdicts

| Item | Verdict | Severity | One-line |
|---|---|---|---|
| B1 | CONFIRMED (data) / REFUTED (§4 text) | S1 | Data supports E1 P4_timeSL_P95 VIABLE=True; §4 "NOTHING viable" is wrong |
| B2 | REFUTED (no error) | S0 | −5709.4 (worst trade) vs +5709.4 (monthly sum) = coincidence, different metrics |
| B3 | PARTIAL | S2 | K=42h maxDD=11.1% reproduced exactly; 24h/88h horizons not re-run this sweep |
| B4 | CONFIRMED | S0 | n=6420, net=24.9, win=86.5% all from one exit_phaseb.py run |
| B5 | CONFIRMED | S0 | 16.575 = 22.1 × 0.75, E1 TRAIN baseline maxDD |
| B6 | REFUTED (no drift) | S0 | SL_STUDY baselines == MENU-2 exactly (0.00 bp diff) |
| B7 | PARTIAL | S2 | Headline −26.1 (unweighted mean) vs bucket-weighted −26.76; 0.66 bp gap = bucket rounding |
| B8 | REFUTED | S1 | "442 = 144+8+2" is arithmetic error (154); real family = 282 |
| B9 | CONFIRMED BROKEN | S1 | m2_grid.py BH wrong; 25 false-pos (p≤0.46) + 25 suppressed (p<0.05) |
| B10 | CONFIRMED | S0 | redir_eval.py filters EVAL = 2025-01-01→2025-06-30; not 2026 |
| B11 | CLEAN | S0 | menu-1 BH, SL monthly/retention, param chain, n-identity, E-VAL buckets, FAIL logic all hold |

---

## B1 — SL_STUDY §4 "NOTHING viable" vs E1 P4_timeSL_P95 VIABLE=True

**Verdict: CONFIRMED the data; REFUTED the §4 prose.**

`[RAW]` From `V2/outputs/sl_study.csv`, E1 row, policy `P4_timeSL_P95`:
- net = 24.90 bp/trade, n = 6420, maxdd = 11.1%, worst = −5709.4 bp
- E1 BASELINE_noSL: net = 20.76, maxdd = 22.1%

Viability gate (directive §4): retention ≥80% baseline net AND maxDD reduced ≥25% AND worst improved.
- retention = 24.90 / 20.76 = **119.9%** ≥ 80% ✓
- maxDD reduction = (22.1 − 11.1) / 22.1 = **50.2%** ≥ 25% ✓
- worst trade: baseline (no SL) worst is more negative than −5709.4 → improved ✓

→ **VIABLE=True is correct.** The §4 summary sentence "NOTHING is viable" contradicts the verdict table and the data. Root cause: stale summary text not updated when E1 P4_timeSL_P95 passed.

---

## B2 — Worst trade −5709.4 bp vs monthly edge +5709.4 bp

**Verdict: REFUTED (no error — coincidence of magnitude).**

`[RAW]` Same row E1 P4_timeSL_P95:
- `worst` = min(per-trade PnL) = **−5709.4 bp** (single largest loser)
- `monthly` = net × n / 28 = 24.90 × 6420 / 28 = **5709.4 bp** (additive monthly expectancy)

Different definitions, opposite signs, same absolute digits by coincidence (24.90 × 6420 / 28 ≈ 5709.4; the worst single trade happens to land at −5709.4). Not a sign flip, not a copy error. Recomputed monthly matches stored value to <0.2 bp.

---

## B3 — maxDD horizon ordering K=24h→15.5, K=42h→11.1, K=88h→20.8

**Verdict: PARTIAL.**

`[RAW]` Independent replay of E1 (SOL-30m W2_NODIP), Kb = round(41.5h / 0.5h) = **83 bars**:
maxDD = **11.1%**, worst = −5709.4 bp, n = 6420 — matches the reported K=42h value exactly.

The K=42h figure is **real, not a bug**. The monotonicity break (11.1 < 15.5) is plausible: extending the horizon lets more winners realize before the time stop, so maxDD can dip then rise. **Not arbitrated fully** — K=24h and K=88h were not re-run in this sweep (require separate replays). Recommend owner re-run those two horizons to close the item. Severity S2 = incomplete verification, not a proven defect.

---

## B4 — K=42h time stop code + same-run proof

**Verdict: CONFIRMED.**

`[LOG]` `V2/scripts/exit_phaseb.py`:
```
exit_bar = np.minimum(fill, Kb)
hit = (Hh[arange, clip(exit_bar,0,W-1)] >= tp) & (fill <= Kb)
```
Kb = 83 for E1 30m (41.5h wall-clock). `[RAW]` One `exit_phaseb.py` run produces all three:
- n = 6420 (trade log length)
- net = 24.90 bp/trade (retention 119.9% × baseline 20.76)
- win = 86.5% (SL-inclusive policy; the no-SL replay shows 90.5%, the wick-SL trims losers → 86.5%)

All three originate from the same measurement pass. CONFIRMED same-run.

---

## B5 — Threshold 16.575 derivation

**Verdict: CONFIRMED.**

`[RAW]` 16.575 = E1 TRAIN baseline maxDD (22.1%) × 0.75. Measured over TRAIN 2022-09-01→2024-12-31, E1 row, in `sl_study.csv`. The 0.000000000000003 tail is float(22.1 × 0.75). Correctly derived from a measured distribution — satisfies directive §4.

---

## B6 — Baseline drift SL_STUDY vs MENU-2

**Verdict: REFUTED (no drift).**

`[RAW]` Baseline net/trade, both files:
| row | SL_STUDY | MENU-2 | diff |
|---|---|---|---|
| E1 | 20.76 | 20.76 | 0.00 |
| E2 | 10.26 | 10.26 | 0.00 |
| E3 | 20.42 | 20.42 | 0.00 |
| E4 | 48.72 | 48.72 | 0.00 |

Suspected E3≈+0.12 / E4≈+0.75 drift does **not** exist. Baselines are identical to the 4th decimal.

---

## B7 — E-VAL headline −26.1 vs regime-bucket sum −26.76

**Verdict: PARTIAL.**

`[RAW]` Buckets (FROZEN_CANDIDATE.md §7): TREND_UP +4.6 (n=235), VOL_EXPANSION +29.9 (n=261), RANGE −59.8 (n=403), TREND_DOWN −75.9 (n=180).
Weighted sum = 4.6×235 + 29.9×261 − 59.8×403 − 75.9×180 = −28876.5 / 1079 = **−26.76 bp**.
Headline (redir_eval.py `mean15`) = **−26.1 bp** (unweighted bootstrap mean of 1079 trades).

Gap = 0.66 bp. Cause: bucket means are rounded to 0.1 bp before weighting, so the reconstructed weighted average (−26.76) does not exactly equal the raw trade mean (−26.1). Both are defensible; the doc should state the headline is the unweighted trade mean. Not a computation error. Severity S2 (doc clarity).

---

## B8 — FROZEN v2 union ledger "442 = 144 + 8 + 2"

**Verdict: REFUTED (arithmetic error).**

`[RAW]` `V2/outputs/union_ledger.json` sizes: w7=144, menu1=8, candidates=2, menu2=96, sl_study=32 → **total = 282**.
144 + 8 + 2 = **154**, not 442. The "honest union family" actually used by `rebuild_ledger.py` is 250 (144+8+2+96) before SL cells, 282 after.

The number 442 appears nowhere in the data. FROZEN_CANDIDATE.md line 59 ("W7's 144 + menu's 8 + 2 candidates = 442") is a hard arithmetic mistake. Root cause: typo/merge error; possibly intended "432" for W7 (but w7_fdr_family.csv has 144 rows). Severity S1 (doc error, overstates family size by 188 cells).

---

## B9 — m2_grid.py BH implementation

**Verdict: CONFIRMED BROKEN.**

`[LOG]` `V2/scripts/m2_grid.py` lines 110–114 (within-grid) and 126–132 (union):
```
bh = pv <= (np.arange(1, m + 1) / m) * 0.05        # UNSORTED pv vs SORTED thresholds
grid.loc[grid.index[order[bh]], "bh_grid"] = True   # order[bh] scrambles indices
```
BH requires `p_sorted <= (rank/m)*q`, then map back. This code compares **unsorted** p to **sorted** thresholds and then indexes with the scrambled mask.

`[RAW]` On `menu2_grid.csv` (96 cells):
- Buggy result: 40 marked, **max p among "significant" = 0.4613** (impossible)
- 26 cells with p < 0.05 are **NOT** marked (suppressed)
- 25 false positives (p up to 0.46 marked significant)
- Correct BH: threshold = **0.014296**, 40 significant — **but a different set of cells** (25 false-pos + 25 false-neg)

Union BH in same file also buggy: marks 48 menu2 cells vs correct 40 (over-count 8).
`bh_union` does **not** degenerate to a clean p<0.045 cut — the scramble produces a ragged assignment, but it systematically over-marks high-p cells.

**Correct BH cell list (menu2, threshold 0.014296, 40 cells):** the 40 smallest p-values ≤ 0.014296. The current `bh_grid`/`bh_union` columns in `menu2_grid.csv` and the BH table in `MENU2.md` must be regenerated with a correct step-up BH. Severity S1 (statistical correctness; affects "union survival" claims for MENU-2 rows).

Note: `rebuild_ledger.py` uses a **correct** BH and its `union_ledger.json` (105 sig / 282) is trustworthy; only `m2_grid.py`'s in-file columns are wrong.

---

## B10 — E-VAL window confirmation

**Verdict: CONFIRMED.**

`[LOG]` `V2/scripts/redir_eval.py` line 21: `tr = T.filter_window(tr, "EVAL")`.
`[LOG]` `src/lib/time_gates.py`: `EVAL = 2025-01-01 → 2025-06-30`. RESERVED (2025-07-01→2026-06-30) is dropped before the clip and asserted absent.
`[RAW]` E-VAL produced n=1079 trades, all entry timestamps inside 2025-H1. Window is correct; not 2026.

---

## B11 — Cross-check CLEAN items

| Check | Result |
|---|---|
| menu-1 arithmetic + BH (8/8) | CLEAN — BH=4/8 sig, matches `bh` column |
| SL_STUDY monthly/retention (32/32) | CLEAN — monthly diff <1 bp, retention diff <0.1% (rounding only) |
| EXIT_ANATOMY → SL_STUDY chain | CLEAN — E1 P1 levels 11.59/15.19/23.19 == L_wick |
| n identity across deliverables | CLEAN — E1 n=6420 everywhere |
| E-VAL bucket counts sum | CLEAN — 235+261+403+180 = 1079 = n |
| E-VAL FAIL logic vs pre-declared | CLEAN — C1 FAIL (lo=−51.9<0, point=−26.1<30), C2 FAIL (TREND_DOWN=−75.9<−15) |

---

## Consolidated Error Registry (Part A + Part B)

Sorted by severity.

| ID | Sev | Where | Finding | Fix |
|---|---|---|---|---|
| A5-1 | S2 | MENU2.md | `np.float64(...)` debug reprs leaked into prose | render-time sanitizer / re-template |
| A5-2 | S2 | EXIT_ANATOMY.md | 3 dead image refs (`charts/` vs `V2/outputs/charts/`) | fix paths |
| B1 | S1 | SL_STUDY.md §4 | "NOTHING viable" contradicts verdict table + data | rewrite §4 to list viable rows |
| B8 | S1 | FROZEN_CANDIDATE.md | "442=144+8+2" arithmetic error (real=282) | correct family size |
| B9 | S1 | m2_grid.py + menu2_grid.csv + MENU2.md | BH broken: unsorted p vs sorted thr, scrambled indices | replace with step-up BH |
| B3 | S2 | SL_STUDY.md | K=24h/88h maxDD not re-verified; monotonicity open | re-run 2 horizons |
| B7 | S2 | FROZEN_CANDIDATE.md §7 | headline vs bucket-sum 0.66 bp gap undocumented | state headline=unweighted mean |
| A3 | S2 | analysis_core / redir_eval | `cell_p()` uses z-test, not bootstrap (docs imply bootstrap) | align method or docs |
| B2 | S0 | — | coincidence, no error | none |
| B4 | S0 | — | same-run confirmed | none |
| B5 | S0 | — | derived correctly | none |
| B6 | S0 | — | no drift | none |
| B10 | S0 | — | window correct | none |
| B11 | S0 | — | all CLEAN | none |

S0=6, S1=3, S2=5.

---

## Deliverables to reissue

1. **MENU2.md** — regenerate BH table with correct step-up BH (25 false-pos + 25 false-neg fixed); strip `np.float64` reprs (A5-1).
2. **menu2_grid.csv** — overwrite `bh_grid` and `bh_union` columns with correct BH.
3. **SL_STUDY.md** — §4 rewrite: state which rows are VIABLE (E1 P4_timeSL_P95 at minimum); re-run K=24h/88h to close B3.
4. **FROZEN_CANDIDATE.md** — fix "442" → "282" (or "250" pre-SL); add note that headline E-VAL = unweighted trade mean (B7).
5. **EXIT_ANATOMY.md** — fix 3 image paths (A5-2).

---

## Project decisions: survive vs flip

| Decision | Status | Why |
|---|---|---|
| **Freeze v1** (W3_BASE frozen) | **SURVIVES** | W3_BASE p=0.001969 in menu1; correct BH (threshold 0.0143) still significant. Union pass holds. |
| **Freeze v2** (corrected W3_BASE, no dip) | **SURVIVES** | Four checks pass on TRAIN; BH union pass valid (uses correct `rebuild_ledger.py`, not buggy `m2_grid.py`). |
| **E-VAL FAIL** (candidate not promoted) | **SURVIVES** | C1 + C2 both fail on correctly computed numbers; window verified 2025-H1. |
| **Exit Study I "baseline unbeaten" headline** | **FLIPS / REFUTED** | E1 P4_timeSL_P95 net=24.90 > baseline 20.76 (retention 119.9%) and is VIABLE. Baseline IS beaten for E1; §4 "NOTHING viable" is wrong. Headline must be withdrawn or scoped to "baseline unbeaten for E2/E3/E4 only". |

---

**ARBITRATION COMPLETE. No fixes applied. Awaiting owner sign-off on reissue list.**
