from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship
from app.model.base_model import BaseModel

if TYPE_CHECKING:
    from app.model.ev_charger_port import EVChargerPort


class PowerPlugType(BaseModel, table=True):
    supplier_name: str = Field(nullable=False)
    power_model: str = Field(nullable=False)
    plug_type: str = Field(nullable=False)
    plug_type_id: str = Field(nullable=False)
    fixed_plug: bool = Field(nullable=True)
    plug_image_url: str = Field(nullable=True)
    additional_note: str = Field(nullable=True)
    power_plug_region: str = Field(nullable=True)
    ev_charger_ports: list["EVChargerPort"] = Relationship(
        back_populates="power_plug_type"
    )
