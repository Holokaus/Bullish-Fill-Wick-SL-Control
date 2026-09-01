"""Print exact row counts and UTC spans for every dataset file (for documentation)."""
import os
import pandas as pd

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
for sym in ["btcusdt", "ethusdt", "solusdt"]:
    for tf in ["1d", "4h", "1h", "30m", "15m"]:
        p = os.path.join(DATA, f"{sym}_{tf}.csv")
        if not os.path.exists(p):
            print(f"{sym}_{tf}: MISSING")
            continue
        d = pd.read_csv(p)
        t0 = pd.to_datetime(d["ts"].iloc[0], unit="ms", utc=True)
        t1 = pd.to_datetime(d["ts"].iloc[-1], unit="ms", utc=True)
        print(f"{sym}_{tf}: rows={len(d):>6}  {t0:%Y-%m-%d %H:%M} -> {t1:%Y-%m-%d %H:%M} UTC")
