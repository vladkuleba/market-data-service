from fastapi.testclient import TestClient

from marketdata.api.main import app

client = TestClient(app)


def test_downloads_valid_request_returns_status():
    response = client.post(
        "/v1/downloads",
        json={"symbol": "BTCUSDT", "interval": "1s", "start_time": 0, "end_time": 200},
    )
    assert response.status_code == 201
    assert response.json() == {"id": 0, "status": "pending", "error": None}


def test_downloads_missing_params_is_rejected():
    response = client.post("/v1/downloads")
    assert response.status_code == 422


def test_downloads_invalid_interval_is_rejected():
    response = client.post(
        "/v1/downloads",
        json={"symbol": "BTCUSDT", "interval": "27s", "start_time": 0, "end_time": 200},
    )
    assert response.status_code == 422


def test_downloads_existing_id_returns_status():
    job_id = 7
    response = client.get(f"/v1/downloads/{job_id}")
    assert response.status_code == 200
    assert response.json() == {"id": job_id, "status": "pending", "error": None}


def test_downloads_unknown_id_is_not_found():
    job_id = -1
    response = client.get(f"/v1/downloads/{job_id}")
    assert response.status_code == 404


def test_downloads_non_numeric_id_is_rejected():
    job_id = "abs"
    response = client.get(f"/v1/downloads/{job_id}")
    assert response.status_code == 422
