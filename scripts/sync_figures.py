"""Copy figures/*.png to report/figures and slides/figures when missing or newer (the report and slides keep self-contained copies for Overleaf).
Does not overwrite a file in report/figures or slides/figures that is NEWER than the one in figures/ (so a hand-redrawn figure is not lost).
   python scripts/sync_figures.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "figures"
copied = 0
for dst in (ROOT / "report" / "figures", ROOT / "slides" / "figures"):
    dst.mkdir(exist_ok=True)
    for f in SRC.glob("*.png"):
        t = dst / f.name
        if not t.exists() or f.stat().st_mtime > t.stat().st_mtime:
            shutil.copy2(f, t)
            copied += 1
print("copied", copied, "files")
