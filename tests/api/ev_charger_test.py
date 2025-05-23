from starlette.testclient import TestClient

from tests.data.ev_charger import (
    create_ev_charger,
    create_ev_charger_wrong_input,
    get_ev_charger_test_data,
)


def test_create_ev_charger(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    rs = create_ev_charger(client, ev_charger)
    assert rs.status_code == 201


def test_create_ev_charger_with_wrong_availability_input(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    ev_charger.availability = "invalid input"
    rs = create_ev_charger(client, ev_charger)
    msg = rs.json()["detail"][0]["msg"]
    assert msg == "Input should be 'available', 'in use' or 'out of order'"
    assert rs.status_code == 422


def test_create_ev_charger_without_optional_data(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    rs = create_ev_charger(client, ev_charger)
    assert rs.status_code == 201


def test_create_ev_charger_with_missing_data(client: TestClient):
    missing_data = {
        "station_name": "Agest",
        "availability": "available",
    }

    rs = create_ev_charger_wrong_input(client, missing_data)
    assert rs.status_code == 422


def test_get_ev_charger(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    rs = create_ev_charger(client, ev_charger)
    rs = client.get(f"/api/v1/ev-chargers/{rs.json()['id']}")
    assert rs.json()["station_name"] == ev_charger.station_name
    assert rs.json()["availability"] == ev_charger.availability
    assert rs.status_code == 200


def test_get_paginated_ev_charger(client: TestClient):
    ev_chargers = get_ev_charger_test_data(client)
    for ev_charger in ev_chargers:
        create_ev_charger(client, ev_charger)
    rs = client.get("/api/v1/ev-chargers")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 3


def test_update_ev_charger(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    rs = create_ev_charger(client, ev_charger)
    ev_charger = get_ev_charger_test_data(client)[1]
    rs = client.patch(
        f"/api/v1/ev-chargers/{rs.json()['id']}",
        json=ev_charger.model_dump(mode="json"),
    )
    assert rs.status_code == 200


def test_update_ev_charger_record_not_exist(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    rs = create_ev_charger(client, ev_charger)
    ev_charger = get_ev_charger_test_data(client)[1]
    rs = client.patch(
        f"/api/v1/ev_chargers/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}",
        json=ev_charger.model_dump(mode="json"),
    )
    assert rs.status_code == 404


def test_delete_ev_charger_record_not_exist(client: TestClient):
    rs = client.delete(f"/api/v1/ev-chargers/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}")
    assert rs.status_code == 404


def test_delete_ev_charger(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    result = create_ev_charger(client, ev_charger)
    rs = client.delete(f"/api/v1/ev-chargers/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/ev-chargers/{result.json()['id']}")
    assert rs.status_code == 404
