from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.gg_map_schema import DirectionRequest
from app.schema.google_api_schema import RouteResponse
from app.schema.location_schema import (
    CreateEditLocation,
    DetailedLocationResponse,
    FindLocation,
    LocationByRadiusQuery,
    LocationResponse,
    LocationResponseWithAmenities,
    SearchLocation,
)
from app.services.location_service import LocationService
from app.util.decode_base64 import decode_base64

router = APIRouter(
    prefix="/locations",
    tags=["locations"],
)


@router.get("/location-on-route", response_model=RouteResponse)
@inject
async def get_location_on_route(
    direction: DirectionRequest = Depends(DirectionRequest),
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.get_location_by_direction(direction)


@router.get("/sync-elastic-data", status_code=204)
@inject
async def sync_elastic_data(
    service: LocationService = Depends(Provide[Container.location_service]),
):
    service.sync_elastic_data()


@router.get("", response_model=FindResult[LocationResponseWithAmenities])
@inject
async def get_location_list(
    find_query: FindLocation = Depends(FindLocation),
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.get_list(find_query)


@router.get("/by_radius", response_model=List[LocationResponse])
@inject
async def get_location_list_by_radius(
    find_query: LocationByRadiusQuery = Depends(LocationByRadiusQuery),
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.get_by_radius(find_query)


@router.get("/nearby", response_model=List[LocationResponse])
@inject
async def search_nearby_location(
    find_query: LocationByRadiusQuery = Depends(LocationByRadiusQuery),
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.search_nearby_location(find_query)


@router.get("/search", response_model=List[LocationResponse])
@inject
async def get_list_location(
    is_fuzzi: bool = Query(description="Fuzzi search", default=False),
    charger_type: List[str] = Query([], description="list charge types"),
    searchlocation: SearchLocation = Depends(SearchLocation),
    amenities: List[str] = Query([], description="list amenities"),
    service: LocationService = Depends(Provide[Container.location_service]),
):
    if (
        all(
            var is None
            for var in [
                searchlocation.power_output_gte,
                searchlocation.power_output_lte,
                searchlocation.query,
                searchlocation.station_count,
            ]
        )
        and len(charger_type) == 0
    ):
        return []

    decoded_charge_types = [decode_base64(item).decode("utf-8") for item in charger_type]
    return service.search_by_elastic(searchlocation, is_fuzzi, decoded_charge_types, amenities)


@router.get("/{location_id}", response_model=DetailedLocationResponse)
@inject
async def get_location(
    location_id: str,
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.get_by_id(location_id)


@router.post("", response_model=DetailedLocationResponse, status_code=201)
@inject
async def create_location(
    location: CreateEditLocation,
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.add(location)


@router.patch("/{location_id}", response_model=LocationResponse)
@inject
async def update_location(
    location_id: str,
    location: CreateEditLocation,
    service: LocationService = Depends(Provide[Container.location_service]),
):
    return service.patch(location_id, location)


@router.delete("/{location_id}", response_model=Blank)
@inject
async def soft_delete_location(
    location_id: str,
    service: LocationService = Depends(Provide[Container.location_service]),
):
    service.soft_remove_by_id(location_id)
    return Blank()


@router.delete("", response_model=Blank)
@inject
async def wipe_locations(
    service: LocationService = Depends(Provide[Container.location_service]),
):
    service.wipe_locations_data()
    return Blank()
