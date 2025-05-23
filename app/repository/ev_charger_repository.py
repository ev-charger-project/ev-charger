from contextlib import AbstractContextManager
from logging import getLogger
from typing import Callable

from sqlalchemy import and_, select
from sqlalchemy.orm import Session, contains_eager, joinedload, selectinload

from app.core.exceptions import NotFoundError
from app.model.ev_charger import EVCharger
from app.model.ev_charger_port import EVChargerPort
from app.repository.base_repository import BaseRepository
from app.schema.base_schema import FindResult
from app.schema.ev_charger_schema import (
    CreateEVCharger,
    EVChargerResponseWithLocation,
    FindEVCharger,
)
from app.util.pagination import paginate
from app.util.query_builder import dict_to_sqlalchemy_filter_options


class EVChargerRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, EVCharger)

    def read_by_options(self, schema: FindEVCharger):
        with self.session_factory() as session:
            query = select(EVCharger).options(joinedload(EVCharger.location))
            filter_options = dict_to_sqlalchemy_filter_options(
                self.model, schema.model_dump(exclude_none=True, exclude={"text_value"})
            )
            filtered_query = query.filter(filter_options)
            return FindResult[EVChargerResponseWithLocation].model_validate(
                paginate(filtered_query, schema, session, EVCharger),
                from_attributes=True,
            )

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                select(EVCharger)
                .options(
                    selectinload(
                        EVCharger.ev_charger_ports.and_(
                            EVChargerPort.is_deleted.__eq__(False)
                        )
                    )
                    .options(joinedload(EVChargerPort.power_output))
                    .options(joinedload(EVChargerPort.power_plug_type))
                )
                .filter(and_(EVCharger.id == id, (EVCharger.is_deleted.__eq__(False))))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            return EVCharger.model_validate(rs, from_attributes=True)

    def create(self, schema: CreateEVCharger):
        # Chech if the EV charger already exists, if so, skip the creation
        # and return the existing one
        with self.session_factory() as session:
            existing_ev_charger = (
                session.query(EVCharger)
                .filter(
                    EVCharger.cpo_evse_emi3_id == schema.cpo_evse_emi3_id,
                    EVCharger.is_deleted.__eq__(False),
                )
                .first()
            )
            if existing_ev_charger:
                getLogger(__name__).warning(
                    f"EV charger with cpo_evse_emi3_id {schema.cpo_evse_emi3_id} already exists."
                )
                return self.read_by_id(existing_ev_charger.id.__str__())
            # If it doesn't exist, create a new one
            getLogger(__name__).info(
                f"Creating new EV charger with ID {schema.cpo_evse_emi3_id}."
            )

            ev_charger = EVCharger(**schema.model_dump(exclude={"ev_charger_ports"}))

            session.add(ev_charger)
            session.commit()
            session.refresh(ev_charger)

            if schema.ev_charger_ports:
                port_list = [
                    EVChargerPort(**port.model_dump(), ev_charger_id=ev_charger.id)
                    for port in schema.ev_charger_ports
                ]

                session.add_all(port_list)
                session.commit()

            return self.read_by_id(ev_charger.id.__str__())

    def _delete_ports_by_list_id(self, id_list):
        with self.session_factory() as session:
            session.query(EVChargerPort).filter(EVChargerPort.id.in_(id_list)).delete(
                synchronize_session=False
            )
            session.commit()

    def read_by_id_without_deleted(self, id: str):
        with self.session_factory() as session:
            query = (
                select(EVCharger)
                .join(
                    EVCharger.ev_charger_ports.and_(
                        EVChargerPort.is_deleted.__eq__(False)
                    ),
                    isouter=True,
                )
                .options(
                    contains_eager(EVCharger.ev_charger_ports)
                    .options(joinedload(EVChargerPort.power_output))
                    .options(joinedload(EVChargerPort.power_plug_type))
                )
                .filter(EVCharger.id.__eq__(id))
            )
            rs = session.execute(query).scalar()
            if not rs:
                raise NotFoundError(detail=f"not found id : {id}")
            return EVCharger.model_validate(rs, from_attributes=True)

    def update(
        self,
        id: str,
        schema: CreateEVCharger,
    ):
        with self.session_factory() as session:
            ev_charger = self.read_by_id(id)
            ports = ev_charger.ev_charger_ports
            upsert_ports = schema.ev_charger_ports
            deleted_port = [
                port
                for port in ports
                if port.id not in [upsert_port.id for upsert_port in upsert_ports]
            ]
            self._delete_ports_by_list_id([port.id for port in deleted_port])
            created_port = (
                [port for port in upsert_ports if port.id is None]
                if upsert_ports
                else []
            )
            updated_port = (
                [port for port in upsert_ports if port.id is not None]
                if upsert_ports
                else []
            )

            session.add_all(
                [
                    EVChargerPort(**port.model_dump(), ev_charger_id=id)
                    for port in created_port
                ]
            )
            session.commit()
            for port in updated_port:
                session.query(EVChargerPort).filter(EVChargerPort.id == port.id).update(
                    port.model_dump()
                )
                session.commit()

            session.query(EVCharger).filter(EVCharger.id == id).update(
                {
                    **schema.model_dump(exclude={"ev_charger_ports"}),
                    "version": EVCharger.version + 1,
                }
            )
            session.commit()

            return self.read_by_id(id), ports
