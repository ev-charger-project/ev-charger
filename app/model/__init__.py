from sqlmodel import SQLModel

from app.model.amenities import Amenities
from app.model.city import City
from app.model.district import District
from app.model.ev_charger import EVCharger
from app.model.ev_charger_port import EVChargerPort
from app.model.location import Location
from app.model.location_amenities import LocationAmenities
from app.model.location_search_history import LocationSearchHistory
from app.model.power_output import PowerOutput
from app.model.power_plug_type import PowerPlugType
from app.model.user_favorite import UserFavorite
from app.model.working_day import WorkingDay

__all__ = [
    "SQLModel",
    "Location",
    "PowerOutput",
    "PowerPlugType",
    "EVChargerPort",
    "EVCharger",
    "WorkingDay",
    "UserFavorite",
    "City",
    "District",
    "LocationAmenities",
    "Amenities",
    "LocationSearchHistory",
]
