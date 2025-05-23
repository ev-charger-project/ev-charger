from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.dependencies import validate_token
from app.schema.base_schema import Blank, FindResult
from app.schema.location_search_history_schema import (
    CreateLocationSearchHistory,
    DetailedLocationSearchHistory,
    EditLocationSearchHistory,
    FindLocationSearchHistory,
    FindLocationSearchHistoryByUser,
    LocationSearchHistoryByUserResponse,
    LocationSearchHistoryResponse,
)
from app.services.location_search_history_service import LocationSearchHistoryService

router = APIRouter(
    prefix="/location-search-history",
    tags=["location-search-history"],
)


@router.get("/user", response_model=FindResult[LocationSearchHistoryByUserResponse])
@inject
async def get_location_search_history_by_user_id(
    find_query: FindLocationSearchHistoryByUser = Depends(),
    authorization=Depends(validate_token),
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    authorization["subject"]

    return service.get_by_user_id(authorization["subject"], find_query)


@router.get("", response_model=FindResult[DetailedLocationSearchHistory])
@inject
async def get_location_search_history_list(
    find_query: FindLocationSearchHistory = Depends(FindLocationSearchHistory),
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    return service.get_list(find_query)


@router.get("/{location_search_history_id}", response_model=DetailedLocationSearchHistory)
@inject
async def get_location_search_history(
    location_search_history_id: str,
    authorization=Depends(validate_token),
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    return service.get_by_id(location_search_history_id)


@router.post("", response_model=DetailedLocationSearchHistory, status_code=201)
@inject
async def create_location_search_history(
    location_search_history: CreateLocationSearchHistory,
    authorization=Depends(validate_token),
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    location_search_history.user_id = authorization["subject"]

    return service.add(location_search_history)


@router.patch("/{location_search_history_id}", response_model=LocationSearchHistoryResponse)
@inject
async def update_location_search_history(
    location_search_history_id: str,
    location_search_history: EditLocationSearchHistory,
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    return service.patch(location_search_history_id, location_search_history)


@router.delete("/{location_search_history_id}", response_model=Blank)
@inject
async def soft_delete_location_search_history(
    location_search_history_id: str,
    service: LocationSearchHistoryService = Depends(Provide[Container.location_search_history_service]),
):
    service.soft_remove_by_id(location_search_history_id)
    return Blank()
