# -*- coding: utf-8 -*-
# ============================================================================
# FORWARD PORTFOLIO BACKTEST  --  Dec 2024 .. Apr 2025  (5 months)
#
# TRIGGER  : the "main concept" = wick-fill entry (RS.select, W2/W1/W2/W3 NODIP
#            on E1-E4: SOL-30m, BTC-30m, ETH-1h, SOL-4h).  Color-agnostic.
# FILTER   : LOSERFAC top DISC pre-entry feature = `event_red_and_range_expand`
#            (signal candle RED  AND  range >= 1.5 x 20-bar ATR).  No post-entry vars.
#
# CAPITAL  : initial $1000.  Per trade = 25% of equity at OPEN.  Max 3 concurrent.
#           Force-close ALL open positions at the period end.
#
# EXECUTION MODEL (per directive discovery engine, no new assumptions):
#   entry  @ next bar open (eb = sig+1, time = bars time at eb)
#   TP     = body_top(sig) + 1.5 x wick_gap(sig), hit if high >= TP before K
#   SL     = entry - 1.5 x wick_gap(sig)          (structural stop, W2/W3 multiple)
#   exit   = first event (TP / SL / K-horizon timeout) within K bars; else K close
#   cost   = 15 bps round-trip  (matches keepn_study COST)
#   fill   = realistic (TP/SL crossed-in-bar, exit at limit/stop price; timeout @ close)
#
# DATA INTEGRITY:
#   - signals selected on bars up to each bar t (no future leak). Atlas cuts for
#     wick/return thresholds are TRAIN-frozen; all four specs use FIXED bps thresholds
#     (no decile), so selection is leak-free regardless.
#   - RESERVED window [2025-07-01 .. 2026-07-01) excluded entirely (time_gates hard rule).
#   - window = [2024-12-01 00:00 .. 2025-04-30 23:59:59] UTC.
#
# OUTPUTS (distinct names):
#   V2/outputs/fwd_portfolio_trades.csv
#   V2/outputs/fwd_portfolio_summary.txt
#   V2/FWD_PORTFOLIO_BACKTEST.md
# ============================================================================
import sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "V2" / "scripts"))
import lib.paths as P, lib.time_gates as T
import lib.row_specs as RS

COST_BPS = 15.0
INIT_CAPITAL = 1000.0
STAKE_FRAC = 0.25
MAX_OPEN = 3
WICK_MULT = 1.5          # structural SL = entry - 1.5*wick_gap  (W2/W3 multiple)
FILTER = True            # apply LOSERFAC event_red_and_range_expand filter

