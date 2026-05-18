from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.auth import get_current_user
from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.plan import PlanType
from app.models.room import Room
from app.models.service import Service
from app.models.user import User
from app.models.user_plan import UserPlan
from app.schemas.booking import BookingCreate, BookingOut, WalkInCreate

router = APIRouter(prefix="/bookings", tags=["bookings"])


def check_capacity(db: Session, start_time: datetime, end_time: datetime) -> bool:
    overlapping = db.query(Booking).filter(
        Booking.start_time < end_time,
        Booking.end_time > start_time,
        Booking.status == BookingStatus.SCHEDULED,
    ).count()
    room_count = db.query(func.count(Room.id)).scalar() or 0
    return overlapping < room_count


def get_active_user_plan(db: Session, user_id: int, booking_time: datetime) -> UserPlan | None:
    user_plans = db.query(UserPlan).options(joinedload(UserPlan.plan)).filter(
        UserPlan.user_id == user_id,
        UserPlan.is_active.is_(True),
        UserPlan.start_date <= booking_time,
        UserPlan.expiry_date >= booking_time,
    ).order_by(UserPlan.id).all()

    for user_plan in user_plans:
        if user_plan.plan.type == PlanType.CREDIT and (user_plan.remaining_credits or 0) > 0:
            return user_plan
        if user_plan.plan.type == PlanType.MONTHLY and user_plan.visits_used < (user_plan.plan.monthly_visit_cap or 0):
            return user_plan
    return None


def apply_plan_usage(user_plan: UserPlan) -> None:
    if user_plan.plan.type == PlanType.CREDIT:
        if not user_plan.remaining_credits:
            raise HTTPException(status_code=400, detail="Insufficient credits")
        user_plan.remaining_credits -= 1
    else:
        if user_plan.visits_used >= (user_plan.plan.monthly_visit_cap or 0):
            raise HTTPException(status_code=400, detail="Monthly visit cap reached")
        user_plan.visits_used += 1


def create_booking_record(
    db: Session,
    *,
    user: User,
    service_id: int,
    start_time: datetime,
    is_walk_in: bool,
    bypass_plan_check: bool,
) -> Booking:
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    normalized_start_time = start_time.astimezone(UTC).replace(tzinfo=None) if start_time.tzinfo else start_time
    end_time = normalized_start_time + timedelta(minutes=service.duration_minutes)
    if not check_capacity(db, normalized_start_time, end_time):
        raise HTTPException(status_code=400, detail="No room capacity available")

    if not bypass_plan_check:
        user_plan = get_active_user_plan(db, user.id, normalized_start_time)
        if user_plan is None:
            raise HTTPException(status_code=400, detail="No active plan available")
        apply_plan_usage(user_plan)

    booking = Booking(
        user_id=user.id,
        service_id=service.id,
        start_time=normalized_start_time,
        end_time=end_time,
        status=BookingStatus.SCHEDULED,
        is_walk_in=is_walk_in,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_booking_record(
        db,
        user=current_user,
        service_id=booking.service_id,
        start_time=booking.start_time,
        is_walk_in=False,
        bypass_plan_check=False,
    )


@router.get("/me", response_model=list[BookingOut])
def list_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(Booking).filter(Booking.user_id == current_user.id).order_by(Booking.start_time).all()


@router.post("/walk-in", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
def create_walk_in(
    booking: WalkInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    if booking.user_id is None:
        raise HTTPException(status_code=400, detail="user_id is required for walk-ins")

    target_user = db.get(User, booking.user_id)
    if target_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return create_booking_record(
        db,
        user=target_user,
        service_id=booking.service_id,
        start_time=booking.start_time,
        is_walk_in=True,
        bypass_plan_check=True,
    )
