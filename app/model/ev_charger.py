from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship

from app.constant.enum.availability import AvailabilityEnum
from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model import EVChargerPort, Location


class EVCharger(BaseModel, table=True):
    location_id: UUID = Field(nullable=False, foreign_key="location.id")
    location: "Location" = Relationship(back_populates="ev_chargers")
    station_name: str | None = Field(nullable=True)
    cpo_id: str | None = Field(nullable=True, max_length=255)
    cpo_evse_emi3_id: str | None = Field(nullable=True, max_length=255)
    availability: AvailabilityEnum = Field(nullable=False)
    last_updated: date | None = Field(nullable=False)
    installation_date: date | None = Field(nullable=True)
    last_maintenance_date: date | None = Field(nullable=True)

    ev_charger_ports: list["EVChargerPort"] = Relationship(back_populates="ev_charger")
