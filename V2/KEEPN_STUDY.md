# KEEPN STUDY — EXIT / SL / TP MEASUREMENT (TRAIN)

> Codename KEEPN (keep-n). Measurement only. No winner selected. Owner evaluates.

## 1. Identity gate

| row | n | max entry (UTC) | max entry OK | baseline net @15bps | net OK | baseline win% | win OK | baseline maxDD% | maxDD OK | baseline worst bps | worst OK | GATE |
|-----|---|-----------------|-------------|----------------------|--------|---------------|--------|-----------------|---------|--------------------|---------|------|
| E1 | 6420 (exp 6420) | 2024-12-31 10:00:00 | True | 20.76 (exp 20.76) | True | 90.6 (exp 90.6) | True | 22.1 (exp 22.1) | True | -7516.4 (exp -7516.4) | True | PASS |
| E2 | 6101 (exp 6101) | 2024-12-31 19:30:00 | True | 10.26 (exp 10.26) | True | 91.1 (exp 91.1) | True | 4.4 (exp 4.4) | True | -2134.6 (exp -2134.6) | True | PASS |
| E3 | 2215 (exp 2215) | 2024-12-31 15:00:00 | True | 20.42 (exp 20.42) | True | 86.8 (exp 86.8) | True | 3.8 (exp 3.8) | True | -2671.2 (exp -2671.2) | True | PASS |
| E4 | 1470 (exp 1470) | 2024-12-30 04:00:00 | True | 48.72 (exp 48.72) | True | 79.0 (exp 79.0) | True | 7.5 (exp 7.5) | True | -6857.1 (exp -6857.1) | True | PASS |

**Identity gate: ALL PASS.**

## 2. Prohibitions kept

- [x] X1 BTC-regime gate (TREND_UP/VOL_EXPANSION) — not done
- [x] X2 Skip RANGE/TREND_DOWN — not done
- [x] X3 wick/ATR vol-normalize trigger — not done
- [x] X4 quiet-volume / rvol gate — not done
- [x] X5 prior-bear/below-SMA/quality-score AND-gates — not done
- [x] X6 green-candle-only — not done
- [x] X7 session filter (Asia skip) — not done
- [x] X8 dip filter (24h/4d) — not done
- [x] X9 switch to thin cells (W3_DIP/W4/1D/ICP) — not done
- [x] X10 funding-rate skip/flatten — not done
- [x] X11 concurrent-risk cap / retune 2% stake — not done
- [x] X12 LightGBM/ML/exhaustion classifier — not done
- [x] X13 re-run W6 ABS/ATR/QMAE grid — not done
- [x] X14 re-run Exit Study I P1/P4/P5 percentiles — not done
- [x] X15 fire E-VAL / E-LOCKBOX — not done
- [x] X16 touch reserved window 2025-07-01→2026-06-30 — not done
- [x] X17 modify FROZEN_CANDIDATE/META_VERDICT/config/SYSTEM_SIGNED — not done
- [x] X18 rebuild union_ledger / fix m2_grid BH / reissue MENU2 — not done
- [x] X19 new assets/TFs/W4/DIP/5m/15m/1D — not done
- [x] X20 L2/order-book/tick data — not done
- [x] X21 extra policy families/f/checkpoints/trail distances — not done
- [x] X22 pick winner / freeze spec / write recommended system — not done
- [x] X23 extra charts/notebooks/dashboards/refactor src/lib — not done
- [x] X24 assume result / skip empty cell — not done

## 3. Derivation sheet

