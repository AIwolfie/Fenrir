"""Unit tests for Web UI FastAPI endpoints and REST APIs."""

from __future__ import annotations

from fastapi.testclient import TestClient
from web.app import app


def test_web_index():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "DeepRecon" in response.text
    assert "Indexed Pages" in response.text


def test_web_search():
    client = TestClient(app)
    response = client.get("/search?q=test")
    assert response.status_code == 200
    assert "DeepRecon Search" in response.text


def test_api_status():
    client = TestClient(app)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "metrics" in data
    assert "tor" in data
    assert "ai" in data


def test_api_sessions():
    client = TestClient(app)
    response = client.get("/api/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert isinstance(data["sessions"], list)


def test_api_tor_renew():
    client = TestClient(app)
    response = client.post("/api/tor/renew")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "tor_ip" in data


def test_api_stop_scan():
    client = TestClient(app)
    response = client.post("/api/scan/1/stop")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True


def test_api_stop_all_scans():
    client = TestClient(app)
    response = client.post("/api/scan/stop")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True

