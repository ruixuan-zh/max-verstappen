import pytest
import requests

from app import data as coe_data


class FakeResponse:
    def __init__(self, payload: dict, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error

    def raise_for_status(self) -> None:
        if self.error:
            raise self.error

    def json(self) -> dict:
        return self.payload


def test_fetch_all_coe_records_paginates_until_all_records_are_fetched(
    monkeypatch,
) -> None:
    calls = []
    pages = [
        {
            "success": True,
            "result": {
                "records": [{"_id": 1}, {"_id": 2}],
                "total": 3,
            },
        },
        {
            "success": True,
            "result": {
                "records": [{"_id": 3}],
                "total": 3,
            },
        },
    ]

    def fake_get(url: str, *, params: dict, timeout: int) -> FakeResponse:
        calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(pages.pop(0))

    monkeypatch.setattr(coe_data.requests, "get", fake_get)

    records = coe_data.fetch_all_coe_records()

    assert records == [{"_id": 1}, {"_id": 2}, {"_id": 3}]
    assert calls == [
        {
            "url": coe_data.DATA_URL,
            "params": {
                "resource_id": coe_data.COE_DATASET_ID,
                "limit": 500,
                "offset": 0,
            },
            "timeout": 10,
        },
        {
            "url": coe_data.DATA_URL,
            "params": {
                "resource_id": coe_data.COE_DATASET_ID,
                "limit": 500,
                "offset": 500,
            },
            "timeout": 10,
        },
    ]


def test_fetch_all_coe_records_raises_when_api_reports_failure(monkeypatch) -> None:
    def fake_get(url: str, *, params: dict, timeout: int) -> FakeResponse:
        return FakeResponse({"success": False})

    monkeypatch.setattr(coe_data.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        coe_data.fetch_all_coe_records()


def test_fetch_latest_coe_records_requests_latest_records(monkeypatch) -> None:
    calls = []
    payload = {
        "success": True,
        "result": {
            "records": [{"_id": 10}, {"_id": 9}],
        },
    }

    def fake_get(url: str, *, params: dict, timeout: int) -> FakeResponse:
        calls.append({"url": url, "params": params, "timeout": timeout})
        return FakeResponse(payload)

    monkeypatch.setattr(coe_data.requests, "get", fake_get)

    records = coe_data.fetch_latest_coe_records(limit=2)

    assert records == [{"_id": 10}, {"_id": 9}]
    assert calls == [
        {
            "url": coe_data.DATA_URL,
            "params": {
                "resource_id": coe_data.COE_DATASET_ID,
                "limit": 2,
                "sort": "month desc, bidding_no desc",
            },
            "timeout": 10,
        }
    ]


def test_fetch_latest_coe_records_raises_http_errors(monkeypatch) -> None:
    def fake_get(url: str, *, params: dict, timeout: int) -> FakeResponse:
        return FakeResponse(
            {},
            error=requests.HTTPError("Request failed."),
        )

    monkeypatch.setattr(coe_data.requests, "get", fake_get)

    with pytest.raises(requests.HTTPError):
        coe_data.fetch_latest_coe_records()
