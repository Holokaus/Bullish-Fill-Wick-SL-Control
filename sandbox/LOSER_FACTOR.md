# LOSER FACTOR STUDY — TRAIN MEASUREMENT (LOSERFAC)

> Among trades that already lost (structural losers = TP never hit), is there a pre-entry feature common in losers AND uncommon in winners? Measurement only. Owner evaluates.

## 1. Identity gate

| row | n | net @15bps | win% | max entry (UTC) | GATE |
|-----|---|-----------|-------|-----------------|------|
| E1 | 6420 (exp 6420) | 20.76 (exp 20.76) | 90.6 (exp 90.6) | 2024-12-31 10:00:00 | PASS |
| E2 | 6101 (exp 6101) | 10.26 (exp 10.26) | 91.1 (exp 91.1) | 2024-12-31 19:30:00 | PASS |
| E3 | 2215 (exp 2215) | 20.42 (exp 20.42) | 86.8 (exp 86.8) | 2024-12-31 15:00:00 | PASS |
| E4 | 1470 (exp 1470) | 48.72 (exp 48.72) | 79.0 (exp 79.0) | 2024-12-30 04:00:00 | PASS |

**Identity gate: ALL PASS.**

## 2. Loser counts

| row | n0 | n_L_struct | n_W_struct | struct WR% | n_L_econ | n_W_econ |
|-----|----|-----------|-----------|----------|---------|---------|
| E1 | 6420 | 612 | 5808 | 90.5 | 602 | 5818 |
| E2 | 6101 | 557 | 5544 | 90.9 | 543 | 5558 |
| E3 | 2215 | 312 | 1903 | 85.9 | 293 | 1922 |
| E4 | 1470 | 335 | 1135 | 77.2 | 309 | 1161 |

## 3. How to read a row

- `p_feat_L ≈ p_feat_W` (lift ≈ 1) means the factor is **common to both** — dropping it does not concentrate on losers.
- `lift ≫ 1` and `winner_cut_pct ≪ loser_cut_pct` means the factor is **loser-concentrated**.
- `CUT50` is the owner's "~50% of losers, not the same share of winners" bar. Empty is allowed.

## 4. Color table

