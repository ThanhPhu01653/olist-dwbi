"""P8-G: general dashboard checklist (huong-dan/dashboards/README.md) and a per-dashboard coverage section (12) appended to D1..D7.md.
Idempotent: the section of each D*.md sits between <!-- p8:start --> and <!-- p8:end --> and is replaced on re-run. Run AFTER scripts/gen_dashboard_docs.py
(which rewrites D*.md from scratch).   python scripts/p8_dashboard_checklist.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "huong-dan" / "dashboards"

# ---- theme: red must stay a warning colour, not a series colour
theme_path = ROOT / "powerbi" / "theme.json"
theme = json.loads(theme_path.read_text(encoding="utf-8"))
if "#D64545" in theme.get("dataColors", []):
    theme["dataColors"] = [c if c != "#D64545" else "#4A5568" for c in theme["dataColors"]]
    theme_path.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("theme.json: red removed from dataColors (kept as the 'bad' colour)")

CHECK = [
    ("Định dạng số", "mọi số trên dashboard dùng đơn vị rút gọn và dấu phân cách; phần trăm 1 chữ số thập phân", "số đơn 12.3K (không phải 12.345); tiền 13.5M; 12,4% (không phải 12,39% hoặc 12%)"),
    ("Tiêu đề dạng câu hỏi", "mỗi visual có tiêu đề là một câu hỏi mà visual trả lời", "\"GMV tháng này tăng hay giảm so với tháng trước?\""),
    ("Màu đỏ chỉ để cảnh báo", "đỏ chỉ dùng cho giá trị xấu hoặc vượt ngưỡng; màu dữ liệu thường dùng xanh, cam, tím", "theme.json không còn đỏ trong dataColors; đỏ chỉ ở định dạng có điều kiện"),
    ("Định dạng có điều kiện", "dùng DAX trả về màu (Color On-time rate…) cho card, bảng, bản đồ", "xem mục 7 của từng D*.md và `powerbi/measures.md`"),
    ("Slicer phân cấp và drill-down (OLAP)", "slicer theo phân cấp (Năm → Quý → Tháng; Vùng → Bang) và biểu đồ có drill-down / drill-up", "Date hierarchy, Geography hierarchy, Product hierarchy trong `powerbi/model.md`"),
    ("Drill-through và tooltip", "chuột phải một điểm để nhảy sang trang chi tiết (drill-through); di chuột hiện trang tooltip", "trang chi tiết đơn, tooltip theo tháng, bang, kênh"),
    ("Chuỗi thời gian có dự báo", "line chart theo tháng có đường dự báo (Analytics → Forecast) để nêu xu thế và mùa", "chỉ cho chuỗi đủ dài; nêu rõ giới hạn 20 tháng dữ liệu"),
    ("Publish web và mã QR", "publish báo cáo công khai (không cần đăng nhập) và in mã QR của link", "`powerbi/model.md` mục 9; mã QR tạo từ link"),
]

# ---- per-dashboard specifics
FMT = {
    "D1": [("GMV", "tiền", '`#,0.0,,"M"` → 13.5M'), ("Orders", "số", '`#,0.0,"K"` → 98.2K'), ("AOV", "tiền", '`#,0.0` → 137.4'), ("On-time rate, Cancel rate", "phần trăm", "`0.0%` → 93.2%"), ("Avg review", "điểm", "`0.00` → 4.09")],
    "D2": [("GMV", "tiền", '`#,0.0,,"M"` hoặc `#,0.0,"K"` theo cỡ'), ("Số đơn", "số", '`#,0.0,"K"`'), ("Freight ratio", "phần trăm", "`0.0%`"), ("Giá TB", "tiền", "`#,0.0`")],
    "D3": [("Avg lead days, Avg promised days", "ngày", "`0.0` → 12.6"), ("On-time rate, Late rate, Cancel rate", "phần trăm", "`0.0%`"), ("Orders placed", "số", '`#,0.0,"K"`')],
    "D4": [("GMV theo bang", "tiền", '`#,0.0,"K"` hoặc `#,0.0,,"M"`'), ("Freight ratio", "phần trăm", "`0.0%`"), ("Khoảng cách", "km", "`#,0`")],
    "D5": [("Avg review", "điểm", "`0.00`"), ("% negative, Repeat customer rate", "phần trăm", "`0.0%`"), ("Giá trị thanh toán", "tiền", '`#,0.0,,"M"`'), ("Số kỳ trả góp TB", "số", "`0.0`")],
    "D6": [("MQLs, Won deals", "số", "`#,0`"), ("MQL to won rate, Won to first sale rate", "phần trăm", "`0.0%`"), ("Avg days to close", "ngày", "`0.0`"), ("GMV seller", "tiền", '`#,0.0,"K"`')],
    "D7": [("Số dòng nạp", "số", '`#,0.0,"K"` hoặc `#,0`'), ("Thời gian chạy", "giây", "`0.0`"), ("pass_pct", "phần trăm", "`0.0%`")],
}
SPEC = {
    # dashboard: (slicer/drill, drill-through + tooltip, forecast)
    "D1": ("Slicer năm và quý dạng phân cấp; line chart GMV theo Năm → Quý → Tháng có nút drill-down / drill-up; treemap Nhóm ngành → Danh mục.",
           "Drill-through: chuột phải một vùng trên cột \"Vùng\" → trang D4 lọc theo vùng; tooltip: trang `Tooltip_Thang` (GMV, Orders, AOV, On-time rate của tháng đang trỏ).",
           "Line chart GMV theo tháng: Analytics → Forecast, 3 điểm, độ tin cậy 95%. Dữ liệu chỉ 20 tháng nên đặt Seasonality để Power BI tự chọn và ghi chú: mùa vụ theo năm chưa đủ dữ liệu (xem mục 3.1 của báo cáo)."),
    "D2": ("Slicer Quý → Tháng; matrix mở Quý → Tháng; Product hierarchy (nhóm ngành → danh mục → sản phẩm) trên treemap, Pareto và matrix.",
           "Drill-through: chuột phải một danh mục → trang chi tiết sản phẩm của danh mục; tooltip `Tooltip_Danh_muc` (GMV, tỷ trọng, giá TB, Freight ratio).",
           "Không áp dụng: D2 phân tích theo danh mục, không phải chuỗi thời gian dài; xu thế theo tháng nằm ở D1."),
    "D3": ("Slicer Năm → Quý → Tháng và Vùng → Bang; bản đồ drill Vùng → Bang → Thành phố.",
           "Drill-through: chuột phải một bang → trang chi tiết đơn của bang (bảng đơn trễ); tooltip `Tooltip_Bang` (Avg lead days, Late rate, Orders).",
           "Line chart Avg lead days theo tháng có Forecast 3 điểm (95%); nêu rõ chỉ dùng để thấy hướng, vì đoạn dữ liệu ngắn."),
    "D4": ("Slicer Vùng → Bang; Geography hierarchy Vùng → Bang → Thành phố → Zip; bản đồ drill từ bang xuống thành phố.",
           "Drill-through: chuột phải một bang → trang D3 lọc theo bang; tooltip `Tooltip_Bang_phi` (GMV, Freight ratio, khoảng cách TB).",
           "Không áp dụng: D4 là phân tích địa lý, không phải chuỗi thời gian."),
    "D5": ("Slicer Năm → Quý → Tháng, Vùng → Bang; cohort drill từ năm xuống tháng.",
           "Drill-through: chuột phải một phân khúc RFM → bảng danh sách khách (ẩn mã khách khi chia sẻ công khai); tooltip `Tooltip_Muc_tre` (số review, điểm TB, % tiêu cực theo nhóm trễ).",
           "Line chart Avg review theo tháng có Forecast 3 điểm (95%), nêu giới hạn dữ liệu ngắn."),
    "D6": ("Slicer Nhóm kênh → Origin (phân cấp Lead origin); bảng seller drill theo bang.",
           "Drill-through: chuột phải một seller → trang `fact_seller_monthly` (đường GMV theo tháng); tooltip `Tooltip_Kenh` (MQLs, Won deals, tỷ lệ chốt, cỡ mẫu).",
           "Không áp dụng cho dự báo: chuỗi MQL theo tháng chỉ có 11 tháng và dừng giữa 2018; dùng cột theo tháng và nêu xu thế bằng lời."),
    "D7": ("Slicer khoảng batch_id, mode, status (không có phân cấp thời gian vì dữ liệu theo lô).",
           "Drill-through: chuột phải một lô → trang `job_run` của lô; tooltip `Tooltip_Lo` (số dòng đọc, chèn, loại, thời gian).",
           "Không áp dụng: dữ liệu theo lô chạy, không phải chuỗi thời gian kinh doanh."),
}
NOFORECAST = {"D2", "D4", "D6", "D7"}


def questions(md: str) -> list[str]:
    m = re.search(r"## 2\..*?\n(.*?)\n## 3\.", md, flags=re.S)
    return [re.sub(r"^[-*]\s*", "", ln).strip() for ln in (m.group(1).splitlines() if m else []) if ln.strip().startswith(("-", "*"))]


rows_status = {}
for name in FMT:
    f = DIR / f"{name}.md"
    s = f.read_text(encoding="utf-8")
    qs = questions(s)
    sl, dt, fc = SPEC[name]
    fmt = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in FMT[name])
    titles = "\n".join(f"- {q if q.endswith('?') else q + '?'}" for q in qs)
    status = [
        ("Định dạng số", "bổ sung (P8)", "xem bảng định dạng bên dưới"),
        ("Tiêu đề dạng câu hỏi", "bổ sung (P8)", "xem danh sách tiêu đề bên dưới"),
        ("Màu đỏ chỉ để cảnh báo", "đã có", "mục 7: đỏ chỉ ở định dạng có điều kiện; theme.json không dùng đỏ cho dữ liệu"),
        ("Định dạng có điều kiện", "đã có", "mục 7 và mục 8 (DAX màu, cảnh báo)"),
        ("Slicer phân cấp và drill-down", "đã có + bổ sung (P8)", sl),
        ("Drill-through và tooltip", "bổ sung (P8)", dt),
        ("Chuỗi thời gian có dự báo", "không áp dụng" if name in NOFORECAST else "bổ sung (P8)", fc),
        ("Publish web và mã QR", "đã có", "cùng báo cáo với các trang khác: `powerbi/model.md` mục 9; thêm mã QR của link (xem README.md trong thư mục này)"),
    ]
    rows_status[name] = status
    table = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in status)
    block = f"""<!-- p8:start (sinh bởi scripts/p8_dashboard_checklist.py; đừng sửa tay trong khối này) -->
