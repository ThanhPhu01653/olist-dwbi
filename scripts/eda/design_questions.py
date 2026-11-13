"""P1 step 6: numeric answers for the design review (12/11) -> handoff/design-questions.md + docs/category_group_draft.csv.

a) customers with more than one zip  -> SCD2 or SCD1 for dim_customer
b) funnel sellers with orders + GMV  -> depth of dashboard DB4
c) fact_seller_monthly dense vs sparse -> number of rows
d) every product category with its orders -> product category group table (draft mapping to approve)
e) customer / seller zips that are missing from geolocation -> how to build dim_geography
"""
from __future__ import annotations

from common import *  # noqa: F401,F403

# Draft mapping category (pt) -> group (DW_DESIGN 6.5). To be reviewed by the team; becomes seeds/category_group.csv in P2.
GROUPS = {
    "Home & Furniture": ["casa_conforto", "casa_conforto_2", "cama_mesa_banho", "moveis_colchao_e_estofado",
                         "moveis_cozinha_area_de_servico_jantar_e_jardim", "moveis_decoracao", "moveis_quarto", "moveis_sala",
                         "utilidades_domesticas", "eletrodomesticos", "eletrodomesticos_2", "eletroportateis",
                         "portateis_casa_forno_e_cafe", "portateis_cozinha_e_preparadores_de_alimentos", "climatizacao", "la_cuisine"],
    "Health & Beauty": ["beleza_saude", "perfumaria"],
    "Electronics & Computers": ["audio", "eletronicos", "informatica_acessorios", "pcs", "pc_gamer", "tablets_impressao_imagem",
                                "telefonia", "telefonia_fixa", "consoles_games", "cine_foto"],
    "Fashion & Accessories": ["fashion_bolsas_e_acessorios", "fashion_calcados", "fashion_esporte", "fashion_roupa_feminina",
                              "fashion_roupa_infanto_juvenil", "fashion_roupa_masculina", "fashion_underwear_e_moda_praia", "malas_acessorios"],
    "Sports & Leisure": ["esporte_lazer"],
    "Toys & Baby": ["brinquedos", "bebes", "fraldas_higiene"],
    "Books, Media & Music": ["livros_importados", "livros_interesse_geral", "livros_tecnicos", "cds_dvds_musicais", "dvds_blu_ray",
                             "musica", "instrumentos_musicais"],
    "Food & Drinks": ["alimentos", "alimentos_bebidas", "bebidas"],
    "Auto & Tools": ["automotivo", "ferramentas_jardim", "casa_construcao", "construcao_ferramentas_construcao",
                     "construcao_ferramentas_ferramentas", "construcao_ferramentas_iluminacao", "construcao_ferramentas_jardim",
                     "construcao_ferramentas_seguranca", "sinalizacao_e_seguranca", "agro_industria_e_comercio",
                     "industria_comercio_e_negocios"],
    "Office & Stationery": ["papelaria", "moveis_escritorio"],
    "Gifts & Others": ["relogios_presentes", "cool_stuff", "artigos_de_festas", "artigos_de_natal", "flores", "market_place",
                       "seguros_e_servicos", "artes", "artes_e_artesanato", "pet_shop"],
    "Unknown": ["unknown"],
}
CATEGORY_GROUP = {c: g for g, cs in GROUPS.items() for c in cs}
CHANNEL_GROUP = {"organic_search": "Organic", "direct_traffic": "Organic", "referral": "Organic", "paid_search": "Paid",
                 "display": "Paid", "other_publicities": "Paid", "social": "Social", "email": "Email", "other": "Other / Unknown",
                 "unknown": "Other / Unknown"}


