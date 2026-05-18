from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.plan import PlanType


class PlanOut(BaseModel):
    id: int
    name: str
    price: float
    type: PlanType
    total_credits: int | None
    expiry_days: int | None
    monthly_visit_cap: int | None

    model_config = ConfigDict(from_attributes=True)


class UserPlanOut(BaseModel):
    id: int
    user_id: int
    plan_id: int
    remaining_credits: int | None
    visits_used: int
    start_date: datetime
    expiry_date: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
