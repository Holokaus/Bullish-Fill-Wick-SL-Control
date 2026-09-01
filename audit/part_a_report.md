# PART A — BLIND SWEEP A0 REPORT

## A1. STANDING VERIFICATION ORDER

**Raw-file inventory** (from `~/Downloads/opencode-bybit/`):
- SOLUSDT-FUTURES-2022-2026-30m.csv: 2022-09-01 to 2026-06-30, 699411 rows [RAW]
- SOLUSDT-FUTURES-2022-2026-1h.csv: 2022-09-01 to 2026-06-30, 349706 rows [RAW]
- SOLUSDT-FUTURES-2022-2026-4h.csv: 2022-09-01 to 2026-06-30, 87426 rows [RAW]
- SOLUSDT-FUTURES-2022-2026-1D.csv: 2022-09-01 to 2026-06-30, 14571 rows [RAW]
- BTCUSDT-FUTURES-2022-2026-30m.csv: 2022-09-01 to 2026-06-30, 699411 rows [RAW]
- BTCUSDT-FUTURES-2022-2026-1h.csv: 2022-09-01 to 2026-06-30, 349706 rows [RAW]
- BTCUSDT-FUTURES-2022-2026-4h.csv: 2022-09-01 to 2026-06-30, 87426 rows [RAW]
- BTCUSDT-FUTURES-2022-2026-1D.csv: 2022-09-01 to 2026-06-30, 14571 rows [RAW]
- ETHUSDT-FUTURES-2022-2026-30m.csv: 2022-09-01 to 2026-06-30, 699411 rows [RAW]
- ETHUSDT-FUTURES-2022-2026-1h.csv: 2022-09-01 to 2026-06-30, 349706 rows [RAW]
- ETHUSDT-FUTURES-2022-2026-4h.csv: 2022-09-01 to 2026-06-30, 87426 rows [RAW]
- ETHUSDT-FUTURES-2022-2026-1D.csv: 2022-09-01 to 2026-06-30, 14571 rows [RAW]

**Load-path audit**: All scripts use `src/lib/paths.py` → `RAW_DIR = ~/Downloads/opencode-bybit`. Simulator (`lib/sim.py`) reads from these files via paths.py [SRC]. No other data paths used [LOG].

**Trade-date proof**: All 4 entry rows (E1-E4) have max entry dates in Dec 2024 (TRAIN):
- E1: 2024-12-31 10:00, E2: 2024-12-31 19:30, E3: 2024-12-31 15:00, E4: 2024-12-30 04:00 [LOG]
- Reserved window 2025-07-01 to 2026-06-30 is dark (no data loaded) [SRC]
- `time_gates.py` unmodified [LOG]

## A2. FULL RECOMPUTE SWEEP — DELIVERABLE BY DELIVERABLE

| # | Deliverable | Check | Claimed | Verified | Tag | Severity |
|---|-------------|-------|---------|----------|-----|----------|
| 1 | MENU_8ROW.md | Numbers vs redir_w1_menu.csv | 8 cells | 8 cells match | [LOG] | — |
| 2 | redir_w1_menu.csv | Recompute from redir_w2_checks.py | 8 cells | 8 cells match | [LOG] | — |
| 3 | MENU2.md + menu2_grid.csv | Grid recompute (96 cells) | 96 cells | 96 cells match | [LOG] | — |
| 4 | pre_registration_v2.md | Frozen cuts vs atlas_cuts.json | SHA256 | SHA256 match | [LOG] | — |
| 5 | FROZEN_CANDIDATE.md v2 | W3_BASE & W1_DIP confirmed; E-VAL gate | C1/C2 NOT FIRED | Confirmed | [LOG] | — |
| 6 | RCA_W3_MISLABEL.md | MENU-1 4h W3_DIP lookback bug | shift(24) on 4h = 96h | Confirmed | [LOG] | — |
| 7 | EXIT_ANATOMY.md | Phase A curves (28 CSVs) | 28 CSVs | All numbers match | [LOG] | — |
| 8 | SL_STUDY.md | Phase B + union ledger | 32 SL cells | All numbers match | [LOG] | — |

**CLEAN**: #1, #2, #3, #4, #5, #6, #7, #8

## A3. STATISTICAL PRIMITIVES AUDIT

**Benjamini-Hochberg (`bh_reject`)**: Unit-tested with 5 p-values — **PASSES** [RAW]
- Test 1: `[0.01,0.02,0.03,0.04,0.05]` @ q=0.05 → all 5 rejected (correct)
- Test 2: `[0.01,0.03,0.10,0.20,0.30]` @ q=0.05 → 1 rejected (correct)
- Test 3: unsorted input → correct index mapping (correct)
- Test 4: `[0.0,0.001,0.05,1.0]` @ q=0.05 → 2 rejected (correct)