def q_a() -> tuple[list[str], dict]:
    r = q("""
    WITH o AS (SELECT c.customer_unique_id AS uid, c.customer_zip_code_prefix AS zip, c.customer_city AS city, c.customer_state AS st,
                      o.order_purchase_timestamp AS ts, o.order_id
               FROM oltp.orders o JOIN oltp.customers c USING (customer_id)),
         seq AS (SELECT *, lag(zip) OVER w AS pz, lag(st) OVER w AS pst, first_value(zip) OVER w AS z1, row_number() OVER w AS rn, count(*) OVER (PARTITION BY uid) AS n_orders
                 FROM o WINDOW w AS (PARTITION BY uid ORDER BY ts, order_id)),
         per AS (SELECT uid, max(n_orders) AS n_orders, count(DISTINCT zip) AS zips, count(DISTINCT st) AS states,
                        count(*) FILTER (WHERE pz IS NOT NULL AND pz <> zip) AS changes,
                        count(*) FILTER (WHERE pst IS NOT NULL AND pst <> st) AS state_changes,
                        count(*) FILTER (WHERE rn > 1 AND zip <> z1) AS orders_after_first_zip
                 FROM seq GROUP BY uid)
    SELECT count(*) AS customers, count(*) FILTER (WHERE n_orders > 1) AS repeat_customers,
           count(*) FILTER (WHERE zips > 1) AS multi_zip, count(*) FILTER (WHERE zips = 2) AS zips2, count(*) FILTER (WHERE zips = 3) AS zips3,
           count(*) FILTER (WHERE zips >= 4) AS zips4p, count(*) FILTER (WHERE states > 1) AS multi_state,
           sum(changes) AS changes, sum(state_changes) AS state_changes, sum(n_orders) AS orders,
           max(zips) AS max_zips,
           sum(orders_after_first_zip) AS orders_other_zip
    FROM per""").iloc[0]
    # "customer_id" rows in the source: one per order
    cust_rows = int(scalar("SELECT count(*) FROM oltp.customers"))
    r = r.astype(float)
    uniq, rep, multi = int(r.customers), int(r.repeat_customers), int(r.multi_zip)
    versions = uniq + int(r.changes)
    lines = [
        "## a) Bao nhiêu `customer_unique_id` có hơn 1 zip qua các đơn? (SCD2 hay SCD1 cho `dim_customer`)", "",
        "**Số liệu**", "",
        md_table(pd.DataFrame({"Chỉ tiêu": [
            "Số dòng customers trong nguồn (mỗi đơn một `customer_id`)", "Số khách thật (`customer_unique_id`)", "Khách có từ 2 đơn trở lên",
            "Khách có hơn 1 zip trên các đơn", "  – đúng 2 zip", "  – đúng 3 zip", "  – từ 4 zip trở lên (nhiều nhất " + n(int(r.max_zips)) + " zip / khách)",
            "Khách đổi sang bang khác", "Số lần đổi zip (= số phiên bản SCD2 phát sinh thêm)", "Số dòng `dim_customer` nếu SCD1", "Số dòng `dim_customer` nếu SCD2",
            "Số đơn đặt từ một zip khác zip của đơn đầu tiên"],
            "Giá trị": [n(cust_rows), n(uniq), f"{n(rep)} ({pct(100 * rep / uniq)} khách)", f"{n(multi)} ({pct(100 * multi / uniq, 2)} khách; {pct(100 * multi / rep)} khách quay lại)",
                        n(int(r.zips2)), n(int(r.zips3)), n(int(r.zips4p)), n(int(r.multi_state)), n(int(r.changes)), n(uniq),
                        f"{n(versions)} (+{pct(100 * r.changes / uniq, 2)})", f"{n(int(r.orders_other_zip))} ({pct(100 * r.orders_other_zip / r.orders, 2)} tổng số đơn)"]}), []), "",
        "**Phương án**", "",
        "1. **SCD1** – ghi đè địa chỉ bằng bản mới nhất: đơn giản, mỗi khách một dòng; nhưng các đơn cũ bị gắn vào địa chỉ mới. "
        "Ảnh hưởng thực tế rất nhỏ vì địa lý của đơn đã nằm trong fact qua `customer_geography_key`, nên phân tích theo vùng không bị sai.",
        f"2. **SCD2** (đặc tả hiện tại) – giữ lịch sử địa chỉ: thêm {n(int(r.changes))} dòng ({pct(100 * r.changes / uniq, 2)}), fact phải tra khoá theo ngày mua. "
        "Chi phí thấp, đúng kỹ thuật SCD mà môn học muốn minh hoạ.",
        "3. SCD0 (không theo dõi đổi): bỏ vì mất thông tin hiện hành.", "",
        "**Khuyến nghị:** giữ **SCD2** (như DW_DESIGN §6.3). Số khách đổi zip rất ít, nên SCD2 chỉ làm dim lớn thêm "
        f"{pct(100 * r.changes / uniq, 2)} nhưng cho ví dụ SCD thật cùng dữ liệu thật để trình bày (cột `effective_from/to`, `is_current`). "
        "Lý do nên nói rõ trong báo cáo: địa lý lịch sử vẫn đúng nhờ `customer_geography_key` ở fact; SCD2 bảo đảm thuộc tính khách cũng đúng theo thời điểm.", ""]
    return lines, {"multi": multi, "uniq": uniq, "changes": int(r.changes), "versions": versions, "rep": rep}


