from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.dependencies import validate_token
from app.schema.base_schema import Blank, FindResult
from app.schema.user_favorite_schema import (
    CreateUserFavorite,
    DetailedUserFavorite,
    EditUserFavorite,
    FindUserFavorite,
    FindUserFavoriteByUser,
    UserFavoriteByUserResponse,
    UserFavoriteResponse,
)
from app.services.user_favorite_service import UserFavoriteService

router = APIRouter(
    prefix="/user-favorite",
    tags=["user-favorite"],
)


@router.get("/user", response_model=FindResult[UserFavoriteByUserResponse])
@inject
async def get_user_favorite_by_user_id(
    find_query: FindUserFavoriteByUser = Depends(),
    authorization=Depends(validate_token),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    authorization["subject"]

    return service.get_by_user_id(authorization["subject"], find_query)


@router.get("", response_model=FindResult[DetailedUserFavorite])
@inject
async def get_user_favorite_list(
    find_query: FindUserFavorite = Depends(),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    return service.get_list(find_query)


@router.get("/{user_favorite_id}", response_model=DetailedUserFavorite)
@inject
async def get_user_favorite(
    user_favorite_id: str,
    authorization=Depends(validate_token),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    return service.get_by_id(user_favorite_id)


@router.post("", response_model=UserFavoriteResponse, status_code=201)
@inject
async def create_user_favorite(
    user_favorite: CreateUserFavorite,
    authorization=Depends(validate_token),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    user_favorite.user_id = authorization["subject"]

    return service.add(user_favorite)


@router.patch("/{user_favorite_id}", response_model=UserFavoriteResponse)
@inject
async def update_user_favorite(
    user_favorite_id: str,
    user_favorite: EditUserFavorite,
    authorization=Depends(validate_token),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    return service.patch(user_favorite_id, user_favorite)


@router.delete("/{user_favorite_id}", response_model=Blank)
@inject
async def soft_delete_user_favorite(
    user_favorite_id: str,
    authorization=Depends(validate_token),
    service: UserFavoriteService = Depends(Provide[Container.user_favorite_service]),
):
    service.soft_remove_by_id(user_favorite_id)
    return Blank()
