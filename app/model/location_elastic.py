from pydantic import BaseModel


class LocationElastic(BaseModel):
    id: str | None
    location_name: str
    latitude: float
    longitude: float
    street: str
    district: str | None
    city: str
    country: str
    postal_code: str | None
    location: str
    pricing: str | None
    phone_number: str | None
    parking_level: str | None
    description: str | None
    is_deleted: bool = False


mapping = {
    "mappings": {
        "properties": {
            "location": {"type": "geo_point"},
            "id": {"type": "text"},
            "location_name": {"type": "text"},
            "latitude": {"type": "double"},
            "longitude": {"type": "double"},
            "street": {"type": "text"},
            "district": {"type": "text"},
            "city": {"type": "text"},
            "country": {"type": "text"},
            "postal_code": {"type": "text"},
            "pricing": {"type": "text"},
            "phone_number": {"type": "text"},
            "parking_level": {"type": "text"},
            "station_count": {"type": "integer"},
            "charging_speed": {"type": "keyword"},
            "description": {"type": "text"},
            "is_deleted": {"type": "boolean"},
            "working_days": {
                "type": "nested",
                "properties": {
                    "day": {"type": "integer"},
                    "open_time": {"type": "date", "format": "HH:mm"},
                    "close_time": {"type": "date", "format": "HH:mm"},
                },
            },
            "charger_types": {"type": "nested", "properties": {"type": {"type": "text"}, "power_output": {"type": "integer"}}},
            "amenities": {"type": "keyword"},
        }
    }
}
