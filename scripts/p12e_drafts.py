"""P12e: redraw of the draft diagrams for the slides (BPMN x2, canvas, business/requirement trees, OLTP ERD, three data flows, taxonomy).

Drawn at insertion size with scripts/p12e_canvas.py (text >= 9.3 pt after insertion).  The old drafts in figures/ are NOT touched (the report keeps them);
bootstrap_report.py is not run.  Run: python scripts/p12e_drafts.py   -> figures/slide/*.png
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from p12e_canvas import BLUE, GREEN, GREY, ORANGE, PINK, PURPLE, TEAL, WHITE, YELLOW, Canvas, bottom, left, right, top  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "scripts/p12e_drafts.py"
NGHIEP_VU = ROOT / "huong-dan" / "05-nghiep-vu-nhap.md"


# ------------------------------------------------------------------------------------------------ BPMN
def bpmn_order() -> None:
    c = Canvas("full_ket")
    steps = ["Đặt hàng,\nthanh toán", "Duyệt\nthanh toán", "Seller chuẩn\nbị, bàn giao", "Vận chuyển\nvà giao", "Khách\nđánh giá"]
    tags = ["purchase_ts\npayment", "approved_ts", "carrier_ts", "delivered_ts", "review_score"]
    w, g = 150, 27.5
    bs = []
    for i, s in enumerate(steps):
        bs.append(c.box(i * (w + g), 30, w, 100, s, fill=GREEN, px=20, bold=True))
        if i:
            c.arrow(right(bs[i - 1]), left(bs[i]))
    for i, t in enumerate(tags):
        b = c.box(i * (w + g) + 10, 190, w - 20, 70, t, fill=YELLOW, px=19, dashed=True)
        c.line(bottom(bs[i]), top(b), color="#b45309", lw=1.4)
    c.text(430, 12, "Quy trình đơn hàng", px=19, color="#374151")
    c.text(c.W, 285, "ô vàng: điểm thu thập dữ liệu", px=19, ha="right", color="#b45309")
    nb = c.box(300, 290, 270, 52, "Hủy / không khả dụng: 1.234 đơn (1,24%)", fill="#F6DADA", px=19)
    c.arrow(bottom(bs[1]), (bs[1][0] + w / 2, 290), color="#b91c1c", dashed=True)
    c.save("3-2-1_bpmn_don_hang", SCRIPT)


def bpmn_seller() -> None:
    c = Canvas("full_ket")
    steps = ["MQL\n(lead)", "SDR sàng\nlọc lead", "SR tư vấn,\nchốt deal", "Deal chốt\n(won)", "Seller có\nđơn đầu"]
    tags = ["crm.mql", "", "", "crm.closed_\ndeals", "fact_lead_\nfunnel"]
    w, g = 150, 27.5
    bs = []
    for i, s in enumerate(steps):
        bs.append(c.box(i * (w + g), 60, w, 100, s, fill=BLUE if i < 3 else GREEN, px=20, bold=True))
        if i:
            c.arrow(right(bs[i - 1]), left(bs[i]))
    for i, t in enumerate(tags):
        if t:
            bx = i * (w + g) - 12
            b = c.box(bx, 215, min(w + 24, c.W - bx - 2), 52, t, fill=YELLOW, px=19, dashed=True)
            c.line(bottom(bs[i]), top(b), color="#b45309", lw=1.4)
    # durations over the arrows
    c.line((bs[0][0] + w / 2, 40), (bs[3][0] + w / 2, 40), color="#b91c1c", lw=2.0)
    c.text((bs[0][0] + bs[3][0]) / 2 + w / 2, 18, "liên hệ → chốt: TB 48,5 ngày", px=20, bold=True, color="#b91c1c")
    c.line((bs[3][0] + w / 2, 300), (bs[4][0] + w / 2, 300), color="#b91c1c", lw=2.0)
    c.text(bs[3][0] + w + 4, 330, "chốt → đơn đầu: TB 51,9 ngày", px=20, bold=True, color="#b91c1c", ha="center")
    c.save("3-2-2_bpmn_thu_hut_seller", SCRIPT)


# ------------------------------------------------------------------------------------------------ canvas
def canvas_bmc() -> None:
    c = Canvas("full_ket_ca")
    cw = 172
    cells = [  # title, x, y, w, h, fill, lines
        ("Đối tác chính", 0, 0, cw, 214, "#DCEBF7", ["Marketplace", "Vận chuyển", "Thanh toán", "Seller"]),
        ("Hoạt động", cw, 0, cw, 107, "#DCEBF7", ["Tìm seller", "Xử lý đơn", "Thu review"]),
        ("Nguồn lực", cw, 107, cw, 107, "#DCEBF7", ["Nền tảng", "Dữ liệu đơn", "Đội SDR, SR"]),
        ("Giá trị", 2 * cw, 0, cw, 214, "#FDE9D2", ["Seller nhỏ bán trên nhiều marketplace qua MỘT hợp đồng", "Người mua: vận chuyển thống nhất"]),
        ("Quan hệ KH", 3 * cw, 0, cw, 107, "#E2F2E8", ["Tư vấn seller", "Review sau giao"]),
        ("Kênh", 3 * cw, 107, cw, 107, "#E2F2E8", ["Organic, paid", "Marketplace"]),
        ("Phân khúc KH", 4 * cw, 0, c.W - 4 * cw, 214, "#E2F2E8", ["Seller: doanh nghiệp, hộ kinh doanh nhỏ", "Người mua tại Brazil (96.096 khách)"]),
        ("Cơ cấu chi phí", 0, 214, 430, 109, "#F6DADA", ["Công nghệ, vận hành, logistics", "Marketing và đội sales"]),
        ("Dòng doanh thu", 430, 214, c.W - 430, 109, "#F6DADA", ["(suy luận, cần xác nhận) phí, hoa hồng trên đơn", "Dữ liệu: GMV 13,49 triệu BRL"]),
    ]
    for title, x, y, w, h, fill, lines in cells:
        c.box(x + 1, y + 1, w - 2, h - 2, "", fill=fill, r=0, lw=1.0)
        c.text(x + 8, y + 16, title, px=19.5, bold=True, ha="left")
        yy = y + 36
        for ln in lines:
            wrapped = c.wrap("• " + ln, w - 6, 19)
            c.text(x + 8, yy, wrapped, px=19, ha="left", va="top")
            yy += 23 * (wrapped.count("\n") + 1) + 4
    c.save("3-2-3_business_model_canvas", SCRIPT)


# ------------------------------------------------------------------------------------------------ trees
SHORT = {"Quản trị dữ liệu và phân tích": "Dữ liệu, phân tích"}
PALETTE = [("#fff3a8", "#b59f00"), ("#d3efc2", "#5c9a3c"), ("#e3d3f7", "#8458b6"), ("#fbd5c0", "#c2623a"), ("#cfe3fb", "#3b6fb5"), ("#f8c8dc", "#b44a77")]


def parse_tree(png: str) -> tuple[str, dict[str, list[str]]]:
    txt = NGHIEP_VU.read_text(encoding="utf-8")
    m = re.search(r"<!-- png: " + re.escape(png) + r"\.png -->\s*```mermaid\s*mindmap\s*(.*?)```", txt, re.S)
    body = m.group(1).splitlines()
    root = re.search(r"root\(\((.*?)\)\)", body[0]).group(1)
    br: dict[str, list[str]] = {}
    cur = None
    for ln in body[1:]:
        if not ln.strip():
            continue
        if len(ln) - len(ln.lstrip()) == 4:
            cur = ln.strip()
            br[cur] = []
        else:
            br[cur].append(ln.strip())
    return root, br


def draw_tree(name: str, root: str, branches: dict[str, list[str]], note: str = "") -> None:
    import textwrap

    c = Canvas("full_ket")
    W, H = c.W, c.H
    n_leaf = sum(len(v) for v in branches.values())
    gap = 6
    row = (H - gap * (len(branches) - 1)) / n_leaf
    x_root, w_root, x_br, w_br, x_leaf = 0, 104, 120, 160, 296
    y = 0
    centers = []
    for k, (bn, leaves) in enumerate(branches.items()):
        fc, ec = PALETTE[k % len(PALETTE)]
        top_y = y
        for leaf in leaves:
            c.box(x_leaf, y + 1, W - x_leaf, row - 2, leaf, fill=fc, ec=ec, px=19, ha="left", lw=1.0, r=4, wrap=False)
            y += row
        mid = (top_y + y) / 2
        centers.append(mid)
        bh = max(50, len(leaves) * row - 8)
        c.box(x_br, mid - bh / 2, w_br, bh, SHORT.get(bn, bn), fill=fc, ec=ec, px=19.5, bold=True)
        c.line((x_br + w_br, mid), (x_leaf, mid), color=ec, lw=1.4)
        y += gap
    cy = sum(centers) / len(centers)
    c.box(x_root, cy - 50, w_root, 100, textwrap.fill(root, 11), fill="#1f3fbf", ec="#14287f", px=20, bold=True, tc="white", wrap=False)
    for mid in centers:
        c.line((x_root + w_root, cy), (x_br, mid), color="#6a6a6a", lw=1.6)
    c.save(name, SCRIPT)


def trees() -> None:
    root, br = parse_tree("3-2-5_cay_nghiep_vu")
    draw_tree("3-2-5_cay_nghiep_vu", root, br)
    root, br = parse_tree("3-2-6_cay_yeu_cau_phan_tich")
    items = list(br.items())
    draw_tree("3-2-6_cay_yeu_cau_phan_tich_a", root, dict(items[:3]))
    draw_tree("3-2-6_cay_yeu_cau_phan_tich_b", root, dict(items[3:]))


# ------------------------------------------------------------------------------------------------ OLTP ERD
def erd_oltp() -> None:
    c = Canvas("full_ket")
    w, h = 200, 64
    xs = [0, 215, 430]
    ys = [4, 125, 246]
    grid = [["customers", "orders", "order_reviews"], ["geolocation", "order_items", "order_payments"], ["sellers", "products", "category_\ntranslation"]]
    pos = {}
    for r, row in enumerate(grid):
        for k, t in enumerate(row):
            pos[t.replace("\n", "")] = c.box(xs[k], ys[r], w, h, t, fill=GREEN, px=19.5, bold=True)
    crm = {"mql": c.box(660, 20, 200, h, "mql\n(crm)", fill=BLUE, px=19.5, bold=True), "closed_deals": c.box(660, 246, 200, h, "closed_deals\n(crm)", fill=BLUE, px=19.5, bold=True)}
    rel = [("customers", "orders"), ("orders", "order_items"), ("orders", "order_payments"), ("orders", "order_reviews"), ("order_items", "products"), ("order_items", "sellers"),
           ("products", "category_translation"), ("customers", "geolocation"), ("sellers", "geolocation")]
    for a, b in rel:
        c.line(_mid(pos[a]), _mid(pos[b]), color="#374151", lw=1.6, z=0)
    c.line(_mid(crm["mql"]), _mid(crm["closed_deals"]), color="#374151", lw=1.6, z=0)
    sx = _mid(pos["sellers"])[0]
    red = "#b91c1c"
    c.line((760, 310), (760, 340), color=red, lw=1.8)
    c.line((760, 340), (sx, 340), color=red, lw=1.8)
    c.line((sx, 340), (sx, 310), color=red, lw=1.8)
    c.text(430, 326, "seller_id nối crm với oltp", px=19, bold=True, color=red)
    c.save("3-2-4_erd_oltp", SCRIPT)



def _mid(b):
    return (b[0] + b[2] / 2, b[1] + b[3] / 2)


# ------------------------------------------------------------------------------------------------ data flows
def flow_current() -> None:
    c = Canvas("full_ket")
    w, g = 150, 27.5
    r1 = [("Khách\nhàng", WHITE), ("Marketplace", BLUE), ("Hệ thống\nđơn hàng\n(oltp)", GREEN), ("Người bán\n(seller)", WHITE), ("Đơn vị\nvận chuyển", WHITE)]
    b1 = []
    for i, (t, f) in enumerate(r1):
        b1.append(c.box(i * (w + g), 10, w, 100, t, fill=f, px=20, bold=True))
        if i:
            c.arrow(right(b1[i - 1]), left(b1[i]))
    c.arrow(bottom(b1[4]), (b1[4][0] + w / 2, 135), head=False)
    c.line((b1[4][0] + w / 2, 135), (b1[2][0] + w / 2 + 30, 135), color="#374151", lw=1.6)
    c.arrow((b1[2][0] + w / 2 + 30, 135), (b1[2][0] + w / 2 + 30, 112), color="#374151")
    c.text(b1[3][0] + w / 2, 152, "trạng thái giao", px=19, color="#374151")
    c.text(640, 190, "chỉ gặp nhau qua seller_id", px=20, bold=True, color="#b91c1c")
    r2 = [("Landing\npage", BLUE), ("CRM:\nmql", GREEN), ("Đội SDR", WHITE), ("Đội SR", WHITE), ("CRM:\nclosed_deals", GREEN)]
    b2 = []
    for i, (t, f) in enumerate(r2):
        b2.append(c.box(i * (w + g), 235, w, 100, t, fill=f, px=20, bold=True))
        if i:
            c.arrow(right(b2[i - 1]), left(b2[i]))
    c.arrow(top(b2[4]), (b2[4][0] + w / 2, 213), head=False, color="#b45309")
    c.line((b2[4][0] + w / 2, 213), (b1[2][0] + w / 2, 213), color="#b45309", lw=1.8)
    c.arrow((b1[2][0] + w / 2, 213), (b1[2][0] + w / 2, 112), color="#b45309", lw=1.8)
    c.save("2-4_data_flow_hien_trang", SCRIPT)


def flow_proposed() -> None:
    c = Canvas("full_ket")
    names = [("Nguồn\noltp, crm", GREEN), ("Staging\nstg_*", GREY), ("ODS\nlàm sạch", GREY), ("Kho dw\n10 dim\n6 fact", BLUE), ("Data mart\n17 view", ORANGE), ("BI\nPower BI", PURPLE)]
    w, g = 124, 23.2
    bs = []
    for i, (t, f) in enumerate(names):
        bs.append(c.box(i * (w + g), 50, w, 120, t, fill=f, px=20, bold=True))
        if i:
            c.arrow(right(bs[i - 1]), left(bs[i]))
    c.text(430, 22, "lô hằng ngày (nạp tăng dần theo watermark)", px=20, bold=True, color="#1d4ed8")
    log = c.box(150, 235, 560, 56, "etl_log: số dòng, thời gian, lỗi", fill="#FDF8E4", px=20, dashed=True)
    for i in (1, 2, 3):
        c.arrow(bottom(bs[i]), (bs[i][0] + w / 2, 235), dashed=True, color="#6b7280")
    c.box(0, 305, c.W, 40, "Điều phối bằng một lệnh Python; biến đổi bằng PostgreSQL procedure", fill=WHITE, px=19, dashed=True)
    c.save("2-4_data_flow_de_xuat", SCRIPT)


def flow_oltp_olap() -> None:
    c = Canvas("full_ket")
    cols = [("Nguồn\noltp, crm\n11 bảng", GREEN), ("ODS\nđã làm sạch\n11 bảng", GREY)]
    b = []
    for i, (t, f) in enumerate(cols):
        b.append(c.box(i * 260, 100, 200, 150, t, fill=f, px=20, bold=True))
    c.arrow(right(b[0]), left(b[1]))
    dim = c.box(560, 20, 300, 130, "Dimension\n10 bảng (xanh)", fill=BLUE, px=20, bold=True)
    fact = c.box(560, 200, 300, 130, "Fact\n6 bảng (cam)\ngồm fact_seller_monthly", fill=ORANGE, px=20, bold=True)
    c.arrow(right(b[1]), left(dim), color="#2563EB")
    c.arrow(right(b[1]), left(fact), color="#C2410C")
    c.text(460, 30, "khoá thay thế", px=19, color="#2563EB")
    c.save("2-5_data_flow_oltp_olap", SCRIPT)


# ------------------------------------------------------------------------------------------------ taxonomy
EXAMPLE_SQL = {
    "customers": ("customer_unique_id", "SELECT customer_unique_id FROM oltp.customers ORDER BY customer_id LIMIT 1", 99441),
    "sellers": ("seller_state", "SELECT seller_state FROM oltp.sellers ORDER BY seller_id LIMIT 1", 3095),
    "products": ("product_category_name", "SELECT product_category_name FROM oltp.products ORDER BY product_id LIMIT 1", 32951),
    "orders": ("order_status", "SELECT order_status FROM oltp.orders ORDER BY order_id LIMIT 1", 99441),
    "order_items": ("price", "SELECT price FROM oltp.order_items ORDER BY order_id, order_item_id LIMIT 1", 112650),
    "order_payments": ("payment_type", "SELECT payment_type FROM oltp.order_payments ORDER BY order_id, payment_sequential LIMIT 1", 103886),
    "order_reviews": ("review_score", "SELECT review_score FROM oltp.order_reviews ORDER BY review_id, order_id LIMIT 1", 99224),
    "mql": ("origin", "SELECT origin FROM crm.mql ORDER BY mql_id LIMIT 1", 8000),
    "closed_deals": ("business_segment", "SELECT business_segment FROM crm.closed_deals ORDER BY mql_id LIMIT 1", 842),
    "geolocation": ("geolocation_lat", "SELECT round(geolocation_lat::numeric, 4) FROM oltp.geolocation ORDER BY id LIMIT 1", 1000163),
    "category_translation": ("product_category_name_english", "SELECT product_category_name_english FROM oltp.product_category_name_translation ORDER BY product_category_name LIMIT 1", 71),
}
GROUPS = [("Dữ liệu chủ", BLUE, ["customers", "sellers", "products"]), ("Giao dịch", ORANGE, ["orders", "order_items", "order_payments"]),
          ("Tương tác", PINK, ["order_reviews", "mql", "closed_deals"]), ("Tham chiếu", GREEN, ["geolocation", "category_translation"])]


def taxonomy() -> None:
    sys.path.insert(0, str(ROOT / "scripts" / "eda"))
    from common import q  # noqa: E402  (olist_full)

    ex = {t: str(q(sql).iloc[0, 0]) for t, (_, sql, _) in EXAMPLE_SQL.items()}
    c = Canvas("full_ket")
    rows = sum(len(g[2]) for g in GROUPS)
    rh = c.H / rows
    y = 0
    gb = []
    for gname, col, tabs in GROUPS:
        top_y = y
        for t in tabs:
            col_name, _, n = EXAMPLE_SQL[t]
            c.box(244, y + 1.5, 616, rh - 3, "", fill="white", ec=col, lw=1.2, r=4)
            c.text(251, y + rh / 2, t, px=19, bold=True, ha="left")
            c.text(522, y + rh / 2, f"{n:,}".replace(",", "."), px=19, ha="right", color="#52514e")
            v = ex[t]
            v = v if len(v) <= 12 else v[:9] + "…"
            c.text(532, y + rh / 2, f"{col_name[:17]}={v}", px=18.7, ha="left", family="monospace")
            y += rh
        gb.append((gname, col, top_y, y))
    for gname, col, a, b in gb:
        mid = (a + b) / 2
        c.box(122, mid - 32, 108, 64, gname, fill=col, px=19.5, bold=True)
        c.line((230, mid), (244, mid), color="#6b7280", lw=1.4)
    c.box(0, c.H / 2 - 44, 104, 88, "11 bảng\n1,56 triệu\ndòng", fill="#0b0b0b", px=18.7, bold=True, tc="white", wrap=False)
    for gname, col, a, b in gb:
        c.line((104, c.H / 2), (122, (a + b) / 2), color="#6b7280", lw=1.4)
    c.save("2-4_data_taxonomy", SCRIPT)



if __name__ == "__main__":
    bpmn_order()
    bpmn_seller()
    canvas_bmc()
    trees()
    erd_oltp()
    flow_current()
    flow_proposed()
    flow_oltp_olap()
    taxonomy()
