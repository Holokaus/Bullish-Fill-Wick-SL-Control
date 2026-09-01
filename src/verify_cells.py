"""Robustness probe: are the standout net-positive cells stable across years?
Rebuilds events per cell and prints net bp by year + Wilson CI on p_win."""
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from conditional_stats import load_events, NET_COST

CELLS = [
    ("solusdt", "1d", (1.3, 1.75)), ("solusdt", "4h", (2.5, np.inf)),
    ("solusdt", "1h", (1.75, 2.5)), ("btcusdt", "1d", (2.5, np.inf)),
    ("ethusdt", "4h", (2.5, np.inf)),
]
for sym, tf, (lo, hi) in CELLS:
    ev = load_events(sym, tf)
    m = (ev["wick_pct"] >= lo) & (ev["wick_pct"] < hi)
    sub = ev[m].copy()
    print(f"\n=== {sym} {tf} wick[{lo},{hi})  n={len(sub)} ===")
    yr = sub.groupby("hour", group_keys=False).apply(lambda g: g, include_groups=False) if False else None
    sub["year"] = pd.to_datetime(sub["ts"] * 0 + sub.index.astype("int64"), unit="ns", utc=True) if False else None
    # entry timestamp = next candle open time -> recompute from ts
    d = pd.read_csv(f"data/{sym}_{tf}.csv")["ts"]
    pos = {t: i for i, t in enumerate(d)}
    sub["yr"] = [pd.to_datetime(int(d.iloc[pos[int(t)] + 1]), unit="ms", utc=True).year for t in sub["ts"]]
    for y, g in sub.groupby("yr"):
        k, n = int(g["win"].sum()), len(g)
        p = k / n
        hw = 1.96 * np.sqrt(p * (1 - p) / n)
        print(f"  {y}: n={n:>4}  p_win={p:.3f}±{hw:.3f}  net={1e4*g['net'].mean():+7.1f}bp")