- E4: n=1470(exp1470,OK) net=48.72(exp48.72,OK) win=79.0(exp79.0,OK) maxdd=7.5(exp7.5,OK) worst=-6857.1(exp-6857.1,OK) maxentry=2024-12-30 04:00:00(<2025-01-01:OK) -> PASS
- E3: n=2215(exp2215,OK) net=20.42(exp20.42,OK) win=86.8(exp86.8,OK) maxdd=3.8(exp3.8,OK) worst=-2671.2(exp-2671.2,OK) maxentry=2024-12-31 15:00:00(<2025-01-01:OK) -> PASS
- E2: n=6101(exp6101,OK) net=10.26(exp10.26,OK) win=91.1(exp91.1,OK) maxdd=4.4(exp4.4,OK) worst=-2134.6(exp-2134.6,OK) maxentry=2024-12-31 19:30:00(<2025-01-01:OK) -> PASS
- E1: n=6420(exp6420,OK) net=20.76(exp20.76,OK) win=90.6(exp90.6,OK) maxdd=22.1(exp22.1,OK) worst=-7516.4(exp-7516.4,OK) maxentry=2024-12-31 10:00:00(<2025-01-01:OK) -> PASS
- E1 A_disaster_P99_9 L_wick=P99.9(MAE_winner)=43.316 (PhaseA MAE_winner_P99.9=43.316, match=True)
- E1 D_scale_1.0_MFEp50 f2=P50(MFE_winner)=2.450 (PhaseA MFE_winner_P50=2.450, match=True)
- E1 F_act_loserMFEp50 A=P50(MFE_loser)=0.815 (PhaseA MFE_loser_P50=0.815, match=True)
- E1 baseline net=20.76 win=90.6 maxdd=22.1 worst=-7516.4
- E2 A_disaster_P99_9 L_wick=P99.9(MAE_winner)=39.267 (PhaseA MAE_winner_P99.9=39.267, match=True)
- E2 D_scale_1.0_MFEp50 f2=P50(MFE_winner)=2.496 (PhaseA MFE_winner_P50=2.496, match=True)
- E2 F_act_loserMFEp50 A=P50(MFE_loser)=0.875 (PhaseA MFE_loser_P50=0.875, match=True)
- E2 baseline net=10.26 win=91.1 maxdd=4.4 worst=-2134.6
- E3 A_disaster_P99_9 L_wick=P99.9(MAE_winner)=30.601 (PhaseA MAE_winner_P99.9=30.601, match=True)
- E3 D_scale_1.0_MFEp50 f2=P50(MFE_winner)=2.361 (PhaseA MFE_winner_P50=2.361, match=True)
- E3 F_act_loserMFEp50 A=P50(MFE_loser)=0.829 (PhaseA MFE_loser_P50=0.829, match=True)
- E3 baseline net=20.42 win=86.8 maxdd=3.8 worst=-2671.2
- E4 A_disaster_P99_9 L_wick=P99.9(MAE_winner)=20.481 (PhaseA MAE_winner_P99.9=20.481, match=True)
- E4 D_scale_1.0_MFEp50 f2=P50(MFE_winner)=2.484 (PhaseA MFE_winner_P50=2.484, match=True)
- E4 F_act_loserMFEp50 A=P50(MFE_loser)=0.971 (PhaseA MFE_loser_P50=0.971, match=True)
- E4 baseline net=48.72 win=79.0 maxdd=7.5 worst=-6857.1
- # BH (§3.6): family size=84 q=0.05 rejected=68
-   REJECTED E1 A_disaster_P99_9 p=0.000215644
-   REJECTED E1 B_close_below_siglow p=2.05609e-09
-   REJECTED E1 B_close_below_entry p=4.53212e-10
-   REJECTED E1 B_close_below_entry_1wick p=1.96777e-06
-   REJECTED E1 C_flat_worst_6h p=0.0387479
-   REJECTED E1 C_flat_worst_12h p=0.00261526
-   REJECTED E1 C_flat_worst_24h p=0.0071319
-   REJECTED E1 D_tp_1.25 p=0.0174253
-   REJECTED E1 D_tp_1.50 p=0.000626198
-   REJECTED E1 D_tp_2.00 p=8.89873e-05
-   REJECTED E1 D_tp_2.50 p=1.96369e-07
-   REJECTED E1 D_scale_1.0_1.5 p=0.011984
-   REJECTED E1 D_scale_1.0_2.0 p=0.00315061
-   REJECTED E1 D_scale_1.0_MFEp50 p=0.000157892
-   REJECTED E1 E_time_TTF_P50 p=0.00210797
-   REJECTED E1 F_act_loserMFEp50 p=0.000713923
-   REJECTED E1 F_act_1wick p=0.00213027
-   REJECTED E1 G_limit_skip p=0.000320005
-   REJECTED E1 G_limit_mkt_fallback p=0.000565169
-   REJECTED E2 A_disaster_P99_9 p=0.00204083
-   REJECTED E2 B_close_below_siglow p=0
-   REJECTED E2 B_close_below_entry p=0
-   REJECTED E2 B_close_below_entry_1wick p=0
-   REJECTED E2 C_flat_worst_6h p=0.00267922
-   REJECTED E2 D_tp_1.25 p=0.00206852
-   REJECTED E2 D_tp_1.50 p=4.3822e-06
-   REJECTED E2 D_tp_2.00 p=1.68998e-11
-   REJECTED E2 D_tp_2.50 p=7.54952e-15
-   REJECTED E2 D_scale_1.0_1.5 p=0.00189445
-   REJECTED E2 D_scale_1.0_2.0 p=5.98285e-06
-   REJECTED E2 D_scale_1.0_MFEp50 p=6.62883e-08
-   REJECTED E2 E_time_TTF_P50 p=0
-   REJECTED E2 E_time_TTF_P75 p=3.11754e-05
-   REJECTED E2 F_act_loserMFEp50 p=1.49924e-05
-   REJECTED E2 F_act_1wick p=4.66724e-05
-   REJECTED E2 G_limit_skip p=1.56083e-08
-   REJECTED E2 G_limit_mkt_fallback p=3.86963e-06
-   REJECTED E3 A_disaster_P99_9 p=0.00772206
-   REJECTED E3 B_close_below_siglow p=0.0018065
-   REJECTED E3 B_close_below_entry p=1.83274e-05
-   REJECTED E3 B_close_below_entry_1wick p=0.0195318
-   REJECTED E3 D_tp_1.00 p=0.0316196
-   REJECTED E3 D_tp_1.25 p=0.00465666
-   REJECTED E3 D_tp_1.50 p=0.000706598
-   REJECTED E3 D_tp_2.00 p=5.20059e-05
-   REJECTED E3 D_tp_2.50 p=1.52605e-06
-   REJECTED E3 D_scale_1.0_1.5 p=0.0037128
-   REJECTED E3 D_scale_1.0_2.0 p=0.000676932
-   REJECTED E3 D_scale_1.0_MFEp50 p=8.75167e-05
-   REJECTED E3 E_time_TTF_P50 p=0.0322863
-   REJECTED E3 F_act_loserMFEp50 p=0.00528475
-   REJECTED E3 F_act_1wick p=0.00175419
-   REJECTED E3 G_limit_skip p=0.000521597
-   REJECTED E3 G_limit_mkt_fallback p=0.000871002
-   REJECTED E4 A_disaster_P99_9 p=0.0037136
-   REJECTED E4 D_tp_1.00 p=0.00877496
-   REJECTED E4 D_tp_1.25 p=0.00130379
-   REJECTED E4 D_tp_1.50 p=0.00134461
-   REJECTED E4 D_tp_2.00 p=0.000775971
-   REJECTED E4 D_tp_2.50 p=5.97234e-05
-   REJECTED E4 D_scale_1.0_1.5 p=0.00256266
-   REJECTED E4 D_scale_1.0_2.0 p=0.00137055
-   REJECTED E4 D_scale_1.0_MFEp50 p=0.00031104
-   REJECTED E4 E_time_TTF_P75 p=0.0289708
-   REJECTED E4 F_act_loserMFEp50 p=6.39572e-07
-   REJECTED E4 F_act_1wick p=1.11232e-06
-   REJECTED E4 G_limit_skip p=0.0138829
-   REJECTED E4 G_limit_mkt_fallback p=0.00214864

