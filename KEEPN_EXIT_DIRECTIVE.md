# KEEPN EXIT / SL / TP STUDY — BINDING AGENT DIRECTIVE

**Codename:** KEEPN (keep-n). **Pass type:** TRAIN measurement only.  
**Owner constraint (overrides every prior suggestion in this chat):** do **not** raise win-rate or PnL by throwing away trades. A ~70% cut in trade count is a failed solution even if net/trade looks better.  
**This file is the spec.** If anything in `META_VERDICT.md`, `SL_STUDY.md`, `FROZEN_CANDIDATE.md`, W5/W6/W7, or a previous chat review conflicts with this file, **this file wins for this pass only.**

**Agent: read this document end-to-end before writing a single line of code. Then execute exactly the work in §8. Then stop.**

---

## 0. One-sentence mission

On the **same frozen entries** already used in Exit Study I (E1–E4), measure whether any **exit / stop / TP / scale-out / limit-fill** change improves stop-loss control, win rate, and net PnL **without dropping signals**.

The data decides. You do not.

---

## 1. What you are not allowed to do

Copy this list into the header of the one new script as comments. If a step would violate any item, **do not do the step**.

### 1.1 Out of scope — previous-reviewer suggestions (CONFLICT REGISTER)

A prior review recommended cutting trades via filters. The owner rejected that class of solution. **Do not implement, “just try”, or “also report as a candidate” any of the following this pass:**

| ID | Suggestion | Why it is forbidden this pass |
|----|------------|-------------------------------|
| X1 | BTC-regime gate (trade only TREND_UP / VOL_EXPANSION) | Entry filter. Cuts a large fraction of trades. |
| X2 | Skip RANGE / TREND_DOWN | Same as X1. |
| X3 | Replace `wick ≥ N bps` with `wick/ATR` (vol-normalize the trigger) | Changes the signal. Changes n. New universe. Not this pass. |
| X4 | Quiet-volume filter / rvol gate | Entry filter. Cuts n. |
| X5 | Prior-bear / below-SMA / quality-score AND-gates | Entry filter. Cuts n. |
| X6 | Green-candle-only (drop red events) | Entry filter. Cuts n. |
| X7 | Session filter (skip Asia / keep US hours) | Entry filter. Cuts n. |
| X8 | Dip filter (24h or 4-day) | Entry filter. Cuts n. DIP rows already exist in MENU-2; do not add them here. |
| X9 | Switch the book to thin cells (W3_DIP, W4, 1D, ICP, etc.) | Solves frequency by abandoning it. |
| X10 | Funding-rate skip / flatten | Entry/hold filter. Also an assumption. Out of scope. |
| X11 | Concurrent-risk cap / change 2% stake as the “fix” | Sizing overlay, not an exit study. Do not retune stake. |
| X12 | LightGBM / ML / exhaustion classifier | §6 alpha. Not this pass. |
| X13 | Re-run W6 ABS/ATR/QMAE price-stop grid | Already 0/3420. Do not repeat. |
| X14 | Re-run Exit Study I P1 P95/P97.5/P99, P4 P90/P95/hazard, P5 P90 | Already in `V2/outputs/sl_study.csv`. Cite, do not recompute as new work. |
| X15 | Fire E-VAL or E-LOCKBOX | One-shot windows. Not this pass. |
| X16 | Touch the reserved window 2025-07-01 → 2026-06-30 | Dark. Fail closed. |
| X17 | Modify `results/FROZEN_CANDIDATE.md`, `META_VERDICT.md`, `config.yaml` candidate block, `docs/SYSTEM_SIGNED.md` | Freeze stays as-is. This pass does not promote. |
| X18 | Rebuild `union_ledger.json` / fix `m2_grid.py` BH / reissue MENU2 | Hygiene for another pass. Not this one. |
| X19 | New assets, new TFs, W4 rows, DIP rows, 5m/15m/1D | Universe is E1–E4 only. |
| X20 | L2 / order book / tick data | Kline OHLCV only. |
| X21 | Invent extra policy families, extra f values, extra checkpoints, extra trail distances | If it is not named in §5, it does not run. |
| X22 | Pick a winner, freeze a spec, write a “recommended system”, or interpret beyond the required MD sections | Owner evaluates. You measure. |
| X23 | “Helpful” extra charts, notebooks, dashboards, refactors of `src/lib/*`, package installs | No. |
| X24 | Assume a result. If a cell is empty, you still run it and write the number. | Data only. |

