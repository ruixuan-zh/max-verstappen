"""
Chronological evaluation for the application's simple forecast baselines.

Each target record is predicted using only records that occurred before it.
This mirrors how a forecast would be produced in normal use and prevents
future information from leaking into an earlier prediction.
"""

from collections.abc import Callable
from functools import partial

from app.forecast import last_value_forecast, rolling_average_forecast


ForecastFunction = Callable[[list[dict], str], int]


def _records_for_category(records: list[dict], category: str) -> list[dict]:
    category_name = category.replace("Category ", "").strip().upper()
    category_records = [
        record
        for record in records
        if record["category"].strip().upper() == category_name
    ]

    return sorted(
        category_records,
        key=lambda record: (record["month"], record["bidding_no"]),
    )


def _direction(current_premium: int, previous_premium: int) -> str:
    if current_premium > previous_premium:
        return "up"
    if current_premium < previous_premium:
        return "down"
    return "unchanged"


def _summarise_results(results: list[dict]) -> dict:
    if not results:
        raise ValueError("At least one forecast result is required.")

    result_count = len(results)
    mean_absolute_error = sum(
        result["absolute_error"] for result in results
    ) / result_count
    mean_absolute_percentage_error = sum(
        result["absolute_percentage_error"] for result in results
    ) / result_count
    correct_directions = sum(
        result["direction_correct"] for result in results
    )

    return {
        "forecast_count": result_count,
        "mean_absolute_error": round(mean_absolute_error, 2),
        "mean_absolute_percentage_error": round(
            mean_absolute_percentage_error,
            2,
        ),
        "directional_accuracy": round(
            correct_directions / result_count * 100,
            2,
        ),
    }


def evaluate_forecast(
    records: list[dict],
    category: str,
    forecast_function: ForecastFunction,
    test_fraction: float = 0.2,
) -> dict:
    """
    Evaluate one forecasting function on the final chronological data portion.

    For every record in the test portion, the forecasting function receives
    only earlier records. The history then expands by one record before the
    following prediction, which is a walk-forward evaluation.
    """

    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1.")

    category_records = _records_for_category(records, category)
    if len(category_records) < 2:
        raise ValueError(
            f"At least two COE records are required for category {category}."
        )

    split_index = max(1, int(len(category_records) * (1 - test_fraction)))
    results = []

    for target_index in range(split_index, len(category_records)):
        history = category_records[:target_index]
        target = category_records[target_index]
        previous_premium = history[-1]["premium"]
        predicted_premium = forecast_function(history, category)
        actual_premium = target["premium"]
        absolute_error = abs(predicted_premium - actual_premium)
        predicted_direction = _direction(predicted_premium, previous_premium)
        actual_direction = _direction(actual_premium, previous_premium)

        results.append(
            {
                "target_month": target["month"],
                "target_bidding_no": target["bidding_no"],
                "previous_premium": previous_premium,
                "predicted_premium": predicted_premium,
                "actual_premium": actual_premium,
                "absolute_error": absolute_error,
                "absolute_percentage_error": (
                    absolute_error / actual_premium * 100
                ),
                "predicted_direction": predicted_direction,
                "actual_direction": actual_direction,
                "direction_correct": predicted_direction == actual_direction,
            }
        )

    return {
        "category": category.replace("Category ", "").strip().upper(),
        "training_record_count": split_index,
        "test_fraction": test_fraction,
        "metrics": _summarise_results(results),
        "results": results,
    }


def evaluate_baselines(
    records: list[dict],
    categories: tuple[str, ...] = ("A", "B", "C", "D", "E"),
    test_fraction: float = 0.2,
    rolling_window: int = 3,
) -> dict:
    """Evaluate the last-value and rolling-average baseline forecasts."""

    if rolling_window <= 0:
        raise ValueError("rolling_window must be greater than 0.")

    forecast_methods: dict[str, ForecastFunction] = {
        "last_value": last_value_forecast,
        f"rolling_average_{rolling_window}": partial(
            rolling_average_forecast,
            window=rolling_window,
        ),
    }
    methods = {}

    for method_name, forecast_function in forecast_methods.items():
        category_evaluations = [
            evaluate_forecast(
                records,
                category,
                forecast_function,
                test_fraction,
            )
            for category in categories
        ]
        all_results = [
            result
            for evaluation in category_evaluations
            for result in evaluation["results"]
        ]
        methods[method_name] = {
            "overall_metrics": _summarise_results(all_results),
            "categories": category_evaluations,
        }

    return {
        "test_fraction": test_fraction,
        "rolling_window": rolling_window,
        "methods": methods,
    }
