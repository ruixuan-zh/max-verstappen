"""
Data access functions for COE records.

Uses data.gov.sg API to fetch COE information for the rest of the application to use.
"""


import requests

DATA_URL = "https://data.gov.sg/api/action/datastore_search"
COE_DATASET_ID = "d_69b3380ad7e51aff3a7dcc84eba52b8a"


def fetch_all_coe_records():
    all_records = []
    limit = 500
    offset = 0

    # Paginated approach to fetching data
    while True:
        params = {
            "resource_id": COE_DATASET_ID,
            "limit": limit,
            "offset": offset,
        }

        # GET request for all the data and check for error
        response = requests.get(DATA_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data["success"]:
            raise requests.HTTPError("API call failed.")

        result = data["result"]
        records = result["records"]
        total = result["total"]

        all_records.extend(records)

        if len(all_records) >= total:
            break
        offset += limit


    return all_records


def fetch_latest_coe_records(limit: int = 10):
    params = {
        "resource_id": COE_DATASET_ID,
        "limit": limit,
        "sort": "month desc, bidding_no desc",
    }

    response = requests.get(DATA_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    if not data["success"]:
        raise requests.HTTPError("API call failed.")
    
    return data["result"]["records"]