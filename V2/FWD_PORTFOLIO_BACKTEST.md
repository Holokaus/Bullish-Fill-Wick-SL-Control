# FORWARD PORTFOLIO BACKTEST — Dec 2024 → Apr 2025

## Mandate

- **Trigger:** the 'main concept' wick-fill entry (`RS.select`, W2/W1/W2/W3 NODIP on E1–E4).
- **Filter:** LOSERFAC top DISC pre-entry feature `event_red_and_range_expand` (drop a signal if its candle is RED **and** range ≥ 1.5×20-bar ATR). Pre-entry only.
- **Capital:** $1000 start; each trade stakes 25% of equity at open; up to 3 concurrent; force-close all at period end.

## Execution model (from the discovery engine — no new assumptions)

- Entry @ next bar open after the signal. TP = body_top(sig) + 1.5×wick_gap. Exit = TP hit OR K-bar timeout (no intra-trade SL; the LOSERFAC filter is the stop-loss control). Cost = 15.0 bps round-trip.
- Cost = 15.0 bps round-trip (matches `keepn_study.COST`).
- Realistic fills: TP crossed-in-bar exits at limit price; timeout exits at the K-bar close.

## Data integrity

- Signal thresholds use TRAIN-frozen atlas cuts; all four specs are FIXED bps (no decile) → no future leak in selection.
- The RESERVED window (2025-07-01 → 2026-07-01) is excluded entirely per the repo's hard rule.
- Study window: 2024-12-01 00:00:00+00:00 → 2025-04-30 23:59:59+00:00 UTC.

## Result

FORWARD PORTFOLIO BACKTEST  Dec 2024 - Apr 2025 (5 months)
============================================================
TRIGGER : wick-fill (W2/W1/W2/W3 NODIP) on E1-E4 = SOL-30m,BTC-30m,ETH-1h,SOL-4h
FILTER  : LOSERFAC event_red_and_range_expand = DROP if signal bar RED & range>=1.5xATR(20)
COST    : 15.0 bps round-trip
CAPITAL : $1000.00  stake = 25% equity at open  max_open = 3
TP      : body_top(sig) + 1.5*wick_gap ;  exit = TP hit OR K-bar timeout (no intra-trade SL; SL control = LOSERFAC filter)
WINDOW  : 2024-12-01 00:00:00+00:00 .. 2025-04-30 23:59:59+00:00 UTC  (RESERVED 2025-07-01+ excluded)
------------------------------------------------------------
candidate trades (after filter) : 1304
trades taken (opened)           : 383
  of which skipped (max-open)   : 921
closed (TP/SL/timeout/force)    : 383
  wins                          : 324
  losses                        : 59
win rate (of closed)            : 84.6%
avg pnl/trade $                : -0.44
start capital                  : $1000.00
final capital                  : $832.53
net return                     : -16.75%
------------------------------------------------------------
per-row (closed):
  E1: n=24 win=79% net$=-47.67 avgBps=-125.6
  E2: n=53 win=92% net$=12.66 avgBps=16.3
  E3: n=226 win=85% net$=-182.77 avgBps=-44.7
  E4: n=80 win=81% net$=50.30 avgBps=22.3
============================================================
NOTE: LOSERFAC filter is TRAIN-derived; this is the requested forward check,
NOT the locked E-VAL. Treat as indicative, not validated.

## Files

- `V2/outputs/fwd_portfolio_trades.csv` — every trade (open/close times, prices, reason, pnl, stake, equity).
- `V2/outputs/fwd_portfolio_summary.txt` — the block above.

## Caveats

- Concurrency cap (3) means some candidate trades are skipped when all slots are full; they are logged with `SKIPPED_MAXOPEN`.
- Force-close marks remaining positions at their computed exit price (approximation at period end).
- This is the user-requested forward check on a TRAIN-derived filter; it is NOT the locked E-VAL window. Do not treat as validated out-of-sample performance.