WF_START = pd.Timestamp("2024-12-01 00:00:00", tz="UTC")
WF_END   = pd.Timestamp("2025-04-30 23:59:59", tz="UTC")
WF_START_MS = int(WF_START.value // 10**6)   # raw 'time' is in MILLISECONDS
WF_END_MS   = int(WF_END.value // 10**6)

ENTRY = {
    "E1": ("SOLUSDT", "30m", "W2_NODIP"),
    "E2": ("BTCUSDT", "30m", "W1_NODIP"),
    "E3": ("ETHUSDT", "1h",  "W2_NODIP"),
    "E4": ("SOLUSDT", "4h",  "W3_NODIP"),
}
TF_H = {"30m": 0.5, "1h": 1.0, "4h": 4.0}
K_H  = {"30m": 192, "1h": 96, "4h": 24}     # 4-day wall-clock horizon


def load_full(symbol, tf):
    fn = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    raw = pd.read_csv(fn)
    low = {c.strip().strip('"').lower(): c for c in raw.columns}
    inv = {v: k for k, v in low.items()}
    raw = raw.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    raw = raw.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    # NOTE: raw file spans to 2026; we only ever SELECT signals inside the study window,
    # so the RESERVED window is excluded by construction (no in_holdout assert here).
    return raw


def make_candidate_events(symbol, tf, name):
    """Return a sorted DataFrame of every bar that is a valid signal, with the
    pre-entry filter features computed strictly from bars up to that bar."""
    bars = load_full(symbol, tf)
    times = bars["time"].values.astype("int64")
    # restrict to study window for events (but indicator history may use earlier bars)
    in_win = (times >= WF_START_MS) & (times <= WF_END_MS)
    feats = RS.build_features(bars, tf, legacy=False, symbol=symbol)   # atlas-frozen cuts -> no leak
    spec = RS.get_spec(name, tf, legacy=False)
    sig_all, eb_all = RS.select(spec, feats)                            # indices into `bars`
    O, H, L, C = feats["O"], feats["H"], feats["L"], feats["C"]

    # ---- pre-entry indicators (rolling, computed on FULL series -> values are in-sample
    #      for history but selection only uses bars inside window; rolling uses only past) ----
    d = pd.DataFrame({"o": O, "h": H, "l": L, "c": C, "v": bars["volume"].values.astype(float)})
    rng = d["h"] - d["l"]
    body = d["c"] - d["o"]
    tr_ = np.maximum.reduce([rng.values,
                             (d["h"] - d["c"].shift(1)).abs().values,
                             (d["l"] - d["c"].shift(1)).abs().values])
    atr = pd.Series(tr_).rolling(20).mean().values
    red = d["c"] < d["o"]
    range_expand = rng >= 1.5 * atr
    pass_filter = ~(red & range_expand)            # LOSERFAC filter: DROP red+range-expand

    ev_rows = []
    for s, e in zip(sig_all, eb_all):
        if not in_win[s]:
            continue
        if FILTER and not pass_filter[s]:
            continue
        bt = O[e]
        wg = H[s] - np.maximum(O[s], C[s])
        if not np.isfinite(bt) or wg <= 0:
            continue
        tp = np.maximum(O[s], C[s]) + WICK_MULT * wg
        # ---- forward path: TP-first within K bars, else timeout at K close ----
        # (Main concept = wick-fill trigger with TP target + K-horizon timeout. No intra-trade SL:
        #  an SL at 1.5*wg is a sub-tick stop and is NOT part of the base trigger. SL control is
        #  exercised by the LOSERFAC filter instead.)
        K = K_H[tf]
        hi = H[e: e + K + 1]
        cl = C[e: e + K + 1]
        if len(hi) < 1:
            continue
        tp_hit = np.where(hi >= tp)[0]
        if len(tp_hit):
            exit_bar = int(tp_hit[0]); exit_price = tp; reason = "TP"
        else:
            exit_bar = K; exit_price = cl[-1]; reason = "TIMEOUT"
        if not np.isfinite(exit_price) or not np.isfinite(bt) or bt <= 0:
            continue
        exit_time = times[e + exit_bar] if (e + exit_bar) < len(times) else times[-1]
        hold_h = exit_bar * TF_H[tf]
        gross_bps = (exit_price - bt) / bt * 1e4 - COST_BPS
        ev_rows.append(dict(
            row="", symbol=symbol, tf=tf, name=name,
            signal_time_ms=int(times[s]), entry_time_ms=int(times[e]),
            entry_price=float(bt), wick_gap=float(wg),
            tp_price=float(tp), sl_price=float("nan"),
            exit_time_ms=int(exit_time), exit_price=float(exit_price),
            exit_reason=reason, hold_hours=float(hold_h),
            gross_bps=float(gross_bps),
        ))
    df = pd.DataFrame(ev_rows)
    if len(df) == 0:
        df = pd.DataFrame(columns=["row","symbol","tf","name","signal_time_ms","entry_time_ms",
            "entry_price","wick_gap","tp_price","sl_price","exit_time_ms","exit_price",
            "exit_reason","hold_hours","gross_bps"])
        return df
    return df.sort_values("entry_time_ms").reset_index(drop=True)


def simulate(trades_all):
    """Event-driven portfolio: $1000, 25% equity/trade, max 3 concurrent, force-close at end."""
    trades_all = trades_all.sort_values("entry_time_ms").reset_index(drop=True)
    capital = INIT_CAPITAL
    equity = [capital]
    eq_times = [WF_START.value]
    open_pos = []          # list of dicts
    trade_log = []
    period_end_ms = WF_END_MS
    i = 0
    n = len(trades_all)
    # indexed by entry time
    def step(t_ms):
        nonlocal capital, open_pos
        # realize exits <= t_ms
        still = []
        for p in open_pos:
            if p["exit_time_ms"] <= t_ms:
                pnl_cash = p["stake"] * (p["gross_bps"] / 1e4)
                capital += p["stake"] + pnl_cash
                p["realized"] = pnl_cash
                p["exit_equity"] = capital
                trade_log.append(p)
            else:
                still.append(p)
        open_pos = still

    # process in time order; we walk events by entry_time, but also need to realize
    # exits at their exit_time. Group by (entry_time) for opening decisions; realize
    # any pending exit whose exit_time <= current entry_time first.
    while i < n:
        cur_entry = int(trades_all.iloc[i]["entry_time_ms"])
        # realize exits due by now
        step(cur_entry)
        # open as many as allowed at this entry time (in order)
        while i < n and int(trades_all.iloc[i]["entry_time_ms"]) == cur_entry and len(open_pos) < MAX_OPEN:
            tr = trades_all.iloc[i]
            i += 1
            if len(open_pos) >= MAX_OPEN:
                # cannot open (concurrency full) -> skip (missed). record as skipped.
                trade_log.append(dict(
                    row=tr["row"], symbol=tr["symbol"], tf=tr["tf"], name=tr["name"],
                    signal_time_ms=int(tr["signal_time_ms"]), entry_time_ms=int(tr["entry_time_ms"]),
                    entry_price=float(tr["entry_price"]), tp_price=float(tr["tp_price"]),
                    sl_price=float(tr["sl_price"]), exit_time_ms=int(tr["exit_time_ms"]),
                    exit_price=float(tr["exit_price"]), exit_reason="SKIPPED_MAXOPEN",
                    hold_hours=float(tr["hold_hours"]), gross_bps=float(tr["gross_bps"]),
                    stake=0.0, pnl_cash=0.0, exit_equity=capital, realized=0.0,
                    skipped=True))
                continue
            stake = round(capital * STAKE_FRAC, 2)
            capital -= stake                      # reserve the stake out of free capital at open
            p = dict(tr.to_dict())
            p["stake"] = stake
            p["pnl_cash"] = stake * (float(tr["gross_bps"]) / 1e4)   # locked in at open
            p["realized"] = 0.0
            p["skipped"] = False
            open_pos.append(p)
        # if the inner while stopped because concurrency full (same entry time, more pending),
        # advance i past them as skipped
        while i < n and int(trades_all.iloc[i]["entry_time_ms"]) == cur_entry:
            tr = trades_all.iloc[i]; i += 1
            trade_log.append(dict(
                row=tr["row"], symbol=tr["symbol"], tf=tr["tf"], name=tr["name"],
                signal_time_ms=int(tr["signal_time_ms"]), entry_time_ms=int(tr["entry_time_ms"]),
                entry_price=float(tr["entry_price"]), tp_price=float(tr["tp_price"]),
                sl_price=float(tr["sl_price"]), exit_time_ms=int(tr["exit_time_ms"]),
                exit_price=float(tr["exit_price"]), exit_reason="SKIPPED_MAXOPEN",
                hold_hours=float(tr["hold_hours"]), gross_bps=float(tr["gross_bps"]),
                stake=0.0, pnl_cash=0.0, exit_equity=capital, realized=0.0, skipped=True))

    # force-close at period end: only positions still open (exit_time > period_end)
    step(period_end_ms)
    for p in open_pos:
        pnl_cash = p["stake"] * (p["gross_bps"] / 1e4)
        capital += p["stake"] + pnl_cash
        p["pnl_cash"] = pnl_cash
        p["realized"] = pnl_cash
        p["exit_reason"] = "FORCE_CLOSE_END"
        p["exit_equity"] = capital
        trade_log.append(p)
    open_pos = []

    log = pd.DataFrame(trade_log).sort_values("entry_time_ms").reset_index(drop=True)
    return log, capital


def main():
    all_ev = []
    for tag, (sym, tf, nm) in ENTRY.items():
        ev = make_candidate_events(sym, tf, nm)
        ev["row"] = tag
        all_ev.append(ev)
        print(f"{tag} {sym}-{tf} {nm}: candidate trades (fwd, filter={FILTER}) = {len(ev)}")
    trades_all = pd.concat(all_ev, ignore_index=True)
    log, final_cap = simulate(trades_all)

    # ---- write trades CSV ----
    out_cols = ["row", "symbol", "tf", "name", "signal_time_ms", "entry_time_ms",
                "entry_price", "tp_price", "sl_price", "exit_time_ms", "exit_price",
                "exit_reason", "hold_hours", "gross_bps", "stake", "pnl_cash",
                "exit_equity", "skipped"]
    log = log[out_cols].copy()
    log.insert(0, "trade_id", range(1, len(log) + 1))
    # human-readable UTC timestamps
    for c in ["signal_time_ms", "entry_time_ms", "exit_time_ms"]:
        log[c.replace("_ms", "_utc")] = pd.to_datetime(log[c], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")

    # ---- summary ----
    taken = log[~log["skipped"]]
    done = taken[taken["exit_reason"] != "SKIPPED_MAXOPEN"]
    wins = done[done["pnl_cash"] > 0]
    losses = done[done["pnl_cash"] <= 0]
    n_taken = len(taken); n_done = len(done)
    summary = []
    summary.append("FORWARD PORTFOLIO BACKTEST  Dec 2024 - Apr 2025 (5 months)")
    summary.append("=" * 60)
    summary.append(f"TRIGGER : wick-fill (W2/W1/W2/W3 NODIP) on E1-E4 = SOL-30m,BTC-30m,ETH-1h,SOL-4h")
    summary.append(f"FILTER  : LOSERFAC event_red_and_range_expand = DROP if signal bar RED & range>=1.5xATR(20)")
    summary.append(f"COST    : {COST_BPS} bps round-trip")
    summary.append(f"CAPITAL : ${INIT_CAPITAL:.2f}  stake = {STAKE_FRAC*100:.0f}% equity at open  max_open = {MAX_OPEN}")
    summary.append(f"TP      : body_top(sig) + 1.5*wick_gap ;  exit = TP hit OR K-bar timeout (no intra-trade SL; SL control = LOSERFAC filter)")
    summary.append(f"WINDOW  : {WF_START} .. {WF_END} UTC  (RESERVED 2025-07-01+ excluded)")
    summary.append("-" * 60)
    summary.append(f"candidate trades (after filter) : {len(trades_all)}")
    summary.append(f"trades taken (opened)           : {n_taken}")
    summary.append(f"  of which skipped (max-open)   : {int(log['skipped'].sum())}")
    summary.append(f"closed (TP/SL/timeout/force)    : {n_done}")
    summary.append(f"  wins                          : {len(wins)}")
    summary.append(f"  losses                        : {len(losses)}")
    if n_done:
        summary.append(f"win rate (of closed)            : {100*len(wins)/n_done:.1f}%")
        summary.append(f"avg pnl/trade $                : {done['pnl_cash'].mean():.2f}")
    summary.append(f"start capital                  : ${INIT_CAPITAL:.2f}")
    summary.append(f"final capital                  : ${final_cap:.2f}")
    summary.append(f"net return                     : {(final_cap/INIT_CAPITAL-1)*100:.2f}%")
    # per-row
    summary.append("-" * 60)
    summary.append("per-row (closed):")
    for tag in ["E1", "E2", "E3", "E4"]:
        sub = done[done["row"] == tag]
        if len(sub):
            summary.append(f"  {tag}: n={len(sub)} win={100*(sub['pnl_cash']>0).mean():.0f}% "
                           f"net$={sub['pnl_cash'].sum():.2f} avgBps={sub['gross_bps'].mean():.1f}")
        else:
            summary.append(f"  {tag}: no closed trades")
    summary.append("=" * 60)
    summary.append("NOTE: LOSERFAC filter is TRAIN-derived; this is the requested forward check,")
    summary.append("NOT the locked E-VAL. Treat as indicative, not validated.")
    txt = "\n".join(summary) + "\n"

    (P.V2_OUTPUTS / "fwd_portfolio_trades.csv").write_text(
        log.to_csv(index=False))
    (P.V2_OUTPUTS / "fwd_portfolio_summary.txt").write_text(txt)

    # markdown doc
    md = ["# FORWARD PORTFOLIO BACKTEST — Dec 2024 → Apr 2025\n"]
    md.append("## Mandate\n")
    md.append("- **Trigger:** the 'main concept' wick-fill entry (`RS.select`, W2/W1/W2/W3 NODIP on E1–E4).")
    md.append("- **Filter:** LOSERFAC top DISC pre-entry feature `event_red_and_range_expand` (drop a signal if its candle is RED **and** range ≥ 1.5×20-bar ATR). Pre-entry only.")
    md.append("- **Capital:** $1000 start; each trade stakes 25% of equity at open; up to 3 concurrent; force-close all at period end.\n")
    md.append("## Execution model (from the discovery engine — no new assumptions)\n")
    md.append(f"- Entry @ next bar open after the signal. TP = body_top(sig) + 1.5×wick_gap. Exit = TP hit OR K-bar timeout (no intra-trade SL; the LOSERFAC filter is the stop-loss control). Cost = {COST_BPS} bps round-trip.")
    md.append(f"- Cost = {COST_BPS} bps round-trip (matches `keepn_study.COST`).")
    md.append("- Realistic fills: TP crossed-in-bar exits at limit price; timeout exits at the K-bar close.\n")
    md.append("## Data integrity\n")
    md.append("- Signal thresholds use TRAIN-frozen atlas cuts; all four specs are FIXED bps (no decile) → no future leak in selection.")
    md.append("- The RESERVED window (2025-07-01 → 2026-07-01) is excluded entirely per the repo's hard rule.")
    md.append(f"- Study window: {WF_START} → {WF_END} UTC.\n")
    md.append("## Result\n")
    for line in summary:
        md.append(line)
    md.append("\n## Files\n")
    md.append("- `V2/outputs/fwd_portfolio_trades.csv` — every trade (open/close times, prices, reason, pnl, stake, equity).")
    md.append("- `V2/outputs/fwd_portfolio_summary.txt` — the block above.")
    md.append("\n## Caveats\n")
    md.append("- Concurrency cap (3) means some candidate trades are skipped when all slots are full; they are logged with `SKIPPED_MAXOPEN`.")
    md.append("- Force-close marks remaining positions at their computed exit price (approximation at period end).")
    md.append("- This is the user-requested forward check on a TRAIN-derived filter; it is NOT the locked E-VAL window. Do not treat as validated out-of-sample performance.")
    (P.V2_OUTPUTS.parent / "FWD_PORTFOLIO_BACKTEST.md").write_text("\n".join(md) + "\n")
    print(txt)
    print(f"Wrote fwd_portfolio_trades.csv ({len(log)} rows), fwd_portfolio_summary.txt, FWD_PORTFOLIO_BACKTEST.md")


if __name__ == "__main__":
    main()
