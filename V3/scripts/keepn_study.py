# -*- coding: utf-8 -*-
# ============================================================================
# KEEPN_EXIT_DIRECTIVE.md  --  KEEPN EXIT / SL / TP STUDY  (TRAIN measurement only)
# Single new implementation file. Header = forbidden-suggestion register (§1.1).
#
# PROHIBITIONS (do NOT implement, "just try", or "also report as candidate"):
#   X1  BTC-regime gate (trade only TREND_UP / VOL_EXPANSION)           -- entry filter, cuts n
#   X2  Skip RANGE / TREND_DOWN                                         -- entry filter, cuts n
#   X3  Replace wick>=N bps with wick/ATR (vol-normalize trigger)       -- changes signal/universe
#   X4  Quiet-volume filter / rvol gate                                 -- entry filter, cuts n
#   X5  Prior-bear / below-SMA / quality-score AND-gates                -- entry filter, cuts n
#   X6  Green-candle-only (drop red events)                             -- entry filter, cuts n
#   X7  Session filter (skip Asia / keep US hours)                      -- entry filter, cuts n
#   X8  Dip filter (24h or 4-day)                                       -- entry filter, cuts n
#   X9  Switch book to thin cells (W3_DIP,W4,1D,ICP...)                 -- abandons frequency
#   X10 Funding-rate skip / flatten                                     -- entry/hold filter, assumption
#   X11 Concurrent-risk cap / retune 2% stake as "fix"                  -- sizing overlay
#   X12 LightGBM / ML / exhaustion classifier                           -- §6 alpha, not this pass
#   X13 Re-run W6 ABS/ATR/QMAE price-stop grid                          -- already 0/3420
#   X14 Re-run Exit Study I P1/P4/P5 percentiles                        -- cite sl_study.csv only
#   X15 Fire E-VAL or E-LOCKBOX                                         -- one-shot windows, not this pass
#   X16 Touch reserved window 2025-07-01 -> 2026-06-30                  -- dark, fail closed
#   X17 Modify FROZEN_CANDIDATE/META_VERDICT/config/SYSTEM_SIGNED       -- freeze stays as-is
#   X18 Rebuild union_ledger.json / fix m2_grid BH / reissue MENU2      -- other pass hygiene
#   X19 New assets, new TFs, W4 rows, DIP rows, 5m/15m/1D               -- E1-E4 universe only
#   X20 L2 / order book / tick data                                     -- kline OHLCV only
#   X21 Invent extra policy families / f / checkpoints / trail distances-- only §5 names run
#   X22 Pick a winner / freeze a spec / write "recommended system"      -- owner evaluates
#   X23 Extra charts / notebooks / dashboards / refactor src/lib/*       -- none
#   X24 Assume a result; if a cell is empty, still run it and write it  -- data only
#
# HARD n RULE: every A-F policy n must equal baseline n. G is the only family
# allowed n_filled <= n (§5.7). Do NOT edit src/lib/* (import only).
# ============================================================================
import sys, json, traceback
from pathlib import Path
import numpy as np, pandas as pd

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
from scipy.stats import norm

COST = 15.0
COST_4 = 4.0
COST_11_5 = 11.5
N_BOOT = 2000
SEED = 42
Q = 0.05

# §2.1 frozen identity (exact). Tolerances: n exact; net ±0.05; win ±0.15;
# maxDD ±0.15; worst ±1.0 bp.
BSL = {
    "E1": dict(n=6420, max_entry="2024-12-31 10:00", net=20.76, win=90.6, maxdd=22.1, worst=-7516.4),
    "E2": dict(n=6101, max_entry="2024-12-31 19:30", net=10.26, win=91.1, maxdd=4.4,  worst=-2134.6),
    "E3": dict(n=2215, max_entry="2024-12-31 15:00", net=20.42, win=86.8, maxdd=3.8,  worst=-2671.2),
    "E4": dict(n=1470, max_entry="2024-12-30 04:00", net=48.72, win=79.0, maxdd=7.5,  worst=-6857.1),
}


# ---------------------------------------------------------------------------
# §3.6 correct BH step-up (do NOT copy m2_grid / exit_phaseb / rebuild_ledger)
# ---------------------------------------------------------------------------
def bh_reject(pvals, q=0.05):
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    p_sorted = p[order]
    thresh = (np.arange(1, m + 1) / m) * q
    below = p_sorted <= thresh
    rej = np.zeros(m, dtype=bool)
    if below.any():
        kstar = int(np.where(below)[0].max())
        rej[order[:kstar + 1]] = True
    return rej


def cell_p(pnl):
    """§3.5 two-sided z-test on mean (exit_phaseb.cell_p)."""
    se = pnl.std(ddof=1) / np.sqrt(len(pnl))
    if se == 0:
        return 1.0
    z = pnl.mean() / se
    return float(2 * (1 - norm.cdf(abs(z))))