| row | feature | n_def | p_feat_L | p_feat_W | lift | delta_pp | p2 | bh | loser_cut% | winner_cut% | collateral | wr_keep | net_keep | CUT50 | DISC |
|-----|---------|-------|----------|----------|------|----------|----|----|-----------|------------|-----------|---------|---------|------|------|
| E1 | event_red | 6420 | 0.5016 | 0.4287 | 1.17 | 7.3 | 0.00054 | True | 50.2 | 42.9 | 0.855 | 91.6 | 16.51 | False | False |
| E1 | event_green | 6420 | 0.4951 | 0.5623 | 0.88 | -6.7 | 0.001454 | True | 49.5 | 56.2 | 1.136 | 89.2 | 26.49 | False | False |
| E1 | prev_red | 6420 | 0.4412 | 0.4604 | 0.958 | -1.9 | 0.364008 | False | 44.1 | 46.0 | 1.044 | 90.2 | 21.27 | False | False |
| E1 | prev_green | 6420 | 0.5556 | 0.5355 | 1.038 | 2.0 | 0.343151 | False | 55.6 | 53.5 | 0.964 | 90.8 | 20.27 | False | False |
| E1 | rr | 6420 | 0.2288 | 0.1982 | 1.154 | 3.1 | 0.07259 | False | 22.9 | 19.8 | 0.866 | 90.8 | 20.53 | False | False |
| E1 | rg | 6420 | 0.2712 | 0.2295 | 1.182 | 4.2 | 0.020284 | True | 27.1 | 23.0 | 0.846 | 90.9 | 17.73 | False | False |
| E1 | gr | 6420 | 0.2108 | 0.2583 | 0.816 | -4.7 | 0.010246 | True | 21.1 | 25.8 | 1.225 | 89.9 | 21.51 | False | False |
| E1 | gg | 6420 | 0.2827 | 0.301 | 0.939 | -1.8 | 0.347452 | False | 28.3 | 30.1 | 1.065 | 90.2 | 23.82 | False | False |
| E2 | event_red | 6101 | 0.5027 | 0.421 | 1.194 | 8.2 | 0.000204 | True | 50.3 | 42.1 | 0.837 | 92.1 | 4.7 | False | False |
| E2 | event_green | 6101 | 0.4937 | 0.5781 | 0.854 | -8.4 | 0.000125 | True | 49.4 | 57.8 | 1.171 | 89.2 | 17.56 | False | False |
| E2 | prev_red | 6101 | 0.3698 | 0.4369 | 0.847 | -6.7 | 0.002324 | True | 37.0 | 43.7 | 1.181 | 89.9 | 7.13 | False | False |
| E2 | prev_green | 6101 | 0.6284 | 0.5626 | 1.117 | 6.6 | 0.002809 | True | 62.8 | 56.3 | 0.895 | 92.1 | 14.42 | False | False |
| E2 | rr | 6101 | 0.2011 | 0.1833 | 1.097 | 1.8 | 0.301842 | False | 20.1 | 18.3 | 0.911 | 91.1 | 7.23 | False | False |
| E2 | rg | 6101 | 0.2998 | 0.2372 | 1.264 | 6.3 | 0.001018 | True | 30.0 | 23.7 | 0.791 | 91.6 | 9.35 | False | False |
| E2 | gr | 6101 | 0.167 | 0.2531 | 0.66 | -8.6 | 7e-06 | True | 16.7 | 25.3 | 1.516 | 89.9 | 11.14 | False | False |
| E2 | gg | 6101 | 0.3268 | 0.325 | 1.005 | 0.2 | 0.93438 | False | 32.7 | 32.5 | 0.995 | 90.9 | 13.93 | False | False |
| E3 | event_red | 2215 | 0.5256 | 0.4235 | 1.241 | 10.2 | 0.000754 | True | 52.6 | 42.4 | 0.806 | 88.1 | 15.86 | False | False |
| E3 | event_green | 2215 | 0.4744 | 0.5759 | 0.824 | -10.2 | 0.000804 | True | 47.4 | 57.6 | 1.214 | 83.1 | 26.39 | False | False |
| E3 | prev_red | 2215 | 0.4295 | 0.4162 | 1.032 | 1.3 | 0.658818 | False | 42.9 | 41.6 | 0.969 | 86.2 | 26.21 | False | False |
| E3 | prev_green | 2215 | 0.5673 | 0.5838 | 0.972 | -1.7 | 0.583794 | False | 56.7 | 58.4 | 1.029 | 85.4 | 11.91 | False | False |
| E3 | rr | 2215 | 0.2372 | 0.1645 | 1.442 | 7.3 | 0.001721 | True | 23.7 | 16.4 | 0.693 | 87.0 | 22.88 | False | False |
| E3 | rg | 2215 | 0.2853 | 0.2591 | 1.101 | 2.6 | 0.329906 | False | 28.5 | 25.9 | 0.908 | 86.3 | 13.93 | False | False |
| E3 | gr | 2215 | 0.1923 | 0.2517 | 0.764 | -5.9 | 0.023426 | True | 19.2 | 25.2 | 1.309 | 85.0 | 22.2 | False | False |
| E3 | gg | 2215 | 0.2821 | 0.3242 | 0.87 | -4.2 | 0.138256 | False | 28.2 | 32.4 | 1.15 | 85.2 | 22.29 | False | False |
| E4 | event_red | 1470 | 0.5642 | 0.3982 | 1.417 | 16.6 | 0.0 | True | 56.4 | 39.8 | 0.706 | 82.4 | 70.55 | False | False |
| E4 | event_green | 1470 | 0.4358 | 0.5982 | 0.729 | -16.2 | 0.0 | True | 43.6 | 59.8 | 1.373 | 70.7 | 21.71 | False | False |
| E4 | prev_red | 1470 | 0.4448 | 0.4467 | 0.996 | -0.2 | 0.950471 | False | 44.5 | 44.7 | 1.004 | 77.1 | 59.39 | False | False |
| E4 | prev_green | 1470 | 0.5552 | 0.5515 | 1.007 | 0.4 | 0.905204 | False | 55.5 | 55.2 | 0.993 | 77.4 | 37.82 | False | False |
| E4 | rr | 1470 | 0.2657 | 0.1718 | 1.546 | 9.4 | 0.000131 | True | 26.6 | 17.2 | 0.647 | 79.3 | 61.94 | False | True |
| E4 | rg | 1470 | 0.2985 | 0.2256 | 1.323 | 7.3 | 0.006164 | True | 29.9 | 22.6 | 0.756 | 78.9 | 51.11 | False | False |
| E4 | gr | 1470 | 0.1791 | 0.2731 | 0.656 | -9.4 | 0.000493 | True | 17.9 | 27.3 | 1.525 | 75.0 | 42.69 | False | False |
| E4 | gg | 1470 | 0.2567 | 0.3242 | 0.792 | -6.8 | 0.018768 | True | 25.7 | 32.4 | 1.263 | 75.5 | 39.34 | False | False |

