"""Tests for the fixture and HTTP adapters."""

import json
from pathlib import Path
from typing import Any

import pytest
import requests

from pizza_client.adapters import FixturePizzeriaSource, HttpPizzeriaSource
from pizza_client.exceptions import MalformedPayloadError, TransientAPIError


class FakeResponse:
    """Just enough of `requests.Response` for the adapter."""

    def __init__(self, status_code: int, payload: Any = None) -> None:  # noqa: ANN401
        self.status_code = status_code
        self._payload = payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self) -> Any:  # noqa: ANN401
        return self._payload


# --- fixture adapter --------------------------------------------------------


def test_fixture_reads_the_shipped_dataset(fixture_file: Path) -> None:
    pizzerias = FixturePizzeriaSource(fixture_file).read_pizzerias()
    assert len(pizzerias) > 10
    assert any(p.has_coordinates for p in pizzerias)
    assert any(not p.has_coordinates for p in pizzerias), "keep one unmappable entry in the fixture"


def test_fixture_reads_a_custom_file(tmp_path: Path, api_record: dict[str, Any]) -> None:
    path = tmp_path / "one.json"
    path.write_text(json.dumps([api_record]), encoding="utf-8")
    assert [p.name for p in FixturePizzeriaSource(path).read_pizzerias()] == ["50 Kalò"]


def test_fixture_missing_file(tmp_path: Path) -> None:
    with pytest.raises(MalformedPayloadError, match="not found"):
        FixturePizzeriaSource(tmp_path / "nope.json").read_pizzerias()


def test_fixture_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(MalformedPayloadError, match="not valid JSON"):
        FixturePizzeriaSource(path).read_pizzerias()


# --- http adapter -----------------------------------------------------------


def test_http_builds_the_endpoint_from_base_url(
    monkeypatch: pytest.MonkeyPatch, api_record: dict[str, Any]
) -> None:
    seen: list[str] = []

    def fake_get(url: str, timeout: float) -> FakeResponse:
        seen.append(url)
        return FakeResponse(200, [api_record])

    monkeypatch.setattr(requests, "get", fake_get)
    pizzerias = HttpPizzeriaSource("http://api.test/").read_pizzerias()

    assert seen == ["http://api.test/pizzerias/all"]
    assert pizzerias[0].id == 7


def test_http_retries_on_retryable_status(
    monkeypatch: pytest.MonkeyPatch, api_record: dict[str, Any]
) -> None:
    answers = iter([FakeResponse(503), FakeResponse(200, [api_record])])
    monkeypatch.setattr(requests, "get", lambda url, timeout: next(answers))  # noqa: ARG005
    monkeypatch.setattr("tenacity.nap.time.sleep", lambda _: None)

    assert len(HttpPizzeriaSource("http://api.test", max_attempts=2).read_pizzerias()) == 1


def test_http_gives_up_after_max_attempts(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def always_down(url: str, timeout: float) -> FakeResponse:
        nonlocal calls
        calls += 1
        raise requests.ConnectionError("down")

    monkeypatch.setattr(requests, "get", always_down)
    monkeypatch.setattr("tenacity.nap.time.sleep", lambda _: None)

    with pytest.raises(TransientAPIError, match="unreachable"):
        HttpPizzeriaSource("http://api.test", max_attempts=3).read_pizzerias()
    assert calls == 3


def test_http_does_not_retry_client_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(requests, "get", lambda url, timeout: FakeResponse(404))  # noqa: ARG005
    with pytest.raises(requests.HTTPError):
        HttpPizzeriaSource("http://api.test").read_pizzerias()
