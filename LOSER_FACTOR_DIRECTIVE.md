# LOSER-FACTOR STUDY — BINDING AGENT DIRECTIVE

**Codename:** LOSERFAC. **Pass type:** TRAIN measurement only.  
**This file is the spec.** KEEPN measured *exits* on frozen entries. This pass does not touch exits. It asks one question about the **same baseline trades**:

> Among trades that already lost, is there a pre-entry feature that is common in losers **and uncommon in winners**? If we drop trades with that feature, how many losers go away, and how many winners go with them?

**Agent: read this document end-to-end before writing code. Execute §8. Stop.**

---

## 0. What the owner means (do not invent a different question)

A factor that appears in losing trades is **useless** if it appears in winning trades at the same rate.

Example the owner already gave: some winners had a red event candle, some losers had a red event candle. That is a *shared* factor. Dropping “event is red” then deletes winners and losers in the same proportion and **win rate does not move**.

The only useful factor is a **discriminant**:

```
P(feature | loser)  ≫  P(feature | winner)
```

Equivalently, after dropping trades with the feature:

- a large share of **losers** disappear
- a **smaller** share of **winners** disappear

The owner said: even cutting losers by ~50% is progress — **provided** winners are not cut at the same rate. You will measure both. You will not decide.

You do **not** look at losers in isolation and then “check winners later” as a story. Every feature is scored on losers **and** winners in the **same table**, same sample.

---

## 1. Frozen universe (same as KEEPN / Exit Study I)

```
E1 = (SOLUSDT, 30m, W2_NODIP)   n = 6420
E2 = (BTCUSDT, 30m, W1_NODIP)   n = 6101
E3 = (ETHUSDT, 1h,  W2_NODIP)   n = 2215
E4 = (SOLUSDT, 4h,  W3_NODIP)   n = 1470
```

Load by name via `src/lib/row_specs.py` (`legacy=False`). Color-agnostic. NODIP. TRAIN only (`lib.time_gates.filter_window(..., "TRAIN")`). Raw files via `lib.paths.RAW_DIR`.

**Baseline trade (do not change):** market next-bar open, TP = `body_top + 1.5 * wick_gap`, no price stop, 4-day time stop `K_HORIZON = {30m:192, 1h:96, 4h:24}`, cost **15 bps** flat. Reuse `measure()` from `V2/scripts/exit_anatomy.py` and the same gross/net construction as KEEPN baseline (`keepn_study.py::base_gross` / `metrics_from_gross` if present; otherwise copy that logic, do not invent a third simulator).

**Identity gate — abort the whole pass on mismatch:**

| row | n | baseline net @15bps | baseline win% |
|-----|---|---------------------|---------------|
| E1 | 6420 | 20.76 | 90.6 |
| E2 | 6101 | 10.26 | 91.1 |
| E3 | 2215 | 20.42 | 86.8 |
| E4 | 1470 | 48.72 | 79.0 |

Tolerances: n exact; net ±0.05 bps; win ±0.15 pp. Max entry < 2025-01-01. Reserved window 2025-07-01 → 2026-06-30 dark.

If KEEPN already reproduced these, you still re-assert them in this script. Do not skip the gate.

---

## 2. Outcome labels (locked)

On the baseline path, per trade:

- `hit_tp` = TP touched before time-stop K (same definition as `fill_bar < K` in `exit_anatomy.measure`)
- `loser_struct` = `not hit_tp`     ← **primary** “losing trade” (the fill failed)
- `winner_struct` = `hit_tp`
- `net` = gross bps − 15
- `loser_econ` = `net <= 0`         ← secondary, reported, not used to pick features

Primary rates, tests, and exclusion economics use **`loser_struct` / `winner_struct`**. Also store econ counts as extra columns so the owner can see fee-edge cases. Do not mix the two in one rate.

---

## 3. Feature list (closed — if it is not named here it does not run)

All features are known **at or before the signal bar close**. No look-ahead. No path features (MAE/MFE/time-to-fill are exits; forbidden here).

