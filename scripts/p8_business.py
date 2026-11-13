"""P8-C2: draft tables for report sections 2.1-2.3 (business, requirements, KPI) -> report/tables/p8_*.tex and
the block between the p8 markers at the end of huong-dan/05-nghiep-vu-nhap.md.   python scripts/p8_business.py

Numbers quoted in the data-limits table come from queries on olist_full / olist_dw (14/11/2026).
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABLES = ROOT / "report" / "tables"
MD = ROOT / "huong-dan" / "05-nghiep-vu-nhap.md"

# ---------------------------------------------------------------- 1. analysis points on the BPMN
ANALYSIS = [
    ("A1", "Quy trình đơn: đặt hàng và thanh toán", "D1, D2, D5", "GMV, Orders, AOV, cơ cấu thanh toán, số kỳ trả góp", "thời gian, sản phẩm, địa lý, hình thức thanh toán"),
    ("A2", "Quy trình đơn: duyệt thanh toán", "D3", "approval_hours (trung bình 10,3 giờ)", "thời gian, trạng thái đơn"),
    ("A3", "Quy trình đơn: seller chuẩn bị và bàn giao", "D3, D6", "handling_days (trung bình 2,9 ngày)", "seller, vùng, thời gian"),
    ("A4", "Quy trình đơn: vận chuyển và giao hàng", "D3, D4", "Avg lead days, On-time rate, Promised vs actual, Freight ratio", "bang và vùng, khoảng cách, thời gian"),
    ("A5", "Quy trình đơn: khách đánh giá", "D5", "Avg review, % negative, Repeat customer rate", "mức trễ giao hàng, nhóm ngành, khách"),
    ("A6", "Quy trình đơn: hủy hoặc không khả dụng", "D1, D3", "Cancel rate, phễu trạng thái đơn", "trạng thái, thời gian"),
    ("A7", "Quy trình seller: khách tiềm năng để lại thông tin (MQL)", "D6", "MQLs theo tháng liên hệ đầu", "kênh (origin), thời gian"),
    ("A8", "Quy trình seller: SDR sàng lọc, SR tư vấn", "D6", "Avg days to close", "nhân viên sales (SDR, SR), phân khúc"),
    ("A9", "Quy trình seller: chốt thương vụ", "D6", "Won deals, MQL to won rate", "kênh, phân khúc kinh doanh"),
    ("A10", "Quy trình seller: seller bán đơn đầu tiên", "D6, D2", "Sellers with first sale, Won to first sale rate, GMV 90 ngày đầu", "kênh, thời gian, seller"),
    ("A11", "Vận hành dữ liệu: nạp và kiểm thử kho", "D7", "số dòng nạp, thời gian chạy, số dòng bị loại, số kiểm thử đạt", "lô nạp, bảng"),
]
ANALYSIS_COLS = ["Mã", "Bước trên quy trình (BPMN)", "Dashboard", "KPI", "Khía cạnh phân tích"]

# ---------------------------------------------------------------- 2. business model canvas
BMC = [
    ("Phân khúc khách hàng", "Ai mua và mua ở đâu; ai là seller bán tốt?", "số khách, Repeat customer rate, tỷ trọng vùng (Sudeste 65,4% GMV)", "D1, D4, D5"),
    ("Giá trị đề xuất", "Giao có đúng hạn và đủ rẻ để seller nhỏ vẫn bán được?", "On-time rate, Promised vs actual, Freight ratio (16,6%)", "D3, D4"),
    ("Kênh", "Kênh marketing nào đưa về seller chốt được?", "MQLs, MQL to won rate theo kênh", "D6"),
    ("Quan hệ khách hàng", "Khách có hài lòng không; đội sales chốt nhanh không?", "Avg review (4,09), % negative, Avg days to close", "D5, D6"),
    ("Dòng doanh thu", "Doanh số trên sàn tăng hay giảm?", "GMV, Orders, AOV (dữ liệu không có doanh thu của Olist)", "D1, D2"),
    ("Nguồn lực chính", "Nền tảng và đội sales đang phục vụ bao nhiêu seller?", "số seller có đơn, số thương vụ trên mỗi nhân viên sales", "D6"),
    ("Hoạt động chính", "Xử lý đơn và thu hút seller mất bao lâu ở từng chặng?", "approval_hours, handling_days, Avg lead days, Avg days to close", "D3, D6"),
    ("Đối tác chính", "Seller và đơn vị vận chuyển nào làm chậm đơn?", "tỷ lệ trễ theo seller và bang, scorecard seller", "D3, D4, D6"),
    ("Cấu trúc chi phí", "Chi phí vận chuyển chiếm bao nhiêu giá hàng?", "Freight ratio theo vùng và nhóm ngành (dữ liệu không có chi phí marketing)", "D2, D4"),
]
BMC_COLS = ["Khối Canvas", "Câu hỏi quản trị", "Chỉ số", "Dashboard"]

# ---------------------------------------------------------------- 3. current state -> requirement
GAP = [
    ("Hai hệ thống nguồn (bán hàng, CRM) tách rời, chỉ gặp nhau qua seller_id", "Tích hợp bằng chiều dùng chung dim_seller để hỏi được seller đến từ kênh nào thì bán tốt", "2.4, 3.4"),
    ("Báo cáo phải nối nhiều bảng chuẩn hóa của hệ thống giao dịch", "Mô hình chiều (fact và dimension) và data mart tổng hợp sẵn cho từng chủ điểm", "3.5"),
    ("Trạng thái đơn chỉ là giá trị hiện tại, không có lịch sử các mốc", "Bảng fact snapshot tích luỹ ghi 5 mốc thời gian và thời gian từng chặng", "3.5"),
    ("Địa chỉ khách chỉ giữ bản mới nhất", "SCD loại 2 cho dim_customer để gắn đơn với địa chỉ tại ngày mua", "3.4"),
    ("Dữ liệu có nhiều lỗi (45 loại bất thường, 58 phép kiểm tra)", "Tầng ODS gắn cờ lỗi và ghi dòng bị loại kèm lý do, không xoá âm thầm", "3.3"),
    ("Mỗi báo cáo có thể định nghĩa KPI khác nhau (GMV, Orders)", "Định nghĩa mỗi KPI một lần bằng DAX và đối chiếu với SQL", "2.3"),
    ("Ngày dự kiến giao quá rộng (trung bình 24,4 ngày so với thực tế 12,6 ngày) nên chỉ số đúng hạn không phản ánh trải nghiệm", "KPI ngày hứa giao so với ngày giao thực tế, phân tích theo mức trễ", "2.3, 3.1"),
    ("Không có công cụ giám sát chất lượng nạp dữ liệu", "Nhật ký etl_log và dashboard D7", "3.3, 4"),
]
GAP_COLS = ["Hiện trạng", "Yêu cầu cải tiến", "Mục báo cáo"]

# ---------------------------------------------------------------- 4. audience
AUDIENCE = [
    ("Ban điều hành", "Doanh thu có tăng không? Giao hàng và khách hàng ra sao?", "D1", "hằng tuần, hằng tháng"),
    ("Quản lý kinh doanh và danh mục", "Nhóm ngành nào bán chạy; giá và phí vận chuyển theo ngành?", "D2", "hằng tuần"),
    ("Quản lý vận hành và logistics", "Chặng nào chậm; bang nào trễ nhiều; phí vận chuyển theo khoảng cách?", "D3, D4", "hằng ngày đến hằng tuần"),
    ("Chăm sóc khách hàng", "Vì sao review thấp; khách nào quay lại?", "D5", "hằng tuần"),
    ("Quản lý seller và đội sales (SDR, SR)", "Kênh nào chuyển đổi tốt; seller từ funnel bán ra sao?", "D6", "hằng tuần, hằng tháng"),
    ("Quản trị dữ liệu", "Lần nạp gần nhất có đúng không; dòng nào bị loại?", "D7", "hằng ngày (mỗi lần chạy ETL)"),
]
AUDIENCE_COLS = ["Người dùng", "Câu hỏi", "Dashboard", "Tần suất xem"]

# ---------------------------------------------------------------- 5. topics - aspects - metrics
TOPICS = [
    ("Bán hàng", "thời gian, sản phẩm (danh mục, nhóm ngành), địa lý", "GMV, Orders, AOV, tăng trưởng MoM và YoY, tỷ trọng 80/20"),
    ("Xử lý đơn", "thời gian, địa lý, trạng thái, seller", "approval_hours, handling_days, transit_days, Avg lead days, On-time rate, Promised vs actual, Cancel rate"),
    ("Thanh toán", "thời gian, hình thức thanh toán", "cơ cấu hình thức, số kỳ trả góp, giá trị thanh toán"),
    ("Trải nghiệm khách", "mức trễ, nhóm ngành, khách, vùng", "Avg review, % negative, Repeat customer rate, RFM, cohort"),
    ("Seller", "seller, thời gian, vùng", "GMV theo seller, tỷ lệ trễ, điểm review, tháng không bán"),
    ("Thu hút seller", "kênh (origin), thời gian, phân khúc, nhân viên sales", "MQLs, Won deals, MQL to won rate, Avg days to close, Won to first sale rate, GMV 90 ngày đầu"),
]
TOPICS_COLS = ["Chủ điểm", "Khía cạnh", "Chỉ số"]

# ---------------------------------------------------------------- 6. data limits -> KPI
LIMITS = [
    ("GMV có hai cách đo", "GMV (chỉ đơn không thuộc nhóm Failed) là 13.494.400,74 BRL; tổng giá hàng của mọi đơn là 13.591.643,70 BRL (chênh 97.242,96 BRL)", "Dashboard dùng GMV loại đơn Failed; ghi rõ định nghĩa cạnh con số"),
    ("Orders khác Orders placed", "Orders (đơn có doanh thu) là 98.199; Orders placed (mọi đơn đã đặt) là 99.441; chênh 1.242 đơn gồm 1.234 đơn hủy hoặc không khả dụng và 8 đơn không có dòng hàng", "AOV = GMV chia Orders; Cancel rate chia Orders placed"),
    ("380 so với 379 seller có đơn", "380 deal đã chốt có đơn ở mọi trạng thái; chỉ 379 seller có đơn không thuộc nhóm Failed (first_sale_date)", "KPI Sellers with first sale dùng 379; con số 380 chỉ xuất hiện ở khám phá dữ liệu"),
    ("Năm 2016 thưa, tháng 2018-09 bị cắt", "2016 chỉ có 329 đơn; 2018-09 có 16 đơn và 2018-10 có 4 đơn (nguồn dừng giữa tháng)", "Dashboard D1 đến D6 lọc cửa sổ 2017-01 đến 2018-08 (cột InWindow); xu hướng ngoài cửa sổ không diễn giải"),
    ("Đơn có nhiều review", "547 trong 98.673 đơn có review có từ 2 đến 3 review (tổng 99.224 review); điểm trung bình tính theo review là 4,0864, theo đơn là 4,0868", "Avg review tính theo review; chênh lệch nhỏ nên không đổi kết luận"),
    ("Điểm review nhóm đúng hạn", "Trước 07/11 đơn chưa giao bị tính vào nhóm đúng hạn nên điểm là 4,21; sau khi thêm is_delivered vào fact_review điểm đúng là 4,29", "Sửa ở tầng kho (cột is_delivered), không sửa ở Power BI"),
]
LIMITS_COLS = ["Giới hạn", "Số liệu", "Cách xử lý trong KPI"]


def esc(s: str) -> str:
    s = str(s).replace("\\", "\\textbackslash{}")
    for a, b in [("_", "\\_"), ("&", "\\&"), ("%", "\\%"), ("#", "\\#")]:
        s = s.replace(a, b)
    return s


def tex(cols, rows, caption, label, widths, size="scriptsize"):
    head = " & ".join("\\textbf{%s}" % esc(c) for c in cols) + "\\\\\\midrule"
    body = "\n".join(" & ".join(esc(v) for v in r) + "\\\\" for r in rows)
    ws = [float(w.replace("cm", "")) for w in widths]
    k = (15.7 - 0.42 * len(ws)) / sum(ws)  # fit the 16 cm text width (column padding included)
    spec = "".join("p{%.2fcm}" % (x * k) for x in ws)
    return ("\\begin{table}[htbp]\\centering\\%s\\caption{%s}\\label{%s}\n\\begin{tabular}{%s}\\toprule\n%s\n%s\n\\bottomrule\\end{tabular}\\end{table}\n"
            % (size, caption, label, spec, head, body))


def md_table(cols, rows):
    out = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    out += ["| " + " | ".join(str(v).replace("|", "\\|") for v in r) + " |" for r in rows]
    return "\n".join(out)


TABLES.mkdir(exist_ok=True)
SPECS = [
    ("p8_analysis_points", ANALYSIS_COLS, ANALYSIS, "Điểm phân tích trên quy trình: bước BPMN, dashboard, KPI và khía cạnh phân tích", "tab:diem-phan-tich", ["0.9cm", "4.4cm", "1.9cm", "4.6cm", "4.3cm"]),
    ("p8_bmc_questions", BMC_COLS, BMC, "Business Model Canvas: câu hỏi quản trị, chỉ số và dashboard tương ứng", "tab:bmc-cau-hoi", ["3.0cm", "4.6cm", "6.0cm", "2.2cm"]),
    ("p8_gap", GAP_COLS, GAP, "Hiện trạng và yêu cầu cải tiến", "tab:hien-trang", ["6.4cm", "7.0cm", "1.8cm"]),
    ("p8_audience", AUDIENCE_COLS, AUDIENCE, "Đối tượng sử dụng, câu hỏi, dashboard và tần suất xem", "tab:doi-tuong", ["3.6cm", "6.0cm", "1.8cm", "3.6cm"]),
    ("p8_topics", TOPICS_COLS, TOPICS, "Bảng chủ điểm, khía cạnh và chỉ số", "tab:chu-diem-khia-canh", ["2.6cm", "5.0cm", "7.6cm"]),
    ("p8_data_limits", LIMITS_COLS, LIMITS, "Giới hạn của dữ liệu ảnh hưởng tới KPI", "tab:gioi-han", ["3.0cm", "7.4cm", "4.8cm"]),
]
for name, cols, rows, cap, lab, w in SPECS:
    (TABLES / f"{name}.tex").write_text(tex(cols, rows, cap, lab, w), encoding="utf-8")

# ---------------------------------------------------------------- markdown block
BLOCK = f"""<!-- p8:start (sinh bởi scripts/p8_business.py; đừng sửa tay trong khối này) -->
## 8. Điểm phân tích trên quy trình (P8)
Mỗi điểm phân tích có mã A1, A2… đặt trên BPMN (các hình thoi vàng "📊" ở mục 1 và 2): bước nào của quy trình, dashboard nào, KPI nào và phân tích theo khía cạnh nào.

