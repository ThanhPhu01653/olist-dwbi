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


# ----------------------------------------------------------------------------- E1: layered architecture (stacked blocks, NOT a flow)
def _counts():
    import sys

    from diagram_kit import ROOT
    from sqlalchemy import text

    sys.path.insert(0, str(ROOT))
    from etl import config
    from etl.db import get_engine

    eng = get_engine(config.DB_NAME)
    out = {}
    with eng.connect() as c:
        for sch in ["oltp", "crm", "staging", "ods", "dw", "etl_log"]:
            names = [r[0] for r in c.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema=:s AND table_type='BASE TABLE'"), {"s": sch})]
            out[sch] = (len(names), sum(c.execute(text(f'SELECT count(*) FROM "{sch}"."{t}"')).scalar_one() for t in names))
        marts = ["mart_sales", "mart_fulfillment", "mart_cx", "mart_acquisition"]
        v = c.execute(text("SELECT count(*) FROM information_schema.views WHERE table_schema = ANY(:s)"), {"s": marts}).scalar_one()
        m = c.execute(text("SELECT count(*) FROM pg_matviews WHERE schemaname = ANY(:s)"), {"s": marts}).scalar_one()
        out["mart"] = (v + m, m)
    return out


TECH = {  # brand colour tiles (text tiles: official logos are not bundled)
    "PostgreSQL": ("#336791", "#FFFFFF"), "Python": ("#3776AB", "#FFE873"), "Power BI": ("#F2C811", "#111111"), "GitHub": ("#24292F", "#FFFFFF"),
}


def architecture_layers() -> None:
    cnt = _counts()
    n = lambda x: f"{x:,}".replace(",", ".")
    d = Diagram("Kiến trúc các lớp", 1700, 1010)
    d.label(20, 8, 1650, 34, "Kiến trúc kho dữ liệu theo lớp: mỗi lớp liệt kê thành phần, công nghệ, số bảng và số dòng (trạng thái cuối)", font=17)
    d.label(20, 46, 1650, 24, "Các khối xếp tầng từ lớp trình bày (trên) xuống lớp nguồn (dưới); dữ liệu đi từ dưới lên nhưng sơ đồ này mô tả cấu trúc, không vẽ luồng.", font=11, bold=False, color="#4B5563")
    layers = [
        ("TRÌNH BÀY / BI", PURPLE, "Power BI Desktop (Import, mô hình ngữ nghĩa, DAX)", ["D1 Executive", "D2 Sales và Product", "D3 Order Fulfillment", "D4 Geography và Freight", "D5 Customer Experience", "D6 Seller Acquisition", "D7 Data Quality và ETL"],
         "7 dashboard · 37 file CSV · 32 quan hệ", ["Power BI", "Python"]),
        ("DATA MART", ORANGE, "mart_sales · mart_fulfillment · mart_cx · mart_acquisition", ["mart_sales (6 view)", "mart_fulfillment (4 view)", "mart_cx (4 view)", "mart_acquisition (3 view)"],
         f"{cnt['mart'][0]} view, trong đó {cnt['mart'][1]} materialized view", ["PostgreSQL"]),
        ("KHO DỮ LIỆU (dw)", BLUE, "Lược đồ constellation: 10 dimension + 6 fact", ["dim_date", "dim_geography", "dim_customer (SCD2)", "dim_seller", "dim_product", "dim_order_status", "dim_payment_type", "dim_lead_origin", "dim_lead_profile", "dim_sales_rep",
                                                                                          "fact_order_item", "fact_order_fulfillment", "fact_payment", "fact_review", "fact_lead_funnel", "fact_seller_monthly"],
         f"{cnt['dw'][0]} bảng · {n(cnt['dw'][1])} dòng", ["PostgreSQL"]),
        ("ODS (ods)", GREY, "Làm sạch, chuẩn hoá, gắn cờ chất lượng (dq_flags)", ["orders, customers, order_items", "order_payments, order_reviews", "products, sellers, category_translation", "geolocation_zip (gom 19.010 mã)", "mql, closed_deals", "ref_* (6 bảng seed)"],
         f"{cnt['ods'][0]} bảng · {n(cnt['ods'][1])} dòng", ["PostgreSQL"]),
        ("STAGING (staging)", GREY, "Bản sao thô của nguồn + mã lô nạp", ["stg_orders, stg_customers, stg_order_items", "stg_order_payments, stg_order_reviews", "stg_products, stg_sellers, stg_geolocation", "stg_product_category_name_translation", "stg_mql, stg_closed_deals"],
         f"{cnt['staging'][0]} bảng · {n(cnt['staging'][1])} dòng", ["PostgreSQL", "Python"]),
        ("NGUỒN (oltp, crm)", GREEN, "Hai hệ thống nguồn mô phỏng từ 11 file CSV Kaggle", ["oltp: orders, order_items, order_payments, order_reviews", "oltp: customers, sellers, products", "oltp: geolocation, product_category_name_translation", "crm: mql, closed_deals"],
         f"{cnt['oltp'][0] + cnt['crm'][0]} bảng · {n(cnt['oltp'][1] + cnt['crm'][1])} dòng", ["PostgreSQL", "Python"]),
    ]
    y = 80
    heights = [110, 100, 180, 100, 100, 100]
    for (name, fill, sub, comps, stat, techs), h in zip(layers, heights):
        d.frame(20, y, 1660, h, "", fill="#FFFFFF")
        d.box(30, y + 10, 190, h - 20, name + "\n\n" + stat, fill=fill, bold=True, font=12)
        d.label(235, y + 6, 900, 22, sub, font=12, bold=True)
        # component chips in a grid
        per_row = 5 if len(comps) > 8 else 4
        cw, ch = (1010 - 10 * (per_row - 1)) / per_row, 26
        for i, cmp_ in enumerate(comps):
            r, c = divmod(i, per_row)
            d.box(235 + c * (cw + 10), y + 34 + r * (ch + 6), cw, ch, cmp_, fill=fill if fill != GREY else "#F3F4F6", font=10)
        # technology tiles
        for j, t in enumerate(techs):
            bg, fg = TECH[t]
            d.box(1290 + j * 190, y + 20, 170, 46, t, fill=bg, bold=True, font=13, color=fg)
        y += h + 12
    # cross-cutting bars
    d.box(20, y, 1100, 56, "GIÁM SÁT etl_log: job_run, rejected_rows, dq_check (136 phép kiểm thử), watermark, batch_metrics, fact_load_issue · " + f"{cnt['etl_log'][0]} bảng · {n(cnt['etl_log'][1])} dòng", fill=YELLOW, font=11, bold=True)
    d.box(1130, y, 550, 56, "ĐIỀU PHỐI: python -m etl.run_pipeline (Python) · mã nguồn quản lý bằng Git trên GitHub", fill="#FFFFFF", font=11, bold=True)
    for j, t in enumerate(["Python", "GitHub", "PostgreSQL"]):
        bg, fg = TECH[t]
        d.box(1130 + j * 183, y + 64, 170, 36, t, fill=bg, bold=True, font=12, color=fg)
    d.save("kien-truc-cac-lop.drawio", "3-2_kien_truc_cac_lop.png")


def all_p8_arch() -> None:
    architecture_layers()


# ----------------------------------------------------------------------------- E4: data model figures (logic, physical, data marts)
def _fk_and_cols():
    import sys

    from diagram_kit import ROOT
    from sqlalchemy import text

    sys.path.insert(0, str(ROOT))
    from etl import config
    from etl.db import get_engine

    eng = get_engine(config.DB_NAME)
    with eng.connect() as c:
        fks = c.execute(text("""SELECT tc.table_name AS fact, kcu.column_name AS col, ccu.table_name AS dim
                                FROM information_schema.table_constraints tc
                                JOIN information_schema.key_column_usage kcu USING (constraint_schema, constraint_name)
                                JOIN information_schema.constraint_column_usage ccu USING (constraint_schema, constraint_name)
                                WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='dw' AND tc.table_name LIKE 'fact\\_%' ORDER BY 1, 2""")).all()
        cols = c.execute(text("""SELECT table_name, column_name, CASE WHEN data_type='numeric' THEN 'numeric(' || numeric_precision || ',' || numeric_scale || ')'
                                      WHEN data_type='character' THEN 'char(' || character_maximum_length || ')' WHEN data_type='character varying' THEN 'varchar'
                                      WHEN data_type='timestamp with time zone' THEN 'timestamptz' WHEN data_type='timestamp without time zone' THEN 'timestamp'
                                      WHEN data_type='double precision' THEN 'double' ELSE data_type END AS ty
                                 FROM information_schema.columns WHERE table_schema='dw' AND table_name IN (SELECT table_name FROM information_schema.tables WHERE table_schema='dw' AND table_type='BASE TABLE')
                                 ORDER BY table_name, ordinal_position""")).all()
        pks = c.execute(text("""SELECT kcu.table_name, kcu.column_name FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu USING (constraint_schema, constraint_name)
                                WHERE tc.constraint_type='PRIMARY KEY' AND tc.table_schema='dw'""")).all()
    return fks, cols, set(map(tuple, pks))


DIM_LEVELS = {
    "dim_date": "Năm → Quý → Tháng → Ngày", "dim_geography": "Vùng → Bang → Thành phố → Zip", "dim_customer": "Vùng → Bang → Thành phố → Zip → Khách → Phiên bản (SCD2)",
    "dim_seller": "Vùng → Bang → Thành phố → Seller; Kênh → Origin → Seller", "dim_product": "Nhóm ngành → Danh mục → Sản phẩm", "dim_order_status": "Nhóm trạng thái → Trạng thái",
    "dim_payment_type": "Nhóm → Hình thức", "dim_lead_origin": "Nhóm kênh → Origin", "dim_lead_profile": "(chiều rác) 7 thuộc tính của deal", "dim_sales_rep": "Vai trò (SDR, SR) → Nhân viên",
}
FACT_GRAIN = {
    "fact_order_item": "Bán hàng · transaction\n1 dòng hàng của 1 đơn", "fact_order_fulfillment": "Xử lý đơn · snapshot tích luỹ\n1 đơn, 5 mốc thời gian", "fact_payment": "Thanh toán · transaction\n1 lần thanh toán",
    "fact_review": "Đánh giá · transaction\n1 review của 1 đơn", "fact_lead_funnel": "Thu hút seller · snapshot tích luỹ\n1 khách tiềm năng (MQL)", "fact_seller_monthly": "Hiệu suất seller · snapshot định kỳ\n1 seller × 1 tháng",
}
MARTS = [
    ("mart_sales", ["fact_order_item"], ["Doanh thu (GMV) theo tháng, danh mục, vùng thay đổi thế nào?", "Bao nhiêu danh mục tạo 80% GMV (quy luật 80/20)?", "Vùng nào đóng góp nhiều nhất, vùng nào tăng nhanh nhất?", "AOV và tăng trưởng MoM, YoY?"]),
    ("mart_fulfillment", ["fact_order_fulfillment"], ["Chặng nào (duyệt, bàn giao, vận chuyển) mất lâu nhất?", "Bang nào giao trễ nhiều nhất?", "Ngày hứa giao so với giao thực tế chênh bao nhiêu?", "Khoảng cách seller đến khách ảnh hưởng lead time thế nào?"]),
    ("mart_cx", ["fact_review", "fact_payment"], ["Giao trễ làm điểm review giảm bao nhiêu?", "Cơ cấu hình thức thanh toán và số kỳ trả góp?", "Bao nhiêu khách quay lại mua (RFM, cohort)?", "Tỷ lệ review tiêu cực theo tháng và vùng?"]),
    ("mart_acquisition", ["fact_lead_funnel", "fact_seller_monthly"], ["Kênh marketing nào chuyển MQL thành seller tốt nhất?", "Mất bao nhiêu ngày từ liên hệ đến chốt deal và đến đơn đầu?", "Seller từ funnel bán được bao nhiêu GMV?", "Seller nào ngừng bán sau khi chốt?"]),
]


def data_model_logic(fks) -> None:
    d = Diagram("Data model logic", 1750, 900)
    d.label(20, 8, 1700, 34, "Data model logic: 6 quy trình (fact) nối với dimension và các cấp phân cấp (không ghi kiểu dữ liệu)", font=16)
    facts = list(FACT_GRAIN)
    dims = list(DIM_LEVELS)
    fid = {f: d.box(20, 70 + i * 130, 330, 100, f + "\n" + FACT_GRAIN[f], fill=ORANGE, bold=True, font=11) for i, f in enumerate(facts)}
    did = {m: d.box(900, 60 + i * 80, 820, 66, m + "\n" + DIM_LEVELS[m], fill=BLUE, bold=False, font=11) for i, m in enumerate(dims)}
    seen = set()
    for f, col, m in fks:
        if (f, m) in seen:
            continue
        seen.add((f, m))
        d.arrow(fid[f], did[m], "", color="#6B7280", width=1.0)
    d.box(380, 800, 480, 70, "Mỗi fact trỏ tới dimension bằng khoá thay thế (…_key); dòng Unknown (−1) bảo đảm khoá ngoại không bao giờ rỗng. dim_date đóng vai nhiều lần (ngày mua, duyệt, bàn giao, giao…).", fill=WHITE, shape="rect", font=10, dashed=True)
    d.save("data-model-logic.drawio", "3-5_data_model_logic.png")


def data_model_physical(fks, cols, pks) -> None:
    fk_of = {(f, c): m for f, c, m in fks}
    tables = {}
    for t, c, ty in cols:
        tables.setdefault(t, []).append((c, ty))
    layout = [
        ["dim_date", "dim_order_status", "dim_payment_type", "dim_lead_origin"],
        ["fact_order_item", "fact_payment", "fact_review"],
        ["fact_order_fulfillment", "fact_seller_monthly", "fact_lead_funnel"],
        ["dim_customer", "dim_seller", "dim_sales_rep", "dim_lead_profile"],
        ["dim_geography", "dim_product"],
    ]
    d = Diagram("Data model vật lý", 1900, 1500)
    d.label(20, 8, 1850, 34, "Data model vật lý của schema dw (sinh từ information_schema): fact màu cam, dimension màu xanh; PK đậm, FK ghi sang chiều tương ứng", font=15)
    xs = [20, 400, 790, 1180, 1560]
    for x, col in zip(xs, layout):
        y = 60
        for t in col:
            rows = []
            for c, ty in tables[t]:
                if (t, c) in pks:
                    rows.append((f"{c}  {ty}  PK", False, True))
                elif (t, c) in fk_of:
                    rows.append((f"{c}  {ty}  FK→{fk_of[(t, c)].replace('dim_', '')}", False, False))
                else:
                    rows.append((f"{c}  {ty}", False, False))
            e = d.entity(x, y, 350, t, rows, fill=ORANGE if t.startswith("fact") else BLUE, font=9, header=ORANGE if t.startswith("fact") else BLUE)
            y += d._box(e)["h"] + 16
    d.save("data-model-vat-ly.drawio", "3-5_data_model_vat_ly.png")


def data_model_marts(fks) -> None:
    d = Diagram("Data model theo data mart", 1800, 1130)
    d.label(20, 8, 1750, 34, "Data mart: mỗi mart gồm fact (cam), các dimension (xanh) và 3–4 câu hỏi phân tích", font=16)
    dims_of = {}
    for f, col, m in fks:
        dims_of.setdefault(f, [])
        if m not in dims_of[f]:
            dims_of[f].append(m)
    for k, (mart, facts, qs) in enumerate(MARTS):
        x0, y0 = 20 + (k % 2) * 890, 60 + (k // 2) * 520
        d.frame(x0, y0, 870, 500, mart)
        fy = y0 + 40
        dset = []
        for f in facts:
            for m in dims_of.get(f, []):
                if m not in dset:
                    dset.append(m)
        fids = [d.box(x0 + 20, fy + i * 80, 300, 66, f + "\n" + FACT_GRAIN[f], fill=ORANGE, bold=True, font=11) for i, f in enumerate(facts)]
        dids = {m: d.box(x0 + 450, y0 + 40 + j * 38, 400, 30, m, fill=BLUE, font=11) for j, m in enumerate(dset)}
        for f, fid_ in zip(facts, fids):
            for m in dims_of.get(f, []):
                d.arrow(fid_, dids[m], "", color="#6B7280", width=1.0)
        d.box(x0 + 20, y0 + 300, 830, 180, "Câu hỏi phân tích:\n" + "\n".join(f"{i + 1}. {q_}" for i, q_ in enumerate(qs)), fill=WHITE, shape="rect", font=11, align="left")
    d.save("data-model-theo-mart.drawio", "3-5_data_mart.png")


def all_p8_model() -> None:
    fks, cols, pks = _fk_and_cols()
    data_model_logic(fks)
    data_model_physical(fks, cols, pks)
    data_model_marts(fks)
