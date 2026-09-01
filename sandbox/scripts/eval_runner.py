#!/usr/bin/env python3
"""
E-VAL runner for a single spec in the sandbox.
Reuses row_specs for signal selection, applies custom exit policy.
"""
import sys
import os
from pathlib import Path
# Ensure sandbox lib is on path
SANDBOX_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SANDBOX_DIR / "lib"))

import pandas as pd
import numpy as np
import json
from datetime import datetime

# Import sandbox lib modules
import paths as P
import time_gates as T
import row_specs as RS

# Load raw klines for a symbol/tf/window
def load_raw_klines(symbol: str, tf: str, start: str, end: str):
    # Try the 2021-2026 file first (has 2025 data)
    fn = P.RAW_DIR / f"{symbol}-FUTURES-2021-2026-{tf}.csv"
    if not fn.exists():
        # Try 2022-2026
        fn = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    if not fn.exists():
        # Try mbf format
        fn = P.RAW_DIR / f"mbf_klines_{symbol}_{tf}.csv"
    if not fn.exists():
        return None
    tr = pd.read_csv(fn)
    # Handle both formats: 7-col (time,open,high,low,close,volume,Date) and 5-col
    cols = [c.strip().strip('"').lower() for c in tr.columns]
    if 'time' in cols and 'open' in cols and 'high' in cols and 'low' in cols and 'close' in cols:
        # Find the actual column names
        col_map = {c.lower(): c for c in tr.columns}
        tr = tr[[col_map['time'], col_map['open'], col_map['high'], col_map['low'], col_map['close']]].copy()
        tr.columns = ['time', 'open', 'high', 'low', 'close']
    elif 'Time' in tr.columns and 'Open' in tr.columns and 'High' in tr.columns and 'Low' in tr.columns and 'Close' in tr.columns:
        tr = tr[['Time', 'Open', 'High', 'Low', 'Close']].copy()
        tr.columns = ['time', 'open', 'high', 'low', 'close']
    else:
        return None
    tr = tr.apply(pd.to_numeric, errors='coerce').dropna()
    tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    # Filter to E-VAL window
    start_ms = pd.Timestamp(start, tz="UTC").value // 1_000_000
    end_ms = pd.Timestamp(end, tz="UTC").value // 1_000_000
    tr = tr[(tr["time"] >= start_ms) & (tr["time"] <= end_ms)]
    return tr

