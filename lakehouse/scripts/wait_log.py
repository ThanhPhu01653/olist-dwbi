"""Bounded wait on a log file: print progress every --every seconds, stop at the first END pattern or after --timeout seconds (max 600).

    python lakehouse/scripts/wait_log.py LOGFILE --end "EXIT=|STREAM_END" --fail "Traceback|AnalysisException" [--timeout 600] [--every 60]
Exit code 0 = END pattern seen, 1 = FAIL pattern seen, 2 = timeout (the job is NOT stopped; the caller decides). Never waits without limit.
"""
import argparse
import re
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("--end", default=r"^EXIT=")
ap.add_argument("--fail", default=r"^Traceback|AnalysisException|Py4JJavaError")
ap.add_argument("--timeout", type=int, default=600)
ap.add_argument("--every", type=int, default=60)
ap.add_argument("--progress", default=r"^(BATCH|PROGRESS)")
a = ap.parse_args()
a.timeout = min(a.timeout, 600)
end, fail, prog = re.compile(a.end, re.M), re.compile(a.fail, re.M), re.compile(a.progress, re.M)
t0 = last = time.time()
seen = 0
while True:
    txt = Path(a.log).read_text(encoding="utf-8", errors="replace") if Path(a.log).exists() else ""
    f = fail.search(txt)
    if f:
        print(f"FAIL after {time.time() - t0:.0f}s: {txt[max(0, f.start() - 200): f.start() + 400]}")
        sys.exit(1)
    if end.search(txt):
        lines = [l for l in txt.splitlines() if prog.search(l)]
        print(f"END after {time.time() - t0:.0f}s; progress lines: {len(lines)}; last: {lines[-1][:300] if lines else '-'}")
        sys.exit(0)
    if time.time() - last >= a.every:
        lines = [l for l in txt.splitlines() if prog.search(l)]
        print(f"[{time.time() - t0:4.0f}s] progress lines: {len(lines)}; last: {lines[-1][:300] if lines else '(no batch yet)'}", flush=True)
        last = time.time()
    if time.time() - t0 >= a.timeout:
        print(f"TIMEOUT after {a.timeout}s (job still running; log has {len(txt.splitlines())} lines)")
        sys.exit(2)
    time.sleep(5)
