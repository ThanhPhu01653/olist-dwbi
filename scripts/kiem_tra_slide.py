"""Kiểm tra slide Beamer theo slides/QUY-TAC-TRINH-BAY.md (trình chiếu bằng máy chiếu).

    python scripts/kiem_tra_slide.py                       # mọi file trong slides/sections/
    python scripts/kiem_tra_slide.py slides/sections/04-mo-rong.tex
    python scripts/kiem_tra_slide.py --strict ...          # trả mã lỗi 1 nếu còn LỖI (dùng trước khi commit)
    python scripts/kiem_tra_slide.py --anh slides/main.pdf 138-177
        # xuất ảnh xem trước các trang (cần: pip install pymupdf) vào slides/_xem_truoc/,
        # kèm bảng ghép 3x3 để xem nhanh như trên máy chiếu

Mức báo:
  LỖI  : vi phạm quy tắc cứng (phải sửa)
  NÊN  : nên sửa, trừ khi có lý do (ghi lý do bằng dòng chú thích "% cho-phep: <mã quy tắc> <lý do>" trong frame)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ROOT / "slides" / "sections"

IMG = re.compile(r"\\(includegraphics|anh|HinhLon|AnhChup|HinhChu)\b|\\begin\{AnhKhoanh\}")
SMALL = re.compile(r"\\(scriptsize|tiny|footnotesize)\b")
TITLE_MAX = 65          # P12: tiêu đề = tên mục trong checklist của thầy + ": kết luận ngắn"; tối đa 65 ký tự
KETLUAN_MAX = 85        # thanh kết luận một dòng
MAX_ITEMS = 5
MAX_ITEM_CHARS = 110
MAX_ROWS = 8            # gồm dòng tiêu đề và dòng tổng
MAX_WORDS = 70          # chữ nhìn thấy trên một trang (không tính \note)


def strip_note(s: str) -> str:
    out, i = [], 0
    while True:
        j = s.find("\\note{", i)
        if j < 0:
            out.append(s[i:]); break
        out.append(s[i:j]); k = j + 6; depth = 1
        while k < len(s) and depth:
            depth += {"{": 1, "}": -1}.get(s[k], 0); k += 1
        i = k
    return "".join(out)


def brace_arg(s: str, start: int) -> tuple[str, int]:
    """s[start] == '{' -> (nội dung, vị trí sau '}')"""
    depth, k = 0, start
    while k < len(s):
        if s[k] == "{": depth += 1
        elif s[k] == "}":
            depth -= 1
            if depth == 0: return s[start + 1:k], k + 1
        k += 1
    return s[start + 1:], len(s)


def visible_text(s: str) -> str:
    s = s.replace("\\%", "\x00")
    s = re.sub(r"(?<!\\)%.*", "", s).replace("\x00", "%")
    s = re.sub(r"\\(texttt|textbf|emph|code)\{([^{}]*)\}", r"\2", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?(<[^>]*>)?", " ", s)
    s = re.sub(r"[{}&\\$]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def frames(path: Path):
    text = path.read_text(encoding="utf-8")
    for m in re.finditer(r"\\begin\{frame\}(?:<[^>]*>)?(?:\[[^\]]*\])?", text):
        end = text.find("\\end{frame}", m.end())
        body = text[m.end():end]
        line = text.count("\n", 0, m.start()) + 1
        title = ""
        if body.lstrip().startswith("{"):
            off = len(body) - len(body.lstrip())
            title, after = brace_arg(body, off)
            body = body[after:]
        yield line, title, body


def check_frame(title: str, body: str) -> list[tuple[str, str, str]]:
    msgs = []
    allow = set(re.findall(r"%\s*cho-phep:\s*(R\d+)", body))
    b = strip_note(body)

    def add(level, code, msg):
        if code not in allow:
            msgs.append((level, code, msg))

    t = visible_text(title)
    if len(t) > TITLE_MAX:
        add("LỖI", "R1", f"tiêu đề {len(t)} ký tự > {TITLE_MAX}: dùng tên mục + kết luận ngắn, con số chi tiết để ở \\KetLuan")

    # R2: số hình nhìn thấy cùng lúc (hình trong \only<n>{...} tính theo từng bước)
    only_imgs: dict[str, int] = {}
    rest = b
    for m in re.finditer(r"\\only<([^>]*)>\s*\{", b):
        arg, _ = brace_arg(b, m.end() - 1)
        only_imgs[m.group(1)] = only_imgs.get(m.group(1), 0) + len(IMG.findall(arg))
        rest = rest.replace(arg, "")
    base = len(IMG.findall(rest))
    shown = base + (max(only_imgs.values()) if only_imgs else 0)
    if shown > 1:
        add("LỖI", "R2", f"{shown} hình cùng lúc trên một trang: tách slide hoặc dùng \\only<1>/\\only<2>")

    # R3: chữ nhỏ
    if SMALL.search(re.sub(r"\\Nguon\{[^}]*\}", "", b)):
        add("LỖI", "R3", "dùng \\scriptsize/\\footnotesize/\\tiny cho nội dung: không đọc được trên máy chiếu")

    # R4: hình nằm trong cột hẹp
    for cm in re.finditer(r"\\begin\{column\}\{([0-9.]+)\\(?:textwidth|linewidth)\}(.*?)\\end\{column\}", b, re.S):
        if IMG.search(cm.group(2)) and float(cm.group(1)) < 0.58:
            add("LỖI", "R4", f"hình trong cột rộng {cm.group(1)}: dùng \\HinhChu (hình 60%) hoặc để hình một mình")

    # R5: gạch đầu dòng
    items = re.findall(r"\\item\s+(.*?)(?=\\item|\\end\{itemize\}|\\end\{enumerate\}|$)", b, re.S)
    if len(items) > MAX_ITEMS:
        add("LỖI", "R5", f"{len(items)} gạch đầu dòng > {MAX_ITEMS}: chia slide hoặc gộp ý")
    long_items = [visible_text(i) for i in items if len(visible_text(i)) > MAX_ITEM_CHARS]
    if long_items:
        add("NÊN", "R5", f"{len(long_items)} ý dài quá {MAX_ITEM_CHARS} ký tự (quá 2 dòng): rút gọn, chi tiết đưa vào \\note")

    # R6: bảng
    for tm in re.finditer(r"\\begin\{(tabular|tabularx|BangTC)\}(.*?)\\end\{\1\}", b, re.S):
        rows = tm.group(2).count("\\\\")
        if rows > MAX_ROWS:
            add("LỖI", "R6", f"bảng {rows} dòng > {MAX_ROWS}: gom nhóm dòng nhỏ hoặc tách slide")
        if tm.group(1) != "BangTC":
            add("NÊN", "R6", "bảng dùng tabular thường: đổi sang môi trường BangTC (chữ \\small, rộng hết khung)")

    # R7: thanh kết luận
    km = re.search(r"\\KetLuan\{", b)
    if km:
        kt, _ = brace_arg(b, km.end() - 1)
        if len(visible_text(kt)) > KETLUAN_MAX:
            add("LỖI", "R7", f"\\KetLuan {len(visible_text(kt))} ký tự > {KETLUAN_MAX}: phải nằm trên một dòng")
    elif IMG.search(b) or re.search(r"\\begin\{(tabular|BangTC)", b):
        add("NÊN", "R7", "slide có hình/bảng nhưng thiếu \\KetLuan{...} (một câu có số)")

    # R8: hình bị đặt quá nhỏ
    for hm in re.finditer(r"\\(?:anh|HinhLon|AnhChup)\[([0-9.]+)\\textheight\]", b):
        if float(hm.group(1)) < 0.45:
            add("NÊN", "R8", f"hình cao {hm.group(1)}\\textheight: quá nhỏ khi chiếu, dùng mặc định (\\HinhCao)")

    # R9: quá nhiều chữ
    words = len(visible_text(re.sub(r"\\begin\{(tabular|tabularx|BangTC)\}.*?\\end\{\1\}", "", b, flags=re.S)).split())
    if words > MAX_WORDS:
        add("NÊN", "R9", f"{words} từ trên trang > {MAX_WORDS}: chuyển bớt sang ghi chú người nói (\\note)")
    # R10 (P12b): slide thưa = không có hình, bảng, thẻ số, khung chờ; chỉ có danh sách tối đa 3 mục, mỗi mục dưới 90 ký tự
    if not re.search(r"\\(HinhLon|AnhChup|HinhChu|includegraphics|HangSo|TruocSau|khungchen|anh|LoTrinh)\b|\\begin\{(AnhKhoanh|BangTC|tabular|tikzpicture)\}", b):
        items = re.findall(r"\\item\s+([^\n]*)", b)
        if 1 <= len(items) <= 3 and all(len(visible_text(x)) < 90 for x in items):
            add("NÊN", "R10", f"slide thưa: chỉ {len(items)} gạch đầu dòng ngắn, không hình, bảng hay thẻ số; thêm thẻ số, bảng hoặc hình, hoặc ghi lý do bằng % cho-phep: R10")
    return msgs


def render(pdf: Path, pages: str):
    try:
        import fitz  # pymupdf
    except ImportError:
        sys.exit("Cần: pip install pymupdf")
    a, _, b = pages.partition("-")
    first, last = int(a), int(b or a)
    out = ROOT / "slides" / "_xem_truoc"; out.mkdir(exist_ok=True)
    doc = fitz.open(pdf)
    files = []
    for p in range(first, last + 1):
        pix = doc[p - 1].get_pixmap(dpi=96)          # ~ 1280 px chiều rộng như máy chiếu thường
        f = out / f"trang-{p:03d}.png"; pix.save(f); files.append(f)
    try:
        from PIL import Image
        ims = [Image.open(f) for f in files]
        w, h = ims[0].size
        for k in range(0, len(ims), 9):
            part = ims[k:k + 9]; rows = (len(part) + 2) // 3
            sheet = Image.new("RGB", (3 * w + 20, rows * h + 10 * (rows - 1)), "gray")
            for i, im in enumerate(part):
                sheet.paste(im, ((i % 3) * (w + 10), (i // 3) * (h + 10)))
            sheet.save(out / f"ghep-{first + k:03d}.png")
    except ImportError:
        pass
    print(f"Đã xuất {len(files)} trang vào {out}")


def check_pdf(pdf: Path, include_backup: bool = False) -> tuple[int, int]:
    """P12d: check geometry on the rendered PDF (see scripts/do_vung_slide.py). Returns (errors, warnings)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import hashlib  # noqa: F401
    import json
    from do_vung_slide import measure
    ms = measure(pdf)
    try:
        import pymupdf
        doc = pymupdf.open(str(pdf))
        first_backup = next((i for i, pg in enumerate(doc) if "accumulating snapshot (3)" in pg.get_text()), len(ms))
    except Exception:
        first_backup = len(ms)
    man_path = ROOT / "figures" / "slide" / "_manifest.json"
    man = json.loads(man_path.read_text(encoding="utf-8")) if man_path.exists() else {}
    by_px = {tuple(v["px"]): (k, v) for k, v in man.items()}
    GAP = 2.0
    FULL_W = 428.0
    HINH_CAO = 175.0
    n_err = n_warn = 0

    def say(level, pg, msg):
        nonlocal n_err, n_warn
        print(f"pdf trang {pg}  {level} P12d  {msg}")
        n_err += level == "LỖI"
        n_warn += level == "NÊN"

    for m in ms:
        pg = m["page"]
        if not include_backup and pg - 1 >= first_backup:
            break
        bar, foot = m["bar_bottom"], m["footer_top"]
        if bar is None or foot is None:
            continue  # title / section / thanks pages
        boxes = [("hình", f["bbox"]) for f in m["figs"]]
        if m["ket"]:
            boxes.append(("thanh KetLuan", m["ket"]))
        for name, (x0, y0, x1, y1) in boxes:
            if y0 < bar + GAP:
                say("LỖI", pg, f"{name} chạm thanh tiêu đề/nhãn mục (khe {y0 - bar:.1f} pt < {GAP:g})")
            if y1 > foot - GAP:
                say("LỖI", pg, f"{name} chạm chân trang (khe {foot - y1:.1f} pt < {GAP:g})")
            if x0 < 0 or x1 > m["w"] or y1 > m["h"]:
                say("LỖI", pg, f"{name} ra ngoài trang")
        for f in m["figs"]:
            x0, y0, x1, y1 = f["bbox"]
            w, h = x1 - x0, y1 - y0
            hit = by_px.get(tuple(f["px"]))
            if hit:
                nm, v = hit
                scale = w / (v["w_in"] * 72.0)
                shown = v["min_pt"] * scale
                if shown < 9.0 - 0.05:
                    say("LỖI", pg, f"{nm}: chữ nhỏ nhất sau khi chèn {shown:.1f} pt < 9 (cỡ {v['min_pt']:.1f} pt, thu phóng {scale:.2f})")
            if w < 0.55 * FULL_W and h >= HINH_CAO - 4 and w < 0.45 * m["w"]:
                say("NÊN", pg, f"hình hẹp ({w:.0f} pt trên khung {FULL_W:.0f} pt) mà đã chạm trần chiều cao: vẽ lại theo chiều ngang")
    return n_err, n_warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--final", action="store_true", help="ban thuyet trinh cuoi: LOI neu con khung cho, nhan xac nhan, todo, lorem")
    ap.add_argument("--anh", nargs=2, metavar=("PDF", "TRANG"))
    ap.add_argument("--pdf", metavar="PDF", help="P12d: do hình, thanh KetLuan, chữ trong hình trên PDF (bộ chính; thêm --ca-du-phong để gồm cả dự phòng)")
    ap.add_argument("--ca-du-phong", action="store_true")
    a = ap.parse_args()
    if a.anh:
        render(Path(a.anh[0]), a.anh[1]); return
    if a.pdf:
        e, w = check_pdf(Path(a.pdf), a.ca_du_phong)
        print(f"\nPDF: {e} LỖI, {w} NÊN")
        if a.strict and e:
            sys.exit(1)
        return
    files = [Path(f) for f in a.files] or sorted(SECTIONS.glob("*.tex"))
    n_err = n_warn = 0
    for f in files:
        for line, title, body in frames(f):
            for level, code, msg in check_frame(title, body):
                print(f"{f.name}:{line}  {level} {code}  [{visible_text(title)[:60]}]  {msg}")
                n_err += level == "LỖI"; n_warn += level == "NÊN"
    if a.final:
        pat = re.compile(r"\\khungchen|\\canxacnhan|\\todo|TODO|lorem|CHÈN (HÌNH|ẢNH|BẢNG)", re.I)
        for f in files:
            for i, ln in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if ln.lstrip().startswith("%") or "\\newcommand" in ln:
                    continue
                if pat.search(ln):
                    print(f"{f.name}:{i}  LỖI final  còn chữ giữ chỗ: {ln.strip()[:70]}")
                    n_err += 1
    print(f"\nTổng: {n_err} LỖI, {n_warn} NÊN")
    if a.strict and n_err:
        sys.exit(1)


if __name__ == "__main__":
    main()