## 5. Volume table

| row | feature | n_def | p_feat_L | p_feat_W | lift | delta_pp | p2 | bh | loser_cut% | winner_cut% | collateral | wr_keep | net_keep | CUT50 | DISC |
|-----|---------|-------|----------|----------|------|----------|----|----|-----------|------------|-----------|---------|---------|------|------|
| E1 | rvol_ge_1_3 | 6418 | 0.6699 | 0.5501 | 1.218 | 12.0 | 0.0 | True | 67.0 | 55.0 | 0.821 | 92.8 | 19.5 | False | False |
| E1 | rvol_ge_2_0 | 6418 | 0.4412 | 0.3233 | 1.365 | 11.8 | 0.0 | True | 44.1 | 32.3 | 0.733 | 92.0 | 22.56 | False | False |
| E1 | rvol_top_q | 6418 | 0.3056 | 0.1889 | 1.617 | 11.7 | 0.0 | True | 30.6 | 18.9 | 0.618 | 91.7 | 24.5 | False | True |
| E1 | prev_rvol_ge_2_0 | 6418 | 0.3497 | 0.2632 | 1.329 | 8.6 | 5e-06 | True | 35.0 | 26.3 | 0.752 | 91.5 | 26.17 | False | False |
| E1 | event_vol_gt_prev | 6420 | 0.6258 | 0.5647 | 1.108 | 6.1 | 0.003691 | True | 62.6 | 56.5 | 0.902 | 91.7 | 20.29 | False | False |
| E2 | rvol_ge_1_3 | 6099 | 0.7558 | 0.6321 | 1.196 | 12.4 | 0.0 | True | 75.6 | 63.2 | 0.836 | 93.8 | 12.74 | False | False |
| E2 | rvol_ge_2_0 | 6099 | 0.5978 | 0.446 | 1.34 | 15.2 | 0.0 | True | 59.8 | 44.6 | 0.746 | 93.2 | 13.15 | False | False |
| E2 | rvol_top_q | 6099 | 0.3268 | 0.1873 | 1.745 | 13.9 | 0.0 | True | 32.7 | 18.7 | 0.573 | 92.3 | 12.45 | False | True |
| E2 | prev_rvol_ge_2_0 | 6099 | 0.4219 | 0.3659 | 1.153 | 5.6 | 0.009146 | True | 42.2 | 36.6 | 0.867 | 91.6 | 9.27 | False | False |
| E2 | event_vol_gt_prev | 6101 | 0.6338 | 0.5676 | 1.116 | 6.6 | 0.002634 | True | 63.4 | 56.8 | 0.896 | 92.2 | 11.59 | False | False |
| E3 | rvol_ge_1_3 | 2207 | 0.7821 | 0.686 | 1.14 | 9.6 | 0.000606 | True | 78.2 | 68.3 | 0.874 | 89.9 | 20.72 | False | False |
| E3 | rvol_ge_2_0 | 2207 | 0.5833 | 0.4412 | 1.322 | 14.2 | 3e-06 | True | 58.3 | 43.9 | 0.753 | 89.1 | 19.13 | False | False |
| E3 | rvol_top_q | 2207 | 0.3109 | 0.1821 | 1.708 | 12.9 | 0.0 | True | 31.1 | 18.1 | 0.583 | 87.9 | 18.04 | False | True |
| E3 | prev_rvol_ge_2_0 | 2207 | 0.3365 | 0.3303 | 1.019 | 0.6 | 0.829413 | False | 33.7 | 32.9 | 0.977 | 86.1 | 17.8 | False | False |
| E3 | event_vol_gt_prev | 2215 | 0.7436 | 0.6148 | 1.209 | 12.9 | 1.2e-05 | True | 74.4 | 61.5 | 0.827 | 90.2 | 36.45 | False | False |
| E4 | rvol_ge_1_3 | 1466 | 0.5269 | 0.4408 | 1.195 | 8.6 | 0.005517 | True | 52.5 | 44.0 | 0.837 | 80.0 | 42.5 | False | False |
| E4 | rvol_ge_2_0 | 1466 | 0.2784 | 0.1979 | 1.407 | 8.1 | 0.001674 | True | 27.8 | 19.7 | 0.711 | 79.0 | 45.12 | False | False |
| E4 | rvol_top_q | 1466 | 0.2695 | 0.1802 | 1.495 | 8.9 | 0.000344 | True | 26.9 | 18.0 | 0.669 | 79.2 | 48.5 | False | False |
| E4 | prev_rvol_ge_2_0 | 1466 | 0.1377 | 0.1767 | 0.78 | -3.9 | 0.094122 | False | 13.7 | 17.6 | 1.283 | 76.4 | 36.7 | False | False |
| E4 | event_vol_gt_prev | 1470 | 0.6627 | 0.5427 | 1.221 | 12.0 | 9.7e-05 | True | 66.3 | 54.3 | 0.819 | 82.1 | 73.98 | False | False |

