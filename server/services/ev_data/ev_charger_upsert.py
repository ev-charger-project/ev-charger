# Add the root directory to the Python path
import os
import sys


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from app.constant.enum.availability import AvailabilityEnum
from app.constant.enum.power_plug_type import PowerModel
from app.schema.ev_charger_schema import CreateEVCharger, CreatePort
from app.schema.power_plug_type_schema import CreatePowerPlugType
from app.schema.power_output_schema import CreatePowerOutput


def create_ev_chargers_from_data(
    locations_and_items,
    ev_charger_service,
    power_plug_type_service,
    power_output_service,
):

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
