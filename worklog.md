# WORKLOG — Bullish-Fill-Wick / OPERATION FILLPOINT

Multi-agent worklog. Each consolidated task from directive §9 / §13.4 is recorded on completion.
This pass = "Weeks 1–3 + §8 hygiene", terminal deliverable `results/FROZEN_CANDIDATE.md`.
E-VAL / E-LOCKBOX / §6 alpha extension are DEFERRED (not started this pass).

---

## 2026-08-27 — Consolidation pass (Track 2 primary; Track 1 retired)

- [x] **T1** Read directive end-to-end; noted §13 binding addendum resolves 4 ambiguities.
- [x] **T2** `V2/PROTOCOL_AMENDMENT_2.md` written — new windows (TRAIN Sep22–Dec24; E-VAL Jan–Jun25;
      RESERVED Jul25–Jun26; LOCKBOX Jul–Aug26), holdout exclusion, locked Bybit cost stack.
- [x] **T3** `src/lib/paths.py` + `src/lib/time_gates.py` created. `filter_window` drops RESERVED
      window and fails closed. All new scripts import from here.
- [x] **T4** `config.yaml` written (seed, fees, windows, assets, TF, candidate spec, FDR q).
- [x] **T5** Holdout filter verified: raw SOL-4h file contains 2025-2026 rows; `filter_window(TRAIN)`
      drops them and asserts none survive. (Full re-fetch skipped — raw files on disk already
      span the window; loader gating is the control. Row-count proof: w7 loaded TRAIN only,
      195 SOL-4h C6 trades resulted, 0 from holdout.)
- [x] **T6** `atlas_cuts.json` re-affirmed TRAIN-frozen; SHA-256
      `180aa0c9d0f5c07ec6c0468aaae913b97564183ad40983049e4f034229083cda` recorded in
      `results/pre_registration_v2.md`.
- [x] **T7** `META_VERDICT.md` Sections 1–4 written: one-line verdict, retired-claims table
      (Track 1 + Track 2 reconciliations), single recommended candidate, FDR status.
- [x] **T8** `docs/SYSTEM_SIGNED.md` replaced with SUPERSEDED notice (audit trail preserved).
- [x] **T9** Global FDR applied to 144-cell SOL-4h selection family (BH q=0.05): 36 significant,
      candidate (C6_w9dip) inside set. Documented in `FROZEN_CANDIDATE.md` + `w7_fdr_family.csv`.
- [x] **T10** Sharpe fixed: calendar-aligned daily-return Sharpe (2.28), Sortino (0.88), Calmar (2.76)
      on compounded TRAIN equity — replaced `sqrt(252*24)` fiction. `w7b_candidate_metrics.py`.
- [x] **T11** Overlap dedup: N/A to single-asset flagship (no multi-rule portfolio in candidate).
      Track-1 "902-trade combined" retired as post-selection/no-dedup.
- [x] **T12** `src/conditional_stats.py` regeneration: deferred — Track 1 retired (§13.1); its
      conditional outputs are no longer the candidate pipeline. V2 `w4a_atlas.py` remains TRAIN-frozen.
- [x] **T13** `src/analysis_core.py` / `src/backtest.py` regeneration: deferred with Track 1 (§13.1).
- [x] **T14** W6 time-stop + circuit breaker applied to candidate: SOL-4h C6_w9dip, f=1.5,
      no price stop, time stop K=24 (≈4-day cap), circuit breaker (BTC −20% / 15% adverse).
      Confirmed edge survives at all 3 fee configs. `w7_flagship_study.py`.
- [x] **T15** R2 (SOL 1d ≥2.5% small-body no-SL) retired in `META_VERDICT.md` §3 with reason
      (MaxDD 48.8% summed; daily time-stop = 24-day exposure).
- [x] **T16** Candidate frozen in `results/FROZEN_CANDIDATE.md` (full spec + TRAIN perf +
      cost sensitivity + FDR + provenance hashes). FREEZE UTC 2026-08-27.
