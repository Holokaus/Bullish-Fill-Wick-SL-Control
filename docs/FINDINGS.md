# FINDINGS — Every Measured Number, Organized
**Snapshot:** 2026-08-24 ~22:00 UTC · **Coverage:** Core statistics + fee ledger: BTCUSDT, ETHUSDT (full). SOLUSDT: conditional atlas only (its core-ΔP/fee-ledger run was started later and interrupted — NOT included below; flagged wherever relevant).

---

## F1. The headline fact — ΔP vs matched control (Phase 1, pre-registered)
ΔP = P(target reached | wick event) − P(same required return reachable | non-event candles), day-cluster bootstrap 95% CIs.

| Cell | n events | P(win\|event) | P(control) | ΔP | 95% CI | Significant |
|---|---|---|---|---|---|---|
| BTC 1d | 1508 | 59.8% | 63.6% | −3.8pp | [−8.8, +1.1] | no |
| BTC 4h | 6188 | 53.9% | 51.6% | **+2.3pp** | [+0.4, +4.2] | yes |
| BTC 1h | 12698 | 48.3% | 40.9% | **+7.4pp** | [+6.2, +8.5] | yes |
| BTC 30m | 7622 | 45.1% | 35.3% | **+9.8pp** | [+8.5, +11.2] | yes |
| BTC 15m | 7534 | 41.1% | 28.0% | **+13.1pp** | [+11.8, +14.4] | yes |
| ETH 1d | 1576 | 59.6% | 64.8% | −5.2pp | [−11.4, +1.0] | no |
| ETH 4h | 7308 | 56.0% | 54.4% | +1.5pp | [−0.4, +3.5] | no |
| ETH 1h | 17417 | 51.4% | 45.5% | **+5.9pp** | [+4.8, +7.0] | yes |
| ETH 30m | 12987 | 47.6% | 42.4% | **+5.3pp** | [+4.0, +6.5] | yes |
| ETH 15m | 14592 | 44.0% | 35.2% | **+8.8pp** | [+7.7, +10.0] | yes |

Reading: elevated short-horizon up-reach after upper-wick candles is real on intraday timeframes, absent/negative on daily. Effect grows as timeframe shrinks.

### Stationarity (per-year ΔP)
- BTC 4h: '22 +0.002 · '23 +0.019 · '24 −0.008 · '25 +0.057 · '26 +0.006 (weak, unstable)
- BTC 1h: +0.013 / +0.099 / +0.041 / +0.109 / +0.081 — positive every year
- BTC 30m ('24–'26): +0.063 / +0.126 / +0.105 · BTC 15m: +0.099 / +0.156 / +0.143
- ETH 4h: −0.049 / +0.071 / +0.016 / −0.046 / +0.003 (unstable) · ETH 1h: −0.006 / +0.108 / +0.025 / +0.035 / +0.059 · ETH 30m: +0.049 / +0.033 / +0.077 · ETH 15m: +0.090 / +0.067 / +0.109

### 2026 holdout (entered no tuning anywhere)
Win rate vs same-year control: BTC 15m 40.7% vs ~26.4% (Δ +14.3pp) · BTC 30m 43.8% vs 33.3% (+10.5) · BTC 1h 46.9% vs 38.9% (+8.1) · BTC 4h 50.6% vs 50.0% (+0.6) · ETH 15m 42.1% vs 31.2% (+10.9) · ETH 30m 45.3% vs 37.6% (+7.7) · ETH 1h 48.5% vs 42.6% (+5.9). Effect persists out-of-sample.

## F2. Is it the WICK or just volatility? (range-decile decomposition)
Reach probability WITHIN each range decile, groups: A=event, B=mirror(lower-wick-dominant), C=body-dominant.
- BTC 1h: A beats B by ~2–7pp and B beats C by ~2–5pp in EVERY decile (A: 0.266→0.509 rising across deciles; B trails ~0.03 behind; C ~0.06–0.08 behind).
- BTC 4h: A>B in 9/10 bins (one bin flips: 0.386 vs 0.408).
- ETH 1h: same ordering every decile (A 0.258→0.559).
- Group means (BTC 1h): A 0.413 > B 0.357 > C 0.288 > D_other 0.261. Same ladder on ETH, and on SOL in the atlas era.
Conclusion: two layers — (1) volatility persistence carries most of the level; (2) an upper-wick-specific residual of ~3–7pp survives range-matching, uniformly.

## F3. Wick-size buckets (pre-registered edges), win rates
BTC 1d: 63.1 / 68.0 / 66.3 / 54.6 / 41.8 % (buckets [0.2–0.35), [0.35–0.6), [0.6–1.0), [1.0–1.75), [1.75+)) — small wicks fill more reliably on daily.
BTC 4h: 63.8 / 55.2 / 44.6 / 37.1 / 29.2 % — monotone decline with size.
BTC 1h: 53.6 / 45.4 / 34.6 / 28.9 / 17.5 %. Same shape everywhere: bigger wick ⇒ harder to fully retrace within 2 candles.

