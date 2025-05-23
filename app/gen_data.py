import random
import math
import os
import sys
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from elasticsearch import Elasticsearch


# Add the root directory to the Python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

# Import necessary modules from the app
from app.core.config import configs
from app.model.amenities import Amenities

# Define your current location
CURRENT_LAT = 10.80008
CURRENT_LNG = 106.66473

# # Function to generate random locations around a given point
# def generate_random_location(lat: float, lng: float, distance_km: float):
#     # Convert distance from km to degrees
#     delta_lat = distance_km / 111.32  # 1 degree latitude is approximately 111.32 km
#     delta_lng = distance_km / (111.32 * abs(math.cos(math.radians(lat))))  # Adjust for longitude

#     random_lat = lat + random.uniform(-delta_lat, delta_lat)
#     random_lng = lng + random.uniform(-delta_lng, delta_lng)

#     return random_lat, random_lng

# # Function to create a location using the service
# def create_location(service, lat: float, lng: float, name: str, amenities_ids: list):
#     from app.schema.location_schema import CreateEditLocation, WorkingDay

#     schema = CreateEditLocation(
#         location_name=name,
#         street="Random Street",
#         district="Random District",
#         city="Random City",
#         country="Vietnam",
#         postal_code="123456",
#         latitude=lat,
#         longitude=lng,
#         description="Random Description",
#         image_url="http://example.com/image.jpg",
#         pricing="Free",
#         phone_number="+1234567890",
#         parking_level="1",
#         working_days=[
#             WorkingDay(day=1, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=2, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=3, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=4, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=5, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=6, open_time="08:00", close_time="18:00"),
#             WorkingDay(day=7, open_time="08:00", close_time="18:00"),
#         ],
#         amenities_id=amenities_ids
#     )
#     location = service.add(schema)
#     print(f"Location '{name}' created successfully with ID: {location.id}")
    
def create_power_plug_type(service, power_model, plug_type, plug_image_url, power_plug_region, additional_note):
    from app.schema.power_plug_type_schema import CreatePowerPlugType
    schema = CreatePowerPlugType(
        power_model=power_model,
        plug_type=plug_type,
        plug_image_url=plug_image_url,
        power_plug_region=power_plug_region,
        additional_note=additional_note
    )
    power_plug_type = service.add(schema)
    print(f"Power Plug Type '{plug_type}' created successfully with ID: {power_plug_type.id}")

def create_power_plug_types(service):
    # Data for power plug types
    power_plug_types = [
        {
            "power_model": "AC",
            "plug_type": "Type 2",
            "plug_image_url": "https://example.com/type2.png",
            "power_plug_region": "Europe, Asia, Oceania",
            "additional_note": "Widely adopted in European Union EVs and charging stations."
        },
        {
            "power_model": "DC",
            "plug_type": "CCS Combo 1",
            "plug_image_url": "https://example.com/ccs1.png",
            "power_plug_region": "North America",
            "additional_note": "Used for rapid DC charging and supported by many North American EV brands."
        },
        {
            "power_model": "DC",
            "plug_type": "CCS Combo 2",
            "plug_image_url": "https://example.com/ccs2.png",
            "power_plug_region": "Europe, Asia, Oceania",
            "additional_note": "Preferred connector for DC fast charging in Europe."
        },
        {
            "power_model": "DC",
            "plug_type": "CHAdeMO",
            "plug_image_url": "https://example.com/chademo.png",
            "power_plug_region": "Japan, Europe, North America",
            "additional_note": "Popular for fast charging and supports vehicle-to-grid technology."
        },
        {
            "power_model": "AC",
            "plug_type": "Tesla Connector",
            "plug_image_url": "https://example.com/tesla_connector.png",
            "power_plug_region": "North America, Europe, Asia-Pacific",
            "additional_note": "Widely used for Tesla vehicles globally, with CCS adapter compatibility in select regions."
        },
        {
            "power_model": "DC",
            "plug_type": "Tesla Supercharger",
            "plug_image_url": "https://example.com/tesla_supercharger.png",
            "power_plug_region": "North America, Europe, Asia-Pacific",
            "additional_note": "Exclusive to Tesla vehicles and provides rapid DC charging."
        }
    ]

    for ppt in power_plug_types:
        create_power_plug_type(
            service,
            ppt["power_model"],
            ppt["plug_type"],
            ppt["plug_image_url"],
            ppt["power_plug_region"],
            ppt["additional_note"]
        )
def create_power_output(service, output_value, charging_speed, voltage, description):
    from app.schema.power_output_schema import CreatePowerOutput
    schema = CreatePowerOutput(
        output_value=output_value,
        charging_speed=charging_speed,
        voltage=voltage,
        description=description
    )
    power_output = service.add(schema)
    print(f"Power Output with value '{output_value}' created successfully with ID: {power_output.id}")

