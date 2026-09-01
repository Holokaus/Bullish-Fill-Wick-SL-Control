"""
Core analysis: upper-wick continuation study.
Builds event/outcome tables per symbol x timeframe and computes the pre-registered statistics.

Conventions (frozen in ../results/pre_registration.md):
  event        : wick_up > 0.002 * close          (wick_up = high - max(open, close))
  entry        : open of candle e+1               (long)
  target T     : body_top_e + 0.95 * wick_up_e    (body_top = max(open, close))
  win          : high(e+1) >= T  or  high(e+2) >= T   (limit-order fill semantics)
  no-SL exit   : if not filled by end of e+2 -> exit at close(e+2)
  contiguity   : e->e+1->e+2 must be exactly adjacent candles
  gap-trivial  : entry >= T  (target already breached at entry) -> flagged, counted separately
"""
import os, json
import numpy as np
import pandas as pd
from scipy import stats as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
os.makedirs(RES, exist_ok=True)

IV_MS = {"1d": 86_400_000, "4h": 14_400_000, "1h": 3_600_000, "30m": 1_800_000, "15m": 900_000}
SYMS = {s: ["1d", "4h", "1h", "30m", "15m"] for s in ["btcusdt", "ethusdt", "solusdt"]}
BUCKET_EDGES = [0.2, 0.35, 0.6, 1.0, 1.75, np.inf]   # % of close, chosen before any outcome was seen


def wilson(k, n, z=1.959963985):
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    den = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, ctr - hw, ctr + hw)


def load(sym, tf):
    d = pd.read_csv(os.path.join(DATA, f"{sym.lower()}_{tf}.csv"))
    d = d.sort_values("ts").reset_index(drop=True)
    d["contig_next"] = d["ts"].shift(-1) - d["ts"] == IV_MS[tf]     # e->e+1
    d["contig_next2"] = d["ts"].shift(-2) - d["ts"] == 2 * IV_MS[tf]  # e->e+2
    bt = d[["open", "close"]].max(axis=1)
    d["body_top"] = bt
    d["wick_up"] = d["high"] - bt
    d["wick_pct"] = 100 * d["wick_up"] / d["close"]
    d["is_event"] = d["wick_up"] > 0.002 * d["close"]
    d["bull_e"] = d["close"] >= d["open"]
    # max achievable return buying next open, within 2 candles (for controls)
    o1 = d["open"].shift(-1)
    hmax2 = pd.concat([d["high"].shift(-1), d["high"].shift(-2)], axis=1).max(axis=1)
    d["m_ratio"] = hmax2 / o1 - 1.0            # NaN if no next candle
    d["ok_pair"] = d["contig_next"] & d["contig_next2"]
    return d


def build_events(d, sym, tf):
    e = d[d["is_event"] & d["ok_pair"]].copy()
    nxt = d.shift(-1)
    nn = d.shift(-2)
    e["ts_entry"] = nxt["ts"][e.index]
    e["entry"] = nxt["open"][e.index]
    e["T"] = e["body_top"] + 0.95 * e["wick_up"]
    e["gap_trivial"] = e["entry"] >= e["T"]
    e["win1"] = nxt["high"][e.index] >= e["T"]
    e["win2"] = nn["high"][e.index] >= e["T"]
    e["win"] = e["win1"] | e["win2"]
    e["r_req"] = e["T"] / e["entry"] - 1.0                      # required return
    e["exit_ret"] = np.where(e["win"], e["r_req"], nn["close"][e.index] / e["entry"] - 1.0)
    e["dt_utc"] = pd.to_datetime(e["ts_entry"], unit="ms", utc=True)
    e["day"] = e["dt_utc"].dt.date                               # bootstrap cluster
    e["year"] = e["dt_utc"].dt.year
    e["hour"] = e["dt_utc"].dt.hour
    e["symbol"], e["tf"] = sym, tf
    cols = ["symbol", "tf", "ts", "ts_entry", "bull_e", "wick_pct", "r_req", "gap_trivial",
            "win1", "win2", "win", "exit_ret", "day", "year", "hour"]
    return e[cols].reset_index(drop=True)


def control_reach(d, r_grid):
    """For non-event tradable candles: P(m_ratio >= r) for each r in grid (TRUE reach prob)."""
    m = d.loc[d["ok_pair"] & ~d["is_event"], "m_ratio"].dropna().to_numpy(copy=True)
    m.sort()
    n = len(m)
    # searchsorted('left') counts elements STRICTLY BELOW r -> reach = 1 - that/n = P(m >= r)
    ks = np.searchsorted(m, r_grid, side="left")
    return {"n_controls": int(n), "grid": list(map(float, r_grid)),
            "reach": [(int(n - k), r, (n - k) / n) for k, r in zip(ks, r_grid)]}


