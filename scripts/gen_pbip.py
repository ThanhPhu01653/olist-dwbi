"""P8c: generate the Power BI project (PBIP, TMDL + PBIR) in powerbi/olist_base/ from the repo documents.

    python scripts/gen_pbip.py            # generate + validate (reads exports/powerbi/*.csv when present)
    python scripts/gen_pbip.py --no-csv   # skip the CSV type check

Sources (nothing about tables, columns, measures or relationships is typed here):
  powerbi/model.md     appendix  -> tables, columns, Power Query types (same as the manual fallback)
                       section 4 -> relationships;  section 6 -> hierarchies;  DAX blocks -> calculated columns
  powerbi/measures.md  -> every measure (DAX, number format, display folder by DB1-DB4)
  powerbi/theme.json   -> report theme
Output: powerbi/olist_base/{olist_base.pbip, olist_base.SemanticModel/, olist_base.Report/}
Formats follow the public Microsoft docs and JSON schemas (TMDL; PBIR: report 2.0.0, page 2.0.0, definition.pbir 4.0).
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PB = ROOT / "powerbi"
OUT = PB / "olist_base"
NAME = "olist_base"
SM = OUT / f"{NAME}.SemanticModel"
RP = OUT / f"{NAME}.Report"
NS = uuid.UUID("6f0d2a52-3b6e-4c5e-9a41-2c1f3b7a9e10")
DEFAULT_FOLDER = r"C:\Olist\01_pBI_data"
WINDOW = ("2017-01", "2018-08")


def guid(*parts: str) -> str:
    return str(uuid.uuid5(NS, "/".join(parts)))


def q(name: str) -> str:
    """TMDL object name: single quotes when it has . = : ' or whitespace (or other non-identifier characters)."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        return name
    return "'" + name.replace("'", "''") + "'"


def dq(value: str) -> str:
    """TMDL text property value in double quotes (embedded quotes doubled)."""
    return '"' + value.replace('"', '""') + '"'


# ----------------------------------------------------------------------------- parse model.md
MODEL = (PB / "model.md").read_text(encoding="utf-8")
MEAS = (PB / "measures.md").read_text(encoding="utf-8")

TYPE_MAP = {  # Power Query type -> (TMDL dataType, underlying)
    "Int64.Type": "int64",
    "type number": "double",
    "Currency.Type": "decimal",
    "type text": "string",
    "type date": "dateTime",
    "type datetime": "dateTime",
    "type datetimezone": "dateTime",
    "type logical": "boolean",
}
MONEY = {"price", "freight_value", "item_total", "payment_value", "order_value", "freight_total", "payment_total", "gmv", "freight", "monetary",
         "customer_gmv", "seller_gmv_first_90d", "declared_monthly_revenue", "avg_item_price", "gmv_per_selling_seller", "aov"}
# ETL timestamp columns are text with an offset ("2026-11-08 13:43:32.346451+07"): read as text then cut to datetime (see tables_m)
TS_TEXT = {"started_at", "finished_at", "checked_at", "taken_at", "logged_at", "last_logged_at"}

appendix = MODEL.split("<!-- APPENDIX:START -->")[1].split("<!-- APPENDIX:END -->")[0]
TABLES: dict[str, dict] = {}
for m in re.finditer(r"\*\*(\w+)\*\* – (.+?)\n\n```m\n(.*?)```", appendix, flags=re.S):
    name, desc, code = m.groups()
    cols = []
    for cn, ct in re.findall(r'\{"(\w+)",\s*([A-Za-z0-9_. ]+?)\}', code):
        ct = ct.strip()
        if cn in MONEY and ct == "type number":
            ct = "Currency.Type"
        cols.append((cn, ct))
    TABLES[name] = {"desc": desc.strip(), "cols": cols}

DIMS = [t for t in TABLES if t.startswith("dim_")]
FACTS = [t for t in TABLES if t.startswith("fact_") and t != "fact_load_issue"]
ETL = ["job_run", "v_run_summary", "v_dq_summary", "v_rejected_summary", "batch_metrics", "fact_load_issue"]
MARTS = [t for t in TABLES if t.startswith("v_") and t not in ETL]
ORDER = DIMS + FACTS + MARTS + ETL
assert set(ORDER) == set(TABLES), set(TABLES) ^ set(ORDER)

