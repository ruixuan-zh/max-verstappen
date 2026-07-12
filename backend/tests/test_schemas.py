import pytest
from pydantic import ValidationError

from app.schemas import CoeRecord


def make_valid_record(**overrides: object) -> dict:
    """
    Return valid record data with optional field overrides.
    """

    record = {
        "month": "2026-05",
        "bidding_no": 2,
        "category": "A",
        "quota": 1239,
        "bids_success": 1227,
        "bids_received": 2283,
        "premium": 124229,
    }
    record.update(overrides)
    return record


def test_valid_record_is_accepted() -> None:
    record = CoeRecord.model_validate(make_valid_record())

    assert record.month == "2026-05"
    assert record.bidding_no == 2
    assert record.category == "A"
    assert record.quota == 1239
    assert record.bids_success == 1227
    assert record.bids_received == 2283
    assert record.premium == 124229


@pytest.mark.parametrize(
    "month",
    [
        "2026-00",
        "2026-13",
        "2026-5",
        "May 2026",
    ],
)
def test_invalid_month_is_rejected(month: str) -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(make_valid_record(month=month))


@pytest.mark.parametrize("bidding_no", [0, 3, -1])
def test_invalid_bidding_number_is_rejected(bidding_no: int) -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(
            make_valid_record(bidding_no=bidding_no),
        )


@pytest.mark.parametrize("category", ["F", "Unknown", "Category A", "a"])
def test_invalid_category_is_rejected(category: str) -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(
            make_valid_record(category=category),
        )


@pytest.mark.parametrize(
    "field",
    [
        "quota",
        "bids_success",
        "bids_received",
    ],
)
def test_negative_count_is_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(
            make_valid_record(**{field: -1}),
        )


@pytest.mark.parametrize("premium", [0, -1])
def test_non_positive_premium_is_rejected(premium: int) -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(
            make_valid_record(premium=premium),
        )


def test_successful_bids_cannot_exceed_received_bids() -> None:
    with pytest.raises(
        ValidationError,
        match="Successful bids cannot exceed received bids",
    ):
        CoeRecord.model_validate(
            make_valid_record(
                bids_success=101,
                bids_received=100,
            ),
        )


def test_unexpected_field_is_rejected() -> None:
    record = make_valid_record()
    record["unexpected"] = "value"

    with pytest.raises(ValidationError):
        CoeRecord.model_validate(record)


def test_numeric_strings_are_rejected() -> None:
    with pytest.raises(ValidationError):
        CoeRecord.model_validate(
            make_valid_record(quota="1239"),
        )


def test_record_can_be_serialised_to_dictionary() -> None:
    record = CoeRecord.model_validate(make_valid_record())

    assert record.model_dump() == make_valid_record()