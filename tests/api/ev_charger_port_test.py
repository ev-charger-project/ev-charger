from starlette.testclient import TestClient

from tests.data.ev_charger_port import get_ev_charger_port_test_data

URL = "/api/v1/ev-charger-ports"


def create_ev_charger_port(client: TestClient):
    ev_charger_port = get_ev_charger_port_test_data(client)[0]
    result = client.post(url=URL, json=ev_charger_port.model_dump(mode="json"))
    return result


def test_get_ev_charger_port(client: TestClient):
    ev_charger_port = create_ev_charger_port(client)
    rs = client.get(url=f"{URL}/{ev_charger_port.json()['id']}")

    assert rs.status_code == 200
    assert "id" in rs.json()


def test_create_ev_charger_port(client: TestClient):
    rs = create_ev_charger_port(client)
    assert rs.status_code == 201


def test_update_ev_charger_port(client: TestClient):
    ev_charger_port = create_ev_charger_port(client)
    ev_charger_port_data = ev_charger_port.json()
    rs = client.patch(url=f"{URL}/{ev_charger_port.json()['id']}", json=ev_charger_port_data)

    assert rs.status_code == 200


def test_delete_ev_charger_port(client: TestClient):
    ev_charger_port = create_ev_charger_port(client).json()
    rs = client.delete(url=f"{URL}/{ev_charger_port['id']}")

    assert rs.status_code == 200

    rs = client.get(url=f"{URL}/{ev_charger_port['id']}")
    assert rs.status_code == 404
