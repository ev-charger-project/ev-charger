from app.repository.power_output_repository import PowerOutputRepository
from app.services.base_service import BaseService


class PowerOutputService(BaseService):
    def __init__(self, power_output_repository: PowerOutputRepository):
        self.power_plug_type_repository = power_output_repository
        super().__init__(power_output_repository)
