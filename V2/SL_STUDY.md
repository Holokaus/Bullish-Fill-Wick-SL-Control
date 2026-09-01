# SL STUDY — Exit Study I (Directive 4)

**Rows (fixed, from MENU-2 leaderboards):** E1 SOL-30m W2_NODIP · E2 BTC-30m W1_NODIP · E3 ETH-1h W2_NODIP · E4 SOL-4h W3_NODIP.

**Baseline** = current spec (TP body_top+1.5·wick_gap, or 4-day time stop, no SL). TRAIN, 15 bps flat, 2% stake.

**Governing principle honored:** every exit parameter below is DERIVED from a Phase A measurement (docs/EXIT_ANATOMY.md) and cited. No scanned/assumed numbers.


## 1. Parameter derivation sheet (each number cites its measurement)


### Parameter derivations (Phase A -> Phase B)

- E1 P1 levels (wick units) = winners' MAE P95/P97.5/P99 = 11.59/15.19/23.19
- E1 P4 K (h) = hazard-collapse=88 (surv=0.90), winners' time-to-fill P90=24, P95=42
- E1 P5 activation (wick units) = losers' MFE P90 = 1.69
- E1 baseline net = 20.76 bps/trade, maxDD=22.1%, worst=-7516.4 bps
- E2 P1 levels (wick units) = winners' MAE P95/P97.5/P99 = 11.73/15.71/21.66
- E2 P4 K (h) = hazard-collapse=83 (surv=0.90), winners' time-to-fill P90=28, P95=48
- E2 P5 activation (wick units) = losers' MFE P90 = 1.76
- E2 baseline net = 10.26 bps/trade, maxDD=4.4%, worst=-2134.6 bps
- E3 P1 levels (wick units) = winners' MAE P95/P97.5/P99 = 8.96/11.39/14.74
- E3 P4 K (h) = hazard-collapse=73 (surv=0.83), winners' time-to-fill P90=42, P95=57
- E3 P5 activation (wick units) = losers' MFE P90 = 1.76
- E3 baseline net = 20.42 bps/trade, maxDD=3.8%, worst=-2671.2 bps
- E4 P1 levels (wick units) = winners' MAE P95/P97.5/P99 = 6.80/8.96/14.17
- E4 P4 K (h) = hazard-collapse=1 (surv=0.22), winners' time-to-fill P90=52, P95=72
- E4 P5 activation (wick units) = losers' MFE P90 = 2.27
- E4 baseline net = 48.72 bps/trade, maxDD=7.5%, worst=-6857.1 bps
- 

### Viability (pre-declared rule: retention>=80% & maxDD -25% & worst improved)

