import json
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable

from sqlalchemy import and_, delete, not_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager, selectinload

from app.core.exceptions import DuplicatedError, NotFoundError
from app.model.city import City
from app.model.district import District
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.city_schema import (
    CityResponse,
    CreateEditCity,
    DetailedCityResponse,
    FindCity,
)
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class CityRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, City)

    def generate_starter_data(self):
        f = open("app/countries_states_cities_min.json", encoding="utf-8")
        data: list[dict[str, Any]] = json.load(f)
        schemas: list[CreateEditCity] = []
        for country in data:
            schemas.extend(
                [CreateEditCity(name=city["name"], country=country["name"], districts=city["cities"]) for city in country["states"]]
            )

        with self.session_factory() as session:
            # Wipe old data first
            delete_stmt = delete(District)
            delete_stmt_2 = delete(City)
            session.execute(delete_stmt)
            session.execute(delete_stmt_2)
            session.commit()

            cities = [
                City(
                    **schema.model_dump(exclude={"districts"}),
                    districts=[District(**district.model_dump()) for district in schema.districts],
                )
                for schema in schemas
            ]

            try:
                session.add_all(cities)
                session.commit()
                [session.refresh(city) for city in cities]
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            return [City(**city.model_dump()) for city in cities]

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(City)
                .join(City.districts.and_(District.is_deleted.__eq__(False)), isouter=True)
                .options(contains_eager(City.districts))
                .filter(and_(City.id.__eq__(id), City.is_deleted.__eq__(False)))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            return DetailedCityResponse.model_validate(rs, from_attributes=True)

    def get_cities_by_country(self, country: str, find_query: FindCity):
        with self.session_factory() as session:
            filter_options = dict_to_sqlalchemy_filter_options(self.model, find_query.model_dump(exclude_none=True))
            query = select(City)
            filtered_query = query.filter(filter_options).filter(and_(not_(City.is_deleted), City.country.__eq__(country)))

            return FindResult[CityResponse].model_validate(
                paginate(filtered_query, find_query, session, City),
                from_attributes=True,
            )

    def create(self, schema: CreateEditCity):
        with self.session_factory() as session:
            city = City(
                **schema.model_dump(exclude={"districts"}), districts=[District(**district.model_dump()) for district in schema.districts]
            )
            try:
                session.add(city)
                session.commit()
                session.refresh(city)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))
            return City(**city.model_dump())

    def update(self, id: str, schema: CreateEditCity):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(
                {**schema.model_dump(exclude_none=True, exclude={"districts"}), "version": City.version + 1}
            )

            for district in schema.districts:
                session.query(District).filter(and_(District.city_id == id, District.name == district.name)).update(
                    {"name": district.name, "version": District.version + 1}
                )
            session.commit()
            return self.read_by_id(id)

    def delete_by_id(self, id: str):
        with self.session_factory() as session:
            query = select(City).options(selectinload(City.districts)).filter(and_(City.id.__eq__(id), not_(City.is_deleted)))
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            if rs.districts.__len__() > 0:
                delete_district_query = delete(District).filter(District.city_id.__eq__(id))
                session.execute(delete_district_query)

            delete_query = delete(City).filter(City.id.__eq__(id))
            session.execute(delete_query)
            session.commit()

    def soft_delete_by_id(self, id: str):
        with self.session_factory() as session:
            query = select(City).options(selectinload(City.districts)).filter(and_(City.id.__eq__(id), not_(City.is_deleted)))
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            if rs.districts.__len__() > 0:
                delete_district_query = (
                    update(District)
                    .filter(District.city_id.__eq__(id))
                    .values(
                        is_deleted=True,
                        deleted_at=datetime.utcnow(),
                    )
                )
                session.execute(delete_district_query)

            delete_query = (
                update(City)
                .filter(City.id.__eq__(id))
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                )
            )
            session.execute(delete_query)
            session.commit()
