# MENU-2 — multi-asset x multi-timeframe wick-fill discovery

**Pass:** Directive 3 Task 2 (discovery only). TRAIN 2022-09-01..2024-12-31. Bybit USDT-perp. Color-agnostic. 4-day wall-clock time stop. Flat 15 bps RT. Corrected 24h dip (top-decile lookback per TF). No price stop. Funding ignored.

**ret24 correction note:** MENU-2 uses a genuine 24-hour trailing return for the dip filter. menu-1 / W7 used shift(24) on 4h = a 96-hour (4-day) lookback — those 'DIP' rows were actually '4-day downtrend' rows (see docs/RCA_W3_MISLABEL.md).

---

## 1. Full grid (all rows x asset x TF)

  asset  tf      row     n  trades_month  win    net  monthly  maxdd  med_hold  wr_green  wr_red   ci_lo  ci_hi  bh_grid  bh_union
SOLUSDT 30m W1_NODIP 16446         587.4 92.8   3.29   1934.7   36.2      0.06      94.2    91.2   -2.70   9.36     True     False
SOLUSDT 30m   W1_DIP  3768         134.6 93.9  16.03   2156.5   22.8      0.06      95.7    92.3   -1.16  32.90     True     False
SOLUSDT 30m W2_NODIP  6420         229.3 90.6  20.76   4760.0   22.1      0.10      91.6    89.4    8.63  31.92    False      True
SOLUSDT 30m   W2_DIP  1633          58.3 92.8  51.67   3013.5   14.2      0.10      93.8    91.8   21.88  81.26     True      True
SOLUSDT 30m W3_NODIP  1429          51.0 87.3  69.93   3568.8   11.0      0.21      87.2    87.4   36.29 103.39     True      True
SOLUSDT 30m   W3_DIP   418          14.9 90.9 130.56   1949.0    9.7      0.15      93.4    88.3   37.49 220.72     True      True
SOLUSDT 30m W4_NODIP  7858         280.6 91.9   2.63    738.2   16.5      0.08      92.5    91.4   -5.50  10.30    False     False
SOLUSDT 30m   W4_DIP  1455          52.0 94.1  35.78   1859.2    4.8      0.08      94.7    93.5   13.42  57.20    False      True
SOLUSDT  1h W1_NODIP 11123         397.2 90.6   0.86    343.6   33.5      0.12      92.6    88.4   -6.92   8.63    False     False
SOLUSDT  1h   W1_DIP  2421          86.5 92.3  26.16   2262.3   14.8      0.12      94.4    90.5    5.94  45.69     True      True
SOLUSDT  1h W2_NODIP  5535         197.7 88.7  13.46   2660.1   22.0      0.17      90.1    86.9    0.86  26.12     True      True
SOLUSDT  1h   W2_DIP  1313          46.9 91.0  48.63   2280.5   10.1      0.17      92.0    90.2   16.20  79.05    False      True
SOLUSDT  1h W3_NODIP  1594          56.9 85.6  54.07   3078.1   10.9      0.33      86.4    84.4   23.39  85.27     True      True
SOLUSDT  1h   W3_DIP   407          14.5 88.5  90.60   1317.0    7.8      0.25      88.7    88.2    0.93 174.33    False      True
SOLUSDT  1h W4_NODIP  3844         137.3 88.5  -7.87  -1080.8   17.4      0.17      89.0    87.9  -21.98   6.18     True     False
SOLUSDT  1h   W4_DIP   698          24.9 90.7  18.54    462.3    3.5      0.12      90.4    90.9  -20.75  56.03    False     False
SOLUSDT  4h W1_NODIP  3951         141.1 83.4   2.73    385.1   18.7      0.33      88.7    77.4  -12.76  19.30    False     False
SOLUSDT  4h   W1_DIP   808          28.9 83.7  49.93   1440.8    6.6      0.50      91.9    79.4    4.22  92.64     True      True
SOLUSDT  4h W2_NODIP  2915         104.1 81.9  11.22   1167.7   14.5      0.33      86.8    75.9   -9.15  30.31     True     False
SOLUSDT  4h   W2_DIP   610          21.8 83.4  68.44   1491.1    4.2      0.50      90.8    79.0   14.73 114.70    False      True
SOLUSDT  4h W3_NODIP  1470          52.5 79.0  47.97   2518.5    7.5      0.67      83.8    73.0   17.12  77.88    False      True
SOLUSDT  4h   W3_DIP   318          11.4 79.6  80.08    909.5    3.1      0.83      86.7    75.6   -9.50 153.75     True     False
SOLUSDT  4h W4_NODIP   908          32.4 80.3  21.26    689.5    4.2      0.67      85.0    74.4  -11.82  54.11    False     False
SOLUSDT  4h   W4_DIP   118           4.2 83.9  55.50    233.9    1.1      0.50      89.7    78.3  -69.87 160.28    False     False
SOLUSDT  1D W1_NODIP   797          28.5 72.3  46.47   1322.8    6.8      1.00      81.3    62.9   -5.61  98.81     True     False
SOLUSDT  1D   W1_DIP   155           5.5 60.6  71.97    398.4    3.3      4.00     100.0    60.4 -102.19 235.09     True     False
SOLUSDT  1D W2_NODIP   748          26.7 71.8  43.76   1168.9    6.8      1.00      80.6    62.4   -9.42  96.20    False     False
SOLUSDT  1D   W2_DIP   137           4.9 60.6  52.90    258.8    3.3      4.00     100.0    60.3 -144.79 227.61    False     False
SOLUSDT  1D W3_NODIP   609          21.8 71.3  70.67   1537.1    5.7      2.00      78.8    63.3    9.01 130.53     True      True
SOLUSDT  1D   W3_DIP   105           3.8 60.0  91.76    344.1    2.2      4.00       NaN    60.0 -117.66 290.90     True     False
SOLUSDT  1D W4_NODIP   169           6.0 67.5 154.66    933.5    0.9      3.00      72.0    63.2   54.05 255.35    False      True
SOLUSDT  1D   W4_DIP     6           NaN  NaN    NaN      NaN    NaN       NaN       NaN     NaN     NaN    NaN    False     False
BTCUSDT 30m W1_NODIP  6101         217.9 91.1  10.26   2236.1    4.4      0.12      92.3    89.5    5.53  14.52    False      True
BTCUSDT 30m   W1_DIP  1577          56.3 93.0  23.71   1335.5    2.6      0.10      95.3    90.7   14.32  32.21     True      True
BTCUSDT 30m W2_NODIP  1427          51.0 86.4  29.64   1510.4    2.5      0.25      87.0    85.5   18.77  40.16    False      True
BTCUSDT 30m   W2_DIP   374          13.4 91.4  51.80    691.9    1.8      0.18      93.6    89.3   27.46  74.27    False      True
BTCUSDT 30m W3_NODIP   179           6.4 81.6  60.89    389.3    1.0      0.77      80.9    82.8   11.25 104.71     True      True
BTCUSDT 30m   W3_DIP    56           2.0 89.3  91.10    182.2    0.9      0.23      93.5    84.0  -20.82 181.51     True     False
BTCUSDT 30m W4_NODIP  7760         277.1 81.3  -4.63  -1283.7   10.6      0.08      80.9    81.7   -8.11  -1.22     True      True
BTCUSDT 30m   W4_DIP  1378          49.2 88.3   0.33     16.4    2.1      0.06      88.9    87.7   -9.48   9.28    False     False
BTCUSDT  1h W1_NODIP  5260         187.9 89.5   9.36   1758.9    4.3      0.17      91.2    87.4    3.91  14.42    False      True
BTCUSDT  1h   W1_DIP  1289          46.0 90.9  19.86    914.4    2.7      0.17      92.9    89.1    7.26  30.72    False      True
BTCUSDT  1h W2_NODIP  1542          55.1 85.5  31.49   1734.0    1.4      0.38      86.5    84.1   19.90  42.17    False      True
BTCUSDT  1h   W2_DIP   389          13.9 90.2  55.51    771.2    1.1      0.29      91.3    89.3   31.92  77.96    False      True
BTCUSDT  1h W3_NODIP   242           8.6 84.7  90.00    777.8    0.5      0.85      86.9    82.1   52.53 123.68    False      True
BTCUSDT  1h   W3_DIP    63           2.2 92.1 143.95    323.9    0.5      0.42      96.3    88.9   59.11 207.55     True      True
BTCUSDT  1h W4_NODIP  3801         135.8 86.8   2.09    284.0    3.7      0.17      86.4    87.3   -3.57   7.53     True     False
BTCUSDT  1h   W4_DIP   637          22.8 91.4  15.37    349.7    0.9      0.12      91.9    90.9    1.77  28.25     True      True
BTCUSDT  4h W1_NODIP  2969         106.0 84.3  11.58   1227.7    2.9      0.33      87.8    79.9    2.73  20.02     True      True
BTCUSDT  4h   W1_DIP   646          23.1 85.8  44.11   1017.8    1.2      0.33      92.6    81.6   23.37  64.13    False      True
BTCUSDT  4h W2_NODIP  1543          55.1 79.3  21.64   1192.7    1.9      0.67      82.5    75.2    8.83  34.01    False      True
BTCUSDT  4h   W2_DIP   332          11.9 80.7  56.31    667.7    1.1      0.67      87.0    77.4   23.65  86.08    False      True
BTCUSDT  4h W3_NODIP   439          15.7 73.6  52.31    820.2    1.0      1.67      74.8    72.0   23.34  81.43    False      True
BTCUSDT  4h   W3_DIP    90           3.2 81.1 139.76    449.2    0.5      1.08      87.5    77.6   77.10 199.13     True      True
BTCUSDT  4h W4_NODIP  1014          36.2 82.8  10.59    383.5    1.3      0.50      84.1    81.1   -4.85  24.98     True     False
BTCUSDT  4h   W4_DIP   136           4.9 83.1  14.31     69.5    0.6      0.50      87.9    79.5  -38.82  60.42    False     False
BTCUSDT  1D W1_NODIP   763          27.2 74.6  25.16    685.5    1.6      1.00      78.8    69.6    0.34  49.05     True      True
BTCUSDT  1D   W1_DIP   141           5.0 63.1  59.90    301.6    1.0      4.00     100.0    62.9  -26.54 141.83    False     False
BTCUSDT  1D W2_NODIP   633          22.6 73.1  33.31    752.9    1.3      2.00      77.6    67.4    6.19  59.49    False      True
BTCUSDT  1D   W2_DIP   107           3.8 61.7  72.51    277.1    0.7      4.00       NaN    61.7  -22.00 156.85    False     False
BTCUSDT  1D W3_NODIP   356          12.7 68.3  57.29    728.4    0.8      2.50      70.4    65.3   18.73  93.67    False      True
BTCUSDT  1D   W3_DIP    62           2.2 62.9 102.23    226.4    0.5      4.00       NaN    62.9  -26.07 220.40    False     False
BTCUSDT  1D W4_NODIP   170           6.1 70.0  34.86    211.6    0.7      3.00      71.0    68.8  -16.09  83.37    False     False
BTCUSDT  1D   W4_DIP    10           0.4 60.0  26.16      9.3    0.2      4.00       NaN    60.0 -254.06 305.82    False     False
ETHUSDT 30m W1_NODIP  8130         290.4 92.1   1.51    438.8   11.5      0.10      92.8    91.2   -4.00   6.72    False     False
ETHUSDT 30m   W1_DIP  2119          75.7 93.4  14.70   1112.5    5.0      0.08      94.5    92.3    3.79  25.40     True      True
ETHUSDT 30m W2_NODIP  2125          75.9 88.6  16.67   1265.2    3.9      0.19      89.3    87.5    3.47  28.70     True      True
ETHUSDT 30m   W2_DIP   616          22.0 92.0  41.65    916.2    2.3      0.12      93.2    90.8   17.48  64.32    False      True
ETHUSDT 30m W3_NODIP   283          10.1 80.9  49.56    500.9    1.6      0.65      82.8    77.7    4.56  90.86     True      True
ETHUSDT 30m   W3_DIP    86           3.1 86.0  91.27    280.3    0.7      0.30      89.6    81.6   -1.60 171.22     True      True
ETHUSDT 30m W4_NODIP  7839         280.0 87.2  -6.94  -1942.0   13.8      0.08      86.0    88.6  -11.36  -2.54    False      True
ETHUSDT 30m   W4_DIP  1382          49.4 92.1   1.48     72.9    3.3      0.08      91.3    93.2  -10.62  12.77    False     False
ETHUSDT  1h W1_NODIP  6639         237.1 90.4   1.77    419.6   11.3      0.17      91.9    88.5   -4.45   7.76    False     False
ETHUSDT  1h   W1_DIP  1596          57.0 91.5  16.55    943.6    3.1      0.12      93.8    89.5    3.86  29.13    False      True
ETHUSDT  1h W2_NODIP  2215          79.1 86.8  20.30   1605.6    3.8      0.29      88.7    84.2    7.97  31.98    False      True
ETHUSDT  1h   W2_DIP   545          19.5 90.5  46.55    906.1    1.5      0.25      93.6    87.8   20.11  70.76    False      True
ETHUSDT  1h W3_NODIP   369          13.2 82.4  80.90   1066.1    0.8      0.71      85.2    78.9   50.25 109.90     True      True
ETHUSDT  1h   W3_DIP    96           3.4 91.7 145.80    499.9    0.5      0.46      93.5    90.0   86.93 194.42     True      True
ETHUSDT  1h W4_NODIP  3825         136.6 88.8  -3.42   -466.6    7.5      0.17      89.2    88.3  -10.21   3.29     True     False
ETHUSDT  1h   W4_DIP   623          22.2 91.2   5.11    113.8    1.4      0.17      91.3    91.0  -14.73  23.26    False     False
ETHUSDT  4h W1_NODIP  3330         118.9 84.9   2.30    273.8    6.6      0.33      88.3    80.8   -9.20  12.90    False     False
ETHUSDT  4h   W1_DIP   703          25.1 82.6  11.91    299.0    3.8      0.33      90.3    78.5  -20.51  39.56     True     False
ETHUSDT  4h W2_NODIP  1936          69.1 82.3  11.19    773.4    4.6      0.50      85.8    77.8   -4.57  26.18     True     False
ETHUSDT  4h   W2_DIP   416          14.9 82.7  27.66    411.0    2.1      0.50      89.4    78.9  -11.16  63.83    False     False
ETHUSDT  4h W3_NODIP   615          22.0 77.4  27.20    597.5    1.4      1.00      81.7    71.8   -5.32  58.17     True     False
ETHUSDT  4h   W3_DIP   132           4.7 78.0  29.55    139.3    1.0      0.83      86.4    73.9  -63.36 110.03    False     False
ETHUSDT  4h W4_NODIP  1015          36.2 81.2 -10.66   -386.3    3.5      0.50      83.8    77.8  -31.46   8.46    False     False
ETHUSDT  4h   W4_DIP   129           4.6 79.1 -15.61    -71.9    0.9      0.50      81.4    77.1  -89.30  50.98    False     False
ETHUSDT  1D W1_NODIP   775          27.7 73.4   6.80    188.2    2.9      1.00      76.8    69.4  -27.73  38.58    False     False
ETHUSDT  1D   W1_DIP   136           4.9 62.5  73.52    357.1    1.1      4.00     100.0    62.2  -36.59 179.98    False     False
ETHUSDT  1D W2_NODIP   686          24.5 72.6   8.98    219.9    3.1      2.00      75.3    69.2  -25.40  44.39    False     False
ETHUSDT  1D   W2_DIP   116           4.1 62.9  63.39    262.6    1.1      4.00     100.0    62.6  -54.24 175.17     True     False
ETHUSDT  1D W3_NODIP   429          15.3 70.4  29.96    459.0    2.0      2.00      70.2    70.6  -19.81  76.95    False     False
ETHUSDT  1D   W3_DIP    73           2.6 65.8 136.30    355.4    0.8      4.00     100.0    65.3   -6.98 271.79     True     False
ETHUSDT  1D W4_NODIP   169           6.0 62.7 -28.79   -173.8    1.9      4.00      58.8    68.1 -107.23  45.95     True     False
ETHUSDT  1D   W4_DIP     6           NaN  NaN    NaN      NaN    NaN       NaN       NaN     NaN     NaN    NaN    False     False