## F4. Event color (bull vs bear event candle)
Win rates — BTC: 1d 73.0/45.8 · 4h 65.2/41.2 · 1h 57.9/37.2 · 30m 53.7/34.6 · 15m 50.0/31.7 (bull/bear).
ETH: 1d 73.8/44.0 · 4h 68.4/41.9 · 1h 61.2/39.7 · 30m 55.6/37.4 · 15m 52.2/34.3.
Caveat discovered in Phase 2 geometry: bullish targets are mechanically ~half as far (entry sits AT body-top for bulls; bears need to climb the body first) — part of this gap is geometry, not psychology.

## F5. Fill timing (one candle or two)
Share of events filling on e+1 / only on e+2 / never:
- BTC: 1d 46.7/13.1/40.2 · 4h 41.0/12.9/46.1 · 1h 35.1/13.3/51.7 · 30m 31.2/13.9/54.9 · 15m 27.3/13.9/58.9
- ETH: 1d 46.9/12.8/40.4 · 4h 43.5/12.4/44.0 · 1h 38.6/12.8/48.7 · 30m 34.0/13.7/52.4 · 15m 30.1/13.9/56.0
- SOL: 1d 46.8/11.7/41.4 · 4h 45.1/11.9/43.0 · 1h 42.0/12.7/45.3 · 30m 37.7/13.9/48.4 · 15m 34.5/13.6/51.9
Constant across everything: the 2nd candle adds ~+12–14pp fills. A third would add little; the 2-candle window is well-calibrated.

## F6. Path before outcome (bounces/dips)
Winner MAE (deepest dip before target hit), percentiles p10/p25/p50/p75/p90 (bp):
- BTC 1h: −101 / −55 / −26 / −11 / −3 · ETH 1h: −124 / −68 / −32 / −14 / −4 · SOL 1h: −164 / −94 / −47 / −20 / −7 · SOL 1d: −771 / −473 / −251 / −110 / −47
Loser MFE (closest approach to T before failing), p50/p75/p90: BTC 1h 22/39/64 bp · ETH 1h 25/47/80 · SOL 1h 33/64/108.
Implication recorded: any future SL tighter than ~p75 winner-dip will kill 25%+ of winners; SOL needs far wider room than BTC. This quantifies why SL design is a separate task.

## F7. Preceding candle (e−1)
Color-pair table (prev→event), p_win / net_bp@11bp costs:
- BTC 1h: BEAR→BEAR 0.398/−5.5 · BEAR→BULL 0.609/−11.7 · BULL→BEAR 0.351/−11.7 · BULL→BULL 0.551/−11.1 (n≈2.7–3.5k each)
- ETH 1h: same shape (best cell prevBEAR→BEAR −7.4bp)
- SOL 1d: BEAR→BEAR 0.417/−11.7 · **BEAR→BULL 0.765/−19.9** · BULL→BEAR 0.410/−43.1 · **BULL→BULL 0.751/+12.7**
  ⚠ SOL paradox: highest-win cell loses money (far targets), lower-win cell makes money (cheap targets) — win rate ≠ expectancy.
- Prev-candle-was-event: negligible effect (BTC 1h 0.468 vs 0.501; SOL 1d 0.602 vs 0.585).
- Prev range tercile: no stable monotone pattern on BTC/ETH.

## F8. Trend context
Trend12 (12-candle return: up/down/flat), p_win / net_bp:
- SOL 4h: up 0.602/−7.4 · flat 0.516/−21.5 · down 0.543/−13.7 — trend helps probability, not enough for net.
- BTC 4h: up 0.559/−6.5 · flat 0.514/−13.6 · down 0.524/−6.9. ETH similar. Intraday TFs: trend lifts p_win by 2–5pp, net stays negative.
Position-in-24bar-range: SOL 1d hi-third 0.636 vs lo-third 0.534 (continuation behavior); BTC 1h flat (0.499/0.471/0.474).

## F9. Event-candle volume (RVOL vs trailing 20-median)
Consistent INVERSE gradient on all assets:
- BTC 1h: <0.7 → 0.528 · 0.7–1.3 → 0.507 · 1.3–2.0 → 0.481 · ≥2.0 → 0.425 (win rate falls as volume rises)
- ETH 1h: 0.588 / 0.533 / 0.492 / 0.439. SOL 1h: 0.616 / 0.559 / 0.520 / 0.464.
- Exception pocket: SOL 1d RVOL 1.3–2.0 is the only volume band with positive net (+19.7bp, n=315).
Reading: quiet exhaustion wicks retrace better than high-volume wicks — contradicts "volume confirms" folklore, measured directly.

## F10. Candle anatomy (body share × color), net_bp@11bp
- BTC 1h: large_body_bear +10.8 (ONLY positive class) · large_body_bull −7.2 · mid_bear −7.1 · mid_bull −11.5 · small_* ≈ −11.6/−11.9
- ETH 1h: large_body_bear −5.9 best; small_body_bull −13.4 worst.
- SOL 1h: large_body_bear +4.9 best. SOL 1d: small_body_bull +31.1, large_body_bull +2.5, everything bearish ≤ −18.8.
Doji-like events are consistently the worst buys; big-bodied events carry whatever edge exists.

