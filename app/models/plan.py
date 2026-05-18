import enum

from sqlalchemy import Enum, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlanType(str, enum.Enum):
    CREDIT = "CREDIT"
    MONTHLY = "MONTHLY"


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    type: Mapped[PlanType] = mapped_column(Enum(PlanType), nullable=False)
    total_credits: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expiry_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_visit_cap: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user_plans = relationship("UserPlan", back_populates="plan")
