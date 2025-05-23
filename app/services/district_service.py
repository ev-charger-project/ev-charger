from app.repository import DistrictRepository
from app.schema.district_schema import FindDistrict
from app.services.base_service import BaseService


class DistrictService(BaseService):
    def __init__(
        self,
        district_repository: DistrictRepository,
    ):
        self.district_repository = district_repository
        super().__init__(district_repository)

    def get_list(self, country: str | None, city: str | None, find_query: FindDistrict):
        if city is not None:
            return self.district_repository.get_districts_by_city(country, city, find_query)
        return self.district_repository.read_by_options(find_query)
