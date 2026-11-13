"""P8 diagrams (called from scripts/gen_drawio.py): data flow of IT systems (current / proposed), OLTP -> OLAP flow.\nArrows carry INFORMATION that is passed (order, delivery status, payment, review, lead), not actions.\n"""
from __future__ import annotations

from diagram_kit import BLUE, GREEN, GREY, ORANGE, PINK, PURPLE, TEAL, WHITE, YELLOW, Diagram


def dataflow_current() -> None:
    d = Diagram("Data flow hiện trạng", 1800, 880)
    d.label(20, 8, 1700, 34, "Luồng dữ liệu giữa các hệ thống CNTT hiện trạng (mũi tên ghi thông tin được truyền)", font=17)
    kh = d.box(20, 110, 150, 80, "Khách hàng", fill=WHITE, bold=True)
    mk = d.box(350, 110, 200, 80, "Marketplace / kênh bán\n(sàn thương mại điện tử)", fill=BLUE, bold=True)
    od = d.box(740, 110, 220, 80, "Hệ thống đơn hàng Olist\n(oltp: orders, order_items)", fill=GREEN, bold=True)
    sl = d.box(1130, 110, 180, 80, "Người bán (seller)", fill=WHITE, bold=True)
    ca = d.box(1130, 330, 200, 80, "Đơn vị vận chuyển", fill=WHITE, bold=True)
    pay = d.box(350, 360, 200, 80, "Hệ thống thanh toán\n(oltp: order_payments)", fill=GREEN, bold=True)
    rv = d.box(20, 360, 220, 80, "Hệ thống đánh giá\n(oltp: order_reviews)", fill=GREEN, bold=True)
    geo = d.box(740, 360, 240, 80, "Dữ liệu địa chỉ\n(oltp: geolocation, customers, sellers)", fill=GREEN, bold=True)
    d.arrow(kh, mk, "thông tin đơn đặt (sản phẩm, số lượng, địa chỉ giao)")
    d.arrow(mk, od, "thông tin đơn (người mua, dòng hàng, giá, phí vận chuyển)")
    d.arrow(od, sl, "đơn cần chuẩn bị, hạn bàn giao")
    d.arrow(sl, ca, "kiện hàng bàn giao, thời điểm bàn giao")
    d.arrow(ca, od, "trạng thái giao, ngày giao thực tế", color="#6B7280")
    d.arrow(mk, pay, "thông tin thanh toán (hình thức, số kỳ, số tiền)")
    d.arrow(pay, od, "xác nhận thanh toán, thời điểm duyệt đơn")
    d.arrow(kh, rv, "điểm đánh giá và nhận xét")
    d.arrow(rv, od, "điểm review gắn với mã đơn")
    d.arrow(geo, od, "toạ độ theo mã bưu chính")
    d.frame(20, 520, 1700, 340, "Quy trình thu hút người bán (marketing funnel, hệ thống CRM)", fill="#FFFBEA")
    lp = d.box(1480, 590, 220, 80, "Trang đích (landing page)\nvà kênh marketing", fill=BLUE, bold=True)
    crm = d.box(1190, 590, 200, 80, "CRM: khách tiềm năng\n(crm.mql)", fill=GREEN, bold=True)
    sdr = d.box(900, 590, 190, 80, "Đội SDR\n(sàng lọc lead)", fill=WHITE, bold=True)
    sr = d.box(610, 590, 190, 80, "Đội SR\n(tư vấn, chốt deal)", fill=WHITE, bold=True)
    cd = d.box(320, 590, 220, 80, "CRM: thương vụ đã chốt\n(crm.closed_deals)", fill=GREEN, bold=True)
    d.arrow(lp, crm, "lead (kênh, ngày liên hệ)")
    d.arrow(crm, sdr, "lead cần sàng lọc")
    d.arrow(sdr, sr, "lead đã đủ điều kiện")
    d.arrow(sr, cd, "kết quả chốt")
    d.arrow(cd, od, "seller mới (seller_id) được phép bán", color="#B45309")
    d.box(50, 740, 1640, 90, "Hai hệ thống nguồn độc lập: hệ thống bán hàng (oltp, 9 bảng) và CRM (crm, 2 bảng). Chỉ gặp nhau qua seller_id; không có khoá ngoại giữa hai hệ thống.\nHiện trạng mỗi báo cáo lấy trực tiếp từ từng hệ thống nên số liệu khó đối chiếu; đây là lý do dựng kho dữ liệu.", fill=WHITE, shape="rect", font=12, dashed=True)
    d.save("data-flow-hien-trang.drawio", "2-4_data_flow_hien_trang.png")


