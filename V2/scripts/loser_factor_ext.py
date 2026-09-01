# -*- coding: utf-8 -*-
# ============================================================================
# LOSER_FACTOR_EXT  --  EXTENDED pre-entry feature sweep (TRAIN measurement only)
# Sibling of LOSERFAC. Same frozen E1-E4 baseline, same two hard rules:
#   (1) pre-entry features only  (bar index <= signal bar; signal bar fully closed)
#   (2) never drop a single trade from the book (we only MEASURE exclusion cost)
#
# DIFFERENCE: LOSERFAC locked a small closed list (§3.3). This EXT study
# pre-declares a MUCH WIDER closed universe (every feature derivable from the
# available OHLCV, computed at signal bar or strictly before). The candidate
# set is fixed up front -- the data, not the author, picks the winner via the
# same BH / CUT50 / DISC machinery.
#
# HARD PROHIBITIONS (same spirit as LOSERFAC §6, none done):
#   - no post-entry path variable (MAE/MFE/time-to-fill/checkpoint uPnL)
#   - no change to entry/TP/stop/K/cost/stake
#   - no E-VAL / E-LOCKBOX; 2025-07-01 -> 2026-06-30 untouched
#   - no modification of FROZEN_CANDIDATE / META_VERDICT / config / src/lib / KEEPN outputs
#   - no picking a winner / freezing a filter / writing "recommended system"
#   - no packages beyond numpy/pandas/scipy
# Outputs are DISTINCTLY named (loser_factor_ext.*) to separate from LOSERFAC.
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
from exit_anatomy import measure, ENTRY, TF_H, K_HORIZON
from keepn_study import base_gross, metrics_from_gross, bh_reject

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
# 4h files available for HTF confluence (E4 is itself 4h -> would need daily, not present)
HTF_FILES = {
    "E1": ("SOLUSDT", "4h"),
    "E2": ("BTCUSDT", "4h"),
    "E3": ("BTCUSDT", "4h"),
}


