from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.power_output_schema import (
    CreatePowerOutput,
    DetailedPowerOutput,
    EditPowerOutput,
    FindPowerOutput,
    PowerOutputResponse,
)
from app.services.power_output_service import PowerOutputService

router = APIRouter(
    prefix="/power-outputs",
    tags=["power-outputs"],
)


@router.get("", response_model=FindResult[PowerOutputResponse])
@inject
async def get_power_output_list(
    find_query: FindPowerOutput = Depends(),
    service: PowerOutputService = Depends(Provide[Container.power_output_service]),
):
    return service.get_list(find_query)


@router.get("/{power_output_id}", response_model=DetailedPowerOutput)
@inject
async def get_power_output(
    power_output_id: str,
    service: PowerOutputService = Depends(Provide[Container.power_output_service]),
):
    return service.get_by_id(power_output_id)


@router.post("", response_model=PowerOutputResponse, status_code=201)
@inject
async def create_power_output(
    power_output: CreatePowerOutput,
    service: PowerOutputService = Depends(Provide[Container.power_output_service]),
):
    return service.add(power_output)


@router.patch("/{power_output_id}", response_model=PowerOutputResponse)
@inject
async def update_power_output(
    power_output_id: str,
    power_output: EditPowerOutput,
    service: PowerOutputService = Depends(Provide[Container.power_output_service]),
):
    return service.patch(power_output_id, power_output)


@router.delete("/{power_output_id}", response_model=Blank)
@inject
async def soft_delete_power_output(
    power_output_id: str,
    service: PowerOutputService = Depends(Provide[Container.power_output_service]),
):
    service.soft_remove_by_id(power_output_id)
    return Blank()
