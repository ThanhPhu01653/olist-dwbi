"""Merge a person's work (the zip downloaded from Overleaf: Menu -> Download -> Source) back into slides/.

    python scripts/ghep_tex_nop.py nguoi2 duong/dan/slides_overleaf_nguoi2.zip            # extract + show what would change (nothing is copied)
    python scripts/ghep_tex_nop.py nguoi2 duong/dan/slides_overleaf_nguoi2.zip --ap-dung  # copy into slides/sections and slides/figures

Steps: unzip into tex-nop/<nguoi>/ ; compare only that person's section files (scripts/make_slides_zip.py PEOPLE) and NEW figures
(a figure with a name that is not yet in slides/figures; an existing figure with different bytes is listed as "đổi", copied only with --ap-dung).
Other files in the zip (khung.tex, main.tex, theme .sty, .latexmkrc) are ignored, so nobody can change the theme by accident.
Not run yet: prepared for the submission round (tex-nop/ is not committed).
"""
from __future__ import annotations

import filecmp
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from make_slides_zip import PEOPLE  # noqa: E402

SL = ROOT / "slides"


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[1] not in PEOPLE:
        sys.exit(__doc__ + "\nnguoi một trong: " + ", ".join(PEOPLE))
    who, zpath = sys.argv[1], Path(sys.argv[2])
    apply = "--ap-dung" in sys.argv
    dest = ROOT / "tex-nop" / who
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(zpath) as z:
        z.extractall(dest)
    print(f"đã giải nén vào {dest.relative_to(ROOT)}")
    changed = 0
    for s in PEOPLE[who]:
        src, dst = dest / "sections" / f"{s}.tex", SL / "sections" / f"{s}.tex"
        if not src.exists():
            print(f"  THIẾU  sections/{s}.tex (không có trong zip)")
            continue
        if dst.exists() and filecmp.cmp(src, dst, shallow=False):
            print(f"  giống  sections/{s}.tex")
            continue
        changed += 1
        print(f"  ĐỔI    sections/{s}.tex")
        if apply:
            shutil.copy2(src, dst)
    figdir = dest / "figures"
    if figdir.exists():
        for src in sorted(p for p in figdir.rglob("*") if p.is_file()):
            rel = src.relative_to(figdir)
            dst = SL / "figures" / rel
            if not dst.exists():
                tag = "MỚI "
            elif not filecmp.cmp(src, dst, shallow=False):
                tag = "ĐỔI "
            else:
                continue
            changed += 1
            print(f"  {tag}   figures/{rel.as_posix()}")
            if apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
    print(f"{changed} file thay đổi" + (" (đã chép vào slides/)" if apply else " (chưa chép; thêm --ap-dung để chép)"))


if __name__ == "__main__":
    main()
