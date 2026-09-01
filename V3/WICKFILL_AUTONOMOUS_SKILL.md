# WICK-FILL AUTONOMOUS STUDY — MASTER SKILL (canonical, v2.0)

**Status:** replaces `SKILL-4.md`, `Bullish-Fill-Wick-Skill-4.md`, `Bullish_Fill_Wick_Autonomous_Skill_v1-4.md`.
**Authoritative for:** running the color-agnostic upper-wick-fill statistical study for ONE named Bybit
USDT-perp asset, end-to-end, repeatably, with every number derived from THAT asset's own data.

**One-line contract:** Owner names ONE asset → agent runs fetch → TRAIN anatomy → full option grid
(all cells, all exit policies) → delivers the complete tested menu → **owner picks ONE spec** →
agent freezes it, fires one-shot E-VAL, reports, stops. Same methodology, different numbers, every time.

> This skill was written *after* the three prior drafts were reviewed against the real repo. Where it
> disagrees with those drafts, THIS file wins. The most important correction: the multiplicity
> correction is `V3/lib/stats.py::bh_reject` (correct step-up). Two prior drafts told the agent to use
> `rebuild_ledger.py`/`exit_phaseb.py` BH — those are BROKEN (verified by `V3/tests/test_bh_canonical.py`)
> and MUST NOT be copied. See §0.

---

## 0. The one rule that overrides everything: STATS COME FROM `lib.stats`

The project's worst historical bug was a **broken Benjamini–Hochberg** that mislabeled ~50/96 cells.
The repo contains THREE BH implementations:

| Module | Verdict | Why |
|---|---|---|
| `V3/lib/stats.py::bh_reject` | **USE THIS** | correct step-up (k* chaining). Mandated by `KEEPN_EXIT_DIRECTIVE.md:157`. |
| `V2/scripts/rebuild_ledger.py::bh_reject` | **BANNED** | elementwise `rej[order]=p[order]<=thr` — no k* chaining; under/over-rejects on gap vectors. |
| `V2/scripts/exit_phaseb.py::bh_reject` | **BANNED** | identical broken elementwise impl. |
| `V2/scripts/m2_grid.py` (inline) | **BANNED** | compares UNSORTED p against sorted-step threshold — scrambles indices. |

`V3/lib/stats.py` is also the ONLY home for `bootstrap_ci`, `bootstrap_ci_by_day`, `wilson_ci`, `cell_p`.
**No other file may define these.** If you are about to copy a BH/bootstrap/cell_p into a script, stop
and `from stats import bh_reject, bootstrap_ci, cell_p` (V3/lib on sys.path). `V3/tests/test_bh_canonical.py` asserts the
canonical one is correct AND the three banned ones diverge — it runs in `make test` (from V3/).

---

## 1. Invocation & autonomy scope

- **Trigger:** owner message naming exactly one asset, e.g. `"Run a full wick-fill study on AVAXUSDT"`.
- **Autonomy:** Stages S0–S4 run end-to-end, no owner questions (except irrecoverable data failure → halt).
- **Mandatory stops (never skip):**
  1. S0 irrecoverable data failure (asset not listed on Bybit USDT-perp).
  2. **S5 — menu delivered, owner picks.** The agent NEVER selects, recommends, or freezes a winner.
  3. **S6 — the literal word FIRE** before E-VAL (E-VAL is irreversible / one-shot).
- One asset per run. Never compare assets inside a menu. Portfolio / cross-asset = out of scope.

## 2. Fixed vs derived (the heart of "same method, different numbers")

### 2.1 Fixed constants — change ONLY by owner order, in writing
Venue/symbol `Bybit USDT-perp {ASSET}USDT` · TF set `30m,1h,4h,1D` · TRAIN `2022-09-01→2024-12-31` ·
E-VAL `2025-01-01→2025-12-31` (one-shot) · RESERVED `2025-07-01→2026-06-30` (DARK, never loaded) ·
E-LOCKBOX `2026-07-01→2026-08-26` (unfired; only after E-VAL PASS on owner order) · TP `body_top+1.5·wick_gap` ·
baseline stop = 4-day wall-clock K = `round(4h/TF)` bars, no price stop · costs 15 bps RT headline,
true-cost 4/11.5/15 bps (per `lib.time_gates.RT_CONFIGS`); funding charged from real history ·
bootstrap B=2000 seed=42 · BH q=0.05 over the global union ledger · stake 2% per trade, overlapping,
additive bps · entry = market buy at next bar open; require `ts(e+1)-ts(e)==TF`, else skip (count+disclose).