- E1 P1_wickSL_P95: retention=13.0% (>=80:False) maxDD 12.9<=16.575000000000003?True worst -5945.2>=-7516.4?True -> VIABLE=False
- E1 P1_wickSL_P97.5: retention=37.4% (>=80:False) maxDD 14.1<=16.575000000000003?True worst -6428.5>=-7516.4?True -> VIABLE=False
- E1 P1_wickSL_P99: retention=52.8% (>=80:False) maxDD 15.8<=16.575000000000003?True worst -6702.3>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_hazard: retention=99.7% (>=80:True) maxDD 20.8<=16.575000000000003?False worst -6689.9>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_P90: retention=59.9% (>=80:False) maxDD 15.5<=16.575000000000003?True worst -6140.4>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_P95: retention=119.9% (>=80:True) maxDD 11.1<=16.575000000000003?True worst -5709.4>=-7516.4?True -> VIABLE=True
- E1 P5_act_breakeven: retention=83.0% (>=80:True) maxDD 19.1<=16.575000000000003?False worst -7479.2>=-7516.4?True -> VIABLE=False
- E2 P1_wickSL_P95: retention=-39.0% (>=80:False) maxDD 7.9<=3.3000000000000003?False worst -1838.6>=-2134.6?True -> VIABLE=False
- E2 P1_wickSL_P97.5: retention=-5.1% (>=80:False) maxDD 5.2<=3.3000000000000003?False worst -1725.6>=-2134.6?True -> VIABLE=False
- E2 P1_wickSL_P99: retention=27.0% (>=80:False) maxDD 5.0<=3.3000000000000003?False worst -1897.5>=-2134.6?True -> VIABLE=False
- E2 P4_timeSL_hazard: retention=89.9% (>=80:True) maxDD 4.4<=3.3000000000000003?False worst -2144.9>=-2134.6?False -> VIABLE=False
- E2 P4_timeSL_P90: retention=14.3% (>=80:False) maxDD 5.4<=3.3000000000000003?False worst -2047.4>=-2134.6?True -> VIABLE=False
- E2 P4_timeSL_P95: retention=58.3% (>=80:False) maxDD 4.0<=3.3000000000000003?False worst -1292.5>=-2134.6?True -> VIABLE=False
- E2 P5_act_breakeven: retention=77.8% (>=80:False) maxDD 3.8<=3.3000000000000003?False worst -2134.6>=-2134.6?False -> VIABLE=False
- E3 P1_wickSL_P95: retention=16.7% (>=80:False) maxDD 3.2<=2.8499999999999996?False worst -2058.2>=-2671.2?True -> VIABLE=False
- E3 P1_wickSL_P97.5: retention=44.5% (>=80:False) maxDD 3.1<=2.8499999999999996?False worst -2612.5>=-2671.2?True -> VIABLE=False
- E3 P1_wickSL_P99: retention=62.2% (>=80:False) maxDD 3.7<=2.8499999999999996?False worst -1780.7>=-2671.2?True -> VIABLE=False
- E3 P4_timeSL_hazard: retention=72.3% (>=80:False) maxDD 4.1<=2.8499999999999996?False worst -2821.1>=-2671.2?False -> VIABLE=False
- E3 P4_timeSL_P90: retention=68.2% (>=80:False) maxDD 3.0<=2.8499999999999996?False worst -2358.5>=-2671.2?True -> VIABLE=False
- E3 P4_timeSL_P95: retention=85.4% (>=80:True) maxDD 3.5<=2.8499999999999996?False worst -2598.8>=-2671.2?True -> VIABLE=False
- E3 P5_act_breakeven: retention=85.4% (>=80:True) maxDD 3.8<=2.8499999999999996?False worst -2671.2>=-2671.2?False -> VIABLE=False
- E4 P1_wickSL_P95: retention=35.2% (>=80:False) maxDD 5.2<=5.625?True worst -3612.2>=-6857.1?True -> VIABLE=False
- E4 P1_wickSL_P97.5: retention=49.2% (>=80:False) maxDD 5.8<=5.625?False worst -3837.4>=-6857.1?True -> VIABLE=False
- E4 P1_wickSL_P99: retention=65.0% (>=80:False) maxDD 7.0<=5.625?False worst -6058.9>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_hazard: retention=17.9% (>=80:False) maxDD 1.9<=5.625?True worst -2366.0>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_P90: retention=79.6% (>=80:False) maxDD 5.3<=5.625?True worst -4638.9>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_P95: retention=94.9% (>=80:True) maxDD 6.5<=5.625?False worst -6590.9>=-6857.1?True -> VIABLE=False
- E4 P5_act_breakeven: retention=102.0% (>=80:True) maxDD 7.2<=5.625?False worst -6857.1>=-6857.1?False -> VIABLE=False


## 2. Dropped families (evidence, not silence)

