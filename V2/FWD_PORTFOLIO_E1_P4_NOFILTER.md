# E1 P4_timeSL_P95 EXPERIMENT — nofilter

## Mandate

- **Trigger:** wick-fill entry (`RS.select`, W2_NODIP) on **SOL-30m only (E1)**, wick ≥ 45 bps. Color-agnostic.
- **Time stop:** `P4_timeSL_P95` = K = 42h (84 bars on 30m). Exit = TP hit OR K-bar timeout. No intra-trade wick SL.
- **Filter:** NONE — plain trigger only.
- **Capital:** $1000 start; 25% of equity per trade at open; max 3 concurrent; force-close at period end.

## Execution model

- Entry @ next bar open. TP = body_top(sig) + 1.5×wick_gap. Exit = TP hit OR K=84-bar (42h) timeout. Cost 15.0 bps round-trip.
- This is an EXPERIMENT reusing the `P4_timeSL_P95` policy (the one E1 row SL_STUDY flagged VIABLE=True).

## Data integrity

- W2_NODIP uses a FIXED 45 bps threshold → leak-free selection.
- RESERVED window (2025-07-01 → 2026-07-01) excluded per repo hard rule.
- Window: 2024-12-01 00:00:00+00:00 → 2025-04-30 23:59:59+00:00 UTC.

## Result

E1 P4_timeSL_P95 EXPERIMENT  Dec 2024 - Apr 2025  [nofilter]
================================================================
TRIGGER : wick-fill W2_NODIP on SOL-30m ONLY (E1), wick>=45 bps
TIME STOP: P4_timeSL_P95 K=42h (84 bars) ; exit = TP hit OR K timeout ; no intra-trade SL
FILTER  : NONE (plain trigger)
COST    : 15.0 bps round-trip
CAPITAL : $1000.00  stake = 25% equity at open  max_open = 3
WINDOW  : 2024-12-01 00:00:00+00:00 .. 2025-04-30 23:59:59+00:00 UTC  (RESERVED 2025-07-01+ excluded)
----------------------------------------------------------------
candidate trades (after filter) : 175
trades taken (opened)           : 93
  of which skipped (max-open)   : 82
closed (TP/timeout/force)       : 93
  wins                          : 72
  losses                        : 21
win rate (of closed)            : 77.4%
avg pnl/trade $                : -0.66
start capital                  : $1000.00
final capital                  : $938.70
net return                     : -6.13%
================================================================

## Files

- `V2/outputs/fwd_portfolio_e1_p4_nofilter_trades.csv` — every trade.
- `V2/outputs/fwd_portfolio_e1_p4_nofilter_summary.txt` — summary above.

## Caveats

- Concurrency cap (3) may skip candidates (logged SKIPPED_MAXOPEN).
- Forward check on TRAIN-derived context; not the locked E-VAL. Indicative only.