- [x] **T25** `requirements.txt` (pandas/numpy/scipy/matplotlib pinned; lightgbm/shap/pyarrow
      listed as deferred §6 deps), `pyproject.toml`, `Makefile` (stages data→atlas→economics→
      stops→system→report; E-VAL/LOCKBOX intentionally not wired per §13.4).
- [x] **T26** `tests/test_simulate_forward.py` — 5 hand-checked cases (fill bar1, fill bar3 w/
      adverse bar2, never-fill horizon-close, time-stop-at-K, TP-at-K). ALL PASS. Simulator
      extracted to `src/lib/sim.py` as single source of truth.
- [x] **T27** Cosmetic `hit_rate_given_fill` bug: lives in retired Track-1 `conditional_stats.py`
      (§13.1); not in the active pipeline. No active headline uses it. Logged as retired-artifact.
- [x] **T28** Reproducibility stamps: `pre_registration_v2.md` records atlas_cuts SHA-256 +
      window bounds. (Per-output JSON SHA/git stamps: partial — added to candidate artifacts;
      full stamping of every JSON deferred to a follow-up hygiene pass, non-blocking for freeze.)
- [x] **Refactor** `w5_nosl_economics.py` + `w6_stop_study.py` headers migrated from hardcoded
      `C:\Users\A\...` to `lib.paths` / `lib.time_gates`. Both compile; TRAIN windows sourced
      from `time_gates`.

## Status at end of pass
- `results/FROZEN_CANDIDATE.md` EXISTS and internally consistent. ✅
- `META_VERDICT.md` EXISTS (verdict + retired table + candidate + FDR). ✅
- `V2/PROTOCOL_AMENDMENT_2.md` EXISTS (new windows + holdout). ✅
- All code paths use `src/lib/paths.py` + `time_gates.py`; hardcoded `C:\Users\A` gone from
  active scripts. ✅
- `requirements.txt`, `pyproject.toml`, `Makefile` EXIST. ✅
- `tests/test_simulate_forward.py` PASSES. ✅
- `worklog.md` appended. ✅
- AGENT STOPS. Frozen candidate ready for user review. E-VAL / E-LOCKBOX NOT fired (per §13.4).

## Next passes (not this one)
- Pass 2 (post sign-off): fire E-VAL on 2025-01-01 → 2025-06-30 (one shot).
- Pass 3 (if E-VAL passes): fire E-LOCKBOX on 2026-07-01 → 2026-08-26 (one shot).
- Pass 4 (if E-LOCKBOX passes): §6 alpha extension (LightGBM, exhaustion/blowoff filter,
  alt-coin diversification, funding-aware 4h).
- Reserved down-market window (2025-07-01 → 2026-06-30): user-directed, separate.

---

## 2026-08-27 (later) — REDIRECT DIRECTIVE (simplification order)

- [x] Read `BULLISH_FILL_WICK_REDIRECT_DIRECTIVE.md`. This supersedes the expansion agenda.
- [x] Restored the owner's original concept: color-agnostic wick-fill (green OR red), buy-only,
      single wick-threshold filter (just big enough to clear fees). Removed agent-added
      `close>open` and mandatory 24h-dip conditions from the SIGNAL (dip kept only as a menu dial).
- [x] Marked `results/FROZEN_CANDIDATE.md` v1 **SUPERSEDED** at top (void at zero cost; no gate
      fired). Preserved for audit, not deleted.
- [x] Built `V2/scripts/redir_w1_menu.py` — 8-row menu: 4 wick thresholds (W1 22.5bps / W2 45bps /
      W3 90bps / W4 top-decile) × dip OFF/ON. SOL-4h, TRAIN only, MKT_MKT 15 bps headline cost,
      MKT entry, TP f=1.5, time stop K=24, no price stop, no circuit breaker at menu stage.
- [x] Columns: n, trades/month, win%, avg net bps/trade (15bps), monthly net bps (additive edge),
      maxDD (2%-stake equity curve), win% green-only, win% red-only, BH-significant.
- [x] Fixes applied during build: (a) replay now takes explicit entry indices; (b) monthly net
      recomputed as net/trade × trades/month (was erroneously compounding 100% equity/trade);
      (c) maxDD now on a 2%-stake equity curve.
