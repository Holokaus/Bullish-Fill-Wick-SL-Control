"""Render V2/SL_STUDY.md (Directive 4 Task 3/4): derivations, eval table, frontier, verdicts, union."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, ".")
OUT = Path("V2/outputs")
sl = pd.read_csv(OUT/"sl_study.csv")
deriv = open(OUT/"sl_deriv.txt").read()

L = []
L.append("# SL STUDY — Exit Study I (Directive 4)\n")
L.append("**Rows (fixed, from MENU-2 leaderboards):** E1 SOL-30m W2_NODIP · E2 BTC-30m W1_NODIP · E3 ETH-1h W2_NODIP · E4 SOL-4h W3_NODIP.\n")
L.append("**Baseline** = current spec (TP body_top+1.5·wick_gap, or 4-day time stop, no SL). TRAIN, 15 bps flat, 2% stake.\n")
L.append("**Governing principle honored:** every exit parameter below is DERIVED from a Phase A measurement (docs/EXIT_ANATOMY.md) and cited. No scanned/assumed numbers.\n")
L.append("\n## 1. Parameter derivation sheet (each number cites its measurement)\n")
for line in deriv.strip().split("\n"):
    if line.startswith("# "):
        L.append(f"\n### {line[2:]}\n" if "derivation" in line or "Viability" in line else "")
    elif line.startswith("#"):
        continue
    else:
        L.append(f"- {line}")
L.append("")

# dropped families
L.append("\n## 2. Dropped families (evidence, not silence)\n")
L.append("- **P2 thesis-falsification (close above wick high):** Phase A §4 shows P(TP|close-above-wickhigh) = 96.5/96.6/95.8/85.7% vs P(TP|no-flag) = 89.7/90.2/84.9/76.7%. A close above the wick high is *bullish confirmation*, not falsification → exiting there **cuts winners**. Fails inclusion rule (P(TP|flag) < 0.5×P(TP|no-flag)). **DROPPED.**")
L.append("- **P3 downside-falsification (close below wick low):** directionally correct (82/82/73/54% vs 100/100/99/98%) but fails the strict rule P(TP|flag) < 0.5×P(TP|no-flag) (e.g. 82.3 vs 49.9). **DROPPED** (directional evidence retained).")
L.append("- **P6 combo:** = best falsification stop (none survived) + P4 → **reduces to P4**.")
L.append("- **P4_hazard variant:** Phase A hazard curve has **no knee** within 96h (survival still >0.95 at max-hazard) → no falsification collapse point. Variant **UNDEFINED → dropped**; P4 evaluated at P90/P95 of winners' time-to-fill only.")
L.append("")

# eval table
L.append("\n## 3. Evaluation table (per policy × row)\n")
cols = ["row","policy","n","win","net","monthly","maxdd","med_hold","worst","retention","pval","bh_union"]
L.append("| "+" | ".join(cols)+" |")
L.append("|"+"---|"*len(cols))
for _, r in sl.iterrows():
    L.append("| "+" | ".join(str(r[c]) for c in cols)+" |")
L.append("")
L.append("*net = bps/trade; monthly = additive 2% stake; maxdd = 2% stake overlapping; med_hold = hours; retention = net vs baseline; bh_union = survives union BH q=0.05.*\n")

# viability verdicts
L.append("\n## 4. Viability verdicts (pre-declared: retention ≥ 80% AND maxDD ≤ 75% of baseline AND worst trade improved)\n")
for line in deriv.strip().split("\n"):
    if "VIABLE=" in line:
        L.append(f"- {line}")
L.append("")
L.append("**Result: NOTHING is viable.** Every candidate fails at least one prong:")
L.append("- **P1 static wick-unit SL:** re-confirmed dead at *derived* levels. P95 retention 13–37% (even P99 only 27–65%). This is the honest re-test of W6 — the winners' MAE P95 (6.8–11.6 wick units) is so wide that any SL tight enough to catch losers also stops winners. Composite finding: **static SL re-confirmed dead at derived levels.**")
L.append("- **P4 short-K time SL:** retains edge (P95 retention 58–120%) and improves worst trade, but **maxDD does NOT drop ≥25%** (shorter horizon barely changes DD) → fails prong 2 on every row.")
L.append("- **P5 activation/breakeven:** retains edge (retention 77–102%) but **maxDD does NOT drop ≥25%** → fails prong 2 on every row (E2/E3 tie at baseline DD, E1/E4 higher).")
L.append("")

# frontier
L.append("\n## 5. Frontier (owner picks the P&L-vs-WR point)\n")
L.append("For each row, the frontier is the set of policies that *improve* on baseline on at least one metric without being declared non-viable. Since none is viable, the frontier is informational only — these are the points where edge is retained but DD is not yet reduced:\n")
for tag in ["E1","E2","E3","E4"]:
    sub = sl[(sl.row==tag) & (sl.policy!="BASELINE_noSL")]
    best = sub.sort_values("retention", ascending=False).head(2)
    names = ", ".join(f"{r.policy} (ret {r.retention}%, net {r.net}, maxDD {r.maxdd}%)" for _,r in best.iterrows())
    L.append(f"- **{tag}**: {names}")
L.append("")
L.append("Owner's stated preference is the P&L-vs-WR tradeoff; the above are the candidate points. **No policy is recommended for promotion** — see §6.\n")

# multiplicity
L.append("\n## 6. Multiplicity & union ledger\n")
L.append("- BH q=0.05 across the 28 SL cells (baselines excluded): 14 significant (within-family).")
L.append("- Union ledger (rebuild_ledger.py): **282 cells** = W7 144 + menu-1 8 + candidates 2 + MENU-2 96 + SL 32. **105 BH-significant** at q=0.05. **18/32 SL cells survive the union** (mostly P4/P5 variants + baselines).")
L.append("- Same-bar ambiguity: Phase A uses optimistic (TP-first). For P1/P5 the static-SL and breakeven exits are mostly pessimistic-dominated (SL fired before TP in the same bar when both touched) — pessimistic bounds are tighter than reported; this only strengthens the 'static SL kills edge' conclusion. Flagged, not resolved (granularity limit).")
L.append("")

# trade date proof
L.append("\n## 7. Trade-entry-date proof (reserved window dark)\n")
L.append("All four entry rows' trades enter before 2025-01-01 (TRAIN). Max entry dates: E1 2024-12-31 10:00, E2 2024-12-31 19:30, E3 2024-12-31 15:00, E4 2024-12-30 04:00 UTC. Reserved window 2025-07-01→2026-06-30 untouched; no validation fired; time_gates.py unmodified.\n")

# stop
L.append("\n## 8. Definition of done / stop\n")
L.append("- [x] Phase A delivered first (EXIT_ANATOMY.md + exit_anatomy_*.csv + charts).")
L.append("- [x] sl_study.csv + SL_STUDY.md with cited derivations, eval table, frontier, verdicts.")
L.append("- [x] Multiplicity (BH within SL + union ledger).")
L.append("- [x] Trade-entry-date proof.")
L.append("- **Agent stops. Owner picks from the frontier (or orders Exit Study II: TP optimization, using Phase A MFE data).**")
L.append("")

Path("V2/SL_STUDY.md").write_text("\n".join(L))
print("wrote V2/SL_STUDY.md")
