import pytest

from app.evaluation import evaluate_baselines, evaluate_forecast


def make_record(
    *,
    month: str,
    bidding_no: int,
    category: str = "A",
    premium: int,
) -> dict:
    """Return one cleaned COE record for evaluation tests."""

    return {
        "month": month,
        "bidding_no": bidding_no,
        "category": category,
        "quota": 1000,
        "bids_success": 1000,
        "bids_received": 1200,
        "premium": premium,
    }


def make_category_records(category: str, base_premium: int) -> list[dict]:
    """Return four chronological records for one COE category."""

    return [
        make_record(
            month="2026-04",
            bidding_no=1,
            category=category,
            premium=base_premium,
        ),
        make_record(
            month="2026-04",
            bidding_no=2,
            category=category,
            premium=base_premium + 10,
        ),
        make_record(
            month="2026-05",
            bidding_no=1,
            category=category,
            premium=base_premium + 20,
        ),
        make_record(
            month="2026-05",
            bidding_no=2,
            category=category,
            premium=base_premium + 30,
        ),
    ]


def test_evaluate_forecast_sorts_records_and_never_uses_target_as_history() -> None:
    records = [
        make_record(month="2026-05", bidding_no=2, premium=130),
        make_record(month="2026-04", bidding_no=1, premium=100),
        make_record(month="2026-05", bidding_no=1, premium=120),
        make_record(month="2026-04", bidding_no=2, premium=110),
        make_record(
            month="2026-05",
            bidding_no=2,
            category="B",
            premium=999,
        ),
    ]
    received_histories = []

    def recording_forecast(history: list[dict], category: str) -> int:
        assert category == "Category A"
        received_histories.append(history.copy())
        return history[-1]["premium"]

    evaluation = evaluate_forecast(
        records,
        "Category A",
        recording_forecast,
        test_fraction=0.5,
    )

    assert [
        [(record["month"], record["bidding_no"]) for record in history]
        for history in received_histories
    ] == [
        [("2026-04", 1), ("2026-04", 2)],
        [("2026-04", 1), ("2026-04", 2), ("2026-05", 1)],
    ]
    assert [
        (result["target_month"], result["target_bidding_no"])
        for result in evaluation["results"]
    ] == [
        ("2026-05", 1),
        ("2026-05", 2),
    ]


def test_evaluate_forecast_calculates_errors_and_directions() -> None:
    records = [
        make_record(month="2026-03", bidding_no=1, premium=80),
        make_record(month="2026-03", bidding_no=2, premium=90),
        make_record(month="2026-04", bidding_no=1, premium=100),
        make_record(month="2026-04", bidding_no=2, premium=120),
        make_record(month="2026-05", bidding_no=1, premium=110),
        make_record(month="2026-05", bidding_no=2, premium=110),
    ]
    predictions_by_history_length = {
        3: 110,
        4: 100,
        5: 110,
    }

    def controlled_forecast(history: list[dict], category: str) -> int:
        assert category == "A"
        return predictions_by_history_length[len(history)]

    evaluation = evaluate_forecast(
        records,
        "A",
        controlled_forecast,
        test_fraction=0.5,
    )

    assert evaluation["category"] == "A"
    assert evaluation["training_record_count"] == 3
    assert evaluation["test_fraction"] == 0.5
    assert evaluation["metrics"] == {
        "forecast_count": 3,
        "mean_absolute_error": 6.67,
        "mean_absolute_percentage_error": 5.81,
        "directional_accuracy": 100.0,
    }
    assert [
        (
            result["predicted_direction"],
            result["actual_direction"],
            result["direction_correct"],
        )
        for result in evaluation["results"]
    ] == [
        ("up", "up", True),
        ("down", "down", True),
        ("unchanged", "unchanged", True),
    ]


@pytest.mark.parametrize("test_fraction", [-0.1, 0, 1, 1.1])
def test_evaluate_forecast_rejects_invalid_test_fraction(
    test_fraction: float,
) -> None:
    records = make_category_records("A", 100)

    with pytest.raises(
        ValueError,
        match="test_fraction must be between 0 and 1",
    ):
        evaluate_forecast(
            records,
            "A",
            lambda history, category: history[-1]["premium"],
            test_fraction=test_fraction,
        )


@pytest.mark.parametrize(
    "records",
    [
        [],
        [make_record(month="2026-04", bidding_no=1, premium=100)],
    ],
)
def test_evaluate_forecast_requires_at_least_two_category_records(
    records: list[dict],
) -> None:
    with pytest.raises(
        ValueError,
        match="At least two COE records are required for category A",
    ):
        evaluate_forecast(
            records,
            "A",
            lambda history, category: history[-1]["premium"],
        )


def test_evaluate_baselines_aggregates_methods_and_categories() -> None:
    categories = ("A", "B", "C", "D", "E")
    records = [
        record
        for category_index, category in enumerate(categories)
        for record in make_category_records(
            category,
            base_premium=100 + category_index * 100,
        )
    ]

    evaluation = evaluate_baselines(
        records,
        categories=categories,
        test_fraction=0.5,
        rolling_window=2,
    )

    assert evaluation["test_fraction"] == 0.5
    assert evaluation["rolling_window"] == 2
    assert set(evaluation["methods"]) == {
        "last_value",
        "rolling_average_2",
    }

    assert evaluation["methods"]["last_value"]["overall_metrics"] == {
        "forecast_count": 10,
        "mean_absolute_error": 10.0,
        "mean_absolute_percentage_error": pytest.approx(3.96, abs=0.01),
        "directional_accuracy": 0.0,
    }
    assert evaluation["methods"]["rolling_average_2"]["overall_metrics"] == {
        "forecast_count": 10,
        "mean_absolute_error": 15.0,
        "mean_absolute_percentage_error": pytest.approx(5.94, abs=0.01),
        "directional_accuracy": 0.0,
    }

    for method in evaluation["methods"].values():
        assert [
            category_evaluation["category"]
            for category_evaluation in method["categories"]
        ] == list(categories)
        assert all(
            category_evaluation["training_record_count"] == 2
            for category_evaluation in method["categories"]
        )


@pytest.mark.parametrize("rolling_window", [0, -1])
def test_evaluate_baselines_rejects_non_positive_rolling_window(
    rolling_window: int,
) -> None:
    records = make_category_records("A", 100)

    with pytest.raises(
        ValueError,
        match="rolling_window must be greater than 0",
    ):
        evaluate_baselines(
            records,
            categories=("A",),
            rolling_window=rolling_window,
        )
