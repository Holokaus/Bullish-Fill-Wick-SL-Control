import pandas as pd
pd.set_option("display.width",200); pd.set_option("display.max_rows",200)
R=pd.read_csv("outputs/w6_stop_study.csv")
print("=== TIME-stop cells above cost (CI>0), best by net ===")
t=R[(R.stop_type=="TIME") & R.sig_maker].sort_values("net_maker",ascending=False)
print(t[["series","cond","entry","f","stop_param","N","stop_out","net_maker","ci_lo","ci_hi","wr"]].head(15).to_string(index=False))
print("\nTIME-stop above-cost count by series:")
print(t.groupby("series").size())

# For the strongest W5 candidate (ICP-1h), show how edge decays with each stop type
print("\n=== ICPUSDT-1h, ALL, PB, f=1.0 : stop sweep (net bps, stop-out rate) ===")
sub=R[(R.series=="ICPUSDT-1h")&(R.cond=="ALL")&(R.entry=="PB")&(R.f==1.0)].copy()
for st in ["NOSL","ABS","ATR","QMAE","TIME"]:
    s=sub[sub.stop_type==st].sort_values("stop_param")
    print(f"\n-- {st} --")
    print(s[["stop_param","N","stop_out","net_maker","ci_lo","ci_hi","wr"]].to_string(index=False))

print("\n=== Best ABS/ATR/QMAE cell per series (highest net_maker, even if <cost) ===")
for st in ["ABS","ATR","QMAE"]:
    s=R[R.stop_type==st].sort_values("net_maker",ascending=False).head(8)
    print(f"\n-- {st} --")
    print(s[["series","cond","entry","f","stop_param","N","stop_out","net_maker","ci_lo","ci_hi"]].to_string(index=False))
