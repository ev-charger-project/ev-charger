from pydantic import BaseModel

from app.schema.ev_charger_schema import LocationResponse


class Coordinate(BaseModel):
    lat: float
    lng: float


class RouteResponse(BaseModel):
    locations: list[LocationResponse] = []
    coordinates: list[Coordinate] = []
    overview_polyline: str | None = None