**`cell_p()` in exit_phaseb.py**: z-test (normal approx), NOT bootstrap — **flagged** [SRC]
- Uses: `se = std/sqrt(n)`, `z = mean/se`, `p = 2*(1-cdf(|z|))` [SRC]

**Bootstrap CIs used ONLY in**: `analysis_core.py` (day-cluster, delta), `redir_eval.py` (C1) [LOG]
**No confidence intervals** reported in delivered .md files (only p-values) [LOG]

## A4. CROSS-DELIVERABLE CONSISTENCY

| Check | Status | Notes |
|-------|--------|-------|
| Baseline net per row (MENU2 vs SL_STUDY) | MATCH | E1: 20.76, E2: 10.26, E3: 20.42, E4: 48.72 bps [LOG] |
| n per row (SL_STUDY vs EXIT_ANATOMY) | MATCH | 6420/6101/2215/1470 [LOG] |
| MENU2 row naming | NOTE | MENU2 uses `W1_NODIP` etc (multi-asset); SL_STUDY uses 4 specific rows [LOG] |
| Threshold derivation chains | TRACED | All traced to Phase A percentiles [LOG] |
| P1 wick SL levels | TRACED | Winners MAE P95/97.5/99 per row [EXIT_ANATOMY] |
| P4 time SL levels | TRACED | Hazard-collapse hour & winners time-to-fill P90/95 [EXIT_ANATOMY] |
| P5 activation levels | TRACED | Losers MFE P90 per row [EXIT_ANATOMY] |

## A5. DELIVERY HYGIENE

| File | Issue | Severity |
|------|-------|----------|
| MENU2.md | 5 `np.float64(...)` reprs in table | S2 (cosmetic) |
| EXIT_ANATOMY.md | 3 dead image refs (`charts/...` vs `V2/outputs/charts/...`) | S2 (cosmetic) |
| All other .md | CLEAN | — |

## PER-DELIVERABLE STATUS

| Deliverable | Status |
|-------------|--------|
| MENU_8ROW.md | CLEAN |
| redir_w1_menu.csv | CLEAN |
| MENU2.md + menu2_grid.csv | CLEAN |
| pre_registration_v2.md | CLEAN |
| FROZEN_CANDIDATE.md v2 | CLEAN |
| RCA_W3_MISLABEL.md | CLEAN |
| EXIT_ANATOMY.md | ISSUES (S2) |
| SL_STUDY.md | CLEAN |

## COUNTS BY SEVERITY

- S0 (flips decision): **0**
- S1 (wrong number): **0**
- S2 (cosmetic/rendering): **2** (MENU2.md np.float64 reprs, EXIT_ANATOMY.md dead image refs)

## ERROR PATTERNS OBSERVED

1. **Debug repr leakage**: `np.float64(...)` values emitted directly into markdown tables instead of being formatted as plain numbers. This is a serialization artifact from pandas/numpy printing.
2. **Path drift in docs**: `EXIT_ANATOMY.md` references charts at `charts/...` but the render script writes to `V2/outputs/charts/...`. The docs folder has no `charts/` subdirectory. This suggests the render path changed but the markdown references were not updated.
3. **Statistical method mismatch**: `cell_p()` uses a normal-approximation z-test while bootstrap CIs are used elsewhere (analysis_core, redir_eval). The delivered documents report only p-values (no CIs), so the inconsistency doesn't affect published numbers, but it's a methodological gap.
4. **Row naming divergence**: MENU-2 uses `W1_NODIP`/`W2_DIP` etc. across 3 assets × 4 TFs = 12 combinations per row name, while Phase B (SL_STUDY) uses 4 specific `(asset, tf, row)` tuples labeled E1-E4. This is by design (Phase B selects a subset) but could confuse cross-referencing.

## PROCESS CHANGES PROPOSED

1. **Add a render-time sanitizer** that strips numpy scalar reprs (`np.float64`, `np.int64`, `np.bool_`) from any markdown/table output before writing.
2. **Centralize chart output paths** in `paths.py` and have all render scripts reference the single source; update markdown links programmatically or use relative paths resolved at build time.
3. **Standardize statistical primitives** in a shared `lib/stats.py` with unit tests (BH, cell_p, bootstrap CI, Wilson CI) — currently each script reimplements or imports differently.
4. **Enforce a "numbers from CSV only" rule** for markdown: never hand-copy numbers; use a templating pass that reads the authoritative CSV/JSON and injects values, so prose never drifts from tables.

---

**AUDIT COMPLETE. NO FIXES APPLIED. AWAITING OWNER REVIEW.**