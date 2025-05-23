from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.schema.gg_map_schema import DirectionRequest
from app.services import GGMapService

router = APIRouter(
    prefix="/gg-map",
    tags=["gg-map"],
)


@router.get("/directions")
@inject
async def directions(
    direction_request: DirectionRequest = Depends(DirectionRequest),
    service: GGMapService = Depends(Provide[Container.gg_map_service]),
):
    return service.get_directions(direction_request)
