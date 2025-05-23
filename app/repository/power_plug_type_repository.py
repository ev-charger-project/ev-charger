from contextlib import AbstractContextManager
from typing import Callable, Dict, List
from logging import getLogger

from sqlalchemy.orm import Session

from app.core.exceptions import DuplicatedError
from app.model.power_plug_type import PowerPlugType
from app.repository.base_repository import BaseRepository
from app.schema.power_plug_type_schema import CreatePowerPlugType


class PowerPlugTypeRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PowerPlugType)

    def all_charger_type(self, options) -> List[Dict]:
        with self.session_factory() as session:
            query = session.query(
                PowerPlugType.plug_type,
                PowerPlugType.power_model,
                PowerPlugType.plug_image_url,
            ).distinct(
                PowerPlugType.plug_type,
                PowerPlugType.power_model,
                PowerPlugType.plug_image_url,
            )
            results = query.all()
            summary_list = [
                {
                    "plug_type": row[0],
                    "power_model": row[1],
                    "plug_image_url": row[2] if row[2] is not None else "",
                }
                for row in results
            ]
            return summary_list

    def create(self, schema: CreatePowerPlugType):
        with self.session_factory() as session:
            get_ppt = (
                session.query(PowerPlugType)
                .filter(
                    PowerPlugType.power_model == schema.power_model,
                    PowerPlugType.plug_type == schema.plug_type,
                    PowerPlugType.is_deleted.__eq__(False),
                )
                .first()
            )
            # Check if the power plug type already exists, if so, skip the creation
            # and return the existing one
            if get_ppt:
                getLogger(__name__).warning(
                    f"Power plug type with model {schema.power_model} and type {schema.plug_type} already exists."
                )
                return get_ppt
            # If it doesn't exist, create a new one
            getLogger(__name__).info(
                f"Creating new power plug type with model {schema.power_model} and type {schema.plug_type}."
            )
            # Create a new PowerPlugType instance
            ppt = PowerPlugType(**schema.model_dump())
            session.add(ppt)
            session.commit()
            session.refresh(ppt)
            return ppt
