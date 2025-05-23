from app.repository.user_favorite_repository import UserFavoriteRepository
from app.schema.user_favorite_schema import FindUserFavoriteByUser
from app.services.base_service import BaseService


class UserFavoriteService(BaseService):
    def __init__(self, user_favorite_repository: UserFavoriteRepository):
        self.user_favorite_repository = user_favorite_repository
        super().__init__(user_favorite_repository)

    def get_by_user_id(self, user_id: str, schema: FindUserFavoriteByUser):
        return self.user_favorite_repository.read_by_user_id(user_id, schema)