## 4. Full results table

| row | policy | family | n | n0 | win% | win0 | net | net0 | netΔbps | maxdd | worst | pval | ci_lo | ci_hi | bh | improve | defend | n_ret% | fill |
|-----|--------|--------|---|----|------|------|-----|------|---------|-------|-------|------|-------|-------|----|--------|-------|--------|------|
| E1 | BASELINE | BASE | 6420 | 6420 | 90.6 | 90.6 | 20.76 | 20.76 | 0.0 | 22.1 | -7516.4 | 0.000626 | 8.63 | 31.92 | False | False | False |  | 1.0 |
| E1 | A_disaster_P99_9 | A | 6420 | 6420 | 90.5 | 90.6 | 20.71 | 20.76 | -0.05 | 16.3 | -5272.8 | 0.000216 | 9.66 | 31.36 | True | False | True |  | 1.0 |
| E1 | B_close_below_siglow | B | 6420 | 6420 | 46.6 | 90.6 | -15.6 | 20.76 | -36.36 | 18.3 | -2613.7 | 0.0 | -20.72 | -10.44 | True | False | False |  | 1.0 |
| E1 | B_close_below_entry | B | 6420 | 6420 | 33.9 | 90.6 | -12.36 | 20.76 | -33.12 | 14.8 | -2229.1 | 0.0 | -16.33 | -8.43 | True | False | False |  | 1.0 |
| E1 | B_close_below_entry_1wick | B | 6420 | 6420 | 50.8 | 90.6 | -12.84 | 20.76 | -33.6 | 15.5 | -2613.7 | 2e-06 | -18.24 | -7.38 | True | False | False |  | 1.0 |
| E1 | C_flat_worst_6h | C | 6420 | 6420 | 76.1 | 90.6 | 8.35 | 20.76 | -12.41 | 9.3 | -5140.3 | 0.038748 | 0.42 | 16.1 | True | False | False |  | 1.0 |
| E1 | C_flat_worst_12h | C | 6420 | 6420 | 80.5 | 90.6 | 13.42 | 20.76 | -7.34 | 12.5 | -5243.0 | 0.002615 | 4.63 | 21.94 | True | False | False |  | 1.0 |
| E1 | C_flat_worst_24h | C | 6420 | 6420 | 84.9 | 90.6 | 13.73 | 20.76 | -7.03 | 15.7 | -6371.1 | 0.007132 | 3.22 | 24.09 | True | False | False |  | 1.0 |
| E1 | D_tp_1.00 | D | 6420 | 6420 | 92.9 | 90.6 | 7.09 | 20.76 | -13.67 | 18.8 | -7361.0 | 0.182767 | -3.29 | 17.19 | False | False | False |  | 1.0 |
| E1 | D_tp_1.25 | D | 6420 | 6420 | 91.7 | 90.6 | 13.65 | 20.76 | -7.11 | 21.2 | -7516.4 | 0.017425 | 2.66 | 24.39 | True | False | False |  | 1.0 |
| E1 | D_tp_1.50 | D | 6420 | 6420 | 90.6 | 90.6 | 20.76 | 20.76 | 0.0 | 22.1 | -7516.4 | 0.000626 | 8.63 | 31.92 | True | True | False |  | 1.0 |
| E1 | D_tp_2.00 | D | 6420 | 6420 | 88.1 | 90.6 | 27.09 | 20.76 | 6.33 | 28.2 | -7516.4 | 8.9e-05 | 13.3 | 40.35 | True | False | False |  | 1.0 |
| E1 | D_tp_2.50 | D | 6420 | 6420 | 85.9 | 90.6 | 38.54 | 20.76 | 17.78 | 29.5 | -7516.4 | 0.0 | 24.16 | 52.57 | True | False | False |  | 1.0 |
| E1 | D_scale_1.0_1.5 | D | 6420 | 6420 | 90.8 | 90.6 | 13.93 | 20.76 | -6.83 | 20.5 | -7361.0 | 0.011984 | 2.91 | 24.34 | True | False | False |  | 1.0 |
| E1 | D_scale_1.0_2.0 | D | 6420 | 6420 | 88.4 | 90.6 | 17.09 | 20.76 | -3.67 | 23.6 | -7361.0 | 0.003151 | 5.72 | 28.32 | True | False | True |  | 1.0 |
| E1 | D_scale_1.0_MFEp50 | D | 6420 | 6420 | 86.5 | 90.6 | 22.36 | 20.76 | 1.6 | 23.8 | -7361.0 | 0.000158 | 10.61 | 33.6 | True | False | True |  | 1.0 |
| E1 | E_time_TTF_P50 | E | 6420 | 6420 | 57.3 | 90.6 | -8.69 | 20.76 | -29.45 | 10.9 | -3791.2 | 0.002108 | -14.31 | -3.08 | True | False | False |  | 1.0 |
| E1 | E_time_TTF_P75 | E | 6420 | 6420 | 71.8 | 90.6 | 2.6 | 20.76 | -18.16 | 11.0 | -5337.2 | 0.503844 | -4.98 | 10.18 | False | False | False |  | 1.0 |
| E1 | F_act_loserMFEp50 | F | 6420 | 6420 | 88.9 | 90.6 | 14.99 | 20.76 | -5.77 | 11.5 | -7361.0 | 0.000714 | 6.36 | 23.2 | True | False | False |  | 1.0 |
| E1 | F_act_1wick | F | 6420 | 6420 | 89.3 | 90.6 | 14.52 | 20.76 | -6.24 | 12.5 | -7361.0 | 0.00213 | 5.24 | 23.21 | True | False | False |  | 1.0 |
| E1 | G_limit_skip | G | 4773 | 6420 | 89.6 | 90.6 | 26.94 | 20.76 | 6.18 | 20.0 | -7516.4 | 0.00032 | 11.85 | 41.49 | True | False | False | 74.3 | 0.7435 |
| E1 | G_limit_mkt_fallback | G | 6420 | 6420 | 85.3 | 90.6 | 20.94 | 20.76 | 0.18 | 22.2 | -7516.4 | 0.000565 | 8.99 | 32.43 | True | False | False |  | 1.0 |
| E2 | BASELINE | BASE | 6101 | 6101 | 91.1 | 91.1 | 10.26 | 10.26 | 0.0 | 4.4 | -2134.6 | 4e-06 | 5.53 | 14.52 | False | False | False |  | 1.0 |
| E2 | A_disaster_P99_9 | A | 6101 | 6101 | 91.0 | 91.1 | 7.33 | 10.26 | -2.93 | 5.2 | -1760.9 | 0.002041 | 2.42 | 11.93 | True | False | False |  | 1.0 |
| E2 | B_close_below_siglow | B | 6101 | 6101 | 49.1 | 91.1 | -13.71 | 10.26 | -23.98 | 15.4 | -859.6 | 0.0 | -15.73 | -11.72 | True | False | False |  | 1.0 |
| E2 | B_close_below_entry | B | 6101 | 6101 | 34.4 | 91.1 | -14.28 | 10.26 | -24.54 | 16.0 | -596.2 | 0.0 | -15.87 | -12.74 | True | False | False |  | 1.0 |
| E2 | B_close_below_entry_1wick | B | 6101 | 6101 | 52.6 | 91.1 | -12.57 | 10.26 | -22.83 | 14.2 | -596.2 | 0.0 | -14.68 | -10.52 | True | False | False |  | 1.0 |
| E2 | C_flat_worst_6h | C | 6101 | 6101 | 75.5 | 91.1 | -5.37 | 10.26 | -15.64 | 7.3 | -2134.6 | 0.002679 | -8.87 | -1.72 | True | False | False |  | 1.0 |
| E2 | C_flat_worst_12h | C | 6101 | 6101 | 79.7 | 91.1 | -1.49 | 10.26 | -11.76 | 5.5 | -2134.6 | 0.415602 | -5.1 | 2.26 | False | False | False |  | 1.0 |
| E2 | C_flat_worst_24h | C | 6101 | 6101 | 84.3 | 91.1 | 1.69 | 10.26 | -8.57 | 5.3 | -1833.0 | 0.386336 | -2.16 | 5.63 | False | False | False |  | 1.0 |
| E2 | D_tp_1.00 | D | 6101 | 6101 | 93.2 | 91.1 | 2.41 | 10.26 | -7.85 | 3.5 | -2134.6 | 0.219015 | -1.58 | 6.12 | False | False | False |  | 1.0 |
| E2 | D_tp_1.25 | D | 6101 | 6101 | 92.2 | 91.1 | 6.48 | 10.26 | -3.78 | 3.9 | -2134.6 | 0.002069 | 2.19 | 10.58 | True | False | False |  | 1.0 |
| E2 | D_tp_1.50 | D | 6101 | 6101 | 91.1 | 91.1 | 10.26 | 10.26 | 0.0 | 4.4 | -2134.6 | 4e-06 | 5.53 | 14.52 | True | True | False |  | 1.0 |
| E2 | D_tp_2.00 | D | 6101 | 6101 | 88.8 | 91.1 | 16.75 | 10.26 | 6.48 | 5.2 | -2134.6 | 0.0 | 11.64 | 21.43 | True | False | False |  | 1.0 |
| E2 | D_tp_2.50 | D | 6101 | 6101 | 86.3 | 91.1 | 21.35 | 10.26 | 11.09 | 6.7 | -2134.6 | 0.0 | 15.8 | 26.56 | True | False | False |  | 1.0 |
| E2 | D_scale_1.0_1.5 | D | 6101 | 6101 | 91.2 | 91.1 | 6.34 | 10.26 | -3.92 | 3.9 | -2134.6 | 0.001894 | 2.14 | 10.21 | True | False | False |  | 1.0 |
| E2 | D_scale_1.0_2.0 | D | 6101 | 6101 | 89.0 | 91.1 | 9.58 | 10.26 | -0.68 | 4.2 | -2134.6 | 6e-06 | 5.23 | 13.51 | True | False | False |  | 1.0 |
| E2 | D_scale_1.0_MFEp50 | D | 6101 | 6101 | 86.8 | 91.1 | 11.86 | 10.26 | 1.6 | 4.9 | -2134.6 | 0.0 | 7.36 | 16.06 | True | False | False |  | 1.0 |
| E2 | E_time_TTF_P50 | E | 6101 | 6101 | 54.0 | 91.1 | -11.24 | 10.26 | -21.51 | 12.8 | -1328.6 | 0.0 | -13.55 | -9.01 | True | False | False |  | 1.0 |
| E2 | E_time_TTF_P75 | E | 6101 | 6101 | 70.8 | 91.1 | -6.46 | 10.26 | -16.73 | 9.0 | -1156.1 | 3.1e-05 | -9.57 | -3.48 | True | False | False |  | 1.0 |
| E2 | F_act_loserMFEp50 | F | 6101 | 6101 | 90.9 | 91.1 | 7.06 | 10.26 | -3.2 | 2.1 | -2134.6 | 1.5e-05 | 3.94 | 10.12 | True | False | False |  | 1.0 |
| E2 | F_act_1wick | F | 6101 | 6101 | 90.8 | 91.1 | 7.02 | 10.26 | -3.24 | 2.3 | -2134.6 | 4.7e-05 | 3.63 | 10.2 | True | False | False |  | 1.0 |
| E2 | G_limit_skip | G | 4392 | 6101 | 89.9 | 91.1 | 15.76 | 10.26 | 5.5 | 3.2 | -1819.0 | 0.0 | 9.96 | 21.03 | True | False | False | 72.0 | 0.7199 |
| E2 | G_limit_mkt_fallback | G | 6101 | 6101 | 84.5 | 91.1 | 10.33 | 10.26 | 0.07 | 4.3 | -2139.4 | 4e-06 | 5.64 | 14.71 | True | False | False |  | 1.0 |
| E3 | BASELINE | BASE | 2215 | 2215 | 86.8 | 86.8 | 20.42 | 20.42 | 0.0 | 3.8 | -2671.2 | 0.000707 | 8.14 | 32.04 | False | False | False |  | 1.0 |
| E3 | A_disaster_P99_9 | A | 2215 | 2215 | 86.7 | 86.8 | 16.73 | 20.42 | -3.69 | 4.1 | -2662.0 | 0.007722 | 4.22 | 28.83 | True | False | True |  | 1.0 |
| E3 | B_close_below_siglow | B | 2215 | 2215 | 48.6 | 86.8 | -9.36 | 20.42 | -29.78 | 4.4 | -949.3 | 0.001807 | -15.25 | -3.34 | True | False | False |  | 1.0 |
| E3 | B_close_below_entry | B | 2215 | 2215 | 33.0 | 86.8 | -9.5 | 20.42 | -29.92 | 4.3 | -716.4 | 1.8e-05 | -13.78 | -5.24 | True | False | False |  | 1.0 |
| E3 | B_close_below_entry_1wick | B | 2215 | 2215 | 52.7 | 86.8 | -6.93 | 20.42 | -27.35 | 3.8 | -716.4 | 0.019532 | -12.72 | -1.02 | True | False | False |  | 1.0 |
| E3 | C_flat_worst_6h | C | 2215 | 2215 | 68.7 | 86.8 | 2.8 | 20.42 | -17.62 | 2.3 | -2073.3 | 0.533172 | -6.38 | 11.64 | False | False | False |  | 1.0 |
| E3 | C_flat_worst_12h | C | 2215 | 2215 | 73.2 | 86.8 | 8.12 | 20.42 | -12.3 | 2.3 | -1920.7 | 0.074219 | -0.84 | 16.88 | False | False | False |  | 1.0 |
| E3 | C_flat_worst_24h | C | 2215 | 2215 | 77.7 | 86.8 | 4.5 | 20.42 | -15.92 | 3.4 | -2461.1 | 0.383443 | -5.93 | 14.53 | False | False | False |  | 1.0 |
| E3 | D_tp_1.00 | D | 2215 | 2215 | 90.3 | 86.8 | 11.24 | 20.42 | -9.18 | 2.8 | -2671.2 | 0.03162 | 0.48 | 21.46 | True | False | False |  | 1.0 |
| E3 | D_tp_1.25 | D | 2215 | 2215 | 88.6 | 86.8 | 15.96 | 20.42 | -4.46 | 3.4 | -2671.2 | 0.004657 | 4.21 | 26.68 | True | False | False |  | 1.0 |
| E3 | D_tp_1.50 | D | 2215 | 2215 | 86.8 | 86.8 | 20.42 | 20.42 | 0.0 | 3.8 | -2671.2 | 0.000707 | 8.14 | 32.04 | True | True | False |  | 1.0 |
| E3 | D_tp_2.00 | D | 2215 | 2215 | 83.2 | 86.8 | 27.34 | 20.42 | 6.92 | 5.2 | -2671.2 | 5.2e-05 | 13.09 | 40.54 | True | False | False |  | 1.0 |
| E3 | D_tp_2.50 | D | 2215 | 2215 | 79.4 | 86.8 | 34.68 | 20.42 | 14.26 | 5.1 | -2671.2 | 2e-06 | 19.47 | 48.19 | True | False | False |  | 1.0 |
| E3 | D_scale_1.0_1.5 | D | 2215 | 2215 | 87.0 | 86.8 | 15.83 | 20.42 | -4.59 | 3.3 | -2671.2 | 0.003713 | 4.22 | 26.16 | True | False | False |  | 1.0 |
| E3 | D_scale_1.0_2.0 | D | 2215 | 2215 | 83.9 | 86.8 | 19.29 | 20.42 | -1.13 | 4.0 | -2671.2 | 0.000677 | 7.52 | 30.36 | True | False | False |  | 1.0 |
| E3 | D_scale_1.0_MFEp50 | D | 2215 | 2215 | 81.7 | 86.8 | 22.68 | 20.42 | 2.25 | 4.0 | -2671.2 | 8.8e-05 | 10.5 | 33.74 | True | False | False |  | 1.0 |
| E3 | E_time_TTF_P50 | E | 2215 | 2215 | 54.9 | 86.8 | -6.74 | 20.42 | -27.16 | 3.7 | -1589.5 | 0.032286 | -12.8 | -0.88 | True | False | False |  | 1.0 |
| E3 | E_time_TTF_P75 | E | 2215 | 2215 | 67.9 | 86.8 | 1.21 | 20.42 | -19.21 | 3.0 | -2290.2 | 0.774275 | -7.1 | 9.53 | False | False | False |  | 1.0 |
| E3 | F_act_loserMFEp50 | F | 2215 | 2215 | 88.0 | 86.8 | 13.04 | 20.42 | -7.38 | 2.9 | -2671.2 | 0.005285 | 3.57 | 21.92 | True | False | False |  | 1.0 |
| E3 | F_act_1wick | F | 2215 | 2215 | 88.1 | 86.8 | 15.76 | 20.42 | -4.66 | 2.9 | -2671.2 | 0.001754 | 5.06 | 25.68 | True | False | False |  | 1.0 |
| E3 | G_limit_skip | G | 1549 | 2215 | 84.7 | 86.8 | 26.02 | 20.42 | 5.59 | 3.3 | -2138.7 | 0.000522 | 11.01 | 40.76 | True | False | False | 69.9 | 0.6993 |
| E3 | G_limit_mkt_fallback | G | 2215 | 2215 | 82.4 | 86.8 | 19.96 | 20.42 | -0.46 | 3.8 | -2656.3 | 0.000871 | 7.63 | 31.27 | True | False | True |  | 1.0 |
| E4 | BASELINE | BASE | 1470 | 1470 | 79.0 | 79.0 | 48.72 | 48.72 | 0.0 | 7.5 | -6857.1 | 0.001345 | 18.03 | 78.86 | False | False | False |  | 1.0 |
| E4 | A_disaster_P99_9 | A | 1470 | 1470 | 78.8 | 79.0 | 44.15 | 48.72 | -4.57 | 7.2 | -6857.1 | 0.003714 | 13.56 | 73.37 | True | False | False |  | 1.0 |
| E4 | B_close_below_siglow | B | 1470 | 1470 | 51.2 | 79.0 | -1.49 | 48.72 | -50.21 | 3.6 | -2497.2 | 0.872975 | -19.69 | 16.59 | False | False | False |  | 1.0 |
| E4 | B_close_below_entry | B | 1470 | 1470 | 38.4 | 79.0 | 0.03 | 48.72 | -48.69 | 1.9 | -1447.1 | 0.996562 | -13.47 | 13.59 | False | False | False |  | 1.0 |
| E4 | B_close_below_entry_1wick | B | 1470 | 1470 | 51.6 | 79.0 | -2.45 | 48.72 | -51.17 | 2.6 | -2002.7 | 0.791663 | -20.68 | 16.53 | False | False | False |  | 1.0 |
| E4 | C_flat_worst_6h | C | 1470 | 1470 | 63.6 | 79.0 | 18.31 | 48.72 | -30.41 | 4.9 | -6857.1 | 0.146599 | -7.22 | 42.53 | False | False | False |  | 1.0 |
| E4 | C_flat_worst_12h | C | 1470 | 1470 | 65.4 | 79.0 | 19.61 | 48.72 | -29.11 | 5.8 | -6857.1 | 0.130058 | -6.76 | 44.11 | False | False | False |  | 1.0 |
| E4 | C_flat_worst_24h | C | 1470 | 1470 | 69.9 | 79.0 | 24.06 | 48.72 | -24.65 | 4.6 | -4869.9 | 0.059906 | -0.8 | 48.69 | False | False | False |  | 1.0 |
| E4 | D_tp_1.00 | D | 1470 | 1470 | 84.1 | 79.0 | 36.18 | 48.72 | -12.54 | 5.7 | -6857.1 | 0.008775 | 9.63 | 63.29 | True | False | False |  | 1.0 |
| E4 | D_tp_1.25 | D | 1470 | 1470 | 82.0 | 79.0 | 47.26 | 48.72 | -1.46 | 6.2 | -6857.1 | 0.001304 | 18.56 | 76.96 | True | False | False |  | 1.0 |
| E4 | D_tp_1.50 | D | 1470 | 1470 | 79.0 | 79.0 | 48.72 | 48.72 | 0.0 | 7.5 | -6857.1 | 0.001345 | 18.03 | 78.86 | True | True | False |  | 1.0 |
| E4 | D_tp_2.00 | D | 1470 | 1470 | 74.1 | 79.0 | 57.83 | 48.72 | 9.11 | 9.5 | -6859.4 | 0.000776 | 23.52 | 91.99 | True | False | False |  | 1.0 |
| E4 | D_tp_2.50 | D | 1470 | 1470 | 70.6 | 79.0 | 73.65 | 48.72 | 24.94 | 9.5 | -6859.4 | 6e-05 | 37.5 | 109.86 | True | False | False |  | 1.0 |
| E4 | D_scale_1.0_1.5 | D | 1470 | 1470 | 80.1 | 79.0 | 42.45 | 48.72 | -6.27 | 6.6 | -6857.1 | 0.002563 | 14.36 | 70.49 | True | False | False |  | 1.0 |
| E4 | D_scale_1.0_2.0 | D | 1470 | 1470 | 76.0 | 79.0 | 47.0 | 48.72 | -1.71 | 7.6 | -6857.1 | 0.001371 | 17.88 | 76.26 | True | False | False |  | 1.0 |
| E4 | D_scale_1.0_MFEp50 | D | 1470 | 1470 | 73.3 | 79.0 | 54.37 | 48.72 | 5.65 | 7.5 | -6857.1 | 0.000311 | 24.86 | 84.13 | True | False | False |  | 1.0 |
| E4 | E_time_TTF_P50 | E | 1470 | 1470 | 56.9 | 79.0 | 11.79 | 48.72 | -36.93 | 3.2 | -2693.4 | 0.166587 | -4.43 | 28.72 | False | False | False |  | 1.0 |
| E4 | E_time_TTF_P75 | E | 1470 | 1470 | 65.0 | 79.0 | 24.21 | 48.72 | -24.51 | 2.6 | -4869.9 | 0.028971 | 3.19 | 45.91 | True | False | False |  | 1.0 |
| E4 | F_act_loserMFEp50 | F | 1470 | 1470 | 84.8 | 79.0 | 64.43 | 48.72 | 15.72 | 5.1 | -6857.1 | 1e-06 | 37.71 | 89.81 | True | True | True |  | 1.0 |
| E4 | F_act_1wick | F | 1470 | 1470 | 84.6 | 79.0 | 63.55 | 48.72 | 14.84 | 5.3 | -6857.1 | 1e-06 | 36.27 | 88.51 | True | True | True |  | 1.0 |
| E4 | G_limit_skip | G | 1085 | 1470 | 76.0 | 79.0 | 47.81 | 48.72 | -0.91 | 7.0 | -6857.1 | 0.013883 | 10.33 | 86.32 | True | False | False | 73.8 | 0.7381 |
| E4 | G_limit_mkt_fallback | G | 1470 | 1470 | 74.0 | 79.0 | 46.61 | 48.72 | -2.11 | 7.2 | -6857.1 | 0.002149 | 16.26 | 76.37 | True | False | False |  | 1.0 |

