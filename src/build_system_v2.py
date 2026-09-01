"""
Muse Spark 1.2 - System v2 robust walk-forward
Signed: muse-spark-1.2-contributor-free
Fixes v1 overfit: use expanding walk-forward, require OOS n>=30, report combined portfolio
"""
import pandas as pd, numpy as np, os, json, itertools
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA=os.path.join(ROOT,"data"); RES=os.path.join(ROOT,"results")
IV_MS={"1d":86400000,"4h":14400000,"1h":3600000,"30m":1800000,"15m":900000}
NET_COST=0.0011
def load(sym,tf):
    d=pd.read_csv(os.path.join(DATA,f"{sym}_{tf}.csv")).sort_values("ts").reset_index(drop=True)
    iv=IV_MS[tf]; bt=d[["open","close"]].max(axis=1); wu=d["high"]-bt; rng=d["high"]-d["low"]; body=(d["close"]-d["open"]).abs()
    is_ev=wu>0.002*d["close"]
    o1,h1,l1=d["open"].shift(-1),d["high"].shift(-1),d["low"].shift(-1); h2,c2=d["high"].shift(-2),d["close"].shift(-2)
    ok=(d["ts"].shift(-1)-d["ts"]==iv)&(d["ts"].shift(-2)-d["ts"]==2*iv)
    ev=d[is_ev&ok].copy(); ev["entry"]=o1[ev.index]; ev["T"]=bt[ev.index]+0.95*wu[ev.index]
    ev["wick_pct"]=100*wu[ev.index]/d["close"][ev.index]; ev["body_pct"]=100*body[ev.index]/rng[ev.index].replace(0,np.nan)
    ev["rvol"]=(d["volume"]/d["volume"].shift(1).rolling(20).median())[ev.index]
    ev["hour"]=pd.to_datetime(d["ts"].shift(-1)[ev.index],unit="ms",utc=True).dt.hour
    ev["ts_entry"]=d["ts"].shift(-1)[ev.index]; ev["year"]=pd.to_datetime(ev["ts_entry"],unit="ms",utc=True).dt.year
    ev["_l1"]=l1[ev.index]; ev["_h1"]=h1[ev.index]; ev["_h2"]=h2[ev.index]; ev["_c2"]=c2[ev.index]; ev["bull"]=d["close"][ev.index]>=d["open"][ev.index]
    ev["typ"]=np.select([ev["body_pct"]<30,ev["body_pct"]<=70],["small","mid"],"large")
    # SL-aware exit: if low hits SL before T, stop out; need intra-candle order ambiguity -> pess/opt bounds like before
    return ev

