"""Draw the dbt lineage (sources -> seeds -> dimensions -> facts -> marts) from dbt/target/manifest.json -> figures/5-1_dbt_lineage.png (+ copies for report and slides).

    python lakehouse/scripts/gen_lineage.py          (run `dbt docs generate` first)
This is a drawing made from the same manifest as the dbt docs site (`dbt docs serve`); the group may replace it with a screenshot of the site's lineage graph.
"""
from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parent.parent.parent
manifest = json.loads((ROOT / "lakehouse" / "dbt" / "target" / "manifest.json").read_text(encoding="utf-8"))
nodes = {**manifest["nodes"], **manifest["sources"]}
parents = manifest["parent_map"]
keep = {k: v for k, v in nodes.items() if v["resource_type"] in ("model", "seed", "source")}


def kind(k):
    v = keep[k]
    if v["resource_type"] == "source":
        return "silver"
    if v["resource_type"] == "seed":
        return "seed"
    n = v["name"]
    return "dim" if n.startswith("dim_") else "fact" if n.startswith("fact_") else "mart"


# layer = longest path from a source/seed
depth = {}


def d(k):
    if k in depth:
        return depth[k]
    ps = [p for p in parents.get(k, []) if p in keep]
    depth[k] = 0 if not ps else 1 + max(d(p) for p in ps)
    return depth[k]


for k in keep:
    d(k)
cols = defaultdict(list)
for k in keep:
    cols[depth[k]].append(k)
order = {"silver": 0, "seed": 1, "dim": 2, "fact": 3, "mart": 4}
for c in cols:
    cols[c].sort(key=lambda k: (order[kind(k)], keep[k]["name"]))
COLORS = {"silver": "#D9DDE3", "seed": "#FFF3C4", "dim": "#8ECAE6", "fact": "#F4A261", "mart": "#CDE8D6"}
nlayers = max(cols) + 1
maxh = max(len(v) for v in cols.values())
W, H = 3.0 * nlayers + 1, 0.42 * maxh + 1.6
fig, ax = plt.subplots(figsize=(W * 1.25, H * 1.25))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
pos = {}
for c, ks in cols.items():
    gap = (H - 1.4) / max(len(ks), 1)
    for i, k in enumerate(ks):
        x, y = 0.4 + c * 3.0, H - 0.9 - (i + 0.5) * gap
        pos[k] = (x, y)
for k, ps in parents.items():
    if k not in keep:
        continue
    for p in ps:
        if p in keep:
            (x1, y1), (x2, y2) = pos[p], pos[k]
            ax.annotate("", xy=(x2, y2), xytext=(x1 + 2.2, y1), arrowprops=dict(arrowstyle="-|>", color="#9CA3AF", lw=0.5, shrinkA=0, shrinkB=0), zorder=1)
for k, (x, y) in pos.items():
    label = keep[k]["name"] if kind(k) != "silver" else "silver." + keep[k]["name"]
    ax.add_patch(FancyBboxPatch((x, y - 0.15), 2.2, 0.3, boxstyle="round,pad=0.01,rounding_size=0.06", fc=COLORS[kind(k)], ec="#4B5563", lw=0.6, zorder=2))
    ax.text(x + 1.1, y, label, ha="center", va="center", fontsize=7, zorder=3)
ax.text(0.1, H - 0.3, "Lineage dbt: Silver (nguồn) và seed → dimension → fact → mart, đọc từ dbt/target/manifest.json "
        f"({sum(1 for k in keep if kind(k) == 'dim')} dimension, {sum(1 for k in keep if kind(k) == 'fact')} fact, {sum(1 for k in keep if kind(k) == 'mart')} mart)", fontsize=11, fontweight="bold")
for i, (n, c) in enumerate((("Silver", "silver"), ("seed", "seed"), ("dimension", "dim"), ("fact", "fact"), ("mart", "mart"))):
    ax.add_patch(FancyBboxPatch((0.1 + i * 1.6, 0.1), 1.4, 0.25, boxstyle="round,pad=0.01", fc=COLORS[c], ec="#4B5563", lw=0.6))
    ax.text(0.8 + i * 1.6, 0.225, n, ha="center", va="center", fontsize=7)
out = ROOT / "figures" / "5-1_dbt_lineage.png"
fig.savefig(out, dpi=170, bbox_inches="tight")
for sub in ("report/figures", "slides/figures"):
    if (ROOT / sub).exists():
        shutil.copy2(out, ROOT / sub / out.name)
print("written", out.relative_to(ROOT), f"({len(keep)} nodes)")
