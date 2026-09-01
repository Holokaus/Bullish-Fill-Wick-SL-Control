# METHODOLOGY — Upper-Wick Continuation Study
**Version:** 1.0 · **Date:** 2026-08-24 · **Status:** Complete through Phase 2 (conditional atlas). Phase 3 (walk-forward validation of selected rulesets) not yet run.

---

## PART I — THE THINK CHAIN (why every step exists)

### Step 0 — Framing decision: treat the candle as a data structure, not a pattern.
The user's request: study the "bullish/bearish candle with upper wick" concept with *purely statistical* methods, ignoring all traditional TA doctrine, and convert any discovery into a tradeable method. The correct epistemic stance: a candle is just four numbers (O/H/L/C). "Upper wick" = `High − max(Open, Close)`. No meaning is assumed; meanings are *tested*. Everything downstream follows from refusing to assume.

### Step 1 — Operationalize before computing anything.
The user's verbal spec was converted into exact formulas and **frozen in `results/pre_registration.md` BEFORE any outcome statistic was computed**. This prevents the deadliest research sin: defining success after seeing the data. The frozen definitions are in Part II below. Two things were deliberately deferred by user instruction: stop-loss design ("next task") and fee-tier confirmation (my defaults were declared openly).

### Step 2 — Data first, skeptically.
Binance official monthly archives (data.binance.vision) + REST tail for the current month; spot market only (user chose crypto for data quality; BTC+ETH initially per my proposal, SOL added later when the user demanded per-asset treatment). During ingestion a real vendor format change was caught: archives switched timestamp units ms→µs (and added header rows) starting 2025-01. First build produced exactly 1096 daily rows (=2022–2024 only) which exposed the bug; fixed per-file, both timestamp columns normalized, re-verified to zero gaps. Lesson recorded: always sanity-check row counts against calendar arithmetic.

### Step 3 — Baselines or it didn't happen.
A raw win rate proves nothing: ANY 2-candle window has some probability of rising X%. The core question was framed as **ΔP = P(win | event) − P(win | matched control)** where controls are non-event candles required to rise the SAME distance (same r_req distribution via decile grid). Without this, a high hit rate on tiny targets would masquerade as edge. Additionally: day-clustered bootstrap CIs (clusters = UTC days, because intraday candles overlap in regime), non-overlapping-trade subsets (consecutive events share candles), Wilson intervals, per-year stationarity splits, and a true holdout year (2026 YTD entered no tuning decision).

### Step 4 — Attack your own result (the falsification pass).
Finding #1 (elevated reach after wick events) was immediately stress-tested with a decomposition: bin ALL candles into RANGE deciles; within each decile compare upper-wick events vs mirror-wick candles vs body-dominant candles vs rest. Rationale: volatility clusters, so wide candles follow wide candles regardless of shape; if the wick effect were pure volatility persistence it would die inside range bins. It did not die — a uniform ~3–7pp residual survived in every decile, both assets, all intraday TFs. This is what distinguishes "the wick matters" from "big candles matter."
A second self-catch: the FIRST control curve implementation had an inverted sign (`searchsorted side='right'` returns the complement). The bug was detected because two independent implementations of the same quantity disagreed — keep redundant computations precisely so they can catch each other. All reported numbers are post-fix.

### Step 5 — Money conversion is arithmetic, not opinion — but cost assumptions ARE choices.
The user's brief demanded conversion into a tradeable method. That requires a cost stack; the stack used (Binance base tiers: spot taker 20bp RT, futures taker 10bp, futures maker/taker 7bp, slippage allowance 4bp) was MY choice and is flagged as such throughout. The verdict layer is therefore conditional: "net at THESE costs." The user later challenged this framing; the response documented which parts are measurement (gross expectancy, win rates — facts) and which are assumptions (fee tiers).