def boot_ci(pnl, B=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(pnl, float)
    n = len(arr)
    means = np.empty(B)
    idx = rng.integers(0, n, size=(B, n))
    means = arr[idx].mean(axis=1)
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


# ---------------------------------------------------------------------------
# measure() wrapper: build windowed idx, bt, wg, tp exactly as exit_phaseb does.
# ---------------------------------------------------------------------------
def setup_meas(symbol, tf, name):
    m = measure(symbol, tf, name)
    K = m["K"]; W = K + 2
    starts = np.clip(m["eb"], 0, len(m["L"]) - 1)
    m["idx"] = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(m["L"]) - 1)
    m["bt"] = m["O"][m["eb"]]
    m["O_sig"] = m["O"][m["sig"]]
    m["C_sig"] = m["C"][m["sig"]]
    m["H_sig"] = m["Hh"][m["sig"]]
    m["L_sig"] = m["L"][m["sig"]]
    m["wg"] = (m["Hh"][m["sig"]] - np.maximum(m["O_sig"], m["C_sig"]))
    m["body_top"] = np.maximum(m["O_sig"], m["C_sig"])
    m["tp"] = m["body_top"] + 1.5 * m["wg"]
    m["n"] = len(m["sig"])
    m["W"] = W
    m["tf_h"] = TF_HOURS[tf]
    m["Hp"] = m["Hh"][m["idx"]]
    m["Lp"] = m["L"][m["idx"]]
    m["Cp"] = m["C"][m["idx"]]
    # baseline fill (first bar high touches tp, else K)
    tp_hit0 = m["Hp"] >= m["tp"][:, None]
    m["fill_bar"] = np.where(tp_hit0.any(1), tp_hit0.argmax(1), K)
    return m


def clipb(x, W):
    return np.clip(x, 0, W - 1)


def metrics_from_gross(gross, hold, cost=COST):
    """gross per-trade bps (pre-cost). Returns net/win/monthly/maxdd/med_hold/worst."""
    pnl = gross - cost
    n = len(pnl)
    win = float((pnl > 0).mean()) * 100
    mean = float(pnl.mean())
    eq = pd.Series(np.cumprod(1 + 0.02 * (pnl / 1e4)))
    dd = (eq - eq.cummax()) / eq.cummax()
    maxdd = float(-dd.min()) * 100
    worst = float(pnl.min())
    monthly = float(mean * n / 28.0)
    med_hold = float(np.nanmedian(hold)) if n else 0.0
    return dict(net=mean, win=win, monthly=monthly, maxdd=maxdd, med_hold=med_hold, worst=worst)


# ---------------------------------------------------------------------------
# POLICY ENGINES  (all reuse m arrays; never reimplement path construction)
# ---------------------------------------------------------------------------
def base_gross(m):
    bt, tp, K, W = m["bt"], m["tp"], m["K"], m["W"]
    fill = m["fill_bar"]
    exit_bar = np.minimum(fill, K)
    tp_hit = (m["Hp"][np.arange(m["n"]), clipb(exit_bar, W)] >= tp) & (fill < K)
    close_at = m["Cp"][np.arange(m["n"]), clipb(exit_bar, W)]
    ex = np.where(tp_hit, tp, close_at)
    gross = (ex - bt) / bt * 1e4
    hold = exit_bar * m["tf_h"]
    return gross, hold


def fam_A(m, L_units):
    """Disaster touch-SL (Family A). Headline = SL-first (pessimistic)."""
    bt, wg, tp, K, W = m["bt"], m["wg"], m["tp"], m["K"], m["W"]
    sl_price = bt - L_units * wg
    fill = m["fill_bar"]
    sl_trig = (m["Lp"] <= sl_price[:, None]) & (np.arange(W)[None, :] < fill[:, None])
    has_sl = sl_trig.any(1)
    first_sl = np.where(has_sl, sl_trig.argmax(1), K)
    sl_fired = has_sl & (first_sl < fill)
    clash = has_sl & (first_sl == fill) & (fill < K)   # same bar low<=SL & high>=TP
    ex_head = np.where(sl_fired | clash, sl_price,
              np.where(fill < K, tp, m["Cp"][np.arange(m["n"]), clipb(np.minimum(fill, K), W)]))
    ex_opt = np.where(sl_fired, sl_price,
             np.where(fill < K, tp, m["Cp"][np.arange(m["n"]), clipb(np.minimum(fill, K), W)]))
    gross_head = (ex_head - bt) / bt * 1e4
    gross_opt = (ex_opt - bt) / bt * 1e4
    exit_bar = np.where(sl_fired | clash, first_sl,
               np.where(fill < K, fill, K))
    hold = exit_bar * m["tf_h"]
    return gross_head, gross_opt, gross_head, hold   # (head, opt, pess=head)


def fam_B(m, level):
    """Close-based invalidation (Family B). Headline = TP-first; net_pess = close-first."""
    bt, tp, K, W = m["bt"], m["tp"], m["K"], m["W"]
    fill = m["fill_bar"]
    close_trig = (m["Cp"] <= level[:, None])
    has_close = close_trig.any(1)
    first_close = np.where(has_close, close_trig.argmax(1), W)   # sentinel beyond horizon
    tp_c = np.where(fill < K, fill, W)
    cl_c = first_close
    head = np.minimum.reduce([tp_c, cl_c, np.full(m["n"], K)])
    ex_head = np.where(head == tp_c, tp,
              np.where(head == cl_c, m["Cp"][np.arange(m["n"]), clipb(first_close, W)],
                       m["Cp"][np.arange(m["n"]), clipb(np.full(m["n"], K), W)]))
    # net_pess: close-first (ignore TP that bar)
    pess = np.minimum(cl_c, K)
    ex_pess = np.where(pess == cl_c, m["Cp"][np.arange(m["n"]), clipb(first_close, W)],
                      m["Cp"][np.arange(m["n"]), clipb(np.full(m["n"], K), W)])
    gross_head = (ex_head - bt) / bt * 1e4
    gross_pess = (ex_pess - bt) / bt * 1e4
    hold = head * m["tf_h"]
    return gross_head, gross_head, gross_pess, hold


