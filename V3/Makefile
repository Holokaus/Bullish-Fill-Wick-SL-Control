# Bullish-Fill-Wick / OPERATION FILLPOINT pipeline
# Track 2 (V2, Bybit USDT-perp). One `make all` runs the in-scope pass (stops at FROZEN_CANDIDATE).
# E-VAL / E-LOCKBOX / Section 6 are intentionally NOT wired here (directive s13.4).

PY := python
SRC := src
V2 := V2

.PHONY: all data atlas economics stops system report test clean

all: atlas economics stops system report

# fetch + QC (raw klines already on disk; assert holdout exclusion)
data:
	$(PY) $(SRC)/fetch_data.py

# conditional atlas on TRAIN (writes atlas_cuts.json + parquet event tables)
atlas:
	$(PY) $(V2)/scripts/w4a_atlas.py

# economic layer on TRAIN (W4c-equivalent, frozen-cost)
economics:
	$(PY) $(V2)/scripts/w4c_economics.py

# stop study on TRAIN (W6-equivalent, corrected fee stack)
stops:
	$(PY) $(V2)/scripts/w6_stop_study.py

# flagship corrected-cost study + FDR + candidate metrics (W7)
system:
	$(PY) $(V2)/scripts/w7_flagship_study.py
	$(PY) $(V2)/scripts/w7b_candidate_metrics.py

# META_VERDICT + figures (docs already authored; regenerate figures if needed)
report:
	$(PY) $(SRC)/make_figure.py || true

# unit tests (simulator + canonical stats + identity/freeze gates)
test:
	$(PY) -m pytest tests -q

clean:
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
