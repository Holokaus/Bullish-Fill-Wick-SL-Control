"""
Decomposition experiment: is the elevated reach probability WICK-SPECIFIC
or just RANGE/VOLATILITY persistence?

Method: bin ALL tradable candles by RANGE decile (computed on the full sample).
Within each range decile, compare reach probability P(max(high(e+1),high(e+2))/open(e+1)-1 >= r)
averaged over the SAME required-return grid used in the core study, across four geometry groups:
  A_event : upper wick > 0.2% of close            (the user's event)
  B_lowwk : NOT an event, lower wick >= upper wick and lower wick > 0.2% (mirror geometry)
  C_body  : NOT an event, body >= max(wicks)      (pure-body candle)
  D_other : everything else (non-event)
Equal-weight average of reach over the event-r grid, per group. If A ~= B ~= C within
range bins -> pure volatility effect. If A > B,C -> wick-specific information.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
IV_MS = {"1d": 86_400_000, "4h": 14_400_000, "1h": 3_600_000, "30m": 1_800_000, "15m": 900_000}
SYMS = ["btcusdt", "ethusdt"]


def load(sym, tf):
    d = pd.read_csv(os.path.join(DATA, f"{sym.lower()}_{tf}.csv")).sort_values("ts").reset_index(drop=True)
    bt = d[["open", "close"]].max(axis=1)
    bb = d[["open", "close"]].min(axis=1)
    d["wick_up"] = d["high"] - bt
    d["wick_dn"] = bb - d["low"]
    d["body"] = d["close"] - d["open"]
    d["range"] = d["high"] - d["low"]
    d["is_event"] = d["wick_up"] > 0.002 * d["close"]
    o1 = d["open"].shift(-1)
    hmax2 = pd.concat([d["high"].shift(-1), d["high"].shift(-2)], axis=1).max(axis=1)
    d["m_ratio"] = hmax2 / o1 - 1.0
    d["ok_pair"] = ((d["ts"].shift(-1) - d["ts"]) == IV_MS[tf]) & ((d["ts"].shift(-2) - d["ts"]) == 2 * IV_MS[tf])
    return d


def main():
    out = {}
    for sym in SYMS:
        for tf in IV_MS:
            d = load(sym, tf)
            dd = d[d["ok_pair"] & d["m_ratio"].notna()].copy()
            # required-return grid: deciles of EVENT r_req (same spirit as core)
            ev_mask = dd["is_event"]
            bt_e = dd.loc[ev_mask, ["open", "close"]].max(axis=1)
            T_e = bt_e + 0.95 * dd.loc[ev_mask, "wick_up"]
            r_req_e = (T_e / dd.loc[ev_mask, "open"].shift(1) - 1.0).replace([np.inf, -np.inf], np.nan).dropna()
            r_req_e = r_req_e[r_req_e > 0]
            grid = np.unique(np.concatenate([[0.0], np.quantile(r_req_e, np.arange(0.1, 1.0, 0.1))]))

            rng_edges = np.unique(np.quantile(dd["range"], np.arange(0, 1.01, 0.1)))
            dd["rbin"] = pd.cut(dd["range"], rng_edges, include_lowest=True)

            wu, wd, bd = dd["wick_up"].to_numpy(), dd["wick_dn"].to_numpy(), dd["body"].to_numpy()
            ev = dd["is_event"].to_numpy()
            grp = np.where(ev, "A_event",
                  np.where((wd >= wu) & (wd > 0.002 * dd["close"].to_numpy()), "B_mirror",
                  np.where(bd >= np.maximum(wu, wd), "C_body", "D_other")))
            dd["grp"] = grp
            M = dd["m_ratio"].to_numpy()[:, None] >= grid[None, :]     # reach mask per grid point

            res = {}
            for g in ["A_event", "B_mirror", "C_body", "D_other"]:
                sel = (dd["grp"] == g).to_numpy()
                if sel.sum() < 50:
                    continue
                res[g] = {"n": int(sel.sum()), "p_reach_avg": float(M[sel].mean())}

            # range-bin detail for A vs best non-event competitor
            bins = {}
            for b, idx in dd.groupby("rbin", observed=True).groups.items():
                ii = dd.index.isin(idx)
                row = {}
                for g in ["A_event", "B_mirror", "C_body"]:
                    sel = ii & (dd["grp"] == g).to_numpy()
                    if sel.sum() >= 30:
                        row[g] = {"n": int(sel.sum()), "p": float(M[sel].mean())}
                if len(row) >= 2:
                    bins[str(b)] = row
            out[f"{sym}_{tf}"] = {"groups": res, "by_range_bin": bins,
                                  "grid_mean_r": float(grid.mean())}
            print(f"{sym} {tf}: " + json.dumps({g: (round(v['p_reach_avg'], 4), v['n']) for g, v in res.items()}))

    with open(os.path.join(RES, "decomposition.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("SAVED decomposition.json")


if __name__ == "__main__":
    main()
