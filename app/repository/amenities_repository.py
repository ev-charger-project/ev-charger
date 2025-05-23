from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError
from app.model.amenities import Amenities
from app.repository.base_repository import BaseRepository
from app.schema.amenities_schema import CreateAmenities


class AmenitiesRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Amenities)

    def create(self, schema: CreateAmenities):
        with self.session_factory() as session:
            get_am = (
                session.query(Amenities)
                .filter(
                    Amenities.amenities_types == schema.amenities_types,
                    Amenities.image_url == schema.image_url,
                    Amenities.is_deleted.__eq__(False),
                )
                .first()
            )
            if get_am:
                raise DuplicatedError(f"Amenities with {schema.amenities_types} and image {schema.image_url} already exists")
            am = Amenities(**schema.model_dump())
            session.add(am)
            session.commit()
            session.refresh(am)
            return am
