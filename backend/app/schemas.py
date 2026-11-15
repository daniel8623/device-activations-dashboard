from datetime import datetime

from pydantic import BaseModel, Field


class ActivationIn(BaseModel):
    device_id: str = Field(min_length=1, max_length=128)
    activated_at: datetime | None = None


class ActivationOut(BaseModel):
    device_id: str
    activated_at: datetime
    is_new: bool

class SummaryOut(BaseModel):
    today: int
    week: int
    month: int
    year: int
    timezone: str