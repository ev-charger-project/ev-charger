from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.base_schema import Blank, FindResult
from app.schema.ev_charger_port_schema import (
    CreateEVChargerPort,
    DetailedEVChargerPortResponse,
    EVChargerPortResponse,
    FindEVChargerPort,
    UpdateEVChargerPort,
)
from app.services.ev_charger_port_service import EVChargerPortService

router = APIRouter(
    prefix="/ev-charger-ports",
    tags=["ev-charger-ports"],
)


@router.get("", response_model=FindResult[EVChargerPortResponse])
@inject
async def get_ev_charger_ports(
    find_query: FindEVChargerPort = Depends(),
    service: EVChargerPortService = Depends(Provide[Container.ev_charger_port_service]),
):
    return service.get_list(find_query)


@router.get("/{ev_charger_port_id}", response_model=DetailedEVChargerPortResponse)
@inject
async def get_ev_charger_port(
    ev_charger_port_id: str,
    service: EVChargerPortService = Depends(Provide[Container.ev_charger_port_service]),
):
    return service.get_by_id(ev_charger_port_id)


@router.post("", response_model=EVChargerPortResponse, status_code=201)
@inject
async def create_ev_charger_port(
    ev_charger_port: CreateEVChargerPort,
    service: EVChargerPortService = Depends(Provide[Container.ev_charger_port_service]),
):
    return service.add(ev_charger_port)


@router.patch("/{ev_charger_port_id}", response_model=EVChargerPortResponse)
@inject
async def update_ev_charger_port(
    ev_charger_port_id: str,
    ev_charger_port: UpdateEVChargerPort,
    service: EVChargerPortService = Depends(Provide[Container.ev_charger_port_service]),
):
    return service.patch(ev_charger_port_id, ev_charger_port)


@router.delete("/{ev_charger_port_id}", response_model=Blank)
@inject
async def soft_delete_ev_charger_port(
    ev_charger_port_id: str,
    service: EVChargerPortService = Depends(Provide[Container.ev_charger_port_service]),
):
    service.soft_remove_by_id(ev_charger_port_id)
    return Blank()