## F11. Time-of-day (entry hour, UTC)
Best/worst hour by net (n≥80/hour-bucket):
- BTC 1h: best 12UTC p=0.641 net −2.8 (n=412) · worst 01UTC p=0.422 net −17.2 (n=587) — 22pp spread
- ETH 1h: best 20UTC (0.540/−5.6) · worst 06UTC (0.489/−19.7)
- SOL 1h: best 00UTC (0.631/−4.8) · worst 15UTC (0.505/−20.6)
US-session wicks retrace best; Asian-session wicks worst, on all three assets.

## F12. Entry optimization — limit orders below Open(e+1)
Net bp PER SIGNAL (costs charged only when filled), optimistic/pessimistic bounds bracket same-candle touch ambiguity:
| Discount | BTC 1h opt/pess | ETH 1h opt/pess | SOL 1h opt/pess | SOL 1d opt/pess |
|---|---|---|---|---|
| 0bp (market) | +0.8 / −13.3 | −0.2 / −17.7 | +0.9 / −23.1 | −4.6 / −106.1 |
| 10bp | +3.0 / −8.9 | +2.1 / −13.3 | +3.3 / −18.9 | −0.2 / −101.9 |
| 20bp | +4.0 / −5.8 | +3.3 / −9.9 | +5.8 / −15.0 | +5.1 / −98.0 |
| 30bp | +4.0 / −3.8 | +4.0 / −7.4 | +7.1 / −11.8 | +9.9 / −94.2 |
Fill rates fall slowly (BTC 1h: 100%→82% at 10bp→52% at 30bp). Dipping into the wick improves expectancy monotonically; SOL daily's pessimistic bound stays catastrophically negative because its failures are huge (daily no-SL exits).
Known display bug (quarantined): `hit_rate_given_fill` field shows 0.0% — comparison used T instead of L; bounds above unaffected.

## F13. Tradeability ledger (BTC & ETH complete; SOL pending — run interrupted)
Gross expectancy bp/trade (zero costs): BTC 1d ALL +1.7 (BULL +3.6) · 4h +3.7 · 1h +0.8 · 30m +0.1 · 15m +0.4. ETH: 1d −11.6 · 4h −0.8 · others ≈ −1.
Net @ futures maker-in/taker-out + slippage (11bp RT): best cells BTC 4h −7.3, BTC 1d BULL −7.4 … everything negative.
Target distance medians (r_req): BTC 124/59/41/35/33 bp (1d/4h/1h/30m/15m) · ETH 161/72/46/38/35.
Verdict as-specified (market buy next open, no SL, 95%-wick target, 2 candles): information real, arithmetic negative at declared cost assumptions.
Mechanics notes measured: Open(e+1)=Close(e) to 0.001bp median (no session gaps); bull-event climbs ≈ wick only (~31bp median @1h), bear-events ≈ body-climb (~21–26bp) + wick (~30bp).

## F14. Asset personality (user hypothesis — CONFIRMED)
Same concept, different optimum per asset: BTC pays for EXTREME wicks (≥2.5% daily: +39.3bp net, n=94), SOL pays for MODERATE wicks (1.3–1.75% daily: +37.3bp, n=221; 1.75–2.5% hourly: +19.4bp across all five years), ETH sits between (4h ≥2.5%: +35.6bp, n=86 but thin years). Volume/trend/anatomy conditioners also rank differently per asset. No parameters were pooled or borrowed across assets.

## F15. Candidate rulesets GENERATED (not yet validated — selection bias applies)
1. SOL daily: wick 1.3–1.75% + RVOL 1.3–2.0 + prior-candle-bull context → cheapest-target quadrant (net +12.7bp unconditioned-cell evidence; year-stable 3/5 years, weak '23/'26).
2. SOL 1h: wick 1.75–2.5%, any context → +19.4bp net, positive ALL 5 years, n=344 (strongest persistence found).
3. BTC daily: wick ≥2.5% extreme-exhaustion longs → +39.3bp net, n=94, unstable early years, 2026 n=5 (insufficient).
4. Dip-entry overlay: 20–30bp limit below open adds +3–7bp/signal on 1h cells (bounds-aware).
ALL of these await Phase-3 walk-forward/pre-registered validation before any live claim.

## Coverage & gaps
Complete (BTC, ETH): pre-registered ΔP study, controls, bootstrap CIs, stationarity, holdout, decomposition, buckets, timing, path, prev-candle, trend, volume, anatomy, hours, dip-ladder, fee ledger.
SOL: data + conditional atlas (F5–F12 partially, F14) ONLY — core ΔP table, control baselines, and fee ledger NOT yet computed for SOL (run interrupted by user; deliberately not restarted without instruction).
Not started anywhere: SL design task (deferred by user), walk-forward validation of F15 candidates, finer wick grids, additional assets/timeframes.
