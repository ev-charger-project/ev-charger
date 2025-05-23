from starlette.testclient import TestClient

from tests.data.location_amenities import get_location_amenities_test_data

URL = "/api/v1/location-amenities"


def create_location_amenities(client: TestClient):
    location_amenities = get_location_amenities_test_data(client)[0]
    result = client.post(url=URL, json=location_amenities.model_dump(mode="json"))
    return result


def test_create_location_amenities(client: TestClient):
    rs = create_location_amenities(client)
    assert rs.status_code == 201


def test_get_location_amenities(client: TestClient):
    location_amenities = create_location_amenities(client)
    rs = client.get(url=f"{URL}/{location_amenities.json()['id']}")
    assert rs.status_code == 200
    assert "id" in rs.json()


def test_update_location_amenities(client: TestClient):
    location_amenities = create_location_amenities(client)
    location_amenities_data = location_amenities.json()
    rs = client.patch(url=f"{URL}/{location_amenities.json()['id']}", json=location_amenities_data)

    assert rs.status_code == 200


def test_delete_location_amenities(client: TestClient):
    location_amenities = create_location_amenities(client).json()
    rs = client.delete(url=f"{URL}/{location_amenities['id']}")

    assert rs.status_code == 200

    rs = client.get(url=f"{URL}/{location_amenities['id']}")
    assert rs.status_code == 404
