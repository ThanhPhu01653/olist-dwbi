"""Distance seller -> customer (haversine, no PostGIS) vs freight and lead time.

    python scripts/geo_analysis.py
Reads mart_fulfillment.v_shipping_distance; writes handoff/geo-distance.md, figures/3-5-2_distance_vs_freight.png and
figures/3-5-2_distance_vs_leadtime.png. Items of orders in status group 'Failed' are left out; lead time uses delivered orders only.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from etl import config
from etl.db import get_engine

BLUE, ORANGE, RED, GREY = "#1F6FB2", "#F28E2B", "#D64545", "#8A94A6"
BANDS = ["0-100 km", "100-500 km", "500-1000 km", "Trên 1000 km"]


def main() -> None:
    eng = get_engine(config.DB_NAME)
    df = pd.read_sql_query("SELECT * FROM mart_fulfillment.v_shipping_distance", eng)
    total, missing = len(df), int((~df["has_distance"]).sum())
    miss_orders = df.loc[~df["has_distance"], "order_id"].nunique()
    failed = int((df["status_group"] == "Failed").sum())
    d = df[df["has_distance"] & (df["status_group"] != "Failed")].copy()
    d["distance_km"] = d["distance_km"].astype(float)
    for c in ("freight_value", "price", "freight_ratio", "lead_days", "delay_days"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    dl = d[d["is_delivered"] == 1]
    g = d.groupby("distance_band").agg(items=("order_id", "size"), avg_distance=("distance_km", "mean"), avg_freight=("freight_value", "mean"),
                                       median_freight=("freight_value", "median"), avg_price=("price", "mean"), avg_ratio=("freight_ratio", "mean")).reindex(BANDS)
    gl = dl.groupby("distance_band").agg(delivered_items=("order_id", "size"), avg_lead=("lead_days", "mean"), median_lead=("lead_days", "median"),
                                         late_rate=("is_late", "mean")).reindex(BANDS)
    g["share_pct"] = 100 * g["items"] / g["items"].sum()
    corr = {
        ("distance_km", "freight_value"): (d["distance_km"].corr(d["freight_value"]), d["distance_km"].corr(d["freight_value"], method="spearman"), len(d)),
        ("distance_km", "freight_ratio"): (d["distance_km"].corr(d["freight_ratio"]), d["distance_km"].corr(d["freight_ratio"], method="spearman"), int(d["freight_ratio"].notna().sum())),
        ("distance_km", "lead_days"): (dl["distance_km"].corr(dl["lead_days"]), dl["distance_km"].corr(dl["lead_days"], method="spearman"), int(dl["lead_days"].notna().sum())),
    }
    same_state = float((d["seller_state"] == d["customer_state"]).mean() * 100)

    # figure 1: distance vs freight
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), dpi=200)
    s = d[d["freight_value"] <= 120].sample(min(60000, len(d)), random_state=1)
    hb = ax[0].hexbin(s["distance_km"], s["freight_value"], gridsize=45, cmap="Blues", mincnt=1, bins="log")
    ax[0].set(xlabel="Khoảng cách seller → khách (km)", ylabel="Phí vận chuyển của dòng hàng (BRL)", title="Phí vận chuyển tăng theo khoảng cách")
    fig.colorbar(hb, ax=ax[0], label="số dòng hàng (log)")
    x = range(len(BANDS))
    ax[1].bar(x, g["avg_freight"], color=BLUE, width=0.55)
    for i, v in enumerate(g["avg_freight"]):
        ax[1].text(i, v + 0.4, f"{v:.1f}", ha="center", fontsize=9)
    ax[1].set_xticks(list(x), [f"{b}\n(n={int(n):,})" for b, n in zip(BANDS, g["items"])], fontsize=8)
    ax[1].set(ylabel="Phí vận chuyển TB (BRL)", title="Phí vận chuyển trung bình theo nhóm khoảng cách")
    ax2 = ax[1].twinx()
    ax2.plot(list(x), 100 * g["avg_ratio"], color=ORANGE, marker="o")
    ax2.set_ylabel("Freight / giá hàng (%)", color=ORANGE)
    for a in (ax[0], ax[1]):
        a.spines[["top"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(config.ROOT / "figures" / "3-5-2_distance_vs_freight.png")
    plt.close(fig)

    # figure 2: distance vs lead time
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), dpi=200)
    ax[0].bar(list(x), gl["avg_lead"], color=BLUE, width=0.55)
    for i, v in enumerate(gl["avg_lead"]):
        ax[0].text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=9)
    ax[0].set_xticks(list(x), [f"{b}\n(n={int(n):,})" for b, n in zip(BANDS, gl["delivered_items"])], fontsize=8)
    ax[0].set(ylabel="Lead time TB (ngày, từ mua đến giao)", title="Khoảng cách xa hơn thì giao lâu hơn")
    ax[1].bar(list(x), 100 * gl["late_rate"], color=RED, width=0.55)
    for i, v in enumerate(100 * gl["late_rate"]):
        ax[1].text(i, v + 0.15, f"{v:.1f}%", ha="center", fontsize=9)
    ax[1].set_xticks(list(x), BANDS, fontsize=8)
    ax[1].set(ylabel="Tỷ lệ giao trễ (%)", title="Tỷ lệ giao trễ theo nhóm khoảng cách")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(config.ROOT / "figures" / "3-5-2_distance_vs_leadtime.png")
    plt.close(fig)

    out = ["# Khoảng cách seller → khách (haversine) và quan hệ với phí vận chuyển, lead time – sinh tự động", "",
           f"Nguồn: `mart_fulfillment.v_shipping_distance` (khoảng cách tính bằng `dw.haversine_km` trên toạ độ median của zip, không dùng PostGIS).", "",
           f"- Tổng dòng hàng: **{total:,}**. Bị bỏ khỏi phân tích vì **thiếu toạ độ** (zip của seller hoặc của khách không có toạ độ hợp lệ): **{missing:,}** dòng ({100 * missing / total:.2f}%), thuộc {miss_orders:,} đơn.",
           f"- Loại thêm {failed:,} dòng của đơn thuộc nhóm Failed; còn **{len(d):,}** dòng hàng được phân tích ({len(dl):,} dòng của đơn đã giao dùng cho lead time).",
           f"- Khoảng cách trung bình {d['distance_km'].mean():.0f} km, trung vị {d['distance_km'].median():.0f} km; **{same_state:.1f}%** dòng hàng có seller và khách cùng bang.", "",
           "## Theo nhóm khoảng cách", "",
           "| Nhóm | Dòng hàng | Tỷ trọng | Freight TB (BRL) | Freight trung vị | Giá hàng TB | Freight / giá (TB) | Dòng đã giao | Lead time TB (ngày) | Lead trung vị | Tỷ lệ trễ |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for b in BANDS:
        r, l = g.loc[b], gl.loc[b]
        out.append(f"| {b} | {int(r['items']):,} | {r['share_pct']:.1f}% | {r['avg_freight']:.2f} | {r['median_freight']:.2f} | {r['avg_price']:.2f} | {100 * r['avg_ratio']:.1f}% | "
                   f"{int(l['delivered_items']):,} | {l['avg_lead']:.1f} | {l['median_lead']:.1f} | {100 * l['late_rate']:.1f}% |")
    out += ["", "## Tương quan", "", "| Cặp biến | Pearson | Spearman | Số dòng |", "| --- | ---: | ---: | ---: |"]
    for (a, b), (p, sp, n) in corr.items():
        out.append(f"| {a} ~ {b} | {p:.3f} | {sp:.3f} | {n:,} |")
    out += ["", "Pearson đo quan hệ tuyến tính, Spearman đo quan hệ đơn điệu (ít bị ảnh hưởng bởi giá trị lớn bất thường). Tương quan không chứng minh nhân quả: khoảng cách đi kèm vùng, loại hàng và cân nặng.", ""]
    (config.ROOT / "handoff" / "geo-distance.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out[:12]))
    print(g.round(2).to_string()); print(gl.round(3).to_string())
    print({k: tuple(round(x, 3) for x in v[:2]) for k, v in corr.items()})


if __name__ == "__main__":
    main()
