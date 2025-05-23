from httpx import Response
from starlette.testclient import TestClient

from app.schema.amenities_schema import CreateAmenities


def get_amenities_test_data():
    return [
        CreateAmenities(amenities_types="Dining", image_url="abc.png"),
        CreateAmenities(amenities_types="Sleeping", image_url="defg.png"),
        CreateAmenities(amenities_types="Shopping", image_url="hijk.png"),
        CreateAmenities(amenities_types="Restroom", image_url="lmnop.png"),
    ]


def create_amenities(client: TestClient, amenities: CreateAmenities) -> Response:
    result = client.post(
        "/api/v1/amenities",
        json=amenities.model_dump(),
    )
    return result
