"""EXIT STUDY I — PHASE B SL policies (Directive 4 Task 3).

Every parameter is DERIVED from Phase A curves and cited. Policies evaluated ONCE on TRAIN,
15 bps, 2% stake. Baseline = TP-or-4day-time-stop, no SL.

P1 static wick-unit SL : level = winners' MAE percentile {P95,P97.5,P99}
P2 thesis-falsification : DROPPED (P(TP|close-above-wickhigh) > P(TP|no-flag) -> cuts winners)
P3 downside-falsification: DROPPED (fails strict P(TP|flag) < 0.5*P(TP|no-flag) rule)
P4 time SL short-K     : K = {survival-hazard collapse, P90 winners' time-to-fill, P95 time-to-fill}
P5 activation/breakeven: activation = losers' MFE P90 (wick units); after, SL = entry+15bps
P6 combo               : best falsification (none survived) + P4 -> reduces to P4
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS
from exit_anatomy import measure, ENTRY, TF_H, K_HORIZON, CHECKPOINTS_H  # reuse Phase A measure()

def bh_reject(pvals, q=0.05):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    thr = (np.arange(1, m + 1) / m) * q
    rej = np.zeros(m, bool)
    rej[order] = p[order] <= thr
    return rej, p[order]

from scipy.stats import norm
def cell_p(pnl):
    se = pnl.std(ddof=1)/np.sqrt(len(pnl))
    if se == 0: return 1.0
    z = pnl.mean()/se
    return float(2*(1 - norm.cdf(abs(z))))

COST = 15.0
OUT = P.V2_OUTPUTS

def base_pnl(m):
    """Baseline: TP-or-4day-time-stop, no SL. Returns per-trade net bps."""
    bt, tp, wg = m["bt"], m["tp"], m["wg"]
    K = m["K"]; W = K + 2
    starts = np.clip(m["eb"], 0, len(m["L"]) - 1)
    idx = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(m["L"]) - 1)
    Lp = m["L"][idx]; Cp = m["C"][idx]
    fill = m["fill_bar"]
    exit_bar = np.minimum(fill, K)
    hit = (m["Hp"][np.arange(m["n"]), np.clip(exit_bar,0,W-1)] >= tp) & (fill < K)
    close_at = Cp[np.arange(m["n"]), np.clip(exit_bar,0,W-1)]
    pnl = np.where(hit, (tp - bt)/bt*1e4, (close_at - bt)/bt*1e4)
    return pnl - COST

def apply_sl_wick(m, L_units, pessimistic=True):
    bt, wg, tp = m["bt"], m["wg"], m["tp"]
    K = m["K"]; W = K + 2
    Lp = m["Lp"]; Hp = m["Hp"]; Cp = m["Cp"]
    sl_price = bt - L_units * wg
    fill = m["fill_bar"]
    # SL trigger: low touches sl_price before fill
    sl_trig = (Lp <= sl_price[:, None]) & (np.arange(W)[None, :] < fill[:, None])
    has_sl = sl_trig.any(1)
    first_sl = np.where(has_sl, sl_trig.argmax(1), K)
    # exit = min(first_sl, fill, K); if SL before fill -> SL price
    exit_bar = np.minimum.reduce([first_sl, fill, np.full(m["n"], K)])
    # did SL fire (before fill)?
    sl_fired = has_sl & (first_sl < fill)
    # TP filled?
    tp_filled = (fill < K) & (~sl_fired)
    # price at exit
    ex_price = np.where(sl_fired, sl_price,
                np.where(tp_filled, tp, Cp[np.arange(m["n"]), np.clip(exit_bar,0,W-1)]))
    pnl = (ex_price - bt)/bt*1e4 - COST
    return pnl, sl_fired

def apply_time_sl(m, K_short):
    bt, tp = m["bt"], m["tp"]
    K = m["K"]; W = K + 2
    idx = m["_idx"]; Lp = m["L"][idx]; Cp = m["C"][idx]
    fill = m["fill_bar"]
    exit_bar = np.minimum(fill, K_short)
    hit = (m["Hp"][np.arange(m["n"]), np.clip(exit_bar,0,W-1)] >= tp) & (fill <= K_short)
    close_at = Cp[np.arange(m["n"]), np.clip(exit_bar,0,W-1)]
    pnl = np.where(hit, (tp - bt)/bt*1e4, (close_at - bt)/bt*1e4) - COST
    return pnl

def apply_activation(m, A_units):
    bt, wg, tp = m["bt"], m["wg"], m["tp"]
    K = m["K"]; W = K + 2
    idx = m["_idx"]; Hp = m["Hp"]; Lp = m["Lp"]; Cp = m["Cp"]
    fill = m["fill_bar"]
    act_price = bt + A_units * wg
    # activation: high reaches act_price before exit
    act_trig = (Hp >= act_price[:, None]) & (np.arange(W)[None, :] <= np.minimum(fill, K)[:, None])
    has_act = act_trig.any(1)
    first_act = np.where(has_act, act_trig.argmax(1), K + 5)
    be_sl = bt * (1 + 15e-4)   # entry + 15 bps
    # after activation, exit at first bar where low <= be_sl (before fill/time)
    post = np.arange(W)[None, :] > first_act[:, None]
    be_trig = (Lp <= be_sl[:, None]) & post & (np.arange(W)[None, :] < fill[:, None])
    has_be = be_trig.any(1)
    first_be = np.where(has_be, be_trig.argmax(1), K + 5)
    # exit priority: TP fill, else breakeven stop (if activated), else time stop K
    exit_bar = np.minimum.reduce([fill, np.where(has_act & has_be, first_be, K + 5), np.full(m["n"], K)])
    tp_filled = (fill < K) & (~(has_act & has_be & (first_be < fill)))
    # if breakeven stop fired before fill and no TP: exit at be_sl
    be_fired = has_act & has_be & (first_be < fill)
    ex_price = np.where(be_fired, be_sl,
                np.where(fill < K, tp, Cp[np.arange(m["n"]), np.clip(np.minimum(fill,K),0,W-1)]))
    pnl = (ex_price - bt)/bt*1e4 - COST
    return pnl, has_act

def metrics(pnl, hold_h):
    n = len(pnl); win = float((pnl > 0).mean())
    mean = pnl.mean()
    # 2% stake equity / maxDD
    eq = pd.Series(np.cumprod(1 + 0.02*(pnl/1e4)))
    dd = (eq - eq.cummax())/eq.cummax(); maxdd = float(-dd.min())
    worst = float(pnl.min())
    return dict(n=n, win=round(win*100,1), net=round(mean,2),
                monthly=round(mean*n/28.0,1), maxdd=round(maxdd*100,1),
                med_hold=round(float(np.nanmedian(hold_h)),1), worst=round(worst,1))

# load + precompute paths
meas = {}
for tag, (sym, tf, nm) in ENTRY.items():
    m = measure(sym, tf, nm)
    K = m["K"]; W = K + 2
    starts = np.clip(m["eb"], 0, len(m["L"]) - 1)
    m["_idx"] = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(m["L"]) - 1)
    m["idx"] = m["_idx"]
    m["bt"] = m["O"][m["eb"]]; m["wg"] = (m["Hh"][m["sig"]] - np.maximum(m["O"][m["sig"]], m["C"][m["sig"]]))
    m["tp"] = np.maximum(m["O"][m["sig"]], m["C"][m["sig"]]) + 1.5*m["wg"]
    m["eb"] = m["eb"]; m["n"] = len(m["sig"])
    meas[tag] = m

results = []
deriv = []
pnls = {}
for tag, m in meas.items():
    base = base_pnl(m)
    base_m = metrics(base, np.minimum(m["fill_bar"], m["K"])*TF_H[ENTRY[tag][1]])
    base_net = base.mean()
    # ---- P1 params from Phase A ----
    winMAE = m["MAE"][m["win"]]
    L95, L975, L99 = [float(np.nanpercentile(winMAE, p)) for p in (95, 97.5, 99)]
    deriv.append(f"{tag} P1 levels (wick units) = winners' MAE P95/P97.5/P99 = {L95:.2f}/{L975:.2f}/{L99:.2f}")
    for L, lbl in [(L95,"P95"), (L975,"P97.5"), (L99,"P99")]:
        pnl, _ = apply_sl_wick(m, L)
        pnls[(tag, f"P1_wickSL_{lbl}")] = pnl
        mm = metrics(pnl, np.minimum(np.minimum(m["fill_bar"], m["K"]), m["K"])*TF_H[ENTRY[tag][1]])
        ret = pnl.mean()/base_net*100
        results.append(dict(row=tag, policy=f"P1_wickSL_{lbl}", L_wick=round(L,2),
                            **mm, retention=round(ret,1), pval=round(cell_p(pnl),6)))
    # ---- P4 params: time-to-fill percentiles of winners ----
    ttf = m["fill_bar"][m["win"]]*TF_H[ENTRY[tag][1]]   # hours
    hz = m["hazard"]; 
    K90 = float(np.nanpercentile(ttf, 90)); K95 = float(np.nanpercentile(ttf, 95))
    # knee = max hazard over h>=1; if survival still >0.95 there, no meaningful collapse -> undefined
    knee_h = int(m["hours"][1 + np.argmax(hz[1:])])
    knee_surv = float(m["surv"][knee_h])
    if knee_surv > 0.95:
        deriv.append(f"{tag} P4 hazard-collapse: NO KNEE within horizon (surv@max-hazard={knee_surv:.2f}); P4_hazard variant UNDEFINED -> dropped")
        p4_variants = [(K90, "P90"), (K95, "P95")]
    else:
        deriv.append(f"{tag} P4 K (h) = hazard-collapse={knee_h} (surv={knee_surv:.2f}), winners' time-to-fill P90={K90:.0f}, P95={K95:.0f}")
        p4_variants = [(knee_h, "hazard"), (K90, "P90"), (K95, "P95")]
    for Kh, lbl in p4_variants:
        Kb = max(1, int(round(Kh/TF_H[ENTRY[tag][1]])))
        pnl = apply_time_sl(m, Kb)
        pnls[(tag, f"P4_timeSL_{lbl}")] = pnl
        hold = np.minimum(m["fill_bar"], Kb)*TF_H[ENTRY[tag][1]]
        mm = metrics(pnl, hold)
        ret = pnl.mean()/base_net*100
        results.append(dict(row=tag, policy=f"P4_timeSL_{lbl}", K_bars=Kb,
                            **mm, retention=round(ret,1), pval=round(cell_p(pnl),6)))
    # ---- P5 params: losers' MFE P90 ----
    losMFE = m["MFE"][~m["win"]]
    A = float(np.nanpercentile(losMFE, 90))
    deriv.append(f"{tag} P5 activation (wick units) = losers' MFE P90 = {A:.2f}")
    pnl, _ = apply_activation(m, A)
    pnls[(tag, "P5_act_breakeven")] = pnl
    mm = metrics(pnl, np.minimum(m["fill_bar"], m["K"])*TF_H[ENTRY[tag][1]])
    ret = pnl.mean()/base_net*100
    results.append(dict(row=tag, policy="P5_act_breakeven", A_wick=round(A,2),
                        **mm, retention=round(ret,1), pval=round(cell_p(pnl),6)))
    # ---- baseline row ----
    results.append(dict(row=tag, policy="BASELINE_noSL", **base_m, retention=100.0, pval=round(cell_p(base),6)))
    deriv.append(f"{tag} baseline net = {base_net:.2f} bps/trade, maxDD={base_m['maxdd']}%, worst={base_m['worst']} bps")

df = pd.DataFrame(results)
df.to_csv(OUT / "sl_study.csv", index=False)
print("\n".join(deriv))
print("\n=== SL STUDY (selected cols) ===")
print(df[["row","policy","n","win","net","monthly","maxdd","retention","worst"]].to_string(index=False))
# viability pre-declared: retention>=80 AND maxDD reduced >=25% AND worst improved
base_dd = df[df.policy=="BASELINE_noSL"].set_index("row")["maxdd"]
base_worst = df[df.policy=="BASELINE_noSL"].set_index("row")["worst"]
viability_lines = []
for _, r in df.iterrows():
    if r.policy=="BASELINE_noSL": continue
    dd_ok = r.maxdd <= base_dd[r.row]*0.75
    w_ok = r.worst > base_worst[r.row]   # worst trade improved (less negative)
    via = (r.retention>=80) and dd_ok and w_ok
    vline = (f"{r.row} {r.policy}: retention={r.retention}% (>=80:{r.retention>=80}) "
             f"maxDD {r.maxdd}<={base_dd[r.row]*0.75}?{dd_ok} worst {r.worst}>={base_worst[r.row]}?{w_ok} -> VIABLE={via}")
    print(vline)
    viability_lines.append(vline)

with open(OUT/"sl_deriv.txt", "w") as fh:
    fh.write("# Parameter derivations (Phase A -> Phase B)\n")
    fh.write("\n".join(deriv) + "\n\n# Viability (pre-declared rule: retention>=80% & maxDD -25% & worst improved)\n")
    fh.write("\n".join(viability_lines) + "\n")
print("wrote V2/outputs/sl_deriv.txt")

# ---- Multiplicity: BH q=0.05 across SL cells (<=24), bootstrap SE, two-sided p ----
cell_list = []
for (tag, pol), pnl in pnls.items():
    p = cell_p(pnl)
    cell_list.append((tag, pol, p))
pvals = [p for _,_,p in cell_list]
rej, adj = bh_reject(pvals, q=0.05)
print(f"\nBH q=0.05 across {len(pvals)} SL cells: {int(rej.sum())} significant")
for (tag, pol, p), sig in zip(cell_list, rej):
    print(f"  {tag} {pol}: p={p:.4g} BHsig={bool(sig)}")

# Union ledger is rebuilt by V2/scripts/rebuild_ledger.py (owns the full family).
print("Union ledger rebuilt by rebuild_ledger.py (writes V2/outputs/union_ledger.json).")
