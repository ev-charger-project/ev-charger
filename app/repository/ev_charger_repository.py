from contextlib import AbstractContextManager
from typing import Callable
import logging

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

logger = logging.getLogger(__name__)


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
        # Chech if the EV charger with the same here_id already exists, if so, update it
        # and return the existing one
        with self.session_factory() as session:
            existing_ev_charger = (
                session.query(EVCharger)
                .filter(
                    EVCharger.here_id == schema.here_id,
                    EVCharger.is_deleted.__eq__(False),
                )
                .first()
            )
            if existing_ev_charger:
                logger.info(
                    f"EV charger with ID {schema.here_id} already exists. Updating it."
                )
                # return self.read_by_id(existing_ev_charger.id.__str__())
                # Update the existing EV charger with the new data
                print(f"Updating existing EV charger with ID {existing_ev_charger.id}.")
                return self.update(existing_ev_charger.id.__str__(), schema)
                # session.commit()
                # session.refresh(existing_ev_charger)
                # # If there are ports to update, handle them
                # if schema.ev_charger_ports:
                #     # Get the existing ports for the EV charger
                #     existing_ports = {
                #         port.here_id: port
                #         for port in existing_ev_charger.ev_charger_ports
                #     }
                #     # Prepare a list to hold new ports
                #     new_ports = []
                #     for port in schema.ev_charger_ports:
                #         if port.id in existing_ports:
                #             # Update existing port
                #             session.query(EVChargerPort).filter(
                #                 EVChargerPort.id == port.id
                #             ).update(port.model_dump())
                #         else:
                #             # Create new port
                #             new_ports.append(
                #                 EVChargerPort(
                #                     **port.model_dump(),
                #                     ev_charger_id=existing_ev_charger.id,
                #                 )
                #             )
                #     if new_ports:
                #         session.add_all(new_ports)
                #     session.commit()
                #     session.refresh(existing_ev_charger)
                # return self.read_by_id(existing_ev_charger.id.__str__())

            # If it doesn't exist, create a new one
            logger.info(f"Creating new EV charger with ID {schema.here_id}.")
            print(f"Creating new EV charger with ID {schema.here_id}.")
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

            print(f"Created EV charger with ID {ev_charger.id}.")
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
            print(f"ports: {ports}")
            upsert_ports = schema.ev_charger_ports
            print(f"upsert_ports: {upsert_ports}")
            deleted_port = [
                port
                for port in ports
                if port.here_id
                not in [upsert_port.here_id for upsert_port in upsert_ports]
            ]
            self._delete_ports_by_list_id([port.here_id for port in deleted_port])
            # created_port = (
            #     [port for port in upsert_ports if port.here_id is None]
            #     if upsert_ports
            #     else []
            # )
            updated_port = (
                [port for port in upsert_ports if port.here_id is not None]
                if upsert_ports
                else []
            )

            # session.add_all(
            #     [
            #         EVChargerPort(**port.model_dump(), ev_charger_id=id)
            #         for port in created_port
            #     ]
            # )
            session.commit()
            for port in updated_port:
                session.query(EVChargerPort).filter(
                    EVChargerPort.here_id == port.here_id
                ).update(port.model_dump())
                session.commit()

            session.query(EVCharger).filter(EVCharger.id == id).update(
                {
                    **schema.model_dump(exclude={"ev_charger_ports"}),
                    "version": EVCharger.version + 1,
                }
            )
            session.commit()
            print(f"Updated EV charger with ID {id}.")

            return self.read_by_id(id), ports
