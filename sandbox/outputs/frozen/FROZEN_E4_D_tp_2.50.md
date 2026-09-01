# FROZEN CANDIDATE — E4 D_tp_2.50

**Frozen:** 2026-09-01 (this session)
**Owner:** User (direct FIRE instruction)
**Status:** FROZEN pending E-LOCKBOX

---

## 1. Frozen Spec Definition

| Field | Value |
|-------|-------|
| **Asset / Venue** | SOLUSDT / Bybit USDT-perp |
| **Timeframe** | 4h |
| **Signal** | W3_NODIP — upper-wick bps ≥ 90 bps (W3 = 6×RT floor), no dip filter |
| **Direction** | Buy only |
| **Entry** | Market, next bar open |
| **Target (TP)** | body_top + **2.5 × wick_gap** |
| **Exit** | TP touch **or** time stop at **K=24 bars (~4 days)** |
| **Price Stop** | NONE |
| **Cost Model** | Flat 15 bps round-trip |

**Spec Hash:** `E4|4h|W3_NODIP|D_tp_2.50|body_top+2.5x_wick|K=24|no_SL|15bps`

---

## 2. TRAIN Metrics (2022-09-01 → 2024-12-31, from `keepn_study.csv`)

| Metric | Value |
|--------|-------|
| n trades | **1,470** |
| Win rate | **70.6%** |
| Net/trade @ 15bps | **+73.7 bps** |
| Monthly net | ~+3,867 bps |
| Max DD (2% stake) | **9.5%** |
| Worst trade | **-6,859 bps** |
| Median hold | 40.0 hours |
| BH significant | **True** (p=6e-05) |
| keepn_improve | **True** |
| keepn_defend | False |

---

## 3. E-VAL Metrics (2025-10-01 → 2026-06-30, 9-month window)

| Metric | Value |
|--------|-------|
| n trades | **291** |
| Win rate | **55.0%** |
| Net/trade @ 15bps | **+40.7 bps** |
| Max DD (2% stake) | **2.85%** |
| Worst trade | **-2,315 bps** |
| **C1** (net > 0 & point ≥ 30 bps) | **PASS** |
| **C2** (worst BTC regime > -15 bps) | **PASS** (heuristic) |

---

## 4. E-LOCKBOX Protocol (Locked — One Shot)

**Window:** 2025-07-01 → 2026-06-30 (full 12-month reserved window)

**Pass Criteria (all must hold):**
1. **Net expectancy @ 15bps:** Bootstrap CI lower bound > 0 (B=2000, seed=42) **AND** point estimate ≥ 30 bps
2. **Worst BTC-regime bucket:** Net > −15 bps

**Sizing:** 2% stake per trade, overlapping positions.

---

## 5. Owner Sign-Off

**I, the owner, confirm this spec is frozen exactly as defined above. No changes after this line.**

_Signed: _________________ Date: _________________