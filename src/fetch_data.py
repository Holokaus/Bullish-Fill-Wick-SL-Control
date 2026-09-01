"""
Fetch spot OHLCV (BTCUSDT, ETHUSDT) from Binance.
Monthly archives from data.binance.vision + REST tail to now.
Output: data/{SYM}_{tf}.csv with columns ts,open,high,low,close,volume (ts = UTC ms, open time).
Only fully closed candles are kept (last bar dropped if its close_time is in the future).
"""
import io, os, json, time, zipfile, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RAW = os.path.join(DATA, "raw")
os.makedirs(RAW, exist_ok=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
SPECS = {"1d": "2022-01", "4h": "2022-01", "1h": "2022-01", "30m": "2024-01", "15m": "2024-01"}
INTERVAL_MS = {"1d": 86_400_000, "4h": 14_400_000, "1h": 3_600_000, "30m": 1_800_000, "15m": 900_000}
COLS = ["open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "ntrades", "tbv", "tbqv", "ig"]


def utcnow_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def http_get(url, tries=5, timeout=90):
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "wick-research/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:
            err = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"GET failed {url}: {err}")


def ym_list(start_ym, end_ym):
    y, m = map(int, start_ym.split("-"))
    ey, em = map(int, end_ym.split("-"))
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}")
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def month_path(sym, tf, ym):
    return os.path.join(RAW, sym, tf, f"{ym}.csv")


def fetch_month(sym, tf, ym):
    p = month_path(sym, tf, ym)
    if os.path.exists(p):
        return sym, tf, ym, p, True, None
    url = f"https://data.binance.vision/data/spot/monthly/klines/{sym}/{tf}/{sym}-{tf}-{ym}.zip"
    try:
        raw = http_get(url)
    except Exception as e:
        return sym, tf, ym, None, False, str(e)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    zf = zipfile.ZipFile(io.BytesIO(raw))
    name = [n for n in zf.namelist() if n.lower().endswith(".csv")][0]
    with open(p, "wb") as f:
        f.write(zf.read(name))
    return sym, tf, ym, p, False, None


def read_part(path):
    with open(path) as f:
        first = f.readline()
    skip = 1 if any(c.isalpha() for c in first.split(",")[0]) else 0  # newer files carry a header row
    d = pd.read_csv(path, header=None, names=COLS, skiprows=skip)
    for c in COLS:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    # Unit normalization PER FILE: pre-2025 archives use milliseconds,
    # 2025+ archives use microseconds (and a header row). Normalize both ts cols.
    if len(d) and d["open_time"].max() > 1e14:  # > 1e14 can only be microseconds
        d["open_time"] = (d["open_time"] // 1000).astype("int64")
        d["close_time"] = (d["close_time"] // 1000).astype("int64")
    return d.dropna(subset=["open_time", "open", "high", "low", "close"])


def rest_tail(sym, tf, start_ms, end_ms):
    rows = []
    cursor = start_ms
    while cursor < end_ms:
        url = ("https://api.binance.com/api/v3/klines"
               f"?symbol={sym}&interval={tf}&startTime={cursor}&endTime={end_ms}&limit=1000")
        arr = json.loads(http_get(url))
        if not arr:
            break
        rows.extend(arr)
        last_open = arr[-1][0]
        nxt = last_open + INTERVAL_MS[tf]
        if nxt <= cursor:
            break
        cursor = nxt
        if len(arr) < 1000:
            break
    if not rows:
        return pd.DataFrame(columns=COLS)
    d = pd.DataFrame(rows, columns=COLS[: len(rows[0])] if len(rows[0]) != 12 else COLS)
    if d.shape[1] < 12:
        pad = pd.DataFrame([[None] * (12 - d.shape[1])] * len(d))
        d = pd.concat([d.reset_index(drop=True), pad], axis=1)
        d.columns = COLS
    return d


def build(sym, tf, start_ym, now_ms):
    now_dt = datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
    ym_now = f"{now_dt.year:04d}-{now_dt.month:02d}"
    months = ym_list(start_ym, ym_now)
    months = months[:-1] if len(months) > 1 else months  # current (incomplete) month comes from REST

    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = [ex.submit(fetch_month, sym, tf, ym) for ym in months]
        missing = []
        got = 0
        for fu in as_completed(futs):
            _, _, ym, path, cached, err = fu.result()
            if err or path is None:
                missing.append((ym, err))
            else:
                got += 1

    parts = [month_path(sym, tf, ym) for ym in months if os.path.exists(month_path(sym, tf, ym))]
    df = pd.concat([read_part(p) for p in parts], ignore_index=True) if parts else pd.DataFrame(columns=COLS)

    if len(df):
        tail_from = int(df["open_time"].max()) + INTERVAL_MS[tf]
    else:
        tail_from = int(pd.Timestamp(start_ym + "-01", tz="UTC").timestamp() * 1000)
    tail = rest_tail(sym, tf, tail_from, now_ms)
    if len(tail):
        tail = tail[[c for c in COLS if c in tail.columns]]
        for c in COLS:
            if c not in tail.columns:
                tail[c] = None
            tail[c] = pd.to_numeric(tail[c], errors="coerce")
        df = pd.concat([df, tail[COLS]], ignore_index=True)

    # ---- cleaning & QC ----  (timestamps are already normalized to ms in read_part)
    n_raw = len(df)
    df = df.drop_duplicates(subset="open_time", keep="first").sort_values("open_time").reset_index(drop=True)
    n_dupes = n_raw - len(df)
    # keep only fully closed candles
    df = df[df["close_time"] <= now_ms].reset_index(drop=True)
    ohlc_bad = int(((df["high"] < df[["open", "close"]].max(axis=1)) |
                    (df["low"] > df[["open", "close"]].min(axis=1)) |
                    (df["low"] <= 0)).sum())

    exp = INTERVAL_MS[tf]
    gaps = int((df["open_time"].diff().dropna() != exp).sum())
    out = df[["open_time", "open", "high", "low", "close", "volume"]].copy()
    out.insert(0, "ts", df["open_time"].astype("int64"))
    out = out.drop(columns=["open_time"])
    dest = os.path.join(DATA, f"{sym.lower()}_{tf}.csv")
    out.to_csv(dest, index=False)

    t0 = datetime.fromtimestamp(out["ts"].iloc[0] / 1000, tz=timezone.utc)
    t1 = datetime.fromtimestamp(out["ts"].iloc[-1] / 1000, tz=timezone.utc)
    print(json.dumps({"symbol": sym, "tf": tf, "rows": len(out),
                      "start_utc": t0.strftime("%Y-%m-%d %H:%M"), "end_utc": t1.strftime("%Y-%m-%d %H:%M"),
                      "gap_breaks": gaps, "dupes_removed": n_dupes, "ohlc_violations": ohlc_bad,
                      "missing_months": missing, "file": dest}))


def main():
    now_ms = utcnow_ms()
    for sym in SYMBOLS:
        for tf, start in SPECS.items():
            build(sym, tf, start, now_ms)


if __name__ == "__main__":
    main()
