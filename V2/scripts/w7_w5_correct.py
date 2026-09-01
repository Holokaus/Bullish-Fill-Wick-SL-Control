import pandas as pd
pd.set_option("display.width",220); pd.set_option("display.max_rows",300)
R=pd.read_csv("outputs/w5_nosl_economics.csv")
# W5 stored net_maker = mean(pnl_bps) - FEE_M(4.0). Recover gross and re-apply correct fee.
CORR = {"MKT":15.0, "PB":11.5}
R["gross"] = R.net_maker + 4.0
R["cnet"] = R.gross - R.entry.map(CORR)
R["ci_lo_c"] = R.ci_lo_m + 4.0 - R.entry.map(CORR)
R["ci_hi_c"] = R.ci_hi_m + 4.0 - R.entry.map(CORR)
print("=== W5 NOSL cells at CORRECT fee (taker 15 / PB 11.5 bps RT) ===")
sig=R[(R.exit=="NOSL") & (R.ci_lo_c>0)].sort_values("cnet",ascending=False)
print(f"NOSL cells above cost at correct fee: {len(sig)} (was 118 at fake 4bps)")
print(sig[["series","cond","entry","f","N","cnet","ci_lo_c","ci_hi_c","wr"]].head(25).to_string(index=False))
print("\n=== By entry (above-cost) ===")
for e in ["PB","MKT"]:
    s=sig[sig.entry==e]
    print(f"\n-- {e}: {len(s)} cells --")
    print(s[["series","cond","f","N","cnet","ci_lo_c","ci_hi_c","wr"]].head(12).to_string(index=False))
# how many series have >=1 above-cost NOSL cell at correct fee
print("\nSeries with >=1 above-cost NOSL cell (correct fee):",
      sorted(sig.series.unique().tolist()))
