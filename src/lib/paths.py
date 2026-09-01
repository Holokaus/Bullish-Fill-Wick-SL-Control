"""Single source of path resolution for the Bullish-Fill-Wick project.

Track 2 (V2 / OPERATION FILLPOINT, Bybit USDT-perp) is the primary pipeline.
All scripts import ROOT/DATA/RESULTS/... from here so nothing hardcodes
C:\\Users\\A\\... and the project is reproducible on any machine.

The raw Bybit klines physically live in the user's Downloads folder (a paper
trail that survived the F-drive loss). We resolve that via an env override
BULLISH_WICK_RAW_DIR so the path is not hardcoded in source.
"""
from pathlib import Path
import os

# Repo root = Bullish-Fill-Wick/ (this file is src/lib/paths.py -> parents[2])
ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "V2"
SRC = ROOT / "src"
LIB = SRC / "lib"

# Primary pipeline outputs (Track 2 / V2)
V2_OUTPUTS = V2 / "outputs"
ATLAS_DIR = V2_OUTPUTS / "atlas"
RESULTS = ROOT / "results"
V2_SCRIPTS = V2 / "scripts"
LOGS = V2 / "logs"

# Track-1 artifacts (retired, preserved for audit only)
TRACK1_RESULTS = RESULTS
TRACK1_REPORTS = ROOT / "reports"
TRACK1_DOCS = ROOT / "docs"

# Raw klines: resolved via env so the absolute path is never hardcoded in source.
# Default to the known Download location; override with BULLISH_WICK_RAW_DIR.
RAW_DIR = Path(os.environ.get(
    "BULLISH_WICK_RAW_DIR",
    r"C:\Users\A\Downloads\opencode-bybit"
)).resolve()

LOCKBOX_DIR = V2 / "data_lockbox"

# SHA / audit provenance dir
PROVENANCE = RESULTS / "provenance"

for _d in (V2_OUTPUTS, ATLAS_DIR, RESULTS, LOGS, LOCKBOX_DIR, PROVENANCE, LIB):
    _d.mkdir(parents=True, exist_ok=True)
