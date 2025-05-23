from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.ev_charger_port import EVChargerPort


class PowerOutput(BaseModel, table=True):
    output_value: float = Field(nullable=False)
    voltage: int = Field(nullable=False)
    amperage: int = Field(nullable=False)
    charging_speed: str = Field(nullable=True)
    description: str = Field(nullable=True)

    ev_charger_ports: list["EVChargerPort"] = Relationship(
        back_populates="power_output"
    )
