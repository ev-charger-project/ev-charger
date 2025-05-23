import json
import os
import sys
import datetime
import re

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from elasticsearch import Elasticsearch


# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Import necessary modules from the app
from app.constant.enum.location import Country
from app.core.config import configs
from app.model.amenities import Amenities
from app.constant.enum.location_access import LocationAccess


def get_enum_value(enum_cls, value, default=None):
    """Helper to safely get enum value from string."""
    try:
        return enum_cls(value)
    except Exception:
        # Try to match by name (case-insensitive)
        for member in enum_cls:
            if member.name.lower() == value.lower().replace(" ", "_"):
                return member
        if default is not None:
            return default
        raise


def create_locations_from_json(location_service, json_path="multi-connectors.json"):
    from app.schema.location_schema import CreateEditLocation

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    created_locations = []

    for item in data.get("items", []):
        address = item.get("address", {})
        position = item.get("position", {})
        contacts = item.get("contacts", [])
        ev_station = item.get("extended", {}).get("evStation", {})

        # Extract phone and website from contacts
        phone_number = None
        website_url = None
        if contacts:
            contact = contacts[0]
            phones = contact.get("phone", [])
            if phones:
                phone_number = phones[0].get("value")
            wwws = contact.get("www", [])
            if wwws:
                website_url = wwws[0].get("value")

        # Payment methods (only accepted ones)
        payment_methods = []
        for pm in ev_station.get("paymentMethods", []):
            if pm.get("accepted"):
                payment_methods.append(pm.get("id"))

        # Map country string to Country enum
        country_str = address.get("countryName", "United States")
        try:
            country = get_enum_value(Country, country_str)
        except Exception:
            print(f"Unknown country: {country_str}, skipping item.")
            continue

        # Map access string to LocationAccess enum
        access_str = ev_station.get("access")
        access = None
        if access_str:
            try:
                access = get_enum_value(LocationAccess, access_str)
            except Exception:
                print(f"Unknown access: {access_str}, setting as None.")

        # print external_id, county, state, image_url, total_charging_ports, access, payment_methods
        print(f"Processing item with external_id: {item.get('id')}")
        print(f"County: {address.get('county')}")
        print(f"State: {address.get('state')}")
        print(f"Image URL: {item.get('imageUrl')}")
        print(f"Total Charging Ports: {ev_station.get('totalNumberOfConnectors')}")
        print(f"Access: {access}")
        print(f"Payment Methods: {payment_methods}")

        schema = CreateEditLocation(
            external_id=item.get("id"),
            location_name=item.get("title"),
            street=address.get("street", ""),
            house_number=address.get("houseNumber"),
            district=address.get("district"),
            city=address.get("city", ""),
            state=address.get("state"),
            county=address.get("county"),
            country=country,
            postal_code=address.get("postalCode"),
            latitude=position.get("lat"),
            longitude=position.get("lng"),
            phone_number=phone_number,
            website_url=website_url,
            description=address.get("label"),
            image_url=None,
            pricing=None,
            parking_level=None,
            total_charging_ports=ev_station.get("totalNumberOfConnectors"),
            access=access,
            payment_methods=payment_methods if payment_methods else None,
            working_days=parse_opening_hours(item.get("openingHours", [])),
        )

        try:
            location = location_service.add(schema)
            print(f"Created location: {schema.location_name} (ID: {location.id})")
            created_locations.append((location, item))

        except Exception as e:
            print(f"Failed to create location '{schema.location_name}': {e}")
    return created_locations


def parse_opening_hours(opening_hours_json):
    from app.schema.location_schema import WorkingDay

    working_days = []
    if not opening_hours_json:
        return working_days

    for oh in opening_hours_json:
        structured = oh.get("structured", [])
        for s in structured:
            recurrence = s.get("recurrence", "")
            days = []
            if "BYDAY:" in recurrence:
                days_str = recurrence.split("BYDAY:")[1].split(";")[0]
                day_map = {
                    "MO": 1,
                    "TU": 2,
                    "WE": 3,
                    "TH": 4,
                    "FR": 5,
                    "SA": 6,
                    "SU": 7,
                }
                days = [day_map[d] for d in days_str.split(",") if d in day_map]

            start_str = s.get("start", "T000000")
            open_time = datetime.time(
                int(start_str[1:3]), int(start_str[3:5]), int(start_str[5:7])
            )
            print("open_time: ", open_time)
            duration = s.get("duration", "PT24H00M")
            match = re.match(r"PT(\d+)H(\d+)M", duration)
            hours = int(match.group(1)) if match else 24
            minutes = int(match.group(2)) if match else 0
            # Avoid open_time == close_time
            # Calculate close_time by adding duration to open_time
            dt_open = datetime.datetime(
                2000, 1, 1, open_time.hour, open_time.minute, open_time.second
            )
            dt_close = dt_open + datetime.timedelta(hours=hours, minutes=minutes)
            close_time = dt_close.time()
            print("close_time: ", close_time)

            # If close_time is exactly midnight, set to 23:59:59
            if close_time == datetime.time(0, 0, 0):
                close_time = datetime.time(23, 59, 59)
                print("close_time: ", close_time)
            for day in days:
                working_days.append(
                    WorkingDay(day=day, open_time=open_time, close_time=close_time)
                )
    return working_days


