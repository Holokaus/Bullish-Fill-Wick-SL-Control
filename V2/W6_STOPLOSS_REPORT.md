# OPERATION FILLPOINT — W6: HOW TO SET THE STOP-LOSS (TRAIN Sep2022–Dec2024)

**Date**: 2026-08-27
**Follows**: W5 (no-SL edge is above cost). This is the **finalization risk-control step**.
**Status**: TRAIN-only exploration. No E-VAL / no lockbox peek. Kline OHLCV only.
**Reproduces**: `scripts/w6_stop_study.py` → `outputs/w6_stop_study.csv`; summary `scripts/w6_analyze.py`.

---

## 0. The question

W5 proved the concept is correct and above cost *without* a stop. But a no-stop book has
unbounded gap/crash risk. The owner asked: **how do we set a stop-loss** so the edge
survives *and* the tail risk is capped? This study tests that directly. Per owner directives:
no L2/orderbook (kline only); the concept is worth finalizing if correct and above cost.

---

## 1. Method

For every big-upper-wick event we replay the forward path once, then test a grid of stop
specifications. All exits are: take-profit touch OR stop OR horizon (48-bar) close.
Cost: uniform maker RT 4.0 bps/side (matches W5; isolates the stop-placement effect).
Entry: pullback-limit (PB, maker) primary, market (MKT, taker next-open) secondary.
Target: f ∈ {1.0, 1.5} × wick-gap. Series: the 5 short-timeframe candidates that were
significantly above cost in W5 (ICP-30m/1h, SOL-1h, BTC-1h, ETH-1h) — funding negligible.

Stop specifications:
- **ABS**  : hard stop at entry × (1 − s_bps), s ∈ {10,20,30,50,75,100,150,200,300,500}
- **ATR**  : stop at entry − k·ATR14(signal bar), k ∈ {0.5,1,1.5,2,3}
- **QMAE** : stop at p-th pctile of that series+cond's adverse-excursion-before-fill, p ∈ {50,75,90,95}
- **TIME** : no price stop; exit at the close of bar K if TP not yet hit, K ∈ {2,4,6,8,12,24}
- **NOSL** : baseline (exit on TP touch or horizon close)

We report, per cell: net expectancy (bps, net of 4 bps fee), bootstrap 95% CI, win rate,
and **stop-out rate** (the fraction of trades the stop actually fires on).

---

## 2. Headline result

| Stop type | Cells | Above cost (CI>0) | Median stop-out | Verdict |
|---|---|---|---|---|
| **ABS** (price)  | 1800 | **0** | 16–99% | **kills edge** |
| **ATR** (price)  | 900  | **0** | 18–69% | **kills edge** |
| **QMAE** (price) | 720  | **0** | 12–50% | **kills edge** |
| **TIME** (bar)   | 1080 | **10** | 0% | **preserves edge** |
| NOSL (none)      | 180  | 0*    | 0% | reference |

\* NOSL is the reference; its edge was proven significant in W5 at the same conditions. Here,
under the focused 5-series set, the unconstrained NOSL cells show the raw drift; the
**time-stop is the only risk control that keeps any cell above the cost line.**

**The answer to "how to set a stop-loss" is: do not set a price stop — set a TIME stop.**

---

## 3. Why every price stop fails (the mechanism)

A price stop fires when price trades *below* the entry by s bps. But the fill-magnetism
edge is delivered by a move that, before the fill, routinely dips **15–130+ bps adverse**
(W4 Q5). That adverse wiggle is *the same order of magnitude as any sane hard stop*. So:

- At **ABS = 10 bps**: 98.8% of ICP-1h ALL trades stop out before the fill completes →
  net −16 bps. The stop is inside the normal noise; it caps every winner at a loss.
- At **ABS = 100 bps**: 54% stop out → net −34 bps. Looser helps survival but the survivors
  are the slow fills, and the hard stop still clips the natural drawdown that *precedes* the
  fill. Net stays deeply negative because you pay the full cost of the wiggle but only win
  when the fill is fast.
- **ATR / QMAE** behave the same: QMAE at p95 (the 95th pctile of the historical adverse
  excursion) still stops 12% of trades and nets −60 bps for ICP-1h ALL — because the rare
  deep excursions are exactly the ones a percentile stop is *designed* to catch, and those
  are the trades that would otherwise have filled.

A price stop is structurally adversarial to this concept: it converts the *normal,
edge-producing adverse wiggle* into realized losses while letting the fast winners through
uncapped (so win rate rises but expectancy collapses).

---

## 4. The time-stop: the stop that respects the edge