# relationships (model.md section 4)
RELS = []
for m in re.finditer(r"^\| *(\d+) *\| *(\w+)\[(\w+)\] *\| *(\w+)\[(\w+)\] *\| *\*:1 *\| *(.*?) *\|$", MODEL, flags=re.M):
    n, ft, fc, tt, tc, st = m.groups()
    RELS.append({"n": int(n), "from": (ft, fc), "to": (tt, tc), "active": "Inactive" not in st, "note": st})

# hierarchies (model.md section 6)
HIERS: dict[str, list[tuple[str, list[str]]]] = {}
sec6 = MODEL.split("## 6. Phân cấp")[1].split("## 7.")[0]
for m in re.finditer(r"^\| (dim_\w+) \| ([^|]+?) \| (.+?) \|$", sec6, flags=re.M):
    t, hn, levels = m.groups()
    HIERS.setdefault(t, []).append((hn.strip(), re.findall(r"`(\w+)`", levels)))

# calculated columns (model.md DAX blocks)
CALC: list[dict] = []
body = MODEL.split("<!-- APPENDIX:START -->")[0]
CALC_META = {  # name -> (table, TMDL dataType, hidden, sortBy)
    "Delay bucket": ("fact_order_fulfillment", "string", False, "Delay bucket order"),
    "Delay bucket order": ("fact_order_fulfillment", "int64", True, None),
    "Review type": ("fact_review", "string", False, None),
    "Delay days (order)": ("fact_review", "int64", False, None),
    "Lead days (order)": ("fact_review", "double", False, None),
    "Promised days (order)": ("fact_review", "int64", False, None),
    "Freight (order)": ("fact_review", "decimal", False, None),
    "Order value (order)": ("fact_review", "decimal", False, None),
    "Item count (order)": ("fact_review", "int64", False, None),
}
for blk in re.findall(r"```dax\n(.*?)```", body, flags=re.S):
    cur = None
    for line in blk.rstrip("\n").split("\n"):
        mm = re.match(r"^([A-Z][A-Za-z ()]*?) =\s*(.*)$", line)
        if mm and mm.group(1) in CALC_META:
            cur = {"name": mm.group(1), "lines": [mm.group(2)] if mm.group(2) else []}
            CALC.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
assert [c["name"] for c in CALC] == list(CALC_META), [c["name"] for c in CALC]

SORT_BY = {("dim_date", "month_name"): "month", ("dim_date", "day_name"): "day_of_week", ("v_review_vs_delay", "delay_bucket"): "delay_bucket_no", ("v_status_funnel", "stage"): "stage_no"}
CATEGORY = {("dim_geography", "latitude"): "Latitude", ("dim_geography", "longitude"): "Longitude", ("dim_geography", "state_code"): "StateOrProvince",
            ("dim_geography", "city"): "City", ("dim_geography", "country"): "Country", ("dim_geography", "zip_code_prefix"): "PostalCode"}

# ----------------------------------------------------------------------------- parse measures.md
SECTION_FOLDER = {}
for m in re.finditer(r"^## (\d)\. (DB\d) – (.+)$", MEAS, flags=re.M):
    SECTION_FOLDER[int(m.group(1))] = f"{m.group(2)} {m.group(3).strip()}"
SECTION_FOLDER[6] = "Cảnh báo màu"
ETL_FOLDER = "Giám sát ETL"

KM_MONEY = '[>=1000000]#,0.0,,"M";[>=1000]#,0.0,"K";#,0.00'
KM_COUNT = '[>=1000000]#,0.0,,"M";[>=1000]#,0.0,"K";#,0'
KM_MONEY_NAMES = {"GMV", "GMV last month", "GMV last year", "GMV YTD", "GMV by shipping limit date", "GMV by seller state", "Freight", "Payment value",
                  "Seller GMV (monthly)", "Seller GMV first 90d"}
KM_COUNT_NAMES = {"Orders", "Items", "Orders placed", "Failed orders", "Delivered orders", "Late orders", "Reviews", "Payments", "Customers", "Repeat customers",
                  "Delivered orders by delivery date"}

