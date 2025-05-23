from httpx import Response
from starlette.testclient import TestClient

from app.schema.city_schema import CreateEditCity
from app.schema.district_schema import BaseDistrict


def get_city_test_data():
    return [
        CreateEditCity(
            name="Thành phố Hồ Chí Minh",
            country="Vietnam",
            districts=[BaseDistrict(name="Quận 1"), BaseDistrict(name="Quận 2"), BaseDistrict(name="Quận 3")],
        ),
        CreateEditCity(
            name="Thành phố Hà Nội",
            country="Vietnam",
            districts=[BaseDistrict(name="Quận Long Biên"), BaseDistrict(name="Quận Cam"), BaseDistrict(name="Quận Ngọc Hải")],
        ),
        CreateEditCity(
            name="Tỉnh Khánh Hòa", country="Vietnam", districts=[BaseDistrict(name="Quận Hòa"), BaseDistrict(name="Quận Không Tên")]
        ),
        CreateEditCity(
            name="California", country="United States", districts=[BaseDistrict(name="Orange District"), BaseDistrict(name="Blue District")]
        ),
        CreateEditCity(name="Washington", country="United States", districts=[BaseDistrict(name="Unknown")]),
    ]


def create_city_wrong_input(client: TestClient, missing_data) -> Response:
    return client.post("/api/v1/cities", json=missing_data)


def create_city(client: TestClient, city: CreateEditCity) -> Response:
    result = client.post(
        "/api/v1/cities",
        json=city.model_dump(mode="json"),
    )
    return result
