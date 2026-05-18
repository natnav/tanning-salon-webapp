from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    service_id: int
    start_time: datetime


class WalkInCreate(BaseModel):
    service_id: int
    start_time: datetime
    user_id: int | None = None


class BookingOut(BaseModel):
    id: int
    user_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    is_walk_in: bool

    model_config = ConfigDict(from_attributes=True)
