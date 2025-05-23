from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.constant.enum.power_plug_type import PowerModel
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional


class _BasePowerPlugType(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    supplier_name: str = Field(description="Name of the supplier")
    power_model: PowerModel
    plug_type: str = Field(description="Type of power plug")
    plug_type_id: str = Field(description="ID of the power plug type")
    fixed_plug: bool = Field(
        description="Indicates if the plug is fixed", default=False
    )
    plug_image_url: Optional[str] = Field(
        description="URL to the image of the power plug", default=None
    )
    power_plug_region: str | None = None


class CreatePowerPlugType(_BasePowerPlugType):
    additional_note: Optional[str] = Field(
        max_length=1000,
        description="Additional notes about the power plug type",
        default=None,
    )


class EditPowerPlugType(_BasePowerPlugType):
    additional_note: Optional[str] = Field(
        max_length=1000,
        description="Additional notes about the power plug type",
        default=None,
    )


class PowerPlugTypeResponse(ModelBaseInfo, _BasePowerPlugType):
    additional_note: Optional[str] = Field(
        max_length=1000,
        description="Additional notes about the power plug type",
        default=None,
    )


class DetailedPowerPlugType(PowerPlugTypeResponse):
    pass


class FindPowerPlugType(PaginationQuery, _BasePowerPlugType, metaclass=AllOptional): ...


class UpsertPowerPlugType(_BasePowerPlugType): ...
