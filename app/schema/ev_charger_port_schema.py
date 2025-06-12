import uuid

from pydantic import BaseModel, ConfigDict

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.ev_charger_schema import EVChargerResponse
from app.schema.power_output_schema import PowerOutputResponse
from app.schema.power_plug_type_schema import PowerPlugTypeResponse
from app.util.schema import AllOptional


class _BaseEVChargerPort(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    here_id: str
    power_plug_type_id: uuid.UUID
    power_output_id: uuid.UUID
    ev_charger_id: uuid.UUID


class EVChargerPortResponse(_BaseEVChargerPort, ModelBaseInfo): ...


class DetailedEVChargerPortResponseWithoutEVCharger(EVChargerPortResponse):
    power_plug_type: PowerPlugTypeResponse
    power_output: PowerOutputResponse


class DetailedEVChargerPortResponse(EVChargerPortResponse):
    power_plug_type: PowerPlugTypeResponse
    power_output: PowerOutputResponse
    ev_charger: EVChargerResponse


class CreateEVChargerPort(_BaseEVChargerPort): ...


class UpdateEVChargerPort(CreateEVChargerPort, metaclass=AllOptional): ...


class FindEVChargerPort(PaginationQuery, _BaseEVChargerPort, metaclass=AllOptional): ...
