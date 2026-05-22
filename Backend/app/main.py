from fastapi import FastAPI
from app.data import fetch_all_coe_records, fetch_latest_coe_records

NUM_OF_LATEST_RECORDS = 10

app = FastAPI(title="Singapore COE Tracker API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/coe/history")
def get_history():
    records = fetch_all_coe_records()
    return {"count": len(records), "records": records}


@app.get("/api/coe/latest")
def get_latest():
    records = fetch_latest_coe_records(limit=NUM_OF_LATEST_RECORDS)
    return {"count": len(records), "records": records}