## 12. Đáp ứng checklist chung (P8)

Checklist chung của mọi dashboard ở [`README.md`](README.md). Với {name}:

| Mục checklist | Trạng thái | Cách đáp ứng trong {name} |
| --- | --- | --- |
{table}

**Định dạng số (đặt trong *Measure tools → Format → Custom* hoặc *Display units* của visual):**

| Chỉ số | Loại | Định dạng |
| --- | --- | --- |
{fmt}

**Tiêu đề visual dạng câu hỏi** (lấy từ mục 2; mỗi visual chọn một câu phù hợp làm tiêu đề):

{titles}
<!-- p8:end -->
"""
    if "<!-- p8:start" in s:
        s = re.sub(r"<!-- p8:start.*?<!-- p8:end -->\n", lambda m: block, s, flags=re.S)
    else:
        s = s.rstrip("\n") + "\n\n" + block
    f.write_text(s, encoding="utf-8", newline="\n")

# ---- README.md (general checklist + matrix)
mat_head = "| Mục checklist | " + " | ".join(FMT) + " |\n| --- | " + " | ".join("---" for _ in FMT) + " |"
sym = {"đã có": "✓", "đã có + bổ sung (P8)": "✓ +", "bổ sung (P8)": "+", "không áp dụng": "–"}
mat = "\n".join(f"| {CHECK[i][0]} | " + " | ".join(sym[rows_status[n][i][1]] for n in FMT) + " |" for i in range(len(CHECK)))
chk = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in CHECK)
readme = f"""# Hướng dẫn dựng dashboard: checklist chung (P8)