def create_power_outputs(service):
    power_outputs = [
        {
            "output_value": 3.7,
            "charging_speed": "Slow",
            "voltage": 230,
            "description": "Standard home charging method, suitable for overnight charging of EVs."
        },
        {
            "output_value": 22,
            "charging_speed": "Fast",
            "voltage": 400,
            "description": "Faster alternative for home and public stations; suitable for daily charging needs."
        },
        {
            "output_value": 350,
            "charging_speed": "Ultra-Fast",
            "voltage": 800,
            "description": "High-speed charging for modern EVs; provides 80% charge in 15-30 minutes."
        }
    ]

    for po in power_outputs:
        create_power_output(
            service,
            po["output_value"],
            po["charging_speed"],
            po["voltage"],
            po["description"]
        )
       
def create_amenity(service, amenities_types, image_url):
    from app.schema.amenities_schema import CreateAmenities
    schema = CreateAmenities(
        amenities_types=amenities_types,
        image_url=image_url
    )
    amenity = service.add(schema)
    print(f"Amenity '{amenities_types}' created successfully with ID: {amenity.id}")

def create_amenities(service):
    amenities = [
        {
            "amenities_types": "Restrooms",
            "image_url": "https://example.com/restrooms.png"
        },
        {
            "amenities_types": "Wi-Fi",
            "image_url": "https://example.com/wi-fi.png"
        },
        {
            "amenities_types": "Convenience Store",
            "image_url": "https://example.com/convenience_store.png"
        },
        {
            "amenities_types": "Restaurant",
            "image_url": "https://example.com/restaurant.png"
        },
        {
            "amenities_types": "Parking",
            "image_url": "https://example.com/parking.png"
        },
        {
            "amenities_types": "Security Cameras",
            "image_url": "https://example.com/security_cameras.png"
        },
        {
            "amenities_types": "Charging Station Information",
            "image_url": "https://example.com/charging_station_info.png"
        }
    ]

    for amenity in amenities:
        create_amenity(
            service,
            amenity["amenities_types"],
            amenity["image_url"]
        )
        
# Function to generate random locations around a given point
def generate_random_location(base_lat, base_lng, radius):
    lat = base_lat + (random.random() - 0.5) * radius / 111.32
    lng = base_lng + (random.random() - 0.5) * radius / (111.32 * abs(base_lat))
    return lat, lng

def create_location(service, lat, lng, name, district, amenities_ids, working_days):
    from app.schema.location_schema import CreateEditLocation
    schema = CreateEditLocation(
        location_name=name,
        street="Random Street",
        district=district,
        city="Thành phố Hồ Chí Minh",
        country="Vietnam",
        postal_code="700000",
        latitude=lat,
        longitude=lng,
        description="Description of the location",
        image_url="https://example.com/location.png",
        pricing="Free",
        phone_number="0123456789",
        parking_level="Ground",
        working_days=working_days,
        amenities_id=amenities_ids
    )
    location = service.add(schema)
    print(f"Location '{name}' created successfully with ID: {location.id}")

def create_locations_for_districts(service, amenities_ids):
    districts = [
        "Quận 1", "Quận 12", "Quận Gò Vấp", "Quận Bình Thạnh", "Quận Tân Bình",
        "Quận Tân Phú", "Quận Phú Nhuận", "Thành phố Thủ Đức", "Quận 3", "Quận 10",
        "Quận 11", "Quận 4", "Quận 5", "Quận 6", "Quận 8", "Quận Bình Tân",
        "Quận 7", "Huyện Củ Chi", "Huyện Hóc Môn", "Huyện Bình Chánh",
        "Huyện Nhà Bè", "Huyện Cần Giờ"
    ]

    base_lat = 10.8231  # Latitude for Ho Chi Minh City
    base_lng = 106.6297  # Longitude for Ho Chi Minh City

    place_types = ["Restaurant", "Supermarket", "Gas Station", "Mall", "Hotel", "Parking Lot", "Office Building"]

    for district in districts:
        for i in range(5):
            lat, lng = generate_random_location(base_lat, base_lng, 10)
            place_type = random.choice(place_types)
            name = f"{place_type} {district} {i+1}"

            # Randomly select amenities
            selected_amenities = random.sample(amenities_ids, k=random.randint(1, len(amenities_ids)))

            # Randomly generate working days
            working_days = [
                {"day": day, "open_time": "08:00", "close_time": "18:00"} for day in random.sample(range(1, 8), k=random.randint(1, 7))
            ]

            create_location(service, lat, lng, name, district, selected_amenities, working_days)

power_plug_type_to_power_output = {
    "Tesla Supercharger": [350],  # Example values in kW
    "Tesla Connector": [22, 3.7],
    "CHAdeMO": [350],
    "CCS Combo 2": [350],
    "CCS Combo 1": [350],
    "Type 2": [22, 3.7]
}

