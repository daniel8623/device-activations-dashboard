"""Fill the database with fake device activations for local development.

Usage, from the backend folder:
    python -m app.seed --reset
    python -m app.seed --count 5000 --days 365
"""
import argparse
import random
import uuid
from datetime import timedelta

from sqlalchemy import delete

from .database import Base, SessionLocal, engine
from .models import Device, utc_now


def generate_activations(count: int, days: int, rng: random.Random) -> list[Device]:
    now = utc_now()
    # Recent days get more weight (up to x2), so the chart shows growth over time.
    weights = [1 + (days - offset) / days for offset in range(days)]
    offsets = rng.choices(range(days), weights=weights, k=count)

    devices = []
    for offset in offsets:
        activated_at = now - timedelta(days=offset, seconds=rng.randint(0, 86_399))
        devices.append(Device(device_id=f"seed-{uuid.uuid4()}", activated_at=activated_at))
    return devices


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database with fake device activations.")
    parser.add_argument("--count", type=int, default=3000, help="How many activations to create")
    parser.add_argument("--days", type=int, default=400, help="How many days back to spread them")
    parser.add_argument("--reset", action="store_true", help="Delete all existing devices first")
    parser.add_argument("--seed", type=int, default=42, help="Random seed, for repeatable data")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    rng = random.Random(args.seed)

    with SessionLocal() as db:
        if args.reset:
            deleted = db.execute(delete(Device)).rowcount
            print(f"Deleted {deleted} existing devices")
        db.add_all(generate_activations(args.count, args.days, rng))
        db.commit()

    print(f"Inserted {args.count} activations spread over the last {args.days} days")


if __name__ == "__main__":
    main()