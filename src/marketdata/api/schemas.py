from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

Interval = Literal[
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "2h",
    "4h",
    "6h",
    "8h",
    "12h",
    "1d",
    "3d",
    "1w",
    "1M",
]


class Candle(BaseModel):
    open_time: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    close_time: int
    quote_volume: Decimal
    trades: int
    taker_buy_base_volume: Decimal
    taker_buy_quote_volume: Decimal


class CandlePage(BaseModel):
    data: list[Candle]
    next_cursor: str | None = None
