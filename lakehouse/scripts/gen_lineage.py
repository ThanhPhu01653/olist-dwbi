"""Draw the dbt lineage as four columns Silver | Dimension | Fact | Mart from dbt/target/manifest.json -> figures/5-1_dbt_lineage.png (+ copies for report and slides).

    python lakehouse/scripts/gen_lineage.py          (run `dbt docs generate` first)
Seeds and tests are left out; the prefix of each layer is dropped from the labels (the column header names the layer) so that the text stays at 14 pt
on a figure of 11.3 x 5.9 inches, which the slides scale to about 52% (about 7 pt on the slide). The same manifest feeds the dbt docs site (`dbt docs serve`).
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, PathPatch
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent.parent.parent
manifest = json.loads((ROOT / "lakehouse" / "dbt" / "target" / "manifest.json").read_text(encoding="utf-8"))
allnodes = {**manifest["nodes"], **manifest["sources"]}
parents = manifest["parent_map"]


def layer(k):
    v = allnodes.get(k)
    if v is None:
        return None
    if v["resource_type"] == "source":
        return "silver"
    if v["resource_type"] != "model":
        return None          # seeds, tests
    n = v["name"]
    return "dim" if n.startswith("dim_") else "fact" if n.startswith("fact_") else "mart" if n.startswith("mart_") else None


keep = {k: layer(k) for k in allnodes if layer(k)}
edges = [(p, k) for k in keep for p in parents.get(k, []) if p in keep]
# silver sources that nothing reads are not drawn
used = {p for p, _ in edges} | {k for _, k in edges}
keep = {k: v for k, v in keep.items() if k in used or v != "silver"}
name = {k: allnodes[k]["name"] for k in keep}
PREFIX = {"silver": "", "dim": "dim_", "fact": "fact_", "mart": "mart_"}
label = {k: name[k][len(PREFIX[keep[k]]):] if name[k].startswith(PREFIX[keep[k]]) else name[k] for k in keep}

cols = {c: sorted([k for k in keep if keep[k] == c], key=lambda k: name[k]) for c in ("silver", "dim", "fact", "mart")}
idx = {}


def place(c):
    n = len(cols[c])
    for i, k in enumerate(cols[c]):
        idx[k] = i / max(n - 1, 1) * (len(cols["silver"]) - 1)


place("dim")
for _ in range(3):                                      # order each column by the mean position of its neighbours to cut crossings
    for c, nbrs in (("fact", lambda k: [a for a, b in edges if b == k]), ("mart", lambda k: [a for a, b in edges if b == k]),
                    ("silver", lambda k: [b for a, b in edges if a == k])):
        def key(k, nbrs=nbrs):
            nb = [x for x in nbrs(k) if x in idx]
            return sum(idx[x] for x in nb) / len(nb) if nb else 1e9
        cols[c].sort(key=lambda k: (key(k), name[k]))
        place(c)

FONT = 14
COLORS = {"silver": "#C9D1D9", "dim": "#8ECAE6", "fact": "#F4A261", "mart": "#B7E4C7"}
X = {"silver": 0.0, "dim": 3.6, "fact": 6.1, "mart": 8.75}
BW = {"silver": 3.1, "dim": 1.85, "fact": 2.25, "mart": 2.95}
nrows = len(cols["silver"])
RH = 0.3
HDR = 0.45
W, H = 11.7, HDR + nrows * RH + 0.1
fig, ax = plt.subplots(figsize=(W, H))
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")
pos = {}
for c, ks in cols.items():
    span = nrows * RH
    for i, k in enumerate(ks):
        y = H - HDR - (i + 0.5) * span / len(ks)
        pos[k] = (X[c], y)
for p, k in edges:
    (x1, y1), (x2, y2) = pos[p], pos[k]
    xa, xb = x1 + BW[keep[p]], x2
    mid = (xa + xb) / 2
    path = MPath([(xa, y1), (mid, y1), (mid, y2), (xb, y2)], [MPath.MOVETO, MPath.CURVE4, MPath.CURVE4, MPath.CURVE4])
    ax.add_patch(PathPatch(path, fc="none", ec="#6B7280", lw=0.7, alpha=0.45, zorder=1))
for k, (x, y) in pos.items():
    c = keep[k]
    ax.add_patch(FancyBboxPatch((x, y - 0.115), BW[c], 0.23, boxstyle="round,pad=0.005,rounding_size=0.05", fc=COLORS[c], ec="#374151", lw=0.7, zorder=2))
    ax.text(x + BW[c] / 2, y - 0.005, label[k], ha="center", va="center", fontsize=FONT, color="#111827", zorder=3)
for c, t in (("silver", "Silver"), ("dim", "Dimension"), ("fact", "Fact"), ("mart", "Mart")):
    ax.text(X[c] + BW[c] / 2, H - 0.2, t, ha="center", va="center", fontsize=FONT, fontweight="bold")
out = ROOT / "figures" / "5-1_dbt_lineage.png"
fig.savefig(out, dpi=220, bbox_inches="tight", facecolor="white")
for sub in ("report/figures", "slides/figures"):
    if (ROOT / sub).exists():
        shutil.copy2(out, ROOT / sub / out.name)
print("written", out.relative_to(ROOT), {c: len(v) for c, v in cols.items()}, f"{len(edges)} edges")