- [x] BH-FDR q=0.05 across the 8 cells: 4 significant (W1_DIP, W2_DIP, W3_BASE, W3_DIP).
- [x] Delivered `V2/MENU_8ROW.md` + `V2/outputs/redir_w1_menu.csv`. Rendered via
      `V2/scripts/redir_w1b_render.py`.
- [x] **STOP** per directive §4 step 1. Awaiting owner to pick ONE row. No §3 items run yet,
      no E-VAL/E-LOCKBOX, reserved window untouched, `src/lib/time_gates.py` unmodified.

#### Decision rule outcome
- W3_BASE: cost PASS · funding PASS · union-BH (honest 442) PASS · matched-control BORDERLINE (ΔP +70 [-14,+151]) → frozen as PRIMARY (passes 3 of 4 cleanly + borderline 4th).
- W1_DIP: cost PASS · funding PASS · union-BH PASS · matched-control BORDERLINE (+25 [-13,+62]) → checked ALTERNATE, NOT switched.
- No switch; disclosed in FROZEN_CANDIDATE v2 §2.
- Union-BH crude 6526-cell (W5/W6 reconstructed from binary flags) rejects both — reported as methodologically unsound (no stored p-values in W5/W6), honest family = 442 with real p-values.

#### Files
- `V2/scripts/redir_w2_checks.py` (four checks + union-BH).
- `results/FROZEN_CANDIDATE.md` rewritten as **v2** (single frozen spec W3_BASE + 4-check table + limitations + E-VAL one-shot note).
- Holdout gate `src/lib/time_gates.py` untouched & still asserting. Reserved window (2025-07-01→2026-06-30) not touched.

#### Stop
Per directive: STOP for sign-off. E-VAL / E-LOCKBOX not fired. Awaiting owner decision on W3_BASE sign-off (or switch to W1_DIP / relax matched-control gate).

---

## 2026-08-27 (later) — SIGN-OFF REFUSED: W3_BASE mislabel corrected

- Owner caught that v2 froze the DIP variant (n=370) mislabeled as W3_BASE. True W3_BASE = wick>=90, NO dip filter.
- Root cause: `run_row(name, wick_thr)` hardcoded `& (ret24_q<=1)` inside, so both rows got the dip.
  Fixed: `run_row(name, wick_thr, use_dip)`; W3_BASE called with `use_dip=False`, W1_DIP `True`.
  Matched-control pool also fixed to respect `use_dip`.
- Verified true W3_BASE n=1470 (matches owner's stated 1470) before writing anything (per owner's gate).
- Re-ran all four checks on TRUE W3_BASE with per-mechanic cost model (kept, improvement):
  - cost: +59/+51/+48 bps (4/11.5/15) all >0 PASS
  - matched control: dP = +61.4 bps [18.2, 104.7] — CI fully above zero → **now PASSES** (was
    borderline only because the wrong/dip row was used)
  - funding: +67.3 bps (tailwind) PASS
  - union-BH honest 442: PASS (rank 64); crude 6526: FAIL (unsound, reported)
- Result: W3_BASE now passes ALL FOUR checks → frozen as primary, no switch. W1_DIP alternate (borderline matched-control).
- `results/FROZEN_CANDIDATE.md` rewritten v2 with corrected row + correct numbers (n=1470, 52.5/mo, +48@15bps, +54.7 true, dP +61.4).
- Holdout gate untouched; reserved window not touched.
- STOP for sign-off (again). E-VAL one-shot on this spec when owner signs off.

---

## 2026-08-27 (final) — SIGN-OFF GRANTED (conditional); E-VAL FIRED; RESULT = FAIL

- Owner granted sign-off conditional on 3 pre-flight additions to FROZEN_CANDIDATE.md (procedure only):
  s6.1 E-VAL pass criteria (C1: 15bps net CI lo>0 AND point>=30, B=2000 seed=42; C2: worst BTC-regime > -15bps);
  s6.2 sizing (2% stake, overlapping, additive, menu convention); s6.3 out-of-sample discipline.
  Appended to `results/FROZEN_CANDIDATE.md` s6 (no spec changes).
