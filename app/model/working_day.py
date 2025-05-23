import datetime
import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.location import Location


class WorkingDay(BaseModel, table=True):
    day: int = Field(nullable=False, gt=0, lt=8)
    open_time: datetime.time = Field(nullable=False)
    close_time: datetime.time = Field(nullable=False)

    location_id: uuid.UUID = Field(foreign_key="location.id")
    location: "Location" = Relationship(back_populates="working_days")
