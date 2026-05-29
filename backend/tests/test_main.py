from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)


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


def make_clean_record(
    *,
    month: str = "2026-05",
    bidding_no: int = 2,
    category: str = "A",
    quota: int = 1239,
    bids_success: int = 1227,
    bids_received: int = 2283,
    premium: int = 124229,
) -> dict:
    return {
        "month": month,
        "bidding_no": bidding_no,
        "category": category,
        "quota": quota,
        "bids_success": bids_success,
        "bids_received": bids_received,
        "premium": premium,
    }


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_history_returns_missing_data_message_when_clean_file_is_missing(
    monkeypatch,
) -> None:
    monkeypatch.setattr(main, "clean_coe_records_exist", lambda: False)

    response = client.get("/api/coe/history")

    assert response.status_code == 200
    assert response.json() == {
        "status": "missing_data",
        "message": "Run POST /api/coe/backfill first.",
    }


def test_get_history_returns_clean_records_from_storage(monkeypatch) -> None:
    records = [make_clean_record()]
    monkeypatch.setattr(main, "clean_coe_records_exist", lambda: True)
    monkeypatch.setattr(main, "load_clean_coe_records", lambda: records)

    response = client.get("/api/coe/history")

    assert response.status_code == 200
    assert response.json() == {"count": 1, "records": records}


def test_get_latest_fetches_raw_records_and_returns_clean_records(monkeypatch) -> None:
    raw_records = [make_raw_record()]

    def fake_fetch_latest_coe_records(limit: int) -> list[dict]:
        assert limit == main.NUM_OF_LATEST_RECORDS
        return raw_records

    monkeypatch.setattr(main, "fetch_latest_coe_records", fake_fetch_latest_coe_records)

    response = client.get("/api/coe/latest")

    assert response.status_code == 200
    assert response.json() == {"count": 1, "records": [make_clean_record()]}


def test_backfill_fetches_saves_cleans_and_reports_counts(monkeypatch) -> None:
    raw_records = [
        make_raw_record(month="2026-05", bidding_no="2", vehicle_class="Category B"),
        make_raw_record(month="2026-05", bidding_no="1", vehicle_class="Category A"),
    ]
    saved_records = {}

    monkeypatch.setattr(main, "fetch_all_coe_records", lambda: raw_records)
    monkeypatch.setattr(
        main,
        "save_raw_coe_records",
        lambda records: saved_records.setdefault("raw", records),
    )
    monkeypatch.setattr(
        main,
        "save_clean_coe_records",
        lambda records: saved_records.setdefault("clean", records),
    )

    response = client.post("/api/coe/backfill")

    assert response.status_code == 200
    assert response.json() == {
        "status": "saved",
        "raw_count": 2,
        "clean_count": 2,
        "raw_path": "data/raw/coe_bidding_results_raw.json",
        "clean_path": "data/processed/coe_bidding_results_clean.json",
    }
    assert saved_records["raw"] == raw_records
    assert saved_records["clean"] == [
        make_clean_record(month="2026-05", bidding_no=1, category="A"),
        make_clean_record(month="2026-05", bidding_no=2, category="B"),
    ]
