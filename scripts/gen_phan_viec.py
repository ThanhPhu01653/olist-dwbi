"""P8d: fill the generated parts of huong-dan/phan-viec/*.md from the real slide and report sources.

    python scripts/gen_phan_viec.py

Markers in each .md file (replaced in place; the rest of the file is hand-written):
  <!-- SLIDES:file1.tex,file2.tex -->  ...  <!-- /SLIDES -->     table of the existing frames of those slide files
  <!-- TODOS:chapter1.tex,chapter2.tex -->  ...  <!-- /TODOS --> count and list of \\todo in those report chapters (with page ranges from report/main.toc if present)
Nothing is typed by hand: titles, figures, tables, [Sxx] numbers and \\todo texts are read from slides/sections/*.tex and report/chapters/*.tex.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SL = ROOT / "slides" / "sections"
CH = ROOT / "report" / "chapters"
OUT = ROOT / "huong-dan" / "phan-viec"

# selected for the spoken presentation (marked "T"); everything else is a detail slide for questions / the report
PRESENT: dict[str, set[int]] = {}


def clean(s: str) -> str:
    s = s.replace("\\symbol{95}", "_").replace("\\_", "_").replace("\\%", "%").replace("\\&", "&").replace("$\\rightarrow$", "→").replace("\\rightarrow", "→")
    s = s.replace("\\#", "#").replace("--", "–").replace("~", " ").replace("\\ldots", "…")
    s = re.sub(r"\\(?:textbf|emph|texttt|code|textit|scriptsize|small)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?", "", s)
    s = s.replace("{", "").replace("}", "").replace("$", "")
    return re.sub(r"\s+", " ", s).strip()


def frames(tex: str) -> list[dict]:
    out = []
    sub = ""
    for blk in re.split(r"(?=\\subsection\{|\\begin\{frame\})", tex):
        m = re.match(r"\\subsection\{([^}]*)\}", blk)
        if m:
            sub = m.group(1)
            continue
        if not blk.startswith("\\begin{frame}"):
            continue
        t = re.match(r"\\begin\{frame\}(?:\[[^\]]*\])?\{(.*?)\}\n", blk, flags=re.S)
        title = clean(t.group(1)) if t else "?"
        n = re.search(r"\\note\{\[S(\d+)\]", blk)
        figs = re.findall(r"\\anh(?:\[[^\]]*\])?\{([^}]+)\}", blk) + re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", blk)
        items = [clean(x) for x in re.findall(r"\\item (.*)", blk)]
        has_table = "\\begin{tabular" in blk
        ph = re.search(r"\\khungchen(?:\[[^\]]*\])?\{([^}]*)\}", blk)
        out.append(dict(sub=sub, title=title, s=int(n.group(1)) if n else None, figs=figs, items=items, table=has_table, placeholder=clean(ph.group(1)) if ph else "",
                        confirm="canxacnhan" in blk))
    return out


def md(s: str) -> str:
    return s.replace("|", "\\|")


def slides_table(files: list[str]) -> str:
    rows = ["| STT | S | Tiêu đề (câu kết luận) | Nội dung chính | Hình / bảng | Trạng thái |", "| ---: | ---: | --- | --- | --- | --- |"]
    n = 0
    for f in files:
        for fr in frames((SL / f).read_text(encoding="utf-8")):
            n += 1
            content = "; ".join(fr["items"][:2])[:150] or ("bảng" if fr["table"] else "")
            vis = ", ".join(f"`{x}`" for x in fr["figs"]) or ("bảng" if fr["table"] else "–")
            if fr["placeholder"]:
                status = "cần ảnh: " + fr["placeholder"][:60]
                vis = "khung chờ"
            elif fr["confirm"]:
                status = "đã có, nhóm xác nhận"
            elif any("BẢN NHÁP" in x for x in [fr["title"]]):
                status = "đã có"
            else:
                status = "đã có"
            rows.append(f"| {n} | {fr['s'] if fr['s'] else '–'} | {md(fr['title'])} | {md(content)} | {md(vis)} | {md(status)} |")
    rows.append("")
    rows.append(f"*{n} frame trong {', '.join('`'+f+'`' for f in files)} (đếm từ mã `.tex`; cột S là số `[Sxx]` trong ghi chú người nói và trong `slides/slide-script.md`).*")
    return "\n".join(rows)


def toc_pages() -> dict[str, tuple[int, int]]:
    """Page range of each numbered chapter / section from report/main.toc (a section that shares its last page with the next one counts that page)."""
    toc = ROOT / "report" / "main.toc"
    if not toc.exists():
        return {}
    ent = []  # (kind, number or None, page)
    for line in toc.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"\\contentsline \{(chapter|section)\}\{(?:\\numberline \{([^}]*)\})?(.*?)\}\{(\w+)\}\{", line)
        if m and m.group(4).isdigit():
            ent.append((m.group(1), m.group(2), int(m.group(4))))
    out = {}
    for i, (kind, num, p) in enumerate(ent):
        if not num:
            continue
        if kind == "chapter":
            nxt = next((q for k, _, q in ent[i + 1:] if k == "chapter"), p)
        else:
            nxt = ent[i + 1][2] if i + 1 < len(ent) else p
        out[num] = (p, max(p, nxt - 1 if nxt > p else p))
    return out


def todos_table(files: list[str]) -> str:
    rows = ["| File | Số `\\todo` | Nội dung các `\\todo` |", "| --- | ---: | --- |"]
    total = 0
    for f in files:
        t = (CH / f).read_text(encoding="utf-8")
        todos = []
        for m in re.finditer(r"\\todo(?:\[[^\]]*\])?\{", t):
            i, depth = m.end(), 1
            while depth and i < len(t):
                depth += (t[i] == "{") - (t[i] == "}")
                i += 1
            todos.append(clean(t[m.end():i - 1]))
        total += len(todos)
        rows.append(f"| `report/chapters/{f}` | {len(todos)} | " + ("<br>".join(f"{k + 1}. {md(x[:210])}{'…' if len(x) > 210 else ''}" for k, x in enumerate(todos)) or "–") + " |")
    rows.append(f"| **Tổng** | **{total}** | |")
    return "\n".join(rows)


def pages_line(nums: list[str]) -> str:
    tp = toc_pages()
    parts = []
    tot = 0
    for n in nums:
        if n in tp:
            a, b = tp[n]
            rng = f"trang {a}" if a == b else f"trang {a}–{b}"
            parts.append(f"{'chương' if '.' not in n else 'mục'} {n}: {rng} ({b - a + 1} trang)")
            tot += b - a + 1
    return "; ".join(parts) + (f"; tổng {tot} trang" if len(parts) > 1 else "") if parts else "(chưa có main.toc: biên dịch báo cáo để lấy số trang)"


def qa_block(nums: list[int]) -> str:
    t = (ROOT / "huong-dan" / "04-cau-hoi-van-dap.md").read_text(encoding="utf-8")
    out = []
    for n in nums:
        m = re.search(rf"^\*\*{n}\. (.*?)\*\*\n(.*?)(?=^\*\*\d+\. |^## |\Z)", t, flags=re.S | re.M)
        if m:
            ans = re.sub(r"\n{2,}", "\n\n", m.group(2).strip())
            out.append(f"**Q{n}. {m.group(1)}**\n{ans}")
    return "\n\n".join(out)


def fill(path: Path) -> None:
    t = path.read_text(encoding="utf-8")

    def sl(m):
        return f"<!-- SLIDES:{m.group(1)} -->\n{slides_table(m.group(1).split(','))}\n<!-- /SLIDES -->"

    def td(m):
        return f"<!-- TODOS:{m.group(1)} -->\n{todos_table(m.group(1).split(','))}\n<!-- /TODOS -->"

    def pg(m):
        return f"<!-- PAGES:{m.group(1)} -->{pages_line(m.group(1).split(','))}<!-- /PAGES -->"

    def qa(m):
        return f"<!-- QA:{m.group(1)} -->\n{qa_block([int(x) for x in m.group(1).split(',')])}\n<!-- /QA -->"

    t = re.sub(r"<!-- PAGES:([^>]*?) -->.*?<!-- /PAGES -->", pg, t, flags=re.S)
    t = re.sub(r"<!-- QA:([^>]*?) -->.*?<!-- /QA -->", qa, t, flags=re.S)
    t = re.sub(r"<!-- SLIDES:([^>]*?) -->.*?<!-- /SLIDES -->", sl, t, flags=re.S)
    t = re.sub(r"<!-- TODOS:([^>]*?) -->.*?<!-- /TODOS -->", td, t, flags=re.S)
    path.write_text(t, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for p in sorted(OUT.glob("*.md")):
        fill(p)
        print("filled", p.name)
