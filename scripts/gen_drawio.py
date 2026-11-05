"""Generate simple, editable draw.io diagrams in docs/diagrams/*.drawio.   python scripts/gen_drawio.py
  kien-truc-cac-lop.drawio   layered architecture (oltp/crm -> staging -> ods -> dw -> mart -> Power BI, etl_log)
  data-model-theo-mart.drawio  facts (orange) grouped by data mart (frames), dimensions (blue), keys as arrows
  pipeline-etl.drawio        ETL flow with the tools used
Open with https://app.diagrams.net (File > Open from > Device) or the draw.io desktop app / VS Code extension; every shape is a normal shape you can move, recolour and relabel.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "diagrams"
ORANGE, BLUE, GREY, GREEN, YELLOW, PURPLE = "#F4A261", "#8ECAE6", "#E5E7EB", "#CDE8D6", "#FFF3C4", "#E2D4F0"


class Diagram:
    def __init__(self, name: str):
        self.name, self.cells, self.n = name, [], 1

    def box(self, x, y, w, h, text, fill=GREY, style="rounded=1", stroke="#4B5563", font=12, bold=False) -> str:
        self.n += 1
        cid = f"c{self.n}"
        st = f"{style};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize={font};" + ("fontStyle=1;" if bold else "")
        self.cells.append(f'<mxCell id="{cid}" value="{escape(text, {chr(10): "&#10;"})}" style="{st}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def frame(self, x, y, w, h, title, fill="#FFFBEA") -> str:
        return self.box(x, y, w, h, title, fill=fill, style="rounded=0;verticalAlign=top;align=left;spacingLeft=8;dashed=1", font=13, bold=True)

    def arrow(self, a, b, label="", dashed=False) -> None:
        self.n += 1
        st = "endArrow=classic;html=1;rounded=0;strokeColor=#374151;" + ("dashed=1;" if dashed else "")
        self.cells.append(f'<mxCell id="e{self.n}" value="{escape(label)}" style="{st}" edge="1" parent="1" source="{a}" target="{b}"><mxGeometry relative="1" as="geometry"/></mxCell>')

    def save(self, fname: str) -> None:
        xml = (f'<mxfile host="app.diagrams.net"><diagram name="{escape(self.name)}" id="d1"><mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" page="1" pageScale="1" pageWidth="1654" pageHeight="1169">'
               f'<root><mxCell id="0"/><mxCell id="1" parent="0"/>{"".join(self.cells)}</root></mxGraphModel></diagram></mxfile>')
        (OUT / fname).write_text(xml, encoding="utf-8")
        print("written docs/diagrams/" + fname)


def layers() -> None:
    d = Diagram("Kiến trúc các lớp")
    d.box(20, 10, 1300, 30, "Olist DW & BI – kiến trúc các lớp (số dòng ở trạng thái cuối)", fill="#FFFFFF", style="text", font=16, bold=True)
    src = d.frame(20, 70, 230, 330, "Nguồn (mô phỏng)")
    a = d.box(40, 120, 190, 110, "oltp (bán hàng)\n9 bảng, 1.550.922 dòng\norders, order_items, payments, reviews, customers, sellers, products, geolocation", fill=GREEN)
    b = d.box(40, 260, 190, 110, "crm (marketing)\n2 bảng, 8.842 dòng\nmql, closed_deals", fill=GREEN)
    stg = d.box(300, 120, 170, 250, "STAGING\nstg_* (11 bảng)\n1.559.764 dòng\nbản sao thô + load_batch_id, loaded_at", fill=GREY, bold=False)
    ods = d.box(520, 120, 170, 250, "ODS\n18 bảng, 678.183 dòng\nlàm sạch, chuẩn hoá, dq_flags\ndòng lỗi → rejected_rows", fill=GREY)
    dw = d.box(740, 120, 190, 250, "KHO dw\n10 dimension + 6 fact\n614.223 dòng\nhình sao, SCD2, khoá thay thế, dòng Unknown −1", fill=BLUE, bold=True)
    mart = d.box(980, 120, 170, 250, "DATA MART\nmart_sales, mart_fulfillment, mart_cx, mart_acquisition\n17 view (4 materialized)", fill=ORANGE)
    bi = d.box(1200, 120, 170, 250, "POWER BI\n37 file CSV (Import)\nmô hình quan hệ + DAX\n7 dashboard\nPublish to web", fill=PURPLE, bold=True)
    log = d.box(300, 440, 850, 70, "etl_log: job_run, rejected_rows, watermark, dq_check (133 test), fact_load_issue, batch_metrics, v_run_summary… → dashboard D7", fill=YELLOW)
    for s, t, lab in [(a, stg, "extract"), (b, stg, ""), (stg, ods, "SQL procedure"), (ods, dw, "dim + fact"), (dw, mart, "view"), (mart, bi, "export CSV")]:
        d.arrow(s, t, lab)
    d.arrow(dw, bi, "export CSV (dim, fact)", dashed=True)
    for t in (stg, ods, dw):
        d.arrow(log, t, "", dashed=True)
    d.box(20, 560, 1350, 40, "Python điều phối (etl.run_pipeline) · PostgreSQL 18 · SQL procedure PL/pgSQL · Mermaid/draw.io cho sơ đồ · Git/GitHub", fill="#FFFFFF", style="text", font=12)
    d.save("kien-truc-cac-lop.drawio")


def data_model() -> None:
    d = Diagram("Data model theo data mart")
    d.box(20, 10, 1500, 30, "Data model theo data mart – fact màu cam, dimension màu xanh, khung = data mart", fill="#FFFFFF", style="text", font=16, bold=True)
    dims = {}
    dim_list = [("dim_date", "dim_date\n(role-playing: mua, duyệt, bàn giao, giao, dự kiến, liên hệ, chốt…)"), ("dim_customer", "dim_customer\nSCD2, 96.339 dòng"), ("dim_geography", "dim_geography\nzip → thành phố → bang → vùng"),
                ("dim_seller", "dim_seller\nconformed (bán hàng + funnel)"), ("dim_product", "dim_product\nsản phẩm → danh mục → nhóm ngành"), ("dim_order_status", "dim_order_status"),
                ("dim_payment_type", "dim_payment_type"), ("dim_lead_origin", "dim_lead_origin"), ("dim_lead_profile", "dim_lead_profile\n(junk dimension)"), ("dim_sales_rep", "dim_sales_rep\n(SDR / SR)")]
    for i, (k, t) in enumerate(dim_list):
        dims[k] = d.box(1180, 70 + i * 80, 300, 62, t, fill=BLUE)
    facts = [
        ("mart_sales", 70, 130, [("fact_order_item", "fact_order_item (transaction)\n1 dòng hàng của 1 đơn · 112.650 dòng\nprice, freight_value, item_total", ["dim_date", "dim_customer", "dim_geography", "dim_seller", "dim_product", "dim_order_status"])]),
        ("mart_fulfillment", 270, 130, [("fact_order_fulfillment", "fact_order_fulfillment (accumulating snapshot)\n1 đơn · 99.441 dòng\nlead_days, delay_days, promised_days, is_late", ["dim_date", "dim_customer", "dim_geography", "dim_order_status"])]),
        ("mart_cx", 470, 250, [("fact_payment", "fact_payment (transaction)\n1 lần thanh toán · 103.886 dòng", ["dim_date", "dim_customer", "dim_payment_type"]),
                               ("fact_review", "fact_review (transaction)\n1 review · 99.224 dòng\nreview_score, is_negative", ["dim_date", "dim_customer"])]),
        ("mart_acquisition", 800, 250, [("fact_lead_funnel", "fact_lead_funnel (accumulating snapshot)\n1 MQL · 8.000 dòng\nis_won, days_to_close", ["dim_date", "dim_seller", "dim_lead_origin", "dim_lead_profile", "dim_sales_rep"]),
                                        ("fact_seller_monthly", "fact_seller_monthly (periodic snapshot)\n1 seller × tháng · 36.583 dòng\ngmv, late_rate", ["dim_date", "dim_seller"])]),
    ]
    for mart, y, h, items in facts:
        d.frame(20, y, 560 if len(items) == 1 else 560, h + (60 if len(items) == 2 else 0) - (0), mart)
        for j, (fk, ft, links) in enumerate(items):
            fid = d.box(50, y + 40 + j * 110, 480, 80 if len(items) == 2 else 70, ft, fill=ORANGE, bold=True)
            for lk in links:
                d.arrow(fid, dims[lk])
    d.save("data-model-theo-mart.drawio")


def pipeline() -> None:
    d = Diagram("Pipeline ETL")
    d.box(20, 10, 1500, 30, "Pipeline ETL: python -m etl.run_pipeline --mode full | incremental (một batch_id mỗi lần chạy)", fill="#FFFFFF", style="text", font=16, bold=True)
    csv = d.box(20, 100, 120, 70, "CSV Kaggle\n11 file\n(data/raw)", fill=GREEN)
    ld = d.box(180, 100, 150, 70, "load_source --initial\nsimulate_increment\n(Python, COPY)", fill=PURPLE)
    src = d.box(370, 100, 130, 70, "oltp + crm\n(hệ thống nguồn)", fill=GREEN)
    ext = d.box(540, 100, 140, 70, "1. extract\nfull / incremental\n(Python + SQL)", fill=GREY)
    stg = d.box(720, 100, 120, 70, "staging\nstg_*", fill=GREY)
    ods = d.box(880, 100, 140, 70, "2. ODS\nlàm sạch, dq_flags,\nthử lại mồ côi", fill=GREY)
    dim = d.box(1060, 100, 120, 70, "3. dimension\nSCD1 / SCD2", fill=BLUE)
    fact = d.box(1220, 100, 140, 70, "4. fact\ninsert / upsert / tính lại", fill=ORANGE)
    mart = d.box(1220, 240, 140, 70, "5. mart\nrefresh materialized view", fill=ORANGE)
    tst = d.box(1060, 240, 120, 70, "6. tests\n133 phép + đối chiếu EDA", fill=YELLOW)
    snap = d.box(880, 240, 140, 70, "7. snapshot\nbatch_metrics", fill=YELLOW)
    exp = d.box(720, 240, 120, 70, "8. export_powerbi\nCSV", fill=PURPLE)
    pbi = d.box(540, 240, 140, 70, "Power BI\nImport + DAX\n7 dashboard", fill=PURPLE)
    log = d.box(540, 380, 820, 60, "etl_log.job_run · rejected_rows · dq_check · fact_load_issue · watermark · batch_metrics (ghi ở mọi bước; lỗi → dừng, status failed)", fill=YELLOW)
    for s, t in [(csv, ld), (ld, src), (src, ext), (ext, stg), (stg, ods), (ods, dim), (dim, fact), (fact, mart), (mart, tst), (tst, snap), (snap, exp), (exp, pbi)]:
        d.arrow(s, t)
    for s in (ext, ods, fact, tst):
        d.arrow(s, log, "", dashed=True)
    d.box(20, 240, 480, 120, "Chế độ full: xoá và dựng lại toàn bộ (~56 giây trên dữ liệu đến 2017-12-31).\nChế độ incremental: chỉ lấy dòng chưa có (~20 giây/đợt, 11 đợt hằng tháng).\nKết quả incremental = full (16/16 bảng khớp).", fill="#FFFFFF", style="rounded=0", font=12)
    d.save("pipeline-etl.drawio")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    layers()
    data_model()
    pipeline()
