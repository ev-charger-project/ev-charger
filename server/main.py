import os
import sys
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from elasticsearch import Elasticsearch


# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from server.services.here.here_api import get_here_ev_data
from server.services.ev_data.location_upsert import create_locations_from_data
from server.services.ev_data.ev_charger_upsert import create_ev_chargers_from_data
from server.services.here.here_grid_fetch import (
    fetch_and_upsert_la_ev_data,
)


from app.constant.enum.location import Country
from app.core.config import configs
from app.model.amenities import Amenities
from app.constant.enum.location_access import LocationAccess


os.makedirs("logs", exist_ok=True)  # Ensure logs directory exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    filename="logs/server.log",
    filemode="a",
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

logger = logging.getLogger(__name__)


def fetch_ev_data():
    return get_here_ev_data()


def create_locations(data, location_service):
    return create_locations_from_data(location_service, data)


def create_ev_chargers(
    locations_and_items,
    ev_charger_service,
    power_plug_type_service,
    power_output_service,
):

    return create_ev_chargers_from_data(
        locations_and_items,
        ev_charger_service,
        power_plug_type_service,
        power_output_service,
    )


def scheduled_job(
    location_service, ev_charger_service, power_plug_type_service, power_output_service
):
    try:
        fetch_and_upsert_la_ev_data(
            location_service,
            ev_charger_service,
            power_plug_type_service,
            power_output_service,
        )
        logger.info("Scheduled job completed successfully.")
    except Exception as e:
        logger.error(f"Error during scheduled job: {e}", exc_info=True)
        raise e


if __name__ == "__main__":
    from app.services.location_service import LocationService
    from app.repository.location_repository import LocationRepository
    from app.repository.elastic_repository import ElasticsearchRepository
    from app.services.gg_map_service import GGMapService
    from app.repository.power_plug_type_repository import PowerPlugTypeRepository
    from app.services.power_plug_type_service import PowerPlugTypeService
    from app.repository.power_output_repository import PowerOutputRepository
    from app.services.power_output_service import PowerOutputService
    from app.repository.ev_charger_repository import EVChargerRepository
    from app.services.ev_charger_service import EVChargerService

    # Create the database engine and session factory
    DATABASE_URI = configs.DATABASE_URI
    engine = create_engine(DATABASE_URI, echo=True)
    session_factory = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )

    # Create the Elasticsearch client
    es_client = Elasticsearch(
        hosts=[configs.ES_URL], basic_auth=(configs.ES_USERNAME, configs.ES_PASSWORD)
    )

    # Initialize the necessary services and repositories
    location_repository = LocationRepository(session_factory)
    es_repository = ElasticsearchRepository(es_client)
    gg_map_service = GGMapService()
    location_service = LocationService(
        location_repository, es_repository, gg_map_service
    )

    power_plug_type_repository = PowerPlugTypeRepository(session_factory)
    power_plug_type_service = PowerPlugTypeService(power_plug_type_repository)

    power_output_repository = PowerOutputRepository(session_factory)
    power_output_service = PowerOutputService(power_output_repository)

    ev_charger_repository = EVChargerRepository(session_factory)
    ev_charger_service = EVChargerService(ev_charger_repository, es_repository)

    # min = int(os.getenv("MINUTE_INTERVAL", "10"))
    min = 1
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        lambda: scheduled_job(
            location_service=location_service,
            ev_charger_service=ev_charger_service,
            power_plug_type_service=power_plug_type_service,
            power_output_service=power_output_service,
        ),
        "interval",
        minutes=min,
    )
    scheduler.start()
    logger.info(f"Scheduler started with interval of {min} minutes.")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler stopped.")
