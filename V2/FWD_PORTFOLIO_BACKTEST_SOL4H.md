# FORWARD PORTFOLIO BACKTEST — Dec 2024 → Apr 2025

## Mandate

- **Trigger:** the 'main concept' wick-fill entry (`RS.select`, W3_NODIP) on **SOL-4h only (E4)**. Color-agnostic. (Narrowed run per user request.)
- **Filter:** LOSERFAC top DISC pre-entry feature `event_red_and_range_expand` (drop a signal if its candle is RED **and** range ≥ 1.5×20-bar ATR). Pre-entry only.
- **Capital:** $1000 start; each trade stakes 25% of equity at open; up to 3 concurrent; force-close all at period end.

## Execution model (from the discovery engine — no new assumptions)

- Entry @ next bar open after the signal. TP = body_top(sig) + 1.5×wick_gap. Exit = TP hit OR K-bar timeout (no intra-trade SL; the LOSERFAC filter is the stop-loss control). Cost = 15.0 bps round-trip.
- Cost = 15.0 bps round-trip (matches `keepn_study.COST`).
- Realistic fills: TP crossed-in-bar exits at limit price; timeout exits at the K-bar close.

## Data integrity

- Signal thresholds use TRAIN-frozen atlas cuts; the SOL-4h W3_NODIP spec uses a FIXED bps threshold (90 bps), so selection is leak-free regardless.
- The RESERVED window (2025-07-01 → 2026-07-01) is excluded entirely per the repo's hard rule.
- Study window: 2024-12-01 00:00:00+00:00 → 2025-04-30 23:59:59+00:00 UTC.

## Result

FORWARD PORTFOLIO BACKTEST  Dec 2024 - Apr 2025 (5 months)
============================================================
TRIGGER : wick-fill W3_NODIP on SOL-4h ONLY (E4)  -- narrowed per user request
FILTER  : LOSERFAC event_red_and_range_expand = DROP if signal bar RED & range>=1.5xATR(20)
COST    : 15.0 bps round-trip
CAPITAL : $1000.00  stake = 25% equity at open  max_open = 3
TP      : body_top(sig) + 1.5*wick_gap ;  exit = TP hit OR K-bar timeout (no intra-trade SL; SL control = LOSERFAC filter)
WINDOW  : 2024-12-01 00:00:00+00:00 .. 2025-04-30 23:59:59+00:00 UTC  (RESERVED 2025-07-01+ excluded)
------------------------------------------------------------
candidate trades (after filter) : 248
trades taken (opened)           : 195
  of which skipped (max-open)   : 53
closed (TP/SL/timeout/force)    : 195
  wins                          : 155
  losses                        : 40
win rate (of closed)            : 79.5%
avg pnl/trade $                : 0.38
start capital                  : $1000.00
final capital                  : $1073.28
net return                     : 7.33%
------------------------------------------------------------
per-row (closed):
  E4: n=195 win=79% net$=73.28 avgBps=31.1
============================================================
NOTE: LOSERFAC filter is TRAIN-derived; this is the requested forward check,
NOT the locked E-VAL. Treat as indicative, not validated.

## Files

- `V2/outputs/fwd_portfolio_sol4h_trades.csv` — every trade (open/close times, prices, reason, pnl, stake, equity).
- `V2/outputs/fwd_portfolio_sol4h_summary.txt` — the block above.

## Caveats

- Concurrency cap (3) means some candidate trades are skipped when all slots are full; they are logged with `SKIPPED_MAXOPEN`.
- Force-close marks remaining positions at their computed exit price (approximation at period end).
- This is the user-requested forward check on a TRAIN-derived filter; it is NOT the locked E-VAL window. Do not treat as validated out-of-sample performance.
