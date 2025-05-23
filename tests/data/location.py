from httpx import Response
from starlette.testclient import TestClient

from app.schema.location_schema import CreateEditLocation, WorkingDay


def get_location_test_data():
    return [
        CreateEditLocation(
            location_name="Agest",
            street="456 Hoang Van Thu",
            district="Tan Binh",
            city="HCMC",
            country="Vietnam",
            postal_code="VN",
            latitude=40,
            longitude=50,
            working_days=[
                WorkingDay(
                    day=1,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=2,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=3,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=4,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
            ],
            pricing="test",
            phone_number="0945157286",
            parking_level="B3",
        ),
        CreateEditLocation(
            location_name="Agest 2",
            street="456 Ngo Quyen",
            district="10",
            city="Ha Noi",
            country="Vietnam",
            postal_code="US",
            latitude=25.5,
            longitude=12.2,
            working_days=[
                WorkingDay(
                    day=1,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=2,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=3,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=4,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
            ],
            pricing="test",
            phone_number="0956438275",
            parking_level="B2",
        ),
        CreateEditLocation(
            location_name="Vincom Ha Nam",
            street="456 Nguyen Van A",
            district="2",
            city="Ha Noi",
            country="Vietnam",
            postal_code="VN",
            latitude=80,
            longitude=50,
            working_days=[
                WorkingDay(
                    day=1,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=2,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=3,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
                WorkingDay(
                    day=4,
                    open_time="06:00:00.000000",
                    close_time="09:00:00.000000",
                ),
            ],
            pricing="test",
            phone_number="0841275398",
            parking_level="3",
        ),
    ]


def create_location_wrong_input(client: TestClient, missing_data) -> Response:
    return client.post("/api/v1/locations", json=missing_data)


def create_location(client: TestClient, location: CreateEditLocation) -> Response:
    result = client.post(
        "/api/v1/locations",
        json=location.model_dump(mode="json"),
    )
    return result
