from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.constant.enum.power_output import ChargingSpeed
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional


class _BasePowerOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    output_value: float = Field(gt=0)
    charging_speed: ChargingSpeed | None = Field(
        description="Charging speed of the power output",
        default=None,
    )
    voltage: int = Field(gt=0)
    amperage: int = Field(gt=0)


class CreatePowerOutput(_BasePowerOutput):
    description: Optional[str] = Field(max_length=1000, default=None)


class EditPowerOutput(_BasePowerOutput):
    description: Optional[str] = Field(max_length=1000, default=None)


class PowerOutputResponse(ModelBaseInfo, _BasePowerOutput):
    description: Optional[str] = Field(max_length=1000, default=None)


class DetailedPowerOutput(PowerOutputResponse):
    pass


class FindPowerOutput(PaginationQuery, _BasePowerOutput, metaclass=AllOptional): ...


class UpsertPowerOutput(_BasePowerOutput):
    description: Optional[str] = None
