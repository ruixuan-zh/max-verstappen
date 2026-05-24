from fastapi import FastAPI
from app.data import fetch_all_coe_records, fetch_latest_coe_records
from app.storage import load_raw_coe_records, raw_coe_records_exist, save_raw_coe_records, save_clean_coe_records
from app.clean_data import clean_all_records

NUM_OF_LATEST_RECORDS = 10

app = FastAPI(title="Singapore COE Tracker API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/coe/history")
def get_history():
    if not raw_coe_records_exist():
        return {
            "status": "missing_data",
            "message": "Run POST /api/coe/backfill first.",
        }

    records = load_raw_coe_records()
    return {"count": len(records), "records": records}


@app.get("/api/coe/latest")
def get_latest():
    records = fetch_latest_coe_records(limit=NUM_OF_LATEST_RECORDS)
    return {"count": len(records), "records": records}


@app.post("/api/coe/backfill")
def backfill_coe_history():
    raw_records = fetch_all_coe_records()
    save_raw_coe_records(raw_records)
    
    clean_records = clean_all_records(raw_records)
    save_clean_coe_records(clean_records)

    return {
        "status": "saved",
        "raw_count": len(raw_records),
        "clean_count": len(clean_records),
        "raw_path": "data/raw/coe_bidding_results_raw.json",
        "clean_path": "data/processed/coe_bidding_results_clean.json",
    }