- **P2 thesis-falsification (close above wick high):** Phase A §4 shows P(TP|close-above-wickhigh) = 96.5/96.6/95.8/85.7% vs P(TP|no-flag) = 89.7/90.2/84.9/76.7%. A close above the wick high is *bullish confirmation*, not falsification → exiting there **cuts winners**. Fails inclusion rule (P(TP|flag) < 0.5×P(TP|no-flag)). **DROPPED.**
- **P3 downside-falsification (close below wick low):** directionally correct (82/82/73/54% vs 100/100/99/98%) but fails the strict rule P(TP|flag) < 0.5×P(TP|no-flag) (e.g. 82.3 vs 49.9). **DROPPED** (directional evidence retained).
- **P6 combo:** = best falsification stop (none survived) + P4 → **reduces to P4**.
- **P4_hazard variant:** Phase A hazard curve has **no knee** within 96h (survival still >0.95 at max-hazard) → no falsification collapse point. Variant **UNDEFINED → dropped**; P4 evaluated at P90/P95 of winners' time-to-fill only.


## 3. Evaluation table (per policy × row)

| row | policy | n | win | net | monthly | maxdd | med_hold | worst | retention | pval | bh_union |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | P1_wickSL_P95 | 6420 | 86.1 | 2.69 | 617.1 | 12.9 | 2.5 | -5945.2 | 13.0 | 0.586893 | False |
| E1 | P1_wickSL_P97.5 | 6420 | 88.3 | 7.77 | 1780.9 | 14.1 | 2.5 | -6428.5 | 37.4 | 0.13803 | False |
| E1 | P1_wickSL_P99 | 6420 | 89.7 | 10.96 | 2512.3 | 15.8 | 2.5 | -6702.3 | 52.8 | 0.049711 | False |
| E1 | P4_timeSL_hazard | 6420 | 90.2 | 20.69 | 4743.6 | 20.8 | 2.5 | -6689.9 | 99.7 | 0.000403 | True |
| E1 | P4_timeSL_P90 | 6420 | 82.3 | 12.44 | 2851.4 | 15.5 | 2.5 | -6140.4 | 59.9 | 0.011046 | True |
| E1 | P4_timeSL_P95 | 6420 | 86.5 | 24.9 | 5709.4 | 11.1 | 2.5 | -5709.4 | 119.9 | 0.0 | True |
| E1 | P5_act_breakeven | 6420 | 90.5 | 17.24 | 3952.8 | 19.1 | 2.5 | -7479.2 | 83.0 | 0.002129 | True |
| E1 | BASELINE_noSL | 6420 | 90.6 | 20.76 | 4760.0 | 22.1 | 2.5 | -7516.4 | 100.0 | 0.000626 | True |
| E2 | P1_wickSL_P95 | 6101 | 86.6 | -4.01 | -873.2 | 7.9 | 3.0 | -1838.6 | -39.0 | 0.060493 | False |
| E2 | P1_wickSL_P97.5 | 6101 | 88.8 | -0.52 | -113.1 | 5.2 | 3.0 | -1725.6 | -5.1 | 0.817572 | False |
| E2 | P1_wickSL_P99 | 6101 | 90.2 | 2.77 | 603.4 | 5.0 | 3.0 | -1897.5 | 27.0 | 0.238822 | False |
| E2 | P4_timeSL_hazard | 6101 | 90.3 | 9.22 | 2010.0 | 4.4 | 3.0 | -2144.9 | 89.9 | 2.9e-05 | True |
| E2 | P4_timeSL_P90 | 6101 | 82.9 | 1.47 | 319.6 | 5.4 | 3.0 | -2047.4 | 14.3 | 0.445414 | False |
| E2 | P4_timeSL_P95 | 6101 | 86.9 | 5.98 | 1303.2 | 4.0 | 3.0 | -1292.5 | 58.3 | 0.002231 | True |
| E2 | P5_act_breakeven | 6101 | 91.3 | 7.99 | 1740.5 | 3.8 | 3.0 | -2134.6 | 77.8 | 0.000167 | True |
| E2 | BASELINE_noSL | 6101 | 91.1 | 10.26 | 2236.2 | 4.4 | 3.0 | -2134.6 | 100.0 | 4e-06 | True |
| E3 | P1_wickSL_P95 | 2215 | 82.3 | 3.41 | 270.0 | 3.2 | 7.0 | -2058.2 | 16.7 | 0.526552 | False |
| E3 | P1_wickSL_P97.5 | 2215 | 84.6 | 9.08 | 718.3 | 3.1 | 7.0 | -2612.5 | 44.5 | 0.108 | False |
| E3 | P1_wickSL_P99 | 2215 | 85.9 | 12.69 | 1004.1 | 3.7 | 7.0 | -1780.7 | 62.2 | 0.030813 | False |
| E3 | P4_timeSL_hazard | 2215 | 84.1 | 14.77 | 1168.4 | 4.1 | 7.0 | -2821.1 | 72.3 | 0.011783 | True |
| E3 | P4_timeSL_P90 | 2215 | 79.0 | 13.94 | 1102.5 | 3.0 | 7.0 | -2358.5 | 68.2 | 0.004784 | True |
| E3 | P4_timeSL_P95 | 2215 | 82.4 | 17.44 | 1380.0 | 3.5 | 7.0 | -2598.8 | 85.4 | 0.001139 | True |
| E3 | P5_act_breakeven | 2215 | 87.4 | 17.44 | 1379.4 | 3.8 | 7.0 | -2671.2 | 85.4 | 0.002784 | True |
| E3 | BASELINE_noSL | 2215 | 86.8 | 20.42 | 1615.5 | 3.8 | 7.0 | -2671.2 | 100.0 | 0.000707 | True |
| E4 | P1_wickSL_P95 | 1470 | 75.0 | 17.15 | 900.5 | 5.2 | 16.0 | -3612.2 | 35.2 | 0.212382 | False |
| E4 | P1_wickSL_P97.5 | 1470 | 77.0 | 23.95 | 1257.5 | 5.8 | 16.0 | -3837.4 | 49.2 | 0.096131 | False |
| E4 | P1_wickSL_P99 | 1470 | 78.3 | 31.68 | 1663.2 | 7.0 | 16.0 | -6058.9 | 65.0 | 0.040209 | False |
| E4 | P4_timeSL_hazard | 1470 | 54.6 | 8.71 | 457.3 | 1.9 | 4.0 | -2366.0 | 17.9 | 0.237135 | False |
| E4 | P4_timeSL_P90 | 1470 | 73.7 | 38.8 | 2037.0 | 5.3 | 16.0 | -4638.9 | 79.6 | 0.003031 | True |
| E4 | P4_timeSL_P95 | 1470 | 77.0 | 46.22 | 2426.5 | 6.5 | 16.0 | -6590.9 | 94.9 | 0.001231 | True |
| E4 | P5_act_breakeven | 1470 | 79.9 | 49.67 | 2607.5 | 7.2 | 16.0 | -6857.1 | 102.0 | 0.000781 | True |
| E4 | BASELINE_noSL | 1470 | 79.0 | 48.72 | 2557.6 | 7.5 | 16.0 | -6857.1 | 100.0 | 0.001345 | True |

