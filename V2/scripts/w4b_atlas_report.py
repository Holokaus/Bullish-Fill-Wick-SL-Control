"""OF-W4b: ATLAS REPORTER - turns event tables into the owner's question list.

Per series INDEPENDENTLY:
  A. Wick-length dose response (deciles 1..10): fill rate, 2-bar fill, extended-target
     reach, time-to-hit, forward return, adverse dip before fill.
  B. Trend context (ret24 quintiles) + SMA50 alignment.
  C. Prior-candle direction impact.  D. Event-candle volume quintile impact.
  E. Candle type (body-dominant / normal / lower-wick-heavy) impact.
  F. Path anatomy: P(fill<=2 bars), bounce counts before fill, MAE-before-fill quantiles.
  G. Time-of-day (4 blocks) and day-of-week personality.
  H. Regime split.  I. Single-condition lift scan with BH within series +
     five locked combo gates. All TRAIN-only, exploratory.

Outputs: logs/w4b.log digest + outputs/w4b_conditions.csv (all series pooled rows).
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

STUDY = Path(r"C:\Users\A\Bullish-Fill-Wick\V2")
ATLAS = STUDY/"outputs"/"atlas"
OUT = STUDY/"outputs"

COMBOS = {
    "C1_wick8_trend_up": lambda d: (d.uwd>=8)&(d.trend>=3),
    "C2_wick8_sma_above": lambda d: (d.uwd>=8)&(d.smaal==1),
    "C3_wick8_quietvol": lambda d: (d.uwd>=8)&(d.volq<=1),
    "C4_wick8_bear_regime": lambda d: (d.uwd>=8)&(d.reg==0),
    "C5_wick8_bodydom": lambda d: (d.uwd>=8)&(d.typ==0),
    "C6_wick910_dipbuy": lambda d: (d.uwd>=9)&(d.trend<=1),
}

def thinned_r24(d, gap=24):
    """mean of r24 keeping events >=gap bars apart is impossible post-hoc (no idx kept);
    approximate by stride-thinning every other event when n large (conservative display)."""
    x = d["r24"].dropna().values
    if len(x) > 400:  # thin to reduce overlap inflation for display
        x = x[::2]
    return float(np.mean(x)) if len(x) else np.nan

def cell_stats(d):
    return dict(n=len(d),
                hit2=d.hit2.mean() if len(d) else np.nan,
                hitH=d.hitH.mean() if len(d) else np.nan,
                e2=d.e2.mean() if len(d) else np.nan,
                med_t=int(d.loc[d.hitH,"t_hit"].median()) if d.hitH.any() else -1,
                med_nb=float(d.loc[d.hitH,"n_bounce_pre"].median()) if d.hitH.any() else np.nan,
                med_mae=float(d.loc[d.hitH,"mae_pre"].abs().median()) if d.hitH.any() else np.nan,
                r24_mean=thinned_r24(d))

cond_rows=[]
all_keys = sorted(p.stem.replace("_events","") for p in ATLAS.glob("*_events.parquet"))
for key in all_keys:
    d = pd.read_parquet(ATLAS/f"{key}_events.parquet")
    print(f"\n################ {key}  (n={len(d)}) ################", flush=True)
    base = cell_stats(d)
    print(f"BASE: hit2={base['hit2']:.3f} hitH={base['hitH']:.3f} ext1.5x={base['e2']:.3f} "
          f"medT={base['med_t']} medBounces={base['med_nb']} medMAE={base['med_mae']:.0f}bps "
          f"r24={base['r24_mean']:+.1f}bps")

    def show(title, grp):
        print(f"-- {title}")
        for gname, gd in grp:
            s = cell_stats(gd)
            print(f"   {str(gname):>14s}: n={s['n']:>5d} hit2={s['hit2']:.3f} hitH={s['hitH']:.3f} "
                  f"ext={s['e2']:.3f} T={s['med_t']:>3d} nb={s['med_nb']} mae={s['med_mae']:.0f} r24={s['r24_mean']:+.1f}")

    show("A. wick decile dose-response", d.groupby("uwd"))
    show("B1. trend quintile", d.groupby("trend"))
    show("B2. SMA50 alignment", d.groupby("smaal"))
    show("C. prior candle dir", d.groupby("prev"))
    show("D. volume quintile", d.groupby("volq"))
    show("E. candle type", d.groupby("typ"))
    show("G1. session block", d.assign(blk=d.hr//6).groupby("blk"))
    show("G2. day of week", d.groupby("dow"))
    show("H. BTC regime", d.groupby("reg"))

    # ---- single-condition lift scan with BH ----
    scans=[]
    feat_specs = [("uwd", list(range(1,11))), ("uwd_ge", list(range(5,11))),
                  ("trend", [0,1,2,3,4]), ("trend_ge",[1,2,3]),
                  ("smaal",[-1,1]), ("prev",[-1,0,1]), ("volq",[0,1,2,3,4]),
                  ("volq_ge",[2,3]), ("typ",[0,1,2]), ("rng_q",[0,1,2,3,4]),
                  ("reg",[0,1,2])]
    pvals=[]
    keys_order=[]
    for feat, vals in feat_specs:
        for v in vals:
            if feat.endswith("_ge"):
                f,v2 = feat[:-3], v
                m = d[f]>=v2
            else:
                m = d[feat]==v
            sub = d[m]
            rest = d[~m]
            if len(sub)<80 or len(rest)<80: continue
            s = cell_stats(sub)
            # BH test: hitH vs rest (two-prop z)
            n1,x1 = len(sub), sub.hitH.sum()
            rest = d[~m]; n0,x0 = len(rest), rest.hitH.sum()
            p1,p0 = x1/n1, x0/n0
            pp=(x1+x0)/(n1+n0); se=np.sqrt(pp*(1-pp)*(1/n1+1/n0))
            z=(p1-p0)/se if se>0 else 0
            pv=2*(1-stats.norm.cdf(abs(z)))
            pvals.append(pv); keys_order.append((feat,v,s,p1-p0))
    q = stats.false_discovery_control(np.array(pvals), method="bh") if pvals else []
    print("-- I. single-condition scan (BH<0.05 shown)")
    for (feat,v,s,delta),qi in zip(keys_order,q):
        if qi<0.05:
            print(f"   * {feat}={v}: n={s['n']} hitH={s['hitH']:.3f} (Δ{delta:+.3f}, q={qi:.3f}) "
                  f"ext={s['e2']:.3f} r24={s['r24_mean']:+.1f}")
            cond_rows.append(dict(series=key, cond=f"{feat}={v}", **s, delta_hitH=delta, q=round(float(qi),4)))
        else:
            cond_rows.append(dict(series=key, cond=f"{feat}={v}", **s, delta_hitH=delta, q=round(float(qi),4)))

    # ---- combo gates ----
    print("-- J. combo gates")
    for cname, fn in COMBOS.items():
        m = fn(d); sub=d[m]
        if len(sub)<40:
            print(f"   {cname}: n={len(sub)} too few"); continue
        s = cell_stats(sub)
        rest=d[~m]
        print(f"   {cname}: n={s['n']} hit2={s['hit2']:.3f} hitH={s['hitH']:.3f} ext={s['e2']:.3f} "
              f"T={s['med_t']} r24={s['r24_mean']:+.1f} (rest hitH={rest.hitH.mean():.3f})")
        cond_rows.append(dict(series=key, cond=cname, **s, delta_hitH=s['hitH']-rest.hitH.mean(), q=np.nan))

pd.DataFrame(cond_rows).to_csv(OUT/"w4b_conditions.csv", index=False)
print("\nwrote outputs/w4b_conditions.csv")
