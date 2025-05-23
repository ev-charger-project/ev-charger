import uuid
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.amenities import Amenities
    from app.model.location import Location


class LocationAmenities(BaseModel, table=True):

    location_id: uuid.UUID = Field(foreign_key="location.id", nullable=False)
    amenities_id: uuid.UUID = Field(foreign_key="amenities.id", nullable=False)

    __table_args__ = (UniqueConstraint("location_id", "amenities_id", "deleted_at", name="uix_location_id_amenities_id"),)

    location: "Location" = Relationship(back_populates="location_amenities")
    amenities: "Amenities" = Relationship(back_populates="location_amenities")