{md_table(ANALYSIS_COLS, ANALYSIS)}

## 9. Business Model Canvas: từ khối Canvas đến dashboard
{md_table(BMC_COLS, BMC)}

Lưu ý: dữ liệu chỉ có giá hàng và phí vận chuyển, không có doanh thu hay chi phí marketing của Olist; vì vậy ô *dòng doanh thu* và *cấu trúc chi phí* chỉ có thể dùng GMV và phí vận chuyển làm chỉ số thay thế.

## 10. Hiện trạng và yêu cầu cải tiến
{md_table(GAP_COLS, GAP)}

## 11. Đối tượng sử dụng dashboard
{md_table(AUDIENCE_COLS, AUDIENCE)}

## 12. Chủ điểm, khía cạnh và chỉ số
{md_table(TOPICS_COLS, TOPICS)}

## 13. Giới hạn của dữ liệu ảnh hưởng tới KPI
{md_table(LIMITS_COLS, LIMITS)}
<!-- p8:end -->
"""
s = MD.read_text(encoding="utf-8")
if "<!-- p8:start" in s:
    s = re.sub(r"<!-- p8:start.*?<!-- p8:end -->\n", lambda m: BLOCK, s, flags=re.S)
else:
    s = s.rstrip("\n") + "\n\n" + BLOCK
MD.write_text(s, encoding="utf-8", newline="\n")
print("tables:", [x[0] for x in SPECS])
