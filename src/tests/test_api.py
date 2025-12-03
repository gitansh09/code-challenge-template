# src/tests/test_api.py
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_weather_endpoint_works():
    response = client.get("/api/weather?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data


def test_stats_endpoint_works():
    response = client.get("/api/weather/stats?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "page_size" in data
    assert "total" in data
