from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.city import City


class District(BaseModel, table=True):
    name: str = Field(nullable=False)

    city_id: UUID = Field(nullable=False, foreign_key="city.id")
    city: "City" = Relationship(back_populates="districts")
