from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.ev_charger_schema import (  # DetailedEVCharger,
    CreateEVCharger,
    DetailedEVCharger,
    EVChargerResponse,
    EVChargerResponseWithLocation,
    FindEVCharger,
    UpdateEVCharger,
)
from app.services.ev_charger_service import EVChargerService

router = APIRouter(
    prefix="/ev-chargers",
    tags=["ev-chargers"],
)


@router.get("", response_model=FindResult[EVChargerResponseWithLocation])
@inject
async def get_ev_charger_list(
    find_query: FindEVCharger = Depends(FindEVCharger),
    service: EVChargerService = Depends(Provide[Container.ev_charger_service]),
):
    return service.get_list(find_query)


@router.get("/{charger_id}", response_model=DetailedEVCharger)
@inject
async def get_ev_charger(
    charger_id: str,
    service: EVChargerService = Depends(Provide[Container.ev_charger_service]),
):
    return service.get_by_id(charger_id)


@router.post("", response_model=EVChargerResponse, status_code=201)
@inject
async def create_ev_charger(
    ev_charger: CreateEVCharger,
    service: EVChargerService = Depends(Provide[Container.ev_charger_service]),
):
    return service.add(ev_charger)


@router.patch("/{charger_id}", response_model=EVChargerResponse)
@inject
async def update_ev_charger(
    charger_id: str,
    ev_charger: UpdateEVCharger,
    service: EVChargerService = Depends(Provide[Container.ev_charger_service]),
):
    return service.patch(charger_id, ev_charger)


@router.delete("/{charger_id}", response_model=Blank)
@inject
async def soft_delete_ev_charger(
    charger_id: str,
    service: EVChargerService = Depends(Provide[Container.ev_charger_service]),
):
    service.soft_remove_by_id(charger_id)
    return Blank()
