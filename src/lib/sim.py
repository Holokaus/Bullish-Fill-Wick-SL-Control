"""Minimal, tested forward simulator for the upper-wick-fill strategy.

Replay semantics (matches V2/scripts/w7_flagship_study.py::replay):
  - entry at bar `eb` (0-based index into the price arrays)
  - target `tp` (price); exit on first touch of TP within TMAX bars
  - K=0  => NOSL: if TP never touched, exit at horizon close (bar TMAX-1)
  - K>0  => TIME stop: if TP not touched by bar K, exit at close of bar K
  - returns gross pnl in bps vs entry price `bt`

This module is the single source of simulator truth; tests cover it (directive s8.3).
"""
import numpy as np

TMAX = 48

def replay(O, Hh, L, C, sidx, eb, bt, tp, K=0, window=TMAX):
    """Vectorised forward replay.

    Arrays O,Hh,L,C are full series (float). sidx = signal bar indices, eb = entry bar
    indices (eb>=0 valid). bt,tp = entry/target prices per event. K per directive.
    `window` = forward lookback length (must be >= K+1 so the time-stop is reachable).
    Returns (pnl_bps, filled_bool).
    """
    E = len(sidx)
    win = max(window, K + 1) if K > 0 else max(window, 1)
    starts = np.where(eb >= 0, eb, 0)
    idx = np.clip(starts[:, None] + np.arange(win)[None, :], 0, len(L) - 1)
    fhi = Hh[idx]
    fcl = C[idx]
    tp_hit = fhi >= tp[:, None]
    tp_idx = np.where(tp_hit.any(1), tp_hit.argmax(1), win)
    filled = tp_idx < win
    if K > 0:
        exit_idx = np.minimum(tp_idx, K)
        hit_at_exit = fhi[np.arange(E), np.clip(exit_idx, 0, win - 1)] >= tp
        pnl = np.where(hit_at_exit,
                       (tp - bt) / bt * 1e4,
                       (fcl[np.arange(E), np.clip(exit_idx, 0, win - 1)] - bt) / bt * 1e4)
    else:
        pnl = np.where(filled,
                       (tp - bt) / bt * 1e4,
                       (fcl[:, -1] - bt) / bt * 1e4)
    return pnl, filled