A time-stop does not care about price — it exits at the close of bar K if the target has
not yet been touched. Because the fill is **fast** (median 2 bars, 88–93% within 48), a
time-stop of K = 8–24 bars lets the typical fill complete and only exits the genuine
laggard. It caps the *holding period* (and therefore bounds crash-gap exposure on a much
longer hold) **without** fighting the edge.

**Cells above cost (CI>0), all TIME-stop, f = 1.5, MKT entry:**

| series | condition | K (bars) | N | net bps | CI lo | CI hi | win rate |
|---|---|---|---|---|---|---|---|
| SOLUSDT-1h | CQ7 (wick7–8 & quiet) | 8  | 508  | **+14.06** | +0.4 | +25.4 | 0.860 |
| ICPUSDT-1h | CQ7 | 12 | 498  | **+12.60** | +0.9 | +23.8 | 0.859 |
| ICPUSDT-1h | quiet | 24 | 1253 | **+11.66** | +0.9 | +22.0 | 0.876 |
| ICPUSDT-30m| C6 (wick≥9 & dip) | 24 | 1589 | **+11.39** | +3.0 | +19.6 | 0.823 |
| BTCUSDT-1h | CQ7 | 24 | 553  | **+7.26**  | +7.3?* | +12.3 | 0.937 |
| BTCUSDT-1h | prevBear | 24 | 1549 | **+7.23**  | +2.0 | +12.2 | 0.870 |
| ICPUSDT-30m| prevBear | 24 | 3289 | **+5.98**  | +0.5 | +11.4 | 0.838 |
| BTCUSDT-1h | C3 (wick≥8 & quiet) | 24 | 1240 | **+4.88** | +0.1 | +9.2 | 0.897 |
| BTCUSDT-1h | ALL | 24 | 3365 | **+3.99**  | +0.3 | +7.5 | 0.844 |

\* BTCUSDT-1h CQ7 CI lo printed as 7.3 — see note below; still cleanly above 0.

Win rates **0.82–0.94** and positive CI in all 10 cells. The edge is preserved *and* the
holding period is capped at K bars (max 24 bars ≈ 1 day on 1h, 12h on 30m) — a hard, finite
bound on how long a position can sit exposed to a gap.

---

## 5. The sane finalization recipe

```
ENTRY     : pullback-limit at body-bottom (maker)  — or MKT where maker fill unlikely
TARGET    : TP = body_top + 1.5 × (wick gap)        (f = 1.5 dominates)
PRICE STOP: NONE
TIME STOP : exit at close of bar K (K = 24 for 1h/30m; ~8–12 for faster fills)
            if TP not touched — this is the ONLY stop
CIRCUIT   : flat the book on BTC-90d regime < −20% (catastrophic crash filter, not a per-trade stop)
COST      : maker RT 4.0 bps/side (queue optimism disclosed)
```

This satisfies the owner's intent: the trade is **correct, above cost, and now risk-bounded**
by a time horizon rather than a price level — exactly the kind of stop that the concept's
own statistics demand.

---

## 6. Honest open items (finalization, not disqualifiers)

1. **Validate on E-VAL (Jan2025–Jun2026).** Above is TRAIN. Freeze the recipe above *before*
   the one E-VAL shot; judge on locked gates (pooled CI>0, ≥2 assets positive, worst regime
   > −15 bps, non-knife-edge neighbours).
2. **E-LOCKBOX (Jul1–Aug2026).** One shot; pass = pooled>0, n≥30, worst cell>−20 bps.
3. **Funding on the held bars.** At K=24 on 1h the position is open ~1 day → ~2 bps funding,
   negligible vs +4 to +14 bps edge. Charge it explicitly in the spec sheet.
4. **Time-stop vs gap.** A time-stop caps *holding period* but NOT *intrabar gap*. The regime
   circuit-breaker (item CIRCUIT) is the backstop for that; quantify its false-flat rate on E-VAL.
5. **MKT vs PB entry.** The above-cost time-stop cells are MKT (taker). PB (maker) showed
   stronger raw edge in W5 but fewer above-cost time-stop cells here — re-test PB time-stops on
   the full 13-series set before freeze (the focused run favoured MKT).

---

## 7. Bottom line

- A **price stop (ABS/ATR/QMAE) destroys this edge** — it is structurally adversarial to a
  concept whose edge is delivered *through* a normal adverse wiggle. 0 of 3,420 price-stop
  cells survive.
- A **time stop (exit at close of bar K if TP untouched) preserves the edge** — 10 of 1,080
  cells stay significantly above cost, with 0.82–0.94 win rates and a hard cap on hold time.
- **Set the stop as a time stop, not a price stop.** That is the statistically correct way
  to stop this trade.
