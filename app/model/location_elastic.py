from pydantic import BaseModel
from typing import Optional, List
from app.constant.enum.location import Country
from app.constant.enum.location_access import LocationAccess


class LocationElastic(BaseModel):
    id: Optional[str]
    here_id: Optional[str]
    external_id: Optional[str]
    location_name: str
    latitude: float
    longitude: float
    street: str
    house_number: Optional[str] = None
    district: Optional[str] = None
    city: str
    state: Optional[str] = None
    county: Optional[str] = None
    country: Country
    postal_code: Optional[str] = None
    location: Optional[str] = None  # For geo_point, usually "lat,lon" string
    pricing: Optional[str] = None
    phone_number: Optional[str] = None
    website_url: Optional[str] = None
    parking_level: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_deleted: bool = False
    total_charging_ports: Optional[int] = None
    access: Optional[LocationAccess] = None
    payment_methods: Optional[List[str]] = None
    working_days: Optional[List[dict]] = None
    charger_types: Optional[List[dict]] = None
    amenities: Optional[List[str]] = None


mapping = {
    "mappings": {
        "properties": {
            "location": {"type": "geo_point"},
            "id": {"type": "keyword"},
            "here_id": {"type": "keyword"},
            "external_id": {"type": "keyword"},
            "location_name": {"type": "text"},
            "latitude": {"type": "double"},
            "longitude": {"type": "double"},
            "street": {"type": "text"},
            "house_number": {"type": "text"},
            "district": {"type": "text"},
            "city": {"type": "text"},
            "state": {"type": "text"},
            "county": {"type": "text"},
            "country": {"type": "keyword"},
            "postal_code": {"type": "text"},
            "pricing": {"type": "text"},
            "phone_number": {"type": "text"},
            "website_url": {"type": "text"},
            "parking_level": {"type": "text"},
            "description": {"type": "text"},
            "image_url": {"type": "text"},
            "is_deleted": {"type": "boolean"},
            "total_charging_ports": {"type": "integer"},
            "access": {"type": "keyword"},
            "payment_methods": {"type": "keyword"},
            "working_days": {
                "type": "nested",
                "properties": {
                    "day": {"type": "integer"},
                    "open_time": {"type": "date", "format": "HH:mm"},
                    "close_time": {"type": "date", "format": "HH:mm"},
                },
            },
            "charger_types": {
                "type": "nested",
                "properties": {
                    "type": {"type": "keyword"},
                    "power_output": {"type": "integer"},
                },
            },
            "amenities": {"type": "keyword"},
        }
    }
}

# from pydantic import BaseModel


# class LocationElastic(BaseModel):
#     id: str | None
#     external_id: str | None
#     location_name: str
#     latitude: float
#     longitude: float
#     street: str
#     house_number: str | None
#     district: str | None
#     city: str
#     state: str | None
#     county: str | None
#     country: str
#     postal_code: str | None
#     location: str
#     pricing: str | None
#     phone_number: str | None
#     website_url: str | None
#     parking_level: str | None
#     description: str | None
#     image_url: str | None
#     is_deleted: bool = False
#     total_charging_ports: int | None = None
#     access: str | None = None
#     payment_methods: list[str] | None = None


# mapping = {
#     "mappings": {
#         "properties": {
#             "location": {"type": "geo_point"},
#             "id": {"type": "text"},
#             "external_id": {"type": "text"},
#             "location_name": {"type": "text"},
#             "latitude": {"type": "double"},
#             "longitude": {"type": "double"},
#             "street": {"type": "text"},
#             "house_number": {"type": "text"},
#             "district": {"type": "text"},
#             "city": {"type": "text"},
#             "state": {"type": "text"},
#             "county": {"type": "text"},
#             "country": {"type": "text"},
#             "postal_code": {"type": "text"},
#             "pricing": {"type": "text"},
#             "phone_number": {"type": "text"},
#             "website_url": {"type": "text"},
#             "parking_level": {"type": "text"},
#             "station_count": {"type": "integer"},
#             "charging_speed": {"type": "keyword"},
#             "description": {"type": "text"},
#             "is_deleted": {"type": "boolean"},
#             "working_days": {
#                 "type": "nested",
#                 "properties": {
#                     "day": {"type": "integer"},
#                     "open_time": {"type": "date", "format": "HH:mm"},
#                     "close_time": {"type": "date", "format": "HH:mm"},
#                 },
#             },
#             "charger_types": {
#                 "type": "nested",
#                 "properties": {
#                     "type": {"type": "text"},
#                     "power_output": {"type": "integer"},
#                 },
#             },
#             "amenities": {"type": "keyword"},
#         }
#     }
# }
