from decimal import Decimal

import pytest
from pydantic import ValidationError

from marketdata.api.schemas import Candle


@pytest.fixture
def candle_fields():
    return {
        "open_time": 1735689600000,
        "open": Decimal("93500.10"),
        "high": Decimal("93610.55"),
        "low": Decimal("93480.00"),
        "close": Decimal("93590.25"),
        "volume": Decimal("12.34567"),
        "close_time": 1735689659999,
        "quote_volume": Decimal("1154938.27"),
        "trades": 1543,
        "taker_buy_base_volume": Decimal("6.12345"),
        "taker_buy_quote_volume": Decimal("572847.91"),
    }


def test_candle_valid_values_are_accepted(candle_fields):
    Candle(**candle_fields)


def test_candle_negative_price_is_rejected(candle_fields):
    candle_fields["open"] = Decimal("-1")
    with pytest.raises(ValidationError):
        Candle(**candle_fields)


def test_candle_too_many_whole_digits_is_rejected(candle_fields):
    candle_fields["open"] = Decimal("93500153421.10")
    with pytest.raises(ValidationError):
        Candle(**candle_fields)


def test_candle_too_many_decimal_places_is_rejected(candle_fields):
    candle_fields["open"] = Decimal("93500.101242134")
    with pytest.raises(ValidationError):
        Candle(**candle_fields)
