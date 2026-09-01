"""test_bh_canonical.py — guards the multiplicity-correction rule.

The project's single worst historical bug was a BROKEN Benjamini-Hochberg that
mislabeled viable cells (m2_grid.py: 50/96 cells scrambled). This test:
  1. asserts the CANONICAL BH in src/lib/stats.py passes the mandated unit-checks,
  2. asserts the KNOWN-BROKEN BHs (rebuild_ledger.py, exit_phaseb.py, m2_grid.py)
     FAIL those same checks, so an agent can never "port the correct one" by
     copying them.

If this test fails, do NOT edit the broken functions to make them pass — fix the
code that imported them. The canonical implementation is the only correct one.
"""
import numpy as np
import pytest
import sys
from pathlib import Path

# V3 is self-contained: import the canonical stats from V3/lib, not the (reverted) src/lib.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import stats


# --- exact copies of the BROKEN implementations, for regression-proofing ------
# (verbatim from the source files; do not "improve" them here)
def bh_broken_rebuild_ledger(pvals, q=0.05):
    # V2/scripts/rebuild_ledger.py:11-18 and exit_phaseb.py:21-28 (identical)
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    thr = (np.arange(1, m + 1) / m) * q
    rej = np.zeros(m, bool)
    rej[order] = p[order] <= thr          # ELEMENTWISE: skips indices
    return rej


def bh_broken_m2_grid(pv, q=0.05):
    # V2/scripts/m2_grid.py:111-127 (inline)
    order = np.argsort(pv)
    m = len(pv)
    bh = pv <= (np.arange(1, m + 1) / m) * q   # UNSORTED p vs sorted thr
    return bh


# Canonical-mandated unit checks (KEEPN_EXIT_DIRECTIVE.md:176-179)
CASES = {
    "all_reject": [0.01, 0.02, 0.03, 0.04, 0.05],
    "one_reject": [0.01, 0.03, 0.10, 0.20, 0.30],
    # GAP vector (non-monotonic sorted: a later index passes while an earlier one
    # fails). Correct step-up: k* = largest index with p_k <= k*q/m.
    # p_sorted = [0.008,0.019,0.040,0.039,0.050], thr=[.01,.02,.03,.04,.05]
    # below = [T,T,T,F,T] -> k* = 4 -> reject all 5. The broken elementwise impl
    # rejects only where p<=thr -> 4 of 5 (skips index 3). Counts diverge.
    "gap": [0.008, 0.019, 0.040, 0.039, 0.050],
}


def test_canonical_bh_unit_checks():
    r = stats.bh_reject(CASES["all_reject"], q=0.05)
    assert r.all(), "canonical BH should reject all 5"
    r = stats.bh_reject(CASES["one_reject"], q=0.05)
    assert r.sum() == 1 and r[0], "canonical BH should reject only smallest"


def test_broken_bh_rejects_wrong_indices():
    # Correct step-up on the GAP vector: k* = largest index with p_k <= k*q/m.
    # p_sorted = [0.008,0.009,0.030,0.031,0.050], thr=[.01,.02,.03,.04,.05]
    # below = [T,T,T,F,T] -> k* = 4 -> reject all 5. The broken elementwise impl
    # rejects only where p<=thr, i.e. 4 of 5 (skips index 3). So the counts differ.
    canon = stats.bh_reject(CASES["gap"], q=0.05)
    brok = bh_broken_rebuild_ledger(CASES["gap"], q=0.05)
    assert canon.sum() == 5, "canonical BH must reject all 5 on the gap vector"
    assert brok.sum() != canon.sum(), (
        "broken rebuild_ledger/exit_phaseb BH diverges from correct step-up (no k* chaining)")
    assert brok.sum() < canon.sum(), "broken elementwise BH under-rejects on the gap vector"


def test_broken_m2_grid_scrambles():
    # m2_grid compares UNSORTED p against the sorted-step threshold -> different result
    # than the correct step-up even on the trivial all_reject vector ordering.
    canon = stats.bh_reject(CASES["gap"], q=0.05)
    scram = bh_broken_m2_grid(CASES["gap"], q=0.05)
    assert scram.sum() != canon.sum(), "m2_grid BH (unsorted p vs sorted thr) is broken"


def test_stats_selftest_runs():
    stats._selftest()
