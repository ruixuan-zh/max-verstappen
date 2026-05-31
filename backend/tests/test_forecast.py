import pytest

from app.forecast import last_value_forecast, rolling_average_forecast


def make_record(
    *,
    month: str,
    bidding_no: int,
    category: str,
    premium: int,
) -> dict:
    return {
        "month": month,
        "bidding_no": bidding_no,
        "category": category,
        "quota": 1000,
        "bids_success": 1000,
        "bids_received": 1200,
        "premium": premium,
    }


def test_last_value_forecast_returns_latest_premium_for_category() -> None:
    records = [
        make_record(month="2026-05", bidding_no=2, category="A", premium=120000),
        make_record(month="2026-05", bidding_no=1, category="A", premium=100000),
        make_record(month="2026-05", bidding_no=2, category="B", premium=150000),
    ]

    assert last_value_forecast(records, "A") == 120000


def test_last_value_forecast_accepts_category_prefix() -> None:
    records = [
        make_record(month="2026-05", bidding_no=2, category="A", premium=120000),
    ]

    assert last_value_forecast(records, "Category A") == 120000


def test_rolling_average_forecast_uses_latest_window_for_category() -> None:
    records = [
        make_record(month="2026-04", bidding_no=1, category="A", premium=90000),
        make_record(month="2026-04", bidding_no=2, category="A", premium=100000),
        make_record(month="2026-05", bidding_no=1, category="A", premium=110000),
        make_record(month="2026-05", bidding_no=2, category="A", premium=120000),
        make_record(month="2026-05", bidding_no=2, category="B", premium=200000),
    ]

    assert rolling_average_forecast(records, "A", window=3) == 110000


def test_rolling_average_forecast_uses_available_records_when_window_is_large() -> None:
    records = [
        make_record(month="2026-05", bidding_no=1, category="A", premium=100000),
        make_record(month="2026-05", bidding_no=2, category="A", premium=120001),
    ]

    assert rolling_average_forecast(records, "A", window=10) == 110001


def test_forecast_raises_when_category_has_no_records() -> None:
    records = [
        make_record(month="2026-05", bidding_no=1, category="A", premium=100000),
    ]

    with pytest.raises(ValueError, match="No COE records found for category B"):
        last_value_forecast(records, "B")


def test_rolling_average_forecast_raises_when_window_is_not_positive() -> None:
    records = [
        make_record(month="2026-05", bidding_no=1, category="A", premium=100000),
    ]

    with pytest.raises(ValueError, match="window must be greater than 0"):
        rolling_average_forecast(records, "A", window=0)
