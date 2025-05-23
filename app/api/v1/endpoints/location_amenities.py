from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.location_amenities_schema import (
    CreateLocationAmenities,
    DetailedLocationAmenities,
    EditLocationAmenities,
    FindLocationAmenities,
    LocationAmenitiesResponse,
)
from app.services.location_amenities_service import LocationAmenitiesService

router = APIRouter(
    prefix="/location-amenities",
    tags=["location-amenities"],
)


@router.get("", response_model=FindResult[DetailedLocationAmenities])
@inject
async def get_location_amenities_list(
    find_query: FindLocationAmenities = Depends(),
    service: LocationAmenitiesService = Depends(Provide[Container.location_amenities_service]),
):
    return service.get_list(find_query)


@router.get("/{location_amenities_id}", response_model=DetailedLocationAmenities)
@inject
async def get_location_amenities(
    location_amenities_id: str,
    service: LocationAmenitiesService = Depends(Provide[Container.location_amenities_service]),
):
    return service.get_by_id(location_amenities_id)


@router.post("", response_model=LocationAmenitiesResponse, status_code=201)
@inject
async def create_location_amenities(
    location_amenities: CreateLocationAmenities,
    service: LocationAmenitiesService = Depends(Provide[Container.location_amenities_service]),
):
    return service.add(location_amenities)


@router.patch("/{location_amenities_id}", response_model=LocationAmenitiesResponse)
@inject
async def update_location_amenities(
    location_amenities_id: str,
    location_amenities: EditLocationAmenities,
    service: LocationAmenitiesService = Depends(Provide[Container.location_amenities_service]),
):
    return service.patch(location_amenities_id, location_amenities)


@router.delete("/{location_amenities_id}", response_model=Blank)
@inject
async def soft_delete_location_amenities(
    location_amenities_id: str,
    service: LocationAmenitiesService = Depends(Provide[Container.location_amenities_service]),
):
    service.soft_remove_by_id(location_amenities_id)
    return Blank()
