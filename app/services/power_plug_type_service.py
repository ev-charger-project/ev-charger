from typing import Dict, List

from app.repository.power_plug_type_repository import PowerPlugTypeRepository
from app.schema.power_plug_type_schema import FindPowerPlugType
from app.services.base_service import BaseService


class PowerPlugTypeService(BaseService):
    def __init__(self, power_plug_type_repository: PowerPlugTypeRepository):
        self.power_plug_type_repository = power_plug_type_repository
        super().__init__(power_plug_type_repository)

    def get_unique_types_list(self, options: FindPowerPlugType) -> List[Dict[str, str]]:
        return self._repository.all_charger_type(options)
