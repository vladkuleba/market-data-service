from fastapi.testclient import TestClient

from marketdata.api import main

client = TestClient(main.app)


def test_health_database_available_returns_up(monkeypatch):
    monkeypatch.setattr(main, "load_settings", lambda: None)
    monkeypatch.setattr(main, "check_connection", lambda settings: True)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_health_database_down_is_unavailable(monkeypatch):
    monkeypatch.setattr(main, "load_settings", lambda: None)
    monkeypatch.setattr(main, "check_connection", lambda settings: False)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
