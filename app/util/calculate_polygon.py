from geopandas import GeoSeries
from shapely import LineString
from shapely.geometry import mapping

from app.schema.google_api_schema import Coordinate


def create_polygon_from_line(coordinates: list[Coordinate]):
    line_string = LineString([(c.lat, c.lng) for c in coordinates])
    geo_series = GeoSeries(line_string)
    buffered_line = geo_series.buffer(0.01, join_style="bevel", resolution=1, cap_style="square")
    poly = buffered_line.array[0]
    polygon: list[Coordinate] = []
    for lat, lon in mapping(poly)["coordinates"][0]:
        polygon.append(Coordinate(lat=lat, lng=lon))
    return polygon
