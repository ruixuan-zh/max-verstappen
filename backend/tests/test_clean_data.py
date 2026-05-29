from app.clean_data import clean_all_records, clean_record, normalize_category, parse_int


def make_raw_record(
    *,
    month: str = "2026-05",
    bidding_no: str = "2",
    vehicle_class: str = "Category A",
    quota: str = "1,239",
    bids_success: str = "1,227",
    bids_received: str = "2,283",
    premium: str = "124,229",
) -> dict:
    return {
        "month": month,
        "bidding_no": bidding_no,
        "vehicle_class": vehicle_class,
        "quota": quota,
        "bids_success": bids_success,
        "bids_received": bids_received,
        "premium": premium,
    }


def test_parse_int_converts_plain_number_string() -> None:
    assert parse_int("1301") == 1301


def test_parse_int_removes_commas_and_whitespace() -> None:
    assert parse_int(" 1,301 ") == 1301


def test_normalize_category_removes_category_prefix() -> None:
    assert normalize_category("Category A") == "A"


def test_clean_record_converts_raw_api_record_to_app_record() -> None:
    raw_record = make_raw_record()

    assert clean_record(raw_record) == {
        "month": "2026-05",
        "bidding_no": 2,
        "category": "A",
        "quota": 1239,
        "bids_success": 1227,
        "bids_received": 2283,
        "premium": 124229,
    }


def test_clean_all_records_sorts_by_month_bidding_number_and_category() -> None:
    raw_records = [
        make_raw_record(month="2026-05", bidding_no="2", vehicle_class="Category B"),
        make_raw_record(month="2026-04", bidding_no="2", vehicle_class="Category A"),
        make_raw_record(month="2026-05", bidding_no="1", vehicle_class="Category E"),
    ]

    cleaned_records = clean_all_records(raw_records)

    assert [
        (record["month"], record["bidding_no"], record["category"])
        for record in cleaned_records
    ] == [
        ("2026-04", 2, "A"),
        ("2026-05", 1, "E"),
        ("2026-05", 2, "B"),
    ]


def test_clean_all_records_returns_new_list_without_mutating_input() -> None:
    raw_records = [make_raw_record()]
    original_records = [record.copy() for record in raw_records]

    cleaned_records = clean_all_records(raw_records)

    assert cleaned_records is not raw_records
    assert raw_records == original_records