def q_b() -> tuple[list[str], dict]:
    d = q(f"""
    WITH sales AS (SELECT i.seller_id, count(DISTINCT i.order_id) AS orders, sum(i.price) FILTER (WHERE {OK_ORDER}) AS gmv,
                          min(o.order_purchase_timestamp) AS first_sale
                   FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY 1)
    SELECT coalesce(m.origin, 'unknown') AS origin, d.seller_id, (sales.seller_id IS NOT NULL) AS has_orders,
           coalesce(sales.gmv, 0)::float AS gmv, coalesce(sales.orders, 0) AS orders
    FROM crm.closed_deals d JOIN crm.mql m USING (mql_id) LEFT JOIN sales ON sales.seller_id = d.seller_id""")
    d["channel"] = d.origin.map(CHANNEL_GROUP)
    tot = len(d)
    wo = d[d.has_orders]
    platform = float(scalar(f"SELECT sum(i.price) FROM oltp.order_items i JOIN oltp.orders o USING (order_id) WHERE {OK_ORDER}"))
    by = d.groupby("channel").agg(deals=("seller_id", "size"), with_orders=("has_orders", "sum"), gmv=("gmv", "sum")).sort_values("gmv", ascending=False)
    by["avg"] = by.gmv / by.with_orders.replace(0, np.nan)
    by["pct_orders"] = 100 * by.with_orders / by.deals
    won_after = int(scalar("SELECT count(*) FROM crm.closed_deals WHERE won_date > '2017-12-31 23:59:59'"))
    lines = [
        "## b) Bao nhiêu seller từ funnel có đơn hàng, và tổng GMV của họ? (độ sâu dashboard DB4)", "",
        "**Số liệu**", "",
        f"- {n(tot)} deal đã chốt trong CRM; **{n(len(wo))} seller ({pct(100 * len(wo) / tot)}) có đơn hàng** trong hệ thống bán hàng, "
        f"{n(tot - len(wo))} seller ({pct(100 * (tot - len(wo)) / tot)}) không có đơn nào (tất cả đều không có mặt trong `oltp.sellers`).",
        f"- Nhóm có đơn: {n(int(wo.orders.sum()))} đơn, **GMV {n(wo.gmv.sum(), 2)} BRL** = {pct(100 * wo.gmv.sum() / platform, 2)} GMV toàn sàn "
        f"({n(platform / 1e6, 2)} triệu BRL); trung bình {n(wo.gmv.sum() / len(wo), 0)} BRL / seller.",
        f"- {n(won_after)} / {n(tot)} deal có ngày chốt sau 2017-12-31, tức chỉ xuất hiện qua các đợt nạp tăng dần.", "",
        md_table(pd.DataFrame({"Nhóm kênh": by.index, "Deal": by.deals.map(lambda v: n(int(v))), "Có đơn": by.with_orders.map(lambda v: n(int(v))),
                               "% deal có đơn": by.pct_orders.map(lambda v: pct(v, 1)), "GMV (BRL)": by.gmv.map(lambda v: n(v, 0)),
                               "GMV TB / seller có đơn": by.avg.map(lambda v: n(v, 0))}), ["Deal", "Có đơn", "% deal có đơn", "GMV (BRL)", "GMV TB / seller có đơn"]), "",
        "**Phương án**", "",
        "1. **DB4 đầy đủ** (funnel + hiệu suất seller + GMV theo kênh): đủ dữ liệu cho phần funnel (8.000 MQL, 842 deal) nhưng phần hiệu suất / GMV chỉ dựa trên "
        f"{n(len(wo))} seller, và theo nhóm kênh có chỗ chỉ vài chục seller.",
        "2. **DB4 vừa phải**: trang 1 funnel MQL → chốt → có đơn đầu tiên theo kênh và tháng; trang 2 seller từ funnel (GMV, tỷ lệ trễ, điểm review, số ngày từ chốt đến đơn đầu) "
        "với cảnh báo cỡ mẫu.", "3. **DB4 chỉ funnel**: bỏ phần hiệu suất. Mất câu hỏi xuyên quy trình mà đề tài muốn trả lời.", "",
        f"**Khuyến nghị:** phương án 2. {pct(100 * len(wo) / tot)} deal liên kết được với đơn hàng là đủ để minh hoạ tích hợp hai nguồn "
        f"qua `dim_seller`, nhưng GMV của nhóm này chỉ {pct(100 * wo.gmv.sum() / platform, 2)} GMV toàn sàn nên không nên kết luận mạnh về hiệu suất theo kênh; "
        "nên gộp kênh theo `dim_lead_origin.channel_group` (5 nhóm) và luôn hiển thị số seller. "
        f"Phần {pct(100 * (tot - len(wo)) / tot)} deal không có đơn nên được thể hiện rõ như một kết quả (\"deal chốt nhưng chưa bán / không nằm trong sàn\"), không phải lỗi dữ liệu.", ""]
    return lines, {"with_orders": len(wo), "deals": tot, "gmv": float(wo.gmv.sum()), "gmv_share": 100 * wo.gmv.sum() / platform}


