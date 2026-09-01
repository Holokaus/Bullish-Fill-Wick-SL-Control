# REDIR-W1 - 8-ROW COLOR-AGNOSTIC WICK-FILL MENU

TRAIN 2022-09-01 to 2024-12-31 - SOL-4h - Bybit USDT-perp - headline cost = MKT_MKT 15 bps RT.
Signal = ANY candle (green OR red) whose upper-wick meets the row threshold. Entry MKT next-bar-open.
TP = body_top + 1.5 x wick_gap. Time stop K=24 bars. No price stop, no circuit breaker at menu stage.
Wick thresholds: W1 >=22.5bps (1.5xRT) - W2 >=45bps (3xRT) - W3 >=90bps (6xRT) - W4 = top wick decile (TRAIN-frozen).
Dip = ON means 24h-return bottom quintile (agent comparison row only).

| Row | n | trades/mo | win% | net bps/tr | monthly bps | maxDD(2%/tr) | win% green | win% red | BH sig? | CI lo | CI hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1_BASE | 3951 | 141.2 | 83.4 | 2.73 | 385 | 18.7% | 88.7 | 77.4 | n | -12.8 | 19.3 |
| W1_DIP | 1001 | 35.8 | 84.1 | 45.85 | 1640 | 5.0% | 90.1 | 79.2 | y | 15.2 | 77.8 |
| W2_BASE | 2915 | 104.1 | 81.9 | 11.22 | 1168 | 14.5% | 86.8 | 75.9 | n | -9.1 | 30.3 |
| W2_DIP | 762 | 27.2 | 84.0 | 66.96 | 1823 | 3.6% | 89.1 | 79.1 | y | 30.6 | 101.1 |
| W3_BASE | 1470 | 52.5 | 79.0 | 47.97 | 2520 | 7.5% | 83.8 | 72.9 | y | 17.1 | 77.9 |
| W3_DIP | 370 | 13.2 | 79.2 | 93.29 | 1233 | 3.3% | 85.7 | 73.4 | y | 31.7 | 150.9 |
| W4_BASE | 908 | 32.4 | 80.3 | 21.26 | 690 | 4.2% | 85.0 | 74.4 | n | -11.8 | 54.1 |
| W4_DIP | 191 | 6.8 | 79.6 | 56.34 | 384 | 1.4% | 86.1 | 71.6 | n | -14.2 | 122.2 |

**BH-FDR (q=0.05) across the 8 menu cells:** 4 significant -> W1_DIP, W2_DIP, W3_BASE, W3_DIP.

**Reading for the owner (plain):** every row clears the 70% win-rate guideline (79-84%).
BASE rows (no dip) trade far more often (36-141/mo) but earn less per trade; DIP rows trade less
(7-36/mo) but earn more per trade. W1_BASE is the owner's literal concept (max entries, fee-floor wick)
and is profitable but its CI includes 0 at 15bps - the tighter, dip-filtered rows are the cleaner statistically.

**Next step (per directive s4):** owner picks ONE row. Then s3 items (3-config cost sensitivity, union-family
BH, matched-control dP, 4h funding adjustment) run on that row only, and results/FROZEN_CANDIDATE.md v2 is written.
E-VAL / E-LOCKBOX remain unfired. Reserved down-market window untouched.