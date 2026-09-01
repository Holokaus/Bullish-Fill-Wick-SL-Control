"""REDIR-W1: 8-row color-agnostic wick-fill menu (TRAIN, SOL-4h, Bybit perp).

Directive: BULLISH_FILL_WICK_REDIRECT_DIRECTIVE.md (simplification order).
Two dials only:
  Dial 1 wick threshold:
    W1 wbur_bps >= 22.5   (1.5x RT floor, RT=15bps)
    W2 wbur_bps >= 45.0   (3x RT)
    W3 wbur_bps >= 90.0   (6x RT)
    W4 uw range-decile >= 9 (top decile, TRAIN-frozen cut from v1)
  Dial 2 dip filter: OFF (owner concept) / ON (ret24 bottom quintile, agent comparison row)
8 rows total (4 x 2). No other asset/TF/filter/model.

Fixed per row: MKT next-bar-open entry, headline cost MKT_MKT=15bps RT,
TP = body_top + 1.5*wick_gap, time stop K=24, NO price stop, NO circuit breaker.

Columns: n, trades/month, win rate, avg net bps/trade, monthly net bps (compounded),
max DD, win rate green-only, win rate red-only, BH-significant (y/n).

BH-FDR q=0.05 across the 8 menu cells (per-row significance flag).
Delivers the menu and STOPS (no owner pick yet, no E-VAL).
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T
from scipy import stats

ATLAS = json.load(open(P.ATLAS_DIR / "atlas_cuts.json"))
SYM, TF = "SOLUSDT", "4h"
KEY = f"{SYM}-{TF}"
tr = pd.read_csv(P.RAW_DIR / f"{SYM}-FUTURES-2022-2026-{TF}.csv")
low = {c.strip().strip('"').lower(): c for c in tr.columns}
ren = {low[a]: a for a in ["time","open","high","low","close","volume"]}
tr = tr.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
tr = T.filter_window(tr, "TRAIN")                      # assert holdout excluded
O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
L=tr.low.values.astype(float);  C=tr.close.values.astype(float); n=len(tr)

rng_ = Hh - L
body_top = np.maximum(O, C)
wick_gap = Hh - body_top
valid = (rng_ > 0) & (wick_gap > 0)
# bps wick metric (per-candle, lookahead-free)
wbur_bps = np.where(valid, wick_gap / C * 1e4, np.nan)
# range-based uw fraction + decile (TRAIN-frozen, from v1)
uw = np.where(rng_>0, wick_gap / rng_, np.nan)
dq = np.array(ATLAS[KEY]["uw_deciles"])
uw_dec = np.where(np.isnan(uw), -1, np.searchsorted(dq, uw)+1)
# 24h return quintile (for dip filter)
ret24 = C / pd.Series(C).shift(24).values - 1.0
rq = np.array(ATLAS[KEY]["ret24_q"])
ret24_q = np.where(np.isnan(ret24), -1, np.searchsorted(rq, ret24)+1)
green = (C > O)
red = (C < O)

# entry = next bar open (MKT); require next bar exists
sig_all = np.where(valid)[0]
eb = sig_all + 1
ok = eb < n
sig = sig_all[ok]; eb = eb[ok]
bt = O[eb]                                  # MKT entry next-bar-open
tp = body_top[sig] + 1.5 * wick_gap[sig]    # TP formula (f=1.5)
is_green = green[sig]; is_red = red[sig]

# ---- replay (K=24 time stop, no price stop) from sim.py ----
def replay(eb_v, bt_v, tp_v, K=24):
    E=len(bt_v)
    starts=np.clip(eb_v,0,n-1)
    idx=np.clip(starts[:,None]+np.arange(48)[None,:],0,n-1)
    fhi=Hh[idx]; fcl=C[idx]
    tp_hit=fhi>=tp_v[:,None]; tp_idx=np.where(tp_hit.any(1),tp_hit.argmax(1),48)
    exit_idx=np.minimum(tp_idx,K)
    hit=fhi[np.arange(E),np.clip(exit_idx,0,47)]>=tp_v
    pnl=np.where(hit,(tp_v-bt_v)/bt_v*1e4,(fcl[np.arange(E),np.clip(exit_idx,0,47)]-bt_v)/bt_v*1e4)
    return pnl, hit

# exit dates for monthly aggregation
def monthly_metrics(pnl_net, eb_v, stake=0.02):
    # monthly net bps (compounded, additive expectation): net/trade x trades/month
    months=(pd.Timestamp("2024-12-31")-pd.Timestamp("2022-09-01")).days/30.44
    monthly_net = float(pnl_net.mean() * (len(pnl_net)/months))
    # max drawdown on an equity curve risking `stake` of equity per trade
    eq=pd.Series(np.cumprod(1 + stake*(pnl_net/1e4)))
    peak=eq.cummax(); dd=(eq-peak)/peak; maxdd=float(-dd.min())
    return monthly_net, maxdd

def boot_ci(x,n=2000,seed=42):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n); d0=0
    while d0<n:
        d=min(64,n-d0); idx=rng.integers(0,n_,size=(d,n_)); ms[d0:d0+d]=x[idx].mean(axis=1); d0+=d
    return tuple(np.quantile(ms,[0.025,0.975]))

WICK = {"W1":("bps",22.5), "W2":("bps",45.0), "W3":("bps",90.0), "W4":("dec",9)}
COST=15.0
rows=[]
for wname,(wmode,wval) in WICK.items():
    wick_mask = (wbur_bps[sig]>=wval) if wmode=="bps" else (uw_dec[sig]>=wval)
    for dip_on in (False, True):
        m = wick_mask & (ret24_q[sig]<=1 if dip_on else np.ones(len(sig),bool))
        if m.sum()<30:
            rows.append(dict(row=f"{wname}_{'DIP' if dip_on else 'BASE'}",n=0,trades_month=0,
                             win=0,net=0,monthly=0,maxdd=0,wr_green=0,wr_red=0,bh="n"))
            continue
        bt_v=bt[m]; tp_v=tp[m]; eb_v=eb[m]
        pnl_g,_=replay(eb_v,bt_v,tp_v,K=24)
        pnl_net=pnl_g-COST
        wr=float((pnl_net>0).mean())
        net=float(pnl_net.mean())
        lo,hi=boot_ci(pnl_net)
        se=(hi-lo)/(2*1.96); z=net/se if se>0 else 0.0
        pval=2*(1-stats.norm.cdf(abs(z))) if z>=0 else stats.norm.cdf(z)
        monthly,maxdd=monthly_metrics(pnl_net,eb_v)
        ntr=len(pnl_net)
        # color subsets
        g=pnl_net[is_green[m]]; r=pnl_net[is_red[m]]
        wrg=float((g>0).mean()) if len(g) else float("nan")
        wrr=float((r>0).mean()) if len(r) else float("nan")
        months=(pd.Timestamp("2024-12-31")-pd.Timestamp("2022-09-01")).days/30.44
        rows.append(dict(row=f"{wname}_{'DIP' if dip_on else 'BASE'}", n=ntr,
                         trades_month=round(ntr/months,1), win=round(wr,3),
                         net=round(net,2), monthly=round(monthly,1), maxdd=round(maxdd,3),
                         wr_green=round(wrg,3), wr_red=round(wrr,3),
                         ci_lo=round(lo,1), ci_hi=round(hi,1), pval=round(pval,6), bh="?"))

# BH-FDR across the 8 cells (q=0.05)
fam=pd.DataFrame([{k:r[k] for k in ("row","pval")} for r in rows if r["n"]>0])
if len(fam):
    p=np.clip(fam.pval.values.astype(float),1e-12,1.0)
    order=np.argsort(p); m=len(p); bh=np.empty(m)
    for i,rank in enumerate(order,1): bh[rank-1]=(i/m)*0.05
    sig=p<=bh
    fam["bh"]=sig
    bhmap=dict(zip(fam.row,fam.bh))
    for r in rows:
        if r["n"]>0: r["bh"]="y" if bhmap.get(r["row"],False) else "n"
        else: r["bh"]="n"

out=pd.DataFrame(rows)
out.to_csv(P.V2_OUTPUTS/"redir_w1_menu.csv",index=False)

print("=== 8-ROW MENU (TRAIN, SOL-4h, 15bps MKT_MKT floor) ===")
print(out[["row","n","trades_month","win","net","monthly","maxdd","wr_green","wr_red","bh","ci_lo","ci_hi"]].to_string(index=False))
print("\nBH-FDR q=0.05 across 8 cells:",
      int((out.bh=="y").sum()), "significant")