## 6. Combo table

| row | feature | n_def | p_feat_L | p_feat_W | lift | delta_pp | p2 | bh | loser_cut% | winner_cut% | collateral | wr_keep | net_keep | CUT50 | DISC |
|-----|---------|-------|----------|----------|------|----------|----|----|-----------|------------|-----------|---------|---------|------|------|
| E1 | rr_and_rvol_ge_2_0 | 6418 | 0.0752 | 0.0539 | 1.394 | 2.1 | 0.02954 | True | 7.5 | 5.4 | 0.717 | 90.7 | 20.09 | False | False |
| E1 | event_red_and_rvol_ge_2_0 | 6418 | 0.1961 | 0.1166 | 1.682 | 7.9 | 0.0 | True | 19.6 | 11.7 | 0.594 | 91.3 | 21.62 | False | True |
| E1 | event_red_and_rvol_ge_1_3 | 6418 | 0.3235 | 0.2163 | 1.496 | 10.7 | 0.0 | True | 32.4 | 21.6 | 0.668 | 91.7 | 18.57 | False | False |
| E1 | event_red_and_rvol_top_q | 6418 | 0.1307 | 0.0636 | 2.057 | 6.7 | 0.0 | True | 13.1 | 6.4 | 0.486 | 91.1 | 23.2 | False | False |
| E2 | rr_and_rvol_ge_2_0 | 6099 | 0.1095 | 0.0751 | 1.459 | 3.4 | 0.003893 | True | 11.0 | 7.5 | 0.685 | 91.2 | 9.06 | False | False |
| E2 | event_red_and_rvol_ge_2_0 | 6099 | 0.2855 | 0.1694 | 1.685 | 11.6 | 0.0 | True | 28.5 | 16.9 | 0.593 | 92.0 | 9.14 | False | True |
| E2 | event_red_and_rvol_ge_1_3 | 6099 | 0.3609 | 0.2519 | 1.433 | 10.9 | 0.0 | True | 36.1 | 25.2 | 0.698 | 92.1 | 7.53 | False | False |
| E2 | event_red_and_rvol_top_q | 6099 | 0.1508 | 0.0653 | 2.309 | 8.5 | 0.0 | True | 15.1 | 6.5 | 0.433 | 91.6 | 10.27 | False | True |
| E3 | rr_and_rvol_ge_2_0 | 2207 | 0.1218 | 0.0675 | 1.803 | 5.4 | 0.000761 | True | 12.2 | 6.7 | 0.552 | 86.6 | 19.81 | False | False |
| E3 | event_red_and_rvol_ge_2_0 | 2207 | 0.2788 | 0.1673 | 1.667 | 11.2 | 2e-06 | True | 27.9 | 16.7 | 0.597 | 87.6 | 15.95 | False | True |
| E3 | event_red_and_rvol_ge_1_3 | 2207 | 0.4038 | 0.2739 | 1.475 | 13.0 | 3e-06 | True | 40.4 | 27.3 | 0.675 | 88.2 | 17.69 | False | False |
| E3 | event_red_and_rvol_top_q | 2207 | 0.1603 | 0.0623 | 2.574 | 9.8 | 0.0 | True | 16.0 | 6.2 | 0.387 | 87.2 | 19.78 | False | True |
| E4 | rr_and_rvol_ge_2_0 | 1466 | 0.0689 | 0.0336 | 2.051 | 3.5 | 0.004536 | True | 6.9 | 3.3 | 0.488 | 77.9 | 48.5 | False | False |
| E4 | event_red_and_rvol_ge_2_0 | 1466 | 0.1437 | 0.0707 | 2.034 | 7.3 | 3.2e-05 | True | 14.3 | 7.0 | 0.492 | 78.6 | 50.36 | False | False |
| E4 | event_red_and_rvol_ge_1_3 | 1466 | 0.2994 | 0.1625 | 1.842 | 13.7 | 0.0 | True | 29.9 | 16.2 | 0.543 | 80.2 | 57.91 | False | True |
| E4 | event_red_and_rvol_top_q | 1466 | 0.1377 | 0.0636 | 2.165 | 7.4 | 1.2e-05 | True | 13.7 | 6.3 | 0.462 | 78.6 | 51.34 | False | False |