def q_c() -> tuple[list[str], dict]:
    r = q("""
    WITH s AS (SELECT i.seller_id, date_trunc('month', o.order_purchase_timestamp)::date AS m
               FROM oltp.order_items i JOIN oltp.orders o USING (order_id) GROUP BY 1, 2),
         first AS (SELECT seller_id, min(m) AS fm FROM s GROUP BY 1),
         bounds AS (SELECT max(m) AS lm FROM s)
    SELECT (SELECT count(*) FROM s) AS sparse_n,
           (SELECT sum(((extract(year FROM b.lm) - extract(year FROM f.fm)) * 12 + extract(month FROM b.lm) - extract(month FROM f.fm) + 1)::int) FROM first f, bounds b) AS dense_full,
           (SELECT sum(greatest(0, ((2018 - extract(year FROM f.fm)) * 12 + 8 - extract(month FROM f.fm) + 1))::int) FROM first f) AS dense_to_2018_08,
           (SELECT sum(greatest(0, ((2017 - extract(year FROM f.fm)) * 12 + 12 - extract(month FROM f.fm) + 1))::int) FROM first f) AS dense_to_2017_12,
           (SELECT count(*) FROM s WHERE m <= '2017-12-01') AS sparse_to_2017_12,
           (SELECT count(*) FROM s WHERE m <= '2018-08-01') AS sparse_to_2018_08,
           (SELECT count(*) FROM first) AS sellers,
           (SELECT to_char(lm, 'YYYY-MM') FROM bounds) AS last_month,
           (SELECT to_char(min(fm), 'YYYY-MM') FROM first) AS first_month""").iloc[0]
    sp, de = int(r.sparse_n), int(r.dense_full)
    lines = [
        "## c) `fact_seller_monthly` dày đặc hay thưa: bao nhiêu dòng?", "",
        "**Số liệu** (seller × tháng; “có đơn” = có ít nhất một dòng hàng trong tháng, mọi trạng thái đơn)", "",
        md_table(pd.DataFrame({"Phương án": ["Thưa (chỉ tháng có đơn)", "Dày đặc: từ tháng đơn đầu của seller đến tháng cuối của dữ liệu (đặc tả hiện tại)",
                                              "Dày đặc, cắt đến 2018-08 (giai đoạn dashboard)", "Dày đặc, chỉ đến 2017-12 (nạp ban đầu)"],
                               "Số dòng đầy đủ": [n(sp), n(de), n(int(r.dense_to_2018_08)), n(int(r.dense_to_2017_12))],
                               "Số dòng đến 2017-12 (olist_dw ban đầu)": [n(int(r.sparse_to_2017_12)), "–", "–", n(int(r.dense_to_2017_12))]}),
                 ["Số dòng đầy đủ", "Số dòng đến 2017-12 (olist_dw ban đầu)"]), "",
        f"- {n(int(r.sellers))} seller; tháng có đơn đầu tiên của kho dữ liệu {r.first_month}, tháng cuối {r.last_month}.",
        f"- Dày đặc lớn gấp {n(de / sp, 2)} lần thưa: {pct(100 * sp / de, 1)} số dòng dày đặc là tháng có đơn, phần còn lại ({n(de - sp)} dòng) là tháng seller không bán (`is_active = 0`).", "",
        "**Phương án**", "",
        f"1. **Thưa** ({n(sp)} dòng): gọn, nhưng không có dòng cho tháng không bán nên khó đo seller ngưng hoạt động, `months_since_first_sale` bị đứt quãng, "
        "và biểu đồ theo tháng cần tự điền 0.",
        f"2. **Dày đặc** ({n(de)} dòng): đúng định nghĩa periodic snapshot của Kimball (mỗi kỳ một dòng), đo được tỷ lệ seller còn hoạt động / rời đi; "
        f"tổng GMV vẫn khớp `fact_order_item`. Chi phí: {n(de - sp)} dòng thêm, vẫn rất nhỏ (dưới {n(de / 1000, 0)} nghìn dòng).", "",
        f"**Khuyến nghị:** **dày đặc** ({n(de)} dòng), như đặc tả; dashboard lọc giai đoạn 2017-01 → 2018-08. Dữ liệu nhỏ nên không có rủi ro hiệu năng, "
        "và dày đặc là lựa chọn mới trả lời được câu hỏi “seller nào ngưng bán”.", ""]
    return lines, {"sparse": sp, "dense": de}


