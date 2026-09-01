"""OF-W0b v2: Download EXTENDED LOCKBOX klines (Jul 1 - Aug 26 2026) fresh from Bybit v5.
Write-only storage in V2/data_lockbox/. Only row COUNTS printed here.
"""
import time
from pathlib import Path
import requests
import pandas as pd

LOCKBOX = Path(r"C:\Users\A\Bullish-Fill-Wick\V2\data_lockbox")
LOCKBOX.mkdir(parents=True, exist_ok=True)
URL = "https://api.bybit.com/v5/market/kline"

SERIES = [("SOLUSDT","5m",5),("SOLUSDT","15m",15),("SOLUSDT","30m",30),
          ("SOLUSDT","1h",60),("SOLUSDT","4h",240),
          ("ICPUSDT","5m",5),("ICPUSDT","15m",15),("ICPUSDT","30m",30),
          ("ICPUSDT","1h",60),("ICPUSDT","4h",240),
          ("BTCUSDT","15m",15),("BTCUSDT","1h",60),("ETHUSDT","1h",60)]

START = int(pd.Timestamp("2026-07-01").value // 10**6)
END   = int(pd.Timestamp("2026-08-26").value // 10**6)

for sym, tf, mins in SERIES:
    out = LOCKBOX / f"{sym}-{tf}-lockbox.csv"
    if out.exists():
        print(f"{sym} {tf}: exists, skip"); continue
    all_rows, cursor = {}, END
    while cursor > START:
        r = requests.get(URL, params=dict(category="linear", symbol=sym,
                                          interval=str(mins), start=str(START),
                                          end=str(cursor), limit=1000), timeout=30)
        data = r.json().get("result", {}).get("list", [])
        if not data: break
        for row in data:
            all_rows[int(row[0])] = row[:6]
        oldest = min(int(x[0]) for x in data)
        if oldest >= cursor: break
        cursor = oldest
        time.sleep(0.12)
    df = pd.DataFrame([all_rows[k] for k in sorted(all_rows)],
                      columns=["time","open","high","low","close","volume"])
    for c in df.columns:
        df[c] = pd.to_numeric(df[c])
    df.to_csv(out, index=False)
    ok = len(df)>0 and df["time"].iloc[0] >= START and df["time"].iloc[-1] < END
    print(f"{sym} {tf}: saved {len(df)} rows span_ok={ok}", flush=True)
print("\nLockbox sealed:", LOCKBOX)
