"""Pack slides/ (with the HUST theme) into slides_overleaf.zip at the project root (NOT committed).   python scripts/make_slides_zip.py
Contains main.tex, slides-notes.tex, .latexmkrc, sections/, figures/ and hust-theme/ (no PDF or build files)."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SL = ROOT / "slides"
out = ROOT / "slides_overleaf.zip"
skip = {".aux", ".log", ".toc", ".nav", ".snm", ".out", ".xdv", ".fls", ".fdb_latexmk", ".pdf", ".zip", ".vrb", ".bbl", ".blg", ".bcf", ".run.xml"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(SL.rglob("*")):
        if p.is_dir() or p.suffix in skip or p.name in {"README.md", "slide-script.md"} or p.name.startswith("build"):
            continue
        z.write(p, p.relative_to(SL).as_posix())
print(f"{out.name}: {out.stat().st_size / 1024 / 1024:.1f} MB, {len(zipfile.ZipFile(out).namelist())} files")