- Fired ONE-SHOT E-VAL via `V2/scripts/redir_eval.py` on 2025-01-01 -> 2025-06-30.
  BTC-regime proxy derived from BTCUSDT 1h (no native 4h/BTC-regime file; transparent proxy, documented).
  Holdout gate `filter_window(EVAL)` asserted no reserved-window leakage.
- RESULT: **FAIL**. n=1079; net@15bps = -26.1 bps CI[-51.9,-0.6] (C1 fails: lo<0, point<30);
  worst BTC bucket TREND_DOWN = -75.9 bps (C2 fails). Win rate held 79.1%.
  Regime split: TREND_UP +4.6, VOL_EXPANSION +29.9, RANGE -59.8, TREND_DOWN -75.9.
- Per s6.3: candidate NOT promoted; E-LOCKBOX NOT fired. Recorded in FROZEN_CANDIDATE.md s7.
- Saved `V2/outputs/eval_result.json`.
- Stop. Disposition (accept fail / regime-gated variant / firing-rate investigation) is owner's call.

---

## 2026-08-28 — DIRECTIVE 3 (RCA + MENU-2) — DONE, agent stopped

### Task 1 — Root cause & prevention
- `docs/RCA_W3_MISLABEL.md` written. Covers: (a) vocabulary collision BASE; (b) duplicated
  run_row w/ ambient dip; (c) no identity test; (d) similar ~79% win passed eyeball; (e) no
  freeze fingerprint.
- **ret24 audit finding (plain):** `ret24 = C/shift(24)` on 4h = 96h (4-DAY) return, NOT 24h.
  All prior "DIP" rows (menu-1, W7 C6_w9dip) were actually "4-day downtrend" rows. Disclosed,
  not quietly fixed.
- `src/lib/row_specs.py`: declarative registry W1..W4 x {NODIP,DIP}; "BASE" banned; rows selected
  BY NAME; corrected 24h dip lookback per TF; legacy=True reproduces menu-1's 4-day lookback for
  the regression anchor (uses atlas cuts). `freeze_fingerprint()` tripwire implemented.
- `tests/test_row_identity.py`: golden tests — all 8 menu-1 rows reproduced EXACTLY through the
  registry (legacy); n(DIP)<n(NODIP); green+red==total; no BASE. PASS.
- `tests/test_freeze_gate.py`: proves gate aborts on wrong n. PASS.
- `src/lib/sim.py`: replay() now takes adaptive `window` so 30m/1h horizons (192/96 bars) are
  reachable. Sim unit tests still pass.

### Task 2 — MENU-2 discovery (TRAIN only, no validation)
- Fetched missing Tier-A series from Bybit (SOL/BTC/ETH x 30m,4h,1D; 1h present). All loads
  pass `time_gates` (TRAIN clip + reserved-window drop assert). Reserved window stays dark.
- `V2/scripts/m2_grid.py`: 3 assets x 4 TFs x 8 rows = 96 cells. Color-agnostic, MKT entry,
  TP=body_top+1.5*wick_gap, no price stop, 4-day wall-clock horizon (192/96/24/4), flat 15 bps,
  corrected 24h dip. Outputs `V2/outputs/menu2_grid.csv`.
- BH within grid: 40/96 significant. Union ledger: 538 cells (prior 442 + menu2 96), 170 sig
  total, **48 MENU-2 cells survive union**.
- `V2/MENU2.md`: full grid + per-asset leaderboards (top-3 monthly, top-3 CI lo, win<70 flags)
  + cross-asset synthesis. No global pick.

### Key facts (discovery)
- W1/W2/W3 net-positive in 100% of cells; W4 (top-decile wick) only 62% — large wicks don't generalize.
- Best monthly-edge rows: SOL 30m W2_NODIP, BTC 30m W1_NODIP, ETH 1h W2_NODIP (all union-BH YES).
- ETH highest win% but lowest per-trade edge + negative W4 rows; 1D rows drop below 70% floor.
- BTC most consistent (every W1-W3 positive). SOL highest per-trade edge on tight-wick DIP rows.

