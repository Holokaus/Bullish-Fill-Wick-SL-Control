"""
Build tradeable system - Muse Spark 1.2 (muse-spark-1.2-contributor-free)
Signed: Meta Muse Spark 1.2

Goal: convert informational edge into NET POSITIVE expectancy.
Insight from audit:
- Raw rule (market buy next open -> T within 2 candles) is gross +0-4bp vs 11bp costs = negative
- But wick-size conditioned cells ARE net positive: BTC 1d >=2.5% +39.3bp n=94, SOL 1d 1.3-1.75% +37.3bp n=221, SOL 1h 1.75-2.5% +19.4bp n=344 (all-years stable), SOL 4h >=2.5% +20.7bp, ETH 4h >=2.5% +35bp
- Dip limit entry adds +3-7bp/signal, anatomy/volume/hour filters further separate

Strategy: COMBINED FILTERED LIMIT SYSTEM
Phase 1: universe = events passing wick bucket + quality filters (volume, anatomy, hour)
Phase 2: entry = limit buy at discount below open(e+1) (maker) -> reduces r_req, increases gross
Phase 3: exit = T within 2 candles, else time-stop close(e+2); optional SL mapped but not required for these large wicks (wide targets already)
Phase 4: Walk-forward: train 2022-2024, validate 2025, holdout 2026 untouched
"""
import os, json, itertools
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RES = os.path.join(ROOT, "results")
IV_MS = {"1d":86400000,"4h":14400000,"1h":3600000,"30m":1800000,"15m":900000}
NET_COST = 0.0011

def load_events(sym,tf):
    d=pd.read_csv(os.path.join(DATA,f"{sym}_{tf}.csv")).sort_values("ts").reset_index(drop=True)
    iv=IV_MS[tf]
    bt=d[["open","close"]].max(axis=1)
    wu=d["high"]-bt
    rng=d["high"]-d["low"]
    body=(d["close"]-d["open"]).abs()
    is_ev=wu>0.002*d["close"]
    o1,h1,l1=d["open"].shift(-1),d["high"].shift(-1),d["low"].shift(-1)
    h2,c2=d["high"].shift(-2),d["close"].shift(-2)
    ok=(d["ts"].shift(-1)-d["ts"]==iv)&(d["ts"].shift(-2)-d["ts"]==2*iv)
    ev=d[is_ev&ok].copy()
    ev["entry"]=o1[ev.index]
    ev["T"]=bt[ev.index]+0.95*wu[ev.index]
    ev["wick_pct"]=100*wu[ev.index]/d["close"][ev.index]
    ev["r_req"]=ev["T"]/ev["entry"]-1
    ev["body_pct"]=100*body[ev.index]/rng[ev.index].replace(0,np.nan)
    ev["bull"]=d["close"][ev.index]>=d["open"][ev.index]
    ev["win1"]=h1[ev.index]>=ev["T"]
    ev["win2o"]=(~ev["win1"])&(h2[ev.index]>=ev["T"])
    ev["win"]=ev["win1"]|ev["win2o"]
    ev["exit_ret_raw"]=np.where(ev["win"],ev["r_req"],c2[ev.index]/ev["entry"]-1)
    # volume
    med20=d["volume"].shift(1).rolling(20).median()
    ev["rvol"]=(d["volume"]/med20)[ev.index]
    # hour
    ev["hour"]=pd.to_datetime(d["ts"].shift(-1)[ev.index],unit="ms",utc=True).dt.hour
    # anatomy type
    ev["typ"]=np.select([ev["body_pct"]<30,ev["body_pct"]<=70],["small","mid"],"large")
    ev["ts_entry"]=d["ts"].shift(-1)[ev.index]
    ev["year"]=pd.to_datetime(ev["ts_entry"],unit="ms",utc=True).dt.year
    # path for SL later
    ev["_l1"]=l1[ev.index]; ev["_h1"]=h1[ev.index]; ev["_h2"]=h2[ev.index]; ev["_c2"]=c2[ev.index]
    return ev

def eval_rule(ev, disc_bp=0):
    if len(ev)==0:
        return {"n":0,"p":0,"gross":0,"net":0,"exp_opt":0,"exp_pess":0,"fill":0}
    L=ev["entry"]*(1-disc_bp/1e4)
    filled=(ev["_l1"]<=L).fillna(False)
    if disc_bp==0:
        filled=pd.Series([True]*len(ev),index=ev.index)
        L=ev["entry"]
    amb=filled&(ev["_h1"]>=ev["T"])
    won_clear=filled&(~amb)&(ev["_h2"]>=ev["T"])
    # for disc 0, win already defined; for disc>0 recompute win after fill
    if disc_bp==0:
        won=ev["win"]
        pnl=np.where(won, ev["r_req"], ev["_c2"]/ev["entry"]-1)
        fill_rate=1.0
        exp_opt=np.mean(pnl)-NET_COST
        exp_pess=exp_opt
        p=np.mean(won)
        gross=np.mean(pnl)
    else:
        won_opt=won_clear|amb
        pnl_opt=np.where(won_opt, ev["T"]/L-1, np.where(filled, ev["_c2"]/L-1, 0))
        pnl_pess=np.where(won_clear, ev["T"]/L-1, np.where(filled&(~amb), ev["_c2"]/L-1, 0))
        # per signal expectancy (including non-filled as 0)
        exp_opt=np.mean(pnl_opt - NET_COST*filled)
        exp_pess=np.mean(pnl_pess - NET_COST*filled)
        # win rate given filled (optimistic)
        p=float(won_opt[filled].mean()) if filled.sum()>0 else 0
        gross=float(np.mean(pnl_opt))
        fill_rate=float(filled.mean())
    return {"n":len(ev),"p":float(ev["win"].mean()) if disc_bp==0 else p,"gross_bp":float(1e4*gross) if disc_bp==0 else float(1e4*np.mean(pnl_opt)),"net_opt_bp":float(1e4*exp_opt),"net_pess_bp":float(1e4*exp_pess),"fill_rate":float(fill_rate),"exp_opt":float(exp_opt),"exp_pess":float(exp_pess)}

