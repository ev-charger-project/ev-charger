from starlette.testclient import TestClient

from tests.data.power_output import create_power_output, get_power_output_test_data


def test_create_power_output(client: TestClient):
    power_out_put = get_power_output_test_data()[0]
    rs = create_power_output(client, power_out_put)
    assert rs.status_code == 201


def test_create_with_missing_data(client: TestClient):
    invalid_data = get_power_output_test_data()[0].model_dump().clear()
    rs = client.post("/api/v1/power-outputs", json=invalid_data)
    assert rs.status_code == 422


def test_create_with_data_out_of_range(client: TestClient):
    invalid_data = {"output_value": 0, "charging_speed": "Slow", "voltage": 0}
    rs = client.post("/api/v1/power-outputs", json=invalid_data)
    assert rs.status_code == 422


def test_create_with_invalid_data_type(client: TestClient):
    invalid_data = get_power_output_test_data()[0]
    invalid_data.output_value = ""
    rs = create_power_output(client, invalid_data)
    assert rs.status_code == 422


def test_get_power_output(client: TestClient):
    power_out_put = get_power_output_test_data()[0]
    rs = create_power_output(client, power_out_put)
    rs = client.get(f"/api/v1/power-outputs/{rs.json()['id']}")
    assert rs.status_code == 200

    assert "id" in rs.json()
    assert power_out_put.output_value == rs.json()["output_value"]


def test_paginate_with_specified_page_size(client: TestClient):
    power_out_put = get_power_output_test_data()
    for power_output in power_out_put:
        create_power_output(client, power_output)
    rs = client.get("/api/v1/power-outputs?page=1&page_size=1")
    assert rs.status_code == 200
    assert len(rs.json()["founds"]) == 1


def test_get_paginated_power_output(client: TestClient):
    power_out_put = get_power_output_test_data()
    for power_output in power_out_put:
        create_power_output(client, power_output)
    rs = client.get("/api/v1/power-outputs")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 3


def test_update_power_output(client: TestClient):
    power_out_put = get_power_output_test_data()[0]
    rs = create_power_output(client, power_out_put)
    power_out_put = get_power_output_test_data()[1]
    rs = client.patch(f"/api/v1/power-outputs/{rs.json()['id']}", json=power_out_put.model_dump(mode="json"))
    assert rs.status_code == 200


def test_update_with_non_existent_id(client: TestClient):
    power_out_put = get_power_output_test_data()[0]
    rs = client.patch("/api/v1/power-outputs/0d49f0ef-a030-4710-8364-4e3a7f348953", json=power_out_put.model_dump(mode="json"))
    assert rs.status_code == 404


def test_delete_power_output(client: TestClient):
    power_out_put = get_power_output_test_data()[0]
    result = create_power_output(client, power_out_put)
    rs = client.delete(f"/api/v1/power-outputs/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/power-outputs/{result.json()['id']}")
    assert rs.status_code == 404
