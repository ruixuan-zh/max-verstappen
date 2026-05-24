"""
Saves data to disk and reads data from disk
"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_COE_FILE = RAW_DATA_DIR / "coe_bidding_results_raw.json"
RAW_COE_METADATA_FILE = RAW_DATA_DIR / "coe_bidding_results_metadata.json"

PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_COE_FILE = PROCESSED_DATA_DIR / "coe_bidding_results_clean.json"
CLEAN_COE_METADATA_FILE = PROCESSED_DATA_DIR / "coe_bidding_results_clean_metadata.json"


def save_raw_coe_records(records: list[dict]) -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with RAW_COE_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    metadata = {
        "source": "data.gov.sg",
        "dataset_id": "d_69b3380ad7e51aff3a7dcc84eba52b8a",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
    }

    with RAW_COE_METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)


def load_raw_coe_records() -> list[dict]:
    with RAW_COE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def raw_coe_records_exist() -> bool:
    return RAW_COE_FILE.exists()


def save_clean_coe_records(records: list[dict]):
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with CLEAN_COE_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    metadata = {
        "source": "data/raw/coe_bidding_results_raw.json",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
    }

    with CLEAN_COE_METADATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)


def load_clean_coe_records() -> list[dict]:
    with CLEAN_COE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def clean_coe_records_exist() -> bool:
    return CLEAN_COE_FILE.exists()