def fam_C(m, h):
    """State flatten at checkpoint (Family C). Flatten worst tercile at checkpoint close."""
    bt, wg, K, W = m["bt"], m["wg"], m["K"], m["W"]
    b = min(int(round(h / m["tf_h"])), K)
    u = (m["Cp"][:, b] - bt) / wg
    q = np.nanquantile(u, [1/3, 2/3])
    terr = np.digitize(u, q) + 1   # 1 worst
    fill = m["fill_bar"]
    open_at = fill > b             # TP not yet touched at checkpoint
    flat = open_at & (terr == 1)
    base_g, base_hold = base_gross(m)
    gross_flat = (m["Cp"][:, b] - bt) / bt * 1e4
    gross = np.where(flat, gross_flat, base_g)
    exit_bar = np.where(flat, b, np.minimum(fill, K))
    hold = exit_bar * m["tf_h"]
    # sanity: P(eventual baseline TP | tercile) -> checked vs divergence CSV in main
    return gross, hold, (terr, fill, b)


def fam_D_full(m, f):
    """Full-position TP multiplier f (Family D)."""
    bt, K, W = m["bt"], m["K"], m["W"]
    tp2 = m["body_top"] + f * m["wg"]
    tp_hit = m["Hp"] >= tp2[:, None]
    fill = np.where(tp_hit.any(1), tp_hit.argmax(1), K)
    exit_bar = np.minimum(fill, K)
    hit = (m["Hp"][np.arange(m["n"]), clipb(exit_bar, W)] >= tp2) & (fill < K)
    close_at = m["Cp"][np.arange(m["n"]), clipb(exit_bar, W)]
    ex = np.where(hit, tp2, close_at)
    gross = (ex - bt) / bt * 1e4
    hold = exit_bar * m["tf_h"]
    return gross, hold


def fam_D_scale(m, f1, f2):
    """Scale-out 50/50 (Family D). Combined gross = 0.5*g1+0.5*g2; one 15 bps charge."""
    bt, K, W = m["bt"], m["K"], m["W"]
    g = []
    holds = []
    for fj in (f1, f2):
        tpj = m["body_top"] + fj * m["wg"]
        tp_hit = m["Hp"] >= tpj[:, None]
        fillj = np.where(tp_hit.any(1), tp_hit.argmax(1), K)
        exitj = np.minimum(fillj, K)
        hit = (m["Hp"][np.arange(m["n"]), clipb(exitj, W)] >= tpj) & (fillj < K)
        exj = np.where(hit, tpj, m["Cp"][np.arange(m["n"]), clipb(exitj, W)])
        g.append((exj - bt) / bt * 1e4)
        holds.append(exitj)
    comb = 0.5 * g[0] + 0.5 * g[1]
    hold = np.maximum.reduce(holds) * m["tf_h"]
    return comb, hold


def fam_E(m, K_hours):
    """Shorter time-stop derived from winners' time-to-fill (Family E)."""
    bt, tp, K, W = m["bt"], m["tp"], m["K"], m["W"]
    Kb = max(1, int(round(K_hours / m["tf_h"])))
    fill = m["fill_bar"]
    exit_bar = np.minimum(fill, Kb)
    hit = (m["Hp"][np.arange(m["n"]), clipb(exit_bar, W)] >= tp) & (fill < Kb)
    close_at = m["Cp"][np.arange(m["n"]), clipb(exit_bar, W)]
    ex = np.where(hit, tp, close_at)
    gross = (ex - bt) / bt * 1e4
    hold = exit_bar * m["tf_h"]
    return gross, hold, Kb


def fam_F(m, A_units):
    """Activation then breakeven (Family F). Headline = SL-first; net_opt = TP-first."""
    bt, wg, tp, K, W = m["bt"], m["wg"], m["tp"], m["K"], m["W"]
    fill = m["fill_bar"]
    act_price = bt + A_units * wg
    act_trig = (m["Hp"] >= act_price[:, None]) & (np.arange(W)[None, :] <= np.minimum(fill, K)[:, None])
    has_act = act_trig.any(1)
    first_act = np.where(has_act, act_trig.argmax(1), K + 5)
    be_sl = bt * (1 + 15e-4)
    post = np.arange(W)[None, :] > first_act[:, None]
    be_trig = (m["Lp"] <= be_sl[:, None]) & post & (np.arange(W)[None, :] < fill[:, None])
    has_be = be_trig.any(1)
    first_be = np.where(has_be, be_trig.argmax(1), K + 5)
    be_before = has_act & has_be & (first_be < fill)
    clash = has_act & has_be & (first_be == fill) & (fill < K)
    ex_head = np.where(be_before | clash, be_sl,
              np.where(fill < K, tp, m["Cp"][np.arange(m["n"]), clipb(np.minimum(fill, K), W)]))
    ex_opt = np.where(be_before, be_sl,
             np.where(fill < K, tp, m["Cp"][np.arange(m["n"]), clipb(np.minimum(fill, K), W)]))
    gross_head = (ex_head - bt) / bt * 1e4
    gross_opt = (ex_opt - bt) / bt * 1e4
    exit_bar = np.where(be_before | clash, first_be, np.where(fill < K, fill, K))
    hold = exit_bar * m["tf_h"]
    return gross_head, gross_opt, gross_head, hold


