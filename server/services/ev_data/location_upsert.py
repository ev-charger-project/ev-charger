import json
import os
import sys
import datetime
import re
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from elasticsearch import Elasticsearch

# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

# Import necessary modules from the app
from app.constant.enum.location import Country
from app.core.config import configs
from app.constant.enum.location_access import LocationAccess

logger = logging.getLogger(__name__)


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
            logger.debug(f"open_time: {open_time}")
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
            logger.debug(f"close_time: {close_time}")

            # If close_time is exactly midnight, set to 23:59:59
            if close_time == datetime.time(0, 0, 0):
                close_time = datetime.time(23, 59, 59)
                logger.debug(f"close_time adjusted to: {close_time}")
            for day in days:
                working_days.append(
                    WorkingDay(day=day, open_time=open_time, close_time=close_time)
                )
    return working_days


def create_locations_from_data(location_service, data: dict):
    from app.schema.location_schema import CreateEditLocation

    created_locations = []

    for item in data.get("items", []):
        address = item.get("address", {})
        position = item.get("position", {})
        contacts = item.get("contacts", [])
        ev_station = item.get("extended", {}).get("evStation", {})
        ev_availability = item.get("extended", {}).get("evAvailability", {})
        station_list = ev_availability.get("stations", [])

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
            logger.warning(f"Unknown country: {country_str}, skipping item.")
            continue

        # Map access string to LocationAccess enum
        access_str = ev_station.get("access")
        access = None
        if access_str:
            try:
                access = get_enum_value(LocationAccess, access_str)
            except Exception:
                logger.warning(f"Unknown access: {access_str}, setting as None.")

        logger.info(
            f"Processing item with external_id: {item.get('id')}, county: {address.get('county')}, state: {address.get('state')}, total_charging_ports: {ev_station.get('totalNumberOfConnectors')}, access: {access}, payment_methods: {payment_methods}"
        )

        schema = CreateEditLocation(
            here_id=station_list[0].get("id") if station_list else None,
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
            logger.info(
                f"Upserted location: {schema.location_name} (ID: {location.id})"
            )
            created_locations.append((location, item))
        except Exception as e:
            logger.warning(f"Failed to upsert location '{schema.location_name}': {e}")
    return created_locations


# import json
# import os
# import sys
# import datetime
# import re

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from elasticsearch import Elasticsearch


# # Add the root directory to the Python path
# root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# sys.path.append(root_dir)

# # Import necessary modules from the app
# from app.constant.enum.location import Country
# from app.core.config import configs
# from app.constant.enum.location_access import LocationAccess


# def get_enum_value(enum_cls, value, default=None):
#     """Helper to safely get enum value from string."""
#     try:
#         return enum_cls(value)
#     except Exception:
#         # Try to match by name (case-insensitive)
#         for member in enum_cls:
#             if member.name.lower() == value.lower().replace(" ", "_"):
#                 return member
#         if default is not None:
#             return default
#         raise


# def parse_opening_hours(opening_hours_json):
#     from app.schema.location_schema import WorkingDay

#     working_days = []
#     if not opening_hours_json:
#         return working_days

#     for oh in opening_hours_json:
#         structured = oh.get("structured", [])
#         for s in structured:
#             recurrence = s.get("recurrence", "")
#             days = []
#             if "BYDAY:" in recurrence:
#                 days_str = recurrence.split("BYDAY:")[1].split(";")[0]
#                 day_map = {
#                     "MO": 1,
#                     "TU": 2,
#                     "WE": 3,
#                     "TH": 4,
#                     "FR": 5,
#                     "SA": 6,
#                     "SU": 7,
#                 }
#                 days = [day_map[d] for d in days_str.split(",") if d in day_map]

#             start_str = s.get("start", "T000000")
#             open_time = datetime.time(
#                 int(start_str[1:3]), int(start_str[3:5]), int(start_str[5:7])
#             )
#             print("open_time: ", open_time)
#             duration = s.get("duration", "PT24H00M")
#             match = re.match(r"PT(\d+)H(\d+)M", duration)
#             hours = int(match.group(1)) if match else 24
#             minutes = int(match.group(2)) if match else 0
#             # Avoid open_time == close_time
#             # Calculate close_time by adding duration to open_time
#             dt_open = datetime.datetime(
#                 2000, 1, 1, open_time.hour, open_time.minute, open_time.second
#             )
#             dt_close = dt_open + datetime.timedelta(hours=hours, minutes=minutes)
#             close_time = dt_close.time()
#             print("close_time: ", close_time)

#             # If close_time is exactly midnight, set to 23:59:59
#             if close_time == datetime.time(0, 0, 0):
#                 close_time = datetime.time(23, 59, 59)
#                 print("close_time: ", close_time)
#             for day in days:
#                 working_days.append(
#                     WorkingDay(day=day, open_time=open_time, close_time=close_time)
#                 )
#     return working_days


# def create_locations_from_data(location_service, data: dict):
#     from app.schema.location_schema import CreateEditLocation

#     created_locations = []

#     for item in data.get("items", []):
#         address = item.get("address", {})
#         position = item.get("position", {})
#         contacts = item.get("contacts", [])
#         ev_station = item.get("extended", {}).get("evStation", {})
#         ev_availability = item.get("extended", {}).get("evAvailability", {})
#         station_list = ev_availability.get("stations", [])

#         # Extract phone and website from contacts
#         phone_number = None
#         website_url = None
#         if contacts:
#             contact = contacts[0]
#             phones = contact.get("phone", [])
#             if phones:
#                 phone_number = phones[0].get("value")
#             wwws = contact.get("www", [])
#             if wwws:
#                 website_url = wwws[0].get("value")

#         # Payment methods (only accepted ones)
#         payment_methods = []
#         for pm in ev_station.get("paymentMethods", []):
#             if pm.get("accepted"):
#                 payment_methods.append(pm.get("id"))

#         # Map country string to Country enum
#         country_str = address.get("countryName", "United States")
#         try:
#             country = get_enum_value(Country, country_str)
#         except Exception:
#             print(f"Unknown country: {country_str}, skipping item.")
#             continue

#         # Map access string to LocationAccess enum
#         access_str = ev_station.get("access")
#         access = None
#         if access_str:
#             try:
#                 access = get_enum_value(LocationAccess, access_str)
#             except Exception:
#                 print(f"Unknown access: {access_str}, setting as None.")

#         # print external_id, county, state, image_url, total_charging_ports, access, payment_methods
#         print(f"Processing item with external_id: {item.get('id')}")
#         print(f"County: {address.get('county')}")
#         print(f"State: {address.get('state')}")
#         print(f"Image URL: {item.get('imageUrl')}")
#         print(f"Total Charging Ports: {ev_station.get('totalNumberOfConnectors')}")
#         print(f"Access: {access}")
#         print(f"Payment Methods: {payment_methods}")

#         schema = CreateEditLocation(
#             here_id=station_list[0].get("id") if station_list else None,
#             external_id=item.get("id"),
#             location_name=item.get("title"),
#             street=address.get("street", ""),
#             house_number=address.get("houseNumber"),
#             district=address.get("district"),
#             city=address.get("city", ""),
#             state=address.get("state"),
#             county=address.get("county"),
#             country=country,
#             postal_code=address.get("postalCode"),
#             latitude=position.get("lat"),
#             longitude=position.get("lng"),
#             phone_number=phone_number,
#             website_url=website_url,
#             description=address.get("label"),
#             image_url=None,
#             pricing=None,
#             parking_level=None,
#             total_charging_ports=ev_station.get("totalNumberOfConnectors"),
#             access=access,
#             payment_methods=payment_methods if payment_methods else None,
#             working_days=parse_opening_hours(item.get("openingHours", [])),
#         )

#         try:
#             location = location_service.add(schema)
#             print(f"Created location: {schema.location_name} (ID: {location.id})")
#             created_locations.append((location, item))

#         except Exception as e:
#             print(f"Failed to create location '{schema.location_name}': {e}")
#     return created_locations