def dataflow_proposed() -> None:
    d = Diagram("Data flow đề xuất", 1500, 600)
    d.label(20, 8, 1450, 34, "Luồng dữ liệu đề xuất: nguồn → staging → ODS → kho dữ liệu → data mart → BI", font=17)
    xs = [20, 270, 520, 770, 1020, 1270]
    names = [("Nguồn\noltp + crm", GREEN), ("Staging\nstg_*", GREY), ("ODS\nlàm sạch", GREY), ("Kho dữ liệu dw\n10 dim + 6 fact", BLUE), ("Data mart\nmart_* (17 view)", ORANGE), ("BI\nPower BI, 7 dashboard", PURPLE)]
    ids = [d.box(x, 120, 200, 120, t, fill=f, bold=True, font=13) for x, (t, f) in zip(xs, names)]
    labs = ["bản sao thô + mã lô nạp", "dữ liệu sạch + cờ chất lượng, dòng lỗi có lý do", "dim (SCD1/SCD2) + fact (khoá thay thế)", "view tổng hợp theo chủ đề", "CSV / mô hình ngữ nghĩa, số đã tính sẵn"]
    for a, b, lb in zip(ids, ids[1:], labs):
        d.arrow(a, b, lb)
    log = d.box(270, 340, 950, 70, "Giám sát etl_log: job_run, rejected_rows, dq_check, watermark, batch_metrics (thông tin chạy: số dòng, thời gian, lỗi) → dashboard D7", fill=YELLOW)
    for t in ids[1:4]:
        d.arrow(t, log, "", dashed=True)
    d.arrow(log, ids[5], "tình trạng ETL", dashed=True)
    d.box(20, 450, 1450, 110, "Điều phối: python -m etl.run_pipeline (một lệnh, ghi nhật ký từng bước) · Biến đổi: PostgreSQL procedure (PL/pgSQL) · Nạp tăng dần theo watermark, mỗi đợt khoảng 20 giây\nNếu cần gần thời gian thực: thêm CDC + Kafka giữa nguồn và staging (chương 5).", fill=WHITE, shape="rect", font=12, dashed=True)
    d.save("data-flow-de-xuat.drawio", "2-4_data_flow_de_xuat.png")


