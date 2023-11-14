from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DonationBase(BaseModel):
    comment: Optional[str]
    full_amount: int = Field(..., ge=1)


class DonationShortDB(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationShortDB, DonationBase):
    user_id: int
    full_amount: int = Field(..., ge=1)
    invested_amount: int = Field(0, ge=0)
    fully_invested: bool = Field(False)


class DonationCreate(DonationBase):
    pass