power_plug_types = [
    {"name": "Tesla Supercharger", "id": "4f01db35-8eb2-47be-ab51-e7def2979544"},
    {"name": "Tesla Connector", "id": "cf693921-099c-4f2e-89b3-ca632a93a534"},
    {"name": "CHAdeMO", "id": "5bd31899-f04e-4892-a527-b5d2ffe9a5bf"},
    {"name": "CCS Combo 2", "id": "0cae0934-a26a-470f-9344-510d93bfa37e"},
    {"name": "CCS Combo 1", "id": "058efdc4-0c75-4241-8010-ef6574b458dc"},
    {"name": "Type 2", "id": "658040de-8437-409d-9ac8-c2b5ec51d2c0"}
]

power_outputs = [
    {"value": 350, "id": "951f494b-61d9-4f17-915b-06686f3e1f74"},
    {"value": 22, "id": "4fbb4734-9ff7-4e73-9313-a27db7f33501"},
    {"value": 3.7, "id": "b884de5b-5e9a-4bc8-ad43-d56fc08f5cff"}
]

# Create a dictionary for quick lookup
power_plug_type_dict = {ppt["name"]: ppt["id"] for ppt in power_plug_types}
power_output_dict = {po["value"]: po["id"] for po in power_outputs}

def create_ev_chargers_for_district(ev_charger_service, location_service, district: str):
    from app.schema.ev_charger_schema import CreateEVCharger, CreatePort
    from app.schema.location_schema import FindLocation

    find_query = FindLocation(district=district)
    locations = location_service.get_list(find_query).founds
    for location in locations:
        num_stations = random.randint(1, 3)  # Random number of stations per location
        for _ in range(num_stations):
            num_ports = random.randint(1, 5)  # Random number of ports per station
            ev_charger_ports = []
            for _ in range(num_ports):
                power_plug_type_name = random.choice(list(power_plug_type_to_power_output.keys()))
                power_output_value = random.choice(power_plug_type_to_power_output[power_plug_type_name])
                ev_charger_ports.append(CreatePort(
                    power_plug_type_id=power_plug_type_dict[power_plug_type_name],
                    power_output_id=power_output_dict[power_output_value]
                ))
            ev_charger_data = CreateEVCharger(
                station_name=f"EV Charger {location.location_name} {num_stations}",
                availability="available",
                installation_date=None,
                last_maintenance_date=None,
                location_id=location.id,
                ev_charger_ports=ev_charger_ports
            )
            ev_charger_service.add(ev_charger_data)

# Main script to create 10 locations
def main():
    from app.services.location_service import LocationService
    from app.repository.location_repository import LocationRepository
    from app.repository.elastic_repository import ElasticsearchRepository
    from app.services.gg_map_service import GGMapService
    from app.repository.power_plug_type_repository import PowerPlugTypeRepository
    from app.services.power_plug_type_service import PowerPlugTypeService
    from app.repository.power_output_repository import PowerOutputRepository
    from app.services.power_output_service import PowerOutputService
    from app.repository.amenities_repository import AmenitiesRepository
    from app.services.amenities_service import AmenitiesService
    from app.repository.ev_charger_repository import EVChargerRepository
    from app.services.ev_charger_service import EVChargerService

    # Create the database engine and session factory
    DATABASE_URI = configs.DATABASE_URI
    engine = create_engine(DATABASE_URI, echo=True)
    session_factory = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    # Create the Elasticsearch client
    es_client = Elasticsearch(
        hosts=[configs.ES_URL],
        basic_auth=(configs.ES_USERNAME, configs.ES_PASSWORD)
    )

    # Initialize the necessary services and repositories
    location_repository = LocationRepository(session_factory)
    es_repository = ElasticsearchRepository(es_client)
    gg_map_service = GGMapService()
    location_service = LocationService(location_repository, es_repository, gg_map_service)
    power_plug_type_repository = PowerPlugTypeRepository(session_factory)
    power_plug_type_service = PowerPlugTypeService(power_plug_type_repository)
    # create_power_plug_types(power_plug_type_service)
    
    power_output_repository = PowerOutputRepository(session_factory)
    power_output_service = PowerOutputService(power_output_repository)
    # create_power_outputs(power_output_service)
    
    amenities_repository = AmenitiesRepository(session_factory)
    amenities_service = AmenitiesService(amenities_repository)
    # create_amenities(amenities_service)
    
    
    # Retrieve existing amenities IDs from the database
    # with session_factory() as session:
    #     amenities_ids = [str(amenity.id) for amenity in session.query(Amenities).all()]
    # create_locations_for_districts(location_service, amenities_ids)
    
    ev_charger_repository = EVChargerRepository(session_factory)
    ev_charger_service = EVChargerService(ev_charger_repository, es_repository)

    # Create EV chargers for locations in "Quận 1"
    create_ev_chargers_for_district(ev_charger_service, location_service, "Quận 3")

    
    
    
    
    # for i in range(10):
    #     lat, lng = generate_random_location(CURRENT_LAT, CURRENT_LNG, 10)
    #     name = f"Location {i+1}"
    #     create_location(location_service, lat, lng, name, amenities_ids)

if __name__ == "__main__":
    main()