## 5. Flag index

**keepn_improve = True:**
- E1 D_tp_1.50 (net=20.76, win=90.6%)
- E2 D_tp_1.50 (net=10.26, win=91.1%)
- E3 D_tp_1.50 (net=20.42, win=86.8%)
- E4 D_tp_1.50 (net=48.72, win=79.0%)
- E4 F_act_loserMFEp50 (net=64.43, win=84.8%)
- E4 F_act_1wick (net=63.55, win=84.6%)

**keepn_defend = True:**
- E1 A_disaster_P99_9 (maxdd=16.3%, worst=-5272.8)
- E1 D_scale_1.0_2.0 (maxdd=23.6%, worst=-7361.0)
- E1 D_scale_1.0_MFEp50 (maxdd=23.8%, worst=-7361.0)
- E3 A_disaster_P99_9 (maxdd=4.1%, worst=-2662.0)
- E3 G_limit_mkt_fallback (maxdd=3.8%, worst=-2656.3)
- E4 F_act_loserMFEp50 (maxdd=5.1%, worst=-6857.1)
- E4 F_act_1wick (maxdd=5.3%, worst=-6857.1)

## 6. n-retention exceptions

- E1 G_limit_skip: n_filled=4773, fill_rate=0.7435, net_filled=26.94, net_all_signals=20.03 -> FAILS OWNER N-FLOOR
- E2 G_limit_skip: n_filled=4392, fill_rate=0.7199, net_filled=15.76, net_all_signals=11.35 -> FAILS OWNER N-FLOOR
- E3 G_limit_skip: n_filled=1549, fill_rate=0.6993, net_filled=26.02, net_all_signals=18.19 -> FAILS OWNER N-FLOOR
- E4 G_limit_skip: n_filled=1085, fill_rate=0.7381, net_filled=47.81, net_all_signals=35.28 -> FAILS OWNER N-FLOOR

