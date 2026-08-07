from decimal import Decimal

from pydantic import BaseModel


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
