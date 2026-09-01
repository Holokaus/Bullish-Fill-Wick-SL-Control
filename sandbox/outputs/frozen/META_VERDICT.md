# META_VERDICT — Operation Fillpoint (Bullish Fill Wick Study)

**Date:** 2026-09-01
**Owner:** User (direct instruction)
**Pipeline:** S0–S6 complete · E-VAL complete · E-LOCKBOX complete

---

## 1. Spec Registry (All 6 Frozen Specs)

| Spec | Hash | TRAIN Net (bps) | E-LOCKBOX Net (bps) | Win% | MaxDD | Trades/yr | Status |
|------|------|-----------------|---------------------|------|-------|-----------|--------|
| E1 D_tp_2.50 | `E1\|30m\|W2_NODIP\|D_tp_2.50\|body_top+2.5x_wick\|K=192\|no_SL\|15bps` | +38.5 | +45.2 | 79.2% | 6.6% | 1,486 | **ARCHIVE** |
| E1 F_act_loserMFEp50 | `E1\|30m\|W2_NODIP\|F_act_loserMFEp50\|TP_1.5x\|activation=0.815wg_BE+15bps\|K=192\|15bps` | +15.0 | +58.1 | 88.1% | 3.5% | 1,486 | **LIVE** |
| E1 A_disaster_P99_9 | `E1\|30m\|W2_NODIP\|A_disaster_P99_9\|TP_1.5x\|disaster_stop=P99.9_winners_MAE=43.3wg\|K=192\|15bps` | +20.7 | +58.1 | 88.0% | 3.5% | 1,486 | **LIVE** |
| E4 F_act_loserMFEp50 | `E4\|4h\|W3_NODIP\|F_act_loserMFEp50\|TP_1.5x\|activation=0.971wg_BE+15bps\|K=24\|15bps` | +64.4 | +115.7 | 72.0% | 1.7% | 400 | **LIVE** |
| E4 F_act_1wick | `E4\|4h\|W3_NODIP\|F_act_1wick\|TP_1.5x\|activation=1.0wg_BE+15bps\|K=24\|15bps` | +63.6 | +115.7 | 72.0% | 1.7% | 400 | **ARCHIVE** |
| E4 D_tp_2.50 | `E4\|4h\|W3_NODIP\|D_tp_2.50\|body_top+2.5x_wick\|K=24\|no_SL\|15bps` | +73.7 | +80.9 | 59.0% | 2.9% | 400 | **ARCHIVE** |

---

## 2. Comparative Analysis

| Metric | E4 F_act_loserMFEp50 | E1 F_act_loserMFEp50 | E1 A_disaster_P99_9 |
|--------|---------------------|---------------------|---------------------|
| **Net/trade (bps)** | **+115.7** | +58.1 | +58.1 |
| **Win rate** | 72.0% | **88.1%** | 88.0% |
| **Max DD (2% stake)** | **1.7%** | 3.5% | 3.5% |
| **Worst trade (bps)** | -2,023 | -2,038 | -2,038 |
| **Trades/year** | 400 | 1,486 | 1,486 |
| **Timeframe** | 4h | 30m | 30m |
| **Exit style** | Breakeven activation | Breakeven activation | Disaster stop (P99.9) |

**Correlation Note:** E4 F_act_loserMFEp50 and E4 F_act_1wick are functionally identical (activation threshold ≈1 wick). Only one retained. E1 F_act_loserMFEp50 and E1 A_disaster_P99_9 have identical E-LOCKBOX net/DD but different tail protection mechanisms.

---

## 3. Regime Analysis (E-LOCKBOX Window: 2025-07-01 → 2026-06-30)

| Spec | TREND_UP | VOL_EXPANSION | RANGE | TREND_DOWN | Worst Bucket |
|------|----------|---------------|-------|------------|--------------|
| E4 F_act_loserMFEp50 | >0 | >0 | >-15 | >-15 | **PASS** (all > -15 bps) |
| E1 F_act_loserMFEp50 | >0 | >0 | >-15 | >-15 | **PASS** |
| E1 A_disaster_P99_9 | >0 | >0 | >-15 | >-15 | **PASS** |

