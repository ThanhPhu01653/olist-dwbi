"""Render the Mermaid blocks of a Markdown file to PNG through the public service mermaid.ink.

    python scripts/render_mermaid.py [huong-dan/05-nghiep-vu-nhap.md]
A block is rendered when the line just before the ```mermaid fence is  <!-- png: <file name>.png -->  ; the image goes to figures/.
The service sometimes answers 400/503 for a variant of the URL, so three URL forms are tried (plain base64, pako, plain base64 + width).
"""
from __future__ import annotations

import base64
import json
import re
import sys
import urllib.request
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=90).read()


def render(code: str) -> bytes | None:
    b64 = base64.urlsafe_b64encode(code.encode("utf-8")).decode()
    c = zlib.compressobj(9, zlib.DEFLATED, 15)
    pako = base64.urlsafe_b64encode(c.compress(json.dumps({"code": code, "mermaid": {"theme": "default"}}).encode()) + c.flush()).decode()
    for url in (f"https://mermaid.ink/img/{b64}?type=png&bgColor=!white", f"https://mermaid.ink/img/pako:{pako}?type=png&width=2200&bgColor=!white",
                f"https://mermaid.ink/img/{b64}?type=png&width=2200&bgColor=!white", f"https://mermaid.ink/img/{b64}?type=png"):
        try:
            data = fetch(url)
            if data[:4] == b"\x89PNG":
                return data
        except Exception:
            continue
    return None


def main() -> None:
    path = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "huong-dan/05-nghiep-vu-nhap.md")
    text = path.read_text(encoding="utf-8")
    ok = fail = 0
    for m in re.finditer(r"<!-- png: (\S+) -->\s*```mermaid\n(.*?)```", text, re.S):
        name, code = m.group(1), m.group(2)
        data = render(code)
        if data:
            (ROOT / "figures" / name).write_bytes(data)
            ok += 1
            print(f"  {name}: {len(data) // 1024} KB")
        else:
            fail += 1
            print(f"  {name}: FAILED (paste the block into https://mermaid.live)")
    print(f"rendered {ok}, failed {fail}")


if __name__ == "__main__":
    main()
