"""Generate the Beamer sections slides/sections/*.tex from slides/slide-script.md (re-runnable).   python scripts/gen_beamer.py

Rules: '### Sxx. title' -> one frame (title = the conclusion sentence); bullets -> itemize; figures named in the 'Hình:' line -> copied to slides/figures/
and placed beside the bullets (1 figure) or below (several); 'report/tables/X.tex' -> the tabular of that table; 'ảnh chụp dashboard Dx' -> a red empty box
"CHÈN ẢNH CHỤP Dx"; other hand-drawn items -> a red box "CHÈN ..."; 'Nói:' -> \\note{...} (speaker note). Slides with a hand-written body are in EXTRAS.
10 backup slides B01-B10 come from the Q&A table at the end of the script and go to the appendix.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SL = ROOT / "slides"
SECTIONS = {1: ("01-ly-thuyet", "Lý thuyết", "Mở đầu và lý thuyết rút gọn"), 2: ("02-bai-toan", "Bài toán và nghiệp vụ", "Bài toán và nghiệp vụ"),
            3: ("03-du-lieu", "Dữ liệu và EDA", "Dữ liệu và khám phá dữ liệu"), 4: ("04-kien-truc", "Kiến trúc và thiết kế", "Kiến trúc và thiết kế kho dữ liệu"),
            5: ("05-etl-mart-olap", "ETL, mart, OLAP", "ETL, data mart, OLAP và hiệu năng"), 6: ("06-dashboard", "Dashboard và mở rộng", "Dashboard và mở rộng"),
            7: ("07-ket-luan", "Kết luận", "Kết luận")}
DRAWIO = {"kien-truc-cac-lop": "3-4-1_pipeline.png", "data-model-theo-mart": "3-3-4_constellation.png", "pipeline-etl": "3-4-1_pipeline.png"}


def esc(s: str) -> str:
    for a, b in [("\\", r"\textbackslash{}"), ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"), ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}")]:
        s = s.replace(a, b)
    return s


def tex(s: str) -> str:
    """markdown-ish text -> LaTeX (code, bold, arrows and other symbols that Lato lacks)."""
    out = []
    for p in re.split(r"(`[^`]+`)", s):
        if p.startswith("`") and p.endswith("`") and len(p) > 2:
            out.append(r"\texttt{" + esc(p[1:-1]).replace(r"\_", r"\_\allowbreak{}") + "}")
            continue
        t = esc(p)
        t = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", t)
        t = t.replace("→", r"$\rightarrow$").replace("≤", r"$\leq$").replace("≥", r"$\geq$").replace("×", r"$\times$").replace("≈", r"$\approx$").replace("Σ", r"$\Sigma$")
        t = t.replace("−", "-").replace("…", "...").replace("·", r"$\cdot$").replace("✓", r"\ding{51}")
        t = re.sub(r"\[nhóm (xác nhận|chèn|hoàn thiện|viết theo giáo trình|bổ sung[^\]]*)\]", r"", t)
        out.append(t)
    return "".join(out).strip()


def cell(c: str) -> str:
    """table cell with raw LaTeX allowed; only `code` spans are escaped."""
    return "".join(r"\texttt{" + esc(p[1:-1]) + "}" if p.startswith("`") and p.endswith("`") and len(p) > 2 else re.sub(r"(?<!\\)%", r"\\%", p) for p in re.split(r"(`[^`]+`)", c))


def TAB(rows, spec, head):
    return ("\\begin{center}\\adjustbox{max width=\\linewidth,max height=0.5\\textheight}{\\scriptsize\\renewcommand{\\arraystretch}{1.15}\\begin{tabular}{" + spec + "}\\toprule\n"
            + " & ".join(f"\\textbf{{{cell(h)}}}" for h in head) + " \\\\\\midrule\n" + "\n".join(" & ".join(cell(c) for c in r) + " \\\\" for r in rows) + "\n\\bottomrule\\end{tabular}}\\end{center}")

EXTRAS = {
    "S05": TAB([["Mục đích", "ghi từng giao dịch", "phân tích, tổng hợp"], ["Mô hình dữ liệu", "9 bảng chuẩn hóa (`oltp`)", "hình sao: 6 fact + 10 chiều (`dw`)"],
                ["Truy vấn điển hình", "nối nhiều bảng, ít dòng", "quét và gom nhiều dòng"], ["Dữ liệu", "trạng thái hiện tại", "có lịch sử (SCD2 cho khách)"], ["Ví dụ", "`orders`, `order_items`", "`fact_order_item`, `dim_date`"]],
               "lll", ["Tiêu chí", "OLTP", "OLAP (kho dữ liệu)"]),
    "S06": TAB([["Cách xây", "từ data mart theo quy trình nghiệp vụ, chiều dùng chung", "kho doanh nghiệp chuẩn hóa 3NF, rồi tách data mart"], ["Mô hình", "chiều (lược đồ sao)", "chuẩn hóa"],
                ["Thời gian ra kết quả", "nhanh, từng quy trình một", "lâu hơn, thiết kế tổng thể trước"], ["Nhóm chọn", "\\ding{51} (bus matrix, `dim_seller` dùng chung)", "--"]], "lll", ["Tiêu chí", "Kimball", "Inmon"]),
    "S08": TAB([["Transaction", "một sự kiện đã xảy ra", "`fact_order_item`, `fact_payment`, `fact_review`"], ["Periodic snapshot", "trạng thái của một kỳ", "`fact_seller_monthly` (36.583 dòng, dày đặc)"],
                ["Accumulating snapshot", "cả vòng đời, cập nhật theo mốc", "`fact_order_fulfillment` (99.441), `fact_lead_funnel` (8.000)"], ["SCD1 / SCD2", "ghi đè / giữ lịch sử", "`dim_seller` / `dim_customer`"]], "lll", ["Loại", "Một dòng là", "Ví dụ trong dự án"]),
    "S10": TAB([["Roll-up", "`ROLLUP`", "quý $\\rightarrow$ năm $\\rightarrow$ tổng"], ["Drill-down", "thêm cấp vào `GROUP BY`", "2017 $\\rightarrow$ Q4 $\\rightarrow$ 11/2017 $\\rightarrow$ ngày"], ["Slice", "`WHERE` một chiều", "năm 2017"],
                ["Dice", "`WHERE` nhiều chiều", "Sudeste $\\times$ Home \\& Furniture $\\times$ Q4"], ["Pivot", "`FILTER`", "vùng $\\times$ năm"]], "lll", ["Thao tác", "SQL", "Ví dụ trong dự án"]),
    "S11": TAB([["Lưu trữ", "khối đa chiều riêng", "bảng quan hệ (lược đồ sao)", "kết hợp hai cách"], ["Tốc độ truy vấn", "rất nhanh (tính sẵn)", "phụ thuộc chỉ mục, materialized view", "cân bằng"],
                ["Độ tươi dữ liệu", "phải xử lý lại khối", "luôn tươi sau mỗi lần nạp", "tùy phần"], ["Công cụ", "ví dụ SSAS", "PostgreSQL + Power BI", "--"], ["Nhóm chọn", "--", "\\ding{51} ROLAP", "--"]],
               "llll", ["Tiêu chí", "MOLAP", "ROLAP", "HOLAP"]),
    "S20": TAB([["Mua $\\rightarrow$ duyệt", "`approval_hours`", "10,3 giờ"], ["Duyệt $\\rightarrow$ bàn giao", "`handling_days`", "2,9 ngày"], ["Bàn giao $\\rightarrow$ giao", "`transit_days`", "9,3 ngày"],
                ["Mua $\\rightarrow$ giao", "`lead_days`", "12,6 ngày"], ["Ngày hứa giao", "`promised_days`", "24,4 ngày"]], "lll", ["Chặng", "Chỉ số của kho", "Trung bình"]),
    "S48": TAB([["Câu a", "`dim_customer` dùng SCD2", "chỉ 0,26% khách đổi zip"], ["Câu b", "D6 hai trang", "380/842 deal có đơn"], ["Câu c", "snapshot seller dày đặc", "36.583 so với 16.441 dòng"],
                ["Câu d", "13 nhóm ngành hàng", "73 danh mục"], ["Câu e", "zip thiếu toạ độ vẫn có dòng", "167 zip, không mất đơn"], ["Câu f", "mốc nạp đầu 2017-12-31", "45.430 đơn, 11 đợt sau"]], "lll", ["Quyết định", "Nội dung", "Số liệu đi kèm"]),
    "S53": TAB([[f, *["\\ding{51}" if c else "" for c in row]] for f, row in [("fact\\_order\\_item", [1, 1, 1, 1, 1, 1, 0, 0, 0, 0]), ("fact\\_order\\_fulfillment", [1, 1, 0, 0, 1, 1, 0, 0, 0, 0]),
                ("fact\\_payment", [1, 1, 0, 0, 0, 0, 1, 0, 0, 0]), ("fact\\_review", [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]), ("fact\\_lead\\_funnel", [1, 0, 1, 0, 0, 0, 0, 1, 1, 1]), ("fact\\_seller\\_monthly", [1, 0, 1, 0, 0, 0, 0, 0, 0, 0])]],
               "l" + "c" * 10, ["Fact", "Date", "Customer", "Seller", "Product", "Geo", "Status", "Payment", "Origin", "Profile", "Rep"]),
    "S59": TAB([["15081", "570eb70f…", "31930", "belo horizonte", "1900-01-01", "2017-11-08", "không", "1"], ["15082", "570eb70f…", "31130", "belo horizonte", "2017-11-09", "9999-12-31", "có", "2"]],
               "llllllll", ["customer\\_key", "khách thật", "zip", "thành phố", "effective\\_from", "effective\\_to", "is\\_current", "version"]),
    "S63": TAB([["approval\\_hours", "36,61"], ["handling\\_days", "0,71"], ["transit\\_days", "12,84"], ["lead\\_days", "15,07"], ["promised\\_days", "21"], ["delay\\_days", "-6 (giao sớm 6 ngày)"], ["order\\_value", "43,00"], ["freight\\_total", "45,30"], ["payment\\_total", "88,30"]],
               "ll", ["Cột của fact\\_order\\_fulfillment (đơn 19c36691…)", "Giá trị"]),
    "S82": TAB([["ODS (số dòng, loại, cleaning)", "25"], ["Dimension (Unknown, SCD2, phủ khoá)", "42"], ["Fact (đối soát, grain, khoá ngoại, logic)", "49"], ["Data mart (khớp fact)", "17"], ["Thử lại dòng mồ côi (kịch bản)", "3"],
                ["\\textbf{Tổng}", "\\textbf{136 (đạt 100\\%)}"], ["Đối chiếu khám phá dữ liệu (chỉ báo cáo)", "6/6 khớp"]], "ll", ["Nhóm kiểm thử", "Số phép"]),
    "S84": TAB([["mart\\_sales", "6", "D1, D2, D4"], ["mart\\_fulfillment", "4", "D3, D4"], ["mart\\_cx", "4 (RFM, cohort materialized)", "D5"], ["mart\\_acquisition", "3 (scorecard, theo kênh materialized)", "D6"]], "lll", ["Mart", "Số view", "Dashboard"]),
}
GRID7 = "\\begin{columns}[c]" + "".join(f"\\begin{{column}}{{0.24\\textwidth}}\\includegraphics[width=\\linewidth,height=0.3\\textheight,keepaspectratio]{{3-2-7_cay_phan_tich_D{i}.png}}\\end{{column}}" + ("\\end{columns}\\vspace{0.3em}\\begin{columns}[c]" if i == 4 else "")
                                  for i in range(1, 8)) + "\\end{columns}"


def parse(md: str):
    part, slides, backups = 0, [], []
    cur = None
    for line in md.splitlines():
        m = re.match(r"## PHẦN (\d+)", line)
        if m:
            part = int(m.group(1))
        m = re.match(r"### (S\d+)\. (.+)", line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(), "bullets": [], "hinh": "", "noi": "", "part": part}
            slides.append(cur)
            continue
        if line.startswith("### B01") or line.startswith("## 10 CÂU"):
            cur = None
        if cur and line.startswith("- "):
            t = line[2:]
            if t.startswith("Hình:"):
                cur["hinh"] = t[5:].strip()
            elif t.startswith("Nói:"):
                cur["noi"] = t[4:].strip()
            else:
                cur["bullets"].append(t)
        m = re.match(r"\| (B\d\d) \| (.+?) \| (.+?) \| (.+?) \|$", line)
        if m:
            backups.append({"id": m.group(1), "q": m.group(2).strip(), "a": m.group(3).strip(), "ref": m.group(4).strip()})
    return slides, backups


def media(s: dict, copied: set) -> tuple[list[str], str]:
    """-> (figure file names, extra body tex or placeholder tex)"""
    h, sid = s["hinh"], s["id"]
    figs = [Path(f).name for f in re.findall(r"figures/([\w\-.]+\.png)", h)]
    for k, v in DRAWIO.items():
        if k in h and v not in figs:
            figs.append(v)
    if sid == "S31":
        for i in range(1, 8):
            shutil.copy2(ROOT / "figures" / f"3-2-7_cay_phan_tich_D{i}.png", SL / "figures" / f"3-2-7_cay_phan_tich_D{i}.png")
        return [], GRID7
    if sid in EXTRAS:
        return figs, EXTRAS[sid]
    for t in re.findall(r"report/tables/(\w+)\.tex", h):
        src = (ROOT / "report" / "tables" / f"{t}.tex").read_text(encoding="utf-8")
        m = re.search(r"\\begin\{tabular\}.*?\\end\{tabular\}", src, re.S)
        sp = re.search(r"\\begin\{tabular\}\{([^}]*)\}\s*\\toprule\s*(.*?\\\\)\s*\\midrule\s*(.*?)\\bottomrule", src, re.S)
        if sp and len(sp.group(3).strip().splitlines()) > 12:        # tall table: two side-by-side halves
            body = [l for l in sp.group(3).strip().splitlines() if l.strip()]
            half = (len(body) + 1) // 2
            one = lambda rows: "\\adjustbox{max width=\\linewidth}{\\scriptsize\\begin{tabular}{" + sp.group(1) + "}\\toprule " + sp.group(2) + " \\midrule\n" + "\n".join(rows) + "\n\\bottomrule\\end{tabular}}"
            return figs, "\\begin{columns}[T]\\begin{column}{0.49\\textwidth}" + one(body[:half]) + "\\end{column}\\begin{column}{0.49\\textwidth}" + one(body[half:]) + "\\end{column}\\end{columns}"
        if m and t != "marts":
            return figs, "\\begin{center}\\adjustbox{max width=\\linewidth,max height=0.5\\textheight}{\\scriptsize" + m.group(0) + "}\\end{center}"
    d = re.search(r"ảnh chụp dashboard (D\d)(?: trang (\d))?", h)
    if d:
        return figs, f"\\khungchen{{CHÈN ẢNH CHỤP {d.group(1)}" + (f" TRANG {d.group(2)}" if d.group(2) else "") + "}"
    if not figs and h and h.lower() not in ("không", "không (danh sách đánh số)"):
        txt = tex(re.sub(r"\[.*?\]", "", h)).strip()
        return figs, f"\\khungchen[0.3\\textheight]{{CHÈN HÌNH / BẢNG: {txt}}}"
    return figs, ""


def frame(s: dict, copied: set, backup: bool = False) -> str:
    figs, extra = media(s, copied)
    for f in figs:
        src = ROOT / "figures" / f
        if src.exists():
            shutil.copy2(src, SL / "figures" / f)
            copied.add(f)
    figs = [f for f in figs if (ROOT / "figures" / f).exists()]
    bl = "\\begin{itemize}\n" + "\n".join(f"  \\item {tex(b)}" for b in s["bullets"]) + "\n\\end{itemize}" if s["bullets"] else ""
    tag = "\\canxacnhan" if "[nhóm xác nhận]" in (" ".join(s["bullets"]) + s["hinh"] + s["noi"]) else ""
    opts = "[noprogressbar,noframenumbering]" if backup else ""
    body = ""
    if len(figs) == 1 and not extra:
        body = "\\begin{columns}[T]\\begin{column}{0.4\\textwidth}\n" + bl + "\n\\end{column}\\begin{column}{0.58\\textwidth}\n\\begin{center}\\anh[0.74\\textheight]{" + figs[0] + "}\\end{center}\n\\end{column}\\end{columns}"
    elif figs and not extra:
        w = round(0.96 / len(figs), 2)
        body = bl + "\n\\begin{columns}[c]" + "".join(f"\\begin{{column}}{{{w}\\textwidth}}\\anh[0.46\\textheight]{{{f}}}\\end{{column}}" for f in figs) + "\\end{columns}"
    else:
        body = bl + "\n" + (f"\\begin{{columns}}[c]\\begin{{column}}{{0.3\\textwidth}}\\anh[0.5\\textheight]{{{figs[0]}}}\\end{{column}}\\begin{{column}}{{0.68\\textwidth}}{extra}\\end{{column}}\\end{{columns}}" if figs and extra and "tabular" in extra else extra)
    note = ("\\note{" + tex(f"[{s['id']}] " + s["noi"]) + "}") if s["noi"] else ""
    title = re.sub(r"\\texttt\{(.*?)\}", r"\1", tex(s["title"]).replace("\\allowbreak{}", "")).replace("\\_", "\\symbol{95}")   # moving argument: no \texttt, \allowbreak, \_
    return f"\\begin{{frame}}{opts}{{{title}}}\n{body}\n{tag}\n{note}\n\\end{{frame}}\n"


def main() -> None:
    (SL / "sections").mkdir(parents=True, exist_ok=True)
    (SL / "figures").mkdir(exist_ok=True)
    slides, backups = parse((SL / "slide-script.md").read_text(encoding="utf-8"))
    copied: set = set()
    by_id = {s["id"]: s for s in slides}
    n = 0
    for part, (fname, short, long) in SECTIONS.items():
        out = [f"\\section[{short}]{{{long}}}\n"]
        for s in [x for x in slides if x["part"] == part]:
            if s["id"] == "S114":
                out.append("\\begin{hustdarkframe}\n\\centering\\vspace*{0.14\\paperheight}\n{\\Huge\\bfseries\\color{white} CẢM ƠN QUÝ THẦY CÔ\\\\VÀ CÁC BẠN ĐÃ LẮNG NGHE!\\par}\\vspace{1em}\n"
                           "{\\large\\color{white!85} Hỏi đáp (Q\\&A)\\par}\\vspace{0.8em}{\\normalsize\\color{white!85} Nhóm \\TenNhom\\ -- GVHD: \\GiangVien\\par}\n\\note{[S114] " + tex(s["noi"]) + "}\n\\end{hustdarkframe}\n")
            else:
                out.append(frame(s, copied))
            n += 1
        (SL / "sections" / f"{fname}.tex").write_text("\n".join(out), encoding="utf-8")
    bk = []
    for b in backups:
        ref = re.findall(r"S\d+", b["ref"])
        src = next((by_id[r] for r in ref if r in by_id and (re.findall(r"figures/([\w\-.]+\.png)", by_id[r]["hinh"]) or by_id[r]["id"] in EXTRAS)), None)
        s = {"id": (src["id"] if src and src["id"] in EXTRAS else b["id"]), "title": b["q"], "bullets": [b["a"], "Slide chính liên quan: " + b["ref"]], "hinh": src["hinh"] if src else "",
             "noi": f"{b['id']} - dự phòng cho câu hỏi: {b['q']}. Xem huong-dan/04-cau-hoi-van-dap.md.", "part": 8}
        bk.append(frame(s, copied, backup=True))
    (SL / "sections" / "08-du-phong.tex").write_text("\n".join(bk), encoding="utf-8")
    print(f"{n} main frames, {len(backups)} backup frames, {len(copied)} figures copied")


if __name__ == "__main__":
    main()
