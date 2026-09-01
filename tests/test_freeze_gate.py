"""Freeze-gate fingerprint test (Directive 3 Task 1.3.4).

Proves the gate trips on a wrong n/trades_month and passes on the correct identity.
"""
import sys, os
from pathlib import Path
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
import lib.row_specs as RS

def test_gate_passes_on_correct():
    fp = RS.freeze_fingerprint("SOLUSDT", "4h", "W3_NODIP", n=1470, trades_month=52.5, legacy=True)
    print("PASS: correct identity accepted ->", fp)

def test_gate_aborts_on_wrong_n():
    try:
        RS.freeze_fingerprint("SOLUSDT", "4h", "W3_NODIP", n=370, trades_month=52.5, legacy=True)
        raise AssertionError("gate did NOT abort on wrong n")
    except AssertionError as e:
        assert "MISMATCH" in str(e)
        print("PASS: wrong n aborted ->", str(e)[:60])

if __name__ == "__main__":
    test_gate_passes_on_correct()
    test_gate_aborts_on_wrong_n()
    print("\nALL FREEZE-GATE TESTS PASS")
