from pydantic import BaseModel, ConfigDict

from app.constant.enum.location import Country
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.district_schema import BaseDistrict, DistrictResponse
from app.util.schema import AllOptional


class _BaseCity(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    country: Country


class CityResponse(_BaseCity, ModelBaseInfo): ...


class DetailedCityResponse(CityResponse):
    districts: list[DistrictResponse]


class CreateEditCity(_BaseCity):
    model_config = ConfigDict(from_attributes=True)

    districts: list[BaseDistrict]


# CRUD
class FindCity(PaginationQuery, metaclass=AllOptional):
    name: str | None = None


class UpsertCity(CreateEditCity, metaclass=AllOptional): ...
