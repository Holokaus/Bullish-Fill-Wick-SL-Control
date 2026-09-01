import pandas as pd
R=pd.read_csv("outputs/w5_nosl_economics.csv")
print("TOTAL cells per exit:", R.groupby("exit").size().to_dict())
print("NOSL significant (ci_lo_m>0):", int(R[R.exit=="NOSL"].sig_maker.sum()))
# short timeframes where funding negligible (<=1h)
mask = R.exit=="NOSL"
short = R[mask & R.series.str.contains("5m|15m|30m|1h", regex=True) & R.sig_maker]
print("\nNOSL significant on <=1h timeframes:", len(short))
print(short.sort_values("net_maker",ascending=False).head(12)[
    ["series","cond","entry","f","N","net_maker","ci_lo_m","ci_hi_m"]].to_string(index=False))
sl=R[R.exit.isin(["low","mid"])]
print("\nSL(low+mid) cells net_maker>0:", int((sl.net_maker>0).sum()), "of", len(sl))
print("\nMedian net_maker by exit:")
print(R.groupby("exit").net_maker.median().round(2).to_dict())