**Hard n rule**

- For every policy in families A–F: `n` **must equal** that row’s baseline `n`. If a policy drops even one signal, it is a **bug**, not a result. Abort that policy and fix it.
- Family G is the only family allowed to have `n_filled ≤ n`. See §5.7.

### 1.2 Do not touch

- `src/lib/sim.py`, `src/lib/row_specs.py`, `src/lib/time_gates.py`, `src/lib/paths.py` — import them. Do not edit them. If you think one is wrong, **stop and report**; do not patch.
- Any file under `results/`, `reports/`, `docs/`, `audit/`, `V2/PROTOCOL*.md`, `V2/MENU*.md`, `V2/SL_STUDY.md`, `V2/W5*.md`, `V2/W6*.md`.
- Atlas cuts, lockbox CSVs, event parquets, Track-1 scripts.

### 1.3 Do not add work

One new script, one identity test, three output files. That is the entire delivery. No second study. No “while I was there”.

---

## 2. Frozen universe (identity is a gate, not a suggestion)

### 2.1 Rows — exact, no substitutes

Reuse `ENTRY` from `V2/scripts/exit_anatomy.py`:

```
E1 = (SOLUSDT, 30m, W2_NODIP)
E2 = (BTCUSDT, 30m, W1_NODIP)
E3 = (ETHUSDT, 1h,  W2_NODIP)
E4 = (SOLUSDT, 4h,  W3_NODIP)
```

Load rows **by name** via `src/lib/row_specs.py` (`get_spec` + `select` + `build_features`). `legacy=False`. Color-agnostic. NODIP only.

**Assert before any policy runs** (abort the whole script on mismatch):

| row | n | max entry (UTC) | baseline net @15 bps | baseline win% | baseline maxDD% | baseline worst bps |
|-----|---|-----------------|----------------------|---------------|-----------------|--------------------|
| E1 | **6420** | ≤ 2024-12-31 10:00 | **20.76** | **90.6** | **22.1** | **−7516.4** |
| E2 | **6101** | ≤ 2024-12-31 19:30 | **10.26** | **91.1** | **4.4** | **−2134.6** |
| E3 | **2215** | ≤ 2024-12-31 15:00 | **20.42** | **86.8** | **3.8** | **−2671.2** |
| E4 | **1470** | ≤ 2024-12-30 04:00 | **48.72** | **79.0** | **7.5** | **−6857.1** |

Tolerances: `n` exact; net ±0.05 bps; win ±0.15 pp; maxDD ±0.15 pp; worst ±1.0 bp.

These numbers are `SL_STUDY.md` / `menu2_grid.csv` / `EXIT_ANATOMY.md`. If you cannot reproduce them, **you have the wrong path, wrong window, wrong cost, or wrong TP**. Stop. Do not invent a new baseline.

### 2.2 Baseline spec (do not change)

Identical to Exit Study I / MENU-2:

- Signal: row spec above, any color, NODIP.
- Entry: **market at next bar open** (`bt = open[eb]`, `eb = sig+1`).
- TP: `body_top + 1.5 * wick_gap` where `body_top = max(open[sig], close[sig])`, `wick_gap = high[sig] - body_top`.
- Price stop: **none**.
- Time stop: close of bar `K` if TP untouched. `K` = 4-day wall-clock:

```
K_HORIZON = {30m: 192, 1h: 96, 4h: 24}
TF_H      = {30m: 0.5, 1h: 1.0, 4h: 4.0}
```