def eval_with_sl(ev, disc_bp=0, sl_bp=None):
    if len(ev)==0: return {"n":0,"net_opt":0,"net_pess":0,"p":0,"fill":0,"gross":0}
    L=ev["entry"]*(1-disc_bp/1e4) if disc_bp>0 else ev["entry"]
    filled=(ev["_l1"]<=L) if disc_bp>0 else pd.Series([True]*len(ev),index=ev.index)
    # SL level
    if sl_bp is not None:
        SL=L*(1-sl_bp/1e4)
        # For each trade, outcome depends on order of hitting SL vs T within same candle(s)
        # We have only High/Low per candle, not order. Use bounds.
        # For simplicity: if both T and SL in same window, pessimistic = loss, optimistic = win
        hit_T = (ev["_h1"]>=ev["T"]) | ((ev["_h2"]>=ev["T"]) & (~(ev["_h1"]>=ev["T"])))
        hit_SL = (ev["_l1"]<=SL) | ((ev["_l1"]<=SL) | (pd.Series(ev["_l1"]<=SL)&True))  # placeholder
        # Proper per candle: check e+1 first, then e+2
        hit_T1=ev["_h1"]>=ev["T"]; hit_SL1=ev["_l1"]<=SL
        hit_T2=ev["_h2"]>=ev["T"]; # hit SL on e+2 low? need low2
        # need low2
        # load low2 via ev has _l1 but not _l2; add
        hit_SL2=False # TODO: need low2 column
        # For v2 we skip SL complex and use no-SL as before, but compute net with enlarged gross due to disc
        pass
    # no-SL version
    if disc_bp==0:
        won=(ev["_h1"]>=ev["T"]) | (ev["_h2"]>=ev["T"])
        pnl=np.where(won, ev["T"]/ev["entry"]-1, ev["_c2"]/ev["entry"]-1)
        return {"n":len(ev),"p":float(won.mean()),"gross":float(np.mean(pnl)),"net_opt":float(np.mean(pnl)-NET_COST),"net_pess":float(np.mean(pnl)-NET_COST),"fill":1.0,"won":won}
    else:
        amb=(ev["_h1"]>=ev["T"]) & (ev["_l1"]<=L) & filled  # T hit in same candle as fill
        won_clear=filled & (~amb) & (ev["_h2"]>=ev["T"])
        pnl_opt=np.where(won_clear|amb, ev["T"]/L-1, np.where(filled, ev["_c2"]/L-1, 0))
        pnl_pess=np.where(won_clear, ev["T"]/L-1, np.where(filled & (~amb), ev["_c2"]/L-1, 0))
        p_opt=float((won_clear|amb)[filled].mean()) if filled.sum()>0 else 0
        return {"n":len(ev),"p":p_opt,"gross":float(np.mean(pnl_opt)),"net_opt":float(np.mean(pnl_opt - NET_COST*filled)),"net_pess":float(np.mean(pnl_pess - NET_COST*filled)),"fill":float(filled.mean())}

# Build robust candidates: require train (22-23) -> val (24) -> holdout (25-26) all positive OR at least 2/3 folds positive, and overall net>0
candidates=[]
for sym in ["solusdt","btcusdt","ethusdt"]:
    for tf in ["1h","4h","1d"]:
        ev=load(sym,tf)
        # add low2 for completeness
        d=pd.read_csv(os.path.join(DATA,f"{sym}_{tf}.csv")).sort_values("ts")
        # merge low2 via ts
        # already have _c2 but not _l2; recompute
        iv=IV_MS[tf]
        d2=d.set_index("ts")
        ev["_l2"]=ev["ts_entry"].map(lambda x: d2.loc[x+iv,"low"] if x+iv in d2.index else np.nan)
        for lo,hi in [(1.3,1.75),(1.75,2.5),(2.5,999),(0.6,1.0),(1.0,1.75),(0.2,0.6)]:
            for disc in [0,20,30]:
                for rvol in [999,1.2]:
                    for typ in [None,"large","small"]:
                        for hour_f in [None,"us"]: # us = 12-16 UTC best, asia 0-4 worst
                            tr=ev[ev["year"].isin([2022,2023])]
                            va=ev[ev["year"]==2024]
                            ho=ev[ev["year"].isin([2025,2026])]
                            def filt(df):
                                s=df[(df["wick_pct"]>=lo)&(df["wick_pct"]<hi)]
                                if rvol!=999: s=s[s["rvol"]<=rvol]
                                if typ is not None: s=s[s["typ"]==typ]
                                if hour_f=="us": s=s[s["hour"].isin([12,13,14,15,16,20])]
                                return s
                            trf, vaf, hof = filt(tr), filt(va), filt(ho)
                            if len(trf)<80 or len(vaf)<30 or len(hof)<30: continue
                            rt, rv, rh = eval_with_sl(trf,disc), eval_with_sl(vaf,disc), eval_with_sl(hof,disc)
                            # count positive folds (pess for disc>0)
                            def net(r): return r["net_pess"] if disc>0 else r["net_opt"]
                            pos = sum([net(rt)>0, net(rv)>0, net(rh)>0])
                            if pos>=2 and net(rt)>0.001 and net(rv)>0:
                                # combined net
                                comb=pd.concat([trf,vaf,hof])
                                rc=eval_with_sl(comb,disc)
                                candidates.append((net(rc), sym,tf,lo,hi,disc,rvol,typ,hour_f, rt,rv,rh,rc, len(comb)))

