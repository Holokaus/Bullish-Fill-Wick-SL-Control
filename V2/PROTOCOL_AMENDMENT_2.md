# OPERATION FILLPOINT — PROTOCOL AMENDMENT 2 (2026-08-27)

**Supersedes:** original `PROTOCOL.md` §3 Windows and any "Jan 2025 – Jun 2026" validation
reference. Binding addendum §13 of the agent directive governs where this conflicts.

## 1. Rebuilt windows (frozen)

| Window | Range (UTC) | Purpose | Use |
|---|---|---|---|
| TRAIN | 2022-09-01 → 2024-12-31 | Discovery, threshold tuning, atlas cuts, system selection | Full use |
| E-VAL (internal) | 2025-01-01 → 2025-06-30 | One-shot walk-forward validation | ONE shot, post-freeze |
| **RESERVED — down market** | **2025-07-01 → 2026-06-30** | Future user-directed stress test | **DO NOT TOUCH (§1.1)** |
| LOCKBOX | 2026-07-01 → 2026-08-26 | Final one-shot confirmation | ONE shot, post E-VAL pass |

## 2. Down-market holdout exclusion (owner rationale)

The owner reserves a 12-month down-market window for a **future, user-directed** validation.
This removes the Jul 2025 – Jun 2026 portion of the original protocol's VALIDATION window.
Consequence: E-VAL is shortened to the 6 months **immediately before** the reserved window
(Jan–Jun 2025). The reserved window must not be used for descriptives, tuning, plotting,
sanity checks, or any analysis — see `src/lib/time_gates.py` `filter_window` which fails
closed on any leakage.

## 3. Cost stack (locked, Bybit USDT-perp VIP0)

- Maker 2.0 bps/side, Taker 5.5 bps/side. Slippage 4.0 bps RT on any taker leg.
- Effective RT cost is **declared per entry/exit mechanics** in `FROZEN_CANDIDATE.md`:
  - PB(maker) entry + PB(maker) exit  → 4.0 bps  (queue optimism disclosed)
  - PB(maker) entry + MKT(taker) exit → 11.5 bps (declared headline)
  - MKT(taker) entry + MKT(taker) exit → 15.0 bps (honest floor)
- Track 1's flat 11 bps Binance-spot stack is **retired** with Track 1 (§13.1).

## 4. Status

TRAIN-only work complete through `W7` (corrected-cost flagship study + global FDR).
Candidate frozen (see `results/FROZEN_CANDIDATE.md`). E-VAL and E-LOCKBOX **not yet fired**
— deferred to subsequent passes per §13.4.
