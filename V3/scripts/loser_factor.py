# -*- coding: utf-8 -*-
# ============================================================================
# LOSER_FACTOR_DIRECTIVE.md  --  LOSERFAC  (TRAIN measurement only)
# Same frozen E1-E4 baseline trades as KEEPN / Exit Study I.
#
# Question (do NOT invent another): among trades that ALREADY LOST (structural
# losers = TP never hit), is there a PRE-ENTRY feature common in losers AND
# uncommon in winners? Measure discriminant. Do not decide. Do not drop signals.
#
# HARD PROHIBITIONS (§6) -- none of these were done:
#   - do not add features / thresholds / AND-OR beyond §3.3
#   - do not scan rvol for a "best" cut (quintile-4 = top 20% is the only
#     data-dependent cut and is pre-declared)
#   - do not use MAE/MFE/time-to-fill/checkpoint uPnL or any post-entry path
#     variable as a "factor"
#   - do not change entry/TP/stop/K/cost/stake
#   - do not drop DIP/W4/1D/ICP/session/regime/ATR/funding
#   - do not fire E-VAL / E-LOCKBOX; do not touch 2025-07-01 -> 2026-06-30
#   - do not modify FROZEN_CANDIDATE/META_VERDICT/config/src/lib/KEEPN outputs
#   - do not pick a winner / freeze a filter / write "recommended system"
#   - do not look at losers first then winners later; all §3 features run all rows
#   - do not install packages (numpy/pandas/scipy only)
# ============================================================================
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "V2" / "scripts"))
import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS
from exit_anatomy import measure, TF_HOURS, K_HORIZON   # reuse Phase A measure()

# Phase-1 frozen reference cells (E1-E4). The repeatable pipeline derives its grid
# per-asset via exit_anatomy.build_grid(); this frozen map only reproduces Phase-1.
ENTRY = {
    "E1": ("SOLUSDT", "30m", "W2_NODIP"),
    "E2": ("BTCUSDT", "30m", "W1_NODIP"),
    "E3": ("ETHUSDT", "1h",  "W2_NODIP"),
    "E4": ("SOLUSDT", "4h",  "W3_NODIP"),
}
from keepn_study import base_gross, metrics_from_gross, bh_reject  # reuse KEEPN baseline + BH

COST = 15.0
N_BOOT = 2000
SEED = 42
Q = 0.05

BSL = {
    "E1": dict(n=6420, net=20.76, win=90.6),
    "E2": dict(n=6101, net=10.26, win=91.1),
    "E3": dict(n=2215, net=20.42, win=86.8),
    "E4": dict(n=1470, net=48.72, win=79.0),
}


def setup_meas(symbol, tf, name):
    m = measure(symbol, tf, name)
    K = m["K"]; W = K + 2
    starts = np.clip(m["eb"], 0, len(m["L"]) - 1)
    m["idx"] = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(m["L"]) - 1)
    m["bt"] = m["O"][m["eb"]]
    m["O_sig"] = m["O"][m["sig"]]
    m["C_sig"] = m["C"][m["sig"]]
    m["wg"] = (m["Hh"][m["sig"]] - np.maximum(m["O_sig"], m["C_sig"]))
    m["tp"] = np.maximum(m["O_sig"], m["C_sig"]) + 1.5 * m["wg"]
    m["n"] = len(m["sig"])
    m["W"] = W
    m["tf_h"] = TF_HOURS[tf]
    # baseline fill (first bar high touches tp, else K)
    tp_hit0 = m["Hp"] >= m["tp"][:, None]
    m["fill_bar"] = np.where(tp_hit0.any(1), tp_hit0.argmax(1), K)
    m["hit_tp"] = m["fill_bar"] < K
    m["loser_struct"] = ~m["hit_tp"]
    # volume aligned to full bar index
    meta = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    raw = pd.read_csv(meta)
    low = {c.strip().strip('"').lower(): c for c in raw.columns}
    inv = {v: k for k, v in low.items()}
    raw = raw.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    raw = raw.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw = T.filter_window(raw, "TRAIN")
    # bars are loaded identically to measure() (same raw file, same filter_window, same
    # sort), so positional alignment is exact; m does not carry 'time' as a key.
    m["vol"] = raw["volume"].values.astype(float)
    return m


