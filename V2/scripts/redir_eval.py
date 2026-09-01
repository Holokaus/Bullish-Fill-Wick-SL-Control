"""E-VAL (one-shot): W3_BASE frozen spec on 2025-01-01 -> 2025-06-30.

Sign-off locked criteria (FROZEN_CANDIDATE.md s6):
  C1 net expectancy @ 15bps flat config: bootstrap CI lo (B=2000, seed=42) > 0  AND point >= 30 bps
  C2 worst BTC-regime bucket net > -15 bps
Sizing: 2% stake/trade, overlapping allowed, per-trade additive (menu convention).
Out-of-sample discipline: reserved window 2025-07-01->2026-06-30 NEVER touched.
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T

SYM, TF = "SOLUSDT", "4h"
tr = pd.read_csv(P.RAW_DIR / f"{SYM}-FUTURES-2022-2026-{TF}.csv")
low = {c.strip().strip('"').lower(): c for c in tr.columns}
ren = {low[a]: a for a in ["time","open","high","low","close","volume"]}
tr = tr.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
tr = T.filter_window(tr, "EVAL")                       # assert: only 2025-01-01..2025-06-30
O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
L=tr.low.values.astype(float);  C=tr.close.values.astype(float); n=len(tr)
rng_=Hh-L; body_top=np.maximum(O,C); wick_gap=Hh-body_top
valid=(rng_>0)&(wick_gap>0)
wbur_bps=np.where(valid, wick_gap/C*1e4, np.nan)
sig=np.where(valid)[0]; eb=sig+1; ok=eb<n; sig=sig[ok]; eb=eb[ok]
bt=O[eb]; tp=body_top[sig]+1.5*wick_gap[sig]

# ---- replay (MKT entry, K=24, no price stop) ----
def replay(eb_v, bt_v, tp_v, K=24):
    E=len(bt_v); starts=np.clip(eb_v,0,n-1)
    idx=np.clip(starts[:,None]+np.arange(48)[None,:],0,n-1)
    fhi=Hh[idx]; fcl=C[idx]
    tph=fhi>=tp_v[:,None]; tpi=np.where(tph.any(1),tph.argmax(1),48)
    ei=np.minimum(tpi,K); hit=fhi[np.arange(E),np.clip(ei,0,47)]>=tp_v
    gross=np.where(hit,(tp_v-bt_v)/bt_v*1e4,(fcl[np.arange(E),np.clip(ei,0,47)]-bt_v)/bt_v*1e4)
    return gross, hit, np.clip(ei,0,47).astype(int)

gross,hit,exitk=replay(eb,bt,tp,K=24)
# cost configs
cost_15=np.full(len(gross),15.0)
cost_4=np.full(len(gross),4.0)
cost_true=5.5+np.where(hit,2.0,5.5)          # entry taker 5.5; exit maker 2 / taker 5.5
net15=gross-cost_15; net4=gross-cost_4; net_true=gross-cost_true

# ---- C1 bootstrap (B=2000, seed=42) on 15bps flat ----
def boot_ci(x,B=2000,seed=42):
    x=np.asarray(x,float); n_=len(x); rng=np.random.default_rng(seed)
    ms=np.empty(B)
    for d0 in range(0,B,64):
        d=min(64,B-d0); ms[d0:d0+d]=x[rng.integers(0,n_,size=(d,n_))].mean(axis=1)
    return ms.mean(), tuple(np.quantile(ms,[0.025,0.975]))

mean15, (lo15,hi15)=boot_ci(net15)
C1 = (lo15>0) and (mean15>=30)

# ---- BTC-regime proxy (derive from BTCUSDT 1h -> 4h) ----
btc=pd.read_csv(P.RAW_DIR/"BTCUSDT-FUTURES-2022-2026-1h.csv")
bl={c.strip().strip('"').lower():c for c in btc.columns}
inv={v:k for k,v in bl.items()}
btc=btc.rename(columns=inv)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
btc=btc[["time","open","high","low","close"]].drop_duplicates("time").sort_values("time").reset_index(drop=True)
# aggregate 1h -> 4h
b=btc.set_index(pd.to_datetime(btc.time,unit="ms",utc=True))
b4=b.resample("4h").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()
b4["ret24"]=b4["close"].pct_change(6)              # 6x4h = 24h
b4["tr"]=(b4["high"]-b4["low"])/b4["close"]
b4["volr"]=b4["tr"]/b4["tr"].rolling(30,min_periods=5).median()
def regime(r):
    if pd.isna(r.ret24): return "RANGE"
    if r.volr>1.5: return "VOL_EXPANSION"
    if r.ret24>0.01: return "TREND_UP"
    if r.ret24<-0.01: return "TREND_DOWN"
    return "RANGE"
b4["regime"]=b4.apply(regime,axis=1)
b4idx=b4["regime"]
# map each trade entry time -> BTC 4h regime
entry_ts=tr.time.values[eb]
reg_at_entry=pd.to_datetime(entry_ts,unit="ms",utc=True).floor("4h").map(b4idx.to_dict()).fillna("RANGE").values
df=pd.DataFrame({"entry":entry_ts,"regime":reg_at_entry,"net15":net15,"gross":gross})

# ---- C2 worst BTC-regime bucket ----
bucket=df.groupby("regime")["net15"].agg(["mean","count"])
worst_reg=bucket["mean"].idxmin(); worst_val=bucket.loc[worst_reg,"mean"]
C2 = worst_val > -15

# ---- sizing equity (2% stake, overlapping) ----
eq=pd.Series(np.cumprod(1+0.02*(net15/1e4)))
peak=eq.cummax(); dd=(eq-peak)/peak; maxdd=float(-dd.min())

print("="*60)
print("E-VAL  W3_BASE  2025-01-01 -> 2025-06-30  (one-shot)")
print("="*60)
print(f"n trades            : {len(gross)}")
print(f"net/trade @15bps    : {mean15:+.2f} bps  CI[{lo15:.2f},{hi15:.2f}]")
print(f"net/trade @4bps     : {net4.mean():+.2f} bps")
print(f"net/trade true-cost : {net_true.mean():+.2f} bps")
print(f"win rate (15bps)    : {float((net15>0).mean())*100:.1f}%")
print(f"2% stake maxDD      : {maxdd*100:.1f}%")
print("-"*60)
print("BTC-regime buckets (net15 bps):")
for r in bucket.index:
    print(f"  {r:14s}  mean={bucket.loc[r,'mean']:+.2f}  n={int(bucket.loc[r,'count'])}")
print(f"worst bucket        : {worst_reg} = {worst_val:+.2f} bps")
print("-"*60)
print(f"C1 net CI lo>0 & point>=30 : {C1}   (lo={lo15:.2f}>0? {lo15>0}, point={mean15:.2f}>=30? {mean15>=30})")
print(f"C2 worst bucket>-15bps     : {C2}   ({worst_reg}={worst_val:+.2f})")
print(f"\nE-VAL VERDICT: {'PASS -> promote (fire E-LOCKBOX next)' if (C1 and C2) else 'FAIL -> do not promote'}")
print(f"  failing: {[c for c,v in [('C1',C1),('C2',C2)] if not v]}")

# save
out={"window":"2025-01-01..2025-06-30","n":int(len(gross)),
     "net15_mean":round(mean15,2),"net15_ci_lo":round(lo15,2),"net15_ci_hi":round(hi15,2),
     "net4_mean":round(net4.mean(),2),"net_true_mean":round(net_true.mean(),2),
     "win15":round(float((net15>0).mean()),4),"maxdd_2pct":round(maxdd,4),
     "C1":bool(C1),"C2":bool(C2),
     "worst_regime":worst_reg,"worst_regime_net":round(worst_val,2),
     "buckets":{r:{"mean":round(bucket.loc[r,'mean'],2),"n":int(bucket.loc[r,'count'])} for r in bucket.index},
     "verdict":"PASS" if (C1 and C2) else "FAIL"}
json.dump(out, open(P.V2_OUTPUTS/"eval_result.json","w"), indent=2)
print("\nwrote V2/outputs/eval_result.json")
