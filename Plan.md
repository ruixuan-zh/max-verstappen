# Singapore COE Tracker And Predictor Plan

## Summary
- Current repo is only a scaffold: tracked files are `README.md` and `.gitignore`; `backend`, `frontend`, `data`, `docs`, and `scripts` are empty.
- Planned stack is directionally good, but should be made more specific: **Next.js + TypeScript**, **Python FastAPI**, **PostgreSQL**, and a separate **data/model pipeline**.
- Build v1 as a **personal tool** that predicts the **next COE bidding round**, using structured signals plus tagged current-event/news inputs.
- Latest official baseline to design around: LTA’s COE results PDF includes May 2026 first bidding results dated 7 May 2026, with Cat A at S$124,790 and Cat B at S$126,236. LTA also announced the May-Jul 2026 quota as 19,052 COEs.

Sources: [data.gov.sg COE dataset](https://data.gov.sg/datasets?groups=&organization=&q=&query=car&resultId=d_69b3380ad7e51aff3a7dcc84eba52b8a), [LTA COE results PDF](https://www.lta.gov.sg/content/dam/ltagov/who_we_are/statistics_and_publications/statistics/pdf/M11-COE_Results_2025_2026.pdf), [LTA May-Jul 2026 quota release](https://www.lta.gov.sg/content/ltagov/en/newsroom/2026/4/news-releases/certificate-of-entitlement--coes--quota-for-may-2026-to-july-202.html), [LTA DataMall static datasets](https://datamall.lta.gov.sg/content/datamall/en/static-data.html).

## Key Changes
- Keep the current folder layout, but formalize it:
  - `frontend`: Next.js App Router, TypeScript, charts, forecast UI.
  - `backend`: FastAPI API for results, forecasts, model metadata, and event tags.
  - `data`: raw and processed local snapshots, preferably CSV/Parquet.
  - `scripts`: ingestion, backfill, training, and evaluation commands.
  - `docs`: data dictionary, modeling notes, source/licensing notes.
- Update `.gitignore` later to include Node/Next.js artifacts: `node_modules`, `.next`, `out`, npm/pnpm logs, local DB dumps, and model artifacts.
- Use Data.gov.sg as the first historical source: dataset `d_69b3380ad7e51aff3a7dcc84eba52b8a`, covering Jan 2010 to Apr 2026 with fields `month`, `bidding_no`, `vehicle_class`, `quota`, `bids_success`, `bids_received`, `premium`.
- Use LTA DataMall/static PDFs for fresher official results and supporting signals: COE bidding results, monthly deregistrations, monthly vehicle population, monthly new registrations, COE revalidations, and quota announcements.
- Do not make an LLM the forecasting model. Use it, if desired, only to tag/summarize events into structured labels.

## Implementation Shape
- Database tables:
  - `coe_results`: category, month, bidding number, quota, successful bids, bids received, premium.
  - `coe_quota_announcements`: quarter, category, announced quota, source URL, announced date.
  - `market_events`: date, source, title, event type, category impact, sentiment/pressure score, URL.
  - `forecast_runs`: model version, training window, run date, metrics.
  - `forecasts`: target bidding round, category, predicted premium, confidence band, explanation fields.
- Backend API:
  - `GET /api/coe/results`
  - `GET /api/coe/latest`
  - `GET /api/events`
  - `GET /api/forecast/latest`
  - `POST /api/forecast/run` for local/manual model refresh only.
- Modeling approach:
  - Start with baselines: last value, moving average, seasonal naive.
  - Add tabular ML: LightGBM/XGBoost or scikit-learn gradient boosting.
  - Features: lagged premiums, bid-to-quota ratio, successful-bid ratio, category, bidding number, month, quota change, latest quarterly quota, deregistration/new-registration trends, and event tags.
  - Evaluate by walk-forward validation, measuring MAE, MAPE, and whether direction was correct.
- Event/news approach:
  - Official policy/quota events from LTA should be treated as high-confidence structured events.
  - News feed tagging can supplement the model, but store source URL and short metadata only; avoid copying full article text.
  - Event tags should be constrained, e.g. `quota_change`, `policy_change`, `motor_show`, `dealer_promotion`, `loan_rate`, `ev_policy`, `economic_signal`.

## What To Do Next
- First milestone: create a data notebook/script that pulls historical COE data, normalizes categories, and produces clean charts.
- Second milestone: build a baseline model and prove it beats naive forecasts for Cat A and Cat B next-round prediction.
- Third milestone: create the FastAPI service and database schema around the cleaned dataset.
- Fourth milestone: build a simple Next.js dashboard showing latest COE prices, category trends, bid pressure, event timeline, and next-round forecast.
- Fifth milestone: add scheduled ingestion and model refresh.

## Test Plan
- Data ingestion tests:
  - Parse all official records from Jan 2010 onward.
  - Confirm numeric fields are cleaned consistently despite commas/currency formatting.
  - Confirm May 2022 category-definition changes are represented without breaking historical comparisons.
- API tests:
  - Latest COE endpoint returns the newest official result by date and bidding number.
  - Forecast endpoint always includes model version, target round, source timestamp, and confidence interval.
- Model tests:
  - Baseline comparison must be reported before accepting ML output.
  - Walk-forward validation must not train on future bidding rounds.
  - Directional accuracy and MAE must be tracked separately for Cat A and Cat B.
- UI acceptance:
  - User can see latest prices, historical chart, bid pressure, event timeline, and next-round prediction on the first screen.
  - Every forecast shows “not financial advice” style uncertainty language and links to data sources.

## Assumptions
- v1 is a personal research tool, not a public financial-advice product.
- Prediction target is the next bidding round.
- The model should forecast car categories first: Cat A, Cat B, and optionally Cat E.
- Current events will combine structured official signals with tagged news/event metadata, but structured data remains the primary model input.
