# FROZEN CANDIDATE — E1 A_disaster_P99_9

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
| **Target (TP)** | body_top + **1.5 × wick_gap** (baseline) |
| **Exit** | TP touch **or** time stop at **K=192 bars (~4 days)** |
| **Price Stop** | **Disaster Stop** — hard stop at P99.9 of winners' MAE = 43.3 wick_gap (extremely wide, hits <0.1% of winners) |
| **Cost Model** | Flat 15 bps round-trip |

**Spec Hash:** `E1|30m|W2_NODIP|A_disaster_P99_9|TP_1.5x|disaster_stop=P99.9_winners_MAE=43.3wg|K=192|15bps`

---

## 2. TRAIN Metrics (2022-09-01 → 2024-12-31, from `keepn_study.csv`)

| Metric | Value |
|--------|-------|
| n trades | **6,420** |
| Win rate | **90.5%** |
| Net/trade @ 15bps | **+20.7 bps** |
| Monthly net | ~+4,750 bps |
| Max DD (2% stake) | **16.3%** |
| Worst trade | **-5,273 bps** |
| Median hold | 2.5 hours |
| BH significant | **True** (p=0.0002) |
| keepn_improve | False |
| keepn_defend | **True** |

---

## 3. E-VAL Metrics (2025-10-01 → 2026-06-30, 9-month window)

| Metric | Value |
|--------|-------|
| n trades | **1,160** |
| Win rate | **87.0%** |
| Net/trade @ 15bps | **+49.0 bps** |
| Max DD (2% stake) | **3.48%** |
| Worst trade | **-2,038 bps** |
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