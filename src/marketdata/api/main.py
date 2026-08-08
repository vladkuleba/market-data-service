from decimal import Decimal
from typing import Annotated

from fastapi import FastAPI, Query

from marketdata.api.schemas import Candle, CandlePage, Interval

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "UP"}


@app.get("/v1/candles")
async def candles(
    symbol: Annotated[str, Query()],
    interval: Annotated[Interval, Query()],
    start_time: Annotated[int, Query(ge=0)],
    end_time: Annotated[int, Query(ge=0)],
    limit: Annotated[int | None, Query(ge=1, le=1000)] = 100,
    cursor: Annotated[str | None, Query()] = None,
) -> CandlePage:

    candle = make_fake_candle()
    candle_page = CandlePage(data=[candle])
    return candle_page


def make_fake_candle() -> Candle:
    return Candle(
        open_time=1735689600000,
        open=Decimal("93500.10"),
        high=Decimal("93610.55"),
        low=Decimal("93480.00"),
        close=Decimal("93590.25"),
        volume=Decimal("12.34567"),
        close_time=1735689659999,
        quote_volume=Decimal("1154938.27"),
        trades=1543,
        taker_buy_base_volume=Decimal("6.12345"),
        taker_buy_quote_volume=Decimal("572847.91"),
    )