def q_d() -> tuple[list[str], dict]:
    d = q(f"""
    SELECT coalesce(p.product_category_name, 'unknown') AS pt, t.product_category_name_english AS en,
           count(DISTINCT p.product_id) AS products,
           count(DISTINCT i.order_id) FILTER (WHERE {OK_ORDER}) AS orders,
           count(i.order_id) FILTER (WHERE {OK_ORDER}) AS items,
           coalesce(sum(i.price) FILTER (WHERE {OK_ORDER}), 0)::float AS gmv
    FROM oltp.products p
    LEFT JOIN oltp.product_category_name_translation t ON t.product_category_name = p.product_category_name
    LEFT JOIN oltp.order_items i ON i.product_id = p.product_id
    LEFT JOIN oltp.orders o ON o.order_id = i.order_id
    GROUP BY 1, 2 ORDER BY 5 DESC, 1""")
    unmapped = [c for c in d.pt if c not in CATEGORY_GROUP]
    assert not unmapped, f"categories without a group: {unmapped}"
    d["group"] = d.pt.map(CATEGORY_GROUP)
    d["en_show"] = d.en.fillna("(thiếu bản dịch)")
    d.loc[d.pt == "unknown", "en_show"] = "(danh mục rỗng → unknown)"
    gm = d.groupby("group").agg(categories=("pt", "size"), products=("products", "sum"), orders=("orders", "sum"), items=("items", "sum"), gmv=("gmv", "sum")).sort_values("gmv", ascending=False)
    total_gmv = d.gmv.sum()
    out = d.assign(share=100 * d.gmv / total_gmv)[["pt", "en_show", "group", "products", "orders", "items", "gmv", "share"]]
    (config.ROOT / "docs").mkdir(exist_ok=True)
    d[["pt", "group"]].rename(columns={"pt": "product_category_name", "group": "category_group"}).sort_values("product_category_name").to_csv(
        config.ROOT / "docs" / "category_group_draft.csv", index=False, encoding="utf-8")
    top_cat = d.sort_values("gmv", ascending=False)
    lines = [
        "## d) Toàn bộ danh mục sản phẩm kèm số đơn, và bảng nhóm ngành hàng đề xuất", "",
        f"**Số liệu**: {n(len(d) - 1)} danh mục có tên (+ nhóm `unknown` cho {n(int(d[d.pt == 'unknown'].products.iloc[0]))} sản phẩm rỗng danh mục) trong {n(int(d.products.sum()))} sản phẩm. "
        "Số đơn và GMV tính trên đơn không bị hủy/không khả dụng (đúng định nghĩa KPI); “số đơn” là số đơn khác nhau có ít nhất một dòng hàng của danh mục.",
        f"- {n(int((d.en.isna() & (d.pt != 'unknown')).sum()))} danh mục thiếu bản dịch tiếng Anh: "
        + ", ".join(f"`{p}`" for p in d[d.en.isna() & (d.pt != 'unknown')].pt) + " → bổ sung qua `seeds/category_translation_extra.csv`.",
        ("- Danh mục không có đơn hợp lệ nào: " + ", ".join(f"`{p}`" for p in d[d.orders == 0].pt) + "." if (d.orders == 0).any()
         else "- Mọi danh mục đều có ít nhất một đơn hợp lệ."),
        f"- Danh mục có GMV cao nhất: `{top_cat.pt.iloc[0]}` ({pct(100 * top_cat.gmv.iloc[0] / total_gmv, 1)} GMV).", "",
        "### Tổng hợp theo nhóm đề xuất (12 nhóm)", "",
        md_table(pd.DataFrame({"Nhóm ngành hàng": gm.index, "Số danh mục": gm.categories.map(lambda v: n(int(v))), "Số sản phẩm": gm.products.map(lambda v: n(int(v))),
                               "Số dòng hàng": gm["items"].map(lambda v: n(int(v))), "GMV (triệu BRL)": (gm.gmv / 1e6).map(lambda v: n(v, 2)),
                               "% GMV": (100 * gm.gmv / total_gmv).map(lambda v: pct(v, 1))}), ["Số danh mục", "Số sản phẩm", "Số dòng hàng", "GMV (triệu BRL)", "% GMV"]), "",
        "### Chi tiết từng danh mục (xếp theo số dòng hàng giảm dần)", "",
        md_table(pd.DataFrame({"Danh mục (pt)": out.pt, "Tiếng Anh": out.en_show, "Nhóm đề xuất": out.group, "Số sản phẩm": out.products.map(lambda v: n(int(v))),
                               "Số đơn": out.orders.map(lambda v: n(int(v))), "Số dòng hàng": out["items"].map(lambda v: n(int(v))),
                               "GMV (BRL)": out.gmv.map(lambda v: n(v, 0)), "% GMV": out.share.map(lambda v: pct(v, 1))}),
                 ["Số sản phẩm", "Số đơn", "Số dòng hàng", "GMV (BRL)", "% GMV"]), "",
        "**Phương án**", "",
        "1. Dùng 12 nhóm như bảng trên (đúng gợi ý ở DW_DESIGN §6.5, có sẵn nhóm `Unknown`).",
        "2. Tách riêng nhóm `Pet` (từ `pet_shop`) và `Art & Crafts` (từ `artes`, `artes_e_artesanato`) để `Gifts & Others` không quá hỗn tạp. "
        f"`Gifts & Others` hiện gồm {n(int(gm.loc['Gifts & Others', 'categories']))} danh mục, {pct(100 * gm.loc['Gifts & Others', 'gmv'] / total_gmv, 1)} GMV.",
        "3. Dùng thẳng danh mục gốc (73 giá trị) – không gom nhóm: quá nhiều cột cho slicer và biểu đồ.", "",
        "**Khuyến nghị:** phương án 1 để chốt bản đầu; các mục dễ gây tranh luận cần nhóm duyệt: `relogios_presentes` (đồng hồ & quà tặng, GMV lớn thứ hai), "
        "`cool_stuff`, `pet_shop`, `casa_construcao` (vào Auto & Tools hay Home), `eletroportateis` / `eletrodomesticos` (vào Home hay Electronics), "
        "`fashion_esporte` (Fashion hay Sports), `instrumentos_musicais`. File nháp: `docs/category_group_draft.csv` (cột `product_category_name`, `category_group`); "
        "sau 12/11 sửa file này rồi mới nạp seed ở P2.", ""]
    return lines, {"n_cat": len(d) - 1, "missing_tr": int((d.en.isna() & (d.pt != 'unknown')).sum()), "groups": len(gm)}


