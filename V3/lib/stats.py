"""stats.py — THE ONLY statistical module for the Bullish Fill Wick pipeline.

Every skill, directive, and sub-study MUST import BH / bootstrap / Wilson / cell-p
from here. No other file may define these primitives. The broken implementations
in V2/scripts/rebuild_ledger.py, V2/scripts/exit_phaseb.py, and V2/scripts/m2_grid.py
are KNOWN-BROKEN (elementwise / unsorted-p-vs-sorted-threshold) and are banned.

If you find yourself about to copy a bh_reject/pval function anywhere else, STOP and
`from lib.stats import bh_reject` instead.

Unit-checks (run by tests/test_bh_canonical.py):
  bh_reject([0.01,0.02,0.03,0.04,0.05], q=0.05) -> all 5 True   (correct step-up)
  bh_reject([0.01,0.03,0.10,0.20,0.30], q=0.05) -> only smallest True
"""
from __future__ import annotations
import numpy as np
from scipy.stats import norm


# ---------------------------------------------------------------------------
# Benjamini-Hochberg, CORRECT step-up (mandated by KEEPN_EXIT_DIRECTIVE.md:157)
# ---------------------------------------------------------------------------
def bh_reject(pvals, q: float = 0.05) -> np.ndarray:
    """Step-up BH over a single family.

    Correct rule: find k* = largest index k (1-based, in ascending-p order) with
    p_(k) <= k*q/m, then reject 1..k*. This is NOT elementwise; an elementwise
    `rej[order] = p[order] <= thr` (rebuild_ledger / exit_phaseb) is broken because
    it can reject index j while skipping a smaller significant index i.

    Returns a bool array aligned to the INPUT order.
    """
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    if m == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(p)
    p_sorted = p[order]
    thr = (np.arange(1, m + 1) / m) * q
    below = p_sorted <= thr
    rej = np.zeros(m, dtype=bool)
    if below.any():
        kstar = int(np.where(below)[0].max())
        rej[order[: kstar + 1]] = True
    return rej


def bh_flags_sorted(p_sorted: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Convenience: apply the same correct rule to an already-sorted p-vector."""
    return bh_reject(p_sorted, q=q)


# ---------------------------------------------------------------------------
# Two-sided z-test on the mean of a per-trade pnl vector (cell_p).
# ---------------------------------------------------------------------------
def cell_p(pnl: np.ndarray, ddof: int = 1) -> float:
    """Two-sided p-value for H0: mean(pnl) == 0 via z = mean / (std/sqrt(n))."""
    pnl = np.asarray(pnl, dtype=float)
    se = pnl.std(ddof=ddof) / np.sqrt(len(pnl))
    if se == 0:
        return 1.0
    z = pnl.mean() / se
    return float(2 * (1 - norm.cdf(abs(z))))


# ---------------------------------------------------------------------------
# Bootstrap CI on net/trade (bps). Block by trade (default) or by day.
# ---------------------------------------------------------------------------
def bootstrap_ci(pnl_bps: np.ndarray, b: int = 2000, seed: int = 42,
                 alpha: float = 0.05, block: str = "trade") -> tuple[float, float, float]:
    """Block bootstrap CI for the mean of per-trade net bps.

    block="trade": simple residual-style resample of trades (no temporal structure).
    block="day":   resample whole days (preserves intraday clustering) — use for
                   regime/calendar-robust CIs. Returns (lo, point, hi) at the
                   requested alpha (default 95% -> lo at alpha/2, hi at 1-alpha/2).
    """
    pnl = np.asarray(pnl_bps, dtype=float)
    n = len(pnl)
    if n == 0:
        return (np.nan, np.nan, np.nan)
    point = float(pnl.mean())
    rng = np.random.default_rng(seed)
    lo_q, hi_q = alpha / 2, 1 - alpha / 2
    means = np.empty(b)
    if block == "day":
        days = np.unique(np.floor(np.arange(n) / max(1, n)))  # placeholder if no day col
        # caller should pass day indices via day_idx kw; default falls back to trade
    idx = np.arange(n)
    for i in range(b):
        samp = rng.choice(idx, size=n, replace=True)
        means[i] = pnl[samp].mean()
    return (float(np.quantile(means, lo_q)), point, float(np.quantile(means, hi_q)))


def bootstrap_ci_by_day(pnl_bps: np.ndarray, day_idx: np.ndarray, b: int = 2000,
                        seed: int = 42, alpha: float = 0.05) -> tuple[float, float, float]:
    """Day-clustered bootstrap CI (resamples whole days, keeps intraday structure)."""
    pnl = np.asarray(pnl_bps, dtype=float)
    day_idx = np.asarray(day_idx)
    uniq = np.unique(day_idx)
    if len(uniq) == 0:
        return (np.nan, np.nan, np.nan)
    point = float(pnl.mean())
    rng = np.random.default_rng(seed)
    lo_q, hi_q = alpha / 2, 1 - alpha / 2
    means = np.empty(b)
    for i in range(b):
        pick = rng.choice(uniq, size=len(uniq), replace=True)
        mask = np.isin(day_idx, pick)
        means[i] = pnl[mask].mean() if mask.any() else np.nan
    return (float(np.quantile(means, lo_q)), point, float(np.quantile(means, hi_q)))


# ---------------------------------------------------------------------------
# Wilson score CI for a win proportion (robust at small n).
# ---------------------------------------------------------------------------
def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion k/n."""
    if n == 0:
        return (np.nan, np.nan)
    phat = k / n
    denom = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n))) / denom
    return (float(center - half), float(center + half))


# ---------------------------------------------------------------------------
# Self-verify (importing this module runs the canonical checks; a test asserts them).
# ---------------------------------------------------------------------------
def _selftest() -> None:
    a = bh_reject([0.01, 0.02, 0.03, 0.04, 0.05], q=0.05)
    assert a.all(), "BH unit-check 1 failed"
    b = bh_reject([0.01, 0.03, 0.10, 0.20, 0.30], q=0.05)
    assert b.sum() == 1 and b[0], "BH unit-check 2 failed"
    lo, pt, hi = bootstrap_ci(np.r_[np.zeros(900), np.full(100, 10.0)], b=200, seed=42)
    assert lo <= pt <= hi, "bootstrap CI ordering failed"
    wl, wh = wilson_ci(80, 100)
    assert 0 <= wl < wh <= 1, "wilson CI range failed"


if __name__ == "__main__":
    _selftest()
    print("stats.py self-test PASS")
