"""OF-W6: STATISTICAL STOP-LOSS PLACEMENT STUDY (TRAIN Sep2022-Dec2024).

Goal: given the no-SL edge is real and above cost (W5), find how to set a STOP that
  (a) preserves the edge above the cost line, and
  (b) caps tail / gap downside (finalization of the no-SL book).
We do NOT kill the concept — we optimize risk. Kline OHLCV only (owner directive #2).

For every event we replay the forward path once, then test a grid of stop specs and
measure the trade-off: stop-out rate vs net expectancy vs edge retained vs max loss.

Stop specifications tested (all exit on TP touch OR stop OR horizon close):
  ABS   : hard stop at entry*(1 - s_bps), s_bps in {10,20,30,50,75,100,150,200,300,500}
  ATR   : stop at entry - k*ATR14(signal bar), k in {0.5,1,1.5,2,3}
  QMAE  : stop at pXX of that series+cond's MAE-before-fill distribution, p in {50,75,90,95}
  TIME  : no hard stop; exit at close of bar K (K in {2,4,6,8,12,24}) if TP not yet hit
Baseline NOSL = exit on TP touch or horizon close (matches W5).

Cost model: uniform maker RT 4.0 bps/side for ALL specs (isolates stop-placement effect;
real stopped exits add taker fee — a further documented drag, not studied here).
Entry: PB at body-bottom (maker) primary; MKT (taker next-open) secondary.
Target: f in {1.0, 1.5} x wick gap. Horizon Tmax=48 bars.
"""
import json, math
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
TRAIN_END_MS = T.TRAIN_END
TMAX = 48
FEE_M = 4.0
# FOCUSED: short-timeframe series that were significantly above cost in W5 (funding negligible)
DATA_FILES = [
    ("ICPUSDT","30m", SRC/r"ICPUSDT-FUTURES-2022-2026-30m.csv"),
    ("ICPUSDT","1h",  SRC/r"ICPUSDT-FUTURES-2022-2026-1h.csv"),
    ("SOLUSDT","1h",  SRC/r"SOLUSDT-FUTURES-2022-2026-1h.csv"),
    ("BTCUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-1h.csv"),
    ("ETHUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\ETHUSDT-FUTURES-2022-2026-1h.csv"),
]
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
ABS_GRID   = [10,20,30,50,75,100,150,200,300,500]
ATR_K      = [0.5,1.0,1.5,2.0,3.0]
Q_PCT      = [50,75,90,95]
TIME_K     = [2,4,6,8,12,24]

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

def simulate_forward(L,Hh,O,C, sidx, eb, bt, tp, bb, sl_level_bps, atr_col):
    """Replay forward path for a batch of events; return pnl array for given stop spec.
    sl_level_bps: (E,) per-event adverse stop in bps, or scalar. atr_col unused here.
    Returns (pnl_bps, stopped_bool, tp_bool)."""
    E=len(sidx)
    starts = np.where(eb>=0, eb, 0)
    idx = starts[:,None] + np.arange(TMAX)[None,:]
    idx = np.clip(idx, 0, len(L)-1)
    flo = L[idx]; fhi = Hh[idx]; fop = O[idx]; fcl = C[idx]
    runmin = np.minimum.accumulate(flo, axis=1)
    adv = (bt[:,None] - runmin)/bt[:,None]*1e4            # (E,T) adverse bps
    tp_hit = fhi >= tp[:,None]
    tp_idx = np.where(tp_hit.any(1), tp_hit.argmax(1), TMAX)
    slv = np.asarray(sl_level_bps)
    if slv.ndim==0: slv=np.full(E, slv)
    stop_hit = adv >= slv[:,None]
    stop_idx = np.where(stop_hit.any(1), stop_hit.argmax(1), TMAX)
    stop_idx = np.clip(stop_idx, 0, TMAX-1)   # safe indexing; non-stopped rows don't read so
    filled = tp_idx < stop_idx
    stopped = (~filled) & (stop_idx < TMAX)
    neither = (~filled) & (~stopped)
    # SL-first exit price
    sl_price = bt*(1 - slv/1e4)
    so = fop[np.arange(E), stop_idx]
    xp = np.where(so >= sl_price, sl_price, np.minimum(so, sl_price))
    pnl_stop = (xp - bt)/bt*1e4
    pnl_tp   = (tp - bt)/bt*1e4
    pnl_neither = (fcl[:,-1] - bt)/bt*1e4
    pnl = np.where(filled, pnl_tp, np.where(stopped, pnl_stop, pnl_neither))
    return pnl, stopped, filled

