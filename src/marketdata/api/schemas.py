from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

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
    open: Decimal = Field(max_digits=18, decimal_places=8, gt=0)
    high: Decimal = Field(max_digits=18, decimal_places=8, gt=0)
    low: Decimal = Field(max_digits=18, decimal_places=8, gt=0)
    close: Decimal = Field(max_digits=18, decimal_places=8, gt=0)
    volume: Decimal = Field(max_digits=24, decimal_places=8, ge=0)
    close_time: int
    quote_volume: Decimal = Field(max_digits=24, decimal_places=8, ge=0)
    trades: int
    taker_buy_base_volume: Decimal = Field(max_digits=24, decimal_places=8, ge=0)
    taker_buy_quote_volume: Decimal = Field(max_digits=24, decimal_places=8, ge=0)


class CandlePage(BaseModel):
    data: list[Candle]
    next_cursor: str | None = None
