from datetime import date, datetime

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


class TimeseriesPoint(BaseModel):
    bucket_start: date
    count: int


class TimeseriesOut(BaseModel):
    granularity: str
    timezone: str
    points: list[TimeseriesPoint]
