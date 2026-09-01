"""OF-W5: NO-SL ECONOMIC LAYER — directly answers the owner's SL/backtest question.

Reuses the W4c machinery but adds a NO-SL exit mode (exit on TP touch OR horizon
close, never a stop). This proves two things:
  (1) a backtest does NOT require a stop-loss to run — SL is optional risk control,
      not a simulator prerequisite;
  (2) the project ALREADY models SL (low/mid), so "no SL" was never the blocker.

It also surfaces the cells whose point-estimate net expectancy sits ABOVE the
cost line (net_maker > 0), i.e. the optimization targets, under all three exit
modes. TRAIN window only. No lockbox / validation peek.
"""
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P
import lib.time_gates as T

STUDY = P.V2
SRC   = P.RAW_DIR
OUT   = P.V2_OUTPUTS
ATLAS_CUTS = json.load(open(P.ATLAS_DIR/"atlas_cuts.json"))

TRAIN_START_MS = T.TRAIN_START
TRAIN_END_MS   = T.TRAIN_END
FEE_T, FEE_M   = 11.0, 4.0   # RT bps (taker / maker)

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
    ren = {low[a]: a for a in ["time","open","high","low","close","volume"]}
    df = df.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
    return df.drop_duplicates("time").sort_values("time").reset_index(drop=True)

def boot_ci(x, n=2000, seed=5):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n); d0=0
    while d0<n:
        d=min(64,n-d0); idx=rng.integers(0,n_,size=(d,n_)); ms[d0:d0+d]=x[idx].mean(axis=1); d0+=d
    return tuple(np.quantile(ms,[0.025,0.975]))

CONDS = {
    "ALL":      lambda F: np.ones(len(F["uwd"]), bool),
    "quiet":    lambda F: F["volq"]<=1,
    "uwd78":    lambda F: (F["uwd"]>=7)&(F["uwd"]<=8),
    "uwd79":    lambda F: (F["uwd"]>=7)&(F["uwd"]<=9),
    "prevBear": lambda F: F["prev"]<0,
    "smaBelow": lambda F: F["smaal"]<0,
    "C3_w8q":   lambda F: (F["uwd"]>=8)&(F["volq"]<=1),
    "C6_w9dip": lambda F: (F["uwd"]>=9)&(F["trend"]<=1),
    "CQ7_w78q": lambda F: (F["uwd"]>=7)&(F["uwd"]<=8)&(F["volq"]<=1),
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
    rx=rng_/pd.Series(rng_).rolling(14).mean().shift(1).values
    vr=V/pd.Series(V).rolling(20).mean().shift(1).values
    ret24=C/pd.Series(C).shift(24).values-1.0
    sma50=pd.Series(C).rolling(50).mean().shift(1).values
    smaal=np.where(C>sma50,1,np.where(C<sma50,-1,0)).astype(float)
    prev=pd.Series(np.sign(C-O)).shift(1).values
    dq=np.array(cuts["uw_deciles"])
    sig=np.where((C>O)&(rng_>0)&(uw>=cuts["uw_tercile"])
                 &~np.isnan(rx)&~np.isnan(vr)&~np.isnan(ret24)&~np.isnan(prev))[0]
    if len(sig)==0: continue
    F=dict(uwd=np.searchsorted(dq,uw[sig])+1, trend=np.searchsorted(np.array(cuts["ret24_q"]),ret24[sig]),
           volq=np.searchsorted(np.array(cuts["vr_q"]),vr[sig]), prev=prev[sig], smaal=smaal[sig],
           typ=np.where(np.abs(C-O)[sig]/rng_[sig]>=0.7,0,np.where((np.minimum(O,C)-L)[sig]/rng_[sig]>=0.33,2,1)))
    bt=np.maximum(O[sig],C[sig]); bb=np.minimum(O[sig],C[sig]); wh=Hh[sig]; slo=L[sig]; sidx=sig
    Tmax=48
    for entry in ["MKT","PB"]:
        if entry=="MKT":
            eb=sidx+1; ok=eb<n; ep=O[np.clip(eb,0,n-1)]
        else:
            ep=bb.copy(); eb=np.full(len(sidx),-1)
            for k,i in enumerate(sidx):
                lo_b,hi_b=i+1,min(i+12,n-1)
                jj=np.flatnonzero(L[lo_b:hi_b+1]<bb[k]*(1-1e-4))
                eb[k]=lo_b+jj[0] if len(jj) else -1
            ok=eb>=0
        for fv in [1.0,1.5]:
            tp=bt+fv*(wh-bt)
            for slname,slv in [("low",slo),("mid",0.5*(bb+slo)),("NOSL",np.full(len(sidx),-np.inf))]:
                valid=ok&(tp>ep); vi=np.where(valid)[0]
                pnl_g=np.full(len(sidx),np.nan)
                for k in vi:
                    j=int(eb[k]); start=j if entry=="PB" else j+1; end=min(j+Tmax,n-1)
                    if start>end: continue
                    segH=Hh[start:end+1]; segL=L[start:end+1]
                    i_sl=np.flatnonzero(segL<=slv[k]); i_tp=np.flatnonzero(segH>=tp[k])
                    if len(i_sl)>0 and (len(i_tp)==0 or i_sl[0]<=i_tp[0]):
                        xa=int(i_sl[0]); opx=O[start+xa]; xp=slv[k] if opx>=slv[k] else min(opx,slv[k])
                    elif len(i_tp)>0:
                        xp=tp[k]
                    else:
                        xp=C[end]
                    pnl_g[k]=(xp-ep[k])/ep[k]*1e4
                for cname,fn in CONDS.items():
                    m=fn(F)&valid&~np.isnan(pnl_g); x=pnl_g[m]
                    if len(x)<30: continue
                    lo,hi=boot_ci(x)
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,exit=slname,
                        N=len(x), net_taker=round(float(x.mean())-FEE_T,2),
                        net_maker=round(float(x.mean())-FEE_M,2),
                        ci_lo_m=round(lo-FEE_M,1), ci_hi_m=round(hi-FEE_M,1),
                        wr=round(float((x>0).mean()),3)))
    print(f"{key} done", flush=True)

R=pd.DataFrame(rows)
R["sig_maker"]=R.ci_lo_m>0
R.to_csv(OUT/"w5_nosl_economics.csv", index=False)
print("\n===== SUMMARY (TRAIN, all exit modes) =====")
for ex in ["low","mid","NOSL"]:
    sub=R[R.exit==ex]
    pos=(sub.net_maker>0).sum()
    sig=sub.sig_maker.sum()
    best=sub.sort_values("net_maker",ascending=False).head(5)
    print(f"\nexit={ex}: cells={len(sub)}  net_maker>0 (above cost, pt-est)={pos}  "
          f"CI>0 (significant)={sig}")
    print(best[["series","cond","entry","f","N","net_maker","ci_lo_m","ci_hi_m"]].to_string(index=False))