def create_ev_chargers_from_json(
    locations_and_items,
    ev_charger_service,
    power_plug_type_service,
    power_output_service,
):
    from app.constant.enum.availability import AvailabilityEnum
    from app.constant.enum.power_plug_type import PowerModel
    from app.schema.ev_charger_schema import CreateEVCharger, CreatePort
    from app.schema.power_plug_type_schema import CreatePowerPlugType
    from app.schema.power_output_schema import CreatePowerOutput

    for location, item in locations_and_items:
        extended = item.get("extended", {})
        ev_availability = extended.get("evAvailability", {})
        ev_station = extended.get("evStation", {})
        station_list = ev_availability.get("stations", [])
        connectors_info = ev_station.get("connectors", [])

        if station_list:
            evses = station_list[0].get("evses", [])
            for evse in evses:
                cpo_id = evse.get("cpoId")
                cpo_evse_emi3_id = evse.get("cpoEvseEMI3Id")
                availability = AvailabilityEnum(evse.get("state", "UNAVAILABLE"))
                last_updated = evse.get("last_updated")
                if last_updated:
                    import datetime

                    last_updated = datetime.datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                print("last_updated: ", last_updated)

                ports = []
                for connector in evse.get("connectors", []):
                    type_id = connector.get("typeId")
                    connector_detail = next(
                        (
                            c
                            for c in connectors_info
                            if c.get("connectorType", {}).get("id") == type_id
                        ),
                        None,
                    )
                    if not connector_detail:
                        print(
                            f"Connector type {type_id} not found in evStation.connectors."
                        )
                        continue

                    supplier_name = connector_detail.get("supplierName")
                    connector_type = connector_detail.get("connectorType", {})
                    plug_type = connector_type.get("name")
                    plug_type_id = connector_type.get("id")
                    fixed_plug = connector_detail.get("fixedCable")
                    volts_range = connector_detail.get("chargingPoint", {}).get(
                        "voltsRange", ""
                    )
                    amps_range = connector_detail.get("chargingPoint", {}).get(
                        "ampsRange", ""
                    )
                    max_power_level = connector_detail.get("maxPowerLevel")

                    if "DC" in volts_range:
                        power_model = PowerModel.DC
                    else:
                        power_model = PowerModel.AC

                    voltage = None
                    amperage = None
                    try:
                        voltage = int(
                            volts_range.split("-")[0].replace("V", "").replace(" ", "")
                        )
                    except Exception:
                        pass
                    try:
                        amperage = int(amps_range.replace("A", "").replace(" ", ""))
                    except Exception:
                        pass

                    print("Creaing power plug type")
                    print("supplier_name: ", supplier_name)
                    print("power_model: ", power_model)
                    print("plug_type: ", plug_type)
                    print("plug_type_id: ", plug_type_id)
                    print("fixed_plug: ", fixed_plug)

                    # Create or get PowerPlugType
                    power_plug_type_schema = CreatePowerPlugType(
                        supplier_name=supplier_name,
                        power_model=power_model,
                        plug_type=plug_type,
                        plug_type_id=plug_type_id,
                        fixed_plug=fixed_plug,
                        plug_image_url=None,
                        additional_note=None,
                        power_plug_region=None,
                    )
                    power_plug_type = power_plug_type_service.add(
                        power_plug_type_schema
                    )

                    print("Creating power output")
                    print("max_power_level: ", max_power_level)
                    print("voltage: ", voltage)
                    print("amperage: ", amperage)

                    # Create or get PowerOutput
                    power_output_schema = CreatePowerOutput(
                        output_value=max_power_level,
                        voltage=voltage,
                        amperage=amperage,
                        charging_speed=None,
                        description=None,
                    )
                    power_output = power_output_service.add(power_output_schema)

                    port = CreatePort(
                        power_plug_type_id=power_plug_type.id,
                        power_output_id=power_output.id,
                    )
                    ports.append(port)

                print("Creating EV Charger")
                ev_charger_schema = CreateEVCharger(
                    location_id=location.id,
                    # external_id=external_id,
                    cpo_id=cpo_id,
                    cpo_evse_emi3_id=cpo_evse_emi3_id,
                    availability=availability,
                    last_updated=last_updated,
                    station_name=None,
                    installation_date=None,
                    last_maintenance_date=None,
                    ev_charger_ports=ports,
                )
                ev_charger_service.add(ev_charger_schema)


def main():
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
    from app.repository.ev_charger_port_repository import EVChargerPortRepository
    from app.services.ev_charger_port_service import EVChargerPortService

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

    ev_charger_port_repository = EVChargerPortRepository(session_factory)
    ev_charger_port_service = EVChargerPortService(ev_charger_port_repository)

    locations_and_items = create_locations_from_json(
        location_service, json_path="multi-connectors.json"
    )
    create_ev_chargers_from_json(
        locations_and_items,
        ev_charger_service,
        power_plug_type_service,
        power_output_service,
    )


if __name__ == "__main__":
    main()
