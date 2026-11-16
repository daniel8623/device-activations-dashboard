from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Device

LOCAL_TZ = ZoneInfo("Asia/Jerusalem")


def local_midnight_to_utc(day: date) -> datetime:
    """Midnight of a local (Israel) calendar day, as naive UTC to compare with the database."""
    local_midnight = datetime.combine(day, time.min, tzinfo=LOCAL_TZ)
    return local_midnight.astimezone(timezone.utc).replace(tzinfo=None)


def period_starts(now_local: datetime) -> dict[str, datetime]:
    """Start of today, this week (from Sunday), this month and this year, in naive UTC."""
    today = now_local.date()
    days_since_sunday = (today.weekday() + 1) % 7  # Python: Monday=0 ... Sunday=6
    starts = {
        "today": today,
        "week": today - timedelta(days=days_since_sunday),
        "month": today.replace(day=1),
        "year": today.replace(month=1, day=1),
    }
    return {name: local_midnight_to_utc(day) for name, day in starts.items()}


def count_between(db: Session, start_utc: datetime, end_utc: datetime) -> int:
    stmt = (
        select(func.count())
        .select_from(Device)
        .where(Device.activated_at >= start_utc, Device.activated_at < end_utc)
    )
    return db.scalar(stmt) or 0


def compute_summary(db: Session, now: datetime) -> dict[str, int]:
    now_local = now.astimezone(LOCAL_TZ)
    now_utc = now.astimezone(timezone.utc).replace(tzinfo=None)
    starts = period_starts(now_local)
    return {name: count_between(db, start, now_utc) for name, start in starts.items()}

def week_start(day: date) -> date:
    """The Sunday that starts the week of the given day."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def add_months(day: date, months: int) -> date:
    """First day of the month, shifted by a number of months (negative goes back)."""
    month_index = day.year * 12 + (day.month - 1) + months
    return date(month_index // 12, month_index % 12 + 1, 1)


def bucket_starts(today: date, granularity: str, buckets: int) -> list[date]:
    """Start dates of the last `buckets` periods, oldest first. The last one contains today."""
    if granularity == "day":
        return [today - timedelta(days=i) for i in range(buckets - 1, -1, -1)]
    if granularity == "week":
        current = week_start(today)
        return [current - timedelta(weeks=i) for i in range(buckets - 1, -1, -1)]
    if granularity == "month":
        current = today.replace(day=1)
        return [add_months(current, -i) for i in range(buckets - 1, -1, -1)]
    raise ValueError(f"Unknown granularity: {granularity}")


def compute_timeseries(db: Session, now: datetime, granularity: str, buckets: int) -> list[dict]:
    now_local = now.astimezone(LOCAL_TZ)
    now_utc = now.astimezone(timezone.utc).replace(tzinfo=None)

    starts = bucket_starts(now_local.date(), granularity, buckets)
    boundaries = [local_midnight_to_utc(day) for day in starts] + [now_utc]

    return [
        {"bucket_start": day, "count": count_between(db, boundaries[i], boundaries[i + 1])}
        for i, day in enumerate(starts)
    ]