### Step 6 — Condition, don't conclude.
After user criticism that aggregate verdicts were thin, the full conditional atlas was built (Phase 2): wick-size buckets, fill timing, path (MAE/MFE), preceding candle, trend context, volume, anatomy, hour-of-day, entry-optimization ladder — each computed separately for every asset × timeframe, because the user's hypothesis "each asset has its own personality" was itself treated as a testable claim (it held).
Meta-risk acknowledged: scanning ~15 cells × 9 dimensions means some optima are noise (winner's curse). The atlas is hypothesis GENERATION; selected candidates require pre-registered walk-forward validation (Phase 3, pending). Year-stability probes of the top five net-positive cells were run immediately as a cheap robustness screen: most persisted across most years; none were bulletproof; samples are small (n≈86–344).

### Step 7 — What would change our mind.
Pre-registered falseness conditions (in pre_registration.md): ΔP ≤ 0 or CI straddling 0 everywhere → concept dead as stated. Gross edge but fails costs → real-but-untradeable-as-specified. Both branches were actually used: intraday TFs took branch 2, daily TFs failed outright. Any future claim from the atlas must survive: (a) fresh out-of-sample period untouched during selection, (b) both ambiguity bounds in the dip-entry ladder, (c) per-asset re-estimation (no parameter borrowing).

---

## PART II — FROZEN DEFINITIONS

```
Event candle e        : wick_up > 0.002 × close_e, where wick_up = High_e − max(Open_e, Close_e)
                        (bullish AND bearish events both included, per user)
Entry                 : Open(e+1)  — long position, spot semantics
Target T              : BodyTop_e + 0.95 × WickUp_e, BodyTop = max(Open_e, Close_e)
Success               : High(e+1) ≥ T OR High(e+2) ≥ T   (limit-order touch semantics)
No-SL failure exit    : Close(e+2)  (market out after 2nd candle)
Contiguity rule       : e → e+1 → e+2 must be exactly adjacent candles (interval-exact);
                        violations excluded (only one benign 1h gap exists in all data)
Gap-trivial trades    : Entry ≥ T would be pre-filled — none occurred in any cell
Control baseline      : non-event candles, P(max(H(e+1),H(e+2))/Open(e+1) − 1 ≥ r_req)
                        averaged over the event r_req decile grid (matched-target control)
Net cost stack (declared assumption): spot taker 20bp RT; fut taker 10bp;
                        fut maker-in/taker-out 7bp; slippage allowance 4bp RT.
                        NET figures in reports = gross − 11bp (fut mm/taker + slip) unless stated.
```

## PART III — COMPLETE ASSUMPTION REGISTER

| # | Assumption | Why | Risk if wrong | Mitigation |
|---|---|---|---|---|
| A1 | Exchange kline H/L are valid extremes of each interval | Only OHLCV available free at this depth | Slightly overstates fills (snapshot misses intra-second spikes); affects events & controls equally | Directional conclusions rely on ΔP (differential), robust to symmetric noise |
| A2 | Fill at target requires only High ≥ T | Standard limit-order backtest convention | Real book depth/queue priority may reduce fills | Effect is conservative for the CONTROL too; live paper-trade gate recommended |
| A3 | Same-candle touch ambiguity in dip-entry ladder handled by dual bounds | Candle data cannot order intra-candle touches | True result lies inside [pessimistic, optimistic] envelope | Both bounds reported; never quote the favorable one alone |
| A4 | Fees/slippage defaults (see Part II) | User did not supply tiers | Verdicts shift linearly; ~±5–15bp swings conclusions near zero | Flagged everywhere as assumption; user can override with real tiers |
| A5 | Returns summed, not compounded; unit notional | Isolates signal quality from sizing | None for ranking; absolute $ results would differ | Stated on every ledger |
| A6 | Volume = base-asset kline volume; RVOL vs trailing 20-candle median | Standard, robust to asset scale | Different window changes bucket edges slightly | Buckets are wide (0.7/1.3/2.0) |
| A7 | Trend windows: tr12 = 12-candle return; pctB = 24-cannel range position | Round numbers chosen BEFORE looking at conditioning results | Other windows might flatter differently | Frozen in code; noted as arbitrary-but-fixed |
| A8 | Bucket edges for wick size ([0.2,0.3,...,2.5,∞)) chosen before outcomes seen | Prevents edge-shopping | Coarse edges may blur finer optima | Finer scan possible later under Phase-3 discipline |
| A9 | Day-cluster bootstrap (B=1000, seed=42) captures serial dependence | Overlapping windows correlate trades within days | Underestimates dependence across adjacent days | Non-overlapping subset checked separately; conclusions unchanged |
| A10 | 2026-YTD = holdout; earlier = exploration | Chronological split | 2026 regime may differ structurally (n smaller) | Reported separately everywhere |
| A11 | Each asset×timeframe estimated independently (no pooling) | User's asset-personality hypothesis confirmed in data | Small cells noisy | Year-stability screens; Phase-3 validation pending |
| A12 | Spot data proxies the tradable venue | Futures have distinct microstructure (funding, liq cascades) | Futures-only effects invisible here | Declared scope limitation |

## PART IV — ERRORS MADE AND CAUGHT (audit trail)

1. **Timestamp unit bug (vendor-side, caught by row-count audit):** µs/ms switch corrupted first build → silent loss of all 2025+ rows. Fixed per-file; both ts columns.
2. **Inverted control curve sign (my bug, caught by redundancy):** two implementations of P(control reaches r) disagreed; `searchsorted(side='right')` gave the complement. Fixed; ALL headline numbers re-derived post-fix. The pre-fix numbers had wrongly suggested negative ΔP intraday.
3. **Console column mislabeling (cosmetic, caught by user-facing review):** a digest printed "gross" over a fees-included column; corrected in the same session; JSON artifacts were always correct.
4. **"19–28bp target distance" understatement (my error, user-adjacent):** misread summary table; corrected to measured medians (33–161bp by TF) after user challenged it.
5. **hit_rate_given_fill display bug in dip ladder (unfixed, quarantined):** shows 0.0% due to a comparison against T rather than L; the OPTIMISTIC/PESSIMISTIC expectancy bounds do NOT depend on it and are the quoted quantities. Fix scheduled before Phase 3.

## PART V — REPRODUCIBILITY MAP

```
src/fetch_data.py          acquisition + QC (monthly zips cached in data/raw/, REST tail)
src/analysis_core.py       events, controls, ΔP, bootstrap, buckets, years  → results/summary_core.json
src/decompose.py           range-decile wick-vs-mirror-vs-body decomposition → results/decomposition.json
src/backtest.py            fee scenarios, equity curves, 2026 holdout      → results/backtest.json, curves.json
src/make_figure.py         reports/final_figure.png
src/conditional_stats.py   9-dimension conditional atlas                   → results/conditional/*.json (+master.json)
src/verify_cells.py        year-stability probe of top net-positive cells
src/explain_trades.py      worked examples + open/close gap proof
src/data_inventory.py      dataset inventory
results/pre_registration.md  frozen BEFORE outcome statistics
docs/FINDINGS.md           every measured number, organized by question
```
Bootstrap seed 42 everywhere; environment Python 3.11.16, pandas 3.0.5, numpy 2.4.3, scipy 1.17.1.
Data snapshot note: files refetch tails on each run; row counts in FINDINGS.md reflect snapshot 2026-08-24 ~22:00 UTC.
