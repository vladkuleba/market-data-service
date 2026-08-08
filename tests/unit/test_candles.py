from fastapi.testclient import TestClient

from marketdata.api.main import app

client = TestClient(app)


def test_candles_valid_request_returns_page():
    response = client.get(
        "/v1/candles",
        params={
            "symbol": "BTCUSDT",
            "interval": "15m",
            "start_time": 100,
            "end_time": 200,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "open_time": 1735689600000,
                "open": "93500.10",
                "high": "93610.55",
                "low": "93480.00",
                "close": "93590.25",
                "volume": "12.34567",
                "close_time": 1735689659999,
                "quote_volume": "1154938.27",
                "trades": 1543,
                "taker_buy_base_volume": "6.12345",
                "taker_buy_quote_volume": "572847.91",
            }
        ],
        "next_cursor": None,
    }


def test_candles_missing_params_is_rejected():
    response = client.get("/v1/candles")
    assert response.status_code == 422
