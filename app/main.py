from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.api.auth import router as auth_router
from app.api.bookings import router as bookings_router
from app.api.plans import router as plans_router
from app.api.services import router as services_router
from app.database import Base, engine
from app.models.booking import Booking  # noqa: F401
from app.models.plan import Plan, PlanType  # noqa: F401
from app.models.room import Room  # noqa: F401
from app.models.service import Service  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_plan import UserPlan  # noqa: F401


def seed_reference_data(db: Session) -> None:
    if db.query(Plan).count() == 0:
        db.add_all(
            [
                Plan(name="5-Pack", price=99.0, type=PlanType.CREDIT, total_credits=5, expiry_days=90, monthly_visit_cap=None),
                Plan(name="10-Pack", price=179.0, type=PlanType.CREDIT, total_credits=10, expiry_days=180, monthly_visit_cap=None),
                Plan(name="Monthly Unlimited", price=149.0, type=PlanType.MONTHLY, total_credits=None, expiry_days=30, monthly_visit_cap=30),
            ]
        )

    if db.query(Service).count() == 0:
        db.add_all(
            [
                Service(name="UV Tanning", description="Traditional UV tanning session.", duration_minutes=20),
                Service(name="Spray Tanning", description="Automated spray tanning session.", duration_minutes=15),
                Service(name="Teeth Whitening", description="Standalone teeth whitening treatment.", duration_minutes=45),
            ]
        )

    if db.query(Room).count() == 0:
        db.add_all([Room(name="Room 1"), Room(name="Room 2")])

    db.commit()


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        seed_reference_data(db)

    application = FastAPI(title="Tanning Salon API")
    application.include_router(auth_router)
    application.include_router(plans_router)
    application.include_router(services_router)
    application.include_router(bookings_router)

    @application.get("/")
    def read_root():
        return {"message": "Tanning Salon API"}

    return application


app = create_app()
