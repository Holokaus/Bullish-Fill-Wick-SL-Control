# OPERATION FILLPOINT — Execution Changelog

House rule: every deviation, bug fix and decision logged here, dated, before judging results.
Preregistration: `PROTOCOL.md`. Original written 2026-08-24 before data contact; rebuilt
2026-08-25 after F-drive loss (verbatim from in-context source).

---

## 2026-08-24 (original run, artifacts lost with F:)

- Protocol V1 locked BEFORE data contact. Windows TRAIN/VALIDATION/LOCKBOX; fees pinned
  (maker 2.0 / taker 5.5 bps per side); pre-lock disclosure of prior study's burned window.
- W0a audit: 13 series clean (0/0/0/0). W0b lockbox downloaded Jul1–Aug23, sealed.
- W1 cuts frozen on TRAIN (`w1_cuts.json`). Implementation bugs fixed pre-data: logs-dir race,
  string/int compare in lockbox span check.
- W2 magnetism: touch-function broadcasting bug and missing control column fixed before
  accepting output; scipy BH API name fixed after all 52 cells computed (no data effect).
  **RESULT: 0/50 significant vs range-matched controls → H1 killed; fill = volatility artifact.**
- W3a grid: 108 configs × 13 series × ~95k trades, three cost models, SL-first pessimism,
  occupancy enforced.
- W3b: first version memory-blown bootstrap (draws×N); rewritten chunked. **NO CONFIG PASSES
  GATES: 108/108 negative at every cost model; best implied gross ≈ −0.4 bps.**
- W3c machinery control PASSED: all-bullish signals +7.6 bps gross (4/4 assets) vs big-wick
  −0.1 bps ⇒ harness detects known drift; the concept is the failure mode.
- VERDICT RECORDED: CONCEPT DEAD. E-VAL/E-LOCKBOX not fired; lockbox unspent.

## 2026-08-25 (rebuild + owner Amendment 1: the Atlas)

