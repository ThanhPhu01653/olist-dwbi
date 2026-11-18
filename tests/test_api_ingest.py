"""pytest for api_ingest.   python -m pytest tests -q        (the tests marked db need PostgreSQL and the landing zone data/raw/api)

No test calls the real APIs: a fake session returns canned responses, so the suite is fast and works offline.
"""
from __future__ import annotations

import json
from datetime import date

import pytest

from api_ingest import config
from api_ingest.collect import Collector, SourceError
from api_ingest.http import Client
from api_ingest.match import fuzzy_pick
from api_ingest import stage


# ----------------------------------------------------------------------------- fakes
class FakeResponse:
    def __init__(self, status: int, body: bytes = b"[]"):
        self.status_code, self.content = status, body


class FakeSession:
    """Returns the queued responses (or raises) in order; the last one repeats."""

    def __init__(self, queue):
        self.queue, self.calls, self.headers = list(queue), [], {}

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))
        item = self.queue.pop(0) if len(self.queue) > 1 else self.queue[0]
        if isinstance(item, Exception):
            raise item
        return item


def client(queue):
    sleeps = []
    c = Client(FakeSession(queue), sleep=sleeps.append, clock=lambda: 0.0)
    return c, sleeps


# ----------------------------------------------------------------------------- HTTP client
def test_retries_with_backoff_then_succeeds():
    import requests
    c, sleeps = client([FakeResponse(503), requests.ConnectionError("boom"), FakeResponse(200, b'{"a": 1}')])
    r = c.get("https://api.bcb.gov.br/x")
    assert r.ok and r.attempts == 3
    assert [s for s in sleeps if s >= config.BACKOFF_SECONDS] == [config.BACKOFF_SECONDS, config.BACKOFF_SECONDS * 2]   # exponential back-off


def test_gives_up_after_max_attempts_and_reports_the_error():
    c, _ = client([FakeResponse(500)])
    r = c.get("https://brasilapi.com.br/api/feriados/v1/2017")
    assert not r.ok and r.attempts == config.MAX_ATTEMPTS and r.error == "HTTP 500"


def test_client_error_is_not_retried():
    c, _ = client([FakeResponse(404)])
    r = c.get("https://brasilapi.com.br/api/feriados/v1/2017")
    assert not r.ok and r.attempts == 1 and r.error == "HTTP 404"


def test_rate_limit_waits_between_calls_to_the_same_host():
    clock = {"t": 0.0}
    sleeps = []
    c = Client(FakeSession([FakeResponse(200)]), sleep=lambda s: (sleeps.append(s), clock.__setitem__("t", clock["t"] + s)), clock=lambda: clock["t"])
    c.get("https://api.bcb.gov.br/a")
    c.get("https://api.bcb.gov.br/b")
    assert sleeps and sleeps[0] == pytest.approx(config.MIN_INTERVAL["api.bcb.gov.br"])


def test_user_agent_is_generic_not_a_personal_address():
    assert "@" not in config.USER_AGENT and "olist" in config.USER_AGENT


# ----------------------------------------------------------------------------- collector (landing zone, idempotency, failure isolation)
def collector(tmp_path, queue):
    c, _ = client(queue)
    return Collector(None, None, c, run_date="2026-11-18", landing_root=tmp_path)


def test_rerun_does_not_duplicate_landing_files_or_manifest_entries(tmp_path):
    body = json.dumps([{"date": "2017-01-01", "name": "Confraternização mundial", "type": "national"}]).encode()
    col = collector(tmp_path, [FakeResponse(200, body)])
    for _ in range(2):
        col.call("holidays", "feriados_2017", "https://brasilapi.com.br/api/feriados/v1/2017")
    folder = tmp_path / "holidays" / "2026-11-18"
    assert sorted(p.name for p in folder.iterdir()) == ["feriados_2017.json", "manifest.json"]
    assert (folder / "feriados_2017.json").read_bytes() == body                      # the response, byte for byte
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == 1 and manifest[0]["records"] == 1 and manifest[0]["http_status"] == 200 and len(manifest[0]["sha256"]) == 64


def test_a_failing_source_does_not_stop_the_others(tmp_path):
    col = collector(tmp_path, [FakeResponse(500)])
    col.collect_bcb = lambda: None                                                      # this source works
    outcome = col.collect(["holidays", "bcb"])
    assert outcome["holidays"] and "500" in outcome["holidays"] and outcome["bcb"] is None
    assert not list((tmp_path / "holidays").glob("**/*.json")) or all(p.name == "manifest.json" for p in (tmp_path / "holidays").glob("**/*.json"))


def test_bcb_asks_only_for_dates_after_the_watermark(tmp_path):
    col = collector(tmp_path, [FakeResponse(200, json.dumps([{"data": "04/01/2021", "valor": "5.1"}]).encode())])
    col.watermark = lambda key: date(2020, 12, 15)
    saved = {}
    col.set_watermark = lambda key, d: saved.__setitem__(key, d)
    col.collect_bcb()
    first = col.client.session.calls[0]
    assert first[1]["dataInicial"] == "16/12/2020"                                      # day after the watermark
    assert saved["api.bcb_sgs_1"] == date(2021, 1, 4)


