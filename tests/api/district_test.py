from starlette.testclient import TestClient

from tests.data.district import create_district, get_district_test_data


def test_create_district(client: TestClient):
    district = get_district_test_data(client)[0]
    rs = create_district(client, district)
    assert rs.status_code == 201


def test_get_district(client: TestClient):
    district = get_district_test_data(client)[0]
    rs = create_district(client, district)
    rs = client.get(f"/api/v1/districts/{rs.json()['id']}")
    assert rs.json()["name"] == district.name
    assert rs.status_code == 200


def test_get_district_by_city(client: TestClient):
    districts = get_district_test_data(client)
    for district in districts:
        create_district(client, district)
    rs = client.get(
        "/api/v1/districts",
        params={
            "city": "Thành phố Hồ Chí Minh",
            "order_by": "updated_at",
            "ordering": "asc",
        },
    )
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert items[0]["name"] == districts[0].name
    assert items[1]["name"] == districts[1].name
    assert items[2]["name"] == districts[2].name
    assert len(items) == 3
    rs = client.get(
        "/api/v1/districts",
        params={
            "city": "Thành phố Hà Nội",
            "order_by": "updated_at",
            "ordering": "asc",
        },
    )
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert items[0]["name"] == districts[3].name
    assert len(items) == 1


def test_get_paginated_district(client: TestClient):
    districts = get_district_test_data(client)
    for district in districts:
        create_district(client, district)
    rs = client.get("/api/v1/districts")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 4


def test_update_district(client: TestClient):
    district = get_district_test_data(client)[0]
    rs = create_district(client, district)
    district = get_district_test_data(client)[1]
    rs = client.patch(
        f"/api/v1/districts/{rs.json()['id']}",
        json=district.model_dump(mode="json"),
    )
    assert rs.status_code == 200


def test_update_district_record_not_exist(client: TestClient):
    district = get_district_test_data(client)[0]
    rs = create_district(client, district)
    district = get_district_test_data(client)[1]
    rs = client.patch(
        f"/api/v1/districts/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}",
        json=district.model_dump(mode="json"),
    )
    assert rs.status_code == 404


def test_delete_district_record_not_exist(client: TestClient):
    rs = client.delete(f"/api/v1/districts/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}")
    assert rs.status_code == 404


def test_delete_district(client: TestClient):
    district = get_district_test_data(client)[0]
    result = create_district(client, district)
    rs = client.delete(f"/api/v1/districts/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/districts/{result.json()['id']}")
    assert rs.status_code == 404
