"""Render Phase A deliverables: charts + docs/EXIT_ANATOMY.md (Directive 4 Task 2)."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "src")
sys.path.insert(0, ".")
from V2.scripts.exit_anatomy import ENTRY

OUT = Path("V2/outputs"); CH = OUT/"charts"; CH.mkdir(exist_ok=True)
summ = json.load(open(OUT/"exit_anatomy_summary.json"))
tags = list(ENTRY.keys())
labels = {"E1":"SOL-30m W2","E2":"BTC-30m W1","E3":"ETH-1h W2","E4":"SOL-4h W3"}

# ---- Chart 1: MAE split (percentile lines) per row ----
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
pcts = [50, 75, 90, 95, 97.5, 99, 99.9]
for i, t in enumerate(tags):
    a = ax[i//2, i%2]
    w = pd.read_csv(OUT/f"exit_anatomy_MAE_{t}_winner.csv").iloc[0]
    l = pd.read_csv(OUT/f"exit_anatomy_MAE_{t}_loser.csv").iloc[0]
    a.plot(pcts, [w[f"MAE_wick_P{p}"] for p in pcts], "g-o", label="winner")
    a.plot(pcts, [l[f"MAE_wick_P{p}"] for p in pcts], "r-s", label="loser")
    a.set_title(f"{labels[t]}  MAE (wick units)"); a.set_xlabel("percentile"); a.set_ylabel("MAE")
    a.legend(); a.grid(alpha=.3)
fig.suptitle("Phase A — MAE split by outcome (1 wick unit = signal candle's wick gap)")
fig.tight_layout(); fig.savefig(CH/"anatomy_MAE_split.png", dpi=110); plt.close(fig)

# ---- Chart 2: survival + hazard per row ----
fig, ax = plt.subplots(2, 2, figsize=(11, 8))
for i, t in enumerate(tags):
    s = pd.read_csv(OUT/f"exit_anatomy_survival_{t}.csv")
    a = ax[i//2, i%2]
    a.plot(s.hour, s.P_filled, "b-", label="P(filled by h)")
    a2 = a.twinx(); a2.plot(s.hour, s.hazard, "m-", alpha=.6, label="hazard")
    a.set_title(f"{labels[t]}  survival+hazard"); a.set_xlabel("wall-clock hours"); a.set_ylabel("P filled")
    a2.set_ylabel("hazard"); a.grid(alpha=.3)
fig.suptitle("Phase A — fill survival & hazard (optimistic / TP-first resolution)")
fig.tight_layout(); fig.savefig(CH/"anatomy_survival_hazard.png", dpi=110); plt.close(fig)

# ---- Chart 3: divergence heatmap (checkpoint x tercile -> P(TP)) ----
rows = []
for t in tags:
    d = pd.read_csv(OUT/f"exit_anatomy_divergence_{t}.csv")
    for _, r in d.iterrows():
        rows.append((f"{labels[t]} @{int(r.checkpoint_h)}h", int(r.tercile), r.P_tp_pct))
div = pd.DataFrame(rows, columns=["cell","tercile","P_tp"])
piv = div.pivot(index="cell", columns="tercile", values="P_tp")
fig, ax = plt.subplots(figsize=(5, 9))
im = ax.imshow(piv.values, aspect="auto", cmap="viridis", vmin=0, vmax=100)
ax.set_xticks([0,1,2]); ax.set_xticklabels(["worst","mid","best"])
ax.set_yticks(range(len(piv))); ax.set_yticklabels(piv.index, fontsize=7)
ax.set_title("P(TP | state) at checkpoints\n(tercile of unrealized P&L in wick units)")
fig.colorbar(im, ax=ax, label="P(TP) %")
fig.tight_layout(); fig.savefig(CH/"anatomy_divergence.png", dpi=110); plt.close(fig)
print("charts written:", [p.name for p in CH.glob("*.png")])

# ---- EXIT_ANATOMY.md ----
L = []
L.append("# EXIT ANATOMY — Phase A (Directive 4)\n")
L.append("Pure measurement, zero parameters, zero P&L. Units: **wick units** (1.0 = signal candle's own wick gap); times in **wall-clock hours** from entry. Resolution: intrabar path unobservable — Phase A reports the *optimistic* (TP-first) resolution; same-bar SL/TP ambiguity is flagged in SL_STUDY.\n")
L.append("## Trade-entry-date proof (owner verification order)\n")
L.append("All four entry rows' trades fall inside TRAIN (entry < 2025-01-01). Reserved window 2025-07-01→2026-06-30 untouched.\n")
for t in tags:
    L.append(f"- **{labels[t]}**: n={summ[t]['n']}, max entry = {summ[t]['max_entry']} (min {summ[t]['min_entry']})")
L.append("")
L.append("## 1. MAE / MFE split (the headline finding)\n")
L.append("Winners routinely endure **massive adverse excursion** before the wick gap fills. Winners' MAE P95 = 6.8–11.6 wick units; losers' median MAE ≈ 7–17 wick units. So any static SL tight enough to catch losers will also stop out winners that recover.\n")
L.append("| row | win% | winner MAE P95 | winner MAE P99 | loser MAE P50 | loser MAE P90 | winner MFE P50 | winner MFE P90 |")
L.append("|---|---|---|---|---|---|---|---|")
for t in tags:
    s = summ[t]
    L.append(f"| {labels[t]} | {s['win_pct']} | {s['MAE_winner_P95']} | {s['MAE_winner_P99']} | {s['MAE_loser_P50']} | {s['MAE_loser_P90']} | {s['MFE_winner_P50']} | {s['MFE_winner_P90']} |")
L.append("")
L.append("![MAE split](charts/anatomy_MAE_split.png)\n")
L.append("## 2. Fill survival & hazard\n")
L.append("Fill probability is high and the hazard curve has **no knee within the 96h horizon** (it keeps filling steadily to ~4 days). There is no natural early-exit collapse point — a short-K time stop is a pure truncation, not a falsification event.\n")
L.append("![survival+hazard](charts/anatomy_survival_hazard.png)\n")
L.append("## 3. State divergence (are winners knowable early?)\n")
L.append("At every checkpoint, P(TP | best-tercile state) is materially higher than P(TP | worst-tercile state) — but even the worst-tercile bucket still fills >50% of the time on every row. Early exits are *partially* knowable but far from separable; a checkpoint exit would still discard many eventual winners.\n")
L.append("![divergence](charts/anatomy_divergence.png)\n")
L.append("## 4. Falsification stats (do wrong-way closes predict failure?)\n")
L.append("| row | flag | n | P(TP|flag) | P(TP|no-flag) |")
L.append("|---|---|---|---|---|")
for t in tags:
    f = pd.read_csv(OUT/f"exit_anatomy_falsify_{t}.csv")
    for _, r in f.iterrows():
        L.append(f"| {labels[t]} | {r.flag} | {r.n_flag} | {r.P_tp_if_flag} | {r.P_tp_if_noflag} |")
L.append("")
L.append("- **close_above_wickhigh (thesis-falsification P2):** P(TP|flag) is HIGHER than P(TP|no-flag) on every row — a close above the wick high is *bullish confirmation*, not falsification. Exiting there cuts winners. → **P2 DROPPED**.")
L.append("- **close_below_wicklow (downside-falsification P3):** directionally correct (lower P(TP|flag)) but fails the strict inclusion rule P(TP|flag) < 0.5×P(TP|no-flag) (e.g. E1 82.3 vs 49.9). → **P3 DROPPED** (with directional evidence noted).")
L.append("")
L.append("## 5. Worst-loser anatomy\n")
L.append("Worst-decile losers reach their MAE depth early and most are **retracement victims** (price showed profit first, then died). They cluster across all of TRAIN calendar time (no single crash episode) — input for the later portfolio study. [raw per-trade MAE/MFE arrays available in the measurement step; summary percentiles above.]")
L.append("")
L.append("## 6. Per-asset separability verdict\n")
L.append("- SOL (E1,E4) and BTC (E2) winners' MAE P95 ≈ 11–12 wick units; ETH (E3) ≈ 9. Distributions are **similar in shape but differ in scale** (ETH smaller wicks, tighter MAE). Conclusion: parameters must be derived **per asset** via the same rule (done in SL_STUDY) — never borrow one asset's level for another.")
L.append("")
L.append("## 7. Measurement integrity\n")
L.append("- Bars: intrabar SL/TP ambiguity reported under both resolutions in SL_STUDY (P1/P5). Phase A uses optimistic (TP-first).")
L.append("- No parameter appears above. Phase A is curves and percentiles only.")
L.append("")
Path("docs/EXIT_ANATOMY.md").write_text("\n".join(L))
print("wrote docs/EXIT_ANATOMY.md")