## 7. rvol percentile snapshot

| row | group | P10 | P25 | P50 | P75 | P90 |
|-----|-------|-----|-----|-----|-----|-----|
| E1 | loser | 0.765 | 1.087 | 1.802 | 3.189 | 5.377 |
| E1 | winner | 0.625 | 0.893 | 1.421 | 2.383 | 3.964 |
| E2 | loser | 0.817 | 1.334 | 2.552 | 5.034 | 8.671 |
| E2 | winner | 0.608 | 0.967 | 1.767 | 3.388 | 6.007 |
| E3 | loser | 0.916 | 1.412 | 2.367 | 4.053 | 6.505 |
| E3 | winner | 0.778 | 1.132 | 1.798 | 2.97 | 4.57 |
| E4 | loser | 0.731 | 0.977 | 1.389 | 2.153 | 2.844 |
| E4 | winner | 0.634 | 0.852 | 1.191 | 1.812 | 2.662 |

## 8. CUT50 index

- NONE

## 9. DISC index

- E1 rvol_top_q (lift=1.617, loser_cut=30.6%, bh=True)
- E1 event_red_and_rvol_ge_2_0 (lift=1.682, loser_cut=19.6%, bh=True)
- E2 rvol_top_q (lift=1.745, loser_cut=32.7%, bh=True)
- E2 event_red_and_rvol_ge_2_0 (lift=1.685, loser_cut=28.5%, bh=True)
- E2 event_red_and_rvol_top_q (lift=2.309, loser_cut=15.1%, bh=True)
- E3 rvol_top_q (lift=1.708, loser_cut=31.1%, bh=True)
- E3 event_red_and_rvol_ge_2_0 (lift=1.667, loser_cut=27.9%, bh=True)
- E3 event_red_and_rvol_top_q (lift=2.574, loser_cut=16.0%, bh=True)
- E4 rr (lift=1.546, loser_cut=26.6%, bh=True)
- E4 event_red_and_rvol_ge_1_3 (lift=1.842, loser_cut=29.9%, bh=True)