def oltp_to_olap() -> None:
    """High-level flow of OLTP tables -> ODS -> DW tables (which OLTP table feeds which dw table)."""
    d = Diagram("Data flow OLTP sang OLAP", 1500, 860)
    d.label(20, 8, 1450, 34, "Luồng dữ liệu OLTP → OLAP: bảng nguồn nào nuôi bảng nào của kho", font=17)
    d.frame(20, 60, 330, 770, "Nguồn (oltp, crm)")
    src_names = ["orders", "order_items", "order_payments", "order_reviews", "customers", "sellers", "products", "product_category_name_translation", "geolocation", "mql", "closed_deals"]
    src = {}
    for i, s in enumerate(src_names):
        src[s] = d.box(40, 100 + i * 62, 290, 48, s, fill=GREEN, font=11)
    d.frame(420, 60, 280, 770, "ODS (đã làm sạch)")
    ods_names = ["ods.orders", "ods.order_items", "ods.order_payments", "ods.order_reviews", "ods.customers", "ods.sellers", "ods.products", "ods.category_translation", "ods.geolocation_zip", "ods.mql", "ods.closed_deals"]
    ods = {}
    for i, s in enumerate(ods_names):
        ods[src_names[i]] = d.box(440, 100 + i * 62, 240, 48, s, fill=GREY, font=11)
        d.arrow(src[src_names[i]], ods[src_names[i]])
    d.frame(780, 60, 350, 770, "Dimension (xanh)")
    dims = {"dim_date": 100, "dim_customer": 190, "dim_seller": 280, "dim_product": 370, "dim_geography": 460, "dim_order_status": 550, "dim_payment_type": 640, "dim_lead_origin / profile / sales_rep": 730}
    dm = {k: d.box(800, y, 310, 56, k, fill=BLUE, font=11) for k, y in dims.items()}
    d.frame(1200, 60, 280, 770, "Fact (cam)")
    facts = {"fact_order_item": 100, "fact_order_fulfillment": 205, "fact_payment": 310, "fact_review": 415, "fact_lead_funnel": 520, "fact_seller_monthly": 625}
    fm = {k: d.box(1220, y, 240, 62, k, fill=ORANGE, font=11, bold=True) for k, y in facts.items()}
    link_dim = [("orders", "dim_date"), ("orders", "dim_order_status"), ("customers", "dim_customer"), ("sellers", "dim_seller"), ("closed_deals", "dim_seller"), ("products", "dim_product"),
                ("category_translation" if False else "product_category_name_translation", "dim_product"), ("geolocation", "dim_geography"), ("customers", "dim_geography"), ("sellers", "dim_geography"),
                ("order_payments", "dim_payment_type"), ("mql", "dim_lead_origin / profile / sales_rep"), ("closed_deals", "dim_lead_origin / profile / sales_rep")]
    for s, t in link_dim:
        d.arrow(ods[s], dm[t], color="#2563EB", width=1.0)
    link_fact = [("orders", "fact_order_item"), ("order_items", "fact_order_item"), ("orders", "fact_order_fulfillment"), ("order_payments", "fact_payment"), ("order_reviews", "fact_review"),
                 ("mql", "fact_lead_funnel"), ("closed_deals", "fact_lead_funnel")]
    for s, t in link_fact:
        d.arrow(ods[s], fm[t], color="#C2410C", width=1.0)
    d.arrow(fm["fact_order_item"], fm["fact_seller_monthly"], "tổng hợp theo seller-tháng", dashed=True)
    d.save("data-flow-oltp-olap.drawio", "2-5_data_flow_oltp_olap.png")


def all_p8() -> None:
    dataflow_current()
    dataflow_proposed()
    oltp_to_olap()


# ----------------------------------------------------------------------------- ERD OLTP with columns used in OLAP underlined
def used_oltp_columns():
    """oltp/crm (table, column) pairs that reach the warehouse, derived from docs/mapping.csv (source -> ods -> dw)."""
    import re
    import pandas as pd
    from diagram_kit import ROOT

    m = pd.read_csv(ROOT / "docs" / "mapping.csv", encoding="utf-8-sig")
    a, b = m[m.layer == "nguồn → ods"], m[m.layer == "ods → dw"]
    ods_to_src = {(r.target_table, r.target_column): (r.source_table, r.source_column) for r in a.itertuples()}
    used = set()
    for r in b.itertuples():
        tabs = re.findall(r"ods\.\w+", str(r.source_table))
        cols = [c.strip() for c in re.split(r"[,/]", str(r.source_column)) if c.strip()]
        for t in tabs:
            for c in cols:
                if (t, c) in ods_to_src:
                    used.add(ods_to_src[(t, c)])
    # join keys used only to look up a surrogate key (mapping.csv lists the dw lookup table, not the source column)
    used |= {("oltp.order_items", "product_id"), ("oltp.product_category_name_translation", "product_category_name")}
    # mapping.csv row "business_segment ... average_stock (7 columns)": the junk dimension dim_lead_profile takes these 7 closed_deals attributes
    used |= {("crm.closed_deals", c) for c in ["business_segment", "lead_type", "lead_behaviour_profile", "has_company", "has_gtin", "average_stock", "business_type"]}
    return used, a