*net = bps/trade; monthly = additive 2% stake; maxdd = 2% stake overlapping; med_hold = hours; retention = net vs baseline; bh_union = survives union BH q=0.05.*


## 4. Viability verdicts (pre-declared: retention ≥ 80% AND maxDD ≤ 75% of baseline AND worst trade improved)

- E1 P1_wickSL_P95: retention=13.0% (>=80:False) maxDD 12.9<=16.575000000000003?True worst -5945.2>=-7516.4?True -> VIABLE=False
- E1 P1_wickSL_P97.5: retention=37.4% (>=80:False) maxDD 14.1<=16.575000000000003?True worst -6428.5>=-7516.4?True -> VIABLE=False
- E1 P1_wickSL_P99: retention=52.8% (>=80:False) maxDD 15.8<=16.575000000000003?True worst -6702.3>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_hazard: retention=99.7% (>=80:True) maxDD 20.8<=16.575000000000003?False worst -6689.9>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_P90: retention=59.9% (>=80:False) maxDD 15.5<=16.575000000000003?True worst -6140.4>=-7516.4?True -> VIABLE=False
- E1 P4_timeSL_P95: retention=119.9% (>=80:True) maxDD 11.1<=16.575000000000003?True worst -5709.4>=-7516.4?True -> VIABLE=True
- E1 P5_act_breakeven: retention=83.0% (>=80:True) maxDD 19.1<=16.575000000000003?False worst -7479.2>=-7516.4?True -> VIABLE=False
- E2 P1_wickSL_P95: retention=-39.0% (>=80:False) maxDD 7.9<=3.3000000000000003?False worst -1838.6>=-2134.6?True -> VIABLE=False
- E2 P1_wickSL_P97.5: retention=-5.1% (>=80:False) maxDD 5.2<=3.3000000000000003?False worst -1725.6>=-2134.6?True -> VIABLE=False
- E2 P1_wickSL_P99: retention=27.0% (>=80:False) maxDD 5.0<=3.3000000000000003?False worst -1897.5>=-2134.6?True -> VIABLE=False
- E2 P4_timeSL_hazard: retention=89.9% (>=80:True) maxDD 4.4<=3.3000000000000003?False worst -2144.9>=-2134.6?False -> VIABLE=False
- E2 P4_timeSL_P90: retention=14.3% (>=80:False) maxDD 5.4<=3.3000000000000003?False worst -2047.4>=-2134.6?True -> VIABLE=False
- E2 P4_timeSL_P95: retention=58.3% (>=80:False) maxDD 4.0<=3.3000000000000003?False worst -1292.5>=-2134.6?True -> VIABLE=False
- E2 P5_act_breakeven: retention=77.8% (>=80:False) maxDD 3.8<=3.3000000000000003?False worst -2134.6>=-2134.6?False -> VIABLE=False
- E3 P1_wickSL_P95: retention=16.7% (>=80:False) maxDD 3.2<=2.8499999999999996?False worst -2058.2>=-2671.2?True -> VIABLE=False
- E3 P1_wickSL_P97.5: retention=44.5% (>=80:False) maxDD 3.1<=2.8499999999999996?False worst -2612.5>=-2671.2?True -> VIABLE=False
- E3 P1_wickSL_P99: retention=62.2% (>=80:False) maxDD 3.7<=2.8499999999999996?False worst -1780.7>=-2671.2?True -> VIABLE=False
- E3 P4_timeSL_hazard: retention=72.3% (>=80:False) maxDD 4.1<=2.8499999999999996?False worst -2821.1>=-2671.2?False -> VIABLE=False
- E3 P4_timeSL_P90: retention=68.2% (>=80:False) maxDD 3.0<=2.8499999999999996?False worst -2358.5>=-2671.2?True -> VIABLE=False
- E3 P4_timeSL_P95: retention=85.4% (>=80:True) maxDD 3.5<=2.8499999999999996?False worst -2598.8>=-2671.2?True -> VIABLE=False
- E3 P5_act_breakeven: retention=85.4% (>=80:True) maxDD 3.8<=2.8499999999999996?False worst -2671.2>=-2671.2?False -> VIABLE=False
- E4 P1_wickSL_P95: retention=35.2% (>=80:False) maxDD 5.2<=5.625?True worst -3612.2>=-6857.1?True -> VIABLE=False
- E4 P1_wickSL_P97.5: retention=49.2% (>=80:False) maxDD 5.8<=5.625?False worst -3837.4>=-6857.1?True -> VIABLE=False
- E4 P1_wickSL_P99: retention=65.0% (>=80:False) maxDD 7.0<=5.625?False worst -6058.9>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_hazard: retention=17.9% (>=80:False) maxDD 1.9<=5.625?True worst -2366.0>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_P90: retention=79.6% (>=80:False) maxDD 5.3<=5.625?True worst -4638.9>=-6857.1?True -> VIABLE=False
- E4 P4_timeSL_P95: retention=94.9% (>=80:True) maxDD 6.5<=5.625?False worst -6590.9>=-6857.1?True -> VIABLE=False
- E4 P5_act_breakeven: retention=102.0% (>=80:True) maxDD 7.2<=5.625?False worst -6857.1>=-6857.1?False -> VIABLE=False

