from app.core.config import configs
from app.repository import EVChargerRepository
from app.repository.elastic_repository import ElasticsearchRepository
from app.services.base_service import BaseService


class EVChargerService(BaseService):
    def __init__(
        self,
        ev_charger_repository: EVChargerRepository,
        es_repository: ElasticsearchRepository,
    ):
        self.ev_charger_repository = ev_charger_repository
        self.es_repository = es_repository
        super().__init__(ev_charger_repository)

    def get_by_id(self, id: str):
        return self.ev_charger_repository.read_by_id(id)

    def add(self, schema):
        rs = self.ev_charger_repository.create(schema)

        charger_types = self.__get_ev_charger_port_details(
            ev_charger_ports=rs.ev_charger_ports
        )

        self.es_repository.add_charger_type_and_power_output(
            configs.ES_LOCATION_INDEX,
            rs.location_id,
            charger_types,
            number_of_station=1,
        )

        return rs

    def patch(self, id: str, schema):
        ev_charger, ports = self.ev_charger_repository.update(id, schema)

        types_to_remove = self.__get_ev_charger_port_details(ev_charger_ports=ports)

        charger_types = self.__get_ev_charger_port_details(
            ev_charger_ports=ev_charger.ev_charger_ports
        )

        self.es_repository.update_charger_type_and_power_output(
            configs.ES_LOCATION_INDEX,
            ev_charger.location_id,
            charger_types=charger_types,
            types_to_remove=types_to_remove,
        )

        return ev_charger

    def soft_remove_by_id(self, id):
        rs = self.ev_charger_repository.soft_delete_by_id(id)

        charger_types = self.__get_ev_charger_port_details(
            ev_charger_ports=rs.ev_charger_ports
        )

        self.es_repository.delete_charger_type_and_power_output(
            configs.ES_LOCATION_INDEX,
            location_id=str(rs.location_id),
            charger_types=charger_types,
        )

    def __get_ev_charger_port_details(self, ev_charger_ports):

        charger_types = [
            {
                "type": f"{ev_charger_port.power_plug_type.plug_type} - {ev_charger_port.power_plug_type.power_model}",
                "power_output": ev_charger_port.power_output.output_value,
            }
            for ev_charger_port in ev_charger_ports
        ]

        return charger_types