Load `volume` from the same raw OHLCV CSV (column name case-insensitive `volume` / `vol`). `src/lib/row_specs.build_features` does not return volume — **do not edit `row_specs.py`**. Join volume in the new script from the TRAIN-clipped bars aligned to the same index.

If `sig == 0` or fewer than 20 prior bars exist, that trade is **undefined** for features that need history. Drop it from that feature’s rate denominator only; still keep it in the row’s baseline n. Report `n_defined` per feature.

### 3.1 Color (event = signal bar `sig`; prev = `sig-1`)

`red = close < open`. Doji (`close == open`) is **not red** and **not green**. Do not fold dojis into red.

| id | definition |
|----|------------|
| `event_red` | signal bar red |
| `event_green` | signal bar green |
| `prev_red` | previous bar red |
| `prev_green` | previous bar green |
| `rr` | prev red **AND** event red |
| `rg` | prev red **AND** event green |
| `gr` | prev green **AND** event red |
| `gg` | prev green **AND** event green |

`event_green` / `prev_green` / `rg` / `gg` / `gr` are **controls**. The owner’s hypothesis is about red/red and red+volume. You still measure the other color pairs so “red/red is common in losers” can be compared to “green/green is also common in losers”.

### 3.2 Volume

`vol[i]` = volume of bar i.  
`rvol_event` = `vol[sig] / median(vol[sig-20 : sig])`  (20 bars **strictly before** the signal; not including sig).  
`rvol_prev`  = `vol[sig-1] / median(vol[sig-21 : sig-1])` when `sig >= 21`, else undefined.

Cuts are **pre-declared**. Do not search for a better threshold.

| id | definition |
|----|------------|
| `rvol_ge_1_3` | rvol_event ≥ 1.3 |
| `rvol_ge_2_0` | rvol_event ≥ 2.0 |
| `rvol_top_q` | rvol_event ≥ TRAIN **quintile-4 cut** of rvol_event on **this row’s defined trades** (top 20%). Cut is computed once on the row, applied to the same row. **Disclose: in-sample cut.** |
| `prev_rvol_ge_2_0` | rvol_prev ≥ 2.0 |
| `event_vol_gt_prev` | vol[sig] > vol[sig-1] |

### 3.3 Combinations the owner named (only these ANDs)

| id | definition |
|----|------------|
| `rr_and_rvol_ge_2_0` | `rr` AND `rvol_ge_2_0` |
| `event_red_and_rvol_ge_2_0` | `event_red` AND `rvol_ge_2_0` |
| `event_red_and_rvol_ge_1_3` | `event_red` AND `rvol_ge_1_3` |
| `event_red_and_rvol_top_q` | `event_red` AND `rvol_top_q` |

**No other AND/OR. No 3-way. No “or volume high or prev red”. No session, SMA, dip, ATR, funding, hour, weekday, body-size, wick-size.** Wick-size already defined the row.

### 3.4 Continuous snapshot (not a filter, no extra cuts)

For each row, write a small table of **rvol_event** percentiles among structural losers vs structural winners:

`P10, P25, P50, P75, P90` of rvol_event | loser vs winner.

This answers “is loser volume shifted?” without letting you pick a cut from the shift. The only volume **filters** remain §3.2 / §3.3.

---

## 4. What you compute per (row × feature)

Let L = structural losers with the feature defined, W = structural winners with the feature defined.

| name | formula |
|------|---------|
| `n_defined` | trades where the feature is defined |
| `n_L`, `n_W` | structural losers / winners among defined |
| `p_feat_L` | P(feature=True \| loser, defined) |
| `p_feat_W` | P(feature=True \| winner, defined) |
| `lift` | `p_feat_L / p_feat_W`  (if p_feat_W=0, write `inf` and skip the z-test) |
| `delta_pp` | `(p_feat_L - p_feat_W) * 100` |
| `p_two_prop` | two-proportion z-test of p_feat_L vs p_feat_W, two-sided (see §5) |

**Exclusion economics** (drop trades with feature=True; keep undefined trades — they were not flagged):

Let `drop` = defined AND feature=True. Remaining = not drop.

