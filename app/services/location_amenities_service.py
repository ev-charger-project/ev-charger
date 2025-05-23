from app.repository.location_amenities_repository import LocationAmenitiesRepository
from app.services.base_service import BaseService


class LocationAmenitiesService(BaseService):
    def __init__(self, location_amenities_repository: LocationAmenitiesRepository):
        self.location_amenities_repository = location_amenities_repository
        super().__init__(location_amenities_repository)
