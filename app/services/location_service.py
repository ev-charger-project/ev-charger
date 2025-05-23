from typing import Any, List

from app.core.config import configs
from app.model.location_elastic import LocationElastic
from app.repository import LocationRepository
from app.repository.elastic_repository import ElasticsearchRepository
from app.schema.base_schema import FindResult
from app.schema.ev_charger_port_schema import (
    DetailedEVChargerPortResponseWithoutEVCharger,
)
from app.schema.ev_charger_schema import EVChargerResponseWithEVChargerPort
from app.schema.gg_map_schema import DirectionRequest
from app.schema.location_schema import (
    CreateEditLocation,
    DetailedLocationResponse,
    FindLocation,
    LocationByRadiusQuery,
    LocationResponse,
    SearchLocation,
)
from app.services.base_service import BaseService
from app.services.gg_map_service import GGMapService
from app.util.calculate_polygon import create_polygon_from_line


class LocationService(BaseService):
    def __init__(
        self,
        location_repository: LocationRepository,
        es_repository: ElasticsearchRepository,
        gg_map_service: GGMapService,
    ):
        self.location_repository = location_repository
        self.es_repository = es_repository
        self.gg_map_service = gg_map_service
        super().__init__(location_repository)

    def get_by_id(self, id: str):
        return self.location_repository.read_by_id(id)

    def __get_ev_charger_port_details(
        self, ev_charger_ports: list[DetailedEVChargerPortResponseWithoutEVCharger]
    ):

        charger_types: list[dict[str, Any]] = [
            {
                "type": f"{ev_charger_port.power_plug_type.plug_type} - {ev_charger_port.power_plug_type.power_model}",
                "power_output": ev_charger_port.power_output.output_value,
            }
            for ev_charger_port in ev_charger_ports
        ]

        return charger_types

    def __get_ev_charger_port_details_with_count(
        self, ev_chargers: list[EVChargerResponseWithEVChargerPort]
    ):
        charger_types: list[dict[str, Any]] = []
        station_count: int = 0
        for ev_charger in ev_chargers:
            charger_types.extend(
                self.__get_ev_charger_port_details(ev_charger.ev_charger_ports)
            )
            station_count += 1
        return {"charger_types": charger_types, "station_count": station_count}

    def sync_elastic_data(self) -> None:
        self.es_repository.wipe_data(configs.ES_LOCATION_INDEX)
        locations_data: FindResult[DetailedLocationResponse] = (
            self.location_repository.read_by_options(
                FindLocation(), detailed=True, disable_pagination=True
            )
        )

        locations_elastic = [
            {
                "_index": configs.ES_LOCATION_INDEX,
                "_id": str(location.id),
                "_source": {
                    **LocationElastic(
                        id=str(location.id),
                        **location.model_dump(exclude={"id"}),
                        location=f"{location.latitude}, {location.longitude}",
                    ).model_dump(exclude={"ev_chargers", "working_days"}),
                    "working_days": [
                        {
                            "day": wd.day,
                            "open_time": wd.open_time.strftime(configs.TIME_FORMAT),
                            "close_time": wd.close_time.strftime(configs.TIME_FORMAT),
                        }
                        for wd in location.working_days
                    ],
                    "amenities": [
                        location_amenities.amenities.amenities_types
                        for location_amenities in location.location_amenities
                    ],
                    **self.__get_ev_charger_port_details_with_count(
                        location.ev_chargers
                    ),
                },
            }
            for location in locations_data.founds
        ]
        self.es_repository.bulk_create_documents(
            configs.ES_LOCATION_INDEX, locations_elastic
        )

    def get_by_radius(self, schema: LocationByRadiusQuery):
        return self.location_repository.read_by_radius(schema)

    def search_nearby_location(self, schema: LocationByRadiusQuery):
        return self.es_repository.search_nearby_location(schema)

    def search_by_elastic(
        self,
        searchlocation: SearchLocation,
        is_fuzzi: bool,
        charger_type: List[str],
        amenities: List[str],
    ) -> List[LocationResponse]:
        return self.es_repository.search_location(
            searchlocation, is_fuzzi, charger_type, amenities
        )

    def add(self, schema: CreateEditLocation):
        location = self.location_repository.create(schema)

        location_elastic = LocationElastic(
            id=str(location.id),
            **location.model_dump(exclude={"id"}),
            location=f"{location.latitude}, {location.longitude}",
        )
        # self.es_repository.create_document(
        #     index_name=configs.ES_LOCATION_INDEX,
        #     doc_id=str(location.id),
        #     body={
        #         **location_elastic.model_dump(exclude={"ev_chargers", "working_days", "location_amenities"}),
        #         "working_days": [
        #             {
        #                 "day": wd.day,
        #                 "open_time": wd.open_time.strftime(configs.TIME_FORMAT),
        #                 "close_time": wd.close_time.strftime(configs.TIME_FORMAT),
        #             }
        #             for wd in schema.working_days
        #         ],
        #         "amenities": [location_amenities.amenities.amenities_types for location_amenities in location.location_amenities],
        #     },
        # )

        return location

    def patch(self, id: str, schema: CreateEditLocation):
        location = self.location_repository.update(id, schema)
        update_fields = {
            **location.model_dump(
                exclude={"ev_chargers", "working_days", "location_amenities"}
            ),
            "working_days": [
                {
                    "day": wd.day,
                    "open_time": wd.open_time.strftime(configs.TIME_FORMAT),
                    "close_time": wd.close_time.strftime(configs.TIME_FORMAT),
                }
                for wd in location.working_days
            ],
            "amenities": [
                location_amenities.amenities.amenities_types
                for location_amenities in location.location_amenities
            ],
        }

        self.es_repository.update_document(
            index=configs.ES_LOCATION_INDEX, doc_id=id, update_fields=update_fields
        )
        return location

    def soft_remove_by_id(self, id):

        self._repository.soft_delete_by_id(id)
        self.es_repository.delete_document(configs.ES_LOCATION_INDEX, doc_id=str(id))

    def get_location_by_direction(self, direction: DirectionRequest):
        directions = self.gg_map_service.get_directions(direction)

        coordinates = create_polygon_from_line(directions.coordinates)

        locations = self.es_repository.search_location_on_direction(coordinates)

        directions.locations = locations

        return directions

    def wipe_locations_data(self):
        self.location_repository.wipe_locations_data()
        self.es_repository.wipe_data(configs.ES_LOCATION_INDEX)
