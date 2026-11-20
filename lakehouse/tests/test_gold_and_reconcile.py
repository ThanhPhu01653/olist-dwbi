"""Gold checks: the 71 dbt tests and the reconciliation with the chapter 3 warehouse (16 tables). Slow (about 2 minutes), so run on request:

    python -m pytest lakehouse/tests -q --run-slow
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture(scope="module")
def run_slow(request):
    if not request.config.getoption("--run-slow"):
        pytest.skip("slow: add --run-slow")


def test_dbt_tests_pass(run_slow):
    env = {**os.environ, "DBT_PROFILES_DIR": "dbt"}
    r = subprocess.run(["dbt", "test", "--project-dir", "dbt"], cwd=ROOT / "lakehouse", capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stdout[-2000:]
    text = re.sub(r"\[[0-9;]*m", "", r.stdout)
    m = re.search(r"PASS=(\d+) WARN=(\d+) ERROR=(\d+) SKIP=(\d+) NO-OP=\d+ TOTAL=(\d+)", text)
    assert m, text[-1500:]
    assert m.group(1) == m.group(5) and m.group(3) == "0", m.group(0)   # every dbt test passes (71)


def test_reconcile_all_tables_match(run_slow):
    r = subprocess.run([sys.executable, str(ROOT / "lakehouse" / "scripts" / "reconcile.py")], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-2000:]
    assert "RESULT: all tables match" in r.stdout
