from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.city_schema import (
    CityResponse,
    CreateEditCity,
    DetailedCityResponse,
    FindCity,
)
from app.services.city_service import CityService

router = APIRouter(
    prefix="/cities",
    tags=["cities"],
)


@router.post("/starter_data")
@inject
async def generate_starter_data(
    service: CityService = Depends(Provide[Container.city_service]),
):
    return service.generate_starter_data()


@router.get("", response_model=FindResult[CityResponse])
@inject
async def get_cities_list(
    country: str | None = Query(description="Cities belongs to this country will be fetched", default=None),
    find_query: FindCity = Depends(FindCity),
    service: CityService = Depends(Provide[Container.city_service]),
):
    return service.get_list(country, find_query)


@router.get("/{city_id}", response_model=DetailedCityResponse)
@inject
async def get_city(
    city_id: str,
    service: CityService = Depends(Provide[Container.city_service]),
):
    return service.get_by_id(city_id)


@router.post("", response_model=CityResponse, status_code=201)
@inject
async def create_city(
    city: CreateEditCity,
    service: CityService = Depends(Provide[Container.city_service]),
):
    return service.add(city)


@router.patch("/{city_id}", response_model=CityResponse)
@inject
async def update_city(
    city_id: str,
    city: CreateEditCity,
    service: CityService = Depends(Provide[Container.city_service]),
):
    return service.patch(city_id, city)


@router.delete("/{city_id}", response_model=Blank)
@inject
async def soft_delete_city(
    city_id: str,
    service: CityService = Depends(Provide[Container.city_service]),
):
    service.soft_remove_by_id(city_id)
    return Blank()
