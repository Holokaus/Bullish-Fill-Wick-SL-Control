import pandas as pd
import numpy as np

pd.set_option("display.width", 200)
SYMS = ["btcusdt", "ethusdt"]

# ---------- Q1: Open(e+1) vs Close(e) ----------
print("=" * 70)
print("Q1  Is Open(e+1) ~= Close(e)?")
print("=" * 70)
for sym in SYMS:
    for tf in ["1h"]:
        d = pd.read_csv(f"data/{sym}_{tf}.csv").sort_values("ts").reset_index(drop=True)
        nxt = d["open"].shift(-1)
        gap_bp = (1e4 * (nxt / d["close"] - 1)).replace([np.inf, -np.inf], np.nan).dropna()
        print(f"{sym} {tf}: median |Open(e+1)-Close(e)| = {gap_bp.abs().median():.3f} bp | "
              f"90pct {gap_bp.abs().quantile(.9):.2f} | 99pct {gap_bp.abs().quantile(.99):.2f}")

# ---------- geometry decomposition ----------
print()
print("=" * 70)
print("Q1b Required climb decomposition by candle color (BTC & ETH 1h)")
print("=" * 70)
for sym in SYMS:
    d = pd.read_csv(f"data/{sym}_1h.csv").sort_values("ts").reset_index(drop=True)
    d["entry"] = d["open"].shift(-1)          # buy price = open of the candle AFTER the event
    e = pd.read_csv(f"results/events_{sym}_1h.csv")
    j = e.merge(d[["ts", "open", "high", "low", "close", "entry"]], left_on="ts", right_on="ts")
    j = j.rename(columns={"open": "open_e", "high": "high_e", "low": "low_e", "close": "close_e"})
    bt = j[["open_e", "close_e"]].max(axis=1)
    bb = j[["open_e", "close_e"]].min(axis=1)
    wick = j["high_e"] - bt
    j["climb_to_bodytop"] = 1e4 * (bt / j["entry"] - 1)
    j["climb_body_to_target"] = 1e4 * (0.95 * wick / j["entry"])
    for name, sub in [("BULLISH events", j[j["bull_e"]]), ("BEARISH events", j[~j["bull_e"]])]:
        print(f"{sym} {name}: entry->body_top {sub['climb_to_bodytop'].median():7.1f} bp "
              f"+ body_top->target {sub['climb_body_to_target'].median():6.1f} bp "
              f"= total {sub['climb_to_bodytop'].median()+sub['climb_body_to_target'].median():7.1f} bp  (n={len(sub)})")

# ---------- Q2 + five executed trades ----------
print()
print("=" * 70)
print("FIVE EXAMPLE TRADES (real rows, BTCUSDT 1h)")
print("=" * 70)
d = pd.read_csv("data/btcusdt_1h.csv").sort_values("ts").reset_index(drop=True)
idx = {t: i for i, t in enumerate(d["ts"])}
e = pd.read_csv("results/events_btcusdt_1h.csv")
sample = e.sample(5, random_state=7).sort_values("ts_entry")

for _, r in sample.iterrows():
    iE, i1, i2 = idx[int(r.ts)], idx[int(r.ts_entry)], idx[int(r.ts_entry)] + 1
    E, C1, C2 = d.iloc[iE], d.iloc[i1], d.iloc[i2]
    bt = max(E.open, E.close)
    wick = E.high - bt
    T = bt + 0.95 * wick
    tE = pd.to_datetime(int(r.ts), unit="ms", utc=True).strftime("%m-%d %H:%M")
    t1 = pd.to_datetime(int(C1.ts), unit="ms", utc=True).strftime("%m-%d %H:%M")
    print(f"\n--- event candle {tE} UTC | color: {'BULL' if r.bull_e else 'BEAR'} ---")
    print(f"  e   : O={E.open:.2f} H={E.high:.2f} L={E.low:.2f} C={E.close:.2f}")
    print(f"       body_top={bt:.2f}  upper_wick={wick:.2f} ({100*wick/E.close:.3f}% of close > 0.2%) -> EVENT")
    print(f"  BUY @ open(e+1) {t1} = {C1.open:.2f}")
    print(f"  TARGET T = body_top + 95%*wick = {bt:.2f} + {0.95*wick:.2f} = {T:.2f}")
    req = 1e4 * (T / C1.open - 1)
    print(f"       required climb = {T:.2f}/{C1.open:.2f}-1 = {req:+.1f} bp")
    hit1 = C1.high >= T
    hit2 = (not hit1) and (C2.high >= T)
    if hit1 or hit2:
        when = "during e+1" if hit1 else "during e+2"
        print(f"  RESULT: WIN  - high reached T {when}")
        print(f"          e+1: H={C1.high:.2f} L={C1.low:.2f}   e+2: H={C2.high:.2f} L={C2.low:.2f}")
        gross = req
    else:
        exit_px = C2.close
        gross = 1e4 * (exit_px / C1.open - 1)
        print(f"  RESULT: NO FILL within e+1/e+2 -> EXIT at close(e+2) {exit_px:.2f}")
        print(f"          e+1: H={C1.high:.2f} L={C1.low:.2f}   e+2: H={C2.high:.2f} L={C2.low:.2f}, close={exit_px:.2f}")
    print(f"  PnL gross = {gross:+.1f} bp per unit notional"
          + (f"  (net futures maker/taker {gross-14:+.1f} bp)" if False else ""))