def setup_meas_ext(symbol, tf, name):
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
    m["tf_h"] = TF_H[tf]
    tp_hit0 = m["Hp"] >= m["tp"][:, None]
    m["fill_bar"] = np.where(tp_hit0.any(1), tp_hit0.argmax(1), K)
    m["hit_tp"] = m["fill_bar"] < K
    m["loser_struct"] = ~m["hit_tp"]
    # load raw TRAIN bars (positional alignment with measure's feats)
    meta = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    raw = pd.read_csv(meta)
    low = {c.strip().strip('"').lower(): c for c in raw.columns}
    inv = {v: k for k, v in low.items()}
    raw = raw.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    raw = raw.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw = T.filter_window(raw, "TRAIN").reset_index(drop=True)
    m["vol"] = raw["volume"].values.astype(float)
    # ---- pre-entry indicator frame (computed on closed bars only) ----
    d = pd.DataFrame({
        "time": raw["time"].values, "o": raw["open"].values, "h": raw["high"].values,
        "l": raw["low"].values, "c": raw["close"].values, "v": raw["volume"].values.astype(float),
    })
    d["body"] = d["c"] - d["o"]
    d["rng"] = d["h"] - d["l"]
    d["body_abs"] = d["body"].abs()
    d["body_frac"] = np.where(d["rng"] > 0, d["body_abs"] / d["rng"], 0.0)
    d["uw"] = d["h"] - d[["o", "c"]].max(axis=1)
    d["lw"] = d[["o", "c"]].min(axis=1) - d["l"]
    d["lw_safe"] = d["lw"].clip(lower=1e-9)
    d["wick_ratio"] = np.where(d["lw"] > 0, d["uw"] / d["lw"], np.where(d["uw"] > 0, np.inf, 0.0))
    d["prev_uw"] = d["uw"].shift(1)
    d["prev_lw"] = d["lw"].shift(1)
    d["prev_body_frac"] = d["body_frac"].shift(1)
    d["prev_red"] = (d["c"].shift(1) < d["o"].shift(1))
    d["prev_green"] = (d["c"].shift(1) > d["o"].shift(1))
    d["inside"] = (d["h"] < d["h"].shift(1)) & (d["l"] > d["l"].shift(1))
    d["outside"] = (d["h"] > d["h"].shift(1)) & (d["l"] < d["l"].shift(1))
    d["sma20"] = d["c"].rolling(20).mean()
    d["sma50"] = d["c"].rolling(50).mean()
    tr = np.maximum.reduce([d["rng"].values,
                            (d["h"] - d["c"].shift(1)).abs().values,
                            (d["l"] - d["c"].shift(1)).abs().values])
    d["atr20"] = pd.Series(tr).rolling(20).mean().values
    d["vol_ma20"] = d["v"].rolling(20).mean()
    d["rvol"] = d["v"] / d["vol_ma20"]
    d["rng_rank60"] = d["rng"].rolling(60).rank(pct=True)
    d["vol_rank60"] = d["v"].rolling(60).rank(pct=True)
    ret = np.log(d["c"] / d["c"].shift(1))
    d["volstd60"] = pd.Series(ret).rolling(60).std()
    d["dist_ma20"] = (d["c"] - d["sma20"]) / d["sma20"]
    d["ma_bull"] = d["sma20"] > d["sma50"]
    d["rolling_max20"] = d["c"].rolling(20).max()
    d["pullback"] = (d["c"] - d["rolling_max20"]) / d["sma20"]   # <=0 below recent high
    d["at_recent_high"] = (d["rolling_max20"] - d["c"]) <= 0.2 * d["atr20"]
    d["vol_slope"] = d["v"] / d["v"].shift(5) - 1.0
    # streak + bars_since_high (small loop over T, acceptable)
    nT = len(d)
    sign = np.where(d["c"].values > d["o"].values, 1, np.where(d["c"].values < d["o"].values, -1, 0))
    red_streak = np.zeros(nT, dtype=int); green_streak = np.zeros(nT, dtype=int)
    for i in range(1, nT):
        if sign[i] == -1:
            red_streak[i] = red_streak[i - 1] + 1; green_streak[i] = 0
        elif sign[i] == 1:
            green_streak[i] = green_streak[i - 1] + 1; red_streak[i] = 0
        else:
            red_streak[i] = 0; green_streak[i] = 0
    d["red_streak"] = red_streak
    d["green_streak"] = green_streak
    # bars since 20-bar high
    bsh = np.zeros(nT, dtype=int)
    cmax = np.full(nT, np.nan)
    for i in range(nT):
        lo = max(0, i - 19)
        w = d["c"].values[lo:i + 1]
        cmax[i] = w.argmax() + lo
        bsh[i] = i - int(cmax[i])
    d["bars_since_high"] = bsh
    dt = pd.to_datetime(d["time"].values, unit="s", utc=True)
    d["hour"] = dt.hour.values
    d["dow"] = dt.dayofweek.values
    m["d"] = d
    # HTF where available
    if name in HTF_FILES:
        hsym, htf = HTF_FILES[name]
        m["htf"] = load_htf(hsym, htf, d["time"].values)
    else:
        m["htf"] = None
    return m