def erd_oltp() -> None:
    import sys

    from diagram_kit import ROOT
    from sqlalchemy import text

    sys.path.insert(0, str(ROOT))
    from etl import config
    from etl.db import get_engine

    used, a = used_oltp_columns()
    eng = get_engine(config.DB_NAME_FULL)
    cols, pks = {}, {}
    with eng.connect() as c:
        for sch, t, col in c.execute(text("SELECT table_schema, table_name, column_name FROM information_schema.columns WHERE table_schema IN ('oltp','crm') ORDER BY table_schema, table_name, ordinal_position")):
            cols.setdefault(f"{sch}.{t}", []).append(col)
        for sch, t, col in c.execute(text("""SELECT kcu.table_schema, kcu.table_name, kcu.column_name FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu USING (constraint_schema, constraint_name) WHERE tc.constraint_type='PRIMARY KEY' AND kcu.table_schema IN ('oltp','crm')""")):
            pks.setdefault(f"{sch}.{t}", set()).add(col)
    d = Diagram("ERD OLTP", 1900, 900)
    d.label(20, 8, 1850, 34, "ERD hệ thống nguồn (oltp, crm): màu = nhóm dữ liệu; gạch chân = cột được dùng sang OLAP; đậm = khoá chính", font=16)
    GROUP = {"customers": BLUE, "sellers": BLUE, "products": BLUE, "orders": ORANGE, "order_items": ORANGE, "order_payments": ORANGE,
             "order_reviews": PINK, "mql": PINK, "closed_deals": PINK, "geolocation": GREEN, "product_category_name_translation": GREEN}
    POS = {"customers": (40, 80), "orders": (420, 80), "order_items": (800, 80), "products": (1180, 80), "product_category_name_translation": (1540, 80),
           "order_reviews": (40, 350), "order_payments": (420, 350), "sellers": (800, 350), "closed_deals": (1180, 350), "mql": (1540, 350), "geolocation": (420, 640)}
    ids, stat = {}, []
    for t, (x, y) in POS.items():
        sch = "crm" if t in ("mql", "closed_deals") else "oltp"
        full = f"{sch}.{t}"
        n_used = sum((full, c) in used for c in cols[full])
        stat.append((full, len(cols[full]), n_used))
        rows = [(c, (full, c) in used, c in pks.get(full, set())) for c in cols[full]]
        ids[t] = d.entity(x, y, 320 if t == "product_category_name_translation" else 300, full, rows, fill=GROUP[t] + "", header=GROUP[t])
    rel = [("orders", "customers", "customer_id", False), ("order_items", "orders", "order_id", False), ("order_items", "products", "product_id", False), ("order_items", "sellers", "seller_id", False),
           ("order_payments", "orders", "order_id", False), ("order_reviews", "orders", "order_id", False), ("closed_deals", "mql", "mql_id", False),
           ("products", "product_category_name_translation", "", True), ("customers", "geolocation", "zip (logic)", True),
           ("sellers", "geolocation", "zip (logic)", True), ("closed_deals", "sellers", "", True)]
    for s_, t_, lab, dashed in rel:
        d.arrow(ids[s_], ids[t_], lab, dashed=dashed)
    d.box(1180, 660, 700, 160, "Cách đọc: khung xanh dương = dữ liệu chủ, cam = giao dịch, hồng = tương tác, xanh lá = tham chiếu.\nCột gạch chân là cột nguồn được dùng để tạo cột của dimension hoặc fact (suy ra tự động từ docs/mapping.csv: nguồn sang ODS sang kho).\nĐường nét đứt là quan hệ logic, không có khoá ngoại.", fill=WHITE, shape="rect", font=11, dashed=True)
    d.save("erd-oltp-tomau.drawio", "2-5_erd_oltp_gach_chan.png")
    return stat


def all_p8_erd() -> None:
    stat = erd_oltp()
    print("used columns:", sum(s[2] for s in stat), "of", sum(s[1] for s in stat))
