import uuid

from pydantic import BaseModel

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.location_schema import LocationResponse
from app.util.schema import AllOptional


class _BaseLocationSearchHistory(BaseModel):
    location_id: uuid.UUID
    user_id: uuid.UUID | None = None


class LocationSearchHistoryQueryByUser(BaseModel, metaclass=AllOptional):
    name: str | None = None


class LocationSearchHistoryQuery(_BaseLocationSearchHistory, metaclass=AllOptional):
    name: str | None = None


class LocationSearchHistoryByUserResponse(ModelBaseInfo):
    location: LocationResponse


class LocationSearchHistoryResponse(_BaseLocationSearchHistory, ModelBaseInfo): ...


class EditLocationSearchHistory(_BaseLocationSearchHistory): ...


class DetailedLocationSearchHistory(LocationSearchHistoryResponse):
    location: LocationResponse


class CreateLocationSearchHistory(_BaseLocationSearchHistory): ...


class UpdateLocationSearchHistory(CreateLocationSearchHistory, metaclass=AllOptional): ...


class FindLocationSearchHistory(PaginationQuery, LocationSearchHistoryQuery, metaclass=AllOptional): ...


class FindLocationSearchHistoryByUser(PaginationQuery, LocationSearchHistoryQueryByUser, metaclass=AllOptional): ...
