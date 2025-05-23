import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from app.constant.enum.status import LocationStatusEnum
from app.core.config import configs
from app.core.exceptions import NotFoundError
from app.model.location_elastic import mapping as location_elastic_mapping
from app.schema.google_api_schema import Coordinate
from app.schema.location_schema import (
    LocationByRadiusQuery,
    LocationResponse,
    SearchLocation,
)


class ElasticsearchRepository:
    def __init__(self, es_client: Elasticsearch) -> None:
        self.es_client = es_client

    def bulk_create_documents(self, index_name: str, body: list[dict[str, Any]]) -> None:
        if not self.es_client.indices.exists(index=index_name):
            self.es_client.indices.create(index=index_name, body=location_elastic_mapping)

        try:
            bulk(self.es_client, body, refresh=True)
        except Exception as e:
            raise RuntimeError(f"Failed to bulk create document: {e}")

    def create_document(self, index_name: str, doc_id: str, body: dict) -> dict:
        if not self.es_client.indices.exists(index=index_name):
            self.es_client.indices.create(index=index_name, body=location_elastic_mapping)

        try:
            response = self.es_client.index(index=index_name, id=doc_id, body=body)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to index document: {e}")

    def get_document(self, index: str, doc_id: str) -> Optional[dict]:
        try:
            response = self.es_client.get(index=index, id=doc_id)
            return response["_source"]
        except Exception as e:
            raise RuntimeError(f"Failed to get document: {e}")

    def update_document(self, index: str, doc_id: str, update_fields: Dict[str, Any]) -> None:
        try:
            update_body = {"doc": update_fields}
            self.es_client.update(index=index, id=doc_id, body=update_body)
        except Exception as e:
            raise RuntimeError(f"Failed to update document: {e}")

    def delete_document(self, index: str, doc_id: str) -> dict:
        try:
            response = self.es_client.delete(index=index, id=doc_id)
            return response
        except Exception as e:
            raise RuntimeError(f"Failed to delete document: {e}")

    def change_station_count(self, index: str, doc_id: str, number_of_station: int = 1) -> None:
        try:
            update_body = {
                "script": {
                    "source": """
                        if (ctx._source.station_count == null) {
                            ctx._source.station_count = 1;
                        } else {
                            ctx._source.station_count += params.number_of_station;
                        }
                    """,
                    "params": {"number_of_station": number_of_station},
                }
            }
            self.es_client.update(index=index, id=doc_id, body=update_body)
        except Exception as e:
            raise RuntimeError(f"Failed to update document: {e}")

    def add_charger_type_and_power_output(self, index: str, doc_id: str, charger_types, number_of_station: int = 0) -> None:
        try:
            if not self.es_client.exists(index=index, id=doc_id):
                raise RuntimeError(f"Document with ID {doc_id} does not exist in index {index}.")

            update_body = {
                "script": {
                    "source": """
                                    if (ctx._source.charger_types == null) {
                                        ctx._source.charger_types = params.charger_types;
                                    } else {
                                        ctx._source.charger_types.addAll(params.charger_types);
                                    }

                                    if (ctx._source.station_count == null) {
                                        ctx._source.station_count = params.number_of_station;
                                    } else {
                                        ctx._source.station_count += params.number_of_station;
                                    }
                                """,
                    "params": {"charger_types": charger_types, "number_of_station": number_of_station},
                }
            }

            self.es_client.update(index=index, id=doc_id, body=update_body)

        except Exception as e:
            raise RuntimeError(f"Failed to update document: {e}")

    def check_special_chars(self, value: str, max_special_chars: int = 2) -> bool:
        if value is None:
            return False
        special_chars = re.findall(r"[^\w\s]", value)
        return len(special_chars) > max_special_chars

    def check_special_word(self, value: str) -> bool:
        if value is None:
            return False
        words = re.findall(r"\b\w+\b", value)
        return any(len(word) > 9 for word in words)

    def __calculate_status(self, working_hours: list, current_day: int, current_time) -> str:

        if not working_hours:
            return LocationStatusEnum.CLOSE

        working_hours.sort(key=lambda x: x["day"])

        left, right, mid = 0, working_hours.__len__() - 1, 0

        while left <= right:
            mid = (left + right) // 2
            if working_hours[mid]["day"] == current_day:
                break
            elif working_hours[mid]["day"] < current_day:
                left = mid + 1
            else:
                right = mid - 1

        if working_hours[mid]["day"] != current_day:
            return LocationStatusEnum.CLOSE

        start = datetime.strptime(working_hours[mid]["open_time"], configs.TIME_FORMAT)
        end = datetime.strptime(working_hours[mid]["close_time"], configs.TIME_FORMAT)

        if start.time() <= current_time <= end.time():
            return LocationStatusEnum.OPEN
        else:
            return LocationStatusEnum.CLOSE

    def search_location(
        self,
        searchlocation: SearchLocation,
        is_fuzzi: bool = False,
        charger_type: List[str] = [],
        amenities: List[str] = [],
    ) -> List[LocationResponse]:
        query = searchlocation.query
        station_count = searchlocation.station_count
        power_output_gte = searchlocation.power_output_gte
        power_output_lte = searchlocation.power_output_lte
        radius = searchlocation.radius

        if self.check_special_chars(query):
            return []
        if self.check_special_word(query):
            return []

        must_queries = []

        if charger_type:
            should_clauses = [{"match_phrase": {"charger_types.type": ctype}} for ctype in charger_type]
            must_queries.append(
                {"nested": {"path": "charger_types", "query": {"bool": {"should": should_clauses, "minimum_should_match": 1}}}}
            )

        if power_output_gte is not None or power_output_lte is not None:
            must_queries.append(
                {
                    "nested": {
                        "path": "charger_types",
                        "query": {
                            "bool": {
                                "must": [{"range": {"charger_types.power_output": {"gte": power_output_gte, "lte": power_output_lte}}}]
                            }
                        },
                    }
                }
            )

        if station_count:
            must_queries.append({"range": {"station_count": {"gte": station_count}}})

        if radius is not None:
            must_queries.append(
                {"geo_distance": {"distance": f"{radius}km", "location": {"lat": searchlocation.lat, "lon": searchlocation.lon}}}
            )

        if amenities:
            must_queries.append({"terms": {"amenities": amenities}})

        es_query = {
            "query": {
                "bool": {
                    "must": must_queries,
                    **(
                        {
                            "should": [
                                {"wildcard": {"location_name": {"value": f"{query}*", "boost": 2.0}}},
                                {"wildcard": {"street": {"value": f"{query}*", "boost": 1.0}}},
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["location_name", "street", "district", "city", "country"],
                                        **({"fuzziness": "AUTO"} if is_fuzzi else {}),
                                    }
                                },
                            ],
                            "minimum_should_match": 1,
                        }
                        if query is not None
                        else {"filter": {"match_all": {}}}
                    ),
                }
            },
            **(
                {"sort": [{"_geo_distance": {"location": {"lat": searchlocation.lat, "lon": searchlocation.lon}, "order": "asc"}}]}
                if searchlocation.lat is not None and searchlocation.lon is not None
                else {}
            ),
            "size": 10 if query is not None else 500,
        }

        try:
            response = self.es_client.search(index=configs.ES_LOCATION_INDEX, body=es_query)
            hits = response["hits"]["hits"]
            results = self.__process_search_results_location_list(hits)
        except Exception as e:
            raise NotFoundError(detail=str(e))

        return results

    def search_nearby_location(self, schema: LocationByRadiusQuery) -> List[LocationResponse]:

        es_query = {
            "query": {
                "geo_distance": {"distance": str(schema.radius) + "km", "location": {"lat": schema.user_lat, "lon": schema.user_long}}
            }
        }
        try:
            response = self.es_client.search(index=configs.ES_LOCATION_INDEX, body=es_query)
            hits = response["hits"]["hits"]
            results = self.__process_search_results_location_list(hits)
        except Exception as e:
            raise NotFoundError(detail=str(e))

        return results

    def __process_search_results_location_list(self, hits) -> List[LocationResponse]:
        results = []

        current_day = datetime.now(pytz.utc).isoweekday()
        current_time = datetime.now().time()

        for hit in hits:
            source = hit["_source"]
            working_hours = source.get("working_days", [])

            status = self.__calculate_status(working_hours, current_day, current_time)
            source["status"] = status

            results.append(LocationResponse(**source))

        return results

    def update_charger_type_and_power_output(self, index, location_id, charger_types, types_to_remove) -> None:
        try:
            if not self.es_client.exists(index=index, id=location_id):
                raise RuntimeError(f"Document with ID {location_id} does not exist in index {index}.")

            update_body = {
                "script": {
                    "source": """

                                if (ctx._source.charger_types == null) {
                                    ctx._source.charger_types = params.charger_types;
                                } else {
                                    def types_to_remove = params.types_to_remove;

                                    for (def type_to_remove : types_to_remove) {
                                        for (int i = 0; i < ctx._source.charger_types.size(); i++) {
                                            def charger = ctx._source.charger_types[i];
                                            if (charger.power_output == type_to_remove.power_output && charger.type == type_to_remove.type) {
                                                ctx._source.charger_types.remove(i);
                                                break;
                                            }
                                        }
                                    }

                                    ctx._source.charger_types.addAll(params.charger_types);
                                }
                                """,
                    "params": {"types_to_remove": types_to_remove, "charger_types": charger_types},
                }
            }

            self.es_client.update(index=index, id=location_id, body=update_body)

        except Exception as e:
            raise RuntimeError(f"Failed to update document: {e}")

    def delete_charger_type_and_power_output(self, index, location_id, charger_types, number_of_station: int = 1) -> None:
        try:
            if not self.es_client.exists(index=index, id=location_id):
                raise RuntimeError(f"Document with ID {location_id} does not exist in index {index}.")

            update_body = {
                "script": {
                    "source": """

                                if (ctx._source.charger_types != null) {
                                    def types_to_remove = params.types_to_remove;

                                    for (def type_to_remove : types_to_remove) {
                                        for (int i = 0; i < ctx._source.charger_types.size(); i++) {
                                            def charger = ctx._source.charger_types[i];
                                            if (charger.power_output == type_to_remove.power_output && charger.type == type_to_remove.type) {
                                                ctx._source.charger_types.remove(i);
                                                break;
                                            }
                                        }
                                    }

                                    ctx._source.station_count -= params.number_of_station;
                                }
                                """,
                    "params": {"types_to_remove": charger_types, "number_of_station": number_of_station},
                }
            }

            self.es_client.update(index=index, id=location_id, body=update_body)

        except Exception as e:
            raise RuntimeError(f"Failed to update document: {e}")

    def search_location_on_direction(self, coordinates: list[Coordinate]) -> List[LocationResponse]:

        es_query = {
            "query": {
                "bool": {
                    "filter": {
                        "geo_polygon": {
                            "location": {"points": [{"lat": coordinate.lat, "lon": coordinate.lng} for coordinate in coordinates]}
                        }
                    },
                }
            }
        }

        try:
            response = self.es_client.search(index=configs.ES_LOCATION_INDEX, body=es_query)
            hits = response["hits"]["hits"]
            results = self.__process_search_results_location_list(hits)
        except Exception as e:
            raise NotFoundError(detail=str(e))

        return results

    def wipe_data(self, index: str):
        if self.es_client.indices.exists(index=index):
            response = self.es_client.indices.delete(index=index)
            return response
        return None


def get_search_result(response):
    return [hit["_source"] for hit in response["hits"]["hits"]]