### 2.2 Derived per (asset, tf, cell) — ALWAYS recomputed, ALWAYS cited
W thresholds (W1–W3 = 1.5/3/6 × RT; W4 = TRAIN top upper-wick decile), trigger rates n, win% (total/green/red),
net at all cost configs, monthly additive, maxDD, median hold, bootstrap CIs, p-values, BH flags,
matched-control ΔP, funding-adjusted net, exit params (winners' MAE P95/97.5/99, time-to-fill P90/P95,
losers' MFE P90), E-VAL results. **No derived number is hand-typed into a document** (§8).

## 3. Hard rules (each maps to a real Phase-1 incident)
- **R1 No agent selection.** Banned words in agent text: *best, recommended, winner, top pick, suggest, should choose*.
- **R2 Parameters derived, never assumed.** Inheriting another asset's numbers (e.g. SOL K=42h, its MAE levels) is a violation.
- **R3 Windows sacred.** All loads route through `lib.time_gates.filter_window`. Reserved window dropped + asserted dark on every load. Trade-date proof: max entry ts ≤ 2024-12-31 for every TRAIN artifact.
- **R4 One-shot gates.** E-VAL fires ONCE per frozen spec. No re-runs, no post-hoc spec changes. Check burn registry before firing.
- **R5 No silent filters.** Every condition is an explicit named kwarg in `lib.row_specs`; no script re-implements row logic.
- **R6 Vocabulary.** Rows `W1..W4_NODIP`/`W1..W4_DIP`. Word **"BASE" banned everywhere** (lint-checked).
- **R7 Stats only from `V3/lib/stats.py`** (§0). The banned BHs (`rebuild_ledger.py`, `exit_phaseb.py`, `m2_grid.py`) must never be imported or copied. There is NO `analysis_core.py` in this repo — if a draft names it as the bootstrap source, that draft is wrong; bootstrap/Wilson/cell_p live only in `V3/lib/stats.py`. Do not port `rebuild_ledger.py`'s BH under any name — it is the broken elementwise version, not a correct one.
- **R8 Numbers flow from CSV/JSON to docs by template.** Verdict lines code-generated.
- **R9 Honest costs + multiplicity.** 15 bps floor; funding from real history (never assumed away); every tested cell enters the union ledger; family size disclosed in every menu.
- **R10 Report, then stop.** Each stage ends at its artifact; agent never advances its own agenda.
- **R11 Anomalies investigated, not waved away.** Identical digits / non-monotonic / retention>100% → recompute from raw logs, prove arithmetically.
- **R12 Provenance.** Append-only worklog; every artifact carries run_id + atlas cuts hash.

## 4. Pipeline

### S0 — Intake & data (autonomous)
1. `RAW_DIR = lib.paths.RAW_DIR` (env `BULLISH_WICK_RAW_DIR`, default `C:\Users\A\Downloads\opencode-bybit`).
   For each TF fetch `{SYM}-FUTURES-2022-2026-{TF}.csv` if missing (Bybit v5 kline, de-dupe on `time`, drop a last bar whose close_time is in the future). UTC ms.
2. Fetch funding-rate history for the asset.
3. **Data inventory:** per file — first/last ts, row count, dup count, gap count, expected-vs-actual bars. No interpolation; gaps reported + handled by the skip rule.
4. **Load-path audit:** assert every consumer loads through `lib.time_gates.filter_window`; reserved window dropped.
5. **TRAIN floor:** usable TRAIN < 12 months → halt + report (owner decides on disclosed weaker TRAIN).
6. Re-verify Bybit fee schedule vs §2.1; report drift (constants unchanged unless owner orders).
7. Check burn registry: if E-VAL already burned for this asset, deliver the menu but mark every artifact "E-VAL BURNED — no validation available".

### S1 — TRAIN anatomy & parameter derivation (autonomous)
Freeze analysis cuts BEFORE any grid run; write `atlas_cuts_{SYM}.json` (+ SHA-256).
1. Upper-wick distribution per TF (bps histogram, deciles). Report where W1–W3 ladder lands on THIS asset.
2. W4 = TRAIN top upper-wick decile (frozen).
3. Dip quintile cuts: trailing 24h return, lookback bars = `round(24/TF_HOURS[tf])` (the `ret24` bug was a 24-bar lookback on 4h = 96h).
4. Trigger-rate table (events/month per row per TF) — needed for the E-VAL anomaly check.
5. Baseline target anatomy: T−entry distance vs 15 bps cost floor.

### S2 — Entry grid (autonomous, TRAIN)
Full cross = 4 TF × {W1..W4} × {NODIP, DIP} = **32 cells, all run, all delivered.** (An asset may
add its own native percentile tiers as EXTRA rows that join the ledger — see §2.2 — but the 32 fixed
cells are the baseline and are never dropped.)
Per cell (all from `lib.row_specs` + `lib.sim` + `lib.stats`): n · trades/month · win% · win% green ·
win% red · net @ {4,11.5,15,true-cost} · net pessimistic bound · monthly additive · maxDD (2%) ·
median hold · worst trade · bootstrap CI (B=2000, seed=42) · p-value (`cell_p`) · within-grid BH flag.
Append every cell (with p-value) to the **global union ledger**; compute `bh_union` over the entire ledger.

### S3 — Integrity battery (autonomous, TRAIN — every cell, no pre-filtering)
(1) cost sensitivity; (2) matched-control ΔP (paired non-wick buys matched on color + range decile, bootstrap CI on win-increment); (3) funding-adjusted net from real funding history (no data → UNAVAILABLE, flagged, never silently zero); (4) `bh_union` flag. Failing cells stay in the menu with flags. Diagnostic only — never narrows the field.

### S4 — Exit study (autonomous, TRAIN — every cell × policy)
**Phase A** per cell (use `V2/scripts/exit_anatomy.py` — now asset-agnostic: `python exit_anatomy.py --symbol {SYM} --tf 30m 1h 4h 1D`):
winners' MAE P95/P97.5/P99 (wick units) · losers' MFE P90 · winners' time-to-fill P90/P95 (h) · hazard knee.
**Phase B** policies — params derived from THAT cell's Phase A, never another asset (use `V2/scripts/exit_phaseb.py`):
`BASELINE_noSL` (S2 spec) · `P1_wickSL_P95/97.5/99` · `P4_timeSL_P90/P95` (+ `P4_timeSL_hazard` if a knee exists, else UNDEFINED/dropped) · `P5_act_breakeven` · P2/P3 falsification ONLY if `P(TP|flag) < 0.5·P(TP|no-flag)` on that cell.
Per cell × policy: full metric set + retention vs that cell's baseline + viability verdict computed by code
(retention ≥ 80% of baseline net AND maxDD ≤ 75% of baseline AND worst trade improved). Full cross (32 × ~8 = ~256 rows) → `exit_grid.csv`; every row delivered. No policy promoted/removed by the agent.

### S5 — MENU delivery (MANDATORY STOP — owner's decision)
Generate `MENU.md` from CSVs by template. Contents:
1. Complete option space: all 32 entry cells (S2+S3) + all cell×policy exit rows (S4), including NaN/low-n (flag n<100).
2. Mechanical leaderboards (sort only): by win%, by net/trade, by monthly, by maxDD asc, by retention. Sorting is data; commentary is not.
3. Multiplicity bill: union-ledger family size, BH-significant count, this run's contribution.
4. Asset data-quality summary (S0); burn-registry status; skipped-event counts; same-bar ambiguity bounds.
5. The exact E-VAL protocol that will run on the owner's pick (§6), pre-declared.
**Then STOP. No recommendation sentence anywhere in MENU.md.**

### S6 — Freeze & E-VAL (one-shot, after owner's pick)
1. On owner's pick (asset+TF+row+policy): assert against `lib.row_specs.freeze_fingerprint` (n, trades/month, asset/TF/threshold/dip/K/TP). Mismatch → abort, never "fix".
2. Write `FROZEN_CANDIDATE.md` (full spec, all TRAIN numbers by template, four-check results, honest limitations) + `pre_registration.json` (cuts hash, family size, criteria, run_id).
3. Echo the freeze fingerprint. **Wait for the literal word FIRE.** No FIRE, no E-VAL.
4. Fire E-VAL ONCE on `2025-01-01→2025-12-31`: n · win% · net @ {4,11.5,15,true-cost} · CI (B=2000, seed=42) · maxDD · worst · BTC-regime buckets (`lib.regimes` if present, else BTC 1h 24h-return proxy) · **trigger-rate ratio** (actual n ÷ TRAIN-implied expected n; flag >2×) · funding-adjusted net.
5. Verdict (see §5). Report each criterion's numbers + verdict; state disposition. Append burn record.
6. If PASS and owner orders it: E-LOCKBOX one-shot on `2026-07-01→2026-08-26`, same criteria. Otherwise STOP.

## 5. E-VAL pass criteria (single definition — overrides the divergent gates in the three prior drafts)
- **C1:** net/trade @15 bps — bootstrap CI lower bound > 0 AND point estimate ≥ 30 bps (2× the cost hurdle).
- **C2:** worst BTC-regime bucket net > −15 bps.
- **C3:** win rate within ±5% of TRAIN (edge stability / concept survival).
- **C4:** n within [0.5×, 3.0×] of TRAIN-implied expected (trigger-rate sanity; flags the 3.4× anomaly).
- **PASS only if C1 AND C2 AND C3 AND C4 hold.** FAIL on any → candidate NOT promoted. No re-run, no spec mutation, no window reuse.

## 6. Deliverables & schemas
Under `V2/outputs/` (asset-prefixed, never overwriting): `data_inventory.md` · `atlas_cuts_{SYM}.json`(+SHA) ·
`anatomy.md` · `entry_grid.csv` · `integrity.csv` · `exit_anatomy_*` · `exit_grid.csv` · `MENU.md` ·
`FROZEN_CANDIDATE.md` + `pre_registration.json` · `EVAL_REPORT.md` · global `union_ledger.json`.

## 7. Self-check battery (gates: before S2, before S5, before FIRE)
1. `make test` passes (stats unit checks incl. BH correctness; row identity; freeze gate). Fail → abort stage.
2. Row identity: registry n == golden == grid n per row (`lib.row_specs.freeze_fingerprint`).
3. Trade-date proof: max TRAIN entry ≤ 2024-12-31; reserved-window darkness assert passes.
4. Load-path audit clean (only intended files feed the simulator, all via `filter_window`).
5. Render sanitizer: no `np.float64/int64` reprs, no unrendered `{...}`, floats ≤ 4 decimals.
6. Doc-number diff: every number in prose traces to a CSV/JSON cell (template check).
7. All verdict lines code-generated (grep for hand-typed `VIABLE=` returns nothing).
8. Worklog appended; run_id + cuts hash stamped.

## 8. Banned behaviors (each maps to a real Phase-1 failure)
1. Selecting/recommending/freezing any option without the owner's explicit pick.
2. Tuning thresholds beyond §2.1 because results look weak (p-hacking); a negative grid is a delivered finding.
3. Re-implementing row logic or stats outside the central modules; **copying the banned BH** (§0).
4. Hand-typing numbers into documents.
5. Touching the reserved window, re-firing E-VAL, editing frozen artifacts.
6. Silent filters in copied function bodies; ambiguous names (BASE).
7. Inheriting another asset's derived numbers.
8. Assuming funding away / hiding costs / reporting only the favorable cost config.
9. Dropping failing cells, NaNs, or low-n rows from the menu.
10. Dismissing numeric anomalies without arithmetic proof.
11. Mixing another asset's or the pre-Phase-1 repo's numbers into this asset's deliverables.
12. Interpolating data or fabricating values to cover gaps.
13. **Running the forward "sanity" window and then E-VALing on a frontier picked from it** (leak). The forward window (if used at all) is owner-level context ONLY; it must not feed the E-VAL cell selection.

## 9. Edge cases & honest failure
- All-negative TRAIN grid: deliver the menu showing it; "no cell passes; retire asset or order a changed ladder". Do NOT iterate silently.
- Code bug mid-run: fix, re-run affected TRAIN stages (TRAIN is free), disclose in worklog. NEVER re-run E-VAL for any reason.
- Identity/fingerprint mismatch at freeze: abort, report, await owner.
- Zero-trade cells: NaN metrics, low-n flag, delivered as-is.
- Funding missing: check UNAVAILABLE; nets flagged "funding unpriced"; owner informed.
- E-VAL anomaly (trigger-rate ratio > 2×): first-class finding with TRAIN baseline cited.

## 10. Out of scope (owner-directed later passes, never started autonomously)
TP-multiple optimization · portfolio/correlation · regime-gated variants · cross-asset comparison · ML · live/paper trading · any change to §2.1 constants.

---

**Execution epitaph:** the owner sets the concept and the rules; every number is derived from this asset's
own data via the one canonical stats module; the data presents every option; the owner alone decides;
validation fires once and honestly; failure kills cleanly; the agent reports and stops.
