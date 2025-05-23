from contextlib import AbstractContextManager
from logging import getLogger
from typing import Callable

from sqlalchemy.orm import Session

from app.model.power_output import PowerOutput
from app.repository.base_repository import BaseRepository
from app.schema.power_output_schema import CreatePowerOutput


class PowerOutputRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, PowerOutput)

    def create(self, schema: CreatePowerOutput):
        with self.session_factory() as session:
            # Check if the power output already exists, if so, skip the creation
            # and return the existing one
            existing_power_output = (
                session.query(PowerOutput)
                .filter(
                    PowerOutput.output_value == schema.output_value,
                    PowerOutput.voltage == schema.voltage,
                    PowerOutput.amperage == schema.amperage,
                    PowerOutput.is_deleted.__eq__(False),
                )
                .first()
            )
            if existing_power_output:
                getLogger(__name__).warning(
                    f"Power output with value {schema.output_value}, voltage {schema.voltage}, and amperage {schema.amperage} already exists."
                )
                return existing_power_output
            # If it doesn't exist, create a new one
            getLogger(__name__).info(
                f"Creating new power output with value {schema.output_value}, voltage {schema.voltage}, and amperage {schema.amperage}."
            )
            # Create a new PowerOutput instance
            power_output = PowerOutput(**schema.model_dump())
            session.add(power_output)
            session.commit()
            session.refresh(power_output)
            return power_output
