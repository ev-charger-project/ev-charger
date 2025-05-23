import uuid

from pydantic import BaseModel, ConfigDict

from app.schema.amenities_schema import AmenitiesResponse
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.location_schema import LocationResponse
from app.util.schema import AllOptional


class _BaseLocationAmenities(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_id: uuid.UUID
    amenities_id: uuid.UUID


class LocationAmenitiesResponse(_BaseLocationAmenities, ModelBaseInfo): ...


class EditLocationAmenities(_BaseLocationAmenities): ...


class DetailedLocationAmenities(LocationAmenitiesResponse):
    location: LocationResponse
    amenities: AmenitiesResponse


class CreateLocationAmenities(_BaseLocationAmenities): ...


class UpdateLocationAmenities(CreateLocationAmenities, metaclass=AllOptional): ...


class FindLocationAmenities(PaginationQuery, _BaseLocationAmenities, metaclass=AllOptional): ...