def load_htf(hsym, htf, sig_times):
    meta = P.RAW_DIR / f"{hsym}-FUTURES-2022-2026-{tf}.csv".replace("{tf}", htf)
    raw = pd.read_csv(meta)
    low = {c.strip().strip('"').lower(): c for c in raw.columns}
    inv = {v: k for k, v in low.items()}
    raw = raw.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    raw = raw.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    raw = T.filter_window(raw, "TRAIN").reset_index(drop=True)
    t = raw["time"].values.astype("int64")
    c = raw["close"].values.astype(float)
    o = raw["open"].values.astype(float)
    v = raw["volume"].values.astype(float)
    sma = pd.Series(c).rolling(20).mean().values
    # for each signal time, find the htf bar whose window contains it (start <= t < start+barsec)
    barsec = int(pd.Timedelta(hours=4).total_seconds())
    # searchsorted: largest htf start <= sig_time
    idx = np.searchsorted(t, sig_times.astype("int64"), side="right") - 1
    idx = np.clip(idx, 0, len(t) - 1)
    h = {
        "close": c[idx], "open": o[idx], "volume": v[idx], "sma20": sma[idx],
        "red": (c[idx] < o[idx]),
        "above_ma": (c[idx] > sma[idx]),
        "vol_rank": pd.Series(v).rolling(60).rank(pct=True).values[idx],
    }
    h["defined"] = idx >= 0
    return h


