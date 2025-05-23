from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from sqlalchemy import and_, delete, insert, not_, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, contains_eager, joinedload, selectinload

from app.core.exceptions import DuplicatedError, NotFoundError
from app.model.ev_charger import EVCharger
from app.model.ev_charger_port import EVChargerPort
from app.model.location import Location
from app.model.location_amenities import LocationAmenities
from app.model.location_search_history import LocationSearchHistory
from app.model.power_output import PowerOutput
from app.model.power_plug_type import PowerPlugType
from app.model.user_favorite import UserFavorite
from app.model.working_day import WorkingDay
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.location_schema import (
    CreateEditLocation,
    DetailedLocationResponse,
    FindLocation,
    LocationByRadiusQuery,
    LocationResponseWithAmenities,
)
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class LocationRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Location)

    def read_by_options(
        self,
        schema: FindLocation,
        detailed: bool = False,
        soft_delete_visibility: bool = False,
        disable_pagination: bool = False,
    ):
        with self.session_factory() as session:
            query = select(Location).options(
                selectinload(
                    Location.location_amenities.and_(
                        LocationAmenities.is_deleted.__eq__(False)
                    )
                ),
            )
            if detailed:
                query.options(
                    selectinload(
                        Location.ev_chargers.and_(EVCharger.is_deleted.__eq__(False))
                    )
                    .selectinload(
                        EVCharger.ev_charger_ports.and_(
                            EVChargerPort.is_deleted.__eq__(False)
                        )
                    )
                    .options(
                        joinedload(
                            EVChargerPort.power_output.and_(
                                EVChargerPort.is_deleted.__eq__(False)
                            )
                        ),
                        joinedload(
                            EVChargerPort.power_plug_type.and_(
                                PowerPlugType.is_deleted.__eq__(False)
                            )
                        ),
                    ),
                    selectinload(
                        Location.working_days.and_(WorkingDay.is_deleted.__eq__(False))
                    ),
                )
            filter_options = dict_to_sqlalchemy_filter_options(
                self.model, schema.model_dump(exclude_none=True, exclude={"text_value"})
            )
            if schema.text_value:
                query = query.filter(
                    or_(
                        Location.location_name.ilike(f"%{schema.text_value}%"),
                        Location.street.ilike(f"%{schema.text_value}%"),
                    )
                )

            filtered_query = query.filter(filter_options)
            if detailed:
                return FindResult[DetailedLocationResponse].model_validate(
                    paginate(
                        filtered_query,
                        schema,
                        session,
                        Location,
                        soft_delete_visibility,
                        not disable_pagination,
                    ),
                    from_attributes=True,
                )

            return FindResult[LocationResponseWithAmenities].model_validate(
                paginate(
                    filtered_query,
                    schema,
                    session,
                    Location,
                    soft_delete_visibility,
                    not disable_pagination,
                ),
                from_attributes=True,
            )

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(Location)
                .options(
                    selectinload(
                        Location.ev_chargers.and_(EVCharger.is_deleted.__eq__(False))
                    )
                    .selectinload(
                        EVCharger.ev_charger_ports.and_(
                            EVChargerPort.is_deleted.__eq__(False)
                        )
                    )
                    .options(
                        joinedload(
                            EVChargerPort.power_output.and_(
                                PowerOutput.is_deleted.__eq__(False)
                            )
                        ),
                        joinedload(
                            EVChargerPort.power_plug_type.and_(
                                PowerPlugType.is_deleted.__eq__(False)
                            )
                        ),
                    ),
                    selectinload(
                        Location.working_days.and_(WorkingDay.is_deleted.__eq__(False))
                    ),
                    selectinload(
                        Location.location_amenities.and_(
                            LocationAmenities.is_deleted.__eq__(False)
                        )
                    ),
                )
                .filter(and_(Location.id.__eq__(id), Location.is_deleted.__eq__(False)))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            return DetailedLocationResponse.model_validate(rs, from_attributes=True)

    def read_by_radius(self, schema: LocationByRadiusQuery):
        with self.session_factory() as session:
            query = select(Location)

            if schema.radius is not None:
                radius_in_lat_long = schema.radius / 100  # Estimation, low accuracy
                query = query.filter(
                    and_(
                        not_(Location.is_deleted),
                        Location.latitude.__ge__(schema.user_lat - radius_in_lat_long),
                        Location.longitude.__ge__(
                            schema.user_long - radius_in_lat_long
                        ),
                        Location.latitude.__le__(schema.user_lat + radius_in_lat_long),
                        Location.longitude.__le__(
                            schema.user_long + radius_in_lat_long
                        ),
                    )
                )

            rs = session.execute(query).scalars().all()

            return rs

    def create(self, schema: CreateEditLocation):
        with self.session_factory() as session:
            location = Location(
                **schema.model_dump(exclude={"working_days", "amenities_id"}),
                working_days=[
                    WorkingDay(**day.model_dump()) for day in schema.working_days
                ],
            )
            try:
                session.add(location)
                session.commit()
                session.refresh(location)
            except IntegrityError as e:
                raise DuplicatedError(detail=str(e.orig))

            if schema.amenities_id.__len__() > 0:
                amentities_list = [
                    LocationAmenities(amenities_id=amenity_id, location_id=location.id)
                    for amenity_id in schema.amenities_id
                ]
                session.add_all(amentities_list)
                session.commit()
            return self.read_by_id(location.id.__str__())

    def update(self, id: str, schema: CreateEditLocation):
        with self.session_factory() as session:
            is_updated = (
                session.query(self.model)
                .filter(self.model.id == id)
                .update(
                    {
                        **schema.model_dump(
                            exclude_none=True, exclude={"working_days", "amenities_id"}
                        ),
                        "version": Location.version + 1,
                    }
                )
            )
            if is_updated:
                working_days_append_list: list[WorkingDay] = []
                removed_working_days_no: list[int] = [1, 2, 3, 4, 5, 6, 7]
                for day in schema.working_days:
                    removed_working_days_no.remove(day.day)
                    working_day_is_updated = (
                        session.query(WorkingDay)
                        .filter(
                            and_(
                                WorkingDay.location_id == id, WorkingDay.day == day.day
                            )
                        )
                        .update(
                            {
                                "open_time": day.open_time,
                                "close_time": day.close_time,
                                "is_deleted": False,
                                "deleted_at": None,
                                "version": WorkingDay.version + 1,
                            }
                        )
                    )
                    if not working_day_is_updated:
                        working_days_append_list.append(
                            WorkingDay(**day.model_dump(), location_id=id).model_dump()
                        )
                if working_days_append_list.__len__() > 0:
                    session.execute(insert(WorkingDay), working_days_append_list)
                session.execute(
                    update(WorkingDay)
                    .filter(
                        WorkingDay.location_id.__eq__(id),
                        WorkingDay.day.in_(removed_working_days_no),
                    )
                    .values(is_deleted=True, deleted_at=datetime.utcnow())
                )

                session.commit()

                location = self.read_by_id(id)
                amenities = location.location_amenities

                upsert_location_amenities_id = schema.amenities_id
                deleted_location_amenities_id = [
                    amenity.id
                    for amenity in amenities
                    if amenity
                    not in [
                        upsert_amenity_id
                        for upsert_amenity_id in upsert_location_amenities_id
                    ]
                ]
                self._delete_amenities_by_list_id(deleted_location_amenities_id)
                session.add_all(
                    [
                        LocationAmenities(
                            amenities_id=amenity_id, location_id=location.id
                        )
                        for amenity_id in upsert_location_amenities_id
                    ]
                )
                session.commit()

            return self.read_by_id(id)

    def _delete_amenities_by_list_id(self, id_list):
        with self.session_factory() as session:
            session.query(LocationAmenities).filter(
                LocationAmenities.id.in_(id_list)
            ).delete(synchronize_session=False)
            session.commit()

    def _soft_delete_amenities_by_list_id(self, id_list):
        with self.session_factory() as session:
            session.query(LocationAmenities).filter(
                LocationAmenities.id.in_(id_list)
            ).update(
                {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "version": self.model.version + 1,
                },
                synchronize_session=False,
            )
            session.commit()

    def delete_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(Location)
                .options(selectinload(Location.ev_chargers))
                .filter(and_(Location.id.__eq__(id), not_(Location.is_deleted)))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            if rs.ev_chargers.__len__() > 0:
                delete_ev_chargers_query = delete(EVCharger).filter(
                    EVCharger.location_id.__eq__(id)
                )
                session.execute(delete_ev_chargers_query)
            if rs.location_search_histories.__len__() > 0:
                delete_location_search_histories_query = delete(
                    LocationSearchHistory
                ).filter(LocationSearchHistory.location_id.__eq__(id))
                session.execute(delete_location_search_histories_query)
            delete_query = delete(Location).filter(Location.id.__eq__(id))
            session.execute(delete_query)
            session.commit()

    def soft_delete_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(Location)
                .join(
                    Location.ev_chargers.and_(EVCharger.is_deleted.__eq__(False)),
                    isouter=True,
                )
                .options(contains_eager(Location.ev_chargers))
                .filter(and_(Location.id.__eq__(id), not_(Location.is_deleted)))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            if rs.ev_chargers.__len__() > 0:
                delete_ev_chargers_query = (
                    update(EVCharger)
                    .filter(EVCharger.location_id.__eq__(id))
                    .values(is_deleted=True, deleted_at=datetime.utcnow())
                )
                session.execute(delete_ev_chargers_query)
            if rs.location_search_histories.__len__() > 0:
                delete_location_search_histories_query = (
                    update(LocationSearchHistory)
                    .filter(LocationSearchHistory.location_id.__eq__(id))
                    .values(is_deleted=True, deleted_at=datetime.utcnow())
                )
                session.execute(delete_location_search_histories_query)
            delete_query = (
                update(Location)
                .filter(Location.id.__eq__(id))
                .values(
                    is_deleted=True,
                    deleted_at=datetime.utcnow(),
                )
            )
            session.execute(delete_query)
            session.commit()

    def wipe_locations_data(self):
        with self.session_factory() as session:
            ev_charger_port_delete_stmt = delete(EVChargerPort)
            session.execute(ev_charger_port_delete_stmt)

            ev_charger_delete_stmt = delete(EVCharger)
            session.execute(ev_charger_delete_stmt)

            user_favorite_delete_stmt = delete(UserFavorite)
            session.execute(user_favorite_delete_stmt)

            location_search_history_delete_stmt = delete(LocationSearchHistory)
            session.execute(location_search_history_delete_stmt)

            location_amenities_delete_stmt = delete(LocationAmenities)
            session.execute(location_amenities_delete_stmt)

            working_day_delete_stmt = delete(WorkingDay)
            session.execute(working_day_delete_stmt)

            location_delete_stmt = delete(Location)
            session.execute(location_delete_stmt)

            session.commit()
