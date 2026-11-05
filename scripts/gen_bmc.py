"""Draw the (draft) Business Model Canvas of Olist -> figures/3-2-3_business_model_canvas.png.  python scripts/gen_bmc.py"""
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
BOXES = {  # name: (x, y, w, h, colour, lines)
    "8. Đối tác chính": (0, 2, 2, 4, "#DCEBF7", ["Các marketplace lớn", "Đơn vị vận chuyển / logistics", "Đơn vị thanh toán (thẻ, boleto, voucher)", "Seller"]),
    "7. Hoạt động chính": (2, 4, 2, 2, "#DCEBF7", ["Thu hút và chốt seller", "Tích hợp sản phẩm lên sàn", "Xử lý đơn: duyệt, bàn giao, giao", "Thu thập đánh giá"]),
    "6. Nguồn lực chính": (2, 2, 2, 2, "#DCEBF7", ["Nền tảng công nghệ", "Dữ liệu đơn hàng và review", "Đội marketing và sales (SDR, SR)", "Hợp đồng logistics"]),
    "2. Giá trị đề xuất": (4, 2, 2, 4, "#FDE9D2", ["Seller nhỏ bán trên nhiều marketplace qua MỘT hợp đồng, MỘT hệ thống", "Người mua: mua ở sàn quen, vận chuyển thống nhất"]),
    "4. Quan hệ khách hàng": (6, 4, 2, 2, "#E2F2E8", ["Seller: sales tư vấn, onboarding, hỗ trợ", "Người mua: đánh giá sau giao, hậu mãi"]),
    "3. Kênh": (6, 2, 2, 2, "#E2F2E8", ["Thu hút seller: organic, paid search, social, email, referral, direct, display (landing page)", "Kênh bán: marketplace đối tác"]),
    "1. Phân khúc khách hàng": (8, 2, 2, 4, "#E2F2E8", ["Người bán: doanh nghiệp / hộ kinh doanh nhỏ (reseller, manufacturer...)", "Người mua cuối tại Brazil (96.096 khách)"]),
    "9. Cơ cấu chi phí": (0, 0, 5, 2, "#F6DADA", ["Công nghệ và vận hành nền tảng; hậu cần và vận chuyển", "Marketing (paid search, display) và đội sales", "Xử lý thanh toán; chăm sóc khách"]),
    "5. Dòng doanh thu": (5, 0, 5, 2, "#F6DADA", ["(suy luận, cần xác nhận) phí / hoa hồng trên đơn bán qua nền tảng, phí dịch vụ seller", "Dữ liệu: GMV 13,49 triệu BRL; phí vận chuyển ≈ 16,6% giá hàng"]),
}
fig, ax = plt.subplots(figsize=(16, 9.5), dpi=200)
for title, (x, y, w, h, col, lines) in BOXES.items():
    ax.add_patch(Rectangle((x, y), w, h, facecolor=col, edgecolor="#4B5563", linewidth=1.2))
    ax.text(x + 0.06, y + h - 0.12, title, fontsize=11, fontweight="bold", va="top")
    width = 34 if w <= 2 else 78
    ypos = y + h - 0.45
    for ln in lines:
        wrapped = textwrap.fill("• " + ln, width)
        ax.text(x + 0.08, ypos, wrapped, fontsize=8.6, va="top")
        ypos -= 0.2 * (wrapped.count("\n") + 1) + 0.16
ax.set_xlim(0, 10); ax.set_ylim(0, 6.5); ax.axis("off")
ax.text(5, 6.35, "Business Model Canvas – Olist (bản nháp để nhóm sửa)", ha="center", fontsize=14, fontweight="bold")
fig.savefig(ROOT / "figures" / "3-2-3_business_model_canvas.png", bbox_inches="tight")
print("ok")
