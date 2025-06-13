import math
import logging

from server.services.ev_data.ev_charger_upsert import create_ev_chargers_from_data
from server.services.ev_data.location_upsert import create_locations_from_data
from server.services.here.here_api import get_here_ev_data

logger = logging.getLogger(__name__)
CENTER_LAT = 34.0522
CENTER_LON = -118.2437
LAT_RANGE = 0.4  # ~45km N-S
LON_RANGE = 0.7  # ~70km E-W
RADIUS_KM = 10
STEP_KM = 8


def generate_grid(center_lat, center_lon, lat_range, lon_range, step_km):
    lat_step = step_km / 111
    lon_step = step_km / (111 * math.cos(math.radians(center_lat)))
    lat_points = int(lat_range / lat_step) + 1
    lon_points = int(lon_range / lon_step) + 1
    grid = []
    for i in range(lat_points):
        for j in range(lon_points):
            lat = center_lat - lat_range / 2 + i * lat_step
            lon = center_lon - lon_range / 2 + j * lon_step
            grid.append((lat, lon))
    return grid


# def fetch_here_ev_data_at(lat, lon, radius_km):
#     return get_here_ev_data(lat=lat, lon=lon, radius_km=radius_km)


# def fetch_all_la_ev_data():
#     grid = generate_grid(CENTER_LAT, CENTER_LON, LAT_RANGE, LON_RANGE, STEP_KM)
#     all_items = {}
#     for lat, lon in grid:
#         data = fetch_here_ev_data_at(lat, lon, RADIUS_KM)
#         for item in data.get("items", []):
#             ext_id = item.get("id")
#             if ext_id not in all_items:
#                 all_items[ext_id] = item
#     return {"items": list(all_items.values())}


def fetch_and_upsert_la_ev_data(
    location_service, ev_charger_service, power_plug_type_service, power_output_service
):
    grid = generate_grid(CENTER_LAT, CENTER_LON, LAT_RANGE, LON_RANGE, STEP_KM)
    seen_ids = set()

    def process_cell(lat, lon, radius_km):
        logger.info(f"Processing cell at ({lat},{lon}), r={radius_km}km")
        data = get_here_ev_data(lat=lat, lon=lon, radius_km=radius_km)
        items = data.get("items", [])
        # Keep track of how many unique items we have seen
        if not items:
            logger.info(f"No items found at ({lat},{lon}), r={radius_km}km")
            return
        new_items = []
        for item in items:
            ext_id = item.get("id")
            if ext_id not in seen_ids:
                seen_ids.add(ext_id)
                new_items.append(item)
        logger.info(f"Fetched {len(items)} items at ({lat},{lon}), r={radius_km}km")
        # Upsert as soon as you get data
        locations_and_items = create_locations_from_data(
            location_service, {"items": items}
        )
        create_ev_chargers_from_data(
            locations_and_items,
            ev_charger_service,
            power_plug_type_service,
            power_output_service,
        )
        # If dense, subdivide
        if len(items) >= 100 and radius_km > 2:
            logger.info(f"Subdividing cell at ({lat},{lon}), r={radius_km}km")
            for dlat in [-0.25, 0, 0.25]:
                for dlon in [-0.25, 0, 0.25]:
                    if dlat == 0 and dlon == 0:
                        continue
                    process_cell(
                        lat + dlat * radius_km / 111,
                        lon + dlon * radius_km / (111 * math.cos(math.radians(lat))),
                        radius_km / 2,
                    )

    for lat, lon in grid:
        process_cell(lat, lon, RADIUS_KM)
        # Log number of unique items seen so far
        logger.info(f"Total unique items seen: {len(seen_ids)}")
