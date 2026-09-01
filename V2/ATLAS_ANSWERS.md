# OPERATION FILLPOINT — THE ATLAS ANSWERS (W4, TRAIN Sep2022–Dec2024)

Every owner question, answered with measured statistics. Per asset×timeframe independently;
155,000+ big-upper-wick events across 13 series. Full tables: `outputs/w4b_conditions.csv`,
`w4c_economics.csv`, `w4d_inverted_gates.csv`; per-series digest: `logs/w4b.log`.

---

## Q1. Optimal wick length? (dose-response, deciles per series)
YES — measurable and consistent in **13/13 series**: the fill-probability sweet spot is
**deciles 7–8** of uw_frac (~0.42–0.55), NOT the longest wicks.
- BTC-15m: dec7 93.8% / dec8 92.9% / dec10 89.1% fill within 48 bars (q<0.001)
- BTC-1h: dec8 95.0% vs dec10 89.2%
- Decile 7–8 also fills FASTER (median 1 bar vs 2).
- But: optimal length for FILL ≠ for PROFIT (see Q10).

## Q2. Trend-following statistics?
Measured two ways (per series):
- Trailing 24-bar return quintile: falling context (Q0–Q2) fills MORE (BTC-15m: 92.8–93.6%)
  than hot-rally context (Q4: 88.3%, q<0.001). Rallies into strength fail to revisit less.
- SMA50 position: wicks formed BELOW SMA50 fill MORE (BTC-15m 93.5% vs 89.9% above, q<0.001)
  in 12/13 series. Counter-trend wicks are the ones that get filled.

## Q3. Target reached after 1–2 candles?
- **P(fill ≤ 2 bars): 52–57%** in ALL 13 series (median time-to-fill = 2 bars everywhere).
- P(fill ≤ 48 bars): 88–93%. So half of all fills happen almost immediately; the tail is long.

## Q4. Bounces before reaching the target?
Median number of down-crossings of body-bottom BEFORE the up-fill: **0** in all series
(75th pct ≈ 0–1). Meaning: when the fill comes, it usually comes without prior failure —
but when it doesn't fill fast, MAE-before-fill grows (see Q5).

## Q5. Adverse excursion before the fill?
Median dip before fill (from close): 15 bps (5m) → 28–59 bps (15m–1h) → **130+ bps (4h)**.
High-volume events dip deeper (BTC-15m: vol-Q5 median 17 vs 9 bps for vol-Q1).
This is the number that kills tight stops: at 4h, a stop inside −130 bps stops out half the winners.

## Q6. Impact of candle TYPE on entry?
Lower-wick-bearing hammers (type=2, lower shadow ≥ ⅓ range) fill MORE:
BTC-15m 93.3% vs 90.8% plain (q<0.001); body-dominant marubozu-wicks (type=0) are rare (<1%).

## Q7. Influence of the candle BEFORE the event candle?
Real and significant in 13/13: prior BEARISH candle → higher fill rate
(BTC-15m: 93.0% vs 89.9% after prior bullish, q<0.001; ETH-1h: +3.4%; ICP-30m: +3.1%).
A wick printed after a down candle = exhaustion of the dip → better retrace odds.

## Q8. Correlation of event-candle VOLUME?
The strongest single factor found, monotonic in **13/13 series**:
- QUIET volume (Q1–Q2) → highest fill rates (BTC-15m: 94.4%, Δ+3.8pp q<0.001)
- LOUD volume (Q5) → worst fills (BTC-15m 84.5%, Δ−8.8pp; SOL-1h −8.3pp; BTC-1h −8.4pp)
Interpretation: high-volume wick = initiative bought AND sold (churn/top); low-volume wick =
thin probe that nobody defends → price drifts back up through it.

## Q9. Timeframe dependence & per-asset personality?
All effects replicate at 5m/15m/30m/1h/4h — direction identical, magnitudes scale:
MAE-before-fill 15→130+ bps, r24 dispersion 3→235 bps (SOL-4h's train window was a super-bull).
Personalities: SOL = widest tails; ICP = weakest trends; BTC = cleanest volume effect;
ETH-1h ≈ BTC-1h shifted +6–8pp fill. Session blocks (UTC 0–6/6–12/12–18/18–24) and weekdays:
minor (≤±2pp), not exploitable after costs.

## Q10. THE CONVERSION: does ANY of it become net-positive trades?
Tested BOTH philosophies exhaustively (entry {market, pullback-limit} × TP {1.0×, 1.5× wick}
× SL {low, mid} × Tmax 48 × 9 quality gates + 8 inverted gates, per series):

| Gate philosophy | Cells | CI > 0 |
|---|---|---|
| Quality gates (quiet vol, wick d7–8, prior-bear, below-SMA…) | 936 | **0** |
| Inverted/loud gates (vol≥Q4, decile 10, above-SMA, hot trend) | 832 | **0** |

Best cell anywhere: SOL-4h prior-bear pullback +2.2 bps maker, CI [−10.7, +16.2] — noise.
The reason is structural: conditional fill-rate gains (+2…+9pp) are real but SMALL, while
the expected move to target shrinks proportionally with the same factors. At bar granularity,
the market already prices the wick. **~1,768 economic cells, zero significant.**

## Bottom line
- The FACTS you asked for exist now, per asset, with multiplicity control — see table above.
- The TRADE does not survive arithmetic: fill-edge ≪ cost hurdle (4–11 bps RT) at every
  tested granularity, both gate philosophies, both entry mechanics, all 13 personalities.
- Bound set honestly: any true edge here is smaller than ~4 bps/trade net of the modeled
  mechanics — below VIP0 taker by an order of magnitude, below even maker with queue risk.

## What could legitimately change the answer (requires new data/tools, not new curve-fitting)
1. **Order-book execution layer** (L2 snapshots / queue modeling): if maker fills can be
   obtained at better-than-touch probability, the +7.6 bps generic dip-buy drift and the
   quiet-volume fill edge become worth re-pricing. Kline data cannot answer this.
2. **Bearish mirror preregistration** (short the big-upper-wick): the contrarian side is
   the only untested direction; the atlas gives it priors (loud volume, above-SMA, hot trend
   = the failing cohort).
3. **Funding-aware 4h holds**: at 4h horizons funding swaps dwarf the modeled edge and could
   dominate either direction — needs funding-history integration first.