def q_e() -> tuple[list[str], dict]:
    r = q(f"""
    WITH geo AS (SELECT DISTINCT geolocation_zip_code_prefix AS zip FROM oltp.geolocation),
         geo_city AS (SELECT DISTINCT lower(unaccent(trim(geolocation_city))) AS city, geolocation_state AS st FROM oltp.geolocation),
         geo3 AS (SELECT DISTINCT left(geolocation_zip_code_prefix, 3) AS p3 FROM oltp.geolocation),
         cz AS (SELECT customer_zip_code_prefix AS zip, mode() WITHIN GROUP (ORDER BY customer_city) AS city, mode() WITHIN GROUP (ORDER BY customer_state) AS st,
                       count(*) AS rows_n FROM oltp.customers GROUP BY 1),
         sz AS (SELECT seller_zip_code_prefix AS zip, mode() WITHIN GROUP (ORDER BY seller_city) AS city, mode() WITHIN GROUP (ORDER BY seller_state) AS st,
                       count(*) AS rows_n FROM oltp.sellers GROUP BY 1)
    SELECT
      (SELECT count(*) FROM geo) AS geo_zips,
      (SELECT count(*) FROM cz) AS cust_zips, (SELECT count(*) FROM cz WHERE zip NOT IN (SELECT zip FROM geo)) AS cust_missing_zips,
      (SELECT coalesce(sum(rows_n), 0) FROM cz WHERE zip NOT IN (SELECT zip FROM geo)) AS cust_missing_rows,
      (SELECT count(*) FROM cz WHERE zip NOT IN (SELECT zip FROM geo) AND (lower(unaccent(trim(city))), st) IN (SELECT city, st FROM geo_city)) AS cust_city_ok,
      (SELECT count(*) FROM cz WHERE zip NOT IN (SELECT zip FROM geo) AND left(zip, 3) IN (SELECT p3 FROM geo3)) AS cust_p3_ok,
      (SELECT count(*) FROM sz) AS sell_zips, (SELECT count(*) FROM sz WHERE zip NOT IN (SELECT zip FROM geo)) AS sell_missing_zips,
      (SELECT coalesce(sum(rows_n), 0) FROM sz WHERE zip NOT IN (SELECT zip FROM geo)) AS sell_missing_rows,
      (SELECT count(*) FROM sz WHERE zip NOT IN (SELECT zip FROM geo) AND (lower(unaccent(trim(city))), st) IN (SELECT city, st FROM geo_city)) AS sell_city_ok,
      (SELECT count(*) FROM (SELECT zip FROM geo UNION SELECT zip FROM cz UNION SELECT zip FROM sz) u) AS union_zips,
      (SELECT count(*) FROM cz WHERE zip IN (SELECT zip FROM sz)) AS shared_zips""").iloc[0].astype(float)
    imp = q(f"""
    SELECT count(DISTINCT o.order_id) AS orders,
           coalesce(sum(i.price) FILTER (WHERE {OK_ORDER}), 0)::float AS gmv
    FROM oltp.orders o JOIN oltp.customers c USING (customer_id)
    LEFT JOIN oltp.order_items i ON i.order_id = o.order_id
    WHERE NOT EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = c.customer_zip_code_prefix)""").iloc[0]
    imp_s = q(f"""
    SELECT count(*) AS items, coalesce(sum(i.price) FILTER (WHERE {OK_ORDER}), 0)::float AS gmv
    FROM oltp.order_items i JOIN oltp.orders o USING (order_id) JOIN oltp.sellers s USING (seller_id)
    WHERE NOT EXISTS (SELECT 1 FROM oltp.geolocation g WHERE g.geolocation_zip_code_prefix = s.seller_zip_code_prefix)""").iloc[0]
    tot_orders = int(scalar("SELECT count(*) FROM oltp.orders"))
    n_cust, n_sell = int(scalar("SELECT count(*) FROM oltp.customers")), int(scalar("SELECT count(*) FROM oltp.sellers"))
    tot_items = int(scalar("SELECT count(*) FROM oltp.order_items"))
    tot_gmv = float(scalar(f"SELECT sum(i.price) FROM oltp.order_items i JOIN oltp.orders o USING (order_id) WHERE {OK_ORDER}"))
    extra = int(r.union_zips - r.geo_zips)
    lines = [
        "## e) Zip của customers / sellers không có trong geolocation", "",
        "**Số liệu**", "",
        md_table(pd.DataFrame({
            "Chỉ tiêu": ["Số zip khác nhau trong geolocation", "Zip khác nhau của customers", "  – trong đó KHÔNG có trong geolocation",
                         "Số khách (dòng customers) có zip thiếu", "Số đơn có khách ở zip thiếu", "GMV các đơn đó",
                         "Zip khác nhau của sellers", "  – trong đó KHÔNG có trong geolocation", "Số seller có zip thiếu",
                         "Dòng hàng của các seller đó", "GMV các dòng hàng đó",
                         "Tổng zip khác nhau nếu hợp nhất geolocation + customers + sellers (số dòng `dim_geography`)"],
            "Giá trị": [n(int(r.geo_zips)), n(int(r.cust_zips)), f"{n(int(r.cust_missing_zips))} ({pct(100 * r.cust_missing_zips / r.cust_zips, 2)})",
                        f"{n(int(r.cust_missing_rows))} ({pct(100 * r.cust_missing_rows / n_cust, 2)} khách)",
                        f"{n(int(imp.orders))} ({pct(100 * imp.orders / tot_orders, 2)} tổng đơn)", f"{n(imp.gmv, 0)} BRL ({pct(100 * imp.gmv / tot_gmv, 2)} GMV)",
                        n(int(r.sell_zips)), f"{n(int(r.sell_missing_zips))} ({pct(100 * r.sell_missing_zips / r.sell_zips, 2)})",
                        f"{n(int(r.sell_missing_rows))} ({pct(100 * r.sell_missing_rows / n_sell, 2)} seller)",
                        f"{n(int(imp_s['items']))} ({pct(100 * imp_s['items'] / tot_items, 2)} tổng dòng hàng)", f"{n(imp_s.gmv, 0)} BRL ({pct(100 * imp_s.gmv / tot_gmv, 2)} GMV)",
                        f"{n(int(r.union_zips))} (thêm {n(extra)} so với geolocation)"]}), []), "",
        f"- Có thể điền toạ độ gần đúng bằng **trung tâm thành phố** (median toạ độ của cùng thành phố + bang trong geolocation) cho "
        f"{n(int(r.cust_city_ok))} / {n(int(r.cust_missing_zips))} zip khách và {n(int(r.sell_city_ok))} / {n(int(r.sell_missing_zips))} zip seller thiếu.",
        f"- Có thể dùng **zip lân cận** (cùng 3 chữ số đầu) cho {n(int(r.cust_p3_ok))} / {n(int(r.cust_missing_zips))} zip khách thiếu.", "",
        "**Phương án**", "",
        "1. **Tạo dòng `dim_geography` từ city/state của customers / sellers, `latitude`/`longitude` = NULL** (đúng DW_DESIGN §6.2): trung thực, "
        "đơn giản; các phép tính khoảng cách seller → khách bỏ qua cặp thiếu toạ độ.",
        "2. Như 1 nhưng **điền toạ độ gần đúng theo trung tâm thành phố** và thêm cờ `is_approx_location`: bản đồ đầy đủ hơn, "
        "nhưng thêm cột mới vào đặc tả và pha tạp dữ liệu thật với dữ liệu suy ra.",
        "3. Loại các đơn/khách có zip thiếu: **không chấp nhận** (mất doanh thu, vi phạm nguyên tắc không bỏ dữ liệu).", "",
        f"**Khuyến nghị:** phương án 1. Chỉ {pct(100 * imp.orders / tot_orders, 2)} số đơn và {pct(100 * imp.gmv / tot_gmv, 2)} GMV bị ảnh hưởng; "
        "dim_geography vẫn đủ mọi zip (khoá ngoại luôn trỏ được), toạ độ NULL được ghi rõ trong tài liệu. Nếu nhóm cần bản đồ đầy đủ thì nâng lên phương án 2 sau, "
        "khi đó cập nhật DW_DESIGN trước.", ""]
    return lines, {"cust_missing": int(r.cust_missing_zips), "sell_missing": int(r.sell_missing_zips), "orders": int(imp.orders),
                   "gmv_share": 100 * imp.gmv / tot_gmv, "union": int(r.union_zips), "extra": extra}