def two_prop_p(p1, n1, p2, n2):
    if n1 < 20 or n2 < 20:
        return 1.0
    p = (p1 * n1 + p2 * n2) / (n1 + n2)
    if p <= 0 or p >= 1:
        return 1.0
    se = np.sqrt(p * (1 - p) * (1.0 / n1 + 1.0 / n2))
    if se == 0:
        return 1.0
    z = (p1 - p2) / se
    return float(2 * (1 - norm.cdf(abs(z))))


def boot_ci(x, B=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    a = np.asarray(x, float)
    n = len(a)
    if n == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, n, size=(B, n))
    means = a[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# ---------------------------------------------------------------------------
# Feature computations. Each returns a boolean array aligned to trade index,
# plus a "defined" mask (False where feature is undefined -> excluded from rate
# denominator but the trade stays in row n0).
# ---------------------------------------------------------------------------
def color_features(m):
    red = m["C_sig"] < m["O_sig"]
    green = m["C_sig"] > m["O_sig"]   # doji (==) is neither
    O_prev = m["O"][m["sig"] - 1]
    C_prev = m["C"][m["sig"] - 1]
    prev_red = C_prev < O_prev
    prev_green = C_prev > O_prev
    feats = {
        "event_red": (red, np.ones(m["n"], bool)),
        "event_green": (green, np.ones(m["n"], bool)),
        "prev_red": (prev_red, m["sig"] >= 1),
        "prev_green": (prev_green, m["sig"] >= 1),
        "rr": (red & prev_red, m["sig"] >= 1),
        "rg": (red & prev_green, m["sig"] >= 1),
        "gr": (green & prev_red, m["sig"] >= 1),
        "gg": (green & prev_green, m["sig"] >= 1),
    }
    return feats


def vol_features(m):
    vol = m["vol"]
    sig = m["sig"]
    n = m["n"]
    rvol_event = np.full(n, np.nan)
    rvol_prev = np.full(n, np.nan)
    defd_ev = np.zeros(n, bool)
    defd_pv = np.zeros(n, bool)
    for i in range(n):
        s = int(sig[i])
        if s >= 20:
            window = vol[s - 20:s]          # strictly before sig (s-20..s-1)
            med = np.median(window)
            if med > 0:
                rvol_event[i] = vol[s] / med
                defd_ev[i] = True
        if s >= 21:
            window_p = vol[s - 21:s - 1]    # strictly before prev (s-21..s-2)
            medp = np.median(window_p)
            if medp > 0:
                rvol_prev[i] = vol[s - 1] / medp
                defd_pv[i] = True
    # rvol top-q cut (top 20%) on this row's defined rvol_event
    defined_rev = defd_ev
    if defined_rev.any():
        cut_q = float(np.nanquantile(rvol_event[defined_rev], 0.8))
    else:
        cut_q = np.nan
    feats = {
        "rvol_ge_1_3": (rvol_event >= 1.3, defd_ev),
        "rvol_ge_2_0": (rvol_event >= 2.0, defd_ev),
        "rvol_top_q": (rvol_event >= cut_q, defd_ev),
        "prev_rvol_ge_2_0": (rvol_prev >= 2.0, defd_pv),
        "event_vol_gt_prev": (vol[sig] > vol[sig - 1], sig >= 1),
    }
    return feats, (cut_q if defined_rev.any() else None), rvol_event


def combo_features(m, color, vol):
    rr = color["rr"][0]
    ev_red = color["event_red"][0]
    rvol_2 = vol["rvol_ge_2_0"][0]
    rvol_13 = vol["rvol_ge_1_3"][0]
    rvol_q = vol["rvol_top_q"][0]
    defd = vol["rvol_ge_2_0"][1] & color["rr"][1]
    defd_e = vol["rvol_ge_2_0"][1] & color["event_red"][1]
    defd_e13 = vol["rvol_ge_1_3"][1] & color["event_red"][1]
    defd_eq = vol["rvol_top_q"][1] & color["event_red"][1]
    feats = {
        "rr_and_rvol_ge_2_0": (rr & rvol_2, defd),
        "event_red_and_rvol_ge_2_0": (ev_red & rvol_2, defd_e),
        "event_red_and_rvol_ge_1_3": (ev_red & rvol_13, defd_e13),
        "event_red_and_rvol_top_q": (ev_red & rvol_q, defd_eq),
    }
    return feats


# ---------------------------------------------------------------------------
def main():
    rows_out = []
    ident_lines = []
    ident_rows = []
    deriv = []
    rvol_pct_rows = []
    loser_counts = {}
    bh_cells = []
    abort = False

    for tag, (sym, tf, nm) in ENTRY.items():
        bsl = BSL[tag]
        m = setup_meas(sym, tf, nm)
        n = m["n"]; n0 = bsl["n"]
        # identity gate
        base_g, base_hold = base_gross(m)
        bm = metrics_from_gross(base_g, base_hold)
        ok_n = (n == n0)
        ok_net = abs(bm["net"] - bsl["net"]) <= 0.05
        ok_win = abs(bm["win"] - bsl["win"]) <= 0.15
        max_entry = pd.to_datetime(m["entry_dates"]).max()
        ok_entry = max_entry < pd.Timestamp("2025-01-01", tz="UTC")
        ident_pass = ok_n and ok_net and ok_win and ok_entry
        ident_lines.append(f"{tag}: n={n}(exp{n0},{'OK' if ok_n else 'FAIL'}) "
                           f"net={bm['net']:.2f}(exp{bsl['net']},{'OK' if ok_net else 'FAIL'}) "
                           f"win={bm['win']:.1f}(exp{bsl['win']},{'OK' if ok_win else 'FAIL'}) "
                           f"maxentry={str(max_entry).replace('+00:00','')}(<2025-01-01:{'OK' if ok_entry else 'FAIL'}) -> "
                           f"{'PASS' if ident_pass else 'FAIL'}")
        ident_rows.append((tag, n, n0, bm["net"], bsl["net"], ok_n, bm["win"], bsl["win"], ok_win,
                           str(max_entry).replace("+00:00", ""), ok_entry, ident_pass))
        if not ident_pass:
            abort = True
            break

        net0 = bm["net"]; win0 = bm["win"]
        loser_struct = m["loser_struct"]; winner_struct = m["hit_tp"]
        n_L_row = int(loser_struct.sum())
        n_W_row = int(winner_struct.sum())
        # econ labels (extra columns)
        net = base_g - COST
        loser_econ = net <= 0
        winner_econ = net > 0
        deriv.append(f"{tag}: n0={n0} n_L_struct={n_L_row} n_W_struct={n_W_row} struct_WR={100*n_W_row/n0:.1f} "
                     f"n_L_econ={int(loser_econ.sum())} n_W_econ={int(winner_econ.sum())}")
        gross_keep_full = base_g
        net_keep_full = net

        color = color_features(m)
        vol, cut_q, rvol_event = vol_features(m)
        if cut_q is not None:
            deriv.append(f"{tag}: rvol_top_q cut (P80 rvol_event) = {cut_q:.3f} (in-sample)")
        combo = combo_features(m, color, vol)

        # §3.4 rvol percentile snapshot (struct loser vs winner) — raw rvol_event, defined
        rev_def = rvol_event.copy(); rev_def[~vol["rvol_ge_1_3"][1]] = np.nan
        perd = rev_def.copy(); perd[loser_struct] = np.nan  # keep only winners
        perw = rev_def.copy(); perw[winner_struct] = np.nan  # keep only losers
        for label, grp_vals in (("loser", perw), ("winner", perd)):
            vals = grp_vals
            if np.isfinite(vals).any():
                ps = np.nanpercentile(vals, [10, 25, 50, 75, 90])
            else:
                ps = [np.nan] * 5
            rvol_pct_rows.append((tag, label, *[round(float(x), 3) for x in ps]))
        # loser/econ counts for report
        loser_counts[tag] = dict(n0=n0, n_L=n_L_row, n_W=n_W_row,
                                 wr=round(100.0 * n_W_row / n0, 1),
                                 n_L_econ=int(loser_econ.sum()), n_W_econ=int(winner_econ.sum()))

        fam_features = [
            ("color", color),
            ("volume", vol),
            ("combo", combo),
        ]

        def emit(family, fname, feat_tuple):
            flag, defined = feat_tuple
            fl = flag.astype(bool)
            # trades with the feature, among defined, split by structural outcome
            fl_def = fl & defined
            L = fl_def & loser_struct
            W = fl_def & winner_struct
            n_def = int(defined.sum())
            n_L = int(L.sum())
            n_W = int(W.sum())
            # probabilities: P(feature | loser, defined) and P(feature | winner, defined)
            denom_L = int(loser_struct[defined].sum())
            denom_W = int(winner_struct[defined].sum())
            p_feat_L = (n_L / denom_L) if denom_L > 0 else 0.0
            p_feat_W = (n_W / denom_W) if denom_W > 0 else 0.0
            if p_feat_W > 0:
                lift = p_feat_L / p_feat_W
            else:
                lift = float("inf")
            delta_pp = (p_feat_L - p_feat_W) * 100
            p2 = two_prop_p(p_feat_L, denom_L, p_feat_W, denom_W)
            # exclusion economics
            drop = defined & fl
            n_drop = int(drop.sum())
            n_keep = n0 - n_drop
            losers_dropped = int((drop & loser_struct).sum())
            winners_dropped = int((drop & winner_struct).sum())
            loser_cut_pct = 100.0 * losers_dropped / n_L_row if n_L_row > 0 else 0.0
            winner_cut_pct = 100.0 * winners_dropped / n_W_row if n_W_row > 0 else 0.0
            collateral = (winner_cut_pct / loser_cut_pct) if loser_cut_pct > 0 else float("nan")
            keep_mask = ~drop
            wr_keep = float(winner_struct[keep_mask].mean() * 100) if n_keep > 0 else float("nan")
            wr_delta_pp = wr_keep - win0 if n_keep > 0 else float("nan")
            net_keep = float(net[keep_mask].mean()) if n_keep > 0 else float("nan")
            net_delta = net_keep - net0 if n_keep > 0 else float("nan")
            eq = pd.Series(np.cumprod(1 + 0.02 * (net[keep_mask] / 1e4))) if n_keep > 0 else pd.Series([1.0])
            dd = (eq - eq.cummax()) / eq.cummax()
            maxdd_keep = float(-dd.min() * 100) if n_keep > 0 else float("nan")
            ci_lo, ci_hi = boot_ci(net[keep_mask]) if n_keep > 0 else (float("nan"), float("nan"))
            cut50 = bool(loser_cut_pct >= 50 and winner_cut_pct <= 0.5 * loser_cut_pct)
            rows_out.append(dict(
                row=tag, feature=fname, family=family, n0=n0, n_defined=n_def,
                n_L=n_L, n_W=n_W,
                p_feat_L=round(p_feat_L, 4), p_feat_W=round(p_feat_W, 4),
                lift=(round(lift, 3) if np.isfinite(lift) else "inf"),
                delta_pp=round(delta_pp, 1), p_two_prop=round(p2, 6), bh_sig="",
                n_drop=n_drop, n_keep=n_keep, n_keep_pct=round(100.0 * n_keep / n0, 1),
                losers_dropped=losers_dropped, winners_dropped=winners_dropped,
                loser_cut_pct=round(loser_cut_pct, 1), winner_cut_pct=round(winner_cut_pct, 1),
                collateral=(round(collateral, 3) if np.isfinite(collateral) else "nan"),
                wr_keep=(round(wr_keep, 1) if np.isfinite(wr_keep) else ""),
                wr_delta_pp=(round(wr_delta_pp, 1) if np.isfinite(wr_delta_pp) else ""),
                net_keep=(round(net_keep, 2) if np.isfinite(net_keep) else ""),
                net_delta_bps=(round(net_delta, 2) if np.isfinite(net_delta) else ""),
                maxdd_keep=(round(maxdd_keep, 1) if np.isfinite(maxdd_keep) else ""),
                ci_lo_keep=(round(ci_lo, 2) if np.isfinite(ci_lo) else ""),
                ci_hi_keep=(round(ci_hi, 2) if np.isfinite(ci_hi) else ""),
                cut50=str(cut50), disc="", notes=""))
            bh_cells.append((tag, fname, p2))

        for family, feats in fam_features:
            for fname, fset in feats.items():
                emit(family, fname, fset)

    # identity gate
    allpass = (not abort) and all(r[11] for r in ident_rows)
    if abort:
        md = "# LOSER FACTOR STUDY (ABORTED)\n\n## Identity gate\n\n" + "\n".join(ident_lines) + \
             "\n\nAgent stopped: identity FAIL. No CSV written.\n"
        (P.V2_OUTPUTS.parent / "LOSER_FACTOR.md").write_text(md)
        print("ABORT: identity gate failed.")
        sys.exit(1)

    # DISC flag: BH-significant AND lift>=1.5 AND loser_cut_pct>=15
    pvals = [c[2] for c in bh_cells]
    rej = bh_reject(pvals, Q)
    for (tag, fname, _), r in zip(bh_cells, rej):
        for row in rows_out:
            if row["row"] == tag and row["feature"] == fname:
                row["bh_sig"] = str(bool(r))
                if r:
                    try:
                        lift = row["lift"] if isinstance(row["lift"], str) else float(row["lift"])
                    except Exception:
                        lift = float("inf")
                    disc = (np.isfinite(lift) and lift >= 1.5 and row["loser_cut_pct"] >= 15)
                    row["disc"] = str(bool(disc))
                else:
                    row["disc"] = "False"
                break
    rejected = [(c[0], c[1], c[2]) for c, r in zip(bh_cells, rej) if r]

    # ---- cast any np types ----
    for row in rows_out:
        for k, v in list(row.items()):
            if isinstance(v, (np.floating,)):
                row[k] = float(v)
            elif isinstance(v, (np.integer,)):
                row[k] = int(v)

    cols = ["row","feature","family","n0","n_defined","n_L","n_W",
            "p_feat_L","p_feat_W","lift","delta_pp","p_two_prop","bh_sig",
            "n_drop","n_keep","n_keep_pct","losers_dropped","winners_dropped",
            "loser_cut_pct","winner_cut_pct","collateral","wr_keep","wr_delta_pp",
            "net_keep","net_delta_bps","maxdd_keep","ci_lo_keep","ci_hi_keep","cut50","disc","notes"]
    df = pd.DataFrame(rows_out)[cols]
    df.to_csv(P.V2_OUTPUTS / "loser_factor.csv", index=False)

    # rvol percentile snapshot
    pct_df = pd.DataFrame(rvol_pct_rows, columns=["row","group","P10","P25","P50","P75","P90"])
    pct_df.to_csv(P.V2_OUTPUTS / "loser_factor_rvol_pct.csv", index=False)

    # deriv
    deriv.insert(0, "# IDENTITY GATE (§1)")
    for line in ident_lines:
        deriv.insert(1, line)
    deriv.append("")
    deriv.append(f"# BH (§5): family size={len(pvals)} q={Q} rejected={len(rejected)}")
    for (t, f, pv) in rejected:
        deriv.append(f"  REJECTED {t} {f} p={pv:.6g}")
    (P.V2_OUTPUTS / "loser_factor_deriv.txt").write_text("\n".join(deriv) + "\n")

    # report
    md = build_report(df, pct_df, ident_rows, ident_lines, rejected, bh_cells, loser_counts)
    (P.V2_OUTPUTS.parent / "LOSER_FACTOR.md").write_text(md)

    print(f"Wrote loser_factor.csv ({len(df)} rows), loser_factor_rvol_pct.csv, "
          f"loser_factor_deriv.txt, LOSER_FACTOR.md. BH rejected={len(rejected)}.")
    print("Identity gate: ALL PASS")


def build_report(df, pct_df, ident_rows, ident_lines, rejected, bh_cells, loser_counts):
    L = []
    L.append("# LOSER FACTOR STUDY — TRAIN MEASUREMENT (LOSERFAC)\n")
    L.append("> Among trades that already lost (structural losers = TP never hit), is there a pre-entry "
             "feature common in losers AND uncommon in winners? Measurement only. Owner evaluates.\n")

    # 1 identity
    L.append("## 1. Identity gate\n")
    L.append("| row | n | net @15bps | win% | max entry (UTC) | GATE |")
    L.append("|-----|---|-----------|-------|-----------------|------|")
    for (tag, n, n0, net, net_e, ok_n, win, win_e, ok_win, me, ok_me, pass_) in ident_rows:
        L.append(f"| {tag} | {n} (exp {n0}) | {net:.2f} (exp {net_e}) | {win:.1f} (exp {win_e}) "
                 f"| {me} | {'PASS' if pass_ else 'FAIL'} |")
    L.append(f"\n**Identity gate: {'ALL PASS' if all(r[11] for r in ident_rows) else 'FAIL'}.**\n")

    # 2 loser counts
    L.append("## 2. Loser counts\n")
    L.append("| row | n0 | n_L_struct | n_W_struct | struct WR% | n_L_econ | n_W_econ |")
    L.append("|-----|----|-----------|-----------|----------|---------|---------|")
    for tag in ("E1", "E2", "E3", "E4"):
        c = loser_counts[tag]
        L.append(f"| {tag} | {c['n0']} | {c['n_L']} | {c['n_W']} | {c['wr']} | "
                 f"{c['n_L_econ']} | {c['n_W_econ']} |")
    L.append("")

    # 3 how to read
    L.append("## 3. How to read a row\n")
    L.append("- `p_feat_L ≈ p_feat_W` (lift ≈ 1) means the factor is **common to both** — dropping it does not concentrate on losers.")
    L.append("- `lift ≫ 1` and `winner_cut_pct ≪ loser_cut_pct` means the factor is **loser-concentrated**.")
    L.append("- `CUT50` is the owner's \"~50% of losers, not the same share of winners\" bar. Empty is allowed.")
    L.append("")

    def table(title, fam):
        L.append(f"## {title}\n")
        L.append("| row | feature | n_def | p_feat_L | p_feat_W | lift | delta_pp | p2 | bh | "
                 "loser_cut% | winner_cut% | collateral | wr_keep | net_keep | CUT50 | DISC |")
        L.append("|-----|---------|-------|----------|----------|------|----------|----|----|"
                 "-----------|------------|-----------|---------|---------|------|------|")
        sub = df[df.family == fam]
        for _, r in sub.iterrows():
            L.append(f"| {r['row']} | {r['feature']} | {r['n_defined']} | {r['p_feat_L']} | {r['p_feat_W']} "
                     f"| {r['lift']} | {r['delta_pp']} | {r['p_two_prop']} | {r['bh_sig']} "
                     f"| {r['loser_cut_pct']} | {r['winner_cut_pct']} | {r['collateral']} | {r['wr_keep']} "
                     f"| {r['net_keep']} | {r['cut50']} | {r['disc']} |")
        L.append("")

    table("4. Color table", "color")
    table("5. Volume table", "volume")
    table("6. Combo table", "combo")

    # 7 rvol percentile snapshot
    L.append("## 7. rvol percentile snapshot\n")
    L.append("| row | group | P10 | P25 | P50 | P75 | P90 |")
    L.append("|-----|-------|-----|-----|-----|-----|-----|")
    for _, r in pct_df.iterrows():
        L.append(f"| {r['row']} | {r['group']} | {r['P10']} | {r['P25']} | {r['P50']} | {r['P75']} | {r['P90']} |")
    L.append("")

    # 8 CUT50 index
    L.append("## 8. CUT50 index\n")
    cut = df[df.cut50 == "True"]
    if len(cut) == 0:
        L.append("- NONE")
    else:
        for _, r in cut.iterrows():
            L.append(f"- {r['row']} {r['feature']} (loser_cut={r['loser_cut_pct']}%, winner_cut={r['winner_cut_pct']}%)")
    L.append("")

    # 9 DISC index
    L.append("## 9. DISC index\n")
    disc = df[df.disc == "True"]
    if len(disc) == 0:
        L.append("- NONE")
    else:
        for _, r in disc.iterrows():
            L.append(f"- {r['row']} {r['feature']} (lift={r['lift']}, loser_cut={r['loser_cut_pct']}%, bh={r['bh_sig']})")
    L.append("")

    # 10 BH
    L.append("## 10. Benjamini–Hochberg (within-study family, q=0.05)\n")
    L.append(f"- Family size (row × feature cells) = {len(bh_cells)}")
    L.append(f"- q = {Q}")
    L.append(f"- Rejected = {len(rejected)}")
    if rejected:
        L.append("- Rejected cells:")
        for (t, f, pv) in rejected:
            L.append(f"  - {t} {f} p={pv:.6g}")
    else:
        L.append("- NONE rejected")
    L.append("- Union ledger (union_ledger.json) was **not** updated by this pass.")
    L.append("")

    # 11 stop
    L.append("## 11. Stop\n")
    L.append("AGENT STOPS. No freeze. No E-VAL. Owner evaluates.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