| name | formula |
|------|---------|
| `n_drop` | count drop |
| `n_keep` | n0 − n_drop |
| `n_keep_pct` | 100 * n_keep / n0 |
| `losers_dropped` | structural losers in drop |
| `winners_dropped` | structural winners in drop |
| `loser_cut_pct` | 100 * losers_dropped / n_L_row   (n_L_row = all structural losers on the row, including undefined) |
| `winner_cut_pct` | 100 * winners_dropped / n_W_row |
| `collateral` | `winner_cut_pct / loser_cut_pct`  (if loser_cut=0, write `nan`) |
| `wr_keep` | structural win% on remaining trades |
| `wr_delta_pp` | wr_keep − baseline win% |
| `net_keep` | mean net bps on remaining trades (15 bps cost, same as baseline) |
| `net_delta_bps` | net_keep − baseline net |
| `maxdd_keep` | 2% overlapping equity maxDD on remaining, chronological |
| `ci_lo_keep`, `ci_hi_keep` | bootstrap 2000, seed 42, on remaining net vector |

**Owner’s “50% loser cut” flag** (report only, do not promote):

`CUT50` = `loser_cut_pct >= 50` AND `winner_cut_pct <= 0.5 * loser_cut_pct`  
i.e. you removed at least half the losers and at most half as many winners (proportionally).  
If no feature hits CUT50, write `NONE`. That is a valid answer.

**Discriminant flag** (weaker, also report only):

`DISC` = two-proportion test BH-significant (§5) AND `lift >= 1.5` AND `loser_cut_pct >= 15`.

A feature may be DISC without CUT50. Neither flag is a freeze.

---

## 5. Tests and multiplicity

Two-proportion z-test, unpooled:

```
p1 = p_feat_L; n1 = n_L
p2 = p_feat_W; n2 = n_W
p  = (p1*n1 + p2*n2) / (n1+n2)
se = sqrt(p*(1-p)*(1/n1 + 1/n2))
z  = (p1-p2) / se
p_two_prop = 2 * (1 - Φ(|z|))
```

If n1 < 20 or n2 < 20 or se=0: p_two_prop = 1.0, do not claim significance.

**BH step-up, q=0.05, chained k*** — same implementation as KEEPN §3.6 (do **not** copy `m2_grid.py`). Family = all (row × feature) cells in §3.1–3.3 (not the percentile snapshot). Unit-check before use:

- `[0.01,0.02,0.03,0.04,0.05]` @ q=0.05 → all 5 rejected
- `[0.01,0.03,0.10,0.20,0.30]` @ q=0.05 → only the smallest 1 rejected

Do not merge into `union_ledger.json`.

Bootstrap on remaining-book net: B=2000, seed=42.

---

## 6. Hard prohibitions

Copy into the script header.

- Do not add features. Do not add thresholds. Do not add AND/OR beyond §3.3.
- Do not scan rvol for a “best” cut. Quintile-4 is the only data-dependent cut and it is pre-declared as top 20%.
- Do not use MAE, MFE, time-to-fill, checkpoint uPnL, or any post-entry path variable as a “factor”. Those are not known at entry.
- Do not change entry, TP, stop, K, cost, or stake.
- Do not drop DIP/W4/1D/ICP/session/regime/ATR/funding. This is not KEEPN and not a new universe.
- Do not fire E-VAL / E-LOCKBOX. Do not touch 2025-07-01 → 2026-06-30.
- Do not modify `FROZEN_CANDIDATE.md`, `META_VERDICT.md`, `config.yaml`, `src/lib/*`, KEEPN outputs.
- Do not pick a winner, freeze a filter, or write “recommended system”.
- Do not look at losers first, keep the “interesting” ones, and only then compute winner rates for those. **All features in §3 run on all rows.**
- Do not install packages. numpy / pandas / scipy only.

---

## 7. Outputs (only these)

Create:

