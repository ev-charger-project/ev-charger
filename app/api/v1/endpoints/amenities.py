from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.amenities_schema import (
    AmenitiesResponse,
    CreateAmenities,
    DetailedAmenities,
    EditAmenities,
    FindAmenities,
)
from app.schema.base_schema import Blank, FindResult
from app.services.amenities_service import AmenitiesService

router = APIRouter(
    prefix="/amenities",
    tags=["amenities"],
)


@router.get("", response_model=FindResult[DetailedAmenities])
@inject
async def get_amenities_list(
    find_query: FindAmenities = Depends(),
    service: AmenitiesService = Depends(Provide[Container.amenities_service]),
):
    return service.get_list(find_query)


@router.get("/{amenities_id}", response_model=DetailedAmenities)
@inject
async def get_amenities(
    amenities_id: str,
    service: AmenitiesService = Depends(Provide[Container.amenities_service]),
):
    return service.get_by_id(amenities_id)


@router.post("", response_model=AmenitiesResponse, status_code=201)
@inject
async def create_amenities(
    amenities: CreateAmenities,
    service: AmenitiesService = Depends(Provide[Container.amenities_service]),
):
    return service.add(amenities)


@router.patch("/{amenities_id}", response_model=AmenitiesResponse)
@inject
async def update_amenities(
    amenities_id: str,
    amenities: EditAmenities,
    service: AmenitiesService = Depends(Provide[Container.amenities_service]),
):
    return service.patch(amenities_id, amenities)


@router.delete("/{amenities_id}", response_model=Blank)
@inject
async def soft_delete_amenities(
    amenities_id: str,
    service: AmenitiesService = Depends(Provide[Container.amenities_service]),
):
    service.soft_remove_by_id(amenities_id)
    return Blank()