def q_f() -> tuple[list[str], dict]:
    cuts = ["2017-06-30", "2017-12-31", "2018-03-31", "2018-05-31"]
    rows, keep = [], {}
    tot_o = int(scalar("SELECT count(*) FROM oltp.orders"))
    tot_m = int(scalar("SELECT count(*) FROM crm.mql"))
    tot_d = int(scalar("SELECT count(*) FROM crm.closed_deals"))
    for c in cuts:
        o = int(scalar("SELECT count(*) FROM oltp.orders WHERE order_purchase_timestamp < (CAST(:c AS date) + 1)", c=c))
        m = int(scalar("SELECT count(*) FROM crm.mql WHERE first_contact_date <= CAST(:c AS date)", c=c))
        d = int(scalar("SELECT count(*) FROM crm.closed_deals WHERE won_date < (CAST(:c AS date) + 1)", c=c))
        months = int(scalar("SELECT ((2018 - extract(year FROM CAST(:c AS date))) * 12 + 8 - extract(month FROM CAST(:c AS date)))::int", c=c))
        if c == "2017-12-31":
            keep = {"o": o, "m": m, "d": d, "months": months}
        rows.append({"Mốc tách": c, "Đơn nạp ban đầu": f"{n(o)} ({pct(100 * o / tot_o, 1)})", "MQL": f"{n(m)} ({pct(100 * m / tot_m, 1)})",
                     "Deal đã chốt": f"{n(d)} ({pct(100 * d / tot_d, 1)})", "Số đợt incremental hằng tháng đến 2018-08": n(months)})
    lines = [
        "## f) (Bổ sung) Mốc tách dữ liệu nạp ban đầu / incremental – đang chờ review ở nhật ký quyết định", "",
        "**Số liệu** (tỷ lệ so với toàn bộ nguồn: " + f"{n(tot_o)} đơn, {n(tot_m)} MQL, {n(tot_d)} deal)", "",
        md_table(pd.DataFrame(rows), ["Đơn nạp ban đầu", "MQL", "Deal đã chốt", "Số đợt incremental hằng tháng đến 2018-08"]), "",
        "**Phương án**", "",
        "1. **2017-12-31** (đặc tả hiện tại): ranh giới năm dễ giải thích, còn 8 đợt incremental hằng tháng (2018-01 → 2018-08) để minh hoạ cập nhật; "
        "nạp ban đầu chỉ có 3 deal nên funnel được “lấp đầy dần” qua các đợt.",
        "2. **Mốc muộn hơn** (2018-03-31 hoặc 2018-05-31): nạp ban đầu có nhiều deal hơn, nhưng còn ít đợt incremental để trình bày.",
        "3. **Mốc sớm hơn** (2017-06-30): nhiều đợt incremental hơn nhưng nạp ban đầu quá ít dữ liệu và không có deal nào.", "",
        "**Khuyến nghị:** giữ **2017-12-31**: đủ 8 đợt incremental và nạp ban đầu vẫn có hơn 45% số đơn; việc funnel gần như trống lúc đầu là điểm để kể chuyện, "
        "không phải lỗi (dashboard dựng trên trạng thái cuối).", ""]
    return lines, keep