- Cost headline: **flat 15.0 bps** subtracted from every trade (MENU-2 / SL_STUDY convention). Also compute net at 4.0 and 11.5 as extra columns, **not** extra rows.
- Stake for maxDD only: **2% of equity per trade**, overlapping, `eq = cumprod(1 + 0.02 * pnl_bps / 1e4)`. Do not change 2%.
- Window: **TRAIN only** via `lib.time_gates.filter_window(df, "TRAIN")`. Reserved window must be absent (the helper already asserts).
- Data: `lib.paths.RAW_DIR` / `{SYMBOL}-FUTURES-2022-2026-{tf}.csv`. No other path.

### 2.3 Trade-entry-date proof

Write into the report the min and max **entry** timestamp per row. All must be `< 2025-01-01`. If any entry is in EVAL, RESERVED, or LOCKBOX: abort.

---

## 3. Measurement rules (locked)

### 3.1 Simulator

Import `measure()` from `V2/scripts/exit_anatomy.py`. Do not reimplement path construction. Reuse the arrays it already returns (`bt`, `tp`, `wg`, `fill_bar`, `Hp`, `Lp`, `Cp`, `MAE`, `MFE`, `win`, `K`, `eb`, `sig`, …). If `measure()` does not expose a field you need, **add a local wrapper in the new script** that calls `measure()` and then indexes `H/L/C` the same way `exit_phaseb.py` does. Do not fork a third path engine.

### 3.2 Same-bar priority (do not mix)

| Stop type | Honest resolution (headline `net`) | Extra column |
|-----------|--------------------------------------|--------------|
| Intrabar **touch** stop (family A disaster SL) | **Pessimistic: SL first** if that bar’s low ≤ SL and high ≥ TP | `net_opt` = TP first |
| **Close-based** stop (family B) | **TP first**: a live TP fills on high; a close-stop cannot fire until the close | `net_pess` = if close is a stop bar, ignore TP that bar |
| Time stop / scale / TP-only | TP on high; else close at K. No SL/TP clash | `net_opt` = `net` |

Never average the two. Headline is the honest column above.

### 3.3 Win definition

`win = (pnl_net > 0)` after costs. For scale-out, `pnl_net` is the **combined** fill (see §5.4). Do not count a partial as a full win.

### 3.4 Bootstrap CI

On the vector of per-trade **headline** net bps: B = **2000**, seed = **42**, percentile 2.5 / 97.5. Report `ci_lo`, `ci_hi`. This is required. Do not skip because it is slow.

### 3.5 p-value

Two-sided z-test on the mean, same as `exit_phaseb.py::cell_p` (`se = std/sqrt(n)`, `p = 2*(1-Φ(|mean/se|))`). Report it. **Do not use it to drop rows.**

### 3.6 Benjamini–Hochberg (within this study only)

Family = every **new** policy cell this pass (not baselines, not copied SL_STUDY rows). q = 0.05.

**Correct step-up BH (mandatory).** Do **not** copy `V2/scripts/m2_grid.py` (broken: unsorted p vs sorted threshold). Do **not** copy `exit_phaseb.py::bh_reject` or `rebuild_ledger.py::bh_reject` (elementwise, no k* chaining).

Implement exactly:

```python
def bh_reject(pvals, q=0.05):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    p_sorted = p[order]
    thresh = (np.arange(1, m + 1) / m) * q
    below = p_sorted <= thresh
    rej = np.zeros(m, dtype=bool)
    if below.any():
        kstar = int(np.where(below)[0].max())  # largest k with p_(k) <= kq/m
        rej[order[:kstar + 1]] = True
    return rej
```

Unit-check before use (abort if fail):

- `p = [0.01, 0.02, 0.03, 0.04, 0.05]`, q=0.05 → all 5 rejected.
- `p = [0.01, 0.03, 0.10, 0.20, 0.30]`, q=0.05 → only the smallest 1 rejected.
- Unsorted input must map back to original indices.

Do **not** merge this family into `union_ledger.json`.

### 3.7 Costs

