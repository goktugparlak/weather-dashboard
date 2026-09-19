"""Exercise the real API/service with only the external HTTP transport mocked."""
from copy import deepcopy

import httpx
import pytest
from fastapi.testclient import TestClient

from backend.main import app, get_weather_client

SAMPLE = {
    "name": "Torino", "sys": {"country": "IT"},
    "main": {"temp": 23.4, "feels_like": 22.8, "humidity": 54},
    "weather": [{"main": "Clouds", "description": "few clouds"}],
    "wind": {"speed": 2.6},
}


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key-not-real")
    state = {"requests": [], "status": 200, "data": deepcopy(SAMPLE)}

    def handler(request):
        state["requests"].append(request)
        if "exception" in state:
            raise state["exception"]("simulated provider failure", request=request)
        if "raw" in state:
            return httpx.Response(state["status"], content=state["raw"])
        return httpx.Response(state["status"], json=state["data"])

    async def client_override():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            yield client

    app.dependency_overrides[get_weather_client] = client_override
    with TestClient(app) as client:
        yield client, state
    app.dependency_overrides.clear()


def test_success_and_provider_parameters(api):
    client, state = api
    response = client.get("/weather", params={"city": "  Torino,IT  "})
    assert response.status_code == 200
    assert response.json() == {
        "city": "Torino", "country": "IT", "temperature": 23.4,
        "feels_like": 22.8, "condition": "Clouds", "description": "few clouds",
        "humidity": 54, "wind_speed": 2.6,
    }
    request = state["requests"][0]
    assert request.url.host == "api.openweathermap.org"
    assert request.url.params["q"] == "Torino,IT"
    assert request.url.params["units"] == "metric"
    assert request.url.params["appid"] == "test-key-not-real"
    assert "test-key" not in response.text


@pytest.mark.parametrize("city", [None, "", " ", "   ", "a", " a ", "x" * 101])
def test_invalid_city_never_calls_provider(api, city):
    client, state = api
    response = client.get("/weather", params={} if city is None else {"city": city})
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)
    assert not state["requests"]


@pytest.mark.parametrize("city", ["São Paulo", "İstanbul", "Clermont-Ferrand", "東京", "x" * 100])
def test_international_and_boundary_city_names(api, city):
    client, state = api
    assert client.get("/weather", params={"city": city}).status_code == 200
    assert state["requests"][0].url.params["q"] == city


@pytest.mark.parametrize("key", [None, "", "   ", "your_api_key_here"])
def test_missing_key_never_calls_provider(api, monkeypatch, key):
    client, state = api
    if key is None:
        monkeypatch.delenv("OPENWEATHER_API_KEY")
    else:
        monkeypatch.setenv("OPENWEATHER_API_KEY", key)
    response = client.get("/weather", params={"city": "Torino"})
    assert response.status_code == 500
    assert response.json()["detail"] == "Weather API key is not configured"
    assert not state["requests"]


@pytest.mark.parametrize("provider_status,expected", [(404, 404), (429, 503), (401, 502), (403, 502), (500, 502), (302, 502)])
def test_provider_status_mapping(api, provider_status, expected, caplog):
    client, state = api
    state["status"] = provider_status
    response = client.get("/weather", params={"city": "Torino"})
    assert response.status_code == expected
    assert isinstance(response.json()["detail"], str)
    assert "test-key-not-real" not in response.text + caplog.text


@pytest.mark.parametrize("exception,expected", [(httpx.ReadTimeout, 504), (httpx.ConnectError, 503)])
def test_network_failures(api, exception, expected):
    client, state = api
    state["exception"] = exception
    response = client.get("/weather", params={"city": "Torino"})
    assert response.status_code == expected
    assert "test-key" not in response.text


@pytest.mark.parametrize("data", [None, [], {}, {**SAMPLE, "weather": []}, {**SAMPLE, "main": None},
    {**SAMPLE, "main": {"temp": 23, "feels_like": 22, "humidity": 101}},
    {**SAMPLE, "wind": {"speed": -1}}, {**SAMPLE, "name": ""}])
def test_malformed_provider_payload(api, data):
    client, state = api
    state["data"] = data
    assert client.get("/weather", params={"city": "Torino"}).status_code == 502


def test_invalid_json(api):
    client, state = api
    state["raw"] = b"<html>temporary outage</html>"
    assert client.get("/weather", params={"city": "Torino"}).status_code == 502


def test_static_files_health_and_docs(api):
    client, state = api
    assert "Weather Dashboard" in client.get("/").text
    assert client.get("/static/script.js").status_code == 200
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/docs").status_code == 200
    assert "/weather" in client.get("/openapi.json").json()["paths"]
    assert not state["requests"]


def test_secrets_are_not_served(api):
    client, _ = api
    for path in ["/.env", "/static/.env", "/backend/weather.py"]:
        assert client.get(path).status_code == 404
