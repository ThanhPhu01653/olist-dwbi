def pytest_addoption(parser):
    parser.addoption("--run-slow", action="store_true", default=False, help="also run dbt test and reconcile.py (about 2 minutes)")
