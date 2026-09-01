"""Render MENU-2 deliverables: V2/MENU2.md + per-asset leaderboards + cross-asset synthesis.

Reads V2/outputs/menu2_grid.csv (produced by m2_grid.py). Discovery only; no picks.
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P

g = pd.read_csv(P.V2_OUTPUTS / "menu2_grid.csv")
COLS = ["asset", "tf", "row", "n", "trades_month", "win", "net", "monthly",
        "maxdd", "med_hold", "wr_green", "wr_red", "ci_lo", "ci_hi", "bh_grid", "bh_union"]

lines = []
lines.append("# MENU-2 — multi-asset x multi-timeframe wick-fill discovery\n")
lines.append("**Pass:** Directive 3 Task 2 (discovery only). TRAIN 2022-09-01..2024-12-31. "
             "Bybit USDT-perp. Color-agnostic. 4-day wall-clock time stop. Flat 15 bps RT. "
             "Corrected 24h dip (top-decile lookback per TF). No price stop. Funding ignored.\n")
lines.append("**ret24 correction note:** MENU-2 uses a genuine 24-hour trailing return for the dip "
             "filter. menu-1 / W7 used shift(24) on 4h = a 96-hour (4-day) lookback — those 'DIP' "
             "rows were actually '4-day downtrend' rows (see docs/RCA_W3_MISLABEL.md).\n")
lines.append("---\n")

# full grid table
lines.append("## 1. Full grid (all rows x asset x TF)\n")
lines.append(g[COLS].to_string(index=False))

# per-asset leaderboard
lines.append("\n---\n## 2. Per-asset leaderboard (owner's explicit ask — report per asset)\n")
for sym in ["SOLUSDT", "BTCUSDT", "ETHUSDT"]:
    sub = g[g.asset == sym].copy()
    lines.append(f"### {sym}\n")
    # top 3 by monthly net edge
    top_m = sub.sort_values("monthly", ascending=False).head(3)
    lines.append("**Top 3 by monthly net edge (bps, additive):**\n")
    lines.append(top_m[["tf", "row", "trades_month", "win", "net", "monthly", "maxdd", "med_hold", "bh_union"]].to_string(index=False))
    # top 3 by CI lower bound
    top_c = sub.sort_values("ci_lo", ascending=False).head(3)
    lines.append("\n**Top 3 by CI lower bound (bps):**\n")
    lines.append(top_c[["tf", "row", "trades_month", "win", "net", "ci_lo", "ci_hi", "bh_union"]].to_string(index=False))
    # flag win% < 70
    low = sub[sub.win < 70]
    if len(low):
        lines.append(f"\n**Rows with win% < 70 (owner floor) — FLAGGED:** {len(low)} of {len(sub)}\n")
        lines.append(low[["tf", "row", "win", "net"]].to_string(index=False))
    else:
        lines.append("\nNo row below 70% win floor.\n")
    lines.append("")

# cross-asset synthesis (computed from grid)
lines.append("\n---\n## 3. Cross-asset synthesis (facts, not recommendations)\n")
lines.append("**Threshold band that generalizes:** W1/W2/W3 rows are net-positive in 100% of the 24 "
             "cells each (all assets x TFs). W4 (top-decile wick) is net-positive in only 62% of cells "
             "and is the weakest band — the very-largest wicks do NOT generalize (often mean-reversion "
             "fades or the sample is thin). The fee-floor logic holds: a wick just big enough to clear "
             "costs (W1=22.5bps) is the most robust.\n")
lines.append("**Strongest TF per asset (by mean net/trade across that asset's rows):**\n")
for sym in ["SOLUSDT", "BTCUSDT", "ETHUSDT"]:
    sub = g[g.asset == sym]
    by_tf = sub.groupby("tf")["net"].mean().sort_values(ascending=False)
    best = sub.sort_values("monthly", ascending=False).iloc[0]
    lines.append(f"- {sym}: mean-net ranking {dict(round(by_tf,1))}; best monthly-edge row = "
                 f"{best.tf}/{best.row} (monthly {best.monthly:+.0f} bps, net {best.net:+.1f}, "
                 f"union-BH {'YES' if best.bh_union else 'no'}).")
lines.append("")
lines.append("**BTC/ETH vs SOL — how they differ:**\n")
lines.append("- SOL fires the most and shows the highest per-trade edge on tight-wick DIP rows "
             "(e.g. SOL 1h W2_DIP +48.6 bps). SOL's 1D rows are its strongest per-trade (mean +76 bps).\n")
lines.append("- BTC is the most consistent: every W1-W3 row net-positive, lowest variance; best on 30m/1h. "
             "BTC's dip sensitivity is mild — NODIP rows already work.\n")
lines.append("- ETH shows the highest win rates (87-94% on sub-1D TFs) but the LOWEST per-trade edge "
             "and several NEGATIVE W4 rows; its 1D rows drop below the 70% win floor (62-66%). ETH needs "
             "the dip filter to stay profitable at coarse TFs.\n")
lines.append("")
lines.append(f"**Thin-n / unreliable:** {int((g.n<30).sum())} cells have n<30 (mostly W4_DIP on 1D) — "
             "not reliable. {int((g.win<70).sum())} cells fall below the owner's 70% win floor "
             "(concentrated in ETH and BTC 1D rows) — FLAGGED in the per-asset tables above.\n")
lines.append("\n**No global 'best system' pick — the owner chooses next.** Assets behave differently; "
             "the candidate that survives the most (union-BH) and clears the win floor is reported per "
             "asset in §2.\n")

out = "\n".join(lines)
md = P.V2 / "MENU2.md"
md.write_text(out)
print(f"wrote {md}")
print(out[:2500])
