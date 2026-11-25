"""Pack report/ into report_overleaf.zip (project root, NOT committed) for upload to Overleaf.   python scripts/make_overleaf_zip.py
Contains main.tex, preamble.tex, refs.bib, .latexmkrc, chapters/, tables/, code/ and ONLY the figures the report uses (Overleaf takes at most 180 files per upload;
this script stops above 175)."""
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "report"
out = ROOT / "report_overleaf.zip"
SKIP = {".aux", ".log", ".toc", ".lof", ".lot", ".bbl", ".blg", ".xdv", ".fls", ".fdb_latexmk", ".out", ".pdf", ".zip"}
IMG = re.compile(r"[{\[ ,]([\w\-./]+\.(?:png|jpg|jpeg|pdf))(?=[}\], ])")
used = set()
for p in REP.rglob("*.tex"):
    used |= {m.group(1) for m in IMG.finditer(p.read_text(encoding="utf-8", errors="ignore"))}
files = {}
for p in sorted(REP.rglob("*")):
    if p.is_dir() or p.suffix in SKIP or p.name == "README.md" or p.name.startswith("build"):
        continue
    rel = p.relative_to(REP)
    if rel.parts[0] == "figures" and p.name not in used and rel.as_posix() not in used:
        continue
    files[rel.as_posix()] = p
n = len(files)
print(f"{out.name}: {n} file; " + ", ".join(f"{d} {c}" for d, c in sorted(Counter(k.split('/')[0] if '/' in k else '(gốc)' for k in files).items())))
if n > 175:
    sys.exit(f"LỖI: {n} file, quá 175")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for arc, p in files.items():
        z.write(p, arc)
print(f"   {out.stat().st_size / 1024 / 1024:.1f} MB")