MEASURES: list[dict] = []
lines = MEAS.split("\n")
section, sub = None, None
i = 0
while i < len(lines):
    ln = lines[i]
    mm = re.match(r"^## (\d)\. ", ln)
    if mm:
        section, sub = int(mm.group(1)), None
    elif ln.startswith("## Phụ lục"):
        section, sub = "etl", None
    elif ln.startswith("## "):
        section, sub = None, None
    elif section in (1, 2, 3, 4) and ln.startswith("**"):
        sub = re.match(r"\*\*(.+?)\*\*", ln).group(1)
    if ln.startswith("```dax") and section is not None:
        j = i + 1
        blk = []
        while not lines[j].startswith("```"):
            blk.append(lines[j])
            j += 1
        i = j
        k = j + 1
        desc = []
        while k < len(lines) and lines[k].strip() and not lines[k].startswith(("#", "```", "**", "|", "<!--")):
            desc.append(lines[k].strip())
            k += 1
        first = re.match(r"^(.+?) =\s*(.*)$", blk[0])
        name, rest = first.group(1).strip(), first.group(2)
        folder = ETL_FOLDER if section == "etl" else SECTION_FOLDER[section]
        if section in (1, 2, 3, 4) and sub:
            folder = f"{folder}\\{sub}"
        text = " ".join(desc)
        fm = re.search(r"Định dạng: (.+)$", text)
        fmt = None
        if fm:
            b = re.search(r"`([^`]+)`", fm.group(1))
            fmt = b.group(1) if b else None
        if name in KM_MONEY_NAMES:
            fmt = KM_MONEY
        elif name in KM_COUNT_NAMES:
            fmt = KM_COUNT
        description = re.sub(r"\s*Định dạng:.*$", "", text).strip()
        body_lines = ([rest] if rest else []) + blk[1:]
        MEASURES.append({"name": name, "lines": body_lines, "folder": folder, "format": fmt, "desc": description})
    i += 1
assert len(MEASURES) == len({m["name"] for m in MEASURES}), "duplicate measure names"

# expected values (measures.md section 7) for README / DAX check query
EXPECTED: dict[str, tuple[str, str]] = {}
exp = MEAS.split("<!-- EXPECTED:START -->")[1].split("<!-- EXPECTED:END -->")[0]
for m in re.finditer(r"^\| (.+?) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|$", exp, flags=re.M):
    nm = re.sub(r" \(.*?\)$", "", m.group(1)) if m.group(1).startswith(("MQLs", "Active sellers")) else m.group(1)
    EXPECTED.setdefault(nm.strip(), (m.group(2).strip(), m.group(3).strip()))


CHECK_MEASURES = ["GMV", "Orders", "AOV", "Freight ratio", "Cancel rate", "On-time rate", "Avg review", "Late rate", "% negative", "MQLs", "Won deals", "Seller GMV (monthly)"]
for _n in CHECK_MEASURES:
    assert _n in EXPECTED and _n in {m["name"] for m in MEASURES}, _n


