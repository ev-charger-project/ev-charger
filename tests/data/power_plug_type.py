from httpx import Response
from starlette.testclient import TestClient

from app.schema.power_plug_type_schema import CreatePowerPlugType


def get_power_plug_type_test_data():
    return [
        CreatePowerPlugType(
            power_model="AC",
            plug_type="SAE J1772",
            plug_image_url="example.png",
            additional_note="Supports fast charging up to 350 kW.",
            power_plug_region="Tesla vehicles",
        ),
        CreatePowerPlugType(
            power_model="DC",
            plug_type="IEC 62196",
            plug_image_url="example.jpg",
            additional_note="Compatible with both 110V and 220V outlets.",
            power_plug_region="Nissan Leaf",
        ),
        CreatePowerPlugType(
            power_model="AC",
            plug_type="SAE J1772",
            plug_image_url="example1.png",
            additional_note="Supports fast charging up to 350 kW.",
            power_plug_region="Europe",
        ),
        CreatePowerPlugType(
            power_model="AC",
            plug_type="SAE J1772",
            plug_image_url="example1.png",
            additional_note="Supports fast charging up to 350 kW.",
            power_plug_region="Europe",
        ),
    ]


def create_power_plug_type(client: TestClient, power_plug_type: CreatePowerPlugType) -> Response:
    result = client.post(
        "/api/v1/power-plug-types",
        json=power_plug_type.model_dump(),
    )
    return result
