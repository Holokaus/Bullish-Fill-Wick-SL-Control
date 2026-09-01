# -*- coding: utf-8 -*-
# ============================================================================
# EXPERIMENT: E1 = SOL-30m, W2_NODIP (>=45 bps), P4_timeSL_P95 time stop K=42h
#
# This is a NEW experiment. It does NOT touch the earlier runs
# (fwd_portfolio_trades.csv / fwd_portfolio_sol4h_*) -- those stay as-is.
#
# TRIGGER  : wick-fill entry (RS.select) on SOL-30m W2_NODIP only.  Color-agnostic.
#            (E1 from the frozen menu; W2_NODIP = wick >= 45 bps, no dip filter.)
# TIME STOP: P4_timeSL_P95 = K = 42h (winners' time-to-fill P95 in SL_STUDY).
#            On 30m that is 84 bars.  Exit = TP hit OR K-bar timeout.
#            (P4 is a TIME stop -- no intra-trade wick SL.)
# FILTER   : optional LOSERFAC top DISC pre-entry feature `event_red_and_range_expand`
#            (drop signal if candle RED and range >= 1.5 x 20-bar ATR).  Run 2 only.
#
# CAPITAL  : $1000 start. Per trade = 25% of equity at OPEN. Max 3 concurrent.
#            Force-close ALL open positions at the period end.
#
# EXECUTION MODEL:
#   entry  @ next bar open (eb = sig+1)
#   TP     = body_top(sig) + 1.5 x wick_gap(sig)
#   exit   = TP hit OR K=84-bar (42h) timeout.  cost = 15 bps round-trip.
#
# WINDOW   : 2024-12-01 00:00 .. 2025-04-30 23:59:59 UTC (RESERVED 2025-07-01+ excluded)
#
# OUTPUTS (distinct names, both runs):
#   fwd_portfolio_e1_p4_nofilter_trades.csv / _summary.txt / .md
#   fwd_portfolio_e1_p4_withfilter_trades.csv / _summary.txt / .md
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
WICK_MULT = 1.5          # TP = body_top + 1.5*wick_gap

