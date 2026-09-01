# RCA — W3_BASE / W3_DIP MISLABEL (and the ret24 trap)

**Date:** 2026-08-28
**Author:** agent (root-cause analysis, binding per Directive 3 Task 1)
**Scope:** the freeze error where `FROZEN_CANDIDATE.md` v2 first froze the DIP variant (n=370)
mislabeled as `W3_BASE`, plus the deeper `ret24` definition bug found during this audit.

---

## 1. Chain of failure (the W3_BASE mislabel)

| # | link | what happened |
|---|---|---|
| a | **Vocabulary collision** | The menu's `W3_BASE` means "wick ≥ W3 (90 bps), **no dip filter**". But the W7 flagship candidate was named `C6_w9dip` ("base candidate") and *did* carry a dip filter. The word "base" meant two different things in two places — "no-dip menu row" vs "primary/reference candidate". The freeze step imported the W7 sense and conflated them. |
| b | **Duplicated logic** | `run_row` was re-implemented inside `redir_w2_checks.py` instead of imported from the menu code. The copied body carried `mask = (wbur>=thr) & (ret24_q<=1)` — the dip filter was **ambient** in the function, applied to every row regardless of name. The menu script's `run_row` took a `dip_on` kwarg; the checks script's did not. |
| c | **No identity test** | The menu CSV reported `W3_BASE n=1470`; the checks script reported `W3_BASE n=370`. The two disagreed **silently** — nothing asserted they matched. No automated check compared the freeze's row identity to the menu's. |
| d | **Similar outputs passed eyeball review** | Both rows showed ~79% win rate (79.0% vs 79.2%). The eye saw "looks like a wick row" and signed off; the n-gap and the dip-filter difference were not surfaced. |
| e | **No fingerprint at the freeze gate** | The freeze file was written with no pre-write assertion of `asset / TF / threshold / dip / n / trades-per-month` against a source of truth. A wrong row could be frozen with no tripwire. |

**Net:** a naming ambiguity + a copy-paste filter + no cross-check = the wrong row (dip variant) frozen under the no-dip name. Owner caught it at sign-off.

---

## 2. ret24 audit (finding — disclosed, not quietly fixed)

**Question:** is `ret24` a 24-hour return or a 24-bar return on 4h bars?

**Answer:** it is a **24-BAR** return = 24 × 4h = **96 hours (4 days)**. Every script computed:

```python
ret24 = C / pd.Series(C).shift(24).values - 1.0   # shift(24) on 4h bars = 4 days, NOT 24h
```

Affected files: `w4a_atlas.py`, `w4c_economics.py`, `w4d_inverted.py`, `w5_nosl_economics.py`,
`w6_stop_study.py`, `redir_w1_menu.py`, `redir_w2_checks.py`. All "dip" cuts (`ret24_q` quintiles in
`atlas_cuts.json`) were therefore computed on a **4-day** trailing return.

**Plain statement of finding:** all prior "DIP" rows (menu-1 W1_DIP…W4_DIP, and the W7 `C6_w9dip`
candidate) were actually **"4-day downtrend"** rows — "in a downtrend over the last 4 days" — not
"in a 24-hour dip" as the directive's vocabulary implied. This is a separate, deeper bug than the
mislabel. The edge-statistics themselves are still valid *for what they measured*; only the label
was wrong. The corrected MENU-2 uses a genuine 24-hour return (TF-appropriate lookback) and the
change is disclosed there.

**Why it slipped:** `ret24` = "24h return" was assumed from the name; nobody opened the code to
check `shift(24)` against the 4h bar size. Same "vocabulary = assumption" trap as (a).

---

## 3. Prevention implemented (Directive 3 Task 1.3)

1. **`src/lib/row_specs.py`** — single declarative registry: row name → exact spec dict
   (wick threshold in bps **or** TRAIN-frozen decile; dip on/off; dip *lookback in hours*, explicit).
   All scripts select rows **by name** from this registry. No script re-implements row logic.
2. **Row rename:** `W1..W4_NODIP` / `W1..W4_DIP`. The word "BASE" is **banned** vocabulary
   everywhere (files, code, docs).
3. **`tests/test_row_identity.py`** — golden tests on TRAIN: per row, trade count == frozen
   menu-1 CSV value; invariants `n(DIP) < n(NODIP)` at same threshold; `green+red == total`;
   spec fingerprint matches registry. (Note: reproduces menu-1's numbers *as computed*, i.e. with
   the 4-day ret24 lookback — that is the regression anchor; the corrected 24h definition is a
   MENU-2 change, not a silent retro-fix.)
4. **Freeze-gate fingerprint:** before any future FROZEN_CANDIDATE write, assert one line
   `asset / TF / threshold / dip / n / trades-per-month` matches the registry-menu row. Mismatch →
   abort and report.
5. **No-silent-filters rule:** every condition is an explicit named kwarg (e.g. `dip_on`,
   `dip_lookback_h`, `wick_thr`); no hardcoded quintile/decile/inequality buried in function bodies.

---

## 4. Residual risk

The `ret24` 4-day-vs-24h finding means every earlier "dip" conclusion (including the E-VAL regime
split that used a *correct* 24h BTC proxy) should be re-read with the 4-day definition in mind for
the SOL dip rows. E-VAL itself used an independent BTC 24h regime proxy, so its FAIL verdict stands
on its own; only the *SOL dip-row labeling* in menu-1 is affected, and menu-1 is superseded by MENU-2.
