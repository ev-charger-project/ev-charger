import uuid

from pydantic import BaseModel

from app.schema.base_schema import ModelBaseInfo, PaginationQuery
from app.schema.location_schema import LocationResponse
from app.util.schema import AllOptional


class _BaseUserFavorite(BaseModel):
    location_id: uuid.UUID
    user_id: uuid.UUID | None = None


class UserFavoriteResponse(_BaseUserFavorite, ModelBaseInfo): ...


class EditUserFavorite(_BaseUserFavorite): ...


class DetailedUserFavorite(UserFavoriteResponse):
    location: LocationResponse


class CreateUserFavorite(_BaseUserFavorite): ...


class UpdateUserFavorite(CreateUserFavorite, metaclass=AllOptional): ...


class FindUserFavorite(PaginationQuery, _BaseUserFavorite, metaclass=AllOptional): ...


class FindUserFavoriteByUser(PaginationQuery, metaclass=AllOptional): ...


class UserFavoriteByUserResponse(UserFavoriteResponse):
    locations: list[LocationResponse] = []
