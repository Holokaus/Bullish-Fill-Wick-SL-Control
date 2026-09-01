"""Window constants and holdout-exclusion gates for OPERATION FILLPOINT.

Per directive §2 / §13.2 (binding):
  TRAIN       2022-09-01 -> 2024-12-31   (discovery, atlas cuts, selection)
  E-VAL       2025-01-01 -> 2025-06-30   (one-shot internal validation)
  RESERVED    2025-07-01 -> 2026-06-30   (DO NOT TOUCH — user down-market stress)
  LOCKBOX     2026-07-01 -> 2026-08-26   (one-shot lockbox confirmation)

Every loader MUST drop the RESERVED window before any analysis. `filter_window`
asserts the exclusion so a script fails closed rather than silently leaking it.
"""
from pathlib import Path
import pandas as pd

# ms epochs (UTC)
TRAIN_START      = pd.Timestamp("2022-09-01", tz="UTC").value // 10**6
TRAIN_END        = pd.Timestamp("2024-12-31 23:59:59", tz="UTC").value // 10**6
EVAL_START       = pd.Timestamp("2025-01-01", tz="UTC").value // 10**6
EVAL_END         = pd.Timestamp("2025-06-30 23:59:59", tz="UTC").value // 10**6
HOLDOUT_START    = pd.Timestamp("2025-07-01", tz="UTC").value // 10**6
HOLDOUT_END      = pd.Timestamp("2026-07-01", tz="UTC").value // 10**6   # exclusive bound [start, end)
LOCKBOX_START    = pd.Timestamp("2026-07-01", tz="UTC").value // 10**6
LOCKBOX_END      = pd.Timestamp("2026-08-26 23:59:59", tz="UTC").value // 10**6

WINDOWS = {
    "TRAIN":   (TRAIN_START, TRAIN_END),
    "EVAL":    (EVAL_START,  EVAL_END),
    "LOCKBOX": (LOCKBOX_START, LOCKBOX_END),
}

# acceptance check constants
FEE_MAKER_SIDE = 0.0002     # 2.0 bps per side
FEE_TAKER_SIDE = 0.00055    # 5.5 bps per side
SLIP_RT_TAKER  = 0.0004     # 4.0 bps ROUND-TRIP, applied once per trade that uses a taker leg

# effective RT cost configs (directive §13.3). Slip added once if any taker leg.
RT_PB_PB   = FEE_MAKER_SIDE + FEE_MAKER_SIDE                          # 4.0 bps  (no taker)
RT_PB_MKT  = FEE_MAKER_SIDE + FEE_TAKER_SIDE + SLIP_RT_TAKER          # 11.5 bps
RT_MKT_MKT = FEE_TAKER_SIDE + FEE_TAKER_SIDE + SLIP_RT_TAKER          # 15.0 bps
RT_CONFIGS = {"PB_PB": RT_PB_PB, "PB_MKT": RT_PB_MKT, "MKT_MKT": RT_MKT_MKT}


def in_holdout(ts_ms):
    """True if a (Series/array of) epoch-ms falls in the reserved down-market window."""
    return (ts_ms >= HOLDOUT_START) & (ts_ms < HOLDOUT_END)


def filter_window(df, which, time_col="time"):
    """Return df restricted to the named window, AFTER asserting no holdout leakage.

    `which` in {TRAIN, EVAL, LOCKBOX}. The reserved window is always excluded first
    (rows in [HOLDOUT_START, HOLDOUT_END) are dropped). We then assert that NO row
    in the *output* lands in the reserved window — i.e. filtering must have removed it.
    Fails closed only if a holdout row survives the drop (a real leak), not merely if
    the raw input happened to contain holdout rows (which is normal and expected).
    """
    if time_col not in df.columns:
        for alt in ("ts", "timestamp", "open_time"):
            if alt in df.columns:
                time_col = alt
                break
    t = df[time_col].astype("int64")
    # drop the reserved window first
    kept = ~in_holdout(t)
    df = df[kept].copy()
    t2 = df[time_col].astype("int64")
    assert not in_holdout(t2).any(), "HOLDOUT LEAK: reserved window survived filtering — abort."
    lo, hi = WINDOWS[which]
    return df[(t2 >= lo) & (t2 <= hi)].copy()


def assert_no_holdout(df, time_col="time"):
    t = df[time_col].astype("int64")
    assert not in_holdout(t).any(), "HOLDOUT LEAK detected — abort."
    return df
