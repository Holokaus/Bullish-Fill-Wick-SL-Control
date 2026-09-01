"""Fetch Bybit USDT-perp klines (TRAIN only: 2022-09-01 -> 2024-12-31) for MENU-2.

Missing Tier-A series/TF written to RAW_DIR as <SYM>-FUTURES-2022-2026-<TF>.csv
(header: Time,Open,High,Low,Close,Volume,Date to match existing files).
Reserved window (2025-07-01+) is intentionally NOT fetched (stay dark). TRAIN clip + assert.
"""
import sys, time, json
from pathlib import Path
import urllib.request
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
import lib.paths as P, lib.time_gates as T

SYMS=["SOLUSDT","BTCUSDT","ETHUSDT"]
TFS={"30m":"30","1h":"60","4h":"240","1D":"D"}
START=int(pd.Timestamp("2022-09-01",tz="UTC").timestamp()*1000)
END=int(pd.Timestamp("2024-12-31 23:59:00",tz="UTC").timestamp()*1000)
HAVE={"SOLUSDT":{"1h","4h"},"BTCUSDT":{"1h"},"ETHUSDT":{"1h"}}   # already present locally

def fetch(sym, interval):
    rows=[]
    cursor=START
    while cursor<=END:
        url=f"https://api.bybit.com/v5/market/kline?category=linear&symbol={sym}&interval={interval}&limit=1000&start={cursor}"
        req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        d=json.load(urllib.request.urlopen(req, timeout=30))
        if d.get("retCode")!=0:
            raise RuntimeError(f"{sym} {interval}: {d.get('retMsg')}")
        batch=d["result"]["list"]
        if not batch: break
        rows.extend(batch)
        # ensure ascending by start time
        batch.sort(key=lambda r:int(r[0]))
        cursor=int(batch[-1][0])+1
        if len(batch)<1000: break
        time.sleep(0.25)
    df=pd.DataFrame(rows, columns=["time","open","high","low","close","volume","turnover"])
    df["time"]=df["time"].astype("int64"); df=df.drop_duplicates("time").sort_values("time")
    df["Date"]=pd.to_datetime(df["time"],unit="ms",utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    out=df[["time","open","high","low","close","volume","Date"]].astype({"open":float,"high":float,"low":float,"close":float,"volume":float})
    return out

for sym in SYMS:
    for tf,iv in TFS.items():
        if tf in HAVE.get(sym,set()):
            print(f"skip {sym} {tf} (present)"); continue
        try:
            out=fetch(sym, iv)
            out=T.filter_window(out, "TRAIN")   # assert no reserved-window leakage
            fn=P.RAW_DIR/f"{sym}-FUTURES-2022-2026-{tf}.csv"
            out.to_csv(fn, index=False)
            print(f"OK {sym} {tf}: {len(out)} rows -> {fn.name}")
        except Exception as e:
            print(f"FAIL {sym} {tf}: {e!r}")
print("FETCH DONE")
