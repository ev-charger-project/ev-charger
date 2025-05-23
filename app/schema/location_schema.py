import datetime
from collections import Counter
from typing import TYPE_CHECKING, Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.constant.enum.location import Country
from app.constant.enum.location_access import LocationAccess
from app.constant.regex import PHONE_NUMBER_REGEX
from app.core.exceptions import ValidationError
from app.schema.amenities_schema import AmenitiesResponse
from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.ev_charger_schema import EVChargerResponseWithEVChargerPort
from app.schema.working_day_schema import WorkingDayResponse
from app.util.schema import AllOptional

if TYPE_CHECKING:
    from app.schema.location_amenities_schema import LocationAmenitiesResponse


class _BaseLocation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    external_id: str
    location_name: str
    street: str
    house_number: str | None = None
    district: str | None = None
    city: str
    state: str | None = None
    county: str | None = None
    country: Country
    postal_code: str | None = None
    latitude: float
    longitude: float
    phone_number: Annotated[str, Field(pattern=PHONE_NUMBER_REGEX)] | None = None
    website_url: str | None = None
    description: Annotated[str, Field(max_length=1000)] | None = None
    image_url: str | None = None
    pricing: str | None = None
    parking_level: str | None = None
    total_charging_ports: int | None = None
    access: LocationAccess | None = None
    payment_methods: list | None = None


class LocationResponse(_BaseLocation, ModelBaseInfo):
    status: str | None = None


class LocationAmenitiesResponse(ModelBaseInfo):
    amenities: AmenitiesResponse


class LocationResponseWithoutEVChargers(LocationResponse):
    working_days: list[WorkingDayResponse] | None = None
    location_amenities: list[LocationAmenitiesResponse] | None = None


class LocationResponseWithAmenities(LocationResponse):
    location_amenities: list[LocationAmenitiesResponse] | None = None


class DetailedLocationResponse(LocationResponse):
    ev_chargers: list[EVChargerResponseWithEVChargerPort]
    working_days: list[WorkingDayResponse]
    location_amenities: list[LocationAmenitiesResponse] | None = None


class LocationByRadiusQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_lat: float
    user_long: float
    radius: float = 10

    @field_validator("radius")
    def validate_radius(cls, v: float | None):
        if v is not None:
            if v >= 0:
                return v
            raise ValidationError("Radius must be a positive number")

    @field_validator("user_lat")
    def validate_latitude(cls, v: float):
        if -90.0 <= v <= 90.0:
            return v
        raise ValidationError("Latitude must be a valid value between -90 and 90.")

    @field_validator("user_long")
    def validate_longitude(cls, v: float):
        if -180.0 <= v <= 180.0:
            return v
        raise ValidationError("Longitude must be a valid value between -180 and 180.")


class LocationQuery(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location_name: str | None = None
    street: str | None = None
    district: str | None = None
    city: str | None = None
    country: Country | None = None
    text_value: str | None = None


class WorkingDay(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day: int
    open_time: datetime.time
    close_time: datetime.time

    @field_validator("day")
    def validate_day(cls, value):
        if not 0 < value < 8:
            raise ValueError("Day must be between 1 and 7")
        return value

    @model_validator(mode="before")
    def validate_open_close_time(cls, values):
        open_time, close_time = values.get("open_time"), values.get("close_time")
        if open_time >= close_time:
            raise ValueError("Close time must be greater than open time")
        return values


class CreateEditLocation(_BaseLocation):
    model_config = ConfigDict(from_attributes=True)

    working_days: list[WorkingDay] = []
    amenities_id: list[str] = []

    @field_validator("location_name")
    def validate_location_name(cls, v: str) -> str:
        if v.__len__() < 1 or v is None:
            raise ValueError("Location name is required.")
        if v.__len__() > 100:
            raise ValueError("Location name must not exceed 100 characters.")
        return v

    @field_validator("street")
    def validate_street(cls, v: str) -> str:
        if v.__len__() < 1 or v is None:
            raise ValueError("Street address is required.")
        if v.__len__() > 255:
            raise ValueError("Street address must not exceed 255 characters.")
        return v

    @field_validator("district")
    def validate_district(cls, v: str | None) -> str:
        if v is not None:
            if v.__len__() > 100:
                raise ValueError("District must not exceed 100 characters.")
            return v

    @field_validator("city")
    def validate_city(cls, v: str) -> str:
        if v.__len__() < 1 or v is None:
            raise ValueError("City is required.")
        if v.__len__() > 100:
            raise ValueError("City must not exceed 100 characters.")
        return v

    @field_validator("postal_code")
    def validate_postal_code(cls, v: str | None) -> str:
        if v is not None:
            if v.__len__() > 20:
                raise ValueError("Postal code must not exceed 20 characters.")
            return v

    @field_validator("pricing")
    def validate_pricing(cls, v: str | None) -> str:
        if v is not None:
            if v.__len__() > 100:
                raise ValueError("Pricing information must not exceed 100 characters.")
            return v

    @field_validator("parking_level")
    def validate_parking_level(cls, v: str | None) -> str:
        if v is not None:
            if v.__len__() > 50:
                raise ValueError("Parking level must not exceed 50 characters.")
            return v

    @field_validator("latitude")
    def validate_latitude(cls, v: float):
        if -90.0 <= v <= 90.0:
            return v
        raise ValueError("Latitude must be a valid value between -90 and 90.")

    @field_validator("longitude")
    def validate_longitude(cls, v: float):
        if -180.0 <= v <= 180.0:
            return v
        raise ValueError("Longitude must be a valid value between -180 and 180.")

    @model_validator(mode="after")
    def validate_working_days(self):
        working_days = self.working_days
        if working_days:
            days = [wd.day for wd in working_days]
            day_counts = Counter(days)
            duplicate_days = {
                day: count for day, count in day_counts.items() if count > 1
            }
            if duplicate_days:
                raise ValueError(f"Duplicate days: {duplicate_days.keys()}")
        return self


class SearchLocation(BaseModel):
    station_count: int | None = Field(default=0)
    power_output_gte: float | None = None
    power_output_lte: float | None = None
    lat: float | None = Field(ge=-90, le=90, default=None)
    lon: float | None = Field(ge=-180, le=180, default=None)
    radius: float | None = None
    query: str | None = None

    @field_validator("radius")
    def validate_radius(cls, v: float | None):
        if v is not None:
            if v >= 0:
                return v
            raise ValidationError("Radius must be a positive number")

    @model_validator(mode="before")
    def validate_radius_lat_lon(cls, values):
        radius = values.get("radius")
        lat = values.get("lat")
        lon = values.get("lon")

        if radius is not None:
            if lat is None or lon is None:
                raise ValidationError(
                    "if you want search with radius must have both latitude and longitude."
                )

        return values

    @model_validator(mode="before")
    def validate_power_output_range(cls, values):
        power_output_gte = values.get("power_output_gte")
        power_output_lte = values.get("power_output_lte")

        if power_output_gte is not None and power_output_lte is not None:
            if power_output_lte < power_output_gte:
                raise ValidationError(
                    "power_output_lte must be greater than or equal to power_output_gte."
                )

        return values


# CRUD


class FindLocation(PaginationQuery, LocationQuery, metaclass=AllOptional): ...


class UpsertLocation(CreateEditLocation, metaclass=AllOptional): ...


from app.schema.location_amenities_schema import LocationAmenitiesResponse  # noqa: E402