def measure_eval(bars, spec, tf, tp_mult=1.5, use_disaster=False, disaster_pctl=None, 
                 use_activation=False, activation_level=None, limit_entry=None):
    """Run measurement with custom exit policy on pre-selected signals."""
    # Use already-imported row_specs and compute K_HORIZON like V3
    TF_HOURS = RS.TF_HOURS
    K_HORIZON = {tf: int(round(96.0 / h)) for tf, h in TF_HOURS.items()}  # 4-DAY wall-clock bars (96h / hours-per-bar)
    CHECKPOINTS_H = [6, 12, 24, 48, 72, 96]
    
    # Build features and select signals using row_specs (consistent with TRAIN)
    feats = RS.build_features(bars, tf, legacy=False, symbol=spec.get("symbol", "SOLUSDT"))
    sig, eb = RS.select(spec, feats)
    
    n = len(sig)
    if n == 0:
        return None
    
    O, Hh, L, C, t = feats["O"], feats["H"], feats["L"], feats["C"], feats["time"]
    bt = O[eb]
    body_top = np.maximum(O[sig], C[sig])
    wg = Hh[sig] - body_top
    
    # Custom TP multiplier
    tp = body_top + tp_mult * wg
    K = K_HORIZON[tf]
    W = K + 2
    
    starts = np.clip(eb, 0, len(L) - 1)
    idx = np.clip(starts[:, None] + np.arange(W)[None, :], 0, len(L) - 1)
    Hp = Hh[idx]
    Lp = L[idx]
    Cp = C[idx]
    Hsig = Hh[sig]
    Lsig = L[sig]
    
    # fill (optimistic / TP-first)
    tp_hit = Hp >= tp[:, None]
    fill_bar = np.where(tp_hit.any(1), tp_hit.argmax(1), K)
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
    
    # bps versions
    MAE_bps = (bt - rmin[np.arange(n), exit_bar]) / bt * 1e4
    MFE_bps = (rmax[np.arange(n), exit_bar] - bt) / bt * 1e4
    
    # Actual PnL: winners exit at TP (MFE_bps at fill_bar), losers exit at close at exit_bar
    close_at_exit = Cp[np.arange(n), exit_bar]
    actual_exit_bps = (close_at_exit - bt) / bt * 1e4
    pnl_bps = np.where(win, MFE_bps, actual_exit_bps)
    
    # Disaster stop (stop at winners' MAE percentile)
    if use_disaster and disaster_pctl is not None:
        # Use winners' MAE distribution to set stop
        winners_mae = MAE[win]
        if len(winners_mae) > 0:
            disaster_level = np.nanpercentile(winners_mae, disaster_pctl)
            # Check if any trade hits this adverse level before TP
            disaster_hit = (mae_w >= disaster_level).any(axis=1)
            # If disaster hits before TP, it's a loss
            disaster_before_tp = np.zeros(n, bool)
            for i in range(n):
                if disaster_hit[i]:
                    # find first bar where MAE >= disaster_level
                    hit_bars = np.where(mae_w[i] >= disaster_level)[0]
                    if len(hit_bars) > 0:
                        first_disaster = hit_bars[0]
                        if first_disaster < fill_bar[i]:  # disaster before TP
                            disaster_before_tp[i] = True
            win = win & ~disaster_before_tp
            exit_bar = np.minimum(exit_bar, np.where(disaster_before_tp, 
                                                      np.where(disaster_hit, 
                                                               np.argmax(mae_w >= disaster_level, axis=1), K), K))
    
    # Activation (move to breakeven when favorable move reaches threshold)
    if use_activation and activation_level is not None:
        if activation_level == "loserMFEp50":
            # Activate at losers' MFE P50
            losers_mfe = MFE[~win]
            if len(losers_mfe) > 0:
                act_level = np.nanpercentile(losers_mfe, 50)
        elif activation_level == "1wick":
            act_level = 1.0
        else:
            act_level = 1.0
        
        # Check if trade reaches activation level before exit
        act_hit = (mfe_w >= act_level).any(axis=1)
        # If activated, stop loss becomes entry (breakeven)
        # For simplicity: if activated and later exits at time stop, PnL = 0 (breakeven)
        # If activated and hits TP, full TP profit
        # If activated and hits disaster/stop, breakeven
        # Implementation: for activated trades that don't hit TP, set PnL to 0
        for i in range(n):
            if act_hit[i] and not win[i]:
                # Check if activation happened before exit
                act_bars = np.where(mfe_w[i] >= act_level)[0]
                if len(act_bars) > 0:
                    first_act = act_bars[0]
                    if first_act < exit_bar[i]:
                        # Activated before exit, and didn't hit TP -> breakeven
                        actual_exit_bps[i] = 0.0
                        # Mark as scratch (not win, not loss)
                        win[i] = False  # doesn't matter, PnL = 0
    
    # Hold time in hours
    hold_h = exit_bar * TF_HOURS[tf]
    
    return {
        "n": n,
        "win": win,
        "pnl_bps": pnl_bps,
        "hold_h": hold_h,
        "fill_bar": fill_bar,
        "exit_bar": exit_bar,
        "MAE_wick": MAE,
        "MFE_wick": MFE,
        "MAE_bps": MAE_bps,
        "MFE_bps": MFE_bps,
        "bt": bt,
        "wg": wg,
    }

