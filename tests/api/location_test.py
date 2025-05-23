from starlette.testclient import TestClient

from tests.data.ev_charger import create_ev_charger, get_ev_charger_test_data
from tests.data.location import (
    create_location,
    create_location_wrong_input,
    get_location_test_data,
)


def test_create_location(client: TestClient):
    location = get_location_test_data()[0]
    rs = create_location(client, location)
    assert rs.status_code == 201


def test_create_location_with_long_postal_code(client: TestClient):
    location = get_location_test_data()[0]
    location.postal_code = "FFJFJFJLFJwidjijIJGSHEGLHEGLSHELGKJSEHGLKJEsdfdSHGLKSE"
    rs = create_location(client, location)

    msg = rs.json()["detail"][0]["msg"]

    assert msg == "Value error, Postal code must not exceed 20 characters."
    assert rs.status_code == 422


def test_create_location_with_missing_data(client: TestClient):
    missing_data = {
        "location_name": "Agest",
        "district": "Tan Binh",
        "country": "VN",
        "postal_code": "VN",
        "latitude": 20,
        "longitude": 40,
        "pricing": "test",
        "phone_number": "0945157286",
        "parking_level": "B3",
    }

    rs = create_location_wrong_input(client, missing_data)
    assert rs.status_code == 422


def test_create_location_with_wrong_latitude_value(client: TestClient):
    location = get_location_test_data()[0]
    location.latitude = 100
    rs = create_location(client, location)

    msg = rs.json()["detail"][0]["msg"]

    assert msg == "Value error, Latitude must be a valid value between -90 and 90."
    assert rs.status_code == 422


def test_create_location_with_wrong_longitude_value(client: TestClient):
    location = get_location_test_data()[0]
    location.longitude = 200
    rs = create_location(client, location)

    msg = rs.json()["detail"][0]["msg"]

    assert msg == "Value error, Longitude must be a valid value between -180 and 180."
    assert rs.status_code == 422


def test_get_location(client: TestClient):
    location = get_location_test_data()[0]
    rs = create_location(client, location)
    rs = client.get(f"/api/v1/locations/{rs.json()['id']}")
    assert rs.json()["location_name"] == location.location_name
    assert rs.json()["working_days"] != []
    assert rs.status_code == 200


def test_get_paginated_location(client: TestClient):
    location = get_location_test_data()
    for location in location:
        create_location(client, location)
    rs = client.get("/api/v1/locations")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 3


def test_update_location(client: TestClient):
    location = get_location_test_data()[0]
    rs = create_location(client, location)
    location = get_location_test_data()[1]
    rs = client.patch(f"/api/v1/locations/{rs.json()['id']}", json=location.model_dump(mode="json"))
    assert rs.status_code == 200


def test_update_location_record_not_exist(client: TestClient):
    location = get_location_test_data()[0]
    rs = create_location(client, location)
    location = get_location_test_data()[1]
    rs = client.patch(
        f"/api/v1/locations/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}",
        json=location.model_dump(mode="json"),
    )
    assert rs.status_code == 404


def test_delete_location_record_not_exist(client: TestClient):
    rs = client.delete(f"/api/v1/locations/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}")
    assert rs.status_code == 404


def test_delete_location(client: TestClient):
    location = get_location_test_data()[0]
    result = create_location(client, location)
    rs = client.delete(f"/api/v1/locations/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/locations/{result.json()['id']}")
    assert rs.status_code == 404


def test_delete_location_when_active_charger_exists(client: TestClient):
    ev_charger = get_ev_charger_test_data(client)[0]
    create_ev_charger(client, ev_charger)
    rs = client.delete(f"/api/v1/locations/{ev_charger.location_id}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/locations/{ev_charger.location_id}")
    assert rs.status_code == 404
    rs = client.get("/api/v1/ev-chargers", params={"location_id": ev_charger.location_id})
    assert rs.json()["founds"].__len__() == 0
