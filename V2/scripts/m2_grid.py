"""MENU-2 grid (Directive 3 Task 2): multi-asset x multi-TF wick-fill discovery.

TRAIN only. Bybit USDT-perp. Color-agnostic. MKT entry, TP=body_top+1.5*wick_gap, no price stop.
Time stop = fixed 4-day WALL-CLOCK horizon (192/96/24/4 bars). Cost flat 15 bps RT. Funding ignored.
Dip = bottom quintile of corrected 24h return (TF-appropriate lookback). Rows from row_specs registry.
All loads pass time_gates (TRAIN clip + reserved-window drop assert). No E-VAL/E-LOCKBOX.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS
from lib.sim import replay

ASSETS = ["SOLUSDT", "BTCUSDT", "ETHUSDT"]          # Tier A (must)
TFS = ["30m", "1h", "4h", "1D"]
HORIZON = {"30m": 192, "1h": 96, "4h": 24, "1D": 4}   # 4-day wall-clock
TF_H = {"30m": 0.5, "1h": 1.0, "4h": 4.0, "1D": 24.0}
TRAIN_MONTHS = 28
COST = 15.0

def load_bars(symbol, tf):
    fn = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    if not fn.exists():
        return None
    tr = pd.read_csv(fn)
    low = {c.strip().strip('"').lower(): c for c in tr.columns}
    inv = {v: k for k, v in low.items()}
    tr = tr.rename(columns=inv)[["time", "open", "high", "low", "close"]].apply(pd.to_numeric)
    tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    tr = T.filter_window(tr, "TRAIN")                 # assert no holdout leakage
    return tr

def boot_ci(x, B=2000, seed=42):
    x = np.asarray(x, float); n_ = len(x)
    if n_ < 10: return np.nan, (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    ms = np.empty(B)
    for d0 in range(0, B, 64):
        d = min(64, B - d0)
        ms[d0:d0 + d] = x[rng.integers(0, n_, size=(d, n_))].mean(axis=1)
    return x.mean(), tuple(np.quantile(ms, [0.025, 0.975]))

def pval_from_mean_ci(mean, lo, hi):
    if np.isnan(lo): return 1.0
    se = (hi - lo) / (2 * 1.96)
    z = mean / se if se > 0 else 0.0
    from scipy import stats
    return 2 * (1 - stats.norm.cdf(abs(z)))

def cell_stats(symbol, tf, name):
    bars = load_bars(symbol, tf)
    if bars is None:
        return None
    feats = RS.build_features(bars, tf, legacy=False, symbol=symbol)
    spec = RS.get_spec(name, tf, legacy=False)
    sig, eb = RS.select(spec, feats)
    n = len(sig)
    if n < 10:
        return dict(asset=symbol, tf=tf, row=name, n=n, trades_month=np.nan, win=np.nan,
                    net=np.nan, monthly=np.nan, maxdd=np.nan, med_hold=np.nan,
                    wr_green=np.nan, wr_red=np.nan, ci_lo=np.nan, ci_hi=np.nan, pval=1.0)
    O, Hh, L, C = feats["O"], feats["H"], feats["L"], feats["C"]
    bt = O[eb]; body_top = np.maximum(O[sig], C[sig]); wg = Hh[sig] - body_top
    tp = body_top + 1.5 * wg
    K = HORIZON[tf]
    gross, _ = replay(O, Hh, L, C, sig, eb, bt, tp, K=K, window=K + 1)
    net = gross - COST
    mean, (lo, hi) = boot_ci(net)
    pval = pval_from_mean_ci(mean, lo, hi)
    win = float((net > 0).mean())
    # 2% stake equity / maxdd
    eq = pd.Series(np.cumprod(1 + 0.02 * (net / 1e4)))
    dd = (eq - eq.cummax()) / eq.cummax(); maxdd = float(-dd.min())
    # median hold in days
    starts = np.clip(eb, 0, len(L) - 1)
    idx = np.clip(starts[:, None] + np.arange(K + 1)[None, :], 0, len(L) - 1)
    fhi = Hh[idx]; tp_hit = fhi >= tp[:, None]
    tp_idx = np.where(tp_hit.any(1), tp_hit.argmax(1), K + 1)
    held = np.minimum(tp_idx, K)
    med_hold = float(np.median(held) * TF_H[tf] / 24.0)
    green_mask = feats["green"][sig]
    wr_g = float((net[green_mask] > 0).mean()) if green_mask.any() else np.nan
    wr_r = float((net[~green_mask] > 0).mean()) if (~green_mask).any() else np.nan
    return dict(asset=symbol, tf=tf, row=name, n=n,
                trades_month=round(n / TRAIN_MONTHS, 1),
                win=round(win * 100, 1), net=round(mean, 2),
                monthly=round(mean * n / TRAIN_MONTHS, 1),
                maxdd=round(maxdd * 100, 1), med_hold=round(med_hold, 2),
                wr_green=round(wr_g * 100, 1), wr_red=round(wr_r * 100, 1),
                ci_lo=round(lo, 2), ci_hi=round(hi, 2), pval=round(pval, 6))

# ---- run grid ----
rows = []
for sym in ASSETS:
    for tf in TFS:
        for name in RS.spec_names():
            r = cell_stats(sym, tf, name)
            if r is None:
                print(f"SKIP {sym} {tf} {name} (no data)")
                continue
            rows.append(r)
            print(f"{sym:8s} {tf:3s} {name:9s} n={r['n']:5d} net={r['net']:+.2f} win={r['win']}% bh_pending")

grid = pd.DataFrame(rows)
grid.to_csv(P.V2_OUTPUTS / "menu2_grid.csv", index=False)

# ---- BH-FDR within grid ----
pv = grid["pval"].values.astype(float)
order = np.argsort(pv); m = len(pv)
bh = pv <= (np.arange(1, m + 1) / m) * 0.05
grid["bh_grid"] = False
grid.loc[grid.index[order[bh]], "bh_grid"] = True

# ---- union ledger (append to prior honest family = 442) ----
fam = []
w7 = pd.read_csv(P.V2_OUTPUTS / "w7_sol4h_corrected.csv")
for _, r in w7.iterrows(): fam.append(r.pval)
menu = pd.read_csv(P.V2_OUTPUTS / "redir_w1_menu.csv")
for _, r in menu.iterrows(): fam.append(r.pval)
# (W3_BASE / W1_DIP candidate p-values from the four-checks run)
fam.extend([0.001307, 0.001069])
for pv_ in grid["pval"].values: fam.append(pv_)
fam = np.clip(np.array(fam, float), 1e-12, 1.0)
order2 = np.argsort(fam); M = len(fam)
union_bh = fam <= (np.arange(1, M + 1) / M) * 0.05
# mark MENU-2 cells' union survival
grid["bh_union"] = False
menu2_start = M - len(grid)
for i, ok in enumerate(union_bh[menu2_start:]):
    grid.loc[grid.index[i], "bh_union"] = bool(ok)
grid.to_csv(P.V2_OUTPUTS / "menu2_grid.csv", index=False)

print("\n=== BH within grid ===")
print(f"cells={m}, significant={int(bh.sum())}")
print(f"union family size={M} (prior 442 + menu2 {len(grid)}), significant total={int(union_bh.sum())}")
print("MENU-2 cells surviving union:", int(grid['bh_union'].sum()))
print("wrote V2/outputs/menu2_grid.csv")
