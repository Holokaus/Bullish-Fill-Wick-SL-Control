# OPERATION FILLPOINT — Preregistered Protocol (V2 Bullish Fill Wick)

**Written**: 2026-08-24, BEFORE any price data was loaded, filtered or plotted in this operation.
**Rebuilt**: 2026-08-25 at C:\Users\A\Bullish-Fill-Wick\V2\ after F: drive unmount (verbatim
from in-context source; see AMENDMENT_1 §4).
**Status**: LOCKED. Any deviation must be logged in EXECUTION_CHANGELOG.md with rationale.

## 0. Mission
Study the Bullish Fill Wick concept from scratch, purely statistically, and either turn it
into a tradeable method or kill it honestly. Deliverable = a system you could actually run.

## 1. Identity
- Codename OPERATION FILLPOINT (OF). Concept: bullish candle with big UPPER wick -> fill.
- Markets: Bybit USDT-perp klines SOL(5m/15m/30m/1h/4h) ICP(same) BTC(15m/1h) ETH(1h).
- Long-only (concept as taught; bearish mirror out of scope unless separately preregistered).
- Goal hierarchy: facts with matched controls -> tradeable system -> validate once ->
  lockbox once -> spec sheet or death certificate.

## 2. Pre-lock disclosure
Prior study explored this data through Jun 2026 (upper-wick fills, body-pullback entries,
MFE/MAE grids). Jan2025-Jun2026 = INTERNAL CONFIRMATION only. Fresh ammunition = LOCKBOX
(Jul-Aug 2026, downloaded fresh, opened once at most). Old answers are priors, not evidence.

## 3. Windows
TRAIN Sep2022-Dec2024 (discovery, thresholds) / VALIDATION Jan2025-Jun2026 (one shot) /
LOCKBOX Jul1-Aug25 2026 (extended after F-drive loss; owner-directed; sealed until E-LOCKBOX).

## 4. Locked definitions
Bullish: close>open, high>low. uw_frac=(H-max(O,C))/(H-L). Big-wick signal: uw>=per-series
TRAIN tercile among bullish candles. Event time: outcomes strictly after signal bar closes.
Touch: low<=level<=high within window (bar granularity).

## 5. Hypotheses & kill conditions
H1 magnetism vs matched controls (ret24 quintile x range-expansion quintile x regime bins);
kill if deltas CI-span zero. H1b artifact decomposition. H2 reclaim entry. H3 pullback entry.
Judged net of costs under BOTH execution models.

## 6. Costs (locked day one)
Maker 0.02% / taker 0.055% per side (Bybit USDT-perp VIP0). RT: TAKER 11.0 bps, MAKER 4.0 bps
(entry fills require trade-through low<limit*(1-1e-4); TP counts on touch, disclosed),
MAKER-MIXED sensitivity (maker legs on TP exits, taker leg otherwise). SL-first pessimism
intra-bar. Funding sensitivity line for holds>8h instead of fake precision.

## 7. System construction (TRAIN only) + gates
Grid L{6,12,24} x f{0.5,0.75,1.0} x SL{low,mid} x Tmax{24,48,96}, one position per series.
Gates: pooled CI>0 (bootstrap 2000), N>=800, >=2 assets positive, neighbors non-knife-edge,
worst regime>-15bps. No flagship passes => NO SYSTEM SHIPS.

## 8. Confirmation shots
E-VAL once on VALIDATION (pass: CI>0, >=2 regimes positive, n>=200). E-LOCKBOX once
(pass: pooled>0 n>=30, worst cell>-20bps; else CONDITIONAL-INSUFFICIENT-AMMO).
KILL is final; no rescue re-rolls.

## 9-11. Hygiene, prohibitions, deliverables
Thinned overlapping-horizon inference; BH q<0.05 within declared families; thresholds printed
with quantile code; tz-naive UTC; background jobs with logs; negative results verbatim.
No param changes post-shot; no lockbox peeks; both execution models always reported.
Deliverables: fact tables + FACTS.md; SPEC SHEET if pass; death certificate if kill.