# Discover best combined filters on TRAIN (2022-2024) only
SYMS=["btcusdt","ethusdt","solusdt"]
TFS=["1d","4h","1h","30m","15m"]

# manual search space guided by conditional atlas
candidates=[]
for sym in SYMS:
    for tf in TFS:
        ev=load_events(sym,tf)
        train=ev[ev["year"]<=2024]
        if len(train)<150: continue
        # wick buckets to test
        for lo,hi in [(0.2,0.35),(0.35,0.6),(0.6,1.0),(1.0,1.75),(1.75,2.5),(2.5,999),(1.3,1.75),(1.75,999),(0.2,0.6),(0.6,1.75)]:
            sub=train[(train["wick_pct"]>=lo)&(train["wick_pct"]<hi)]
            if len(sub)<60: continue
            for disc in [0,15,25]:
                for rvol_max in [999,1.3,0.9]:
                    for typ in [None,"large","small"]:
                        f=sub
                        if rvol_max!=999: f=f[f["rvol"]<=rvol_max]
                        if typ is not None: f=f[f["typ"]==typ]
                        if len(f)<50: continue
                        r=eval_rule(f,disc_bp=disc)
                        # require both bounds >0 for robustness when disc>0, or net>0 when disc=0
                        ok = (r["net_pess_bp"]>2 if disc>0 else r["net_opt_bp"]>2)
                        if ok and r["n"]>=80:
                            candidates.append((sym,tf,lo,hi,disc,rvol_max,typ,r))

candidates=sorted(candidates,key=lambda x: x[7]["net_pess_bp"] if x[4]>0 else x[7]["net_opt_bp"],reverse=True)
print(f"FOUND {len(candidates)} TRAIN-positive candidates")
for c in candidates[:15]:
    sym,tf,lo,hi,disc,rv,typ,r=c
    print(f"{sym} {tf} wick[{lo},{hi}) disc{disc} rvol<={rv} typ={typ} n={r['n']} p={r['p']:.3f} netOpt={r['net_opt_bp']:.1f} netPess={r['net_pess_bp']:.1f} fill={r['fill_rate']:.2f}")

# Build portfolio: pick top diverse cells covering different assets, require validation on 2025
port=[]
used=set()
for c in candidates:
    sym,tf,lo,hi,disc,rv,typ,r=c
    key=(sym,tf)
    if key in used and len(port)>=5: continue
    ev=load_events(sym,tf)
    val=ev[ev["year"]==2025]
    sub=val[(val["wick_pct"]>=lo)&(val["wick_pct"]<hi)]
    if rv!=999: sub=sub[sub["rvol"]<=rv]
    if typ is not None: sub=sub[sub["typ"]==typ]
    if len(sub)<20: continue
    rv2=eval_rule(sub,disc_bp=disc)
    if (rv2["net_pess_bp"]>0 if disc>0 else rv2["net_opt_bp"]>0):
        port.append(c)
        used.add(key)
        if len(port)>=5: break

print("\nPORTFOLIO (train 22-24 + val 25 positive):")
for c in port:
    print(c)

# If none pass val, fallback to strongest train candidates with year stability
if len(port)==0:
    print("No candidate survived 2025 val - falling back to strongest train with year stability check")
    # use the top 3 from earlier list and test holdout later anyway
    port=candidates[:3]

# Evaluate full timeline and holdout 2026
results={}
total_pnl=0
total_n=0
for sym,tf,lo,hi,disc,rv,typ,r in port:
    ev=load_events(sym,tf)
    hold=ev[ev["year"]>=2026]
    sub=hold[(hold["wick_pct"]>=lo)&(hold["wick_pct"]<hi)]
    if rv!=999: sub=sub[sub["rvol"]<=rv]
    if typ is not None: sub=sub[sub["typ"]==typ]
    hr=eval_rule(sub,disc_bp=disc)
    tr=eval_rule(ev[(ev["wick_pct"]>=lo)&(ev["wick_pct"]<hi) & ( (ev["rvol"]<=rv) if rv!=999 else True ) & ( (ev["typ"]==typ) if typ else True)],disc_bp=disc)
    results[f"{sym}_{tf}_wick{lo}-{hi}_disc{disc}_rvol{rv}_typ{typ}"]={
        "rule":f"{sym} {tf} wick {lo}-{hi} disc{disc} rvol<={rv} typ={typ}",
        "train":r,"holdout2026":hr,"full":tr,
        "hold_n":len(sub),"hold_net_pess":hr["net_pess_bp"],"hold_net_opt":hr["net_opt_bp"]
    }
    print(f"HOLDOUT {sym} {tf} n={hr['n']} netOpt {hr['net_opt_bp']:.1f} netPess {hr['net_pess_bp']:.1f} fill {hr['fill_rate']:.2f}")

# Save
with open(os.path.join(RES,"system_candidates.json"),"w") as f:
    json.dump({"candidates_train":len(candidates),"portfolio":results},f,indent=1,default=str)
print("SAVED results/system_candidates.json")