- `V2/scripts/loser_factor.py` — the only new implementation file
- `tests/test_loser_factor_identity.py` — n + max-entry + BH unit checks (no need to re-test full PnL beyond calling baseline once)
- `V2/outputs/loser_factor.csv` — one row per (row × feature in §3.1–3.3)
- `V2/outputs/loser_factor_rvol_pct.csv` — the §3.4 percentile snapshot (8 lines: 4 rows × {loser,winner})
- `V2/outputs/loser_factor_deriv.txt` — identity gate, rvol top-q cut values per row, n_L / n_W per row
- `V2/LOSER_FACTOR.md` — generated **from the CSVs**, not hand-copied

CSV columns for `loser_factor.csv`, this order:

```
row,feature,family,n0,n_defined,n_L,n_W,
p_feat_L,p_feat_W,lift,delta_pp,p_two_prop,bh_sig,
n_drop,n_keep,n_keep_pct,
losers_dropped,winners_dropped,loser_cut_pct,winner_cut_pct,collateral,
wr_keep,wr_delta_pp,net_keep,net_delta_bps,maxdd_keep,ci_lo_keep,ci_hi_keep,
cut50,disc,notes
```

`family` ∈ {color, volume, combo}.  
Booleans `True`/`False`. No `np.float64` reprs. Rates in percent with 1 decimal for cut_pct / wr; probabilities `p_feat_*` as fractions with 4 decimals; lift 3 decimals; net 2 decimals.

**Expected row count:** 4 rows × (8 color + 5 volume + 4 combo) = **68**. If you have another number, you added or skipped something.

---

## 8. Markdown report — required headings, nothing else

`V2/LOSER_FACTOR.md`:

1. **Identity gate** — n / net / win vs §1, PASS/FAIL. Abort note if FAIL.
2. **Loser counts** — per row: n0, n_L_struct, n_W_struct, struct WR, n_L_econ, n_W_econ. One table.
3. **How to read a row** — paste these three sentences, verbatim:
   - `p_feat_L ≈ p_feat_W` (lift ≈ 1) means the factor is **common to both** — dropping it does not concentrate on losers.
   - `lift ≫ 1` and `winner_cut_pct ≪ loser_cut_pct` means the factor is **loser-concentrated**.
   - `CUT50` is the owner’s “~50% of losers, not the same share of winners” bar. Empty is allowed.
4. **Color table** — all color features, all rows (from CSV).
5. **Volume table** — all volume features, all rows.
6. **Combo table** — the four ANDs, all rows.
7. **rvol percentile snapshot** — from `loser_factor_rvol_pct.csv`.
8. **CUT50 index** — list every cell with `cut50=True`, else `NONE`.
9. **DISC index** — list every cell with `disc=True`, else `NONE`.
10. **BH** — family size, q, number rejected, list (row, feature, p). Union ledger not updated.
11. **Stop** — `AGENT STOPS. No freeze. No E-VAL. Owner evaluates.`

No “discussion”. No “I recommend dropping red/red”. No charts.

---

## 9. Execution order

1. Read this file. Read nothing else for ideas (not W4 atlas, not FINDINGS F9, not KEEPN flags). You may import `measure` / KEEPN baseline helpers as **code**.
2. Confirm raw CSVs include a volume column. If a file has no volume: abort that row with a one-line error; do not impute.
3. Write `V2/scripts/loser_factor.py` with §6 in the header.
4. Write `tests/test_loser_factor_identity.py`. Run it. On fail, stop.
5. Run `python V2/scripts/loser_factor.py`. Identity fail → short abort MD only, no fake CSV.
6. Confirm 68 CSV rows; `n_keep + n_drop == n0` per cell; `p_feat_L` in [0,1]; no feature id outside §3.
7. Write the three outputs + MD from the same run.
8. **Stop.**

---

## 10. Abort conditions

- identity n/net/win mismatch  
- any entry ≥ 2025-01-01  
- holdout leak  
- volume column missing  
- BH unit checks fail  
- a feature not in §3 appears, or a §3 feature is missing  
- you would need to edit `src/lib/*`

Do not relax tolerances.

---

## 11. What “done” means

Identity PASS, 68 feature rows, rvol percentile snapshot, CUT50/DISC lists (possibly NONE), agent stopped. Owner will evaluate whether any factor is actually loser-concentrated or merely common to both.
