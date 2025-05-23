from app.repository.location_search_history_repository import (
    LocationSearchHistoryRepository,
)
from app.schema.location_search_history_schema import FindLocationSearchHistoryByUser
from app.services.base_service import BaseService


class LocationSearchHistoryService(BaseService):
    def __init__(self, location_search_history_repository: LocationSearchHistoryRepository):
        self.location_search_history_repository = location_search_history_repository
        super().__init__(location_search_history_repository)

    def get_by_user_id(self, user_id: str, schema: FindLocationSearchHistoryByUser):
        return self.location_search_history_repository.read_by_user_id(user_id, schema)
