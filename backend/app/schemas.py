"""
Pydantic schemas for validated application data.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CoeRecord(BaseModel):
    """
    Represent one validated, cleaned COE bidding result.
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

    # Pydantic validator that runs after Pydantic has validated all the individual fields and created the CoeRecord object.
    # Do not need to call manually.
    @model_validator(mode="after")
    def validate_bid_counts(self) -> Self:
        """
        Ensure successful bids do not exceed received bids.
        """

        if self.bids_success > self.bids_received:
            raise ValueError("Successful bids cannot exceed received bids.")

        return self 