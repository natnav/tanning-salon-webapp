from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api.auth import get_current_user
from app.database import get_db
from app.models.plan import Plan, PlanType
from app.models.user import User
from app.models.user_plan import UserPlan
from app.schemas.plan import PlanOut, UserPlanOut

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db)):
    return db.query(Plan).order_by(Plan.id).all()


@router.post("/purchase/{plan_id}", response_model=UserPlanOut, status_code=status.HTTP_201_CREATED)
def purchase_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    now = datetime.now(UTC).replace(tzinfo=None)
    expiry_date = now + timedelta(days=plan.expiry_days or 30)
    remaining_credits = plan.total_credits if plan.type == PlanType.CREDIT else None

    user_plan = UserPlan(
        user_id=current_user.id,
        plan_id=plan.id,
        remaining_credits=remaining_credits,
        visits_used=0,
        start_date=now,
        expiry_date=expiry_date,
        is_active=True,
    )
    db.add(user_plan)
    db.commit()
    db.refresh(user_plan)
    return user_plan

@router.get("/hello")
def hello(db: Session = Depends(get_db)):
    # get * from session
    return db.query(Plan).all()