Thư mục này chứa hướng dẫn từng dashboard `D1.md` … `D7.md`. Trang này là **checklist chung** rút từ nhận xét mẫu của barem; mỗi file D*.md có mục 12 ghi dashboard đó đáp ứng từng mục thế nào. Ký hiệu trong ma trận: **✓** đã có trong hướng dẫn, **+** bổ sung ở P8, **✓ +** đã có và bổ sung thêm, **–** không áp dụng (lý do ở mục 12).

## 1. Checklist chung

| Mục | Yêu cầu | Ví dụ / nơi xem |
| --- | --- | --- |
{chk}

## 2. Ma trận đáp ứng

{mat_head}
{mat}

## 3. Hướng dẫn chi tiết

**Định dạng số.** Chọn visual → *Format → Display units* (Thousands, Millions) và *Value decimal places = 1*; với measure, dùng *Measure tools → Format → Custom*: `#,0.0,,"M"` (triệu), `#,0.0,"K"` (nghìn), `0.0%` (phần trăm một chữ số thập phân). Dấu phân cách hàng nghìn bật trong *Format → Value*. Luôn ghi đơn vị (BRL, ngày, %) ở tiêu đề hoặc nhãn trục.

**Tiêu đề dạng câu hỏi.** Mỗi visual có tiêu đề là câu hỏi mà nó trả lời (xem mục 12 của từng D*.md); tiêu đề trang cũng là câu hỏi chính của dashboard.