def fam_G(m, skip):
    """Limit at body-bottom (Family G). Only family that may change n."""
    bt, wg, tp, K, W = m["bt"], m["wg"], m["tp"], m["K"], m["W"]
    body_bottom = np.minimum(m["O_sig"], m["C_sig"])
    low_eb = m["L"][m["eb"]]
    filled = low_eb <= body_bottom
    close_eb = m["C"][m["eb"]]
    # entry price: limit if filled; fallback = close[eb] (always in)
    bt_new = np.where(filled, body_bottom, close_eb)
    fill = m["fill_bar"]
    exit_bar = np.minimum(fill, K)
    hit = (m["Hp"][np.arange(m["n"]), clipb(exit_bar, W)] >= tp) & (fill < K)
    ex = np.where(hit, tp, m["Cp"][np.arange(m["n"]), clipb(exit_bar, W)])
    gross_full = (ex - bt_new) / bt_new * 1e4
    hold = exit_bar * m["tf_h"]
    return gross_full, filled, hold


# ---------------------------------------------------------------------------
# PHASE A cross-checks (§3.8) + Family C tercile sanity (§5.3)
# ---------------------------------------------------------------------------
def pae_value(tag, outcome, col):
    fn = P.V2_OUTPUTS / f"exit_anatomy_{outcome}_{tag}_{'winner' if outcome=='MAE' else 'winner'}.csv"
    # MAE -> winner; MFE -> winner/loser
    return None


def read_phaseA(tag, kind, outcome):
    """kind in MAE/MFE; outcome in winner/loser. Returns dict percentile->value."""
    fn = P.V2_OUTPUTS / f"exit_anatomy_{kind}_{tag}_{outcome}.csv"
    if not fn.exists():
        return None
    df = pd.read_csv(fn)
    row = df.iloc[0]
    out = {}
    for c in df.columns:
        if c.startswith(f"{kind}_wick_P"):
            p = c.split("_P")[-1]
            out[p] = float(row[c])
    return out


