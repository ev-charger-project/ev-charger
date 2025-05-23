from typing import Dict, List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.power_plug_type_schema import (
    CreatePowerPlugType,
    DetailedPowerPlugType,
    EditPowerPlugType,
    FindPowerPlugType,
    PowerPlugTypeResponse,
)
from app.services.power_plug_type_service import PowerPlugTypeService

router = APIRouter(
    prefix="/power-plug-types",
    tags=["power-plug-types"],
)


@router.get("", response_model=FindResult[PowerPlugTypeResponse])
@inject
async def get_power_plug_type_list(
    find_query: FindPowerPlugType = Depends(),
    service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
):
    return service.get_list(find_query)


# @router.get("/unique-types", response_model=List[Dict[str, str]])
# @inject
# async def get_unique_power_plug_type_list(
#     find_query: FindPowerPlugType = Depends(),
#     service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
# ):
#     return service.get_unique_types_list(find_query)


@router.get("/{power_plug_type_id}", response_model=DetailedPowerPlugType)
@inject
async def get_power_plug_type(
    power_plug_type_id: str,
    service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
):
    return service.get_by_id(power_plug_type_id)


@router.post("", response_model=PowerPlugTypeResponse)
@inject
async def create_power_plug_type(
    power_plug_type: CreatePowerPlugType,
    service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
):
    return service.add(power_plug_type)


@router.patch("/{power_plug_type_id}", response_model=PowerPlugTypeResponse)
@inject
async def update_power_plug_type(
    power_plug_type_id: str,
    power_plug_type: EditPowerPlugType,
    service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
):
    return service.put_update(power_plug_type_id, power_plug_type)


@router.delete("/{power_plug_type_id}", response_model=Blank)
@inject
async def soft_delete_power_plug_type(
    power_plug_type_id: str,
    service: PowerPlugTypeService = Depends(Provide[Container.power_plug_type_service]),
):
    service.soft_remove_by_id(power_plug_type_id)
    return Blank()