**Màu đỏ chỉ để cảnh báo.** Đỏ (`bad` trong `theme.json`) chỉ dùng cho giá trị xấu hoặc vượt ngưỡng qua định dạng có điều kiện; bảng màu dữ liệu của theme không còn đỏ.

**Định dạng có điều kiện.** Dùng measure DAX trả về mã màu (`Color On-time rate`, `Color Cancel rate`…, xem `powerbi/measures.md`) và gán qua *Conditional formatting → Field value*.

**Slicer phân cấp và drill-down (OLAP).** Slicer thời gian: kéo `Năm → Quý → Tháng` vào một slicer (kiểu phân cấp); slicer địa lý: `Vùng → Bang`. Với biểu đồ, bật *Drill* (mũi tên) và *Expand all down one level*; thao tác này tương ứng roll-up và drill-down của OLAP (`sql/60_olap_examples/`).

**Drill-through.** Tạo trang chi tiết, kéo trường cần lọc vào ô *Drill through → Add drill-through fields here*; người xem chuột phải một điểm → *Drill through*. Nút quay lại được thêm tự động.

**Tooltip.** Tạo trang mới, *Format → Page information → Allow use as tooltip = On*, *Page size = Tooltip*; đặt vài visual nhỏ (card, cột); ở visual nguồn, *Format → Tooltips → Type = Report page* và chọn trang tooltip.

**Chuỗi thời gian có dự báo.** Chọn line chart theo tháng → ngăn *Analytics* → *Forecast → Add* → *Forecast length = 3 points*, *Confidence interval = 95%*. Dữ liệu chỉ có 20 tháng (2017-01 → 2018-08) và mùa vụ theo năm chưa đủ dữ liệu để kết luận (báo cáo mục 3.1), nên dự báo chỉ dùng để thấy hướng đi; ghi chú điều này cạnh biểu đồ. Phân tích xu thế, mùa tuần và Black Friday đã có sẵn ở `handoff/2026-11-14-P8-eda.md` mục D3 để minh hoạ.

**Publish web và mã QR.** Publish theo `powerbi/model.md` mục 9 (File → Embed report → Publish to web). Mã QR: mở link công khai trong Microsoft Edge → menu ⋯ → *Share* → *Create QR code for this page* (hoặc bất kỳ công cụ tạo QR nào), lưu ảnh và đặt vào slide cuối và báo cáo (`figures/4_qr_dashboard.png`, do nhóm tạo sau khi publish).

## 4. Trạng thái đáp ứng
Các mục **+** là yêu cầu cho người dựng Power BI (chưa có `.pbix` nào được dựng ở thời điểm P8). Sau khi dựng, đánh dấu từng mục trong mục 11 của D*.md và bổ sung ảnh chụp vào báo cáo.
"""
(DIR / "README.md").write_text(readme, encoding="utf-8", newline="\n")
print("README.md and D1-D7 section 12 written")
