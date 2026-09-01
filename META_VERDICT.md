# META_VERDICT — Bullish-Fill-Wick (single source of truth)

**Date:** 2026-08-27 · **Pipeline:** Track 2 / V2 / OPERATION FILLPOINT (Bybit USDT-perp)
**Status:** Consolidation complete through candidate freeze. E-VAL / E-LOCKBOX deferred
(directive §13.4). Track 1 retired as a research artifact (preserved, not deleted).

---

## 1. One-line verdict

> **The upper-wick-fill is a real, measured, BH-controlled informational feature (+2 to +13pp
> ΔP on intraday, range-matched, replicated across assets). A single no-price-stop / time-stop
> candidate (SOL-4h, C6_w9dip, f=1.5, MKT entry) is significantly above the cost line on TRAIN
> at every declared fee config (4 / 11.5 / 15 bps) and survives global FDR. Standalone tradability
> pending the one-shot E-VAL (2025-H1) and E-LOCKBOX (2026-07/08) gates, which are NOT yet fired.**

## 2. Reconciliation of prior "final" outputs

### Track 2 / V2 outputs
| Artifact | What remains valid | What is retired / corrected |
|---|---|---|
| `V2/ATLAS_ANSWERS.md` | The measured facts: 88–93% fill within 48 bars, median time-to-fill 2 bars, volume monotonic effect (13/13), wick sweet-spot deciles 7–8, prior-bearish +3pp, below-SMA +3pp. All BH-controlled. | Its "conversion fails on arithmetic" conclusion used the **old SL grid** and under-specified fees; superseded by W5/W6/W7 with the locked cost stack. |
| `V2/W5_NOSL_REPORT.md` | Method (no-SL replay) and the directional finding that removing the stop surfaces the edge. | **Fee under-count:** it subtracted only 4 bps (maker) for every cell, including taker entries. Corrected fees (W7) show only NOSL cells survive, dominated by SOL-4h. The "118 significant cells" figure is the PB_PB best-case, not the honest floor. |
| `V2/W6_STOPLOSS_REPORT.md` | The mechanism: price stops (ABS/ATR/QMAE) are structurally adversarial to this concept (0/3420 cells). | **Fee under-count** again: "10 time-stop cells above cost" were at fake 4 bps. At correct fees even time-stops die on SOL-4h unless K is large; the honest recipe is no-price-stop + time-cap, which W7 confirms. |
| `V2/EXECUTION_CHANGELOG.md` | Audit trail of W0–W6. Valid as history. | — |

### Track 1 outputs (RETIRED per §13.1 — preserved for audit, not candidates)
| Artifact | Retirement reason (verbatim from §13.1) |
|---|---|
| `reports/FINAL_REPORT.md` (Aug 24) | "ΔP table, decomposition, and per-year stationarity remain valid reference facts. The 'commercially insufficient' verdict is retired because the no-SL configuration (W5) and the time-stop configuration (W6) were not tested in this report's cost layer." |
| `reports/FINAL_SYSTEM_REPORT.md` (Aug 25) | "+325% combined return is post-selection on a 1768-cell scan without global FDR correction at the selection layer. Summed, non-compounded equity. Sharpe formula `np.mean/std * sqrt(252*24)` is incorrect for sparse trade counts. Retired; not a candidate." |
| `docs/SYSTEM_SIGNED.md` (Aug 25) | "Signature issued before E-VAL and E-LOCKBOX fired. Both gates remain unfired. Superseded." → replaced with SUPERSEDED notice. |
| `src/final_system.py` / `results/FINAL_SYSTEM.json` / `results/system_v2.json` | "Code artifact of retired reports. Retained for audit; do not execute as the candidate pipeline." |

## 3. The single recommended candidate (frozen)

See `results/FROZEN_CANDIDATE.md` for the full spec. Summary:

- **SOLUSDT-4h, condition C6_w9dip** (wick top-decile + counter-trend dip), **MKT entry**,
  **TP = body_top + 1.5×wick_gap**, **no price stop**, **time stop K=24** (≈4-day cap),
  circuit breaker on BTC −20%/15% adverse.
- **TRAIN:** n=195, win 88.7%, **net +95.7 bps/trade** (11.5 bps cost), CI [+42.4,+142.7],
  CAGR +114%, MaxDD 41.4%, Sharpe 2.28, Sortino 0.88, Calmar 2.76.
- Survives at **all three** declared fee configs (4 / 11.5 / 15 bps) and **global BH-FDR**
  (36/144 family cells significant; candidate inside the set).

### Retired candidates (with one-sentence reason)
- **Track 1 R1 (SOL 1h 1.75–2.5%, no-SL):** retired with all of Track 1 (§13.1) — its Binance-spot
  11 bps stack and summed-equity Sharpe are superseded; the Track-2-equivalent is the SOL-4h cell above.
- **Track 1 R2 (SOL 1d ≥2.5% small-body, no-SL):** retired — MaxDD 48.8% on summed equity;
  daily no-SL tail risk incompatible with prudent risk budget; a daily time-stop = 24-day exposure.
- **Track 1 R3 (SOL 4h ≥2.5%, no-SL):** retired with Track 1; the Track-2 SOL-4h cell above replaces
  it with the corrected Bybit cost stack and FDR control.
- **W6 "time-stop preserves edge" claim:** retired as stated — it was a fee artifact; corrected
  finding is "no-price-stop + time-cap survives; tight time-stops still underperform NOSL on SOL-4h."

## 4. Statistical integrity status

- **Global FDR (§4.1):** applied to the 144-cell SOL-4h selection family → 36 significant, candidate
  inside set. Family size documented in `FROZEN_CANDIDATE.md`. ✅
- **Sharpe (§4.2):** replaced `sqrt(252*24)` fiction with calendar-aligned daily-return Sharpe
  (2.28), Sortino (0.88), Calmar (2.76) on the compounded TRAIN series. ✅
- **Overlap dedup (§4.3):** N/A to the single-asset flagship (no multi-rule portfolio in the
  candidate). The Track-1 "902-trade combined" is retired (post-selection, no dedup). ✅ (not applicable)
- **Walk-forward (§4.4):** atlas cuts frozen on TRAIN; E-VAL/E-LOCKBOX windows per §13.2. ✅

## 5. What is deferred (explicitly out of this pass, §13.4)

- E-VAL (2025-H1) and E-LOCKBOX (2026-07/08) — one shot each, post sign-off.
- Section 6 alpha extension: LightGBM, exhaustion/blowoff filter, alt-coin diversification,
  funding-aware 4h (funding ingestion). Funding is the key open risk for the 4h candidate.
- Reserved down-market window (2025-07-01 → 2026-06-30): never touched.

## 6. Honest bottom line

The concept is correct and the chosen candidate is significantly above cost on TRAIN under the
locked, honestly-counted fee stack, with multiplicity controlled. The remaining questions are
**validation** (E-VAL/E-LOCKBOX) and **funding on the 4h hold** — both are scheduled, not blockers.
No claim of "tradeable" is made until both one-shot gates fire.