Headline net = gross bps − **15.0**.  
Also store `net_4` = gross − 4.0 and `net_11_5` = gross − 11.5. Same gross, different subtraction. No per-mechanic maker/taker split this pass (MENU-2 convention). Do not invent funding.

### 3.8 Derived parameters

Every threshold is computed **at runtime** from that row’s `measure()` arrays, then **checked** against Phase A CSVs if present (tolerance 0.02 wick units or 0.5 hours). On mismatch: abort and print both values.

Phase A files (read-only):

- `V2/outputs/exit_anatomy_MAE_E{1-4}_winner.csv`
- `V2/outputs/exit_anatomy_MFE_E{1-4}_winner.csv`
- `V2/outputs/exit_anatomy_MFE_E{1-4}_loser.csv`
- `V2/outputs/exit_anatomy_divergence_E{1-4}.csv`
- `V2/docs` is `docs/EXIT_ANATOMY.md` (repo root `docs/EXIT_ANATOMY.md`)

Write every derived number into `V2/outputs/keepn_deriv.txt` with the formula and the source array.

**Do not type thresholds into the script as literals** except the locked constants in §2.2 and the f-grid in §5.4.

---

## 4. Flags (report only — you do not promote)

Compute two boolean flags per policy. Put them in the CSV. Do **not** delete policies that fail. Do **not** write “recommended”.

Let `n0, win0, net0, dd0, worst0` be that row’s baseline.

**KEEPN_IMPROVE** (better or equal on n, win, net):

- families A–F: `n == n0`
- family G1: `n_filled / n0 >= 0.80` **and** mean net is the **all-signal** mean (unfilled = 0 bps after costs? **No** — see §5.7: all-signal mean uses unfilled = 0 **gross**, then still subtract 0 cost because no trade). G2: `n == n0`.
- `win >= win0 - 0.05` (percentage points)
- `net >= net0 - 0.05` (bps)

**KEEPN_DEFEND** (n kept, edge mostly kept, tail improved):

- n rule as above
- `net >= 0.80 * net0`
- (`maxdd <= 0.75 * dd0`) OR (`worst > worst0`)   # worst less negative

A policy may have 0, 1, or 2 flags. That is information, not a decision.

---

## 5. Policy families (closed list)

Run **every** policy below on **every** row E1–E4. No skipping because you “already know”. No extras.

Naming: `{family}_{short}` as in the tables. CSV `policy` column uses these exact strings.

### 5.1 Family A — disaster touch-SL (still enter every trade)

One policy.

| policy | SL price | derivation |
|--------|----------|------------|
| `A_disaster_P99_9` | `bt - L * wg` with `L = percentile(MAE_wick of baseline winners, 99.9)` | Phase A winner MAE P99.9. E1 file has 43.316; E4 file has 20.481. Recompute, then assert. |

Exit: first bar where `low <= SL`, else TP, else time-stop K. Headline = SL-first if same bar as TP.

This is **not** P1_P99 (already done). P99.9 was not in SL_STUDY. Do not also run P95/P97.5/P99.

### 5.2 Family B — close-based invalidation (re-open the dropped P3 as an *exit*, not a filter)

Stops evaluate on **bar close**, not on low. n does not change: you still entered.

| policy | flatten at close of first bar (before TP/time-stop) where |
|--------|----------------------------------------------------------|
| `B_close_below_siglow` | `close <= low[sig]` (signal candle low) |
| `B_close_below_entry` | `close <= bt` |
| `B_close_below_entry_1wick` | `close <= bt - wg` |

Exit price if the close-stop fires: **that bar’s close** (not the level).  
If TP high-touch happens on an earlier bar, TP wins.  
If TP high-touch and close-stop are the **same** bar: headline = TP-first (§3.2). Store `net_pess` too.

Do not require `P(TP|flag) < 0.5 * P(TP|no-flag)`. That rule is how P3 was dropped; this pass **measures PnL**, not that inequality.

### 5.3 Family C — state flatten at a checkpoint (still enter every trade)

