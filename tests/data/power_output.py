from httpx import Response
from starlette.testclient import TestClient

from app.schema.power_output_schema import CreatePowerOutput


def get_power_output_test_data():
    return [
        CreatePowerOutput(
            output_value=1,
            charging_speed="Fast",
            voltage=1,
            description="test",
        ),
        CreatePowerOutput(
            output_value=2,
            charging_speed="Slow",
            voltage=2,
            description="test",
        ),
        CreatePowerOutput(
            output_value=3,
            charging_speed="Ultra-Fast",
            voltage=3,
            description="test",
        ),
    ]


def create_power_output(client: TestClient, power_output: CreatePowerOutput) -> Response:
    result = client.post(
        "/api/v1/power-outputs",
        json=power_output.model_dump(),
    )
    return result
