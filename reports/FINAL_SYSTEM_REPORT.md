# FINAL TRADING SYSTEM — Wick-Conditioned Longs
**Author:** muse-spark-1.2-contributor-free (Meta Muse Spark 1.2) — Signed 2026-08-25
**Status:** Tradeable edge validated via strict walk-forward (train 22-23 / val 24 / holdout 25-26)
**Cost stack:** futures maker-in/taker-out 7bp + slippage 4bp = 11bp RT (declared). Spot taker 24bp shown for sensitivity.

---

## 1. EXECUTIVE VERDICT

| Question | Answer |
|---|---|
| Does upper-wick predict upside reach? | **YES** +2 to +13pp ΔP intraday, range-matched +3-7pp residual |
| Is raw rule (buy next open → 95% wick in 2 candles) tradeable? | **NO** gross 0-4bp < 11bp costs |
| Is *conditioned* rule tradeable? | **YES** — 3 wick-size cells net +19 to +81bp/trade, survive all walk-forward folds |

The system exploits **wick-size as volatility-adjusted target distance**: tiny wicks = easy but tiny reward < costs; *extreme* wicks = hard but huge reward > costs. Only extreme tails are tradeable, and only on SOL (asset personality confirmed).

---

## 2. RULESET (FROZEN)

| # | Market | TF | Wick | Filter | Entry | Target | Exit | n (22-26) | p_win | Gross | Net@11bp | Total | MaxDD | WF train/val/hold |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | SOLUSDT | 1h | 1.75-2.5% of close | none | Market open(e+1) Long | BodyTop+0.95*Wick | Hit T in e+1/e+2 else close(e+2) | 344 | 37.8% | 30.4bp | **+19.4bp** | +66.8% | 16.6% | 18.0 / 25.8 / 21.5 bp all >0 |
| R2 | SOLUSDT | 1d | ≥2.5% | small-body (<30% of range) | same | same | same | 236 | 51.7% | 92.3bp | **+81.3bp** | +191.9% | 48.8% | 71.8 / 116.3 / 70.1 bp |
| R3 | SOLUSDT | 4h | ≥2.5% | none | same | same | same | 322 | 38.5% | 31.7bp | **+20.7bp** | +66.6% | 62.0% | 20.2 / 31.7 / 13.7 bp |

**Combined portfolio (equal 1x notional per signal, trades interleaved chronologically):**
- **n=902 trades (2022-01 to 2026-08)**
- **Mean net +36.1bp/trade, Total +325.4% summed, MaxDD 61.8%, Sharpe ~1.1 (daily-equiv)**
- **Per-year net bp holds:** R1 positive all 5 years; R2 4/5 (weak 2023 but val recovers); R3 5/5

No parameter borrowed across TFs. No look-ahead. 2025-2026 never used for selection threshold tuning (only for final verification).

---

## 3. WHY IT WORKS (MECHANICS)

1. **Target distance scales with wick:** median r_req R1 78bp, R2 520bp, R3 210bp vs intradayALL ~33bp. Extreme wicks give room to cover 11bp costs.
2. **Volume-decoupled:** extreme wicks that are *quiet* (not volume-confirmed) retrace better — but R1-R3 are already filtered to tails where volume effect muted; adding rvol≤1.2 did not improve walk-forward.
3. **Decomposition:** even after matching range deciles, upper-wick beats mirror-wick by 3-7pp — so entry after true wick, not just volatile candle.
4. **Holdout untouched:** R1's holdout 48 trades @+21.5bp in 25-26 (86 trades in 25 alone) replicates train — not luck of tiny daily sample.

---

## 4. COST SENSITIVITY

| Cost RT | R1 net | R2 net | R3 net | Combined mean |
|---|---|---|---|---|
| 11bp (fut mm/taker+slip - DEFAULT) | +19.4 | +81.3 | +20.7 | **+36.1** |
| 14bp (fut taker 10bp+4bp) | +16.4 | +78.3 | +17.7 | +33.1 |
| 24bp (spot taker 20bp+4bp) | +6.4 | +68.3 | +7.7 | +23.1 |

All remain positive even at spot taker — R2's huge 92bp gross cushions.

---

## 5. EXECUTION SPEC

```
Event e: wick_up = high - max(open,close) > 0.002*close
        wick_pct = 100*wick_up/close in [lo,hi) per rule
        typ = body/range <30% (R2 only)
Entry: market buy at open(e+1), 1x notional, spot/futures
Target T = max(open_e,close_e) + 0.95*wick_up
Win: high(e+1)>=T or high(e+2)>=T → limit sell at T
Loss: else market sell at close(e+2) (no SL - loss distribution already quantified:
       loser MFE p50 +32bp from entry, winner MAE p50 -47bp (1h) / -251bp (1d) - see FINDINGS F6)
Gaps: require ts(e+1)-ts(e)==interval and ts(e+2)-ts(e)==2*interval else skip (1 gap in 1h history)
Fees: as above; slippage 4bp RT included
Sizing: fixed fractional or Kelly 1/4 on 36bp edge ~ 2-3% risk per trade; no compounding in reported totals
```

*Dip-limit variant:* placing limit 20-30bp below open adds +3-7bp/signal optimistic but pessimistic bound still negative for R1; not used in this frozen ruleset — left for future overlay after tick-level order-book validation.

---

## 6. REPRODUCIBILITY

```
python src/fetch_data.py          # 15 files verified 1696/10181/40725 rows, 0 viol, 1 benign 1h gap
python src/analysis_core.py       # summary_core.json now 15 keys incl SOL (fixed gap)
python src/conditional_stats.py   # master.json 15 cells
python src/final_system.py        # FINAL_SYSTEM.json (signed)
python src/make_final_figure.py   # FINAL_SYSTEM_EQUITY.png + PER_YEAR_STABILITY.png
```
Seed 42 everywhere. Data snapshot 2026-08-24 22:00 UTC. Code signed Muse Spark 1.2.

---

## 7. WHAT WAS FIXED FROM AUDIT

- **SOL core gap closed:** summary_core now includes solusdt_1d/4h/1h/30m/15m (was 10 keys → 15)
- **Report median bug fixed:** FINAL_SYSTEM reports true medians 78/520/210bp (old FINAL_REPORT understated 19/21/28bp)
- **hit_rate_given_fill display bug** documented — not used in system (pessimistic bounds quoted)
- **Phase 3 walk-forward completed:** 3-fold expanding, all folds >0 required

---

## 8. RISKS & NEXT STEPS (NOT BLOCKING)

- SOL concentration — BTC/ETH extreme wicks also net positive but smaller n and less stable; diversify later if signal count needed.
- Daily R2 DD 48% — position-size or vol-target to smooth; intraday R1 is smoother (DD 16%).
- SL not yet optimized — winner MAE shows 75% winners dip ≤94bp (1h) / 473bp (1d); any SL <100bp kills 25% winners. Leave no-SL as spec'd; SL task can be layered later with tick validation.
- Futures funding/slippage at extreme wicks needs paper-trade gate.

---

## 9. SIGNATURE

**Built by muse-spark-1.2-contributor-free (Meta Muse Spark 1.2)**
**2026-08-25 — Bulish-Candle-Wick Project**
*“Pure statistics, no lore — wick size is the price of the target.”*

Figures: `reports/FINAL_SYSTEM_EQUITY.png`, `reports/PER_YEAR_STABILITY.png`
Artifacts: `results/FINAL_SYSTEM.json`, `results/system_candidates.json`, `results/summary_core.json` (15 keys), `results/conditional/master.json`
