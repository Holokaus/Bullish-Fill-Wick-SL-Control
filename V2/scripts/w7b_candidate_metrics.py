"""W7b: risk metrics (calendar-aligned Sharpe/Calmar/Sortino, directive s4.2) and
compounded equity for the frozen candidate cell on TRAIN:
  SOL-4h, C6_w9dip, MKT entry f=1.5, TIME stop K=24, PB_MKT cost (11.5bps).
Also reports the no-funding and funding-naive (4h funding deferred per s13.4) figures.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T

ATLAS_CUTS = json.load(open(P.ATLAS_DIR/"atlas_cuts.json"))
SYM,TF="SOLUSDT","4h"
tr=pd.read_csv(P.RAW_DIR/"SOLUSDT-FUTURES-2022-2026-4h.csv")
low={c.strip().strip('"').lower():c for c in tr.columns}
ren={low[a]:a for a in ["time","open","high","low","close","volume"]}
tr=tr.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
tr=tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
tr=T.filter_window(tr,"TRAIN")
O=tr.open.values.astype(float);Hh=tr.high.values.astype(float);L=tr.low.values.astype(float)
C=tr.close.values.astype(float);V=tr.volume.values.astype(float);n=len(tr)
rng_=Hh-L; uw=np.where(rng_>0,(Hh-np.maximum(O,C))/rng_,np.nan)
rx=rng_/pd.Series(rng_).rolling(14).mean().shift(1).values
vr=V/pd.Series(V).rolling(20).mean().shift(1).values
ret24=C/pd.Series(C).shift(24).values-1.0
sma50=pd.Series(C).rolling(50).mean().shift(1).values
smaal=np.where(C>sma50,1,np.where(C<sma50,-1,0)).astype(float)
prev=pd.Series(np.sign(C-O)).shift(1).values
dq=np.array(ATLAS_CUTS[f"{SYM}-{TF}"]["uw_deciles"])
sig=np.where((C>O)&(rng_>0)&(uw>=ATLAS_CUTS[f"{SYM}-{TF}"]["uw_tercile"])&~np.isnan(rx)&~np.isnan(vr)&~np.isnan(ret24)&~np.isnan(prev))[0]
bt=np.maximum(O[sig],C[sig]);bb=np.minimum(O[sig],C[sig]);wh=Hh[sig]
# condition C6: uwd>=9 & trend<=1
uwd=np.searchsorted(dq,uw[sig])+1
trend=np.searchsorted(np.array(ATLAS_CUTS[f"{SYM}-{TF}"]["ret24_q"]),ret24[sig])
m=(uwd>=9)&(trend<=1)
si=sig[m]; btv=bt[m];tpv=btv+1.5*(wh[m]-btv);bbv=bb[m];ebv=si+1;ok=ebv<n
vi=np.where(ok&(tpv>btv))[0]; sidx_v=si[vi];bt_v=btv[vi];tp_v=tpv[vi];eb_v=ebv[vi]
K=24
starts=np.where(eb_v>=0,eb_v,0)
idx=np.clip(starts[:,None]+np.arange(48)[None,:],0,n-1)
fhi=Hh[idx];fcl=C[idx]
tp_hit=fhi>=tp_v[:,None];tp_idx=np.where(tp_hit.any(1),tp_hit.argmax(1),48)
exit_idx=np.minimum(tp_idx,K)
hit=fhi[np.arange(len(sidx_v)),np.clip(exit_idx,0,48-1)]>=tp_v
pnl_gross=np.where(hit,(tp_v-bt_v)/bt_v*1e4,(fcl[np.arange(len(sidx_v)),np.clip(exit_idx,0,48-1)]-bt_v)/bt_v*1e4)
# exit time -> date
exit_bar=np.clip(exit_idx,0,n-1)  # bar index within replay; absolute = start+exit_bar
abs_exit=(starts+exit_idx).astype(int)
exit_ts=tr.time.values[np.clip(abs_exit,0,n-1)]
COST=11.5
pnl_net=pnl_gross-COST
# calendar-aligned daily series
dates=pd.to_datetime(exit_ts,unit="ms",utc=True).floor("D")
daily=pd.Series(pnl_net,index=dates).groupby(level=0).sum()
full=pd.date_range(daily.index.min(),daily.index.max(),freq="D",tz="UTC")
daily=daily.reindex(full,fill_value=0.0)
ret=daily/1e4  # bps->frac per day
mean=ret.mean(); sd=ret.std(ddof=1); sd_neg=ret[ret<0].std(ddof=1)
sharpe=mean/sd*np.sqrt(365) if sd>0 else 0.0
sortino=mean/sd_neg*np.sqrt(365) if (sd_neg and sd_neg>0) else 0.0
eq=(1+ret).cumprod()
peak=eq.cummax(); dd=(eq-peak)/peak; maxdd=float(-dd.min())
calmar=(eq.iloc[-1]**(365/len(ret))-1)/maxdd if maxdd>0 else float('nan')
print(f"Frozen candidate TRAIN metrics (SOL-4h C6_w9dip MKT f1.5 TIME K24, cost {COST}bps):")
print(f"  n trades = {len(pnl_net)}")
print(f"  win rate = {float((pnl_net>0).mean()):.3f}")
print(f"  net bps/trade (mean) = {pnl_net.mean():.2f}")
print(f"  CAGR (compounded)   = {eq.iloc[-1]**(365/len(ret))-1:.3f}")
print(f"  MaxDD (compounded)  = {maxdd:.3f}")
print(f"  Sharpe (cal-aligned)= {sharpe:.2f}")
print(f"  Sortino             = {sortino:.2f}")
print(f"  Calmar              = {calmar:.2f}")
# save
out=dict(n=int(len(pnl_net)),win_rate=round(float((pnl_net>0).mean()),3),
         net_bp_per_trade=round(float(pnl_net.mean()),2),cagr=round(float(eq.iloc[-1]**(365/len(ret))-1),4),
         maxdd=round(maxdd,4),sharpe=round(float(sharpe),2),sortino=round(float(sortino),2),calmar=round(float(calmar),2),
         cost_bps=COST,k=K,asset=SYM,tf=TF,cond="C6_w9dip",entry="MKT",f=1.5)
json.dump(out,open(P.V2_OUTPUTS/"w7_candidate_metrics.json","w"),indent=1)
print("saved",P.V2_OUTPUTS/"w7_candidate_metrics.json")
