from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel, Extra


class CharityProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    full_amount: int = Field(..., ge=1)


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1)
    full_amount: Optional[int] = Field(None, ge=1)

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectBase):
    id: int
    create_date: datetime
    invested_amount: int = Field(0, ge=0)
    fully_invested: bool = Field(False)
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
