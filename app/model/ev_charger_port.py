import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model import EVCharger, PowerOutput, PowerPlugType


class EVChargerPort(BaseModel, table=True):
    power_plug_type_id: uuid.UUID = Field(foreign_key="powerplugtype.id", primary_key=True, index=True, nullable=False)
    power_output_id: uuid.UUID = Field(foreign_key="poweroutput.id", primary_key=True, index=True, nullable=False)
    ev_charger_id: uuid.UUID = Field(foreign_key="evcharger.id", primary_key=True, index=True, nullable=False)

    power_plug_type: "PowerPlugType" = Relationship(back_populates="ev_charger_ports")
    power_output: "PowerOutput" = Relationship(back_populates="ev_charger_ports")
    ev_charger: "EVCharger" = Relationship(back_populates="ev_charger_ports")
