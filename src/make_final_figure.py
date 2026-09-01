import json, os, matplotlib.pyplot as plt, numpy as np
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES=os.path.join(ROOT,"results"); REP=os.path.join(ROOT,"reports")
os.makedirs(REP,exist_ok=True)
data=json.load(open(os.path.join(RES,"FINAL_SYSTEM.json")))
rules=data["rules"]
plt.figure(figsize=(12,8))
for r in rules:
    eq=np.array(r["equity"])*100  # pct
    ts=np.array(r["ts"])
    # normalize time to index for plot
    plt.plot(eq, label=f"{r['rule']['desc']} n={r['n']} net {r['net_bp']:.1f}bp")
# combined
import pandas as pd
all_trades=[]
for r in rules:
    eq=np.array(r["equity"])
    # recombine already computed combined in final system
comb=json.load(open(os.path.join(RES,"FINAL_SYSTEM.json")))["combined"]
# build combined equity from trades
trades=comb["trades"]
ts_sorted=[t[0] for t in trades]
eq=np.cumsum([t[1] for t in trades])*100
plt.plot(eq, 'k--', linewidth=2, label=f"COMBINED n={comb['n']} {comb['total_pct']:.1f}%")
plt.title("Muse Spark 1.2 - Final System Equity (net -11bp costs) | SOL Wick-Conditioned Longs")
plt.xlabel("Trade sequence (2022-2026)")
plt.ylabel("Cumulative % (summed, 1x notional)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(REP,"FINAL_SYSTEM_EQUITY.png"), dpi=150)
print("SAVED", os.path.join(REP,"FINAL_SYSTEM_EQUITY.png"))
# per-year bar
import matplotlib
fig, ax = plt.subplots(figsize=(10,4))
years=["2022","2023","2024","2025","2026"]
for r in rules:
    vals=[r["per_year"].get(y,{"net_bp":0})["net_bp"] for y in years]
    ax.plot(years, vals, marker='o', label=r["rule"]["desc"])
ax.axhline(0,color='k',linewidth=0.8)
ax.set_title("Per-year net bp/trade - walk-forward stability")
ax.set_ylabel("net bp")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(REP,"PER_YEAR_STABILITY.png"), dpi=150)
print("SAVED per year")
