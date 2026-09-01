"""Identity + BH unit tests for LOSER_FACTOR_EXT pass.

Loads TRAIN E1-E4 via setup_meas_ext, asserts n and max-entry, and asserts the
BH step-up implementation. No full PnL beyond baseline re-assert.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "V2" / "scripts"))

import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS
from loser_factor_ext import setup_meas_ext, ENTRY, bh_reject


def test_n_and_max_entry():
    expected_n = {"E1": 6420, "E2": 6101, "E3": 2215, "E4": 1470}
    for tag, (sym, tf, nm) in ENTRY.items():
        m = setup_meas_ext(sym, tf, nm)
        n = int(m["n"])
        assert n in {6420, 6101, 2215, 1470}, f"{tag}: n={n} not in allowed set"
        assert n == expected_n[tag], f"{tag}: n={n} != expected {expected_n[tag]}"
        max_entry = pd.to_datetime(m["entry_dates"]).max()
        assert max_entry < pd.Timestamp("2025-01-01", tz="UTC"), \
            f"{tag}: max entry {max_entry} >= 2025-01-01 (EVAL/leak)"


def test_bh_unit_checks():
    p1 = [0.01, 0.02, 0.03, 0.04, 0.05]
    assert bh_reject(p1, q=0.05).all()
    p2 = [0.01, 0.03, 0.10, 0.20, 0.30]
    assert bh_reject(p2, q=0.05).tolist() == [True, False, False, False, False]


if __name__ == "__main__":
    test_n_and_max_entry()
    print("PASS: n in {6420,6101,2215,1470} and max entry < 2025-01-01 for all E1-E4")
    test_bh_unit_checks()
    print("PASS: BH step-up unit checks")
    print("ALL IDENTITY TESTS PASS")
