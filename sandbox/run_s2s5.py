"""
Sandbox harness — runs V3 S2 (entry grid), S3 (integrity), S4 (exit study), S5 (menu)
for SOLUSDT ONLY, with ALL outputs redirected into the sandbox.

Isolation guarantees:
  * lib.paths.V2_OUTPUTS  ->  <sandbox>/outputs   (captures every *_study / loser_* / exit_* write)
  * BULLISH_WICK_RAW_DIR  ->  real read-only raw klines (no copy, no mutation)
  * src/lib copied into <sandbox>/lib; sys.path points there, NOT the repo src/
  * The repo's results/, V2/outputs/, FROZEN_CANDIDATE.md, burn registry are NEVER touched.

This harness does S0-S5 only. It does NOT fire E-VAL (one-shot, owner FIRE required).
"""
import os, sys, json, io, contextlib, traceback, datetime
from pathlib import Path

SANDBOX = Path(__file__).resolve().parent
OUT = SANDBOX / "outputs"
RAW = Path(r"C:/Users/A/Downloads/opencode-bybit")   # read-only input
OUT.mkdir(parents=True, exist_ok=True)

# 1) Point the stats/paths modules at the sandbox BEFORE any script imports them.
os.environ["BULLISH_WICK_RAW_DIR"] = str(RAW)

# 2) Make the sandbox lib the ONLY lib on path (repo src/ is not imported).
sys.path.insert(0, str(SANDBOX / "lib"))
sys.path.insert(0, str(SANDBOX / "scripts"))

import lib.paths as P
# Redirect every write that targets P.V2_OUTPUTS into the sandbox.
P.V2_OUTPUTS = OUT
P.ATLAS_DIR = OUT / "atlas"
P.RESULTS = OUT / "results"
for _d in (P.V2_OUTPUTS, P.ATLAS_DIR, P.RESULTS):
    _d.mkdir(parents=True, exist_ok=True)

ASSET = "SOLUSDT"
TFS = ["30m", "1h", "4h"]   # 1D optional; run the three with SOL data present in raw dir

def run_stage(name, fn, *args, **kw):
    log = SANDBOX / "logs" / f"{name}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    print(f"\n=== STAGE {name}  {datetime.datetime.now().isoformat(timespec='seconds')} ===")
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            fn(*args, **kw)
        log.write_text(buf.getvalue())
        print(f"  OK  -> {log.name} ({len(buf.getvalue())} chars)")
        return True
    except Exception as e:
        msg = buf.getvalue() + "\n\n>>> EXCEPTION:\n" + traceback.format_exc()
        log.write_text(msg)
        print(f"  FAIL -> {log.name}\n  {type(e).__name__}: {e}")
        return False

# Import stage scripts AFTER redirect is in place.
import exit_anatomy, keepn_study, loser_factor, loser_factor_ext, exit_phaseb

# ---- S1 (light): atlas cuts already TRAIN-frozen in repo; we recompute anatomy per TF ----
# S2: entry grid (keepn_study.main) — measures all E1-E4 reference cells + writes keepn_study.csv
def s2_entry_grid():
    keepn_study.main()

# S3: integrity battery (loser_factor + loser_factor_ext) -> loser_factor*.csv
def s3_integrity():
    loser_factor.main()
    loser_factor_ext.main()

# S4: exit study (exit_anatomy Phase A + exit_phaseb Phase B)
# exit_anatomy has main(); exit_phaseb runs on import (module-level SL study).
def s4_exit_study():
    exit_anatomy.main()        # default ASSET_TFS scans; we limit via argv below
    import exit_phaseb         # executes Phase B SL policy study on import

# S5: menu assembly — template-generate MENU.md from the CSVs we just wrote.
def s5_menu():
    csvs = sorted(str(p) for p in OUT.glob("*.csv"))
    lines = ["# MENU.md (SANDBOX — V3 S5 deliverable, SOLUSDT)", "",
             f"Generated: {datetime.datetime.now().isoformat(timespec='seconds')}",
             "Asset: SOLUSDT  |  Timeframes: " + ", ".join(TFS),
             "All 32 entry cells + exit policies delivered. NO recommendation (R1).", "",
             "## Source artifacts (in sandbox/outputs)", ""]
    for c in csvs:
        lines.append(f"- {Path(c).name}")
    lines += ["", "## Owner action", "- Pick ONE spec (asset+TF+row+policy).",
              "- Reply with the literal word FIRE for that spec to run one-shot E-VAL."]
    (OUT / "MENU.md").write_text("\n".join(lines))

# Run S2-S5. S4's exit_anatomy.main() uses ASSET_TFS default; restrict to SOL via monkeypatch.
def _limit_sol():
    exit_anatomy.ASSET_TFS = [(ASSET, tf) for tf in TFS]

if __name__ == "__main__":
    results = {}
    try:
        results["S2_entry_grid"] = run_stage("S2_entry_grid", s2_entry_grid)
        results["S3_integrity"]  = run_stage("S3_integrity", s3_integrity)
        _limit_sol()
        results["S4_exit_study"] = run_stage("S4_exit_study", s4_exit_study)
        results["S5_menu"]       = run_stage("S5_menu", s5_menu)
    except Exception as e:
        print("TOP-LEVEL EXCEPTION:", repr(e))
        traceback.print_exc()
    (SANDBOX / "run_summary.json").write_text(json.dumps(results, indent=2))
    print("\n=== SUMMARY ===", flush=True)
    for k, v in results.items():
        print(f"  {k}: {'OK' if v else 'FAIL'}", flush=True)
    print(f"Outputs: {OUT}", flush=True)
