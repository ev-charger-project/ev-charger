from starlette.testclient import TestClient

from tests.data.city import create_city, get_city_test_data


def test_create_city(client: TestClient):
    city = get_city_test_data()[0]
    rs = create_city(client, city)
    assert rs.status_code == 201


def test_get_city(client: TestClient):
    city = get_city_test_data()[0]
    rs = create_city(client, city)
    rs = client.get(f"/api/v1/cities/{rs.json()['id']}")
    assert rs.status_code == 200


def test_get_city_by_country_vn(client: TestClient):
    cities = get_city_test_data()
    for city in cities:
        create_city(client, city)
    rs = client.get(
        "/api/v1/cities",
        params={
            "country": "Vietnam",
            "order_by": "updated_at",
            "ordering": "asc",
        },
    )
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 3
    assert items[0]["name"] == cities[0].name
    assert items[1]["name"] == cities[1].name
    assert items[2]["name"] == cities[2].name
    rs = client.get(
        "/api/v1/cities",
        params={
            "country": "United States",
            "order_by": "updated_at",
            "ordering": "asc",
        },
    )
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert items[0]["name"] == cities[3].name
    assert items[1]["name"] == cities[4].name
    assert len(items) == 2


def test_get_district_by_city(client: TestClient):
    cities = get_city_test_data()
    for city in cities:
        create_city(client, city)
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
    assert items[0]["name"] == cities[0].districts[0].name
    assert items[1]["name"] == cities[0].districts[1].name
    assert items[2]["name"] == cities[0].districts[2].name
    assert len(items) == 3
    rs = client.get(
        "/api/v1/districts",
        params={"city": "California", "order_by": "updated_at", "ordering": "asc"},
    )
    assert rs.status_code == 200

    items = rs.json()["founds"]
    assert items[0]["name"] == cities[3].districts[0].name
    assert items[1]["name"] == cities[3].districts[1].name
    assert len(items) == 2


def test_get_paginated_city(client: TestClient):
    city = get_city_test_data()
    for city in city:
        create_city(client, city)
    rs = client.get("/api/v1/cities")
    assert rs.status_code == 200
    items = rs.json()["founds"]
    assert len(items) == 5


def test_update_city(client: TestClient):
    city = get_city_test_data()[0]
    rs = create_city(client, city)
    city = get_city_test_data()[1]
    rs = client.patch(f"/api/v1/cities/{rs.json()['id']}", json=city.model_dump(mode="json"))
    assert rs.status_code == 200


def test_update_city_record_not_exist(client: TestClient):
    city = get_city_test_data()[0]
    rs = create_city(client, city)
    city = get_city_test_data()[1]
    rs = client.patch(
        f"/api/v1/cities/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}",
        json=city.model_dump(mode="json"),
    )
    assert rs.status_code == 404


def test_delete_city_record_not_exist(client: TestClient):
    rs = client.delete(f"/api/v1/cities/{'7d87be60-fd8b-41fa-a86b-32d6ce1ba8b3'}")
    assert rs.status_code == 404


def test_delete_city(client: TestClient):
    city = get_city_test_data()[0]
    result = create_city(client, city)
    rs = client.delete(f"/api/v1/cities/{result.json()['id']}")
    assert rs.status_code == 200
    rs = client.get(f"/api/v1/cities/{result.json()['id']}")
    assert rs.status_code == 404
