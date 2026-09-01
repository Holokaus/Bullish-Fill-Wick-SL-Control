# FINAL REPORT — Upper-Wick Continuation Study
**Data:** BTCUSDT & ETHUSDT spot, Binance official archives + REST tail.
Daily/4H/1H from 2022-01-01 · 30m/15m from 2024-01-01 → 2026-08-24. Zero gaps (one benign 1h break excluded by contiguity rule).
**Pre-registration:** locked in `results/pre_registration.md` before any outcome was computed.

---

## VERDICT

| Question | Answer |
|---|---|
| Does an upper-wick candle predict elevated short-horizon upside reach? | **YES — real, replicated, stationary informational edge** |
| Is the edge *wick-specific* (not just volatility)? | **YES — survives range-matched controls** |
| Is the rule "buy next open, target 95% of wick within 2 candles" **tradeable**? | **NO — gross edge (+0…+4 bp/trade) < realistic costs (10–24 bp)** |

The concept is scientifically confirmed and commercially insufficient, exactly as specified. Details below.

---

## 1. The measured fact

Event = upper wick > 0.2% of close. Trade = long next open, win if high(e+1) or high(e+2) ≥ body_top + 95%·wick.

**ΔP = P(win | event) − P(win | non-event candles given the same required return)**, day-cluster bootstrap CI:

| Cell | n events | P(win\|event) | P(control) | ΔP | 95% CI | Sig? |
|---|---|---|---|---|---|---|
| BTC 1d | 1508 | 59.8% | 63.6% | **−3.8pp** | [−8.8, +1.1] | no |
| BTC 4h | 6188 | 53.9% | 51.6% | **+2.3pp** | [+0.4, +4.2] | yes |
| BTC 1h | 12698 | 48.3% | 40.9% | **+7.4pp** | [+6.2, +8.5] | yes |
| BTC 30m | 7622 | 45.1% | 35.3% | **+9.8pp** | [+8.5, +11.2] | yes |
| BTC 15m | 7534 | 41.1% | 28.0% | **+13.1pp** | [+11.8, +14.4] | yes |
| ETH 4h | 7308 | 56.0% | 54.4% | +1.5pp | [−0.4, +3.5] | no |
| ETH 1h–15m | … | … | … | +5.3 … +8.8pp | all CIs > 0 | yes |

- **Replication:** 8 of 10 cells significant, both symbols, direction-consistent everywhere except daily (where the effect is absent/negative).
- **Stationarity:** per-year ΔP positive in every year 2022→2026 where significant (e.g. BTC 15m: +9.9, +15.6, +14.3 pp across 2024/25/26). No year flips sign.
- **Holdout 2026 YTD** (untouched during development): BTC 15m ΔP = +14.3pp, 30m = +10.5pp, 1h = +8.1pp. The effect did not decay out-of-sample.

## 2. What the wick actually is (decomposition)

Bin ALL candles into range deciles; compare reach probability *within* decile:

| Group | Description | Typical result |
|---|---|---|
| A_event | upper wick > 0.2%·close | highest reach in every decile |
| B_mirror | lower-wick-dominant, not event | ~3–5pp below A |
| C_body | body-dominant candle | ~7–13pp below A |

Two-layer truth:
1. **~70–80% of the effect is volatility persistence** — wide candles follow wide candles regardless of geometry (reach prob rises ~0.25→0.50 across range deciles for every group).
2. **A genuine wick-specific residual of ~3–7pp remains**, uniform across range bins, both coins, all intraday TFs. An upper wick means the e+1/e+2 window reaches upward more than range-matched peers — including mirror-wick ones. This kills the pure-volatility explanation.

Secondary regularities: bullish events >> bearish events (BTC 1h: 57.9% vs 37.2%); small wicks fill easier than large ones on intraday (monotone declining bucket curve); daily TF is a different world (no positive edge; bull-only daily hit rate 73–74% but driven by drift, expectancy still ≤ 0 gross on ETH).

## 3. Why it is not tradeable as specified — the arithmetic

Median required move to target: **~19 bp (1h) / ~21 bp (15m) / ~28 bp (4h)**.
Cost stack per round trip: spot taker 20 bp + slippage 4 bp = 24 bp · futures taker 14 bp · futures maker-in/taker-out 9 bp.
Gross expectancy (zero costs): BTC best cells **+2 to +4 bp** (4h ALL +3.7, 1d BULL +3.6); 1h/30m/15m ≈ 0; ETH ≤ 0 everywhere.

Net result: **every variant is negative** — e.g. BTC 1h ALL: −10.2 bp/trade on futures maker/taker; cumulative equity curves decline monotonically over 12k+ trades (see figure). The no-SL time-exit hands back most of the small wins on failures (median loser ≈ −0.21%).

The information is real but the *payoff geometry* is inverted: you risk a full adverse candle to chase a ~0.2% target.

## 4. What could become tradeable (directions, not claims)

1. **Maker entry at the wick tip** (resting sell-limit at High_e filled on a pullback, then long): converts the wick itself into entry discount; different trade — requires its own pre-registered test.
2. **Use the event as a filter/regime feature** inside a larger system (it measurably raises 2-candle up-reach probability) instead of a standalone entry signal.
3. **The pending SL task changes the loss distribution** but cannot alone close a gap where target < costs; targets must get bigger (lower fill %, longer horizon) or fills cheaper.

## 5. Reproducibility

```
src/fetch_data.py     data acquisition + QC          results/events_*.csv      all trades
src/analysis_core.py  stats engine                   results/summary_core.json all statistics
src/decompose.py      range-matched decomposition    results/decomposition.json
src/backtest.py       fee scenarios + equity         results/backtest.json, curves.json
src/make_figure.py    final figure                   reports/final_figure.png
```
Bootstrap seed fixed (42). Pre-registration untouched since commit-time.