WF_START = pd.Timestamp("2024-12-01 00:00:00", tz="UTC")
WF_END   = pd.Timestamp("2025-04-30 23:59:59", tz="UTC")
WF_START_MS = int(WF_START.value // 10**6)   # raw 'time' is in MILLISECONDS
WF_END_MS   = int(WF_END.value // 10**6)

ENTRY = {
    "E1": ("SOLUSDT", "30m", "W2_NODIP"),
}
TF_H = {"30m": 0.5}
K_H  = {"30m": 84}     # 42h wall-clock horizon on 30m (= 84 bars)


def load_full(symbol, tf):
    fn = P.RAW_DIR / f"{symbol}-FUTURES-2022-2026-{tf}.csv"
    raw = pd.read_csv(fn)
    low = {c.strip().strip('"').lower(): c for c in raw.columns}
    inv = {v: k for k, v in low.items()}
    raw = raw.rename(columns=inv)[["time", "open", "high", "low", "close", "volume"]].apply(pd.to_numeric)
    raw = raw.drop_duplicates("time").sort_values("time").reset_index(drop=True)
    return raw


def make_candidate_events(symbol, tf, name, filt):
    bars = load_full(symbol, tf)
    times = bars["time"].values.astype("int64")
    in_win = (times >= WF_START_MS) & (times <= WF_END_MS)
    feats = RS.build_features(bars, tf, legacy=False, symbol=symbol)
    spec = RS.get_spec(name, tf, legacy=False)
    sig_all, eb_all = RS.select(spec, feats)
    O, H, L, C = feats["O"], feats["H"], feats["L"], feats["C"]

    d = pd.DataFrame({"o": O, "h": H, "l": L, "c": C, "v": bars["volume"].values.astype(float)})
    rng = d["h"] - d["l"]
    tr_ = np.maximum.reduce([rng.values,
                             (d["h"] - d["c"].shift(1)).abs().values,
                             (d["l"] - d["c"].shift(1)).abs().values])
    atr = pd.Series(tr_).rolling(20).mean().values
    red = d["c"] < d["o"]
    range_expand = rng >= 1.5 * atr
    pass_filter = ~(red & range_expand)            # LOSERFAC filter

    ev_rows = []
    for s, e in zip(sig_all, eb_all):
        if not in_win[s]:
            continue
        if filt and not pass_filter[s]:
            continue
        bt = O[e]
        wg = H[s] - np.maximum(O[s], C[s])
        if not np.isfinite(bt) or wg <= 0:
            continue
        tp = np.maximum(O[s], C[s]) + WICK_MULT * wg
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
    trades_all = trades_all.sort_values("entry_time_ms").reset_index(drop=True)
    capital = INIT_CAPITAL
    equity = [capital]; eq_times = [WF_START.value]
    open_pos = []; trade_log = []; period_end_ms = WF_END_MS
    i = 0; n = len(trades_all)

    def step(t_ms):
        nonlocal capital, open_pos
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

    while i < n:
        cur_entry = int(trades_all.iloc[i]["entry_time_ms"])
        step(cur_entry)
        while i < n and int(trades_all.iloc[i]["entry_time_ms"]) == cur_entry and len(open_pos) < MAX_OPEN:
            tr = trades_all.iloc[i]; i += 1
            if len(open_pos) >= MAX_OPEN:
                trade_log.append(dict(
                    row=tr["row"], symbol=tr["symbol"], tf=tr["tf"], name=tr["name"],
                    signal_time_ms=int(tr["signal_time_ms"]), entry_time_ms=int(tr["entry_time_ms"]),
                    entry_price=float(tr["entry_price"]), tp_price=float(tr["tp_price"]),
                    sl_price=float(tr["sl_price"]), exit_time_ms=int(tr["exit_time_ms"]),
                    exit_price=float(tr["exit_price"]), exit_reason="SKIPPED_MAXOPEN",
                    hold_hours=float(tr["hold_hours"]), gross_bps=float(tr["gross_bps"]),
                    stake=0.0, pnl_cash=0.0, exit_equity=capital, realized=0.0, skipped=True))
                continue
            stake = round(capital * STAKE_FRAC, 2)
            capital -= stake
            p = dict(tr.to_dict())
            p["stake"] = stake
            p["pnl_cash"] = stake * (float(tr["gross_bps"]) / 1e4)
            p["realized"] = 0.0
            p["skipped"] = False
            open_pos.append(p)
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


def run(tag_suffix, filt):
    all_ev = []
    for t, (sym, tf, nm) in ENTRY.items():
        ev = make_candidate_events(sym, tf, nm, filt)
        ev["row"] = t
        all_ev.append(ev)
        print(f"[{tag_suffix}] {t} {sym}-{tf} {nm}: candidates (filter={filt}) = {len(ev)}")
    trades_all = pd.concat(all_ev, ignore_index=True)
    log, final_cap = simulate(trades_all)

    out_cols = ["row", "symbol", "tf", "name", "signal_time_ms", "entry_time_ms",
                "entry_price", "tp_price", "sl_price", "exit_time_ms", "exit_price",
                "exit_reason", "hold_hours", "gross_bps", "stake", "pnl_cash",
                "exit_equity", "skipped"]
    log = log[out_cols].copy()
    log.insert(0, "trade_id", range(1, len(log) + 1))
    for c in ["signal_time_ms", "entry_time_ms", "exit_time_ms"]:
        log[c.replace("_ms", "_utc")] = pd.to_datetime(log[c], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")

    taken = log[~log["skipped"]]
    done = taken[taken["exit_reason"] != "SKIPPED_MAXOPEN"]
    wins = done[done["pnl_cash"] > 0]; losses = done[done["pnl_cash"] <= 0]
    n_taken = len(taken); n_done = len(done)
    summary = []
    summary.append(f"E1 P4_timeSL_P95 EXPERIMENT  Dec 2024 - Apr 2025  [{tag_suffix}]")
    summary.append("=" * 64)
    summary.append(f"TRIGGER : wick-fill W2_NODIP on SOL-30m ONLY (E1), wick>=45 bps")
    summary.append(f"TIME STOP: P4_timeSL_P95 K=42h (84 bars) ; exit = TP hit OR K timeout ; no intra-trade SL")
    summary.append(f"FILTER  : {'LOSERFAC event_red_and_range_expand (drop RED & range>=1.5xATR)' if filt else 'NONE (plain trigger)'}")
    summary.append(f"COST    : {COST_BPS} bps round-trip")
    summary.append(f"CAPITAL : ${INIT_CAPITAL:.2f}  stake = {STAKE_FRAC*100:.0f}% equity at open  max_open = {MAX_OPEN}")
    summary.append(f"WINDOW  : {WF_START} .. {WF_END} UTC  (RESERVED 2025-07-01+ excluded)")
    summary.append("-" * 64)
    summary.append(f"candidate trades (after filter) : {len(trades_all)}")
    summary.append(f"trades taken (opened)           : {n_taken}")
    summary.append(f"  of which skipped (max-open)   : {int(log['skipped'].sum())}")
    summary.append(f"closed (TP/timeout/force)       : {n_done}")
    summary.append(f"  wins                          : {len(wins)}")
    summary.append(f"  losses                        : {len(losses)}")
    if n_done:
        summary.append(f"win rate (of closed)            : {100*len(wins)/n_done:.1f}%")
        summary.append(f"avg pnl/trade $                : {done['pnl_cash'].mean():.2f}")
    summary.append(f"start capital                  : ${INIT_CAPITAL:.2f}")
    summary.append(f"final capital                  : ${final_cap:.2f}")
    summary.append(f"net return                     : {(final_cap/INIT_CAPITAL-1)*100:.2f}%")
    summary.append("=" * 64)
    txt = "\n".join(summary) + "\n"

    trades_csv = f"fwd_portfolio_e1_p4_{tag_suffix}_trades.csv"
    summ_txt = f"fwd_portfolio_e1_p4_{tag_suffix}_summary.txt"
    md_file = f"FWD_PORTFOLIO_E1_P4_{tag_suffix.upper()}.md"
    (P.V2_OUTPUTS / trades_csv).write_text(log.to_csv(index=False))
    (P.V2_OUTPUTS / summ_txt).write_text(txt)

    md = [f"# E1 P4_timeSL_P95 EXPERIMENT — {tag_suffix}\n"]
    md.append("## Mandate\n")
    md.append("- **Trigger:** wick-fill entry (`RS.select`, W2_NODIP) on **SOL-30m only (E1)**, wick ≥ 45 bps. Color-agnostic.")
    md.append("- **Time stop:** `P4_timeSL_P95` = K = 42h (84 bars on 30m). Exit = TP hit OR K-bar timeout. No intra-trade wick SL.")
    md.append(f"- **Filter:** {'LOSERFAC `event_red_and_range_expand` (drop if candle RED & range ≥ 1.5×20-bar ATR).' if filt else 'NONE — plain trigger only.'}")
    md.append("- **Capital:** $1000 start; 25% of equity per trade at open; max 3 concurrent; force-close at period end.\n")
    md.append("## Execution model\n")
    md.append(f"- Entry @ next bar open. TP = body_top(sig) + 1.5×wick_gap. Exit = TP hit OR K=84-bar (42h) timeout. Cost {COST_BPS} bps round-trip.")
    md.append("- This is an EXPERIMENT reusing the `P4_timeSL_P95` policy (the one E1 row SL_STUDY flagged VIABLE=True).\n")
    md.append("## Data integrity\n")
    md.append("- W2_NODIP uses a FIXED 45 bps threshold → leak-free selection.")
    md.append("- RESERVED window (2025-07-01 → 2026-07-01) excluded per repo hard rule.")
    md.append(f"- Window: {WF_START} → {WF_END} UTC.\n")
    md.append("## Result\n")
    for line in summary:
        md.append(line)
    md.append("\n## Files\n")
    md.append(f"- `V2/outputs/{trades_csv}` — every trade.")
    md.append(f"- `V2/outputs/{summ_txt}` — summary above.\n")
    md.append("## Caveats\n")
    md.append("- Concurrency cap (3) may skip candidates (logged SKIPPED_MAXOPEN).")
    md.append("- Forward check on TRAIN-derived context; not the locked E-VAL. Indicative only.")
    (P.V2_OUTPUTS.parent / md_file).write_text("\n".join(md) + "\n")
    print(txt)
    print(f"Wrote {trades_csv} ({len(log)} rows), {summ_txt}, {md_file}\n")
    return final_cap


def main():
    run("nofilter", filt=False)
    run("withfilter", filt=True)


if __name__ == "__main__":
    main()
