import pandas as pd
pd.set_option("display.width",220); pd.set_option("display.max_rows",300)
R=pd.read_csv("outputs/w6_stop_study.csv")
# focus on TIME stops above cost, split by entry
t=R[(R.stop_type=="TIME") & R.sig_maker].copy()
print("=== TIME-stop above-cost cells, by entry ===")
for e in ["PB","MKT"]:
    sub=t[t.entry==e].sort_values("net_maker",ascending=False)
    print(f"\n-- entry={e}: {len(sub)} cells --")
    print(sub[["series","cond","f","stop_param","N","stop_out","net_maker","ci_lo","ci_hi","wr"]].head(12).to_string(index=False))
# Specifically the SOL-1h and ICP-1h candidate candidates
print("\n=== SOLUSDT-1h, CQ7, f=1.5, TIME, both entries ===")
for e in ["PB","MKT"]:
    s=R[(R.series=="SOLUSDT-1h")&(R.cond=="CQ7_w78q")&(R.f==1.5)&(R.stop_type=="TIME")&(R.entry==e)].sort_values("stop_param")
    print(s[["stop_param","N","stop_out","net_maker","ci_lo","ci_hi","wr"]].to_string(index=False))
print("\n=== ICPUSDT-1h, CQ7, f=1.5, TIME, both entries ===")
for e in ["PB","MKT"]:
    s=R[(R.series=="ICPUSDT-1h")&(R.cond=="CQ7_w78q")&(R.f==1.5)&(R.stop_type=="TIME")&(R.entry==e)].sort_values("stop_param")
    print(s[["stop_param","N","stop_out","net_maker","ci_lo","ci_hi","wr"]].to_string(index=False))