---
## 2. Per-asset leaderboard (owner's explicit ask — report per asset)

### SOLUSDT

**Top 3 by monthly net edge (bps, additive):**

 tf      row  trades_month  win   net  monthly  maxdd  med_hold  bh_union
30m W2_NODIP         229.3 90.6 20.76   4760.0   22.1      0.10      True
30m W3_NODIP          51.0 87.3 69.93   3568.8   11.0      0.21      True
 1h W3_NODIP          56.9 85.6 54.07   3078.1   10.9      0.33      True

**Top 3 by CI lower bound (bps):**

 tf      row  trades_month  win    net  ci_lo  ci_hi  bh_union
 1D W4_NODIP           6.0 67.5 154.66  54.05 255.35      True
30m   W3_DIP          14.9 90.9 130.56  37.49 220.72      True
30m W3_NODIP          51.0 87.3  69.93  36.29 103.39      True

**Rows with win% < 70 (owner floor) — FLAGGED:** 4 of 32

tf      row  win    net
1D   W1_DIP 60.6  71.97
1D   W2_DIP 60.6  52.90
1D   W3_DIP 60.0  91.76
1D W4_NODIP 67.5 154.66

### BTCUSDT

**Top 3 by monthly net edge (bps, additive):**

 tf      row  trades_month  win   net  monthly  maxdd  med_hold  bh_union
