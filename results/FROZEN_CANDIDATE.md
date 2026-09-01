# FROZEN CANDIDATE v2 — OPERATION FILLPOINT (pre-E-VAL, post four-checks, CORRECTED)

> v2 corrects a labeling error in the first v2 draft: the prior draft froze the DIP variant
> (wick≥90 + 24h-dip filter, n=370) but called it W3_BASE. The true W3_BASE has NO dip filter
> (n=1470). This file freezes the CORRECT row. E-VAL (2025-01-01 → 2025-06-30) remains a
> ONE-SHOT on this exact spec. E-LOCKBOX unfired.

**Frozen (primary):** `W3_BASE` — wick ≥ 90 bps, **NO dip filter**
**Checked alternate:** `W1_DIP` (wick ≥ 22.5 bps + dip) — retained, not switched
**Decision rule applied (pre-declared):** W3_BASE frozen if it passes all four checks;
W1_DIP only if W3_BASE fails AND W1_DIP passes all four; any switch disclosed → **no switch.**
**Status:** FROZEN pending sign-off. All four checks run on TRAIN only (2022-09-01 → 2024-12-31), SOL-4h, Bybit perp.

---

## 1. Frozen spec (W3_BASE — corrected)

| field | value |
|---|---|
| asset / venue | SOLUSDT / Bybit USDT-perp |
| timeframe | 4h |
| signal (color-agnostic) | ANY candle whose upper-wick bps ≥ **90 bps** (W3 = 6×RT floor) |
| filter | **NONE** (dip filter deliberately absent) |
| direction | buy only |
| entry | market, next bar open |
| target | body_top + **1.5 × wick_gap** |
| exit | TP touch **or** time stop at **K=24 bars (~4 days)** |
| price stop | NONE |
| circuit breaker | NONE at this stage (deferred exit-tuning pass) |
| cost model | per-mechanic: entry taker 5.5 bps + exit maker 2.0 (if TP) / taker 5.5 (if time-stop) |

TRAIN results (n = **1470 trades**, 2022-09-01 → 2024-12-31):

| metric | value |
|---|---|
| win rate | **79.0%** |
| avg net / trade (true cost) | **+54.7 bps** [24.5, 83.8] |
| avg net / trade @ MKT_MKT 15bps | +48.0 bps |
| avg net / trade @ PB_PB 4bps | +59.0 bps |
| avg net / trade @ PB_MKT 11.5bps | +51.5 bps |
| trades / month | ~52.5 |
| monthly net expectancy | ~+2,870 bps (additive; 52.5 × 54.7) |
| funding-adjusted net / trade | **+67.3 bps** [39.1, 94.3] (TRAIN longs paid +12.6 bps avg) |

---

## 2. Four checks (TRAIN, q=0.05)

| check | W3_BASE (primary) | W1_DIP (alternate) | pass? |
|---|---|---|---|
| 1. Cost sensitivity (4 / 11.5 / 15 bps) | +59 / +51 / +48 bps, all >0 | +57 / +49 / +46 bps, all >0 | both PASS |
| 2. Matched control (ΔP wick increment) | ΔP = **+61.4 bps** [18.2, 104.7] | ΔP = +24.9 bps [-13.0, 62.3] | W3 PASS · W1 BORDERLINE |
| 3. Funding (4h, real Bybit 8h history) | net **+67.3** bps (tailwind) | net +74.1 bps | both PASS |
| 4. Union-family BH — honest 442-cell | **PASS** (rank 64/442) | **PASS** (rank 61/442) | both PASS |
| 4. Union-family BH — crude 6526-cell* | FAIL | FAIL | both FAIL |

\* Crude family reconstructs W5/W6/Track-1 p-values from binary `sig` flags (0.01/0.5) because
those scans did not store continuous p-values. Methodologically unsound; reported for transparency.
The **honest** union family uses only cells with real computed p-values (W7's 144 + menu's 8 + 2
candidates = 442).

**Verdict under the pre-declared rule:** W3_BASE now passes **all four** checks (cost ✓, matched-control
✓ with CI fully above zero, funding ✓, union-BH ✓). W1_DIP passes 3 of 4 (matched-control borderline).
→ **W3_BASE is frozen as primary; no switch.** Matched-control ΔP = +61.4 bps [18.2, 104.7] confirms the
wick itself contributes an independently significant increment over matched non-wick buys.

---

## 3. Honest limitations (travel with the candidate)

1. **Funding tailwind is TRAIN-specific.** Longs were paid positive funding over 4h holds in
   2022–2024 (+12.6 bps avg on W3_BASE). Favorable regime artifact; could reverse out-of-sample.
   Funding is charged, not assumed away.
2. **No price stop.** The concept is stop-free; gap risk is bounded only by the 24-bar time stop.
   The reserved down-market window (2025-07 → 2026-06) is excluded and may behave differently.
3. **Selection multiplicity.** Even the honest union-BH pass (442 cells) means this cell is one of
   ~110 significant cells in the family — not unique. E-VAL is the real test.
