"""OF-W4a: CONDITIONAL ANATOMY ATLAS - event-table builder (TRAIN only, EXPLORATION).

Per series (13 asset x TF, INDEPENDENTLY - each asset has its own personality):
builds one row per big-upper-wick event (uw_frac >= TRAIN tercile among bullish candles)
with 10 condition features and forward outcome statistics.

Features (all strictly known at signal-bar close; TRAIN-frozen cuts):
  uw_d    : wick-length decile (1-10)      - dose-response of wick length
  trend   : ret24 quintile (0-4)           - trend-following context
  smaal   : close vs SMA50 alignment       - higher TF trend agreement
  prev    : prior candle type              - the candle before the event candle
  volq    : volume quintile                - event-candle volume vs own history
  typ     : candle type (body/lower-wick)  - marubozu / normal / lower-wick-heavy
  rng_q   : range-expansion quintile       - volatility context
  hr      : hour-of-day bucket             - intraday personality
  dow     : day-of-week                    - weekly personality
  regime  : BTC 90d regime tag             - market weather

Outcomes (event-time, no lookahead):
  hit1/hit2/hitH : wick-high touched within 1/2/H bars   (H=48)
  t_hit          : bars to first high-touch (-1 if never in H)
  cross          : price crossed UP through level before horizon end
  n_bounce_pre   : down-crossings before the up-fill
  mae_pre        : worst adverse dip before the fill
  r24            : 24-bar forward return from signal close (bps)
  e2             : extended target at body_top + 1.5*(wick gap) touched within H

Outputs outputs/atlas/<SYM>-<TF>_events.parquet + a frozen cuts json.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

STUDY = Path(r"C:\Users\A\Bullish-Fill-Wick\V2")
SRC = Path(r"C:\Users\A\Downloads\opencode-bybit")
OUT = STUDY/"outputs"; ATLAS = OUT/"atlas"; ATLAS.mkdir(parents=True, exist_ok=True)

TRAIN_START_MS = int(pd.Timestamp("2022-09-01").value // 10**6)
TRAIN_END_MS   = int(pd.Timestamp("2025-01-01").value // 10**6)
H = 48

DATA_FILES = [
    ("SOLUSDT","5m",  SRC/r"Z-attempt-2\SOLUSDT-FUTURES-2022-2026-5m.csv"),
    ("SOLUSDT","15m", SRC/r"Z-attempt-2\SOLUSDT-FUTURES-2022-2026-15m.csv"),
    ("SOLUSDT","30m", SRC/r"SOLUSDT-FUTURES-2021-2026-30m.csv"),
    ("SOLUSDT","1h",  SRC/r"SOLUSDT-FUTURES-2022-2026-1h.csv"),
    ("SOLUSDT","4h",  SRC/r"SOLUSDT-FUTURES-2022-2026-4h.csv"),
    ("ICPUSDT","5m",  SRC/r"Z-attempt-2\ICPUSDT-FUTURES-2022-2026-5m.csv"),
    ("ICPUSDT","15m", SRC/r"Z-attempt-2\ICPUSDT-FUTURES-2022-2026-15m.csv"),
    ("ICPUSDT","30m", SRC/r"ICPUSDT-FUTURES-2022-2026-30m.csv"),
    ("ICPUSDT","1h",  SRC/r"ICPUSDT-FUTURES-2022-2026-1h.csv"),
    ("ICPUSDT","4h",  SRC/r"ICPUSDT-FUTURES-2022-2026-4h.csv"),
    ("BTCUSDT","15m", SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-15m.csv"),
    ("BTCUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\BTCUSDT-FUTURES-2022-2026-1h.csv"),
    ("ETHUSDT","1h",  SRC/r"deepSeek-new-approach-volume-support-resistance\ETHUSDT-FUTURES-2022-2026-1h.csv"),
]
TF_MIN = {"5m":5,"15m":15,"30m":30,"1h":60,"4h":240}

def load_train(path):
    df = pd.read_csv(path)
    low = {c.strip().strip('"').lower(): c for c in df.columns}
    ren = {}
    for std, al in {"time":["time"],"open":["open"],"high":["high"],
                    "low":["low"],"close":["close"],"volume":["volume"]}.items():
        ren[low[al[0]]] = std
    df = df.rename(columns=ren)[["time","open","high","low","close","volume"]].apply(pd.to_numeric)
    return df.drop_duplicates("time").sort_values("time").reset_index(drop=True)

# BTC regime from train BTC 1h
btc = load_train(DATA_FILES[11][2])
btc = btc[(btc.time>=TRAIN_START_MS)&(btc.time<TRAIN_END_MS)]
bd = btc.set_index(pd.to_datetime(btc["time"], unit="ms"))["close"].resample("1D").last().dropna()
br90 = bd/bd.shift(90)-1.0
def regime_of(ms):
    r = br90.reindex([pd.Timestamp(ms, unit="ms")], method="ffill").iloc[0]
    if pd.isna(r): return 1
    return 2 if r>0.20 else (0 if r<-0.20 else 1)

CUTS_OUT = {}
for sym, tf, path in DATA_FILES:
    key = f"{sym}-{tf}"
    full = load_train(path)
    tr = full[(full.time>=TRAIN_START_MS)&(full.time<TRAIN_END_MS)].reset_index(drop=True)

    O=tr.open.values.astype(float); Hh=tr.high.values.astype(float)
    L=tr.low.values.astype(float);  C=tr.close.values.astype(float); V=tr.volume.values.astype(float)
    times = tr.time.values; n=len(tr); mins=TF_MIN[tf]

    # --- anatomy & context ---
    rng = Hh-L
    body = np.abs(C-O)
    uw = np.where(rng>0,(Hh-np.maximum(O,C))/rng, np.nan)
    lw = np.where(rng>0,(np.minimum(O,C)-L)/rng, np.nan)
    bs = np.where(rng>0, body/rng, np.nan)
    bull = (C>O)&(rng>0)
    prev_dir = pd.Series(np.sign(C-O)).shift(1).values          # prior candle direction
    atr14 = pd.Series(rng).rolling(14).mean().shift(1).values   # ATR of ranges, excl current
    rx = rng/atr14
    sma50 = pd.Series(C).rolling(50).mean().shift(1).values
    smaal = np.where(C>sma50, 1, np.where(C<sma50, -1, 0)).astype(float)
    vma20 = pd.Series(V).rolling(20).mean().shift(1).values
    vr = V/vma20
    ret24 = C/pd.Series(C).shift(24).values-1.0
    hr  = ((times// (3600_000)) % 24)
    dow = (((times//86400000)+4)%7)

    # --- TRAIN cuts (bullish population) ---
    bm = bull & ~np.isnan(rx) & ~np.isnan(vr) & ~np.isnan(ret24)
    uw_terc = float(np.nanquantile(uw[bull], 2/3))
    CUTS_OUT[key] = dict(uw_tercile=uw_terc,
        uw_deciles=[float(x) for x in np.nanquantile(uw[bull], np.arange(0.1,1.0,0.1))],
        ret24_q=[float(x) for x in np.nanquantile(ret24[bm],[.2,.4,.6,.8])],
        vr_q=[float(x) for x in np.nanquantile(vr[bm],[.2,.4,.6,.8])],
        rx_q=[float(x) for x in np.nanquantile(rx[bm],[.2,.4,.6,.8])],
        train_last=int(times[-1]))
    dq = np.array(CUTS_OUT[key]["uw_deciles"])

    # --- events ---
    sig = np.where(bull & (uw>=uw_terc) & ~np.isnan(rx) & ~np.isnan(vr)
                   & ~np.isnan(ret24) & ~np.isnan(prev_dir))[0]
    rows=[]
    for i in sig:
        lvl = Hh[i]; bt=max(O[i],C[i]); bb=min(O[i],C[i]); gap=lvl-bt
        if not (gap>0): continue
        end=min(i+H, n-1)
        segH=Hh[i+1:end+1]; segL=L[i+1:end+1]; segC=C[i+1:end+1]
        if len(segH)==0: continue
        above = segH>lvl; below = segL<bb
        hit = bool(above.any())
        j_hit = int(np.argmax(above)) if hit else -1
        hit2 = bool((segH[:min(2,len(segH))]>lvl).any())
        ext_lvl = bt+1.5*gap
        ext = bool((segH>=ext_lvl).any())
        if hit:
            pre_below = below[:j_hit]
            nb = int(pd.Series(pre_below).diff().fillna(0).eq(1).sum()) if pre_below.any() else 0
            mae = float(segL[:j_hit+1].min())
            t_hit = j_hit+1
        else:
            nb = 0; mae = float(segL.min()); t_hit=-1
        r24 = (C[min(i+24,n-1)]-C[i])/C[i]*1e4 if i+24<n else np.nan
        rows.append(dict(
            uwd = int(np.searchsorted(dq, uw[i])+1),
            trend=int(np.searchsorted(CUTS_OUT[key]["ret24_q"], ret24[i])),
            smaal=int(smaal[i]), prev=int(prev_dir[i]),
            volq=int(np.searchsorted(CUTS_OUT[key]["vr_q"], vr[i])),
            typ = 0 if bs[i]>=0.7 else (2 if lw[i]>=0.33 else 1),
            rng_q=int(np.searchsorted(CUTS_OUT[key]["rx_q"], rx[i])),
            hr=int(hr[i]), dow=int(dow[i]), reg=regime_of(times[i]),
            hit1=bool(segH[0]>lvl), hit2=hit2, hitH=hit,
            t_hit=t_hit, cross=bool(hit), n_bounce_pre=nb,
            mae_pre=(mae-C[i])/C[i]*1e4,
            r24=r24, e2=ext, uw=float(uw[i])))
    ev=pd.DataFrame(rows)
    ev.to_parquet(ATLAS/f"{key}_events.parquet", index=False)
    print(f"{key:16s} events={len(ev):>6d} hit2={ev.hit2.mean():.3f} hitH={ev.hitH.mean():.3f} "
          f"e2={ev.e2.mean():.3f} med_t={ev.loc[ev.hitH,'t_hit'].median() if ev.hitH.any() else -1}", flush=True)

json.dump(CUTS_OUT, open(ATLAS/"atlas_cuts.json","w"), indent=1)
print("\nAtlas event tables -> ", ATLAS)