def two_prop_p(p1, n1, p2, n2):
    if n1 < 20 or n2 < 20 or p1 is None or p2 is None:
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
    a = np.asarray(x, float); n = len(a)
    if n == 0:
        return float("nan"), float("nan")
    idx = rng.integers(0, n, size=(B, n))
    means = a[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# ---------------------------------------------------------------------------
def base_features(m):
    """Return dict name -> (flag_bool array over trades, defined_bool over trades)."""
    d = m["d"]; sig = m["sig"].astype(int); n = m["n"]
    def at(col, minbar=0):
        arr = d[col].values if isinstance(col, str) else col
        vals = arr[sig]
        defined = (sig >= minbar) & np.isfinite(np.asarray(vals, float))
        return vals, defined
    feats = {}
    # ---- A color (8) ----
    o = d["o"].values[sig]; c = d["c"].values[sig]
    red = c < o; green = c > o
    prev_red = d["prev_red"].values[sig].astype(bool)
    prev_green = d["prev_green"].values[sig].astype(bool)
    feats["event_red"] = (red, sig >= 0)
    feats["event_green"] = (green, sig >= 0)
    feats["prev_red"] = (prev_red, sig >= 1)
    feats["prev_green"] = (prev_green, sig >= 1)
    feats["rr"] = (red & prev_red, sig >= 1)
    feats["rg"] = (red & prev_green, sig >= 1)
    feats["gr"] = (green & prev_red, sig >= 1)
    feats["gg"] = (green & prev_green, sig >= 1)
    # ---- B volume (5) ----
    rvol = d["rvol"].values[sig]
    vol = d["v"].values[sig]; vol_prev = d["v"].values[sig - 1]
    feats["rvol_ge_1_3"] = (rvol >= 1.3, sig >= 20)
    feats["rvol_ge_2_0"] = (rvol >= 2.0, sig >= 20)
    cutq = np.nanpercentile(rvol[sig >= 20], 0.8) if (sig >= 20).any() else np.nan
    feats["rvol_top_q"] = (rvol >= cutq, sig >= 20)
    feats["prev_rvol_ge_2_0"] = (vol_prev >= 2.0 * d["vol_ma20"].values[sig - 1], sig >= 21)
    feats["event_vol_gt_prev"] = (vol > vol_prev, sig >= 1)
    # ---- C candle shape (10) ----
    bf = d["body_frac"].values[sig]
    uw = d["uw"].values[sig]; lw = d["lw"].values[sig]
    prev_uw = d["prev_uw"].values[sig]; prev_lw = d["prev_lw"].values[sig]
    feats["body_fat"] = (bf >= 0.7, sig >= 0)
    feats["body_thin"] = (bf <= 0.3, sig >= 0)
    feats["doji"] = (bf < 0.1, sig >= 0)
    feats["long_upper_wick"] = (uw >= 2 * lw, sig >= 0)
    feats["long_lower_wick"] = (lw >= 2 * uw, sig >= 0)
    feats["prev_long_upper_wick"] = (prev_uw >= 2 * prev_lw, sig >= 1)
    feats["prev_long_lower_wick"] = (prev_lw >= 2 * prev_uw, sig >= 1)
    feats["inside_bar"] = (d["inside"].values[sig], sig >= 1)
    feats["outside_bar"] = (d["outside"].values[sig], sig >= 1)
    hi = d["h"].values[sig]; lo = d["l"].values[sig]
    feats["hammer_like"] = ((lw >= 2 * uw) & (np.maximum(o, c) >= (lo + 0.6 * (hi - lo))), sig >= 0)
    # ---- D volatility / range (6) ----
    rng = d["rng"].values[sig]; atr = d["atr20"].values[sig]
    rng_rank = d["rng_rank60"].values[sig]; vol_rank = d["vol_rank60"].values[sig]
    volstd_rank = d["volstd60"].rolling(60).rank(pct=True).values[sig] if False else np.full(n, np.nan)
    feats["range_expand"] = (rng >= 1.5 * atr, sig >= 20)
    feats["range_contract"] = (rng <= 0.5 * atr, sig >= 20)
    feats["range_pctile_high"] = (rng_rank >= 0.8, sig >= 60)
    feats["vol_regime_high"] = (volstd_rank >= 0.8, sig >= 60)
    feats["low_volume"] = (rvol < 0.5, sig >= 20)
    feats["volume_slope_up"] = (d["vol_slope"].values[sig] > 0.2, sig >= 5)
    # ---- E trend / context (11) ----
    sma20 = d["sma20"].values[sig]; sma50 = d["sma50"].values[sig]
    feats["above_ma20"] = (d["c"].values[sig] > sma20, sig >= 20)
    feats["below_ma20"] = (d["c"].values[sig] < sma20, sig >= 20)
    feats["ma_bull"] = (d["ma_bull"].values[sig], sig >= 50)
    feats["ma_bear"] = (~d["ma_bull"].values[sig], sig >= 50)
    feats["pullback_deep"] = (d["pullback"].values[sig] <= -1.0, sig >= 20)
    feats["at_recent_high"] = (d["at_recent_high"].values[sig], sig >= 20)
    feats["red_streak_ge2"] = (d["red_streak"].values[sig] >= 2, sig >= 1)
    feats["red_streak_ge3"] = (d["red_streak"].values[sig] >= 3, sig >= 1)
    feats["green_streak_ge2"] = (d["green_streak"].values[sig] >= 2, sig >= 1)
    feats["green_streak_ge3"] = (d["green_streak"].values[sig] >= 3, sig >= 1)
    feats["bars_since_high_ge10"] = (d["bars_since_high"].values[sig] >= 10, sig >= 20)
    # ---- F time (5) ----
    hour = d["hour"].values[sig]; dow = d["dow"].values[sig]
    feats["hour_0_6"] = ((hour >= 0) & (hour < 6), sig >= 0)
    feats["hour_6_12"] = ((hour >= 6) & (hour < 12), sig >= 0)
    feats["hour_12_18"] = ((hour >= 12) & (hour < 18), sig >= 0)
    feats["hour_18_24"] = ((hour >= 18) & (hour < 24), sig >= 0)
    feats["weekend"] = (dow >= 5, sig >= 0)
    # ---- G HTF (4, only rows with file) ----
    if m["htf"] is not None:
        h = m["htf"]
        hd = h["defined"]
        feats["htf_up"] = (h["above_ma"], hd)
        feats["htf_down"] = (~h["above_ma"], hd)
        feats["htf_red"] = (h["red"], hd)
        feats["htf_vol_high"] = (h["vol_rank"] >= 0.8, hd)
    return feats, cutq


def combo_features(m, base):
    feats = {}
    def both(a, b):
        return (base[a][0] & base[b][0], base[a][1] & base[b][1])
    feats["event_red_and_range_expand"] = both("event_red", "range_expand")
    feats["event_red_and_above_ma20"] = both("event_red", "above_ma20")
    feats["event_red_and_ma_bull"] = both("event_red", "ma_bull")
    feats["rvol_ge_2_and_ma_bull"] = both("rvol_ge_2_0", "ma_bull")
    feats["rvol_ge_2_and_range_expand"] = both("rvol_ge_2_0", "range_expand")
    feats["rvol_top_q_and_ma_bull"] = both("rvol_top_q", "ma_bull")
    feats["rg_and_low_volume"] = both("rg", "low_volume")
    feats["doji_and_high_volume"] = both("doji", "rvol_ge_2_0")
    feats["event_green_and_low_volume"] = both("event_green", "low_volume")
    if "htf_down" in base:
        feats["htf_down_and_rvol_ge_2"] = both("htf_down", "rvol_ge_2_0")
    return feats


# ---------------------------------------------------------------------------
def main():
    rows_out = []; ident_lines = []; ident_rows = []; deriv = []
    rvol_pct_rows = []; loser_counts = {}; bh_cells = []; abort = False

    for tag, (sym, tf, nm) in ENTRY.items():
        bsl = BSL[tag]
        m = setup_meas_ext(sym, tf, nm)
        n = int(m["n"]); n0 = bsl["n"]
        base_g, base_hold = base_gross(m)
        bm = metrics_from_gross(base_g, base_hold)
        ok_n = n == n0
        ok_net = abs(bm["net"] - bsl["net"]) <= 0.05
        ok_win = abs(bm["win"] - bsl["win"]) <= 0.15
        max_entry = pd.to_datetime(m["entry_dates"]).max()
        ok_entry = max_entry < pd.Timestamp("2025-01-01", tz="UTC")
        ident_pass = ok_n and ok_net and ok_win and ok_entry
        ident_lines.append(f"{tag}: n={n}(exp{n0},{'OK' if ok_n else 'FAIL'}) net={bm['net']:.2f}"
                           f"(exp{bsl['net']},{'OK' if ok_net else 'FAIL'}) win={bm['win']:.1f}"
                           f"(exp{bsl['win']},{'OK' if ok_win else 'FAIL'}) maxentry={str(max_entry).replace('+00:00','')}"
                           f"(<2025-01-01:{'OK' if ok_entry else 'FAIL'}) -> {'PASS' if ident_pass else 'FAIL'}")
        ident_rows.append((tag, n, n0, bm["net"], bsl["net"], ok_n, bm["win"], bsl["win"], ok_win,
                           str(max_entry).replace("+00:00", ""), ok_entry, ident_pass))
        if not ident_pass:
            abort = True; break
        net0 = bm["net"]; win0 = bm["win"]
        loser_struct = m["loser_struct"]; winner_struct = m["hit_tp"]
        n_L_row = int(loser_struct.sum()); n_W_row = int(winner_struct.sum())
        net = base_g - COST
        loser_econ = net <= 0; winner_econ = net > 0
        deriv.append(f"{tag}: n0={n0} n_L_struct={n_L_row} n_W_struct={n_W_row} "
                     f"struct_WR={100*n_W_row/n0:.1f} n_L_econ={int(loser_econ.sum())} n_W_econ={int(winner_econ.sum())}")
        loser_counts[tag] = dict(n0=n0, n_L=n_L_row, n_W=n_W_row, wr=round(100*n_W_row/n0, 1),
                                 n_L_econ=int(loser_econ.sum()), n_W_econ=int(winner_econ.sum()))

        base, cutq = base_features(m)
        if cutq is not None:
            deriv.append(f"{tag}: rvol_top_q cut (P80 rvol) = {cutq:.3f} (in-sample)")
        combo = combo_features(m, base)
        fam_features = [("color", {k: base[k] for k in ["event_red","event_green","prev_red","prev_green","rr","rg","gr","gg"]}),
                        ("volume", {k: base[k] for k in ["rvol_ge_1_3","rvol_ge_2_0","rvol_top_q","prev_rvol_ge_2_0","event_vol_gt_prev"]}),
                        ("shape", {k: base[k] for k in ["body_fat","body_thin","doji","long_upper_wick","long_lower_wick","prev_long_upper_wick","prev_long_lower_wick","inside_bar","outside_bar","hammer_like"]}),
                        ("volrange", {k: base[k] for k in ["range_expand","range_contract","range_pctile_high","vol_regime_high","low_volume","volume_slope_up"]}),
                        ("trend", {k: base[k] for k in ["above_ma20","below_ma20","ma_bull","ma_bear","pullback_deep","at_recent_high","red_streak_ge2","red_streak_ge3","green_streak_ge2","green_streak_ge3","bars_since_high_ge10"]}),
                        ("time", {k: base[k] for k in ["hour_0_6","hour_6_12","hour_12_18","hour_18_24","weekend"]}),
                        ("htf", {k: base[k] for k in base if k.startswith("htf_")}),
                        ("combo", combo)]

        def emit(family, fname, feat_tuple):
            flag, defined = feat_tuple
            fl = flag.astype(bool)
            if not defined.any():
                return
            fl_def = fl & defined
            L = fl_def & loser_struct
            W = fl_def & winner_struct
            n_def = int(defined.sum()); n_L = int(L.sum()); n_W = int(W.sum())
            denom_L = int(loser_struct[defined].sum()); denom_W = int(winner_struct[defined].sum())
            pL = (n_L / denom_L) if denom_L > 0 else 0.0
            pW = (n_W / denom_W) if denom_W > 0 else 0.0
            lift = (pL / pW) if pW > 0 else float("inf")
            delta_pp = (pL - pW) * 100
            p2 = two_prop_p(pL, denom_L, pW, denom_W)
            drop = defined & fl; n_drop = int(drop.sum()); n_keep = n0 - n_drop
            losers_dropped = int((drop & loser_struct).sum()); winners_dropped = int((drop & winner_struct).sum())
            lcut = 100.0 * losers_dropped / n_L_row if n_L_row > 0 else 0.0
            wcut = 100.0 * winners_dropped / n_W_row if n_W_row > 0 else 0.0
            coll = (wcut / lcut) if lcut > 0 else float("nan")
            keep_mask = ~drop
            wr_keep = float(winner_struct[keep_mask].mean() * 100) if n_keep > 0 else float("nan")
            wr_delta = wr_keep - win0 if n_keep > 0 else float("nan")
            net_keep = float(net[keep_mask].mean()) if n_keep > 0 else float("nan")
            net_delta = net_keep - net0 if n_keep > 0 else float("nan")
            eq = pd.Series(np.cumprod(1 + 0.02 * (net[keep_mask] / 1e4))) if n_keep > 0 else pd.Series([1.0])
            dd = (eq - eq.cummax()) / eq.cummax()
            maxdd = float(-dd.min() * 100) if n_keep > 0 else float("nan")
            ci_lo, ci_hi = boot_ci(net[keep_mask]) if n_keep > 0 else (float("nan"), float("nan"))
            cut50 = bool(lcut >= 50 and wcut <= 0.5 * lcut)
            rows_out.append(dict(
                row=tag, feature=fname, family=family, n0=n0, n_defined=n_def, n_L=n_L, n_W=n_W,
                p_feat_L=round(pL, 4), p_feat_W=round(pW, 4),
                lift=(round(lift, 3) if np.isfinite(lift) else "inf"),
                delta_pp=round(delta_pp, 1), p_two_prop=round(p2, 6), bh_sig="",
                n_drop=n_drop, n_keep=n_keep, n_keep_pct=round(100.0 * n_keep / n0, 1),
                losers_dropped=losers_dropped, winners_dropped=winners_dropped,
                loser_cut_pct=round(lcut, 1), winner_cut_pct=round(wcut, 1),
                collateral=(round(coll, 3) if np.isfinite(coll) else "nan"),
                wr_keep=(round(wr_keep, 1) if np.isfinite(wr_keep) else ""),
                wr_delta_pp=(round(wr_delta, 1) if np.isfinite(wr_delta) else ""),
                net_keep=(round(net_keep, 2) if np.isfinite(net_keep) else ""),
                net_delta_bps=(round(net_delta, 2) if np.isfinite(net_delta) else ""),
                maxdd_keep=(round(maxdd, 1) if np.isfinite(maxdd) else ""),
                ci_lo_keep=(round(ci_lo, 2) if np.isfinite(ci_lo) else ""),
                ci_hi_keep=(round(ci_hi, 2) if np.isfinite(ci_hi) else ""),
                cut50=str(cut50), disc="", notes=""))
            bh_cells.append((tag, fname, p2))

        for family, feats in fam_features:
            for fname, fset in feats.items():
                emit(family, fname, fset)

    if abort:
        print("ABORT: identity gate failed.")
        sys.exit(1)

    # BH (within-study family)
    pvals = [c[2] for c in bh_cells]
    rej = bh_reject(pvals, Q)
    rejected = []
    for (tag, fname, _), r in zip(bh_cells, rej):
        for row in rows_out:
            if row["row"] == tag and row["feature"] == fname:
                row["bh_sig"] = str(bool(r))
                if r:
                    try: lift = float(row["lift"])
                    except Exception: lift = float("inf")
                    row["disc"] = str(bool(np.isfinite(lift) and lift >= 1.5 and row["loser_cut_pct"] >= 15))
                    rejected.append((tag, fname, _))
                else:
                    row["disc"] = "False"
                break

    for row in rows_out:
        for k, v in list(row.items()):
            if isinstance(v, (np.floating,)):
                row[k] = float(v)
            elif isinstance(v, (np.integer,)):
                row[k] = int(v)

    cols = ["row","feature","family","n0","n_defined","n_L","n_W","p_feat_L","p_feat_W","lift",
            "delta_pp","p_two_prop","bh_sig","n_drop","n_keep","n_keep_pct","losers_dropped",
            "winners_dropped","loser_cut_pct","winner_cut_pct","collateral","wr_keep","wr_delta_pp",
            "net_keep","net_delta_bps","maxdd_keep","ci_lo_keep","ci_hi_keep","cut50","disc","notes"]
    df = pd.DataFrame(rows_out)[cols]
    df.to_csv(P.V2_OUTPUTS / "loser_factor_ext.csv", index=False)
    (P.V2_OUTPUTS / "loser_factor_ext_deriv.txt").write_text(
        "# IDENTITY GATE\n" + "\n".join(ident_lines) + "\n\n" + "\n".join(deriv) +
        f"\n\n# BH q={Q} rejected={len(rejected)}\n" +
        "\n".join(f"  {t} {f} p={pv:.6g}" for (t, f, pv) in rejected) + "\n")
    md = build_report_ext(df, ident_rows, ident_lines, rejected, loser_counts)
    (P.V2_OUTPUTS.parent / "LOSER_FACTOR_EXT.md").write_text(md)
    print(f"Wrote loser_factor_ext.csv ({len(df)} rows), loser_factor_ext_deriv.txt, "
          f"LOSER_FACTOR_EXT.md. BH rejected={len(rejected)}.")
    print("Identity gate: ALL PASS")


def build_report_ext(df, ident_rows, ident_lines, rejected, loser_counts):
    L = []
    L.append("# LOSER FACTOR EXTENDED SWEEP — TRAIN MEASUREMENT\n")
    L.append("> Pre-declared universe of EVERY pre-entry OHLCV feature. Same frozen E1–E4, same two "
             "hard rules (pre-entry only; never drop a trade). The data picks the winner via BH/CUT50/DISC.\n")
    L.append("## 1. Identity gate\n")
    L.append("| row | n | net @15bps | win% | max entry (UTC) | GATE |")
    L.append("|-----|---|-----------|-------|-----------------|------|")
    for (tag, n, n0, net, net_e, ok_n, win, win_e, ok_win, me, ok_me, pass_) in ident_rows:
        L.append(f"| {tag} | {n} (exp {n0}) | {net:.2f} (exp {net_e}) | {win:.1f} (exp {win_e}) "
                 f"| {me} | {'PASS' if pass_ else 'FAIL'} |")
    L.append(f"\n**Identity gate: {'ALL PASS' if all(r[11] for r in ident_rows) else 'FAIL'}.**\n")
    L.append("## 2. Loser counts\n")
    L.append("| row | n0 | n_L_struct | n_W_struct | struct WR% | n_L_econ | n_W_econ |")
    L.append("|-----|----|-----------|-----------|----------|---------|---------|")
    for tag in ("E1", "E2", "E3", "E4"):
        c = loser_counts[tag]
        L.append(f"| {tag} | {c['n0']} | {c['n_L']} | {c['n_W']} | {c['wr']} | {c['n_L_econ']} | {c['n_W_econ']} |")
    L.append("")
    L.append("## 3. How to read\n")
    L.append("- `p_feat_L ≈ p_feat_W` (lift ≈ 1) = shared factor (dropping it hurts winners as much as losers).")
    L.append("- `lift ≫ 1` + `winner_cut_pct ≪ loser_cut_pct` = loser-concentrated factor.")
    L.append("- `CUT50` = owner bar (~50% of losers, winners ≥ 2× that rate). Empty allowed.\n")
    for fam, title in [("color","4. Color"),("volume","5. Volume"),("shape","6. Candle shape"),
                       ("volrange","7. Volatility/range"),("trend","8. Trend/context"),
                       ("time","9. Time-of-day"),("htf","10. Higher-timeframe"),("combo","11. Combos")]:
        sub = df[df.family == fam]
        if len(sub) == 0:
            continue
        L.append(f"## {title}\n")
        L.append("| row | feature | n_def | pL | pW | lift | dpp | p2 | bh | "
                 "lcut% | wcut% | coll | wr_keep | net_keep | CUT50 | DISC |")
        L.append("|-----|---------|-------|----|----|------|-----|----|----|"
                 "------|-------|------|---------|---------|------|------|")
        for _, r in sub.iterrows():
            L.append(f"| {r['row']} | {r['feature']} | {r['n_defined']} | {r['p_feat_L']} | {r['p_feat_W']} "
                     f"| {r['lift']} | {r['delta_pp']} | {r['p_two_prop']} | {r['bh_sig']} "
                     f"| {r['loser_cut_pct']} | {r['winner_cut_pct']} | {r['collateral']} | {r['wr_keep']} "
                     f"| {r['net_keep']} | {r['cut50']} | {r['disc']} |")
        L.append("")
    L.append("## 12. DISC index (BH-significant + lift≥1.5 + loser_cut≥15)\n")
    disc = df[df.disc == "True"]
    if len(disc) == 0:
        L.append("- NONE")
    else:
        for _, r in disc.iterrows():
            L.append(f"- {r['row']} {r['feature']} (lift={r['lift']}, lcut={r['loser_cut_pct']}%, bh={r['bh_sig']})")
    L.append("")
    L.append("## 13. CUT50 index\n")
    cut = df[df.cut50 == "True"]
    L.append("- NONE" if len(cut) == 0 else "\n".join(
        f"- {r['row']} {r['feature']} (lcut={r['loser_cut_pct']}%, wcut={r['winner_cut_pct']}%)" for _, r in cut.iterrows()))
    L.append("")
    L.append("## 14. Stop\n")
    L.append("AGENT STOPS. No freeze. No E-VAL. Owner evaluates.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
