"""
Tradeability layer: convert measured probabilities into net-of-cost expectancy and equity curves.
No SL (user decision). Exit rules frozen: limit-sell at T, else market-out at close(e+2).

Fee scenarios (per side, % of notional):
  spot_taker : 0.10 / 0.10   (Binance spot base)
  spot_maker : 0.10 / 0.10   (same base tier; entry could rest as maker -> no better here)
  fut_taker  : 0.05 / 0.05   (USD-M futures base taker)
  fut_mm     : 0.02 / 0.05   (maker entry, taker exit fallback)
Slippage: 0.02% per side applied to taker legs.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
FEE_SCEN = {"spot_taker": (0.0010, 0.0010), "spot_maker": (0.0010, 0.0010),
            "fut_taker": (0.0005, 0.0005), "fut_mm": (0.0002, 0.0005)}
SLIP = 0.0002
BUCKET_EDGES = [0.2, 0.35, 0.6, 1.0, 1.75, np.inf]


def net_ret(row, fin, fout, slip_in=True):
    gi = row["exit_ret"]
    cost = (fin + (SLIP if slip_in else 0)) + (fout + (SLIP if slip_in else 0))
    return (1 + gi) * (1 - fin - (SLIP if slip_in else 0)) * (1 - fout - (SLIP if slip_in else 0)) - 1 \
        if False else gi - cost


def load_events(sym, tf):
    e = pd.read_csv(os.path.join(RES, f"events_{sym}_{tf}.csv"))
    e["bucket"] = pd.cut(e["wick_pct"], BUCKET_EDGES, right=False)
    return e


def expectancy(sub, fin, fout):
    r = sub["exit_ret"] - (fin + fout + 2 * SLIP)
    eq = r.cumsum()
    dd = (eq - eq.cummax()).min() if len(eq) else 0.0
    return {"n": len(r), "exp_bp": float(1e4 * r.mean()),
            "win_rate": float(sub["win"].mean()), "med_r_req_bp": float(1e4 * sub["r_req"].median()),
            "total_ret_pct": float(100 * r.sum()), "maxDD_pct_sumcurve": float(-100 * dd)}


def main():
    report = {}
    curves = {}
    for sym in ["btcusdt", "ethusdt", "solusdt"]:
        for tf in ["1d", "4h", "1h", "30m", "15m"]:
            e = load_events(sym, tf)
            cell = {}
            for scen, (fin, fout) in FEE_SCEN.items():
                cell[scen] = {
                    "ALL": expectancy(e, fin, fout),
                    "BULL_ONLY": expectancy(e[e["bull_e"]], fin, fout),
                    "BULL_wick_lt_0.6": expectancy(e[e["bull_e"] & (e["wick_pct"] < 0.6)], fin, fout),
                }
            # per-bucket gross + net (spot_taker & fut_mm) detail
            bk = {}
            for b, sub in e.groupby("bucket", observed=True):
                bk[str(b)] = {"n": len(sub), "win_rate": float(sub["win"].mean()),
                              "gross_exp_bp": float(1e4 * sub["exit_ret"].mean()),
                              "net_spot_bp": float(1e4 * (sub["exit_ret"] - 0.0020 - 2 * SLIP).mean()),
                              "net_futmm_bp": float(1e4 * (sub["exit_ret"] - 0.0007 - 2 * SLIP).mean())}
            # holdout: 2026-01-01 onwards (entry-time based)
            h = e[pd.to_datetime(e["ts_entry"], unit="ms", utc=True) >= "2026-01-01"]
            hold = {scen: {k: expectancy(v_sub, *FEE_SCEN[scen]) for k, v_sub in
                           [("ALL", h), ("BULL_ONLY", h[h["bull_e"]])]} if len(h) else {}
                    for scen in FEE_SCEN}
            report[f"{sym}_{tf}"] = {"full": cell, "by_bucket_spotnet": bk,
                                     "holdout2026": hold,
                                     "n_holdout": len(h)}
            # store equity series (non-overlapping) for best-guess viz: ALL & BULL, fut_mm
            sub = e.sort_values("ts_entry")
            for name, s in [("all", sub), ("bull", sub[sub["bull_e"]])]:
                curves[f"{sym}_{tf}_{name}"] = {
                    "ts": s["ts_entry"].tolist(),
                    "cum_net_futmm_pct": (100 * (s["exit_ret"] - 0.0007 - 2 * SLIP)).cumsum().tolist(),
                    "cum_net_spot_pct": (100 * (s["exit_ret"] - 0.0020 - 2 * SLIP)).cumsum().tolist()}
    with open(os.path.join(RES, "backtest.json"), "w") as f:
        json.dump({"report": report}, f, indent=1)
    with open(os.path.join(RES, "curves.json"), "w") as f:
        json.dump(curves, f)

    # ---- console digest ----
    print(f"{'cell':<14}{'rule':<18}{'n':>6}{'win%':>7}{'gross':>8}{'spotNet':>9}{'futmmNet':>9}")
    for k, v in report.items():
        for rule in ["ALL", "BULL_ONLY", "BULL_wick_lt_0.6"]:
            f_ = v["full"]["fut_taker"][rule]
            fs = v["full"]["spot_taker"][rule]
            fm = v["full"]["fut_mm"][rule]
            print(f"{k:<14}{rule:<18}{f_['n']:>6}{100*f_['win_rate']:>7.1f}{f_['exp_bp']:>8.1f}{fs['exp_bp']:>9.1f}{fm['exp_bp']:>9.1f}")
        print()
    print("SAVED backtest.json, curves.json")


if __name__ == "__main__":
    main()
