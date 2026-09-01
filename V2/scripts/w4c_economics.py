"""OF-W4c: ECONOMIC LAYER on the atlas - per-condition EXPECTANCY, not just fill rates.

Per series, per ENTRY {MKT next-open taker | PB limit-at-body maker}, per EXIT
(TP f{1.0, 1.5} x SL{low,mid} x Tmax{48}): simulate every big-wick event trade
(no occupancy - per-trade stats; strict occupancy returns for the flagship only),
then aggregate under condition masks:
  ALL / volq<=1 (quiet) / uwd in 7-8 / uwd in 7-9 / prev==-1 / smaal==-1 /
  C3 = uwd>=8 & volq<=1 / C6 = uwd>=9 & trend<=1 / CQ7 = uwd 7-8 & volq<=1.

Reports net bps/trade (taker RT 11, maker RT 4), WR, PF, N per cell.
Selection flags: CI>0 (bootstrap 2000), N>=300, neighbor-exit not deeply negative.
TRAIN ONLY.
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
FEE_T, FEE_M = 11.0, 4.0   # RT bps

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
    ("ICPUSDT","4h",  SRC/r"ICPUSDT-Futures-2022-2026-4h.csv".replace("Futures","FUTURES")),
    ("BTCUSDT","15m", SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-15m.csv"),
    ("BTCUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-1h.csv"),
    ("ETHUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\ETHUSDT-FUTURES-2022-2026-1h.csv"),
]
TF_MIN = {"5m":5,"15m":15,"30m":30,"1h":60,"4h":240}

def load_train(path):
    df = pd.read_csv(path)
    low = {c.strip().strip('"').lower(): c for c in df.columns}
    ren = {}
    for std, al in {"time":["time"],"open":["open"],"high":["high"],
                    "low":["low"],"close":["close"],"volume":["volume"]}.items():
        ren[low[al[0]]] = std
    df = df.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
    return df.drop_duplicates("time").sort_values("time").reset_index(drop=True)

def boot_ci(x, n=2000, seed=5):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n)
    d0=0
    while d0<n:
        d=min(64,n-d0); idx=rng.integers(0,n_,size=(d,n_)); ms[d0:d0+d]=x[idx].mean(axis=1); d0+=d
    return tuple(np.quantile(ms,[0.025,0.975]))

CONDS = {
    "ALL":       lambda F: np.ones(len(F["uwd"]), bool),
    "quiet":     lambda F: F["volq"]<=1,
    "uwd78":     lambda F: (F["uwd"]>=7)&(F["uwd"]<=8),
    "uwd79":     lambda F: (F["uwd"]>=7)&(F["uwd"]<=9),
    "prevBear":  lambda F: F["prev"]<0,
    "smaBelow":  lambda F: F["smaal"]<0,
    "C3_w8q":    lambda F: (F["uwd"]>=8)&(F["volq"]<=1),
    "C6_w9dip":  lambda F: (F["uwd"]>=9)&(F["trend"]<=1),
    "CQ7_w78q":  lambda F: (F["uwd"]>=7)&(F["uwd"]<=8)&(F["volq"]<=1),
}

rows=[]
for sym, tf, path in DATA_FILES:
    key=f"{sym}-{tf}"; cuts=ATLAS_CUTS[key]
    tr=load_train(path); tr=tr[(tr.time>=TRAIN_START_MS)&(tr.time<TRAIN_END_MS)].reset_index(drop=True)
    O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
    L=tr.low.values.astype(float);  C=tr.close.values.astype(float); V=tr.volume.values.astype(float)
    n=len(tr)
    rng_=Hh-L
    uw=np.where(rng_>0,(Hh-np.maximum(O,C))/rng_,np.nan)
    lw=np.where(rng_>0,(np.minimum(O,C)-L)/rng_,np.nan)
    bs_=np.where(rng_>0,np.abs(C-O)/rng_,np.nan)
    atr14=pd.Series(rng_).rolling(14).mean().shift(1).values
    rx=rng_/atr14
    vma=pd.Series(V).rolling(20).mean().shift(1).values; vr=V/vma
    ret24=C/pd.Series(C).shift(24).values-1.0
    sma50=pd.Series(C).rolling(50).mean().shift(1).values
    smaal=np.where(C>sma50,1,np.where(C<sma50,-1,0)).astype(float)
    prev=pd.Series(np.sign(C-O)).shift(1).values
    dq=np.array(cuts["uw_deciles"])

    sig=np.where((C>O)&(rng_>0)&(uw>=cuts["uw_tercile"])
                 &~np.isnan(rx)&~np.isnan(vr)&~np.isnan(ret24)&~np.isnan(prev))[0]
    if len(sig)==0: continue
    F=dict(
        uwd=np.searchsorted(dq,uw[sig])+1,
        trend=np.searchsorted(np.array(cuts["ret24_q"]),ret24[sig]),
        volq=np.searchsorted(np.array(cuts["vr_q"]),vr[sig]),
        rng_q=np.searchsorted(np.array(cuts["rx_q"]),rx[sig]),
        prev=prev[sig], smaal=smaal[sig],
        typ=np.where(bs_[sig]>=0.7,0,np.where(lw[sig]>=0.33,2,1)),
    )
    bt=np.maximum(O[sig],C[sig]); bb=np.minimum(O[sig],C[sig])
    wh=Hh[sig]; slo=L[sig]; sidx=sig

    Tmax=48
    for entry in ["MKT","PB"]:
        # entry bars/prices per event
        if entry=="MKT":
            eb=sidx+1; ok=eb<n
            ep=O[np.clip(eb,0,n-1)]
        else:
            ep=bb.copy(); eb=np.full(len(sidx),-1)
            for k,i in enumerate(sidx):
                lo_b,hi_b=i+1,min(i+12,n-1)
                jj=np.flatnonzero(L[lo_b:hi_b+1]<bb[k]*(1-1e-4))
                eb[k]=lo_b+jj[0] if len(jj) else -1
            ok=eb>=0
        for fv in [1.0,1.5]:
            tp=bt+fv*(wh-bt)
            for slm in ["low","mid"]:
                sl=slo if slm=="low" else 0.5*(bb+slo)
                valid=ok&(tp>ep)
                vi=np.where(valid)[0]
                pnl_g=np.full(len(sidx),np.nan); oc=np.empty(len(sidx),dtype="U4")
                for k in vi:
                    j=int(eb[k])
                    start=j if entry=="PB" else j+1
                    end=min(j+Tmax,n-1)
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
                    m=fn(F)&valid&~np.isnan(pnl_g)
                    x=pnl_g[m]
                    if len(x)<30: continue
                    lo,hi=boot_ci(x)
                    wr=float((x>0).mean()); pf=float(x[x>0].sum()/max(1e-9,-x[x<=0].sum()))
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,sl=slm,
                        N=len(x),
                        net_taker=round(float(x.mean())-FEE_T,2),
                        net_maker=round(float(x.mean())-FEE_M,2),
                        ci_lo_m=round(float(x.mean()-FEE_M-lo),0)*0+round(lo-FEE_M,1),
                        ci_hi_m=round(hi-FEE_M,1),
                        wr=round(wr,3), pf=round(pf,2)))
    print(f"{key} done", flush=True)

R=pd.DataFrame(rows)
R["sig_maker"]=R.ci_lo_m>0
R.to_csv(OUT/"w4c_economics.csv",index=False)
print("\n=== CELLS WITH CI>0 UNDER MAKER, sorted by net_maker ===")
good=R[R.sig_maker].sort_values("net_maker",ascending=False)
print(good.head(40).to_string(index=False))
print(f"\ntotal cells={len(R)}, CI>0 maker={int(R.sig_maker.sum())}, "
      f"CI>0 count by cond:\n{R[R.sig_maker].groupby('cond').size().to_string()}")
