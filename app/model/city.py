from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.constant.enum.location import Country
from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.district import District


class City(BaseModel, table=True):
    name: str = Field(nullable=False)
    country: Country = Field(nullable=False)

    districts: list["District"] = Relationship(back_populates="city")
