from pydantic import BaseModel, Field


class DirectionRequest(BaseModel):
    start_lat: float = Field(ge=-90, le=90, examples=10.7961894, description="Latitude of start point")
    start_long: float = Field(ge=-180, le=180, examples=106.633319, description="Longitude of start point")
    end_lat: float = Field(ge=-90, le=90, examples=10.7961894, description="Latitude of end point")
    end_long: float = Field(ge=-180, le=180, examples=106.633319, description="Longitude of end point")
