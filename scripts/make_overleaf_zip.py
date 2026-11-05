"""Pack report/ into report_overleaf.zip (project root, NOT committed) for upload to Overleaf.   python scripts/make_overleaf_zip.py
Contains main.tex, preamble.tex, refs.bib, .latexmkrc, chapters/, tables/, code/, figures/ (no build files)."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "report"
out = ROOT / "report_overleaf.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(REP.rglob("*")):
        if p.is_dir() or p.suffix in {".aux", ".log", ".toc", ".lof", ".lot", ".bbl", ".blg", ".xdv", ".fls", ".fdb_latexmk", ".out", ".pdf", ".zip"} or p.name == "README.md":
            continue
        z.write(p, p.relative_to(REP).as_posix())
print(f"{out.name}: {out.stat().st_size / 1024 / 1024:.1f} MB, {len(zipfile.ZipFile(out).namelist())} files")
