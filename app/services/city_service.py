from app.repository import CityRepository
from app.schema.city_schema import FindCity
from app.services.base_service import BaseService


class CityService(BaseService):
    def __init__(
        self,
        city_repository: CityRepository,
    ):
        self.city_repository = city_repository
        super().__init__(city_repository)

    def generate_starter_data(self):
        return self.city_repository.generate_starter_data()

    def get_list(self, country: str | None, find_query: FindCity):
        if country is not None:
            return self.city_repository.get_cities_by_country(country, find_query)
        return self.city_repository.read_by_options(find_query)

    def get_by_id(self, id: str):
        return self.city_repository.read_by_id(id)
