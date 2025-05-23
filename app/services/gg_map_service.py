import requests
from fastapi import HTTPException, status

from app.core.config import configs
from app.schema.gg_map_schema import DirectionRequest
from app.schema.google_api_schema import RouteResponse


class GGMapService:
    def __init__(self) -> None:
        self.base_url = "https://maps.googleapis.com/maps/api"
        pass

    def get_directions(self, direction: DirectionRequest):
        direction_url = f"{self.base_url}/directions/json"

        params = {
            "origin": f"{direction.start_lat},{direction.start_long}",
            "destination": f"{direction.end_lat},{direction.end_long}",
            "key": configs.GOOGLE_MAPS_API_KEY,
            "mode": "driving",
        }

        try:
            response = requests.get(direction_url, params=params)

            directions = []
            if response.json().get("routes").__len__() == 0:
                return directions
            steps = response.json().get("routes")[0].get("legs")[0].get("steps")

            directions.append(steps[0].get("start_location"))
            for step in steps:
                directions.append(step.get("end_location"))

            overview_polyline = response.json().get("routes")[0].get("overview_polyline").get("points")

            return RouteResponse(coordinates=directions, overview_polyline=overview_polyline)

        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