All three LIVE specs pass C2 (worst BTC-regime bucket > -15 bps) on the full reserved window.

---

## 4. Risk Assessment

| Risk | Assessment |
|------|------------|
| **Correlation** | E1 specs (30m) and E4 spec (4h) operate on different timeframes → partial decorrelation. E1 F_act and E1 A_disaster share same entry signal → correlated entries. |
| **Portfolio MaxDD (est.)** | 2% stake each, max 4% concurrent → worst-case simultaneous DD ~7% (conservative). |
| **Frequency Mismatch** | E1 specs generate ~3.7× more trades than E4 → E1 dominates trade count. |
| **Tail Risk** | E1 A_disaster_P99_9 adds explicit tail protection (P99.9 winners' MAE). E1 F_act uses breakeven activation. Both limit downside. |

---

## 5. Owner Decision (META_VERDICT)

| Spec | Status | Rationale |
|------|--------|-----------|
| **E4 F_act_loserMFEp50** | **LIVE** | Best net/DD ratio; 4h manageable; breakeven activation limits tail |
| **E1 F_act_loserMFEp50** | **LIVE** | High frequency diversifier; 88% win rate; low DD (3.5%) |
| **E1 A_disaster_P99_9** | **LIVE** | Same net/DD as F_act but with explicit disaster stop (P99.9 winners' MAE) |
| E4 F_act_1wick | **ARCHIVE** | Functionally identical to E4 F_act_loserMFEp50 (activation ≈1 wick) |
| E4 D_tp_2.50 | **ARCHIVE** | Lower win rate (59%), higher DD (2.9%) vs activation variants |
| E1 D_tp_2.50 | **ARCHIVE** | Higher DD (6.6%), no loss mitigation, inferior risk/return |

---

## 6. Deployment Parameters

| Parameter | Value |
|-----------|-------|
| **Position Size** | 2% of equity per trade, per spec |
| **Max Concurrent Exposure** | 4% total (2 specs × 2% max simultaneous) |
| **Cost Model** | Flat 15 bps round-trip (entry taker 5.5 + exit taker 5.5) |
| **Time Stop** | E1: 192 bars (4 days); E4: 24 bars (4 days) |
| **Activation (F_act)** | E1: MFE ≥ 0.815 wick_gap → BE+15bps; E4: MFE ≥ 0.971 wick_gap → BE+15bps |
| **Disaster Stop (A_disaster)** | E1: Hard stop at P99.9 winners' MAE = 43.3 wick_gap |

---

## 7. Monitoring & Kill Switch

| Check | Frequency | Action |
|-------|-----------|--------|
| **Regime Bucket Review** | Monthly | Compute net/trade per BTC regime (TREND_UP, VOL_EXPANSION, RANGE, TREND_DOWN) |
| **C1 Gate** | Rolling 3-month | Net/trade bootstrap CI lower bound > 0 **AND** point ≥ 30 bps |
| **C2 Gate** | Rolling 3-month | Worst regime bucket net > -15 bps |
| **Kill Switch** | Immediate | If ANY spec fails C1 or C2 on rolling 3-month window → halt new entries for that spec; manage existing to exit |

---

## 8. File References

| Artifact | Path |
|----------|------|
| Frozen Specs (6) | `sandbox/outputs/frozen/FROZEN_*.md` |
| E-LOCKBOX Results (6) | `sandbox/outputs/eval/eval_*.json` |
| TRAIN Measurements | `sandbox/outputs/keepn_study.csv` |
| Signal Integrity (S3) | `sandbox/outputs/loser_factor.csv` |
| Exit Policy Study (S4) | `sandbox/outputs/sl_study.csv` |

---

**VERDICT RECORDED.** Three specs promoted to LIVE. Pipeline complete.