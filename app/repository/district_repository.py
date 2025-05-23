from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager

from app.model.city import City
from app.model.district import District
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.district_schema import DistrictResponse, FindDistrict
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class DistrictRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, District)

    def get_districts_by_city(self, country: str | None, city_name: str, find_query: FindDistrict):
        with self.session_factory() as session:
            filter_options = dict_to_sqlalchemy_filter_options(self.model, find_query.model_dump(exclude_none=True))
            query = select(District)
            if country is not None:
                query = query.join(
                    District.city.and_(City.is_deleted.__eq__(False), City.name.__eq__(city_name), City.country.__eq__(country))
                )
            else:
                query = query.join(District.city.and_(City.is_deleted.__eq__(False), City.name.__eq__(city_name)))

            query = query.options(contains_eager(District.city))
            filtered_query = query.filter(filter_options)

            return FindResult[DistrictResponse].model_validate(
                paginate(filtered_query, find_query, session, District),
                from_attributes=True,
            )
