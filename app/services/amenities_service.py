from app.repository.amenities_repository import AmenitiesRepository
from app.services.base_service import BaseService


class AmenitiesService(BaseService):
    def __init__(self, amenities_repository: AmenitiesRepository):
        self.amenities_repository = amenities_repository
        super().__init__(amenities_repository)
