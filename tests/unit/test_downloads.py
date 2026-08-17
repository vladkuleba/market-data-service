from fastapi.testclient import TestClient

from marketdata.api.main import app

client = TestClient(app)


def test_downloads_valid_request_returns_status():
    response = client.post(
        "/v1/downloads",
        json={"symbol": "string", "interval": "1s", "start_time": 0, "end_time": 0},
    )
    assert response.status_code == 201
    assert response.json() == {"id": 0, "status": "pending", "error": None}


def test_downloads_missing_params_is_rejected():
    response = client.post("/v1/downloads")
    assert response.status_code == 422


def test_downloads_invalid_interval_is_rejected():
    response = client.post(
        "/v1/downloads",
        json={"symbol": "string", "interval": "27s", "start_time": 0, "end_time": 0},
    )
    assert response.status_code == 422