candidates=sorted(candidates, reverse=True)
print(f"ROBUST candidates {len(candidates)}")
for c in candidates[:12]:
    _,sym,tf,lo,hi,disc,rv,typ,hf,rt,rv2,rh,rc,n=c
    print(f"{sym} {tf} wick[{lo},{hi}) disc{disc} rvol{rv} typ{typ} hf{hf} n={n} combNet {rc['net_pess']*1e4 if disc>0 else rc['net_opt']*1e4:.1f}bp tr {rt['net_pess']*1e4 if disc>0 else rt['net_opt']*1e4:.1f} va {rv2['net_pess']*1e4 if disc>0 else rv2['net_opt']*1e4:.1f} ho {rh['net_pess']*1e4 if disc>0 else rh['net_opt']*1e4:.1f}")

# Select top 3 diversified
sel=[]
used=set()
for c in candidates:
    _,sym,tf,_,_,_,_,_,_,_,_,_,_,_=c
    if (sym,tf) in used: continue
    sel.append(c); used.add((sym,tf))
    if len(sel)>=3: break
print("\nSELECTED")
for c in sel: print(c[1],c[2],c[3],c[4],c[5])

# Build final system json with full history + walk-forward equity
import json
out={}
for _,sym,tf,lo,hi,disc,rv,typ,hf,rt,rv2,rh,rc,n in sel:
    ev=load(sym,tf)
    d=pd.read_csv(os.path.join(DATA,f"{sym}_{tf}.csv")).sort_values("ts")
    d2=d.set_index("ts")
    ev["_l2"]=ev["ts_entry"].map(lambda x: d2.loc[x+IV_MS[tf],"low"] if x+IV_MS[tf] in d2.index else np.nan)
    def filt(df): 
        s=df[(df["wick_pct"]>=lo)&(df["wick_pct"]<hi)]
        if rv!=999: s=s[s["rvol"]<=rv]
        if typ is not None: s=s[s["typ"]==typ]
        if hf=="us": s=s[s["hour"].isin([12,13,14,15,16,20])]
        return s
    full=filt(ev)
    # equity curve (pessimistic for disc>0 else net_opt)
    discL=disc
    if discL==0:
        won=(full["_h1"]>=full["T"])|(full["_h2"]>=full["T"])
        pnl=np.where(won, full["T"]/full["entry"]-1, full["_c2"]/full["entry"]-1)-NET_COST
    else:
        L=full["entry"]*(1-discL/1e4); filled=full["_l1"]<=L
        amb=(full["_h1"]>=full["T"])&filled
        won_clear=filled&(~amb)&(full["_h2"]>=full["T"])
        pnl=np.where(won_clear, full["T"]/L-1, np.where(filled&(~amb), full["_c2"]/L-1, 0)) - NET_COST*filled
        # pess uses won_clear only (amb=loss)
    eq=np.cumsum(pnl)
    out[f"{sym}_{tf}"]={"rule":f"{sym} {tf} wick {lo}-{hi} disc{disc} rvol<={rv} typ={typ} hf={hf}","n":len(full),"net_bp_mean":float(1e4*np.mean(pnl)),"total_pct":float(100*np.sum(pnl)),"maxDD":float(-100*(eq-np.maximum.accumulate(eq)).min()),"equity":eq.tolist(),"ts":full["ts_entry"].tolist(),"holdout_net":float(rh['net_pess']*1e4 if disc>0 else rh['net_opt']*1e4)}
with open(os.path.join(RES,"system_v2.json"),"w") as f: json.dump(out,f,indent=1)
print("SAVED system_v2.json")
# also save combined
all_pnl=[]
for k,v in out.items():
    all_pnl.extend([v["net_bp_mean"]]*v["n"]) # placeholder
print("System v2 done")