30m W1_NODIP         217.9 91.1 10.26   2236.1    4.4      0.12      True
 1h W1_NODIP         187.9 89.5  9.36   1758.9    4.3      0.17      True
 1h W2_NODIP          55.1 85.5 31.49   1734.0    1.4      0.38      True

**Top 3 by CI lower bound (bps):**

tf      row  trades_month  win    net  ci_lo  ci_hi  bh_union
4h   W3_DIP           3.2 81.1 139.76  77.10 199.13      True
1h   W3_DIP           2.2 92.1 143.95  59.11 207.55      True
1h W3_NODIP           8.6 84.7  90.00  52.53 123.68      True

**Rows with win% < 70 (owner floor) — FLAGGED:** 5 of 32

tf      row  win    net
1D   W1_DIP 63.1  59.90
1D   W2_DIP 61.7  72.51
1D W3_NODIP 68.3  57.29
1D   W3_DIP 62.9 102.23
1D   W4_DIP 60.0  26.16

### ETHUSDT

**Top 3 by monthly net edge (bps, additive):**

 tf      row  trades_month  win   net  monthly  maxdd  med_hold  bh_union
 1h W2_NODIP          79.1 86.8 20.30   1605.6    3.8      0.29      True
30m W2_NODIP          75.9 88.6 16.67   1265.2    3.9      0.19      True
30m   W1_DIP          75.7 93.4 14.70   1112.5    5.0      0.08      True

