from starlette.testclient import TestClient

from app.schema.ev_charger_port_schema import CreateEVChargerPort
from tests.data.ev_charger import create_ev_charger, get_ev_charger_test_data
from tests.data.power_output import create_power_output, get_power_output_test_data
from tests.data.power_plug_type import (
    create_power_plug_type,
    get_power_plug_type_test_data,
)


def get_ev_charger_port_test_data(client: TestClient):
    power_output_id = create_power_output(client, get_power_output_test_data()[0]).json()["id"]
    power_plug_type_id = create_power_plug_type(client, get_power_plug_type_test_data()[0]).json()["id"]
    ev_charger_id = create_ev_charger(client, get_ev_charger_test_data(client)[0]).json()["id"]

    return [
        CreateEVChargerPort(power_output_id=power_output_id, power_plug_type_id=power_plug_type_id, ev_charger_id=ev_charger_id),
        CreateEVChargerPort(power_output_id=power_output_id, power_plug_type_id=power_plug_type_id, ev_charger_id=ev_charger_id),
        CreateEVChargerPort(power_output_id=power_output_id, power_plug_type_id=power_plug_type_id, ev_charger_id=ev_charger_id),
    ]
