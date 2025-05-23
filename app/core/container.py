import logging

from dependency_injector import containers, providers
from elasticsearch import Elasticsearch

from app.core.config import configs
from app.core.database import Database
from app.repository import (
    AmenitiesRepository,
    CityRepository,
    DistrictRepository,
    EVChargerPortRepository,
    EVChargerRepository,
    LocationAmenitiesRepository,
    LocationRepository,
    LocationSearchHistoryRepository,
    PowerOutputRepository,
    PowerPlugTypeRepository,
    UserFavoriteRepository,
)
from app.repository.elastic_repository import ElasticsearchRepository
from app.services import (
    AmenitiesService,
    CityService,
    DistrictService,
    EVChargerPortService,
    EVChargerService,
    GGMapService,
    LocationAmenitiesService,
    LocationSearchHistoryService,
    LocationService,
    MediaService,
    PowerOutputService,
    PowerPlugTypeService,
    UserFavoriteService,
)


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.ev_charger",
            "app.api.v1.endpoints.power_plug_type",
            "app.api.v1.endpoints.location",
            "app.api.v1.endpoints.power_output",
            "app.api.v1.endpoints.ev_charger_port",
            "app.api.v1.endpoints.gg_map",
            "app.api.v1.endpoints.user_favorite",
            "app.api.v1.endpoints.city",
            "app.api.v1.endpoints.district",
            "app.api.v1.endpoints.media",
            "app.api.v1.endpoints.location_amenities",
            "app.api.v1.endpoints.amenities",
            "app.api.v1.endpoints.location_search_history",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)
    elasticsearch_client = providers.Singleton(
        Elasticsearch,
        hosts=configs.ES_URL,
        basic_auth=(configs.ES_USERNAME, configs.ES_PASSWORD),
        verify_certs=False,
        ssl_show_warn=False,
        http_compress=True,
    )
    logger = providers.Singleton(logging.getLogger, name="uvicorn")
    # Repositories
    ev_charger_repository = providers.Factory(EVChargerRepository, session_factory=db.provided.session)
    power_plug_type_repository = providers.Factory(PowerPlugTypeRepository, session_factory=db.provided.session)
    location_repository = providers.Factory(LocationRepository, session_factory=db.provided.session)
    user_favorite_repository = providers.Factory(UserFavoriteRepository, session_factory=db.provided.session)
    city_repository = providers.Factory(CityRepository, session_factory=db.provided.session)
    district_repository = providers.Factory(DistrictRepository, session_factory=db.provided.session)
    location_amenities_repository = providers.Factory(LocationAmenitiesRepository, session_factory=db.provided.session)
    amenities_repository = providers.Factory(AmenitiesRepository, session_factory=db.provided.session)
    location_search_history_repository = providers.Factory(LocationSearchHistoryRepository, session_factory=db.provided.session)
    power_output_repository = providers.Factory(PowerOutputRepository, session_factory=db.provided.session)
    ev_charger_port_repository = providers.Factory(EVChargerPortRepository, session_factory=db.provided.session)

    es_repository = providers.Factory(ElasticsearchRepository, es_client=elasticsearch_client)

    # Services
    gg_map_service = providers.Factory(GGMapService)
    ev_charger_service = providers.Factory(EVChargerService, ev_charger_repository=ev_charger_repository, es_repository=es_repository)
    location_service = providers.Factory(
        LocationService, location_repository=location_repository, es_repository=es_repository, gg_map_service=gg_map_service
    )
    power_plug_type_service = providers.Factory(PowerPlugTypeService, power_plug_type_repository=power_plug_type_repository)
    power_output_service = providers.Factory(PowerOutputService, power_output_repository=power_output_repository)
    ev_charger_port_service = providers.Factory(EVChargerPortService, ev_charger_port_repository=ev_charger_port_repository)
    city_service = providers.Factory(CityService, city_repository=city_repository)
    district_service = providers.Factory(DistrictService, district_repository=district_repository)
    location_search_history_service = providers.Factory(
        LocationSearchHistoryService, location_search_history_repository=location_search_history_repository
    )
    user_favorite_service = providers.Factory(UserFavoriteService, user_favorite_repository=user_favorite_repository)
    media_service = providers.Factory(MediaService, logger=logger)
    location_amenities_service = providers.Factory(LocationAmenitiesService, location_amenities_repository=location_amenities_repository)
    amenities_service = providers.Factory(AmenitiesService, amenities_repository=amenities_repository)
