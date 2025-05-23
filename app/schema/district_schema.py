from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional

if TYPE_CHECKING:
    from app.schema.city_schema import CityResponse


class BaseDistrict(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str


class DistrictResponse(BaseDistrict, ModelBaseInfo): ...


class DetailedDistrictResponse(DistrictResponse):
    city: "CityResponse"


class CreateEditDistrict(BaseDistrict):
    model_config = ConfigDict(from_attributes=True)

    city_id: UUID


# CRUD
class FindDistrict(PaginationQuery, metaclass=AllOptional):
    name: str | None = None


class UpsertDistrict(CreateEditDistrict, metaclass=AllOptional): ...
