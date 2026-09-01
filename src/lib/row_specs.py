"""row_specs.py — single declarative registry for wick-fill rows (Directive 3 Task 1.3).

One source of truth. All scripts select rows BY NAME from here; none re-implements row logic.
The word "BASE" is banned; rows are W1..W4 x {NODIP, DIP}.

Dip lookback CORRECTED (Directive 3 s2.2): trailing 24-HOUR return, TF-appropriate bar count.
  legacy=True reproduces menu-1's actual (buggy) 4-day lookback for the regression anchor only.
"""
import numpy as np
import pandas as pd
import json
from pathlib import Path

ATLAS_PATH = Path(__file__).resolve().parent.parent.parent / "V2" / "outputs" / "atlas" / "atlas_cuts.json"
_ATLAS = json.load(open(ATLAS_PATH)) if ATLAS_PATH.exists() else {}

TF_HOURS = {"30m": 0.5, "1h": 1.0, "4h": 4.0, "1D": 24.0}

# wick threshold per level: absolute bps of price, OR "uw_decile>=9" (W4, TRAIN-frozen decile)
WICK_BPS = {"W1": 22.5, "W2": 45.0, "W3": 90.0}
W4_DEC = 9  # top decile of range-based upper-wick fraction

# corrected 24h dip lookback in bars, per TF
def dip_lookback_bars(tf, legacy=False):
    if legacy and tf == "4h":
        return 24          # menu-1 actual: shift(24) on 4h = 96h (the bug), for regression only
    return int(round(24.0 / TF_HOURS[tf]))   # 30m:48  1h:24  4h:6  1D:1


def spec_names():
    out = []
    for lvl in ["W1", "W2", "W3", "W4"]:
        for dip in ["NODIP", "DIP"]:
            out.append(f"{lvl}_{dip}")
    return out


def get_spec(name, tf, legacy=False):
    """Return a frozen spec dict for a row name + timeframe."""
    assert name in spec_names(), f"unknown row {name}"
    lvl, dip = name.split("_")
    wick = {"kind": "bps", "value": WICK_BPS[lvl]} if lvl != "W4" else {"kind": "decile", "value": W4_DEC}
    return {
        "name": name,
        "tf": tf,
        "wick": wick,
        "dip_on": dip == "DIP",
        "dip_lookback_bars": dip_lookback_bars(tf, legacy=legacy),
    }


def build_features(bars, tf, legacy=False, symbol="SOLUSDT"):
    """bars: TRAIN-clipped DataFrame [time,open,high,low,close] (numeric, sorted by time).
    Returns dict of np arrays aligned to bar index, plus the signal-eligible bar positions."""
    O = bars["open"].values.astype(float); H = bars["high"].values.astype(float)
    L = bars["low"].values.astype(float); C = bars["close"].values.astype(float)
    n = len(bars)
    rng = H - L
    body_top = np.maximum(O, C)
    wick_gap = H - body_top
    valid = (rng > 0) & (wick_gap > 0)
    wick_bps = np.where(valid, wick_gap / C * 1e4, np.nan)
    uw = np.where(valid, wick_gap / rng, np.nan)
    # uw decile cuts: prefer TRAIN-frozen atlas_cuts.json (matches menu-1), else TRAIN-computed
    key = f"{symbol}-{tf}"
    if _ATLAS and key in _ATLAS and "uw_deciles" in _ATLAS[key]:
        uw_deciles = np.array(_ATLAS[key]["uw_deciles"], dtype=float)
    else:
        uw_v = uw[valid]
        uw_deciles = np.nanquantile(uw_v, np.linspace(0, 1, 11)[1:-1]) if valid.any() else np.array([])
    uw_dec = np.where(np.isnan(uw), -1, np.searchsorted(uw_deciles, uw) + 1)
    # 24h-return quintile cuts
    lb = dip_lookback_bars(tf, legacy=legacy)
    ret = C / pd.Series(C).shift(lb).values - 1.0
    if legacy and _ATLAS and key in _ATLAS and "ret24_q" in _ATLAS[key]:
        # regression anchor: use the SAME atlas cuts menu-1 used (4-day lookback)
        ret_q = np.array(_ATLAS[key]["ret24_q"], dtype=float)
    else:
        ret_v = ret[valid]
        ret_q = np.nanquantile(ret_v, np.linspace(0, 1, 6)[1:-1]) if valid.any() else np.array([])
    ret_dec = np.where(np.isnan(ret), -1, np.searchsorted(ret_q, ret) + 1)
    green = C > O
    return dict(n=n, valid=valid, wick_bps=wick_bps, uw_dec=uw_dec,
                ret_dec=ret_dec, green=green, O=O, H=H, L=L, C=C,
                time=bars["time"].values.astype("int64"))


def freeze_fingerprint(asset, tf, row_name, n, trades_month, legacy=False, symbol=None):
    """Freeze-gate tripwire (Directive 3 Task 1.3.4).

    Before writing any FROZEN_CANDIDATE, assert the row's identity
    (asset / TF / threshold / dip / n / trades-per-month) matches what the registry
    computes on TRAIN. Mismatch => raise, do NOT freeze.
    `symbol` defaults to asset.
    """
    symbol = symbol or asset
    # recompute n + trades_month from registry on TRAIN
    from pathlib import Path
    import lib.paths as _P, lib.time_gates as _T
    fn = _P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    tr = pd.read_csv(fn)
    low = {c.strip().strip('"').lower(): c for c in tr.columns}
    inv = {v: k for k, v in low.items()}
    tr = tr.rename(columns=inv)[["time", "open", "high", "low", "close"]].apply(pd.to_numeric)
    tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    tr = _T.filter_window(tr, "TRAIN")
    feats = build_features(tr, tf, legacy=legacy, symbol=symbol)
    spec = get_spec(row_name, tf, legacy=legacy)
    sig, _ = select(spec, feats)
    n_calc = len(sig)
    tm_calc = round(n_calc / 28.0, 1)
    fp = f"{asset}/{tf}/{row_name}/n={n_calc}/mo={tm_calc}"
    assert n == n_calc, f"FREEZE-GATE MISMATCH: claimed n={n} but registry computes n={n_calc} ({fp})"
    assert abs(trades_month - tm_calc) < 0.05, (
        f"FREEZE-GATE MISMATCH: claimed trades_month={trades_month} but registry {tm_calc} ({fp})")
    return fp


def select(spec, feats):
    """Return (sig_idx, entry_idx) for a spec, using feats from build_features.
    Signal = any candle meeting wick threshold (color-agnostic); DIP adds bottom ret_decile."""
    valid = feats["valid"]
    sig = np.where(valid)[0]
    if spec["wick"]["kind"] == "bps":
        wm = feats["wick_bps"][sig] >= spec["wick"]["value"]
    else:
        wm = feats["uw_dec"][sig] >= spec["wick"]["value"]
    mask = wm
    if spec["dip_on"]:
        mask = mask & (feats["ret_dec"][sig] <= 1)   # bottom quintile
    sig = sig[mask]
    eb = sig + 1
    ok = eb < feats["n"]
    return sig[ok], eb[ok]