4. **Matched control uses bootstrap CI** on ~1:1 paired non-wick controls (same color, same range
   decile); for W3_BASE the control also matches the no-dip population. ΔP is win-the-wick increment.

---

## 4. Reproducibility

- scripts: `V2/scripts/redir_w2_checks.py` (four checks; `run_row(name, wick_thr, use_dip)` —
  W3_BASE called with `use_dip=False`) · `V2/scripts/redir_w1_menu.py` (menu)
- data: `SOLUSDT-FUTURES-2022-2026-4h.csv` (RAW_DIR) · funding `phase36/phase38/data/derivatives/SOLUSDT/funding_rate.csv`
- windows: `src/lib/time_gates.py` (TRAIN asserted holdout-excluded; reserved window ≥ 2025-07-01 untouched)
- atlas cuts: `V2/outputs/atlas/atlas_cuts.json` (TRAIN-frozen, SHA-256
  `180aa0c9d0f5c07ec6c0468aaae913b97564183ad40983049e4f034229083cda`)
- outputs: `V2/outputs/redir_w1_menu.csv`, `w5_nosl_economics.csv`, `w6_stop_study.csv`, `w7_sol4h_corrected.csv`

---

## 5. Owner action required

Sign off and I will fire E-VAL (one shot) on 2025-01-01 → 2025-06-30 with this exact spec.
If E-VAL passes, then E-LOCKBOX (one shot) on 2026-07-01 → 2026-08-26.
Spec is changeable only before sign-off.

---

## 6. E-VAL protocol (locked at sign-off — procedure only, no spec changes)

**One-shot window:** 2025-01-01 → 2025-06-30. Run ONCE. No peeking, no re-runs, no parameter changes.

### 6.1 Pass criteria (all must hold)
1. **Net expectancy (15bps flat config):** bootstrap CI lower bound > 0
   (B=2000 resamples, seed=42) **AND** point estimate ≥ 30 bps (2× the 15bps cost hurdle, single-asset rule).
2. **Worst BTC-regime bucket:** net > −15 bps (no single regime bucket may lose more than −15 bps).

### 6.2 Sizing convention (E-VAL equity curve = menu convention, so TRAIN and E-VAL are comparable)
- **Stake:** 2% of equity per trade.
- **Overlapping positions:** allowed (multiple open trades at once; each sized at 2% of current equity).
- **Reporting:** per-trade additive net bps; equity curve compounded trade-by-trade at the 2% stake;
  max drawdown reported on that curve.
- **Cost config for the headline expectancy:** the honest **flat 15 bps MKT_MKT** config (entry taker 5.5 + exit taker 5.5), matching the menu's headline. Per-mechanic and 4bps sensitivity also reported.

### 6.3 Out-of-sample discipline
- The reserved down-market window (2025-07-01 → 2026-06-30) is NEVER touched by E-VAL.
- If E-VAL passes → fire E-LOCKBOX (one shot) on 2026-07-01 → 2026-08-26.
- If E-VAL fails any criterion → candidate is NOT promoted; report the failing criterion and stop.

---

## 7. E-VAL RESULT (one-shot, fired 2026-08-27) — **FAIL, candidate NOT promoted**

Window: 2025-01-01 → 2025-06-30 (held out from all training/selection). BTC-regime proxy derived
from BTCUSDT 1h (no native 4h/BTC-regime file); bucketed per trade entry. Sizing 2% stake,
overlapping, per-trade additive (menu convention).

| metric | value |
|---|---|
| n trades | **1079** |
| win rate (15bps) | 79.1% (held vs TRAIN 79.0%) |
| net/trade @15bps | **−26.1 bps**  CI[−51.9, −0.6] |
| net/trade @4bps | −15.8 bps |
| net/trade true-cost | −19.9 bps |
| 2% stake maxDD | 10.2% |
| **C1** net CI lo>0 & point≥30 | **FAIL** (lo=−51.9<0; point=−26.1<30) |
| **C2** worst BTC bucket > −15bps | **FAIL** (TREND_DOWN = −75.9 bps) |

BTC-regime buckets (net15 bps): TREND_UP +4.6 (n=235) · VOL_EXPANSION +29.9 (n=261) ·
RANGE −59.8 (n=403) · TREND_DOWN −75.9 (n=180).

**Interpretation:** win rate held (~79%) but net flipped negative out-of-sample. The edge degraded
specifically in RANGE and TREND_DOWN regimes, where time-stop exits during adverse 4h holds produced
larger losses than the filled wick-gap wins. This is the multiplicity/regime-risk the holdout existed to
catch. **The frozen spec is NOT promoted. E-LOCKBOX is NOT fired.** Per §6.3, reporting stops here.

**Disposition options (owner decision, post-sign-off):** (a) accept the fail and retire/restart;
(b) the wick concept still shows positive net in TREND_UP/VOL_EXPANSION regimes — a regime-gated
variant is a separate, later pass; (c) investigate why wick firing rate rose (1079 vs ~315 expected
for 6mo) in 2025-H1. None of these mutate the frozen spec retroactively.