def test_ibge_variable_codes_are_checked_against_the_metadata(tmp_path):
    meta = json.dumps({"variaveis": [{"id": config.POPULATION_VARIABLE, "unidade": "Mil Reais"}]}).encode()   # wrong unit on purpose
    col = collector(tmp_path, [FakeResponse(200, b"[]"), FakeResponse(200, b"[]"), FakeResponse(200, meta)])
    with pytest.raises(SourceError):
        col.collect_ibge()


# ----------------------------------------------------------------------------- parsers
def test_parse_municipios_handles_a_municipality_without_micro_region():
    body = [
        {"id": 1100015, "nome": "Alta Floresta D'Oeste", "microrregiao": {"id": 11006, "nome": "Cacoal", "mesorregiao": {"id": 1102, "nome": "Leste Rondoniense",
         "UF": {"id": 11, "sigla": "RO"}}}, "regiao-imediata": {"id": 110005, "nome": "Cacoal", "regiao-intermediaria": {"id": 1102, "nome": "Ji-Paraná"}}},
        {"id": 5101837, "nome": "Boa Esperança do Norte", "microrregiao": None, "regiao-imediata": {"id": 510008, "nome": "Sorriso",
         "regiao-intermediaria": {"id": 5103, "nome": "Sinop", "UF": {"id": 51, "sigla": "MT"}}}},
    ]
    rows = stage.parse_municipios(body)
    assert rows[0][:4] == (1100015, "Alta Floresta D'Oeste", 11, "RO") and rows[0][4] == 11006
    assert rows[1][:4] == (5101837, "Boa Esperança do Norte", 51, "MT") and rows[1][4] is None


def test_parse_sidra_returns_one_row_per_municipality_and_year():
    body = [{"id": "9324", "resultados": [{"series": [{"localidade": {"id": "1100015"}, "serie": {"2016": "25506", "2017": "..."}}]}]}]
    assert stage.parse_sidra(body) == [(1100015, 2016, "25506"), (1100015, 2017, "...")]          # '...' stays raw: ODS decides


def test_parse_sgs_and_holidays():
    assert stage.parse_sgs(1, [{"data": "02/12/2016", "valor": "3.4650"}]) == [(1, date(2016, 12, 2), "3.4650")]
    assert stage.parse_holidays([{"date": "2017-04-14", "name": "Sexta-feira Santa", "type": "national"}]) == [("2017-04-14", "Sexta-feira Santa", "national")]


def test_parse_ipca_ibge_pairs_change_and_index():
    body = [{"id": "63", "resultados": [{"series": [{"serie": {"201701": "0.38"}}]}]}, {"id": "2266", "resultados": [{"series": [{"serie": {"201701": "4793.85"}}]}]}]
    assert stage.parse_ipca_ibge(body) == [("201701", "0.38", "4793.85")]


# ----------------------------------------------------------------------------- fuzzy matching
CANDS = [("santa izabel do para", 1506500), ("santa maria do para", 1506401), ("sao paulo", 3550308)]


def test_fuzzy_accepts_a_close_unique_candidate():
    assert fuzzy_pick("santa isabel do para", CANDS)[0] == 1506500


def test_fuzzy_rejects_a_candidate_below_the_threshold():
    assert fuzzy_pick("boa vista de minas", [("bela vista de minas", 3106002), ("boa esperanca", 3107109)]) is None   # 92: a wrong match the threshold keeps out


def test_fuzzy_rejects_when_two_candidates_are_close():
    assert fuzzy_pick("santa rita do oeste", [("santa rita do oeste a", 1), ("santa rita do oeste b", 2)]) is None


# ----------------------------------------------------------------------------- database (needs PostgreSQL and data/raw/api)
@pytest.fixture(scope="module")
def engine():
    try:
        from etl.db import get_engine
        e = get_engine()
        with e.connect() as c:
            c.exec_driver_sql("SELECT 1")
    except Exception:       # noqa: BLE001
        pytest.skip("PostgreSQL not available")
    if not (config.LANDING_DIR / "ibge").exists():
        pytest.skip("landing zone data/raw/api is empty")
    return e


@pytest.mark.db
def test_staging_rerun_gives_the_same_row_counts(engine):
    from etl.log import new_batch_id
    first = stage.stage_all(engine, new_batch_id(engine))
    second = stage.stage_all(engine, new_batch_id(engine))
    assert first == second and first["api.stg_api_ibge_municipio"] >= 5570


@pytest.mark.db
def test_no_duplicate_keys_after_two_staging_runs(engine):
    with engine.connect() as c:
        dup = c.exec_driver_sql("SELECT count(*) FROM (SELECT series_code, ref_date FROM api.stg_api_bcb_serie GROUP BY 1, 2 HAVING count(*) > 1) x").scalar()
    assert dup == 0
