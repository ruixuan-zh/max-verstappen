# backend

Python/FastAPI backend for the Singapore COE tracker and next-round predictor.

## MVP Scope

- Uses only historical COE bidding data.
- Fetches the official data.gov.sg COE bidding dataset.
- Trains a PyTorch model in memory.
- Predicts the next bidding round premium for Categories A, B, C, D, and E.
- Does not use PostgreSQL yet.

## Model

The first model is a small single-layer GRU regressor:

- Framework: PyTorch
- Sequence length: 12 historical bidding rounds
- Hidden size: 32
- GRU layers: 1
- Active dropout: 0.0 for the MVP
- Loss: Smooth L1 / Huber loss
- Optimizer: AdamW
- Target: `log(next_premium / latest_premium)`

The model is trained on sliding historical windows. This is normal supervised
time-series sample construction, not data augmentation. No noise injection,
feature masking, synthetic data, or dropout augmentation is used in this MVP.

The API also reports simple baselines on the chronological test split:

- last known premium
- 3-round rolling average premium

Future experiments can test a 0.2 dropout layer or light input noise if the
chronological validation split shows overfitting.

## Run Locally

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

```text
GET  /health
GET  /api/coe/history
GET  /api/coe/latest
GET  /api/coe/predictions/next
GET  /api/coe/model/metrics
POST /api/coe/model/retrain
```

## Optional Local Data

By default the backend fetches data from data.gov.sg. To use a local CSV with
the same columns, set:

```powershell
$env:COE_DATA_CSV="C:\path\to\COEBiddingResultsPrices.csv"
```
