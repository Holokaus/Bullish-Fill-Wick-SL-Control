"""
Conditional statistics engine — every conditioning dimension the study requires,
computed per asset x timeframe, events rebuilt identically to analysis_core.

Dimensions:
  A  wick-length buckets -> win/fill/expectancy, optimal bucket by NET expectancy
  B  fill timing: filled on e+1 / only on e+2 / no fill (overall, by color, by bucket)
  C  path before outcome: MAE of winners, MFE of losers (how deep dips went / how close losses came)
  D  preceding candle (e-1): its color, its range, whether it was itself an event
  E  trend context: 12-candle return sign; close position in 24-candle range
  F  event-candle volume: RVOL vs trailing 20-candle median
  G  candle anatomy: body/range class x color (6 types)
  H  hour-of-day (UTC) seasonality of entry
  I  entry optimization: limit orders below open(e+1) — fill prob, target prob, net expectancy
     (optimistic/pessimistic bounds for same-candle ambiguity)
Net stack everywhere: futures maker-in/taker-out 7bp + slippage 4bp = 11bp round trip.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results", "conditional")
os.makedirs(RES, exist_ok=True)
IV_MS = {"1d": 86_400_000, "4h": 14_400_000, "1h": 3_600_000, "30m": 1_800_000, "15m": 900_000}
SYMS = ["solusdt", "btcusdt", "ethusdt"]
NET_COST = 0.0011          # 7bp fees + 4bp slippage
WICK_EDGES = [0.2, 0.3, 0.4, 0.5, 0.65, 0.8, 1.0, 1.3, 1.75, 2.5, np.inf]


def q(x, ps=(10, 25, 50, 75, 90)):
    return {f"p{p}": float(np.percentile(x, p)) for p in ps} if len(x) else {}


def load_events(sym, tf):
    d = pd.read_csv(os.path.join(DATA, f"{sym}_{tf}.csv")).sort_values("ts").reset_index(drop=True)
    iv = IV_MS[tf]
    bt = d[["open", "close"]].max(axis=1)
    d["wu"] = d["high"] - bt
    d["rng"] = d["high"] - d["low"]
    d["body"] = (d["close"] - d["open"]).abs()
    d["is_ev"] = d["wu"] > 0.002 * d["close"]
    o1, h1, l1 = d["open"].shift(-1), d["high"].shift(-1), d["low"].shift(-1)
    h2, c2 = d["high"].shift(-2), d["close"].shift(-2)
    ok = ((d["ts"].shift(-1) - d["ts"]) == iv) & ((d["ts"].shift(-2) - d["ts"]) == 2 * iv)
    ev = d[d["is_ev"] & ok].copy()
    ev["entry"], ev["T"] = o1[ev.index], bt[ev.index] + 0.95 * d["wu"][ev.index]
    ev = ev[ev["entry"] > 0]
    ev["win1"] = h1[ev.index] >= ev["T"]
    ev["win2o"] = (~ev["win1"]) & (h2[ev.index] >= ev["T"])
    ev["win"] = ev["win1"] | ev["win2o"]
    ev["r_req"] = ev["T"] / ev["entry"] - 1
    ev["exit_ret"] = np.where(ev["win"], ev["r_req"], c2[ev.index] / ev["entry"] - 1)
    ev["net"] = ev["exit_ret"] - NET_COST
    ev["bull"] = d["close"][ev.index] >= d["open"][ev.index]
    ev["wick_pct"] = 100 * d["wu"][ev.index] / d["close"][ev.index]
    ev["body_pct"] = 100 * d["body"][ev.index] / d["rng"][ev.index].replace(0, np.nan)
    # --- preceding candle ---
    ev["prev_bull"] = (d["close"].shift(1) >= d["open"].shift(1))[ev.index]
    ev["prev_is_ev"] = d["is_ev"].shift(1)[ev.index]
    ev["prev_rng_pct"] = 100 * (d["rng"].shift(1) / d["close"].shift(1))[ev.index]
    # --- trend context ---
    ev["tr12"] = (d["close"] / d["close"].shift(12) - 1)[ev.index]
    mx, mn = d["high"].rolling(24).max(), d["low"].rolling(24).min()
    ev["pctB"] = ((d["close"] - mn) / (mx - mn).replace(0, np.nan))[ev.index]
    # --- volume ---
    med20 = d["volume"].shift(1).rolling(20).median()
    ev["rvol"] = (d["volume"] / med20)[ev.index]
    # --- path ---
    ev["mae_w"] = (pd.concat([l1, d["low"].shift(-2)], axis=1).min(axis=1) / ev["entry"] - 1)[ev.index]
    ev["mfe_l"] = (pd.concat([h1, h2], axis=1).max(axis=1) / ev["entry"] - 1)[ev.index]
    ev["hour"] = pd.to_datetime(o1.index.to_series().map(d["ts"]), unit="ms", utc=True).dt.hour.values \
        if False else pd.to_datetime(d["ts"].shift(-1)[ev.index], unit="ms", utc=True).dt.hour
    return ev


def grp_table(ev, key):
    g = ev.groupby(key, dropna=True)
    out = {}
    for k, s in g:
        out[str(k)] = {"n": int(len(s)), "p_win": float(s["win"].mean()),
                       "p_win1": float(s["win1"].mean()), "p_win2only": float(s["win2o"].mean()),
                       "gross_bp": float(1e4 * s["exit_ret"].mean()),
                       "net_bp": float(1e4 * s["net"].mean())}
    return out


def main():
    master = {}
    for sym in SYMS:
        for tf in IV_MS:
            try:
                ev = load_events(sym, tf)
            except FileNotFoundError:
                continue
            if len(ev) < 200:
                continue
            res = {"n_events": len(ev)}

            # A: wick buckets + optimum
            ev["wb"] = pd.cut(ev["wick_pct"], WICK_EDGES, right=False)
            A = grp_table(ev, "wb")
            validA = {k: v for k, v in A.items() if v["n"] >= 60}
            best = max(validA.items(), key=lambda kv: kv[1]["net_bp"])
            res["A_wick_buckets"] = A
            res["A_optimal_bucket_by_net"] = {"bucket": best[0], **best[1]}

            # B: fill timing
            res["B_timing_overall"] = {
                "fill_on_e+1": float(ev["win1"].mean()), "fill_only_on_e+2": float(ev["win2o"].mean()),
                "no_fill": float((~ev["win"]).mean())}
            res["B_timing_by_color"] = grp_table(ev, "bull")

            # C: path
            w, l_ = ev[ev["win"]], ev[~ev["win"]]
            res["C_path"] = {"winner_MAE_bp": q(1e4 * w["mae_w"]),
                             "loser_MFE_bp": q(1e4 * l_["mfe_l"]),
                             "P(winner dipped >=10bp first)": float((w["mae_w"] <= -0.001).mean()),
                             "P(loser got within 10bp of T)": float((l_["mfe_l"] >= l_["r_req"] - 0.001).mean())}

            # D: preceding candle
            res["D_prev_color_x_color"] = grp_table(ev.assign(pc=ev["prev_bull"].astype(str) + "|" + ev["bull"].astype(str)), "pc")
            res["D_prev_was_event"] = grp_table(ev, "prev_is_ev")
            ev["prb"] = pd.qcut(ev["prev_rng_pct"], 3, duplicates="drop")
            res["D_prev_range_tercile"] = grp_table(ev, "prb")

            # E: trend
            ev["trs"] = np.select([ev["tr12"] > 0.003, ev["tr12"] < -0.003], ["up", "down"], "flat")
            res["E_trend12"] = grp_table(ev, "trs")
            ev["pbs"] = np.select([ev["pctB"] > 0.66, ev["pctB"] < 0.33], ["hi33", "lo33"], "mid")
            res["E_posIn24hRange"] = grp_table(ev, "pbs")

            # F: volume
            ev["rv"] = pd.cut(ev["rvol"], [0, 0.7, 1.3, 2.0, np.inf], right=False)
            res["F_rvol"] = grp_table(ev, "rv")

            # G: anatomy
            ev["typ"] = np.select([ev["body_pct"] < 30, ev["body_pct"] <= 70], ["small_body", "mid_body"], "large_body")
            ev["tt"] = ev["typ"] + "_" + np.where(ev["bull"], "bull", "bear")
            res["G_anatomy"] = grp_table(ev, "tt")

            # H: hour of day
            hh = grp_table(ev, "hour")
            good = {k: v for k, v in hh.items() if v["n"] >= 80}
            if good:
                bh = max(good.items(), key=lambda kv: kv[1]["net_bp"])
                wh = min(good.items(), key=lambda kv: kv[1]["net_bp"])
                res["H_hour_best"] = {"utc_hour": bh[0], **bh[1]}
                res["H_hour_worst"] = {"utc_hour": wh[0], **wh[1]}
            res["H_hour_table"] = hh

            # I: dip-entry optimization (limit below open(e+1))
            d = pd.read_csv(os.path.join(DATA, f"{sym}_{tf}.csv")).sort_values("ts").reset_index(drop=True)
            l1 = d["low"].shift(-1)[ev.index]; h1v = d["high"].shift(-1)[ev.index]
            h2v = d["high"].shift(-2)[ev.index]; c2v = d["close"].shift(-2)[ev.index]
            rows = []
            for disc in [0, 5, 10, 15, 20, 30]:
                L = ev["entry"] * (1 - disc / 1e4)
                filled = (l1 <= L).fillna(False)
                amb = filled & (h1v >= ev["T"])                     # both touched in e+1: order unknown
                won_clear = filled & (~amb) & (h2v >= ev["T"])
                lost = filled & (~amb) & (~won_clear)
                pnl_opt = pd.Series(0.0, index=ev.index)
                pnl_opt[won_clear | amb] = (ev["T"] / L)[won_clear | amb] - 1
                pnl_opt[lost] = (c2v / L)[lost] - 1
                pnl_pess = pnl_opt.copy(); pnl_pess[amb] = 0.0      # ambiguous -> no trade credit
                rows.append({"disc_bp": disc, "fill_rate": float(filled.mean()),
                             "hit_rate_given_fill": float((ev["T"][filled] <= L[filled]).mean() if filled.any() else np.nan),
                             "net_opt_bp_per_signal": float(1e4 * pnl_opt.mean() - NET_COST * filled.mean()),
                             "net_pess_bp_per_signal": float(1e4 * pnl_pess.mean() - NET_COST * filled.mean())})
            res["I_dip_entry_ladder"] = rows

            master[f"{sym}_{tf}"] = res
            with open(os.path.join(RES, f"{sym}_{tf}.json"), "w") as f:
                json.dump(res, f, indent=1, default=str)

    # ---- digest print ----
    print("OPTIMAL WICK BUCKET (by net bp/trade, fut maker/taker+slip stack):")
    for k, v in master.items():
        b = v["A_optimal_bucket_by_net"]
        print(f"  {k:<14} {b['bucket']:>16}  n={b['n']:>5} p_win={b['p_win']:.3f} net={b['net_bp']:+6.1f}bp")
    print("\nFILL TIMING (share of events):")
    for k, v in master.items():
        t = v["B_timing_overall"]
        print(f"  {k:<14} e+1:{t['fill_on_e+1']*100:5.1f}%  e+2only:{t['fill_only_on_e+2']*100:5.1f}%  none:{t['no_fill']*100:5.1f}%")
    print("\nTREND12 conditioning (p_win / net_bp):")
    for k, v in master.items():
        row = " ".join(f"{s}:{t['p_win']:.3f}/{t['net_bp']:+5.1f}" for s, t in v["E_trend12"].items())
        print(f"  {k:<14} {row}")
    with open(os.path.join(RES, "master.json"), "w") as f:
        json.dump(master, f, indent=1, default=str)
    print("\nSAVED results/conditional/*.json")


if __name__ == "__main__":
    main()