# ----------------------------------------------------------------------------- emit semantic model
def w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def types_m(tname: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Column types for fnCsv; ETL timestamps are read as text and fixed afterwards."""
    cols, fix = [], []
    for cn, ct in TABLES[tname]["cols"]:
        if ct == "type datetimezone":
            cols.append((cn, "type text"))
            fix.append(cn)
        else:
            cols.append((cn, ct))
    return cols, fix


def partition_m(tname: str) -> list[str]:
    cols, fix = types_m(tname)
    items = [f'{{"{c}", {t}}}' for c, t in cols]
    chunks = [", ".join(items[i:i + 4]) for i in range(0, len(items), 4)]
    typelines = [f"            {c}," for c in chunks]
    typelines[-1] = typelines[-1].rstrip(",")
    out = ["let", f'    Source = fnCsv("{tname}.csv", {{'] + typelines + ["        })"]
    last = "Source"
    if fix:
        tr = ", ".join(f'{{"{c}", each try DateTime.FromText(Text.Start(_, 19)) otherwise null, type nullable datetime}}' for c in fix)
        out[-1] = out[-1] + ","
        out.append(f"    Fixed = Table.TransformColumns(Source, {{{tr}}})")
        last = "Fixed"
    if tname == "dim_date":
        out[-1] = out[-1] + ","
        out.append('    NoUnknown = Table.SelectRows(' + last + ", each [date_key] <> -1),")
        out.append(f'    Window = Table.AddColumn(NoUnknown, "InWindow", each [year_month] >= "{WINDOW[0]}" and [year_month] <= "{WINDOW[1]}", type logical)')
        last = "Window"
    out += ["in", f"    {last}"]
    return out


def col_props(tname: str, cn: str, ct: str) -> list[str]:
    dt = TYPE_MAP[ct]
    p = [f"dataType: {dt}"]
    key_like = cn.endswith("_key") or cn == "etl_batch_id"
    if key_like:
        p.append("isHidden")
    if (tname, cn) == ("dim_date", "full_date"):
        p.append("isKey")
    if dt == "int64":
        if key_like or tname.startswith("dim_") or cn.startswith(("is_", "has_")) or cn in ("order_item_id", "payment_sequential", "year", "quarter", "delay_days", "promised_days", "version_no") \
                or cn.endswith(("_no", "_rank", "_score")) or cn in ("month_date_key",):
            p.append("formatString: 0")
        else:
            p.append("formatString: #,0")
    elif dt == "decimal":
        p.append(f"formatString: {dq('#,0.00')}")
    elif dt == "dateTime":
        if ct == "type date":
            p.append("formatString: yyyy-MM-dd")
        else:
            p.append("formatString: yyyy-MM-dd HH:mm:ss")
    if (tname, cn) in CATEGORY:
        p.append(f"dataCategory: {CATEGORY[(tname, cn)]}")
    if (tname, cn) in SORT_BY:
        p.append(f"sortByColumn: {q(SORT_BY[(tname, cn)])}")
    if key_like or cn in ("order_id", "order_item_id", "payment_sequential") or (dt == "int64" and (tname.startswith("dim_") or cn.startswith(("is_", "has_")) or cn in ("year", "quarter", "delay_days", "promised_days"))):
        p.append("summarizeBy: none")
    elif dt == "double" and cn in ("latitude", "longitude"):
        p.append("summarizeBy: none")
    p.append(f"sourceColumn: {cn}")
    if ct == "type date":
        pass
    return p


def table_tmdl(tname: str) -> str:
    t = TABLES[tname]
    o = [f"/// {t['desc']}", f"table {q(tname)}"]
    if tname == "dim_date":
        o.append("\tdataCategory: Time")
    o.append("")
    cols = list(t["cols"])
    if tname == "dim_date":
        cols.append(("InWindow", "type logical"))
    for cn, ct in cols:
        if tname == "dim_date" and cn == "InWindow":
            o.append(f"\t/// TRUE cho ngày trong giai đoạn {WINDOW[0]} đến {WINDOW[1]}; dùng làm bộ lọc trang của DB1-DB4")
        o.append(f"\tcolumn {q(cn)}")
        for p in col_props(tname, cn, ct):
            if p.startswith("sourceColumn"):
                o.append(f"\t\t{p}")
            else:
                o.append(f"\t\t{p}")
        if ct == "type date":
            o.append("")
            o.append("\t\tannotation UnderlyingDateTimeDataType = Date")
        o.append("")
    for c in CALC:
        tbl, dt, hidden, sort_by = CALC_META[c["name"]]
        if tbl != tname:
            continue
        o.append(f"\tcolumn {q(c['name'])} =")
        for ln in c["lines"]:
            o.append(("\t\t\t" + ln) if ln.strip() else "")
        o.append(f"\t\tdataType: {dt}")
        o.append("\t\tisDataTypeInferred")
        if hidden:
            o.append("\t\tisHidden")
        if dt == "decimal":
            o.append(f"\t\tformatString: {dq('#,0.00')}")
        elif dt == "int64":
            o.append("\t\tformatString: 0")
        if sort_by:
            o.append(f"\t\tsortByColumn: {q(sort_by)}")
        o.append("\t\tsummarizeBy: none" if dt in ("string", "int64") else "\t\tsummarizeBy: none")
        o.append("")
    for hn, levels in HIERS.get(tname, []):
        o.append(f"\thierarchy {q(hn)}")
        for n, lv in enumerate(levels):
            o.append(f"\t\tlevel {q(lv)}")
            o.append(f"\t\t\tcolumn: {q(lv)}")
            o.append(f"\t\t\tordinal: {n}")
        o.append("")
    o.append(f"\tpartition {q(tname)} = m")
    o.append("\t\tmode: import")
    o.append("\t\tsource =")
    for ln in partition_m(tname):
        o.append("\t\t\t\t" + ln)
    o.append("")
    o.append("\tannotation PBI_ResultType = Table")
    return "\n".join(o) + "\n"


def measures_tmdl() -> str:
    o = ["/// Bảng chứa các measure (không có dữ liệu); measure sắp theo thư mục DB1-DB4", "table _Measures", "\tcolumn Column1", "\t\tdataType: string", "\t\tisHidden",
         "\t\tsummarizeBy: none", "\t\tsourceColumn: Column1", ""]
    for m in MEASURES:
        # dedent body
        body = [x.rstrip() for x in m["lines"]]
        if len(body) == 1:
            expr_head, expr_body = f" {body[0].strip()}", []
        else:
            nonblank = [x for x in body if x.strip()]
            ind = min(len(x) - len(x.lstrip(" ")) for x in nonblank)
            expr_head, expr_body = "", [x[ind:] if x.strip() else "" for x in body]
        if m["desc"]:
            o.append(f"\t/// {m['desc']}")
        o.append(f"\tmeasure {q(m['name'])} ={expr_head}")
        for x in expr_body:
            o.append(("\t\t\t" + x) if x else "")
        if m["format"]:
            o.append(f"\t\tformatString: {dq(m['format'])}")
        o.append(f"\t\tdisplayFolder: {dq(m['folder'])}")
        o.append("")
    o += ["\tpartition _Measures = m", "\t\tmode: import", "\t\tsource =", "\t\t\t\tlet", "\t\t\t\t    Source = #table(type table [Column1 = text], {})", "\t\t\t\tin",
          "\t\t\t\t    Source", "", "\tannotation PBI_ResultType = Table"]
    return "\n".join(o) + "\n"


FNCSV = [
    "(fileName as text, types as list) as table =>",
    "let",
    '    Source   = Csv.Document(File.Contents(DataFolder & "\\" & fileName), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),',
    "    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),",
    '    Typed    = Table.TransformColumnTypes(Promoted, types, "en-US")',
    "in",
    "    Typed",
]


def relationships_tmdl() -> str:
    o = []
    for r in RELS:
        o.append(f"/// {r['from'][0]}.{r['from'][1]} -> {r['to'][0]}.{r['to'][1]}" + ("" if r["active"] else " (inactive: bật bằng USERELATIONSHIP)"))
        o.append(f"relationship {guid('rel', str(r['n']))}")
        if not r["active"]:
            o.append("\tisActive: false")
        o.append(f"\tfromColumn: {q(r['from'][0])}.{q(r['from'][1])}")
        o.append(f"\ttoColumn: {q(r['to'][0])}.{q(r['to'][1])}")
        o.append("")
    return "\n".join(o)


def generate() -> None:
    for old in (SM, RP):  # README.md in powerbi/olist_base/ is hand-written and stays
        if old.exists():
            shutil.rmtree(old)
    # --- project shortcut
    w(OUT / f"{NAME}.pbip", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json", "version": "1.0",
                                         "artifacts": [{"report": {"path": f"{NAME}.Report"}}], "settings": {"enableAutoRecovery": True}}, indent=2) + "\n")
    # --- semantic model
    w(SM / "definition.pbism", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
                                           "version": "4.0", "settings": {}}, indent=2) + "\n")
    w(SM / ".platform", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                                    "metadata": {"type": "SemanticModel", "displayName": NAME}, "config": {"version": "2.0", "logicalId": guid("sm")}}, indent=2) + "\n")
    d = SM / "definition"
    w(d / "database.tmdl", f"database {NAME}\n\tcompatibilityLevel: 1567\n")
    query_order = ["DataFolder", "fnCsv"] + ORDER + ["_Measures"]
    model = ["model Model", "\tculture: en-US", "\tdefaultPowerBIDataSourceVersion: powerBI_V3", "\tsourceQueryCulture: en-US", "\tdataAccessOptions", "\t\tlegacyRedirects",
             "\t\treturnErrorValuesAsNull", "", f"annotation PBI_QueryOrder = {json.dumps(query_order)}", "", "annotation __PBI_TimeIntelligenceEnabled = 0", ""]
    model += [f"ref table {q(t)}" for t in ORDER + ["_Measures"]]
    w(d / "model.tmdl", "\n".join(model) + "\n")
    expr = [f'expression DataFolder = "{DEFAULT_FOLDER}" meta [IsParameterQuery=true, IsParameterQueryRequired=true, Type="Text"]',
            "\tlineageTag: " + guid("expr", "DataFolder"), "", "\tannotation PBI_ResultType = Text", "",
            "expression fnCsv ="]
    expr += ["\t\t" + x for x in FNCSV]
    expr += ["\tlineageTag: " + guid("expr", "fnCsv"), "","\tannotation PBI_ResultType = Function"]
    w(d / "expressions.tmdl", "\n".join(expr) + "\n")
    w(d / "relationships.tmdl", relationships_tmdl())
    for t in ORDER:
        w(d / "tables" / f"{t}.tmdl", table_tmdl(t))
    w(d / "tables" / "_Measures.tmdl", measures_tmdl())
    # DAX query for the first check (Power BI Desktop DAX query view reads DAXQueries/*.dax)
    row = ",\n    ".join(f'"{n}", [{n}]' for n in CHECK_MEASURES)
    dax = ["// Kiểm tra số liệu sau Refresh: so với bảng trong README.md (và measures.md mục 7). Chạy từng khối EVALUATE.",
           "// Khối 1: toàn bộ dữ liệu (không lọc ngày)", "EVALUATE", "ROW (", "    " + row, ")", "",
           f"// Khối 2: cửa sổ {WINDOW[0]} đến {WINDOW[1]} (dim_date[InWindow] = TRUE)", "EVALUATE", "CALCULATETABLE (", "    ROW (", "        " + row.replace("\n    ", "\n        "), "    ),",
           "    dim_date[InWindow] = TRUE ()", ")", ""]
    w(SM / "DAXQueries" / "kiem_tra_so_lieu.dax", "\n".join(dax))
    # --- report (PBIR)
    w(RP / "definition.pbir", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json", "version": "4.0",
                                          "datasetReference": {"byPath": {"path": f"../{NAME}.SemanticModel"}}}, indent=2) + "\n")
    w(RP / ".platform", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
                                    "metadata": {"type": "Report", "displayName": NAME}, "config": {"version": "2.0", "logicalId": guid("rp")}}, indent=2) + "\n")
    rd = RP / "definition"
    w(rd / "version.json", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json", "version": "2.0.0"}, indent=2) + "\n")
    w(rd / "report.json", json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/2.0.0/schema.json",
        "themeCollection": {"customTheme": {"name": "olist_theme.json", "reportVersionAtImport": "5.60", "type": "RegisteredResources"}},
        "resourcePackages": [{"name": "RegisteredResources", "type": "RegisteredResources",
                              "items": [{"name": "olist_theme.json", "path": "olist_theme.json", "type": "CustomTheme"}]}],
        "settings": {"useStylableVisualContainerHeader": True},
    }, indent=2) + "\n")
    theme_dst = RP / "StaticResources" / "RegisteredResources" / "olist_theme.json"
    theme_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(PB / "theme.json", theme_dst)
    pages = [
        ("db1_tong_quan", "DB1 Tổng quan và doanh thu", None),
        ("db2_giao_hang", "DB2 Giao hàng và trải nghiệm khách", None),
        ("db3_dia_ly", "DB3 Địa lý và phí vận chuyển", None),
        ("db3_chi_tiet_bang", "DB3 Chi tiết bang", ("dim_geography", "state_code")),
        ("db4_thu_hut_seller", "DB4 Thu hút và hiệu quả seller", None),
        ("db4_chi_tiet_seller", "DB4 Chi tiết seller", ("dim_seller", "seller_id")),
    ]
    w(rd / "pages" / "pages.json", json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
                                               "pageOrder": [p[0] for p in pages], "activePageName": pages[0][0]}, indent=2) + "\n")
    for pid, title, drill in pages:
        page = {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json", "name": pid, "displayName": title,
                "displayOption": "FitToPage", "height": 720, "width": 1280}
        if drill:
            ent, prop = drill
            fexpr = {"Column": {"Expression": {"SourceRef": {"Entity": ent}}, "Property": prop}}
            fname = f"f_{pid}"
            page["type"] = "Drillthrough"
            page["filterConfig"] = {"filters": [{"name": fname, "field": fexpr, "type": "Categorical", "howCreated": "Drillthrough"}]}
            page["pageBinding"] = {"name": guid("binding", pid), "type": "Drillthrough",
                                   "parameters": [{"name": f"p_{pid}", "boundFilter": fname, "fieldExpr": fexpr}]}
        w(rd / "pages" / pid / "page.json", json.dumps(page, indent=2, ensure_ascii=False) + "\n")


# ----------------------------------------------------------------------------- validation (reads the documents, not the generated files)
def dax_text(m: dict) -> str:
    return "\n".join(m["lines"])


def validate(check_csv: bool) -> list[str]:
    log: list[str] = []
    cols = {t: {c for c, _ in TABLES[t]["cols"]} for t in TABLES}
    cols["dim_date"].add("InWindow")
    ctype = {t: dict(TABLES[t]["cols"]) for t in TABLES}
    for c in CALC:
        tbl, dt, _, _ = CALC_META[c["name"]]
        cols[tbl].add(c["name"])
    cols["_Measures"] = {"Column1"}
    names = {m["name"] for m in MEASURES}
    errors = 0
    # 1. every table[column] and [measure] reference
    items = [(m["name"], dax_text(m)) for m in MEASURES] + [(c["name"], "\n".join(c["lines"])) for c in CALC]
    for nm, code in items:
        code_nostr = re.sub(r'"[^"]*"', '""', code)
        for t, c in re.findall(r"'?([A-Za-z_][\w]*)'?\[([^\]]+)\]", code_nostr):
            if t not in cols:
                log.append(f"ERROR {nm}: unknown table {t}")
                errors += 1
            elif c not in cols[t]:
                log.append(f"ERROR {nm}: unknown column {t}[{c}]")
                errors += 1
        for c in re.findall(r"(?<![\w'\]])\[([^\]]+)\]", code_nostr):
            if c not in names:
                log.append(f"ERROR {nm}: unknown measure [{c}]")
                errors += 1
        for t in re.findall(r"\b(?:COUNTROWS|FILTER|ALL|VALUES|SUM|DISTINCTCOUNT)\s*\(\s*(\w+)\s*[,)]", code_nostr):
            if t in TABLES and t not in cols:
                errors += 1
    log.append(f"measures checked: {len(MEASURES)} + {len(CALC)} calculated columns -> {errors} errors")
    # 2. relationships
    rerr = 0
    for r in RELS:
        (ft, fc), (tt, tc) = r["from"], r["to"]
        a, b = ctype.get(ft, {}).get(fc), ctype.get(tt, {}).get(tc)
        if a is None or b is None or TYPE_MAP[a] != TYPE_MAP[b]:
            log.append(f"ERROR relationship #{r['n']} {ft}[{fc}] ({a}) -> {tt}[{tc}] ({b})")
            rerr += 1
    nact = sum(r["active"] for r in RELS)
    # role-playing: at most one active relationship per pair of tables
    pairs: dict[tuple[str, str], int] = {}
    for r in RELS:
        if r["active"]:
            pairs[(r["from"][0], r["to"][0])] = pairs.get((r["from"][0], r["to"][0]), 0) + 1
    multi = {k: v for k, v in pairs.items() if v > 1}
    for k in multi:
        log.append(f"ERROR more than one active relationship {k}")
        rerr += 1
    log.append(f"relationships: {len(RELS)} ({nact} active, {len(RELS) - nact} inactive) -> {rerr} errors")
    # 3. hierarchies and sort columns exist
    herr = 0
    for t, hs in HIERS.items():
        for hn, lv in hs:
            for c in lv:
                if c not in cols[t]:
                    log.append(f"ERROR hierarchy {t}.{hn}: column {c}")
                    herr += 1
    for (t, c), s in SORT_BY.items():
        if c not in cols[t] or s not in cols[t]:
            log.append(f"ERROR sort-by {t}.{c} by {s}")
            herr += 1
    log.append(f"hierarchies: {sum(len(v) for v in HIERS.values())}; sort-by: {len(SORT_BY) + 1} -> {herr} errors")
    # 4. CSV header + value shape per M type
    if check_csv:
        folder = ROOT / "exports" / "powerbi"
        pat = {"Int64.Type": re.compile(r"^-?\d+$"), "type number": re.compile(r"^-?\d+(\.\d+)?([eE][-+]?\d+)?$"), "Currency.Type": re.compile(r"^-?\d+(\.\d{1,4})?$"),
               "type date": re.compile(r"^\d{4}-\d{2}-\d{2}$"), "type datetime": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$"),
               "type logical": re.compile(r"^(true|false)$", re.I), "type datetimezone": re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}(:?\d{2})?$")}
        cerr = 0
        for t in ORDER:
            f = folder / f"{t}.csv"
            if not f.exists():
                log.append(f"SKIP {t}.csv not found")
                continue
            with f.open(encoding="utf-8-sig", newline="") as fh:
                rd = csv.reader(fh)
                head = next(rd)
                want = [c for c, _ in TABLES[t]["cols"]]
                if head != want:
                    log.append(f"ERROR {t}.csv header differs: {set(head) ^ set(want)}")
                    cerr += 1
                    continue
                bad: dict[str, str] = {}
                nrows = 0
                for row in rd:
                    nrows += 1
                    for (c, ct), v in zip(TABLES[t]["cols"], row):
                        if v == "" or ct == "type text" or c in bad:
                            continue
                        if not pat[ct].match(v):
                            bad[c] = v
                for c, v in bad.items():
                    log.append(f"ERROR {t}.{c}: value {v!r} does not fit {dict(TABLES[t]['cols'])[c]}")
                    cerr += 1
            log.append(f"  {t}.csv: {len(want)} columns, {nrows} rows OK" if not bad else f"  {t}.csv: problems")
        # the "one" side of every relationship must have unique, non-blank key values; the "many" side keys must exist there (or be -1 / blank)
        keys = {(r["to"][0], r["to"][1]) for r in RELS}
        uniq: dict[tuple[str, str], set] = {}
        for (t, c) in sorted(keys):
            f = folder / f"{t}.csv"
            if not f.exists():
                continue
            with f.open(encoding="utf-8-sig", newline="") as fh:
                rd = csv.DictReader(fh)
                vals = [r[c] for r in rd]
            if t == "dim_date":
                vals = [v for v in vals if v != "-1"]
            if len(vals) != len(set(vals)) or "" in vals:
                log.append(f"ERROR relationship target {t}[{c}] has duplicate or blank values")
                cerr += 1
            uniq[(t, c)] = set(vals)
        orphan_total = 0
        for r in RELS:
            f = folder / f"{r['from'][0]}.csv"
            if not f.exists() or r["to"] not in uniq:
                continue
            with f.open(encoding="utf-8-sig", newline="") as fh:
                miss = sum(1 for row in csv.DictReader(fh) if row[r["from"][1]] not in uniq[r["to"]] and row[r["from"][1]] not in ("", "-1"))
            if miss:
                log.append(f"  note: relationship #{r['n']} {r['from'][0]}[{r['from'][1]}]: {miss} rows with no match in {r['to'][0]}")
                orphan_total += miss
        log.append(f"relationship keys: unique on the one side; rows without a match (other than -1): {orphan_total}")
        log.append(f"CSV check -> {cerr} errors")
    return log


def fill_readme() -> None:
    f = OUT / "README.md"
    if not f.exists():
        return
    rows = ["| Measure | Kỳ vọng: toàn bộ dữ liệu | Kỳ vọng: cửa sổ 2017-01 → 2018-08 | Giá trị thật (ghi lại) |", "| --- | ---: | ---: | --- |"]
    for n in CHECK_MEASURES:
        a, b = EXPECTED[n]
        rows.append(f"| {n} | {a} | {b} | |")
    txt = f.read_text(encoding="utf-8")
    txt = re.sub(r"<!-- EXPECTED:START -->.*?<!-- EXPECTED:END -->", lambda _m: "<!-- EXPECTED:START -->\n" + "\n".join(rows) + "\n<!-- EXPECTED:END -->", txt, flags=re.S)
    f.write_text(txt, encoding="utf-8", newline="\n")


def main() -> None:
    generate()
    fill_readme()
    log = validate("--no-csv" not in sys.argv)
    print("\n".join(log))
    files = [p for p in OUT.rglob("*") if p.is_file()]
    print(f"\ntables: {len(ORDER)} data + _Measures; relationships: {len(RELS)}; measures: {len(MEASURES)}; calculated columns: {len(CALC)}; files written: {len(files)}")
    if any(x.startswith("ERROR") for x in log):
        sys.exit(1)


if __name__ == "__main__":
    main()