## 7. Benjamini–Hochberg (within-study family, q=0.05)

- Family size (new policy cells) = 84
- q = 0.05
- Rejected = 68
- Rejected cells:
  - E1 A_disaster_P99_9 p=0.000215644
  - E1 B_close_below_siglow p=2.05609e-09
  - E1 B_close_below_entry p=4.53212e-10
  - E1 B_close_below_entry_1wick p=1.96777e-06
  - E1 C_flat_worst_6h p=0.0387479
  - E1 C_flat_worst_12h p=0.00261526
  - E1 C_flat_worst_24h p=0.0071319
  - E1 D_tp_1.25 p=0.0174253
  - E1 D_tp_1.50 p=0.000626198
  - E1 D_tp_2.00 p=8.89873e-05
  - E1 D_tp_2.50 p=1.96369e-07
  - E1 D_scale_1.0_1.5 p=0.011984
  - E1 D_scale_1.0_2.0 p=0.00315061
  - E1 D_scale_1.0_MFEp50 p=0.000157892
  - E1 E_time_TTF_P50 p=0.00210797
  - E1 F_act_loserMFEp50 p=0.000713923
  - E1 F_act_1wick p=0.00213027
  - E1 G_limit_skip p=0.000320005
  - E1 G_limit_mkt_fallback p=0.000565169
  - E2 A_disaster_P99_9 p=0.00204083
  - E2 B_close_below_siglow p=0
  - E2 B_close_below_entry p=0
  - E2 B_close_below_entry_1wick p=0
  - E2 C_flat_worst_6h p=0.00267922
  - E2 D_tp_1.25 p=0.00206852
  - E2 D_tp_1.50 p=4.3822e-06
  - E2 D_tp_2.00 p=1.68998e-11
  - E2 D_tp_2.50 p=7.54952e-15
  - E2 D_scale_1.0_1.5 p=0.00189445
  - E2 D_scale_1.0_2.0 p=5.98285e-06
  - E2 D_scale_1.0_MFEp50 p=6.62883e-08
  - E2 E_time_TTF_P50 p=0
  - E2 E_time_TTF_P75 p=3.11754e-05
  - E2 F_act_loserMFEp50 p=1.49924e-05
  - E2 F_act_1wick p=4.66724e-05
  - E2 G_limit_skip p=1.56083e-08
  - E2 G_limit_mkt_fallback p=3.86963e-06
  - E3 A_disaster_P99_9 p=0.00772206
  - E3 B_close_below_siglow p=0.0018065
  - E3 B_close_below_entry p=1.83274e-05
  - E3 B_close_below_entry_1wick p=0.0195318
  - E3 D_tp_1.00 p=0.0316196
  - E3 D_tp_1.25 p=0.00465666
  - E3 D_tp_1.50 p=0.000706598
  - E3 D_tp_2.00 p=5.20059e-05
  - E3 D_tp_2.50 p=1.52605e-06
  - E3 D_scale_1.0_1.5 p=0.0037128
  - E3 D_scale_1.0_2.0 p=0.000676932
  - E3 D_scale_1.0_MFEp50 p=8.75167e-05
  - E3 E_time_TTF_P50 p=0.0322863
  - E3 F_act_loserMFEp50 p=0.00528475
  - E3 F_act_1wick p=0.00175419
  - E3 G_limit_skip p=0.000521597
  - E3 G_limit_mkt_fallback p=0.000871002
  - E4 A_disaster_P99_9 p=0.0037136
  - E4 D_tp_1.00 p=0.00877496
  - E4 D_tp_1.25 p=0.00130379
  - E4 D_tp_1.50 p=0.00134461
  - E4 D_tp_2.00 p=0.000775971
  - E4 D_tp_2.50 p=5.97234e-05
  - E4 D_scale_1.0_1.5 p=0.00256266
  - E4 D_scale_1.0_2.0 p=0.00137055
  - E4 D_scale_1.0_MFEp50 p=0.00031104
  - E4 E_time_TTF_P75 p=0.0289708
  - E4 F_act_loserMFEp50 p=6.39572e-07
  - E4 F_act_1wick p=1.11232e-06
  - E4 G_limit_skip p=0.0138829
  - E4 G_limit_mkt_fallback p=0.00214864
- Union ledger (union_ledger.json) was **not** updated by this pass.

## 8. Same-bar note

Headline resolution follows §3.2. Intrabar touch SL (Family A disaster SL): pessimistic SL-first if that bar's low ≤ SL and high ≥ TP; `net_opt` (extra col) = TP-first. Close-based stops (Family B): TP-first (a live TP fills on high; a close-stop cannot fire until the close); `net_pess` = close-first on the same bar. Time-stop / scale / TP-only: TP on high else close at K; `net_opt` = `net`. Family F BE-stop same bar as TP after activation: SL-first (touch stop). The two columns are never averaged; the headline is the honest column above for each family.

## 9. In-sample tercile disclosure

Family C cut points (1/3 and 2/3 quantiles of uPnL_wick at each checkpoint h=6/12/24h) are computed on the SAME TRAIN trades used for the baseline — they are an in-sample distribution, not out-of-sample. This is disclosed here and not presented as OOS evidence.

## 10. Stop

AGENT STOPS. No freeze. No E-VAL. Owner evaluates.
