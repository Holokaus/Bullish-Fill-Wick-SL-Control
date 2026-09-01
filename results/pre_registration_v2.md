# OPERATION FILLPOINT — Pre-registration Record (V2, re-affirmed 2026-08-27)

**Purpose:** Record the frozen conditioning cuts and the integrity hash so E-VAL / E-LOCKBOX
are reproducible and tamper-evident (directive §2 action 3, §7.1, §8.5).

## Atlas cuts

- **File:** `V2/outputs/atlas/atlas_cuts.json`
- **Frozen on:** TRAIN window only (2022-09-01 → 2024-12-31). Re-affirmed against the
  rebuilt windows in `PROTOCOL_AMENDMENT_2.md`; the TRAIN definition is unchanged from the
  original V2 protocol, so the existing cuts remain valid (no drift expected).
- **SHA-256:** `180aa0c9d0f5c07ec6c0468aaae913b97564183ad40983049e4f034229083cda`
- **Contents:** per series `uw_tercile`, `uw_deciles` (10), `ret24_q` (4), `vr_q` (4),
  `rx_q` (4), `train_last`. Computed from the bullish-candle population of each series.
- **Reproduce:** `V2/scripts/w4a_atlas.py` (writes the parquet event tables + this json).
  Outputs also gated by `src/lib/time_gates.filter_window(..., "TRAIN")` which asserts the
  reserved down-market window (2025-07-01 → 2026-06-30) is excluded.

## Holdout-exclusion gate

Every loader now routes through `src/lib/time_gates.filter_window`, which:
1. drops any row in `[2025-07-01, 2026-07-01)` (the reserved window),
2. asserts no reserved row survives the drop,
3. then clips to the requested window (TRAIN / E-VAL / LOCKBOX).

The reserved window is **never** analyzed, summarized, or peeked at (directive §1.1).

## Frozen candidate hash anchor

The candidate spec frozen in `results/FROZEN_CANDIDATE.md` references this cuts hash and the
`V2/outputs/w7_sol4h_corrected.csv` / `w7_fdr_family.csv` study artifacts. Any parameter change
after freeze invalidates E-VAL (directive §7.1).