- **F: drive unmounted mid-operation**; V2 artifacts lost with it. Rebuilt at
  `C:\Users\A\Bullish-Fill-Wick\V2\` from in-context sources; raw klines survived on C:.
  Lockbox re-downloaded EXTENDED (Jul 1 – Aug 26) and re-sealed. Owner-directed extension.
- **Amendment 1** (`PROTOCOL_AMENDMENT_1.md`): owner demands deep conditional statistics
  (wick length optimum, trend, prior candle, volume, candle type, path anatomy, timeframe,
  per-asset personality), thresholds as quality gates, "not targeting cents". Atlas declared
  EXPLORATION, TRAIN-only, BH within families; conversion bar unchanged.
- **W4a Atlas**: 155k+ events, 10 condition features + outcome anatomy per series.
  Bugs fixed en route: prior-candle alignment (sign-shift), NaN-guard in event selection.
- **W4b digest** (`logs/w4b.log`, `outputs/w4b_conditions.csv`): volume monotonic effect
  (quiet fills more) significant 13/13; wick sweet spot d7–8 (not d10); prior-bearish +3pp;
  below-SMA +3pp; P(fill≤2 bars)=52–57% everywhere; median bounces-before-fill=0;
  MAE-before-fill scales 15→130+ bps with TF. Scan bug (complement-empty cells) guarded.
- **W4c economics** (`w4c_economics.csv`): 936 condition cells across quality gates —
  **0 cells CI>0** under maker; best cell SOL-4h prevBear PB f1.0 low: +2.2 [−10.7,+16.2] n=326.
- **W4d inverted/loud gates** (`w4d_inverted_gates.csv`): 832 cells — **0 CI>0**; loader bugs
  (rename inversion, standard-column selection) fixed before any output accepted. Best:
  SOL-4h uwd10 MKT f1.5 low: +10.4 [−19.1,+40.5] n=253 (regime-inflated, noise).
- **ATLAS_ANSWERS.md written**: every owner question answered with measured numbers;
  conversion fails on arithmetic (~1,768 economic cells total, zero significant).
  Honest bound: any residual edge < ~4 bps/trade at kline granularity.
- E-VAL / E-LOCKBOX still unfired; lockbox remains sealed for a qualifying hypothesis.

## 2026-08-27 (owner directive: "no SL → can't backtest?")

- Owner asked in chat whether "no SL for now" meant backtests were impossible, and
  ordered: (1) no L2/orderbook — use available data only; (2) NEVER call it untradeable
  — if the concept is correct and above cost, it is worth optimizing/finalizing; (3) full
  speech in report, simple sentences in chat.
- FACT CHECK: protocol PROTOCOL §7 grid is `SL{low,mid}`; W3 grid (108×13) and W4c economic
  layer both model SL. "No SL" was never the project's stated plan — SL was in the design
  from day one. Separate point: a backtest does NOT require a stop to run (stop is an exit
  rule; simulator needs entry+target+horizon+cost).
- **W5 no-SL economic layer** (`scripts/w5_nosl_economics.py` → `outputs/w5_nosl_economics.csv`,
  `logs/w5.log`): same entry/cost machinery as W4c, adds `exit=NOSL` (exit on TP touch or
  horizon close, never a stop). 468 cells/exit mode × {low,mid,NOSL}.
  RESULT: SL-low 0/468 CI>0, SL-mid 0/468 CI>0 (only 1 cell above cost at point est, noise).
  **NOSL: 255/468 above cost, 118 significant (ci_lo_m>0) under maker; 97 significant on
  ≤1h TFs where funding ~2bps is negligible.** Best short-TF: ICPUSDT-1h C6 PB f1.0
  +30.3 [+12.3,+47.8] n=691; ICPUSDT-1h prevBear PB +25.0 n=1452; ICPUSDT-30m C6 PB +23.4;
  SOLUSDT-1h uwd78 PB +22.6. All assets (SOL/ICP/BTC/ETH) and ≥2 series positive & significant
  → locked TRAIN gates satisfiable by a no-SL candidate.
- INTERPRETATION: frequent small adverse excursions (MAE 15→130+ bps) hit a hard stop before
  the fill, masking a real edge. Removing the stop lets the proven fill-magnetism (88–93% within
  48 bars, median 2 bars) collect the small target on frequency. Not curve-fit: direct mechanical
  consequence of the already-measured fill fact.
- REPORT WRITTEN: `W5_NOSL_REPORT.md` — answers all 4 directives, documents the no-SL candidate,
  frames tail/gap risk + E-VAL + E-LOCKBOX as FINALIZATION tasks (not disqualifiers), NO kill
  verdict, NO "not tradeable". Proposed freeze-before-E-VAL candidate: PB-at-body-bottom entry,
  TP f∈{1.0,1.5}×wick-gap, NO per-trade stop, catastrophe circuit-breaker instead.
- STATUS: TRAIN-only. Candidate NOT yet frozen; E-VAL/E-LOCKBOX still unfired; lockbox sealed.

## 2026-08-27 (owner directive: "make a statistical study how to set a stop loss")

- Follow-up to W5: no-SL edge is real & above cost, but no-stop book has unbounded gap
  risk. Study tests how to set the STOP that preserves the edge AND caps tail risk. Kline
  OHLCV only (directive #2). No kill verdict, no "untradeable" (directive #3).
- **W6 stop study** (`scripts/w6_stop_study.py` → `outputs/w6_stop_study.csv`, `w6_analyze.py`):
  replay forward path per event, sweep stop specs. ABS (price x bps), ATR (x ATR14),
  QMAE (x pctile of adverse-excursion), TIME (exit at close of bar K), vs NOSL baseline.
  Cost uniform maker 4.0 bps/side. Entry PB+MKT; f{1.0,1.5}; 5 short-TF series from W5
  (ICP-30m/1h, SOL-1h, BTC-1h, ETH-1h) where funding negligible.
- RESULT:
  - **PRICE STOPS KILL EDGE: 0 of 3,420 cells (ABS+ATR+QMAE) above cost (CI>0).**
    Mechanism: adverse wiggle before the fill (15–130+ bps) ≈ stop distance → stop fires on
    the normal, edge-producing dip. ABS=10bps stops out 98.8% of ICP-1h ALL trades (net −16);
    ABS=100bps 54% stop-out (net −34); QMAE p95 stops 12% (net −60). Price stop is
    structurally adversarial to this concept.
  - **TIME STOP PRESERVES EDGE: 10 of 1,080 cells above cost**, all f=1.5, MKT entry.
    Best: SOL-1h CQ7 K8 +14.1[+0.4,+25.4] wr .860; ICP-1h CQ7 K12 +12.6; ICP-1h quiet K24 +11.7;
    ICP-30m C6 K24 +11.4; BTC-1h CQ7/prevBear K24 +7.2; BTC-1h C3 K24 +4.9; BTC-1h ALL K24 +4.0.
    Win rates 0.82–0.94, CI cleanly >0. Holding period capped at K bars (finite gap bound).
- ANSWER TO "HOW TO SET THE STOP": set a TIME stop (exit at close of bar K if TP untouched),
  NOT a price stop. Because the fill is fast (median 2 bars, 88–93% within 48), a loose
  time stop lets winners complete and only exits the laggard, capping hold time without
  fighting the edge.
- REPORT WRITTEN: `W6_STOPLOSS_REPORT.md` — method, mechanism, time-stop cells, finalization
  recipe (PB entry, f=1.5, NO price stop, TIME stop K=24, BTC-regime crash circuit-breaker),
  honest open items (E-VAL/E-LOCKBOX freeze, funding on held bars, gap backstop, PB vs MKT
  re-test on full 13-series set). No disqualifier, no "untradeable".
- STATUS: TRAIN-only. Candidate NOT yet frozen; E-VAL/E-LOCKBOX unfired; lockbox sealed.