## 10. Benjamini–Hochberg (within-study family, q=0.05)

- Family size (row × feature cells) = 68
- q = 0.05
- Rejected = 54
- Rejected cells:
  - E1 event_red p=0.000539907
  - E1 event_green p=0.00145353
  - E1 rg p=0.0202838
  - E1 gr p=0.0102462
  - E1 rvol_ge_1_3 p=1.33473e-08
  - E1 rvol_ge_2_0 p=4.12497e-09
  - E1 rvol_top_q p=6.942e-12
  - E1 prev_rvol_ge_2_0 p=4.72315e-06
  - E1 event_vol_gt_prev p=0.00369114
  - E1 rr_and_rvol_ge_2_0 p=0.0295399
  - E1 event_red_and_rvol_ge_2_0 p=1.42524e-08
  - E1 event_red_and_rvol_ge_1_3 p=1.68246e-09
  - E1 event_red_and_rvol_top_q p=5.80983e-10
  - E2 event_red p=0.000203823
  - E2 event_green p=0.000125464
  - E2 prev_red p=0.00232364
  - E2 prev_green p=0.00280924
  - E2 rg p=0.00101795
  - E2 gr p=6.71227e-06
  - E2 rvol_ge_1_3 p=6.16096e-09
  - E2 rvol_ge_2_0 p=7.27574e-12
  - E2 rvol_top_q p=4.44089e-15
  - E2 prev_rvol_ge_2_0 p=0.00914607
  - E2 event_vol_gt_prev p=0.00263363
  - E2 rr_and_rvol_ge_2_0 p=0.00389308
  - E2 event_red_and_rvol_ge_2_0 p=1.09253e-11
  - E2 event_red_and_rvol_ge_1_3 p=2.45971e-08
  - E2 event_red_and_rvol_top_q p=1.49658e-13
  - E3 event_red p=0.000753681
  - E3 event_green p=0.000803614
  - E3 rr p=0.00172062
  - E3 gr p=0.0234259
  - E3 rvol_ge_1_3 p=0.000606396
  - E3 rvol_ge_2_0 p=3.04104e-06
  - E3 rvol_top_q p=1.36987e-07
  - E3 event_vol_gt_prev p=1.2197e-05
  - E3 rr_and_rvol_ge_2_0 p=0.000760896
  - E3 event_red_and_rvol_ge_2_0 p=2.33637e-06
  - E3 event_red_and_rvol_ge_1_3 p=2.90641e-06
  - E3 event_red_and_rvol_top_q p=1.46937e-09
  - E4 event_red p=7.37475e-08
  - E4 event_green p=1.41068e-07
  - E4 rr p=0.000131466
  - E4 rg p=0.00616439
  - E4 gr p=0.000493402
  - E4 gg p=0.0187675
  - E4 rvol_ge_1_3 p=0.00551672
  - E4 rvol_ge_2_0 p=0.00167365
  - E4 rvol_top_q p=0.000344173
  - E4 event_vol_gt_prev p=9.74369e-05
  - E4 rr_and_rvol_ge_2_0 p=0.0045359
  - E4 event_red_and_rvol_ge_2_0 p=3.24917e-05
  - E4 event_red_and_rvol_ge_1_3 p=2.68042e-08
  - E4 event_red_and_rvol_top_q p=1.21227e-05
- Union ledger (union_ledger.json) was **not** updated by this pass.

## 11. Stop

AGENT STOPS. No freeze. No E-VAL. Owner evaluates.
