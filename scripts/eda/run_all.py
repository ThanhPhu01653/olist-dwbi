"""Run every P1 EDA script in order (python scripts/eda/run_all.py). Needs the olist_full database loaded."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = ["profile.py", "data_quality.py", "distributions.py", "correlations.py", "funnel.py", "design_questions.py", "excel_export.py",
           "source_profile.py", "p8_outliers.py", "p8_association.py", "p8_seasonality.py", "p8_describe.py", "p8_dictionary.py"]

for name in SCRIPTS:
    t0 = time.perf_counter()
    print(f"== {name}")
    subprocess.run([sys.executable, str(HERE / name)], check=True)
    print(f"   done in {time.perf_counter() - t0:.1f}s")