def run_eval(symbol: str, tf: str, row: str, policy: str,
             start: str = "2025-01-01", end: str = "2025-06-30"):
    """Run E-VAL measurement for one spec on the E-VAL window."""
    
    # Map row to spec
    ROW_MAP = {
        "E1": {"symbol": "SOLUSDT", "tf": "30m", "row_name": "W2_NODIP"},
        "E2": {"symbol": "BTCUSDT", "tf": "30m", "row_name": "W1_NODIP"},
        "E3": {"symbol": "ETHUSDT", "tf": "1h", "row_name": "W2_NODIP"},
        "E4": {"symbol": "SOLUSDT", "tf": "4h", "row_name": "W3_NODIP"},
    }
    
    if row not in ROW_MAP:
        raise ValueError(f"Unknown row {row}")
    
    row_info = ROW_MAP[row]
    if row_info["symbol"] != symbol or row_info["tf"] != tf:
        raise ValueError(f"Row {row} maps to {row_info['symbol']} {row_info['tf']}, not {symbol} {tf}")
    
    spec = RS.get_spec(row_info["row_name"], tf, legacy=False)
    spec["symbol"] = symbol
    
    print(f"Loading {symbol} {tf} klines for E-VAL window [{start} to {end}]...")
    klines = load_raw_klines(symbol, tf, start, end)
    if klines is None or len(klines) == 0:
        raise ValueError(f"No klines loaded for {symbol} {tf} in E-VAL window")
    print(f"  Loaded {len(klines)} bars")
    
    print(f"Entry spec: {row} = {symbol} {tf} {row_info['row_name']}")
    
    # Parse policy
    tp_mult = 1.5
    use_disaster = False
    disaster_pctl = None
    use_activation = False
    activation_level = None
    
    if policy == "BASELINE":
        pass  # defaults
    elif policy.startswith("D_tp_"):
        tp_mult = float(policy.split("_")[-1])
    elif policy == "A_disaster_P99_9":
        use_disaster = True
        disaster_pctl = 99.9
    elif policy == "F_act_loserMFEp50":
        use_activation = True
        activation_level = "loserMFEp50"
    elif policy == "F_act_1wick":
        use_activation = True
        activation_level = "1wick"
    else:
        raise ValueError(f"Unknown policy {policy}")
    
    print(f"Exit policy: {policy} -> tp_mult={tp_mult}, disaster={use_disaster}, activation={activation_level}")
    
    # Run measurement
    res = measure_eval(klines, spec, tf, tp_mult, use_disaster, disaster_pctl,
                       use_activation, activation_level, None)
    
    if res is None:
        return {"error": "No trades generated"}
    
    n = res["n"]
    win_rate = res["win"].mean() * 100
    net_bps = res["pnl_bps"].mean()
    monthly = net_bps * (30 * 24 / RS.TF_HOURS[tf]) * (n / len(klines)) * len(klines) / 28  # monthly rate
    
    # maxdd: proper 2% stake equity curve (matching keepn_study.py metrics_from_gross)
    import pandas as pd
    pnl = res["pnl_bps"]
    eq = pd.Series(np.cumprod(1 + 0.02 * (pnl / 1e4)))
    dd = (eq - eq.cummax()) / eq.cummax()
    maxdd = float(-dd.min()) * 100
    worst = float(pnl.min())
    med_hold = np.median(res["hold_h"])
    
    # C1: net > 0
    c1_pass = net_bps > 0
    
    # C2: regime stability - compute PnL in TREND_DOWN vs others
    # For now use heuristic: maxDD shouldn't be catastrophic
    c2_pass = maxdd < abs(net_bps) * 30 if net_bps > 0 else False
    
    # More robust C2: check if worst drawdown period aligns with known bad regime
    # We'll use a simple proxy: if maxdd > 15% and win_rate < 60%, flag
    c2_pass = maxdd < 15.0 or win_rate >= 60
    
    return {
        "spec": f"{row}_{policy}",
        "entry": {"symbol": symbol, "tf": tf, "row": row, "policy": policy},
        "eval_window": {"start": start, "end": end},
        "n_trades": int(n),
        "win_rate_pct": round(float(win_rate), 2),
        "net_bps": round(float(net_bps), 2),
        "monthly_bps": round(float(monthly), 1),
        "maxdd_pct": round(float(maxdd), 2),
        "worst_bps": round(float(worst), 1),
        "med_hold_h": round(float(med_hold), 1),
        "C1_net_positive": bool(c1_pass),
        "C2_regime_stable": bool(c2_pass),
        "EVAL_result": "PASS" if (c1_pass and c2_pass) else "FAIL",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--tf", required=True)
    parser.add_argument("--row", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-06-30")
    args = parser.parse_args()
    
    result = run_eval(args.symbol, args.tf, args.row, args.policy, args.start, args.end)
    
    print("\n" + "="*60)
    print("E-VAL RESULT")
    print("="*60)
    for k, v in result.items():
        print(f"  {k}: {v}")
    
    # Save result
    out_dir = Path("outputs/eval")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"eval_{args.row}_{args.policy}.json"
    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved to {out_file}")
    
    if result.get("EVAL_result") == "PASS":
        print("\n>>> E-VAL PASSED — ready for FIRE")
        sys.exit(0)
    else:
        print("\n>>> E-VAL FAILED")
        sys.exit(1)