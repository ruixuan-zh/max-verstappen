"""
Clean raw data 
"""

def parse_int(val: str) -> int:
    cleaned_val = val.replace(",", "").strip()
    return int(cleaned_val) 


def normalize_category(val: str) -> str:
    return val.replace("Category ", "").strip()


def clean_record(record: dict) -> dict:
    return {
        "month": record["month"],
        "bidding_no": parse_int(record["bidding_no"]),
        "category": normalize_category(record["vehicle_class"]),
        "quota": parse_int(record["quota"]),
        "bids_success": parse_int(record["bids_success"]),
        "bids_received": parse_int(record["bids_received"]),
        "premium": parse_int(record["premium"]),
    }


def clean_all_records(records: list[dict]) -> list[dict]:
    cleaned_records = []
    for record in records:
        cleaned_records.append(clean_record(record))

    return sorted(
        cleaned_records,
        key=lambda record: (
            record["month"],
            record["bidding_no"],
            record["category"],
        ),
    )

