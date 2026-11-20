"""P10: architecture diagram of the Lakehouse -> docs/diagrams/lakehouse-kien-truc.drawio, figures/5-1_kien_truc_lakehouse.png (draft), docs/lakehouse.mmd.

    python scripts/gen_lakehouse_diagram.py
The Mermaid text is the same one that is shown in docs/LAKEHOUSE.md section 3.3 (taken from there, so the two never differ).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from diagram_kit import BLUE, GREEN, GREY, ORANGE, PURPLE, TEAL, YELLOW, Diagram

d = Diagram("Lakehouse", 1760, 700)
d.label(20, 8, 1700, 32, "Kiến trúc Lakehouse: nguồn → CDC → Kafka → Bronze / Silver / Gold (MinIO + Iceberg) → Trino → Superset; đối soát với kho chương 3", font=16)

# sources
csv = d.box(20, 70, 200, 50, "CSV Kaggle\n(data/raw)", fill=GREY, font=11)
rep = d.box(20, 140, 200, 56, "replay_events.py\nINSERT / UPDATE theo thời gian", fill=GREY, font=11)
pg = d.box(20, 230, 200, 100, "PostgreSQL nguồn :5433\noltp + crm\nwal_level=logical", fill=BLUE, font=11)
api = d.box(20, 540, 200, 56, "API công khai (P9)\nIBGE, Banco Central,\nBrasilAPI, Open-Meteo", fill=GREY, font=10)
col = d.box(20, 440, 200, 50, "collector api_ingest/\n(dùng lại từ P9)", fill=GREY, font=11)
# ingest
dbz = d.box(270, 240, 190, 60, "Debezium\n(Kafka Connect)", fill=ORANGE, font=11)
kafka = d.box(270, 340, 190, 70, "Kafka (KRaft)\nmỗi bảng một topic", fill=ORANGE, font=11)
# lake
d.frame(520, 70, 860, 540, "MinIO (S3) + Apache Iceberg, catalog REST (JDBC trên PostgreSQL)")
land = d.box(540, 430, 150, 90, "landing/api\nJSON thô\n(schema-on-read)", fill=YELLOW, font=10)
br = d.box(540, 120, 140, 110, "bronze\nappend sự kiện\n(key, payload, op,\nts_ms, offset)", fill="#E8C9A0", font=10)
si = d.box(700, 120, 150, 110, "silver\nlàm sạch, MERGE,\n*_rejected,\norder_status_history,\nSCD2 địa chỉ", fill="#D9DDE3", font=10)
go = d.box(860, 120, 150, 110, "gold\n10 dim + 6 fact\ncùng star schema\nmart_sales", fill="#F6E3A1", font=10)
ops = d.box(1200, 430, 160, 90, "ops\ndq_results,\nreconciliation,\nmaintenance_log", fill=PURPLE, font=10)
spark = d.box(540, 290, 310, 70, "Spark Structured Streaming (Kafka → Bronze → Silver)\n+ Spark batch (SCD2); micro-batch 30 giây", fill=GREEN, font=10)
dbt = d.box(870, 290, 330, 70, "dbt (adapter dbt-trino)\nSilver → Gold, test, lineage", fill=GREEN, font=10)
d.box(710, 410, 470, 70, "Bảng Iceberg: ACID, MERGE, time travel, rollback_to_snapshot, đổi schema không viết lại dữ liệu; tệp Parquet trong bucket lakehouse", fill="#FFFFFF", shape="rect", font=10, dashed=True)
d.box(710, 500, 470, 70, "Lưu trữ (MinIO) tách khỏi tính toán (Spark, Trino): thêm engine không phải di chuyển dữ liệu", fill="#FFFFFF", shape="rect", font=10, dashed=True)
# serving
trino = d.box(1430, 120, 200, 70, "Trino (connector Iceberg)\nuser bi_viewer: chỉ đọc gold", fill=TEAL, font=10)
sup = d.box(1430, 230, 200, 60, "Superset\ndashboard DB1", fill=TEAL, font=11)
rec = d.box(1430, 340, 200, 60, "reconcile.py\nso gold với olist_dw", fill=PURPLE, font=11)
dw = d.box(1430, 440, 200, 80, "PostgreSQL olist_dw\nkho chương 3\n(10 dim + 6 fact)", fill=BLUE, font=11)

d.arrow(csv, rep)
d.arrow(rep, pg)
d.arrow(pg, dbz, "WAL")
d.arrow(dbz, kafka)
d.arrow(kafka, spark)
d.arrow(api, col)
d.arrow(col, land, "JSON")
d.arrow(land, spark, dashed=True)
d.arrow(spark, br)
d.arrow(br, si)
d.arrow(si, dbt)
d.arrow(dbt, go)
d.arrow(go, trino)
d.arrow(trino, sup)
d.arrow(trino, rec)
d.arrow(dw, rec)
d.arrow(rec, ops, dashed=True)
d.save("lakehouse-kien-truc.drawio", "5-1_kien_truc_lakehouse.png")

# Mermaid source: copied from docs/LAKEHOUSE.md section 3.3
text = (ROOT / "docs" / "LAKEHOUSE.md").read_text(encoding="utf-8")
m = re.search(r"```mermaid\n(.*?)```", text, flags=re.S)
if m:
    (ROOT / "docs" / "lakehouse.mmd").write_text("%% Lakehouse architecture (P10); same text as docs/LAKEHOUSE.md section 3.3\n%% Render: https://mermaid.live  (or mmdc -i docs/lakehouse.mmd -o figures/5-1_kien_truc_lakehouse.png -s 2)\n" + m.group(1), encoding="utf-8")
    print("written docs/lakehouse.mmd")
