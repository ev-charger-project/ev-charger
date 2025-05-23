from datetime import date

from httpx import Response
from starlette.testclient import TestClient

from app.schema.ev_charger_schema import CreateEVCharger
from tests.data.location import create_location, get_location_test_data


def get_ev_charger_test_data(client: TestClient):
    location_id = create_location(client, get_location_test_data()[0]).json()["id"]
    return [
        CreateEVCharger(
            location_id=location_id,
            station_name="Vincom Station",
            availability="available",
            installation_date=date(2024, 7, 2),
            last_maintenance_date=date(2024, 7, 11),
        ),
        CreateEVCharger(
            location_id=location_id,
            station_name="Agest Charger",
            availability="in use",
            installation_date=date(2024, 7, 5),
            last_maintenance_date=date(2024, 7, 8),
        ),
        CreateEVCharger(
            location_id=location_id,
            station_name="EA Chargers",
            availability="out of order",
            installation_date=date(2024, 7, 5),
            last_maintenance_date=date(2024, 7, 8),
        ),
    ]


def create_ev_charger_wrong_input(client: TestClient, missing_data) -> Response:
    return client.post("/api/v1/ev-chargers", json=missing_data)


def create_ev_charger(client: TestClient, ev_charger: CreateEVCharger) -> Response:
    result = client.post(
        "/api/v1/ev-chargers",
        json=ev_charger.model_dump(mode="json"),
    )
    return result
