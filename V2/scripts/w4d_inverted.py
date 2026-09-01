"""OF-W4d: INVERTED GATES - loud/high-energy wick events (owner: 'not targeting cents').

Hypothesis from atlas r24 stats: HIGH relative volume + extreme wicks fill LESS often
but carry bigger forward returns -> maybe the profitable gate is INVERTED.
Conditions: loud(volq>=3), uwd10, uwd910, prevBull, smaAbove, trendHi(trend>=3),
            XL = uwd>=9 & volq>=3 & trend>=3.
Entries MKT/PB, exits f{1.0,1.5} x sl{low,mid}, Tmax 48. TRAIN only.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

STUDY = Path(r"C:\Users\A\Bullish-Fill-Wick\V2")
SRC = Path(r"C:\Users\A\Downloads\opencode-bybit")
OUT = STUDY/"outputs"
ATLAS_CUTS = json.load(open(OUT/"atlas"/"atlas_cuts.json"))
TRAIN_START_MS = int(pd.Timestamp("2022-09-01").value // 10**6)
TRAIN_END_MS   = int(pd.Timestamp("2025-01-01").value // 10**6)
FEE_T, FEE_M = 11.0, 4.0

DATA_FILES = [
    ("SOLUSDT","5m",  SRC/r"Z-attempt-2\SOLUSDT-FUTURES-2022-2026-5m.csv"),
    ("SOLUSDT","15m", SRC/r"Z-attempt-2\SOLUSDT-FUTURES-2022-2026-15m.csv"),
    ("SOLUSDT","30m", SRC/r"SOLUSDT-FUTURES-2021-2026-30m.csv"),
    ("SOLUSDT","1h",  SRC/r"SOLUSDT-FUTURES-2022-2026-1h.csv"),
    ("SOLUSDT","4h",  SRC/r"SOLUSDT-FUTURES-2022-2026-4h.csv"),
    ("ICPUSDT","5m",  SRC/r"Z-attempt-2\ICPUSDT-FUTURES-2022-2026-5m.csv"),
    ("ICPUSDT","15m", SRC/r"Z-attempt-2\ICPUSDT-FUTURES-2022-2026-15m.csv"),
    ("ICPUSDT","30m", SRC/r"ICPUSDT-FUTURES-2022-2026-30m.csv"),
    ("ICPUSDT","1h",  SRC/r"ICPUSDT-FUTURES-2022-2026-1h.csv"),
    ("ICPUSDT","4h",  SRC/r"ICPUSDT-FUTURES-2022-2026-4h.csv"),
    ("BTCUSDT","15m", SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-15m.csv"),
    ("BTCUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-1h.csv"),
    ("ETHUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\ETHUSDT-FUTURES-2022-2026-1h.csv"),
]

def load_train(path):
    df = pd.read_csv(path)
    low = {c.strip().strip('"').lower(): c for c in df.columns}
    ren = {low[al[0]]: std for std, al in
           {"time":["time"],"open":["open"],"high":["high"],"low":["low"],
            "close":["close"],"volume":["volume"]}.items()}
    df = df.rename(columns=ren)[list(ren.values())].apply(pd.to_numeric)
    return df.drop_duplicates("time").sort_values("time").reset_index(drop=True)

def boot_ci(x, n=2000, seed=5):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n); d0=0
    while d0<n:
        d=min(64,n-d0); idx=rng.integers(0,n_,size=(d,n_)); ms[d0:d0+d]=x[idx].mean(axis=1); d0+=d
    return tuple(np.quantile(ms,[0.025,0.975]))

CONDS = {
    "loud":     lambda F: F["volq"]>=3,
    "uwd10":    lambda F: F["uwd"]>=10,
    "uwd910":   lambda F: F["uwd"]>=9,
    "prevBull": lambda F: F["prev"]>0,
    "smaAbove": lambda F: F["smaal"]>0,
    "trendHi":  lambda F: F["trend"]>=3,
    "XL":       lambda F: (F["uwd"]>=9)&(F["volq"]>=3),
    "XLtrend":  lambda F: (F["uwd"]>=9)&(F["volq"]>=3)&(F["trend"]>=3),
}
rows=[]
for sym, tf, path in DATA_FILES:
    key=f"{sym}-{tf}"; cuts=ATLAS_CUTS[key]
    tr=load_train(path); tr=tr[(tr.time>=TRAIN_START_MS)&(tr.time<TRAIN_END_MS)].reset_index(drop=True)
    O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
    L=tr.low.values.astype(float);  C=tr.close.values.astype(float); V=tr.volume.values.astype(float)
    n=len(tr); rng_=Hh-L
    uw=np.where(rng_>0,(Hh-np.maximum(O,C))/rng_,np.nan)
    atr=pd.Series(rng_).rolling(14).mean().shift(1).values; rx=rng_/atr
    vr=V/pd.Series(V).rolling(20).mean().shift(1).values
    ret24=C/pd.Series(C).shift(24).values-1.0
    sma50=pd.Series(C).rolling(50).mean().shift(1).values
    smaal=np.where(C>sma50,1,np.where(C<sma50,-1,0))
    prev=pd.Series(np.sign(C-O)).shift(1).values
    dq=np.array(cuts["uw_deciles"])
    sig=np.where((C>O)&(rng_>0)&(uw>=cuts["uw_tercile"])
                 &~np.isnan(rx)&~np.isnan(vr)&~np.isnan(ret24)&~np.isnan(prev))[0]
    if len(sig)==0: continue
    F=dict(uwd=np.searchsorted(dq,uw[sig])+1,
           trend=np.searchsorted(np.array(cuts["ret24_q"]),ret24[sig]),
           volq=np.searchsorted(np.array(cuts["vr_q"]),vr[sig]),
           prev=prev[sig], smaal=smaal[sig])
    bt=np.maximum(O[sig],C[sig]); bb=np.minimum(O[sig],C[sig]); wh=Hh[sig]; slo=L[sig]
    Tmax=48
    for entry in ["MKT","PB"]:
        if entry=="MKT":
            eb=sidx=sig; eb=sidx+1; ok=eb<n; ep=O[np.clip(eb,0,n-1)]
        else:
            ep=bb.copy(); eb=np.full(len(sig),-1)
            for k,i in enumerate(sig):
                lo_b,hi_b=i+1,min(i+12,n-1)
                jj=np.flatnonzero(L[lo_b:hi_b+1]<bb[k]*(1-1e-4))
                eb[k]=lo_b+jj[0] if len(jj) else -1
            ok=eb>=0
        for fv in [1.0,1.5]:
            tp=bt+fv*(wh-bt)
            for slm in ["low","mid"]:
                sl=slo if slm=="low" else 0.5*(bb+slo)
                valid=ok&(tp>ep)
                pnl_g=np.full(len(sig),np.nan)
                for k in np.where(valid)[0]:
                    j=int(eb[k]); start=j if entry=="PB" else j+1; end=min(j+Tmax,n-1)
                    if start>end: continue
                    segH=Hh[start:end+1]; segL=L[start:end+1]
                    i_sl=np.flatnonzero(segL<=sl[k]); i_tp=np.flatnonzero(segH>=tp[k])
                    if len(i_sl)>0 and (len(i_tp)==0 or i_sl[0]<=i_tp[0]):
                        xa=int(i_sl[0]); opx=O[start+xa]; xp=sl[k] if opx>=sl[k] else min(opx,sl[k])
                    elif len(i_tp)>0:
                        xa=int(i_tp[0]); xp=tp[k]
                    else:
                        xp=C[end]
                    pnl_g[k]=(xp-ep[k])/ep[k]*1e4
                for cname,fn in CONDS.items():
                    m=fn(F)&valid&~np.isnan(pnl_g); x=pnl_g[m]
                    if len(x)<30: continue
                    lo,hi=boot_ci(x)
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,sl=slm,N=len(x),
                        net_taker=round(float(x.mean())-FEE_T,2),
                        net_maker=round(float(x.mean())-FEE_M,2),
                        ci_lo_m=round(lo-FEE_M,1), ci_hi_m=round(hi-FEE_M,1),
                        wr=round(float((x>0).mean()),3)))
    print(key,"done",flush=True)

R=pd.DataFrame(rows); R["sig_maker"]=R.ci_lo_m>0
R.to_csv(OUT/"w4d_inverted_gates.csv",index=False)
print("\n=== TOP 15 INVERTED-GATE CELLS by net_maker ===")
print(R.sort_values("net_maker",ascending=False).head(15).to_string(index=False))
print(f"\ncells={len(R)} CI>0={int(R.sig_maker.sum())}")
