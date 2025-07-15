from __future__ import annotations

import uuid
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.constant.enum.availability import AvailabilityEnum
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional


class _BaseEVCharger(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    here_id: str
    station_name: str | None
    cpo_id: str | None
    cpo_evse_emi3_id: str | None
    availability: AvailabilityEnum
    last_updated: datetime
    installation_date: date | None
    last_maintenance_date: date | None
    location_id: UUID


class CreatePort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    here_id: str
    power_plug_type_id: uuid.UUID
    power_output_id: uuid.UUID


class CreateEVCharger(_BaseEVCharger):
    model_config = ConfigDict(from_attributes=True)
    ev_charger_ports: list[CreatePort] | None = None


class UpsertPort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    power_plug_type_id: uuid.UUID | None
    power_output_id: uuid.UUID | None
    id: uuid.UUID | None = None


class UpdateEVCharger(_BaseEVCharger):
    model_config = ConfigDict(from_attributes=True)
    ev_charger_ports: list[UpsertPort] | None = None


class EVChargerResponse(_BaseEVCharger, ModelBaseInfo): ...


class LocationNameResponse(BaseModel):
    location_name: str | None = None


class EVChargerResponseWithLocation(EVChargerResponse, metaclass=AllOptional):
    location: LocationNameResponse


class EVChargerResponseWithEVChargerPort(EVChargerResponse, metaclass=AllOptional):
    ev_charger_ports: list[DetailedEVChargerPortResponseWithoutEVCharger]


class DetailedEVCharger(EVChargerResponse, metaclass=AllOptional):
    ev_charger_ports: list[DetailedEVChargerPortResponse]
    location: LocationResponse


class FindEVCharger(PaginationQuery, _BaseEVCharger, metaclass=AllOptional): ...


from app.schema.ev_charger_port_schema import (  # noqa: E402
    DetailedEVChargerPortResponse,
    DetailedEVChargerPortResponseWithoutEVCharger,
)
from app.schema.location_schema import LocationResponse  # noqa: E402
