from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.location_amenities import LocationAmenities


class Amenities(BaseModel, table=True):

    amenities_types: str = Field(nullable=False)
    image_url: str = Field(nullable=True)

    __table_args__ = (UniqueConstraint("amenities_types", "deleted_at", name="uix_amenities_types"),)

    location_amenities: list["LocationAmenities"] = Relationship(back_populates="amenities")
