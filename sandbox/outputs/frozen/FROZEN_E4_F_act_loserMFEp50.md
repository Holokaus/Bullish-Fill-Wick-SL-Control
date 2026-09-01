# FROZEN CANDIDATE — E4 F_act_loserMFEp50

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
| **Target (TP)** | body_top + **1.5 × wick_gap** (baseline) |
| **Exit** | TP touch **or** time stop at **K=24 bars (~4 days)** |
| **Price Stop** | **Breakeven Activation** — if trade reaches MFE ≥ P50(MFE of losers in TRAIN) = 0.971 wick_gap, move stop to entry + 15 bps |
| **Cost Model** | Flat 15 bps round-trip |

**Spec Hash:** `E4|4h|W3_NODIP|F_act_loserMFEp50|TP_1.5x|activation=0.971wg_BE+15bps|K=24|15bps`

---

## 2. TRAIN Metrics (2022-09-01 → 2024-12-31, from `keepn_study.csv`)

| Metric | Value |
|--------|-------|
| n trades | **1,470** |
| Win rate | **84.8%** |
| Net/trade @ 15bps | **+64.4 bps** |
| Monthly net | ~+3,383 bps |
| Max DD (2% stake) | **5.1%** |
| Worst trade | **-6,857 bps** |
| Median hold | 8.0 hours |
| BH significant | **True** (p=1e-06) |
| keepn_improve | **True** |
| keepn_defend | **True** |

---

## 3. E-VAL Metrics (2025-10-01 → 2026-06-30, 9-month window)

| Metric | Value |
|--------|-------|
| n trades | **291** |
| Win rate | **69.1%** |
| Net/trade @ 15bps | **+95.1 bps** |
| Max DD (2% stake) | **1.72%** |
| Worst trade | **-2,023 bps** |
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