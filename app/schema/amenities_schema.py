from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional


class _BaseAmenities(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    amenities_types: str
    image_url: Optional[str]


class CreateAmenities(_BaseAmenities): ...


class EditAmenities(_BaseAmenities): ...


class AmenitiesResponse(ModelBaseInfo, _BaseAmenities): ...


class DetailedAmenities(AmenitiesResponse):
    pass


class FindAmenities(PaginationQuery, _BaseAmenities, metaclass=AllOptional): ...


class UpsertAmenities(_BaseAmenities): ...