At wall-clock hour `h` from entry, look at unrealized PnL in wick units  
`u = (close_at_bar(h) - bt) / wg`  
where `bar(h) = min(round(h / TF_H[tf]), K)`.

Tercile cuts = **that row’s** 1/3 and 2/3 quantiles of `u` at that checkpoint, on the same TRAIN trades (in-sample distribution; **disclose this in the MD**, do not pretend it is OOS).

If the trade is still open (TP not yet touched, time-stop not yet reached) **and** `u` is in tercile 1 (worst): flatten at **that bar’s close**.

| policy | h |
|--------|---|
| `C_flat_worst_6h` | 6 |
| `C_flat_worst_12h` | 12 |
| `C_flat_worst_24h` | 24 |

Do not flatten mid or best terciles. Do not add 48/72/96. Do not use a different state variable than `u` above.

Sanity: at each checkpoint, P(eventual baseline TP | tercile) must match `exit_anatomy_divergence_E*.csv` within 1.0 pp for the three terciles. If not, your checkpoint bar index is wrong — abort family C.

### 5.4 Family D — TP and scale-out (the win-rate vs PnL lever)

Full-position TP multiplier `f`, same 4-day time-stop, no price stop, same entries:

| policy | f | notes |
|--------|---|-------|
| `D_tp_1.00` | 1.00 | new |
| `D_tp_1.25` | 1.25 | new |
| `D_tp_1.50` | 1.50 | **must match baseline net** (±0.05). If not, TP code is wrong — abort. |
| `D_tp_2.00` | 2.00 | new |
| `D_tp_2.50` | 2.50 | new |

`tp = body_top + f * wg`. Do not add 0.75, 1.75, 3.0, or any other f.

Scale-out (always 50% / 50% of notional, same entry, no price stop):

| policy | first half | second half |
|--------|------------|-------------|
| `D_scale_1.0_1.5` | TP at 1.0×, else that half’s time-stop | TP at 1.5×, else time-stop |
| `D_scale_1.0_2.0` | 1.0× | 2.0× |
| `D_scale_1.0_MFEp50` | 1.0× | `f = percentile(MFE_wick of baseline winners, 50)` from `measure()` |

Combined pnl = `0.5 * pnl_half1 + 0.5 * pnl_half2` (each half already net of **half** the 15 bps? **No.** Charge **15 bps once per trade** on the combined gross, same as a single round-trip. Do not double-fee a scale-out. Gross combined = 0.5*gross1 + 0.5*gross2; net = combined_gross − 15.)

If half-1 hits 1.0× and half-2 later time-stops: that is one trade, one 15 bps, combined gross may still be positive.

Do not trail. Do not 30/70. Do not three targets.

### 5.5 Family E — shorter time-stop, derived (not the ones already in SL_STUDY)

SL_STUDY already has P4 P90 / P95 / hazard. **Do not rerun those.**

New:

| policy | K_hours | then K_bars = max(1, round(K_hours / TF_H[tf])) |
|--------|---------|--------------------------------------------------|
| `E_time_TTF_P50` | percentile(time-to-fill_hours of **baseline winners**, 50) | |
| `E_time_TTF_P75` | same, 75 | |

`time-to-fill_hours = fill_bar[win] * TF_H[tf]`. Same definition as `exit_phaseb.py`.

Exit: TP or close at `K_bars`, no price stop.

### 5.6 Family F — activation then breakeven (tighter activation than P5)

P5 used losers’ MFE **P90**. Do not rerun P5.

After activation, SL becomes **entry + 15 bps** (same as `apply_activation` in `exit_phaseb.py`). Until activation, no price stop. Then TP / BE-stop / time-stop K.

| policy | activation price |
|--------|------------------|
| `F_act_loserMFEp50` | `bt + A * wg`, `A = percentile(MFE_wick of baseline losers, 50)` |
| `F_act_1wick` | `bt + 1.0 * wg` |

Headline same-bar: if BE-stop and TP in the same bar after activation → SL-first (touch stop).

