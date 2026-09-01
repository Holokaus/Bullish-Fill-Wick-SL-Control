import pandas as pd
pd.set_option("display.width",220); pd.set_option("display.max_rows",300)
R=pd.read_csv("outputs/w6_stop_study.csv")
# W6 stored net_maker = mean(pnl_bps) - FEE_M(4.0). Recover gross mean and re-apply correct fee.
# Cost stack (Bybit perp VIP0, directive §1.3):
#   maker 2.0/side, taker 5.5/side, slippage 4 bps RT on taker legs.
#   MKT entry (taker) + TP-touch exit (taker)  = 5.5+5.5+4 = 15.0 bps RT
#   PB  entry (maker) + TP-touch exit (taker)  = 2.0+5.5+4 = 11.5 bps RT
CORR = {"MKT":15.0, "PB":11.5}
R["gross_mean_bps"] = R.net_maker + 4.0          # undo the uniform 4bps
R["correct_net"] = R.gross_mean_bps - R.entry.map(CORR)
R["correct_ci_lo"] = R.ci_lo + 4.0 - R.entry.map(CORR)
R["correct_ci_hi"] = R.ci_hi  # ci_hi unaffected by constant fee shift (it was hi-4)
# ci_hi was (hi - 4); correct ci_hi = hi - correct_fee = ci_hi + 4 - correct_fee
R["correct_ci_hi"] = R.ci_hi + 4.0 - R.entry.map(CORR)

print("=== TIME-stop cells, CORRECTED cost (taker 15 / PB 11.5 bps RT) ===")
t=R[(R.stop_type=="TIME")].copy()
sig=t[t.correct_ci_lo>0].sort_values("correct_net",ascending=False)
print(f"TIME cells above cost at correct fee: {len(sig)} (was 10 at fake 4bps)")
print(sig[["series","cond","entry","f","stop_param","N","stop_out","correct_net","correct_ci_lo","correct_ci_hi","wr"]].to_string(index=False))

print("\n=== All stop types, corrected, any cell above cost (ci_lo>0)? ===")
for st in ["ABS","ATR","QMAE","TIME","NOSL"]:
    sub=R[R.stop_type==st]
    print(f"  {st}: {int((sub.correct_ci_lo>0).sum())} / {len(sub)} above cost at correct fee")

print("\n=== Closest-to-cost TIME cells by entry (top 12 net) ===")
for e in ["PB","MKT"]:
    s=t[t.entry==e].sort_values("correct_net",ascending=False).head(8)
    print(f"\n-- {e} --")
    print(s[["series","cond","f","stop_param","N","correct_net","correct_ci_lo","correct_ci_hi","wr"]].to_string(index=False))
