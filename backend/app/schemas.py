"""
Pydantic schemas for validated application data.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CoeRecord(BaseModel):
    """
    Represent a single validated and cleaned COE bidding result.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True
    )

    month: str = Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    bidding_no: int = Field(gt=0, lt=3)
    category: Literal['A', 'B', 'C', 'D', 'E']
    quota: int = Field(ge=0)
    bids_success: int = Field(ge=0)
    bids_received: int = Field(ge=0)
    premium: int = Field(gt=0)

    # Pydantic (post) validator that runs after Pydantic has validated all the individual fields and created the CoeRecord object.
    # Do not need to call manually.
    @model_validator(mode="after")
    def validate_bid_counts(self) -> Self:
        """
        Ensure successful bids do not exceed received bids.
        """

        if self.bids_success > self.bids_received:
            raise ValueError("Successful bids cannot exceed received bids.")

        return self 


class ForecastMetrics(BaseModel):
    """
    Represent summary measurements for a set of COE forecasts.
    Summarises the quality of the forecast over a set of predictions.
    """

    forecast_count: int = Field(ge=0)
    mean_absolute_error: float = Field(ge=0)
    mean_absolute_percentage_error: float = Field(ge=0)
    directional_accuracy: float = Field(ge=0, le=100)


class CategoryEvaluationMetrics(BaseModel):
    """
    Represent the evaluation summary for one COE category.
    Makes use of previous class defined: Forecast Metrics
    """

    category: Literal['A', 'B', 'C', 'D', 'E']
    training_record_count: int = Field(gt=0)
    test_fraction: float = Field(gt=0, lt=1)
    metrics: ForecastMetrics


class ForecastMethodMetrics(BaseModel):
    """
    Represent all the metrics for each category for one forecast method.
    """

    overall_metrics: ForecastMetrics
    categories: list[CategoryEvaluationMetrics]


class BaselineMetricsResponse(BaseModel):
    """
    Represent the API response returned by endpoint containing baseline evaluation metrics.
    """

    test_fraction: float = Field(gt=0, lt=1)
    rolling_window: int = Field(ge=1)
    methods: dict[str, ForecastMethodMetrics]


class CategoryPrediction(BaseModel):
    """
    Represent the predictions of price for that specific category.
    """

    category: Literal['A', 'B', 'C', 'D', 'E']
    latest_premium: int = Field(ge=1)
    last_value_prediction: int = Field(ge=1)
    rolling_average_prediction: int = Field(ge=1)


class NextPredictionResponse(BaseModel):
    """
    Represent the aggregation of all the predictions for multiple categories.
    """

    rolling_window: int = Field(ge=1)
    predictions: list[CategoryPrediction]
