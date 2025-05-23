from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.district_schema import (
    CreateEditDistrict,
    DistrictResponse,
    FindDistrict,
)
from app.services.district_service import DistrictService

router = APIRouter(
    prefix="/districts",
    tags=["districts"],
)


@router.get("", response_model=FindResult[DistrictResponse])
@inject
async def get_districts_list(
    country: str | None = Query(description="Country belongs to this city will be fetched", default=None),
    city: str | None = Query(description="Districts belongs to this city will be fetched", default=None),
    find_query: FindDistrict = Depends(FindDistrict),
    service: DistrictService = Depends(Provide[Container.district_service]),
):
    return service.get_list(country, city, find_query)


@router.get("/{district_id}", response_model=DistrictResponse)
@inject
async def get_district(
    district_id: str,
    service: DistrictService = Depends(Provide[Container.district_service]),
):
    return service.get_by_id(district_id)


@router.post("", response_model=DistrictResponse, status_code=201)
@inject
async def create_district(
    district: CreateEditDistrict,
    service: DistrictService = Depends(Provide[Container.district_service]),
):
    return service.add(district)


@router.patch("/{district_id}", response_model=DistrictResponse)
@inject
async def update_district(
    district_id: str,
    district: CreateEditDistrict,
    service: DistrictService = Depends(Provide[Container.district_service]),
):
    return service.patch(district_id, district)


@router.delete("/{district_id}", response_model=Blank)
@inject
async def soft_delete_district(
    district_id: str,
    service: DistrictService = Depends(Provide[Container.district_service]),
):
    service.soft_remove_by_id(district_id)
    return Blank()
