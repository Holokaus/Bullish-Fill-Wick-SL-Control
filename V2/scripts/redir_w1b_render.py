"""REDIR-W1b: render the 8-row menu CSV into a clean markdown deliverable."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P
import pandas as pd

out = pd.read_csv(P.V2_OUTPUTS / "redir_w1_menu.csv")
md = ["# REDIR-W1 - 8-ROW COLOR-AGNOSTIC WICK-FILL MENU",
      "",
      "TRAIN 2022-09-01 to 2024-12-31 - SOL-4h - Bybit USDT-perp - headline cost = MKT_MKT 15 bps RT.",
      "Signal = ANY candle (green OR red) whose upper-wick meets the row threshold. Entry MKT next-bar-open.",
      "TP = body_top + 1.5 x wick_gap. Time stop K=24 bars. No price stop, no circuit breaker at menu stage.",
      "Wick thresholds: W1 >=22.5bps (1.5xRT) - W2 >=45bps (3xRT) - W3 >=90bps (6xRT) - W4 = top wick decile (TRAIN-frozen).",
      "Dip = ON means 24h-return bottom quintile (agent comparison row only).",
      "",
      "| Row | n | trades/mo | win% | net bps/tr | monthly bps | maxDD(2%/tr) | win% green | win% red | BH sig? | CI lo | CI hi |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|"]
for _, r in out.iterrows():
    md.append("| %s | %s | %s | %.1f | %.2f | %.0f | %.1f%% | %.1f | %.1f | %s | %s | %s |" % (
        r.row, int(r.n), r.trades_month, r.win*100, r.net, r.monthly, r.maxdd*100,
        r.wr_green*100, r.wr_red*100, r.bh, r.ci_lo, r.ci_hi))
md += ["",
      "**BH-FDR (q=0.05) across the 8 menu cells:** 4 significant -> W1_DIP, W2_DIP, W3_BASE, W3_DIP.",
      "",
      "**Reading for the owner (plain):** every row clears the 70% win-rate guideline (79-84%).",
      "BASE rows (no dip) trade far more often (36-141/mo) but earn less per trade; DIP rows trade less",
      "(7-36/mo) but earn more per trade. W1_BASE is the owner's literal concept (max entries, fee-floor wick)",
      "and is profitable but its CI includes 0 at 15bps - the tighter, dip-filtered rows are the cleaner statistically.",
      "",
      "**Next step (per directive s4):** owner picks ONE row. Then s3 items (3-config cost sensitivity, union-family",
      "BH, matched-control dP, 4h funding adjustment) run on that row only, and results/FROZEN_CANDIDATE.md v2 is written.",
      "E-VAL / E-LOCKBOX remain unfired. Reserved down-market window untouched."]
open(str(P.V2 / "MENU_8ROW.md"), "w").write("\n".join(md))
print("wrote", P.V2 / "MENU_8ROW.md")
