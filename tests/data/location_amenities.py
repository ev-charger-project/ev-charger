from starlette.testclient import TestClient

from app.schema.location_amenities_schema import CreateLocationAmenities
from tests.data.amenities import create_amenities, get_amenities_test_data
from tests.data.location import create_location, get_location_test_data


def get_location_amenities_test_data(client: TestClient):
    amenities_id = create_amenities(client, get_amenities_test_data()[0]).json()["id"]
    location_id = create_location(client, get_location_test_data()[0]).json()["id"]

    return [
        CreateLocationAmenities(location_id=location_id, amenities_id=amenities_id),
        CreateLocationAmenities(location_id=location_id, amenities_id=amenities_id),
    ]
