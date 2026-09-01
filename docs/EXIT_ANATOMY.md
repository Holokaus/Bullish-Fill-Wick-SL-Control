# EXIT ANATOMY — Phase A (Directive 4)

Pure measurement, zero parameters, zero P&L. Units: **wick units** (1.0 = signal candle's own wick gap); times in **wall-clock hours** from entry. Resolution: intrabar path unobservable — Phase A reports the *optimistic* (TP-first) resolution; same-bar SL/TP ambiguity is flagged in SL_STUDY.

## Trade-entry-date proof (owner verification order)

All four entry rows' trades fall inside TRAIN (entry < 2025-01-01). Reserved window 2025-07-01→2026-06-30 untouched.

- **SOL-30m W2**: n=6420, max entry = 2024-12-31 10:00:00+00:00 (min 2022-09-01 02:00:00+00:00)
- **BTC-30m W1**: n=6101, max entry = 2024-12-31 19:30:00+00:00 (min 2022-09-01 02:00:00+00:00)
- **ETH-1h W2**: n=2215, max entry = 2024-12-31 15:00:00+00:00 (min 2022-09-28 01:00:00+00:00)
- **SOL-4h W3**: n=1470, max entry = 2024-12-30 04:00:00+00:00 (min 2022-09-28 12:00:00+00:00)

## 1. MAE / MFE split (the headline finding)

Winners routinely endure **massive adverse excursion** before the wick gap fills. Winners' MAE P95 = 6.8–11.6 wick units; losers' median MAE ≈ 7–17 wick units. So any static SL tight enough to catch losers will also stop out winners that recover.

| row | win% | winner MAE P95 | winner MAE P99 | loser MAE P50 | loser MAE P90 | winner MFE P50 | winner MFE P90 |
|---|---|---|---|---|---|---|---|
| SOL-30m W2 | 90.5 | 11.589 | 23.187 | 17.396 | 38.498 | 2.45 | 4.884 |
| BTC-30m W1 | 90.9 | 11.728 | 21.661 | 16.14 | 36.642 | 2.496 | 5.0 |
| ETH-1h W2 | 85.9 | 8.957 | 14.739 | 10.691 | 26.679 | 2.361 | 4.446 |
| SOL-4h W3 | 77.2 | 6.804 | 14.173 | 7.182 | 15.162 | 2.484 | 5.116 |

![MAE split](charts/anatomy_MAE_split.png)

## 2. Fill survival & hazard

Fill probability is high and the hazard curve has **no knee within the 96h horizon** (it keeps filling steadily to ~4 days). There is no natural early-exit collapse point — a short-K time stop is a pure truncation, not a falsification event.

![survival+hazard](charts/anatomy_survival_hazard.png)

## 3. State divergence (are winners knowable early?)

At every checkpoint, P(TP | best-tercile state) is materially higher than P(TP | worst-tercile state) — but even the worst-tercile bucket still fills >50% of the time on every row. Early exits are *partially* knowable but far from separable; a checkpoint exit would still discard many eventual winners.

![divergence](charts/anatomy_divergence.png)

## 4. Falsification stats (do wrong-way closes predict failure?)

| row | flag | n | P(TP|flag) | P(TP|no-flag) |
|---|---|---|---|---|
| SOL-30m W2 | close_above_wickhigh | 743 | 96.5 | 89.7 |
| SOL-30m W2 | close_below_wicklow | 3424 | 82.3 | 99.8 |
| SOL-30m W2 | close_below_entry_1wick | 3158 | 80.8 | 99.8 |
| BTC-30m W1 | close_above_wickhigh | 651 | 96.6 | 90.2 |
| BTC-30m W1 | close_below_wicklow | 3104 | 82.2 | 99.8 |
| BTC-30m W1 | close_below_entry_1wick | 2889 | 81.0 | 99.8 |
| ETH-1h W2 | close_above_wickhigh | 215 | 95.8 | 84.9 |
| ETH-1h W2 | close_below_wicklow | 1132 | 73.2 | 99.2 |
| ETH-1h W2 | close_below_entry_1wick | 1046 | 70.7 | 99.6 |
| SOL-4h W3 | close_above_wickhigh | 77 | 85.7 | 76.7 |
| SOL-4h W3 | close_below_wicklow | 712 | 54.5 | 98.5 |
| SOL-4h W3 | close_below_entry_1wick | 705 | 54.5 | 98.2 |

- **close_above_wickhigh (thesis-falsification P2):** P(TP|flag) is HIGHER than P(TP|no-flag) on every row — a close above the wick high is *bullish confirmation*, not falsification. Exiting there cuts winners. → **P2 DROPPED**.
- **close_below_wicklow (downside-falsification P3):** directionally correct (lower P(TP|flag)) but fails the strict inclusion rule P(TP|flag) < 0.5×P(TP|no-flag) (e.g. E1 82.3 vs 49.9). → **P3 DROPPED** (with directional evidence noted).

## 5. Worst-loser anatomy

Worst-decile losers reach their MAE depth early and most are **retracement victims** (price showed profit first, then died). They cluster across all of TRAIN calendar time (no single crash episode) — input for the later portfolio study. [raw per-trade MAE/MFE arrays available in the measurement step; summary percentiles above.]

## 6. Per-asset separability verdict

- SOL (E1,E4) and BTC (E2) winners' MAE P95 ≈ 11–12 wick units; ETH (E3) ≈ 9. Distributions are **similar in shape but differ in scale** (ETH smaller wicks, tighter MAE). Conclusion: parameters must be derived **per asset** via the same rule (done in SL_STUDY) — never borrow one asset's level for another.

## 7. Measurement integrity

- Bars: intrabar SL/TP ambiguity reported under both resolutions in SL_STUDY (P1/P5). Phase A uses optimistic (TP-first).
- No parameter appears above. Phase A is curves and percentiles only.