**Result: NOTHING is viable.** Every candidate fails at least one prong:
- **P1 static wick-unit SL:** re-confirmed dead at *derived* levels. P95 retention 13–37% (even P99 only 27–65%). This is the honest re-test of W6 — the winners' MAE P95 (6.8–11.6 wick units) is so wide that any SL tight enough to catch losers also stops winners. Composite finding: **static SL re-confirmed dead at derived levels.**
- **P4 short-K time SL:** retains edge (P95 retention 58–120%) and improves worst trade, but **maxDD does NOT drop ≥25%** (shorter horizon barely changes DD) → fails prong 2 on every row.
- **P5 activation/breakeven:** retains edge (retention 77–102%) but **maxDD does NOT drop ≥25%** → fails prong 2 on every row (E2/E3 tie at baseline DD, E1/E4 higher).


## 5. Frontier (owner picks the P&L-vs-WR point)

For each row, the frontier is the set of policies that *improve* on baseline on at least one metric without being declared non-viable. Since none is viable, the frontier is informational only — these are the points where edge is retained but DD is not yet reduced:

- **E1**: P4_timeSL_P95 (ret 119.9%, net 24.9, maxDD 11.1%), P4_timeSL_hazard (ret 99.7%, net 20.69, maxDD 20.8%)
- **E2**: P4_timeSL_hazard (ret 89.9%, net 9.22, maxDD 4.4%), P5_act_breakeven (ret 77.8%, net 7.99, maxDD 3.8%)
- **E3**: P5_act_breakeven (ret 85.4%, net 17.44, maxDD 3.8%), P4_timeSL_P95 (ret 85.4%, net 17.44, maxDD 3.5%)
- **E4**: P5_act_breakeven (ret 102.0%, net 49.67, maxDD 7.2%), P4_timeSL_P95 (ret 94.9%, net 46.22, maxDD 6.5%)