def main() -> None:
    la, ra = q_a()
    lb, rb = q_b()
    lc, rc = q_c()
    ld, rd = q_d()
    le, re_ = q_e()
    lf, rf = q_f()
    summary = pd.DataFrame({
        "Câu": ["a", "b", "c", "d", "e"],
        "Câu hỏi": ["Khách có hơn 1 zip → SCD2 hay SCD1", "Seller từ funnel có đơn / GMV → độ sâu DB4", "`fact_seller_monthly` dày đặc hay thưa",
                    "Danh mục sản phẩm → bảng nhóm ngành hàng", "Zip thiếu trong geolocation → xây `dim_geography`"],
        "Số chính": [f"{n(ra['multi'])} / {n(ra['uniq'])} khách đổi zip ({pct(100 * ra['multi'] / ra['uniq'], 2)}); +{n(ra['changes'])} phiên bản",
                     f"{n(rb['with_orders'])} / {n(rb['deals'])} seller có đơn; GMV {n(rb['gmv'], 0)} BRL ({pct(rb['gmv_share'], 2)} GMV sàn)",
                     f"dày đặc {n(rc['dense'])} dòng, thưa {n(rc['sparse'])} dòng",
                     f"{n(rd['n_cat'])} danh mục → {n(rd['groups'])} nhóm; {n(rd['missing_tr'])} thiếu bản dịch",
                     f"{n(re_['cust_missing'])} zip khách + {n(re_['sell_missing'])} zip seller thiếu; {pct(100 * re_['orders'] / int(scalar('SELECT count(*) FROM oltp.orders')), 2)} đơn bị ảnh hưởng"],
        "Khuyến nghị": ["Giữ SCD2", "DB4 vừa phải (2 trang), gộp kênh, hiển thị cỡ mẫu", "Dày đặc", "12 nhóm đề xuất, nhóm duyệt các mục tranh luận", "Toạ độ NULL (phương án 1)"]})
    summary = pd.concat([summary, pd.DataFrame({"Câu": ["f"], "Câu hỏi": ["(Bổ sung) Mốc tách dữ liệu nạp ban đầu"], "Số chính": [f"2017-12-31: {n(rf['o'])} đơn, {n(rf['m'])} MQL, {n(rf['d'])} deal; còn {n(rf['months'])} đợt incremental"],
                                                  "Khuyến nghị": ["Giữ 2017-12-31"]})], ignore_index=True)
    lines = ["# Câu hỏi thiết kế cần chốt ngày 12/11 – trả lời bằng số (olist_full)", "", source_note("design_questions.py"), "",
             "Mỗi câu có số liệu, các phương án và khuyến nghị. GMV = tổng `price` của các đơn không bị hủy/không khả dụng (DW_DESIGN §9).", "",
             "## Tóm tắt", "", md_table(summary, []), "", *la, *lb, *lc, *ld, *le, *lf]
    write_md("design-questions.md", lines)


if __name__ == "__main__":
    main()
