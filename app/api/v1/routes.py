from fastapi import APIRouter

from app.api.v1.endpoints.amenities import router as amenities_router
from app.api.v1.endpoints.city import router as city_router
from app.api.v1.endpoints.district import router as district_router
from app.api.v1.endpoints.ev_charger import router as ev_charger_router
from app.api.v1.endpoints.ev_charger_port import router as ev_charger_port_router
from app.api.v1.endpoints.gg_map import router as gg_map_router
from app.api.v1.endpoints.location import router as location_router
from app.api.v1.endpoints.location_amenities import router as location_amenities_router
from app.api.v1.endpoints.location_search_history import (
    router as location_search_history_router,
)
from app.api.v1.endpoints.media import router as media_router
from app.api.v1.endpoints.power_output import router as power_output_router
from app.api.v1.endpoints.power_plug_type import router as power_plug_type_router
from app.api.v1.endpoints.user_favorite import router as user_favorite_router

routers = APIRouter()

router_list = [
    location_router,
    power_plug_type_router,
    power_output_router,
    ev_charger_port_router,
    ev_charger_router,
    gg_map_router,
    user_favorite_router,
    city_router,
    district_router,
    media_router,
    location_amenities_router,
    amenities_router,
    location_search_history_router,
]

for router in router_list:
    routers.include_router(router)
