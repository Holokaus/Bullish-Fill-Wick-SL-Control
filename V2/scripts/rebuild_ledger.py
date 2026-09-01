"""Reconstruct the union multiplicity ledger and append SL-study cells (Directive 3 + 4).

Prior honest family (442): W7 redo (144) + menu-1 (8) + two candidates (2) + MENU-2 (96).
SL-study adds 28 cells. Total = 470. BH q=0.05 across all. Report SL cells' union survival.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "src")

def bh_reject(pvals, q=0.05):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    thr = (np.arange(1, m + 1) / m) * q
    rej = np.zeros(m, bool)
    rej[order] = p[order] <= thr
    return rej, p[order]

OUT = Path("V2/outputs")

def pvals(path, col="pval"):
    return pd.read_csv(path)[col].clip(1e-12, 1.0).values.astype(float)

sl = pd.read_csv(OUT/"sl_study.csv")
sl_p = sl["pval"].clip(1e-12, 1.0).values.astype(float)

fam = {
    "w7": pvals(OUT/"w7_fdr_family.csv"),
    "menu1": pvals(OUT/"redir_w1_menu.csv"),
    "candidates": np.array([0.001307, 0.001069]),
    "menu2": pvals(OUT/"menu2_grid.csv"),
    "sl_study": sl_p,
}
ledger = {"families": {k: [float(x) for x in v] for k, v in fam.items()},
          "sizes": {k: len(v) for k, v in fam.items()}}
allp = np.concatenate(list(fam.values()))
rej, _ = bh_reject(allp, q=0.05)
ledger["total_cells"] = int(len(allp))
ledger["total_sig"] = int(rej.sum())
json.dump(ledger, open(OUT/"union_ledger.json", "w"), indent=2)

# SL cells' union survival
sl_start = len(allp) - len(sl_p)
sl_union = rej[sl_start:]
sl["bh_union"] = sl_union
sl.to_csv(OUT/"sl_study.csv", index=False)
print(f"Union ledger: {ledger['total_cells']} cells, {ledger['total_sig']} BH-significant (q=0.05)")
print(f"  sizes: " + ", ".join(f"{k}={v}" for k, v in ledger['sizes'].items()))
print(f"SL cells surviving union (q=0.05): {int(sl_union.sum())} / {len(sl_p)}")
print(sl[["row","policy","net","retention","pval","bh_union"]].to_string(index=False))