def main():
    out = {}
    for sym, tfs in SYMS.items():
        for tf in tfs:
            d = load(sym, tf)
            ev = build_events(d, sym, tf)

            # ---- required-return deciles (event side) -> pseudo-target grid ----
            ev_nz = ev[~ev["gap_trivial"]]
            qs = np.quantile(ev_nz["r_req"], [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
            grid = np.unique(np.concatenate([[0.0], qs]))

            ctl = control_reach(d, grid)

            # baseline win prob for events = average control reach across the event r-distribution
            # (weight deciles equally; robust variant reported too)
            base_probs = [p for (_, _, p) in ctl["reach"]]
            p_base_mean = float(np.mean(base_probs))

            k_ev = int(ev_nz["win"].sum()); n_ev = len(ev_nz)
            p_ev = k_ev / n_ev if n_ev else np.nan
            w_lo, w_hi = wilson(k_ev, n_ev)[1:]
            delta = p_ev - p_base_mean

            # ---- day-cluster bootstrap CI for delta ----
            rng = np.random.default_rng(42)
            ev_days = ev_nz["day"].to_numpy()
            uniq_days, day_idx = np.unique(ev_days, return_inverse=True)
            wins_by_day = np.bincount(day_idx, weights=ev_nz["win"].astype(float))
            cnt_by_day = np.bincount(day_idx)
            # control side: boolean reach masks at the fixed grid
            mm = d.loc[d["ok_pair"] & ~d["is_event"], ["m_ratio", "ts"]].dropna()
            mm_day = pd.to_datetime(mm["ts"], unit="ms", utc=True).dt.date.to_numpy()
            udays_c, cidx = np.unique(mm_day, return_inverse=True)
            masks = (mm["m_ratio"].to_numpy()[:, None] >= grid[None, :])
            cwins_by_day = np.vstack([np.bincount(cidx, weights=masks[:, j]) for j in range(len(grid))]).T
            ccnt_by_day = np.bincount(cidx)
            B = 1000
            deltas = np.empty(B)
            nd = len(uniq_days); ncd = len(udays_c)
            for b in range(B):
                di = rng.integers(0, nd, nd)
                ci = rng.integers(0, ncd, ncd)
                pe = wins_by_day[di].sum() / cnt_by_day[di].sum()
                pb = np.mean(cwins_by_day[ci].sum(axis=0) / ccnt_by_day[ci].sum())
                deltas[b] = pe - pb
            lo, hi = np.percentile(deltas, [2.5, 97.5])

            # ---- buckets, color, fill timing, years ----
            ev_nz = ev_nz.copy()
            ev_nz["bucket"] = pd.cut(ev_nz["wick_pct"], BUCKET_EDGES, right=False)
            bkt = ev_nz.groupby("bucket", observed=True)["win"].agg(["sum", "count"])
            col = ev_nz.groupby("bull_e")["win"].agg(["sum", "count"])
            ytab = ev_nz.groupby("year")["win"].agg(["sum", "count"])
            f1 = int(ev_nz["win1"].sum())
            f2_only = int((ev_nz["win"] & ~ev_nz["win1"]).sum())

            # ---- overlapping-window subset (non-overlapping trades only) ----
            ts_entry = ev_nz["ts_entry"].to_numpy()
            keep, last_end = [], -1
            for i in range(len(ev_nz)):
                if ts_entry[i] > last_end:
                    keep.append(i)
                    last_end = ts_entry[i] + 2 * IV_MS[tf]
            nov = ev_nz.iloc[keep]

            # ---- per-year DELTA (event win rate minus same-year control reach at same grid) ----
            mm_year = pd.to_datetime(mm["ts"], unit="ms", utc=True).dt.year.to_numpy()
            ev_nz_y = ev_nz["year"].to_numpy()
            delta_by_year = {}
            for y in sorted(set(ev_nz_y.tolist()) | set(mm_year.tolist())):
                ey = ev_nz_y == y
                cy = mm_year == y
                if ey.sum() < 30 or cy.sum() < 200:
                    continue
                pe_y = float(ev_nz.loc[ey, "win"].mean())
                pb_y = float(np.mean((mm.loc[cy, "m_ratio"].to_numpy()[:, None] >= grid[None, :]).mean(axis=0)))
                delta_by_year[str(int(y))] = {"p_event": pe_y, "p_ctrl": pb_y, "delta": pe_y - pb_y}

            summ = {
                "symbol": sym, "tf": tf,
                "events_all": len(ev), "gap_trivial": int(ev["gap_trivial"].sum()),
                "events_tested": n_ev, "wins": k_ev,
                "p_event": p_ev, "ci_lo_wilson": w_lo, "ci_hi_wilson": w_hi,
                "p_baseline_matched": p_base_mean, "delta": delta,
                "delta_boot_lo": float(lo), "delta_boot_hi": float(hi),
                "sig_delta": bool(lo > 0),
                "gross_exit_ret_mean_pct": float(100 * ev["exit_ret"].mean()),
                "gross_exit_ret_median_pct": float(100 * ev["exit_ret"].median()),
                "fill_on_1st": f1, "fill_only_on_2nd": f2_only,
                "nonoverlap_events": len(nov), "nonoverlap_p": float(nov["win"].mean()) if len(nov) else np.nan,
                "buckets": {str(k): {"wins": int(v["sum"]), "n": int(v["count"]),
                                     "p": float(v["sum"] / v["count"]) if v["count"] else np.nan}
                            for k, v in bkt.iterrows()},
                "by_color": {"bull": {"wins": int(col.loc[True, "sum"]), "n": int(col.loc[True, "count"]),
                                      "p": float(col.loc[True, "sum"] / col.loc[True, "count"])},
                             "bear": {"wins": int(col.loc[False, "sum"]), "n": int(col.loc[False, "count"]),
                                      "p": float(col.loc[False, "sum"] / col.loc[False, "count"])}},
                "by_year": {str(y): {"wins": int(v["sum"]), "n": int(v["count"]),
                                     "p": float(v["sum"] / v["count"])} for y, v in ytab.iterrows()},
                "baseline_curve": [{"r": round(r, 6), "p_control": p} for (k, r, p) in ctl["reach"]],
                "n_controls": ctl["n_controls"],
                "delta_by_year": delta_by_year,
            }
            out[f"{sym}_{tf}"] = summ
            ev.to_csv(os.path.join(RES, f"events_{sym}_{tf}.csv"), index=False)
            print(json.dumps(summ))

    with open(os.path.join(RES, "summary_core.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nSAVED summary_core.json + per-TF event tables")


if __name__ == "__main__":
    main()
