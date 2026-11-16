from datetime import date, datetime

from app.models import Device
from app.stats import LOCAL_TZ, add_months, compute_summary, compute_timeseries, week_start

# A fixed "now" for every test: Monday, Nov 16 2026, 10:00 Israel time (08:00 UTC).
NOW = datetime(2026, 11, 16, 10, 0, tzinfo=LOCAL_TZ)


def add_device(db, device_id: str, activated_at_utc: datetime) -> None:
    db.add(Device(device_id=device_id, activated_at=activated_at_utc))
    db.commit()


def test_week_starts_on_sunday():
    assert week_start(date(2026, 11, 16)) == date(2026, 11, 15)  # Monday -> the Sunday before
    assert week_start(date(2026, 11, 15)) == date(2026, 11, 15)  # Sunday -> itself
    assert week_start(date(2026, 11, 21)) == date(2026, 11, 15)  # Saturday -> the Sunday before


def test_add_months_crosses_year_boundary():
    assert add_months(date(2026, 1, 1), -1) == date(2025, 12, 1)
    assert add_months(date(2026, 11, 1), -11) == date(2025, 12, 1)


def test_summary_uses_calendar_periods(db_session):
    add_device(db_session, "today", datetime(2026, 11, 16, 6, 0))       # Mon 08:00 Israel
    add_device(db_session, "sunday", datetime(2026, 11, 15, 6, 0))      # this week, not today
    add_device(db_session, "this-month", datetime(2026, 11, 2, 6, 0))   # this month, not this week
    add_device(db_session, "this-year", datetime(2026, 3, 1, 6, 0))     # this year, not this month
    add_device(db_session, "last-year", datetime(2025, 6, 1, 6, 0))     # not counted at all

    summary = compute_summary(db_session, now=NOW)

    assert summary == {"today": 1, "week": 2, "month": 3, "year": 4}


def test_late_night_utc_counts_in_next_israel_day(db_session):
    # 23:30 UTC on Dec 31 is already 01:30 on Jan 1 in Israel.
    add_device(db_session, "new-year", datetime(2025, 12, 31, 23, 30))

    summary = compute_summary(db_session, now=datetime(2026, 1, 1, 12, 0, tzinfo=LOCAL_TZ))

    assert summary["today"] == 1
    assert summary["year"] == 1


def test_timeseries_fills_empty_periods_with_zero(db_session):
    add_device(db_session, "device-1", datetime(2026, 11, 14, 10, 0))

    points = compute_timeseries(db_session, now=NOW, granularity="day", buckets=3)

    assert [p["bucket_start"] for p in points] == [date(2026, 11, 14), date(2026, 11, 15), date(2026, 11, 16)]
    assert [p["count"] for p in points] == [1, 0, 0]


def test_activation_at_midnight_is_counted_once(db_session):
    # Midnight on Nov 15 in Israel (UTC+2 in winter) is 22:00 UTC on Nov 14.
    add_device(db_session, "midnight", datetime(2026, 11, 14, 22, 0))

    points = compute_timeseries(db_session, now=NOW, granularity="day", buckets=3)

    assert [p["count"] for p in points] == [0, 1, 0]


def test_yearly_buckets(db_session):
    add_device(db_session, "last-year", datetime(2025, 6, 1, 6, 0))
    add_device(db_session, "this-year", datetime(2026, 3, 1, 6, 0))

    points = compute_timeseries(db_session, now=NOW, granularity="year", buckets=3)

    assert [p["bucket_start"] for p in points] == [date(2024, 1, 1), date(2025, 1, 1), date(2026, 1, 1)]
    assert [p["count"] for p in points] == [0, 1, 1]
