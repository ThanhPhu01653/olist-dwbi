"""Create the DB1 dashboard in Superset (Step 10): database connection to Trino as the read-only user bi_viewer, four datasets, four charts, one dashboard.

    python lakehouse/scripts/superset_setup.py [--export lakehouse/superset/db1_export.zip]

Superset (http://127.0.0.1:8088) must be running (docker compose --profile demo up -d superset). Safe to rerun: existing objects with the same
name are reused, charts are updated in place. Every query goes through Trino with bi_viewer, which can only SELECT from iceberg.gold.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lh_env import ROOT, load_env  # noqa: E402

env = load_env()
BASE = f"http://127.0.0.1:{env.get('LH_SUPERSET_PORT', '8088')}"
ap = argparse.ArgumentParser()
ap.add_argument("--export")
a = ap.parse_args()

s = requests.Session()
r = s.post(f"{BASE}/api/v1/security/login", json={"username": "admin", "password": env["LH_SUPERSET_ADMIN_PASSWORD"], "provider": "db", "refresh": True}, timeout=60)
r.raise_for_status()
s.headers["Authorization"] = "Bearer " + r.json()["access_token"]
s.headers["Referer"] = BASE
s.headers["X-CSRFToken"] = s.get(f"{BASE}/api/v1/security/csrf_token/", timeout=60).json()["result"]


def call(method, path, **kw):
    resp = s.request(method, BASE + path, timeout=120, **kw)
    if resp.status_code >= 400:
        print("ERROR", method, path, resp.status_code, resp.text[:600])
        resp.raise_for_status()
    return resp.json() if resp.content else {}


def find(path, name_field, name):
    q = json.dumps({"filters": [{"col": name_field, "opr": "eq", "value": name}]})
    res = call("GET", path, params={"q": q})["result"]
    return res[0]["id"] if res else None


# ---------------------------------------------------------------- database
DB_NAME = "Olist Gold (Trino, bi_viewer)"
db_id = find("/api/v1/database/", "database_name", DB_NAME)
if not db_id:
    db_id = call("POST", "/api/v1/database/", json={"database_name": DB_NAME, "sqlalchemy_uri": "trino://bi_viewer@trino:8080/iceberg/gold", "expose_in_sqllab": True})["id"]
print("database id", db_id)

# ---------------------------------------------------------------- datasets
DATASETS = {}
for t in ("mart_sales_daily", "mart_sales_state_month", "mart_sales_category_month"):
    q = json.dumps({"filters": [{"col": "table_name", "opr": "eq", "value": t}]})
    res = call("GET", "/api/v1/dataset/", params={"q": q})["result"]
    ds_id = res[0]["id"] if res else call("POST", "/api/v1/dataset/", json={"database": db_id, "schema": "gold", "table_name": t})["id"]
    DATASETS[t] = ds_id
print("datasets", DATASETS)
# the day column must be temporal for the monthly line
cols = call("GET", f"/api/v1/dataset/{DATASETS['mart_sales_daily']}")["result"]["columns"]
fix = [{"id": c["id"], "column_name": c["column_name"], "is_dttm": True} for c in cols if c["column_name"] == "full_date" and not c.get("is_dttm")]
if fix:
    call("PUT", f"/api/v1/dataset/{DATASETS['mart_sales_daily']}", json={"columns": [{"id": c["id"], "column_name": c["column_name"], "type": c.get("type"), "is_dttm": c["column_name"] == "full_date" or bool(c.get("is_dttm")), "filterable": True, "groupby": True} for c in cols]})


def metric(sql, label):
    return {"expressionType": "SQL", "sqlExpression": sql, "label": label, "hasCustomLabel": True}


GMV = metric("SUM(gmv)", "GMV (BRL)")
IN_WINDOW = {"expressionType": "SQL", "clause": "WHERE", "sqlExpression": "in_window", "comparator": None, "subject": None, "operator": None}
CHARTS = [
    dict(name="DB1 · GMV tổng (BRL)", ds="mart_sales_daily", viz="big_number_total",
         params={"metric": GMV, "adhoc_filters": [], "header_font_size": 0.5, "subheader_font_size": 0.15, "y_axis_format": ",.2f", "subheader": "đơn không thuộc nhóm Failed", "time_range": "No filter"}),
    dict(name="DB1 · GMV theo tháng", ds="mart_sales_daily", viz="echarts_timeseries_line",
         params={"x_axis": "full_date", "time_grain_sqla": "P1M", "x_axis_sort_asc": True, "metrics": [GMV], "groupby": [], "adhoc_filters": [IN_WINDOW], "row_limit": 10000,
                 "y_axis_format": ",.0f", "show_legend": False, "markerEnabled": True, "markerSize": 6, "time_range": "No filter", "truncateYAxis": False, "y_axis_title": "BRL", "y_axis_title_margin": 40}),
    dict(name="DB1 · GMV theo bang", ds="mart_sales_state_month", viz="echarts_timeseries_bar",
         params={"x_axis": "state_code", "metrics": [GMV], "groupby": [], "adhoc_filters": [], "orientation": "vertical", "row_limit": 27, "x_axis_sort": "GMV (BRL)", "x_axis_sort_asc": False,
                 "show_legend": False, "y_axis_format": ",.0f", "time_range": "No filter", "show_value": False}),
    dict(name="DB1 · GMV theo danh mục (10 cao nhất)", ds="mart_sales_category_month", viz="echarts_timeseries_bar",
         params={"x_axis": "category_name_en", "metrics": [GMV], "groupby": [], "adhoc_filters": [], "orientation": "horizontal", "row_limit": 10, "x_axis_sort": "GMV (BRL)", "x_axis_sort_asc": True,   # horizontal bars start at the bottom: ascending puts the largest on top
                 "show_legend": False, "y_axis_format": ",.0f", "time_range": "No filter", "show_value": False}),
]
chart_ids = []
for c in CHARTS:
    params = {"viz_type": c["viz"], "datasource": f"{DATASETS[c['ds']]}__table", **c["params"]}
    body = {"slice_name": c["name"], "viz_type": c["viz"], "datasource_id": DATASETS[c["ds"]], "datasource_type": "table", "params": json.dumps(params)}
    cid = find("/api/v1/chart/", "slice_name", c["name"])
    if cid:
        call("PUT", f"/api/v1/chart/{cid}", json=body)
    else:
        cid = call("POST", "/api/v1/chart/", json=body)["id"]
    chart_ids.append(cid)
    # run the query once to prove that Trino (as bi_viewer) answers
    data = call("POST", "/api/v1/chart/data", json={"datasource": {"id": DATASETS[c["ds"]], "type": "table"}, "force": True, "queries": [{
        "metrics": [m for m in params.get("metrics", [params.get("metric")]) if m], "columns": ([params["x_axis"]] if params.get("x_axis") and params["x_axis"] != "full_date" else []),
        "row_limit": 5, "filters": []}], "result_format": "json", "result_type": "full"})
    print("chart", cid, c["name"], "->", str(data["result"][0].get("data"))[:90])

# ---------------------------------------------------------------- dashboard
TITLE = "DB1 – Tổng quan doanh thu (Gold, Trino)"


def chart_node(i, cid, width, height):
    return {"type": "CHART", "id": f"CHART-{cid}", "children": [], "parents": ["ROOT_ID", "GRID_ID", f"ROW-{i}"],
            "meta": {"width": width, "height": height, "chartId": cid, "sliceName": CHARTS[chart_ids.index(cid)]["name"]}}


position = {
    "DASHBOARD_VERSION_KEY": "v2",
    "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
    "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": ["ROW-1", "ROW-2"], "parents": ["ROOT_ID"]},
    "HEADER_ID": {"id": "HEADER_ID", "type": "HEADER", "meta": {"text": TITLE}},
    "ROW-1": {"type": "ROW", "id": "ROW-1", "children": [f"CHART-{chart_ids[0]}", f"CHART-{chart_ids[1]}"], "parents": ["ROOT_ID", "GRID_ID"], "meta": {"background": "BACKGROUND_TRANSPARENT"}},
    "ROW-2": {"type": "ROW", "id": "ROW-2", "children": [f"CHART-{chart_ids[2]}", f"CHART-{chart_ids[3]}"], "parents": ["ROOT_ID", "GRID_ID"], "meta": {"background": "BACKGROUND_TRANSPARENT"}},
    f"CHART-{chart_ids[0]}": chart_node(1, chart_ids[0], 4, 40),
    f"CHART-{chart_ids[1]}": chart_node(1, chart_ids[1], 8, 40),
    f"CHART-{chart_ids[2]}": chart_node(2, chart_ids[2], 6, 55),
    f"CHART-{chart_ids[3]}": chart_node(2, chart_ids[3], 6, 55),
}
dash_id = find("/api/v1/dashboard/", "dashboard_title", TITLE)
body = {"dashboard_title": TITLE, "slug": "db1-gold", "published": True, "position_json": json.dumps(position), "json_metadata": json.dumps({"color_scheme": "supersetColors"})}
if dash_id:
    call("PUT", f"/api/v1/dashboard/{dash_id}", json=body)
else:
    dash_id = call("POST", "/api/v1/dashboard/", json=body)["id"]
for cid in chart_ids:
    call("PUT", f"/api/v1/chart/{cid}", json={"dashboards": [dash_id]})
print("dashboard", dash_id, f"{BASE}/superset/dashboard/db1-gold/")

if a.export:
    out = ROOT / a.export
    out.parent.mkdir(parents=True, exist_ok=True)
    resp = s.get(f"{BASE}/api/v1/dashboard/export/", params={"q": json.dumps([dash_id])}, timeout=120)
    resp.raise_for_status()
    out.write_bytes(resp.content)
    print("exported", a.export, len(resp.content), "bytes")