def read_divergence(tag):
    fn = P.V2_OUTPUTS / f"exit_anatomy_divergence_{tag}.csv"
    if not fn.exists():
        return None
    return pd.read_csv(fn)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    deriv = []
    identity_lines = []
    ident_rows = []        # structured per-row identity (for MD table)
    rows_out = []
    bh_cells = []          # (row, policy, p) for new (non-baseline) cells
    abort = False

    for tag, (sym, tf, nm) in ENTRY.items():
        bsl = BSL[tag]
        m = setup_meas(sym, tf, nm)
        n = m["n"]
        n0 = bsl["n"]
        # ---- identity gate (abort whole pass on mismatch) ----
        max_entry = pd.to_datetime(m["entry_dates"]).max()
        max_entry_str = str(max_entry).replace("+00:00", "")
        ok_n = (n == n0)
        base_g, base_hold = base_gross(m)
        bm = metrics_from_gross(base_g, base_hold)
        ok_net = abs(bm["net"] - bsl["net"]) <= 0.05
        ok_win = abs(bm["win"] - bsl["win"]) <= 0.15
        ok_dd = abs(bm["maxdd"] - bsl["maxdd"]) <= 0.15
        ok_worst = abs(bm["worst"] - bsl["worst"]) <= 1.0
        ok_entry = max_entry < pd.Timestamp("2025-01-01", tz="UTC")
        ident_pass = ok_n and ok_net and ok_win and ok_dd and ok_worst and ok_entry
        identity_lines.append(
            f"{tag}: n={n}(exp{n0},{'OK' if ok_n else 'FAIL'}) "
            f"net={bm['net']:.2f}(exp{bsl['net']},{'OK' if ok_net else 'FAIL'}) "
            f"win={bm['win']:.1f}(exp{bsl['win']},{'OK' if ok_win else 'FAIL'}) "
            f"maxdd={bm['maxdd']:.1f}(exp{bsl['maxdd']},{'OK' if ok_dd else 'FAIL'}) "
            f"worst={bm['worst']:.1f}(exp{bsl['worst']},{'OK' if ok_worst else 'FAIL'}) "
            f"maxentry={max_entry_str}(<2025-01-01:{'OK' if ok_entry else 'FAIL'}) -> "
            f"{'PASS' if ident_pass else 'FAIL'}")
        ident_rows.append(dict(tag=tag, n=n, n_exp=n0, n_ok=ok_n,
                               max_entry=max_entry_str, max_entry_ok=ok_entry,
                               net=bm["net"], net_exp=bsl["net"], net_ok=ok_net,
                               win=bm["win"], win_exp=bsl["win"], win_ok=ok_win,
                               maxdd=bm["maxdd"], maxdd_exp=bsl["maxdd"], maxdd_ok=ok_dd,
                               worst=bm["worst"], worst_exp=bsl["worst"], worst_ok=ok_worst,
                               pass_=ident_pass))
        if not ident_pass:
            abort = True
            break

        # baseline anchors
        net0, win0, maxdd0, worst0 = bm["net"], bm["win"], bm["maxdd"], bm["worst"]

        # ---- BASELINE row ----
        ci_lo, ci_hi = boot_ci(base_g - COST)
        rows_out.append(dict(
            row=tag, policy="BASELINE", family="BASE",
            n=int(n), n0=int(n0), n_retention_pct="",
            win=round(bm["win"], 1), win0=round(win0, 1), win_delta_pp=round(bm["win"] - win0, 1),
            net=round(net0, 2), net0=round(net0, 2), net_delta_bps=0.0,
            net_4=round(float((base_g - COST_4).mean()), 2),
            net_11_5=round(float((base_g - COST_11_5).mean()), 2),
            net_opt=round(net0, 2), net_pess=round(net0, 2), net_all_signals=round(net0, 2),
            monthly=round(bm["monthly"], 1), maxdd=round(maxdd0, 1), maxdd0=round(maxdd0, 1),
            maxdd_delta_pp=0.0, med_hold_h=round(bm["med_hold"], 1),
            worst=round(worst0, 1), worst0=round(worst0, 1),
            worst_delta_bps=round(bm["worst"] - worst0, 1),
            pval=round(cell_p(base_g - COST), 6), ci_lo=round(ci_lo, 2), ci_hi=round(ci_hi, 2),
            bh_sig="False", keepn_improve="False", keepn_defend="False",
            fill_rate=1.0, notes="baseline reference (TP 1.5x / 4d time-stop / no SL)"))

        def emit(family, policy, gross, hold, gross_opt=None, gross_pess=None,
                 n_filled=None, filled_mask=None, bt_for_all=None, notes=""):
            """Emit one policy row; enforces n-rule and flags."""
            nonlocal abort
            gross_opt = gross if gross_opt is None else gross_opt
            gross_pess = gross if gross_pess is None else gross_pess
            if n_filled is None:
                # A-F, G_fallback: n must equal n0
                nn = len(gross)
                if nn != n0:
                    identity_lines.append(f"ABORT {tag} {policy}: n={nn} != n0={n0}")
                    abort = True
                    return
                nfill = n0
                ret_pct = ""
                net_all = None
                fill_rate = 1.0
                g_for_net = gross
            else:
                nn = int(n_filled)
                ret_pct = round(100.0 * nn / n0, 1)
                fill_rate = round(nn / n0, 4)
                g_for_net = gross   # gross over filled trades only
                # net_all_signals (G_skip): unfilled contribute 0
                net_all = float((gross - COST).sum() / n0)
            mm = metrics_from_gross(g_for_net, hold)
            net = mm["net"]
            p = cell_p(g_for_net - COST)
            lo, hi = boot_ci(g_for_net - COST)
            # flags (§4)
            if n_filled is None:
                keepn_improve = (mm["win"] >= win0 - 0.05) and (net >= net0 - 0.05)
            else:
                # G1 uses net_all_signals; require retention >= 80
                keepn_improve = (ret_pct >= 80.0) and (net_all >= net0 - 0.05) and (mm["win"] >= win0 - 0.05)
            if n_filled is None:
                keepn_defend = (net >= 0.80 * net0) and ((mm["maxdd"] <= 0.75 * maxdd0) or (mm["worst"] > worst0))
            else:
                keepn_defend = (ret_pct >= 80.0) and (net_all >= 0.80 * net0) and ((mm["maxdd"] <= 0.75 * maxdd0) or (mm["worst"] > worst0))
            rows_out.append(dict(
                row=tag, policy=policy, family=family,
                n=int(nn), n0=int(n0), n_retention_pct=ret_pct,
                win=round(mm["win"], 1), win0=round(win0, 1), win_delta_pp=round(mm["win"] - win0, 1),
                net=round(net, 2), net0=round(net0, 2), net_delta_bps=round(net - net0, 2),
                net_4=round(float((g_for_net - COST_4).mean()), 2),
                net_11_5=round(float((g_for_net - COST_11_5).mean()), 2),
                net_opt=round(float((gross_opt - COST).mean()), 2),
                net_pess=round(float((gross_pess - COST).mean()), 2),
                net_all_signals=(round(net_all, 2) if net_all is not None else round(net, 2)),
                monthly=round(mm["monthly"], 1), maxdd=round(mm["maxdd"], 1), maxdd0=round(maxdd0, 1),
                maxdd_delta_pp=round(mm["maxdd"] - maxdd0, 1), med_hold_h=round(mm["med_hold"], 1),
                worst=round(mm["worst"], 1), worst0=round(worst0, 1),
                worst_delta_bps=round(mm["worst"] - worst0, 1),
                pval=round(p, 6), ci_lo=round(lo, 2), ci_hi=round(hi, 2),
                bh_sig="", keepn_improve=str(bool(keepn_improve)), keepn_defend=str(bool(keepn_defend)),
                fill_rate=fill_rate, notes=notes))
            bh_cells.append((tag, policy, p))

        # ---- Family A: disaster touch-SL P99.9 (winners' MAE) ----
        L = float(np.nanpercentile(m["MAE"][m["win"]], 99.9))
        pa = read_phaseA(tag, "MAE", "winner")
        if pa is not None:
            expL = pa.get("99.9")
            if expL is not None:
                match = abs(L - expL) <= 0.02
                deriv.append(f"{tag} A_disaster_P99_9 L_wick=P99.9(MAE_winner)={L:.3f} "
                             f"(PhaseA MAE_winner_P99.9={expL:.3f}, match={match})")
                if not match:
                    identity_lines.append(f"ABORT {tag} A: PhaseA MAE P99.9 mismatch {L:.3f} vs {expL:.3f}")
                    abort = True
        g, go, gp, h = fam_A(m, L)
        emit("A", "A_disaster_P99_9", g, h, gross_opt=go, gross_pess=gp,
             notes=f"L_wick={L:.3f} (P99.9 winners' MAE)")

        # ---- Family B: close-based invalidation ----
        emit("B", "B_close_below_siglow", *fam_B(m, m["L_sig"]), notes="close<=low[sig]")
        emit("B", "B_close_below_entry", *fam_B(m, m["bt"]), notes="close<=bt")
        emit("B", "B_close_below_entry_1wick", *fam_B(m, m["bt"] - m["wg"]), notes="close<=bt-1wick")

        # ---- Family C: state flatten at checkpoint ----
        div = read_divergence(tag)
        for h in (6, 12, 24):
            g, hold, (terr, fill, bb) = fam_C(m, h)
            # sanity: P(baseline TP | tercile) vs divergence CSV within 1.0 pp
            if div is not None:
                sub = div[div.checkpoint_h == h]
                ok = True
                for tt in (1, 2, 3):
                    exp_pp = float(sub[sub.tercile == tt].P_tp_pct.iloc[0]) if (sub.tercile == tt).any() else None
                    if exp_pp is not None:
                        got = float(m["win"][terr == tt].mean() * 100)
                        if abs(got - exp_pp) > 1.0:
                            ok = False
                            identity_lines.append(f"ABORT {tag} C h={h} tercile{tt}: P(TP)={got:.1f} vs PhaseA {exp_pp:.1f}")
                if not ok:
                    abort = True
            emit("C", f"C_flat_worst_{h}h", g, hold, notes=f"flatten worst tercile @ {h}h checkpoint")

        # ---- Family D: TP multiplier + scale-out ----
        for f in (1.00, 1.25, 1.50, 2.00, 2.50):
            g, h = fam_D_full(m, f)
            if abs(f - 1.5) < 1e-9:
                chk = float((g - COST).mean())
                if abs(chk - net0) > 0.05:
                    identity_lines.append(f"ABORT {tag} D_tp_1.50 net={chk:.2f} != baseline {net0:.2f}")
                    abort = True
            emit("D", f"D_tp_{f:.2f}", g, h, notes=f"TP f={f:.2f}")
        # scale-out
        MFEp50 = float(np.nanpercentile(m["MFE"][m["win"]], 50))
        paM = read_phaseA(tag, "MFE", "winner")
        if paM is not None:
            expM = paM.get("50")
            if expM is not None:
                match = abs(MFEp50 - expM) <= 0.02
                deriv.append(f"{tag} D_scale_1.0_MFEp50 f2=P50(MFE_winner)={MFEp50:.3f} "
                             f"(PhaseA MFE_winner_P50={expM:.3f}, match={match})")
                if not match:
                    identity_lines.append(f"ABORT {tag} D scale MFEp50 mismatch {MFEp50:.3f} vs {expM:.3f}")
                    abort = True
        emit("D", "D_scale_1.0_1.5", *fam_D_scale(m, 1.0, 1.5), notes="scale 50/50 f1=1.0 f2=1.5")
        emit("D", "D_scale_1.0_2.0", *fam_D_scale(m, 1.0, 2.0), notes="scale 50/50 f1=1.0 f2=2.0")
        emit("D", "D_scale_1.0_MFEp50", *fam_D_scale(m, 1.0, MFEp50),
             notes=f"scale 50/50 f1=1.0 f2=MFEp50={MFEp50:.3f}")

        # ---- Family E: shorter time-stop, derived ----
        ttf = m["fill_bar"][m["win"]] * m["tf_h"]
        for pp, lbl in ((50, "P50"), (75, "P75")):
            Kh = float(np.nanpercentile(ttf, pp))
            g, h, Kb = fam_E(m, Kh)
            emit("E", f"E_time_TTF_{lbl}", g, h, notes=f"K_hours=P{pp}(win ttf)={Kh:.1f} -> K_bars={Kb}")

        # ---- Family F: activation then breakeven ----
        A_loser = float(np.nanpercentile(m["MFE"][~m["win"]], 50))
        paL = read_phaseA(tag, "MFE", "loser")
        if paL is not None:
            expL2 = paL.get("50")
            if expL2 is not None:
                match = abs(A_loser - expL2) <= 0.02
                deriv.append(f"{tag} F_act_loserMFEp50 A=P50(MFE_loser)={A_loser:.3f} "
                             f"(PhaseA MFE_loser_P50={expL2:.3f}, match={match})")
                if not match:
                    identity_lines.append(f"ABORT {tag} F loser MFEp50 mismatch {A_loser:.3f} vs {expL2:.3f}")
                    abort = True
        g, go, gp, h = fam_F(m, A_loser)
        emit("F", "F_act_loserMFEp50", g, h, gross_opt=go, gross_pess=gp,
             notes=f"activation=bt+P50(MFE_loser)={A_loser:.3f}wg, BE=entry+15bps")
        g, go, gp, h = fam_F(m, 1.0)
        emit("F", "F_act_1wick", g, h, gross_opt=go, gross_pess=gp, notes="activation=bt+1.0wick, BE=entry+15bps")

        # ---- Family G: limit at body-bottom ----
        g_full, filled, hold = fam_G(m, skip=True)
        emit("G", "G_limit_skip", g_full[filled], hold[filled], n_filled=int(filled.sum()),
             notes="limit=body_bottom; unfilled -> no trade")
        g_full, filled, hold = fam_G(m, skip=False)
        emit("G", "G_limit_mkt_fallback", g_full, hold, notes="limit=body_bottom; unfilled -> fill close[eb]")

        deriv.append(f"{tag} baseline net={net0:.2f} win={win0:.1f} maxdd={maxdd0:.1f} worst={worst0:.1f}")

    # ---- identity gate result ----
    deriv.insert(0, "# IDENTITY GATE (§2.1)")
    for line in identity_lines:
        deriv.insert(1 if line.startswith(("E1","E2","E3","E4")) else len(deriv), line)
    ident_all_pass = (not abort) and all(l.endswith("PASS") for l in identity_lines if l.startswith(("E1","E2","E3","E4")))

    if abort:
        # write short abort note only
        md = "# KEEPN STUDY (ABORTED)\n\n## Identity gate\n\n" + "\n".join(identity_lines) + \
             "\n\nAgent stopped: identity gate FAIL. No CSV / no deriv emitted.\n"
        (P.V2_OUTPUTS.parent / "KEEPN_STUDY.md").write_text(md)
        print("ABORT: identity gate failed. Wrote short KEEPN_STUDY.md only.")
        sys.exit(1)

    # ---- BH across new policy cells (§3.6) ----
    pvals = [c[2] for c in bh_cells]
    rej = bh_reject(pvals, Q)
    rejected = [(c[0], c[1], c[2]) for c, r in zip(bh_cells, rej) if r]
    for (tag, pol, _), r in zip(bh_cells, rej):
        for row in rows_out:
            if row["row"] == tag and row["policy"] == pol:
                row["bh_sig"] = str(bool(r))
                break

    # ---- write CSV ----
    cols = ["row","policy","family","n","n0","n_retention_pct","win","win0","win_delta_pp",
            "net","net0","net_delta_bps","net_4","net_11_5","net_opt","net_pess","net_all_signals",
            "monthly","maxdd","maxdd0","maxdd_delta_pp","med_hold_h","worst","worst0","worst_delta_bps",
            "pval","ci_lo","ci_hi","bh_sig","keepn_improve","keepn_defend","fill_rate","notes"]
    df = pd.DataFrame(rows_out)[cols]
    # ensure no np.float64 leaks: cast
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(lambda v: float(v) if isinstance(v, (np.floating,)) else
                              (int(v) if isinstance(v, (np.integer,)) else v))
    df.to_csv(P.V2_OUTPUTS / "keepn_study.csv", index=False)

    # ---- deriv.txt ----
    deriv.append("")
    deriv.append(f"# BH (§3.6): family size={len(pvals)} q={Q} rejected={len(rejected)}")
    for (t, p, pv) in rejected:
        deriv.append(f"  REJECTED {t} {p} p={pv:.6g}")
    (P.V2_OUTPUTS / "keepn_deriv.txt").write_text("\n".join(deriv) + "\n")

    # ---- Markdown report (§7, generated from CSV) ----
    md = build_report(df, ident_rows, deriv, rejected, bh_cells)
    (P.V2_OUTPUTS.parent / "KEEPN_STUDY.md").write_text(md)

    print(f"Wrote keepn_study.csv ({len(df)} rows), keepn_deriv.txt, KEEPN_STUDY.md. BH rejected={len(rejected)}.")
    print("Identity gate: ALL PASS")
    return df, identity_lines, deriv, rejected, bh_cells