Do not grid trail distances. Do not chandelier. Do not ATR trail.

### 5.7 Family G — limit at body-bottom (only family that may change n)

`limit = min(open[sig], close[sig])`  # body bottom of the **signal** candle  
Fill on entry bar `eb` if `low[eb] <= limit`. Fill price = `limit`.

| policy | if unfilled on bar `eb` |
|--------|-------------------------|
| `G_limit_skip` | **no trade**. `n_filled` may drop. |
| `G_limit_mkt_fallback` | fill at `close[eb]` (always in). `n == n0`. |

TP / time-stop / no price stop unchanged (f=1.5, K=4-day). Path starts at `eb` in both cases (same as baseline). For G_limit_mkt_fallback the entry price is `close[eb]` not `open[eb]` — replay must use that `bt`.

**G_limit_skip reporting (mandatory, both means):**

- `n` = n_filled  
- `n_retention_pct` = 100 * n_filled / n0  
- `net` = mean net **over filled trades only**  
- `net_all_signals` = (sum of filled nets + 0 for each skip) / n0   # opportunity-cost mean  
- KEEPN_IMPROVE / KEEPN_DEFEND for G1 use **`net_all_signals`** vs `net0`, and require `n_retention_pct >= 80`.  
- If `n_retention_pct < 80`, flags are False even if filled-only net is huge. Still **keep the row** in the CSV.

Do not place the limit 20/30 bp below open. Do not use a fraction of the wick. Body-bottom only. Do not expire later than bar `eb`.

---

## 6. CSV schema (one file, one row per row×policy)

Write `V2/outputs/keepn_study.csv` with **exactly** these columns, in this order:

```
row,policy,family,n,n0,n_retention_pct,win,win0,win_delta_pp,
net,net0,net_delta_bps,net_4,net_11_5,net_opt,net_pess,net_all_signals,
monthly,maxdd,maxdd0,maxdd_delta_pp,med_hold_h,worst,worst0,worst_delta_bps,
pval,ci_lo,ci_hi,bh_sig,keepn_improve,keepn_defend,fill_rate,notes
```

Rules:

- `family` ∈ {A,B,C,D,E,F,G,BASE}.
- Include **one BASELINE row per E** (`policy=BASELINE`, `family=BASE`) as the first rows. These must match §2.1.
- Unused fields: empty (not `nan` printed as text). `net_all_signals` filled only for `G_limit_skip`; elsewhere copy `net`.
- `fill_rate` = 1.0 for A–F, G_limit_mkt_fallback, BASE; = n_filled/n0 for G_limit_skip.
- Booleans as `True`/`False`.
- Numbers: net/ci/delta 2 decimals; win 1 decimal; pct 1 decimal; pval 6 decimals; n integers.
- No `np.float64(...)` reprs in the file.

Also write `V2/outputs/keepn_deriv.txt`: plain text, one derived parameter per line, tagged with row and policy, plus the identity-gate pass/fail lines.

---

## 7. Markdown report — required sections, nothing else

Write `V2/KEEPN_STUDY.md`. **No executive recommendation. No “I think”. No cherry-picked story.**

Required headings, in order:

1. **Identity gate** — table of n / max-entry / baseline net/win/maxDD/worst vs §2.1, PASS/FAIL. If FAIL, the rest of the file is a short abort note and you stop.
2. **Prohibitions kept** — paste the X1–X24 list with a checkmark that each was not done. One line each.
3. **Derivation sheet** — every A/C/E/F/D_scale_MFEp50 threshold, formula, value, Phase A cross-check.
4. **Full results table** — all policies, all rows. Same numbers as the CSV (generate the table **from the CSV**, do not hand-copy).
5. **Flag index** — list every policy with `keepn_improve=True` and every policy with `keepn_defend=True`. If a list is empty, write `NONE`. Do not then propose a substitute.
6. **n-retention exceptions** — only G_limit_skip: n_filled, fill_rate, net_filled, net_all_signals. If fill_rate < 0.80, write `FAILS OWNER N-FLOOR`.
7. **BH** — family size, q, number rejected, list of rejected (row, policy, p). State that union ledger was **not** updated.
8. **Same-bar note** — one paragraph restating §3.2 and that headlines follow it.
9. **In-sample tercile disclosure** — one paragraph: family C cuts are TRAIN quantiles on the same trades.
10. **Stop** — the sentence: `AGENT STOPS. No freeze. No E-VAL. Owner evaluates.`

