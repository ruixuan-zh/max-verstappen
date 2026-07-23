from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status   

from app.data import fetch_all_coe_records, fetch_latest_coe_records
from app.forecast import last_value_forecast, rolling_average_forecast
from app.schemas import BaselineMetricsResponse, NextPredictionResponse
from app.storage import load_clean_coe_records, clean_coe_records_exist, save_raw_coe_records, save_clean_coe_records
from app.clean_data import clean_all_records
from app.evaluation import evaluate_baselines

NUM_OF_LATEST_RECORDS = 10

app = FastAPI(title="Singapore COE Tracker API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/coe/history")
def get_history():
    """
    Return saved historical COE bidding records.

    Records are loaded from the local processed data file.
    Each record uses the app's cleaned format, with normalized categories and integer numeric fields.
    """

    if not clean_coe_records_exist():
        return {
            "status": "missing_data",
            "message": "Run POST /api/coe/backfill first.",
        }

    records = load_clean_coe_records()
    return {"count": len(records), "records": records}


@app.get("/api/coe/latest")
def get_latest():
    """
    Return the last NUM_OF_LATEST_RECORDS historical COE bidding records from gov website.

    Latest records are loaded directly from the gov API, and not the stored data.
    Each record uses the app's cleaned format, with normalized categories and integer numeric fields.
    """

    records = fetch_latest_coe_records(limit=NUM_OF_LATEST_RECORDS)
    return {"count": len(records), "records": clean_all_records(records)}


@app.post("/api/coe/backfill")
def backfill_coe_history():
    """
    Retrieve all the historical COE bidding records from gov website.

    All records are loaded directly from the gov API, and not the stored data.
    Returns counts for both raw and cleaned records plus the local output paths.
    """

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

@app.get("/api/coe/model/metrics", response_model=BaselineMetricsResponse)
def get_metrics(test_fraction: Annotated[float, Query(gt=0, lt=1)] = 0.2, rolling_window: Annotated[int, Query(ge=1)] = 3):
    """
    Evaluate the baseline forecasting methods using stored COE records.

    The latest chronological portion of each category is used for evaluation.
    """

    if not clean_coe_records_exist():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Clean COE data is unavailable. "
                "Run POST /api/coe/backfill first."
            ),
        )

    records = load_clean_coe_records()

    evaluation = evaluate_baselines(records, test_fraction=test_fraction, rolling_window=rolling_window)
    return evaluation

@app.get("/api/coe/predictions/next", response_model=NextPredictionResponse)
def get_next_predictions(rolling_window: Annotated[int, Query(ge=1)] = 3):
    """
    Return the next predictions in NextPredictionResponse format
    """
    
    if not clean_coe_records_exist():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Clean COE data is unavailable. Run backfill: POST /api/coe/backfill first.")
        
    predictions = []
    records = load_clean_coe_records()
    for category in ("A", "B", "C", "D", "E"):
        latest = last_value_forecast(records, category)
        predictions.append(
            {
                "category": category,
                "latest_premium": latest,
                "last_value_prediction": latest,
                "rolling_average_prediction": rolling_average_forecast(records, category, rolling_window)
            }
        )
        
    return {
        "rolling_window": rolling_window,
            "predictions": predictions
    }
    