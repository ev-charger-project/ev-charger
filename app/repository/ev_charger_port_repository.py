from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, not_
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import NotFoundError
from app.model.ev_charger_port import EVChargerPort
from app.repository.base_repository import BaseRepository


class EVChargerPortRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, EVChargerPort)

    def read_by_id(self, id: str):
        with self.session_factory() as session:
            query = (
                session.query(self.model)
                .options(
                    joinedload(EVChargerPort.ev_charger),
                    joinedload(EVChargerPort.power_plug_type),
                    joinedload(EVChargerPort.power_output),
                )
                .filter(and_(self.model.id == id, not_(self.model.is_deleted)))
                .first()
            )

            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            return query