Do not add a “discussion”, “next steps”, “recommended spec”, or “what this means” section.

---

## 8. Execution order (do not reorder)

1. Read this file fully. Read `docs/EXIT_ANATOMY.md` §1–4 and `V2/SL_STUDY.md` §1 and §3 **only** for citation. Do not re-read W5/W6/W7 to “get ideas”.
2. Confirm `BULLISH_WICK_RAW_DIR` / `lib.paths.RAW_DIR` resolves and the four CSVs exist. If not, stop with the missing path.
3. Write `V2/scripts/keepn_study.py` (the only new implementation file). Header comments = §1.1 list.
4. Write `tests/test_keepn_identity.py` that: loads TRAIN E1–E4 via `row_specs` + `time_gates`; asserts n ∈ {6420,6101,2215,1470}; asserts max entry < 2025-01-01; asserts `bh_reject` unit checks in §3.6. No PnL tests beyond calling the script’s baseline function if you factor it.
5. Run the identity test. On fail: stop.
6. Run `python V2/scripts/keepn_study.py`. On identity-gate fail inside the script: stop, do not write a fake CSV.
7. Write `V2/outputs/keepn_study.csv`, `V2/outputs/keepn_deriv.txt`, `V2/KEEPN_STUDY.md` from the same run (the script should emit all three; do not hand-edit numbers into the MD).
8. Re-read the CSV: confirm 4 baseline rows match §2.1; confirm `n == n0` for every non-G1 row; confirm no policy name outside §5; confirm no `np.float64`.
9. **Stop.** Do not open EVAL. Do not plot. Do not freeze. Do not commit a candidate.

---

## 9. Files allowed to create or overwrite

**Create:**

- `V2/scripts/keepn_study.py`
- `tests/test_keepn_identity.py`
- `V2/outputs/keepn_study.csv`
- `V2/outputs/keepn_deriv.txt`
- `V2/KEEPN_STUDY.md`

**Overwrite:** only those five, and only if you re-run this same pass.

**Forbidden to create:** extra reports, charts, notebooks, “summary for owner”, protocol amendments, new row specs, copies of this directive inside `docs/`.

---

## 10. Counts you should end up with

Policies per row:

- BASE: 1  
- A: 1  
- B: 3  
- C: 3  
- D: 5 full-TP + 3 scale = 8  
- E: 2  
- F: 2  
- G: 2  

= **22 lines per row × 4 rows = 88 CSV rows**. If you have a different count, you added or skipped something — fix it before writing the MD.

---

## 11. Abort conditions (fail closed)

Stop the pass and write nothing except a short `V2/KEEPN_STUDY.md` identity-gate failure if:

- any E-row n mismatches §2.1  
- baseline net/win/maxDD/worst mismatch beyond tolerance  
- any entry timestamp ≥ 2025-01-01  
- holdout leak assertion fires  
- Phase A CSV cross-check on a derived percentile misses by more than the stated tolerance  
- BH unit checks fail  
- a family A–F policy produces `n != n0`  
- you would need to edit `src/lib/*` to proceed  

Do not “relax the tolerance”. Do not “use the new baseline”.

---

## 12. What “done” means

`V2/KEEPN_STUDY.md` exists, identity gate PASS, 88 CSV rows, flags filled, BH reported, agent stopped. The owner will bring that CSV/MD back for evaluation.

You are not asked whether the concept is tradeable. You are not asked to beat E-VAL. You are asked to measure the closed policy list on the frozen entries and leave the numbers unspun.
