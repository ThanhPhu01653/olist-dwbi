"""Pack the slides for Overleaf / MiKTeX (zips are NOT committed).   python scripts/make_slides_zip.py [--nhap-nguoi on|off]

  slides_overleaf.zip                              the whole deck (main.tex + all sections), 276 pages
  slides_overleaf_nguoi1.zip ... nguoi4, phu       one person's sections only (main.tex = wrapper -> khung.tex), small and fast to compile

Overleaf limits: at most 180 files per upload (this script stops above 175), 10 s compile time on the Free plan.
Layout of every zip: theme .sty/.tex, bocuc.sty, hust-override.sty, main.tex (or khung.tex) at the ROOT, so `lualatex main.tex` works anywhere
(MiKTeX + TeXstudio, no latexmk, no TEXINPUTS); assets/ (only the theme images in use), figures/ (only the figures the sections use), sections/.
"""
from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SL = ROOT / "slides"
THEME = SL / "hust-theme"
MAX_FILES = 175
IMG = re.compile(r"[{\[ ,]([\w\-./]+\.(?:png|jpg|jpeg|pdf))(?=[}\], ])")

PEOPLE = {  # zip suffix -> section files (handoff P12, khung chờ theo người)
    "nguoi1": ["01a-nghiep-vu-yeu-cau"],
    "nguoi2": ["00b-ly-thuyet-rut-gon", "01b-du-lieu-nguon-erd", "02a-kham-pha"],
    "nguoi3": ["02b-kien-truc-etl-model"],
    "nguoi4": ["03-dashboard", "05-tong-ket"],
    "phu": ["00-mo-dau", "04-mo-rong"],
}
THEME_ROOT_FILES = ["beamerthemeHUST.sty", "beamercolorthemeHUST.sty", "beamerfontthemeHUST.sty", "beamerinnerthemeHUST.sty", "beamerouterthemeHUST.sty", "hust-core.sty", "hust-setup.tex"]
# theme images actually read by a build of this deck (from main.fls); the zip fails loudly if one is missing
THEME_ASSETS = ["bg-cover-blue-169.png", "bg-dark-blue-169.png", "bg-diag-blue.png", "bg-panel-blue-169.png", "fami-shield.png", "footer-mark.png", "hust-shield.png"]
LATEXMKRC = "$pdf_mode = 4;   # LuaLaTeX (Overleaf đọc dòng này để chọn trình biên dịch)\n$bibtex_use = 0;\n"


def images_of(text: str) -> set[str]:
    return {m.group(1) for m in IMG.finditer(text)}


def resolve_figures(names: set[str]) -> tuple[dict[str, Path], list[str]]:
    found, missing = {}, []
    for n in sorted(names):
        for cand in (SL / "figures" / n, SL / n):
            if cand.is_file():
                found[cand.relative_to(SL).as_posix() if cand.is_relative_to(SL / "figures") else "figures/" + n] = cand
                break
        else:
            if (THEME / "assets" / n).is_file() or n in THEME_ASSETS:
                continue  # theme asset (handled separately)
            missing.append(n)
    return found, missing


def frame_text(tex_names: list[str]) -> str:
    return (SL / "main.tex").read_text(encoding="utf-8") + "".join((SL / "sections" / f"{n}.tex").read_text(encoding="utf-8") for n in tex_names)


def common_files() -> dict[str, Path]:
    files = {}
    for n in THEME_ROOT_FILES:
        files[n] = THEME / n
    files["bocuc.sty"] = SL / "bocuc.sty"
    files["hust-override.sty"] = SL / "hust-override.sty"
    for a in THEME_ASSETS:
        p = THEME / "assets" / a
        assert p.is_file(), f"thiếu ảnh theme {a}"
        files[f"assets/{a}"] = p
    return files


def khung_text() -> str:
    t = (SL / "main.tex").read_text(encoding="utf-8")
    t = t.replace("\\graphicspath{{hust-theme/assets/}{assets/}{figures/}}", "\\graphicspath{{assets/}{figures/}}")
    t = t.replace("% Theme HUST: thư mục hust-theme/ (đường dẫn đặt trong .latexmkrc).", "% Theme HUST: các file .sty nằm ở gốc (không cần TEXINPUTS).")
    return t


