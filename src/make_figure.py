"""Final figure: (top) measured informational edge per timeframe with bootstrap CIs;
(bottom) cumulative net PnL of the mechanical rule — the honest tradeability picture."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
s = json.load(open(os.path.join(RES, "summary_core.json")))
curves = json.load(open(os.path.join(RES, "curves.json")))

tfs = ["1d", "4h", "1h", "30m", "15m"]
fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), height_ratios=[1, 1.15])

# ---- panel 1: delta with CI, BTC ----
ax = axes[0, 0]
for i, tf in enumerate(tfs):
    v = s[f"btcusdt_{tf}"]
    lo, hi = v["delta_boot_lo"], v["delta_boot_hi"]
    c = "#2a9d8f" if v["sig_delta"] else "#b0b0b0"
    ax.errorbar(i, v["delta"], yerr=[[v["delta"] - lo], [hi - v["delta"]]],
                fmt="o", color=c, capsize=4, markersize=7)
ax.axhline(0, color="k", lw=0.8, ls="--")
ax.set_xticks(range(5), tfs); ax.set_ylabel("ΔP = P(win|event) − P(control)")
ax.set_title("BTC: informational edge (day-cluster bootstrap 95% CI)", fontsize=11)
ax.grid(alpha=0.3)

# ---- panel 2: delta ETH ----
ax = axes[0, 1]
for i, tf in enumerate(tfs):
    v = s[f"ethusdt_{tf}"]
    lo, hi = v["delta_boot_lo"], v["delta_boot_hi"]
    c = "#2a9d8f" if v["sig_delta"] else "#b0b0b0"
    ax.errorbar(i, v["delta"], yerr=[[v["delta"] - lo], [hi - v["delta"]]],
                fmt="o", color=c, capsize=4, markersize=7)
ax.axhline(0, color="k", lw=0.8, ls="--")
ax.set_xticks(range(5), tfs); ax.set_title("ETH: informational edge", fontsize=11)
ax.grid(alpha=0.3)

# ---- panels 3/4: cumulative NET pnl (fut maker/taker stack) ----
for j, (sym, cell) in enumerate([("btcusdt", axes[1, 0]), ("ethusdt", axes[1, 1])]):
    ax = cell
    for name, lbl, c in [("all", "ALL events", "#e76f51"), ("bull", "bullish only", "#457b9d")]:
        cv = curves[f"{sym}_1h_{name}"]
        ax.plot(range(len(cv["cum_net_futmm_pct"])), cv["cum_net_futmm_pct"], label=f"1h {lbl}", color=c)
        cv5 = curves[f"{sym}_15m_{name}"]
        ax.plot(range(len(cv5["cum_net_futmm_pct"])), cv5["cum_net_futmm_pct"],
                label=f"15m {lbl}", color=c, ls="--", alpha=0.65)
    ax.axhline(0, color="k", lw=0.8)
    ax.set_title(f"{sym.upper()}: cumulative NET PnL (futures maker-in/taker-out, slippage)", fontsize=11)
    ax.set_xlabel("trade #"); ax.set_ylabel("sum of per-trade returns (%)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

fig.suptitle("Upper-Wick Continuation Study — BTC/ETH spot, 2022→2026 (daily/4h/1h), 2024→2026 (30m/15m)\n"
             "Event: wick>0.2%·close · Long next open · Target body_top+95%·wick within 2 candles · no SL",
             fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.93])
out = os.path.join(ROOT, "reports", "final_figure.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
fig.savefig(out, dpi=130)
print("SAVED", out)