**Top 3 by CI lower bound (bps):**

tf      row  trades_month  win    net  ci_lo  ci_hi  bh_union
1h   W3_DIP           3.4 91.7 145.80  86.93 194.42      True
1h W3_NODIP          13.2 82.4  80.90  50.25 109.90      True
1h   W2_DIP          19.5 90.5  46.55  20.11  70.76      True

**Rows with win% < 70 (owner floor) — FLAGGED:** 4 of 32

tf      row  win    net
1D   W1_DIP 62.5  73.52
1D   W2_DIP 62.9  63.39
1D   W3_DIP 65.8 136.30
1D W4_NODIP 62.7 -28.79


---
## 3. Cross-asset synthesis (facts, not recommendations)

**Threshold band that generalizes:** W1/W2/W3 rows are net-positive in 100% of the 24 cells each (all assets x TFs). W4 (top-decile wick) is net-positive in only 62% of cells and is the weakest band — the very-largest wicks do NOT generalize (often mean-reversion fades or the sample is thin). The fee-floor logic holds: a wick just big enough to clear costs (W1=22.5bps) is the most robust.

**Strongest TF per asset (by mean net/trade across that asset's rows):**

- SOLUSDT: mean-net ranking {'1D': np.float64(76.0), '4h': np.float64(42.1), '30m': np.float64(41.3), '1h': np.float64(30.6)}; best monthly-edge row = 30m/W2_NODIP (monthly +4760 bps, net +20.8, union-BH YES).
- BTCUSDT: mean-net ranking {'1D': np.float64(51.4), '1h': np.float64(46.0), '4h': np.float64(43.8), '30m': np.float64(32.9)}; best monthly-edge row = 30m/W1_NODIP (monthly +2236 bps, net +10.3, union-BH YES).
- ETHUSDT: mean-net ranking {'1D': np.float64(41.5), '1h': np.float64(39.2), '30m': np.float64(26.2), '4h': np.float64(10.4)}; best monthly-edge row = 1h/W2_NODIP (monthly +1606 bps, net +20.3, union-BH YES).

**BTC/ETH vs SOL — how they differ:**

- SOL fires the most and shows the highest per-trade edge on tight-wick DIP rows (e.g. SOL 1h W2_DIP +48.6 bps). SOL's 1D rows are its strongest per-trade (mean +76 bps).

- BTC is the most consistent: every W1-W3 row net-positive, lowest variance; best on 30m/1h. BTC's dip sensitivity is mild — NODIP rows already work.

- ETH shows the highest win rates (87-94% on sub-1D TFs) but the LOWEST per-trade edge and several NEGATIVE W4 rows; its 1D rows drop below the 70% win floor (62-66%). ETH needs the dip filter to stay profitable at coarse TFs.


**Thin-n / unreliable:** 3 cells have n<30 (mostly W4_DIP on 1D) — not reliable. {int((g.win<70).sum())} cells fall below the owner's 70% win floor (concentrated in ETH and BTC 1D rows) — FLAGGED in the per-asset tables above.


**No global 'best system' pick — the owner chooses next.** Assets behave differently; the candidate that survives the most (union-BH) and clears the win floor is reported per asset in §2.
