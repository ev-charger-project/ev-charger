import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.location import Location


class LocationSearchHistory(BaseModel, table=True):
    location_id: uuid.UUID = Field(foreign_key="location.id", nullable=False)
    user_id: uuid.UUID = Field(index=True, nullable=False)

    __table_args__ = (UniqueConstraint("location_id", "user_id", "deleted_at", name="uix_location_id_user_id_search_history"),)

    location: "Location" = Relationship(back_populates="location_search_histories")
