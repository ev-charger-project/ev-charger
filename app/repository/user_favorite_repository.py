from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, joinedload

from app.model.location import Location
from app.model.user_favorite import UserFavorite
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult, SearchOptions
from app.schema.location_schema import LocationResponse
from app.schema.user_favorite_schema import (
    DetailedUserFavorite,
    FindUserFavorite,
    FindUserFavoriteByUser,
    UserFavoriteByUserResponse,
)
from app.util.pagination import paginate


class UserFavoriteRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, UserFavorite)

    def read_by_options(self, sc: FindUserFavorite):
        with self.session_factory() as session:
            query = select(UserFavorite).options(joinedload(UserFavorite.location.and_(Location.is_deleted.__eq__(False))))
            if sc.user_id:
                query = query.filter(UserFavorite.user_id.__eq__(sc.user_id))

            if sc.location_id:
                query = query.filter(UserFavorite.location_id.__eq__(sc.user_id))

            return FindResult[DetailedUserFavorite].model_validate(obj=paginate(query, sc, session, UserFavorite), from_attributes=True)

    def read_by_user_id(self, user_id: str, schema: FindUserFavoriteByUser):
        with self.session_factory() as session:

            query = (
                select(UserFavorite)
                .filter(and_(UserFavorite.user_id.__eq__(user_id), UserFavorite.is_deleted.__eq__(False)))
                .join(UserFavorite.location, isouter=True)
            )

            paginated_query = query.offset(schema.offset).limit(schema.limit)
            total = session.query(func.count()).select_from(query.subquery()).scalar()

            if schema.page_size * (schema.page - 1) > total:
                raise ValueError("Page out of range")

            rs = session.execute(paginated_query).unique().scalars().all()

            return FindResult(
                founds=(
                    [UserFavoriteByUserResponse(**rs[0].model_dump(), locations=[LocationResponse(**r.location.model_dump()) for r in rs])]
                    if rs
                    else []
                ),
                search_options=SearchOptions(
                    total_count=total, page=schema.page, page_size=schema.page_size, ordering=schema.ordering, order_by=schema.order_by
                ),
            )
