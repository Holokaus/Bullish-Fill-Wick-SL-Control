"""EXIT STUDY I — PHASE A anatomy (Directive 4 Task 2).

Pure measurement, zero parameters, zero P&L. For each of the 4 fixed entry rows (E1-E4),
replay every trade's forward path and record: MAE, MFE, fill survival + hazard, state
divergence, falsification stats, worst-loser anatomy, per-asset separability.

Units: wick units (1.0 = signal candle's own wick gap); times in wall-clock hours from entry.
Bars: intrabar ambiguity noted; Phase A uses optimistic (TP-first) resolution, flagged.
Rows loaded BY NAME from src/lib/row_specs.py. TRAIN only (time_gates).
"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS

ENTRY = {
    "E1": ("SOLUSDT", "30m", "W2_NODIP"),
    "E2": ("BTCUSDT", "30m", "W1_NODIP"),
    "E3": ("ETHUSDT", "1h",  "W2_NODIP"),
    "E4": ("SOLUSDT", "4h",  "W3_NODIP"),
}
TF_H = {"30m": 0.5, "1h": 1.0, "4h": 4.0}
K_HORIZON = {"30m": 192, "1h": 96, "4h": 24}   # 4-day wall-clock
CHECKPOINTS_H = [6, 12, 24, 48, 72, 96]

def load(symbol, tf):
    fn = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    tr = pd.read_csv(fn)
    low = {c.strip().strip('"').lower(): c for c in tr.columns}
    inv = {v: k for k, v in low.items()}
    tr = tr.rename(columns=inv)[["time", "open", "high", "low", "close"]].apply(pd.to_numeric)
    tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    return T.filter_window(tr, "TRAIN")

def measure(symbol, tf, name):
    bars = load(symbol, tf)
    feats = RS.build_features(bars, tf, legacy=False, symbol=symbol)
    spec = RS.get_spec(name, tf, legacy=False)
    sig, eb = RS.select(spec, feats)
    O, Hh, L, C, t = feats["O"], feats["H"], feats["L"], feats["C"], feats["time"]
    n = len(sig)
    bt = O[eb]
    body_top = np.maximum(O[sig], C[sig]); wg = Hh[sig] - body_top
    tp = body_top + 1.5 * wg
    K = K_HORIZON[tf]; W = K + 2
    starts = np.clip(eb, 0, len(L) - 1)
    idx = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(L) - 1)
    Hp = Hh[idx]; Lp = L[idx]; Cp = C[idx]
    Hsig = Hh[sig]; Lsig = L[sig]
    # fill (optimistic / TP-first)
    tp_hit = Hp >= tp[:, None]
    fill_bar = np.where(tp_hit.any(1), tp_hit.argmax(1), K)     # bar of first TP touch (<=K) else K
    win = fill_bar < K
    exit_bar = np.minimum(fill_bar, K)
    # running min low / max high up to exit
    rmin = np.minimum.accumulate(Lp, axis=1)
    rmax = np.maximum.accumulate(Hp, axis=1)
    # MAE / MFE in wick units, up to exit_bar (inclusive)
    ebidx = exit_bar[:, None]
    mask = np.arange(W)[None, :] <= ebidx
    mae_w = (bt[:, None] - rmin) / wg[:, None]
    mfe_w = (rmax - bt[:, None]) / wg[:, None]
    MAE = np.where(mask, mae_w, -np.inf).max(axis=1)
    MFE = np.where(mask, mfe_w, -np.inf).max(axis=1)
    # bps versions: MAE_bps = (bt - min_low)/bt*1e4 ; MFE_bps = (max_high - bt)/bt*1e4
    MAE_bps = (bt - rmin[np.arange(n), exit_bar]) / bt * 1e4
    MFE_bps = (rmax[np.arange(n), exit_bar] - bt) / bt * 1e4
    # survival in wall-clock hours (optimistic)
    filled_cum = np.maximum.accumulate(tp_hit.astype(int), axis=1)
    bar_per_h = int(round(1.0 / TF_H[tf]))
    surv_bar = filled_cum   # 1 if filled by that bar
    # aggregate to hourly
    hours = np.arange(0, 96 + 1)
    def surv_at_h(h):
        b = min(int(round(h / TF_H[tf])), W - 1)
        return surv_bar[:, b].mean()
    surv = np.array([surv_at_h(h) for h in hours])
    hazard = np.zeros_like(surv)
    for i in range(1, len(hours)):
        s_prev = surv[i - 1]
        hazard[i] = (surv[i - 1] - surv[i]) / s_prev if s_prev > 0 else 0.0
    # state divergence: uPnL_wick at checkpoints, tercile, P(TP|tercile)
    div = []
    for h in CHECKPOINTS_H:
        b = min(int(round(h / TF_H[tf])), W - 1)
        uPnL = (Cp[:, b] - bt) / wg
        q = np.nanquantile(uPnL, [1/3, 2/3])
        terr = np.digitize(uPnL, q) + 1   # 1 worst,2,3 best
        for tt in (1, 2, 3):
            msk = terr == tt
            div.append((h, tt, int(msk.sum()), round(float(win[msk].mean()) * 100, 1)))
    # falsification: before fill, did a CLOSE cross wick-high / wick-low / entry-1wick?
    pre = np.arange(W)[None, :] < fill_bar[:, None]
    close_above_wh = (Cp >= Hsig[:, None]) & pre
    close_below_wl = (Cp <= Lsig[:, None]) & pre
    close_below_e1 = (Cp <= (bt - wg)[:, None]) & pre
    def falsify_stat(flag):
        f = flag.any(1)
        p_tp_f = float(win[f].mean()) if f.sum() else np.nan
        p_tp_nf = float(win[~f].mean()) if (~f).sum() else np.nan
        return int(f.sum()), round(p_tp_f * 100, 1), round(p_tp_nf * 100, 1)
    fal = {
        "close_above_wickhigh": falsify_stat(close_above_wh),
        "close_below_wicklow": falsify_stat(close_below_wl),
        "close_below_entry_1wick": falsify_stat(close_below_e1),
    }
    # worst-loser anatomy (worst decile of losers by MAE_wick)
    los = ~win
    n_los = int(los.sum())
    mael = MAE[los]
    thr = np.nanquantile(mael, 0.9)
    worst = los & (MAE >= thr)
    # time-to-MAE for worst losers: first bar where rmin reached MAE
    # retracement victims: MFE>0 before reaching MAE depth
    retrace = np.zeros(n, bool)
    for k in np.where(worst)[0]:
        rb = exit_bar[k]
        reached = rmin[k, :rb + 1] >= MAE[k] - 1e-9
        first = np.argmax(reached) if reached.any() else rb
        retrace[k] = mfe_w[k, :first + 1].max() > 0
    entry_dates = pd.to_datetime(t[eb], unit="ms", utc=True)
    return dict(
        symbol=symbol, tf=tf, name=name, n=n, K=K, wick_gap_mean=float(wg.mean()),
        win=win, MAE=MAE, MFE=MFE, MAE_bps=MAE_bps, MFE_bps=MFE_bps,
        fill_bar=fill_bar, exit_bar=exit_bar, surv=surv, hazard=hazard, hours=hours,
        div=div, fal=fal, los=los, worst=worst, retrace=retrace,
        entry_dates=entry_dates,
        max_entry_date=str(entry_dates.max()), min_entry_date=str(entry_dates.min()),
        btc_like=(symbol == "BTCUSDT"),
        # raw arrays for Phase B
        bt=bt, wg=wg, tp=tp, O=O, Hh=Hh, L=L, C=C, sig=sig, eb=eb,
        Hp=Hp, Lp=Lp, Cp=Cp, idx=idx,
    )

OUT = P.V2_OUTPUTS
all_meas = {}
for tag, (sym, tf, nm) in ENTRY.items():
    m = measure(sym, tf, nm)
    all_meas[tag] = m
    print(f"{tag} {sym}-{tf} {nm}: n={m['n']} win%={m['win'].mean()*100:.1f} "
          f"MAE_wick win P95={np.nanpercentile(m['MAE'][m['win']],95):.2f} "
          f"loser P50={np.nanmedian(m['MAE'][~m['win']]):.2f} "
          f"max_entry={m['max_entry_date']}")
    # CSVs
    pd.DataFrame({"hour": m["hours"], "P_filled": m["surv"], "hazard": m["hazard"]}).to_csv(
        OUT / f"exit_anatomy_survival_{tag}.csv", index=False)
    pd.DataFrame(m["div"], columns=["checkpoint_h", "tercile", "n", "P_tp_pct"]).to_csv(
        OUT / f"exit_anatomy_divergence_{tag}.csv", index=False)
    fal_df = pd.DataFrame([(k, v[0], v[1], v[2]) for k, v in m["fal"].items()],
                          columns=["flag", "n_flag", "P_tp_if_flag", "P_tp_if_noflag"])
    fal_df.to_csv(OUT / f"exit_anatomy_falsify_{tag}.csv", index=False)
    # MAE/MFE percentiles split by outcome
    for label, mask in [("winner", m["win"]), ("loser", ~m["win"])]:
        sub = m["MAE"][mask]
        row = {"outcome": label, "n": int(mask.sum())}
        for p in [50, 75, 90, 95, 97.5, 99, 99.9]:
            row[f"MAE_wick_P{p}"] = round(float(np.nanpercentile(sub, p)), 3)
        pd.DataFrame([row]).to_csv(OUT / f"exit_anatomy_MAE_{tag}_{label}.csv", index=False)
        sub2 = m["MFE"][mask]
        row2 = {"outcome": label, "n": int(mask.sum())}
        for p in [50, 75, 90, 95, 97.5, 99]:
            row2[f"MFE_wick_P{p}"] = round(float(np.nanpercentile(sub2, p)), 3)
        pd.DataFrame([row2]).to_csv(OUT / f"exit_anatomy_MFE_{tag}_{label}.csv", index=False)
    print(f"  wrote exit_anatomy_*_{tag}.csv")

json.dump({t: {"n": m["n"], "win_pct": round(float(m["win"].mean())*100,1),
               "max_entry": m["max_entry_date"], "min_entry": m["min_entry_date"],
               "MAE_winner_P95": round(float(np.nanpercentile(m["MAE"][m["win"]],95)),3),
               "MAE_winner_P99": round(float(np.nanpercentile(m["MAE"][m["win"]],99)),3),
               "MAE_loser_P50": round(float(np.nanmedian(m["MAE"][~m["win"]])),3),
               "MAE_loser_P90": round(float(np.nanpercentile(m["MAE"][~m["win"]],90)),3),
               "MFE_winner_P50": round(float(np.nanpercentile(m["MFE"][m["win"]],50)),3),
               "MFE_winner_P90": round(float(np.nanpercentile(m["MFE"][m["win"]],90)),3),
               "median_fill_h": round(float(np.nanmedian(m["fill_bar"][m["win"]]) * TF_H[ENTRY[t][1]]), 2)
              } for t, m in all_meas.items()},
          open(OUT / "exit_anatomy_summary.json", "w"), indent=2)
print("PHASE A measurement done")
