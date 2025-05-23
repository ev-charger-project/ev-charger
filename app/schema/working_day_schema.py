import datetime
import uuid
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.util.schema import AllOptional

if TYPE_CHECKING:
    from app.schema.location_schema import LocationResponse


class _BaseWorkingDay(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    day: int
    open_time: datetime.time
    close_time: datetime.time


class CreateEditWorkingDay(_BaseWorkingDay):
    location_id: uuid.UUID

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


class WorkingDayResponse(ModelBaseInfo, _BaseWorkingDay, metaclass=AllOptional):
    location_id: uuid.UUID


class DetailedWorkingDay(WorkingDayResponse):
    location: "LocationResponse"


class FindWorkingDay(PaginationQuery, _BaseWorkingDay, metaclass=AllOptional):
    location_id: uuid.UUID


class UpsertWorkingDay(CreateEditWorkingDay, metaclass=AllOptional): ...
