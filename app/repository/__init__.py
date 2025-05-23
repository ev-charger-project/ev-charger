from app.repository.amenities_repository import AmenitiesRepository
from app.repository.city_repository import CityRepository
from app.repository.district_repository import DistrictRepository
from app.repository.ev_charger_port_repository import EVChargerPortRepository
from app.repository.ev_charger_repository import EVChargerRepository
from app.repository.location_amenities_repository import LocationAmenitiesRepository
from app.repository.location_repository import LocationRepository
from app.repository.location_search_history_repository import (
    LocationSearchHistoryRepository,
)
from app.repository.power_output_repository import PowerOutputRepository
from app.repository.power_plug_type_repository import PowerPlugTypeRepository
from app.repository.user_favorite_repository import UserFavoriteRepository

__all__ = [
    "LocationRepository",
    "PowerOutputRepository",
    "PowerPlugTypeRepository",
    "EVChargerPortRepository",
    "EVChargerRepository",
    "UserFavoriteRepository",
    "CityRepository",
    "DistrictRepository",
    "LocationAmenitiesRepository",
    "AmenitiesRepository",
    "LocationSearchHistoryRepository",
]
