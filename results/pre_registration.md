# Pre-Registration — Upper-Wick Continuation Study (locked BEFORE results computed)

Date locked: 2026-08-24 (before any outcome statistic was computed)

## Hypothesis under test (user's theory, stated neutrally)
After any candle `e` whose upper wick exceeds 0.2% of its close,
buying at the open of `e+1` reaches `T = BodyTop_e + 0.95 * WickUp_e`
within candles `e+1`..`e+2` more often than chance would imply.

## Definitions (frozen)
- WickUp_e = High_e − max(Open_e, Close_e); Event iff WickUp_e > 0.002 × Close_e.
- Entry = Open(e+1). Target T = BodyTop_e + 0.95 × WickUp_e.
- Win = High(e+1) ≥ T or High(e+2) ≥ T. Trades require contiguous candles (exact ts spacing).
- Gap-trivial trades (Entry ≥ T): counted separately; excluded from the information test,
  included in mechanical accounting.
- Stop-loss: EXCLUDED from this phase (user decision; separate later task).

## Primary metric
ΔP = P(win | event) − P(win | matched control), per symbol × timeframe.
Controls: non-event candles, pseudo-target placed at the SAME required return
(T−Entry)/Entry (decile-matched), same 2-candle reach logic.

## Success criteria (fixed NOW)
1. STATISTICAL EDGE: ΔP > 0 with 95% CI excluding 0 (block-bootstrap, block≈1 day),
   replicated in ≥4 of 5 timeframes on BTC, direction-consistent on ETH.
2. STATIONARITY: sign(ΔP) agrees between 2022–2023 and 2024–2026 halves (per TF where data allows).
3. TRADEABILITY: after round-trip taker fees (0.10% × 2) and slippage allowance (0.02%),
   net expectancy > 0 per trade for at least one timeframe, AND walk-forward equity
   (train first 70% of each year, test remaining 30%, rolled) stays above water OOS.
4. MULTIPLE COMPARISONS: Benjamini–Hochberg FDR q=0.05 across the 5 TF × 2 bucket-color
   families tested; only surviving cells may be declared discoveries.

## Falseness conditions
If ΔP ≤ 0 or CI straddles 0 across all TFs → hypothesis DEAD as stated; report plainly.
If gross edge exists but fails criterion 3 → concept is REAL but NOT tradeable as specified;
report the gap in exact basis points and what parameter space could close it (no silent tuning).

## Outputs promised regardless of result
Per-TF win rates with Wilson CIs, ΔP table, bucket curve (win rate vs wick size),
candle-of-fill split, year-by-year stability, control-matched difference, net expectancy ledger.
