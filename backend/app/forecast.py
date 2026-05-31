"""
Simple COE forecast functions. Does not use machine learning, as each prediction is based only on recent historical premiums for each COE category.
"""


def _normalise_category(category: str) -> str:
    return category.replace("Category ", "").strip().upper()


def _records_for_category(records: list[dict], category: str) -> list[dict]:
    category_name = _normalise_category(category)
    matching_records = [
        record
        for record in records
        if _normalise_category(record["category"]) == category_name
    ]

    if not matching_records:
        raise ValueError(f"No COE records found for category {category_name}.")

    return sorted(
        matching_records,
        key=lambda record: (record["month"], record["bidding_no"]),
    )


def last_value_forecast(records: list[dict], category: str) -> int:
    """
    Predict the next premium by literally copy and pasting the latest known premium for the category.
    E.g. if Catefory A closed at $100,000 in the latest bidding exercise, the forecast is $100,000.
    """

    category_records = _records_for_category(records, category)
    return category_records[-1]["premium"]


def rolling_average_forecast(
    records: list[dict],
    category: str,
    window: int = 3,
) -> int:
    """
    Predict the next premium using the average of the latest "window" number of records.
    If fewer than "window" records are available, all available records for that category are used.
    """

    if window <= 0:
        raise ValueError("window must be greater than 0.")

    category_records = _records_for_category(records, category)
    recent_records = category_records[-window:]
    total_premium = sum(record["premium"] for record in recent_records)
    average_premium = total_premium / len(recent_records)

    return int(average_premium + 0.5)
