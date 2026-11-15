from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Device, utc_now
from .schemas import ActivationIn, ActivationOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Device Activations API")


def to_utc_naive(dt: datetime) -> datetime:
    """Convert any datetime to UTC without tzinfo. A naive value is assumed to already be UTC."""
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


@app.post("/api/activations", response_model=ActivationOut, status_code=status.HTTP_201_CREATED)
def register_activation(payload: ActivationIn, response: Response, db: Session = Depends(get_db)):
    existing = db.get(Device, payload.device_id)
    if existing:
        response.status_code = status.HTTP_200_OK
        return ActivationOut(device_id=existing.device_id, activated_at=existing.activated_at, is_new=False)

    activated_at = to_utc_naive(payload.activated_at) if payload.activated_at else utc_now()
    device = Device(device_id=payload.device_id, activated_at=activated_at)
    db.add(device)

    try:
        db.commit()
    except IntegrityError:
        # Two pings from the same device arrived at the same moment: the other one won.
        db.rollback()
        existing = db.get(Device, payload.device_id)
        response.status_code = status.HTTP_200_OK
        return ActivationOut(device_id=existing.device_id, activated_at=existing.activated_at, is_new=False)

    return ActivationOut(device_id=device.device_id, activated_at=device.activated_at, is_new=True)