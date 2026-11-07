"""Check every relative link / image in the repository's .md files points to an existing file or folder.

    python scripts/check_md_links.py            # prints broken links, exit code 1 if any
Also checks paths written in `inline code` that start with a repo folder (figures/, docs/, handoff/ ...) and end in a known extension.
Skips web links (http, https, mailto), pure anchors (#...), fenced code blocks and folders such as data/ and .venv/.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "data", "node_modules", "__pycache__", "hust-theme"}
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE = re.compile(r"^\s*(```|~~~)")


def md_files():
    for p in sorted(ROOT.rglob("*.md")):
        if not SKIP_DIRS.intersection(p.relative_to(ROOT).parts):
            yield p


def broken_links() -> list[tuple[Path, int, str]]:
    bad = []
    for path in md_files():
        in_code = False
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                in_code = not in_code
                continue
            if in_code:
                continue
            for m in LINK.finditer(line):
                target = m.group(1)
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                rel = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if rel and not (path.parent / rel).exists():
                    bad.append((path, no, target))
    return bad


CODE_PATH = re.compile(r"`([^`\s]+)`")
TOP_DIRS = {"figures", "docs", "handoff", "huong-dan", "powerbi", "report", "slides", "exports", "sql", "etl", "scripts", "seeds"}
EXTS = {".md", ".png", ".csv", ".sql", ".py", ".tex", ".mmd", ".drawio", ".json", ".xlsx", ".bib"}


def broken_code_paths() -> list[tuple[Path, int, str]]:
    bad = []
    for path in md_files():
        in_code = False
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FENCE.match(line):
                in_code = not in_code
                continue
            if in_code:
                continue
            for m in CODE_PATH.finditer(line):
                t = m.group(1).rstrip(".,;:)")
                if any(ch in t for ch in "*<>{}$|()[]"):
                    continue
                if t.split("/")[0] in TOP_DIRS and Path(t).suffix in EXTS and not (ROOT / t).exists():
                    bad.append((path, no, t))
    return bad


def main() -> None:
    files = list(md_files())
    bad = broken_links()
    for path, no, target in bad:
        print(f"{path.relative_to(ROOT)}:{no}: broken link -> {target}")
    code_bad = broken_code_paths()
    for path, no, target in code_bad:
        print(f"{path.relative_to(ROOT)}:{no}: missing file named in code span -> {target}")
    print(f"{len(files)} .md files checked, {len(bad)} broken relative links, {len(code_bad)} missing paths in code spans")
    bad = bad + code_bad
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
