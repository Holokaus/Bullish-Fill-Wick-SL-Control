"""REDIR-W2: FOUR CHECKS on W3_BASE (primary) and W1_DIP (alternate), TRAIN only.

Checks (directive s3, absorbed from reviewer):
  1. COST SENSITIVITY : net at PB_PB 4 / PB_MKT 11.5 / MKT_MKT 15 bps (per-mechanic + headline).
  2. MATCHED CONTROL  : wick incremental edge vs matched non-wick candles (same color, size, regime).
  3. FUNDING          : 4h long funding (8h Bybit history) subtracted; net survives?
  4. UNION-FAMILY BH  : row significant on the combined W5+W6+W7+menu selection family (q=0.05).

Decision rule (pre-declared by owner):
  W3_BASE frozen if it passes all four; else W1_DIP frozen only if it passes all four;
  any switch disclosed in FROZEN_CANDIDATE v2. Then STOP for sign-off. E-VAL stays one-shot.

W3_BASE = wick >= W3 (90 bps) AND 24h-dip bottom quintile.
W1_DIP  = wick >= W1 (22.5 bps) AND 24h-dip bottom quintile.
Both color-agnostic (green OR red). MKT entry, TP f=1.5, time stop K=24, no price stop.
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

# ---------- load + TRAIN gate ----------
tr = pd.read_csv(P.RAW_DIR / f"{SYM}-FUTURES-2022-2026-{TF}.csv")
low = {c.strip().strip('"').lower(): c for c in tr.columns}
ren = {low[a]: a for a in ["time","open","high","low","close","volume"]}
tr = tr.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
tr = T.filter_window(tr, "TRAIN")                       # assert holdout excluded
O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
L=tr.low.values.astype(float);  C=tr.close.values.astype(float); n=len(tr)

# ---------- features ----------
rng_=Hh-L; body_top=np.maximum(O,C); wick_gap=Hh-body_top
valid=(rng_>0)&(wick_gap>0)
wbur_bps=np.where(valid, wick_gap/C*1e4, np.nan)
uw=(wick_gap/rng_)
dq=np.array(ATLAS[KEY]["uw_deciles"]); uw_dec=np.where(np.isnan(uw),-1,np.searchsorted(dq,uw)+1)
ret24=C/pd.Series(C).shift(24).values-1.0
rq=np.array(ATLAS[KEY]["ret24_q"]); ret24_q=np.where(np.isnan(ret24),-1,np.searchsorted(rq,ret24)+1)
rng_pct=(rng_/C); rng_d=np.searchsorted(np.quantile(rng_pct[valid],np.linspace(0,1,11)[1:-1]),rng_pct)+1
rng_d=np.where(np.isnan(rng_pct),-1,rng_d)
green=(C>O); red=(C<O)

sig=np.where(valid)[0]; eb=sig+1; ok=eb<n; sig=sig[ok]; eb=eb[ok]
bt=O[eb]; tp=body_top[sig]+1.5*wick_gap[sig]
is_green=green[sig]; is_red=red[sig]

# ---------- replay (MKT entry, K=24 time stop, no price stop) ----------
def replay(eb_v, bt_v, tp_v, K=24):
    E=len(bt_v); starts=np.clip(eb_v,0,n-1)
    idx=np.clip(starts[:,None]+np.arange(48)[None,:],0,n-1)
    fhi=Hh[idx]; fcl=C[idx]
    tph=fhi>=tp_v[:,None]; tpi=np.where(tph.any(1),tph.argmax(1),48)
    ei=np.minimum(tpi,K); hit=fhi[np.arange(E),np.clip(ei,0,47)]>=tp_v
    gross=np.where(hit,(tp_v-bt_v)/bt_v*1e4,(fcl[np.arange(E),np.clip(ei,0,47)]-bt_v)/bt_v*1e4)
    return gross, hit, np.clip(ei,0,47).astype(int)

def boot_ci(x,n=3000,seed=7):
    x=np.asarray(x,float); n_=len(x)
    if n_<10: return (np.nan,np.nan)
    rng=np.random.default_rng(seed); ms=np.empty(n)
    for d0 in range(0,n,64):
        d=min(64,n-d0); ms[d0:d0+d]=x[rng.integers(0,n_,size=(d,n_))].mean(axis=1)
    return tuple(np.quantile(ms,[0.025,0.975]))

def pval_from_mean_ci(net):
    lo,hi=boot_ci(net); se=(hi-lo)/(2*1.96); z=net.mean()/se if se>0 else 0.0
    return 2*(1-stats.norm.cdf(abs(z))), lo, hi

# ---------- funding series (8h) ----------
fund=pd.read_csv(P.RAW_DIR/"phase36/phase38/data/derivatives/SOLUSDT/funding_rate.csv")
fund["ts"]=fund.fundingRateTimestamp.astype("int64")
fund=fund[(fund.ts>=T.TRAIN_START)&(fund.ts<T.TRAIN_END)].sort_values("ts")
fund_times=fund.ts.values; fund_rates=fund.fundingRate.values.astype(float)

def funding_bps(entry_bar, exit_bar):
    # long pays positive funding; sum rates whose timestamp in (entry_time, exit_time]
    et=tr.time.values[entry_bar]; xt=tr.time.values[exit_bar]
    m=(fund_times>et)&(fund_times<=xt)
    return float(-fund_rates[m].sum()*1e4)   # total effect on long pnl in bps

# ---------- matched control ----------
# control = same color, same range-decile, same ret24-quintile, BUT wick below the row threshold
def matched_control(mask, wick_thr, use_dip):
    color_bin=np.where(is_green,"G",np.where(is_red,"R","F"))
    ctrl_pool=~mask & (rng_d[sig]>=0)
    if use_dip:
        ctrl_pool=ctrl_pool & (ret24_q[sig]<=1)
    ctrl_pool=ctrl_pool & (wick_below_met(sig,wick_thr))
    out=[]
    rng=np.random.default_rng(11)
    for i in np.where(mask)[0]:
        cb,cd,cq=color_bin[i],rng_d[sig][i],(ret24_q[sig][i] if use_dip else -1)
        if use_dip:
            cand=np.where(ctrl_pool & (color_bin==cb) & (rng_d[sig]==cd) & (ret24_q[sig]==cq))[0]
        else:
            cand=np.where(ctrl_pool & (color_bin==cb) & (rng_d[sig]==cd))[0]
        if len(cand)==0: continue
        j=cand[rng.integers(0,len(cand))]
        out.append(j)
    return np.array(out)

def wick_below_met(sig_idx, thr):
    return wbur_bps[sig_idx] < thr

# ---------- run a row ----------
def run_row(name, wick_thr, use_dip):
    mask=(wbur_bps[sig]>=wick_thr)
    if use_dip:
        mask=mask&(ret24_q[sig]<=1)
    m=mask; ntr=int(m.sum())
    if ntr<30:
        return dict(row=name,n=ntr)
    eb_v=eb[m]; bt_v=bt[m]; tp_v=tp[m]
    gross,hit,exitk=replay(eb_v,bt_v,tp_v,K=24)
    # per-mechanic cost: entry taker 5.5; exit maker 2.0 if TP else taker 5.5
    exit_cost=np.where(hit,2.0,5.5)
    cost_true=5.5+exit_cost                      # per-trade true RT bps
    cost_15=np.full(ntr,15.0)
    cost_4=np.full(ntr,4.0)
    cost_115=np.full(ntr,11.5)
    net_true=gross-cost_true
    net_15=gross-cost_15; net_4=gross-cost_4; net_115=gross-cost_115
    p_true,lo_true,hi_true=pval_from_mean_ci(net_true)
    p_15,_,_=pval_from_mean_ci(net_15)
    # funding adjustment (true cost basis)
    fb=np.array([funding_bps(eb_v[k],eb_v[k]+exitk[k]) for k in range(ntr)])
    net_fund=net_true+fb
    p_fund,lo_f,hi_f=pval_from_mean_ci(net_fund)
    # matched control
    ctrl_idx=matched_control(m,wick_thr,use_dip)
    dP=np.nan; dlo=np.nan; dhi=np.nan
    if len(ctrl_idx)>=30:
        cg,ch,cek=replay(eb[ctrl_idx],bt[ctrl_idx],tp[ctrl_idx],K=24)
        cc=5.5+np.where(ch,2.0,5.5)
        ctrl_net=cg-cc
        dP=net_true.mean()-ctrl_net.mean()
        # bootstrap delta CI
        rng2=np.random.default_rng(3); B=2000
        it=rng2.integers(0,ntr,size=(B,ntr)); ic=rng2.integers(0,len(ctrl_net),size=(B,len(ctrl_net)))
        ds=net_true[it].mean(axis=1)-ctrl_net[ic].mean(axis=1)
        dlo,dhi=tuple(np.quantile(ds,[0.025,0.975]))
    return dict(row=name,n=ntr,
        wr=float((net_15>0).mean()),
        net_4=round(float(net_4.mean()),2), net_115=round(float(net_115.mean()),2),
        net_15=round(float(net_15.mean()),2), net_true=round(float(net_true.mean()),2),
        lo_true=round(lo_true,2), hi_true=round(hi_true,2), p_true=round(p_true,6),
        net_fund=round(float(net_fund.mean()),2), lo_fund=round(lo_f,2), hi_fund=round(hi_f,2), p_fund=round(p_fund,6),
        funding_avg_bps=round(float(fb.mean()),2),
        dP=round(dP,2) if not np.isnan(dP) else None,
        dP_lo=round(dlo,2) if not np.isnan(dlo) else None, dP_hi=round(dhi,2) if not np.isnan(dhi) else None)

print("computing W3_BASE + W1_DIP ...")
R3=run_row("W3_BASE",90.0,use_dip=False)
R1=run_row("W1_DIP",22.5,use_dip=True)
print(json.dumps(R3,indent=2,default=str))
print(json.dumps(R1,indent=2,default=str))

# ---------- UNION-FAMILY BH (q=0.05): two definitions, reported transparently ----------
def bh_pass(cells, pvals):
    p=np.clip(np.asarray(pvals,float),1e-12,1.0)
    order=np.argsort(p); m=len(p); bh=np.empty(m)
    for i,rank in enumerate(order,1): bh[rank-1]=(rank/m)*0.05
    return set(c for c,pp,bb in zip(cells,p,bh) if pp<=bb)

# (A) crude full family: W5/W6/Track1 have only binary sig flags -> reconstruct p=0.01/0.5
fam=[]
w5=pd.read_csv(P.V2_OUTPUTS/"w5_nosl_economics.csv"); w5["p"]=w5["sig_maker"].map({True:0.01,False:0.5})
for _,r in w5.iterrows(): fam.append(("W5",f"{r.series}_{r.cond}_{r.entry}_f{r.f}",r.p))
w6=pd.read_csv(P.V2_OUTPUTS/"w6_stop_study.csv"); w6["p"]=w6["sig_maker"].map({True:0.01,False:0.5})
for _,r in w6.iterrows(): fam.append(("W6",f"{r.series}_{r.cond}_{r.entry}_{r.stop_type}{r.stop_param}",r.p))
w7=pd.read_csv(P.V2_OUTPUTS/"w7_sol4h_corrected.csv")
for _,r in w7.iterrows(): fam.append(("W7",f"sol4h_{r.cond}_{r.entry}_f{r.f}_{r.exit}_K{r.K}_{r.cost_cfg}",r.pval))
menu=pd.read_csv(P.V2_OUTPUTS/"redir_w1_menu.csv")
for _,r in menu.iterrows(): fam.append(("MENU",r.row,r.pval))
fam.append(("CAND","W3_BASE",R3.get("p_true",0.5))); fam.append(("CAND","W1_DIP",R1.get("p_true",0.5)))
famdf=pd.DataFrame(fam,columns=["src","cell","p"]); famdf["p"]=np.clip(famdf["p"].astype(float),1e-12,1.0)
famdf=famdf.sort_values("p").reset_index(drop=True)
sigA=bh_pass(famdf.cell.values, famdf.p.values)
print(f"[Union-A crude, n={len(famdf)}] W3_BASE passes={ 'W3_BASE' in sigA }  W1_DIP passes={ 'W1_DIP' in sigA }")

# (B) honest family: only cells with real computed p-values (W7 144 + menu 8 + cand 2 = 154)
famB=[]
for _,r in w7.iterrows(): famB.append((f"sol4h_{r.cond}_{r.entry}_f{r.f}_{r.exit}_K{r.K}_{r.cost_cfg}",r.pval))
for _,r in menu.iterrows(): famB.append((r.row,r.pval))
famB.append(("W3_BASE",R3.get("p_true",0.5))); famB.append(("W1_DIP",R1.get("p_true",0.5)))
famBdf=pd.DataFrame(famB,columns=["cell","p"]); famBdf["p"]=np.clip(famBdf["p"].astype(float),1e-12,1.0)
famBdf=famBdf.sort_values("p").reset_index(drop=True)
sigB=bh_pass(famBdf.cell.values, famBdf.p.values)
print(f"[Union-B honest, n={len(famBdf)}] W3_BASE passes={ 'W3_BASE' in sigB }  W1_DIP passes={ 'W1_DIP' in sigB }")
print(f"Union-B significant cells = {len(sigB)}")
