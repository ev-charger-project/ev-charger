from app.repository.ev_charger_port_repository import EVChargerPortRepository
from app.services.base_service import BaseService


class EVChargerPortService(BaseService):
    def __init__(self, ev_charger_port_repository: EVChargerPortRepository):
        self.ev_charger_port_repository = ev_charger_port_repository
        super().__init__(ev_charger_port_repository)

    def get_by_id(self, id: str):
        return self._repository.read_by_id(id)
