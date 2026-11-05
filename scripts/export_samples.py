"""P2: before/after samples of the ODS cleaning -> handoff/before-after-samples.md + figures/3-4-3_before_after_<table>.png.

For each table with a transformation: 5 rows of the SAME records in staging (before) and ods (after); changed cells are highlighted.
    python scripts/export_samples.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "eda"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import text

from etl import config
from etl.db import get_engine

AMBER = "#fde8b0"
HEAD = "#2a78d6"
engine = get_engine(config.DB_NAME)
ROOT = config.ROOT


def q(sql: str, **p) -> pd.DataFrame:
    with engine.connect() as c:
        return pd.read_sql_query(text(sql), c, params=p or None)


def norm(v) -> str:
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NaT else str(v).strip().lower()


def short(v, n=26) -> str:
    s = "NULL" if v is None or v is pd.NaT or (isinstance(v, float) and pd.isna(v)) else str(v)
    s = s.replace("[", "{").replace("]", "}") if s.startswith("[") else s
    return s if len(s) <= n else s[: n - 1] + "…"


def draw_table(ax, df: pd.DataFrame, changed: pd.DataFrame, title: str) -> None:
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=11, fontweight="bold")
    cells = [[short(v) for v in row] for row in df.itertuples(index=False)]
    tb = ax.table(cellText=cells, colLabels=list(df.columns), loc="upper left", cellLoc="left")
    tb.auto_set_font_size(False)
    tb.set_fontsize(8.5)
    tb.scale(1, 1.55)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#e1e0d9")
        if r == 0:
            cell.set_facecolor(HEAD)
            cell.set_text_props(color="white", fontweight="bold")
        elif changed.iloc[r - 1, c]:
            cell.set_facecolor(AMBER)
    tb.auto_set_column_width(list(range(len(df.columns))))


def render(name: str, before: pd.DataFrame, after: pd.DataFrame, cb: pd.DataFrame, ca: pd.DataFrame, rule: str) -> str:
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(max(9, 1.35 * max(len(before.columns), len(after.columns))), 1.0 + 0.36 * (len(before) + len(after) + 4)))
    draw_table(a1, before, cb, f"TRƯỚC (staging.stg_{name})")
    draw_table(a2, after, ca, f"SAU (ods.{name})")
    fig.suptitle(f"{name}: {rule}   (ô tô vàng = giá trị bị thay đổi)", x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    path = ROOT / "figures" / f"3-4-3_before_after_{name}.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return f"figures/{path.name}"


def md(df: pd.DataFrame) -> str:
    rows = ["| " + " | ".join(map(str, df.columns)) + " |", "| " + " | ".join("---" for _ in df.columns) + " |"]
    rows += ["| " + " | ".join(short(v, 40).replace("|", "\\|") for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


def paired(name: str, keys_sql: str, key: str, bcols: list[str], acols: list[str], rule: str, extra_after: int = 0):
    """bcols / acols are aligned by position (renames); the last `extra_after` columns of acols exist only after cleaning."""
    keys = q(keys_sql)[key].tolist()
    if not keys:
        return name, None, None, None, None, rule
    b = q(f"SELECT {', '.join(bcols)} FROM staging.stg_{name} WHERE {key} = ANY(:k) ORDER BY {key}", k=keys)
    a = q(f"SELECT {', '.join(acols)} FROM ods.{name} WHERE {acols[0]} = ANY(:k) ORDER BY {acols[0]}", k=keys)
    n_pair = len(bcols)
    cb = pd.DataFrame(False, index=b.index, columns=b.columns)
    ca = pd.DataFrame(False, index=a.index, columns=a.columns)
    for i in range(len(b)):
        for j in range(n_pair):
            if norm(b.iloc[i, j]) != norm(a.iloc[i, j]):
                cb.iloc[i, j] = ca.iloc[i, j] = True
        for j in range(n_pair, n_pair + extra_after):
            ca.iloc[i, j] = bool(a.iloc[i, j] not in (None, "{}", []) and len(a.iloc[i, j]) > 0) if isinstance(a.iloc[i, j], list) else True
    for df in (b, a):
        for c in df.columns:
            if str(c).endswith("id") and df[c].dtype == object:
                df[c] = df[c].str[:8] + "…"
    return name, b, a, cb, ca, rule


def main() -> None:
    (ROOT / "figures").mkdir(exist_ok=True)
    out = ["# Mẫu trước / sau khi làm sạch (staging → ods)", "",
           "*Sinh tự động bởi `scripts/export_samples.py` trên `olist_dw`. Mỗi bảng: 5 bản ghi của cùng một đối tượng ở staging và ods; ô thay đổi được tô vàng trong ảnh.*", ""]
    specs = []
    specs.append(paired("products",
        "(SELECT product_id FROM staging.stg_products WHERE product_category_name IS NULL ORDER BY product_id LIMIT 3) UNION ALL "
        "(SELECT product_id FROM staging.stg_products WHERE product_weight_g IS NULL OR product_weight_g = 0 ORDER BY product_id LIMIT 2)", "product_id",
        ["product_id", "product_category_name", "product_name_lenght", "product_description_lenght", "product_weight_g"],
        ["product_id", "product_category_name", "name_length", "description_length", "weight_g", "dq_missing_dimensions"],
        "danh mục rỗng → 'unknown'; *_lenght → *_length; cờ dq_missing_dimensions", extra_after=1))
    specs.append(paired("orders",
        "SELECT order_id FROM (SELECT DISTINCT ON (f) order_id, f FROM ods.orders, unnest(dq_flags) f ORDER BY f, order_id) x LIMIT 5", "order_id",
        ["order_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date"],
        ["order_id", "order_status", "order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "dq_flags"],
        "giữ nguyên đơn, thêm cờ lỗi dq_flags", extra_after=1))
    specs.append(paired("order_payments",
        "(SELECT order_id FROM staging.stg_order_payments WHERE payment_installments = 0 LIMIT 2) UNION ALL "
        "(SELECT order_id FROM staging.stg_order_payments WHERE payment_type = 'not_defined' LIMIT 3)", "order_id",
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value", "dq_flags"],
        "installments 0 → 1; cờ cho not_defined / giá trị 0", extra_after=1))
    specs.append(paired("mql",
        "SELECT mql_id FROM staging.stg_mql WHERE origin IS NULL ORDER BY mql_id LIMIT 5", "mql_id",
        ["mql_id", "first_contact_date", "landing_page_id", "origin"], ["mql_id", "first_contact_date", "landing_page_id", "origin"],
        "origin NULL → 'unknown'"))
    specs.append(paired("closed_deals",
        "SELECT mql_id FROM staging.stg_closed_deals WHERE has_company IS NULL OR business_segment IS NULL OR lead_type IS NULL ORDER BY (business_segment IS NULL) DESC, mql_id LIMIT 5", "mql_id",
        ["mql_id", "business_segment", "lead_type", "lead_behaviour_profile", "has_company", "average_stock", "declared_monthly_revenue"],
        ["mql_id", "business_segment", "lead_type", "lead_behaviour_profile", "has_company", "average_stock", "declared_monthly_revenue", "dq_flags"],
        "NULL → 'unknown' cho cột phân loại; cờ declared = 0", extra_after=1))
    specs.append(paired("sellers",
        "(SELECT seller_id FROM staging.stg_sellers WHERE seller_city <> lower(unaccent(trim(seller_city))) LIMIT 1) UNION ALL "
        "(SELECT seller_id FROM staging.stg_sellers WHERE seller_city = lower(unaccent(trim(seller_city))) ORDER BY seller_id LIMIT 4)", "seller_id",
        ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"], ["seller_id", "zip_code_prefix", "city", "state_code"],
        "city = lower(unaccent(trim())); zip = char(5)"))
    for name, b, a, cb, ca, rule in specs:
        if b is None:
            out += [f"## {name} – {rule}", "", "Không có bản ghi cần làm sạch theo quy tắc này trong dữ liệu nạp ban đầu (đến 2017-12-31); chạy lại sau các đợt incremental.", ""]
            continue
        fig = render(name, b, a, cb, ca, rule)
        out += [f"## {name} – {rule}", "", f"Ảnh: `{fig}`", "", "**Trước (staging)**", "", md(b), "", "**Sau (ods)**", "", md(a), ""]

    # geolocation: several raw points of one zip -> one cleaned row
    zip_ = q("SELECT geolocation_zip_code_prefix AS z FROM staging.stg_geolocation GROUP BY 1 HAVING count(DISTINCT geolocation_city) > 1 "
             "AND count(*) BETWEEN 6 AND 12 ORDER BY 1 LIMIT 1").z.iloc[0]
    b = q("SELECT geolocation_zip_code_prefix, geolocation_lat, geolocation_lng, geolocation_city, geolocation_state FROM staging.stg_geolocation "
          "WHERE geolocation_zip_code_prefix = :z ORDER BY geolocation_city, geolocation_lat LIMIT 5", z=zip_)
    a = q("SELECT zip_code_prefix, latitude, longitude, city, state_code, n_points FROM ods.geolocation_zip WHERE zip_code_prefix = :z", z=zip_)
    cb = pd.DataFrame(False, index=b.index, columns=b.columns)
    ca = pd.DataFrame(True, index=a.index, columns=a.columns)
    ca.iloc[0, 0] = False
    cb.iloc[:, 1:4] = True
    rule = "nhiều điểm / zip → 1 dòng (median lat/lng, mode city/state, city chuẩn hoá)"
    fig = render("geolocation", b, a, cb, ca, rule)
    out += [f"## geolocation → geolocation_zip – {rule}", "", f"Ảnh: `{fig}`", "", f"**Trước (staging)**: 5 trong số các điểm của zip {zip_}", "", md(b), "", "**Sau (ods.geolocation_zip)**", "", md(a), ""]
    (ROOT / "handoff" / "before-after-samples.md").write_text("\n".join(out), encoding="utf-8")
    print("written handoff/before-after-samples.md;", len(list((ROOT / "figures").glob("3-4-3_before_after_*.png"))), "figures")


if __name__ == "__main__":
    main()
