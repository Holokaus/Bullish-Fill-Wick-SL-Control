"""W7: FLAGSHIP CORRECTED-COST STUDY — SOLUSDT-4h (Track 2 primary candidate).

Honest cost stack (directive s13.3): PB_PB=4, PB_MKT=11.5, MKT_MKT=15 bps RT.
Tests entry{PB,MKT} x f{1.0,1.5} x exit{NOSL, TIME K in 12/24/48}
      x condition{9 masks} x cost{3 configs}.
Reports net bps (correct fee), bootstrap CI seed=42 B=2000, win rate.
Uses src/lib/paths + time_gates; never touches reserved window.
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P
import lib.time_gates as T

ATLAS_CUTS = json.load(open(P.ATLAS_DIR / "atlas_cuts.json"))
TMAX = 48
SEED = 42
SYM, TF = "SOLUSDT", "4h"
DATA_FILE = P.RAW_DIR / "SOLUSDT-FUTURES-2022-2026-4h.csv"

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
COST = {"PB_PB":4.0, "PB_MKT":11.5, "MKT_MKT":15.0}
TIME_K = [12,24,48]

def load_train(path):
    df = pd.read_csv(path)
    low = {c.strip().strip('"').lower(): c for c in df.columns}
    ren = {low[a]: a for a in ["time","open","high","low","close","volume"]}
    df = df.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
    df = df.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    return T.filter_window(df, "TRAIN")

def boot_ci(x, n=2000, seed=SEED):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n); d0=0
    while d0<n:
        d=min(64,n-d0); idx=rng.integers(0,n_,size=(d,n_)); ms[d0:d0+d]=x[idx].mean(axis=1); d0+=d
    return tuple(np.quantile(ms,[0.025,0.975]))

def replay(O,Hh,L,C, sidx, eb, bt, tp, K):
    """Forward replay. K=0 => NOSL (exit on TP touch or horizon close).
    K>0 => TIME stop: exit at close of bar K if TP not touched by then.
    Returns pnl_bps array (gross of fees)."""
    E=len(sidx)
    starts=np.where(eb>=0,eb,0)
    idx=np.clip(starts[:,None]+np.arange(TMAX)[None,:],0,len(L)-1)
    fhi=Hh[idx]; fcl=C[idx]
    tp_hit=fhi>=tp[:,None]; tp_idx=np.where(tp_hit.any(1),tp_hit.argmax(1),TMAX)
    filled=tp_idx<TMAX
    if K>0:
        exit_idx=np.minimum(tp_idx, K)
        hit_at_exit=fhi[np.arange(E),np.clip(exit_idx,0,TMAX-1)]>=tp
        pnl=np.where(hit_at_exit, (tp-bt)/bt*1e4, (fcl[np.arange(E),np.clip(exit_idx,0,TMAX-1)]-bt)/bt*1e4)
    else:
        pnl=np.where(filled, (tp-bt)/bt*1e4, (fcl[:,-1]-bt)/bt*1e4)
    return pnl, filled

# load + features
key=f"{SYM}-{TF}"; cuts=ATLAS_CUTS[key]
tr=load_train(DATA_FILE)
O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
L=tr.low.values.astype(float);  C=tr.close.values.astype(float); V=tr.volume.values.astype(float)
n=len(tr); rng_=Hh-L
uw=np.where(rng_>0,(Hh-np.maximum(O,C))/rng_,np.nan)
rx=rng_/pd.Series(rng_).rolling(14).mean().shift(1).values
vr=V/pd.Series(V).rolling(20).mean().shift(1).values
ret24=C/pd.Series(C).shift(24).values-1.0
sma50=pd.Series(C).rolling(50).mean().shift(1).values
smaal=np.where(C>sma50,1,np.where(C<sma50,-1,0)).astype(float)
prev=pd.Series(np.sign(C-O)).shift(1).values
dq=np.array(cuts["uw_deciles"])
sig=np.where((C>O)&(rng_>0)&(uw>=cuts["uw_tercile"])&~np.isnan(rx)&~np.isnan(vr)&~np.isnan(ret24)&~np.isnan(prev))[0]
F=dict(uwd=np.searchsorted(dq,uw[sig])+1, trend=np.searchsorted(np.array(cuts["ret24_q"]),ret24[sig]),
       volq=np.searchsorted(np.array(cuts["vr_q"]),vr[sig]), prev=prev[sig], smaal=smaal[sig])
bt=np.maximum(O[sig],C[sig]); bb=np.minimum(O[sig],C[sig]); wh=Hh[sig]; sidx=sig
eb_pb=np.full(len(sidx),-1)
for k,i in enumerate(sidx):
    lo_b,hi_b=i+1,min(i+12,n-1)
    jj=np.flatnonzero(L[lo_b:hi_b+1]<bb[k]*(1-1e-4)); eb_pb[k]=lo_b+jj[0] if len(jj) else -1
ok_pb=eb_pb>=0; eb_mkt=sidx+1; ok_mkt=eb_mkt<n

rows=[]
for entry,(eb,ok) in [("PB",(eb_pb,ok_pb)),("MKT",(eb_mkt,ok_mkt))]:
    ep=bb.copy() if entry=="PB" else O[np.clip(eb,0,n-1)]
    for fv in [1.0,1.5]:
        tp=bt+fv*(wh-bt); valid=ok&(tp>ep); vi=np.where(valid)[0]
        if len(vi)==0: continue
        sidx_v=sidx[vi]; bt_v=bt[vi]; tp_v=tp[vi]; eb_v=eb[vi]; Fv={k:v[vi] for k,v in F.items()}
        for cname,fn in CONDS.items():
            m=fn(Fv)
            for K in [0]+TIME_K:
                pnl,_=replay(O,Hh,L,C,sidx_v,eb_v,bt_v,tp_v,K)
                mm=pnl[m]
                if len(mm)<30: continue
                for ck,cv in COST.items():
                    x=mm-cv; lo,hi=boot_ci(x)
                    # p-value: H0 mean<=0; use normal approx from CI
                    se=(hi-lo)/(2*1.96); z=float(x.mean())/se if se>0 else 0.0
                    pval=2*(1-stats.norm.cdf(abs(z))) if z>=0 else stats.norm.cdf(z)
                    rows.append(dict(entry=entry,f=fv,cond=cname,exit=("NOSL" if K==0 else "TIME"),
                        K=K,cost_cfg=ck,N=len(x),net=round(float(x.mean()),2),
                        ci_lo=round(lo,1),ci_hi=round(hi,1),wr=round(float((x>0).mean()),3),
                        pval=round(pval,6)))
out=P.V2_OUTPUTS/"w7_sol4h_corrected.csv"; pd.DataFrame(rows).to_csv(out,index=False)
best=pd.DataFrame(rows); ab=best[best.ci_lo>0].sort_values("net",ascending=False)
print(f"SOL-4h: {len(rows)} cells, {len(ab)} above-cost(CI>0) at correct fees")
print(ab[["entry","f","cond","exit","K","cost_cfg","N","net","ci_lo","ci_hi","wr"]].head(25).to_string(index=False))
print("saved", out)

# ---- Global FDR at the selection layer (directive s4.1) ----
# Selection family = every cell tested in this study (the grid the candidate was picked from).
# Use the declared headline cost (PB_MKT = 11.5 bps) for the FDR family.
fam = pd.DataFrame(rows)
fam_pb = fam[fam.cost_cfg == "PB_MKT"].copy()
p = fam_pb["pval"].values.astype(float)
p = np.clip(p, 1e-12, 1.0)
order = np.argsort(p)
m = len(p)
bh_thresh = np.empty(m)
for i, rank in enumerate(order, start=1):
    bh_thresh[rank-1] = (i / m) * 0.05
sig = p <= bh_thresh
# largest k where all k'<=k significant (step-up)
kmax = 0
for i in range(m-1, -1, -1):
    if sig[order[i]]:
        kmax = i + 1
        break
n_sig = int(sig.sum())
print(f"\nGLOBAL FDR (BH q=0.05) on selection family (PB_MKT, {m} cells): "
      f"{n_sig} significant (p<=BH). Candidate C6_w9dip survives: "
      f"{bool((fam_pb.cond=='C6_w9dip').any() and (fam_pb[(fam_pb.cond=='C6_w9dip')].ci_lo>0).any())}")
fam_pb["bh_sig"] = sig
fam_pb.to_csv(P.V2_OUTPUTS/"w7_fdr_family.csv", index=False)
print("saved FDR family ->", P.V2_OUTPUTS/"w7_fdr_family.csv")

