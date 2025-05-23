from starlette.testclient import TestClient

from tests.data.power_plug_type import (
    create_power_plug_type,
    get_power_plug_type_test_data,
)


def test_create_power_plug_type(client: TestClient):
    power_plug_type = get_power_plug_type_test_data()[1]
    rs = create_power_plug_type(client, power_plug_type)
    assert rs.status_code == 200


def test_create_power_plug_type_duplicate_type_and_model(client: TestClient):
    power_plug_type = get_power_plug_type_test_data()[0]
    create_power_plug_type(client, power_plug_type)
    rs = create_power_plug_type(client, power_plug_type)
    assert rs.status_code == 400


def test_create_power_plug_type_missing_power_model(client: TestClient):
    power_plug_type = {
        "plug_type": "Type 2 (IEC 62196)",
        "plug_image_url": "example.png",
        "power_plug_region": "Europe",
    }
    rs = client.post("/api/v1/power-plug-types", json=power_plug_type)
    assert rs.status_code == 422


def test_get_power_plug_type(client: TestClient):
    power_plug_type = get_power_plug_type_test_data()[0]
    rs = create_power_plug_type(client, power_plug_type)
    rs = client.get(f"/api/v1/power-plug-types/{rs.json()['id']}")
    assert rs.status_code == 200


def test_get_all_charger_type(client: TestClient):
    power_plug_type_data = get_power_plug_type_test_data()
    for power_plug_type in power_plug_type_data:
        create_power_plug_type(client, power_plug_type)

    rs = client.get("/api/v1/power-plug-types/unique-types")
    assert rs.status_code == 200
    assert isinstance(rs.json(), list)
    assert len(rs.json()) == len({(item["plug_type"], item["power_model"], item["plug_image_url"]) for item in rs.json()})


def test_get_power_plug_types_empty(client: TestClient):
    rs = client.get("/api/v1/power-plug-types")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 0


def test_update_power_plug_type(client: TestClient):
    power_plug_type = get_power_plug_type_test_data()[0]
    rs = create_power_plug_type(client, power_plug_type)
    power_plug_type = get_power_plug_type_test_data()[1]
    rs = client.patch(f"/api/v1/power-plug-types/{rs.json()['id']}", json=power_plug_type.model_dump(mode="json"))
    assert rs.status_code == 200


def test_delete_power_plug_type(client: TestClient):
    power_plug_type = get_power_plug_type_test_data()[0]
    result = create_power_plug_type(client, power_plug_type)
    rs = client.delete(f"/api/v1/power-plug-types/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/power-plug-types/{result.json()['id']}")
    assert rs.status_code == 404
