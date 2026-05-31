import json

from app import storage


def configure_storage_paths(monkeypatch, tmp_path) -> None:
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"

    monkeypatch.setattr(storage, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(storage, "RAW_COE_FILE", raw_dir / "coe_bidding_results_raw.json")
    monkeypatch.setattr(
        storage,
        "RAW_COE_METADATA_FILE",
        raw_dir / "coe_bidding_results_metadata.json",
    )
    monkeypatch.setattr(storage, "PROCESSED_DATA_DIR", processed_dir)
    monkeypatch.setattr(
        storage,
        "CLEAN_COE_FILE",
        processed_dir / "coe_bidding_results_clean.json",
    )
    monkeypatch.setattr(
        storage,
        "CLEAN_COE_METADATA_FILE",
        processed_dir / "coe_bidding_results_clean_metadata.json",
    )


def test_save_and_load_raw_coe_records(monkeypatch, workspace_tmp_path) -> None:
    configure_storage_paths(monkeypatch, workspace_tmp_path)
    records = [
        {
            "month": "2026-05",
            "bidding_no": "2",
            "vehicle_class": "Category A",
            "quota": "1239",
            "bids_success": "1227",
            "bids_received": "2283",
            "premium": "124229",
        }
    ]

    assert storage.raw_coe_records_exist() is False

    storage.save_raw_coe_records(records)

    assert storage.raw_coe_records_exist() is True
    assert storage.load_raw_coe_records() == records


def test_save_raw_coe_records_writes_metadata(monkeypatch, workspace_tmp_path) -> None:
    configure_storage_paths(monkeypatch, workspace_tmp_path)
    records = [{"month": "2026-05"}]

    storage.save_raw_coe_records(records)

    metadata = json.loads(storage.RAW_COE_METADATA_FILE.read_text(encoding="utf-8"))
    assert metadata["source"] == "data.gov.sg"
    assert metadata["dataset_id"] == "d_69b3380ad7e51aff3a7dcc84eba52b8a"
    assert metadata["record_count"] == 1
    assert "fetched_at" in metadata


def test_save_and_load_clean_coe_records(monkeypatch, workspace_tmp_path) -> None:
    configure_storage_paths(monkeypatch, workspace_tmp_path)
    records = [
        {
            "month": "2026-05",
            "bidding_no": 2,
            "category": "A",
            "quota": 1239,
            "bids_success": 1227,
            "bids_received": 2283,
            "premium": 124229,
        }
    ]

    assert storage.clean_coe_records_exist() is False

    storage.save_clean_coe_records(records)

    assert storage.clean_coe_records_exist() is True
    assert storage.load_clean_coe_records() == records


def test_save_clean_coe_records_writes_metadata(monkeypatch, workspace_tmp_path) -> None:
    configure_storage_paths(monkeypatch, workspace_tmp_path)
    records = [{"month": "2026-05"}]

    storage.save_clean_coe_records(records)

    metadata = json.loads(storage.CLEAN_COE_METADATA_FILE.read_text(encoding="utf-8"))
    assert metadata["source"] == "data/raw/coe_bidding_results_raw.json"
    assert metadata["record_count"] == 1
    assert "processed_at" in metadata
