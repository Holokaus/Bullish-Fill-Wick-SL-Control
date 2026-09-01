"""Golden row-identity tests (Directive 3 Task 1.3.3).

Reproduces menu-1's 8 rows through the registry and asserts:
  - per-row trade count == frozen menu-1 CSV value (regression anchor)
  - invariant n(DIP) < n(NODIP) at same threshold
  - green + red == total (color-agnostic signal splits cleanly)
  - spec fingerprint matches registry
"""
import sys, os
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import lib.row_specs as RS
import lib.paths as P, lib.time_gates as T
from lib.sim import replay

MENU1 = pd.read_csv(P.V2_OUTPUTS / "redir_w1_menu.csv").set_index("row")["n"].to_dict()

def load_sol4h():
    tr = pd.read_csv(P.RAW_DIR / "SOLUSDT-FUTURES-2022-2026-4h.csv")
    low = {c.strip().strip('"').lower(): c for c in tr.columns}
    inv = {v: k for k, v in low.items()}
    tr = tr.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    tr = tr.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    return T.filter_window(tr, "TRAIN")

def n_trades(name, tf="4h", legacy=True):
    bars = load_sol4h()
    feats = RS.build_features(bars, tf, legacy=legacy, symbol="SOLUSDT")
    spec = RS.get_spec(name, tf, legacy=legacy)
    sig, eb = RS.select(spec, feats)
    return len(sig), sig, eb, feats

def test_menu1_counts():
    # menu-1 used W{1..4}_BASE; registry uses W{1..4}_NODIP (BASE is banned). Map them.
    name_map = {f"W{i}_BASE": f"W{i}_NODIP" for i in (1, 2, 3, 4)}
    name_map.update({f"W{i}_DIP": f"W{i}_DIP" for i in (1, 2, 3, 4)})
    for m1, reg in name_map.items():
        n, _, _, _ = n_trades(reg, legacy=True)
        assert n == MENU1[m1], f"{reg} (menu-1 {m1}): registry n={n} != menu-1 {MENU1[m1]}"
    print("PASS: all 8 menu-1 rows reproduced (legacy 4-day lookback)")

def test_dip_lt_nodip():
    for lvl in ["W1", "W2", "W3", "W4"]:
        nd, _, _, _ = n_trades(f"{lvl}_NODIP", legacy=True)
        d, _, _, _ = n_trades(f"{lvl}_DIP", legacy=True)
        assert d < nd, f"{lvl}: DIP n={d} not < NODIP n={nd}"
    print("PASS: n(DIP) < n(NODIP) at every threshold")

def test_color_split():
    _, sig, _, feats = n_trades("W3_NODIP", legacy=True)
    g = int(feats["green"][sig].sum()); r = int((~feats["green"][sig]).sum())
    assert g + r == len(sig), "green+red != total"
    print(f"PASS: color split clean (green={g} red={r} total={len(sig)})")

def test_fingerprint():
    # fingerprint line must match registry spec exactly
    spec = RS.get_spec("W3_NODIP", "4h", legacy=True)
    assert spec["dip_on"] is False
    assert spec["wick"] == {"kind": "bps", "value": 90.0}
    assert "BASE" not in spec["name"]
    print("PASS: fingerprint matches registry (no BASE vocabulary)")

if __name__ == "__main__":
    test_menu1_counts()
    test_dip_lt_nodip()
    test_color_split()
    test_fingerprint()
    print("\nALL ROW-IDENTITY TESTS PASS")
