"""Time `lualatex main.tex` (one pass, font cache warm) on each person's zip, without .latexmkrc.   python scripts/do_thoi_gian_zip.py [--nhap]
Unzips into a temp folder, runs a warm-up pass is NOT done (the first pass is timed after one throw-away run of nguoi1), prints seconds and pages."""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ["nguoi1", "nguoi2", "nguoi3", "nguoi4", "phu"]


def run(key: str, nhap: bool | None) -> tuple[float, int, int, str]:
    tmp = Path(tempfile.mkdtemp(prefix=f"zip_{key}_"))
    try:
        zipfile.ZipFile(ROOT / f"slides_overleaf_{key}.zip").extractall(tmp)
        (tmp / ".latexmkrc").unlink(missing_ok=True)
        if nhap is not None:
            m = (tmp / "main.tex").read_text(encoding="utf-8")
            if nhap and "\\def\\NHAP{}" not in m:
                m = m.replace("\\def\\CHIPHAN", "\\PassOptionsToPackage{draft}{graphicx}\n\\def\\NHAP{}\n\\def\\CHIPHAN", 1)
            if not nhap:
                m = m.replace("\\PassOptionsToPackage{draft}{graphicx}\n", "").replace("\\def\\NHAP{}\n", "")
            (tmp / "main.tex").write_text(m, encoding="utf-8")
        t0 = time.time()
        r = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], cwd=tmp, capture_output=True, text=True, encoding="utf-8", errors="replace")
        dt = time.time() - t0
        log = (tmp / "main.log").read_text(encoding="utf-8", errors="replace") if (tmp / "main.log").exists() else ""
        pages = re.search(r"Output written on main.pdf \((\d+) pages", log)
        return dt, r.returncode, int(pages.group(1)) if pages else 0, ("Overfull" if "Overfull \\vbox" in log else "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    mode = {"--nhap": True, "--that": False}.get(sys.argv[1] if len(sys.argv) > 1 else "", None)
    run("nguoi1", mode)  # warm up fonts
    for k in KEYS:
        dt, rc, pg, warn = run(k, mode)
        print(f"{k}: {dt:.1f} s, rc={rc}, {pg} trang {warn}")