def build_report(df, ident_rows, deriv, rejected, bh_cells):
    L = []
    L.append("# KEEPN STUDY — EXIT / SL / TP MEASUREMENT (TRAIN)\n")
    L.append("> Codename KEEPN (keep-n). Measurement only. No winner selected. Owner evaluates.\n")

    # 1. Identity gate
    L.append("## 1. Identity gate\n")
    L.append("| row | n | max entry (UTC) | max entry OK | baseline net @15bps | net OK | baseline win% | win OK | baseline maxDD% | maxDD OK | baseline worst bps | worst OK | GATE |")
    L.append("|-----|---|-----------------|-------------|----------------------|--------|---------------|--------|-----------------|---------|--------------------|---------|------|")
    for r in ident_rows:
        L.append(f"| {r['tag']} | {r['n']} (exp {r['n_exp']}) | {r['max_entry']} | {r['max_entry_ok']} "
                 f"| {r['net']:.2f} (exp {r['net_exp']}) | {r['net_ok']} | {r['win']:.1f} (exp {r['win_exp']}) | {r['win_ok']} "
                 f"| {r['maxdd']:.1f} (exp {r['maxdd_exp']}) | {r['maxdd_ok']} | {r['worst']:.1f} (exp {r['worst_exp']}) | {r['worst_ok']} "
                 f"| {'PASS' if r['pass_'] else 'FAIL'} |")
    allpass = all(r['pass_'] for r in ident_rows)
    L.append(f"\n**Identity gate: {'ALL PASS' if allpass else 'FAIL — abort'}.**\n")

    # 2. Prohibitions kept
    L.append("## 2. Prohibitions kept\n")
    X = [
        "X1 BTC-regime gate (TREND_UP/VOL_EXPANSION)", "X2 Skip RANGE/TREND_DOWN",
        "X3 wick/ATR vol-normalize trigger", "X4 quiet-volume / rvol gate",
        "X5 prior-bear/below-SMA/quality-score AND-gates", "X6 green-candle-only",
        "X7 session filter (Asia skip)", "X8 dip filter (24h/4d)",
        "X9 switch to thin cells (W3_DIP/W4/1D/ICP)", "X10 funding-rate skip/flatten",
        "X11 concurrent-risk cap / retune 2% stake", "X12 LightGBM/ML/exhaustion classifier",
        "X13 re-run W6 ABS/ATR/QMAE grid", "X14 re-run Exit Study I P1/P4/P5 percentiles",
        "X15 fire E-VAL / E-LOCKBOX", "X16 touch reserved window 2025-07-01→2026-06-30",
        "X17 modify FROZEN_CANDIDATE/META_VERDICT/config/SYSTEM_SIGNED",
        "X18 rebuild union_ledger / fix m2_grid BH / reissue MENU2",
        "X19 new assets/TFs/W4/DIP/5m/15m/1D", "X20 L2/order-book/tick data",
        "X21 extra policy families/f/checkpoints/trail distances",
        "X22 pick winner / freeze spec / write recommended system",
        "X23 extra charts/notebooks/dashboards/refactor src/lib",
        "X24 assume result / skip empty cell",
    ]
    for x in X:
        L.append(f"- [x] {x} — not done")
    L.append("")

    # 3. Derivation sheet
    L.append("## 3. Derivation sheet\n")
    for line in deriv:
        if line.startswith("# IDENTITY GATE") or line.strip() == "":
            continue
        L.append(f"- {line}")
    L.append("")

    # 4. Full results table (from CSV)
    L.append("## 4. Full results table\n")
    L.append("| row | policy | family | n | n0 | win% | win0 | net | net0 | netΔbps | maxdd | worst | pval | ci_lo | ci_hi | bh | improve | defend | n_ret% | fill |")
    L.append("|-----|--------|--------|---|----|------|------|-----|------|---------|-------|-------|------|-------|-------|----|--------|-------|--------|------|")
    for _, r in df.iterrows():
        nret = "" if (r["n_retention_pct"] == "" or (isinstance(r["n_retention_pct"], float) and np.isnan(r["n_retention_pct"]))) else f"{r['n_retention_pct']}"
        L.append(f"| {r['row']} | {r['policy']} | {r['family']} | {r['n']} | {r['n0']} | {r['win']} | {r['win0']} "
                 f"| {r['net']} | {r['net0']} | {r['net_delta_bps']} | {r['maxdd']} | {r['worst']} | {r['pval']} "
                 f"| {r['ci_lo']} | {r['ci_hi']} | {r['bh_sig']} | {r['keepn_improve']} | {r['keepn_defend']} | {nret} | {r['fill_rate']} |")
    L.append("")

    # 5. Flag index
    L.append("## 5. Flag index\n")
    imp = df[df.keepn_improve == "True"]
    dfn = df[df.keepn_defend == "True"]
    L.append("**keepn_improve = True:**")
    if len(imp) == 0:
        L.append("- NONE")
    else:
        for _, r in imp.iterrows():
            L.append(f"- {r['row']} {r['policy']} (net={r['net']}, win={r['win']}%)")
    L.append("")
    L.append("**keepn_defend = True:**")
    if len(dfn) == 0:
        L.append("- NONE")
    else:
        for _, r in dfn.iterrows():
            L.append(f"- {r['row']} {r['policy']} (maxdd={r['maxdd']}%, worst={r['worst']})")
    L.append("")

    # 6. n-retention exceptions (G_limit_skip only)
    L.append("## 6. n-retention exceptions\n")
    g = df[(df.family == "G") & (df.policy == "G_limit_skip")]
    if len(g) == 0:
        L.append("- NONE")
    else:
        for _, r in g.iterrows():
            nret = r["n_retention_pct"]
            status = "OK" if (isinstance(nret, (int, float)) and nret >= 80) else "FAILS OWNER N-FLOOR"
            L.append(f"- {r['row']} G_limit_skip: n_filled={r['n']}, fill_rate={r['fill_rate']}, "
                     f"net_filled={r['net']}, net_all_signals={r['net_all_signals']} -> {status}")
    L.append("")

    # 7. BH
    L.append("## 7. Benjamini–Hochberg (within-study family, q=0.05)\n")
    L.append(f"- Family size (new policy cells) = {len(bh_cells)}")
    L.append(f"- q = {Q}")
    L.append(f"- Rejected = {len(rejected)}")
    if rejected:
        L.append("- Rejected cells:")
        for (t, p, pv) in rejected:
            L.append(f"  - {t} {p} p={pv:.6g}")
    else:
        L.append("- NONE rejected")
    L.append("- Union ledger (union_ledger.json) was **not** updated by this pass.")
    L.append("")

    # 8. Same-bar note
    L.append("## 8. Same-bar note\n")
    L.append("Headline resolution follows §3.2. Intrabar touch SL (Family A disaster SL): pessimistic "
             "SL-first if that bar's low ≤ SL and high ≥ TP; `net_opt` (extra col) = TP-first. "
             "Close-based stops (Family B): TP-first (a live TP fills on high; a close-stop cannot fire "
             "until the close); `net_pess` = close-first on the same bar. Time-stop / scale / TP-only: "
             "TP on high else close at K; `net_opt` = `net`. Family F BE-stop same bar as TP after "
             "activation: SL-first (touch stop). The two columns are never averaged; the headline is the "
             "honest column above for each family.")
    L.append("")

    # 9. In-sample tercile disclosure
    L.append("## 9. In-sample tercile disclosure\n")
    L.append("Family C cut points (1/3 and 2/3 quantiles of uPnL_wick at each checkpoint h=6/12/24h) are "
             "computed on the SAME TRAIN trades used for the baseline — they are an in-sample distribution, "
             "not out-of-sample. This is disclosed here and not presented as OOS evidence.")
    L.append("")

    # 10. Stop
    L.append("## 10. Stop\n")
    L.append("AGENT STOPS. No freeze. No E-VAL. Owner evaluates.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
