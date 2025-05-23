from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, not_, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.model.location_amenities import LocationAmenities
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.location_amenities_schema import (
    DetailedLocationAmenities,
    FindLocationAmenities,
)
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class LocationAmenitiesRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, LocationAmenities)

    def read_by_options(self, sc: FindLocationAmenities):
        with self.session_factory() as session:
            query = select(LocationAmenities).options(joinedload(LocationAmenities.location), joinedload(LocationAmenities.amenities))

            filter_options = dict_to_sqlalchemy_filter_options(self.model, sc.model_dump(exclude_none=True))
            filtered_query = query.filter(filter_options)

            return FindResult[DetailedLocationAmenities].model_validate(
                obj=paginate(filtered_query, sc, session, LocationAmenities),
                from_attributes=True,
            )

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .options(
                    joinedload(LocationAmenities.location),
                    joinedload(LocationAmenities.amenities),
                )
                .filter(and_(self.model.id == id, not_(self.model.is_deleted)))
                .first()
            )

            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            return query
