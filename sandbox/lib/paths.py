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

# Repo root = sandbox/ (this file is sandbox/lib/paths.py -> parents[1])
ROOT = Path(__file__).resolve().parents[1]
SANDBOX = ROOT
OUTPUTS = SANDBOX / "outputs"
ATLAS_DIR = Path(r"C:\Users\A\Bullish-Fill-Wick-SL-Control\V2\outputs\atlas")
RESULTS = SANDBOX / "results"
LOGS = SANDBOX / "logs"

# Raw klines: resolved via env so the absolute path is never hardcoded in source.
# Default to the known Download location; override with BULLISH_WICK_RAW_DIR.
RAW_DIR = Path(os.environ.get(
    "BULLISH_WICK_RAW_DIR",
    r"C:\Users\A\Downloads\opencode-bybit"
)).resolve()