def write_zip(out: Path, files: dict[str, Path], texts: dict[str, str]) -> None:
    n = len(files) + len(texts)
    by_dir = Counter((k.split("/")[0] if "/" in k else "(gốc)") for k in list(files) + list(texts))
    print(f"{out.name}: {n} file; " + ", ".join(f"{d} {c}" for d, c in sorted(by_dir.items())))
    if n > MAX_FILES:
        sys.exit(f"LỖI: {out.name} có {n} file, quá {MAX_FILES} (Overleaf bỏ phần thừa sau 180 file)")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, p in sorted(files.items()):
            z.write(p, arc)
        for arc, s in sorted(texts.items()):
            z.writestr(arc, s)
    print(f"   {out.stat().st_size / 1024 / 1024:.1f} MB")


def wrapper(sections: list[str], nhap: bool, who: str) -> str:
    lst = ",".join(f"sections/{s}" for s in sections)
    head = (
        "% !TeX program = lualatex\n"
        f"% Zip của {who}: chỉ có phần slide của bạn ({', '.join(sections)}). Mở là biên dịch đúng phần này, không cần đổi Main document.\n"
        "% Các file theme (.sty) nằm ở gốc nên `lualatex main.tex` chạy thẳng, kể cả MiKTeX + TeXstudio (không cần latexmk).\n"
    )
    if nhap:
        head += (
            "% CHẾ ĐỘ NHÁP đang bật (dòng \\def\\NHAP{} bên dưới): hình thành khung trống, không có trang tiêu đề, mục lục, trang chuyển phần,\n"
            "% để biên dịch kịp 10 giây của Overleaf Free. Muốn xem hình thật thì xoá dòng `\\def\\NHAP{}`; có thể quá 10 giây trên Overleaf Free.\n"
            "\\PassOptionsToPackage{draft}{graphicx}\n\\def\\NHAP{}\n"
        )
    head += f"\\def\\CHIPHAN{{{lst}}}\n\\input{{khung.tex}}\n"
    return head


def main() -> None:
    nhap_mode = "auto"
    if "--nhap-nguoi" in sys.argv:
        nhap_mode = sys.argv[sys.argv.index("--nhap-nguoi") + 1]
    cm = common_files()
    khung = khung_text()
    all_sections = sorted(p.stem for p in (SL / "sections").glob("*.tex"))

    # ---- full deck
    figs, missing = resolve_figures(images_of(frame_text(all_sections)))
    if missing:
        print("CẢNH BÁO hình không tìm thấy:", ", ".join(missing))
    files = dict(cm)
    files.update(figs)
    for s in all_sections:
        files[f"sections/{s}.tex"] = SL / "sections" / f"{s}.tex"
    write_zip(ROOT / "slides_overleaf.zip", files, {"main.tex": khung, ".latexmkrc": LATEXMKRC})

    # ---- one zip per person
    for key, secs in PEOPLE.items():
        figs, missing = resolve_figures(images_of(frame_text(secs)))
        if missing:
            print(f"CẢNH BÁO {key}: hình không tìm thấy:", ", ".join(missing))
        files = dict(cm)
        files.update(figs)
        for s in secs:
            files[f"sections/{s}.tex"] = SL / "sections" / f"{s}.tex"
        nhap = {"on": True, "off": False}.get(nhap_mode, NHAP_DEFAULT.get(key, False))
        texts = {"main.tex": wrapper(secs, nhap, key), "khung.tex": khung, ".latexmkrc": LATEXMKRC}
        write_zip(ROOT / f"slides_overleaf_{key}.zip", files, texts)


# người nào bật chế độ nháp mặc định (đặt theo thời gian biên dịch đo được, xem handoff/2026-11-25-P12g-zip.md)
NHAP_DEFAULT: dict[str, bool] = {k: True for k in PEOPLE}   # hình thật: 6,7–10,6 s (quá sát 10 s); nháp: 4,7–6,7 s

if __name__ == "__main__":
    main()
