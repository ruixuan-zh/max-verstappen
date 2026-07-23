import pytest
from pydantic import ValidationError

from app.schemas import CategoryPrediction, NextPredictionResponse


def make_valid_prediction(**overrides: object) -> dict:
    """Return valid category prediction data with optional overrides."""

    prediction = {
        "category": "A",
        "latest_premium": 103000,
        "last_value_prediction": 103000,
        "rolling_average_prediction": 102000,
    }
    prediction.update(overrides)
    return prediction


def test_category_prediction_accepts_valid_prediction() -> None:
    prediction = CategoryPrediction.model_validate(make_valid_prediction())

    assert prediction.model_dump() == make_valid_prediction()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("category", "F"),
        ("latest_premium", 0),
        ("last_value_prediction", 0),
        ("rolling_average_prediction", 0),
    ],
)
def test_category_prediction_rejects_invalid_values(
    field: str,
    value: object,
) -> None:
    with pytest.raises(ValidationError):
        CategoryPrediction.model_validate(
            make_valid_prediction(**{field: value}),
        )


def test_next_prediction_response_validates_nested_predictions() -> None:
    response = NextPredictionResponse.model_validate(
        {
            "rolling_window": 3,
            "predictions": [make_valid_prediction()],
        }
    )

    assert response.rolling_window == 3
    assert response.predictions[0].category == "A"


def test_next_prediction_response_rejects_invalid_nested_prediction() -> None:
    with pytest.raises(ValidationError):
        NextPredictionResponse.model_validate(
            {
                "rolling_window": 3,
                "predictions": [make_valid_prediction(category="F")],
            }
        )


def test_next_prediction_response_rejects_non_positive_window() -> None:
    with pytest.raises(ValidationError):
        NextPredictionResponse.model_validate(
            {
                "rolling_window": 0,
                "predictions": [],
            }
        )