def net_stats(pnl_valid):
    if len(pnl_valid)<30: return None
    lo,hi = boot_ci(pnl_valid)
    # match W5 convention: subtract single-side maker fee FEE_M (4.0 bps) for comparability
    return dict(N=len(pnl_valid), net=round(float(pnl_valid.mean())-FEE_M,2),
               ci_lo=round(lo-FEE_M,1), ci_hi=round(hi-FEE_M,1),
               wr=round(float((pnl_valid>0).mean()),3))

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
    atr14=pd.Series(rng_).rolling(14).mean().shift(1).values
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
           volq=np.searchsorted(np.array(cuts["vr_q"]),vr[sig]), prev=prev[sig], smaal=smaal[sig])
    bt=np.maximum(O[sig],C[sig]); bb=np.minimum(O[sig],C[sig]); wh=Hh[sig]; sidx=sig

    # entry resolutions
    # PB
    eb_pb=np.full(len(sidx),-1)
    for k,i in enumerate(sidx):
        lo_b,hi_b=i+1,min(i+12,n-1)
        jj=np.flatnonzero(L[lo_b:hi_b+1]<bb[k]*(1-1e-4))
        eb_pb[k]=lo_b+jj[0] if len(jj) else -1
    ok_pb=eb_pb>=0
    # MKT
    eb_mkt=sidx+1; ok_mkt=eb_mkt<n

    for entry, (eb, ok) in [("PB",(eb_pb,ok_pb)),("MKT",(eb_mkt,ok_mkt))]:
        ep = bb.copy() if entry=="PB" else O[np.clip(eb,0,n-1)]
        for fv in [1.0,1.5]:
            tp=bt+fv*(wh-bt)
            valid=ok&(tp>ep)
            vi=np.where(valid)[0]
            if len(vi)==0: continue
            sidx_v=sidx[vi]; bt_v=bt[vi]; tp_v=tp[vi]; eb_v=eb[vi]
            atr_v=atr14[sidx_v]
            # precompute forward MAE-per-event once (adverse bps from entry up to fill/horizon)
            starts=np.where(eb_v>=0,eb_v,0)
            idx=np.clip(starts[:,None]+np.arange(TMAX)[None,:],0,len(L)-1)
            flo=L[idx]; fhi=Hh[idx]
            runmin=np.minimum.accumulate(flo,axis=1)
            adv_ev=(bt_v[:,None]-runmin)/bt_v[:,None]*1e4
            tp_hit_ev=fhi>=tp_v[:,None]
            tp_idx_ev=np.where(tp_hit_ev.any(1),tp_hit_ev.argmax(1),TMAX)
            mae_pre_all=np.take_along_axis(adv_ev,np.minimum(tp_idx_ev,TMAX-1)[:,None],axis=1).ravel()
            # baseline NOSL
            pnl_nosl, _, _ = simulate_forward(L,Hh,O,C, sidx_v, eb_v, bt_v, tp_v, bb[vi], 1e9, atr_v)
            base=net_stats(pnl_nosl[~np.isnan(pnl_nosl)])
            base_net = base["net"] if base else np.nan
            for cname,fn in CONDS.items():
                m=fn(F)[vi]
                pnl_c=pnl_nosl[m]; b=net_stats(pnl_c)
                if not b: continue
                base_c=b["net"]
                rows.append(dict(series=key,cond=cname,entry=entry,f=fv,stop_type="NOSL",stop_param=0,
                    N=b["N"],stop_out=0.0,net_maker=b["net"],ci_lo=b["ci_lo"],ci_hi=b["ci_hi"],
                    wr=b["wr"],edge_ret=1.0))
                # ABS stops
                for s in ABS_GRID:
                    pnl,stopped,_=simulate_forward(L,Hh,O,C,sidx_v,eb_v,bt_v,tp_v,bb[vi],s,atr_v)
                    pnl_c=pnl[m]; st=stopped[m]
                    bs=net_stats(pnl_c)
                    if not bs: continue
                    ret=round(bs["net"]/base_c,3) if (base_c and not math.isnan(base_c) and abs(base_c)>1e-6) else np.nan
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,stop_type="ABS",stop_param=s,
                        N=bs["N"],stop_out=round(float(st.mean()),3),net_maker=bs["net"],
                        ci_lo=bs["ci_lo"],ci_hi=bs["ci_hi"],wr=bs["wr"],edge_ret=ret))
                # ATR stops
                for k in ATR_K:
                    slv=(k*atr_v/bt_v*1e4)
                    pnl,stopped,_=simulate_forward(L,Hh,O,C,sidx_v,eb_v,bt_v,tp_v,bb[vi],slv,atr_v)
                    pnl_c=pnl[m]; st=stopped[m]
                    bs=net_stats(pnl_c)
                    if not bs: continue
                    ret=round(bs["net"]/base_c,3) if (base_c and not math.isnan(base_c) and abs(base_c)>1e-6) else np.nan
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,stop_type="ATR",stop_param=k,
                        N=bs["N"],stop_out=round(float(st.mean()),3),net_maker=bs["net"],
                        ci_lo=bs["ci_lo"],ci_hi=bs["ci_hi"],wr=bs["wr"],edge_ret=ret))
                # QMAE stops (per series+cond quantile of MAE-before-fill)
                for p in Q_PCT:
                    s_q=float(np.nanpercentile(mae_pre_all,p))
                    if not np.isfinite(s_q) or s_q<=0: continue
                    pnl,stopped,_=simulate_forward(L,Hh,O,C,sidx_v,eb_v,bt_v,tp_v,bb[vi],s_q,atr_v)
                    pnl_c=pnl[m]; st=stopped[m]
                    bs=net_stats(pnl_c)
                    if not bs: continue
                    ret=round(bs["net"]/base_c,3) if (base_c and not math.isnan(base_c) and abs(base_c)>1e-6) else np.nan
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,stop_type="QMAE",stop_param=p,
                        N=bs["N"],stop_out=round(float(st.mean()),3),net_maker=bs["net"],
                        ci_lo=bs["ci_lo"],ci_hi=bs["ci_hi"],wr=bs["wr"],edge_ret=ret))
                # TIME stops (no hard stop)
                starts=np.where(eb_v>=0,eb_v,0)
                idx=np.clip(starts[:,None]+np.arange(TMAX)[None,:],0,len(L)-1)
                fhi=Hh[idx]; fcl=C[idx]
                tp_hit=fhi>=tp_v[:,None]; tp_idx=np.where(tp_hit.any(1),tp_hit.argmax(1),TMAX)
                for K in TIME_K:
                    filled_K=tp_idx<K
                    pnl_ts=np.where(filled_K, (tp_v-bt_v)/bt_v*1e4, (fcl[:,K-1]-bt_v)/bt_v*1e4)
                    pnl_c=pnl_ts[m]
                    bs=net_stats(pnl_c)
                    if not bs: continue
                    ret=round(bs["net"]/base_c,3) if (base_c and not math.isnan(base_c) and abs(base_c)>1e-6) else np.nan
                    rows.append(dict(series=key,cond=cname,entry=entry,f=fv,stop_type="TIME",stop_param=K,
                        N=bs["N"],stop_out=0.0,net_maker=bs["net"],
                        ci_lo=bs["ci_lo"],ci_hi=bs["ci_hi"],wr=bs["wr"],edge_ret=ret))
    print(f"{key} done", flush=True)

R=pd.DataFrame(rows)
R["sig_maker"]=R.ci_lo>0
R.to_csv(OUT/"w6_stop_study.csv", index=False)
print("\n===== W6 STOP STUDY SUMMARY =====")
print("rows:", len(R))
for st in ["ABS","ATR","QMAE","TIME","NOSL"]:
    sub=R[R.stop_type==st]
    print(f"\n--- {st}: cells={len(sub)}, above_cost(CI>0)={int(sub.sig_maker.sum())}, "
          f"median edge retained={sub.edge_ret.median():.2f}")
    if st in ("ABS","ATR","QMAE"):
        top=sub[sub.sig_maker].sort_values("net_maker",ascending=False).head(6)
        print(top[["series","cond","entry","f","stop_param","N","stop_out","net_maker","ci_lo","ci_hi","edge_ret"]].to_string(index=False))
