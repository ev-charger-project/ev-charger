from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship

from app.constant.enum.location import Country
from app.constant.enum.location_access import LocationAccess
from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.ev_charger import EVCharger
    from app.model.location_amenities import LocationAmenities
    from app.model.location_search_history import LocationSearchHistory
    from app.model.user_favorite import UserFavorite
    from app.model.working_day import WorkingDay


class Location(BaseModel, table=True):
    here_id: str = Field(nullable=False, max_length=255, unique=True)
    external_id: str | None = Field(nullable=False, max_length=255)
    location_name: str = Field(nullable=False, max_length=100)
    street: str = Field(nullable=False, max_length=255)
    house_number: str | None = Field(default=None, nullable=True, max_length=20)
    district: str | None = Field(default=None, nullable=True, max_length=100)
    city: str = Field(nullable=False, max_length=100)
    state: str | None = Field(default=None, nullable=True, max_length=100)
    county: str | None = Field(default=None, max_length=100, nullable=True)  # NEW
    country: Country = Field(nullable=False)
    postal_code: str | None = Field(default=None, nullable=True, max_length=20)
    latitude: float = Field(nullable=False)
    longitude: float = Field(nullable=False)
    phone_number: str | None = Field(nullable=True, default=None)
    website_url: str | None = Field(default=None, nullable=True, max_length=1000)
    description: str | None = Field(default=None, nullable=True, max_length=1000)
    image_url: str | None = Field(default=None, nullable=True, max_length=1000)
    pricing: str | None = Field(nullable=True, max_length=100, default=None)
    parking_level: str | None = Field(nullable=True, max_length=50)

    total_charging_ports: int | None = Field(default=None, nullable=True)
    access: LocationAccess = Field(nullable=True, default=None)
    payment_methods: list | None = Field(default=None, sa_column=Column(JSON))

    ev_chargers: list["EVCharger"] = Relationship(back_populates="location")
    working_days: list["WorkingDay"] = Relationship(back_populates="location")
    user_favorite: list["UserFavorite"] = Relationship(back_populates="location")
    location_amenities: list["LocationAmenities"] = Relationship(
        back_populates="location"
    )
    location_search_histories: list["LocationSearchHistory"] = Relationship(
        back_populates="location"
    )
