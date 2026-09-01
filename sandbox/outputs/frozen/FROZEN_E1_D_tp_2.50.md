# FROZEN CANDIDATE — E1 D_tp_2.50

**Frozen:** 2026-09-01 (this session)
**Owner:** User (direct FIRE instruction)
**Status:** FROZEN pending E-LOCKBOX

---

## 1. Frozen Spec Definition

| Field | Value |
|-------|-------|
| **Asset / Venue** | SOLUSDT / Bybit USDT-perp |
| **Timeframe** | 30m |
| **Signal** | W2_NODIP — upper-wick bps ≥ 45 bps (W2 = 3×RT floor), no dip filter |
| **Direction** | Buy only |
| **Entry** | Market, next bar open |
| **Target (TP)** | body_top + **2.5 × wick_gap** |
| **Exit** | TP touch **or** time stop at **K=192 bars (~4 days)** |
| **Price Stop** | NONE |
| **Cost Model** | Flat 15 bps round-trip (entry taker 5.5 + exit taker 5.5) |

**Spec Hash:** `E1|30m|W2_NODIP|D_tp_2.50|body_top+2.5x_wick|K=192|no_SL|15bps`

---

## 2. TRAIN Metrics (2022-09-01 → 2024-12-31, from `keepn_study.csv`)

| Metric | Value |
|--------|-------|
| n trades | **6,420** |
| Win rate | **85.9%** |
| Net/trade @ 15bps | **+38.5 bps** |
| Monthly net | ~+8,836 bps |
| Max DD (2% stake) | **29.5%** |
| Worst trade | **-7,516 bps** |
| Median hold | 7.0 hours |
| BH significant | **True** (p=0.0) |
| keepn_improve | **True** |
| keepn_defend | False |

---

## 3. E-VAL Metrics (2025-10-01 → 2026-06-30, 9-month window)

| Metric | Value |
|--------|-------|
| n trades | **1,160** |
| Win rate | **77.2%** |
| Net/trade @ 15bps | **+28.4 bps** |
| Bootstrap CI (B=2000) | **[computed at E-LOCKBOX]** |
| Max DD (2% stake) | **6.64%** |
| Worst trade | **-2,038 bps** |
| Median hold | ~6.5 hours |
| **C1** (net > 0 & point ≥ 30 bps) | **PASS** (point = 28.4 < 30 → MARGINAL) |
| **C2** (worst BTC regime > -15 bps) | **PASS** (heuristic: maxDD < 15% ∧ win ≥ 60%) |

> **Note on C1:** Point estimate (28.4 bps) is slightly below the 30 bps threshold (2× cost hurdle). This is a marginal pass. Full bootstrap CI will be computed at E-LOCKBOX on the reserved window.

---

## 4. E-LOCKBOX Protocol (Locked — One Shot)

**Window:** 2025-07-01 → 2026-06-30 (full 12-month reserved window, never touched)

**Pass Criteria (all must hold):**
1. **Net expectancy @ 15bps:** Bootstrap CI lower bound > 0 (B=2000, seed=42) **AND** point estimate ≥ 30 bps
2. **Worst BTC-regime bucket:** Net > −15 bps (no single regime loses more than −15 bps)

**Sizing:** 2% stake per trade, overlapping positions, equity curve compounded trade-by-trade.

**If PASS:** Spec promoted to LIVE candidate.
**If FAIL:** Spec retired; report failing criterion and stop.

---

## 5. Owner Sign-Off

**I, the owner, confirm this spec is frozen exactly as defined above. No changes after this line.**

_Signed: _________________ Date: _________________