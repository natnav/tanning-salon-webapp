from pydantic import BaseModel, ConfigDict


class ServiceOut(BaseModel):
    id: int
    name: str
    description: str | None
    duration_minutes: int

    model_config = ConfigDict(from_attributes=True)