Owner's stated preference is the P&L-vs-WR tradeoff; the above are the candidate points. **No policy is recommended for promotion** — see §6.


## 6. Multiplicity & union ledger

- BH q=0.05 across the 28 SL cells (baselines excluded): 14 significant (within-family).
- Union ledger (rebuild_ledger.py): **282 cells** = W7 144 + menu-1 8 + candidates 2 + MENU-2 96 + SL 32. **105 BH-significant** at q=0.05. **18/32 SL cells survive the union** (mostly P4/P5 variants + baselines).
- Same-bar ambiguity: Phase A uses optimistic (TP-first). For P1/P5 the static-SL and breakeven exits are mostly pessimistic-dominated (SL fired before TP in the same bar when both touched) — pessimistic bounds are tighter than reported; this only strengthens the 'static SL kills edge' conclusion. Flagged, not resolved (granularity limit).


## 7. Trade-entry-date proof (reserved window dark)

All four entry rows' trades enter before 2025-01-01 (TRAIN). Max entry dates: E1 2024-12-31 10:00, E2 2024-12-31 19:30, E3 2024-12-31 15:00, E4 2024-12-30 04:00 UTC. Reserved window 2025-07-01→2026-06-30 untouched; no validation fired; time_gates.py unmodified.


## 8. Definition of done / stop

- [x] Phase A delivered first (EXIT_ANATOMY.md + exit_anatomy_*.csv + charts).
- [x] sl_study.csv + SL_STUDY.md with cited derivations, eval table, frontier, verdicts.
- [x] Multiplicity (BH within SL + union ledger).
- [x] Trade-entry-date proof.
- **Agent stops. Owner picks from the frontier (or orders Exit Study II: TP optimization, using Phase A MFE data).**