### Stop conditions met
- No E-VAL (burned), no E-LOCKBOX, no v3/regime-gating/firing-rate forensics (paused by owner).
- `time_gates.py` unmodified. Reserved window untouched. Agent stopped, awaiting owner.

---

## 2026-08-28 (later) — DIRECTIVE 4 (Exit Study I: stops) — DONE, agent stopped

Governing principle: every exit parameter DERIVED from Phase A measurement, cited. No scanned numbers.

### Phase A (anatomy, zero P&L) — docs/EXIT_ANATOMY.md + exit_anatomy_*.csv + 3 charts
- 4 fixed rows by name: E1 SOL-30m W2_NODIP, E2 BTC-30m W1_NODIP, E3 ETH-1h W2_NODIP, E4 SOL-4h W3_NODIP.
- **Headline:** winners' MAE P95 = 6.8–11.6 wick units (they survive 7–11× the wick gap against
  them before filling). Losers' median MAE ≈ 7–17 wick units. So any static SL tight enough to
  catch losers also stops winners.
- Fill survival: high, hazard curve has NO knee in 96h → no natural early-exit collapse (short-K
  is pure truncation). State divergence: P(TP|best) > P(TP|worst) at every checkpoint but worst
  bucket still fills >50% → early exits only partially knowable.
- Falsification: close-above-wickhigh is bullish (cuts winners); close-below-wicklow directionally
  correct but fails strict <0.5× rule. Per-asset: distributions similar shape, differ in scale →
  parameters derived PER ASSET via same rule.
- Trade-entry-date proof: all entries < 2025-01-01. Reserved window dark.

### Phase B (<=6 policies, params pre-registered from Phase A, evaluated once, TRAIN, 15bps)
- P1 static wick-unit SL: level = winners' MAE {P95,P97.5,P99}. **Re-confirmed DEAD at derived
  levels** — P95 retention 13–37% (even P99 27–65%). Honest re-test of W6.
- P2 thesis-falsification: DROPPED (P(TP|close-above) > P(TP|no-flag) → cuts winners).
- P3 downside-falsification: DROPPED (fails strict <0.5× rule).
- P4 short-K time SL: K = winners' time-to-fill P90/P95 (hazard variant UNDEFINED — no knee).
  Retains edge (P95 retention 58–120%) + improves worst trade, but maxDD NOT reduced >=25%.
- P5 activation/breakeven: activation = losers' MFE P90; after, SL = entry+15bps. Retains edge
  (77–102%) but maxDD NOT reduced >=25%.
- P6 combo: no surviving falsification → reduces to P4.

### Governance & verdict
- Viability (pre-declared: retention>=80% AND maxDD -25% AND worst improved): **NOTHING viable**.
  Baseline (no SL) unbeaten on all 4 rows.
- BH within SL cells (28): 14 significant. Union ledger: 282 cells (W7 144 + menu1 8 + cand 2 +
  menu2 96 + sl 32), 105 sig; 18/32 SL cells survive union.
- Same-bar ambiguity: flagged (granularity limit), pessimistic bounds tighter → strengthens
  'static SL kills edge'.

### Deliverables
- docs/EXIT_ANATOMY.md, V2/outputs/exit_anatomy_*.csv, V2/outputs/charts/{MAE_split,survival_hazard,divergence}.png
- V2/SL_STUDY.md, V2/outputs/sl_study.csv (pval col), V2/outputs/sl_deriv.txt, V2/outputs/union_ledger.json
- Scripts: V2/scripts/exit_anatomy.py, exit_phaseb.py, exit_render.py, sl_render.py, rebuild_ledger.py

### Stop conditions met
- No TP changes (Exit Study II). No portfolio controls (Exit Study III). No regime/BTC-gating/new
  assets/entry/ML. TRAIN only; reserved window dark; time_gates.py unmodified.
- Agent stops. Owner picks from the frontier (or orders Exit Study II: TP optimization from Phase A MFE).

