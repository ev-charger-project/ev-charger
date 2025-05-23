from starlette.testclient import TestClient

from tests.data.amenities import create_amenities, get_amenities_test_data


def test_create_amenities(client: TestClient):
    amenities = get_amenities_test_data()[0]
    rs = create_amenities(client, amenities)
    assert rs.status_code == 201


def test_create_with_missing_data(client: TestClient):
    invalid_data = get_amenities_test_data()[0].model_dump().clear()
    rs = client.post("/api/v1/amenities", json=invalid_data)
    assert rs.status_code == 422


def test_create_with_invalid_data_type(client: TestClient):
    invalid_data = get_amenities_test_data()[0]
    invalid_data.amenities_types = 0
    rs = create_amenities(client, invalid_data)
    assert rs.status_code == 422


def test_get_amenities(client: TestClient):
    amenities = get_amenities_test_data()[0]
    rs = create_amenities(client, amenities)
    rs = client.get(f"/api/v1/amenities/{rs.json()['id']}")
    assert rs.status_code == 200

    assert "id" in rs.json()
    assert amenities.amenities_types == rs.json()["amenities_types"]


def test_paginate_with_specified_page_size(client: TestClient):
    amenities = get_amenities_test_data()
    for amenities in amenities:
        create_amenities(client, amenities)
    rs = client.get("/api/v1/amenities?page=1&page_size=1")
    assert rs.status_code == 200
    assert len(rs.json()["founds"]) == 1


def test_get_paginated_amenities(client: TestClient):
    amenities = get_amenities_test_data()
    for amenities in amenities:
        create_amenities(client, amenities)
    rs = client.get("/api/v1/amenities")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 4


def test_update_amenities(client: TestClient):
    amenities = get_amenities_test_data()[0]
    rs = create_amenities(client, amenities)
    amenities = get_amenities_test_data()[1]
    rs = client.patch(f"/api/v1/amenities/{rs.json()['id']}", json=amenities.model_dump(mode="json"))
    assert rs.status_code == 200


def test_update_with_non_existent_id(client: TestClient):
    amenities = get_amenities_test_data()[0]
    rs = client.patch("/api/v1/amenities/0d49f0ef-a030-4710-8364-4e3a7f348953", json=amenities.model_dump(mode="json"))
    assert rs.status_code == 404


def test_delete_amenities(client: TestClient):
    amenities = get_amenities_test_data()[0]
    result = create_amenities(client, amenities)
    rs = client.delete(f"/api/v1/amenities/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/amenities/{result.json()['id']}")
    assert rs.status_code == 404
