from httpx import Response
from starlette.testclient import TestClient

from app.schema.city_schema import CreateEditCity
from app.schema.district_schema import CreateEditDistrict
from tests.data.city import create_city


def get_district_test_data(client: TestClient):
    city_id_1 = create_city(
        client,
        CreateEditCity(name="Thành phố Hồ Chí Minh", country="Vietnam", districts=[]),
    ).json()["id"]
    city_id_2 = create_city(
        client,
        CreateEditCity(name="Thành phố Hà Nội", country="Vietnam", districts=[]),
    ).json()["id"]
    return [
        CreateEditDistrict(city_id=city_id_1, name="Quận 1"),
        CreateEditDistrict(city_id=city_id_1, name="Quận 2"),
        CreateEditDistrict(city_id=city_id_1, name="Quận 3"),
        CreateEditDistrict(city_id=city_id_2, name="Quận Long Biên"),
    ]


def create_district_wrong_input(client: TestClient, missing_data) -> Response:
    return client.post("/api/v1/districts", json=missing_data)


def create_district(client: TestClient, district: CreateEditDistrict) -> Response:
    result = client.post(
        "/api/v1/districts",
        json=district.model_dump(mode="json"),
    )
    return result
