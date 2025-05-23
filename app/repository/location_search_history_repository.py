from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, insert, select, update
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.model.location import Location
from app.model.location_search_history import LocationSearchHistory
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.location_search_history_schema import (
    CreateLocationSearchHistory,
    DetailedLocationSearchHistory,
    FindLocationSearchHistory,
)
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class LocationSearchHistoryRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, LocationSearchHistory)

    def read_by_options(self, schema: FindLocationSearchHistory):
        with self.session_factory() as session:
            query = select(LocationSearchHistory).options(
                joinedload(LocationSearchHistory.location.and_(Location.is_deleted.__eq__(False)))
            )
            filter_options = dict_to_sqlalchemy_filter_options(self.model, schema.model_dump(exclude_none=True))
            filtered_query = query.filter(filter_options)
            return FindResult[DetailedLocationSearchHistory].model_validate(
                paginate(filtered_query, schema, session, LocationSearchHistory),
                from_attributes=True,
            )

    def read_by_user_id(self, user_id: str, schema: FindLocationSearchHistory):
        with self.session_factory() as session:
            query = (
                select(LocationSearchHistory)
                .options(joinedload(LocationSearchHistory.location.and_(Location.is_deleted.__eq__(False))))
                .filter(LocationSearchHistory.user_id.__eq__(user_id))
            )
            filter_options = dict_to_sqlalchemy_filter_options(self.model, schema.model_dump(exclude_none=True))
            filtered_query = query.filter(filter_options)
            return FindResult[DetailedLocationSearchHistory].model_validate(
                paginate(filtered_query, schema, session, LocationSearchHistory),
                from_attributes=True,
            )

    def create(self, schema: CreateLocationSearchHistory):
        with self.session_factory() as session:
            select_stmt = (
                select(LocationSearchHistory)
                .options(joinedload(LocationSearchHistory.location.and_(Location.is_deleted.__eq__(False))))
                .filter(LocationSearchHistory.is_deleted.__eq__(False), LocationSearchHistory.location_id.__eq__(schema.location_id))
            )
            select_rs = session.execute(select_stmt).scalar()
            rs: LocationSearchHistory | None = None
            if select_rs:
                query = (
                    update(LocationSearchHistory)
                    .returning(LocationSearchHistory)
                    .filter(LocationSearchHistory.location_id.__eq__(schema.location_id))
                    .values(version=LocationSearchHistory.version + 1)
                )
                rs = session.execute(query).scalar()
            else:
                query = insert(LocationSearchHistory).returning(LocationSearchHistory)
                rs = session.execute(query, {**schema.model_dump(exclude_none=True)}).scalar()
            session.commit()
            return self.read_by_id(rs.id)

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(LocationSearchHistory)
                .options(joinedload(LocationSearchHistory.location.and_(Location.is_deleted.__eq__(False))))
                .filter(and_(LocationSearchHistory.id.__eq__(id), LocationSearchHistory.is_deleted.__eq__(False)))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            return DetailedLocationSearchHistory.model_validate(rs, from_attributes=True)
