# DECISIONS LOG — Who Decided What, and Why
Every material decision in this project, attributed: **[USER]** = your explicit instruction · **[AGENT]** = my judgment call (challengeable) · status = whether it stands or awaits your ruling.

---

## User instructions (verbatim intent, chronologically)
1. **[USER]** Study "bullish/bearish candle with upper wick" purely statistically, no traditional TA theories; goal is a tradeable method, not theoretical proof.
2. **[USER]** Assets: crypto (I proposed BTC; ETH added later as robustness; SOL added after your asset-personality demand).
3. **[USER]** Timeframes: daily → 15m (daily-4h-1h-30m-15m).
4. **[USER]** History: since 2022 for daily/4h/1h; since 2024 for 30m/15m.
5. **[USER]** Event definition: any candle with upper wick > 0.2% of its close.
6. **[USER]** Outcome: LONG ONLY, enter at next candle's open, target ≥95% of the wick (your C=1000/H=1100 → sell 1095 example), trade resolves within e+1 and e+2. This corrected my initial misreading (I had framed it as a short/limit-fill problem).
7. **[USER]** Stop-loss: deferred to a separate later task. NOT part of any result so far.
8. **[USER]** Challenged the money-judgment framing → documented which parts are measurement vs assumption; cost stack remains my declared default until you supply real tiers.
9. **[USER]** Demanded full conditional statistics per asset per timeframe ("each asset has its own personality") → conditional atlas built; hypothesis CONFIRMED in data (different optima per asset).
10. **[USER]** Demanded complete documentation ("document everything").
11. **[USER]** Stopped me from launching the SOL core-run/backtest extension: documentation only. Honored — SOL's ΔP/control/fee-ledger numbers are therefore ABSENT from FINDINGS.md and marked as gaps.

## Agent judgment calls (open to override)
| # | Decision | Rationale | Status |
|---|---|---|---|
| J1 | Pre-registration file frozen before outcomes | Blocks hindsight redefinition of success | Stands |
| J2 | Matched-target control baseline as THE comparator | Raw hit rates are meaningless without reachability baseline | Stands |
| J3 | Day-cluster bootstrap, B=1000, seed 42 | Overlapping windows correlate within days; determinism for reproducibility | Stands |
| J4 | Wick bucket edges / trend windows / RVOL cutoffs fixed before conditioning results | Prevents edge-shopping; arbitrary-but-frozen beats tuned-but-silent | Stands |
| J5 | Cost stack defaults: spot taker 20bp RT, fut taker 10bp, fut mm/taker 7bp, slippage 4bp | You had not supplied tiers | **Awaiting your real numbers** |
| J6 | Returns summed not compounded, unit notional | Isolates signal from sizing | Stands |
| J7 | 2026-YTD treated as holdout | Chronological honesty | Stands |
| J8 | No-SL exit at Close(e+2) | Your instruction #7 implies exits still needed for accounting | Stands until SL task |
| J9 | Spot data as proxy venue | Deepest free history | Declared limitation |
| J10 | SOL added to atlas immediately but core-run halted on your stop | Respect instruction over completeness | Awaiting go/no-go |

## Open questions parked for you
1. Real fee tier / venue (changes every NET number linearly; changes nothing gross).
2. Proceed to SL task? (Winner-dip distributions now exist to design it against: BTC 1h median −26bp/p75 −55bp; SOL 1h −47/−94; SOL daily −251/−473.)
3. Authorize Phase-3 validation battery on F15 candidates (pre-registered, walk-forward)?
4. Authorize completing SOL through the core pipeline?
5. Any additional assets you consider personality-distinct?

## Known defects carried forward (none silently)
- `hit_rate_given_fill` display bug in dip ladder (bounds unaffected) — fix scheduled with Phase 3.
- SOL core/fee artifacts missing (see above).
- Conditional-atlas optima carry selection bias until validated (stated in every document that quotes them).
